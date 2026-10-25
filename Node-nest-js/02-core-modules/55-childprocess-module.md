# 55. child_process Module
# हिंदी में: child_process Module — External Processes चलाना

---

## 🔵 Simple Definition (English)
The **`child_process`** module (`require('child_process')`) lets Node.js spawn and interact with OS-level child processes — running shell commands, other programs (ffmpeg, Python scripts, ImageMagick), or even other Node.js scripts in a separate process. It's essential because Node's single-threaded event loop can't efficiently do heavy CPU work itself — offloading it to a child process keeps the main process responsive.

## 🔵 सरल परिभाषा (Hindi)
**`child_process`** module Node.js को OS-level child processes spawn करने और उनसे interact करने देता है — shell commands चलाना, दूसरे programs (ffmpeg, Python scripts) चलाना, या दूसरा Node.js script अलग process में चलाना। यह ज़रूरी है क्योंकि Node का single-threaded event loop खुद heavy CPU काम efficiently नहीं कर सकता — child process में offload करने से main process responsive रहता है।

---

## 🔴 Problem it Solves
Node.js's single-threaded event loop is great for I/O-bound work (handling thousands of concurrent network requests) but terrible for CPU-bound work (image resizing, video transcoding, complex calculations) — a long CPU task blocks the entire event loop, freezing ALL other requests. Before `child_process`, there was no way to run truly parallel OS-level work from Node. The module solves this by delegating heavy/external work to separate OS processes, which run on their own, don't block Node's event loop, and can even run non-JavaScript programs (Python, shell utilities, compiled binaries).

## 🔴 यह क्यों बना? (Hindi)
Node.js का single-threaded event loop I/O-bound काम के लिए अच्छा है पर CPU-bound काम (image resize, video transcode) के लिए बुरा — लंबा CPU task पूरे event loop को freeze कर देता है, सभी requests रुक जाते हैं। `child_process` से पहले Node से truly parallel OS-level काम करने का कोई तरीका नहीं था। यह module heavy/external काम को अलग OS processes में delegate करता है, जो अपने आप चलते हैं, Node का event loop block नहीं करते।

---

## 🟢 How it Works — Step by Step

Step 1 → Four main functions: `exec()`, `execFile()`, `spawn()`, `fork()` — each has different tradeoffs (covered in detail in topic 56).
Step 2 → `exec(command, callback)` — runs a shell command, buffers ALL output, invokes the callback with `(error, stdout, stderr)` once the process exits.
Step 3 → `spawn(command, args, options)` — runs a command, returns a `ChildProcess` object immediately (a streaming interface: `child.stdout`, `child.stderr` are Readable streams, `child.stdin` is Writable).
Step 4 → `fork(modulePath, args)` — a special case of `spawn()` specifically for running ANOTHER Node.js script, with a built-in IPC (inter-process communication) channel for message-passing (`child.send()`/`process.on('message')`).
Step 5 → The child process is fully independent — it has its own memory space, event loop, and PID; communication happens only through stdin/stdout/stderr pipes or (for `fork`) the IPC channel.
Step 6 → Always handle the `'exit'` and `'error'` events to know when the child finishes and whether it failed, and check `child.exitCode`/`signal` to determine success/failure.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → चार मुख्य functions: `exec()`, `execFile()`, `spawn()`, `fork()` — हर एक के अलग tradeoffs (topic 56 में detail)।
Step 2 → `exec()` — shell command चलाता है, पूरा output buffer करता है, exit होने पर callback `(error, stdout, stderr)` के साथ call होता है।
Step 3 → `spawn()` — command चलाता है, तुरंत `ChildProcess` object return करता है (streaming interface)।
Step 4 → `fork()` — दूसरा Node.js script चलाने के लिए `spawn()` का special case, built-in IPC channel के साथ।
Step 5 → Child process independent है — अपनी memory, event loop, PID; communication सिर्फ pipes/IPC से होती है।
Step 6 → हमेशा `'exit'`, `'error'` events handle करो, `exitCode`/`signal` check करो।

---

## 🟡 Real World Example
**Zomato's image processing pipeline:** When a restaurant uploads a menu photo, resizing it to thumbnail/medium/large variants is CPU-intensive (image decode, resize, re-encode). Doing this synchronously in the main Node process would freeze all order-placing requests for the duration. Instead, Zomato's backend spawns an `imagemagick` CLI process (via `spawn()`) or forks a dedicated Node worker script to do the resizing, keeping the main API server responsive to handle thousands of concurrent food orders while the image processing happens in parallel.

