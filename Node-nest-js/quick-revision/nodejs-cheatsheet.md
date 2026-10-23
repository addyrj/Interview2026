# Node.js Quick Revision — Top Concepts Cheatsheet

---

## ⚡ Event Loop (Most Asked Topic)

```javascript
// Execution ORDER:
// 1. Synchronous code (call stack)
// 2. process.nextTick() — microtask, highest priority
// 3. Promise.then() — microtask, after nextTick
// 4. setTimeout(fn, 0) — TIMERS phase
// 5. setImmediate() — CHECK phase (after POLL)
// 6. I/O callbacks (fs, http, db) — POLL phase

setTimeout(() => console.log('C'), 0);
setImmediate(() => console.log('D'));
process.nextTick(() => console.log('A'));
Promise.resolve().then(() => console.log('B'));
console.log('SYNC');
// Output: SYNC → A → B → C or D (uncertain) → D or C

// INSIDE I/O callback: setImmediate ALWAYS before setTimeout!
fs.readFile('./file', () => {
  setTimeout(() => console.log('2'), 0);
  setImmediate(() => console.log('1'));  // ALWAYS first
});
```

---

## ⚡ Non-Blocking I/O

```javascript
// WRONG: Blocks Event Loop
const data = fs.readFileSync('./large-file.txt');  // ← blocks ALL requests!

// CORRECT: Non-blocking
const data = await fs.promises.readFile('./large-file.txt');  // ← yields to Event Loop

// PARALLEL (fastest pattern):
const [user, orders] = await Promise.all([
  db.query('SELECT * FROM users WHERE id = ?', [id]),
  db.query('SELECT * FROM orders WHERE user_id = ?', [id]),
]);
// Total time = max(query1, query2) instead of query1 + query2
```

---

## ⚡ Express Middleware Chain

```javascript
// Order matters! Always:
app.use(helmet());          // 1. Security headers
app.use(cors());            // 2. CORS
app.use(express.json());    // 3. Body parsing (BEFORE routes!)
app.use(rateLimiter);       // 4. Rate limiting
app.use(requestLogger);     // 5. Logging
app.use('/api', routes);    // 6. Routes
app.use(notFoundHandler);   // 7. 404 (after routes)
app.use(errorHandler);      // 8. Error handler (4 params, LAST!)

// Error handler signature (MUST be 4 params):
app.use((err, req, res, next) => {  // ← 4 params!
  res.status(err.statusCode || 500).json({ error: err.message });
});

// Middleware that forgets next() → request hangs:
app.use((req, res, next) => {
  console.log('logged');
  next();  // MUST call next() or send a response
});
```

---

## ⚡ JWT Authentication

```javascript
// Generate (on login):
const accessToken = jwt.sign(
  { userId: user._id, email: user.email, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: '15m' }  // short-lived!
);
const refreshToken = jwt.sign(
  { userId: user._id },
  process.env.JWT_REFRESH_SECRET,  // different secret!
  { expiresIn: '30d' }
);

// Verify (in middleware):
const payload = jwt.verify(token, process.env.JWT_SECRET);

// NEVER: localStorage, ALWAYS: memory + HttpOnly cookie
// NEVER: sensitive data in payload (it's Base64, not encrypted!)
// ALWAYS: separate secrets for access + refresh tokens
```

---

## ⚡ bcrypt Password Hashing

```javascript
// Hash (on registration):
const hash = await bcrypt.hash(password, 12);  // cost 12 = ~300ms

// Verify (on login):
const isMatch = await bcrypt.compare(password, storedHash);

// Timing attack prevention:
const dummyHash = '$2b$12$dummy.hash.for.timing.attack.0000000';
const hash = user?.passwordHash || dummyHash;
const isMatch = await bcrypt.compare(password, hash);  // same timing
if (!user || !isMatch) throw new UnauthorizedException('Invalid credentials');

// NEVER: MD5, SHA1, SHA256 for passwords (too fast → brute-forceable)
// NEVER: cost < 10 (too fast), cost > 14 (too slow for UX)
```

---

## ⚡ Streams (Senior Level)

