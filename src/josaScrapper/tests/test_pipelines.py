
from logger import *

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

# ── ensure project root is on sys.path ──────────────────────────────────────
sys.path.insert(0, os.getcwd())

# ── load .env (MLflow credentials, Kaggle keys, etc.) ────────────────────────
load_dotenv()


from src.josaScrapper.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig,
)
from src.josaScrapper.pipelines.DataIngestion_pipeline import DataIngestionPipeline
from src.josaScrapper.pipelines.DataValidation_pipeline import DataValidationPipeline
from src.josaScrapper.pipelines.DataTransformation_pipeline import DataTransformationPipeline
from src.josaScrapper.pipelines.ModelTraining_pipeline import ModelTrainerPipeline
from src.josaScrapper.pipelines.ModelEvaluation_pipeline import ModelEvaluationPipeline
from src.josaScrapper.entity.artifact_entity import DataValidationArtifact, DataTransformationArtifact


async def main():
    logging.info("=" * 70)
    logging.info("  FULL TRAINING PIPELINE TEST")
    logging.info("=" * 70)

    # ── 1. Data Ingestion ─────────────────────────────────────────────────────
    logging.info("\n[STEP 1] DataIngestion")
    data_ingestion_config = DataIngestionConfig()
    data_ingestion_pipeline = DataIngestionPipeline(data_ingestion_config=data_ingestion_config)
    data_ingestion_artifact = await data_ingestion_pipeline.initiate()
    logging.info("DataIngestionArtifact: %s", data_ingestion_artifact)

    # ── 2. Data Validation ────────────────────────────────────────────────────
    logging.info("\n[STEP 2] DataValidation")
    data_validation_config: DataValidationConfig = DataValidationConfig()
    data_validation_pipeline = DataValidationPipeline(
        data_ingestion_artifact=data_ingestion_artifact,
        data_validation_config=data_validation_config,
    )
    data_validation_artifact: DataValidationArtifact = await data_validation_pipeline.initiate()
    logging.info("DataValidationArtifact: %s", data_validation_artifact)

    # ── 3. Data Transformation ────────────────────────────────────────────────
    logging.info("\n[STEP 3] DataTransformation")
    data_transformation_config: DataTransformationConfig = DataTransformationConfig()
    data_transformation_pipeline = DataTransformationPipeline(
        data_ingestion_artifact=data_ingestion_artifact,
        data_transformation_config=data_transformation_config,
    )
    data_transformation_artifact = await data_transformation_pipeline.initiate()
    logging.info("DataTransformationArtifact: %s", data_transformation_artifact)

    # ── 4. Model Training ─────────────────────────────────────────────────────
    logging.info("\n[STEP 4] ModelTraining")
    model_trainer_config = ModelTrainerConfig()
    model_trainer_pipeline = ModelTrainerPipeline(
        model_trainer_config=model_trainer_config,
        data_transformation_artifact=data_transformation_artifact,
    )
    model_trainer_artifact = await model_trainer_pipeline.initiate()
    logging.info("ModelTrainerArtifact: %s", model_trainer_artifact)

    # ── 5. Model Evaluation ───────────────────────────────────────────────────
    logging.info("\n[STEP 5] ModelEvaluation")
    model_evaluation_config = ModelEvaluationConfig()
    model_evaluation_pipeline = ModelEvaluationPipeline(
        model_evaluation_config=model_evaluation_config,
        model_trainer_config=model_trainer_config,
        model_trainer_artifact=model_trainer_artifact,
        data_transformation_artifact=data_transformation_artifact,
    )
    model_evaluation_artifact = await model_evaluation_pipeline.initiate()
    logging.info("ModelEvaluationArtifact: %s", model_evaluation_artifact)

    logging.info("\n" + "=" * 70)
    logging.info("  FULL TRAINING PIPELINE TEST PASSED ✓")
    logging.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())