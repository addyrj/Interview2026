# 51. Pipe + Pipeline
# हिंदी में: pipe() और pipeline() — Streams को सुरक्षित तरीके से Connect करना

---

## 🔵 Simple Definition (English)
**`.pipe(destination)`** connects a Readable stream to a Writable, automatically handling data flow and backpressure — but it does NOT properly clean up streams if one of them errors. **`stream.pipeline(...streams, callback)`** (Node 10+) does the same job but properly destroys ALL streams in the chain on error, and gives you one unified callback/Promise for success or failure. In production code, `pipeline()` is almost always the better choice.

## 🔵 सरल परिभाषा (Hindi)
**`.pipe(destination)`** Readable को Writable से connect करता है, data flow और backpressure automatically handle करता है — पर अगर कोई stream error करे तो properly cleanup नहीं करता। **`stream.pipeline()`** (Node 10+) वही काम करता है पर error पर chain के सभी streams को properly destroy करता है, और एक unified callback/Promise देता है। Production code में `pipeline()` almost हमेशा बेहतर choice है।

---

## 🔴 Problem it Solves
With plain `.pipe()`, if a stream in the middle of a chain errors (e.g., disk full while writing, or a parse error in a Transform), the OTHER streams in the chain are left open — file descriptors leak, memory isn't freed, and the process can eventually run out of file handles under sustained errors. Also, `.pipe()` provides no single place to know "the whole pipeline finished" or "it failed" — you'd have to attach error listeners to every stream individually and coordinate manually. `pipeline()` solves both: automatic cleanup on any error, and one callback/Promise for the entire chain's outcome.

## 🔴 यह क्यों बना? (Hindi)
Plain `.pipe()` में, अगर chain के बीच में कोई stream error करे (disk full, parse error), बाकी streams खुले रह जाते हैं — file descriptors leak होते हैं, memory free नहीं होती, process धीरे-धीरे file handles ख़त्म कर देता है। साथ ही `.pipe()` में "पूरा pipeline खत्म हुआ या fail हुआ" जानने की कोई single जगह नहीं है। `pipeline()` दोनों solve करता है: error पर automatic cleanup, और पूरी chain के लिए एक callback/Promise।

---

## 🟢 How it Works — Step by Step

Step 1 → Basic pipe: `readable.pipe(writable)` returns the DESTINATION stream, allowing chaining: `a.pipe(b).pipe(c)`.
Step 2 → `.pipe()` internally listens for `'data'` on the source and calls `.write()` on the destination, automatically calling `.pause()`/`.resume()` for backpressure based on `.write()`'s return value and the `'drain'` event.
Step 3 → `.pipe()` automatically calls `.end()` on the destination when the source emits `'end'` (unless `{ end: false }` is passed) — but it does NOT listen for `'error'` on either side, so errors must be handled manually per-stream.
Step 4 → `stream.pipeline(stream1, stream2, ..., callback)` chains all streams together AND wires up error handling: if ANY stream errors, every other stream in the chain is `.destroy()`ed, and the single `callback(err)` fires.
Step 5 → `promisify(pipeline)` (or `require('stream/promises').pipeline` in modern Node) lets you `await` the entire pipeline, catching errors with a normal `try/catch`.
Step 6 → `pipeline()` also supports an `AbortController` signal for manually cancelling an in-progress pipeline.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Basic pipe: `.pipe()` destination stream return करता है, chaining allow करता है।
Step 2 → `.pipe()` internally source पर `'data'` listen करता है, destination पर `.write()` call करता है, backpressure के लिए `.pause()`/`.resume()` automatically करता है।
Step 3 → Source `'end'` emit करे तो destination पर `.end()` auto call होता है — पर `'error'` handle नहीं होता automatically।
Step 4 → `stream.pipeline(...)` सभी streams को chain करता है और error handling wire करता है — कोई भी error हो तो सभी streams `.destroy()` हो जाते हैं, एक callback fire होता है।
Step 5 → `promisify(pipeline)` या `stream/promises` से `await` कर सकते हो, `try/catch` से errors catch करो।
Step 6 → `pipeline()` `AbortController` signal भी support करता है, manually cancel करने के लिए।

---

## 🟡 Real World Example
**Amazon seller's bulk product upload:** A seller uploads a 500MB CSV of product listings. The server pipeline is: `req` (Readable, the upload) → CSV parser (Transform) → validator (Transform, rejects bad rows) → database writer (Writable). If row 50,000 has a malformed price and the validator throws, `pipeline()` ensures the file read stream, the parser, AND the database writer are all properly closed/destroyed — no half-open file handles, no half-committed writes left dangling, and the seller gets a clear error response instead of the server silently leaking resources.