```javascript
// Reading large file WITHOUT streams: loads 10GB into RAM
const data = await fs.promises.readFile('./10gb-file.csv');  // ❌ OOM

// WITH streams: constant ~64KB RAM usage
const readable = fs.createReadStream('./10gb-file.csv', { highWaterMark: 64 * 1024 });
readable.on('data', chunk => processChunk(chunk));
readable.on('end', () => console.log('Done'));

// Pipe: read file → compress → write (memory efficient)
fs.createReadStream('./large.csv')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('./large.csv.gz'));

// Express: stream file download (no RAM spike)
app.get('/download/:file', (req, res) => {
  fs.createReadStream(`./uploads/${req.params.file}`).pipe(res);
});
```

---

## ⚡ Cluster + PM2 (Production)

```javascript
// Cluster: use all CPU cores
const cluster = require('cluster');
const os = require('os');

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) cluster.fork();
  cluster.on('exit', (worker) => cluster.fork());  // restart on crash
} else {
  require('./server');  // worker runs Express
}

// PM2 equivalent (production preferred):
// pm2 start server.js -i max     → creates cluster per CPU
// pm2 start server.js -i 4       → 4 workers
// pm2 startup                    → auto-start on reboot
// pm2 logs / pm2 monit           → monitoring
```

---

## ⚡ Common Tricky Interview Questions

```javascript
// Q1: Output of this code?
setTimeout(() => console.log(1), 0);
Promise.resolve().then(() => console.log(2));
process.nextTick(() => console.log(3));
console.log(4);
// Answer: 4 → 3 → 2 → 1

// Q2: Why does Node.js scale better than traditional servers?
// Traditional: 1 thread per request × 1MB = 1GB RAM for 1000 requests
// Node.js: Event Loop handles 1000 concurrent requests on 1 thread + libuv pool
// Key: I/O delegated to libuv thread pool → JS thread never blocks

// Q3: What blocks the Event Loop?
// ❌ fs.readFileSync, JSON.parse(hugeString), bcrypt.hashSync
// ❌ long for loops, regex on huge strings, crypto without async
// ✅ Fix: async APIs, Worker Threads for CPU work, streaming for large data

// Q4: Difference between process.nextTick and setImmediate?
// nextTick: runs before current phase ends (microtask)
// setImmediate: runs in CHECK phase (after POLL)
// nextTick → higher priority → runs first

// Q5: What is the libuv thread pool?
// Default 4 threads, handles: fs I/O, DNS, crypto, zlib
// Your JS runs on 1 thread; blocking I/O delegated to pool
// Increase: UV_THREADPOOL_SIZE=16 node app.js (max useful = CPU cores)
```

---

## ⚡ Node.js + Express Production Checklist

```
Security:
  ✅ helmet() — security headers
  ✅ cors() with whitelist — no wildcard *
  ✅ rate limiting (express-rate-limit)
  ✅ Input validation (joi or express-validator)
  ✅ JWT expiry (15m access, 30d refresh)
  ✅ bcrypt(12) for passwords
  ✅ SQL parameterized queries / ORM (no string concatenation)
  ✅ HTTPS only in production

Performance:
  ✅ compression middleware (gzip responses)
  ✅ cluster / PM2 (use all CPU cores)
  ✅ Connection pooling (DB connections)
  ✅ Redis caching (frequent reads)
  ✅ No blocking I/O in request handlers

Reliability:
  ✅ Graceful shutdown (SIGTERM handler)
  ✅ process.on('uncaughtException') / 'unhandledRejection'
  ✅ Health check endpoint (/health)
  ✅ Error logging (Winston, Pino)
  ✅ PM2 auto-restart on crash
```

---

## ⚡ Key npm packages to know

| Purpose | Package |
|---------|---------|
| HTTP framework | `express` |
| JWT | `jsonwebtoken` |
| Password hashing | `bcrypt` |
| Validation | `joi`, `express-validator` |
| Security headers | `helmet` |
| CORS | `cors` |
| Rate limiting | `express-rate-limit` |
| Logging | `morgan` (HTTP), `winston` or `pino` (app) |
| Config / env | `dotenv` |
| MySQL ORM | `sequelize`, `prisma` |
| MongoDB ODM | `mongoose` |
| Redis | `ioredis` |
| WebSocket | `socket.io` |
| Job queue | `bullmq` |
| Process manager | `pm2` |
| Testing | `jest`, `supertest` |
