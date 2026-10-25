# 283. Build PDF Generator
# हिंदी में: PDF Generator बनाना

---

## 🔵 Simple Definition (English)
A PDF generator service creates PDF documents (invoices, receipts, reports) programmatically from dynamic data, using libraries like **PDFKit** (draw-based, low-level) or **Puppeteer** (renders HTML/CSS to PDF via headless Chrome) — run server-side so clients get a ready-made file instead of generating it themselves.

## 🔵 सरल परिभाषा (Hindi)
PDF generator service dynamic data से programmatically PDF documents (invoices, receipts, reports) बनाती है, **PDFKit** (draw-based, low-level) या **Puppeteer** (HTML/CSS को headless Chrome से PDF में render करना) जैसी libraries से — server-side चलती है ताकि clients को ready-made file मिले।

---

## 🔴 Problem it Solves
Generating consistent, professional-looking documents (invoices with company branding, tabular data, exact formatting) client-side (browser print-to-PDF) is unreliable — different browsers render differently, and you can't guarantee output for programmatic use (e.g. attaching an invoice PDF to an automated email). Server-side generation guarantees consistent output regardless of client, can be triggered by backend events (order completed → generate invoice → email it), and keeps sensitive document-generation logic off the client.

## 🔴 यह क्यों बना? (Hindi)
Consistent, professional documents (company branding, exact formatting वाले invoices) client-side (browser print-to-PDF) से reliably नहीं बन सकते — अलग browsers अलग render करते हैं, और programmatic use के लिए guarantee नहीं मिलती। Server-side generation client के बावजूद consistent output guarantee करती है, backend events से trigger हो सकती है, sensitive logic client से दूर रखती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Choose an approach: **PDFKit** (programmatic drawing — text, shapes, tables placed at exact coordinates; fast, low memory, but more code for complex layouts) OR **Puppeteer/html-pdf** (write HTML+CSS as you normally would for a webpage, then render it to PDF via headless Chrome; easier for complex/responsive layouts, but heavier — spins up a browser instance).
Step 2 → Design the document template — for PDFKit, functions that draw each section (header, line items, footer); for Puppeteer, an HTML template (often with the same templating engine used for emails).
Step 3 → Populate the template with dynamic data (order details, user info).
Step 4 → Stream the generated PDF — either directly to the HTTP response (`res.setHeader('Content-Type', 'application/pdf')` + pipe) for on-demand downloads, or to a file/buffer for storing in S3 and emailing a link.
Step 5 → For high-volume generation (e.g. monthly statements for all users), offload to a background job queue — PDF rendering (especially Puppeteer) is CPU/memory-intensive and shouldn't run synchronously in a web request handler.
Step 6 → Clean up resources explicitly — Puppeteer browser instances/pages must be closed after use, or they leak memory and file handles over time.
Step 7 → Cache generated PDFs when the underlying data hasn't changed (e.g. an already-finalized invoice never needs regenerating) to avoid redundant CPU-heavy work.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Approach चुनो: **PDFKit** (programmatic drawing) या **Puppeteer** (HTML/CSS को PDF में render)।
Step 2 → Document template design करो।
Step 3 → Template को dynamic data से populate करो।
Step 4 → Generated PDF stream करो — directly response को या file/buffer के रूप में S3 में store।
Step 5 → High-volume generation के लिए background job queue use करो।
Step 6 → Resources explicitly clean up करो — Puppeteer browser/pages close करना ज़रूरी।
Step 7 → Underlying data न बदले तो generated PDFs cache करो।

---

