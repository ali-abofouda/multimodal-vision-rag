"""generate_corpus_pdfs — Multi-document enterprise corpus generator.

Compiles 3 diverse, high-fidelity multimodal PDFs:
1. q3_financial_review.pdf (Financial tables + Bar chart)
2. cloud_architecture_2026.pdf (Infrastructure costs table + Donut distribution chart)
3. supply_chain_logistics.pdf (Fulfillment table + Line trend chart)
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


def _setup_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("T", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#1A365D"), spaceAfter=2),
        "subtitle": ParagraphStyle("ST", parent=styles["Normal"], fontName="Helvetica", fontSize=9.5, leading=13, textColor=colors.HexColor("#4A5568"), spaceAfter=6),
        "meta": ParagraphStyle("M", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=colors.HexColor("#718096")),
        "body": ParagraphStyle("B", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=13, textColor=colors.HexColor("#2D3748")),
        "heading": ParagraphStyle("H", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=colors.HexColor("#2B6CB0"), spaceBefore=6, spaceAfter=4),
        "foot": ParagraphStyle("F", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, textColor=colors.HexColor("#A0AEC0")),
    }


def generate_financial_pdf(output_path: str = "documents/q3_financial_review.pdf") -> str:
    """Document 1: Finance Review with Table and Bar Chart."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    st = _setup_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("Global Enterprises Inc. — Executive Financial Review", st["title"]))
    story.append(Paragraph("Q3 2026 Regional Revenue Performance & Margin Trajectory", st["subtitle"]))
    story.append(Paragraph("Domain: Corporate Finance  |  Audited: Yes  |  ID: FIN-2026-Q3-001  |  Confidential", st["meta"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=8))

    # Narrative Card
    card_text = "<b>Executive Summary:</b> Q3 consolidated revenue expanded <b>14.2% YoY</b> to <b>$362.8M</b>. APAC surpassed operating projections by 22%, while North American operations generated $136.3M against currency headwinds."
    t_card = Table([[Paragraph(card_text, st["body"])]], colWidths=[540])
    t_card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F4F8")), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E0")), ("PADDING", (0, 0), (-1, -1), 6)]))
    story.append(t_card)
    story.append(Spacer(1, 8))

    # Table
    story.append(Paragraph("Table 1: Regional Financial Performance (USD Millions)", st["heading"]))
    data = [
        ["Region", "Target ($M)", "Actual ($M)", "Variance", "Growth YoY"],
        ["North America", "145.0", "136.3", "-6.0%", "+8.4%"],
        ["EMEA", "98.5", "104.2", "+5.8%", "+12.1%"],
        ["APAC", "75.0", "91.5", "+22.0%", "+26.8%"],
        ["LATAM", "32.0", "30.8", "-3.7%", "+4.5%"],
        ["Consolidated Total", "350.5", "362.8", "+3.5%", "+14.2%"],
    ]
    t = Table(data, colWidths=[130, 95, 95, 100, 120])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F8FAFC")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E2E8F0")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # Bar Chart
    story.append(Paragraph("Visual Analytics: Regional Revenue Trajectory", st["heading"]))
    chart_path = "temp_fin_chart.png"
    fig, ax = plt.subplots(figsize=(6.5, 3.0), dpi=200)
    regions = ["North America", "EMEA", "APAC", "LATAM"]
    q2 = [125.7, 92.9, 72.1, 29.5]
    q3 = [136.3, 104.2, 91.5, 30.8]
    x = np.arange(len(regions))
    w = 0.35
    b1 = ax.bar(x - w/2, q2, w, label="Q2 2026 ($M)", color="#63B3ED", edgecolor="#2B6CB0", linewidth=0.8)
    b2 = ax.bar(x + w/2, q3, w, label="Q3 2026 ($M)", color="#1A365D", edgecolor="#0F172A", linewidth=0.8)
    for bar in b1:
        ax.annotate(f"${bar.get_height():.1f}M", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=7.5, color="#2D3748", weight="bold")
    for bar in b2:
        ax.annotate(f"${bar.get_height():.1f}M", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=7.5, color="#1A365D", weight="bold")
    ax.set_ylabel("USD Millions", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=8, weight="bold")
    ax.legend(loc="upper left", frameon=True, fontsize=7.5)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    plt.tight_layout()
    plt.savefig(chart_path, bbox_inches="tight")
    plt.close()

    story.append(RLImage(chart_path, width=6.8 * inch, height=2.9 * inch))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E0"), spaceAfter=4))
    story.append(Paragraph("* Confidential — Internal Document ID: FIN-2026-Q3-001. Audited by Corporate Finance.", st["foot"]))

    doc.build(story)
    if os.path.exists(chart_path): os.remove(chart_path)
    print(f"Generated: {output_path}")
    return output_path


