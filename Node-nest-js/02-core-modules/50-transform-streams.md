# 50. Transform Streams
# हिंदी में: Transform Streams — Data को Flow में Modify करना

---

## 🔵 Simple Definition (English)
A **Transform stream** is a special **Duplex** stream (both Readable and Writable) that MODIFIES data as it passes through — data goes in one end (writable side), gets transformed, and comes out the other end (readable side). Examples: `zlib.createGzip()` (compress), `zlib.createGunzip()` (decompress), `crypto.createCipheriv()` (encrypt). You implement `_transform(chunk, encoding, callback)` to define the modification logic.

## 🔵 सरल परिभाषा (Hindi)
**Transform stream** एक special **Duplex** stream है (Readable + Writable दोनों) जो data को गुज़रते समय MODIFY करता है — data एक तरफ (writable side) से जाता है, transform होता है, दूसरी तरफ (readable side) से निकलता है। Examples: `zlib.createGzip()` (compress), `crypto.createCipheriv()` (encrypt)। आप `_transform(chunk, encoding, callback)` implement करते हो modification logic के लिए।

---

## 🔴 Problem it Solves
Without Transform streams, modifying streamed data (compressing a file, encrypting data, parsing CSV into JSON) requires either loading everything into memory first (defeating the purpose of streaming) or manually wiring a Readable and Writable together with custom glue code. Transform streams give a standard, composable unit that fits directly into a `.pipe()` chain: `source.pipe(transform1).pipe(transform2).pipe(destination)` — each link in the chain only ever holds one chunk's worth of data in memory.

## 🔴 यह क्यों बना? (Hindi)
Transform streams के बिना, streamed data modify करना (file compress करना, data encrypt करना, CSV को JSON parse करना) या तो पूरा data memory में load करना पड़ता (streaming का मतलब खत्म) या manually Readable+Writable जोड़ने के लिए custom glue code लिखना पड़ता। Transform streams एक standard, composable unit देते हैं जो सीधे `.pipe()` chain में fit होता है — हर link सिर्फ एक chunk जितना memory रखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Extend `stream.Transform` (or use its functional form `new Transform({ transform(chunk, enc, cb) {...} })`).
Step 2 → Implement `_transform(chunk, encoding, callback)` — receive an incoming chunk from the writable side, process it, call `this.push(transformedChunk)` zero or more times to send output to the readable side, then call `callback()` to signal "ready for the next chunk."
Step 3 → Optionally implement `_flush(callback)` — called once, after all input has been written, for any final output (e.g., closing tags, checksums, remaining buffered data).
Step 4 → Chunks don't have to map 1:1 — you can call `push()` multiple times per `_transform()` call, or none at all (buffering internally until enough data accumulates, e.g. for line-based parsing).
Step 5 → `objectMode: true` lets the transform accept/emit JavaScript objects instead of Buffers/strings — common for CSV-row-to-JSON-object transforms.
Step 6 → Chain transforms with `.pipe()`: `readable.pipe(transform1).pipe(transform2).pipe(writable)` — or more safely with `pipeline()` for proper error propagation.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `stream.Transform` extend करो (या functional form)।
Step 2 → `_transform(chunk, encoding, callback)` implement करो — incoming chunk लो, process करो, `this.push()` से output भेजो, फिर `callback()` call करो।
Step 3 → `_flush(callback)` optional है — सारा input write होने के बाद एक बार call होता है, final output के लिए।
Step 4 → Chunks 1:1 map नहीं होने चाहिए — एक `_transform()` call में multiple बार `push()` कर सकते हो, या बिल्कुल नहीं।
Step 5 → `objectMode: true` से JS objects accept/emit हो सकते हैं, Buffers/strings की जगह।
Step 6 → Transforms को `.pipe()` से chain करो, या `pipeline()` से safely।

---

## 🟡 Real World Example
**Paytm's transaction log encryption pipeline:** Daily transaction logs (several GB) must be compressed AND encrypted before archiving to cold storage (for compliance). The pipeline is: `fs.createReadStream('transactions.log')` → `.pipe(zlib.createGzip())` (Transform: compress) → `.pipe(crypto.createCipheriv(...))` (Transform: encrypt) → `.pipe(fs.createWriteStream('transactions.log.gz.enc'))`. Each GB of data flows through in 64KB chunks, never fully materializing in memory, while being compressed and encrypted in a single streaming pass.

## 🟡 Real Example Hindi mein
**Paytm transaction log encryption pipeline:** Daily transaction logs (कई GB) को cold storage में archive करने से पहले compress और encrypt करना है। Pipeline: readStream → gzip (Transform: compress) → cipher (Transform: encrypt) → writeStream। हर GB data 64KB chunks में गुज़रता है, कभी पूरा memory में नहीं आता, compress और encrypt एक साथ streaming pass में होता है।

