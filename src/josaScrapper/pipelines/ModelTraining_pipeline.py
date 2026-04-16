import logging
from utils.asyncHandler import asyncHandler

from src.josaScrapper.components.data_ingestion import DataIngestionComponent
from src.josaScrapper.entity.config_entity import (DataIngestionConfig,
                                                   ModelTrainerConfig)
from src.josaScrapper.entity.artifact_entity import (DataIngestionArtifact,
                                                     DataTransformationArtifact,
                                                     ModelTrainerArtifact)

from src.josaScrapper.components.model_training import ModelTrainingComponent
class ModelTrainerPipeline:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        self.data_transformation_artifact=data_transformation_artifact
        self.model_trainer_config=model_trainer_config
        self.model_trainer_component=ModelTrainingComponent(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact
        )
        

    @asyncHandler
    async def initiate(self)->ModelTrainerArtifact:
        logging.info("Entered initiate method of ModelTrainerPipeline")
        model_trainer_artifact:ModelTrainerArtifact=await self.model_trainer_component.initiate_model_training()
        logging.info("Exited initiate method of ModelTrainerPipeline")
        return model_trainer_artifact
        
