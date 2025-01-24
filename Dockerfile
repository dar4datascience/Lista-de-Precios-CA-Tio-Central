# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /workspace

# Install system dependencies required by Tesseract and other packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*


# Copy all files except those specified in .dockerignore
COPY . ./

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable to avoid Python writing pyc files to disk
ENV PYTHONUNBUFFERED=1

# Expose the port (optional, depends on the service you're running)
EXPOSE 80
