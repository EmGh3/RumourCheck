from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
from text_cleaning import *
from pathlib import Path
import os

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