## 🟡 Real World Example
**Razorpay's** settlement reports (monthly breakdown of transactions, fees, payouts for merchants) are generated using Puppeteer: an internal HTML template (with charts rendered as SVG, tables of transactions) is populated with the merchant's data and rendered to PDF in a dedicated worker fleet (separate from API servers, since Puppeteer's Chrome instances are memory-hungry — each can use 100-300MB). Generation is queued via BullMQ when a merchant requests their statement, with the resulting PDF uploaded to S3 and a signed download link emailed, rather than generating it live in the HTTP request (which would time out for merchants with thousands of transactions).

## 🟡 Real Example Hindi mein
**Razorpay** के settlement reports Puppeteer से generate होते हैं: internal HTML template merchant data से populate होकर dedicated worker fleet में PDF में render होता है (API servers से अलग, क्योंकि Puppeteer memory-hungry है)। Generation BullMQ से queued होता है, resulting PDF S3 पर upload होता है, signed download link email होती है — live HTTP request में generate नहीं करते (timeout हो सकता है)।

---

## 💻 Code Example — Basic

```javascript
// basic-pdf-pdfkit.js — minimal invoice PDF using PDFKit (no browser needed, lightweight)
// npm install pdfkit
// Run: node basic-pdf-pdfkit.js  → creates invoice.pdf in current directory

const PDFDocument = require('pdfkit');
const fs = require('fs');

function generateInvoice(order) {
  const doc = new PDFDocument({ margin: 50 });
  doc.pipe(fs.createWriteStream('invoice.pdf')); // write directly to a file

  // ─── Header ─────────────────────────────────────────────────────────────
  doc.fontSize(20).text('INVOICE', { align: 'center' });
  doc.moveDown();
  doc.fontSize(10).text(`Invoice #: ${order.id}`);
  doc.text(`Date: ${new Date().toLocaleDateString()}`);
  doc.moveDown();

  // ─── Line items table (manually positioned — PDFKit is low-level) ───────
  let y = doc.y;
  doc.fontSize(10).text('Item', 50, y).text('Qty', 300, y).text('Price', 400, y);
  y += 20;
  doc.moveTo(50, y).lineTo(550, y).stroke(); // horizontal line separator
  y += 10;

  let total = 0;
  order.items.forEach((item) => {
    doc.text(item.name, 50, y);
    doc.text(String(item.qty), 300, y);
    doc.text(`₹${item.price}`, 400, y);
    total += item.qty * item.price;
    y += 20;
  });

  y += 10;
  doc.moveTo(50, y).lineTo(550, y).stroke();
  y += 10;
  doc.fontSize(12).text(`Total: ₹${total}`, 400, y);

  doc.end(); // finalize the PDF — triggers the write stream to flush
  console.log('Invoice generated: invoice.pdf');
}

generateInvoice({
  id: 1001,
  items: [
    { name: 'Wireless Mouse', qty: 1, price: 799 },
    { name: 'USB Cable', qty: 2, price: 199 },
  ],
});
```

## 💻 Code Example — Advanced

```javascript
// advanced-pdf-puppeteer.js — HTML-to-PDF with Puppeteer, resource cleanup, buffer output
// npm install puppeteer handlebars

const puppeteer = require('puppeteer');
const handlebars = require('handlebars');

const invoiceTemplate = handlebars.compile(`
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; padding: 40px; }
    h1 { color: #2c3e50; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border-bottom: 1px solid #ddd; padding: 8px; text-align: left; }
    .total { font-weight: bold; font-size: 1.2em; text-align: right; margin-top: 10px; }
  </style>
</head>
<body>
  <h1>Invoice #{{orderId}}</h1>
  <p>Date: {{date}}</p>
  <table>
    <tr><th>Item</th><th>Qty</th><th>Price</th></tr>
    {{#each items}}
    <tr><td>{{this.name}}</td><td>{{this.qty}}</td><td>₹{{this.price}}</td></tr>
    {{/each}}
  </table>
  <p class="total">Total: ₹{{total}}</p>
</body>
</html>
`);

// Puppeteer launches a real (headless) Chrome instance — expensive to start,
// so reuse ONE browser instance across many PDF generations when possible
class PdfGenerator {
  async init() {
    this.browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox'], // common flags for containerized/CI environments
    });
  }

  async generateInvoicePdf(order) {
    const total = order.items.reduce((sum, i) => sum + i.qty * i.price, 0);
    const html = invoiceTemplate({
      orderId: order.id,
      date: new Date().toLocaleDateString(),
      items: order.items,
      total,
    });

    const page = await this.browser.newPage(); // new tab, not a new browser instance
    try {
      await page.setContent(html, { waitUntil: 'networkidle0' }); // wait for render to settle
      const pdfBuffer = await page.pdf({
        format: 'A4',
        printBackground: true,
        margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' },
      });
      return pdfBuffer; // return as Buffer — caller decides: save to disk, upload to S3, or stream to response
    } finally {
      await page.close(); // ALWAYS close the page, even if generation fails — prevents memory leaks
    }
  }

  async shutdown() {
    await this.browser.close();
  }
}

module.exports = PdfGenerator;
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const PdfGenerator = require('./advanced-pdf-puppeteer');

const app = express();
const pdfGenerator = new PdfGenerator();
pdfGenerator.init(); // launch the shared browser instance once at server startup

