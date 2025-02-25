import logging
from get_data_revised import get_data_and_summarize

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    # ----------- Step 1: Get Query Input -----------
    # In production, this query might come as a parameter rather than an interactive prompt.
    user_query = input("Enter your search query: ").strip()
    if not user_query:
        logging.error("No query provided. Exiting.")
        return
    
    logging.info(f"Received query: {user_query}")
    
    # ----------- Step 2: Data Retrieval & Summarization -----------
    logging.info("Starting data retrieval and summarization...")
    # Call our new integrated function. You can adjust num_results as needed.
    try:
        results = get_data_and_summarize(query=user_query, num_results=5, output_file="structured_output.txt")
    except Exception as e:
        logging.error(f"Error during data retrieval and summarization: {e}")
        return
    
    logging.info(f"Retrieved and summarized {len(results)} results.")
    
    # Optionally, iterate over results and log them or pass them to the DB storage module.
    for entry in results:
        logging.info(f"URL: {entry['url']}\nSummary: {entry['summary']}\n")
    
    # ----------- Step 3: Store Data in Database (Future Integration) -----------
    # Here you would call your DB storage function (e.g., store_raw_data(results))
    logging.info("Agent orchestration complete.")

if __name__ == "__main__":
    main()
