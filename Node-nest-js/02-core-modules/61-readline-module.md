# 61. readline Module
# हिंदी में: readline Module — Line-by-Line Input पढ़ना

---

## 🔵 Simple Definition (English)
The **`readline`** module (`require('readline')`) reads input ONE LINE AT A TIME from a Readable stream — most commonly `process.stdin` for interactive CLI prompts, but also any file stream for line-by-line text processing. It's how Node.js CLI tools ask "Are you sure? (y/n)" or process large text files one line at a time without loading everything into memory.

## 🔵 सरल परिभाषा (Hindi)
**`readline`** module किसी Readable stream से एक-एक LINE पढ़ता है — सबसे common `process.stdin` (interactive CLI prompts के लिए), पर कोई भी file stream line-by-line text processing के लिए भी। यही तरीका है जिससे Node.js CLI tools "क्या आप sure हैं? (y/n)" पूछते हैं या बड़ी text files को line-by-line process करते हैं बिना पूरा memory में load किए।

---

## 🔴 Problem it Solves
Reading text data chunk-by-chunk (as raw streams deliver it) doesn't align with how humans/programs think about text — we think in LINES, but a stream chunk might contain half a line, three and a half lines, or span across multiple chunks. Manually buffering and splitting on `\n` correctly (handling partial lines across chunk boundaries) is fiddly and easy to get wrong. `readline` handles this buffering/splitting logic internally and ALSO provides interactive terminal features (prompts, history, tab completion) needed for CLI tools — both from one well-tested module.

## 🔴 यह क्यों बना? (Hindi)
Text data को chunk-by-chunk पढ़ना (जैसे raw streams देते हैं) इंसानों के सोचने के तरीके से match नहीं करता — हम LINES में सोचते हैं, पर chunk में आधी line हो सकती है, या कई lines हो सकती हैं, या chunks के बीच बंट सकती है। Manually buffer करके सही तरीके से `\n` पर split करना मुश्किल है। `readline` यह buffering/splitting internally handle करता है, साथ में interactive terminal features (prompts, history) भी देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an interface: `readline.createInterface({ input: process.stdin, output: process.stdout })` — wraps a Readable stream to deliver complete lines.
Step 2 → Listen for lines: `rl.on('line', (line) => {...})` — fires once per complete line, regardless of how the underlying stream chunked the data.
Step 3 → Interactive prompts: `rl.question('Enter your name: ', (answer) => {...})` — displays a prompt, waits for Enter, delivers the typed text.
Step 4 → Modern async iteration: since Node 11, `readline.Interface` is async-iterable — `for await (const line of rl) {...}` processes lines sequentially with clean control flow (no nested callbacks).
Step 5 → File processing: pairing `fs.createReadStream(file)` as the `input` lets you process huge text files (logs, CSVs) line-by-line with constant memory.
Step 6 → Always call `rl.close()` when done (for `process.stdin`-based interfaces) to release the terminal and let the process exit naturally; listen for `'close'` to know when input ends (e.g., Ctrl+D or EOF).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Interface बनाओ: `readline.createInterface({ input, output })` — Readable stream को wrap करता है, पूरी lines देता है।
Step 2 → Lines listen करो: `rl.on('line', fn)` — हर complete line पर fire होता है।
Step 3 → Interactive prompts: `rl.question(prompt, callback)` — prompt दिखाता है, Enter तक wait करता है।
Step 4 → Modern async iteration: `for await (const line of rl)` — sequential processing, clean control flow।
Step 5 → File processing: `fs.createReadStream()` के साथ pair करके बड़ी files line-by-line process करो।
Step 6 → हमेशा `rl.close()` call करो खत्म होने पर; `'close'` event से input खत्म होने का पता चलता है।

---

