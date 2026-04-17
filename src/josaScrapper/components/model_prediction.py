import logging
import os
import pickle
import glob

import mlflow.sklearn
import numpy as np
import pandas as pd

from src.josaScrapper.entity.config_entity import ModelPredictionConfig
from src.josaScrapper.entity.model_downloader import ModelDownloader
from src.josaScrapper.entity.artifact_entity import ModelPredictionArtifact
from utils.asyncHandler import asyncHandler
from utils.main_utils import read_yaml_file_sync


# ── schema path (relative to project root) ─────────────────────────────────
_SCHEMA_PATH = "config/feature_engineering.yml"


def _resolve_pkl(path: str) -> str:
    """MLflow downloads a model as a *directory* (MLmodel, model.pkl, …).
    If `path` is such a directory, return the path to the actual pickle
    file inside it; otherwise return `path` unchanged.
    """
    if os.path.isdir(path):
        candidate = os.path.join(path, "model.pkl")
        if os.path.isfile(candidate):
            logging.info("Resolved MLflow model dir → %s", candidate)
            return candidate
        pkls = glob.glob(os.path.join(path, "**", "*.pkl"), recursive=True)
        if pkls:
            logging.info("Resolved MLflow model dir (fallback) → %s", pkls[0])
            return pkls[0]
    return path


def transform_with_object(
    df: pd.DataFrame,
    obj: dict,      # standarizer_en: {"scalers": {col: StandardScaler}, "encoding_maps": {...}}
    schema: dict,   # parsed feature_engineering.yml
) -> pd.DataFrame:
    """Apply training-time transformations at prediction time.

    obj structure saved by DataTransformationComponent:
      {
        "scalers":       {col: StandardScaler},
        "encoding_maps": {
          col: {"target_map": ..., "freq_map": ..., "global_mean": ..., "type": "hybrid"},
          col: {"target_map": ..., "global_mean": ...,                    "type": "target"},
          col: {"categories": [...],                                       "type": "ohe"},
        }
      }
    """
    df = df.copy()
    enc_maps: dict = obj.get("encoding_maps", {})
    scalers:  dict = obj.get("scalers", {})

    # ── 2. Hybrid encode (Institute, Branch) → col_TargetEnc, col_FreqEnc ──
    for col, info in enc_maps.items():
        if info.get("type") != "hybrid":
            continue
        if col not in df.columns:
            continue
        df[col + "_TargetEnc"] = df[col].map(info["target_map"]).fillna(info["global_mean"])
        df[col + "_FreqEnc"]   = df[col].map(info["freq_map"]).fillna(0)

    # ── 3. Target encode (Seat Type) → col_TargetEnc ──────────────────────
    for col, info in enc_maps.items():
        if info.get("type") != "target":
            continue
        if col not in df.columns:
            continue
        df[col + "_TargetEnc"] = df[col].map(info["target_map"]).fillna(info["global_mean"])

    # ── 4. One-hot encode ─────────────────────────────────────────────────
    for col, info in enc_maps.items():
        if info.get("type") != "ohe":
            continue
        if col not in df.columns:
            continue
        # Use CategoricalDtype to ensure same columns even if some categories are missing
        cat_type = pd.CategoricalDtype(categories=info["categories"])
        s_cat = df[col].astype(cat_type)
        r = pd.get_dummies(s_cat, prefix=col)
        df = df.merge(r, left_index=True, right_index=True)

    # ── 5. Drop raw columns (includes Gender, Quota, Institute, Branch…) ──
    drop_cols = [c for c in schema.get("drop_columns", []) if c in df.columns]
    df = df.drop(columns=drop_cols)

    # ── 6. Log normalise ──────────────────────────────────────────────────
    for col in schema.get("log_normalised_columns", []):
        if col not in df.columns:
            continue
        df[col] = np.log1p(pd.to_numeric(df[col], errors="coerce").fillna(0))

    # ── 7. Standardise using saved StandardScaler objects ─────────────────
    for col, scaler in scalers.items():
        if col not in df.columns:
            logging.warning("Scaler column missing in prediction input (skipping): %s", col)
            continue
        df[col] = scaler.transform(df[[col]])

    # ── Fix bool dtypes (from OHE) ────────────────────────────────────────
    bool_cols = df.select_dtypes(include=["bool"]).columns
    df[bool_cols] = df[bool_cols].astype(int)

    return df


