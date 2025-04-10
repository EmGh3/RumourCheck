from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

from text_cleaning import *

MODEL_FILENAME = 'model\\news_model.joblib'
VECTORIZER_FILENAME = 'model\\vectorizer.joblib'

def main():
    # Load the model and vectorizer
    model, vectorizer = load_model()

    # Prepare new text
    new_text = input("insert news: ")
    cleaned_text = clean_text(new_text)

    # Vectorize and predict
    text_vector = vectorizer.transform([cleaned_text])
    pred, fake_conf, true_conf = predict_with_confidence(model, text_vector)

    print(f"Prediction: {'Fake' if pred == 0 else 'True'}")
    print(f"Confidence: {fake_conf}% fake, {true_conf}% true")


def load_model(model_path=MODEL_FILENAME, vectorizer_path=VECTORIZER_FILENAME):
    """Load model and vectorizer from disk"""
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model, vectorizer


def predict_with_confidence(model, text_vector):
    """
    Predict whether news is fake (0) or true (1) with confidence percentages
    Returns: (prediction, confidence_fake%, confidence_true%)
    """
    # Get probabilities
    probabilities = model.predict_proba(text_vector)[0]

    # Convert to percentages
    confidence_fake = round(probabilities[0] * 100, 2)
    confidence_true = round(probabilities[1] * 100, 2)

    # Get final prediction
    prediction = model.predict(text_vector)[0]

    return prediction, confidence_fake, confidence_true

if __name__ == '__main__':
    main()
