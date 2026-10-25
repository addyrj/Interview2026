# 49. Writable Streams
# हिंदी में: Writable Streams — Data को Destination में Chunks में Write करना

---

## 🔵 Simple Definition (English)
A **Writable stream** is a destination you send data to in chunks — e.g. `fs.createWriteStream()`, `http.ServerResponse` (the `res` object), `process.stdout`. You call `.write(chunk)` repeatedly and `.end()` when done. If the internal buffer fills up faster than the destination can consume it, `.write()` returns `false` — this is the **backpressure** signal telling you to slow down.

## 🔵 सरल परिभाषा (Hindi)
**Writable stream** एक destination है जिसमें आप data chunks में भेजते हो — जैसे `fs.createWriteStream()`, `http.ServerResponse` (`res` object), `process.stdout`। आप `.write(chunk)` repeatedly call करते हो और खत्म होने पर `.end()`। अगर internal buffer destination के consume करने से तेज़ भर जाए, तो `.write()` `false` return करता है — यही **backpressure** signal है, slow down करने के लिए।

---

## 🔴 Problem it Solves
Without a buffering/backpressure mechanism, a fast data producer could overwhelm a slow consumer (e.g. writing to a slow disk, or sending data over a throttled network connection) — causing unbounded memory growth as unwritten data piles up in memory waiting to be flushed. Writable streams solve this with an internal buffer governed by `highWaterMark`, and a clear signal (`write()` returning `false`, followed by a `'drain'` event) that lets producers pace themselves to match the consumer's actual throughput.

## 🔴 यह क्यों बना? (Hindi)
Backpressure mechanism के बिना, एक fast producer किसी slow consumer (जैसे slow disk, throttled network) को overwhelm कर सकता है — unwritten data memory में ढेर हो जाता है, memory unbounded बढ़ती है। Writable streams इसे `highWaterMark` से governed internal buffer से solve करते हैं, और clear signal (`write()` का `false` return, फिर `'drain'` event) देते हैं जिससे producer अपनी speed consumer के throughput से match कर सके।

---

## 🟢 How it Works — Step by Step

Step 1 → Creation: `fs.createWriteStream(path, options)` — options include `highWaterMark` (buffer threshold, default 16KB) and `flags` (`'a'` for append, `'w'` for overwrite).
Step 2 → Write data: `writable.write(chunk, [encoding], [callback])` — returns `true` if it's safe to write more immediately, `false` if the internal buffer exceeded `highWaterMark`.
Step 3 → Backpressure signal: when `.write()` returns `false`, STOP writing and wait for the `'drain'` event, which fires once the buffer has emptied enough to accept more.
Step 4 → Finish writing: `writable.end([chunk])` — flushes any remaining buffered data and emits `'finish'` once ALL data is flushed to the underlying resource.
Step 5 → `'error'` event fires on write failures (disk full, permission denied, broken pipe) — must be handled or it crashes the process.
Step 6 → Custom Writable: extend `stream.Writable` and implement `_write(chunk, encoding, callback)` — call `callback()` when the chunk is fully processed (or `callback(err)` on failure), which internally drives the backpressure mechanism.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Creation: `fs.createWriteStream()` — options में `highWaterMark` (default 16KB), `flags` (`'a'` append, `'w'` overwrite)।
Step 2 → Data write करो: `.write(chunk)` — `true` return करता है लिखना safe है, `false` buffer भर गया।
Step 3 → Backpressure signal: `false` मिलने पर लिखना रोको, `'drain'` event तक wait करो।
Step 4 → Writing खत्म करो: `.end()` — बाकी buffered data flush करता है, `'finish'` emit होता है।
Step 5 → `'error'` event — write failure पर (disk full, permission denied)।
Step 6 → Custom Writable: `stream.Writable` extend करो, `_write(chunk, encoding, callback)` implement करो — chunk process होने पर `callback()` call करो, यही backpressure drive करता है।

---

## 🟡 Real World Example
**Swiggy's delivery partner location logging:** Every 3 seconds, thousands of delivery partner apps send GPS coordinates to a logging service, which writes each entry as a line to a rotating log file using `fs.createWriteStream()` with the `'a'` (append) flag. During peak lunch hours, write volume spikes — the service checks `.write()`'s return value, and if `false`, buffers incoming GPS pings in a small in-memory queue until `'drain'` fires, preventing disk I/O from becoming a bottleneck that crashes the service.

