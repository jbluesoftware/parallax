from pathlib import Path

OLLAMA_COMMAND = "ollama"
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
APP_TITLE = "Parallax Ollama Chat"
APP_WIDTH = 920
APP_HEIGHT = 720
MODEL_REFRESH_INTERVAL_SECONDS = 120
STATE_STORE_PATH = Path.home() / ".parallax_ollama_chat.json"
