

import logging
from utils.asyncHandler import asyncHandler

from src.josaScrapper.constants import DATA_SET_URI
from datasets import load_dataset,Features,Value
import pandas as pd
from utils.main_utils import read_yaml_file_sync
from src.josaScrapper.constants import DATA_LOADER_CONFIG_FILE_PATH

import os

class s3_h_connect:
    def __init__(self, data_set_uri:str=DATA_SET_URI,data_loader_config:str=DATA_LOADER_CONFIG_FILE_PATH):
        self.data_set_uri = data_set_uri
        self._schema=read_yaml_file_sync(data_loader_config)

    @asyncHandler
    async def make_data(self)->pd.DataFrame:
        logging.info(f"Entered make_data method of s3_h_connect")
        logging.debug(f"Building schema from config: {self._schema['columns']}")
        schema={k: Value(v) for item in self._schema['columns'] for k, v in item.items()}
        features=Features(schema)

        logging.info(f"Loading dataset from URI: {self.data_set_uri} with data_files: {self._schema['data_files']}")
        dataset=load_dataset(self.data_set_uri,data_files=self._schema['data_files'],features=features)
        logging.info("Dataset loaded successfully, converting to pandas DataFrame")

        dataset:pd.DataFrame=dataset['train'].to_pandas()
        logging.info(f"DataFrame created with shape: {dataset.shape}")
        logging.info("Exited make_data method of s3_h_connect")
        return dataset

        


    @asyncHandler
    async def fetch_data(self, file_path, bucket_name, object_name)->pd.DataFrame:
        logging.info(f"Entered fetch_data method of s3_h_connect with file_path={file_path}, bucket_name={bucket_name}, object_name={object_name}")

        data:pd.DataFrame=self.make_data()
        logging.info(f"Data fetched successfully with shape: {data.shape}")
        logging.info("Exited fetch_data method of s3_h_connect")

        return data
        