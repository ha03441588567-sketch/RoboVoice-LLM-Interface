"""
Speech-to-Text using OpenAI Whisper.

Two modes:
  - "api"   : sends audio to OpenAI's hosted Whisper API (fast, no local GPU needed)
  - "local" : runs the open-source `openai-whisper` package on your machine
"""
from src.config import settings


def transcribe_api(audio_path: str) -> str:
    """Transcribe audio using the OpenAI Whisper API."""
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    return transcript.text.strip()


_local_model = None


def transcribe_local(audio_path: str, model_size: str = "base") -> str:
    """Transcribe audio using the local openai-whisper package."""
    global _local_model
    import whisper  # pip install openai-whisper

    if _local_model is None:
        _local_model = whisper.load_model(model_size)

    result = _local_model.transcribe(audio_path)
    return result["text"].strip()


def transcribe(audio_path: str) -> str:
    """Transcribe an audio file to text using the configured STT_MODE."""
    if settings.STT_MODE == "local":
        return transcribe_local(audio_path)
    return transcribe_api(audio_path)
