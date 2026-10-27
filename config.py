"""
Load the documented, editable rule thresholds from config.json.

Change the numbers in config.json to raise or lower how strict the
checker is. Restart the program after you edit the file.
"""

from __future__ import annotations

import json
from pathlib import Path


# Defaults used when a key is missing from config.json.
DEFAULTS = {
    "min_length": 8,
    "recommended_length": 12,
    "max_length": 128,
    "weak_max_passed_checks": 2,
    "moderate_min_passed_checks": 3,
    "strong_min_passed_checks": 5,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_number": True,
    "require_special": True,
    "use_local_common_list": True,
    "hibp_enabled": True,
    "hibp_timeout_seconds": 10,
    "hibp_user_agent": (
        "PasswordStrengthChecker/1.0 (classroom project; "
        "+https://github.com/alvi83252-dot/Password-Strength-Checker-)"
    ),
    "hibp_api_url": "https://api.pwnedpasswords.com/range/",
}

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config(path=None):
    """Read config.json and fill in any missing keys with defaults."""
    target = Path(path) if path is not None else CONFIG_PATH
    settings = dict(DEFAULTS)

    if target.is_file():
        with target.open(encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, dict):
            raise ValueError("config.json must contain a JSON object.")
        settings.update(loaded)

    _validate(settings)
    return settings


def _validate(settings):
    """Reject values that would make the rules impossible to use."""
    for key in (
        "min_length",
        "recommended_length",
        "max_length",
        "weak_max_passed_checks",
        "moderate_min_passed_checks",
        "strong_min_passed_checks",
        "hibp_timeout_seconds",
    ):
        if not isinstance(settings[key], int) or isinstance(settings[key], bool):
            raise ValueError(key + " must be a whole number.")
        if settings[key] < 0:
            raise ValueError(key + " cannot be negative.")

    if settings["min_length"] < 1:
        raise ValueError("min_length must be at least 1.")
    if settings["max_length"] < settings["min_length"]:
        raise ValueError("max_length must be greater than or equal to min_length.")
    if settings["recommended_length"] < settings["min_length"]:
        raise ValueError(
            "recommended_length must be greater than or equal to min_length."
        )
    if settings["strong_min_passed_checks"] < settings["moderate_min_passed_checks"]:
        raise ValueError(
            "strong_min_passed_checks must be greater than or equal to "
            "moderate_min_passed_checks."
        )
    if settings["moderate_min_passed_checks"] <= settings["weak_max_passed_checks"]:
        raise ValueError(
            "moderate_min_passed_checks must be greater than weak_max_passed_checks."
        )
    if settings["hibp_timeout_seconds"] < 1:
        raise ValueError("hibp_timeout_seconds must be at least 1.")

    for key in (
        "require_uppercase",
        "require_lowercase",
        "require_number",
        "require_special",
        "use_local_common_list",
        "hibp_enabled",
    ):
        if not isinstance(settings[key], bool):
            raise ValueError(key + " must be true or false.")

    if not isinstance(settings["hibp_user_agent"], str) or not settings["hibp_user_agent"].strip():
        raise ValueError("hibp_user_agent must be a non-empty string.")
    if not isinstance(settings["hibp_api_url"], str) or not settings["hibp_api_url"].startswith(
        "https://"
    ):
        raise ValueError("hibp_api_url must be an https URL.")


# Loaded once when the program starts. Tests can call load_config again.
SETTINGS = load_config()
