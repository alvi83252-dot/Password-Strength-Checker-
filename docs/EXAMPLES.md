# Example inputs and outputs

These are sample passwords for the terminal program and the website. They are not secret. Do not replace them with a password you use for a real account.

The terminal text below is what the program prints. In a real window, the characters you type appear after each prompt. They are shown here so the session is easy to follow.

Start the program with:

```text
python password_checker.py
```

## Quick reference

| What you type | Where | Rating | Score |
| --- | --- | --- | --- |
| `sunshine` | password prompt | Weak | 2 of 5 |
| `BlueHorse1` | password prompt | Medium | 4 of 5 |
| `Nimbus#Trail82` | password prompt | Strong | 5 of 5 |
| `Password1!` | password prompt | Weak | 5 of 5 |
| `hello` | password prompt | Weak | 1 of 5 |
| Enter on an empty line, or spaces only | password prompt | not rated |  |
| 129 letter `a` characters | password prompt | not rated |  |
| `9` | menu | not rated |  |
| `/cancel` | password prompt | returns to the menu |  |
| `2` | menu | quits |  |

The same four main samples are buttons on the website: `sunshine`, `BlueHorse1`, `Nimbus#Trail82`, and `Password1!`.

## Startup and a bad menu choice

```text
========================================================================
                       Password Strength Checker
========================================================================

This program rates a password as Weak, Medium, or Strong.
It checks length, uppercase letters, lowercase letters,
numbers, and special characters.

Your password stays on this computer.
It is not saved, and it is not sent anywhere.

How a rating is chosen
  Weak   : shorter than 8, commonly leaked, or fewer than 3 checks
  Medium : 3 or 4 checks, long enough, and not a common password
  Strong : all 5 checks, and not a common password

Menu
  1) Check a password
  2) Quit

Enter 1 or 2: 9
Please type 1 to check a password, or 2 to quit.

Enter 1 or 2:
```

The program does not crash. It waits for `1` or `2`.

## Weak: sunshine

Input at the menu: `1`  
Input at the password prompt: `sunshine`

```text
------------------------------------------------------------------------
Result
------------------------------------------------------------------------
Password  : "sunshine"
Length    : 8 characters
Rating    : Weak
Score     : 2 out of 5

Why this rating
2 of 5 checks passed, so the rating is Weak. Weak passwords are easier to guess.

  [PASS] Length is 8 characters, which meets the minimum of 8.
  [FAIL] Missing an uppercase letter (A-Z).
  [PASS] Contains a lowercase letter.
  [FAIL] Missing a number (0-9).
  [FAIL] Missing a special character (such as ! ? # or @).

Suggestions
  - Make it longer. Aim for 12 characters or more.
  - Add at least one uppercase letter (A-Z).
  - Add at least one number (0-9).
  - Add at least one special character, such as ! ? # or @.
  - Use a unique password for each account, and keep it in a password manager.
------------------------------------------------------------------------
```

## Medium: BlueHorse1

```text
Password  : "BlueHorse1"
Length    : 10 characters
Rating    : Medium
Score     : 4 out of 5

Why this rating
4 of 5 checks passed, so the rating is Medium. A Medium password still has gaps.

  [PASS] Length is 10 characters, which meets the minimum of 8.
  [PASS] Contains an uppercase letter.
  [PASS] Contains a lowercase letter.
  [PASS] Contains a number.
  [FAIL] Missing a special character (such as ! ? # or @).

Suggestions
  - Make it longer. Aim for 12 characters or more.
  - Add at least one special character, such as ! ? # or @.
  - Use a unique password for each account, and keep it in a password manager.
```

## Strong: Nimbus#Trail82

```text
Password  : "Nimbus#Trail82"
Length    : 14 characters
Rating    : Strong
Score     : 5 out of 5

Why this rating
All 5 checks passed, and this is not a common password, so the rating is Strong.

  [PASS] Length is 14 characters, which meets the minimum of 8.
  [PASS] Contains an uppercase letter.
  [PASS] Contains a lowercase letter.
  [PASS] Contains a number.
  [PASS] Contains a special character.

Good habits
  - No changes are required for a Strong rating.
  - Use this password on only one account.
  - Store it in a password manager so you do not have to reuse it.
```

## Weak because it is common: Password1!

Every character check passes. The rating is still Weak.

```text
Password  : "Password1!"
Length    : 10 characters
Rating    : Weak
Score     : 5 out of 5

Why this rating
This password is on a short list of commonly leaked passwords, so the rating is Weak. Attackers try these passwords first.

  [PASS] Length is 10 characters, which meets the minimum of 8.
  [PASS] Contains an uppercase letter.
  [PASS] Contains a lowercase letter.
  [PASS] Contains a number.
  [PASS] Contains a special character.

Suggestions
  - Choose a different password. This one is widely known.
  - Make it longer. Aim for 12 characters or more.
  - Use a unique password for each account, and keep it in a password manager.
```

## Weak because it is short: hello

```text
Password  : "hello"
Length    : 5 characters
Rating    : Weak
Score     : 1 out of 5

Why this rating
1 of 5 checks passed, but the password is shorter than 8 characters, so the rating is Weak. A short password is easy to guess.

  [FAIL] Length is 5 characters. At least 8 are required.
  [FAIL] Missing an uppercase letter (A-Z).
  [PASS] Contains a lowercase letter.
  [FAIL] Missing a number (0-9).
  [FAIL] Missing a special character (such as ! ? # or @).

Suggestions
  - Make the password at least 8 characters long. 12 or more is safer.
  - Add at least one uppercase letter (A-Z).
  - Add at least one number (0-9).
  - Add at least one special character, such as ! ? # or @.
  - Use a unique password for each account, and keep it in a password manager.
```

## Empty input and spaces

Press Enter without typing, or type only spaces:

```text
Enter a password (or /cancel to go back):
A password cannot be empty or made of only spaces.
Type /cancel to return to the menu.
```

`/cancel` returns to the menu. The program does not invent a rating.

## Input that is too long

129 characters is rejected. 128 characters is still checked.

```text
That input is 129 characters. Please use 128 or fewer.
Type /cancel to return to the menu.
```

## Quit

```text
Enter 1 or 2: 2

Goodbye. Use a different strong password for every account.
```

You can check `sunshine`, then `BlueHorse1`, then `Nimbus#Trail82` in that same run before you type `2`. You do not need to start the program again.

## Website

Open `http://127.0.0.1:5500` after starting `run_web.bat`.

| Action | What you should see |
| --- | --- |
| Click `sunshine` | Weak, 2 of 5 checks, suggestions for uppercase, a number, and a symbol |
| Click `BlueHorse1` | Medium, 4 of 5 checks, missing a special character |
| Click `Nimbus#Trail82` | Strong, 5 of 5 checks, heading "Good habits" |
| Click `Password1!` | Weak, the note "Commonly leaked password", 5 of 5 checks |
| Click **Check strength** with an empty box | "A password cannot be empty or made of only spaces." |
| Type only spaces | The same empty-password message |
| Paste 129 `a` characters | "That input is 129 characters. Please use 128 or fewer." |
| Click **Clear** | The box is empty and the old rating is gone |

The browser rating for each sample matches the terminal rating.
