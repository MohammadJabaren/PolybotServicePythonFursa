FROM python:3.10-bookworm

WORKDIR /app

# Install only necessary system libraries

# Use layer caching for dependencies
COPY ./polybot/requirements.txt ./requirements.txt

# Upgrade pip and setuptools to fixed versions
RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy the full app
COPY . .

CMD ["python3", "-m", "polybot.app"]
