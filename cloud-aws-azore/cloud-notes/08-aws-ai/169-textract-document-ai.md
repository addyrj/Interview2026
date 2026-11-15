# 169. Textract (Document AI)
# AWS: Amazon Textract
# Azure: Azure AI Document Intelligence
# हिंदी में: PDF/scan से text, table और form निकालना

---

## 🔵 Simple Definition
Textract extracts printed text, handwriting, tables and form key-values from scanned documents, invoices and IDs.
हिंदी: Textract scanned documents से text, tables और form fields निकाल देता है।

---

## 🔴 Why it Exists
Plain OCR loses structure (tables, key-value pairs).
Textract returns structured blocks with geometry and confidence.

---

## 🟢 How it Works
```
PDF/image in S3
 -> sync: analyze_document (single page image)
 -> async: start_document_analysis (multi-page PDF) -> SNS -> get_document_analysis
Response = Blocks: PAGE, LINE, WORD, TABLE, CELL, KEY_VALUE_SET
```

---

## 💻 Code / Config Example
```python
import boto3

tx = boto3.client("textract", region_name="us-east-1")

resp = tx.analyze_document(
    Document={"S3Object": {"Bucket": "my-docs", "Name": "invoice.png"}},
    FeatureTypes=["TABLES", "FORMS"],
)
lines = [b["Text"] for b in resp["Blocks"] if b["BlockType"] == "LINE"]
print("\n".join(lines))

# invoices/receipts have a dedicated API
# tx.analyze_expense(Document={...})
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Textract | Document Intelligence |
| Prebuilt models | Expense, ID, Lending | Invoice, receipt, ID, layout |
| Custom | Queries / Adapters | Custom extraction models |
| Pricing | Per page, varies by feature (approximate — check current docs) | Per page |

---

## ⚠️ Common Mistakes
❌ Mistake: Using sync API for multi-page PDFs.
✅ Correct: Use Start*/Get* async APIs for PDFs.

❌ Mistake: Trusting low-confidence values for payments.
✅ Correct: Check `Confidence`, route low scores to human review (A2I).

---

## ⚫ Interview Q&A
Q1: [Easy] Textract vs plain OCR?
A1: Textract understands tables and forms, not just text lines.

Q2: [Medium] How to process 10k PDFs?
A2: S3 event -> SQS -> worker starts async job -> SNS completion -> store JSON; throttle to service quotas.

Q3: [Hard] Build invoice automation.
A3: Textract AnalyzeExpense -> normalise fields -> validate against PO in DB -> low confidence to human review -> post to ERP; encrypt S3, audit logs.

---

## ✅ Quick Checklist
□ Async for PDFs
□ Confidence thresholds
□ PII encrypted at rest

---

## ⚡ 1-Line Summary
Textract turns scanned documents into structured data | Textract scanned documents को structured data में बदलता है।

## ➡️ Next: 170. Comprehend (NLP)
