
import os
import shutil

import sys


sys.path.append(os.getcwd())




from logger import *
from src.josaScrapper.entity.config_entity import DataIngestionConfig
from src.josaScrapper.pipelines.DataIngestion_pipeline import DataIngestionPipeline

import asyncio

async def main():
    data_ingestion_config=DataIngestionConfig()
    data_ingestion_pipeline=DataIngestionPipeline(
        data_ingestion_config=data_ingestion_config
    )
    data_ingestion_artifact=await data_ingestion_pipeline.initiate()
    print(data_ingestion_artifact)

if __name__=="__main__":
    asyncio.run(main())