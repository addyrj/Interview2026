# 299. Stream + Buffer Questions
# हिंदी में: Stream + Buffer Tricky Questions

---

## 🔵 Simple Definition (English)
**Streams** process data in chunks instead of loading everything into memory at once; **Buffers** are Node's fixed-size, raw binary data containers (like a byte array) that streams pass around internally. Interview questions here probe backpressure, chunk boundaries (`data` events don't align with logical records), encoding pitfalls, and memory implications of streaming vs buffering.

## 🔵 सरल परिभाषा (Hindi)
**Streams** data को chunks में process करते हैं, पूरा memory में load किए बिना; **Buffers** Node के fixed-size, raw binary data containers हैं (byte array जैसे) जो streams internally pass करते हैं। Interview questions यहाँ backpressure, chunk boundaries (`data` events logical records से align नहीं होते), encoding pitfalls, और streaming बनाम buffering के memory implications test करते हैं।

---

## 🔴 Problem it Solves
Loading a 2GB file entirely into memory to process it (`fs.readFileSync`) crashes small-memory servers or wastes huge amounts of RAM. Streams solve this by processing data piece-by-piece, but introduce new complexity: what if the consumer is slower than the producer (backpressure)? What if a chunk boundary splits a UTF-8 multi-byte character or a JSON record in half? These interview questions target exactly those real-world gotchas.

## 🔴 यह क्यों बना? (Hindi)
2GB file को पूरा memory में load करके process करना (`fs.readFileSync`) छोटे-memory servers को crash कर सकता है या बहुत RAM waste करता है। Streams data को piece-by-piece process करके यह solve करते हैं, लेकिन नई complexity लाते हैं: consumer producer से slower हो तो क्या (backpressure)? Chunk boundary एक UTF-8 multi-byte character या JSON record को बीच में split कर दे तो क्या? यह interview questions exactly इन real-world gotchas को target करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → A **Readable** stream emits `data` events with Buffer chunks as data becomes available (e.g., reading a file piece by piece from disk).
Step 2 → A **Writable** stream's `.write(chunk)` returns `false` when its internal buffer is full (backpressure signal) — the producer SHOULD pause until a `'drain'` event fires.
Step 3 → `.pipe(destination)` automatically handles backpressure for you — pausing the source when the destination is overwhelmed, resuming when it drains. This is why `readable.pipe(writable)` is preferred over manual `data`/`write` wiring.
Step 4 → Chunk boundaries are ARBITRARY — a single `data` event might contain half a UTF-8 character, half a JSON object, or multiple log lines concatenated. You must buffer partial data yourself (or use a parsing Transform stream) to reassemble logical units.
Step 5 → `Buffer` stores raw bytes; converting to a string requires specifying an encoding (default `'utf8'`), and decoding a multi-byte character split across two buffers incorrectly produces mangled/replacement characters (�) unless you use `StringDecoder` which handles split multi-byte sequences correctly.
Step 6 → `Transform` streams let you modify chunks as they flow through (compression, encryption, parsing) while still respecting backpressure automatically.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक **Readable** stream `data` events के साथ Buffer chunks emit करता है जैसे-जैसे data available होता है (जैसे disk से file piece by piece पढ़ना)।
Step 2 → एक **Writable** stream का `.write(chunk)` `false` return करता है जब internal buffer full हो (backpressure signal) — producer को `'drain'` event तक pause करना चाहिए।
Step 3 → `.pipe(destination)` backpressure automatically handle करता है — destination overwhelmed हो तो source pause, drain होने पर resume। इसलिए `readable.pipe(writable)` manual `data`/`write` wiring से बेहतर है।
Step 4 → Chunk boundaries ARBITRARY हैं — एक `data` event में आधा UTF-8 character, आधा JSON object, या कई log lines concatenated हो सकते हैं। Logical units reassemble करने के लिए partial data खुद buffer करना पड़ेगा (या Transform stream parsing use करो)।
Step 5 → `Buffer` raw bytes store करता है; string में convert करने के लिए encoding specify करना पड़ता है (default `'utf8'`), और split multi-byte character को गलत तरीके से decode करने पर mangled/replacement characters (�) आते हैं, जब तक `StringDecoder` use न करो जो split sequences सही handle करता है।
Step 6 → `Transform` streams chunks को flow के दौरान modify करने देते हैं (compression, encryption, parsing) while backpressure automatically respect होता रहता है।

---

