
from utils.asyncHandler import asyncHandler
from src.josaScrapper.constants import DATA_SET_URI,DATA_LOADER_CONFIG_FILE_PATH,FEATURE_ENGINEERING_CONFIG_FILE_PATH
from src.josaScrapper.data_access.s3_h_connect import s3_h_connect
from src.josaScrapper.entity.config_entity import DataTransformationConfig
from src.josaScrapper.entity.artifact_entity import DataTransformationArtifact
import os
import pandas as pd
from src.josaScrapper.entity.artifact_entity import DataIngestionArtifact
import logging
from sklearn.model_selection import train_test_split
from utils.main_utils import read_yaml_file_sync
from typing import Optional, List, Literal
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold

from sklearn.preprocessing import StandardScaler
from utils.main_utils import save_object




class DataTransformationComponent:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_transformation_config:DataTransformationConfig):
        self.data_ingestion_artifact=data_ingestion_artifact
        self.data_transformation_config=data_transformation_config

        self._schema=read_yaml_file_sync(
            self.data_transformation_config.data_transformation_schema_path
        )

        self.standarizer_en={}
    @asyncHandler
    async def StandardizeColumn(self, df: pd.DataFrame, col: str):
        df[col] = pd.to_numeric(df[col], errors='coerce')
        sts=StandardScaler()
        sts.fit(df[[col]])
        self.standarizer_en[col]=sts
        standardized = sts.transform(df[[col]]).flatten()
        return standardized

    @asyncHandler
    async def log_transform_column(self, df: pd.DataFrame, col: str):
        df[col] = pd.to_numeric(df[col], errors='coerce')
        log_transformed = np.log1p(df[col].fillna(0))  # log1p to handle zero values
        return log_transformed

    @asyncHandler
    async def OneHotEncodeColumn(self, df: pd.DataFrame, col: str):
        one_hot = pd.get_dummies(df[col], prefix=col)
        return one_hot

    @asyncHandler
    async def hybrid_encode_column_kfold(self, df: pd.DataFrame, col: str, target_cols: List[str], 
                                n_splits=5, alpha=10, random_state=42):
        """
        K-Fold Target + Frequency Encoding (Leakage-free)

        Returns:
        target_encoded_series, freq_encoded_series
        """

        data = df.copy()
        
        # 🎯 combined target
        temp_target = data[target_cols].mean(axis=1)

        # 🌍 global mean
        global_mean = temp_target.mean()

        # 🧠 KFold setup
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        target_encoded = pd.Series(index=data.index, dtype=float)

        # 🔁 K-Fold loop
        for train_idx, val_idx in kf.split(data):
            train_fold = data.iloc[train_idx]
            val_fold = data.iloc[val_idx]

            train_target = temp_target.iloc[train_idx]

            # group stats on TRAIN FOLD ONLY
            means = train_fold.groupby(col)[target_cols].mean().mean(axis=1)
            counts = train_fold[col].value_counts()

            # smoothing
            smooth = (means * counts + global_mean * alpha) / (counts + alpha)

            # apply on validation fold
            val_encoded = val_fold[col].map(smooth)

            # handle unseen
            val_encoded.fillna(global_mean, inplace=True)

            target_encoded.iloc[val_idx] = val_encoded

        # 🔁 Frequency encoding (full data pe safe hai)
        freq = data[col].value_counts()
        freq_encoded = data[col].map(freq)

        return target_encoded, freq_encoded
    @asyncHandler
    async def add_col(self,df:pd.DataFrame)->pd.DataFrame:
        add_columns=self._schema['add_columns']
        participants_map=add_columns['appeared_candidates']
        df['appeared_candidates']=df['Year'].map(participants_map)
        
        # Extract Branch and Duration from Academic Program Name
        df['Branch'] = df['Academic Program Name'].str.split(' \(').str[0]
        df['Duration'] = pd.to_numeric(df['Academic Program Name'].str.extract(r'\((\d+)\s+Years').iloc[:, 0], errors='coerce')
        
        return df

    @asyncHandler
    @staticmethod
    async def load_dataset(path:str)->pd.DataFrame:
        df=pd.read_csv(path)

        return df
    
    @asyncHandler
    async def encode_col(self,df:pd.DataFrame,type=None)->pd.DataFrame:
        if type=='hybrid':
            for col in self._schema['hybrid_encode']['columns']:
                df[col+"_TargetEnc"],df[col+"_FreqEnc"]=await self.hybrid_encode_column_kfold(
                    df,col,
                    target_cols=self._schema['hybrid_encode']['target'],
                    alpha=self._schema['hybrid_encode']['alpha'],
                    n_splits=self._schema['hybrid_encode']['n_splits'],
                    random_state=self._schema['hybrid_encode']['random_state']
                )
        elif type=="oneHot":
            for col in self._schema['one_hot_encode']['columns']:
                r=await self.OneHotEncodeColumn(df,col)
                df=df.merge(r, left_index=True, right_index=True)

        elif type=="target":
            for col in self._schema['target_encode']['columns']:
                df[col+"_TargetEnc"],_=await self.hybrid_encode_column_kfold(
                    df,col,
                    target_cols=self._schema['hybrid_encode']['target'],
                    alpha=self._schema['hybrid_encode']['alpha'],
                    n_splits=self._schema['hybrid_encode']['n_splits'],
                    random_state=self._schema['hybrid_encode']['random_state']
                )

        return df   


    @asyncHandler
    async def normalise_col(self, df: pd.DataFrame, type: Literal['log', 'standardize'] = 'log') -> pd.DataFrame:
        
        match type:
            case "log":
                for col in self._schema['log_normalised_columns']:
                    df[col]= await self.log_transform_column(df,col=col)
                return df 
            
            case "standardize":
                for col in self._schema['standarize_columns']:
                    df[col]=await self.StandardizeColumn(df,col)
                return df    


            case _:
                raise ValueError("Invalid input provided")     

    @asyncHandler
    @staticmethod
    async def fixingCol(df:pd.DataFrame)->pd.DataFrame:
        bool_cols=df.select_dtypes(include=['bool']).columns

        df[bool_cols] = df[bool_cols].astype(int)
        return df            
    @asyncHandler
    async def initiate(self)->DataTransformationArtifact:
        logging.info(f"Entered in the initiate method on data transformation component")
        
        # ================ Creating Dir early to avoid missing folder on failure
        logging.info(f"Creating directory at {self.data_transformation_config.data_transformation_dir} for data transformation")
        os.makedirs(self.data_transformation_config.data_transformation_dir, exist_ok=True)

        logging.info("Loading training dataset")
        train_df=await DataTransformationComponent.load_dataset(path=self.data_ingestion_artifact.trained_file_path)
        test_df=await DataTransformationComponent.load_dataset(path=self.data_ingestion_artifact.test_file_path)

        logging.info("Handleing missing values")
        train_df.dropna(inplace=True)
        test_df.dropna(inplace=True)
        logging.info("Adding columns in data")
        train_df,test_df=await self.add_col(train_df),await self.add_col(test_df)

        # ============= incoding cols ============================

        logging.info("Encoding Train")
        await self.encode_col(train_df,type='hybrid')
        await self.encode_col(train_df,type='target')
        await self.encode_col(train_df,type='oneHot')

        logging.info("Encoding Test")
        await self.encode_col(test_df,type='hybrid')
        await self.encode_col(test_df,type='target')
        await self.encode_col(test_df,type='oneHot')


        # =================== Droping Cols =================

        logging.info(f"Droping cols {self._schema['drop_columns']}")
        train_df,test_df=train_df.drop(columns=self._schema['drop_columns']),test_df.drop(columns=self._schema['drop_columns'])
        

        # =================== Normalising Cols =====================
        logging.info("Normalising cols started")
        train_df,test_df=await self.normalise_col(train_df,type="log"),await self.normalise_col(test_df,type="log")
        train_df,test_df=await self.normalise_col(train_df,type="standardize"),await self.normalise_col(test_df,type="standardize")

        # ==================== Fixing DataTypes ===============================
        logging.info("Fixing DataTypes")
        await DataTransformationComponent.fixingCol(train_df)
        await DataTransformationComponent.fixingCol(test_df)


        logging.info(f"Saving train set to {self.data_transformation_config.training_file_path} and test set to {self.data_transformation_config.testing_file_path}")
        os.makedirs(os.path.dirname(self.data_transformation_config.training_file_path), exist_ok=True)
        train_df.to_csv(self.data_transformation_config.training_file_path, index=False)
        test_df.to_csv(self.data_transformation_config.testing_file_path, index=False)

        # =================== Saving Objects ==============
        await save_object(file_path=self.data_transformation_config.obj_file_path,obj=self.standarizer_en)
        data_transformation_artifact:DataTransformationArtifact=DataTransformationArtifact(
            transformed_train_file_path=self.data_transformation_config.training_file_path,
            transformed_test_file_path=self.data_transformation_config.testing_file_path,
            transformed_object_file_path=self.data_transformation_config.obj_file_path

        )
        logging.info("Exited the initiate method of data ingestion component")

        return data_transformation_artifact
