import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Download required NLTK data
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def clean_text(text):
    """
    Perform comprehensive text cleaning
    """
    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize text
    tokens = word_tokenize(text)

    # Initialize lemmatizer(reduces words to their base form)
    lemmatizer = WordNetLemmatizer()

    # Remove stopwords and lemmatize
    stop_words = set(stopwords.words('english'))
    cleaned_tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token not in stop_words and len(token) > 2
    ]

    # Join tokens back into string
    cleaned_text = ' '.join(cleaned_tokens)

    return cleaned_text


def apply_text_cleaning(df, text_column='full_text'):
    """
    Apply text cleaning to a pandas DataFrame column
    """
    df['cleaned_text'] = df[text_column].apply(clean_text)
    return df


import csv


def clean_row(row):
    """cleans each row"""
    processed_row = {
        'title': clean_text(row['title']),
        'text': clean_text(row['text']),
        'subject': row['subject'],
        'date': row['date']
    }
    return processed_row


def clean_csv(input_file, output_file, processing_func):
    """
    Process a CSV file and save results to a new file.

    Args:
        input_file (str): Path to input CSV
        output_file (str): Path for output CSV
        processing_func (function): Function to apply to each row
    """
    with open(input_file, mode='r', encoding='utf-8') as infile, \
            open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

        writer.writeheader()

        for row in reader:
            processed_row = processing_func(row)
            writer.writerow(processed_row)

if __name__ == '__main__':
    input_csv = "../dataset/True.csv"
    output_csv = "../dataset/True_processed.csv"
    clean_csv(input_csv, output_csv, clean_row)
    input_csv = "../dataset/Fake.csv"
    output_csv = "../dataset/Fake_processed.csv"
    clean_csv(input_csv, output_csv, clean_row)