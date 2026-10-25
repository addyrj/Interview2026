# 56. exec vs spawn vs fork
# हिंदी में: exec vs spawn vs fork — कब कौन सा इस्तेमाल करें

---

## 🔵 Simple Definition (English)
`exec()`, `spawn()`, and `fork()` are the three main ways to create child processes in Node.js, each suited for different scenarios: **`exec()`** for short shell commands with small output (runs through a shell, buffers everything). **`spawn()`** for long-running or high-output processes (no shell by default, streams output). **`fork()`** specifically for launching another Node.js script with built-in message-passing (IPC).

## 🔵 सरल परिभाषा (Hindi)
`exec()`, `spawn()`, और `fork()` Node.js में child processes बनाने के तीन मुख्य तरीके हैं, हर एक अलग scenario के लिए। **`exec()`** छोटे shell commands के लिए (shell से चलता है, सब buffer करता है)। **`spawn()`** long-running या high-output processes के लिए (default में shell नहीं, output stream करता है)। **`fork()`** specifically दूसरा Node.js script चलाने के लिए, built-in message-passing (IPC) के साथ।

---

## 🔴 Problem it Solves
A single, one-size-fits-all child process API would force every use case into an unsuitable shape — buffering a 10GB `find` command's output would crash; running a trusted internal script shouldn't need shell-injection-prone string commands; and passing structured data between a parent and a Node.js worker shouldn't require manually parsing stdout text. Node provides three specialized functions so each use case gets the right tradeoffs: simplicity (`exec`), scalability/safety (`spawn`), and rich Node-to-Node communication (`fork`).

## 🔴 यह क्यों बना? (Hindi)
एक ही API सभी use cases के लिए सही shape नहीं देगा — 10GB `find` command का output buffer करना crash कर देगा; trusted internal script चलाने के लिए shell-injection-prone string commands नहीं चाहिए; parent-worker के बीच structured data भेजने के लिए stdout text parse नहीं करना चाहिए। Node तीन specialized functions देता है ताकि हर use case को सही tradeoffs मिलें।

---

## 🟢 How it Works — Step by Step

Step 1 → **`exec(command, options, callback)`**: takes a single command STRING, runs it through `/bin/sh` (or `cmd.exe` on Windows) — supports shell features (pipes `|`, redirects `>`, `&&`), buffers stdout/stderr fully, default `maxBuffer` is 1MB.
Step 2 → **`execFile(file, args, callback)`**: like `exec()` but runs a FILE directly without a shell — safer (no shell injection) but no shell features (pipes, globbing).
Step 3 → **`spawn(command, args, options)`**: takes command and args SEPARATELY (array), no shell by default, returns a `ChildProcess` with streaming `stdout`/`stderr`/`stdin` — ideal for large output or long-running processes, and inherently safer against injection.
Step 4 → **`fork(modulePath, args, options)`**: internally calls `spawn()` with `execPath` set to Node and the given script, PLUS automatically creates an IPC channel — `child.send(obj)` / `process.on('message', fn)` let parent and child exchange JS objects directly (JSON-serialized under the hood).
Step 5 → Decision shortcut: need shell features + small output → `exec()`. Need safety + large/streaming output + any external program → `spawn()`. Need to run another Node.js script with message passing → `fork()`.
Step 6 → All three return a `ChildProcess` instance (EventEmitter) with `'exit'`, `'error'`, `'close'` events, and a `.kill(signal)` method to terminate.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **`exec()`**: single command string, shell के through चलता है, shell features support करता है, output पूरा buffer करता है (default maxBuffer 1MB)।
Step 2 → **`execFile()`**: `exec()` जैसा पर shell के बिना — safer, पर shell features (pipes) नहीं।
Step 3 → **`spawn()`**: command+args array में अलग, shell default में नहीं, streaming output — large output/long-running के लिए best।
Step 4 → **`fork()`**: internally `spawn()` ही है Node script के लिए, साथ में IPC channel — `send()`/`message` से JS objects exchange।
Step 5 → Decision: shell features + small output → `exec()`. Safety + large output → `spawn()`. Node script + messaging → `fork()`.
Step 6 → तीनों `ChildProcess` (EventEmitter) return करते हैं — `'exit'`, `'error'`, `'close'` events, `.kill()` method।

---

## 🟡 Real World Example
**Swiggy's deployment/ops tooling vs production services:** An internal DevOps CLI script uses `exec('git log --oneline -10')` — small, trusted, controlled input, shell features (piping to `grep`) are genuinely useful, output is tiny. In contrast, Swiggy's production image-resizing service uses `spawn('convert', [...args])` — handles large binary output safely, no shell injection risk from user-supplied filenames, and streams efficiently. Meanwhile, their order-matching algorithm (CPU-intensive route optimization) is implemented as a separate Node.js script and invoked with `fork('./route-optimizer.js')`, letting the main API server hand off the computation and receive the result back via `message` events without blocking.

