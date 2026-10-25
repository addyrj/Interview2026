# 284. Build CSV Import/Export
# हिंदी में: CSV Import/Export बनाना

---

## 🔵 Simple Definition (English)
CSV import/export lets users bulk-upload data (products, contacts) via a CSV file that gets parsed and validated row-by-row into your database, and bulk-download data as CSV for use in Excel/Sheets. Production implementations use **streaming** parsers so files with hundreds of thousands of rows don't load entirely into memory.

## 🔵 सरल परिभाषा (Hindi)
CSV import/export users को CSV file के through bulk data (products, contacts) upload करने देता है जो row-by-row parse/validate होकर database में जाता है, और bulk data को CSV में download करने देता है Excel/Sheets में use के लिए। Production implementations **streaming** parsers use करते हैं ताकि लाखों rows वाली files पूरी memory में load न हों।

---

## 🔴 Problem it Solves
Manually entering hundreds/thousands of records through a UI form is impractical — bulk operations need a way to move data in and out in a universally-compatible format. Naively reading an entire CSV file into memory (`fs.readFileSync` + split by newlines) works for small files but crashes or severely degrades performance for large ones (a 500MB CSV loaded fully into memory can exceed Node's default heap limits). Streaming parsers process the file chunk-by-chunk, keeping memory usage constant regardless of file size.

## 🔴 यह क्यों बना? (Hindi)
UI form से manually हज़ारों records enter करना impractical है — bulk operations को universally-compatible format में data move करने का तरीका चाहिए। पूरी CSV file memory में naively load करना (`readFileSync`) छोटी files के लिए ठीक है पर बड़ी files के लिए crash/slow हो जाता है। Streaming parsers file को chunk-by-chunk process करते हैं, memory usage file size के बावजूद constant रहता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Import**: accept a CSV file upload (via Multer), stream it through a CSV parser (`csv-parser`, `fast-csv`) that emits one JS object per row as it reads.
Step 2 → Validate each row against a schema (required fields, correct types) — collect errors per row rather than failing the entire import on one bad row.
Step 3 → Batch-insert valid rows into the database (e.g. 500 rows per `INSERT` batch) rather than one-row-at-a-time inserts, which would be extremely slow for large files.
Step 4 → Return a summary: total rows processed, successes, failures with row numbers and reasons — critical for users to fix and re-upload bad rows.
Step 5 → For very large imports, process asynchronously via a job queue, returning a job ID immediately and letting the user poll/get notified on completion.
Step 6 → **Export**: query the database (ideally with a cursor/streaming query rather than loading all results into memory at once), transform each row, and stream it out as CSV directly to the HTTP response using a CSV stringifier.
Step 7 → Set correct response headers (`Content-Type: text/csv`, `Content-Disposition: attachment; filename=...`) so browsers trigger a file download.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Import**: CSV file upload accept करो (Multer), streaming parser से एक-एक row object बनाओ।
Step 2 → हर row schema के against validate करो — errors collect करो, पूरा import fail मत करो।
Step 3 → Valid rows को batch-insert करो (जैसे 500 rows per batch)।
Step 4 → Summary return करो: total, successes, failures row numbers के साथ।
Step 5 → बहुत बड़े imports के लिए job queue use करो।
Step 6 → **Export**: DB query करो (streaming/cursor से), row transform करो, CSV के रूप में response को stream करो।
Step 7 → सही response headers set करो file download trigger के लिए।

---

## 🟡 Real World Example
**Zomato's** restaurant bulk-menu-upload feature lets restaurant owners upload a CSV of menu items (name, price, category, availability) instead of adding each item manually through the UI — handling files with up to 5,000 rows. The import pipeline streams the file, validates each row (rejecting rows with negative prices or missing names), batch-inserts valid rows in chunks of 200, and returns a downloadable "error report" CSV listing exactly which rows failed and why, so the owner can fix just those rows rather than redoing the whole upload.

## 🟡 Real Example Hindi mein
**Zomato** का restaurant bulk-menu-upload feature owners को CSV upload करने देता है (name, price, category, availability) manually add करने के बजाय — 5,000 rows तक handle करता है। Import pipeline file stream करता है, हर row validate करता है, 200 rows के chunks में batch-insert करता है, "error report" CSV return करता है जिससे owner सिर्फ failed rows fix कर सके।

---

## 💻 Code Example — Basic

```javascript
// basic-csv-import.js — minimal streaming CSV parse
// npm install csv-parser
// Run: node basic-csv-import.js  (create a sample.csv with: name,price\nMouse,799\nKeyboard,1999)

const fs = require('fs');
const csv = require('csv-parser');

const results = [];

fs.createReadStream('sample.csv')
  .pipe(csv()) // parses CSV rows into objects using the header row as keys
  .on('data', (row) => {
    // This fires once PER ROW, as it's parsed — never loads whole file into memory
    console.log('Row:', row); // e.g. { name: 'Mouse', price: '799' }
    results.push(row);
  })
  .on('end', () => {
    console.log(`Finished parsing. Total rows: ${results.length}`);
  })
  .on('error', (err) => {
    console.error('CSV parse error:', err.message);
  });
```

## 💻 Code Example — Advanced

```javascript
// advanced-csv-io.js — validated streaming import + streaming export
// npm install csv-parser fast-csv

const fs = require('fs');
const csv = require('csv-parser');
const { format } = require('fast-csv');

// ─── IMPORT: stream, validate, batch-insert ────────────────────────────────
function validateRow(row, rowNumber) {
  const errors = [];
  if (!row.name || row.name.trim() === '') errors.push('name is required');
  const price = Number(row.price);
  if (isNaN(price) || price < 0) errors.push('price must be a non-negative number');
  return { valid: errors.length === 0, errors, rowNumber };
}

async function importProductsFromCsv(filePath, insertBatchFn) {
  return new Promise((resolve, reject) => {
    const validRows = [];
    const invalidRows = [];
    let rowNumber = 0;
    let batch = [];
    const BATCH_SIZE = 500;
    const pendingInserts = [];

    const stream = fs.createReadStream(filePath).pipe(csv());

    stream.on('data', (row) => {
      rowNumber++;
      const { valid, errors } = validateRow(row, rowNumber);

      if (!valid) {
        invalidRows.push({ rowNumber, data: row, errors });
        return;
      }

      batch.push({ name: row.name.trim(), price: Number(row.price) });
      validRows.push(row);

      // Flush batch when it hits the threshold — avoids one-row-at-a-time inserts
      if (batch.length >= BATCH_SIZE) {
        pendingInserts.push(insertBatchFn([...batch]));
        batch = [];
      }
    });

    stream.on('end', async () => {
      if (batch.length > 0) pendingInserts.push(insertBatchFn(batch)); // flush remainder
      try {
        await Promise.all(pendingInserts);
        resolve({
          totalRows: rowNumber,
          successCount: validRows.length,
          failureCount: invalidRows.length,
          errors: invalidRows,
        });
      } catch (err) {
        reject(err);
      }
    });

    stream.on('error', reject);
  });
}

// ─── EXPORT: stream DB results directly to CSV, no full-array buffering ───
function exportProductsToCsvStream(dbCursor, writableStream) {
  const csvStream = format({ headers: true }); // fast-csv formatter as a transform stream
  csvStream.pipe(writableStream);

  // dbCursor is assumed to be an async iterable (e.g. a MongoDB cursor or pg-cursor)
  return (async () => {
    for await (const row of dbCursor) {
      csvStream.write({ id: row.id, name: row.name, price: row.price });
    }
    csvStream.end();
  })();
}

module.exports = { importProductsFromCsv, exportProductsToCsvStream };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const multer = require('multer');
const { importProductsFromCsv, exportProductsToCsvStream } = require('./advanced-csv-io');

const app = express();
const upload = multer({ dest: 'uploads/' });

// Mock DB insert function — real code would batch-INSERT into Postgres/MongoDB
async function insertBatch(rows) {
  console.log(`Inserting batch of ${rows.length} rows`);
  // await db.query('INSERT INTO products (name, price) VALUES ...', [...]);
}

// ─── IMPORT endpoint ────────────────────────────────────────────────────────
app.post('/api/products/import', upload.single('file'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'CSV file required' });

  try {
    const summary = await importProductsFromCsv(req.file.path, insertBatch);
    res.json({
      message: 'Import completed',
      totalRows: summary.totalRows,
      imported: summary.successCount,
      failed: summary.failureCount,
      errors: summary.errors.slice(0, 50), // cap error details returned to avoid huge responses
    });
  } catch (err) {
    res.status(500).json({ error: 'Import failed', details: err.message });
  }
});

// ─── EXPORT endpoint — streams directly to the HTTP response ──────────────
app.get('/api/products/export', async (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="products.csv"');

  // Mock async-iterable cursor — real code: const cursor = db.collection('products').find().stream();
  async function* mockCursor() {
    yield { id: 1, name: 'Mouse', price: 799 };
    yield { id: 2, name: 'Keyboard', price: 1999 };
  }

  await exportProductsToCsvStream(mockCursor(), res); // pipes directly into the response
});

app.listen(3000, () => console.log('CSV import/export API on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Loading the entire CSV file into memory before processing
✅ Correct: Use streaming parsers (`csv-parser`, `fast-csv`) that process row-by-row — `fs.readFileSync(path).toString().split('\n')` loads the WHOLE file into a string first, which fails/degrades badly for large files.

```javascript
// Wrong: entire file in memory, plus a full array of all rows — doesn't scale
const content = fs.readFileSync('huge.csv', 'utf8');
const rows = content.split('\n').map(line => line.split(','));

// Right: streaming, constant memory regardless of file size
fs.createReadStream('huge.csv').pipe(csv()).on('data', row => { /* process one row */ });
```

❌ Mistake 2: One row failing aborts the entire import, forcing users to fix and re-upload everything
✅ Correct: Collect per-row errors and continue processing valid rows — return a detailed summary so users fix only the problematic rows.

```javascript
// Wrong: throws on first bad row, discarding all progress on 9,999 valid rows
stream.on('data', (row) => {
  if (!row.name) throw new Error('Missing name'); // kills the whole import
});

// Right: collect errors, keep processing
stream.on('data', (row) => {
  if (!row.name) { invalidRows.push({ rowNumber, errors: ['Missing name'] }); return; }
  validRows.push(row);
});
```

---

## 🧠 Tricky Interview Question

```javascript
// This CSV export works fine for 100 rows. What breaks it at 5 million rows?
app.get('/export', async (req, res) => {
  const allProducts = await db.collection('products').find().toArray(); // loads ALL into memory
  const csvString = allProducts.map(p => `${p.id},${p.name},${p.price}`).join('\n');
  res.send(csvString);
});
```
Answer: `.toArray()` materializes ALL 5 million documents into a JS array in memory simultaneously — for large collections this can exhaust available heap memory, crash the process, or at minimum cause massive GC pressure and a multi-second (or longer) delay before ANY data is sent to the client (the whole string must be built before `res.send()` is even called). The fix: use the database driver's native cursor/streaming API (`.find().stream()` in MongoDB, `pg-cursor` in Postgres) to pull rows incrementally, and PIPE each row through a CSV-formatting transform stream directly into `res` — this way memory usage stays roughly constant (just the current chunk being processed) regardless of whether the export is 100 rows or 5 million, and the client starts receiving data almost immediately rather than waiting for the entire query to complete first.

---

## ⚫ Interview Questions + Answers

Q1: What's the advantage of batch inserts over row-by-row inserts during CSV import?
A1: Each individual `INSERT` statement carries network round-trip overhead (even for a fast local DB, this adds up) and often transaction/connection overhead. Batching (e.g. a single `INSERT INTO products (...) VALUES (...), (...), (...)` with 500 rows, or using the driver's bulk-insert API) reduces the NUMBER of round-trips from potentially millions to thousands, often making bulk imports 10-100x faster. The tradeoff: a batch failure (e.g. one bad row violating a constraint) can fail the entire batch depending on DB settings — requiring either pre-validation (as shown) or `ON CONFLICT`/upsert handling.

Q2: How would you handle a CSV file with inconsistent/unexpected column order or extra/missing columns?
A2: Most streaming CSV parsers (csv-parser, fast-csv) use the FIRST row as a header row by default, mapping subsequent rows to objects keyed by header name — so column ORDER doesn't matter, only header NAMES do. For extra columns, simply ignore unrecognized keys during validation. For missing REQUIRED columns, validate their presence explicitly and reject/report rows (or the whole file) accordingly — a good import tool often validates the header row itself upfront before processing any data rows, failing fast with "missing required column: price" rather than discovering it row-by-row.

Q3: How do you prevent a malicious/malformed CSV from causing a denial-of-service (e.g. a file with a single 1GB line, or deeply nested quoting)?
A3: Set upload size limits (Multer's `limits.fileSize`) to cap the overall file size regardless of content. For line-length attacks, streaming parsers generally handle this gracefully since they process byte-by-byte rather than reading full lines into memory first — but it's worth testing your specific parser library's behavior with pathological inputs. Also sanitize/validate field values before using them in SQL (always use parameterized queries, never string-concatenate CSV values into a SQL string) to prevent injection via malicious CSV content.

Q4: Why might you prefer `fast-csv`'s formatter (a transform stream) over `Array.join(',')` for CSV export?
A4: Proper CSV formatting must handle edge cases: values containing commas, quotes, or newlines need to be quoted/escaped correctly (`"Product, Deluxe"` needs surrounding quotes, embedded quotes need doubling `""`). A naive `.join(',')` breaks the moment any field contains a comma, producing a malformed CSV. Dedicated CSV libraries handle RFC 4180 escaping rules correctly and, as transform STREAMS, integrate directly into Node's piping model for memory-efficient large exports.

Q5: How would you let a user track the progress of a very large (e.g. 1-hour-long) CSV import?
A5: Move the import into a background job (BullMQ), returning a job ID immediately on upload. Use `job.updateProgress(percentComplete)` periodically as rows are processed (e.g. every 1000 rows), and expose a `/import-status/:jobId` polling endpoint (or push updates via Socket.io/WebSocket) so the frontend can show a progress bar instead of a blocked, possibly-timing-out HTTP request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Bulk data entry/migration workflows (initial data seeding, periodic catalog updates from suppliers)
- Users need to export data for offline analysis (Excel/Sheets) or for use in other systems
- Data volumes are large enough that manual UI entry is impractical

❌ Avoid when:
- Data needs real-time, row-level validation feedback during entry (a web form with inline validation is better UX than a bulk file fix-and-reupload cycle)
- The dataset is small (a handful of records) — a simple form or direct API call is simpler than building CSV tooling

---

## 📊 Visual Diagram
```
IMPORT (streaming, validated, batched)
────────────────────────────────────────
CSV file → createReadStream → csv-parser transform → row-by-row 'data' events
                                                             │
                                               ┌─────────────┴─────────────┐
                                           valid row                  invalid row
                                               │                             │
                                               ▼                             ▼
                                        accumulate batch              push to errors[]
                                               │
                                     batch.length >= 500?
                                               │
                                              yes
                                               ▼
                                     insertBatchFn(batch) → DB
                                               │
                                    (repeat until stream ends)
                                               ▼
                               return { total, success, failures, errors }

EXPORT (streaming, constant memory)
────────────────────────────────────
DB cursor (async iterable) → for await (row of cursor) → csvStream.write(row)
                                                                  │
                                                          csvStream.pipe(res)
                                                                  │
                                                      client receives chunks progressively
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming Parser | Processes data chunk-by-chunk, not all at once | Data को chunk-by-chunk process करने वाला parser |
| Batch Insert | Inserting many rows in one DB operation | एक DB operation में कई rows insert करना |
| Cursor | Incremental DB query result iterator | DB query result का incremental iterator |
| RFC 4180 | CSV format escaping/quoting standard | CSV format की escaping/quoting standard |
| Transform Stream | Stream that modifies data as it passes through | Data को transform करने वाला stream |
| Backpressure | Mechanism pausing fast producers for slow consumers | तेज़ producer को धीमे consumer के लिए रोकने का mechanism |

---

## ⚡ 3-Line Summary
English: 1. CSV import/export should always use streaming parsers/formatters, never load entire files into memory, to handle arbitrarily large files with constant memory usage. 2. Validate rows individually and collect errors rather than aborting the whole import on one bad row; batch-insert valid rows for performance. 3. For very large imports/exports, use background job queues with progress tracking instead of blocking the HTTP request.
Hindi: 1. CSV import/export हमेशा streaming parsers/formatters use करें, पूरी files memory में load न करें, constant memory usage के साथ बड़ी files handle करें। 2. Rows individually validate करो, errors collect करो, एक bad row पर पूरा import abort न करो; valid rows batch-insert करो। 3. बहुत बड़े imports/exports के लिए background job queues और progress tracking use करो।

---

## ➡️ Next Topic
**285. Build Search API** — full-text search और filtering के साथ search endpoint बनाना।
