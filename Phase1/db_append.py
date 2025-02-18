# File: db_append.py

import logging
import psycopg2
from psycopg2.extras import execute_values
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database configuration
DB_NAME = "agentic_analysis"
DB_USER = "jay"
DB_HOST = os.getenv("DB_HOST", "localhost")  # Adjust if your DB is on a different host
DB_PORT = os.getenv("DB_PORT", "5432")         # Default PostgreSQL port

def store_articles(articles):
    """
    Insert or update a list of articles in the PostgreSQL database.
    
    Each article should be a dictionary with the following keys:
      - url (str): The URL of the article.
      - summary (str): The summarized content.
      - query (str): The query that resulted in this article.
      - tags (list of str): A list of tags associated with the article.
      
    If an article with the same URL already exists, update its summary, query, and tags.
    """
    conn = None
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        
        insert_query = """
        INSERT INTO articles (url, summary, query, tags)
        VALUES %s
        ON CONFLICT (url) DO UPDATE SET
            summary = EXCLUDED.summary,
            query = EXCLUDED.query,
            tags = EXCLUDED.tags,
            retrieval_timestamp = NOW();
        """
        
        # Prepare data as a list of tuples
        data_tuples = []
        for article in articles:
            url = article.get("url")
            summary = article.get("summary")
            query = article.get("query")
            tags = article.get("tags")  # Should be a list of strings
            data_tuples.append((url, summary, query, tags))
        
        # Bulk insert/update using execute_values for efficiency
        execute_values(cur, insert_query, data_tuples)
        conn.commit()
        logging.info(f"Successfully stored {len(articles)} articles in the database.")
        cur.close()
    except Exception as e:
        logging.error("Error storing articles to the database: %s", str(e))
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Test the function with sample data
    test_articles = [
        {
            "url": "https://example.com/article1",
            "summary": "This is a summary of article 1.",
            "query": "New Tariff rules by Donald Trump",
            "tags": ["Trump", "Tariff"]
        },
        {
            "url": "https://example.com/article2",
            "summary": "This is a summary of article 2.",
            "query": "New Tariff rules by Donald Trump",
            "tags": ["Trump", "Tariff"]
        }
    ]
    store_articles(test_articles)
