"""Rendu PDF d'un devis (reportlab)."""

from __future__ import annotations

from datetime import date

from . import QuoteDraft


def render_quote_pdf(
    draft: QuoteDraft,
    *,
    project_name: str = "",
    client_name: str = "",
    tva_rate: float = 0.20,
) -> bytes:
    """Génère un PDF A4 du devis et retourne ses octets."""
    # Imports paresseux : reportlab n'est requis que pour la génération PDF.
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=f"Devis {draft.reference}")
    styles = getSampleStyleSheet()
    elements: list[object] = []

    elements.append(Paragraph(f"<b>DEVIS {draft.reference}</b>", styles["Title"]))
    elements.append(Paragraph(f"Date : {date.today().isoformat()}", styles["Normal"]))
    if project_name:
        elements.append(Paragraph(f"Projet : {project_name}", styles["Normal"]))
    if client_name:
        elements.append(Paragraph(f"Client : {client_name}", styles["Normal"]))
    elements.append(Spacer(1, 8 * mm))

    header = ["#", "Désignation", "Unité", "Qté", "PU HT (€)", "Total HT (€)"]
    rows: list[list[str]] = [header]
    for i, line in enumerate(draft.lines, start=1):
        rows.append(
            [
                str(i),
                line.designation,
                line.unit,
                f"{line.quantity:g}",
                f"{line.unit_price:,.2f}",
                f"{line.total:,.2f}",
            ]
        )

    total_ht = draft.total_ht
    tva = round(total_ht * tva_rate, 2)
    rows.append(["", "", "", "", "Total HT", f"{total_ht:,.2f}"])
    rows.append(["", "", "", "", f"TVA {tva_rate * 100:.0f}%", f"{tva:,.2f}"])
    rows.append(["", "", "", "", "Total TTC", f"{total_ht + tva:,.2f}"])

    table = Table(rows, colWidths=[10 * mm, 70 * mm, 18 * mm, 18 * mm, 27 * mm, 27 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6feb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -4), 0.4, colors.grey),
                ("LINEABOVE", (4, -3), (-1, -3), 0.8, colors.black),
                ("FONTNAME", (4, -1), (-1, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -4), [colors.white, colors.HexColor("#f4f6fb")]),
            ]
        )
    )
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue()