## 🟡 Real Example Hindi mein
**Amazon seller का bulk product upload:** Seller 500MB CSV upload करता है। Pipeline: req → CSV parser → validator → DB writer। अगर row 50,000 में malformed price हो और validator throw करे, `pipeline()` सुनिश्चित करता है कि सभी streams properly close/destroy हों — कोई half-open file handle नहीं, कोई dangling write नहीं, seller को clear error मिलता है।

---

## 💻 Code Example — Basic
```javascript
// pipe-pipeline-basics.js
const fs = require('fs');
const zlib = require('zlib');
const { pipeline } = require('stream');

// 1. BASIC .pipe() -- simple, but error handling is manual and incomplete
fs.createReadStream('./input.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('./output.txt.gz'));
// If input.txt doesn't exist, this throws an UNHANDLED error and crashes!

// 2. .pipe() WITH MANUAL ERROR HANDLING (verbose, easy to miss a stream)
const read1 = fs.createReadStream('./input.txt');
const gzip1 = zlib.createGzip();
const write1 = fs.createWriteStream('./output2.txt.gz');

read1.on('error', (err) => console.error('Read error:', err.message));
gzip1.on('error', (err) => console.error('Gzip error:', err.message));
write1.on('error', (err) => console.error('Write error:', err.message));
read1.pipe(gzip1).pipe(write1);
// Works, but verbose -- and streams may still not be properly destroyed on error

// 3. pipeline() -- ONE error handler for the WHOLE chain, auto-cleanup
pipeline(
  fs.createReadStream('./input.txt'),
  zlib.createGzip(),
  fs.createWriteStream('./output3.txt.gz'),
  (err) => {
    if (err) {
      console.error('Pipeline failed:', err.message); // all streams already cleaned up
    } else {
      console.log('Pipeline succeeded!');
    }
  }
);
```

## 💻 Code Example — Advanced
```javascript
// pipe-pipeline-advanced.js -- production patterns
const fs = require('fs');
const zlib = require('zlib');
const { pipeline } = require('stream');
const { pipeline: pipelinePromise } = require('stream/promises'); // Node 15+ built-in Promise API

// ─── 1. ASYNC/AWAIT PIPELINE (modern, preferred style) ────────────────────────
async function compressFile(inputPath, outputPath) {
  try {
    await pipelinePromise(
      fs.createReadStream(inputPath),
      zlib.createGzip(),
      fs.createWriteStream(outputPath)
    );
    console.log(`Compressed ${inputPath} -> ${outputPath}`);
  } catch (err) {
    console.error('Compression failed:', err.message);
    throw err; // propagate to caller for proper error handling
  }
}

// ─── 2. CANCELLING A PIPELINE WITH AbortController ────────────────────────────
async function compressFileWithTimeout(inputPath, outputPath, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    await pipelinePromise(
      fs.createReadStream(inputPath),
      zlib.createGzip(),
      fs.createWriteStream(outputPath),
      { signal: controller.signal } // abort cancels the whole pipeline
    );
    clearTimeout(timer);
  } catch (err) {
    clearTimeout(timer);
    if (err.name === 'AbortError') {
      console.error('Pipeline timed out and was cancelled');
    } else {
      console.error('Pipeline error:', err.message);
    }
  }
}

// ─── 3. MULTI-STAGE ETL PIPELINE WITH TRANSFORMS + ERROR RECOVERY ─────────────
const { Transform } = require('stream');

function createValidationTransform() {
  return new Transform({
    objectMode: true,
    transform(row, encoding, callback) {
      if (!row.price || isNaN(parseFloat(row.price))) {
        // Instead of throwing (which would kill the whole pipeline),
        // skip invalid rows and log them -- more resilient for bulk uploads
        console.warn('Skipping invalid row:', row);
        return callback(); // no push() -- row dropped, pipeline continues
      }
      callback(null, row);
    }
  });
}

async function processProductUpload(inputStream, dbWriteStream) {
  const csv = require('csv-parse'); // npm install csv-parse

  await pipelinePromise(
    inputStream,
    csv.parse({ columns: true }),
    createValidationTransform(),
    dbWriteStream
  );
}

// ─── 4. COMPARISON: pipe() leaves file handles open on error, pipeline() doesn't ─
function demonstrateLeak() {
  const badRead = fs.createReadStream('./does-not-exist.txt');
  const badWrite = fs.createWriteStream('./output-leak-test.txt');
  badRead.pipe(badWrite);
  // badWrite's file descriptor stays open even though badRead failed -- LEAK
  badRead.on('error', () => {}); // suppresses crash but doesn't fix the leak
}

function demonstrateNoLeak() {
  pipeline(
    fs.createReadStream('./does-not-exist.txt'),
    fs.createWriteStream('./output-no-leak-test.txt'),
    (err) => {
      // pipeline() automatically destroys badWrite's stream too -- no leak
      if (err) console.log('Properly cleaned up after error:', err.message);
    }
  );
}

module.exports = { compressFile, compressFileWithTimeout, processProductUpload };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const fs = require('fs');
const zlib = require('zlib');
const { pipeline } = require('stream/promises');
const app = express();

// 1. STREAMING FILE DOWNLOAD WITH PROPER ERROR HANDLING VIA pipeline()
app.get('/download/:filename', async (req, res) => {
  const filePath = `./uploads/${req.params.filename}`;

  try {
    await pipeline(fs.createReadStream(filePath), res);
    // If the file doesn't exist, pipeline() rejects -- caught below, res properly handled
  } catch (err) {
    console.error('Download failed:', err.message);
    if (!res.headersSent) {
      res.status(404).json({ error: 'File not found or stream error' });
    }
  }
});

// 2. UPLOAD PROCESSING PIPELINE: req -> validate -> gzip -> save to disk
app.post('/upload-compressed', async (req, res) => {
  const outputPath = `./uploads/compressed-${Date.now()}.gz`;

  try {
    await pipeline(
      req,                              // Readable: incoming upload body
      zlib.createGzip(),                // Transform: compress on the way in
      fs.createWriteStream(outputPath)  // Writable: save to disk
    );
    res.json({ message: 'Upload compressed and saved', path: outputPath });
  } catch (err) {
    res.status(500).json({ error: 'Upload processing failed: ' + err.message });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `.pipe()` chains in production without per-stream error handlers
```javascript
// Wrong -- any error in the chain is unhandled, crashes the process
fs.createReadStream('./input').pipe(zlib.createGzip()).pipe(fs.createWriteStream('./out'));

