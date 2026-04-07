

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
