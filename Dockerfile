# Use the Tesseract OCR base image
FROM franky1/tesseract:latest

# Set the working directory in the container
WORKDIR /workspace

# Install Python runtime (Python 3.9) and pip
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-distutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (make sure to copy your requirements.txt first)
COPY requirements.txt ./
RUN python3.9 -m ensurepip --upgrade \
    && pip3 install --no-cache-dir -r requirements.txt

# Set environment variable to avoid Python writing pyc files to disk
ENV PYTHONUNBUFFERED=1

# Expose the port (optional, depends on your service)
EXPOSE 80

# Copy your application code into the container
COPY . ./

# Commented out: Specify the command to run your application (replace with your actual command)
# CMD ["python3", "your_application.py"]
