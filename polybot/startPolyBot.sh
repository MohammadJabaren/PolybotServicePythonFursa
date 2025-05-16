#!/bin/bash
set -e

# Function to start ngrok if it's not running
start_ngrok_if_needed() {
    if ! pgrep -f "ngrok http 8443" > /dev/null; then
        echo " Starting ngrok on port 8443..."
        nohup ngrok http 8443 > /dev/null 2>&1 &
        sleep 3
    else
        echo "ngrok is already running."
    fi
}

# Function to get ngrok public URL
fetch_ngrok_url() {
    curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[0].public_url'
}

# Function to update .env with BOT_APP_URL
update_env_file_with_url() {
    local env_file="$1"
    local url="$2"

    if grep -q "^BOT_APP_URL=" "$env_file"; then
        sed -i "s|^BOT_APP_URL=.*|BOT_APP_URL=$url|" "$env_file"
    else
        echo "BOT_APP_URL=$url" >> "$env_file"
    fi

    export BOT_APP_URL="$url"
}

# === Main Script ===
main() {
    local project_path="$1"

    if [ -z "$project_path" ]; then
        echo "Usage: $0 <project_path>"
        exit 1
    fi

    ENV_FILE="$project_path/polybot/.env"
    VENV_PATH="$project_path/.venv"

    echo "Project path: $project_path"

    # Start ngrok
    start_ngrok_if_needed

    # Get ngrok URL
    bot_url=$(fetch_ngrok_url)
    if [ -z "$bot_url" ]; then
        echo "❌ Failed to retrieve ngrok public URL"
        exit 1
    fi
    echo "ngrok URL: $bot_url"

    # Update .env and export URL
    update_env_file_with_url "$ENV_FILE" "$bot_url"

    # Activate venv and run the app
    source "$VENV_PATH/bin/activate"
    echo "Virtual environment activated."

    echo "Launching bot..."
    python -m polybot.app
}

main "$1"
