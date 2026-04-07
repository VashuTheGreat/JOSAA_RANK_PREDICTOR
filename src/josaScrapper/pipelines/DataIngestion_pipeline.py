import logging
from utils.asyncHandler import asyncHandler

from src.josaScrapper.components.data_ingestion import DataIngestionComponent
from src.josaScrapper.entity.config_entity import DataIngestionConfig
from src.josaScrapper.entity.artifact_entity import DataIngestionArtifact
class DataIngestionPipeline:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        self.data_ingestion_config=data_ingestion_config
        self.data_ingestion_component=DataIngestionComponent(self.data_ingestion_config)
        

    @asyncHandler
    async def initiate(self)->DataIngestionArtifact:
        logging.info("Entered initiate method of DataIngestionPipeline")
        data_ingestion_artifact:DataIngestionArtifact=await self.data_ingestion_component.initiate()
        logging.info(f"DataIngestionPipeline completed. Artifact — trained: {data_ingestion_artifact.trained_file_path}, test: {data_ingestion_artifact.test_file_path}")
        logging.info("Exited initiate method of DataIngestionPipeline")
        return data_ingestion_artifact
        
