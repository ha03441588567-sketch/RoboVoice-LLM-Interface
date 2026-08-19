"""
RoboVoice-LLM-Interface — CLI entry point.

Usage:
    python main.py --mode text  --input "Move forward two meters"
    python main.py --mode file  --input path/to/command.wav
    python main.py --mode voice
"""
import argparse
import os
import sys
import tempfile

from src.config import settings
from src.pipeline import run_from_text, run_from_audio_file


def record_from_mic() -> str:
    """Record audio from the default microphone until Enter is pressed. Returns wav path."""
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    import threading

    samplerate = 16000
    channels = 1
    frames = []
    stop_flag = {"stop": False}

    def callback(indata, frame_count, time_info, status):
        if not stop_flag["stop"]:
            frames.append(indata.copy())

    print("Recording... press Enter to stop.")
    stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback)
    stream.start()
    input()
    stop_flag["stop"] = True
    stream.stop()
    stream.close()

    audio = np.concatenate(frames, axis=0) if frames else np.zeros((1, channels))
    tmp_path = os.path.join(tempfile.gettempdir(), "robovoice_input.wav")
    sf.write(tmp_path, audio, samplerate)
    return tmp_path


def main():
    parser = argparse.ArgumentParser(description="RoboVoice-LLM-Interface")
    parser.add_argument(
        "--mode", choices=["text", "file", "voice"], default="text",
        help="text = type a command | file = process a .wav/.mp3 file | voice = live mic input",
    )
    parser.add_argument("--input", help="Text string (mode=text) or audio file path (mode=file)")
    parser.add_argument("--no-speak", action="store_true", help="Skip TTS playback (text-only output)")
    args = parser.parse_args()

    try:
        settings.validate(mode=args.mode)
    except EnvironmentError as e:
        print(f"[config error] {e}")
        sys.exit(1)

    speak_reply = not args.no_speak

    if args.mode == "text":
        if not args.input:
            print("Provide --input \"your command\" for text mode.")
            sys.exit(1)
        run_from_text(args.input, speak_reply=speak_reply)

    elif args.mode == "file":
        if not args.input:
            print("Provide --input path/to/audio.wav for file mode.")
            sys.exit(1)
        run_from_audio_file(args.input, speak_reply=speak_reply)

    elif args.mode == "voice":
        wav_path = record_from_mic()
        run_from_audio_file(wav_path, speak_reply=speak_reply)


if __name__ == "__main__":
    main()
