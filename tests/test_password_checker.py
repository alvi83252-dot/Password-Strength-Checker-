"""Tests for strength rules, HIBP parsing, the menu, and web parity."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import config as config_module  # noqa: E402
import hibp  # noqa: E402
import password_checker  # noqa: E402


RESULT_FIELDS = (
    "ok",
    "error",
    "rating",
    "score",
    "length",
    "checks",
    "is_common",
    "summary",
    "details",
    "suggestions",
    "habits",
)


def offline_result(password, settings=None):
    """Rate a password without calling Have I Been Pwned."""
    return password_checker.evaluate_password(
        password,
        settings=settings,
        check_breaches=False,
    )


class RatingTests(unittest.TestCase):
    """Weak / Moderate / Strong detection from the documented rule set."""

    def test_short_password_is_weak_even_with_many_character_types(self):
        result = offline_result("Ab1!")
        self.assertTrue(result["ok"])
        self.assertEqual(result["rating"], "Weak")
        self.assertEqual(result["score"], 4)
        self.assertFalse(result["checks"]["length"])
        self.assertIn("shorter than", result["summary"])

    def test_length_and_lowercase_only_is_weak(self):
        result = offline_result("sunshine")
        self.assertEqual(result["rating"], "Weak")
        self.assertEqual(result["score"], 2)

    def test_three_checks_is_moderate(self):
        result = offline_result("HelloWorld")
        self.assertEqual(result["rating"], "Moderate")
        self.assertEqual(result["score"], 3)

    def test_four_checks_is_moderate(self):
        result = offline_result("BlueHorse1")
        self.assertEqual(result["rating"], "Moderate")
        self.assertEqual(result["score"], 4)
        self.assertFalse(result["checks"]["special"])
        self.assertIn(
            "Add at least one special character, such as ! ? # or @.",
            result["suggestions"],
        )

    def test_all_five_checks_is_strong_offline(self):
        result = offline_result("Nimbus#Trail82")
        self.assertEqual(result["rating"], "Strong")
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["suggestions"], [])
        self.assertEqual(len(result["habits"]), 3)

    def test_common_password_is_weak_even_when_it_looks_complex(self):
        result = offline_result("Password1!")
        self.assertEqual(result["score"], 5)
        self.assertTrue(result["is_common"])
        self.assertEqual(result["rating"], "Weak")

    def test_space_does_not_count_as_a_special_character(self):
        result = offline_result("Blue Horse")
        self.assertTrue(result["ok"])
        self.assertFalse(result["checks"]["special"])
        self.assertEqual(result["rating"], "Moderate")


class ConfigurableThresholdTests(unittest.TestCase):
    """Thresholds come from config.json and can be overridden in tests."""

    def test_raising_min_length_turns_an_eight_character_password_weak(self):
        settings = dict(config_module.DEFAULTS)
        settings["min_length"] = 12
        settings["recommended_length"] = 16
        result = offline_result("BlueHorse1", settings=settings)
        self.assertFalse(result["checks"]["length"])
        self.assertEqual(result["rating"], "Weak")
        self.assertIn("At least 12 are required.", result["details"][0]["text"])

    def test_config_file_loads_documented_defaults(self):
        settings = config_module.load_config(ROOT / "config.json")
        self.assertEqual(settings["min_length"], 8)
        self.assertEqual(settings["moderate_min_passed_checks"], 3)
        self.assertEqual(settings["strong_min_passed_checks"], 5)
        self.assertTrue(settings["hibp_enabled"])


class InvalidInputTests(unittest.TestCase):
    """Bad input is explained and never rated."""

    def test_empty_string(self):
        result = offline_result("")
        self.assertFalse(result["ok"])
        self.assertIn("cannot be empty", result["error"])

    def test_spaces_only(self):
        result = offline_result("   ")
        self.assertFalse(result["ok"])
        self.assertIn("only spaces", result["error"])

    def test_too_long(self):
        result = offline_result("a" * 129)
        self.assertFalse(result["ok"])
        self.assertIn("129 characters", result["error"])


class HibpUnitTests(unittest.TestCase):
    """Have I Been Pwned helpers without depending on the live network."""

    def test_sha1_for_known_password(self):
        # Published example from Troy Hunt: P@ssw0rd
        self.assertEqual(
            hibp.sha1_hex("P@ssw0rd"),
            "21BD12DC183F740EE76F27B78EB39C8AD972A757",
        )

    def test_parse_range_response_reads_breach_count(self):
        body = (
            "0018A45C4D1DEF81644B54AB7F969B88D65:1\r\n"
            "2DC183F740EE76F27B78EB39C8AD972A757:6421042\r\n"
            "AAAA0000000000000000000000000000000:0\r\n"
        )
        count = hibp.parse_range_response(
            body,
            "2DC183F740EE76F27B78EB39C8AD972A757",
        )
        self.assertEqual(count, 6421042)

    def test_parse_range_response_returns_zero_when_absent(self):
        body = "0018A45C4D1DEF81644B54AB7F969B88D65:1\r\n"
        self.assertEqual(hibp.parse_range_response(body, "FFFFFFFFFF"), 0)

    def test_compromised_password_screams_and_forces_weak(self):
        fake_breach = {
            "checked": True,
            "compromised": True,
            "breach_count": 6421042,
            "error": "",
            "prefix": "21BD1",
        }
        with mock.patch("password_checker.check_hibp", return_value=fake_breach):
            result = password_checker.evaluate_password(
                "P@ssw0rd",
                check_breaches=True,
            )
        self.assertEqual(result["rating"], "Weak")
        self.assertTrue(result["breach"]["compromised"])
        self.assertEqual(result["breach"]["breach_count"], 6421042)
        self.assertIn("COMPROMISED", result["summary"])
        self.assertIn("6,421,042 times", result["summary"])
        self.assertIn(
            "Stop using this password everywhere. It has appeared in known data breaches.",
            result["suggestions"],
        )

    def test_clean_hibp_result_keeps_strong_rating(self):
        fake_breach = {
            "checked": True,
            "compromised": False,
            "breach_count": 0,
            "error": "",
            "prefix": "ABCDE",
        }
        with mock.patch("password_checker.check_hibp", return_value=fake_breach):
            result = password_checker.evaluate_password(
                "Nimbus#Trail82",
                check_breaches=True,
            )
        self.assertEqual(result["rating"], "Strong")
        self.assertFalse(result["breach"]["compromised"])


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_HIBP") == "1",
    "Set RUN_LIVE_HIBP=1 to hit the live Have I Been Pwned API.",
)
class HibpLiveTests(unittest.TestCase):
    """Optional live API check. Off by default so CI stays offline-friendly."""

    def test_known_pwned_password_is_compromised(self):
        result = password_checker.evaluate_password("P@ssw0rd", check_breaches=True)
        self.assertTrue(result["ok"])
        self.assertTrue(result["breach"]["checked"])
        self.assertTrue(result["breach"]["compromised"])
        self.assertGreater(result["breach"]["breach_count"], 0)
        self.assertEqual(result["rating"], "Weak")
        self.assertIn("COMPROMISED", result["summary"])


class WebParityTests(unittest.TestCase):
    """The browser checker and the Python checker must agree offline."""

    def test_common_password_list_matches(self):
        javascript = (ROOT / "public" / "checker.js").read_text(encoding="utf-8")
        match = re.search(
            r"const COMMON_PASSWORDS = \[(.*?)\];",
            javascript,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        found = re.findall(r'"([^"]*)"', match.group(1))
        self.assertEqual(tuple(found), password_checker.COMMON_PASSWORDS)

    def test_web_results_match_python(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not installed")

        cases = [
            "sunshine",
            "BlueHorse1",
            "Nimbus#Trail82",
            "Password1!",
            "hello",
            "Ab1!",
            "Blue Horse",
            "   ",
            "",
            "a" * 129,
        ]
        completed = subprocess.run(
            [node, str(ROOT / "tests" / "compare_web.js")],
            input=json.dumps(cases),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            cwd=str(ROOT),
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        web_results = json.loads(completed.stdout)

        for password, web_result in zip(cases, web_results):
            python_result = offline_result(password)
            for field in RESULT_FIELDS:
                self.assertEqual(
                    web_result[field],
                    python_result[field],
                    msg="Field " + field + " did not match for " + repr(password),
                )


class CommandLineTests(unittest.TestCase):
    """The menu program rates several passwords in one run and exits cleanly."""

    def test_session_handles_samples_and_bad_input(self):
        lines = [
            "9",
            "1",
            "sunshine",
            "1",
            "BlueHorse1",
            "1",
            "Nimbus#Trail82",
            "1",
            "Password1!",
            "1",
            "   ",
            "/cancel",
            "2",
        ]
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        env["PASSWORD_CHECKER_OFFLINE"] = "1"

        completed = subprocess.run(
            [sys.executable, str(ROOT / "password_checker.py")],
            input="\n".join(lines) + "\n",
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            env=env,
            cwd=str(ROOT),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        output = completed.stdout

        self.assertIn("Please type 1 to check a password, or 2 to quit.", output)
        self.assertIn("A password cannot be empty or made of only spaces.", output)
        self.assertIn("Dark Web radar", output)
        self.assertIn("Goodbye. Use a different strong password for every account.", output)

        ratings = re.findall(r"Rating\s+:\s+(\w+)", output)
        scores = re.findall(r"Score\s+:\s+(\d+) out of 5", output)
        self.assertEqual(ratings, ["Weak", "Moderate", "Strong", "Weak"])
        self.assertEqual(scores, ["2", "4", "5", "5"])


if __name__ == "__main__":
    unittest.main()
