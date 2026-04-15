import logging
from utils.asyncHandler import asyncHandler

from src.josaScrapper.components.data_transformation import DataTransformationComponent
from src.josaScrapper.entity.config_entity import DataTransformationConfig,DataIngestionConfig
from src.josaScrapper.entity.artifact_entity import DataIngestionArtifact,DataTransformationArtifact
class DataTransformationPipeline:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_transformation_config:DataTransformationConfig):
        self.data_ingestion_artifact=data_ingestion_artifact
        self.data_transformation_config=data_transformation_config
        self.data_transformation_component=DataTransformationComponent(
            self.data_ingestion_artifact,
            self.data_transformation_config
        )
        

    @asyncHandler
    async def initiate(self)->DataTransformationArtifact:
        logging.info("Entered initiate method of DataTransformationPipeline")
        data_transformation_artifact:DataTransformationArtifact=await self.data_transformation_component.initiate()
        logging.info(f"DataTransformationPipeline completed. Artifact — trained: {data_transformation_artifact.transformed_train_file_path}, test: {data_transformation_artifact.transformed_test_file_path}")
        logging.info("Exited initiate method of DataTransformationPipeline")
        return data_transformation_artifact
        
