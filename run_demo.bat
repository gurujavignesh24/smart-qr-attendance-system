@echo off
setlocal

set PYTHON_CMD=python
python --version >nul 2>&1
if errorlevel 1 set PYTHON_CMD=py

%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
  echo Python is not installed or not added to PATH.
  echo Install Python from python.org and enable Add Python to PATH.
  pause
  exit /b 1
)

echo Installing required packages...
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo Generating QR codes...
%PYTHON_CMD% generate_qr.py

echo.
echo Marking sample attendance from QR image...
%PYTHON_CMD% scan_qr.py --image qrcodes/STU001_Moukhika.png

echo.
echo Creating attendance report...
%PYTHON_CMD% attendance_report.py --html

echo.
echo Demo complete. Open attendance_report.html to view the dashboard.
pause
