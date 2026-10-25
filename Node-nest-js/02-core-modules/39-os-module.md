# 39. os Module
# हिंदी में: os Module — Operating System Information

---

## 🔵 Simple Definition (English)
The **`os`** module is Node's built-in API for retrieving operating-system-level information — CPU details, total/free memory, network interfaces, hostname, platform, uptime, and the system's home/temp directories.

## 🔵 सरल परिभाषा (Hindi)
**`os`** module Node का built-in API है operating-system-level information लेने के लिए — CPU details, total/free memory, network interfaces, hostname, platform, uptime, और system की home/temp directories।

---

## 🔴 Problem it Solves
Server applications often need to adapt behavior based on the hardware/environment they're running on: spawning one worker process per CPU core (clustering), monitoring memory pressure to trigger alerts before an out-of-memory crash, logging which host handled a request in a multi-server deployment, or building cross-platform CLI tools that need the correct temp/home directory regardless of OS. `os` provides all this system-level insight without needing external OS-specific commands or shelling out.

## 🔴 यह क्यों बना? (Hindi)
Server applications को अक्सर hardware/environment के हिसाब से behavior adapt करना होता है: हर CPU core के लिए एक worker process spawn करना (clustering), memory pressure monitor करना out-of-memory crash से पहले alerts trigger करने के लिए, multi-server deployment में कौन सा host request handle किया यह log करना, या cross-platform CLI tools बनाना जिन्हें OS के हिसाब से correct temp/home directory चाहिए। `os` यह सब system-level insight देता है बिना external OS-specific commands या shell out किए।

---

## 🟢 How it Works — Step by Step

Step 1 → `const os = require('os')` or `require('node:os')` — built-in, no installation.
Step 2 → `os.cpus()` returns an array of CPU core info objects (model, speed, times spent in user/system/idle) — `os.cpus().length` gives the number of logical cores, essential for the `cluster` module to spawn one worker per core.
Step 3 → `os.totalmem()`/`os.freemem()` return total and currently-free system memory in bytes — used for health checks and memory-pressure monitoring.
Step 4 → `os.platform()` returns the OS identifier (`'linux'`, `'darwin'`, `'win32'`); `os.arch()` returns CPU architecture (`'x64'`, `'arm64'`).
Step 5 → `os.hostname()` returns the machine's network hostname — useful for logging which server instance handled a request in load-balanced deployments.
Step 6 → `os.homedir()`/`os.tmpdir()` give the correct per-OS home directory and temp directory paths — critical for CLI tools that must store user config or scratch files correctly on ANY platform.
Step 7 → `os.networkInterfaces()` returns detailed info about all network interfaces and their IP addresses — used in tools that need to know the machine's own IP for service discovery/binding.
Step 8 → `os.uptime()` returns how long the OPERATING SYSTEM (not the Node process) has been running, in seconds — different from `process.uptime()` which tracks the current Node process only.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const os = require('os')` या `require('node:os')` — built-in, install नहीं चाहिए।
Step 2 → `os.cpus()` CPU core info objects का array देता है (model, speed, user/system/idle में बिता समय) — `os.cpus().length` logical cores की संख्या देता है, `cluster` module के लिए हर core पर एक worker spawn करने के लिए ज़रूरी।
Step 3 → `os.totalmem()`/`os.freemem()` total और currently-free system memory bytes में देते हैं — health checks और memory-pressure monitoring के लिए use होता है।
Step 4 → `os.platform()` OS identifier देता है (`'linux'`, `'darwin'`, `'win32'`); `os.arch()` CPU architecture देता है (`'x64'`, `'arm64'`)।
Step 5 → `os.hostname()` machine का network hostname देता है — load-balanced deployments में कौन सा server instance request handle किया यह log करने के लिए useful।
Step 6 → `os.homedir()`/`os.tmpdir()` per-OS correct home directory और temp directory paths देते हैं — CLI tools के लिए critical जो ANY platform पर correctly user config या scratch files store करने होते हैं।
Step 7 → `os.networkInterfaces()` सभी network interfaces और उनके IP addresses की detailed info देता है — उन tools में use होता है जिन्हें machine का अपना IP service discovery/binding के लिए जानना होता है।
Step 8 → `os.uptime()` OPERATING SYSTEM (Node process नहीं) कितने समय से चल रहा है, seconds में देता है — `process.uptime()` से अलग जो सिर्फ current Node process track करता है।

---

## 🟡 Real World Example
**Zomato's order-matching microservice cluster scaling:** On each server instance, the service uses `os.cpus().length` to determine how many Node.js worker processes to spawn via the `cluster` module — fully utilizing a 16-core server by running 16 worker processes, each handling a share of incoming order-matching requests. A separate health-monitoring sidecar periodically checks `os.freemem() / os.totalmem()` and triggers an alert (and potentially a graceful restart) if free memory drops below 10%, preventing an OOM crash mid-peak-hours traffic.

## 🟡 Real Example Hindi mein
**Zomato का order-matching microservice cluster scaling:** हर server instance पर, service `os.cpus().length` use करके decide करती है कि `cluster` module से कितने Node.js worker processes spawn करने हैं — 16-core server को fully utilize करती है 16 worker processes चलाकर, हर एक incoming order-matching requests का हिस्सा handle करता है। एक अलग health-monitoring sidecar periodically `os.freemem() / os.totalmem()` check करती है और free memory 10% से कम होने पर alert trigger करती है (और possibly graceful restart), peak-hours traffic के दौरान OOM crash रोकने के लिए।

---

## 💻 Code Example — Basic

```javascript
// osBasics.js — exploring system information
const os = require('os');

