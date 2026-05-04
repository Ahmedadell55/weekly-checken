from schemas import PHQ9, GAD7, MentalHealthInput, MentalHealthOutput
from datetime import datetime, timezone
from db import get_db


# ==========================
# Emergency Contacts
# ==========================
EMERGENCY_CONTACTS = {
    "EG": {
        "hotline": "123",
        "mental_health_support": "16328"
    },
    "INTL": {
        "hotline": "911",
        "mental_health_support": "988"
    }
}


class MentalHealthModel:

    # ==========================
    # PHQ-9 SCORING
    # ==========================
    def score_phq9(self, phq: PHQ9) -> int:
        data = phq.model_dump()

        # ❌ suicidal thoughts NOT part of score
        score = sum(v for k, v in data.items() if k != "suicidal_thoughts")
        return score

    def phq9_severity(self, score: int) -> str:
        if score <= 4:
            return "Minimal"
        elif score <= 9:
            return "Mild"
        elif score <= 14:
            return "Moderate"
        elif score <= 19:
            return "Moderately Severe"
        else:
            return "Severe"

    # ==========================
    # GAD-7 SCORING
    # ==========================
    def score_gad7(self, gad: GAD7) -> int:
        return sum(gad.model_dump().values())

    def gad7_severity(self, score: int) -> str:
        if score <= 4:
            return "Minimal"
        elif score <= 9:
            return "Mild"
        elif score <= 14:
            return "Moderate"
        else:
            return "Severe"

    # ==========================
    # ALERTS
    # ==========================
    def generate_alerts(self, phq: PHQ9, phq_score: int, gad_score: int):
        alerts = []
        emergency = False

        if phq.suicidal_thoughts:
            alerts.append("🚨 Suicide risk detected – Immediate help required")
            emergency = True

        if phq_score >= 20:
            alerts.append("🚨 Severe depression detected")
            emergency = True
        elif phq_score >= 15:
            alerts.append("⚠️ Moderately severe depression detected")

        if gad_score >= 15:
            alerts.append("⚠️ Severe anxiety detected")

        return alerts, emergency

    # ==========================
    # CRITICAL MESSAGE
    # ==========================
    def get_critical_message(self, phq: PHQ9) -> str:
        if phq.suicidal_thoughts:
            return (
                "🚨 IMMEDIATE SUPPORT NEEDED 🚨\n\n"
                "If you are in danger, please seek help immediately.\n\n"
                f"📞 Emergency: {EMERGENCY_CONTACTS['EG']['hotline']}\n"
                f"📞 Mental Health Support: {EMERGENCY_CONTACTS['EG']['mental_health_support']}\n\n"
                "You are not alone. Help is available. Please talk to someone now."
            )

        return "No immediate risk detected. Keep taking care of yourself."

    # ==========================
    # ADVICE ENGINE
    # ==========================
    def depression_advice(self, severity: str) -> list[str]:
        tips = {
            "Minimal": [
                "Maintain healthy sleep (7–9 hours)",
                "Stay physically active",
                "Keep social connections",
                "Practice gratitude"
            ],
            "Mild": [
                "Light daily exercise",
                "Reduce caffeine",
                "Mood journaling",
                "Breathing exercises"
            ],
            "Moderate": [
                "Consider therapy",
                "Structured routine",
                "Mindfulness practice",
                "Set small goals"
            ],
            "Moderately Severe": [
                "Professional therapy (CBT)",
                "Talk to trusted people",
                "Avoid isolation",
                "Monitor symptoms closely"
            ],
            "Severe": [
                "Seek immediate professional help",
                "Do not stay alone",
                "Contact crisis hotline",
                "Consider emergency care"
            ]
        }

        return tips.get(severity, [])

    def anxiety_advice(self, severity: str) -> list[str]:
        tips = {
            "Minimal": ["Deep breathing", "Regular sleep", "Reduce caffeine"],
            "Mild": ["Relaxation techniques", "Identify triggers", "Daily walks"],
            "Moderate": ["CBT techniques", "Exercise", "Stress reduction"],
            "Severe": ["Professional help", "Grounding techniques", "Medical consultation"]
        }

        return tips.get(severity, [])

    # ==========================
    # SAVE TO DATABASE (FOR GRAPHS)
    # ==========================
    async def save_scores(self, user_id, phq_score, gad_score,
                      phq_severity, gad_severity):

      db = get_db()
      now = datetime.now(timezone.utc)
  
      await db.mental_health_scores.insert_one({
          "user_id": user_id,
          "phq9_score": phq_score,
          "gad7_score": gad_score,
          "phq9_severity": phq_severity,
          "gad7_severity": gad_severity,
          "created_at": now,
          "week": now.isocalendar().week,
          "month": now.month,
          "year": now.year
      })
    # ==========================
    # MAIN PREDICT FUNCTION
    # ==========================
    async def predict(self, data: MentalHealthInput):

      phq_score = self.score_phq9(data.phq9)
      gad_score = self.score_gad7(data.gad7)
  
      phq_severity = self.phq9_severity(phq_score)
      gad_severity = self.gad7_severity(gad_score)
  
      alerts, emergency = self.generate_alerts(
          data.phq9, phq_score, gad_score
      )
  
      critical_message = self.get_critical_message(data.phq9)
  
      await self.save_scores(
          data.user_id,
          phq_score,
          gad_score,
          phq_severity,
          gad_severity
      )
  
      return MentalHealthOutput(
          phq9_score=phq_score,
          phq9_severity=phq_severity,
          gad7_score=gad_score,
          gad7_severity=gad_severity,
          alerts=alerts,
          emergency=emergency,
          critical_message=critical_message,
          depression_advice=self.depression_advice(phq_severity),
          anxiety_advice=self.anxiety_advice(gad_severity),
      )
