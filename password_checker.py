#!/usr/bin/env python3
"""
Password Strength Checker
=========================

A console program that rates one password at a time as Weak, Moderate,
or Strong. It also runs a Have I Been Pwned "Dark Web" radar. If the
password shows up in known breach data, the program screams COMPROMISED
and shows how many times that password has appeared.

You can check as many passwords as you like, then quit from the menu.

How privacy works for the breach check:
- The password is hashed with SHA-1 on this computer.
- Only the first 5 characters of that hash are sent to Have I Been Pwned.
- The full password is never uploaded.

Edit config.json to change length thresholds and other rules.

Run it with:

    python password_checker.py

On Windows you can also double-click run.bat.
"""

from __future__ import annotations

import os
import sys

from config import SETTINGS, load_config
from hibp import check_password as check_hibp


# How wide the headings are. Kept under a typical terminal width.
WIDTH = 72

# Used when the user presses Ctrl+C or the input stream ends.
# An object is used so it can never collide with a real password.
QUIT = object()

# Exact passwords, compared after lowercasing, that show up constantly
# in leaked-password lists. A match is always Weak when the local list
# is enabled in config.json.
# Keep this tuple in the same order as COMMON_PASSWORDS in public/checker.js.
COMMON_PASSWORDS = (
    "password",
    "password1",
    "password12",
    "password123",
    "password!",
    "password1!",
    "passw0rd",
    "123456",
    "1234567",
    "12345678",
    "123456789",
    "1234567890",
    "qwerty",
    "qwerty123",
    "qwertyuiop",
    "abc123",
    "letmein",
    "admin",
    "welcome",
    "welcome1",
    "iloveyou",
    "monkey",
    "dragon",
    "master",
    "login",
    "trustno1",
    "111111",
    "000000",
    "654321",
)

COMMON_PASSWORD_SET = set(COMMON_PASSWORDS)


def characters_label(count):
    """Return '1 character' or '8 characters'."""
    if count == 1:
        return "1 character"
    return str(count) + " characters"


def empty_checks():
    """Return the five checks, all failed. Used when input is rejected."""
    return {
        "length": False,
        "uppercase": False,
        "lowercase": False,
        "number": False,
        "special": False,
    }


def empty_breach():
    """Return the unused breach fields for rejected or offline results."""
    return {
        "checked": False,
        "compromised": False,
        "breach_count": 0,
        "error": "",
        "prefix": "",
    }


def validate_password(password, settings=None):
    """Return an error message, or None when the password can be rated.

    Order matters. A long string of spaces is still "only spaces", so
    that message wins over the length message.
    """
    options = settings if settings is not None else SETTINGS

    if not isinstance(password, str):
        return "Please enter a password made of text."

    if password.strip() == "":
        return "A password cannot be empty or made of only spaces."

    max_length = options["max_length"]
    if len(password) > max_length:
        return (
            "That input is "
            + characters_label(len(password))
            + ". Please use "
            + str(max_length)
            + " or fewer."
        )

    return None


def is_number(character):
    """Return True for the digits 0 through 9 only."""
    return character in "0123456789"


def is_special_character(character):
    """Return True for a symbol such as ! ? # or @.

    Letters and numbers do not count. Spaces do not count either.
    Spaces are allowed in a passphrase, but a space alone does not
    satisfy the special-character check.
    """
    if character.isalnum():
        return False
    if character.isspace():
        return False
    return True


def contains_uppercase(password):
    """Return True if any character is an uppercase letter."""
    for character in password:
        if character.isupper():
            return True
    return False


def contains_lowercase(password):
    """Return True if any character is a lowercase letter."""
    for character in password:
        if character.islower():
            return True
    return False


def contains_number(password):
    """Return True if any character is a digit from 0 to 9."""
    for character in password:
        if is_number(character):
            return True
    return False


def contains_special(password):
    """Return True if any character is a special character."""
    for character in password:
        if is_special_character(character):
            return True
    return False


def is_repeated_character(password):
    """Return True when every character is the same, such as aaaaaaaa."""
    if password == "":
        return False
    first = password[0]
    for character in password:
        if character != first:
            return False
    return True


def collect_checks(password, settings=None):
    """Run the five strength checks and return them in a dictionary."""
    options = settings if settings is not None else SETTINGS
    return {
        "length": len(password) >= options["min_length"],
        "uppercase": contains_uppercase(password),
        "lowercase": contains_lowercase(password),
        "number": contains_number(password),
        "special": contains_special(password),
    }


def count_passed_checks(checks):
    """Count how many of the five checks passed."""
    total = 0
    for passed in checks.values():
        if passed:
            total = total + 1
    return total


