# AgenticAI: AI-Powered Data Analysis Tool

## Introduction

**AgenticAI** is an innovative tool that generates detailed, research-backed reports from user queries. Built with a combination of AI models, external APIs, and a PostgreSQL database, it automates data retrieval, summarization, and analysis. Key features include:

- Tag extraction using HuggingFace KeyBERT.
- Dynamic data supplementation via Google and Jina AI.
- Summarization with facebook/bart-large-cnn.
- Report generation powered by GPT-4o.
- Real-time process visibility in a Streamlit app.

Whether you're analyzing stocks or researching trends, AgenticAI delivers actionable insights efficiently.

---

## Process Flow

AgenticAI’s workflow is managed by an intelligent agent built with LangChain. Here’s how it works:

1. **User Submits Query**  
   - The user enters a query in the Streamlit app (e.g., "Analyze the DPZ stock, should I buy it in Feb 2025?").  
   - **Output**: Raw query text.

2. **Agent Orchestrates Processing**  
   - The agent sends the raw query to an LLM to generate domain-specific prompts (extra instructions).  
   - It then oversees the following steps:

     a. **Extract Tags from Query**  
        - Uses a HuggingFace KeyBERT model to identify key tags (e.g., "DPZ," "stock," "investment").  
        - **Output**: List of tags.

     b. **Query Database for Articles**  
        - Searches a PostgreSQL database for articles matching the tags.  
        - **Condition**: If fewer than 7 articles are found (MIN_ARTICLE_THRESHOLD), triggers data supplementation.  
        - **Output**: List of articles or a signal to fetch more data.

     c. **Supplement Data (If Needed)**  
        - Searches Google for relevant results.  
        - Fetches markdown content via Jina AI.  
        - Summarizes content using facebook/bart-large-cnn.  
        - Updates the database with new articles (no duplicates).  
        - **Output**: Updated article list.

     d. **Collate Article Summaries**  
        - Combines summaries into a context string, prefixed with source URLs.  
        - **Output**: Unified context.

     e. **Generate Analysis Report**  
        - Sends context, query, and extra instructions to GPT-4o.  
        - **Report Structure**:  
          - Executive Summary  
          - Detailed Analysis  
          - Supplementary Insights  
          - Conclusion  
        - **Output**: Detailed report text.

3. **Display Report in Streamlit App**  
   - Shows the final report and real-time "thinking" logs in the Streamlit interface.  
   - **Output**: User-friendly report and logs.

The agent ensures data sufficiency and guides the process seamlessly.

---

## Process Flow Diagram

To better understand the workflow, refer to the following diagram:

![Process Flow Diagram](Process_Flow.png)

---

## Dependencies and Requirements

- **Libraries**:  
  - Streamlit  
  - LangChain  
  - HuggingFace Transformers  
  - psycopg2 (PostgreSQL)  
  - KeyBERT  
  - requests  

- **APIs**:  
  - Jina AI  
  - OpenAI (GPT-4o)  

- **Models**:  
  - facebook/bart-large-cnn  
  - KeyBERT  

- **Database**: PostgreSQL  

---

## Database Setup and Schema

Set up a PostgreSQL database with this schema:

- **Table**: `articles`  
  - `id` (serial primary key)  
  - `url` (text, unique)  
  - `summary` (text)  
  - `query` (text)  
  - `tags` (text[])  
  - `retrieval_timestamp` (timestamp)  

- **Indexes**:  
  - GIN index on `tags`  
  - Unique index on `url`  

Run this SQL:
```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    summary TEXT,
    query TEXT,
    tags TEXT[],
    retrieval_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tags ON articles USING GIN (tags);
CREATE UNIQUE INDEX idx_url ON articles (url);
```

## Installation and Setup

### Option 1: Local Setup

1. Clone the Repository

```bash
git clone https://github.com/Captain-Jay29/DataAnalysis_Langchain.git
cd DataAnalysis_Langchain
```

2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Set Environment Variables, Create a ```.env``` file
```text
OPENAI_API_KEY=your_openai_key
JINA_API_KEY=your_jina_key
DATABASE_URL=postgres://$USER:yourpassword@localhost:5432/agentic_analysis
```

4. Run the App
```bash
streamlit run dashboard/app.py
```

### Option 2: Docker Setup

1. Clone the Repository

```bash
git clone https://github.com/Captain-Jay29/DataAnalysis_Langchain.git
cd DataAnalysis_Langchain
```

2. Set Environment Variables, Create a ```.env``` file
```text
OPENAI_API_KEY=your_openai_key
JINA_API_KEY=your_jina_key
POSTGRES_DB=agentic_analysis
POSTGRES_USER=$USER
POSTGRES_PASSWORD=yourpassword
```

3. Build and Run with Docker Compose
```bash
docker-compose up --build
```

4. Access the App
- The app will be available at http://localhost:8501

Note: Docker Compose sets up both the Streamlit app and the PostgreSQL database in separate containers, handling dependencies automatically. Ensure Docker and Docker Compose are installed on your system.

## Configuration
- API Keys: Set in .env.
- Model: Change facebook/bart-large-cnn in code if needed.
- Threshold: Adjust MIN_ARTICLE_THRESHOLD in the script.

## Future Work
- Visualizations and Interactive Graphs:
  - Add charts and graphs using Plotly or D3.js to make reports visually engaging.
  - Enable interactivity (e.g., zoom, hover) for exploring data like stock trends or comparisons.
  - Tailor visuals to query types, enhancing insight delivery.

