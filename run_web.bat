@echo off
cd /d "%~dp0public"
echo Open http://127.0.0.1:5500 in your browser.
echo The password stays in the browser. It is not uploaded.
echo Press Ctrl+C to stop the server.
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -m http.server 5500
) else (
  python -m http.server 5500
)
echo.
pause
