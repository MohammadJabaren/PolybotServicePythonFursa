#!/bin/bash
set -e

# === 1. Fetch parameters from script arguments ===
PROJECT_DIR="$1"
TELEGRAM_TOKEN="$2"
YOLO_IP="$3"

cd "$PROJECT_DIR"

# === 1.5: Ensure correct Git branch is checked out and up to date ===
BRANCH="feature/automation"
echo "==> Fetching latest code from branch: $BRANCH"
git fetch origin
if git show-ref --quiet refs/heads/$BRANCH; then
    echo "==> Branch $BRANCH exists locally. Checking out..."
    git checkout $BRANCH
else
    echo "==> Branch $BRANCH does not exist locally. Creating tracking branch..."
    git checkout -b $BRANCH origin/$BRANCH
fi
git pull origin $BRANCH

# === 2. Variables ===
VENV_DIR="$PROJECT_DIR/.venv"
ENV_FILE="$PROJECT_DIR/polybot/.env"
SERVICE_FILE="polyservice.service"  # change this if your service file has a different name

# === 3. Copy the systemd service file ===
sudo cp "$SERVICE_FILE" /etc/systemd/system/

echo "==> Using project directory: $PROJECT_DIR"

# === 4. Check/create virtual environment ===
if [ -d "$VENV_DIR" ]; then
    echo " Virtual environment exists."
else
    echo " Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# === 5. Activate the virtual environment ===
source "$VENV_DIR/bin/activate"

echo " Python requirements installed."

# === 6. Ensure .env file contains correct secrets ===
if [ ! -f "$ENV_FILE" ]; then
    echo ".env file does NOT exist — creating it..."
    touch "$ENV_FILE"
fi

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

echo " .env file is up to date."

# === 7. Restart the service ===
if [ -f "$SERVICE_FILE" ]; then
    echo " Installing systemd service..."
    sudo systemctl daemon-reload
    sudo systemctl restart "$SERVICE_FILE"
    sudo systemctl enable "$SERVICE_FILE"
    echo " Service reloaded and restarted."

    if ! systemctl is-active --quiet polybot.service; then
        echo "❌ polybot.service is not running."
        sudo systemctl status polybot.service --no-pager
        exit 1
    fi
else
    echo "❌ Service file $SERVICE_FILE not found!"
    exit 1
fi
