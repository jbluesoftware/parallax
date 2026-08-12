from app.core.agent_client import OllamaClient


def test_extract_response_from_chat_payload():
    client = OllamaClient()
    payload = {
        "choices": [
            {
                "message": {"content": "Hello from the model."},
            }
        ]
    }

    assert client._extract_response(payload) == "Hello from the model."


def test_extract_response_falls_back_to_text_field():
    client = OllamaClient()
    payload = {
        "choices": [
            {
                "text": "Simple text output.",
            }
        ]
    }

    assert client._extract_response(payload) == "Simple text output."


def test_extract_response_falls_back_to_result_field():
    client = OllamaClient()
    payload = {"result": "Direct result content."}

    assert client._extract_response(payload) == "Direct result content."