## 🟡 Real World Example
**Hotstar's video streaming backend** processes multi-gigabyte video files for transcoding using Node.js streams with `pipe()` chains: read from storage → transform (chunk/decrypt) → write to output — never loading a full video into memory. A real bug they'd guard against: naive `data` event handlers assuming each chunk is a complete "segment" would corrupt output, since TCP/disk I/O chunk boundaries don't respect video segment boundaries — exactly the kind of gotcha these interview questions test.

## 🟡 Real Example Hindi mein
**Hotstar का video streaming backend** multi-gigabyte video files को transcoding के लिए Node.js streams से process करता है `pipe()` chains के साथ: storage से read → transform (chunk/decrypt) → output में write — कभी पूरी video memory में load नहीं होती। एक real bug जिससे वे बचते हैं: naive `data` event handlers जो assume करें हर chunk एक complete "segment" है, output corrupt कर देंगे, क्योंकि TCP/disk I/O chunk boundaries video segment boundaries को respect नहीं करते — exactly यह gotcha यह interview questions test करते हैं।

---

## 💻 Code Example — Basic

```javascript
// stream-basic.js — reading a file as a stream vs buffering it all at once.
// Run: node stream-basic.js (creates and reads a demo file)
const fs = require('fs');

// Create a demo file first
fs.writeFileSync('demo.txt', 'Line1\nLine2\nLine3\n'.repeat(1000));

// --- BUFFERED approach: loads the WHOLE file into memory at once ---
const wholeFile = fs.readFileSync('demo.txt', 'utf8');
console.log('Buffered: loaded', wholeFile.length, 'characters into memory at once');

// --- STREAMING approach: processes the file piece by piece ---
const readStream = fs.createReadStream('demo.txt', { encoding: 'utf8', highWaterMark: 64 }); // small chunks for demo

let chunkCount = 0;
readStream.on('data', (chunk) => {
  chunkCount++;
  // NOTE: chunk boundaries are arbitrary — this might cut a "Line2\n" in half across two chunks!
  if (chunkCount <= 3) console.log(`Chunk ${chunkCount} (${chunk.length} chars):`, JSON.stringify(chunk.slice(0, 30)));
});

readStream.on('end', () => {
  console.log(`Streaming: processed file in ${chunkCount} chunks, low memory footprint throughout`);
  fs.unlinkSync('demo.txt'); // cleanup
});

readStream.on('error', (err) => console.error('Stream error:', err));
```

## 💻 Code Example — Advanced

```javascript
// stream-advanced.js — backpressure-aware pipe, Transform stream, and correct multi-byte decoding.
// Run: node stream-advanced.js
const { Readable, Transform } = require('stream');
const { StringDecoder } = require('string_decoder');

// --- 1. Custom Readable stream producing data on demand ---
class NumberStream extends Readable {
  constructor(max) {
    super();
    this.current = 1;
    this.max = max;
  }
  _read() {
    // _read is called by the stream machinery when the consumer is ready for more data (respects backpressure)
    if (this.current > this.max) {
      this.push(null); // signals end of stream
      return;
    }
    this.push(`${this.current}\n`);
    this.current++;
  }
}

// --- 2. Transform stream: doubles each number as it flows through ---
class DoubleTransform extends Transform {
  _transform(chunk, encoding, callback) {
    const num = parseInt(chunk.toString().trim(), 10);
    this.push(`${num * 2}\n`);
    callback(); // MUST call callback to signal "ready for next chunk" — forgetting this stalls the stream forever
  }
}

// --- 3. Custom Writable-like consumer using a Transform as a sink, tracking backpressure ---
const source = new NumberStream(5);
const doubler = new DoubleTransform();

source.pipe(doubler).on('data', (chunk) => {
  process.stdout.write(`Doubled: ${chunk}`);
});

// --- 4. Correctly decoding multi-byte UTF-8 characters split across buffer chunks ---
function demoStringDecoder() {
  const decoder = new StringDecoder('utf8');
  const fullString = 'Hello नमस्ते'; // mix of ASCII + multi-byte Devanagari characters
  const fullBuffer = Buffer.from(fullString, 'utf8');

  // Simulate the buffer arriving in two chunks, splitting MID-CHARACTER on purpose
  const splitPoint = 7; // likely splits inside a multi-byte Devanagari character
  const chunk1 = fullBuffer.slice(0, splitPoint);
  const chunk2 = fullBuffer.slice(splitPoint);

  console.log('--- Naive (WRONG) approach: toString() on each chunk independently ---');
  console.log(JSON.stringify(chunk1.toString('utf8') + chunk2.toString('utf8'))); // may show mangled/replacement chars

  console.log('--- Correct approach: StringDecoder handles split multi-byte sequences ---');
  const decoded = decoder.write(chunk1) + decoder.write(chunk2) + decoder.end();
  console.log(JSON.stringify(decoded)); // correctly reassembled, no mangling
}

demoStringDecoder();

// --- 5. Demonstrating backpressure with a slow writable ---
const { Writable } = require('stream');
class SlowWritable extends Writable {
  _write(chunk, encoding, callback) {
    setTimeout(() => {
      console.log('Slowly wrote chunk of size', chunk.length);
      callback(); // signals ready for next write — stream machinery waits for this before pushing more
    }, 50);
  }
}

const fastSource = new NumberStream(3);
const slowSink = new SlowWritable({ highWaterMark: 1 }); // tiny buffer to force backpressure quickly
fastSource.pipe(slowSink); // pipe() automatically pauses fastSource when slowSink can't keep up
```

