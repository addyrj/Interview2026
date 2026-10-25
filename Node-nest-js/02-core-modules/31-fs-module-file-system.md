# 31. fs Module — File System
# हिंदी में: fs Module — File System को Handle करना

---

## 🔵 Simple Definition (English)
The **`fs`** (File System) module is Node.js's built-in API for interacting with the file system — reading, writing, creating, deleting, and watching files/directories. It offers three styles: synchronous (`fs.readFileSync`), callback-based (`fs.readFile`), and Promise-based (`fs.promises` / `node:fs/promises`).

## 🔵 सरल परिभाषा (Hindi)
**`fs`** (File System) module Node.js का built-in API है file system से interact करने के लिए — files/directories पढ़ना, लिखना, बनाना, delete करना, और watch करना। इसके तीन styles हैं: synchronous (`fs.readFileSync`), callback-based (`fs.readFile`), और Promise-based (`fs.promises` / `node:fs/promises`)।

---

## 🔴 Problem it Solves
Any real server application needs to read config files, serve static assets, log to disk, process uploaded files, or generate reports/exports — all requiring filesystem access. JavaScript running in a browser has NO filesystem access for security reasons, so when Node brought JS to the server, it needed a completely new capability: a safe, flexible API to touch the local disk. `fs` provides this, modeled loosely on POSIX file operations, with Node-specific ergonomics (callbacks → Promises evolution).

## 🔴 यह क्यों बना? (Hindi)
कोई भी real server application को config files पढ़नी होती हैं, static assets serve करनी होती हैं, disk पर log करना होता है, uploaded files process करनी होती हैं, या reports/exports generate करने होते हैं — इन सबके लिए filesystem access चाहिए। Browser में चलने वाला JavaScript security reasons की वजह से filesystem access नहीं रखता, इसलिए जब Node ने JS को server पर लाया, एक बिलकुल नई capability चाहिए थी: local disk को safely, flexibly touch करने का API। `fs` यह देता है, POSIX file operations पर loosely modeled, Node-specific ergonomics के साथ (callbacks → Promises evolution)।

---

## 🟢 How it Works — Step by Step

Step 1 → `const fs = require('fs')` (CJS) or `import fs from 'node:fs'` (ESM) — the `node:` prefix is the recommended modern way to import core modules, making it unambiguous they're built-in (not an npm package named `fs`).
Step 2 → Three API styles for nearly every operation: `fs.readFileSync(path)` (blocks the event loop until done — returns value directly), `fs.readFile(path, callback)` (non-blocking, result via callback), `fs.promises.readFile(path)` or `require('fs/promises').readFile(path)` (non-blocking, returns a Promise — usable with `async/await`).
Step 3 → Reading: `readFile`/`readFileSync` load the ENTIRE file into memory at once — fine for small/medium files, dangerous for huge ones (use streams instead, covered separately).
Step 4 → Writing: `writeFile`/`writeFileSync` overwrite the whole file; `appendFile`/`appendFileSync` add to the end without overwriting.
Step 5 → Metadata: `fs.stat(path)` returns file info (size, type, timestamps) without reading content — essential for checking existence, size, or whether a path is a file vs. directory.
Step 6 → Directories: `fs.mkdir`, `fs.readdir`, `fs.rmdir` manage folders; `fs.watch` observes changes.
Step 7 → ALWAYS prefer async (`fs.promises` or callback) versions in server code — sync versions BLOCK the entire event loop, freezing all other requests until the disk operation completes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const fs = require('fs')` (CJS) या `import fs from 'node:fs'` (ESM) — `node:` prefix core modules import करने का modern recommended तरीका है, स्पष्ट करता है कि built-in हैं (fs नाम का कोई npm package नहीं)।
Step 2 → हर operation के लगभग तीन API styles: `fs.readFileSync(path)` (event loop को block करता है जब तक पूरा न हो — value directly return करता है), `fs.readFile(path, callback)` (non-blocking, result callback से), `fs.promises.readFile(path)` या `require('fs/promises').readFile(path)` (non-blocking, Promise return करता है — `async/await` के साथ usable)।
Step 3 → Reading: `readFile`/`readFileSync` पूरी file एक बार में memory में load करते हैं — छोटी/medium files के लिए fine, बड़ी files के लिए dangerous (उसके लिए streams use करो, अलग topic में)।
Step 4 → Writing: `writeFile`/`writeFileSync` पूरी file overwrite करते हैं; `appendFile`/`appendFileSync` बिना overwrite किए end में add करते हैं।
Step 5 → Metadata: `fs.stat(path)` file info देता है (size, type, timestamps) content पढ़े बिना — existence check, size, या path file है या directory जानने के लिए ज़रूरी।
Step 6 → Directories: `fs.mkdir`, `fs.readdir`, `fs.rmdir` folders manage करते हैं; `fs.watch` changes observe करता है।
Step 7 → Server code में हमेशा async (`fs.promises` या callback) versions prefer करो — sync versions पूरे event loop को BLOCK करते हैं, disk operation पूरा होने तक सभी requests freeze हो जाती हैं।

---

## 🟡 Real World Example
**Swiggy's restaurant onboarding service:** When a new restaurant signs up, the service receives their menu as a CSV upload, reads it with `fs.promises.readFile()`, parses it, validates entries, and writes a processed JSON version to a staging folder with `fs.promises.writeFile()`. It also writes to an audit log file using `fs.promises.appendFile()` for every onboarding action (immutable record, never overwritten). All operations are async so the service can handle hundreds of concurrent onboarding requests without one slow disk write blocking everyone else.

## 🟡 Real Example Hindi mein
**Swiggy का restaurant onboarding service:** जब कोई नया restaurant sign up करता है, service उनका menu CSV upload की तरह receive करती है, `fs.promises.readFile()` से पढ़ती है, parse करती है, entries validate करती है, और processed JSON version `fs.promises.writeFile()` से staging folder में लिखती है। यह हर onboarding action के लिए `fs.promises.appendFile()` से audit log file में भी लिखती है (immutable record, कभी overwrite नहीं)। सभी operations async हैं ताकि service सैकड़ों concurrent onboarding requests handle कर सके बिना किसी एक slow disk write से बाकी सब को block किए।

---

## 💻 Code Example — Basic

```javascript
// fsBasics.js — core fs operations using Promises (recommended modern style)
const fs = require('fs/promises'); // Promise-based API, no callbacks needed

