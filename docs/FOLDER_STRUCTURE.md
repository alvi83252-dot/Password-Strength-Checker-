# Suggested GitHub folder structure

Repository name: `password-strength-checker`

The Python program stays at the root of the repository. The website lives in `public` because that is the folder Vercel publishes when there is no build step.

```text
password-strength-checker/
├── password_checker.py          # Terminal program. This is the main Python file.
├── requirements.txt             # States that no third-party packages are required.
├── run.bat                      # Windows shortcut for the terminal program.
├── run_web.bat                  # Windows shortcut that opens the local website.
├── run_tests.bat                # Windows shortcut for the tests.
├── vercel.json                  # Tells Vercel to publish public/ with no build.
├── .gitignore                   # Keeps cache files and local secrets out of Git.
├── README.md                    # How to run, test, and deploy the project.
├── SUBMISSION_CHECKLIST.md      # What to check before you hand the work in.
├── public/                      # The website. Vercel serves this folder.
│   ├── index.html               # The page layout.
│   ├── styles.css               # The page design.
│   ├── checker.js               # The rating rules, matching the Python file.
│   ├── app.js                   # Connects the text box to the rating rules.
│   └── favicon.svg              # The small icon in the browser tab.
├── tests/                       # Checks that the rules stay correct.
│   ├── __init__.py
│   ├── test_password_checker.py # Python tests and the menu session.
│   └── compare_web.js           # Lets the tests read the browser rules.
├── docs/
│   ├── EXAMPLES.md              # Sample inputs and the program's output.
│   ├── FOLDER_STRUCTURE.md      # This file.
│   └── SCREENSHOTS.md           # Which screenshots to take, and how.
└── screenshots/                 # Put your images here before you submit.
```

## What to commit

Commit the source files, the docs, and your screenshots.

Do not commit:

- `__pycache__/`
- `.venv/` or `venv/`
- `.env`
- `.vercel/`
- A password you actually use, including one pasted into a screenshot

## How the two checkers stay together

`password_checker.py` is the terminal program. `public/checker.js` is the browser copy of the same rules. `tests/test_password_checker.py` fails if those rules drift apart. If you change a rating sentence, change it in both files and run the tests.