## 💻 Code Example — Basic
```javascript
// readline-basics.js
const readline = require('readline');

// 1. INTERACTIVE CLI PROMPT (classic usage)
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question('What is your name? ', (name) => {
  console.log(`Hello, ${name}!`);
  rl.question('Are you sure you want to proceed? (y/n) ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      console.log('Proceeding...');
    } else {
      console.log('Cancelled.');
    }
    rl.close(); // ALWAYS close when done to release stdin and allow process exit
  });
});

// 2. LISTENING TO 'line' EVENT FOR EACH LINE OF INPUT
// (uncomment to test by piping input: `echo -e "line1\nline2" | node readline-basics.js`)
// const rl2 = readline.createInterface({ input: process.stdin });
// rl2.on('line', (line) => console.log('Received:', line));
// rl2.on('close', () => console.log('Input stream ended'));
```

## 💻 Code Example — Advanced
```javascript
// readline-advanced.js -- production file processing patterns
const readline = require('readline');
const fs = require('fs');

// ─── 1. PROCESSING A LARGE LOG FILE LINE-BY-LINE (constant memory) ───────────
async function countErrorLines(filePath) {
  const fileStream = fs.createReadStream(filePath);
  const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });
  // crlfDelay: Infinity treats \r\n as a single line break (Windows-safe)

  let errorCount = 0;
  let totalLines = 0;

  for await (const line of rl) { // modern async iteration -- clean sequential processing
    totalLines++;
    if (line.includes('ERROR')) errorCount++;
  }

  return { totalLines, errorCount };
}

// ─── 2. MULTI-STEP INTERACTIVE CLI WIZARD ─────────────────────────────────────
function askQuestion(rl, query) {
  return new Promise((resolve) => rl.question(query, resolve)); // promisify rl.question
}

async function runSetupWizard() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  const projectName = await askQuestion(rl, 'Project name: ');
  const useTypeScript = await askQuestion(rl, 'Use TypeScript? (y/n): ');
  const packageManager = await askQuestion(rl, 'Package manager (npm/yarn/pnpm): ');

  rl.close();

  return {
    projectName,
    typescript: useTypeScript.toLowerCase() === 'y',
    packageManager: packageManager || 'npm',
  };
}

// ─── 3. CSV-LIKE FILE PARSING WITHOUT A FULL CSV LIBRARY (simple cases) ──────
async function parseSimpleCsv(filePath) {
  const rl = readline.createInterface({ input: fs.createReadStream(filePath) });
  const rows = [];
  let headers = null;

  for await (const line of rl) {
    if (!line.trim()) continue; // skip empty lines
    const values = line.split(',').map((v) => v.trim());
    if (!headers) {
      headers = values;
      continue;
    }
    const row = {};
    headers.forEach((h, i) => (row[h] = values[i]));
    rows.push(row);
  }
  return rows;
}

// ─── 4. PASSWORD-STYLE MASKED INPUT (custom readline behavior) ──────────────
function askHiddenInput(query) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(query, (answer) => { rl.close(); resolve(answer); });

    // Mute stdout echo while typing (common pattern for password prompts)
    rl._writeToOutput = function (stringToWrite) {
      if (stringToWrite.includes(query)) {
        rl.output.write(stringToWrite); // show the prompt itself
      } else {
        rl.output.write('*'); // mask typed characters
      }
    };
  });
}

module.exports = { countErrorLines, runSetupWizard, parseSimpleCsv, askHiddenInput };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const readline = require('readline');
const fs = require('fs');
const app = express();

// readline is primarily a CLI/file-processing tool, not typically used directly
// inside HTTP request handlers -- but it's useful for processing uploaded text files
// or for admin/setup scripts that run ALONGSIDE an Express server.

// 1. PROCESSING AN UPLOADED LOG FILE LINE-BY-LINE TO EXTRACT STATS
app.post('/analyze-log/:filename', async (req, res) => {
  const filePath = `./uploads/${req.params.filename}`;

  try {
    const rl = readline.createInterface({ input: fs.createReadStream(filePath) });
    let errorCount = 0, warnCount = 0, totalLines = 0;

    for await (const line of rl) {
      totalLines++;
      if (line.includes('ERROR')) errorCount++;
      if (line.includes('WARN')) warnCount++;
    }

    res.json({ totalLines, errorCount, warnCount });
  } catch (err) {
    res.status(404).json({ error: 'File not found or unreadable' });
  }
});

// 2. A SEPARATE CLI SCRIPT (run independently, NOT as part of request handling)
// using readline to prompt an admin for confirmation before a destructive DB operation
// seed-admin.js:
//   const readline = require('readline');
//   const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
//   rl.question('This will WIPE the database. Type "yes" to confirm: ', (answer) => {
//     if (answer === 'yes') { /* run wipe */ }
//     rl.close();
//   });

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to call `rl.close()` after an interactive session
```javascript
// Wrong -- the process never exits because stdin remains "open" waiting for more input
rl.question('Name? ', (name) => {
  console.log(`Hi ${name}`);
  // missing rl.close() -- process hangs indefinitely
});

