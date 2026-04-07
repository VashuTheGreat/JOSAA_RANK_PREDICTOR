
from utils.asyncHandler import asyncHandler
from src.josaScrapper.constants import DATA_SET_URI,DATA_LOADER_CONFIG_FILE_PATH,FEATURE_ENGINEERING_CONFIG_FILE_PATH
from src.josaScrapper.data_access.s3_h_connect import s3_h_connect
from src.josaScrapper.entity.config_entity import DataIngestionConfig
import os
import pandas as pd
from src.josaScrapper.entity.artifact_entity import DataIngestionArtifact
import logging
from sklearn.model_selection import train_test_split
from utils.main_utils import read_yaml_file_sync


class DataIngestionComponent:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        self.data_access_class=s3_h_connect(data_loader_config=DATA_LOADER_CONFIG_FILE_PATH,data_set_uri=DATA_SET_URI)
        self.data_ingestion_config=data_ingestion_config
        
        self._schema=read_yaml_file_sync(FEATURE_ENGINEERING_CONFIG_FILE_PATH)


    @asyncHandler
    async def split(self,data:pd.DataFrame):
        try:
            logging.info(f"Entered split method of DataIngestionComponent with train_test_split_ratio={self._schema['feature_engineering']['TRAIN_TEST_SPLIT_RATIO']}")
            logging.info(f"Splitting data into train and test sets with ratio {self._schema['feature_engineering']['TRAIN_TEST_SPLIT_RATIO']} and random_state {self._schema['feature_engineering']['RANDOM_STATE']}")
            train_set, test_set = train_test_split(data, test_size=self._schema['feature_engineering']['TRAIN_TEST_SPLIT_RATIO'], random_state=self._schema['feature_engineering']['RANDOM_STATE'])
            logging.info(f"Data split successfully into train set with shape {train_set.shape} and test set with shape {test_set.shape}")
            logging.info("Exited split method of DataIngestionComponent")
            return train_set, test_set
        except Exception as e:
            logging.error(f"Error in split method of DataIngestionComponent: {e}")
            raise e
        

    async def initiate(self)->DataIngestionArtifact:
        logging.info(f"Entered in the initiate method on data ingestion component")
        logging.info(f"Creating directory at {self.data_ingestion_config.data_ingestion_dir} for data ingestion")
        os.makedirs(self.data_ingestion_config.data_ingestion_dir, exist_ok=True)

        logging.info(f"Creating directory at {os.path.dirname(self.data_ingestion_config.feature_store_file_path)} for feature store")
        dir_name=os.path.dirname(self.data_ingestion_config.feature_store_file_path)
        os.makedirs(dir_name, exist_ok=True)

        logging.info(f"Fetching data from s3")
        data:pd.DataFrame=await self.data_access_class.make_data()
        data.to_csv(self.data_ingestion_config.feature_store_file_path, index=False)


        logging.info(f"Splitting data into train and test sets with ratio {self.data_ingestion_config.train_test_split_ratio}")

        train_set, test_set = await self.split(data=data)
        logging.info(f"Saving train set to {self.data_ingestion_config.training_file_path} and test set to {self.data_ingestion_config.testing_file_path}")
        os.makedirs(os.path.dirname(self.data_ingestion_config.training_file_path), exist_ok=True)
        train_set.to_csv(self.data_ingestion_config.training_file_path, index=False)
        test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False)
        data_ingestion_artifact:DataIngestionArtifact=DataIngestionArtifact(
            trained_file_path=self.data_ingestion_config.training_file_path,
            test_file_path=self.data_ingestion_config.testing_file_path
        )
        logging.info("Exited the initiate method of data ingestion component")

        return data_ingestion_artifact
