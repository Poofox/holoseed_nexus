#!/usr/bin/env python3
"""Generate a clean PDF of the Chocolate Flavors LLM guide."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def create_pdf():
    doc = SimpleDocTemplate(
        "C:/Users/foxAsteria/Downloads/chocolate_flavors.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1  # center
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10
    )

    elements = []

    # Title
    elements.append(Paragraph("LLM Chocolate Flavors Guide", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Table 1: Chocolate Flavors
    elements.append(Paragraph("Chocolate Flavors", heading_style))

    data1 = [
        ["Flavor", "Representative LLMs", "Key Traits (taste)"],
        ["Milk-Chocolate\n(general-purpose chat)", "GPT-4-Turbo, Claude-3-Haiku,\nGemini-1.5-Flash", "Creamy, balanced, safe,\nlow latency, cost-effective"],
        ["Dark-Chocolate\n(high-capacity, long-context)", "GPT-4-Turbo-16k, Gemini-1.5-Pro,\nLLaMA-2-70B (cluster)", "Rich, deep, strong reasoning"],
        ["Bittersweet\n(open-source, single-GPU)", "Mistral-7B-Instruct,\nMixtral-8x7B, Falcon-180B", "Good performance with fewer\nparameters, cheap to run"],
        ["White-Chocolate\n(domain-specific)", "AlphaCode, Command-R,\nJurassic-2, Claude-3-Opus", "Tuned for code, retrieval,\nor legal/medical drafting"],
        ["Gourmet Truffles\n(multimodal)", "GPT-4o, Gemini-1.5-Pro,\nLLaVA-1.5, Claude-3-Vision", "Text + image (+ audio)"],
        ["Sugar-Free\n(tiny, efficient)", "GPT-3.5-Turbo, Claude-Haiku,\nMistral-7B-Instruct-v0.2", "Very low latency, high-throughput,\ncheap per-token"],
    ]

    t1 = Table(data1, colWidths=[1.8*inch, 2.2*inch, 2.5*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a3728')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f0eb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#8b7355')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f0eb'), colors.HexColor('#ebe5dc')]),
    ]))
    elements.append(t1)

    # Table 2: Quick Pick Matrix
    elements.append(Paragraph("Quick Pick-That-Flavor Matrix", heading_style))

    data2 = [
        ["Goal", "Best Flavor", "Example Model"],
        ["Cheap, fast chat", "Milk-Chocolate", "GPT-3.5-Turbo"],
        ["On-prem, 12 GB GPU", "Bittersweet", "Mistral-7B-Instruct"],
        ["Long context (>10k)", "Dark-Chocolate", "Gemini-1.5-Pro"],
        ["Image+text Q&A", "Gourmet Truffles", "LLaVA-1.5"],
        ["Code generation", "White-Chocolate", "StarCoder-16B"],
        ["High-throughput bots", "Sugar-Free", "Claude-Haiku"],
    ]

    t2 = Table(data2, colWidths=[2*inch, 2*inch, 2*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a3728')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#8b7355')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f0eb'), colors.HexColor('#ebe5dc')]),
    ]))
    elements.append(t2)

    # Table 3: Exotic vs Dark
    elements.append(Paragraph("Exotic vs. Dark - Quick Comparison", heading_style))

    data3 = [
        ["Property", "Exotic (neg-energy)", "Dark (matter/energy)"],
        ["Gravitational sign", "Repulsive (local)", "Dark matter: attractive\nDark energy: repulsive on cosmic scales"],
        ["Energy density sign", "Negative (local)", "Positive (both)"],
        ["Observational evidence", "None (only Casimir\neffect, tiny)", "Dark matter: lensing, rotation curves\nDark energy: accelerated expansion (SN Ia)"],
        ["Typical theory context", "Wormholes, Alcubierre", "Cosmology, LCDM"],
    ]

    t3 = Table(data3, colWidths=[1.8*inch, 2*inch, 2.7*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#4a4a6a')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8e8f0'), colors.HexColor('#d8d8e8')]),
    ]))
    elements.append(t3)

    doc.build(elements)
    print("PDF created: C:/Users/foxAsteria/Downloads/chocolate_flavors.pdf")

if __name__ == "__main__":
    create_pdf()
