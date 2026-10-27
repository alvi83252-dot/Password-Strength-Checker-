# Suggested GitHub folder structure

Repository name: `Password-Strength-Checker-`

```text
password-strength-checker/
├── password_checker.py          # Terminal program
├── hibp.py                      # Have I Been Pwned k-anonymity client
├── config.py                    # Loads and validates thresholds
├── config.json                  # Editable rule thresholds for the terminal
├── requirements.txt             # States that no pip packages are required
├── run.bat
├── run_web.bat
├── run_tests.bat
├── vercel.json                  # Publishes public/ and allows HIBP connect-src
├── .gitignore
├── README.md
├── SUBMISSION_CHECKLIST.md
├── public/                      # Website served by Vercel
│   ├── index.html
│   ├── styles.css
│   ├── checker.js               # Local Weak / Moderate / Strong rules
│   ├── hibp.js                  # Browser Dark Web radar
│   ├── app.js
│   ├── config.json              # Website copy of the thresholds
│   └── favicon.svg
├── tests/
│   ├── test_password_checker.py
│   └── compare_web.js
├── docs/
│   ├── EXAMPLES.md
│   ├── FOLDER_STRUCTURE.md
│   └── SCREENSHOTS.md
└── screenshots/
```

## Keep these in sync

- `config.json` and `public/config.json`
- The common-password list in `password_checker.py` and `public/checker.js`
