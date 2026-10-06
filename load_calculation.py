"""
Basic load calculations.

Engineering load combination rules will be implemented
according to D1 confirmed engineering rules.
"""

from .validation import validate_positive


def calculate_gravity_force(
    mass_kg: float,
    gravity: float = 9.80665,
) -> float:
    """
    Calculate gravitational force.

    Fg = m * g

    Parameters
    ----------
    mass_kg : float
        Mass in kg.
    gravity : float
        Gravitational acceleration in m/s^2.

    Returns
    -------
    float
        Gravitational force in N.
    """

    validate_positive(mass_kg, "mass_kg")
    validate_positive(gravity, "gravity")

    return mass_kg * gravity


def calculate_inertial_force(
    mass_kg: float,
    acceleration_m_s2: float,
) -> float:
    """
    Calculate inertial force.

    Fa = m * a

    Parameters
    ----------
    mass_kg : float
        Mass in kg.
    acceleration_m_s2 : float
        Acceleration in m/s^2.

    Returns
    -------
    float
        Inertial force in N.
    """

    validate_positive(mass_kg, "mass_kg")
    validate_positive(acceleration_m_s2, "acceleration_m_s2")

    return mass_kg * acceleration_m_s2