#!/bin/bash
set -e
#Test
# === 1. Fetch parameters from script arguments ===
PROJECT_DIR="$1"
TELEGRAM_TOKEN="$2"
YOLO_IP="$3"
AWS_S3_BUCKET="$4"
DEB_FILE="otelcol_0.127.0_linux_amd64.deb"


#Monitoring
while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do
  echo "Waiting for dpkg lock to be released..."
  sleep 5
done
if ! command -v otelcol &> /dev/null; then
  echo "otelcol not found. Installing..."
  sudo apt-get update
  sudo apt-get -y install wget

  if [ ! -f "$DEB_FILE" ]; then
    wget "https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.127.0/$DEB_FILE"
  else
    echo "$DEB_FILE already exists. Skipping download."
  fi

  sudo dpkg -i "$DEB_FILE"
else
  echo "otelcol is already installed. Skipping installation."
fi



# Check if otelcol service is active
if ! systemctl is-active --quiet otelcol; then
  echo "otelcol service is NOT running."
  exit 1
else
  echo "otelcol service is running."
fi


cd "$PROJECT_DIR"

#Copy the file into etc/otelcol
sudo cp "$PROJECT_DIR/config.yaml" /etc/otelcol/


#restart otelcol
sudo systemctl daemon-reload
sudo systemctl restart otelcol
sudo systemctl enable otelcol
if ! systemctl is-active --quiet otelcol; then
      echo "❌ otelcol is not running Yet."
      sudo systemctl status otelcol --no-pager
      exit 1
fi


# copy the .servcie file
sudo cp polyservice.service /etc/systemd/system/
VENV_DIR="$PROJECT_DIR/.venv"
ENV_FILE="$PROJECT_DIR/polybot/.env"
SERVICE_FILE="polyservice.service"  # change this if your service file has a different name

echo "==> Using project directory: $PROJECT_DIR"

# === 2. Check/create virtual environment ===
if [ -d "$VENV_DIR" ]; then
    echo " Virtual environment exists."
else
    echo " Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# === 3. Activate the virtual environment ===
source "$VENV_DIR/bin/activate"
#Test
pip install --upgrade pip
pip install -r "$PROJECT_DIR/polybot/requirements.txt"
echo " Python requirements installed."

# === 5. Ensure .env file contains correct secrets ===
if [ ! -f "$ENV_FILE" ]; then
    echo ".env file does NOT exist — creating it..."
    touch "$ENV_FILE"
fi
###
set_env_var() {
    KEY="$1"
    VALUE="$2"
    if grep -q "^$KEY=" "$ENV_FILE"; then
        echo " Updating $KEY in .env"
        sed -i "s|^$KEY=.*|$KEY=$VALUE|" "$ENV_FILE"
    else
        echo " Adding $KEY to .env"
        echo "$KEY=$VALUE" >> "$ENV_FILE"
    fi
}

set_env_var "TELEGRAM_BOT_TOKEN" "$TELEGRAM_TOKEN"
set_env_var "YOLO_IP" "$YOLO_IP"
set_env_var "AWS_S3_BUCKET" "$AWS_S3_BUCKET"

echo " .env file is up to date."

# === 6. restart the service ===
if [ -f "$SERVICE_FILE" ]; then
    echo "  Installing systemd service..."
    sudo systemctl daemon-reload
    sudo systemctl restart "$SERVICE_FILE"
    sudo systemctl enable "$SERVICE_FILE"
    echo " Service reloaded and restarted."
    if ! systemctl is-active --quiet polyservice.service; then
      echo "❌ polybot.service is not running Yet."
      sudo systemctl status polyservice.service --no-pager
      exit 1
    fi
fi
#TEst