import fastapi
import fastapi

import os

import pandas as pd
import numpy as np

from src.josaScrapper.entity.config_entity import ModelPredictionConfig
from src.josaScrapper.pipelines.ModelPrediction_pipeline import ModelPredictionPipeline
from api.constants import FEATURES_FILE_PATH
import logging
router=fastapi.APIRouter()




from typing import Any

@router.post("/fit_on_year")
async def build_sample_input(year:int=2026,appeared_candidates:int=1415110) -> Any:
    # data = {
    #     "Institute": [
    #         "Indian Institute of Technology Bombay",
    #         "Indian Institute of Technology Delhi",
    #     ],
    #     "Academic Program Name": [
    #         "Computer Science and Engineering (4 Years, Bachelor of Technology)",
    #         "Electrical Engineering (4 Years, Bachelor of Technology)",
    #     ],
    #     "Quota": ["AI", "AI"],
    #     "Seat Type": ["OPEN", "OPEN"],
    #     "Gender": ["Gender-Neutral", "Gender-Neutral"],
    #     "Year": [2023, 2023],
    #     "Round": [6, 6],
    # }

    try:

        data=pd.read_csv(FEATURES_FILE_PATH)
        data.drop(columns=["Opening Rank","Closing Rank"],inplace=True)
        data.drop_duplicates(inplace=True)
        data.dropna(inplace=True)

        data['Year']=np.full((data.shape[0],1),fill_value=year)

        df = data.copy()

        appeared_candidates_map = {
            year:appeared_candidates
        }
        df["appeared_candidates"] = df["Year"].map(appeared_candidates_map)
        df["Branch"] = df["Academic Program Name"].str.split(r" \(").str[0]
        df["Duration"] = pd.to_numeric(
            df["Academic Program Name"].str.extract(r"\((\d+)\s+Years").iloc[:, 0],
            errors="coerce",
        )
        df.reset_index(drop=True, inplace=True)
        config = ModelPredictionConfig()
        pipeline = ModelPredictionPipeline(model_prediction_config=config)
        
        artifact = await pipeline.initiate(df)
        data = pd.DataFrame(artifact.model_predicted,columns=["Opening Rank","Closing Rank"])
        
        df = df.merge(data,left_index=True,right_index=True)
        os.makedirs("api/data",exist_ok=True)
        df.to_csv(f"api/data/predicted_{year}.csv",index=False)
        return {"success":True,"message":f"Predictions for year {year} have been saved to api/data/predicted_{year}.csv"}

    except Exception as e:
        return {"success":False,"message":str(e)}


