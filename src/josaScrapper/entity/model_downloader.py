import logging
import os
import mlflow
from utils.asyncHandler import asyncHandler


class ModelDownloader:
    """Downloads a single MLflow model/artifact to a local path.

    Args:
        tracking_uri: MLflow tracking server URI.
        model_uri:    e.g. ``"models:/JOSAA/1"``
        local_path:   Destination directory on disk.
    """

    def __init__(self, tracking_uri: str, model_uri: str, local_path: str):
        self.tracking_uri = tracking_uri
        self.model_uri = model_uri
        self.local_path = local_path

    @asyncHandler
    async def download_model(self):
        logging.info("Setting MLflow tracking URI: %s", self.tracking_uri)
        mlflow.set_tracking_uri(self.tracking_uri)

        logging.info("Downloading artifact — uri: %s → dst: %s", self.model_uri, self.local_path)
        os.makedirs(self.local_path, exist_ok=True)
        downloaded_path = mlflow.artifacts.download_artifacts(
            artifact_uri=self.model_uri,
            dst_path=self.local_path,
        )
        logging.info("Artifact downloaded to: %s", downloaded_path)
        return downloaded_path