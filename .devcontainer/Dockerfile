# Use an official Python image as the base
FROM python:3.12

# Install system dependencies for Tesseract
RUN apt-get update && apt-get install -y \
  tesseract-ocr \
  libleptonica-dev \
  libtiff-dev \
  libicu-dev \
  libpango1.0-dev \
  libcairo2-dev \
  && rm -rf /var/lib/apt/lists/*

# Install pip dependencies
COPY requirements.txt /workspaces/requirements.txt

# Set the working directory
WORKDIR /workspaces

# Ensure tesseract is installed correctly
RUN tesseract --version
