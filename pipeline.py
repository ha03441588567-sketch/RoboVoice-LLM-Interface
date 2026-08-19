"""
Orchestrates the full loop: STT -> LLM -> Robot Controller -> TTS.
"""
from src import stt, llm, tts
from src.robot_controller import execute_command, MockRobot

robot = MockRobot()  # swap for your real robot implementation


def run_from_text(transcript: str, speak_reply: bool = True) -> dict:
    """Run the LLM -> robot -> (optional) TTS steps starting from raw text."""
    print(f"[you said] {transcript}")

    result = llm.think(transcript)
    reply = result.get("reply", "")
    command = result.get("command", {"action": "none"})

    print(f"[llm reply] {reply}")
    print(f"[llm command] {command}")

    execute_command(command, robot=robot)

    if speak_reply and reply:
        audio_path = tts.speak(reply)
        tts.play(audio_path)

    return result


def run_from_audio_file(audio_path: str, speak_reply: bool = True) -> dict:
    """Run the full STT -> LLM -> robot -> TTS pipeline starting from an audio file."""
    transcript = stt.transcribe(audio_path)
    return run_from_text(transcript, speak_reply=speak_reply)
