# 47. Streams
# हिंदी में: Streams — Large Data को Chunks में Process करो

---

## 🔵 Simple Definition (English)
**Streams** are Node.js's way of handling data that's too large to load all at once, or data that arrives over time. Instead of loading a 10GB file into memory, a stream reads it in small chunks (64KB by default), processes each chunk, and moves on — keeping memory usage constant. Streams are **EventEmitter** objects with events like `data`, `end`, `error`. They're composable — you can `.pipe()` them together like Unix pipes.

4 types: **Readable** (source), **Writable** (destination), **Duplex** (both), **Transform** (duplex with modification).

## 🔵 सरल परिभाषा (Hindi)
**Streams** Node.js का तरीका है large data handle करने का। 10GB file को memory में load करने की जगह, stream 64KB chunks में read करता है, हर chunk process करता है, और आगे बढ़ता है — memory constant रहती है। Streams **EventEmitter** objects हैं — `data`, `end`, `error` events। Composable हैं — `.pipe()` से Unix pipes जैसे chain करो।

4 types: **Readable** (source), **Writable** (destination), **Duplex** (दोनों), **Transform** (duplex + modification)।

---

## 🔴 Problem it Solves
```
WITHOUT STREAMS (memory problem):
  // Read 10GB CSV file:
  const data = fs.readFileSync('./10gb-sales-data.csv');  // ← 10GB in RAM!
  // OR
  const data = await fs.promises.readFile('./10gb-file');  // ← still 10GB in RAM!
  
  Result: Out of Memory crash
  Node.js default heap: ~1.5GB → crash at ~1.5GB file

  Video streaming:
  // Sending a 4GB video file:
  const video = await fs.promises.readFile('./movie.mp4');  // 4GB in RAM!
  res.send(video);  // Loads ENTIRE file before sending
  User waits forever for download to start

WITH STREAMS:
  // Read 10GB CSV:
  const stream = fs.createReadStream('./10gb-sales-data.csv');
  stream.on('data', chunk => processChunk(chunk));  // 64KB at a time
  // RAM usage: ~64KB constant (not 10GB!)

  Video streaming:
  res.setHeader('Content-Type', 'video/mp4');
  fs.createReadStream('./movie.mp4').pipe(res);
  // Video starts playing in browser within seconds!
  // Chunks flow: file → network → browser (without loading everything)
```

---

## 🟢 Stream Types

```
STREAM TYPES:
──────────────────────────────────────────────────────────

  READABLE STREAM (source):
    fs.createReadStream('./file.txt')
    http.IncomingMessage (req)
    process.stdin
    crypto.createHash() output
    
  WRITABLE STREAM (destination):
    fs.createWriteStream('./output.txt')
    http.ServerResponse (res)
    process.stdout
    
  DUPLEX (both read + write):
    TCP sockets (net.Socket)
    WebSocket connections
    
  TRANSFORM (duplex + modifies data):
    zlib.createGzip() → compress data in flight
    zlib.createGunzip() → decompress
    crypto.createCipheriv() → encrypt
    csv-parse → parse CSV
    
PIPE (connect streams):
  readable.pipe(writable)
  
  // Chain example:
  fs.createReadStream('./large.csv')    // READ
    .pipe(zlib.createGzip())            // TRANSFORM (compress)
    .pipe(fs.createWriteStream('./large.csv.gz'))  // WRITE
  
  // Data flows chunk by chunk: no full file in memory!
```

---

## 🟡 Real World Example
**Amazon India's order export system:** Operations team needs to export 50 million orders to CSV for analysis. With `readFile`: 50M orders × 200 bytes each = 10GB in RAM → crash. With streams: `createQueryStream()` from database → pipe to CSV transformer → pipe to file write stream. Memory stays under 100MB regardless of file size. Processing time: same. The stream also handles **backpressure**: if file write is slower than DB read, the stream automatically pauses reading until writing catches up.

---

## 💻 Code Example — Basic