## 🟡 Real Example Hindi mein
**Swiggy delivery partner location logging:** हर 3 seconds में हज़ारों delivery partner apps GPS coordinates भेजते हैं, logging service `fs.createWriteStream()` (append mode) से हर entry को log file में लिखती है। Peak hours में write volume बढ़ता है — service `.write()` का return value check करती है, `false` मिलने पर incoming pings को छोटे queue में buffer करती है जब तक `'drain'` न आए — disk I/O bottleneck बनने से बचता है।

---

## 💻 Code Example — Basic
```javascript
// writable-basics.js
const fs = require('fs');
const { Writable } = require('stream');

// 1. BASIC WRITABLE STREAM -- write to a file
const writeStream = fs.createWriteStream('./output.log', { flags: 'a' }); // 'a' = append

writeStream.write('Line 1: Server started\n');
writeStream.write('Line 2: Processing request\n');
writeStream.end('Line 3: Final line before close\n'); // last write + signal end

writeStream.on('finish', () => console.log('All data flushed to disk'));
writeStream.on('error', (err) => console.error('Write error:', err.message));

// 2. CHECKING BACKPRESSURE RETURN VALUE
const fastWriteStream = fs.createWriteStream('./big-output.log');
const canContinue = fastWriteStream.write('some data chunk');
console.log('Can write more immediately?', canContinue); // true/false

// 3. CUSTOM WRITABLE STREAM -- collect data into an array (useful for testing)
class ArrayCollectorStream extends Writable {
  constructor() {
    super();
    this.collected = [];
  }
  _write(chunk, encoding, callback) {
    this.collected.push(chunk.toString()); // store the chunk
    callback(); // MUST call callback to signal chunk is processed
  }
}

const collector = new ArrayCollectorStream();
collector.write('first chunk');
collector.write('second chunk');
collector.end(() => {
  console.log('Collected:', collector.collected); // ['first chunk', 'second chunk']
});

// 4. process.stdout IS A WRITABLE STREAM
process.stdout.write('Direct write to stdout\n');
```

## 💻 Code Example — Advanced
```javascript
// writable-advanced.js -- production patterns
const fs = require('fs');
const { Writable } = require('stream');

// ─── 1. CUSTOM WRITABLE WITH ASYNC _write (e.g. writing to a database) ────────
class DatabaseWriteStream extends Writable {
  constructor(dbClient, options = {}) {
    super({ ...options, objectMode: true }); // objectMode: accept JS objects, not just buffers
    this.dbClient = dbClient;
    this.writeCount = 0;
  }

  async _write(record, encoding, callback) {
    try {
      await this.dbClient.insert(record); // simulate async DB insert
      this.writeCount++;
      callback(); // success -- ready for next chunk
    } catch (err) {
      callback(err); // propagates as 'error' event, stops the stream
    }
  }

  _final(callback) {
    // Called when .end() is invoked -- good place for final cleanup/flush
    console.log(`Finalizing: ${this.writeCount} records written`);
    callback();
  }
}

// Mock DB client
const mockDb = { insert: async (record) => new Promise((res) => setTimeout(res, 10)) };

// ─── 2. HANDLING BACKPRESSURE PROPERLY WHEN WRITING A LARGE DATASET ──────────
async function writeManyRecords(writable, records) {
  for (const record of records) {
    const canContinue = writable.write(record);
    if (!canContinue) {
      // Wait for 'drain' before writing more -- prevents unbounded buffering
      await new Promise((resolve) => writable.once('drain', resolve));
    }
  }
  writable.end();
}

// ─── 3. BATCHED WRITABLE (buffer N items, then flush as one write -- performance) ─
class BatchedFileWriter extends Writable {
  constructor(filePath, batchSize = 100) {
    super({ objectMode: true });
    this.fileStream = fs.createWriteStream(filePath, { flags: 'a' });
    this.batchSize = batchSize;
    this.buffer = [];
  }

  _write(record, encoding, callback) {
    this.buffer.push(JSON.stringify(record));
    if (this.buffer.length >= this.batchSize) {
      this.flush(callback); // flush when batch is full
    } else {
      callback(); // accept more without flushing yet
    }
  }

  flush(callback) {
    const lines = this.buffer.join('\n') + '\n';
    this.buffer = [];
    this.fileStream.write(lines, callback); // single disk write for the whole batch
  }

  _final(callback) {
    if (this.buffer.length > 0) {
      this.flush(() => { this.fileStream.end(callback); });
    } else {
      this.fileStream.end(callback);
    }
  }
}

// ─── DEMO ──────────────────────────────────────────────────────────────────────
(async () => {
  const dbStream = new DatabaseWriteStream(mockDb);
  const records = Array.from({ length: 5 }, (_, i) => ({ id: i, name: `Item ${i}` }));
  await writeManyRecords(dbStream, records);
  dbStream.end();
})();
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const fs = require('fs');
const app = express();

// 1. res IS A WRITABLE STREAM -- you can write chunks directly
app.get('/stream-response', (req, res) => {
  res.setHeader('Content-Type', 'text/plain');
  res.write('Starting data export...\n');

  let i = 0;
  const interval = setInterval(() => {
    const canContinue = res.write(`Chunk ${i}\n`); // backpressure-aware write
    i++;
    if (i >= 5) {
      clearInterval(interval);
      res.end('Export complete.\n'); // finalize the response
    }
    if (!canContinue) {
      console.log('Response buffer full -- client is slow to receive');
    }
  }, 500);
});

// 2. LOGGING MIDDLEWARE USING A SHARED WRITABLE LOG STREAM
const accessLogStream = fs.createWriteStream('./access.log', { flags: 'a' });

app.use((req, res, next) => {
  const logLine = `${new Date().toISOString()} ${req.method} ${req.url}\n`;
  const ok = accessLogStream.write(logLine);
  if (!ok) {
    // Buffer full -- in a real app, you might queue or sample logs under heavy load
    console.warn('Access log stream backpressure detected');
  }
  next();
});

// 3. PIPING UPLOADED FILE DIRECTLY TO A WRITABLE DESTINATION
app.post('/upload', (req, res) => {
  const destStream = fs.createWriteStream('./uploads/incoming-file.bin');
  req.pipe(destStream); // req (Readable) -> destStream (Writable), backpressure handled automatically

  destStream.on('finish', () => res.json({ message: 'Upload saved successfully' }));
  destStream.on('error', (err) => res.status(500).json({ error: err.message }));
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Ignoring the return value of `.write()` and writing in a tight loop
```javascript
// Wrong -- ignores backpressure, can cause unbounded memory growth
for (const record of millionsOfRecords) {
  writable.write(JSON.stringify(record)); // never checks if buffer is full
}

