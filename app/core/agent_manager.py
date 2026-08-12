import os
import subprocess
import threading
import time
from typing import List

from app.config import OLLAMA_COMMAND


class OllamaServerManager:
    def __init__(self, host: str = "127.0.0.1", port: int = 11434, command: str = OLLAMA_COMMAND):
        self.host = host
        self.port = port
        self.command = command
        self.process = None
        self._lock = threading.Lock()

    def start_server(self, timeout_seconds: int = 20) -> None:
        with self._lock:
            if self.process and self.process.poll() is None:
                return

            env = os.environ.copy()
            env["OLLAMA_HOST"] = f"{self.host}:{self.port}"

            try:
                self.process = subprocess.Popen(
                    [self.command, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=env,
                    text=True,
                )
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "Could not start Ollama. Make sure the 'ollama' binary is installed and available in PATH."
                ) from exc

        self._wait_for_server_ready(timeout_seconds)

    def _wait_for_server_ready(self, timeout_seconds: int) -> None:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if self.process and self.process.poll() is not None:
                raise RuntimeError("Ollama server terminated unexpectedly while starting.")
            try:
                self._run_list_command()
                return
            except RuntimeError as exc:
                if "could not connect" in str(exc).lower():
                    time.sleep(0.5)
                    continue
                raise

        raise RuntimeError("Ollama server did not become ready in time.")

    def stop_server(self) -> None:
        with self._lock:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                finally:
                    self.process = None

    def get_available_models(self) -> List[str]:
        output = self._run_list_command()
        return self._parse_list_output(output)

    def _run_list_command(self) -> str:
        env = os.environ.copy()
        env["OLLAMA_HOST"] = f"{self.host}:{self.port}"

        try:
            return subprocess.check_output(
                [self.command, "list"], stderr=subprocess.STDOUT, text=True, timeout=20, env=env
            )
        except subprocess.CalledProcessError as exc:
            output = exc.output or ""
            if "could not connect" in output.lower() or "run 'ollama serve'" in output.lower():
                raise RuntimeError(output.strip()) from exc
            return output
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Could not run 'ollama list'. Make sure the 'ollama' CLI is installed and available in PATH."
            ) from exc

    @staticmethod
    def _parse_list_output(output: str) -> List[str]:
        models = []
        for line in output.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.lower().startswith("name") or stripped.startswith("-") or stripped.lower().startswith("model"):
                continue
            columns = stripped.split()
            if columns:
                models.append(columns[0])
        return models

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None
