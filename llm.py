"""
LLM "brain" of the robot.

Takes a natural-language transcript and returns:
  {
    "reply": "<what the robot should say back>",
    "command": { ... structured robot action, or null ... }
  }

Swappable between GPT-4o-mini (OpenAI) and Mistral.
"""
import json
from src.config import settings

SYSTEM_PROMPT = """You are the reasoning core of a voice-controlled robot assistant.

You will receive a transcribed voice command from a human. Respond with ONLY a JSON object
(no markdown fences, no extra text) in this exact shape:

{
  "reply": "<short, natural spoken reply to the human, 1-2 sentences>",
  "command": {
    "action": "<one of: move, stop, turn, grip, release, speak_status, none>",
    "direction": "<forward|backward|left|right, only for move/turn, else omit>",
    "distance_m": <number, only for move, else omit>,
    "angle_deg": <number, only for turn, else omit>,
    "target": "<object name, only for grip, else omit>",
    "then": <optional nested command object for chained actions, else omit>
  }
}

Rules:
- If the human's request doesn't map to a physical action (e.g. small talk, a question),
  set "command": {"action": "none"} and just answer conversationally in "reply".
- Keep "reply" short — it will be spoken out loud by TTS.
- Only use the allowed action values listed above.
- Always return valid JSON and nothing else.
"""


def _parse_llm_json(raw_text: str) -> dict:
    """Strip markdown fences if present and parse JSON safely."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: LLM didn't return clean JSON — treat as plain speech, no robot action
        return {"reply": raw_text.strip(), "command": {"action": "none"}}


def think_gpt4o_mini(transcript: str) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0.4,
    )
    raw = response.choices[0].message.content
    return _parse_llm_json(raw)


def think_mistral(transcript: str) -> dict:
    from mistralai import Mistral

    client = Mistral(api_key=settings.MISTRAL_API_KEY)
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0.4,
    )
    raw = response.choices[0].message.content
    return _parse_llm_json(raw)


def think(transcript: str) -> dict:
    """Run the configured LLM provider and return {reply, command}."""
    if settings.LLM_PROVIDER == "mistral":
        return think_mistral(transcript)
    return think_gpt4o_mini(transcript)
