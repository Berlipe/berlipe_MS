@echo off
REM Build berlip_MS for Windows using PyInstaller
cd /d "%~dp0..\.."

python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean ^
  --name berlip_MS ^
  --windowed ^
  --onefile ^
  --add-data "assets;assets" ^
  main.py

echo.
echo Build finished. Executable should be in dist\berlip_MS.exe
pause
