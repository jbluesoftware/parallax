import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"

if not VENV_PYTHON.exists():
    print("Virtual environment not found at .venv/bin/python")
    print("Create it with: python3 -m venv .venv")
    sys.exit(1)

cmd = [str(VENV_PYTHON), "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
print(f"Starting Parallax app from {BACKEND_DIR}")
print("Open: http://127.0.0.1:8000")
subprocess.run(cmd, cwd=str(BACKEND_DIR), check=True)