class ModelPredictionComponent:
    """Loads pre-trained model + transformation object from MLflow (or local
    cache) and runs inference on new data.
    """

    def __init__(self, model_prediction_config: ModelPredictionConfig):
        self.config = model_prediction_config

        # Load schema so transform_with_object can use it
        self._schema = read_yaml_file_sync(_SCHEMA_PATH)

        # Downloader for the regression model  (JOSAA/1)
        self._model_downloader = ModelDownloader(
            tracking_uri=self.config.mlflow_tracking_uri,
            model_uri=self.config.model_uri,
            local_path=self.config.local_model_path,
        )

        # Downloader for the transformation object  (JOSAA_OBJECT/1)
        self._object_downloader = ModelDownloader(
            tracking_uri=self.config.mlflow_tracking_uri,
            model_uri=self.config.model_object_uri,
            local_path=self.config.local_object_path,
        )

        logging.info(
            "ModelPredictionComponent initialised — model_uri: %s | object_uri: %s",
            self.config.model_uri,
            self.config.model_object_uri,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _ensure_model(self):
        if not os.path.exists(self.config.local_model_path):
            logging.info("Model not found locally — downloading: %s", self.config.model_uri)
            await self._model_downloader.download_model()
        else:
            logging.info("Using cached model: %s", self.config.local_model_path)

    async def _ensure_object(self):
        if not os.path.exists(self.config.local_object_path):
            logging.info("Object not found locally — downloading: %s", self.config.model_object_uri)
            await self._object_downloader.download_model()
        else:
            logging.info("Using cached object: %s", self.config.local_object_path)

    @staticmethod
    def _load_mlflow_sklearn(path: str):
        """Load an MLflow sklearn artifact from its downloaded directory."""
        # MLflow downloads to a directory; use the directory as model path
        model_dir = path if os.path.isdir(path) else os.path.dirname(path)
        logging.info("Loading MLflow sklearn model from dir: %s", model_dir)
        return mlflow.sklearn.load_model(model_dir)

    # ------------------------------------------------------------------
    # Public entrypoint
    # ------------------------------------------------------------------

    @asyncHandler
    async def initiate_model_prediction(self, x: pd.DataFrame) -> ModelPredictionArtifact:
        """Run end-to-end prediction.

        Args:
            x: Input DataFrame with add_col already applied
               (appeared_candidates, Branch, Duration present).

        Returns:
            ModelPredictionArtifact with model predictions.
        """
        logging.info("━━━ Entered initiate_model_prediction [ModelPredictionComponent] ━━━")

        # 1. Ensure both artefacts are available locally
        await self._ensure_model()
        await self._ensure_object()

        # 2. Load model (MLflow sklearn dir)
        model = self._load_mlflow_sklearn(self.config.local_model_path)
        logging.info("Model loaded — type: %s", type(model).__name__)

        # 3. Load transformation object (standarizer_en)
        obj = self._load_mlflow_sklearn(self.config.local_object_path)
        logging.info(
            "Object loaded — type: %s | top-level keys: %s",
            type(obj).__name__,
            list(obj.keys()) if isinstance(obj, dict) else "N/A",
        )

        # 4. Apply transformation
        logging.info("Applying transformation to input data (shape=%s)", x.shape)
        x_transformed = transform_with_object(x, obj, self._schema)
        logging.info(
            "Transformation complete — shape: %s | cols: %s",
            x_transformed.shape,
            x_transformed.columns.tolist(),
        )

        # 5. Predict
        logging.info("Running model prediction...")
        predictions = model.predict(x_transformed)
        logging.info("Prediction complete — output shape: %s", predictions.shape)

        model_prediction_artifact = ModelPredictionArtifact(model_predicted=predictions)
        logging.info("━━━ Exited initiate_model_prediction [ModelPredictionComponent] ━━━")
        return model_prediction_artifact
