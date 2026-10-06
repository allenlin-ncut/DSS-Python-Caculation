"""
Input validation utilities for the engineering calculation system.
"""


def validate_positive(value: float, name: str) -> float:
    """
    Validate that a value is a positive number.

    Parameters
    ----------
    value : float
        Value to validate.
    name : str
        Name of the parameter.

    Returns
    -------
    float
        Validated value.

    Raises
    ------
    ValueError
        If the value is None or not greater than zero.
    TypeError
        If the value is not a number.
    """

    if value is None:
        raise ValueError(f"{name} cannot be None")

    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")

    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")

    return float(value)


def validate_non_negative(value: float, name: str) -> float:
    """
    Validate that a value is zero or greater.
    """

    if value is None:
        raise ValueError(f"{name} cannot be None")

    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")

    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0")

    return float(value)