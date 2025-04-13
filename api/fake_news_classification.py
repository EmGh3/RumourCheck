from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from src.text_cleaning import *

app = FastAPI()


class NewsRequest(BaseModel):
    text: str


# Load models
try:
    model = joblib.load("../model/news_model.joblib")
    vectorizer = joblib.load("../model/vectorizer.joblib")
except Exception as e:
    raise RuntimeError(f"Failed to load models: {str(e)}")


@app.post("/predict")
async def predict(news: NewsRequest):
    cleaned_text = clean_text(news.text)
    text_vector = vectorizer.transform([cleaned_text])
    probabilities = model.predict_proba(text_vector)[0]
    return {
        "prediction": bool(model.predict(text_vector)[0]),
        "confidence_fake": float(probabilities[0]),
        "confidence_true": float(probabilities[1])
    }
