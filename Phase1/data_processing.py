import spacy
from textblob import TextBlob
import re

def clean_text(text: str) -> str:
    """
    Remove special characters and extra spaces, but replace URLs with their domain names.
    """
    # Replace URLs with the domain name.
    # This regex matches http or https URLs, optionally starting with www, and captures the domain.
    text = re.sub(r'https?://(?:www\.)?([^/\s]+)', r'\1', text)
    
    # In case there are any remaining URLs starting with "www.", remove them or replace as needed.
    text = re.sub(r'www\.(\S+)', r'\1', text)
    
    # Remove any additional special characters, while preserving basic punctuation.
    text = re.sub(r'[^a-zA-Z0-9 .,!?]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_text(text: str):
    """Tokenize text using spaCy NLP model."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [token.text for token in doc]

def get_sentiment(text: str) -> str:
    """Perform sentiment analysis using TextBlob."""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    return "Neutral"

def extract_entities(text: str):
    """Extract named entities using spaCy."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return {ent.text: ent.label_ for ent in doc.ents}

def process_text(text: str) -> dict:
    """Perform full text processing pipeline."""
    cleaned_text = clean_text(text)
    tokens = tokenize_text(cleaned_text)
    sentiment = get_sentiment(cleaned_text)
    entities = extract_entities(cleaned_text)
    
    return {
        "cleaned_text": cleaned_text,
        "tokens": tokens,
        "sentiment": sentiment,
        "entities": entities
    }

# Example Usage
if __name__ == "__main__":
    sample_text = "Apple is planning to launch a new iPhone in California! #TechNews"
    result = process_text(sample_text)
    print(result)
