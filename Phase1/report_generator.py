# File: report_generator.py

import os
import logging
from typing import List, Dict

# Import our utility functions and data retrieval function
from utilities import extract_tags, query_database_by_tags, append_articles
from get_data_revised import get_data_and_summarize

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
# Define a threshold for minimum number of articles from the DB
MIN_ARTICLE_THRESHOLD = 3

def supplement_data(query: str, num_results: int = 5) -> List[Dict]:
    """
    Supplement data by fetching additional articles using get_data_and_summarize.
    Returns a list of article dictionaries.
    """
    logging.info("Supplementing data using get_data_and_summarize...")
    try:
        results = get_data_and_summarize(query=query, num_results=num_results, output_file=None)
        return results
    except Exception as e:
        logging.error("Error supplementing data: " + str(e))
        return []

def collate_article_summaries(articles: List[Dict]) -> str:
    """
    Collate the summaries of the articles into a single context string.
    Each article's summary is prefixed by its URL for reference.
    """
    collated = ""
    for i, article in enumerate(articles):
        summary = article.get("summary", "")
        url = article.get("url", "Unknown URL")
        if summary:
            collated += f"Article {i+1} (URL: {url}):\n{summary}\n\n"
    return collated

def generate_analysis_report(context: str, query: str) -> str:
    """
    Generate a detailed report using OpenAI's ChatCompletion API.
    The prompt instructs the model to produce a well-formatted report with separate sections:
      1. Executive Summary
      2. Detailed Analysis
      3. Supplementary Insights
      4. Conclusion
    """
    prompt = f"""
You are an expert data analyst. Based on the following information extracted from various articles:
{context}

Generate a comprehensive and well-formatted report addressing the query: "{query}".
Your report should have the following sections:
1. Executive Summary: Provide a brief overview of the main findings.
2. Detailed Analysis: Offer a thorough analysis answering the query.
3. Supplementary Insights: Include additional insights, such as historical trends, contextual factors, or policy implications.
4. Conclusion: Summarize the overall insights.

Ensure that the report is clearly structured with section headers.
"""
    try:
        # Using OpenAI's ChatCompletion via the OpenAI package
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), project="proj_q0KFYLlNxkE81QCA7dmJjacF")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional data analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        report = response.choices[0].message.content.strip()
        return report
    except Exception as e:
        logging.error("Error generating analysis report: " + str(e))
        return "Error generating report."

def generate_report_for_query(query: str) -> str:
    """
    Orchestrates the report generation process:
      1. Extract tags from the query.
      2. Query the database for articles with matching tags.
      3. Supplement data if the number of articles is below a threshold.
         - Append any newly fetched articles to the database.
      4. Collate article summaries.
      5. Generate a detailed analysis report using OpenAI.
    Returns the final report as a string.
    """
    logging.info("Generating report for query: " + query)
    
    # Step 1: Extract tags from the query
    tags = extract_tags(query)
    logging.info("Extracted tags: " + ", ".join(tags))
    
    # Step 2: Query the database for articles matching the tags
    articles_from_db = query_database_by_tags(tags)
    logging.info(f"Found {len(articles_from_db)} articles in the database with matching tags.")
    
    # Step 3: Supplement data if needed
    if len(articles_from_db) < MIN_ARTICLE_THRESHOLD:
        logging.info("Not enough articles in the database. Supplementing data...")
        supplementary_articles = supplement_data(query, num_results=5)
        # Avoid duplicates by filtering out articles with URLs already in the database
        existing_urls = set(article["url"] for article in articles_from_db)
        supplementary_articles = [article for article in supplementary_articles if article["url"] not in existing_urls]
        
        # Ensure each supplemental article has "query" and "tags" set
        for article in supplementary_articles:
            if "query" not in article or not article["query"]:
                article["query"] = query
            if "tags" not in article or not article["tags"]:
                article["tags"] = tags
        
        # Append the new supplemental articles to the database
        if supplementary_articles:
            logging.info("Appending supplemental articles to the database...")
            append_articles(supplementary_articles)
            
        articles = articles_from_db + supplementary_articles
    else:
        articles = articles_from_db
    
    if not articles:
        return "No relevant articles found to generate a report."
    
    # Step 4: Collate the article summaries into context text
    context = collate_article_summaries(articles)
    
    # Step 5: Generate the detailed report using OpenAI
    report = generate_analysis_report(context, query)
    return report

# Optional: Main block for testing
if __name__ == "__main__":
    sample_query = input("Enter your query for report generation: ").strip()
    report = generate_report_for_query(sample_query)
    print("\nGenerated Report:\n")
    print(report)
