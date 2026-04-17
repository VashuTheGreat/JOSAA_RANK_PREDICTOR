import fastapi
import pandas as pd
import numpy as np
from typing import Optional
from api.constants import PREDICTED_FILES_FOLDER_PATH

router = fastapi.APIRouter()


@router.post("/rank_based_recommend")
async def recomment_institutes(
    rank: int = 5000,
    category: str = "OPEN",
    gender: str = "Gender-Neutral",
    quota: str = "AI",
    round: int = 1,
    year: int = 2026
):
    try:
        df = pd.read_csv(f"{PREDICTED_FILES_FOLDER_PATH}/predicted_{year}.csv")
    except FileNotFoundError:
        return {"success": False, "message": f"Data for year {year} not found"}

    df_filtered = df[
        (df["Seat Type"] == category) &
        (df["Gender"] == gender) &
        (df["Quota"] == quota) &
        (df["Round"] == round)
    ]

    result = df_filtered[
        (df_filtered["Opening Rank"] <= rank) &
        (df_filtered["Closing Rank"] >= rank)
    ].copy()

    if len(result) > 0:
        conditions = [
            (rank < result["Closing Rank"] * 0.8),
            (rank < result["Closing Rank"])
        ]
        choices = ["Safe", "Borderline"]
        result["status"] = np.select(conditions, choices, default="Low Chance")
    else:
        result["status"] = []

    # Replace NaNs to avoid FastAPI serialization issues
    result = result.replace({np.nan: None})
    return result.to_dict(orient="records")


@router.post("/cutOffcheck")
async def check_institue_cuttoff(
    category: str = "OBC-NCL",
    gender: str = "Gender-Neutral",
    quota: str = "AI",
    college: Optional[str] = "IIT Bhubaneswar",
    branch: Optional[str] = "Civil Engineering",
    year: int = 2026
):
    try:
        df = pd.read_csv(f"{PREDICTED_FILES_FOLDER_PATH}/predicted_{year}.csv")
    except FileNotFoundError:
        return {"success": False, "message": f"Data for year {year} not found"}

    df_filtered = df[
        (df["Seat Type"] == category) &
        (df["Gender"] == gender) &
        (df["Quota"] == quota)
    ].copy()

    # optional filters
    if college:
        df_filtered = df_filtered[df_filtered["Institute"].str.contains(college, case=False, na=False)]

    if branch:
        df_filtered = df_filtered[df_filtered["Branch"].str.contains(branch, case=False, na=False)]

    df_filtered = df_filtered.replace({np.nan: None})
    return df_filtered.to_dict(orient="records")