```javascript
// streams-basics.js
const fs = require('fs');
const zlib = require('zlib');
const path = require('path');

// ─── 1. READABLE STREAM ───────────────────────────────────────────────────────
const readStream = fs.createReadStream('./large-file.txt', {
  encoding: 'utf8',
  highWaterMark: 64 * 1024,  // chunk size: 64KB (default)
});

let totalChars = 0;
let chunkCount = 0;

readStream.on('data', (chunk) => {
  // Called for each 64KB chunk
  chunkCount++;
  totalChars += chunk.length;
  // process chunk here
});

readStream.on('end', () => {
  console.log(`Done! ${chunkCount} chunks, ${totalChars} total chars`);
  // Memory used: ~64KB (not entire file)
});

readStream.on('error', (err) => {
  console.error('Stream error:', err.message);
});

// ─── 2. WRITABLE STREAM ───────────────────────────────────────────────────────
const writeStream = fs.createWriteStream('./output.txt');

writeStream.write('Line 1\n');
writeStream.write('Line 2\n');
writeStream.write('Line 3\n');
writeStream.end();  // signals end of writing

writeStream.on('finish', () => console.log('File written'));
writeStream.on('error', (err) => console.error('Write error:', err));

// ─── 3. PIPE (most common pattern) ───────────────────────────────────────────
// Copy file using streams (memory efficient):
fs.createReadStream('./source.txt')
  .pipe(fs.createWriteStream('./destination.txt'));

// ─── 4. COMPRESS FILE ─────────────────────────────────────────────────────────
// Read → gzip compress → write (all in chunks, no full file in memory)
fs.createReadStream('./large-log.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('./large-log.txt.gz'))
  .on('finish', () => console.log('File compressed'));

// ─── 5. DECOMPRESS ───────────────────────────────────────────────────────────
fs.createReadStream('./data.gz')
  .pipe(zlib.createGunzip())
  .pipe(fs.createWriteStream('./data-decompressed.txt'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-streams.js — Production patterns

const { Transform, Readable, Writable, pipeline } = require('stream');
const { promisify } = require('util');
const fs = require('fs');
const csv = require('csv-parse');  // npm install csv-parse

const pipelineAsync = promisify(pipeline);  // pipeline with error handling

// ─── 1. TRANSFORM STREAM ──────────────────────────────────────────────────────
// Convert CSV rows to JSON objects, filtering invalid rows

class CsvToJsonTransform extends Transform {
  constructor(options = {}) {
    super({ ...options, objectMode: true });
    this.headers = null;
    this.lineCount = 0;
    this.errorCount = 0;
  }

  _transform(chunk, encoding, callback) {
    // chunk is a line from CSV (if using csv-parse in line mode)
    try {
      if (!this.headers) {
        // First chunk = headers
        this.headers = chunk.toString().split(',').map(h => h.trim());
        return callback();
      }

      const values = chunk.toString().split(',');
      const row = {};
      this.headers.forEach((header, i) => {
        row[header] = values[i]?.trim();
      });

      this.lineCount++;
      this.push(row);  // push transformed data downstream
      callback();
    } catch (err) {
      this.errorCount++;
      callback();  // skip bad row, continue processing
    }
  }

  _flush(callback) {
    // Called when source stream ends
    console.log(`Processed ${this.lineCount} rows, ${this.errorCount} errors`);
    callback();
  }
}

// ─── 2. PIPELINE WITH ERROR HANDLING ──────────────────────────────────────────
// pipeline() correctly handles errors and cleanup
// pipe() leaves streams open on error — memory leaks!

async function processLargeCSV(inputPath, outputPath) {
  await pipelineAsync(
    fs.createReadStream(inputPath),                    // READ
    new CsvToJsonTransform(),                          // TRANSFORM
    new Transform({                                    // FILTER
      objectMode: true,
      transform(row, encoding, callback) {
        if (row.amount && parseFloat(row.amount) > 0) {
          this.push(JSON.stringify(row) + '\n');        // only valid amounts
        }
        callback();
      }
    }),
    zlib.createGzip(),                                 // COMPRESS
    fs.createWriteStream(outputPath),                  // WRITE
  );
  console.log('CSV processed and saved!');
}

// ─── 3. BACKPRESSURE HANDLING ─────────────────────────────────────────────────
// Backpressure: destination is slower than source
// pipe() handles this automatically!
// Manual handling:

function createCopierWithBackpressure(src, dest) {
  const readable = fs.createReadStream(src);
  const writable = fs.createWriteStream(dest);

  readable.on('data', (chunk) => {
    const canContinue = writable.write(chunk);

    if (!canContinue) {
      // Destination buffer full → pause reading
      readable.pause();
    }
  });

  writable.on('drain', () => {
    // Destination drained → resume reading
    readable.resume();
  });

  readable.on('end', () => writable.end());
  readable.pipe = readable.pipe.bind(readable);  // use pipe for cleanliness
}

// ─── 4. READABLE STREAM FROM DATA ────────────────────────────────────────────
// Create a readable stream from an array (useful for testing)
function arrayToReadable(data) {
  return new Readable({
    objectMode: true,
    read() {},  // noop — we push manually
    construct(callback) {
      data.forEach(item => this.push(item));
      this.push(null);  // signals end of stream
      callback();
    }
  });
}

// ─── 5. HTTP STREAMING RESPONSE ───────────────────────────────────────────────
// Stream database results directly to HTTP response
const express = require('express');
const app = express();

app.get('/export/orders', async (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="orders.csv"');
  res.write('id,amount,status,date\n');  // CSV header

  // Stream query results — never loads all records into memory
  const stream = Order.createQueryStream({ status: 'completed' });
  // (using pg cursor or mongoose streaming, depending on ORM)

  stream.on('data', (order) => {
    res.write(`${order.id},${order.amount},${order.status},${order.createdAt}\n`);
  });

  stream.on('end', () => res.end());
  stream.on('error', (err) => {
    res.status(500).end('Error generating export');
  });
});

// ─── 6. UPLOAD: PROCESS STREAM WITHOUT SAVING TO DISK ────────────────────────
const multer = require('multer');
const upload = multer({ storage: multer.memoryStorage() });

app.post('/upload-csv', upload.single('file'), async (req, res) => {
  // req.file.buffer contains file bytes in memory
  // For large files, stream from multer to processing:

  const { Readable } = require('stream');
  const fileStream = Readable.from(req.file.buffer);
  
  let rowCount = 0;
  await pipelineAsync(
    fileStream,
    csv.parse({ columns: true }),
    new Transform({
      objectMode: true,
      async transform(row, enc, cb) {
        await db.insert(row);  // process each row
        rowCount++;
        cb();
      }
    }),
    new Writable({ objectMode: true, write(_, __, cb) { cb(); } })
  );

  res.json({ message: `Imported ${rowCount} rows` });
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// Most common stream use cases in Express:

// 1. STREAM FILE DOWNLOAD (no memory spike)
app.get('/download/:filename', (req, res) => {
  const filePath = path.join(__dirname, 'uploads', req.params.filename);
  
  // Check file exists first
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'File not found' });
  }

  // Get file size for Content-Length header
  const stat = fs.statSync(filePath);
  res.setHeader('Content-Length', stat.size);
  res.setHeader('Content-Disposition', `attachment; filename="${req.params.filename}"`);
  
  fs.createReadStream(filePath).pipe(res);
  // Streams file → client in chunks, never loads full file
});

// 2. RANGE REQUESTS (video seeking)
app.get('/video/:filename', (req, res) => {
  const filePath = path.join(__dirname, 'videos', req.params.filename);
  const stat = fs.statSync(filePath);
  const fileSize = stat.size;
  const range = req.headers.range;

  if (range) {
    // Parse Range: bytes=0-1000000
    const [start, end] = range.replace('bytes=', '').split('-');
    const startByte = parseInt(start);
    const endByte = end ? parseInt(end) : fileSize - 1;
    const chunkSize = endByte - startByte + 1;

    res.writeHead(206, {  // Partial Content
      'Content-Range': `bytes ${startByte}-${endByte}/${fileSize}`,
      'Accept-Ranges': 'bytes',
      'Content-Length': chunkSize,
      'Content-Type': 'video/mp4',
    });

    // Stream only the requested byte range
    fs.createReadStream(filePath, { start: startByte, end: endByte }).pipe(res);
  } else {
    res.writeHead(200, { 'Content-Length': fileSize, 'Content-Type': 'video/mp4' });
    fs.createReadStream(filePath).pipe(res);
  }
});

// 3. PROXY/FORWARD STREAM (avoid double buffering)
app.get('/proxy-image', async (req, res) => {
  const { default: fetch } = await import('node-fetch');
  const response = await fetch('https://external-service.com/large-image.jpg');
  response.body.pipe(res);  // pipe external stream directly to response
  // Never buffers the image in this server's memory
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `pipe()` instead of `pipeline()` for error handling
```javascript
// WRONG: pipe() doesn't properly clean up on error
fs.createReadStream('./input')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('./output'));
// If any stream errors → other streams leak (stay open)!

