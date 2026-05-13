import os
import tempfile
from faster_whisper import WhisperModel


class WhisperEngine:
    """
    Offline speech-to-text using faster-whisper with a local CPU model.
    No API keys required. All processing is done on-device.
    """

    def __init__(self, model_size: str = "base"):
        """
        Initialize the Whisper model.

        Args:
            model_size: Whisper model size to load. 'base' is recommended
                        for low-resource devices (~150MB, good accuracy).
        """
        print(f"[WhisperEngine] Loading Whisper model '{model_size}' on CPU...")
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )
        print("[WhisperEngine] Model loaded and ready.")

    def transcribe_file(self, audio_path: str) -> str:
        """
        Transcribe an audio file and return the full transcript.

        Args:
            audio_path: Path to the audio file (WAV, MP3, OGG, etc.).

        Returns:
            Full transcript as a single string.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            RuntimeError: If transcription fails.
        """
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                language=None,  # auto-detect language
            )
            transcript_parts = [segment.text for segment in segments]
            return " ".join(transcript_parts).strip()
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}") from e

    def transcribe_bytes(self, audio_bytes: bytes, suffix: str = ".wav") -> str:
        """
        Transcribe raw audio bytes by writing to a temp file.

        Args:
            audio_bytes: Raw audio file contents.
            suffix: File extension for the temp file (e.g. '.wav', '.webm').

        Returns:
            Full transcript as a single string.

        Raises:
            RuntimeError: If transcription fails.
        """
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=suffix, delete=False
            ) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name

            return self.transcribe_file(tmp_path)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