---

## 💻 Code Example — Basic
```javascript
// transform-basics.js
const { Transform } = require('stream');
const fs = require('fs');

// 1. SIMPLE TRANSFORM -- convert text to uppercase as it streams through
const upperCaseTransform = new Transform({
  transform(chunk, encoding, callback) {
    const upper = chunk.toString().toUpperCase(); // modify the chunk
    callback(null, upper); // callback(error, transformedChunk) -- shortcut for push + callback
  }
});

process.stdin.pipe(upperCaseTransform).pipe(process.stdout);
// Typing "hello" in terminal and pressing enter -> prints "HELLO"

// 2. CUSTOM CLASS-BASED TRANSFORM -- count words passing through
class WordCounterTransform extends Transform {
  constructor(options) {
    super(options);
    this.wordCount = 0;
  }

  _transform(chunk, encoding, callback) {
    const text = chunk.toString();
    this.wordCount += text.split(/\s+/).filter(Boolean).length;
    this.push(chunk); // pass the data through UNCHANGED (pass-through transform)
    callback();
  }

  _flush(callback) {
    // Called once after all input processed -- good for final summary
    this.push(`\n[Total words: ${this.wordCount}]\n`);
    callback();
  }
}

const counter = new WordCounterTransform();
fs.createReadStream('./sample.txt').pipe(counter).pipe(process.stdout);

// 3. GZIP COMPRESSION -- built-in Transform stream from zlib
const zlib = require('zlib');
fs.createReadStream('./sample.txt')
  .pipe(zlib.createGzip())              // Transform: compress
  .pipe(fs.createWriteStream('./sample.txt.gz'));
```

## 💻 Code Example — Advanced
```javascript
// transform-advanced.js -- production ETL-style pipeline
const { Transform, pipeline } = require('stream');
const { promisify } = require('util');
const zlib = require('zlib');
const fs = require('fs');
const pipelineAsync = promisify(pipeline);

// ─── 1. CSV LINE -> JSON OBJECT TRANSFORM (objectMode output) ────────────────
class CsvRowParser extends Transform {
  constructor(options = {}) {
    super({ ...options, objectMode: true }); // output JS objects, not strings
    this.headers = null;
    this.leftover = '';
  }

  _transform(chunk, encoding, callback) {
    const data = this.leftover + chunk.toString();
    const lines = data.split('\n');
    this.leftover = lines.pop(); // last line might be incomplete, save for next chunk

    for (const line of lines) {
      if (!line.trim()) continue;
      if (!this.headers) {
        this.headers = line.split(',').map((h) => h.trim());
        continue;
      }
      const values = line.split(',');
      const row = {};
      this.headers.forEach((h, i) => (row[h] = values[i]?.trim()));
      this.push(row); // emit a parsed object downstream
    }
    callback();
  }

  _flush(callback) {
    // Handle any remaining leftover line at the very end of input
    if (this.leftover.trim() && this.headers) {
      const values = this.leftover.split(',');
      const row = {};
      this.headers.forEach((h, i) => (row[h] = values[i]?.trim()));
      this.push(row);
    }
    callback();
  }
}

// ─── 2. FILTER TRANSFORM -- only pass through rows matching a condition ──────
function createFilterTransform(predicate) {
  return new Transform({
    objectMode: true,
    transform(row, encoding, callback) {
      if (predicate(row)) {
        this.push(row); // only push if predicate matches -- drops others
      }
      callback(); // always callback, even when filtering out
    }
  });
}

// ─── 3. SERIALIZE BACK TO JSON LINES TRANSFORM (objectMode -> string) ────────
function createJsonLineSerializer() {
  return new Transform({
    writableObjectMode: true, // input is objects
    readableObjectMode: false, // output is strings/buffers
    transform(row, encoding, callback) {
      callback(null, JSON.stringify(row) + '\n');
    }
  });
}

// ─── 4. FULL PRODUCTION PIPELINE: CSV -> filter -> JSON lines -> gzip -> file ─
async function processTransactionCsv(inputPath, outputPath) {
  await pipelineAsync(
    fs.createReadStream(inputPath),
    new CsvRowParser(),
    createFilterTransform((row) => parseFloat(row.amount) > 1000), // only big transactions
    createJsonLineSerializer(),
    zlib.createGzip(),
    fs.createWriteStream(outputPath)
  );
  console.log('Pipeline complete:', outputPath);
}

// ─── DEMO (would run against a real CSV file) ─────────────────────────────────
// processTransactionCsv('./transactions.csv', './high-value-transactions.json.gz');
module.exports = { CsvRowParser, createFilterTransform, createJsonLineSerializer };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const { Transform } = require('stream');
const zlib = require('zlib');
const fs = require('fs');
const app = express();

// 1. ON-THE-FLY RESPONSE TRANSFORMATION (e.g. redacting sensitive fields from a stream)
app.get('/export/users', (req, res) => {
  res.setHeader('Content-Type', 'application/json');

  const redactTransform = new Transform({
    objectMode: true,
    transform(user, encoding, callback) {
      const { password, ...safeUser } = user; // strip sensitive field
      callback(null, JSON.stringify(safeUser) + '\n');
    }
  });

  // Mock Readable source of user objects (in real app: DB cursor)
  const { Readable } = require('stream');
  const userSource = Readable.from([
    { id: 1, name: 'Rahul', password: 'secret1' },
    { id: 2, name: 'Priya', password: 'secret2' },
  ], { objectMode: true });

  userSource.pipe(redactTransform).pipe(res); // Transform redacts before client sees it
});

// 2. COMPRESSED FILE DOWNLOAD USING A TRANSFORM (gzip on-the-fly, no pre-compressed file needed)
app.get('/download/report.gz', (req, res) => {
  res.setHeader('Content-Encoding', 'gzip');
  res.setHeader('Content-Type', 'application/json');

  fs.createReadStream('./reports/large-report.json')
    .pipe(zlib.createGzip()) // Transform: compress on the fly
    .pipe(res);
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to call `callback()` inside `_transform()`
```javascript
// Wrong -- stream stalls forever, no further chunks processed
class MyTransform extends Transform {
  _transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    // missing callback() -- pipeline hangs!
  }
}

