# Screenshot instructions

Take these pictures to show that the program works. Save them in the `screenshots` folder using the file names below.

Use only the sample passwords from [EXAMPLES.md](EXAMPLES.md). Do not type a password from a real account. If a shot includes the password, it must be one of the samples.

On Windows, press `Win + Shift + S`, drag a rectangle around the window, and paste it into Paint or Photos. Save as PNG. Crop to the program window. Leave the rating and the reason visible. Do not crop off the suggestions.

## Terminal

Start the program first:

```text
python password_checker.py
```

You can double-click `run.bat` instead.

| File | What to do | What must be visible |
| --- | --- | --- |
| `screenshots/01-terminal-menu.png` | Start the program and do not type yet. | The title, the five ideas it checks, the Weak / Medium / Strong rules, and the menu |
| `screenshots/02-terminal-weak.png` | Choose `1`, type `sunshine`, press Enter. | `Rating : Weak`, the pass/fail lines, and Suggestions |
| `screenshots/03-terminal-medium.png` | Return to the menu, choose `1`, type `BlueHorse1`. | `Rating : Medium` and the missing special character |
| `screenshots/04-terminal-strong.png` | Check `Nimbus#Trail82` in the same run. | `Rating : Strong`, five `[PASS]` lines, and Good habits |
| `screenshots/05-terminal-common.png` | Check `Password1!`. | Score `5 out of 5` and rating `Weak`, plus the "commonly leaked" sentence |
| `screenshots/06-terminal-invalid.png` | At the menu type `9`, or at the password prompt press Enter with no password. | The error sentence, and the program still waiting for another choice |

Shots 02 through 05 should be from one run. That shows you can test more than one password without restarting.

After the last shot, type `2` so the goodbye line is on screen if you want an extra picture. It is optional.

## Website

Start the page:

```text
run_web.bat
```

Open `http://127.0.0.1:5500`. Click **Show**, or click a sample button, so the sample password is readable in the shot.

| File | What to do | What must be visible |
| --- | --- | --- |
| `screenshots/07-web-home.png` | Open the page. Do not type yet. | The title, the five checks, and the empty password box |
| `screenshots/08-web-weak.png` | Click the `sunshine` sample. | The word Weak, `2 of 5 checks`, and the suggestions |
| `screenshots/09-web-medium.png` | Click `BlueHorse1`. | The word Medium and the missing special character |
| `screenshots/10-web-strong.png` | Click `Nimbus#Trail82`. | The word Strong and the Good habits heading |
| `screenshots/11-web-common.png` | Click `Password1!`. | "Commonly leaked password" and the word Weak |
| `screenshots/12-web-invalid.png` | Click **Clear**, then **Check strength**. | "A password cannot be empty or made of only spaces." |

## Optional phone-width shot

Make the browser window narrow, or use the browser's device toolbar, and save `screenshots/13-web-narrow.png`. The checks should sit above the password card, and the buttons should still be readable. No text should run off the side of the screen.

## Before you attach the images

- The password in every shot is a sample, not a personal password.
- The rating word is large enough to read.
- The reason is in the same shot as the rating.
- The terminal shots show more than one password was checked in one run.
- The file names match the table, so a marker can find them quickly.