## 🟡 Real Example Hindi mein
**Zomato का image processing pipeline:** Restaurant menu photo upload होने पर resize करना CPU-intensive है। Main Node process में synchronously करने से सभी order-placing requests freeze हो जाते। इसके बजाय Zomato backend `imagemagick` CLI process spawn करता है या dedicated Node worker script fork करता है — main API server responsive रहता है।

---

## 💻 Code Example — Basic
```javascript
// childprocess-basics.js
const { exec, spawn, fork } = require('child_process');

// 1. exec() -- runs a shell command, buffers all output
exec('node --version', (error, stdout, stderr) => {
  if (error) {
    console.error('Error:', error.message);
    return;
  }
  console.log('Node version:', stdout.trim());
});

// 2. exec() with a shell pipeline (shell features like pipes, &&, etc. work)
exec('ls -la | grep ".js" | wc -l', (error, stdout, stderr) => {
  if (error) return console.error(error);
  console.log('Number of .js files:', stdout.trim());
});

// 3. spawn() -- streaming interface, better for large output or long-running processes
const ls = spawn('ls', ['-la']); // command + args as separate array elements (safer than exec)

ls.stdout.on('data', (data) => {
  console.log(`stdout chunk: ${data}`); // streamed as it arrives, not buffered fully
});
ls.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});
ls.on('close', (code) => {
  console.log(`Process exited with code ${code}`);
});

// 4. fork() -- spawn another Node.js script with IPC messaging
// (assumes a file ./worker.js exists in the same directory)
// const child = fork('./worker.js');
// child.send({ task: 'process-data', payload: [1, 2, 3] });
// child.on('message', (result) => console.log('Worker result:', result));
```

## 💻 Code Example — Advanced
```javascript
// childprocess-advanced.js -- production patterns
const { spawn, fork } = require('child_process');
const path = require('path');

// ─── 1. PROMISIFIED spawn() WITH PROPER ERROR HANDLING ───────────────────────
function runCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, options);
    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => (stdout += data));
    child.stderr.on('data', (data) => (stderr += data));

    child.on('error', (err) => reject(err)); // e.g. command not found

    child.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr, code });
      } else {
        reject(new Error(`Command failed with code ${code}: ${stderr}`));
      }
    });
  });
}

// ─── 2. TIMEOUT HANDLING FOR LONG-RUNNING CHILD PROCESSES ────────────────────
function runWithTimeout(command, args, timeoutMs) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args);
    const timer = setTimeout(() => {
      child.kill('SIGTERM'); // forcibly terminate if it takes too long
      reject(new Error(`Process timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    let output = '';
    child.stdout.on('data', (data) => (output += data));
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ output, code });
    });
  });
}

