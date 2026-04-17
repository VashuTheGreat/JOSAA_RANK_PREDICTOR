import fastapi
from api.constants import FEATURES_FILE_PATH
import os
import pandas as pd
import numpy as np

router=fastapi.APIRouter()


@router.get("/available_data")
async def available_data():
    try:
        # files = os.listdir(PREDICTED_FILES_FOLDER_PATH)
        data=pd.read_csv(FEATURES_FILE_PATH)
        data = data.replace({np.nan: None})
        data.drop(columns=['Opening Rank','Closing Rank'],inplace=True)
        data.dropna(inplace=True)
        columns=data.columns

        res={}
        for col in columns:
            unique_vals = [v for v in data[col].unique().tolist() if v is not None]
            res[col] = unique_vals
            
        return {"success":True,"data":res}
    except Exception as e:
        return {"success":False,"message":str(e)}


@router.get("/institute_branches")
async def institute_branches():
    """Returns a dict: { "Institute Name": ["Branch A", "Branch B", ...], ... }"""
    try:
        data = pd.read_csv(FEATURES_FILE_PATH)
        data = data.dropna(subset=["Institute", "Academic Program Name"])

        # Derive branch name by stripping the duration suffix e.g. " (4 Years, ...)"
        data["Branch"] = data["Academic Program Name"].str.split(r" \(").str[0]

        mapping = (
            data.groupby("Institute")["Branch"]
            .apply(lambda s: sorted(s.unique().tolist()))
            .to_dict()
        )
        return {"success": True, "data": mapping}
    except Exception as e:
        return {"success": False, "message": str(e)}