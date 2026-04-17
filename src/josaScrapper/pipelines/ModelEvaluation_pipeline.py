import logging
import time

from utils.asyncHandler import asyncHandler
from src.josaScrapper.components.model_evaluation import ModelEvaluationComponent
from src.josaScrapper.entity.config_entity import ModelEvaluationConfig, ModelTrainerConfig
from src.josaScrapper.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelEvaluationArtifact,
    ModelTrainerArtifact,
)




class ModelEvaluationPipeline:
   

    def __init__(
        self,
        model_evaluation_config: ModelEvaluationConfig,
        model_trainer_config: ModelTrainerConfig,
        model_trainer_artifact: ModelTrainerArtifact,
        data_transformation_artifact: DataTransformationArtifact,
    ):
        logging.info("[PIPELINE_INIT] Starting ModelEvaluationPipeline initialization...")
        
        self.model_evaluation_config = model_evaluation_config
        self.model_trainer_config = model_trainer_config
        self.model_trainer_artifact = model_trainer_artifact
        self.data_transformation_artifact = data_transformation_artifact
        
        logging.debug("[PIPELINE_INIT] Configs assigned")
        logging.debug(
            "[PIPELINE_INIT] Artifact paths —\n"
            "  Model path: %s\n"
            "  Test data path: %s\n"
            "  Reports dir: %s\n"
            "  Plots dir: %s",
            self.model_trainer_artifact.trained_model_file_path,
            self.data_transformation_artifact.transformed_test_file_path,
            self.model_evaluation_config.model_evaluation_report_file_path,
            self.model_evaluation_config.model_evaluation_plots_dir,
        )

        logging.debug("[PIPELINE_INIT] Creating ModelEvaluationComponent...")
        self.model_evaluation_component = ModelEvaluationComponent(
            model_trainer_artifact=self.model_trainer_artifact,
            model_evaluation_config=self.model_evaluation_config,
            model_trainer_config=self.model_trainer_config,
            data_transformation_artifact=self.data_transformation_artifact,
        )
        logging.debug("[PIPELINE_INIT] ModelEvaluationComponent created ✓")

        logging.info(
            "[PIPELINE_INIT] ModelEvaluationPipeline initialization COMPLETE ✓\n"
            "  → Report output: %s\n"
            "  → Plots output: %s",
            self.model_evaluation_config.model_evaluation_report_file_path,
            self.model_evaluation_config.model_evaluation_plots_dir,
        )

    @asyncHandler
    async def initiate(self) -> ModelEvaluationArtifact:
        """Execute the complete model evaluation pipeline.
        
        Returns:
            ModelEvaluationArtifact: Contains paths to generated report and plots
        """
        logging.info("\n" + "="*80)
        logging.info("═══════════════════ MODEL EVALUATION PIPELINE START ═══════════════════")
        logging.info("="*80)
        
        pipeline_start = time.time()
        
        try:
            # ─────────── STEP 1: Execute component evaluation ───────────────────────
            logging.info("\n[PIPELINE] Executing ModelEvaluationComponent...")
            component_start = time.time()
            
            logging.debug("[PIPELINE] Calling component.initiate_model_evaluation()")
            model_evaluation_artifact: ModelEvaluationArtifact = (
                await self.model_evaluation_component.initiate_model_evaluation()
            )
            
            component_time = time.time() - component_start
            logging.info("[PIPELINE] Component execution COMPLETE ✓ (%.2f seconds)", component_time)

            # ─────────── STEP 2: Validate and log results ───────────────────────────
            logging.info("\n[PIPELINE] Validating evaluation artifacts...")
            
            # Verify report exists
            import os
            if os.path.exists(model_evaluation_artifact.model_evaluation_report_file_path):
                report_size = os.path.getsize(model_evaluation_artifact.model_evaluation_report_file_path)
                logging.info(
                    "[PIPELINE] ✓ Report artifact verified —\n"
                    "  Path: %s\n"
                    "  Size: %d bytes",
                    model_evaluation_artifact.model_evaluation_report_file_path,
                    report_size,
                )
            else:
                logging.warning(
                    "[PIPELINE] ⚠ Report file not found at: %s",
                    model_evaluation_artifact.model_evaluation_report_file_path,
                )
            
            # Verify plots directory exists and count plots
            if os.path.isdir(model_evaluation_artifact.model_evaluation_plots_dir):
                plot_files = [f for f in os.listdir(model_evaluation_artifact.model_evaluation_plots_dir) if f.endswith('.png')]
                logging.info(
                    "[PIPELINE] ✓ Plots directory verified —\n"
                    "  Path: %s\n"
                    "  Plot files: %d",
                    model_evaluation_artifact.model_evaluation_plots_dir,
                    len(plot_files),
                )
                if plot_files:
                    for idx, plot_file in enumerate(plot_files, 1):
                        logging.debug("[PIPELINE]   ├─ Plot %d: %s", idx, plot_file)
            else:
                logging.warning(
                    "[PIPELINE] ⚠ Plots directory not found at: %s",
                    model_evaluation_artifact.model_evaluation_plots_dir,
                )
            
            # ─────────── STEP 3: Return results ───────────────────────────────────────
            total_time = time.time() - pipeline_start
            logging.info("\n" + "="*80)
            logging.info("═══════════════════ MODEL EVALUATION PIPELINE SUCCESS ═══════════════════")
            logging.info(
                "Pipeline completed successfully!\n"
                "  Total execution time: %.2f seconds\n"
                "  Report location: %s\n"
                "  Plots location: %s",
                total_time,
                model_evaluation_artifact.model_evaluation_report_file_path,
                model_evaluation_artifact.model_evaluation_plots_dir,
            )
            logging.info("="*80 + "\n")

            return model_evaluation_artifact
        
        except Exception as e:
            total_time = time.time() - pipeline_start
            logging.error("\n" + "="*80)
            logging.error("═══════════════════ MODEL EVALUATION PIPELINE FAILED ═══════════════════")
            logging.error(
                "Pipeline execution failed!\n"
                "  Error: %s\n"
                "  Time before failure: %.2f seconds",
                str(e),
                total_time,
            )
            logging.error("="*80 + "\n")
            raise
