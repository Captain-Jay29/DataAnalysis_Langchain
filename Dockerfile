# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files
COPY . /app/

# Expose the port Streamlit uses (default: 8501)
EXPOSE 8501

# Define the command to run the Streamlit app
CMD ["streamlit", "run", "dashboard/app.py", "--server.enableCORS", "false"]