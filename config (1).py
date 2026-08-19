"""
Loads settings from environment variables (.env file).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gpt4o_mini")  # gpt4o_mini | mistral
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

    # STT
    STT_MODE = os.getenv("STT_MODE", "api")  # api | local

    # TTS
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")

    @classmethod
    def validate(cls, mode: str = "voice"):
        """Raise a clear error early if required keys are missing."""
        missing = []

        if cls.LLM_PROVIDER == "gpt4o_mini" and not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if cls.LLM_PROVIDER == "mistral" and not cls.MISTRAL_API_KEY:
            missing.append("MISTRAL_API_KEY")
        if cls.STT_MODE == "api" and not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY (needed for Whisper API)")
        if mode in ("voice", "file") and not cls.ELEVENLABS_API_KEY:
            missing.append("ELEVENLABS_API_KEY")

        if missing:
            raise EnvironmentError(
                f"Missing required settings: {', '.join(missing)}. "
                f"Copy .env.example to .env and fill these in."
            )


settings = Settings()