async function main() {
  // WRITE a file (creates it if it doesn't exist, overwrites if it does)
  await fs.writeFile('./notes.txt', 'Hello from Node.js!\n');
  console.log('File written.');

  // READ the file back as a string
  const content = await fs.readFile('./notes.txt', 'utf8'); // 'utf8' = return string, not Buffer
  console.log('File content:', content);

  // APPEND without overwriting existing content
  await fs.appendFile('./notes.txt', 'Second line.\n');

  // Get file metadata (size, type, timestamps)
  const stats = await fs.stat('./notes.txt');
  console.log('File size (bytes):', stats.size);
  console.log('Is file?', stats.isFile());
  console.log('Is directory?', stats.isDirectory());

  // DELETE the file when done
  await fs.unlink('./notes.txt');
  console.log('File deleted.');
}

main().catch(console.error); // always handle errors — async functions reject on failure
```

## 💻 Code Example — Advanced

```javascript
// fsAdvanced.js — production patterns: existence checks, directories, error codes
const fs = require('fs/promises');
const path = require('path');

async function ensureDirectoryExists(dirPath) {
  try {
    await fs.mkdir(dirPath, { recursive: true }); // recursive: true = create nested dirs, no error if exists
  } catch (err) {
    if (err.code !== 'EEXIST') throw err; // ignore "already exists", rethrow anything else
  }
}

async function safeReadJSON(filePath) {
  try {
    const raw = await fs.readFile(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') {
      // ENOENT = "Error NO ENTry" — file doesn't exist. Handle gracefully.
      console.warn(`File not found: ${filePath}, returning default.`);
      return {}; // fallback default instead of crashing
    }
    throw err; // re-throw unexpected errors (permissions, corrupt JSON, etc.)
  }
}

async function processUploadedFile(uploadDir, filename, data) {
  await ensureDirectoryExists(uploadDir); // make sure the folder exists before writing

  const filePath = path.join(uploadDir, filename); // always build paths safely with path.join

  // Check if file already exists to avoid accidental overwrite of user data
  let exists = true;
  try {
    await fs.access(filePath); // fs.access throws if the path doesn't exist
  } catch {
    exists = false;
  }

  if (exists) {
    throw new Error(`File already exists: ${filePath}`);
  }

  await fs.writeFile(filePath, data); // safe to write — confirmed no collision
  return filePath;
}

async function listFilesWithMetadata(dirPath) {
  const entries = await fs.readdir(dirPath, { withFileTypes: true }); // withFileTypes gives Dirent objects
  const results = [];

  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    const stats = await fs.stat(fullPath); // get size, modified time, etc.
    results.push({
      name: entry.name,
      isDirectory: entry.isDirectory(),
      sizeBytes: stats.size,
      modifiedAt: stats.mtime,
    });
  }
  return results;
}

