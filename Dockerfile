# Use an official Python runtime as base image
FROM python:3.10-slim

# Create a working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the Flask port
EXPOSE 8443

# Run the bot
CMD ["python3", "-m", "polybot.app"]
