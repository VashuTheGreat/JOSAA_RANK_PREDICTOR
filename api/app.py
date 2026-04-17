from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes.fit_on_year_route import router as fit_on_year_router
from api.routes.retrain_model import router as retrain_model_router
from api.routes.prediction_route import router as cuttoff_router
from api.routes.available_data import router as available_data_router
from api.routes.view_route import router as view_router

app = FastAPI(
    title="JOSAA Rank Predictor API",
    description="AI-powered JOSAA institute & rank predictor",
    version="1.0.0",
)

# Serve static files
app.mount("/static", StaticFiles(directory="api/static"), name="static")

# Route prefixes
app.include_router(view_router)
app.include_router(fit_on_year_router, prefix="/api/fit_on_year")
app.include_router(retrain_model_router, prefix="/api/retrain_model")
app.include_router(cuttoff_router, prefix="/api/cuttOff")
app.include_router(available_data_router, prefix="/api/available_data")