// Correct
class MyTransform extends Transform {
  _transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback(); // always call, even if push() wasn't called
  }
}
```

❌ Mistake 2: Assuming chunk boundaries align with logical boundaries (e.g. lines, CSV rows)
```javascript
// Wrong -- assumes each chunk is exactly one line (chunks can split mid-line!)
_transform(chunk, encoding, callback) {
  const line = chunk.toString(); // a "line" might actually be half a line
  this.push(line.toUpperCase());
  callback();
}

// Correct -- buffer partial data across chunks (see CsvRowParser's `leftover` pattern)
_transform(chunk, encoding, callback) {
  this.buffer += chunk.toString();
  const lines = this.buffer.split('\n');
  this.buffer = lines.pop(); // keep incomplete last line for next chunk
  lines.forEach((line) => this.push(line.toUpperCase() + '\n'));
  callback();
}
```

❌ Mistake 3: Mixing object mode incorrectly between writable and readable sides
```javascript
// Wrong -- objectMode: true applies to BOTH sides by default, causing type errors downstream
new Transform({ objectMode: true, transform(row, enc, cb) { cb(null, JSON.stringify(row)); } })
// if piped to another objectMode:true stream expecting objects, string output breaks it

// Correct -- set writableObjectMode and readableObjectMode independently when they differ
new Transform({
  writableObjectMode: true,  // input: objects
  readableObjectMode: false, // output: strings/buffers
  transform(row, enc, cb) { cb(null, JSON.stringify(row)); }
});
```

---

## 🧠 Tricky Interview Question
```javascript
const { Transform } = require('stream');

const doubler = new Transform({
  transform(chunk, encoding, callback) {
    this.push(chunk);
    this.push(chunk); // pushing TWICE per input chunk
    callback();
  }
});

