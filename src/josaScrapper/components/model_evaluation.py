import logging
import os
import pickle

import dagshub
import matplotlib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import seaborn as sns
import yaml
from sklearn.metrics import mean_squared_error, r2_score
from utils.main_utils import load_object
matplotlib.use("Agg")  # Non-interactive backend — safe for server/pipeline runs
import matplotlib.pyplot as plt

from utils.asyncHandler import asyncHandler
from utils.main_utils import read_yaml_file_sync
from src.josaScrapper.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelEvaluationArtifact,
    ModelTrainerArtifact,
)
from src.josaScrapper.entity.config_entity import ModelEvaluationConfig, ModelTrainerConfig





class ModelEvaluationComponent:
    """
    Evaluates the trained multi-output regression model against the held-out test set.

    Steps performed:
      1. Load the serialised model (pickle)
      2. Load transformed test data
      3. Compute per-target metrics  (R², MSE, RMSE)
      4. Save error-distribution and actual-vs-predicted PNGs to artifacts/evaluation/plots/
      5. Persist a YAML evaluation report to artifacts/evaluation/report.yaml
      6. Log everything (params, metrics, model, plots, report) to MLflow via DagsHub
    """

    def __init__(
        self,
        model_trainer_artifact: ModelTrainerArtifact,
        model_evaluation_config: ModelEvaluationConfig,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact,
    ):
        self.model_trainer_artifact = model_trainer_artifact
        self.model_evaluation_config = model_evaluation_config
        self.model_trainer_config = model_trainer_config
        self.data_transformation_artifact = data_transformation_artifact

        # Load YAML schemas once
        self._model_schema = read_yaml_file_sync(self.model_trainer_config.model_config_file_path)
        self._eval_schema = read_yaml_file_sync(self.model_evaluation_config.model_evaluation_schema_path)

        self._targets: list[str] = self._model_schema["y_train"]

        logging.info(
            "ModelEvaluationComponent initialised — targets: %s | model: %s | test data: %s",
            self._targets,
            self.model_trainer_artifact.trained_model_file_path,
            self.data_transformation_artifact.transformed_test_file_path,
        )

    
    # Helper Functions
    def _load_model(self):
        path = self.model_trainer_artifact.trained_model_file_path
        logging.info("Loading trained model from: %s", path)
        with open(path, "rb") as f:
            model = pickle.load(f)
        logging.debug("Model loaded — type: %s", type(model).__name__)
        return model

    def _load_test_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        path = self.data_transformation_artifact.transformed_test_file_path
        logging.info("Loading transformed test data from: %s", path)
        test_df = pd.read_csv(path)
        X_test = test_df.drop(columns=self._targets)
        y_test = test_df[self._targets]
        logging.debug("Test data — X: %s, y: %s", X_test.shape, y_test.shape)
        return X_test, y_test

    def _compute_metrics(
        self,
        model,
        X_test: pd.DataFrame,
        y_test: pd.DataFrame,
    ) -> tuple[dict, np.ndarray]:
        """Returns (metrics_dict, y_pred_array)."""
        logging.info("Computing evaluation metrics for %d targets", len(self._targets))
        y_pred: np.ndarray = model.predict(X_test)

        metrics: dict = {}
        for i, target in enumerate(self._targets):
            r2 = float(r2_score(y_test.iloc[:, i], y_pred[:, i]))
            mse = float(mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
            rmse = float(np.sqrt(mse))
            metrics[target] = {"r2_score": r2, "mse": mse, "rmse": rmse}
            logging.info(
                "  %s → R²=%.4f | MSE=%.4f | RMSE=%.4f",
                target, r2, mse, rmse,
            )
        return metrics, y_pred

    def _save_plots(self, y_test: pd.DataFrame, y_pred: np.ndarray) -> list[str]:
        """
        Generates two PNG plots per target:
          - Error distribution (residuals histogram + KDE)
          - Actual vs Predicted scatter

        Files are saved under model_evaluation_plots_dir and their paths are returned.
        """
        plots_dir = self.model_evaluation_config.model_evaluation_plots_dir
        os.makedirs(plots_dir, exist_ok=True)
        logging.info("Saving evaluation plots to: %s", plots_dir)

        plot_paths: list[str] = []

        for i, target in enumerate(self._targets):
            safe_name = target.replace(" ", "_")
            residuals = y_test.iloc[:, i].values - y_pred[:, i]

            # ── Error distribution ──────────────────────────────────────
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(residuals, kde=True, ax=ax, color="steelblue", edgecolor="white")
            ax.set_title(f"Residual Distribution — {target}", fontsize=14, fontweight="bold")
            ax.set_xlabel("Prediction Error (Actual − Predicted)")
            ax.set_ylabel("Frequency")
            ax.axvline(0, color="red", linestyle="--", linewidth=1, label="Zero error")
            ax.legend()
            err_path = os.path.join(plots_dir, f"error_dist_{safe_name}.png")
            fig.savefig(err_path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            plot_paths.append(err_path)
            logging.info("Saved error distribution plot: %s", err_path)

            # ── Actual vs Predicted scatter ─────────────────────────────
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(
                y_test.iloc[:, i], y_pred[:, i],
                alpha=0.35, color="darkorange", s=8, label="Samples",
            )
            lo = min(y_test.iloc[:, i].min(), y_pred[:, i].min())
            hi = max(y_test.iloc[:, i].max(), y_pred[:, i].max())
            ax.plot([lo, hi], [lo, hi], "k--", linewidth=1.2, label="Perfect prediction")
            ax.set_title(f"Actual vs Predicted — {target}", fontsize=14, fontweight="bold")
            ax.set_xlabel("Actual")
            ax.set_ylabel("Predicted")
            ax.legend()
            scatter_path = os.path.join(plots_dir, f"actual_vs_pred_{safe_name}.png")
            fig.savefig(scatter_path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            plot_paths.append(scatter_path)
            logging.info("Saved actual-vs-predicted plot: %s", scatter_path)

        return plot_paths

    def _save_report_yaml(self, metrics: dict) -> str:
        """Persists evaluation metrics dict as a human-readable YAML file."""
        report_path = self.model_evaluation_config.model_evaluation_report_file_path
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            yaml.dump(metrics, f, default_flow_style=False, sort_keys=False)
        logging.info("Evaluation report (YAML) saved to: %s", report_path)
        return report_path

    

    @asyncHandler
    async def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        logging.info("━━━ Entered initiate_model_evaluation [ModelEvaluationComponent] ━━━")

        # 1. Load artefacts
        model = self._load_model()
        X_test, y_test = self._load_test_data()

        # 2. Compute metrics
        metrics, y_pred = self._compute_metrics(model, X_test, y_test)

        # 3. Save PNGs
        plot_paths = self._save_plots(y_test, y_pred)

        # 4. Save YAML report
        report_path = self._save_report_yaml(metrics)

        # 5. MLflow logging
        logging.info("Starting MLflow run to log params, metrics, model and artifacts")
        with mlflow.start_run():

            # — Model hyper-params from config/model.yml
            for param, val in self._model_schema["model_parameters"].items():
                mlflow.log_param(param, val)
                logging.debug("MLflow param logged — %s: %s", param, val)

            # — Per-target metrics (flat keys, e.g. Opening_Rank_r2_score)
            for target, target_metrics in metrics.items():
                prefix = target.replace(" ", "_")
                for metric_name, metric_val in target_metrics.items():
                    mlflow.log_metric(f"{prefix}_{metric_name}", metric_val)
                    logging.debug("MLflow metric logged — %s_%s: %.4f", prefix, metric_name, metric_val)

            # — Serialised model
            object_data = await load_object(self.data_transformation_artifact.transformed_object_file_path)
            mlflow.sklearn.log_model(model, "model", registered_model_name="JOSAA")
            mlflow.sklearn.log_model(object_data, "object", registered_model_name="JOSAA_OBJECT")
            logging.info("MLflow: sklearn model and transformation object logged")

            # — YAML report as artifact
            mlflow.log_artifact(report_path, artifact_path="reports")
            logging.info("MLflow: evaluation report logged — %s", report_path)

            # — PNG plots as artifacts
            for plot_path in plot_paths:
                mlflow.log_artifact(plot_path, artifact_path="plots")
                logging.info("MLflow: plot logged — %s", plot_path)

        logging.info("━━━ Exited  initiate_model_evaluation [ModelEvaluationComponent] ━━━")

        return ModelEvaluationArtifact(
            model_evaluation_report_file_path=report_path,
            model_evaluation_plots_dir=self.model_evaluation_config.model_evaluation_plots_dir,
        )