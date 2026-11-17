"""generate_sample_pdf — High-fidelity enterprise report PDF generator.

Uses ReportLab and Matplotlib to create an executive-grade document featuring:
- Corporate branding and structured header metadata
- Formatted narrative summary with styled bounding card
- ReportLab Table with professional typography and alternating fills
- Embedded high-res comparative bar chart with data labels and legend
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _generate_chart_image(chart_path: str = "temp_chart.png") -> str:
    """Generate a crisp, publication-quality regional revenue comparison chart."""
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=200)

    regions = ["North America", "EMEA", "APAC", "LATAM"]
    q2_actual = [125.7, 92.9, 72.1, 29.5]
    q3_actual = [136.3, 104.2, 91.5, 30.8]

    x = np.arange(len(regions))
    width = 0.35

    bars1 = ax.bar(x - width / 2, q2_actual, width, label="Q2 2026 ($M)", color="#63B3ED", edgecolor="#2B6CB0", linewidth=0.8)
    bars2 = ax.bar(x + width / 2, q3_actual, width, label="Q3 2026 ($M)", color="#1A365D", edgecolor="#0F172A", linewidth=0.8)

    # Add numeric labels on top of bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f"${height:.1f}M",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7.5, color="#2D3748", weight="bold")

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f"${height:.1f}M",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7.5, color="#1A365D", weight="bold")

    ax.set_title("Quarter-over-Quarter Regional Revenue Growth Trajectory", fontsize=10.5, fontweight="bold", color="#1A365D", pad=12)
    ax.set_ylabel("Revenue (USD Millions)", fontsize=8.5, color="#4A5568")
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=8.5, color="#2D3748", weight="semibold")
    ax.legend(loc="upper left", frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E0", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    # Clean borders
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#CBD5E0")

    plt.tight_layout()
    plt.savefig(chart_path, bbox_inches="tight")
    plt.close()
    return chart_path


def generate_report(output_path: str = "sample_document.pdf") -> str:
    """Compile executive PDF with structured layout, styled table, and embedded chart."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=3,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=10,
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#718096"),
    )
    body_style = ParagraphStyle(
        "CardBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=8,
        spaceAfter=6,
    )

    story = []

    # 1. Header & Title Block
    story.append(Paragraph("Global Enterprises Inc. — Executive Review", title_style))
    story.append(Paragraph("Q3 2026 Regional Performance & Revenue Breakdown", subtitle_style))
    story.append(Paragraph("Date: Q3 2026  |  Audited: Yes  |  Classification: Internal Confidential  |  ID: GBL-Q3-REV-981", meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

    # 2. Executive Narrative Summary Card
    summary_text = (
        "<b>Executive Summary:</b> During Q3 2026, global operations experienced an aggregate revenue expansion of "
        "<b>14.2% YoY</b>. Supply chain realignments in <b>APAC</b> produced an unexpected <b>22.0% surge</b> in operating margin, "
        "while North American expansion achieved 94% of adjusted targets despite currency headwinds. "
        "All figures reflect audited management accounting conversions."
    )
    summary_table = Table([[Paragraph(summary_text, body_style)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F4F8")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # 3. Financial Performance Table
    story.append(Paragraph("Table 1: Regional Financial Performance (USD Millions)", section_heading))
    table_data = [
        ["Region", "Target ($M)", "Actual ($M)", "Variance", "Growth YoY"],
        ["North America", "145.0", "136.3", "-6.0%", "+8.4%"],
        ["EMEA", "98.5", "104.2", "+5.8%", "+12.1%"],
        ["APAC", "75.0", "91.5", "+22.0%", "+26.8%"],
        ["LATAM", "32.0", "30.8", "-3.7%", "+4.5%"],
        ["Total Consolidated", "350.5", "362.8", "+3.5%", "+14.2%"],
    ]
    t = Table(table_data, colWidths=[130, 95, 95, 100, 120])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F8FAFC")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E2E8F0")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # 4. Embedded Bar Chart
    story.append(Paragraph("Visual Analytics: Regional Revenue Trajectory", section_heading))
    chart_file = _generate_chart_image("temp_chart.png")
    story.append(RLImage(chart_file, width=6.8 * inch, height=3.0 * inch))
    story.append(Spacer(1, 8))

    # 5. Footer and Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E0"), spaceAfter=6))
    footnote_text = (
        "* Confidential — Internal Corporate Document ID: GBL-2026-Q3-REV-981. "
        "Generated for AI Document Understanding & Multimodal RAG benchmarking."
    )
    story.append(Paragraph(footnote_text, ParagraphStyle("Foot", parent=styles["Normal"], fontSize=7.5, textColor=colors.HexColor("#A0AEC0"))))

    doc.build(story)

    # Clean up temporary chart image
    if os.path.exists(chart_file):
        os.remove(chart_file)

    print(f"[*] Executive multi-modal PDF created successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_report()
