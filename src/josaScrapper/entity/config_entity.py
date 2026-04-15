import logging
from dataclasses import dataclass
from src.josaScrapper.constants import *
import os
from datetime import datetime

TIMESTAMP: str = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

@dataclass
class TrainingPipelineConfig:
    pipeline_name: str = PIPELINE_NAME
    artifact_dir: str = os.path.join(ARTIFACT_DIR, TIMESTAMP)
    timestamp: str = TIMESTAMP


training_pipeline_config:TrainingPipelineConfig=TrainingPipelineConfig()
logging.info(f"TrainingPipelineConfig initialized — pipeline: '{training_pipeline_config.pipeline_name}', artifact_dir: '{training_pipeline_config.artifact_dir}', timestamp: '{training_pipeline_config.timestamp}'")
@dataclass
class DataIngestionConfig:
    data_ingestion_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_INGESTION_DIR_NAME)
    feature_store_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_FEATURE_STORE_DIR, FEATURE_STORE_FILE_NAME)
    training_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_INGESTED_DIR, TRAIN_FILE_NAME)
    testing_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_INGESTED_DIR, TEST_FILE_NAME)
    train_test_split_ratio: float = DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
    # collection_name:str = DATA_INGESTION_COLLECTION_NAME    

@dataclass
class DataValidationConfig:
    data_validation_schema_path:str=os.path.join(BASE_SCHEMA_FOLDER_PATH,DATA_VALIDATION_SCHEMA_NAME)
    validation_report_file_path:str=os.path.join(training_pipeline_config.artifact_dir,DATA_VALIDATION_DIR_NAME,DATA_VALIDATION_FILE_NAME)

@dataclass
class DataTransformationConfig:
    data_transformation_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_TRANSFORMATION_DIR_NAME)

    data_transformation_schema_path:str=os.path.join(BASE_SCHEMA_FOLDER_PATH,DATA_TRANSFORMATION_SCHEMA_NAME)
    training_file_path: str = os.path.join(data_transformation_dir, DATA_INGESTION_INGESTED_DIR, TRAIN_FILE_NAME)
    testing_file_path: str = os.path.join(data_transformation_dir, DATA_INGESTION_INGESTED_DIR, TEST_FILE_NAME)
    obj_file_path:str=os.path.join(data_transformation_dir, DATA_INGESTION_INGESTED_DIR, OBJ_FILE_NAME)
# @dataclass
# class DataValidationConfig:
#     data_validation_dir:str=os.path.join(training_pipeline_config.artifact_dir,DATA_VALIDATION_DIR_NAME)
#     validation_report_file_path:str=os.path.join(data_validation_dir,DATA_VALIDATION_REPORT_FILE_NAME)


# @dataclass
# class DataTransformationConfig:
#     data_transformation_dir:str=os.path.join(training_pipeline_config.artifact_dir,DATA_TRANSFORMATION_DIR)
#     transformed_train_file_path:str=os.path.join(data_transformation_dir,TRANSFORMED_TRAIN_FILE_PATH)
#     transformed_test_file_path:str=os.path.join(data_transformation_dir,TRANSFORMED_TEST_FILE_PATH)
#     transformed_object_file_path:str=os.path.join(data_transformation_dir,TRANSFORMED_OBJECT_FILE_PATH)


 
# @dataclass
# class ModelTrainerConfig:
#     model_trainer_dir: str = os.path.join(training_pipeline_config.artifact_dir, MODEL_TRAINER_DIR_NAME)
#     trained_model_file_path: str = os.path.join(model_trainer_dir, MODEL_TRAINER_TRAINED_MODEL_DIR, MODEL_FILE_NAME)
#     expected_accuracy: float = MODEL_TRAINER_EXPECTED_SCORE
#     model_config_file_path: str = MODEL_TRAINER_MODEL_CONFIG_FILE_PATH
#     n_estimators = MODEL_TRAINER_N_ESTIMATORS
#     min_samples_split = MODEL_TRAINER_MIN_SAMPLES_SPLIT
#     min_samples_leaf = MODEL_TRAINER_MIN_SAMPLES_LEAF
#     max_depth = MIN_SAMPLES_SPLIT_MAX_DEPTH
#     criterion = MIN_SAMPLES_SPLIT_CRITERION
#     random_state = MIN_SAMPLES_SPLIT_RANDOM_STATE