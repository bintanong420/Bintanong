from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_pdf(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=letter, pageCompression=0)
    width, height = letter

    # Page 1: Title and institutional policies
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "PalSU Synthetic Academic Guide 2026-2027")

    c.setFont("Helvetica", 11)
    y = height - 110
    lines = [
        "1. Institutional Policies & Enrollment Requirements",
        "Palawan State University (PalSU) undergraduate students must maintain good academic standing.",
        "A student enrolled in the Bachelor of Science in Computer Science (BSCS) program must complete",
        "all prerequisite courses before enrolling in advanced subject matter.",
        "",
        "2. Grading System & Academic Retention",
        "Passing grade is 3.0 or better. A grade of 4.0 indicates conditional failure requiring re-examination.",
        "A grade of 5.0 is a failure and requires repeating the course.",
        "",
        "3. Prerequisite Evaluation Rules",
        "Course CS311 (Software Engineering) requires CS221 (Data Structures and Algorithms) as prerequisite.",
        "Course CS411 (Thesis Guidance) requires CS311 and CS312.",
    ]
    for line in lines:
        c.drawString(72, y, line)
        y -= 20

    c.showPage()
    c.save()
    return output_path


if __name__ == "__main__":
    out = Path(__file__).parent / "synthetic_academic_guide.pdf"
    generate_pdf(out)
    print(f"Generated synthetic fixture at {out} ({out.stat().st_size} bytes)")
