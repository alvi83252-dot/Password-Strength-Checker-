#!/usr/bin/env python3
"""
Password Strength Checker
=========================

A console program that rates one password at a time as Weak, Medium,
or Strong. You can check as many passwords as you like, then quit
from the menu.

The password stays in memory for the check only. It is not saved and
it is not sent anywhere.

Run it with:

    python password_checker.py

On Windows you can also double-click run.bat.
"""

import sys


# A pasted novel or a whole file should not be treated as a password.
MAX_PASSWORD_LENGTH = 128

# How wide the headings are. Kept under a typical terminal width.
WIDTH = 72

# Used when the user presses Ctrl+C or the input stream ends.
# An object is used so it can never collide with a real password.
QUIT = object()

# Exact passwords, compared after lowercasing, that show up constantly
# in leaked-password lists. A match is always Weak.
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


def validate_password(password):
    """Return an error message, or None when the password can be rated.

    Order matters. A long string of spaces is still "only spaces", so
    that message wins over the length message.
    """
    if not isinstance(password, str):
        return "Please enter a password made of text."

    if password.strip() == "":
        return "A password cannot be empty or made of only spaces."

    if len(password) > MAX_PASSWORD_LENGTH:
        return (
            "That input is "
            + characters_label(len(password))
            + ". Please use "
            + str(MAX_PASSWORD_LENGTH)
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


def collect_checks(password):
    """Run the five strength checks and return them in a dictionary."""
    return {
        "length": len(password) >= 8,
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


def decide_rating(score, checks, is_common):
    """Choose Weak, Medium, or Strong.

    A commonly leaked password is always Weak.
    A password shorter than 8 characters is always Weak.
    Otherwise 0, 1, or 2 passed checks is Weak, 3 or 4 is Medium,
    and 5 is Strong.
    """
    if is_common or (not checks["length"]) or score <= 2:
        return "Weak"
    if score >= 5:
        return "Strong"
    return "Medium"


def build_summary(score, checks, is_common):
    """Explain the rating in one or two plain sentences."""
    if is_common:
        return (
            "This password is on a short list of commonly leaked passwords, "
            "so the rating is Weak. Attackers try these passwords first."
        )

    if not checks["length"]:
        return (
            str(score)
            + " of 5 checks passed, but the password is shorter than "
            "8 characters, so the rating is Weak. A short password is easy to guess."
        )

    if score == 5:
        return (
            "All 5 checks passed, and this is not a common password, "
            "so the rating is Strong."
        )

    if score >= 3:
        return (
            str(score)
            + " of 5 checks passed, so the rating is Medium. "
            "A Medium password still has gaps."
        )

    return (
        str(score)
        + " of 5 checks passed, so the rating is Weak. "
        "Weak passwords are easier to guess."
    )


def length_detail(password, passed):
    """Describe the length check."""
    counted = characters_label(len(password))
    if passed:
        return "Length is " + counted + ", which meets the minimum of 8."
    return "Length is " + counted + ". At least 8 are required."


def build_details(password, checks):
    """Build one line of explanation for each check, in rubric order."""
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
        {"passed": checks["length"], "text": length_detail(password, checks["length"])},
        {"passed": checks["uppercase"], "text": uppercase_text},
        {"passed": checks["lowercase"], "text": lowercase_text},
        {"passed": checks["number"], "text": number_text},
        {"passed": checks["special"], "text": special_text},
    ]


def build_suggestions(password, checks, rating, is_common):
    """List ways to improve a Weak or Medium password.

    A Strong password gets an empty list. Good habits are separate,
    so a Strong rating is not presented as a failure.
    """
    if rating == "Strong":
        return []

    suggestions = []

    if is_common:
        suggestions.append(
            "Choose a different password. This one is widely known."
        )

    # Length advice depends on which length rule failed.
    if not checks["length"]:
        suggestions.append(
            "Make the password at least 8 characters long. 12 or more is safer."
        )
    elif len(password) < 12:
        suggestions.append("Make it longer. Aim for 12 characters or more.")

    if not checks["uppercase"]:
        suggestions.append("Add at least one uppercase letter (A-Z).")

    if not checks["lowercase"]:
        suggestions.append("Add at least one lowercase letter (a-z).")

    if not checks["number"]:
        suggestions.append("Add at least one number (0-9).")

    if not checks["special"]:
        suggestions.append(
            "Add at least one special character, such as ! ? # or @."
        )

    if is_repeated_character(password):
        suggestions.append("Avoid using the same character over and over.")

    suggestions.append(
        "Use a unique password for each account, and keep it in a password manager."
    )
    return suggestions


def build_habits(rating):
    """Return short reminders for a Strong password, otherwise nothing."""
    if rating != "Strong":
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
    }


def evaluate_password(password):
    """Validate and rate a password.

    On bad input, "ok" is False and "error" explains the problem.
    On success, "ok" is True and the rating fields are filled in.
    This function does not print anything, so tests and the website
    rules can share the same decisions.
    """
    error = validate_password(password)
    if error is not None:
        return rejected_result(password, error)

    checks = collect_checks(password)
    score = count_passed_checks(checks)
    is_common = password.lower() in COMMON_PASSWORD_SET
    rating = decide_rating(score, checks, is_common)

    return {
        "ok": True,
        "error": "",
        "rating": rating,
        "score": score,
        "length": len(password),
        "checks": checks,
        "is_common": is_common,
        "summary": build_summary(score, checks, is_common),
        "details": build_details(password, checks),
        "suggestions": build_suggestions(password, checks, rating, is_common),
        "habits": build_habits(rating),
    }


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
    return f"{label:<10}: {value}"


def print_banner():
    """Show the program name and the rating rules once, at startup."""
    line = "=" * WIDTH
    print(line)
    print("Password Strength Checker".center(WIDTH))
    print(line)
    print()
    print("This program rates a password as Weak, Medium, or Strong.")
    print("It checks length, uppercase letters, lowercase letters,")
    print("numbers, and special characters.")
    print()
    print("Your password stays on this computer.")
    print("It is not saved, and it is not sent anywhere.")
    print()
    print("How a rating is chosen")
    print("  Weak   : shorter than 8, commonly leaked, or fewer than 3 checks")
    print("  Medium : 3 or 4 checks, long enough, and not a common password")
    print("  Strong : all 5 checks, and not a common password")
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


def read_password():
    """Ask for a password until it is valid or the user goes back.

    Returns the password text, None when the user types /cancel,
    or QUIT when the user presses Ctrl+C or input ends.
    """
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

        error = validate_password(password)
        if error is not None:
            print(error)
            print("Type /cancel to return to the menu.")
            print()
            continue

        return password


def show_result(password, result):
    """Print the rating, why it was chosen, and how to improve it."""
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
    if result["rating"] == "Strong":
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

    print_banner()

    while True:
        print_menu()
        choice = read_menu_choice()
        if choice == "2":
            break

        password = read_password()
        if password is QUIT:
            break
        if password is None:
            continue

        show_result(password, evaluate_password(password))
        pause()

    say_goodbye()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say_goodbye()
        sys.exit(0)
