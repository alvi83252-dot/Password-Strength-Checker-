# Submission checklist

Tick each line before you hand the project in.

## Program

- [ ] `python password_checker.py` starts and shows the menu.
- [ ] `run.bat` starts the same program on Windows.
- [ ] A weak password (`sunshine`) shows Weak, the failed checks, and suggestions.
- [ ] A medium password (`BlueHorse1`) shows Medium and what is still missing.
- [ ] A strong password (`Nimbus#Trail82`) shows Strong and good habits.
- [ ] `Password1!` shows Weak even though all 5 checks pass, and the reason says it is commonly leaked.
- [ ] `hello` shows Weak because it is shorter than 8 characters.
- [ ] An empty password does not crash the program. It prints a clear message.
- [ ] A menu choice other than 1 or 2 does not crash the program.
- [ ] Several passwords were checked in one run, without closing and opening the program.
- [ ] Typing `2` prints the goodbye line and the program ends.
- [ ] Comments in `password_checker.py` are still clear after any edits.

## Website

- [ ] `run_web.bat` serves the page, and the page opens in a browser.
- [ ] The four sample buttons show the same ratings as the terminal.
- [ ] **Show** and **Hide** change whether the password is visible.
- [ ] **Clear** removes the old rating.
- [ ] **Check strength** on an empty box explains that the password cannot be empty.
- [ ] While typing a sample, the browser's network panel does not send the password anywhere.

## Tests and docs

- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] `README.md` is included.
- [ ] `docs/EXAMPLES.md` is included.
- [ ] `docs/FOLDER_STRUCTURE.md` matches the files in the repository.
- [ ] `docs/SCREENSHOTS.md` was followed.
- [ ] Screenshots are in the `screenshots` folder and use the sample passwords only.
- [ ] `requirements.txt` is included.
- [ ] `vercel.json` is included and Output Directory is `public`.

## Deploy

- [ ] The project is pushed to GitHub.
- [ ] The repository was imported on Vercel with Framework Preset **Other**.
- [ ] Build Command is empty and Output Directory is `public`.
- [ ] The live site opens, and `Nimbus#Trail82` is Strong.
- [ ] The live URL is written here: `_______________________________`

## Secrets

- [ ] No real password appears in the code, the docs, the screenshots, or the terminal scrollback you submit.
- [ ] No `.env` file or API key is committed.
