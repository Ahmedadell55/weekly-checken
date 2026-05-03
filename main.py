from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import logging

from schemas import MentalHealthInput
from mental_model import MentalHealthModel
from bson import ObjectId
from db import db 

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
    description="نظام تقييم الصحة النفسية باستخدام المعايير العالمية - Rule Based System",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — عدّل الـ origins حسب الـ frontend بتاعك
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "https://your-frontend-domain.com"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================
# Model (Singleton)
# ==============================
model = MentalHealthModel()


# ==============================
# Error Handlers
# ==============================
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Invalid input data"},
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )


# ==============================
# Routes
# ==============================

@app.get("/", tags=["General"])
def home():
    return {
        "message": "🧠 Mental Health Assessment API (Rule-Based System)",
        "version": "3.0.0",
        "methodology": "WHO Standards & International Guidelines (PHQ-9, GAD-7)",
        "features": [
            "PHQ-9 Depression Screening (0-27)",
            "GAD-7 Anxiety Screening (0-21)",
            "Suicide Risk Assessment",
            "Evidence-Based Recommendations",
        ],
        "endpoints": {
            "POST /predict":    "تحليل الحالة النفسية",
            "GET  /guidelines": "المعايير العالمية المستخدمة",
            "GET  /health":     "حالة الـ API",
        },
        "emergency_hotline": "🚨 للطوارئ: 123 أو اذهب لأقرب مستشفى",
    }


@app.get("/health", tags=["General"])
def health_check():
    """التحقق من أن الـ API شغال"""
    return {"status": "ok", "version": "3.0.0"}


@app.post("/predict", tags=["Assessment"])
def predict(data: MentalHealthInput):
    """
    تحليل الحالة النفسية بناءً على:
    - استبيان PHQ-9 للاكتئاب (9 أسئلة، كل سؤال 0-3)
    - استبيان GAD-7 للقلق (7 أسئلة، كل سؤال 0-3)

    **تنبيه:** هذا النظام للمساعدة فقط ولا يُغني عن الطبيب المختص.
    """
    try:
        result = model.predict(data)
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Error processing assessment")


@app.get("/guidelines", tags=["Assessment"])
def get_guidelines():
    """عرض المعايير العالمية المستخدمة في التحليل"""
    return {
        "phq9_cutoffs": {
            "0-4":  "لا يوجد اكتئاب - متابعة روتينية",
            "5-9":  "اكتئاب خفيف - مراقبة ذاتية",
            "10-14": "اكتئاب متوسط - استشارة مختص",
            "15-19": "اكتئاب شديد - تدخل مهني",
            "20-27": "اكتئاب شديد جداً - تدخل فوري",
        },
        "gad7_cutoffs": {
            "0-4":  "لا يوجد قلق - لا حاجة للتدخل",
            "5-9":  "قلق خفيف - تمارين استرخاء",
            "10-14": "قلق متوسط - استشارة مختص",
            "15-21": "قلق شديد - تدخل عاجل",
        },
        "suicide_risk": {
            "PHQ-9 Question 9": {
                "0":   "لا توجد أفكار انتحارية",
                "1":   "خطر متوسط - متابعة فورية",
                "2-3": "خطر عالي - تدخل طارئ",
            }
        },
        "evidence_based": "WHO, APA, NICE guidelines",
        "version": "3.0",
    }

@app.get("/user/{user_id}/progress")
def get_user_progress(user_id: str):

    data = db.mental_health_scores.find(
        {"user_id": user_id}
    ).sort("created_at", 1)

    result = []

    for doc in data:
        result.append({
            "id": str(doc["_id"]),
            "phq9_score": doc["phq9_score"],
            "gad7_score": doc["gad7_score"],
            "created_at": doc["created_at"],
            "week": doc.get("week"),
            "month": doc.get("month"),
            "year": doc.get("year"),
        })

    return result
# ==============================
# Run
# ==============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)