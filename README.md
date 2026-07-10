# Smart QR Code-Based Attendance System

A Python-based attendance system that generates QR codes for students, scans the QR code using a webcam or image file, and stores attendance records automatically.

## Project Overview

Manual attendance takes time and can lead to errors. This project solves that problem by using QR codes for quick and accurate attendance marking. Each student gets a unique QR code. When the QR code is scanned, the system records the student's attendance with date and time.

## Features

- Generate unique QR codes for students
- Scan QR codes using webcam
- Scan QR codes from image files for quick demo
- Store attendance records in CSV format
- Prevent duplicate attendance for the same student on the same day
- Generate a simple HTML attendance report
- Includes sample student data for testing

## Technologies Used

- Python
- OpenCV
- QR Code library
- Pillow
- CSV file handling
- HTML and CSS for attendance report

## Folder Structure

```text
smart_qr_attendance_system/
├── attendance_report.py
├── generate_qr.py
├── scan_qr.py
├── students.csv
├── requirements.txt
├── run_demo.bat
├── student_qr.png
├── student_pass.png
├── qrcodes/
│   └── badges/
└── README.md
```

## How to Run

### 1. Install Python

Install Python from:

```text
https://www.python.org/downloads/
```

While installing, select:

```text
Add Python to PATH
```

### 2. Install Required Packages

Open the project folder in Command Prompt and run:

```bash
pip install -r requirements.txt
```

If `python` or `pip` does not work, try:

```bash
py -m pip install -r requirements.txt
```

### 3. Generate QR Codes

```bash
python generate_qr.py
```

This creates student QR codes in the `qrcodes` folder.

### 4. Mark Attendance Using Webcam

```bash
python scan_qr.py
```

Show a generated QR code to the webcam. The system will scan it and mark attendance.

### 5. Mark Attendance Without Webcam

```bash
python scan_qr.py --image qrcodes/STU001_Moukhika.png
```

This is useful for a quick demo.

### 6. Generate Attendance Report

```bash
python attendance_report.py --html
```

Open `attendance_report.html` in a browser to view the report.

## Fast Demo on Windows

Double-click:

```text
run_demo.bat
```

This will install packages, generate QR codes, mark sample attendance, and create the HTML report.

## Sample Output

The attendance record stores:

- Date
- Time
- Student ID
- Student name
- Course
- Attendance status

Example:

## 📊 Attendance Report

![Attendance Report](https://github.com/gurujavignesh24/smart-qr-attendance-system/raw/main/marked%20present.png)

## 📱 QR Attendance Pass

![QR Pass](https://github.com/gurujavignesh24/smart-qr-attendance-system/blob/main/qr.png)