## 🟡 Real Example Hindi mein
**Swiggy DevOps CLI vs production services:** Internal CLI script `exec('git log...')` use करता है — trusted, छोटा output, shell features useful। Production image-resizing service `spawn('convert', [...])` use करता है — large binary output safely handle करता है, shell injection risk नहीं। Order-matching algorithm (CPU-intensive) अलग Node script है, `fork()` से invoke होता है, result `message` event से वापस मिलता है, main server block नहीं होता।

---

## 💻 Code Example — Basic
```javascript
// exec-spawn-fork-basics.js
const { exec, execFile, spawn, fork } = require('child_process');

// 1. exec() -- shell command, full output buffered, shell features work
exec('echo "Hello" && echo "World"', (err, stdout) => {
  console.log('exec output:', stdout); // "Hello\nWorld\n" -- && worked because of shell
});

// 2. execFile() -- runs a specific executable directly, NO shell, safer
execFile('node', ['--version'], (err, stdout) => {
  console.log('execFile output:', stdout.trim());
});

// 3. spawn() -- streaming, array-based args, no shell by default
const child = spawn('echo', ['Hello', 'World']); // NOTE: && would NOT work here (no shell)
child.stdout.on('data', (data) => console.log('spawn stdout:', data.toString()));

// 4. fork() -- spawn another Node script with IPC (requires a separate file)
// Assume ./math-worker.js contains:
//   process.on('message', (nums) => {
//     const sum = nums.reduce((a, b) => a + b, 0);
//     process.send(sum);
//   });
const mathWorker = fork('./math-worker.js');
mathWorker.send([1, 2, 3, 4, 5]);
mathWorker.on('message', (sum) => {
  console.log('fork result:', sum); // 15
  mathWorker.kill(); // clean up after receiving the result
});
```

## 💻 Code Example — Advanced
```javascript
// exec-spawn-fork-advanced.js -- production comparison patterns
const { exec, spawn, fork } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

// ─── 1. exec() -- GOOD for: short trusted commands with shell features ───────
async function getGitInfo() {
  // Shell features (&&) are genuinely useful here, input is NOT user-controlled
  const { stdout } = await execAsync('git rev-parse HEAD && git branch --show-current');
  return stdout.trim().split('\n');
}

// ─── 2. spawn() -- GOOD for: user input, large output, long-running processes ─
function resizeImageSafely(inputPath, outputPath, width) {
  return new Promise((resolve, reject) => {
    // Arguments passed as array -- inputPath/outputPath could be user-controlled,
    // but spawn() never interprets them as shell syntax, so injection is impossible
    const convert = spawn('convert', [inputPath, '-resize', `${width}x`, outputPath]);

    let stderr = '';
    convert.stderr.on('data', (d) => (stderr += d));
    convert.on('close', (code) => {
      code === 0 ? resolve(outputPath) : reject(new Error(`convert failed: ${stderr}`));
    });
    convert.on('error', reject);
  });
}

// ─── 3. fork() -- GOOD for: CPU-heavy JS work needing structured communication ─
function computeFibonacciInWorker(n) {
  return new Promise((resolve, reject) => {
    const worker = fork('./fib-worker.js'); // separate file computing fibonacci(n)
    worker.send({ n });
    worker.on('message', (result) => {
      resolve(result);
      worker.kill();
    });
    worker.on('error', reject);
    setTimeout(() => { worker.kill(); reject(new Error('Worker timeout')); }, 5000);
  });
}

// Example fib-worker.js:
// process.on('message', ({ n }) => {
//   function fib(x) { return x <= 1 ? x : fib(x - 1) + fib(x - 2); }
//   process.send(fib(n)); // CPU-intensive, doesn't block the PARENT's event loop
// });

// ─── 4. COMPARISON TABLE AS CODE (for quick reference/testing) ───────────────
const comparisonMatrix = {
  exec:     { shell: true,  streaming: false, maxOutput: '1MB default', ipc: false, injectionRisk: 'HIGH if user input used' },
  execFile: { shell: false, streaming: false, maxOutput: '1MB default', ipc: false, injectionRisk: 'LOW (no shell)' },
  spawn:    { shell: false, streaming: true,  maxOutput: 'unlimited',   ipc: false, injectionRisk: 'LOW (no shell by default)' },
  fork:     { shell: false, streaming: true,  maxOutput: 'unlimited',   ipc: true,  injectionRisk: 'N/A (runs trusted JS file)' },
};

module.exports = { getGitInfo, resizeImageSafely, computeFibonacciInWorker, comparisonMatrix };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const { exec, spawn, fork } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const app = express();

// 1. exec() for a trusted, internal admin command (no user input in the command string)
app.get('/admin/server-stats', async (req, res) => {
  try {
    const { stdout } = await execAsync('uptime && df -h | head -5'); // fixed command, safe
    res.json({ stats: stdout });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 2. spawn() for user-controlled input (e.g. filename from an upload) -- SAFE from injection
app.post('/convert-image', express.json(), (req, res) => {
  const { filename, format } = req.body; // untrusted user input
  const convert = spawn('convert', [`./uploads/${filename}`, `./converted/${filename}.${format}`]);

  convert.on('close', (code) => {
    code === 0
      ? res.json({ message: 'Converted successfully' })
      : res.status(500).json({ error: 'Conversion failed' });
  });
  convert.on('error', (err) => res.status(500).json({ error: err.message }));
});

// 3. fork() to offload CPU-heavy JS computation without blocking the API
app.post('/calculate-route', express.json(), (req, res) => {
  const worker = fork('./route-optimizer.js');
  worker.send(req.body); // { deliveryPoints: [...] }

  worker.on('message', (optimizedRoute) => {
    res.json({ route: optimizedRoute });
    worker.kill();
  });

  const timeout = setTimeout(() => {
    worker.kill();
    res.status(504).json({ error: 'Route calculation timed out' });
  }, 10000);

  worker.on('message', () => clearTimeout(timeout)); // cancel timeout on success
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `exec()` with any user-supplied data in the command string
```javascript
// Wrong -- classic shell injection vulnerability
exec(`convert ${req.body.filename} output.png`, callback); // filename = "a.jpg; rm -rf /"

