import logging
import os
from dataclasses import dataclass
from datetime import datetime

from src.josaScrapper.constants import *

# TIMESTAMP: str = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
TIMESTAMP:str="timestamp"
@dataclass
class TrainingPipelineConfig:
    pipeline_name: str = PIPELINE_NAME
    artifact_dir: str = os.path.join(ARTIFACT_DIR, TIMESTAMP)
    timestamp: str = TIMESTAMP


training_pipeline_config: TrainingPipelineConfig = TrainingPipelineConfig()
logging.info(
    f"TrainingPipelineConfig initialized — pipeline: '{training_pipeline_config.pipeline_name}', "
    f"artifact_dir: '{training_pipeline_config.artifact_dir}', "
    f"timestamp: '{training_pipeline_config.timestamp}'"
)

@dataclass
class DataIngestionConfig:
    data_ingestion_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_INGESTION_DIR_NAME)
    feature_store_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_FEATURE_STORE_DIR, FEATURE_STORE_FILE_NAME)
    training_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_INGESTED_DIR, TRAIN_FILE_NAME)
    testing_file_path: str = os.path.join(data_ingestion_dir, DATA_INGESTION_INGESTED_DIR, TEST_FILE_NAME)
    train_test_split_ratio: float = DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO

@dataclass
class DataValidationConfig:
    data_validation_schema_path: str = os.path.join(BASE_SCHEMA_FOLDER_PATH, DATA_VALIDATION_SCHEMA_NAME)
    validation_report_file_path: str = os.path.join(training_pipeline_config.artifact_dir, DATA_VALIDATION_DIR_NAME, DATA_VALIDATION_FILE_NAME)

@dataclass
class DataTransformationConfig:
    data_transformation_dir: str = os.path.join(training_pipeline_config.artifact_dir, DATA_TRANSFORMATION_DIR_NAME)
    data_transformation_schema_path: str = os.path.join(BASE_SCHEMA_FOLDER_PATH, DATA_TRANSFORMATION_SCHEMA_NAME)
    training_file_path: str = os.path.join(data_transformation_dir, DATA_INGESTION_INGESTED_DIR, TRAIN_FILE_NAME)
    testing_file_path: str = os.path.join(data_transformation_dir, DATA_INGESTION_INGESTED_DIR, TEST_FILE_NAME)
    obj_file_path: str = os.path.join(data_transformation_dir, DATA_INGESTION_INGESTED_DIR, OBJ_FILE_NAME)


@dataclass
class ModelTrainerConfig:
    model_trainer_dir: str = os.path.join(training_pipeline_config.artifact_dir, MODEL_TRAINER_DIR_NAME)
    trained_model_file_path: str = os.path.join(model_trainer_dir, MODEL_TRAINER_TRAINED_MODEL_DIR, MODEL_FILE_NAME)
    model_config_file_path: str = os.path.join(BASE_SCHEMA_FOLDER_PATH, MODEL_CONFIG_FILE_NAME)

@dataclass
class ModelEvaluationConfig:
    model_evaluation_dir: str = os.path.join(training_pipeline_config.artifact_dir, MODEL_EVALUATION_DIR_NAME)
    model_evaluation_report_file_path: str = os.path.join(model_evaluation_dir, MODEL_EVALUATION_REPORT_FILE_NAME)
    model_evaluation_schema_path: str = os.path.join(BASE_SCHEMA_FOLDER_PATH, MODEL_EVALUATION_SCHEMA_NAME)
    model_evaluation_plots_dir: str = os.path.join(model_evaluation_dir, MODEL_EVALUATION_PLOTS_DIR_NAME)


@dataclass
class ModelPredictionConfig:
    saved_model_dir: str = os.path.join(training_pipeline_config.artifact_dir, SAVED_MODEL_DIR_NAME)

    # Main regression model  — JOSAA/1
    model_uri: str = MLFLOW_MODEL_URI
    local_model_path: str = os.path.join(saved_model_dir, MODEL_NAME)

    # Transformation object  — JOSAA_OBJECT/1
    model_object_uri: str = MLFLOW_MODEL_OBJECT_URI
    local_object_path: str = os.path.join(saved_model_dir, SAVED_OBJECT_NAME)

    mlflow_tracking_uri: str = MLFLOW_TRACKING_URI
    mlflow_username: str = MLFLOW_TRACKING_USERNAME
    mlflow_password: str = MLFLOW_TRACKING_PASSWORD