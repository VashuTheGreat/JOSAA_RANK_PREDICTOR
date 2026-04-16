from dataclasses import dataclass
from typing import Optional

@dataclass
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str

@dataclass
class DataValidationArtifact:
    validation_status:bool
    message:Optional[str]
    validation_report_file_path:str


@dataclass
class DataTransformationArtifact:
    transformed_object_file_path:str
    transformed_train_file_path:str
    transformed_test_file_path:str

# @dataclass
# class RegressionMetricArtifact:
#     r2_score: float
#     mse: float
#     mae: float

@dataclass
class ModelTrainerArtifact:
    trained_model_file_path:str 
    # metric_artifact:RegressionMetricArtifact


# @dataclass
# class RunTrainingArtifact:
#     data_ingestion_artifact:DataIngestionArtifact
#     data_validation_artifact:DataValidationArtifact
#     data_transformed_artifact:DataTransformationArtifact
#     model_trained_artifact:ModelTrainerArtifact
                

@dataclass
class ModelEvaluationArtifact:
    model_evaluation_report_file_path:str
    