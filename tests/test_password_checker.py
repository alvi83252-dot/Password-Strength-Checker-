"""Tests for the password rules, the menu program, and the web checker."""

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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


class RatingTests(unittest.TestCase):
    """The rating rules from the assignment, plus the two safety gates."""

    def test_short_password_is_weak_even_with_many_character_types(self):
        result = password_checker.evaluate_password("Ab1!")
        self.assertTrue(result["ok"])
        self.assertEqual(result["rating"], "Weak")
        self.assertEqual(result["score"], 4)
        self.assertFalse(result["checks"]["length"])
        self.assertIn("shorter than", result["summary"])
        self.assertIn(
            "Make the password at least 8 characters long. 12 or more is safer.",
            result["suggestions"],
        )

    def test_length_and_lowercase_only_is_weak(self):
        result = password_checker.evaluate_password("sunshine")
        self.assertEqual(result["rating"], "Weak")
        self.assertEqual(result["score"], 2)
        self.assertTrue(result["checks"]["length"])
        self.assertTrue(result["checks"]["lowercase"])
        self.assertFalse(result["checks"]["uppercase"])
        self.assertFalse(result["checks"]["number"])
        self.assertFalse(result["checks"]["special"])

    def test_three_checks_is_medium(self):
        result = password_checker.evaluate_password("HelloWorld")
        self.assertEqual(result["rating"], "Medium")
        self.assertEqual(result["score"], 3)

    def test_four_checks_is_medium(self):
        result = password_checker.evaluate_password("BlueHorse1")
        self.assertEqual(result["rating"], "Medium")
        self.assertEqual(result["score"], 4)
        self.assertFalse(result["checks"]["special"])
        self.assertIn(
            "Add at least one special character, such as ! ? # or @.",
            result["suggestions"],
        )
        self.assertIn("Make it longer. Aim for 12 characters or more.", result["suggestions"])

    def test_all_five_checks_is_strong(self):
        result = password_checker.evaluate_password("Nimbus#Trail82")
        self.assertEqual(result["rating"], "Strong")
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["suggestions"], [])
        self.assertEqual(len(result["habits"]), 3)
        self.assertTrue(all(detail["passed"] for detail in result["details"]))

    def test_common_password_is_weak_even_when_it_looks_complex(self):
        result = password_checker.evaluate_password("Password1!")
        self.assertEqual(result["score"], 5)
        self.assertTrue(result["is_common"])
        self.assertEqual(result["rating"], "Weak")
        self.assertIn("commonly leaked", result["summary"])
        self.assertIn(
            "Choose a different password. This one is widely known.",
            result["suggestions"],
        )

    def test_password_with_only_a_capital_letter_is_still_common(self):
        result = password_checker.evaluate_password("Password")
        self.assertTrue(result["is_common"])
        self.assertEqual(result["rating"], "Weak")

    def test_repeated_characters_add_a_suggestion(self):
        result = password_checker.evaluate_password("a" * 8)
        self.assertEqual(result["rating"], "Weak")
        self.assertIn(
            "Avoid using the same character over and over.",
            result["suggestions"],
        )

    def test_space_does_not_count_as_a_special_character(self):
        result = password_checker.evaluate_password("Blue Horse")
        self.assertTrue(result["ok"])
        self.assertFalse(result["checks"]["special"])
        self.assertEqual(result["rating"], "Medium")
        self.assertEqual(result["score"], 3)

    def test_exactly_128_characters_is_accepted(self):
        result = password_checker.evaluate_password("a" * 128)
        self.assertTrue(result["ok"])
        self.assertEqual(result["length"], 128)

    def test_details_follow_the_rubric_order(self):
        result = password_checker.evaluate_password("sunshine")
        texts = [detail["text"] for detail in result["details"]]
        self.assertTrue(texts[0].startswith("Length is"))
        self.assertIn("uppercase", texts[1])
        self.assertIn("lowercase", texts[2])
        self.assertIn("number", texts[3])
        self.assertIn("special", texts[4])


class InvalidInputTests(unittest.TestCase):
    """Bad input is explained and never rated."""

    def test_empty_string(self):
        result = password_checker.evaluate_password("")
        self.assertFalse(result["ok"])
        self.assertEqual(result["rating"], "")
        self.assertIn("cannot be empty", result["error"])

    def test_spaces_only(self):
        result = password_checker.evaluate_password("   ")
        self.assertFalse(result["ok"])
        self.assertIn("only spaces", result["error"])

    def test_too_long(self):
        result = password_checker.evaluate_password("a" * 129)
        self.assertFalse(result["ok"])
        self.assertIn("129 characters", result["error"])
        self.assertIn("128", result["error"])

    def test_long_string_of_spaces_uses_the_spaces_message(self):
        result = password_checker.evaluate_password(" " * 200)
        self.assertIn("only spaces", result["error"])

    def test_non_text(self):
        result = password_checker.evaluate_password(None)
        self.assertFalse(result["ok"])
        self.assertIn("text", result["error"])


class WebParityTests(unittest.TestCase):
    """The browser checker and the Python checker must agree."""

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
            "Password",
            "hello",
            "Ab1!",
            "a" * 8,
            "Blue Horse",
            "CafeTime1!",
            "   ",
            "",
            "a" * 129,
            " " * 200,
            "Nimbus#Trail82" + " ",
        ]
        env = os.environ.copy()
        completed = subprocess.run(
            [node, str(ROOT / "tests" / "compare_web.js")],
            input=json.dumps(cases),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            cwd=str(ROOT),
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        web_results = json.loads(completed.stdout)
        self.assertEqual(len(web_results), len(cases))

        for password, web_result in zip(cases, web_results):
            python_result = password_checker.evaluate_password(password)
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
            "hello",
            "1",
            "   ",
            "/cancel",
            "1",
            "a" * 129,
            "/cancel",
            "2",
        ]
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ROOT / "password_checker.py")],
            input="\n".join(lines) + "\n",
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        output = completed.stdout

        self.assertIn("Please type 1 to check a password, or 2 to quit.", output)
        self.assertIn("A password cannot be empty or made of only spaces.", output)
        self.assertIn("129 characters", output)
        self.assertIn("Goodbye. Use a different strong password for every account.", output)

        ratings = re.findall(r"Rating\s+:\s+(\w+)", output)
        scores = re.findall(r"Score\s+:\s+(\d+) out of 5", output)
        self.assertEqual(ratings, ["Weak", "Medium", "Strong", "Weak", "Weak"])
        self.assertEqual(scores, ["2", "4", "5", "5", "1"])
        self.assertIn("Suggestions", output)
        self.assertIn("Good habits", output)
        self.assertIn("commonly leaked", output)


if __name__ == "__main__":
    unittest.main()
