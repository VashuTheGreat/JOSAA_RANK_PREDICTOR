

from utils.asyncHandler import asyncHandler

from src.josaScrapper.entity.config_entity import (ModelTrainerConfig,
                                                   DataTransformationConfig)
from src.josaScrapper.entity.artifact_entity import (ModelTrainerArtifact,
                                                     DataTransformationArtifact)
from lightgbm import LGBMRegressor
from src.josaScrapper.entity.estimator import MyModel
import pandas as pd
from utils.main_utils import read_yaml_file_sync
import os
from exception import MyException
import pickle
import logging
class ModelTrainingComponent:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        self.model_trainer_config=model_trainer_config
        self.data_transformation_artifact=data_transformation_artifact
        self._schema= read_yaml_file_sync(
            self.model_trainer_config.model_config_file_path
        )

        self.my_model=MyModel(schema=self._schema)



    @asyncHandler
    @staticmethod
    async def load_data(path:str)->pd.DataFrame:
        return pd.read_csv(path)

    @asyncHandler
    async def initiate_model_training(self)->ModelTrainerArtifact:
        logging.info("Entered initiate_model_training method of ModelTrainingComponent")

        logging.info(f"Loading transformed training data from {self.data_transformation_artifact.transformed_train_file_path}")
        train_df:pd.DataFrame=await ModelTrainingComponent.load_data(path=self.data_transformation_artifact.transformed_train_file_path)

        logging.debug(f"Training data loaded with shape: {train_df.shape}")
        
        X_train=train_df.drop(columns=self._schema['y_train'])
        y_train=train_df[self._schema['y_train']]
        
        logging.info(f"Model Training Started with X_train shape {X_train.shape} and y_train shape {y_train.shape}")
        
        success=await self.my_model.fit(X_train,y_train)
        if not success:
            logging.error("Model training failed")
            raise MyException("Error While Training Model")
        
        logging.info("Model Training Completed successfully")
        
        directory=os.path.dirname(self.model_trainer_config.trained_model_file_path)

        logging.info(f"Saving trained model to {self.model_trainer_config.trained_model_file_path}")
        os.makedirs(directory,exist_ok=True)
        with open(self.model_trainer_config.trained_model_file_path,"wb") as f:
            pickle.dump(obj=self.my_model.model,file=f)

        logging.info("Exited initiate_model_training method of ModelTrainingComponent")
        return ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path
        )

