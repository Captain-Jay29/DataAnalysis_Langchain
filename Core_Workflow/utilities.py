# File: utilities.py

import re
from typing import List
import os
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values  # For dict-style results and efficient bulk insertion
from keybert import KeyBERT

# -------------------------------
# Function: extract_tags
# -------------------------------
def extract_tags(query: str, top_n: int = 5):
    """
    Extract tags from the input query using KeyBERT.
    Returns a list of keywords (tags).
    """
    kw_model = KeyBERT('all-MiniLM-L6-v2')
    # Use a stricter ngram range to get more focused tags
    keywords = kw_model.extract_keywords(query, keyphrase_ngram_range=(1, 1), stop_words='english', top_n=top_n)
    # Optionally, filter further by setting a score threshold
    threshold = 0.2
    filtered_keywords = [kw for kw, score in keywords if score > threshold]
    return filtered_keywords

# -------------------------------
# Function: check_duplicate_article
# -------------------------------
def check_duplicate_article(url: str) -> bool:
    """
    Check whether an article with the given URL already exists in the PostgreSQL database.
    
    Database details are taken from environment variables or default values:
      - DB_NAME: "agent_analysis" (or "agentic_analysis" as used here)
      - DB_USER: "jay"
      - DB_HOST: defaults to "localhost"
      - DB_PORT: defaults to "5432"
    
    Returns True if a duplicate exists; otherwise, False.
    """
    DB_NAME = os.getenv("DB_NAME", "agentic_analysis")
    DB_USER = os.getenv("DB_USER", "jay")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    conn = None
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM articles WHERE url = %s", (url,))
        result = cur.fetchone()
        cur.close()
        return result is not None
    except Exception as e:
        print(f"Error checking duplicate for URL {url}: {e}")
        return False
    finally:
        if conn:
            conn.close()

# -------------------------------
# Function: query_database_by_tags
# -------------------------------
def query_database_by_tags(query_tags: List[str], min_matches: int = 4) -> List[dict]:
    """
    Query the PostgreSQL database for articles with overlapping tags.
    
    It retrieves articles where the 'tags' column overlaps with the provided list using the PostgreSQL '&&' operator.
    Then, it filters the results to only include articles that have at least `min_matches` matching tags with the query_tags.
    
    Returns a list of dictionaries containing:
        - url
        - summary
        - query
        - tags
        - retrieval_timestamp
    """
    import os
    import psycopg2
    from psycopg2.extras import RealDictCursor

    DB_NAME = os.getenv("DB_NAME", "agentic_analysis")
    DB_USER = os.getenv("DB_USER", "jay")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    conn = None
    results = []
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # First, fetch articles with any overlapping tags using the && operator
        cur.execute("SELECT url, summary, query, tags, retrieval_timestamp FROM articles WHERE tags && %s", (query_tags,))
        rows = cur.fetchall()
        cur.close()
        # Now, filter articles to require at least `min_matches` common tags.
        for row in rows:
            article_tags = set(row.get("tags", []))
            common_tags = article_tags.intersection(query_tags)
            if len(common_tags) >= min_matches:
                results.append(dict(row))
    except Exception as e:
        print(f"Error querying database by tags: {e}")
    finally:
        if conn:
            conn.close()
    return results

# -------------------------------
# Function: append_articles
# -------------------------------
def append_articles(articles: List[dict]) -> None:
    """
    Append new articles to the PostgreSQL database.
    
    Each article should be a dictionary with the following keys:
        - url: str
        - summary: str
        - query: str
        - tags: list of str
    The function inserts articles into the 'articles' table using an "ON CONFLICT DO NOTHING" clause
    to avoid inserting duplicate entries (based on the unique URL).
    """
    DB_NAME = os.getenv("DB_NAME", "agentic_analysis")
    DB_USER = os.getenv("DB_USER", "jay")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    conn = None
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        insert_query = """
            INSERT INTO articles (url, summary, query, tags)
            VALUES %s
            ON CONFLICT (url) DO NOTHING;
        """
        # Prepare the data as a list of tuples
        data_tuples = []
        for article in articles:
            url = article.get("url")
            summary = article.get("summary")
            query_text = article.get("query")
            tags = article.get("tags")
            data_tuples.append((url, summary, query_text, tags))
        
        # Use execute_values for bulk insertion
        execute_values(cur, insert_query, data_tuples)
        conn.commit()
        print(f"Successfully appended {len(articles)} articles to the database.")
        cur.close()
    except Exception as e:
        print(f"Error appending articles: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# -------------------------------
# Optional: Test the functions when run as a script
# -------------------------------
if __name__ == "__main__":
    # Test extract_tags
    sample_query = "What are the new Tariff rules by Donald Trump affecting China and the US?"
    tags = extract_tags(sample_query)
    print(f'Query: {sample_query}\n')
    print("Extracted tags:", tags)
    
    # Test check_duplicate_article
    sample_url = "https://example.com/article1"
    exists = check_duplicate_article(sample_url)
    print(f"Does {sample_url} exist in the DB? {exists}")
    
    # Test query_database_by_tags (will only work if your DB is set up and has data)
    db_results = query_database_by_tags(tags)
    print("Database results:", db_results)
    
    # Test append_articles with sample data
    test_articles = [
        {
            "url": "https://example.com/article3",
            "summary": "This is a summary of article 1.",
            "query": "New Tariff rules by Donald Trump",
            "tags": ["Trump", "Tariff"]
        },
        {
            "url": "https://example.com/article4",
            "summary": "This is a summary of article 2.",
            "query": "New Tariff rules by Donald Trump",
            "tags": ["Trump", "Tariff"]
        }
    ]
    append_articles(test_articles)
