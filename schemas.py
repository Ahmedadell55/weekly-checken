from pydantic import BaseModel, Field
from datetime import datetime

# ---------------- PHQ9 ----------------
class PHQ9(BaseModel):
    little_interest: int = Field(ge=0, le=3)
    depressed_mood: int = Field(ge=0, le=3)
    sleep_trouble: int = Field(ge=0, le=3)
    tired: int = Field(ge=0, le=3)
    appetite: int = Field(ge=0, le=3)
    feeling_bad: int = Field(ge=0, le=3)
    concentration: int = Field(ge=0, le=3)
    slow_or_restless: int = Field(ge=0, le=3)
    suicidal_thoughts: bool = False
# ---------------- GAD7 ----------------
class GAD7(BaseModel):
    nervous: int = Field(ge=0, le=3)
    uncontrollable_worry: int = Field(ge=0, le=3)
    excessive_worry: int = Field(ge=0, le=3)
    trouble_relaxing: int = Field(ge=0, le=3)
    restless: int = Field(ge=0, le=3)
    irritable: int = Field(ge=0, le=3)
    fear_awful: int = Field(ge=0, le=3)

# ----------- Final Request ------------
class MentalHealthInput(BaseModel):
    user_id: str
    phq9: PHQ9
    gad7: GAD7
    
    
# ==============================
# Output Schema
# ==============================
 
class MentalHealthOutput(BaseModel):
    phq9_score:        int
    phq9_severity:     str
    gad7_score:        int
    gad7_severity:     str
    alerts:            list[str]
    emergency:         bool
    depression_advice: list[str]
    anxiety_advice:    list[str]
    critical_message: str
    
class MentalHealthRecord(BaseModel):
    user_id: str
    phq9_score: int
    gad7_score: int
    phq9_severity: str
    gad7_severity: str
    created_at: datetime = datetime.utcnow()