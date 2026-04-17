import logging

import numpy as np
import pandas as pd

from utils.asyncHandler import asyncHandler
from src.josaScrapper.components.model_prediction import ModelPredictionComponent
from src.josaScrapper.entity.config_entity import ModelPredictionConfig
from src.josaScrapper.entity.artifact_entity import ModelPredictionArtifact


class ModelPredictionPipeline:
    """End-to-end prediction pipeline.

    Downloads the trained model (JOSAA/1) and its transformation object
    (JOSAA_OBJECT/1) from MLflow, applies the stored transformations to
    raw input data, and returns predictions.
    """

    def __init__(self, model_prediction_config: ModelPredictionConfig):
        logging.info("Initialising ModelPredictionPipeline...")
        self.model_prediction_config = model_prediction_config
        self.model_prediction_component = ModelPredictionComponent(
            model_prediction_config=self.model_prediction_config
        )
        logging.info(
            "ModelPredictionPipeline ready — model_uri: %s | object_uri: %s",
            self.model_prediction_config.model_uri,
            self.model_prediction_config.model_object_uri,
        )

    @asyncHandler
    async def initiate(self, x: pd.DataFrame) -> ModelPredictionArtifact:
        """Run prediction pipeline.

        Args:
            x: Raw input DataFrame (pre-transformation).

        Returns:
            ModelPredictionArtifact containing the model's predictions.
        """
        logging.info("━━━ Entered initiate [ModelPredictionPipeline] ━━━")

        model_prediction_artifact: ModelPredictionArtifact = (
            await self.model_prediction_component.initiate_model_prediction(x)
        )

        # Reverse log1p normalisation applied to Opening Rank & Closing Rank
        # during DataTransformationComponent (log_normalised_columns)
        raw_preds = model_prediction_artifact.model_predicted
        actual_preds = np.expm1(raw_preds)
        logging.info(
            "Antilog applied — log-scale predictions converted to actual ranks | shape: %s",
            actual_preds.shape,
        )

        model_prediction_artifact = ModelPredictionArtifact(model_predicted=actual_preds)

        logging.info(
            "ModelPredictionPipeline completed — predicted shape: %s",
            actual_preds.shape,
        )
        logging.info("━━━ Exited initiate [ModelPredictionPipeline] ━━━")

        return model_prediction_artifact
