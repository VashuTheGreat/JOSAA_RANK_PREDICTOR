
import os,sys

sys.path.append(os.getcwd())
from logger import *

import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()


import pandas as pd
import numpy as np

from src.josaScrapper.entity.config_entity import ModelPredictionConfig
from src.josaScrapper.pipelines.ModelPrediction_pipeline import ModelPredictionPipeline



def build_sample_input() -> pd.DataFrame:
    data = {
        "Institute": [
            "Indian Institute of Technology Bombay",
            "Indian Institute of Technology Delhi",
        ],
        "Academic Program Name": [
            "Computer Science and Engineering (4 Years, Bachelor of Technology)",
            "Electrical Engineering (4 Years, Bachelor of Technology)",
        ],
        "Quota": ["AI", "AI"],
        "Seat Type": ["OPEN", "OPEN"],
        "Gender": ["Gender-Neutral", "Gender-Neutral"],
        "Year": [2023, 2023],
        "Round": [6, 6],
    }
    df = pd.DataFrame(data)

    appeared_candidates_map = {
        2016: 1128633, 2017: 1122351, 2018: 1043000, 2019: 1147125,
        2020: 1023000, 2021: 939008,  2022: 905590,  2023: 1113325,
        2024: 1415110, 2025: 1475103,
    }
    df["appeared_candidates"] = df["Year"].map(appeared_candidates_map)
    df["Branch"] = df["Academic Program Name"].str.split(r" \(").str[0]
    df["Duration"] = pd.to_numeric(
        df["Academic Program Name"].str.extract(r"\((\d+)\s+Years").iloc[:, 0],
        errors="coerce",
    )
    return df


async def main():
    logging.info("=" * 60)
    logging.info("  MODEL PREDICTION PIPELINE TEST")
    logging.info("=" * 60)

    # 1. Build config (reads URIs from .env via constants)
    config = ModelPredictionConfig()
    logging.info("ModelPredictionConfig:")
    logging.info("  model_uri       = %s", config.model_uri)
    logging.info("  model_object_uri= %s", config.model_object_uri)
    logging.info("  local_model_path= %s", config.local_model_path)
    logging.info("  local_object_path=%s", config.local_object_path)

    # 2. Build pipeline
    pipeline = ModelPredictionPipeline(model_prediction_config=config)

    # 3. Build sample input
    x = build_sample_input()
    logging.info("Sample input shape: %s", x.shape)
    logging.info("Sample input columns: %s", x.columns.tolist())

    # 4. Run prediction
    artifact = await pipeline.initiate(x)

    logging.info("=" * 60)
    logging.info("PREDICTION RESULTS:")
    logging.info("  Shape: %s", artifact.model_predicted.shape)
    for i, row in enumerate(artifact.model_predicted):
        logging.info("  Sample %d → Opening Rank: %.2f | Closing Rank: %.2f", i + 1, row[0], row[1])
    logging.info("=" * 60)
    logging.info("Test PASSED ✓")

    print("\nPrediction results (raw array):")
    print(artifact.model_predicted)


if __name__ == "__main__":
    asyncio.run(main())
