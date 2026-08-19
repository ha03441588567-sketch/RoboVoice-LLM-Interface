"""
Robot command execution layer.

The LLM never talks to hardware directly. It emits a JSON command, which is
validated here against ALLOWED_COMMANDS before being dispatched to a robot
implementation (MockRobot by default — swap in your own for real hardware).
"""

ALLOWED_ACTIONS = {"move", "stop", "turn", "grip", "release", "speak_status", "none"}


class MockRobot:
    """Prints what it would do — useful for testing without hardware."""

    def move(self, direction: str, distance_m: float = 1.0):
        print(f"[robot] MOVE {direction} for {distance_m}m")

    def stop(self):
        print("[robot] STOP")

    def turn(self, direction: str, angle_deg: float = 90):
        print(f"[robot] TURN {direction} {angle_deg} degrees")

    def grip(self, target: str = "object"):
        print(f"[robot] GRIP '{target}'")

    def release(self):
        print("[robot] RELEASE")

    def speak_status(self, status: str = ""):
        print(f"[robot] STATUS: {status}")


def validate_command(command: dict) -> bool:
    """Return True if the command has a recognized, safe shape."""
    if not isinstance(command, dict):
        return False
    action = command.get("action")
    return action in ALLOWED_ACTIONS


def execute_command(command: dict, robot=None) -> None:
    """
    Validate and execute a single (possibly chained) command against a robot instance.
    Falls back to MockRobot if none is provided.
    """
    if robot is None:
        robot = MockRobot()

    if not validate_command(command):
        print(f"[robot_controller] Rejected invalid/unsafe command: {command}")
        return

    action = command.get("action")

    if action == "move":
        robot.move(command.get("direction", "forward"), command.get("distance_m", 1.0))
    elif action == "stop":
        robot.stop()
    elif action == "turn":
        robot.turn(command.get("direction", "left"), command.get("angle_deg", 90))
    elif action == "grip":
        robot.grip(command.get("target", "object"))
    elif action == "release":
        robot.release()
    elif action == "speak_status":
        robot.speak_status(command.get("status", ""))
    elif action == "none":
        pass  # conversational only, no physical action

    # Handle chained commands, e.g. grip -> then move
    nested = command.get("then")
    if nested:
        execute_command(nested, robot=robot)
