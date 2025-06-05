import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

# Constants
TEST_SIZE = 0.2
RANDOM_STATE = 1
MODEL_FILENAME = '../model/news_model.joblib'
VECTORIZER_FILENAME = '../model/vectorizer.joblib'


def main():
    # Load and prepare the data
    fake_news_data = pd.read_csv("../dataset/Fake_combined.csv")
    true_news_data = pd.read_csv("../dataset/True_processed.csv")

    # Add labels (0 for fake, 1 for true)
    fake_news_data["label"] = 0
    true_news_data["label"] = 1

    # Combine datasets
    news_data = pd.concat([fake_news_data, true_news_data])

    # Shuffle the data
    news_data = news_data.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    # Combine title and text for better features
    news_data['full_text'] = news_data['title'] + ' ' + news_data['text']
    news_data['full_text'] = news_data['full_text'].fillna("")
    # Split into training and test sets
    x_train, x_test, y_train, y_test = train_test_split(
        news_data['full_text'],
        news_data['label'],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    # Initialize TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # Fit and transform train set, transform test set
    tfidf_train = tfidf_vectorizer.fit_transform(x_train)
    tfidf_test = tfidf_vectorizer.transform(x_test)

    # Initialize the LogisticRegression classifier
    # supports predict_proba()
    pac = LogisticRegression(max_iter=1000)
    pac.fit(tfidf_train, y_train)

    # Predict on the test set
    y_pred = pac.predict(tfidf_test)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {round(accuracy * 100, 2)}%')

    # Confusion matrix
    confusion_mat = confusion_matrix(y_test, y_pred, labels=[0, 1])
    print('Confusion Matrix:')
    print(confusion_mat)
    # Save model
    save_model(pac, tfidf_vectorizer)


def save_model(model, vectorizer, model_path=MODEL_FILENAME, vectorizer_path=VECTORIZER_FILENAME):
    """Save model and vectorizer to disk"""
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    print(f"Model saved to {model_path}")
    print(f"Vectorizer saved to {vectorizer_path}")


if __name__ == '__main__':
    main()
