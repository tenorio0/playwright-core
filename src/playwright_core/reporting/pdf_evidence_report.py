from datetime import datetime
from pathlib import Path
from typing import Any
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PdfEvidenceReport:
    def __init__(self, output_path: str) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def build(self, execution_data: list[dict[str, Any]]) -> Path:
        document = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        body_style = styles["BodyText"]
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#1F4E79"),
            spaceAfter=10,
        )

        story = [
            Paragraph("Playwright Core Evidence Report", title_style),
            Spacer(1, 0.4 * cm),
            Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                body_style,
            ),
            Spacer(1, 0.6 * cm),
        ]

        summary_data = [["Metric", "Value"]]
        summary_data.append(["Total tests", str(len(execution_data))])
        summary_data.append(["Passed", str(sum(1 for item in execution_data if item["status"] == "passed"))])
        summary_data.append(["Failed", str(sum(1 for item in execution_data if item["status"] == "failed"))])
        summary_data.append(["Skipped", str(sum(1 for item in execution_data if item["status"] == "skipped"))])

        summary_table = Table(summary_data, colWidths=[7 * cm, 7 * cm])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.extend([summary_table, Spacer(1, 0.8 * cm)])

        for index, item in enumerate(execution_data, start=1):
            story.append(Paragraph(f"Test {index}: {item['name']}", subtitle_style))

            details = [
                ["Status", item["status"].upper()],
                ["Duration", f"{item['duration_seconds']:.2f} seconds"],
            ]
            if item.get("error_message"):
                details.append(["Error", item["error_message"]])

            details_table = Table(details, colWidths=[4 * cm, 11 * cm])
            details_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F6F9")),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("PADDING", (0, 0), (-1, -1), 6),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.extend([details_table, Spacer(1, 0.3 * cm)])

            evidence_steps = item.get("evidence_steps") or []
            available_steps = [
                step for step in evidence_steps if Path(step.get("screenshot_path", "")).exists()
            ]
            if available_steps:
                story.append(Paragraph("Evidence Steps", body_style))
                story.append(Spacer(1, 0.2 * cm))
                for step_index, step in enumerate(available_steps, start=1):
                    story.append(Paragraph(f"Step {step_index}: {step['description']}", body_style))
                    story.append(Spacer(1, 0.15 * cm))
                    story.append(Image(step["screenshot_path"], width=16 * cm, height=9 * cm))
                    story.append(Spacer(1, 0.4 * cm))
            else:
                story.append(Paragraph("No screenshot evidence available.", body_style))
                story.append(Spacer(1, 0.6 * cm))

        document.build(story)
        return self.output_path


def build_safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_").lower() or "report"


def build_procedural_report_path(
    reports_dir: str | Path,
    task_name: str,
    test_name: str,
) -> Path:
    report_directory = Path(reports_dir) / build_safe_name(task_name)
    report_directory.mkdir(parents=True, exist_ok=True)

    existing_indexes: list[int] = []
    for existing_file in report_directory.glob("*.pdf"):
        prefix = existing_file.stem.split("_", 1)[0]
        if prefix.isdigit():
            existing_indexes.append(int(prefix))

    next_index = max(existing_indexes, default=0) + 1
    safe_test_name = build_safe_name(test_name)
    file_name = f"{next_index:03d}_{build_safe_name(task_name)}_{safe_test_name}.pdf"
    return report_directory / file_name