// Correct -- use spawn()/execFile() with arguments as an array
spawn('convert', [req.body.filename, 'output.png']); // filename treated as literal string
```

❌ Mistake 2: Using `fork()` when you actually just need to run an external (non-Node) program
```javascript
// Wrong -- fork() is ONLY for Node.js scripts, this won't work for arbitrary binaries
fork('ffmpeg', ['-i', 'input.mp4']); // fork() expects a NODE.JS module path, not an arbitrary executable

// Correct -- use spawn() for external programs
spawn('ffmpeg', ['-i', 'input.mp4']);
```

❌ Mistake 3: Using `exec()` for processes with large or unpredictable output volume
```javascript
// Wrong -- exceeding default 1MB maxBuffer throws an error and kills the process
exec('find / -type f', (err, stdout) => { /* likely crashes on large filesystems */ });

// Correct -- use spawn() to stream output without a buffer ceiling
const find = spawn('find', ['/', '-type', 'f']);
find.stdout.on('data', (chunk) => processChunkIncrementally(chunk));
```

---

## 🧠 Tricky Interview Question
```javascript
const { spawn } = require('child_process');

const child = spawn('echo hello && echo world'); // single string, not array args!
child.stdout.on('data', (d) => console.log(d.toString()));
child.on('error', (err) => console.log('Error:', err.message));
```
Answer: This triggers an `'error'` event, NOT the expected shell behavior. Because `spawn()` does NOT use a shell by default, it tries to execute a single "command" literally named `'echo hello && echo world'` (the entire string as ONE executable name) — there's no such executable, so it fails with something like `Error: spawn echo hello && echo world ENOENT`. To get shell features with `spawn()`, you must explicitly pass `{ shell: true }` as an option, OR split into `spawn('echo', ['hello'])` and `spawn('echo', ['world'])` as separate calls, OR just use `exec()` instead, which runs through a shell naturally. This is the most common `spawn()` gotcha — forgetting it has no shell parsing unless explicitly enabled.

---

## ⚫ Interview Questions + Answers

Q1: If you need to run `grep | wc -l` style shell pipelines, which function should you use and why?
A1: `exec()` (or `spawn()` with `{ shell: true }`) — because pipe (`|`) syntax is a SHELL feature, not something the OS process-creation API understands natively. `exec()` runs your command string through an actual shell (`/bin/sh`), which interprets the pipe and wires the two commands' stdout/stdin together before returning the final combined result.

Q2: Why is `spawn()` generally considered safer than `exec()` for handling external/user input?
A2: `spawn(command, argsArray)` passes the command and each argument as SEPARATE values directly to the OS process-creation syscall, bypassing shell interpretation entirely (by default) — special shell characters (`;`, `&&`, backticks, `|`) in an argument are treated as a literal, inert string, not executable syntax. `exec(commandString)` concatenates everything into one string that a REAL shell parses, so any unsanitized user input embedded in that string can inject additional commands.

Q3: What unique capability does `fork()` provide that neither `exec()` nor `spawn()` offers directly?
A3: A built-in, automatic IPC (inter-process communication) channel specifically for exchanging structured JavaScript objects between parent and child — `child.send(obj)` on one side and `process.on('message', fn)` on the other, with Node handling the serialization/deserialization. `spawn()` only gives you raw stdin/stdout/stderr pipes (text/binary streams); you'd have to manually serialize/parse JSON yourself to pass structured data, and even then it's less ergonomic than `fork()`'s native message passing.

Q4: Can you use `fork()` to run a Python script or a shell command?
A4: No — `fork()` is specifically hardcoded to spawn a NEW NODE.JS PROCESS running the given JavaScript module path (it sets `execPath` to the current Node binary internally). For non-Node programs (Python scripts, shell commands, compiled binaries), you must use `spawn()` or `exec()`/`execFile()` instead.

Q5: What's the practical difference in memory/output handling between `exec()` and `spawn()` when a command produces 500MB of output?
A5: `exec()` would almost certainly FAIL — it buffers the ENTIRE output in memory before calling the callback, and the default `maxBuffer` is only 1MB (configurable, but even raising it to 500MB+ risks memory pressure and defeats streaming benefits). `spawn()` handles this gracefully because `child.stdout` is a real Readable STREAM — you process data incrementally as it arrives (writing to a file, piping elsewhere, or processing chunk by chunk), never needing to hold all 500MB in memory simultaneously.

---

## 🔷 When to Use + When Not to Use
✅ Use `exec()` when:
- Running short, trusted, fixed commands with small output
- You genuinely need shell features (pipes, redirects, globbing, `&&`)

✅ Use `spawn()` when:
- Output could be large or unbounded (streaming is safer)
- Command/arguments include any user-supplied or dynamic data (avoids injection)
- The process runs long and you want to react to output incrementally

✅ Use `fork()` when:
- You need to run ANOTHER Node.js script and exchange structured data via messages
- Offloading CPU-intensive JS computation from the main process while keeping easy communication

❌ Avoid `exec()` when: user input is involved, or output could be large.
❌ Avoid `fork()` when: the target isn't a Node.js script.
❌ Avoid `spawn()` when: you genuinely need shell syntax and have no injection risk (then `exec()` is simpler).

---

## 📊 Visual Diagram
```
DECISION TREE:

  Need to run another NODE.JS script with message-passing?
       │
       ├─ YES ──► fork()
       │
       └─ NO
            │
            Need shell features (pipes, &&, globbing) AND input is trusted/small?
                 │
                 ├─ YES ──► exec()
                 │
                 └─ NO (large output, untrusted input, long-running) ──► spawn()


