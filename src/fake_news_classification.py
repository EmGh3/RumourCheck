from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import joblib
from text_cleaning import *
from datetime import datetime, timedelta
from database import SessionLocal, Prediction
from sqlalchemy.orm import Session
from pathlib import Path
import os
import random

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
async def predict(news: NewsRequest, db: Session = Depends(get_db)):
    try:
        # Your existing prediction logic
        cleaned_text = clean_text(news.text)
        text_vector = vectorizer.transform([cleaned_text])
        probabilities = model.predict_proba(text_vector)[0]
        prediction = bool(model.predict(text_vector)[0])
        
        # Store in database
        db_prediction = Prediction(
            text=news.text,
            is_fake=prediction,
            confidence_fake=float(probabilities[0]),
            confidence_true=float(probabilities[1])
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        return {
            "prediction": prediction,
            "confidence_fake": float(probabilities[0]),
            "confidence_true": float(probabilities[1]),
            "prediction_id": db_prediction.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(Prediction).count()
    fake = db.query(Prediction).filter(Prediction.is_fake == 0).count()
    
    return {
        "total_analyses": total,
        "verified_news": total - fake,
        "fake_news_detected": fake
    }

@app.get("/dashboard/recent-checks")
async def get_recent_checks(db: Session = Depends(get_db)):
    recent = db.query(Prediction)\
              .order_by(Prediction.created_at.desc())\
              .limit(5)\
              .all()
    
    return [
        {
            "text": p.text[:100] + "..." if len(p.text) > 100 else p.text,
            "is_fake": p.is_fake,
            "date": p.created_at.isoformat()
        }
        for p in recent
    ]