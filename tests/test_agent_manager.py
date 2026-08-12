import subprocess

import pytest

from app.core.agent_manager import OllamaServerManager


def test_parse_list_output_handles_header_and_models():
    raw_output = """
Name    Version    Description
---
llama2    1.0    LLaMA 2
mistral    1.0    Mistral model
"""
    parsed = OllamaServerManager._parse_list_output(raw_output)
    assert parsed == ["llama2", "mistral"]


def test_get_available_models_raises_when_command_missing(monkeypatch):
    def fake_check_output(*args, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    manager = OllamaServerManager()
    with pytest.raises(RuntimeError, match="Could not run 'ollama list'"):
        manager.get_available_models()