---

## 🟠 Express.js Integration

```javascript
// server.js — streaming a large file response WITHOUT loading it fully into memory
const express = require('express');
const fs = require('fs');

const app = express();

app.get('/download/report', (req, res) => {
  const filePath = './large-report.csv'; // could be gigabytes

  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="report.csv"');

  const readStream = fs.createReadStream(filePath);

  // pipe() handles backpressure automatically: if the client's connection is slow,
  // Express/Node pauses reading from disk until the socket can accept more data
  readStream.pipe(res);

  readStream.on('error', (err) => {
    console.error('Stream error:', err);
    if (!res.headersSent) res.status(500).json({ error: 'Failed to stream file' });
  });
});

// Streaming request body upload handling (e.g., large file upload) without buffering it all first
app.post('/upload', (req, res) => {
  const writeStream = fs.createWriteStream('./uploads/incoming.dat');
  req.pipe(writeStream); // streams the incoming request body directly to disk, chunk by chunk

  writeStream.on('finish', () => res.json({ status: 'uploaded' }));
  writeStream.on('error', (err) => res.status(500).json({ error: err.message }));
});

app.listen(3000, () => console.log('Streaming file server on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming each `data` event chunk is a complete logical record (line, JSON object, etc.)
✅ Correct: Buffer partial data across chunk boundaries and split on your delimiter yourself, or use `readline`/a parsing library

```javascript
// Wrong — assumes chunk boundaries align with newlines (they often DON'T for large files)
stream.on('data', (chunk) => {
  const line = chunk.toString(); // might be half a line, or multiple lines concatenated!
  processLine(line);
});

// Right — accumulate and split correctly, keeping any trailing partial line for next chunk
let buffer = '';
stream.on('data', (chunk) => {
  buffer += chunk.toString();
  const lines = buffer.split('\n');
  buffer = lines.pop(); // last entry might be incomplete, keep it for next chunk
  lines.forEach(processLine);
});
```

❌ Mistake 2: Ignoring backpressure by writing in a tight loop without checking `.write()`'s return value
✅ Correct: Check the boolean return of `.write()`; if `false`, pause and wait for `'drain'` before writing more (or just use `.pipe()` which does this for you)

```javascript
// Wrong — floods the writable's internal buffer, unbounded memory growth
for (const chunk of hugeArrayOfChunks) {
  writable.write(chunk); // ignoring backpressure signal entirely
}

// Right
function writeAll(writable, chunks, i = 0) {
  while (i < chunks.length) {
    const ok = writable.write(chunks[i++]);
    if (!ok) { // buffer full -> wait for drain before continuing
      writable.once('drain', () => writeAll(writable, chunks, i));
      return;
    }
  }
}
```

---

## 🧠 Tricky Interview Question

```javascript
const buf1 = Buffer.from('\u{1F600}'); // 😀 emoji, 4 bytes in UTF-8
console.log(buf1.length); // ?

