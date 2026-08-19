"""
Text-to-Speech using ElevenLabs.
"""
from src.config import settings


def speak(text: str, output_path: str = "output.mp3") -> str:
    """
    Convert text to speech via ElevenLabs and save it as an mp3.
    Returns the path to the generated audio file.
    """
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    audio = client.text_to_speech.convert(
        voice_id=settings.ELEVENLABS_VOICE_ID,
        model_id=settings.ELEVENLABS_MODEL_ID,
        text=text,
    )

    with open(output_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)

    return output_path


def play(audio_path: str) -> None:
    """Play an audio file through the default speaker (best-effort, cross-platform)."""
    import platform
    import subprocess

    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["afplay", audio_path], check=False)
        elif system == "Windows":
            os_startfile = __import__("os").startfile
            os_startfile(audio_path)
        else:  # Linux
            subprocess.run(["mpg123", audio_path], check=False)
    except FileNotFoundError:
        print(f"[tts] Could not auto-play. Audio saved at: {audio_path}")