let output = '';
doubler.on('data', (d) => (output += d));
doubler.on('end', () => console.log(output));
doubler.write('A');
doubler.end();
```
Answer: Output is `AA`. A `_transform()` call doesn't have to call `push()` exactly once — you can call it 0, 1, or many times per input chunk. Here, writing `'A'` once triggers TWO `push(chunk)` calls, so the readable side emits `'A'` twice, concatenating to `'AA'`. This demonstrates that Transform streams don't guarantee a 1:1 mapping between input and output chunks — this flexibility is exactly what makes line-splitting, batching, and filtering transforms possible (push less than 1 chunk per input, or more than 1).

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between a Duplex stream and a Transform stream?
A1: A Duplex stream has independent Readable and Writable sides — what you write and what you read are UNRELATED (e.g. a TCP socket: you write a request, read a completely different response). A Transform stream is a SPECIALIZED Duplex where the readable side's output is DERIVED from the writable side's input — data written in gets algorithmically transformed and comes out the readable side (e.g. gzip: input=raw bytes, output=compressed bytes of the SAME data).

Q2: What is `_flush()` used for in a Transform stream, and when is it called?
A2: `_flush(callback)` is called exactly once, after all data has been written to the stream (i.e., after `.end()` is called and all `_transform()` calls have completed) but before the readable side signals `'end'`. It's used for emitting any final buffered/aggregated output — e.g., flushing a leftover incomplete line in a CSV parser, writing a trailing gzip footer, or appending a summary line (like a total count).

Q3: Can a Transform stream emit more or fewer chunks than it receives?
A3: Yes — there's no 1:1 requirement between calls to `_transform()` and calls to `this.push()`. A single `_transform()` call can push zero times (filtering out data), once (typical 1:1 mapping), or multiple times (splitting one input chunk into several output chunks) — this is how filter, batch, and line-splitting transforms work.

Q4: How do you build a transform that converts a stream of JS objects to JSON lines, and vice versa?
A4: Objects → JSON lines: set `objectMode: true` (or `writableObjectMode: true` with `readableObjectMode: false`), and in `_transform`, call `callback(null, JSON.stringify(obj) + '\n')`. JSON lines → objects: buffer incoming string chunks, split on `'\n'`, keep the last (possibly incomplete) line as leftover for the next chunk, `JSON.parse()` each complete line, and `push()` the resulting object with `objectMode: true` set on the output side.

Q5: Why is chaining multiple Transform streams via `.pipe()` memory-efficient compared to doing the same transformations with regular functions on a fully-loaded buffer?
A5: Each Transform in the chain only ever holds roughly one `highWaterMark`'s worth of data (default 16KB-64KB) at any moment — as soon as a chunk is transformed and pushed downstream, it can be garbage collected from the upstream buffer once consumed. Doing the same work with `Buffer.from(wholeFile)` + array methods requires the ENTIRE dataset in memory at every step, multiplied by however many transformation stages you have (each creating a full copy).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to compress, encrypt, decrypt, or parse data as it streams through (no full-buffer-in-memory step)
- Building ETL pipelines: parse → filter → transform → serialize → compress, all chained
- You want composable, reusable units that work with `.pipe()`/`pipeline()`

❌ Avoid when:
- The transformation requires looking at the ENTIRE dataset at once (e.g., sorting, deduplication across the whole set) — streams process sequentially, chunk by chunk, so global operations need a different approach (buffer first, or external sort)
- Data is small — a plain function `transform(wholeData)` is simpler and clearer

---

## 📊 Visual Diagram
```
TRANSFORM STREAM (Duplex that modifies data):

   WRITABLE side                 READABLE side
   (data comes IN)               (data comes OUT, modified)
        │                               │
        ▼                               ▲
  ┌──────────────────────────────────────────┐
  │          Transform Stream                 │
  │                                             │
  │   _transform(chunk, enc, callback) {        │
  │      const modified = process(chunk);       │
  │      this.push(modified);  ◄── 0, 1, or many │
  │      callback();                             │
  │   }                                           │
  │                                                │
  │   _flush(callback) { // called once at the end│
  │      this.push(finalSummary);                 │
  │      callback();                               │
  │   }                                             │
  └──────────────────────────────────────────┘

  CHAIN:
  readStream.pipe(parse).pipe(filter).pipe(serialize).pipe(gzip).pipe(writeStream)
             └─Transform─┘└─Transform┘└──Transform──┘└Transform┘
       Each stage only holds ~highWaterMark bytes at a time
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transform stream | Duplex that modifies data in flight | Flow में data modify करने वाला Duplex |
| _transform() | Core method defining the modification | Modification logic का core method |
| _flush() | Final cleanup/output after all input done | सारा input खत्म होने पर final output |
| push() | Emit output chunk(s) downstream | Output chunk downstream भेजना |
| objectMode | Carry JS objects instead of bytes | Bytes की जगह JS objects carry करना |
| Duplex stream | Independent readable + writable sides | Independent readable + writable sides |

---

## ⚡ 3-Line Summary
English: Transform streams are Duplex streams where output is derived from input, implemented via `_transform(chunk, encoding, callback)` and optionally `_flush(callback)`. They don't require a 1:1 input-to-output chunk mapping, enabling filtering, batching, and parsing. Chainable with `.pipe()`/`pipeline()` for memory-efficient ETL pipelines (parse → filter → compress → write).

Hindi: Transform streams Duplex streams हैं जहाँ output input से derive होता है, `_transform()` और optionally `_flush()` से implement होता है। 1:1 chunk mapping ज़रूरी नहीं — filtering, batching, parsing संभव है। `.pipe()`/`pipeline()` से chain करके memory-efficient ETL pipelines बनाए जा सकते हैं।

---

## ➡️ Next Topic
**51. Pipe + Pipeline** — deep dive into connecting streams safely, error propagation, and `stream.pipeline()` vs `.pipe()`.
