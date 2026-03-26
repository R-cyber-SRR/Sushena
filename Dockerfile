# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Cloud Run uses PORT env variable (default 8080)
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run the FastAPI server using the PORT env var
CMD uvicorn app:app --host 0.0.0.0 --port $PORT