def decide_rating(score, checks, is_common, settings=None):
    """Choose Weak, Moderate, or Strong from the documented thresholds."""
    options = settings if settings is not None else SETTINGS

    if is_common or (not checks["length"]) or score <= options["weak_max_passed_checks"]:
        return "Weak"
    if score >= options["strong_min_passed_checks"]:
        return "Strong"
    if score >= options["moderate_min_passed_checks"]:
        return "Moderate"
    return "Weak"


def build_summary(score, checks, is_common, rating, settings=None):
    """Explain the rating in one or two plain sentences."""
    options = settings if settings is not None else SETTINGS
    min_length = options["min_length"]

    if is_common:
        return (
            "This password is on a short list of commonly leaked passwords, "
            "so the rating is Weak. Attackers try these passwords first."
        )

    if not checks["length"]:
        return (
            str(score)
            + " of 5 checks passed, but the password is shorter than "
            + str(min_length)
            + " characters, so the rating is Weak. A short password is easy to guess."
        )

    if rating == "Strong":
        return (
            "All required checks passed, and this is not a common password, "
            "so the rating is Strong."
        )

    if rating == "Moderate":
        return (
            str(score)
            + " of 5 checks passed, so the rating is Moderate. "
            "A Moderate password still has gaps."
        )

    return (
        str(score)
        + " of 5 checks passed, so the rating is Weak. "
        "Weak passwords are easier to guess."
    )


def length_detail(password, passed, settings=None):
    """Describe the length check using the configured minimum."""
    options = settings if settings is not None else SETTINGS
    counted = characters_label(len(password))
    minimum = options["min_length"]
    if passed:
        return (
            "Length is "
            + counted
            + ", which meets the minimum of "
            + str(minimum)
            + "."
        )
    return (
        "Length is "
        + counted
        + ". At least "
        + str(minimum)
        + " are required."
    )


def build_details(password, checks, settings=None):
    """Build one line of explanation for each check, in rubric order."""
    options = settings if settings is not None else SETTINGS

    if checks["uppercase"]:
        uppercase_text = "Contains an uppercase letter."
    else:
        uppercase_text = "Missing an uppercase letter (A-Z)."

    if checks["lowercase"]:
        lowercase_text = "Contains a lowercase letter."
    else:
        lowercase_text = "Missing a lowercase letter (a-z)."

    if checks["number"]:
        number_text = "Contains a number."
    else:
        number_text = "Missing a number (0-9)."

    if checks["special"]:
        special_text = "Contains a special character."
    else:
        special_text = "Missing a special character (such as ! ? # or @)."

    return [
        {
            "passed": checks["length"],
            "text": length_detail(password, checks["length"], options),
        },
        {"passed": checks["uppercase"], "text": uppercase_text},
        {"passed": checks["lowercase"], "text": lowercase_text},
        {"passed": checks["number"], "text": number_text},
        {"passed": checks["special"], "text": special_text},
    ]


def build_suggestions(password, checks, rating, is_common, compromised, settings=None):
    """List ways to improve a Weak or Moderate password.

    A Strong password that is not compromised gets an empty list.
    Good habits are separate, so a Strong rating is not presented as a failure.
    """
    options = settings if settings is not None else SETTINGS

    if rating == "Strong" and not compromised:
        return []

    suggestions = []

    if compromised:
        suggestions.append(
            "Stop using this password everywhere. It has appeared in known data breaches."
        )
        suggestions.append(
            "Create a brand-new password that you have never used before."
        )

    if is_common:
        suggestions.append(
            "Choose a different password. This one is widely known."
        )

    # Length advice depends on which length rule failed.
    if not checks["length"]:
        suggestions.append(
            "Make the password at least "
            + str(options["min_length"])
            + " characters long. "
            + str(options["recommended_length"])
            + " or more is safer."
        )
    elif len(password) < options["recommended_length"]:
        suggestions.append(
            "Make it longer. Aim for "
            + str(options["recommended_length"])
            + " characters or more."
        )

    if options["require_uppercase"] and not checks["uppercase"]:
        suggestions.append("Add at least one uppercase letter (A-Z).")

    if options["require_lowercase"] and not checks["lowercase"]:
        suggestions.append("Add at least one lowercase letter (a-z).")

    if options["require_number"] and not checks["number"]:
        suggestions.append("Add at least one number (0-9).")

    if options["require_special"] and not checks["special"]:
        suggestions.append(
            "Add at least one special character, such as ! ? # or @."
        )

    if is_repeated_character(password):
        suggestions.append("Avoid using the same character over and over.")

    suggestions.append(
        "Use a unique password for each account, and keep it in a password manager."
    )
    return suggestions