console.log('Platform:', os.platform());        // 'darwin', 'linux', 'win32'
console.log('Architecture:', os.arch());         // 'x64', 'arm64'
console.log('Hostname:', os.hostname());         // e.g. 'my-laptop.local'
console.log('CPU cores:', os.cpus().length);     // e.g. 8

console.log('Total memory (GB):', (os.totalmem() / 1024 ** 3).toFixed(2));
console.log('Free memory (GB):', (os.freemem() / 1024 ** 3).toFixed(2));

console.log('Home directory:', os.homedir());    // e.g. /Users/dev or C:\Users\dev
console.log('Temp directory:', os.tmpdir());      // e.g. /tmp or C:\Users\dev\AppData\Local\Temp

console.log('OS uptime (hours):', (os.uptime() / 3600).toFixed(1)); // how long the MACHINE has been on
```

## 💻 Code Example — Advanced

```javascript
// osAdvanced.js — production patterns using os module data
const os = require('os');
const cluster = require('cluster');
const http = require('http');

// ─── 1. CPU-based cluster scaling ───────────────────────────────────────────
function startClusteredServer(requestHandler) {
  const numCPUs = os.cpus().length; // scale to match available hardware

  if (cluster.isPrimary) {
    console.log(`Primary process ${process.pid} starting ${numCPUs} workers`);
    for (let i = 0; i < numCPUs; i++) {
      cluster.fork(); // one worker per CPU core
    }
    cluster.on('exit', (worker) => {
      console.log(`Worker ${worker.process.pid} died, spawning a replacement`);
      cluster.fork(); // auto-restart crashed workers
    });
  } else {
    http.createServer(requestHandler).listen(3000);
    console.log(`Worker ${process.pid} listening on port 3000`);
  }
}

// ─── 2. Memory pressure health check ────────────────────────────────────────
function getMemoryHealthStatus() {
  const total = os.totalmem();
  const free = os.freemem();
  const usedPercent = ((total - free) / total) * 100;

  return {
    totalGB: (total / 1024 ** 3).toFixed(2),
    freeGB: (free / 1024 ** 3).toFixed(2),
    usedPercent: usedPercent.toFixed(1),
    status: usedPercent > 90 ? 'critical' : usedPercent > 75 ? 'warning' : 'healthy',
  };
}

// ─── 3. Finding the machine's own LAN IP address ────────────────────────────
function getLocalIPAddress() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Skip loopback (127.0.0.1) and IPv6, find the first real IPv4 LAN address
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '127.0.0.1'; // fallback if no external interface found
}

console.log('Memory health:', getMemoryHealthStatus());
console.log('Local IP:', getLocalIPAddress());

// startClusteredServer((req, res) => res.end(`Handled by worker ${process.pid}`));
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express health-check endpoint exposing os-level diagnostics
const express = require('express');
const os = require('os');

const app = express();

