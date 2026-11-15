"""Build PDF Generator: invoice PDF with reportlab, served by FastAPI. pip install reportlab fastapi httpx"""
from __future__ import annotations

import io
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.testclient import TestClient
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


@dataclass
class Item:
    name: str
    qty: int
    price: float


def build_invoice(number: str, customer: str, items: list[Item], gst_rate: float = 0.18) -> bytes:
    buf = io.BytesIO()  # build in memory, no temp files
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Invoice {number}")
    styles = getSampleStyleSheet()
    subtotal = sum(i.qty * i.price for i in items)
    gst = round(subtotal * gst_rate, 2)
    rows = [["Item", "Qty", "Price", "Amount"]]
    rows += [[i.name, i.qty, f"{i.price:.2f}", f"{i.qty * i.price:.2f}"] for i in items]
    rows += [["", "", "Subtotal", f"{subtotal:.2f}"], ["", "", "GST 18%", f"{gst:.2f}"],
             ["", "", "Total", f"{subtotal + gst:.2f}"]]
    table = Table(rows, colWidths=[200, 50, 80, 80])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                               ("GRID", (0, 0), (-1, len(items)), 0.5, colors.grey),
                               ("ALIGN", (1, 0), (-1, -1), "RIGHT")]))
    doc.build([Paragraph(f"Invoice {number}", styles["Title"]),
               Paragraph(f"Billed to: {customer}", styles["Normal"]), Spacer(1, 12), table])
    return buf.getvalue()


app = FastAPI()


@app.get("/invoice/{number}")
def invoice(number: str) -> Response:
    pdf = build_invoice(number, "Asha Traders", [Item("Keyboard", 2, 1499.0), Item("Mouse", 1, 599.5)])
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="invoice-{number}.pdf"'})


if __name__ == "__main__":
    pdf = build_invoice("INV-001", "Asha", [Item("Keyboard", 2, 1499.0)])
    print(pdf[:8], len(pdf) > 1000, pdf.rstrip().endswith(b"%%EOF"))
    assert pdf.startswith(b"%PDF-")
    r = TestClient(app).get("/invoice/INV-9")
    print(r.status_code, r.headers["content-type"], r.headers["content-disposition"])
    assert r.content.startswith(b"%PDF-")
    print("all ok")