def build_habits(rating, compromised):
    """Return short reminders for a Strong, non-compromised password."""
    if rating != "Strong" or compromised:
        return []
    return [
        "No changes are required for a Strong rating.",
        "Use this password on only one account.",
        "Store it in a password manager so you do not have to reuse it.",
    ]


def rejected_result(password, error):
    """Build the result used when the input cannot be rated."""
    if isinstance(password, str):
        length = len(password)
    else:
        length = 0

    return {
        "ok": False,
        "error": error,
        "rating": "",
        "score": 0,
        "length": length,
        "checks": empty_checks(),
        "is_common": False,
        "summary": "",
        "details": [],
        "suggestions": [],
        "habits": [],
        "breach": empty_breach(),
    }


def format_breach_count(count):
    """Format 6421042 as '6,421,042 times' for readable output."""
    try:
        number = int(count)
    except (TypeError, ValueError):
        number = 0
    labeled = f"{number:,}"
    if number == 1:
        return labeled + " time"
    return labeled + " times"


def evaluate_password(password, settings=None, check_breaches=False):
    """Validate and rate a password.

    On bad input, "ok" is False and "error" explains the problem.
    On success, "ok" is True and the rating fields are filled in.

    Breach checking is off by default so unit tests stay offline and
    fast. The console program turns it on. Pass check_breaches=True
    when the Dark Web radar should run.
    """
    options = settings if settings is not None else SETTINGS

    error = validate_password(password, options)
    if error is not None:
        return rejected_result(password, error)

    checks = collect_checks(password, options)
    score = count_passed_checks(checks)
    is_common = False
    if options.get("use_local_common_list", True):
        is_common = password.lower() in COMMON_PASSWORD_SET

    rating = decide_rating(score, checks, is_common, options)

    result = {
        "ok": True,
        "error": "",
        "rating": rating,
        "score": score,
        "length": len(password),
        "checks": checks,
        "is_common": is_common,
        "summary": build_summary(score, checks, is_common, rating, options),
        "details": build_details(password, checks, options),
        "suggestions": build_suggestions(
            password, checks, rating, is_common, False, options
        ),
        "habits": build_habits(rating, False),
        "breach": empty_breach(),
    }

    if not check_breaches:
        return result

    breach = check_hibp(password, options)
    if breach.get("compromised"):
        result["rating"] = "Weak"
        result["summary"] = (
            "COMPROMISED: this password has appeared "
            + format_breach_count(breach["breach_count"])
            + " in Have I Been Pwned breached-password records. "
            "Do not use it. The rule-based score was "
            + str(score)
            + " of 5 before the breach check."
        )
        result["suggestions"] = build_suggestions(
            password, checks, "Weak", is_common, True, options
        )
        result["habits"] = []
        result["breach"] = breach
        return result

    result["breach"] = breach
    if breach.get("error"):
        # Strength result still stands. The offline note is shown separately.
        pass
    return result


def display(text):
    """Print text, even on consoles that cannot show every symbol."""
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe_text = text.encode(encoding, errors="replace").decode(
            encoding, errors="replace"
        )
        print(safe_text)


def labeled_line(label, value):
    """Return a line with the colon lined up, such as 'Rating    : Weak'."""
    return f"{label:<12}: {value}"


def print_banner(settings=None):
    """Show the program name and the rating rules once, at startup."""
    options = settings if settings is not None else SETTINGS
    line = "=" * WIDTH
    print(line)
    print("Password Strength Checker".center(WIDTH))
    print(line)
    print()
    print("This program rates a password as Weak, Moderate, or Strong.")
    print("It checks length, uppercase letters, lowercase letters,")
    print("numbers, and special characters.")
    print()
    print("Dark Web radar: Have I Been Pwned (k-anonymity).")
    print("Only a short hash prefix leaves this computer, never the password.")
    print()
    print("Configured thresholds (edit config.json to change them)")
    print("  Minimum length     : " + str(options["min_length"]))
    print("  Recommended length : " + str(options["recommended_length"]))
    print("  Weak if score <=   : " + str(options["weak_max_passed_checks"]))
    print("  Moderate if score >= " + str(options["moderate_min_passed_checks"]))
    print("  Strong if score >= : " + str(options["strong_min_passed_checks"]))
    print("  HIBP enabled       : " + str(options["hibp_enabled"]))
    print()
    print("How a rating is chosen")
    print("  Weak     : short, common, few checks, or found in breach data")
    print("  Moderate : enough checks, long enough, and not a common password")
    print("  Strong   : all required checks, and not found in breach data")
    print()


def print_menu():
    """Show the two choices. Printed again after every result."""
    print()
    print("Menu")
    print("  1) Check a password")
    print("  2) Quit")
    print()


