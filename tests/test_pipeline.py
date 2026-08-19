"""
Basic unit tests using mocked LLM/TTS/STT calls — no real API keys needed to run these.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.robot_controller import validate_command, execute_command, MockRobot
from src.llm import _parse_llm_json


def test_validate_command_accepts_known_actions():
    assert validate_command({"action": "move", "direction": "forward"}) is True
    assert validate_command({"action": "stop"}) is True
    assert validate_command({"action": "none"}) is True


def test_validate_command_rejects_unknown_actions():
    assert validate_command({"action": "self_destruct"}) is False
    assert validate_command("not a dict") is False
    assert validate_command({}) is False


def test_execute_command_runs_without_error():
    robot = MockRobot()
    execute_command({"action": "move", "direction": "forward", "distance_m": 2}, robot=robot)
    execute_command({"action": "stop"}, robot=robot)
    execute_command(
        {"action": "grip", "target": "red_box", "then": {"action": "move", "direction": "forward"}},
        robot=robot,
    )


def test_parse_llm_json_handles_markdown_fences():
    raw = '```json\n{"reply": "ok", "command": {"action": "stop"}}\n```'
    parsed = _parse_llm_json(raw)
    assert parsed["reply"] == "ok"
    assert parsed["command"]["action"] == "stop"


def test_parse_llm_json_falls_back_on_bad_json():
    raw = "this is not json at all"
    parsed = _parse_llm_json(raw)
    assert parsed["command"]["action"] == "none"
    assert "not json" in parsed["reply"]


if __name__ == "__main__":
    test_validate_command_accepts_known_actions()
    test_validate_command_rejects_unknown_actions()
    test_execute_command_runs_without_error()
    test_parse_llm_json_handles_markdown_fences()
    test_parse_llm_json_falls_back_on_bad_json()
    print("All tests passed.")