// Correct -- use pipeline() instead, one error handler for everything
const { pipeline } = require('stream/promises');
await pipeline(fs.createReadStream('./input'), zlib.createGzip(), fs.createWriteStream('./out'));
```

❌ Mistake 2: Forgetting that `pipeline()`'s last argument must be a callback OR it returns a Promise (don't mix styles)
```javascript
// Wrong -- missing callback AND not using the Promise-returning overload correctly
const { pipeline } = require('stream');
pipeline(readable, writable); // no callback -- Node 15+ may warn, errors go unhandled

// Correct -- EITHER provide a callback OR use stream/promises' pipeline with await
const { pipeline } = require('stream/promises');
await pipeline(readable, writable); // properly awaited, errors caught via try/catch
```

❌ Mistake 3: Assuming `.pipe()` cleans up destination streams on source error
```javascript
// Wrong assumption
const read = fs.createReadStream('./missing.txt');
const write = fs.createWriteStream('./out.txt');
read.pipe(write);
read.on('error', () => write.end()); // manual cleanup attempt -- easy to forget, error-prone

// Correct -- pipeline() does this automatically for ALL streams in the chain
pipeline(fs.createReadStream('./missing.txt'), fs.createWriteStream('./out.txt'), (err) => {
  // write stream already destroyed/cleaned up by the time this callback fires
});
```

---

## 🧠 Tricky Interview Question
```javascript
const { pipeline } = require('stream');
const { Readable, Writable } = require('stream');

const source = Readable.from(['chunk1', 'chunk2']);
const dest = new Writable({
  write(chunk, encoding, callback) {
    if (chunk.toString() === 'chunk2') {
      return callback(new Error('Simulated failure on chunk2'));
    }
    console.log('Wrote:', chunk.toString());
    callback();
  }
});

