# File: agent_langchain.py

import os
import logging
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai import ChatOpenAI
from report_generator import generate_report_for_query  # Make sure this accepts an extra_instructions parameter
from openai import OpenAI  # Using OpenAI for dynamic instruction generation

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_dynamic_instructions(query: str) -> str:
    """
    Uses GPT-4o to generate additional prompt instructions for a given query.
    The instructions should be research-oriented and domain-specific.
    """
    prompt = (
        f"Analyze the following query and generate additional prompt instructions for a detailed, research-oriented report. "
        f"The instructions should focus on the core aspects of the topic, outline key areas of analysis, and specify any domain-specific "
        f"guidelines that would help generate a comprehensive report. Query: '{query}'"
    )
    try:
        # Initialize an OpenAI client using the same API key and project settings
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), project="proj_q0KFYLlNxkE81QCA7dmJjacF")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional data analyst specialized in generating research-oriented report guidelines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        instructions = response.choices[0].message.content.strip()
        logging.info("Dynamic instructions generated: " + instructions)
        return instructions
    except Exception as e:
        logging.error("Error generating dynamic instructions: " + str(e))
        # Fallback: return a generic instruction string
        return (
            "Please provide a detailed analysis focused on the technical and contextual aspects of the query. "
            "Include relevant background information and actionable insights."
        )

def generate_report_tool(query: str) -> str:
    """
    Tool function that wraps our report generation logic.
    It takes a natural language query, dynamically generates additional prompt instructions,
    and returns a comprehensive analysis report.
    """
    logging.info("Generating report for query: " + query)
    
    # Generate extra instructions dynamically using GPT-4o
    extra_instructions = generate_dynamic_instructions(query)
    
    # Call the report generation function with the extra instructions.
    report = generate_report_for_query(query, extra_instructions=extra_instructions)
    return report

# Define the tool for the agent.
tools = [
    Tool(
        name="ReportGenerator",
        func=generate_report_tool,
        description=(
            "Generates a detailed analysis report for a given query by fetching relevant data, "
            "supplementing data if needed, and performing LLM analysis. The tool dynamically enhances the prompt "
            "with query-specific instructions. Input should be a natural language query."
        )
    )
]

def main():
    # Set up the ChatOpenAI model with appropriate API key.
    llm = ChatOpenAI(
        temperature=0.7,
        model_name="gpt-4o",  # You can adjust this model name as needed.
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Initialize the LangChain agent using the ZERO_SHOT_REACT_DESCRIPTION agent type.
    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Get the query from the user (in production this might be provided as a parameter).
    query = input("Enter your query for the agent: ").strip()
    if not query:
        logging.error("No query provided. Exiting.")
        return
    
    # Run the agent with the query.
    response = agent.run(query)
    print("\nAgent Response:\n")
    print(response)

if __name__ == "__main__":
    main()
