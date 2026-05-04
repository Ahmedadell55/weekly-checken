from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from db import get_db

router = APIRouter()

# ==============================
# Schema
# ==============================
class ScoreInput(BaseModel):
    user_id: str
    phq9_score: int
    gad7_score: int
    phq9_severity: str
    gad7_severity: str
    suicidal_flag: bool = False
    emergency: bool = False


# ==============================
# 1️⃣ Save Assessment Result
# ==============================
@router.post("/")
async def save_score(data: ScoreInput):
    db = get_db()
    now = datetime.now(timezone.utc)

    await db.mental_health_scores.insert_one({
        "user_id": data.user_id,
        "phq9_score": data.phq9_score,
        "gad7_score": data.gad7_score,
        "phq9_severity": data.phq9_severity,
        "gad7_severity": data.gad7_severity,
        "suicidal_flag": data.suicidal_flag,
        "emergency": data.emergency,
        "created_at": now,
        "week": now.isocalendar().week,
        "month": now.month,
        "year": now.year
    })

    return {"status": "saved successfully"}

@router.get("/progress/{user_id}")
async def get_progress(user_id: str):
    db = get_db()

    scores = await db.mental_health_scores.find(
        {"user_id": user_id}
    ).sort("created_at", 1).to_list(length=200)

    if not scores:
        raise HTTPException(status_code=404, detail="No data found")

    for s in scores:
        s["_id"] = str(s["_id"])

    return scores


@router.get("/latest/{user_id}")
async def get_latest_analysis(user_id: str):
    db = get_db()

    last = await db.mental_health_scores.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )

    if not last:
        raise HTTPException(status_code=404, detail="No assessment yet")

    last["_id"] = str(last["_id"])
    return last


@router.get("/stats/{user_id}")
async def get_stats(user_id: str):
    db = get_db()

    scores = await db.mental_health_scores.find(
        {"user_id": user_id}
    ).to_list(length=500)

    if not scores:
        raise HTTPException(status_code=404, detail="No data")

    phq_avg = sum(s["phq9_score"] for s in scores) / len(scores)
    gad_avg = sum(s["gad7_score"] for s in scores) / len(scores)

    emergency_count = sum(1 for s in scores if s["emergency"])
    suicide_flags = sum(1 for s in scores if s["suicidal_flag"])

    return {
        "tests_taken": len(scores),
        "avg_phq9": round(phq_avg, 2),
        "avg_gad7": round(gad_avg, 2),
        "emergency_times": emergency_count,
        "suicidal_flags": suicide_flags
    }