// Correct -- pause when write() returns false, resume on 'drain'
for (const record of millionsOfRecords) {
  const canContinue = writable.write(JSON.stringify(record));
  if (!canContinue) {
    await new Promise((resolve) => writable.once('drain', resolve));
  }
}
```

❌ Mistake 2: Calling `.write()` after `.end()`
```javascript
// Wrong -- throws "write after end" error
writable.end();
writable.write('more data'); // ERROR: write after end

// Correct -- .end() is always the LAST call; optionally pass final data to it
writable.end('final chunk of data');
```

❌ Mistake 3: Forgetting to call `callback()` in a custom `_write()` implementation
```javascript
// Wrong -- stream hangs forever, 'finish' never fires, backpressure breaks
class MyWritable extends Writable {
  _write(chunk, encoding, callback) {
    doSomethingAsync(chunk); // callback never called -- stream stalls!
  }
}

// Correct -- always call callback(), even on error
class MyWritable extends Writable {
  _write(chunk, encoding, callback) {
    doSomethingAsync(chunk, (err) => callback(err)); // signals completion/failure
  }
}
```

---

## 🧠 Tricky Interview Question
```javascript
const { Writable } = require('stream');

const writable = new Writable({
  write(chunk, encoding, callback) {
    console.log('Writing:', chunk.toString());
    callback();
  }
});