pipeline(source, dest, (err) => {
  console.log('Pipeline finished. Error:', err ? err.message : 'none');
});
```
Answer: Output is `Wrote: chunk1`, then `Pipeline finished. Error: Simulated failure on chunk2`. `chunk1` is written successfully and logged, but when `chunk2` arrives, the Writable's `_write` calls `callback(new Error(...))`, which `pipeline()` catches — it destroys BOTH the source and destination streams and invokes the final callback with that error. Note that `chunk1` was already written/logged before the failure — `pipeline()` doesn't roll back prior writes; it only ensures proper cleanup and surfaces the error cleanly, it is NOT transactional.

---

## ⚫ Interview Questions + Answers

Q1: What's the single biggest reason to prefer `pipeline()` over `.pipe()` in production code?
A1: Automatic, guaranteed cleanup of ALL streams in the chain when ANY stream errors. `.pipe()` leaves other streams in the chain open on error (file descriptor leaks, dangling connections) because it only handles the happy-path data flow and `'end'` event, not `'error'` propagation across the chain. `pipeline()` wires this up automatically via `.destroy()` calls on every stream, which is critical for long-running servers that process many files/requests over time.

Q2: How do you convert `pipeline()`'s callback style into something you can `await`?
A2: Two options: (1) `const pipelineAsync = require('util').promisify(require('stream').pipeline);` then `await pipelineAsync(...)`. (2) Node 15+ ships a built-in Promise version: `const { pipeline } = require('stream/promises'); await pipeline(...)` — this is the modern, preferred approach, requiring no manual `promisify`.

Q3: Does `.pipe()` return the source or the destination stream, and why does that matter?
A3: `.pipe()` returns the DESTINATION stream. This is what enables chaining: `a.pipe(b).pipe(c)` works because `a.pipe(b)` returns `b`, and `.pipe(c)` is then called on `b`. If it returned the source, you couldn't chain multiple transforms this way — you'd need separate statements for each pipe.

Q4: Can `pipeline()` take more than 2 arguments (more than one intermediate Transform)?
A4: Yes — `pipeline()` accepts any number of streams: `pipeline(readable, transform1, transform2, transform3, writable, callback)`. Each stream is piped into the next in order, and the whole chain shares unified error handling and cleanup, regardless of how many stages there are.

Q5: What happens if you call `pipeline()` with only a Readable and no Writable destination?
A5: As of Node 14+, `pipeline()` can consume a Readable with no destination for side-effect-only processing, but typically pipeline requires at least a source and a destination. If you just want to drain/consume a Readable without a real destination, you'd typically pipe it to a no-op Writable, or better, use `for await (const chunk of readable) {}` to consume it directly without needing `pipeline()` at all.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chaining streams in any production code — `pipeline()` should be the default choice
- You need the entire chain's success/failure as a single outcome (Promise or callback)
- Building file-processing, upload, or ETL pipelines where resource cleanup matters

❌ Avoid when:
- Writing quick, one-off scripts where `.pipe()`'s simplicity is fine and error handling doesn't matter much
- You need fine-grained manual control over individual stream error recovery that `pipeline()`'s all-or-nothing destroy behavior doesn't support (rare — usually handled inside Transform streams instead, like the "skip invalid rows" pattern)

---

## 📊 Visual Diagram
```
.pipe() CHAIN (manual, leaky on error):

  readable ──.pipe()──► transform ──.pipe()──► writable
     │                      │                      │
     └─ 'error' ────────────┴──────────────────────┘
        (NOT automatically connected -- each needs its own handler,
         and streams are NOT destroyed automatically on error)


pipeline() CHAIN (automatic, safe):

  pipeline(readable, transform, writable, callback)
     │
     ├─ happy path: data flows readable → transform → writable
     │              callback(null) fires when writable 'finish's
     │
     └─ ANY stream errors:
            │
            ▼
     ALL streams .destroy()ed automatically
            │
            ▼
     callback(err) fires ONCE with that error
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pipe() | Connect Readable to Writable | Readable को Writable से connect करना |
| pipeline() | Safe multi-stream chaining with cleanup | Safe chaining with cleanup |
| stream/promises | Built-in Promise-based pipeline API | Built-in Promise-based pipeline API |
| destroy() | Force-close a stream and release resources | Stream को force-close करना |
| AbortController | Cancel an in-progress pipeline | Running pipeline cancel करना |
| file descriptor leak | Resources left open after error | Error के बाद resources खुले रहना |

---

## ⚡ 3-Line Summary
English: `.pipe()` connects streams and handles backpressure automatically, but leaves other streams open on error — a resource leak risk. `pipeline()` chains any number of streams with automatic cleanup on error and a single unified callback/Promise outcome. Always prefer `pipeline()` (or `stream/promises`' `pipeline`) in production code.

Hindi: `.pipe()` streams connect करता है और backpressure handle करता है, पर error पर दूसरे streams खुले रह जाते हैं — resource leak risk। `pipeline()` किसी भी संख्या के streams को chain करता है, error पर automatic cleanup और एक unified outcome देता है। Production code में हमेशा `pipeline()` prefer करो।

---

## ➡️ Next Topic
**52. Buffer — Complete Guide** — binary data handling underlying all stream chunks: encoding, `Buffer.from()`, `Buffer.concat()`, and memory implications.
