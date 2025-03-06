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
  pandoc \
  curl \
  gdebi-core \
  && rm -rf /var/lib/apt/lists/*

RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
RUN gdebi --non-interactive quarto-linux-amd64.deb

# Install pip dependencies
COPY requirements.txt /workspaces/requirements.txt

# Set the working directory
WORKDIR /workspaces

# INstall dependencies
RUN pip install -r requirements.txt

# Ensure tesseract is installed correctly
RUN tesseract --version