// ─── 3. FORK WITH IPC FOR CPU-INTENSIVE TASK OFFLOADING ──────────────────────
function processInWorker(data) {
  return new Promise((resolve, reject) => {
    const workerPath = path.join(__dirname, 'cpu-worker.js');
    const child = fork(workerPath);

    child.send({ data }); // send data to the worker via IPC

    child.on('message', (result) => {
      resolve(result);
      child.kill(); // clean up the worker process once done
    });

    child.on('error', reject);
    child.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker exited with code ${code}`));
    });
  });
}

// Example cpu-worker.js content (separate file):
// process.on('message', ({ data }) => {
//   const result = data.reduce((sum, n) => sum + n * n, 0); // CPU-heavy computation
//   process.send(result);
// });

// ─── 4. MANAGING MULTIPLE CONCURRENT CHILD PROCESSES WITH A POOL-LIKE PATTERN ─
async function processMultipleFiles(filePaths) {
  const results = await Promise.all(
    filePaths.map((filePath) => runCommand('file', [filePath])) // run `file` command on each
  );
  return results.map((r) => r.stdout.trim());
}

module.exports = { runCommand, runWithTimeout, processInWorker, processMultipleFiles };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const app = express();

// 1. VIDEO THUMBNAIL GENERATION USING ffmpeg (CPU-intensive, offloaded to child process)
app.post('/generate-thumbnail', express.json(), (req, res) => {
  const { videoPath } = req.body;
  const outputPath = `./thumbnails/${Date.now()}.jpg`;

  const ffmpeg = spawn('ffmpeg', [
    '-i', videoPath,
    '-ss', '00:00:01', // take frame at 1 second
    '-vframes', '1',
    outputPath,
  ]);

  let errorOutput = '';
  ffmpeg.stderr.on('data', (data) => (errorOutput += data));

  ffmpeg.on('close', (code) => {
    if (code === 0) {
      res.json({ message: 'Thumbnail generated', path: outputPath });
    } else {
      res.status(500).json({ error: 'ffmpeg failed', details: errorOutput });
    }
  });
});

// 2. RUNNING A PYTHON SCRIPT FOR DATA ANALYSIS (polyglot architecture)
app.post('/analyze-data', express.json(), (req, res) => {
  const python = spawn('python3', ['./scripts/analyze.py', JSON.stringify(req.body)]);
  let result = '';

  python.stdout.on('data', (data) => (result += data));
  python.on('close', (code) => {
    if (code === 0) {
      res.json({ analysis: JSON.parse(result) });
    } else {
      res.status(500).json({ error: 'Analysis script failed' });
    }
  });
});

// 3. CPU-HEAVY TASK OFFLOADED TO A FORKED NODE WORKER (keeps event loop free)
app.post('/heavy-computation', express.json(), (req, res) => {
  const child = require('child_process').fork(path.join(__dirname, 'compute-worker.js'));
  child.send(req.body.numbers);
  child.on('message', (result) => {
    res.json({ result });
    child.kill(); // always clean up forked processes
  });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `exec()` with unsanitized user input (shell injection vulnerability)
```javascript
// Wrong -- CRITICAL SECURITY BUG: user input goes directly into a shell command
app.get('/ping', (req, res) => {
  exec(`ping -c 1 ${req.query.host}`, (err, stdout) => res.send(stdout));
  // req.query.host = "google.com; rm -rf /" -- SHELL INJECTION!
});

// Correct -- use spawn() with arguments as an array (no shell interpretation of args)
app.get('/ping', (req, res) => {
  const ping = spawn('ping', ['-c', '1', req.query.host]); // host is a literal argument, not shell code
  let output = '';
  ping.stdout.on('data', (data) => (output += data));
  ping.on('close', () => res.send(output));
});
```

❌ Mistake 2: Not setting a `maxBuffer` limit on `exec()` for commands with potentially large output
```javascript
// Wrong -- default maxBuffer is 1MB; exceeding it throws an error and KILLS the process
exec('find / -name "*.log"', (err, stdout) => { /* may throw "stdout maxBuffer exceeded" */ });

// Correct -- use spawn() for large/unknown output size (streams, no buffer limit issue)
const find = spawn('find', ['/', '-name', '*.log']);
find.stdout.on('data', (chunk) => processChunk(chunk)); // streamed, no buffer limit
```

❌ Mistake 3: Forgetting to handle the `'error'` event (e.g. command not found)
```javascript
// Wrong -- if the binary doesn't exist, this crashes the process (unhandled 'error')
const child = spawn('nonexistent-command');

// Correct -- always listen for 'error'
const child = spawn('nonexistent-command');
child.on('error', (err) => console.error('Failed to start process:', err.message));
```

---

## 🧠 Tricky Interview Question
```javascript
const { exec } = require('child_process');

console.log('Before exec');
exec('sleep 1 && echo "done"', (err, stdout) => {
  console.log('Exec callback:', stdout.trim());
});
console.log('After exec');
```
Answer: Output order is `Before exec`, `After exec`, then (after ~1 second) `Exec callback: done`. `exec()` is ASYNCHRONOUS — it spawns the child process and returns immediately, continuing to execute the rest of the synchronous code (`console.log('After exec')`) WITHOUT waiting for the command to finish. The callback only fires once the shell command completes (after the 1-second sleep), demonstrating that `child_process` methods don't block Node's event loop — the main process stays fully responsive while the child process runs independently in the background.

---

## ⚫ Interview Questions + Answers

Q1: Why is `exec()` vulnerable to shell injection, and how does `spawn()` avoid this risk?
A1: `exec()` runs the command string through an actual shell (`/bin/sh` on Unix), which interprets special characters (`;`, `&&`, `|`, backticks) — if user input is concatenated into the command string, an attacker can inject additional shell commands. `spawn(command, args)` takes the command and its arguments as SEPARATE values (an array), and passes them directly to the OS's process-creation syscall without shell interpretation — arguments are treated as literal strings, not executable shell syntax, eliminating injection risk (unless you explicitly pass `{ shell: true }`).

Q2: What's the difference between how `exec()` and `spawn()` handle output?
A2: `exec()` BUFFERS the entire stdout/stderr output in memory and delivers it all at once via the callback once the process exits — simple but risky for large output (default `maxBuffer` is 1MB, exceeding it throws an error). `spawn()` returns a `ChildProcess` with `stdout`/`stderr` as REAL Readable STREAMS — you process output incrementally as it arrives, with no inherent size limit, making it suitable for long-running processes or large output.

Q3: What is `fork()` specifically designed for, and how does it differ from `spawn()`?
A3: `fork()` is a specialized version of `spawn()` exclusively for launching ANOTHER NODE.JS script (not arbitrary commands). It automatically sets up an IPC (inter-process communication) channel, letting the parent and child exchange structured JavaScript objects via `child.send(obj)` and `process.on('message', ...)` in the child — something plain `spawn()` doesn't provide (you'd only have raw stdin/stdout pipes). It's commonly used to offload CPU-intensive JS work to a separate process while retaining easy message-passing.

Q4: How do you properly terminate a child process, and what's the difference between `SIGTERM` and `SIGKILL`?
A4: Call `child.kill(signal)` — default signal is `SIGTERM`, which asks the process to terminate GRACEFULLY (it can catch this signal and clean up before exiting). `SIGKILL` forcibly terminates immediately with NO chance for cleanup — use it only when the process isn't responding to `SIGTERM` (e.g., `child.kill('SIGKILL')` as a last resort after a timeout). Always prefer `SIGTERM` first to allow graceful shutdown (closing file handles, flushing buffers).

Q5: Why would you offload CPU-intensive work to a child process instead of just doing it directly in your Express route handler?
A5: Node.js's event loop is SINGLE-THREADED — any synchronous CPU-intensive code (image processing, complex calculations, video encoding) running directly in a route handler blocks the ENTIRE event loop, meaning NO other requests (even unrelated ones) can be processed until that code finishes. Offloading to a child process (via `spawn()` for external tools, or `fork()`/`worker_threads` for JS computation) runs that work on a separate OS process/thread, keeping the main event loop free to handle other concurrent requests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running external programs/binaries (ffmpeg, ImageMagick, Python scripts, system utilities)
- Offloading CPU-intensive work that would otherwise block the event loop
- Building CLI tools that orchestrate other command-line programs

❌ Avoid when:
- The work is pure I/O (network calls, file reads) — Node's async I/O already handles this efficiently without needing a separate process
- You need shared-memory, low-overhead parallelism for pure JS computation — `worker_threads` (topic 58) is lighter-weight than spawning a full OS process via `fork()`
- Working with untrusted user input in `exec()` without sanitization — always prefer `spawn()`/`execFile()` with argument arrays

---

## 📊 Visual Diagram
```
CHILD_PROCESS FUNCTIONS OVERVIEW:

  exec(cmd, cb)          spawn(cmd, args)         fork(modulePath)
  ─────────────          ────────────────         ─────────────────
  Runs via shell         Runs directly (no shell  Runs ANOTHER Node.js
  Buffers ALL output    by default)               script
  Good for: short        Streams stdout/stderr    Built-in IPC channel
  commands, simple       Good for: long-running,  (child.send/process.on
  output                 large output             'message')

PARENT-CHILD COMMUNICATION:

  Parent Process (Node.js)              Child Process (any program)
  ┌──────────────────┐                  ┌──────────────────┐
  │                   │── stdin ───────►│                   │
  │   spawn()/exec()  │◄── stdout ──────│   ffmpeg/python/  │
  │                   │◄── stderr ──────│   another node    │
  └──────────────────┘                  └──────────────────┘
         │                                      │
         └──── IPC channel (fork() only) ───────┘
              child.send() / process.on('message')
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| child_process | Module to spawn OS processes | OS processes spawn करने का module |
| exec() | Shell command, buffers output | Shell command, output buffer करता है |
| spawn() | Streaming process execution | Streaming process execution |
| fork() | Spawn another Node.js script with IPC | IPC के साथ दूसरा Node script spawn करना |
| IPC | Inter-process communication channel | Processes के बीच communication channel |
| SIGTERM/SIGKILL | Graceful vs forced termination signals | Graceful बनाम forced termination |

---

## ⚡ 3-Line Summary
English: `child_process` spawns external OS processes to run shell commands, external programs, or other Node scripts without blocking the main event loop. `exec()` buffers output (simple, risky for large/untrusted input); `spawn()` streams it (safer, scalable); `fork()` adds IPC for running Node scripts. Always avoid shell injection by using `spawn()`/`execFile()` with argument arrays instead of string-concatenated `exec()` commands.

Hindi: `child_process` external OS processes spawn करता है — shell commands, external programs, या दूसरे Node scripts चलाने के लिए, main event loop को block किए बिना। `exec()` output buffer करता है; `spawn()` stream करता है; `fork()` IPC जोड़ता है। हमेशा `spawn()`/`execFile()` array arguments से use करो, shell injection से बचने के लिए।

---

## ➡️ Next Topic
**56. exec vs spawn vs fork** — detailed side-by-side comparison with decision criteria for choosing the right child_process method.
