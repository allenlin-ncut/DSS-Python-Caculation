"""
Ball screw engineering calculation module.

Implements formula-table items BS-001, BS-002, BS-003, with the input
completeness rule of SEL-003 and the comparison rule of SEL-001.

Input keys (input_data)
-----------------------
lead_mm                 p, 導程 (mm/rev)                      [BS-001, BS-002]
target_speed_mm_s       目標線速度 v (mm/s)                    [BS-001] (擇一)
target_rpm              目標轉速 n (rpm)                       [BS-001] (擇一)
max_rpm                 型號允許轉速 (rpm)                      [BS-001]
axial_force_N           軸向力 F (N)                           [BS-002]
efficiency              正向傳動效率 η, 0 < η <= 1              [BS-002]
available_torque_Nm     設計條件下可用驅動扭矩 (N*m)             [BS-002]
dynamic_load_rating_N   動額定負載 Ca (N)                      [BS-003]
equivalent_axial_load_N 等效軸向負載 Fa (N)                    [BS-003]
required_life_rev       設計要求壽命 (rev)                      [BS-003]

Each check returns PASS / FAIL / INSUFFICIENT_DATA.
"""

import math

PASS = "PASS"
FAIL = "FAIL"
INSUFFICIENT = "INSUFFICIENT_DATA"


def _get_positive(data: dict, key: str, errors: list, required_for: str):
    """Return float if key exists and is a finite number > 0, else None.

    Missing key -> None silently (reported by the caller as insufficient).
    Present but invalid -> None and an entry is appended to errors.
    """
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{key}: 必須為數值 ({required_for})")
        return None
    if not math.isfinite(value) or value <= 0:
        errors.append(f"{key}: 必須為大於 0 的有限數值 ({required_for})")
        return None
    return float(value)


def _check(status, required, actual, direction, unit, formula_id, missing=None):
    return {
        "formula_id": formula_id,
        "status": status,
        "required": required,
        "limit": actual,
        "rule": direction,
        "unit": unit,
        "missing_inputs": missing or [],
    }


def calculate_ball_screw(input_data: dict) -> dict:
    """
    Calculate ball screw engineering parameters.

    Parameters
    ----------
    input_data : dict
        Ball screw input parameters (see module docstring).

    Returns
    -------
    dict
        Ball screw calculation result.
    """
    errors: list = []
    calculations: dict = {}
    checks: dict = {}
    data = input_data if isinstance(input_data, dict) else {}
    if not isinstance(input_data, dict):
        errors.append("input_data 必須為 dict")

    p_mm = _get_positive(data, "lead_mm", errors, "BS-001/BS-002")

    # ---- BS-001: 線速度與所需轉速 -------------------------------------
    v = _get_positive(data, "target_speed_mm_s", errors, "BS-001")
    n_target = _get_positive(data, "target_rpm", errors, "BS-001")
    max_rpm = _get_positive(data, "max_rpm", errors, "BS-001")

    n_req = None
    if p_mm is not None:
        if v is not None:
            n_req = 60.0 * v / p_mm          # n = 60v / p
        elif n_target is not None:
            n_req = n_target
            v = n_target * p_mm / 60.0       # v = n*p / 60
    if v is not None:
        calculations["linear_speed_mm_s"] = v
        calculations["linear_speed_m_s"] = v / 1000.0  # 串接 CF-004 用
    if n_req is not None:
        calculations["required_rpm"] = n_req

    missing = []
    if p_mm is None:
        missing.append("lead_mm")
    if v is None and n_target is None:
        missing.append("target_speed_mm_s 或 target_rpm")
    if max_rpm is None:
        missing.append("max_rpm")
    if missing:
        checks["BS-001_speed"] = _check(INSUFFICIENT, n_req, max_rpm,
                                        "required_rpm <= max_rpm", "rpm",
                                        "BS-001", missing)
    else:
        status = PASS if n_req <= max_rpm else FAIL
        checks["BS-001_speed"] = _check(status, n_req, max_rpm,
                                        "required_rpm <= max_rpm", "rpm",
                                        "BS-001")

    # ---- BS-002: 軸向負載所需驅動扭矩 (正向傳動) -----------------------
    F = _get_positive(data, "axial_force_N", errors, "BS-002")
    eta = _get_positive(data, "efficiency", errors, "BS-002")
    if eta is not None and eta > 1:
        errors.append("efficiency: 必須介於 0 與 1 之間 (BS-002)")
        eta = None
    t_avail = _get_positive(data, "available_torque_Nm", errors, "BS-002")

    T_req = None
    if F is not None and p_mm is not None and eta is not None:
        p_m = p_mm / 1000.0                  # 導程換算為 m/rev
        T_req = F * p_m / (2.0 * math.pi * eta)
        calculations["required_drive_torque_Nm"] = T_req

    missing = []
    if F is None:
        missing.append("axial_force_N")
    if p_mm is None:
        missing.append("lead_mm")
    if eta is None:
        missing.append("efficiency")
    if t_avail is None:
        missing.append("available_torque_Nm")
    if missing:
        checks["BS-002_torque"] = _check(INSUFFICIENT, T_req, t_avail,
                                         "T_req <= available_torque", "N*m",
                                         "BS-002", missing)
    else:
        status = PASS if T_req <= t_avail else FAIL
        checks["BS-002_torque"] = _check(status, T_req, t_avail,
                                         "T_req <= available_torque", "N*m",
                                         "BS-002")

    # ---- BS-003: 基本額定壽命 (簡化) ----------------------------------
    Ca = _get_positive(data, "dynamic_load_rating_N", errors, "BS-003")
    Fa = _get_positive(data, "equivalent_axial_load_N", errors, "BS-003")
    L_req = _get_positive(data, "required_life_rev", errors, "BS-003")

    L10 = None
    if Ca is not None and Fa is not None:
        L10 = (Ca / Fa) ** 3 * 1e6           # rev (基準為 10^6 rev)
        calculations["L10_rev"] = L10

    missing = []
    if Ca is None:
        missing.append("dynamic_load_rating_N")
    if Fa is None:
        missing.append("equivalent_axial_load_N")
    if L_req is None:
        missing.append("required_life_rev")
    if missing:
        checks["BS-003_life"] = _check(INSUFFICIENT, L_req, L10,
                                       "L10 >= required_life", "rev",
                                       "BS-003", missing)
    else:
        status = PASS if L10 >= L_req else FAIL
        checks["BS-003_life"] = _check(status, L_req, L10,
                                       "L10 >= required_life", "rev",
                                       "BS-003")

    # ---- 整體判定 (SEL-001 / SEL-003) ---------------------------------
    statuses = [c["status"] for c in checks.values()]
    if FAIL in statuses:
        overall = FAIL
    elif INSUFFICIENT in statuses:
        overall = INSUFFICIENT
    else:
        overall = PASS

    return {
        "component": "ball_screw",
        "inputs": input_data,
        "calculations": calculations,
        "checks": checks,
        "overall": overall,
        "errors": errors,
    }
