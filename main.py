from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import logging

from routers import scores   # router بتاع حفظ السكور
from schemas import MentalHealthInput
from mental_model import MentalHealthModel

# ==============================
# Logging
# ==============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# App Init
# ==============================
app = FastAPI(
    title="Mental Health Assessment API",
    description="نظام تقييم الصحة النفسية باستخدام PHQ-9 & GAD-7",
    version="4.0.0",
)

# ==============================
# CORS
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Load Model (Singleton)
# ==============================
model = MentalHealthModel()

# ==============================
# Error Handlers
# ==============================
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Invalid input"},
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

# ==============================
# Health Check
# ==============================
@app.get("/", tags=["General"])
def home():
    return {
        "message": "🧠 Mental Health Assessment API",
        "version": "4.0.0",
        "endpoints": {
            "POST /predict": "تحليل الاستبيان",
            "POST /scores": "حفظ السكور",
            "GET /scores/{user_id}/weekly": "بيانات الجراف",
        },
        "emergency": "🚨 في حالة الطوارئ اتصل 123",
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# ==============================
# Prediction Endpoint
# ==============================
@app.post("/predict", tags=["Assessment"])
def predict(data: MentalHealthInput):
    """
    يحلل الاستبيان ويرجع:
    - score
    - severity
    - alerts
    - emergency flag
    - advice
    """
    try:
        result = model.predict(data)
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

# ==============================
# Include Routers
# ==============================
app.include_router(scores.router, prefix="/scores", tags=["Scores"])

# ==============================
# Run
# ==============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
