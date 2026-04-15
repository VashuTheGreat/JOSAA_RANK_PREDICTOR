
from src.josaScrapper.entity.config_entity import DataValidationConfig
from src.josaScrapper.entity.artifact_entity import DataValidationArtifact,DataIngestionArtifact
from utils.main_utils import read_yaml_file
# from src.josaScrapper.constants import SCHEMA_FILE_PATH
# from exception import MyException
from utils.asyncHandler import asyncHandler
import sys
import pandas as pd
import logging
import os
import json
from utils.main_utils import write_yaml_file,read_yaml_file_sync


class DataValidationComponent:
    def __init__(self,data_validation_config:DataValidationConfig,data_ingestion_artifact:DataIngestionArtifact):
        self.data_validation_config=data_validation_config
        self.data_ingestion_artifact=data_ingestion_artifact
        self._schema_config= read_yaml_file_sync(
            self.data_validation_config.data_validation_schema_path
        )
        

    @asyncHandler
    async def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        status=len(dataframe.columns)==len(self._schema_config['columns'])
        logging.info(f"Is required colummn present: [{status}]")
        return status

    @asyncHandler
    async def is_column_exists(self,dataframe:pd.DataFrame)->bool:
        missing_numerical_columns=[]
        missing_categorical_columns=[]
        to_check_col=dataframe.columns
        for col in self._schema_config['numerical_columns']:
            if col not in to_check_col:
                missing_numerical_columns.append(col)
        for col in self._schema_config['categorical_columns']:
            if col not in to_check_col:
                missing_categorical_columns.append(col)
        if len(missing_categorical_columns)>0:
            logging.info(f"Missing categorical columns: {missing_categorical_columns}")
        if len(missing_numerical_columns)>0:
            logging.info(f"Missing numerical columns: {missing_numerical_columns}")
        return False if len(missing_numerical_columns) or len(missing_categorical_columns) else True
       

    @asyncHandler
    @staticmethod
    async def read_data(file_path:str)->pd.DataFrame:
        return pd.read_csv(file_path)
         

    @asyncHandler
    async def initiate_data_validation(self,)->DataValidationArtifact:
        validation_error_msg=None
        logging.info("Starting data validation")
        train_df,test_df=(await DataValidationComponent.read_data(file_path=self.data_ingestion_artifact.test_file_path),
                          await DataValidationComponent.read_data(self.data_ingestion_artifact.trained_file_path))
        # Train_df
        logging.info("Checking validate_number_of_columns training columns")
        status = await self.validate_number_of_columns(dataframe=train_df)  
        if not status:
            validation_error_msg+="Columns are missing in training dataframe.",sys
        logging.info(f"All required columns present in train dataframe: {status}")
        logging.info("Checking is_column_exists")
        status = await self.is_column_exists(dataframe=train_df)  
        if not status:
            validation_error_msg+="Columns are missing in training dataframe.",sys
        logging.info(f"All required columns present in train dataframe: {status}")
        
        # Test_df
        logging.info("Checking validate_number_of_columns testing columns")
        status = await self.validate_number_of_columns(dataframe=test_df)  
        if not status:
            validation_error_msg+="Columns are missing in testing dataframe.",sys
        logging.info(f"All required columns present in test dataframe: {status}")
        logging.info("Checking is_column_exists testing columns")
        status = await self.is_column_exists(dataframe=train_df)  
        if not status:
            validation_error_msg+="Columns are missing in testing dataframe.",sys
        logging.info(f"All required columns present in test dataframe: {status}")
        
        
        data_validation_artifact = DataValidationArtifact(
            validation_status=validation_error_msg==None,
            message=validation_error_msg,
            validation_report_file_path=self.data_validation_config.validation_report_file_path
        )
        # Ensure the directory for validation_report_file_path exists
        logging.info("Making report file")
        report_dir = os.path.dirname(self.data_validation_config.validation_report_file_path)
        os.makedirs(report_dir, exist_ok=True)
        await write_yaml_file(file_path=self.data_validation_config.validation_report_file_path,content=data_validation_artifact)
        
        logging.info("Data validation artifact created and saved to JSON file.")
        logging.info(f"Data validation artifact: {data_validation_artifact}")
        return data_validation_artifact
        




                                





        