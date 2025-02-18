import re
import spacy
from typing import Dict, Optional

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_topic(query: str) -> Optional[str]:
    """
    Extract topic using syntactic patterns and semantic prioritization.
    """
    doc = nlp(query)
    question_words = {"what", "who", "where", "when", "why", "how", "which"}
    platform_keywords = {"twitter", "reddit", "facebook"}
    topic_prepositions = {"about", "regarding", "on", "concerning"}

    # Pattern 1: Look for X in "posts about X" or "discussion regarding X"
    for token in doc:
        if token.text.lower() in topic_prepositions and token.head.pos_ == "NOUN":
            # Get the prepositional phrase complement
            for child in token.children:
                if child.dep_ in ("pobj", "prep"):
                    chunk = doc[child.left_edge.i : child.right_edge.i + 1]
                    if not any(t.ent_type_ in ["GPE", "LOC"] for t in chunk):
                        return chunk.text

    # Pattern 2: Find direct objects of main verbs
    for token in doc:
        if token.dep_ == "dobj" and token.head.pos_ == "VERB":
            chunk = doc[token.left_edge.i : token.right_edge.i + 1]
            if chunk.text.lower() not in platform_keywords:
                return chunk.text

    # Fallback: Filter noun chunks with priority logic
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        
        # Skip unwanted chunks
        if (chunk.root.text.lower() in question_words or
            chunk_text in platform_keywords or
            chunk.root.pos_ == "PRON" or  # Skip pronouns ("me", "it")
            any(t.ent_type_ in ["GPE", "LOC"] for t in chunk)):
            continue
            
        # Prioritize later noun chunks that contain numbers or adjectives
        if any(t.pos_ in ("ADJ", "NUM") for t in chunk):
            return chunk.text

    # Final fallback: First valid noun chunk
    for chunk in doc.noun_chunks:
        if (not any(t.ent_type_ in ["GPE", "LOC"] for t in chunk) and
            chunk.text.lower() not in platform_keywords):
            return chunk.text

    return None

def extract_location(query: str) -> Optional[str]:
    """
    Extract location using improved regex and NLP entity recognition.
    """
    # Improved regex with lookahead for time-related keywords
    pattern = r' in ([A-Za-z, ]+?)(?=\s*(?:over|during|past|last|this|next)\b)'
    location_match = re.search(pattern, query, re.IGNORECASE)
    if location_match:
        return location_match.group(1).strip()
    
    # Fallback to NLP entities
    doc = nlp(query)
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            return ent.text
    return None

def extract_time_range(query: str) -> str:
    """(Unchanged function)"""
    time_keywords = {
        "past 24 hours": "past 24 hours",
        "last day": "past 24 hours",
        "past day": "past 24 hours",
        "last week": "past week",
        "past week": "past week",
        "last month": "past month",
        "past month": "past month",
        "last year": "past year",
        "past year": "past year"
    }
    
    for key in time_keywords:
        if key in query.lower():
            return time_keywords[key]
    return "past 3 days"

def extract_sentiment(query: str) -> Optional[str]:
    """(Unchanged function)"""
    sentiment_keywords = {"positive": "positive", "negative": "negative", "neutral": "neutral"}
    for key, value in sentiment_keywords.items():
        if key in query.lower():
            return value
    return None

def extract_platform(query: str) -> str:
    """(Unchanged function)"""
    platform_keywords = ["Twitter", "Reddit", "Facebook"]
    for keyword in platform_keywords:
        if keyword.lower() in query.lower():
            return keyword
    return "Twitter"

def extract_query_parameters(query: str) -> Dict[str, Optional[str]]:
    """(Unchanged function)"""
    return {
        "topic": extract_topic(query),
        "location": extract_location(query),
        "time_range": extract_time_range(query),
        "sentiment": extract_sentiment(query),
        "platform": extract_platform(query)
    }

# Example usage
if __name__ == "__main__":
    sample_query1 = "What are the top 10 hot topics in Santa Cruz, CA over the past week?"
    sample_query2 = "How is twitter reacting to the new iPhone in New York over the past month?"
    sample_query3 = "Show me the latest posts about climate change on Reddit over the past two years?"

    for i in range(1, 4):
        sample_query = locals()[f"sample_query{i}"]
        extracted_params = extract_query_parameters(sample_query)
        print(f'\nquery: {sample_query}')
        print(f'{extracted_params}\n')

    # extracted_params = extract_query_parameters(sample_query3)
    # print(f'\nquery: {sample_query3}')
    # print(f'{extracted_params}\n')