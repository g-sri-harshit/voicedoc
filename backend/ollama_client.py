import requests
import json
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def query_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send a prompt to the local Ollama instance and return the response text.

    Args:
        prompt: The full prompt string to send to the model.
        model: The Ollama model name to use (default: gemma3:4b).

    Returns:
        The model's response as a plain string.

    Raises:
        ConnectionError: If Ollama is not running or unreachable.
        RuntimeError: If the response cannot be parsed.
    """
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Ollama is not running. Please start it with: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(
            "Ollama request timed out after 120 seconds. "
            "The model may be overloaded or the prompt too long."
        )
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Ollama returned HTTP error: {e}")

    try:
        data = response.json()
        return data["response"]
    except (json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(
            f"Failed to parse Ollama response: {e}. "
            f"Raw response: {response.text[:500]}"
        )


def check_ollama_health() -> bool:
    """
    Check whether Ollama is reachable.

    Returns:
        True if Ollama responds, False otherwise.
    """
    try:
        response = requests.get(f"{OLLAMA_HOST}", timeout=5)
        return response.status_code == 200
    except Exception:
        return False