// Correct -- always close when done with the interface
rl.question('Name? ', (name) => {
  console.log(`Hi ${name}`);
  rl.close();
});
```

❌ Mistake 2: Not setting `crlfDelay: Infinity` when processing files that might have Windows line endings
```javascript
// Wrong -- on files with \r\n, this can sometimes misinterpret line boundaries
const rl = readline.createInterface({ input: fs.createReadStream(file) });

// Correct -- crlfDelay: Infinity treats \r\n as ONE line break reliably
const rl = readline.createInterface({ input: fs.createReadStream(file), crlfDelay: Infinity });
```

❌ Mistake 3: Mixing `rl.on('line', ...)` callback style with `for await...of` on the same interface
```javascript
// Wrong -- combining both consumption patterns on the same rl instance causes confusion/bugs
rl.on('line', (line) => console.log('via event:', line));
for await (const line of rl) { console.log('via iterator:', line); } // conflicting consumption

// Correct -- pick ONE style consistently
for await (const line of rl) { console.log(line); } // modern, preferred
```

---

## 🧠 Tricky Interview Question
```javascript
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });

console.log('Script started');
rl.on('line', (line) => {
  console.log('Got line:', line);
  if (line === 'exit') rl.close();
});
rl.on('close', () => {
  console.log('Readline closed');
  process.exit(0);
});
```
Answer: `'Script started'` prints IMMEDIATELY (synchronous). Then the process WAITS (doesn't exit) for input from stdin — if run interactively, it waits for the user to type lines; if piped (`echo "a\nexit" | node script.js`), it processes each line as it arrives. Each typed line triggers `'Got line: ...'`. Typing `'exit'` calls `rl.close()`, which triggers the `'close'` event, printing `'Readline closed'` and explicitly exiting. The key lesson: an open `readline.Interface` on `process.stdin` keeps the Node.js EVENT LOOP ALIVE (the process won't exit naturally) until the interface is closed or stdin reaches EOF — this is why explicit `rl.close()` calls (or piping EOF) are necessary for scripts to terminate.

---

## ⚫ Interview Questions + Answers

Q1: Why does `readline` exist when you could technically listen for `'data'` events on `process.stdin` directly?
A1: Raw `'data'` events deliver ARBITRARY CHUNKS of a stream — a chunk might contain a partial line, multiple lines, or split a line across two chunks (e.g., if the user types "hello" and the terminal buffers it in two pieces). `readline` internally buffers incoming data and correctly reassembles/splits it into COMPLETE LINES (handling `\n`, `\r\n`), firing `'line'` events only when a full line is available — saving you from writing this buffering/splitting logic yourself, which is easy to get wrong at chunk boundaries.

Q2: How do you use `readline` to process a large file line-by-line, and why is this more memory-efficient than `fs.readFileSync().split('\n')`?
A2: Pair `readline.createInterface({ input: fs.createReadStream(filePath) })` with either the `'line'` event or `for await (const line of rl)`. This processes the file INCREMENTALLY via streaming — only one line's worth of data needs to be in memory at a time (plus internal buffering). `fs.readFileSync(path).split('\n')` loads the ENTIRE file into memory first, then creates an array of ALL lines simultaneously — for a multi-gigabyte log file, this could exhaust available memory, while the streaming `readline` approach keeps memory usage roughly constant.

Q3: What does `rl.question(query, callback)` do, and how would you convert it to work with `async/await`?
A3: `rl.question()` prints the `query` string to the output and waits for the user to type a response and press Enter, then invokes `callback(answer)` with what they typed. It's inherently callback-based; to use it with `async/await`, wrap it in a Promise: `function ask(rl, q) { return new Promise(resolve => rl.question(q, resolve)); }`, then `const answer = await ask(rl, 'Name? ');` — this is a common pattern for building sequential, multi-step interactive CLI wizards cleanly.

Q4: Why does a Node.js script using `readline.createInterface({ input: process.stdin })` not exit immediately after the script's main code finishes running?
A4: An open readline interface on `process.stdin` keeps a reference/listener active on stdin, which Node's event loop considers "work to do," keeping the process ALIVE waiting for more input. The process will only exit naturally once `rl.close()` is called explicitly, or `process.stdin` reaches EOF (e.g., piped input ends, or Ctrl+D is pressed in an interactive terminal) which triggers readline's internal close and the `'close'` event.

Q5: Can `readline` be used with any Readable stream, or only `process.stdin`?
A5: Any Readable stream — `readline.createInterface({ input: someReadableStream })`. This is commonly used with `fs.createReadStream(filePath)` to process text files line-by-line (logs, CSVs), or even with a stream representing network data, as long as it's a valid Node.js Readable stream. `process.stdin` is just the most common use case because it's specifically for interactive terminal input, but the module is general-purpose for any line-oriented text stream.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building interactive CLI tools that need user input/confirmation (setup wizards, migration scripts)
- Processing large text files (logs, CSVs) line-by-line without loading them fully into memory
- Any scenario needing reliable line-boundary detection from a stream

❌ Avoid when:
- Processing structured formats like real CSV (with quoted fields containing commas/newlines) or JSON — use a dedicated parser library (`csv-parse`, `JSON.parse`) instead, since naive line-splitting breaks on edge cases
- Building a web-facing feature — `readline` is for CLI/stdin/file text-processing, not typically for request/response handling

---

## 📊 Visual Diagram
```
READLINE LINE REASSEMBLY:

  Raw stream chunks (arbitrary boundaries):
  chunk1: "Hello Wor"
  chunk2: "ld\nThis is li"
  chunk3: "ne two\n"
       │
       ▼  readline buffers and reassembles
  'line' event: "Hello World"
  'line' event: "This is line two"

