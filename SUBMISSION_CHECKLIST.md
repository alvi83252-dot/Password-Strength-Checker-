# Submission checklist

Tick each line before you hand the project in.

## Program

- [ ] `python password_checker.py` starts and shows the menu.
- [ ] `run.bat` starts the same program on Windows.
- [ ] A weak password (`sunshine`) shows Weak, the failed checks, and suggestions.
- [ ] A moderate password (`BlueHorse1`) shows Moderate and what is still missing.
- [ ] A strong candidate (`Nimbus#Trail82`) shows Strong when not found in HIBP.
- [ ] `Password1!` or `P@ssw0rd` shows **COMPROMISED** and a breach count from Have I Been Pwned.
- [ ] An empty password does not crash the program.
- [ ] Several passwords were checked in one run.
- [ ] Typing `2` prints the goodbye line and the program ends.
- [ ] `config.json` is present and the banner shows the configured thresholds.

## Website

- [ ] `run_web.bat` serves the page.
- [ ] Sample buttons show local ratings.
- [ ] A compromised sample shows the Dark Web radar with **COMPROMISED** and a count.
- [ ] `public/config.json` matches the terminal thresholds you intend to demo.

## Tests and docs

- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] Optional live HIBP test passes with `RUN_LIVE_HIBP=1`.
- [ ] `README.md`, `docs/EXAMPLES.md`, and `docs/FOLDER_STRUCTURE.md` are included.
- [ ] Screenshots are in `screenshots/` and use sample passwords only.

## Deploy

- [ ] The project is pushed to GitHub.
- [ ] Vercel Framework Preset is **Other**, Output Directory is `public`.
- [ ] The live site can reach Have I Been Pwned for a hash-prefix lookup.
- [ ] Live URL: `_______________________________`

## Secrets

- [ ] No real password appears in code, docs, or screenshots.
- [ ] No HIBP paid API key is needed or committed. The free range API is enough.
