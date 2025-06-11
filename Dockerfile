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


# Copy the application code
COPY . .

RUN pip install -r requirements.txt
# Expose the Flask port
EXPOSE 8443

# Run the bot
CMD ["python3", "-m", "polybot.app"]
