FROM python:3.10-slim

WORKDIR /app

# Upgrade system and install patched libs
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxml2 \
    libicu72 \
    libpam0g \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Use layer caching for dependencies
COPY ./polybot/requirements.txt ./requirements.txt

# Upgrade pip/setuptools to reduce CVEs
RUN pip install --upgrade pip setuptools \
    && pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "polybot.app"]
