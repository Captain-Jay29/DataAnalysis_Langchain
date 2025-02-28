# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Git
RUN apt-get update && apt-get install -y git

# Set working directory in the container
WORKDIR /app

# Clone the Git repository
RUN git clone https://github.com/Captain-Jay29/DataAnalysis_Langchain.git .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port Streamlit uses (default: 8501)
EXPOSE 8501

# Define the command to run the Streamlit app
CMD ["streamlit", "run", "dashboard/app.py", "--server.enableCORS", "false"]