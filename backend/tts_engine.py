import os
import tempfile
import pyttsx3


def speak_text(text: str) -> None:
    """
    Speak the given text aloud using the system's TTS engine (pyttsx3).
    Blocking call — returns only after speech completes.

    Args:
        text: The text string to speak.

    Raises:
        RuntimeError: If the TTS engine fails to initialize or speak.
    """
    if not text or not text.strip():
        return

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)   # words per minute
        engine.setProperty("volume", 1.0)  # max volume
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        raise RuntimeError(f"TTS speak_text failed: {e}") from e


def text_to_audio_file(text: str, output_path: str) -> None:
    """
    Convert text to speech and save the result as a WAV file.

    Args:
        text: The text string to convert.
        output_path: Full path for the output WAV file.

    Raises:
        RuntimeError: If saving the audio file fails.
    """
    if not text or not text.strip():
        raise ValueError("text must be a non-empty string")

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        raise RuntimeError(f"TTS text_to_audio_file failed: {e}") from e


def text_to_audio_bytes(text: str) -> bytes:
    """
    Convert text to speech and return the WAV file as bytes.
    Uses a temporary file internally.

    Args:
        text: The text to convert.

    Returns:
        WAV audio bytes.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        text_to_audio_file(text, tmp_path)

        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