// CORRECT: pipeline() handles errors and cleanup
const { pipeline } = require('stream');
const { promisify } = require('util');
const pipelineAsync = promisify(pipeline);

await pipelineAsync(
  fs.createReadStream('./input'),
  zlib.createGzip(),
  fs.createWriteStream('./output'),
);
// On error: all streams are properly destroyed
```

❌ **Mistake 2:** Not handling stream events
```javascript
// WRONG: No error handler
fs.createReadStream('./might-not-exist.txt')
  .pipe(someTransform)
  .pipe(fs.createWriteStream('./output.txt'));
// If file doesn't exist: UnhandledError crashes process!

// CORRECT: Always handle 'error' event
const readable = fs.createReadStream('./file.txt');
readable.on('error', err => console.error('Read error:', err));
// OR: use pipeline() which handles errors
```

❌ **Mistake 3:** Forgetting object mode for non-buffer data
```javascript
// WRONG: Transform stream outputting objects without objectMode
class MyTransform extends Transform {
  _transform(chunk, enc, cb) {
    this.push({ data: chunk.toString() });  // pushing object
    cb();
  }
}
// Error: "Invalid data, chunk must be a string or Buffer"

// CORRECT: Enable objectMode
class MyTransform extends Transform {
  constructor() {
    super({ objectMode: true });  // ← required for objects
  }
  _transform(chunk, enc, cb) {
    this.push({ data: chunk.toString() });  // now works
    cb();
  }
}
```

---

## 🧠 Tricky Interview Question

**Q: What is backpressure in streams and how does Node.js handle it?**

**Answer:** Backpressure occurs when a Writable stream (destination) is slower than a Readable stream (source) — the buffer fills up and data would be lost or memory would spike. Node.js handles this in two ways: (1) **`pipe()`** automatically: when `writable.write(chunk)` returns `false` (buffer full), `pipe` calls `readable.pause()`. When writable emits `'drain'` (buffer drained), `pipe` calls `readable.resume()`. (2) **Manual**: call `readable.pause()` when `writable.write()` returns `false`, resume on `'drain'` event. This ensures the fast producer doesn't overwhelm the slow consumer — key for memory-safe large file processing.

---

## ⚫ Interview Questions + Answers

**Q1: What are the 4 types of streams in Node.js?**
A1: (1) **Readable**: source of data — `fs.createReadStream()`, `http.IncomingMessage`, `process.stdin`. Emits `data`, `end`, `error`. (2) **Writable**: destination — `fs.createWriteStream()`, `http.ServerResponse`, `process.stdout`. Has `write()`, `end()` methods. (3) **Duplex**: both readable and writable — TCP socket (`net.Socket`), WebSocket. Data can flow both ways. (4) **Transform**: duplex that modifies data — `zlib.createGzip()` (compress), `zlib.createGunzip()` (decompress), `crypto.createCipheriv()` (encrypt). Data goes in one end, modified data comes out the other.

**Q2: What is the difference between `pipe()` and `pipeline()`?**
A2: `pipe()`: connects streams, but on error the piped streams are NOT automatically destroyed — memory leaks. Also doesn't return a Promise. `pipeline()` (Node 10+, `require('stream')`): properly destroys all streams in the chain on error, preventing leaks. Returns a callback-based function (promisify with `util.promisify`). Best practice: always use `pipeline()` over `pipe()` in production code. `pipe()` is fine for simple scripts where you don't care about cleanup.

**Q3: What is `highWaterMark` in streams?**
A3: `highWaterMark` is the buffer size threshold (in bytes for binary streams, number of objects for object mode). For Readable: if internal buffer reaches `highWaterMark`, `read()` returns `null` and stops reading from source. For Writable: if buffer exceeds `highWaterMark`, `write()` returns `false` (trigger backpressure). Default: 64KB for bytes, 16 for object mode. Increase for: high-throughput network streams (less chunk overhead). Decrease for: memory-constrained environments, many concurrent streams.

**Q4: What is `objectMode` in streams?**
A4: By default, streams work with `Buffer` and `string` data. `objectMode: true` allows any JavaScript value (objects, arrays, numbers) to flow through the stream. Each `push()` in objectMode emits one object as one `data` event, regardless of size. Required when: Transform stream outputs objects (e.g., parsing CSV → JavaScript objects), or when connecting database cursor → JSON transform → HTTP response. Caveat: `highWaterMark` means number of objects (not bytes) in objectMode.

**Q5: How do you stream database results to an HTTP response?**
A5: Use the database driver's streaming/cursor API. For Mongoose: `Model.find().cursor()`. For TypeORM: `createQueryBuilder().stream()`. For pg: `pg-query-stream`. Then pipe the cursor → transform stream (convert to CSV/JSON) → HTTP response. Pattern:
```javascript
const cursor = Order.find().cursor();
res.setHeader('Content-Type', 'text/csv');
cursor.pipe(csvTransformStream).pipe(res);
```
This way, you never load all records into memory — each row flows from DB → CSV transform → response buffer → client. Memory stays constant regardless of result set size.

---

## 📊 Visual Diagram

```
STREAM PIPELINE:
──────────────────────────────────────────────────────────────────

  10GB CSV file                        Without streams: 10GB RAM
  ┌──────────────┐                     With streams: ~192KB RAM
  │  fs.create   │
  │  ReadStream  │ → [64KB chunk] →
  └──────────────┘
         │
         ▼
  ┌──────────────┐
  │  Transform   │ → parse CSV rows → JavaScript objects
  │  (CSV parse) │
  └──────────────┘
         │
         ▼
  ┌──────────────┐
  │  Transform   │ → filter invalid → push valid rows
  │  (filter)    │
  └──────────────┘
         │
         ▼
  ┌──────────────┐
  │  zlib.Gzip   │ → compress
  └──────────────┘
         │
         ▼
  ┌──────────────┐
  │  fs.create   │ → write to output.csv.gz
  │  WriteStream │
  └──────────────┘

  BACKPRESSURE:
  ReadStream → [FAST] → Transform → [SLOW] → WriteStream
                                    ↑
                               Buffer fills up
                               writable.write() returns false
                               readable.pause() called
                               ... writable drains ...
                               writable emits 'drain'
                               readable.resume() called
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stream | Data in chunks, not all at once | Data chunks में process |
| Readable | Stream you read from | जहाँ से read करो |
| Writable | Stream you write to | जहाँ write करो |
| Transform | Readable+Writable that modifies | Data modify करने वाला |
| pipe() | Connect readable to writable | Streams को connect करना |
| pipeline() | pipe() with error handling | Error-safe pipe |
| Backpressure | Slow consumer signals fast producer | Consumer → producer को slow down |
| highWaterMark | Buffer size threshold | Buffer का maximum size |
| objectMode | Allow JS objects in stream | Objects को stream में flow |
| drain event | Writable buffer has room again | Writable buffer खाली हुई |

---

## ⚡ 3-Line Summary
**English:**
1. Streams process data in small chunks (64KB default) instead of loading everything into memory — essential for large files, video streaming, CSV exports of millions of records.
2. Use `pipeline()` over `pipe()` — it properly destroys all streams on error, preventing memory leaks; `pipe()` leaves streams open on error.
3. Key patterns: `fs.createReadStream().pipe(res)` for downloads, `zlib.createGzip()` transform for compression, `pipeline(readable, transform, writable)` for ETL processing.

**Hindi:**
1. Streams data को 64KB chunks में process करते हैं, पूरा memory में load नहीं — large files, video, CSV export के लिए essential।
2. `pipe()` की जगह `pipeline()` use करो — error पर सभी streams properly destroy होते हैं।
3. Key patterns: download के लिए `readStream.pipe(res)`, compression के लिए `zlib.createGzip()`, ETL के लिए `pipeline(readable, transform, writable)`।

---

## ➡️ Next Topic
**48. Buffers** — Binary data handling, encoding, Buffer.from(), Buffer.concat()।