app.get('/health', (req, res) => {
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const usedPercent = ((totalMem - freeMem) / totalMem) * 100;

  res.json({
    status: usedPercent > 90 ? 'degraded' : 'ok',
    hostname: os.hostname(),           // identifies WHICH server instance responded
    platform: os.platform(),
    cpuCores: os.cpus().length,
    memory: {
      totalMB: Math.round(totalMem / 1024 / 1024),
      freeMB: Math.round(freeMem / 1024 / 1024),
      usedPercent: usedPercent.toFixed(1),
    },
    loadAverage: os.loadavg(), // [1min, 5min, 15min] load averages (POSIX only, [0,0,0] on Windows)
    processUptime: process.uptime(), // Node process uptime (different from os.uptime()!)
  });
});

app.listen(3000, () => console.log(`Server running on ${os.hostname()}, PID ${process.pid}`));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Confusing `os.uptime()` with `process.uptime()`
```javascript
// Wrong — assuming these report the same thing
console.log(os.uptime());      // how long the MACHINE has been powered on (could be days/weeks)
console.log(process.uptime()); // how long THIS Node process has been running (resets on restart)
// Using os.uptime() to measure "how long has my app been running" gives a WRONG, much larger number

// Right — use the correct one for your actual question
console.log('App uptime (seconds):', process.uptime()); // correct for "how long has my app run"
```

❌ Mistake 2: Assuming `os.loadavg()` works identically on all platforms
```javascript
// Wrong — assuming loadavg() is meaningful everywhere
const [load1, load5, load15] = os.loadavg();
console.log(load1); // on Windows, this ALWAYS returns [0, 0, 0] — not a real reading!

// Right — check platform before relying on loadavg for real monitoring logic
if (os.platform() !== 'win32') {
  const [load1] = os.loadavg();
  console.log('1-minute load average:', load1);
} else {
  console.log('Load average not available on Windows — use alternative metrics (e.g., process.cpuUsage())');
}
```

---

## 🧠 Tricky Interview Question

```javascript
const os = require('os');
const cluster = require('cluster');

if (cluster.isPrimary) {
  console.log('CPUs:', os.cpus().length);
  for (let i = 0; i < os.cpus().length; i++) {
    cluster.fork();
  }
}
```
Answer: This spawns ONE worker process PER LOGICAL CPU core reported by `os.cpus().length` — on an 8-core machine (or a 4-core machine with hyperthreading showing 8 logical cores), it forks 8 worker processes. The "trick" interviewers probe: `os.cpus().length` counts LOGICAL cores (including hyperthreaded/SMT virtual cores), NOT physical cores — so a 4-physical-core CPU with hyperthreading reports 8, and spawning 8 workers may NOT yield 2x the real parallel throughput of 4 workers, since hyperthreaded cores share physical execution resources. This is why some high-performance Node deployments deliberately spawn FEWER workers than `os.cpus().length` suggests, benchmarking actual throughput rather than blindly trusting the logical core count.

---

## ⚫ Interview Questions + Answers

Q1: How is `os` module information commonly used in Node.js clustering?
A1: `os.cpus().length` returns the number of logical CPU cores available, which is the standard input for the `cluster` module's worker-spawning logic (`for (let i = 0; i < os.cpus().length; i++) cluster.fork();`). Since Node.js JS execution is single-threaded per process, spawning one worker process per core lets a Node application actually utilize ALL available CPU cores for request handling, since each worker runs in its own OS process with its own event loop.

Q2: What's the difference between `os.uptime()` and `process.uptime()`?
A2: `os.uptime()` returns how long the ENTIRE operating system/machine has been powered on and running, in seconds — unrelated to any specific application. `process.uptime()` returns how long the CURRENT Node.js process has been running since it started — resets to zero every time the app restarts/crashes/redeploys. Confusing the two gives wildly incorrect "how long has my app been up" metrics, especially on long-running servers that have been on for months while the app itself restarts frequently during deploys.

Q3: Why might `os.freemem()` not be a perfectly reliable indicator of how much memory is "actually available" for your application?
A3: Operating systems use "free" memory for disk caching and other OS-level purposes that can be immediately reclaimed when an application needs it — so a low `freemem()` reading doesn't necessarily mean memory is truly scarce; much of it could be reclaimable cache. For more accurate application-level memory pressure, many production systems instead monitor the Node process's OWN memory usage via `process.memoryUsage()` (heap used, RSS) combined with container/cgroup-level memory limits (common in Docker/Kubernetes) rather than relying solely on the host OS's raw free memory figure.

