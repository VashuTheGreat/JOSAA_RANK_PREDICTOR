import logging
from utils.asyncHandler import asyncHandler

from src.josaScrapper.components.data_validation import DataValidationComponent
from src.josaScrapper.entity.config_entity import DataValidationConfig
from src.josaScrapper.entity.artifact_entity import DataValidationArtifact,DataIngestionArtifact
class DataValidationPipeline:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_validation_config:DataValidationConfig):
        self.data_validation_config=data_validation_config
        self.data_ingestion_artifact=data_ingestion_artifact
        self.data_validation_component=DataValidationComponent(data_validation_config=self.data_validation_config,
                                                               data_ingestion_artifact=self.data_ingestion_artifact)
        

    @asyncHandler
    async def initiate(self)->DataValidationArtifact:
        logging.info("Entered initiate method of DataValidationPipeline")
        data_Validation_artifact:DataValidationArtifact=await self.data_validation_component.initiate_data_validation()
        logging.info(f"DataValidationPipeline completed. Artifact — status: {data_Validation_artifact.validation_status}, report: {data_Validation_artifact.validation_report_file_path}")
        logging.info("Exited initiate method of DataValidationPipeline")
        return data_Validation_artifact
        