writable.write('A');
writable.write('B');
writable.end('C');
console.log('After end() call');
```
Answer: Output is `Writing: A`, `Writing: B`, `Writing: C`, then `After end() call` is printed LAST relative to the writes — wait, actually since `_write` here is synchronous (calls `callback()` immediately), all three writes process synchronously in order BEFORE `end()` returns, so the actual order is: `Writing: A`, `Writing: B`, `Writing: C`, `After end() call`. The key insight: `.end(chunk)` both writes the final chunk AND signals no more writes will come — it's equivalent to `.write(chunk)` followed by `.end()`. If `_write` were async (used `setTimeout` before `callback()`), `'After end() call'` would print FIRST because `.end()` doesn't block — it queues the final write and returns immediately; `'finish'` fires only once all queued writes genuinely complete.

---

## ⚫ Interview Questions + Answers

Q1: What does it mean when `.write()` returns `false`, and what should you do?
A1: It means the internal buffer has reached or exceeded `highWaterMark` — the Writable's destination (disk, network, downstream consumer) can't keep up with incoming data. You should STOP calling `.write()` and wait for the `'drain'` event, which fires once the buffer has emptied below the threshold, signaling it's safe to resume writing. Ignoring this and writing anyway still works (Node buffers it) but risks unbounded memory growth under sustained high throughput.

Q2: What's the difference between the `'finish'` and `'close'` events on a Writable stream?
A2: `'finish'` fires when `.end()` has been called AND all buffered data has been successfully flushed to the underlying system (e.g. written to disk) — it means "there's no more data to write." `'close'` fires when the underlying resource (file descriptor, socket) is actually closed, which happens after `'finish'` and may include additional cleanup. For file streams, `'finish'` usually fires before `'close'`.

Q3: How do you implement a custom Writable stream?
A3: Extend `stream.Writable` and implement `_write(chunk, encoding, callback)` (for single chunks) or `_writev(chunks, callback)` (for batched writes, an optimization Node may use internally). Inside `_write`, process the chunk (write to disk, insert into DB, etc.) and call `callback()` on success or `callback(err)` on failure — this callback is what drives the stream's internal state machine and backpressure signaling.

Q4: Why does `res` in an Express/HTTP handler behave like a Writable stream?
A4: `http.ServerResponse` (which `res` is an instance of, with Express extensions) EXTENDS Node's `Writable` stream class. This is why you can call `res.write(chunk)` to send partial data and `res.end()` to finish the response — and why you can `.pipe()` a Readable (like a file stream) directly into `res`, letting Node handle chunked transfer encoding and backpressure between the file read speed and the client's network receive speed automatically.

Q5: What's the purpose of the `_final(callback)` method in a custom Writable?
A5: `_final()` is called automatically when `.end()` is invoked and all previously buffered writes have completed, but BEFORE the `'finish'` event fires. It's the ideal place for final cleanup logic that depends on ALL writes being done — e.g., flushing a remaining batch buffer, closing a database transaction, or writing a trailing footer to a file — ensuring this logic runs exactly once, at the right time, not interleaved with regular `_write()` calls.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing large amounts of data to disk, network, or another stream destination
- You need backpressure control between a fast producer and slow consumer
- Building custom sinks (database writers, log aggregators, batch processors)

❌ Avoid when:
- Writing a small, fixed amount of data where `fs.writeFile()` (one-shot) is simpler
- You don't actually need streaming semantics — sometimes a simple array + single write is clearer for small datasets

---

## 📊 Visual Diagram
```
WRITABLE STREAM BACKPRESSURE FLOW:

  Producer                Writable (buffer: highWaterMark)         Destination
  ┌────────┐              ┌───────────────────────────┐            ┌─────────┐
  │ write()│ ──chunk1───► │ ███░░░░░░░ (buffer filling)│ ──flush──► │  Disk / │
  │ write()│ ──chunk2───► │ ██████░░░░                 │            │  Network│
  │ write()│ ──chunk3───► │ ██████████ (FULL!)          │            └─────────┘
  └────────┘              └───────────────────────────┘
       │                         │
       │   write() returns FALSE │
       ▼                         ▼
   STOP writing            buffer drains as destination catches up
       │                         │
       │   'drain' event fires   │
       └────────◄────────────────┘
       RESUME writing

  .end(chunk) = .write(chunk) + no more writes allowed
  'finish' event = all buffered data flushed successfully
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Writable stream | Destination for chunked data | Chunked data का destination |
| write() | Send a chunk to the stream | Stream में chunk भेजना |
| end() | Signal no more data, flush remaining | आगे data नहीं, बचा हुआ flush करना |
| drain event | Buffer has room again | Buffer में फिर जगह बनी |
| finish event | All data flushed successfully | सारा data successfully flush हुआ |
| _write() | Internal method for custom Writable | Custom Writable का internal method |
| highWaterMark | Buffer size threshold | Buffer size की सीमा |

---

## ⚡ 3-Line Summary
English: Writable streams accept data via `.write()` and signal completion via `.end()`, using `highWaterMark` and the `false`/`'drain'` signal pair to implement backpressure. Custom Writables implement `_write(chunk, encoding, callback)`, always calling `callback()` to avoid stalling the stream. `res` in Express is itself a Writable stream, enabling direct `.pipe()` from file/DB sources.

Hindi: Writable streams `.write()` से data accept करते हैं, `.end()` से completion signal करते हैं, `highWaterMark` और `false`/`'drain'` pair से backpressure implement होता है। Custom Writables `_write()` implement करते हैं, हमेशा `callback()` call करना ज़रूरी है। Express का `res` खुद एक Writable stream है।

---

## ➡️ Next Topic
**50. Transform Streams** — streams that are both Readable and Writable, modifying data as it flows through (compression, encryption, parsing).
