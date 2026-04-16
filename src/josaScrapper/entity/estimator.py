import logging
from typing import Any
from lightgbm import LGBMRegressor
from sklearn.multioutput import MultiOutputRegressor
from utils.asyncHandler import asyncHandler
 
class MyModel:
    def __init__(self,schema:Any):
        logging.info("Initializing MyModel with LGBMRegressor")
        logging.debug(f"Model parameters: {schema['model_parameters']}")
        base_model = LGBMRegressor(
            n_estimators=schema['model_parameters']['n_estimators'],
            max_depth=schema['model_parameters']['max_depth'],
            learning_rate=schema['model_parameters']['learning_rate'],
            subsample=schema['model_parameters']['subsample']
        )
        self.model = MultiOutputRegressor(base_model)
        

    @asyncHandler
    async def predict(self,x):
        logging.info("Predicting using MyModel")
        logging.debug(f"Prediction input shape: {x.shape if hasattr(x, 'shape') else 'unknown'}")
        return self.model.predict(x)
    

    @asyncHandler
    async def fit(self,X_train,y_train):
        logging.info("Fitting MyModel on training data")
        self.model.fit(X_train,y_train)
        logging.info("MyModel fitting completed successfully")
        return True
        
    @asyncHandler
    async def load(self,model:Any):
        logging.info("Loading pre-trained model into MyModel")
        self.model=model