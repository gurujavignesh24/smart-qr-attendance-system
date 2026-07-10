import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent
STUDENTS_FILE = BASE_DIR / "students.csv"
DATA_DIR = BASE_DIR / "data"
ATTENDANCE_FILE = DATA_DIR / "attendance.csv"
FIELDNAMES = ["date", "time", "student_id", "name", "course", "status", "source"]


def load_students():
    with STUDENTS_FILE.open(newline="", encoding="utf-8") as file:
        return {row["student_id"]: row for row in csv.DictReader(file)}


def ensure_attendance_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not ATTENDANCE_FILE.exists():
        with ATTENDANCE_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def read_attendance():
    ensure_attendance_file()
    with ATTENDANCE_FILE.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def parse_qr_data(data):
    if data.startswith("SA|"):
        parts = data.split("|", 3)
        if len(parts) == 4:
            return {
                "student_id": parts[1],
                "name": parts[2],
                "course": parts[3],
                "source": data,
            }

    try:
        payload = json.loads(data)
        if payload.get("type") != "smart_attendance_qr":
            raise ValueError("Unknown QR type")
        return {
            "student_id": payload.get("student_id", "UNKNOWN"),
            "name": payload.get("name", "Unknown Student"),
            "course": payload.get("course", "Unknown Course"),
            "source": data,
        }
    except (json.JSONDecodeError, ValueError):
        student_id = "UNKNOWN"
        name = data
        if "ID:" in data:
            student_id = data.split("ID:", 1)[1].strip().split()[0]
        if "Student:" in data:
            name = data.split("Student:", 1)[1].split("|", 1)[0].strip()
        return {
            "student_id": student_id,
            "name": name,
            "course": "Manual QR",
            "source": data,
        }


def already_marked(student_id, date_value):
    return any(
        row["student_id"] == student_id and row["date"] == date_value
        for row in read_attendance()
    )


def mark_attendance(qr_data, allow_duplicates=False):
    ensure_attendance_file()
    students = load_students()
    student = parse_qr_data(qr_data)
    roster_match = students.get(student["student_id"])
    if roster_match:
        student.update(roster_match)

    now = datetime.now()
    date_value = now.strftime("%Y-%m-%d")
    time_value = now.strftime("%H:%M:%S")

    if not allow_duplicates and already_marked(student["student_id"], date_value):
        return f'Already marked today: {student["name"]} ({student["student_id"]})'

    with ATTENDANCE_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(
            {
                "date": date_value,
                "time": time_value,
                "student_id": student["student_id"],
                "name": student["name"],
                "course": student["course"],
                "status": "Present",
                "source": student["source"],
            }
        )

    return f'Attendance marked: {student["name"]} ({student["student_id"]})'


def scan_image(image_path, allow_duplicates=False):
    detector = cv2.QRCodeDetector()
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    data, _, _ = detector.detectAndDecode(image)
    if not data:
        raise ValueError("No QR code found in the image.")

    print(mark_attendance(data, allow_duplicates=allow_duplicates))


def draw_overlay(frame, message):
    height, width = frame.shape[:2]
    cv2.rectangle(frame, (30, 30), (width - 30, height - 30), (16, 56, 79), 3)
    cv2.rectangle(frame, (0, 0), (width, 82), (16, 56, 79), -1)
    cv2.putText(frame, "Smart QR Attendance Scanner", (28, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(frame, message, (28, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (218, 235, 242), 1)
    cv2.putText(frame, "Press ESC to exit", (28, height - 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (16, 56, 79), 2)


def scan_camera(camera_index=0, allow_duplicates=False):
    detector = cv2.QRCodeDetector()
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        raise RuntimeError("Camera could not be opened. Try --image qrcodes/STU001_Moukhika.png for a no-webcam demo.")

    message = "Show a student QR code to the webcam"
    try:
        while True:
            success, frame = camera.read()
            if not success:
                message = "Waiting for camera frame..."
                continue

            data, bbox, _ = detector.detectAndDecode(frame)
            if bbox is not None:
                points = bbox.astype(int).reshape(-1, 2)
                for index in range(len(points)):
                    start = tuple(points[index])
                    end = tuple(points[(index + 1) % len(points)])
                    cv2.line(frame, start, end, (36, 173, 129), 3)

            if data:
                message = mark_attendance(data, allow_duplicates=allow_duplicates)
                draw_overlay(frame, message)
                cv2.imshow("Smart QR Attendance Scanner", frame)
                cv2.waitKey(1800)
                print(message)
                break

            draw_overlay(frame, message)
            cv2.imshow("Smart QR Attendance Scanner", frame)

            if cv2.waitKey(1) == 27:
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Scan QR codes and mark attendance.")
    parser.add_argument("--image", help="Scan a QR code from an image instead of using the webcam.")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index. Default: 0.")
    parser.add_argument("--allow-duplicates", action="store_true", help="Allow the same student to be marked more than once per day.")
    args = parser.parse_args()

    if args.image:
        scan_image(BASE_DIR / args.image, allow_duplicates=args.allow_duplicates)
    else:
        scan_camera(camera_index=args.camera, allow_duplicates=args.allow_duplicates)


if __name__ == "__main__":
    main()
