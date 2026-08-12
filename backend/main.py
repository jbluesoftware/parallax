import atexit
import json
import os
import subprocess
import time
from contextlib import suppress
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes_ollama import router as ollama_router
from app.config import ALLOWED_ORIGINS, OLLAMA_HOST, OLLAMA_SERVE

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / 'frontend'


class OllamaServeManager:
    def __init__(self):
        self.process = None
        if not self._is_running():
            self.start()

    def _is_running(self) -> bool:
        try:
            response = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=1)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def start(self) -> None:
        self.process = subprocess.Popen(
            OLLAMA_SERVE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if self._is_running():
                return
            time.sleep(0.25)
        raise RuntimeError('Ollama did not start within the expected timeout.')

    def stop(self) -> None:
        if self.process is None:
            return
        with suppress(ProcessLookupError):
            self.process.terminate()
        with suppress(Exception):
            self.process.wait(timeout=5)
        self.process = None


serve_manager = OllamaServeManager()
atexit.register(serve_manager.stop)

app = FastAPI(title='Parallax Ollama Chat')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(ollama_router)


@app.get('/')
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / 'index.html')


@app.get('/static/{filename}')
async def serve_static(filename: str) -> FileResponse:
    file_path = FRONTEND_DIR / 'static' / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail='Static file not found')
    return FileResponse(file_path)


@app.get('/health')
async def health() -> dict:
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000)