const half1 = buf1.slice(0, 2);
const half2 = buf1.slice(2, 4);
console.log(half1.toString('utf8')); // ?
console.log(half2.toString('utf8')); // ?
console.log(half1.toString('utf8') + half2.toString('utf8')); // ?
console.log(Buffer.concat([half1, half2]).toString('utf8')); // ?
```
Answer: `buf1.length` is `4` (the 😀 emoji takes 4 bytes in UTF-8, NOT 1 "character" in byte terms). `half1.toString('utf8')` and `half2.toString('utf8')` BOTH print the Unicode replacement character `�` (U+FFFD) — because each half is an INVALID, incomplete UTF-8 byte sequence on its own, and `Buffer.prototype.toString()` replaces undecodable bytes with `�`. Concatenating the two decoded (already-mangled) STRINGS gives `"��"` — two replacement characters, the original emoji is PERMANENTLY LOST because decoding happened too early, per-half. But `Buffer.concat([half1, half2]).toString('utf8')` correctly prints `😀` — because concatenation happens at the BYTE level BEFORE decoding, reconstructing the valid 4-byte sequence first. **Lesson: never decode (`.toString()`) partial buffer chunks independently — concatenate the raw Buffers first, or use `StringDecoder` which tracks incomplete multi-byte sequences across chunks.**

---

## ⚫ Interview Questions + Answers

Q1: What is backpressure in Node.js streams, and why does it matter?
A1: Backpressure occurs when a Readable stream produces data faster than a Writable stream can consume it. Without handling it, the writable's internal buffer grows unboundedly, risking out-of-memory crashes. Node signals backpressure via `.write()` returning `false`, and streams should pause production until the subsequent `'drain'` event. `.pipe()` handles this automatically, which is why it's preferred over manual `data`/`write` wiring.

Q2: What are the four fundamental stream types in Node.js?
A2: **Readable** (source of data, e.g. `fs.createReadStream`), **Writable** (destination, e.g. `fs.createWriteStream`), **Duplex** (both readable and writable, e.g. TCP sockets), **Transform** (a Duplex stream that modifies data as it passes through, e.g. `zlib.createGzip()`).

Q3: Why shouldn't you decode (`.toString()`) each data chunk from a UTF-8 text stream independently?
A3: Because a multi-byte UTF-8 character can be split across two chunk boundaries (as shown in the tricky question), and decoding an incomplete byte sequence produces replacement characters (`�`), permanently corrupting the data. Use `StringDecoder` (which buffers incomplete trailing bytes across `.write()` calls) or concatenate raw Buffers before decoding.

Q4: What's the difference between `highWaterMark` for object-mode streams vs byte-mode streams?
A4: For byte/buffer streams, `highWaterMark` is the number of BYTES to buffer before backpressure kicks in (default 16KB for fs/network streams). For object-mode streams (`objectMode: true`, used when streaming JS objects instead of bytes), `highWaterMark` is the number of OBJECTS/chunks to buffer, since object sizes vary and byte-counting doesn't apply.

Q5: How would you process a huge CSV file line-by-line without loading it all into memory?
A5: Use `fs.createReadStream(file)` piped into the built-in `readline.createInterface()` (or a CSV-parsing Transform stream), handling each `'line'` event as it arrives. This keeps memory usage proportional to one line/chunk at a time, not the whole file size, and naturally respects backpressure since `readline` consumes the underlying stream properly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Processing large files, HTTP request/response bodies, or any data too big (or unbounded) to hold fully in memory
- Piping data through multiple transformation stages (compress → encrypt → upload)

❌ Avoid when:
- Data is small and fits comfortably in memory — the extra complexity (chunk boundary handling, backpressure) isn't worth it for a 2KB JSON payload; just use `fs.readFile`/buffered APIs

---

## 📊 Visual Diagram
```
 Readable ──data chunks──▶ internal buffer ──.write()──▶ Writable
   (fast producer)          (highWaterMark)      │         (slow consumer)
                                                   │
                            write() returns false when buffer full
                                     │
                                     ▼
                         producer PAUSES (via .pipe()'s auto-pause)
                                     │
                         Writable catches up, buffer drains
                                     │
                                'drain' event fires
                                     │
                         producer RESUMES automatically
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Backpressure | Consumer slower than producer, signal to slow down | Consumer slow, producer को रुकने का signal |
| Chunk | A piece of streamed data, arbitrary boundary | Streamed data का एक टुकड़ा, arbitrary boundary |
| highWaterMark | Buffer size threshold before backpressure | Backpressure से पहले buffer size limit |
| StringDecoder | Correctly decodes split multi-byte sequences | Split multi-byte sequences को सही decode करता है |
| Transform stream | Modifies data as it passes through | Data को गुज़रते समय modify करने वाला stream |

---

## ⚡ 3-Line Summary
English: Streams process data in arbitrary-boundary chunks, so logical records (lines, JSON, multi-byte UTF-8 characters) can split across chunks — never decode or parse a chunk in isolation. Backpressure (via `.write()`'s boolean return and `'drain'`) prevents unbounded memory growth, and `.pipe()` handles it automatically.
Hindi: Streams data को arbitrary-boundary chunks में process करते हैं, इसलिए logical records (lines, JSON, multi-byte UTF-8 characters) chunks के बीच split हो सकते हैं — किसी chunk को अलग से decode/parse मत करो। Backpressure (`.write()` के boolean return और `'drain'` से) unbounded memory growth रोकता है, और `.pipe()` इसे automatically handle करता है।

---

## ➡️ Next Topic
**300. System Design — Node.js Backend** — the capstone: designing a complete scalable Node.js backend end-to-end.
