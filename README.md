# Password Strength Checker

A console program and a small website that rate a password as **Weak**, **Moderate**, or **Strong**, then run a Have I Been Pwned **Dark Web radar**. If that password has appeared in known breach data, the tool screams **COMPROMISED** and shows the exact breach count.

## What this project covers

| Requirement | Status |
| --- | --- |
| Accept a password and return Weak / Moderate / Strong with a short rationale | Done |
| Documented rule set for length and character classes | Done |
| Configurable thresholds | Done — edit `config.json` |
| Have I Been Pwned API integration with breach count | Done — k-anonymity range API |
| Loud **COMPROMISED** result when the password is pwned | Done |
| Test cases for weak and strong passwords | Done — plus HIBP unit tests |
| Terminal app + Vercel-ready website | Done |

## Features

- Type a password in the terminal and get a rating, a reason, suggestions, and a breach scan.
- Check as many passwords as you want, then quit from the menu.
- Empty input, spaces, and very long input are rejected with a clear message.
- Open the same checker in a browser. Local strength updates as you type; the Dark Web radar uses Have I Been Pwned.
- Edit `config.json` (and `public/config.json` for the website) to change length and score thresholds.

## Privacy and Have I Been Pwned

This project uses the free [Pwned Passwords range API](https://haveibeenpwned.com/API/v3#PwnedPasswords). **No API key is required.**

How the Dark Web radar works:

1. The password is hashed with SHA-1 on your computer or in your browser.
2. Only the first 5 characters of that hash are sent to `api.pwnedpasswords.com`.
3. The response is a list of hash suffixes. The program searches that list locally.
4. If there is a match, you see **COMPROMISED** and the number of times that password appeared in breach data.

The full password is never uploaded to Have I Been Pwned, Vercel, or any other server.

Do not type a password you really use. Use the samples below for demos and screenshots.

## The documented rule set

1. Length at least `min_length` (default 8). `recommended_length` (default 12) is safer.
2. An uppercase letter (A-Z), when `require_uppercase` is true.
3. A lowercase letter (a-z), when `require_lowercase` is true.
4. A number (0-9), when `require_number` is true.
5. A special character such as `!`, `?`, `#`, or `@`, when `require_special` is true.

A space is allowed in a passphrase. A space does not count as the special character.

## Configurable thresholds

Edit `config.json` for the terminal program. Edit `public/config.json` for the website. Keep them the same unless you are experimenting.

| Key | Default | Meaning |
| --- | --- | --- |
| `min_length` | `8` | Fail the length check below this |
| `recommended_length` | `12` | Suggest a longer password below this |
| `max_length` | `128` | Reject input longer than this |
| `weak_max_passed_checks` | `2` | Score at or below this is Weak |
| `moderate_min_passed_checks` | `3` | Score at or above this can be Moderate |
| `strong_min_passed_checks` | `5` | Score at or above this can be Strong |
| `hibp_enabled` | `true` | Turn the Dark Web radar on or off |
| `hibp_timeout_seconds` | `10` | Network timeout for the terminal HIBP call |

Restart the terminal program after you change `config.json`.

## How a rating is chosen

| Rating | Rule |
| --- | --- |
| Weak | Shorter than `min_length`, found on the local common list, score at or below `weak_max_passed_checks`, **or found in Have I Been Pwned** |
| Moderate | Score at or above `moderate_min_passed_checks`, long enough, and not common or compromised |
| Strong | Score at or above `strong_min_passed_checks`, and not found in Have I Been Pwned |

`Password1!` can pass every character check and still become **Weak** because Have I Been Pwned marks it **COMPROMISED** with a large breach count.

## Requirements

- Python 3.8 or newer
- Internet access when `hibp_enabled` is true
- No packages to install. `requirements.txt` states that clearly.

```text
python --version
```

## Run the terminal program

```text
python password_checker.py
```

On Windows you can double-click `run.bat`.

Then:

1. Type `1` and press Enter.
2. Type a password and press Enter.
3. Read the rating, the Dark Web radar, the pass/fail lines, and the suggestions.
4. Press Enter to return to the menu.
5. Type `2` to quit.

Try `Password1!` or `P@ssw0rd` to see **COMPROMISED** with a breach count.

## Run the website on your computer

Double-click `run_web.bat`, then open:

```text
http://127.0.0.1:5500
```

Or:

```text
cd public
python -m http.server 5500
```

Use HTTPS or localhost so the browser can hash the password with SubtleCrypto.

## Run the tests

```text
python -m unittest discover -s tests -v
```

Optional live Have I Been Pwned check:

```text
set RUN_LIVE_HIBP=1
python -m unittest tests.test_password_checker.HibpLiveTests -v
```

## Deploy the website on Vercel

1. Push this repository to GitHub.
2. Import it at [vercel.com/new](https://vercel.com/new).
3. Keep the settings from `vercel.json`:
   - Framework Preset: **Other**
   - Build Command: empty
   - Install Command: empty
   - Output Directory: `public`
4. Deploy, then open the live URL and try `Password1!`.

`vercel.json` allows browser calls only to `https://api.pwnedpasswords.com` for the hash-prefix lookup.

## Sample passwords

| Input | Offline strength | Dark Web radar |
| --- | --- | --- |
| `sunshine` | Weak | Often compromised |
| `BlueHorse1` | Moderate | Depends on HIBP |
| `Nimbus#Trail82` | Strong | Depends on HIBP |
| `Password1!` | Weak / common | COMPROMISED with a large count |
| `P@ssw0rd` | Weak pattern | COMPROMISED with a large count |

More transcripts: [docs/EXAMPLES.md](docs/EXAMPLES.md).

## Project layout

```text
password-strength-checker/
├── password_checker.py      # Terminal app
├── hibp.py                  # Have I Been Pwned k-anonymity client
├── config.py                # Loads config.json
├── config.json              # Editable thresholds
├── public/                  # Website + public/config.json
├── tests/
├── docs/
└── screenshots/
```

Details: [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md).

## Before you submit

Use [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md). Screenshot guide: [docs/SCREENSHOTS.md](docs/SCREENSHOTS.md).

## Limits

A Strong rating means the password met these rules and was not found in the Have I Been Pwned range that was returned. It does not prove the password can never be guessed. Use a password manager and a different password for every account.