OUTPUT HANDLING COMPARISON:

  exec():                           spawn():
  ┌────────────────────┐            ┌────────────────────┐
  │ child process runs   │           │ child process runs   │
  │       │               │          │       │               │
  │       ▼               │          │       ▼               │
  │ [ALL output buffered  │          │ stdout/stderr STREAM  │
  │  in memory until done]│          │ chunk by chunk, live  │
  │       │               │          │       │               │
  │       ▼               │          │       ▼               │
  │ callback(err, stdout) │          │ 'data' events as      │
  │ (fires ONCE, at end)  │          │  they arrive           │
  └────────────────────┘            └────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| exec() | Shell command, buffered output | Shell command, buffered output |
| execFile() | Direct executable, no shell | Direct executable, shell नहीं |
| spawn() | Streaming process, array args | Streaming process, array arguments |
| fork() | Node script + IPC messaging | Node script + IPC messaging |
| shell injection | Malicious command via unsanitized input | Unsanitized input से malicious command |
| maxBuffer | exec()'s output size limit | exec() की output size limit |

---

## ⚡ 3-Line Summary
English: `exec()` suits short trusted commands needing shell features (buffers output, injection risk with user input). `spawn()` suits large/unbounded output and untrusted input (streams output, array-based args avoid injection). `fork()` is exclusively for launching Node.js scripts with structured IPC messaging.

Hindi: `exec()` छोटे trusted commands के लिए जिनमें shell features चाहिए (output buffer करता है, user input से injection risk)। `spawn()` large/unbounded output और untrusted input के लिए (streaming, array args से injection नहीं)। `fork()` सिर्फ Node.js scripts चलाने के लिए, structured IPC messaging के साथ।

---

## ➡️ Next Topic
**57. cluster Module** — scaling a Node.js app across multiple CPU cores by forking worker processes that share the same server port.
