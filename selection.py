"""
Unified component selection engine.
"""

from .ball_screw import calculate_ball_screw
from .linear_guide import calculate_linear_guide
from .servo_motor import calculate_servo_motor


def calculate_all(input_data: dict) -> dict:
    """
    Run engineering calculations for all components.

    Engineering selection rules will be implemented
    according to D1 confirmed rules.
    """

    return {
        "ball_screw": calculate_ball_screw(
            input_data.get("ball_screw", {})
        ),
        "linear_guide": calculate_linear_guide(
            input_data.get("linear_guide", {})
        ),
        "servo_motor": calculate_servo_motor(
            input_data.get("servo_motor", {})
        ),
    }