def generate_cloud_pdf(output_path: str = "documents/cloud_architecture_2026.pdf") -> str:
    """Document 2: Cloud Infrastructure & AI Compute with Donut Chart."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    st = _setup_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("NextGen Enterprise Systems — Cloud & AI Infrastructure", st["title"]))
    story.append(Paragraph("2026 Budget Allocation, Cluster Scaling & Compute Breakdown", st["subtitle"]))
    story.append(Paragraph("Domain: Cloud Engineering  |  Tier: Tier-4 Data Centers  |  ID: INF-2026-AI-502  |  Internal", st["meta"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#7C3AED"), spaceAfter=8))

    # Narrative Card
    card_text = "<b>Architecture Overview:</b> Global infrastructure migrated to hybrid multi-region clusters. <b>Dedicated AI Inference (GPU Clusters)</b> represents the fastest-growing cost center at <b>42% of total spend</b> ($1.45M/mo), while Vector Database indexing (Qdrant Cloud) reduced retrieval p99 latency to <b>24ms</b>."
    t_card = Table([[Paragraph(card_text, st["body"])]], colWidths=[540])
    t_card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F3FF")), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#DDD6FE")), ("PADDING", (0, 0), (-1, -1), 6)]))
    story.append(t_card)
    story.append(Spacer(1, 8))

    # Table
    story.append(Paragraph("Table 1: Monthly Infrastructure Expense Breakdown (USD)", st["heading"]))
    data = [
        ["Resource Layer", "Active Units", "Monthly Cost", "P99 Latency", "Utilization"],
        ["GPU Inference Clusters", "48x H100 Nodes", "$1,450,000", "85 ms", "91.2%"],
        ["Vector Database (Qdrant)", "8-Node Clustered", "$185,000", "24 ms", "74.8%"],
        ["Object Storage (Blobs)", "4.2 Petabytes", "$92,000", "12 ms", "62.0%"],
        ["Edge Ingress & Gateway", "12 Edge POPs", "$68,000", "8 ms", "88.4%"],
        ["Total Infrastructure", "Consolidated", "$1,795,000", "N/A", "82.5%"],
    ]
    t = Table(data, colWidths=[140, 100, 100, 100, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4C1D95")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDD6FE")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#FAF5FF")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EDE9FE")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # Donut Chart
    story.append(Paragraph("Visual Analytics: Cloud Spend Budget Distribution (%)", st["heading"]))
    chart_path = "temp_cloud_chart.png"
    fig, ax = plt.subplots(figsize=(6.5, 3.0), dpi=200)
    labels = ["GPU Clusters (42%)", "Vector DB (28%)", "Storage (18%)", "Edge Gateway (12%)"]
    sizes = [42, 28, 18, 12]
    pie_colors = ["#7C3AED", "#A78BFA", "#C4B5FD", "#DDD6FE"]
    wedges, texts = ax.pie(sizes, labels=labels, colors=pie_colors, startangle=140, textprops=dict(color="#1F2937", fontsize=8, weight="bold"), wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
    ax.set_title("2026 Resource Allocation by Cost Category", fontsize=10, fontweight="bold", color="#4C1D95", pad=8)
    plt.tight_layout()
    plt.savefig(chart_path, bbox_inches="tight")
    plt.close()

    story.append(RLImage(chart_path, width=6.8 * inch, height=2.9 * inch))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#DDD6FE"), spaceAfter=4))
    story.append(Paragraph("* Confidential — Internal Document ID: INF-2026-AI-502. Cloud Architecture Review Board.", st["foot"]))

    doc.build(story)
    if os.path.exists(chart_path): os.remove(chart_path)
    print(f"Generated: {output_path}")
    return output_path


def generate_logistics_pdf(output_path: str = "documents/supply_chain_logistics.pdf") -> str:
    """Document 3: Supply Chain Operations with Multi-line Trend Chart."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    st = _setup_styles()
    story = []

    # Title & Metadata
    story.append(Paragraph("Apex Logistics Worldwide — Supply Chain Operations", st["title"]))
    story.append(Paragraph("Freight Modal Efficiency, Transit Delays & Fulfillment KPI Report", st["subtitle"]))
    story.append(Paragraph("Domain: Global Logistics  |  Network: 32 Distribution Hubs  |  ID: SCM-2026-OPS-810  |  Restricted", st["meta"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#059669"), spaceAfter=8))

    # Narrative Card
    card_text = "<b>Operations Summary:</b> Ocean transit lead times expanded significantly during Weeks 4-6 due to port congestion, peaking at <b>28.4 days</b>. Conversely, priority Air Cargo maintained reliable delivery at <b>4.2 days average</b> with a <b>99.1% on-time fulfillment rate</b>."
    t_card = Table([[Paragraph(card_text, st["body"])]], colWidths=[540])
    t_card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#A7F3D0")), ("PADDING", (0, 0), (-1, -1), 6)]))
    story.append(t_card)
    story.append(Spacer(1, 8))

    # Table
    story.append(Paragraph("Table 1: Regional Warehouse Fulfillment Performance", st["heading"]))
    data = [
        ["Logistics Hub", "Weekly Volume", "On-Time Rate", "Avg Processing", "Backlog Units"],
        ["Rotterdam Hub", "142,000 TEU", "94.2%", "18.4 hrs", "2,150"],
        ["Singapore Hub", "215,000 TEU", "98.5%", "12.1 hrs", "840"],
        ["Los Angeles Hub", "185,000 TEU", "88.6%", "26.8 hrs", "5,420"],
        ["Dubai Cargo Village", "95,000 TEU", "99.1%", "8.2 hrs", "310"],
        ["Global Network", "637,000 TEU", "95.1%", "16.4 hrs", "8,720"],
    ]
    t = Table(data, colWidths=[140, 100, 100, 100, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065F46")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A7F3D0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F0FDF4")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D1FAE5")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # Line Chart
    story.append(Paragraph("Visual Analytics: Transit Delay Trajectory by Freight Mode (Days)", st["heading"]))
    chart_path = "temp_log_chart.png"
    fig, ax = plt.subplots(figsize=(6.5, 3.0), dpi=200)
    weeks = [f"W{i}" for i in range(1, 9)]
    ocean_delays = [14.2, 16.5, 21.0, 27.5, 28.4, 25.1, 19.8, 16.2]
    air_delays = [3.8, 4.1, 4.0, 4.5, 4.4, 4.2, 3.9, 4.1]
    ax.plot(weeks, ocean_delays, marker='o', linewidth=2, color="#059669", label="Ocean Freight Transit (Days)")
    ax.plot(weeks, air_delays, marker='s', linewidth=2, color="#D97706", linestyle='--', label="Air Cargo Transit (Days)")
    for i, txt in enumerate(ocean_delays):
        ax.annotate(f"{txt}d", (weeks[i], ocean_delays[i]), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=7.5, color="#065F46", weight='bold')
    ax.set_ylabel("Transit Lead Time (Days)", fontsize=8)
    ax.legend(loc="upper left", frameon=True, fontsize=7.5)
    ax.grid(True, linestyle="--", alpha=0.3)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    plt.tight_layout()
    plt.savefig(chart_path, bbox_inches="tight")
    plt.close()

    story.append(RLImage(chart_path, width=6.8 * inch, height=2.9 * inch))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#A7F3D0"), spaceAfter=4))
    story.append(Paragraph("* Restricted — Internal Document ID: SCM-2026-OPS-810. Global Logistics Oversight.", st["foot"]))

    doc.build(story)
    if os.path.exists(chart_path): os.remove(chart_path)
    print(f"Generated: {output_path}")
    return output_path


def generate_all_corpus():
    os.makedirs("documents", exist_ok=True)
    generate_financial_pdf("documents/q3_financial_review.pdf")
    generate_cloud_pdf("documents/cloud_architecture_2026.pdf")
    generate_logistics_pdf("documents/supply_chain_logistics.pdf")
    print("[*] All 3 multi-modal enterprise PDFs compiled successfully in documents/.")


if __name__ == "__main__":
    generate_all_corpus()
