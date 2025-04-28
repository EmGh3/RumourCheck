from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import joblib
from text_cleaning import *
from datetime import datetime, timedelta
from pathlib import Path
import os
import random


app = FastAPI()


class NewsRequest(BaseModel):
    text: str


# Get the absolute path to the models directory
current_dir = Path(__file__).parent
MODELS_DIR = current_dir.parent / "model"  # Goes up one level then into models

try:
    # Verify paths exist before loading
    model_path = MODELS_DIR / "news_model.joblib"
    vectorizer_path = MODELS_DIR / "vectorizer.joblib"

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    if not vectorizer_path.exists():
        raise FileNotFoundError(f"Vectorizer file not found at: {vectorizer_path}")

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

except Exception as e:
    raise RuntimeError(f"Failed to load models: {str(e)}")


@app.post("/predict")
async def predict(news: NewsRequest):
    try:
        cleaned_text = clean_text(news.text)
        text_vector = vectorizer.transform([cleaned_text])
        probabilities = model.predict_proba(text_vector)[0]
        return {
            "prediction": bool(model.predict(text_vector)[0]),
            "confidence_fake": float(probabilities[0]),
            "confidence_true": float(probabilities[1])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    



@app.get("/Dashboard/stats")
async def get_dashboard_stats():
    # In a real app, you would query your database
    return {
        "TotalAnalyses": random.randint(50, 200),
        "VerifiedNews": random.randint(30, 150),
        "FakeNewsDetected": random.randint(10, 50)
    }

@app.get("/Dashboard/recent-checks")
async def get_recent_checks():
    # Example mock data - replace with DB queries
    sample_texts = [
        "Le gouvernement annonce de nouvelles mesures économiques",
        "Une nouvelle espèce animale découverte en Amazonie",
        "Vaccins liés à des effets secondaires graves - FAKE",
        "Élections reportées en raison de problèmes techniques"
    ]
    
    return [
        {
            "text": text,
            "is_fake": "FAKE" in text,
            "date": (datetime.now() - timedelta(days=i)).isoformat()
        }
        for i, text in enumerate(sample_texts)
    ]