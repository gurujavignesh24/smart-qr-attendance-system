import argparse
import csv
import html
from collections import Counter
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ATTENDANCE_FILE = BASE_DIR / "data" / "attendance.csv"
REPORT_FILE = BASE_DIR / "attendance_report.html"


def load_rows():
    if not ATTENDANCE_FILE.exists():
        return []
    with ATTENDANCE_FILE.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def filter_rows(rows, date_value):
    if not date_value:
        return rows
    return [row for row in rows if row["date"] == date_value]


def print_report(rows):
    if not rows:
        print("No attendance records found yet.")
        return

    print("\nSmart QR Attendance Report")
    print("-" * 72)
    print(f'{"Date":<12} {"Time":<10} {"ID":<10} {"Name":<18} {"Course":<22} Status')
    print("-" * 72)
    for row in rows:
        print(f'{row["date"]:<12} {row["time"]:<10} {row["student_id"]:<10} {row["name"]:<18} {row["course"]:<22} {row["status"]}')


def build_html(rows):
    total_scans = len(rows)
    unique_students = len({row["student_id"] for row in rows})
    course_counts = Counter(row["course"] for row in rows)
    latest_date = max((row["date"] for row in rows), default="No records")
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    course_cards = "\n".join(
        f"""
        <div class="mini-card">
          <span>{html.escape(course)}</span>
          <strong>{count}</strong>
        </div>
        """
        for course, count in course_counts.items()
    ) or '<div class="empty">No course data yet</div>'

    table_rows = "\n".join(
        f"""
        <tr>
          <td>{html.escape(row["date"])}</td>
          <td>{html.escape(row["time"])}</td>
          <td>{html.escape(row["student_id"])}</td>
          <td>{html.escape(row["name"])}</td>
          <td>{html.escape(row["course"])}</td>
          <td><span class="status">{html.escape(row["status"])}</span></td>
        </tr>
        """
        for row in rows
    ) or '<tr><td colspan="6" class="empty">No attendance records found.</td></tr>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart QR Attendance Report</title>
  <style>
    :root {{
      --ink: #102a43;
      --muted: #627386;
      --line: #d9e2ec;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-dark: #10384f;
      --bg: #f4f7fb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      background: var(--accent-dark);
      color: white;
      padding: 32px 24px;
    }}
    .wrap {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 0;
      color: #d7e7ee;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin: 24px 0;
    }}
    .card, .mini-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .card span, .mini-card span {{
      display: block;
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 8px;
    }}
    .card strong {{
      display: block;
      font-size: 34px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 16px;
      align-items: start;
    }}
    .mini-card {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 10px;
    }}
    .mini-card strong {{
      color: var(--accent);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      text-align: left;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      font-size: 14px;
    }}
    th {{
      color: var(--muted);
      background: #f8fafc;
      font-weight: 700;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .status {{
      display: inline-block;
      color: #065f46;
      background: #d1fae5;
      border-radius: 999px;
      padding: 5px 10px;
      font-weight: 700;
      font-size: 12px;
    }}
    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 24px;
    }}
    footer {{
      color: var(--muted);
      padding: 22px 0 36px;
      font-size: 13px;
    }}
    @media (max-width: 760px) {{
      .stats, .grid {{
        grid-template-columns: 1fr;
      }}
      table {{
        display: block;
        overflow-x: auto;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>Smart QR Attendance Report</h1>
      <p class="subtitle">Generated from local CSV attendance records</p>
    </div>
  </header>
  <main class="wrap">
    <section class="stats">
      <div class="card"><span>Total attendance scans</span><strong>{total_scans}</strong></div>
      <div class="card"><span>Unique students present</span><strong>{unique_students}</strong></div>
      <div class="card"><span>Latest attendance date</span><strong>{html.escape(latest_date)}</strong></div>
    </section>
    <section class="grid">
      <aside>
        {course_cards}
      </aside>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Student ID</th>
            <th>Name</th>
            <th>Course</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {table_rows}
        </tbody>
      </table>
    </section>
  </main>
  <footer class="wrap">Generated at {generated_at}</footer>
</body>
</html>
"""


def save_html_report(rows):
    REPORT_FILE.write_text(build_html(rows), encoding="utf-8")
    print(f"HTML report created: {REPORT_FILE.name}")


def main():
    parser = argparse.ArgumentParser(description="View attendance records and create an HTML report.")
    parser.add_argument("--date", help="Filter by date in YYYY-MM-DD format.")
    parser.add_argument("--html", action="store_true", help="Create attendance_report.html.")
    args = parser.parse_args()

    rows = filter_rows(load_rows(), args.date)
    print_report(rows)
    if args.html:
        save_html_report(rows)


if __name__ == "__main__":
    main()