def read_menu_choice():
    """Keep asking until the user chooses check or quit.

    Ctrl+C and a closed input stream count as quit, so the program
    ends cleanly instead of showing an error traceback.
    """
    while True:
        try:
            choice = input("Enter 1 or 2: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return "2"

        if choice in ("1", "check"):
            return "1"
        if choice in ("2", "q", "quit", "exit"):
            return "2"

        print("Please type 1 to check a password, or 2 to quit.")
        print()


def read_password(settings=None):
    """Ask for a password until it is valid or the user goes back.

    Returns the password text, None when the user types /cancel,
    or QUIT when the user presses Ctrl+C or input ends.
    """
    options = settings if settings is not None else SETTINGS

    while True:
        try:
            password = input("Enter a password (or /cancel to go back): ")
        except (EOFError, KeyboardInterrupt):
            print()
            return QUIT

        # /cancel is a command, not a password. It is documented in the
        # prompt so a normal password is not swallowed by the word "quit".
        if password.strip().lower() == "/cancel":
            return None

        error = validate_password(password, options)
        if error is not None:
            print(error)
            print("Type /cancel to return to the menu.")
            print()
            continue

        return password


def show_breach_radar(breach):
    """Print the Dark Web radar block in a loud, hard-to-miss format."""
    print()
    print("!" * WIDTH)
    print("DARK WEB RADAR — Have I Been Pwned".center(WIDTH))
    print("!" * WIDTH)

    if breach.get("compromised"):
        print()
        display(">>> COMPROMISED <<<".center(WIDTH))
        print()
        display(
            "This exact password has appeared "
            + format_breach_count(breach["breach_count"])
            + " in known breach dumps."
        )
        print("It was found in known data-breach password dumps.")
        print("Never use it again.")
        return

    if breach.get("checked"):
        print()
        print("Not found in the Have I Been Pwned breached-password range.")
        print("That is good news, but it does not mean the password is unique.")
        return

    print()
    if breach.get("error"):
        print(breach["error"])
    else:
        print("The breach check did not run.")


def show_result(password, result):
    """Print the rating, the Dark Web radar, why it was chosen, and advice."""
    if not result["ok"]:
        print()
        print(result["error"])
        return

    print()
    print("-" * WIDTH)
    print("Result")
    print("-" * WIDTH)
    display(labeled_line("Password", '"' + password + '"'))
    display(labeled_line("Length", characters_label(result["length"])))
    print(labeled_line("Rating", result["rating"]))
    print(labeled_line("Score", str(result["score"]) + " out of 5"))

    show_breach_radar(result.get("breach", empty_breach()))

    print()
    print("Why this rating")
    print(result["summary"])
    print()

    for detail in result["details"]:
        if detail["passed"]:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        print("  " + status + " " + detail["text"])

    print()
    if result["rating"] == "Strong" and not result.get("breach", {}).get("compromised"):
        print("Good habits")
        for habit in result["habits"]:
            print("  - " + habit)
    else:
        print("Suggestions")
        for suggestion in result["suggestions"]:
            print("  - " + suggestion)

    print("-" * WIDTH)


def pause():
    """Wait for Enter so a result stays on screen.

    Skipped when input is piped in, so automated runs are not stuck
    waiting for a key that will never come.
    """
    if not sys.stdin.isatty():
        return
    try:
        input("Press Enter to return to the menu.")
    except (EOFError, KeyboardInterrupt):
        print()


def say_goodbye():
    """Print the closing line used by every exit path."""
    print()
    print("Goodbye. Use a different strong password for every account.")


def main():
    """Run the menu until the user quits."""
    if sys.version_info < (3, 8):
        print("Python 3.8 or newer is required.")
        return 1

    try:
        settings = load_config()
    except (OSError, ValueError, TypeError) as error:
        print("Could not load config.json: " + str(error))
        return 1

    print_banner(settings)

    while True:
        print_menu()
        choice = read_menu_choice()
        if choice == "2":
            break

        password = read_password(settings)
        if password is QUIT:
            break
        if password is None:
            continue

        # Tests can set PASSWORD_CHECKER_OFFLINE=1 to skip the live API.
        offline = os.environ.get("PASSWORD_CHECKER_OFFLINE", "").strip() == "1"
        should_check_breaches = settings.get("hibp_enabled", True) and not offline

        print()
        if should_check_breaches:
            print("Checking strength and scanning Have I Been Pwned...")
        else:
            print("Checking strength (breach scan offline)...")
        result = evaluate_password(
            password,
            settings=settings,
            check_breaches=should_check_breaches,
        )
        show_result(password, result)
        pause()

    say_goodbye()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say_goodbye()
        sys.exit(0)
