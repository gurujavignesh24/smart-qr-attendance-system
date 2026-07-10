import csv
import shutil
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
STUDENTS_FILE = BASE_DIR / "students.csv"
QR_DIR = BASE_DIR / "qrcodes"
BADGE_DIR = QR_DIR / "badges"
SAMPLE_QR = BASE_DIR / "student_qr.png"
SAMPLE_BADGE = BASE_DIR / "student_pass.png"
FONT_FILE = Path("C:/Windows/Fonts/arial.ttf")


def load_students():
    with STUDENTS_FILE.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def qr_payload(student):
    return f'SA|{student["student_id"]}|{student["name"]}|{student["course"]}'


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def make_badge(student, qr_image):
    badge_width = 760
    badge_height = 980
    background = Image.new("RGB", (badge_width, badge_height), "#f6f8fb")
    draw = ImageDraw.Draw(background)

    title_font = ImageFont.truetype(str(FONT_FILE), 44) if FONT_FILE.exists() else ImageFont.load_default()
    label_font = ImageFont.truetype(str(FONT_FILE), 24) if FONT_FILE.exists() else ImageFont.load_default()
    small_font = ImageFont.truetype(str(FONT_FILE), 20) if FONT_FILE.exists() else ImageFont.load_default()

    draw.rounded_rectangle((42, 42, badge_width - 42, badge_height - 42), radius=36, fill="#ffffff", outline="#dce4ee", width=3)
    draw.rounded_rectangle((42, 42, badge_width - 42, 188), radius=36, fill="#10384f")
    draw.rectangle((42, 118, badge_width - 42, 188), fill="#10384f")

    title = "Smart Attendance Pass"
    title_width, _ = text_size(draw, title, title_font)
    draw.text(((badge_width - title_width) / 2, 82), title, fill="#ffffff", font=title_font)

    qr_box_size = 520
    qr_image = qr_image.resize((qr_box_size, qr_box_size), resample=Image.Resampling.NEAREST)
    qr_x = (badge_width - qr_box_size) // 2
    qr_y = 242
    draw.rounded_rectangle((qr_x - 22, qr_y - 22, qr_x + qr_box_size + 22, qr_y + qr_box_size + 22), radius=28, fill="#edf4f8")
    background.paste(qr_image, (qr_x, qr_y))

    name = student["name"]
    name_width, _ = text_size(draw, name, title_font)
    draw.text(((badge_width - name_width) / 2, 810), name, fill="#102a43", font=title_font)

    details = f'{student["student_id"]}  |  {student["course"]}'
    details_width, _ = text_size(draw, details, label_font)
    draw.text(((badge_width - details_width) / 2, 870), details, fill="#52616f", font=label_font)

    footer = "Scan this QR code to mark attendance"
    footer_width, _ = text_size(draw, footer, small_font)
    draw.text(((badge_width - footer_width) / 2, 925), footer, fill="#6b7a8f", font=small_font)

    return background


def generate_qr_codes():
    QR_DIR.mkdir(exist_ok=True)
    BADGE_DIR.mkdir(exist_ok=True)
    students = load_students()

    for index, student in enumerate(students):
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=16,
            border=4,
        )
        qr.add_data(qr_payload(student))
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="#000000", back_color="#ffffff").convert("RGB")
        badge = make_badge(student, qr_image)

        safe_name = student["name"].replace(" ", "_")
        output_file = QR_DIR / f'{student["student_id"]}_{safe_name}.png'
        badge_file = BADGE_DIR / f'{student["student_id"]}_{safe_name}_pass.png'
        qr_image.save(output_file)
        badge.save(badge_file)

        if index == 0:
            shutil.copyfile(output_file, SAMPLE_QR)
            shutil.copyfile(badge_file, SAMPLE_BADGE)

        print(f"Generated: {output_file.name}")
        print(f"Generated: badges/{badge_file.name}")

    print(f"\nDone. Sample QR saved as: {SAMPLE_QR.name}")
    print(f"Sample pass saved as: {SAMPLE_BADGE.name}")


if __name__ == "__main__":
    generate_qr_codes()
