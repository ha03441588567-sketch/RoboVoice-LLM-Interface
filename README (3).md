# RoboVoice-LLM-Interface

Multimodal voice agent that lets you **talk to a robot** and get **spoken responses back**.

Built by **AstraVoice AI** — voice-to-text → LLM reasoning → text-to-voice, wrapped around a pluggable robot command layer.

```
🎙️ Mic Input
    │
    ▼
[ Whisper STT ]  → transcribes speech to text
    │
    ▼
[ LLM: Mistral / GPT-4o-mini ]  → interprets intent, decides robot action, drafts reply
    │
    ├──▶ [ Robot Controller ]  → executes structured command (move, grip, stop, etc.)
    │
    ▼
[ ElevenLabs TTS ]  → converts reply text back to speech
    │
    ▼
🔊 Speaker Output
```

## Features

- **Speech-to-Text** via OpenAI Whisper (local model or API)
- **LLM reasoning** — swappable between Mistral (open-source/local) and GPT-4o-mini (API), decides both the natural-language reply AND a structured robot command (JSON)
- **Text-to-Speech** via ElevenLabs for natural, low-latency voice replies
- **Robot Controller abstraction** — plug in your own robot's SDK/serial/ROS2 interface without touching the voice pipeline
- **CLI mode** for testing end-to-end without hardware
- **Command safety layer** — LLM output is validated against an allowed-command schema before it ever reaches the robot

## Project Structure

```
RoboVoice-LLM-Interface/
├── main.py                  # Entry point — runs the full pipeline
├── requirements.txt
├── .env.example              # API keys template
├── src/
│   ├── config.py             # Loads env vars / settings
│   ├── stt.py                 # Whisper speech-to-text
│   ├── llm.py                 # LLM brain (Mistral / GPT-4o-mini)
│   ├── tts.py                  # ElevenLabs text-to-speech
│   ├── robot_controller.py    # Robot command execution (mock + real interface)
│   └── pipeline.py             # Orchestrates STT → LLM → Robot → TTS
├── examples/
│   └── sample_commands.json    # Example voice commands & expected robot actions
└── tests/
    └── test_pipeline.py        # Basic unit tests with mocked APIs
```

## Setup

```bash
git clone <your-repo-url>
cd RoboVoice-LLM-Interface
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in your API keys
```

### Environment Variables (`.env`)

```
OPENAI_API_KEY=sk-...          # for GPT-4o-mini and/or Whisper API
MISTRAL_API_KEY=...            # if using Mistral instead of GPT-4o-mini
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM   # default = "Rachel" voice
LLM_PROVIDER=gpt4o_mini        # or "mistral"
STT_MODE=api                   # "api" (Whisper API) or "local" (openai-whisper package)
```

## Usage

### 1. Text-only test (no mic/speaker needed)

```bash
python main.py --mode text --input "Move forward two meters and then stop"
```

### 2. Full voice pipeline (mic in → speaker out)

```bash
python main.py --mode voice
```

This records from your default mic (press Enter to stop recording), transcribes it, sends it to the LLM, executes the resulting robot command via `robot_controller.py`, and speaks the reply back.

### 3. Process a pre-recorded audio file

```bash
python main.py --mode file --input path/to/command.wav
```

## Connecting a Real Robot

`src/robot_controller.py` ships with a `MockRobot` class that just prints actions. To connect real hardware:

1. Implement a class with the same interface as `MockRobot` (`move`, `stop`, `grip`, `release`, `turn`, `speak_status`)
2. Wire it into your ROS2 node, serial connection, or robot SDK inside each method
3. Swap `MockRobot()` for `YourRobot()` in `pipeline.py`

The LLM only ever outputs a **validated JSON command** (see `ALLOWED_COMMANDS` in `robot_controller.py`) — it never touches hardware directly, so safety validation happens before execution.

## Example Command Flow

**You say:** *"Pick up the red box and bring it to the table"*

**Whisper transcribes:** `"Pick up the red box and bring it to the table"`

**LLM outputs:**
```json
{
  "reply": "Sure, picking up the red box and heading to the table now.",
  "command": {
    "action": "grip",
    "target": "red_box",
    "then": {
      "action": "move",
      "destination": "table"
    }
  }
}
```

**Robot controller** executes the validated command.

**ElevenLabs speaks:** *"Sure, picking up the red box and heading to the table now."*

## Roadmap / Extension Ideas

- Wake-word detection (Porcupine) so it's always listening
- ROS2 integration example (`geometry_msgs/Twist` publisher)
- Multi-turn memory so the robot remembers context across commands
- Streaming TTS for lower response latency
- Web dashboard to monitor command history and robot state

## License

MIT — built by AstraVoice AI.
