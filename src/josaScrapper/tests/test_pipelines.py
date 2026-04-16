
import os
import shutil

import sys
import vconsoleprint

sys.path.append(os.getcwd())




from logger import *
from src.josaScrapper.entity.config_entity import (DataIngestionConfig,
                                                   DataValidationConfig,
                                                   DataTransformationConfig,
                                                   ModelTrainerConfig)
from src.josaScrapper.pipelines.DataIngestion_pipeline import DataIngestionPipeline
from src.josaScrapper.pipelines.DataValidation_pipeline import DataValidationPipeline
from src.josaScrapper.pipelines.DataTransformation_pipeline import DataTransformationPipeline
from src.josaScrapper.entity.artifact_entity import DataValidationArtifact,DataTransformationArtifact
from src.josaScrapper.pipelines.ModelTraining_pipeline import ModelTrainerPipeline
import asyncio

async def main():
    data_ingestion_config=DataIngestionConfig()
    data_ingestion_pipeline=DataIngestionPipeline(
        data_ingestion_config=data_ingestion_config
    )
    data_ingestion_artifact=await data_ingestion_pipeline.initiate()
    print(data_ingestion_artifact)

    # Data validation
    data_validation_config:DataValidationConfig=DataValidationConfig()
    data_validation_pipeline=DataValidationPipeline(
        data_ingestion_artifact=data_ingestion_artifact,
        data_validation_config=data_validation_config
    )
    data_validation_artifact:DataValidationArtifact=await data_validation_pipeline.initiate()

    print(data_validation_artifact)


    # Data Transformation
    data_transformation_config:DataTransformationConfig=DataTransformationConfig()
    data_transformation_pipeline=DataTransformationPipeline(
        data_ingestion_artifact=data_ingestion_artifact,
        data_transformation_config=data_transformation_config
    )
    data_transformation_artifact=await data_transformation_pipeline.initiate()

    print(data_transformation_artifact)



    # Model Training
    model_trainer_config=ModelTrainerConfig()
    model_trainer_pipeline=ModelTrainerPipeline(
        model_trainer_config=model_trainer_config,
        data_transformation_artifact=data_transformation_artifact
    )
    
    model_trainer_artifact=await model_trainer_pipeline.initiate()
    print(model_trainer_artifact)

if __name__=="__main__":
    asyncio.run(main())