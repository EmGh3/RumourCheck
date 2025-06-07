from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import joblib
from text_cleaning import *
from database import SessionLocal, Prediction
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from starlette.responses import StreamingResponse

# Pydantic model for request body
class NewsRequest(BaseModel):
    text: str
    user_id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()



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
        cleaned_text = clean_text(news.text)
        text_vector = vectorizer.transform([cleaned_text])
        probabilities = model.predict_proba(text_vector)[0]
        prediction = bool(model.predict(text_vector)[0])
        
        db_prediction = Prediction(
            user_id=news.user_id,  # Extract from request body
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




@app.get("/analytics/daily-stats")
async def get_daily_stats(db: Session = Depends(get_db)):
    # Get last 7 days of data
    daily_counts = db.query(
        func.date(Prediction.created_at).label('date'),
        func.count().label('count')
    ).group_by(
        func.date(Prediction.created_at)
    ).order_by(
        func.date(Prediction.created_at).desc()
    ).limit(7).all()
    
    return [
        {"date": date.strftime("%Y-%m-%d"), "count": count} 
        for date, count in daily_counts
    ]

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/analytics/truth-pie-chart/{user_id}")
async def get_analysis_pie_chart(user_id: int, db: Session = Depends(get_db)):
    try:
        # Query counts
        fake_count = db.query(Prediction).filter(Prediction.user_id == user_id, Prediction.is_fake == False).count()  # Swapped
        true_count = db.query(Prediction).filter(Prediction.user_id == user_id, Prediction.is_fake == True).count()   # Swapped
        
        logger.info(f"User {user_id}: Fake count = {fake_count}, True count = {true_count}")
        
        if fake_count == 0 and true_count == 0:
            logger.warning(f"No predictions found for user {user_id}")
            plt.figure(figsize=(8, 8))
            plt.text(0.5, 0.5, 'No Data Available', anchor='center', horizontalalignment='center', verticalalignment='center', fontsize=14)
            plt.title('News Authenticity Distribution\n', fontsize=14, fontweight='bold')
            plt.axis('off')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return StreamingResponse(buffer, media_type="image/png")
        
        plt.figure(figsize=(8, 8))
        plt.pie(
            [fake_count, true_count],
            labels=['Fake News', 'True News'],
            colors=['#e74a3b', '#1cc88a'],  # Red for Fake, Green for True
            autopct='%1.2f%%',
            startangle=90,
            textprops={'fontsize': 12},
            wedgeprops={'edgecolor': 'white', 'linewidth': 1},
            explode=(0.1, 0)
        )
        plt.title('News Authenticity Distribution\n', fontsize=14, fontweight='bold')
        
        centre_circle = plt.Circle((0,0), 0.7, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        logger.error(f"Error generating pie chart for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating pie chart: {str(e)}")