(async () => {
  await ensureDirectoryExists('./uploads');
  const config = await safeReadJSON('./config.json'); // returns {} if missing, no crash
  console.log('Config:', config);

  const files = await listFilesWithMetadata('./uploads');
  console.log('Files in uploads:', files);
})();
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express route reading/writing files safely (async, non-blocking)
const express = require('express');
const fs = require('fs/promises');
const path = require('path');

const app = express();
app.use(express.json());

// Serve a generated report file
app.get('/reports/:filename', async (req, res) => {
  const filePath = path.join(__dirname, 'reports', req.params.filename); // anchor to __dirname

  try {
    const content = await fs.readFile(filePath, 'utf8'); // non-blocking read
    res.type('text/plain').send(content);
  } catch (err) {
    if (err.code === 'ENOENT') {
      return res.status(404).json({ error: 'Report not found' });
    }
    res.status(500).json({ error: 'Failed to read report' }); // generic server error for anything else
  }
});

// Save user-submitted notes to disk
app.post('/notes', async (req, res) => {
  const { content } = req.body;
  const filePath = path.join(__dirname, 'data', `note-${Date.now()}.txt`);

  try {
    await fs.mkdir(path.dirname(filePath), { recursive: true }); // ensure folder exists
    await fs.writeFile(filePath, content);
    res.status(201).json({ message: 'Note saved', path: filePath });
  } catch (err) {
    res.status(500).json({ error: 'Failed to save note' });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using synchronous `fs` methods inside request handlers
```javascript
// Wrong — fs.readFileSync BLOCKS the entire event loop for every other request
app.get('/data', (req, res) => {
  const data = fs.readFileSync('./bigfile.json', 'utf8'); // server frozen until this completes!
  res.send(data);
});

// Right — use async fs.promises API, keeps the event loop free for other requests
app.get('/data', async (req, res) => {
  const data = await fs.promises.readFile('./bigfile.json', 'utf8');
  res.send(data);
});
```

❌ Mistake 2: Not handling `ENOENT` and other error codes explicitly
```javascript
// Wrong — generic catch treats "file missing" the same as "disk failure"
try {
  await fs.readFile('./maybe-missing.txt');
} catch (err) {
  console.log('Something went wrong'); // unhelpful — can't tell what actually happened
}

// Right — check err.code to respond appropriately
try {
  await fs.readFile('./maybe-missing.txt');
} catch (err) {
  if (err.code === 'ENOENT') {
    console.log('File does not exist — using default');
  } else if (err.code === 'EACCES') {
    console.log('Permission denied');
  } else {
    throw err; // unexpected — let it propagate
  }
}
```

---

## 🧠 Tricky Interview Question

```javascript
const fs = require('fs');

fs.writeFile('./a.txt', 'first', () => {
  console.log('write 1 done');
});
fs.writeFile('./a.txt', 'second', () => {
  console.log('write 2 done');
});

// What does a.txt contain after both callbacks fire?
```
Answer: The final content is **unpredictable** — it could be `"first"` OR `"second"` depending on which async write operation's underlying OS call completes LAST, since both `writeFile` calls target the SAME file concurrently with no ordering guarantee between them (Node dispatches both to the libuv thread pool, and their completion order is not fixed by call order). This is why concurrent, unsynchronized writes to the same file are dangerous — in production code needing ordered writes, use a single sequential write (`await` each one before starting the next) or `fs.createWriteStream()` with proper queuing, or append operations where ordering matters less.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `fs.readFile`, `fs.readFileSync`, and `fs.promises.readFile`?
A1: `fs.readFileSync` is synchronous — blocks the entire event loop until the read completes, returning the data directly (or throwing on error). `fs.readFile` is callback-based async — doesn't block, but requires a callback `(err, data) => {}`. `fs.promises.readFile` (or `require('fs/promises')`) is Promise-based async — doesn't block, returns a Promise usable with `.then()`/`await`, generally preferred in modern code for cleaner error handling via try/catch.

Q2: Why is using `fs.readFileSync` dangerous in a web server?
A2: Because Node.js is single-threaded for JS execution — any synchronous, blocking operation (including sync file I/O) freezes the ENTIRE process, meaning no other incoming HTTP requests can be processed until that one disk read finishes. In a server handling many concurrent users, this creates severe throughput bottlenecks and latency spikes. Sync methods are acceptable only in startup/one-time scripts where nothing else needs to run concurrently (e.g., CLI tools, build scripts).

Q3: How do you check if a file exists without reading its content?
A3: Use `fs.access(path)` (throws if inaccessible/doesn't exist, resolves if it does) or `fs.stat(path)` (throws `ENOENT` if missing, otherwise returns metadata). Avoid the deprecated pattern of `fs.exists()` (removed due to race conditions — checking existence then acting on it separately is inherently racy; better to just attempt the operation and handle the `ENOENT` error if it fails, a pattern sometimes called "ask forgiveness, not permission").

Q4: What does `{ recursive: true }` do in `fs.mkdir()`?
A4: It makes `fs.mkdir()` create ALL missing parent directories in the path, not just the final one, AND doesn't throw an error if the directory already exists (unlike the default behavior, which throws `ENOENT` if parents are missing, or `EEXIST` if the target already exists). This makes `fs.mkdir(path, { recursive: true })` idempotent and safe to call unconditionally, a very common production pattern ("ensure this directory exists" without needing a separate existence check first).

Q5: How would you safely process a very large file without loading it entirely into memory using `fs`?
A5: Don't use `fs.readFile`/`readFileSync` (they load the WHOLE file into RAM). Instead use `fs.createReadStream(path)`, which reads the file in small chunks (default 64KB), emitting `'data'` events per chunk — memory usage stays constant regardless of file size. Pair with `.pipe()` or the `stream.pipeline()` utility to process/transform/write the data chunk by chunk (covered in depth in the Streams topic).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reading/writing config files, logs, small-to-medium uploads, generated reports.
- Checking file metadata (size, existence, modification time) before deciding an action.
- Building CLI tools/scripts where synchronous methods are acceptable (no concurrent request handling to block).

❌ Avoid when:
- Processing very large files in a server context — use streams (`fs.createReadStream`/`createWriteStream`) instead to avoid memory spikes.
- Using sync methods (`readFileSync`, etc.) inside any request handler or hot code path in a running server.
- Managing structured application data that would be better served by an actual database (fs is for files, not a replacement for proper data storage with concurrency/transaction guarantees).

---

## 📊 Visual Diagram
```
fs MODULE — THREE API STYLES:
──────────────────────────────────────────────────────────

  SYNC (blocking):
    const data = fs.readFileSync('./file.txt', 'utf8');
    // ⚠️ Event loop FROZEN until disk read completes

  CALLBACK (non-blocking, older style):
    fs.readFile('./file.txt', 'utf8', (err, data) => {
      if (err) throw err;
      console.log(data);
    });
    // Event loop free immediately; callback fires later

  PROMISE (non-blocking, modern style):
    const data = await fs.promises.readFile('./file.txt', 'utf8');
    // Event loop free; cleaner async/await + try/catch error handling

COMMON OPERATIONS MAP:
  readFile / writeFile / appendFile   → file content
  stat / access                       → metadata / existence
  mkdir / readdir / rmdir             → directories
  unlink                              → delete a file
  watch                               → observe changes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| fs module | Node's file system API | Node का file system API |
| Synchronous (Sync) | Blocks until operation completes | काम पूरा होने तक block |
| Callback-based | Async, result via callback function | Async, callback से result |
| Promise-based | Async, result via Promise/await | Async, Promise/await से result |
| ENOENT | Error: file/path doesn't exist | File/path नहीं मिला error |
| fs.stat | Get file metadata | File की metadata लेना |
| recursive: true | Create nested dirs, no error if exists | Nested dirs बनाना, exist होने पर error नहीं |

---

## ⚡ 3-Line Summary
English: `fs` is Node's built-in module for all file system operations, offered in three flavors — sync (blocking), callback (async), and Promise-based (async, modern preferred). Always use async versions in server code to avoid freezing the event loop for other requests, and handle specific error codes like `ENOENT` for graceful failure handling. For very large files, use streams instead of `readFile`/`writeFile` to keep memory usage constant.
Hindi: `fs` Node का built-in module है सभी file system operations के लिए, तीन styles में — sync (blocking), callback (async), और Promise-based (async, modern preferred)। Server code में हमेशा async versions use करो ताकि event loop बाकी requests के लिए freeze न हो, और `ENOENT` जैसे specific error codes handle करो graceful failure के लिए। बहुत बड़ी files के लिए, `readFile`/`writeFile` की जगह streams use करो memory usage constant रखने के लिए।

---

## ➡️ Next Topic
**32. fs.readFile vs fs.readFileSync** — deeper comparison of blocking vs non-blocking file reads and when each is appropriate.