Q4: Why does `os.loadavg()` return `[0, 0, 0]` on Windows?
A4: "Load average" is a POSIX/Unix-specific concept (tracking the average number of processes waiting for CPU time over 1/5/15 minute windows) that Windows doesn't natively expose in the same way. Node's `os.loadavg()` simply has no real data source to report from on Windows, so it always returns zeros there — code relying on this metric for health monitoring needs a platform check or an alternative Windows-compatible metric.

Q5: How would you use the `os` module to determine the correct cross-platform location to store a CLI tool's config file?
A5: Use `os.homedir()` to get the user's home directory correctly on any OS (`/home/user` on Linux, `/Users/user` on macOS, `C:\Users\user` on Windows), then build a config path with `path.join(os.homedir(), '.mytool', 'config.json')`. For temporary/scratch files that don't need to persist, use `os.tmpdir()` similarly — both avoid hardcoding platform-specific paths that would break when the tool runs on a different OS than it was developed on.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Scaling worker processes to match available CPU cores (`cluster` module setups).
- Building health-check endpoints exposing memory/CPU/host diagnostics.
- Writing cross-platform CLI tools needing correct home/temp directory paths.
- Logging which server instance (hostname) handled a request in multi-server deployments.

❌ Avoid when:
- Relying on `os.loadavg()` for cross-platform monitoring (Windows doesn't support it meaningfully).
- Using `os.freemem()` alone as your sole memory-pressure signal — combine with `process.memoryUsage()` and container-level limits for accuracy in containerized environments.

---

## 📊 Visual Diagram
```
os MODULE — KEY SURFACES:
──────────────────────────────────────────────────────────
  os
    ├── cpus()              → array of CPU core info (model, speed, times)
    ├── totalmem() / freemem() → system memory in bytes
    ├── platform() / arch()  → 'linux'/'darwin'/'win32', 'x64'/'arm64'
    ├── hostname()            → machine's network name
    ├── homedir() / tmpdir()  → correct per-OS paths
    ├── networkInterfaces()   → IP addresses of all interfaces
    ├── uptime()              → OS uptime (NOT app uptime!)
    └── loadavg()              → [1,5,15]-min load (POSIX only)

CLUSTERING WITH os.cpus():
  Server (8 logical cores)
    ├── Worker 1 (PID 1001) ─┐
    ├── Worker 2 (PID 1002)  ├─ all sharing port 3000, load-balanced by OS
    ├── ...                  │
    └── Worker 8 (PID 1008) ─┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| os.cpus() | CPU core information array | CPU core information array |
| os.totalmem/freemem | System memory stats | System memory stats |
| os.platform() | OS identifier | OS identifier |
| os.hostname() | Machine's network name | Machine का network name |
| os.homedir/tmpdir | Correct per-OS paths | Correct per-OS paths |
| Logical core | CPU core incl. hyperthreading | Hyperthreading शामिल CPU core |
| Load average | POSIX CPU queue metric | POSIX CPU queue metric |

---

## ⚡ 3-Line Summary
English: The `os` module exposes system-level info — CPU count, memory, platform, hostname, home/temp directories — commonly used for CPU-based cluster scaling, health-check diagnostics, and cross-platform path resolution. Don't confuse `os.uptime()` (machine uptime) with `process.uptime()` (app uptime), and remember `os.loadavg()` is POSIX-only (returns zeros on Windows). For accurate memory-pressure monitoring in containers, combine `os.freemem()` with `process.memoryUsage()` and container limits rather than relying on OS-level free memory alone.
Hindi: `os` module system-level info expose करता है — CPU count, memory, platform, hostname, home/temp directories — commonly CPU-based cluster scaling, health-check diagnostics, और cross-platform path resolution के लिए use होता है। `os.uptime()` (machine uptime) को `process.uptime()` (app uptime) से confuse मत करो, और याद रखो `os.loadavg()` POSIX-only है (Windows पर zeros return करता है)। Containers में accurate memory-pressure monitoring के लिए, सिर्फ OS-level free memory पर depend करने की जगह `os.freemem()` को `process.memoryUsage()` और container limits के साथ combine करो।

---

## ➡️ Next Topic
**40. http Module — Create Server** — building raw HTTP servers using Node's built-in `http` module, the foundation Express is built on.