app.get('/api/orders/:id/invoice', async (req, res) => {
  try {
    const order = {
      id: req.params.id,
      items: [{ name: 'Laptop Stand', qty: 1, price: 1299 }],
    }; // normally fetched from DB

    const pdfBuffer = await pdfGenerator.generateInvoicePdf(order);

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="invoice-${order.id}.pdf"`);
    res.send(pdfBuffer);
  } catch (err) {
    console.error('PDF generation failed:', err);
    res.status(500).json({ error: 'Failed to generate invoice' });
  }
});

// Graceful shutdown: close the browser instance when the server stops
process.on('SIGTERM', async () => {
  await pdfGenerator.shutdown();
  process.exit(0);
});

app.listen(3000, () => console.log('PDF generation API on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Launching a NEW Puppeteer browser instance for every single PDF request
✅ Correct: Launch ONE browser instance at server startup, open/close a new PAGE (tab) per generation — launching a full browser process per request is extremely slow (seconds) and memory-expensive.

```javascript
// Wrong: launches and closes a full Chrome process for every request — very slow
app.get('/invoice/:id', async (req, res) => {
  const browser = await puppeteer.launch(); // ~1-2 seconds overhead EVERY time
  const page = await browser.newPage();
  // ...
  await browser.close();
});

// Right: one shared browser, cheap per-request page creation
const browser = await puppeteer.launch(); // once, at startup
app.get('/invoice/:id', async (req, res) => {
  const page = await browser.newPage(); // fast
  // ... generate, then page.close() ...
});
```

❌ Mistake 2: Generating heavy PDFs synchronously inside the request handler for bulk operations
✅ Correct: For single on-demand downloads, synchronous generation in the handler is fine (if reasonably fast). For BULK generation (e.g. 10,000 monthly statements), use a background job queue — doing this inline would block the Event Loop and likely time out the HTTP request.

```javascript
// Wrong: generating 10,000 PDFs in a single request handler — times out, blocks everything
app.post('/generate-all-statements', async (req, res) => {
  for (const user of allUsers) { await pdfGenerator.generateInvoicePdf(user.order); }
  res.json({ done: true }); // never reached in reasonable time
});

// Right: enqueue one job per user, process in background workers
app.post('/generate-all-statements', async (req, res) => {
  for (const user of allUsers) { await pdfQueue.add('generate', { userId: user.id }); }
  res.json({ message: 'Generation started', count: allUsers.length });
});
```

---

## 🧠 Tricky Interview Question

```javascript
// Why might this leak memory over time, even though each page is correctly closed?
app.get('/invoice/:id', async (req, res) => {
  const page = await browser.newPage();
  await page.setContent(bigHtmlWithEmbeddedImages);
  const pdf = await page.pdf();
  await page.close(); // closed correctly...
  res.send(pdf);
});
// Server has been running for days under moderate load; memory usage keeps climbing.
```
Answer: Even with correct `page.close()` calls, Puppeteer/Chrome's underlying process can accumulate memory over very long uptimes due to Chrome's own internal caching, zombie renderer processes from edge-case crashes, or leaked event listeners if `page.on(...)` handlers were attached without being removed. The practical production mitigation many teams use: periodically RESTART the browser instance (e.g. every N hours or every M generations) rather than assuming a single long-lived browser process stays perfectly clean forever — treating the browser instance itself as a resource with a health-checked lifecycle, not an infinitely-reusable singleton. This is a classic "it works in a 10-minute load test but degrades over a week in production" interview gotcha.

---

## ⚫ Interview Questions + Answers

Q1: When would you choose PDFKit over Puppeteer, and vice versa?
A1: PDFKit: lightweight (no browser needed), fast, low memory — ideal for simple, highly structured documents (invoices with predictable layouts) generated at high volume where Puppeteer's overhead isn't justified. Puppeteer: renders full HTML/CSS (flexbox, grid, custom fonts, charts via SVG/Canvas) — ideal for visually complex documents where replicating the layout in PDFKit's coordinate-based drawing API would be tedious, at the cost of a heavier runtime (needs Chrome installed, more memory per instance).

Q2: How do you handle PDF generation for a very large dataset (e.g. a report with 50,000 rows) without running out of memory?
A2: Avoid building the ENTIRE HTML string (or in-memory data structure) for all 50,000 rows before rendering — for PDFKit, STREAM content page by page, writing and flushing incrementally rather than holding the whole document in memory. For Puppeteer-based HTML rendering, consider paginating the report into multiple smaller PDFs or using PDFKit instead for pure tabular data at that scale, since Puppeteer's DOM-based rendering of tens of thousands of rows can itself become a memory/performance bottleneck in the headless browser.

Q3: Why must Puppeteer's browser launch include flags like `--no-sandbox` in many server/container environments?
A3: Chrome's sandboxing feature (a security mechanism isolating renderer processes) relies on OS-level primitives that often aren't available or are restricted inside containers (Docker) or CI environments running as root without the right kernel capabilities — without disabling it via `--no-sandbox`, Puppeteer fails to launch at all in these environments. This is a common "works on my Mac, fails on the Docker image" interview/debugging scenario; the tradeoff is accepting reduced process isolation, acceptable since the content being rendered is YOUR OWN generated HTML, not arbitrary untrusted web pages.

Q4: How would you cache a generated PDF so it's not regenerated on every request for the same unchanged data?
A4: For a FINALIZED document (e.g. an invoice that's been issued and won't change), generate once, upload to S3/cloud storage, and store the resulting URL/key in your database alongside the order record — subsequent requests simply redirect to or stream the cached file instead of regenerating. For documents that CAN change (a draft report), cache with a version/hash key tied to the underlying data (similar to the Redis caching pattern), invalidating when the source data updates.

Q5: What security risks exist in HTML-to-PDF generation if user-supplied content is included in the template?
A5: If user input (e.g. a custom message field) is interpolated into the HTML without escaping, it's an XSS-style injection risk — malicious HTML/JS COULD execute within Puppeteer's rendering context (less dangerous than a browser since there's no interactive user, but still risky if the rendered page can make network requests during rendering, potentially exfiltrating data or hitting internal services via SSRF). Mitigations: use a templating engine with auto-escaping (Handlebars `{{var}}`), disable JavaScript execution during PDF rendering if not needed (`page.setJavaScriptEnabled(false)`), and restrict/validate any user-supplied content before it reaches the template.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Generating invoices, receipts, reports, certificates — any document needing consistent, server-controlled formatting
- Triggering document generation from backend events (order completion, scheduled reports) rather than client interaction

❌ Avoid when:
- Simple data export suffices (CSV/JSON) and a formatted PDF isn't actually required — PDF generation (especially Puppeteer) is comparatively expensive
- Extremely high-frequency, low-value document generation where the CPU/memory cost outweighs the benefit — consider simpler templating (plain HTML email) instead

---

## 📊 Visual Diagram
```
PDFKIT APPROACH (lightweight, draw-based)
──────────────────────────────────────────
  Data → doc.text(), doc.lineTo() calls at exact coordinates → PDF stream
  Fast, low memory, more manual layout code

PUPPETEER APPROACH (HTML-to-PDF via headless Chrome)
──────────────────────────────────────────────────────
  Data → Handlebars template → full HTML/CSS
                                     │
                                     ▼
                          ┌───────────────────┐
                          │ Shared Browser      │ (launched once at startup)
                          │  └─ new Page() ──┐  │
                          │       render HTML │  │
                          │       page.pdf()  │  │
                          │       page.close()│  │
                          └───────────────────┘  │
                                     ▼
                              PDF Buffer returned
                           (send to client / upload to S3)

BULK GENERATION (background job pattern):
  API request → enqueue N jobs → Worker pool renders each PDF → upload to S3 → notify user
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PDFKit | Low-level, draw-based PDF generation library | Low-level, draw-based PDF generation library |
| Puppeteer | Headless Chrome automation, renders HTML to PDF | HTML को PDF में render करने वाला headless Chrome tool |
| Headless Browser | Browser running without a visible UI | बिना visible UI चलने वाला browser |
| Page (Puppeteer) | A tab within a shared browser instance | Shared browser instance के अंदर एक tab |
| Buffer | In-memory binary data (the generated PDF bytes) | In-memory binary data |
| SSRF | Server-Side Request Forgery, a web security risk | Server-side request forgery, एक security risk |

---

## ⚡ 3-Line Summary
English: 1. PDFKit suits simple, high-volume structured documents (invoices); Puppeteer suits visually complex HTML/CSS-based reports at the cost of heavier resource usage. 2. Reuse a single shared Puppeteer browser instance across requests, opening/closing lightweight pages per generation, and periodically restart it to avoid long-uptime memory creep. 3. Offload bulk PDF generation to background job queues — it's CPU/memory-intensive and shouldn't run synchronously in request handlers.
Hindi: 1. PDFKit simple, high-volume structured documents के लिए सही है; Puppeteer visually complex HTML/CSS reports के लिए, heavier resource usage की कीमत पर। 2. एक shared Puppeteer browser instance reuse करो, हर generation में lightweight pages खोलो/बंद करो, periodically restart करो। 3. Bulk PDF generation को background job queues में offload करो — request handlers में synchronously मत चलाओ।

---

## ➡️ Next Topic
**284. Build CSV Import/Export** — bulk data को CSV format में import/export करना streams के साथ।