INTERACTIVE PROMPT FLOW:

  rl.question('Name? ', callback)
       │
       ▼
  Prints "Name? " to output
       │
       ▼
  WAITS for user input + Enter key
       │
       ▼
  callback(typedAnswer) fires
       │
       ▼
  rl.close() -- releases stdin, allows process to exit naturally
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| readline.createInterface | Wraps a stream for line-based reading | Stream को line-based reading के लिए wrap करना |
| 'line' event | Fires once per complete line | हर complete line पर fire होता है |
| question() | Interactive prompt + callback | Interactive prompt + callback |
| crlfDelay | Treats \r\n as one line break | \r\n को एक line break मानना |
| for await...of | Async-iterable line consumption | Async-iterable line consumption |
| close() | Releases the interface/stdin | Interface/stdin release करना |

---

## ⚡ 3-Line Summary
English: `readline` reads input line-by-line from any Readable stream, correctly handling line-boundary buffering that raw `'data'` events don't. It powers interactive CLI prompts (`rl.question()`) and memory-efficient large file processing (paired with `fs.createReadStream()`). Always call `rl.close()` or let EOF naturally end the interface so the process can exit.

Hindi: `readline` किसी भी Readable stream से line-by-line input पढ़ता है, line-boundary buffering सही तरीके से handle करता है। यह interactive CLI prompts और memory-efficient large file processing के लिए इस्तेमाल होता है। हमेशा `rl.close()` call करो, process exit करने के लिए।

---

## ➡️ Next Topic
**62. timer Module (setTimeout, setInterval, setImmediate)** — Node's timer functions and how they interact with the event loop's phases.
