
import os
# ----------------- Data Ingestion ------------
PIPELINE_NAME="Ingestion"
ARTIFACT_DIR="artifacts"
HUGGING_FACE_DATA_DOWNLOAD_URL=""
DATA_INGESTION_DIR_NAME="ingestion"
DATA_INGESTION_FEATURE_STORE_DIR="features"
FEATURE_STORE_FILE_NAME="features.csv"
DATA_INGESTION_INGESTED_DIR="train_test"

TRAIN_FILE_NAME="train.csv"
TEST_FILE_NAME="test.csv"

DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO=0.2
# DATA_INGESTION_COLLECTION_NAME



# ------------------------- S3_h ------------------
DATA_SET_URI="VashuTheGreat2/JOSAA_COUNSELLING_DATASET"



# ------------------------- data acess ----------------
DATA_LOADER_CONFIG_FILE_PATH="config/data_loader.yml"


# ------------------------- Feature Engineering ----------------
FEATURE_ENGINEERING_CONFIG_FILE_PATH="config/feature_engineering.yml"



# -------------------------- Data Validation ------------------
BASE_SCHEMA_FOLDER_PATH="config"
DATA_VALIDATION_SCHEMA_NAME="data_validation.yml"
DATA_VALIDATION_DIR_NAME="data_validation"
DATA_VALIDATION_FILE_NAME="data_validation.yml"


# ========================== Data Transformation ========================
DATA_TRANSFORMATION_SCHEMA_NAME="feature_engineering.yml"
DATA_TRANSFORMATION_DIR_NAME="data_transformation"
OBJ_FILE_NAME="obj.pkl"



# ============================== MOdel Traininig ================
MODEL_TRAINER_DIR_NAME="training"
MODEL_TRAINER_TRAINED_MODEL_DIR="model"
MODEL_FILE_NAME="model.pkl"

MODEL_CONFIG_FILE_NAME="model.yml"



# ============================== Model Evaluation ========================
MODEL_EVALUATION_DIR_NAME="evaluation"
MODEL_EVALUATION_REPORT_FILE_NAME="report.yaml"
MODEL_EVALUATION_SCHEMA_NAME="model_evaluation.yml"
MODEL_EVALUATION_PLOTS_DIR_NAME="plots"



# ========================= Prediction ============================
MLFLOW_TRACKING_URI=os.getenv('MLFLOW_TRACKING_URI')
MLFLOW_TRACKING_USERNAME=os.getenv("MLFLOW_TRACKING_USERNAME")
MLFLOW_TRACKING_PASSWORD=os.getenv("MLFLOW_TRACKING_PASSWORD")
MLFLOW_MODEL_URI= os.getenv("MLFLOW_MODEL_URI")
MLFLOW_MODEL_OBJECT_URI = os.getenv("MLFLOW_MODEL_OBJECT_URI")
SAVED_MODEL_DIR_NAME="saved_model"
MODEL_NAME="model.pkl"
SAVED_OBJECT_NAME="obj.pkl"
