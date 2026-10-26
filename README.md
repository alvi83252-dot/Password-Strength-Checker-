# Password Strength Checker

A console program and a small website that rate a password as **Weak**, **Medium**, or **Strong**. Both use the same five checks. The password stays on your computer. It is not saved, and it is not uploaded.

This is a teaching tool. A Strong rating means the password met these rules. It does not promise that the password can never be guessed.

## Features

- Type a password in the terminal and get a rating, a reason, and suggestions.
- Check as many passwords as you want, then quit from the menu.
- Empty input, spaces, and very long input are rejected with a clear message.
- Open the same checker in a browser. The page updates as you type.
- The website is ready to publish on Vercel. The check still happens in the browser, so the password is not sent to Vercel.

## The five checks

1. At least 8 characters. 12 or more is safer.
2. An uppercase letter (A-Z).
3. A lowercase letter (a-z).
4. A number (0-9).
5. A special character such as `!`, `?`, `#`, or `@`.

A space is allowed in a passphrase. A space does not count as the special character.

## How a rating is chosen

| Rating | Rule |
| --- | --- |
| Weak | Shorter than 8 characters, found on a short list of commonly leaked passwords, or fewer than 3 checks passed |
| Medium | 3 or 4 checks passed, at least 8 characters, and not a common password |
| Strong | All 5 checks passed, and not a common password |

`Password1!` passes every character check and is still **Weak**, because that exact password is widely known. Attackers try common passwords first.

Weak and Medium passwords get suggestions. A Strong password gets a short list of good habits instead, so a passing password is not treated as a mistake.

## Privacy

- The terminal program only keeps the password in memory while it rates it.
- The website rates the password with JavaScript in the page. It does not call a server.
- Do not type a password you really use. Use the samples below for demos and screenshots.
- Vercel hosts the page only. It does not run the Python program, and it does not receive the password.

## Requirements

- Python 3.8 or newer
- No packages to install. `requirements.txt` is included so that is explicit.

Check your version:

```text
python --version
```

If that command is not found on Windows, try `py -3 --version`.

## Run the terminal program

From this folder:

```text
python password_checker.py
```

On Windows you can double-click `run.bat`.

Then:

1. Type `1` and press Enter to check a password.
2. Type a password and press Enter.
3. Read the rating, the pass/fail lines, and the suggestions.
4. Press Enter to return to the menu and test another password.
5. Type `2` and press Enter to quit.

Other commands:

- At the menu, `check` works like `1`. `q`, `quit`, and `exit` work like `2`.
- At the password prompt, `/cancel` goes back to the menu without rating anything.
- Ctrl+C quits without an error traceback.
- A wrong menu choice, such as `9`, asks you to type `1` or `2`. The program keeps running.

## Run the website on your computer

Double-click `run_web.bat`, then open:

```text
http://127.0.0.1:5500
```

Or run this yourself from the `public` folder:

```text
python -m http.server 5500
```

Press Ctrl+C in that window when you want to stop the site.

The page checks as you type. **Check strength** repeats the check. **Show** reveals the letters. **Clear** resets the box. The sample buttons fill in passwords that are safe to put in a screenshot.

You can also open `public/index.html` directly in a browser. The local server is the method to use if the page does not run from a file link.

## Run the tests

```text
python -m unittest discover -s tests -v
```

On Windows, `run_tests.bat` does the same thing. The tests check the rating rules, bad input, a full menu session, and that `public/checker.js` matches `password_checker.py`.

## Deploy the website on Vercel

The site is a static page. There is no build step and nothing to install.

1. Create a GitHub repository and push this project. A good repository name is `password-strength-checker`.
2. Sign in at [vercel.com/new](https://vercel.com/new).
3. Import that repository.
4. Leave the settings that `vercel.json` already chooses:
   - Framework Preset: **Other**
   - Build Command: empty
   - Install Command: empty
   - Output Directory: `public`
5. Click **Deploy**.
6. Open the site URL and try `sunshine`, `BlueHorse1`, `Nimbus#Trail82`, and `Password1!`.

`vercel.json` sets those four values. It also sends security headers, including a content security policy that blocks the page from connecting to other sites.

If Vercel asks you to pick a framework and the deploy fails:

- Set Framework Preset to **Other**.
- Turn on the override for Build Command and leave the box empty.
- Set Output Directory to `public`.
- Turn on the override for Install Command and leave the box empty.
- Deploy again.

The Python file stays in the GitHub repository. Vercel publishes only the files inside `public`.

## Sample passwords

Use these. Do not use a real password.

| Input | Rating | Score | Why |
| --- | --- | --- | --- |
| `sunshine` | Weak | 2 of 5 | Long enough and lowercase only |
| `BlueHorse1` | Medium | 4 of 5 | Missing a special character |
| `Nimbus#Trail82` | Strong | 5 of 5 | All five checks passed |
| `Password1!` | Weak | 5 of 5 | Commonly leaked, even though every check passed |
| `hello` | Weak | 1 of 5 | Shorter than 8 characters |
| blank, or spaces only | not rated |  | Asks for a real password |
| 129 `a` characters | not rated |  | Longer than 128 characters |
| `9` at the menu | not rated |  | Asks for 1 or 2 |

A full terminal transcript is in [docs/EXAMPLES.md](docs/EXAMPLES.md).

One result, copied from a real run:

```text
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
```

## Project layout

```text
password-strength-checker/
├── password_checker.py
├── requirements.txt
├── run.bat
├── run_web.bat
├── run_tests.bat
├── vercel.json
├── README.md
├── SUBMISSION_CHECKLIST.md
├── public/
├── tests/
├── docs/
└── screenshots/
```

Each file is explained in [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md).

## Screenshots

[docs/SCREENSHOTS.md](docs/SCREENSHOTS.md) lists the shots to take, what to type, and what must be visible. Save the images in `screenshots/`. Use the sample passwords only.

## Before you submit

Use [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md).

## Limits of this checker

The rules are the usual classroom checks, plus two extra gates: short passwords and a small list of common passwords are always Weak. A real attacker also tries names, dates, and passwords stolen from other sites. A password manager and a different password for each account matter more than adding one more symbol.
