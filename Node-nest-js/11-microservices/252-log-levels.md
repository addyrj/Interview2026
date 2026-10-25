# 252. Log Levels
# हिंदी में: Log Levels — error, warn, info, debug Hierarchy

---

## 🔵 Simple Definition (English)
**Log levels** are a priority ranking system for log messages, so you can control HOW MUCH gets logged and WHERE it goes. Winston's npm log levels (lowest number = highest severity) are: `error(0) > warn(1) > info(2) > http(3) > verbose(4) > debug(5) > silly(6)`. Setting a logger's `level` shows that level AND everything more severe (lower number), hiding everything less severe.

## 🔵 सरल परिभाषा (Hindi)
**Log levels** एक priority ranking system हैं log messages के लिए, जिससे आप control कर सकते हो कि कितना log होगा और कहां जाएगा। Winston के npm log levels (कम number = ज़्यादा severity) हैं: `error(0) > warn(1) > info(2) > http(3) > verbose(4) > debug(5) > silly(6)`। Logger का `level` set करने से वो level AND उससे ज़्यादा severe (कम number वाले) levels दिखते हैं, कम severe वाले hide हो जाते हैं।

---

## 🔴 Problem it Solves
```
WITHOUT LOG LEVELS (log everything always):
  console.log('Entering function processOrder');
  console.log('Validating input...');
  console.log('Cache hit for product 123');
  console.log('ERROR: Payment gateway down!');
  console.log('Order saved to DB');

  Problems:
    1. In production, this floods log files with noise — "Cache hit for
       product 123" happens 10,000 times/sec, drowning out the ONE
       critical "Payment gateway down" error
    2. Can't tell what's important vs routine debug chatter
    3. Searching for real problems means scrolling through megabytes
       of verbose noise
    4. No way to say "show me only serious stuff in prod, but everything
       in dev" without changing code

LOG LEVELS SOLUTION:
  logger.debug('Entering function processOrder');  // dev only
  logger.debug('Cache hit for product 123');        // dev only
  logger.error('Payment gateway down!');             // ALWAYS shown
  logger.info('Order saved to DB');                  // shown in prod too

  Set level='debug' in dev → see everything
  Set level='info' in prod → only info/warn/error shown, debug/verbose hidden
  ONE line of config change, zero code changes needed
```

## 🔴 यह क्यों बना? (Hindi)
```
Log levels के बिना (हमेशा सब log करना):
  - Production में हर चीज़ log होने से files noise से भर जाती हैं
  - "Cache hit" जैसे routine messages असली critical error को दबा देते हैं
  - क्या important है और क्या सिर्फ debug chatter है पता नहीं चलता
  - असली problem ढूंढने के लिए megabytes noise में scroll करना पड़ता है

Log levels solution:
  - debug level dev में सब दिखाता है
  - info level prod में सिर्फ ज़रूरी चीज़ें दिखाता है (info/warn/error)
  - सिर्फ एक config line बदलकर behavior change होता है, code नहीं
```

---

## 🟢 How it Works — Step by Step

Step 1 → Winston defines npm levels with numeric priority: `error:0, warn:1, info:2, http:3, verbose:4, debug:5, silly:6` (lower number = more severe/important).
Step 2 → You configure the logger's `level` option — e.g., `level: 'info'`. This acts as a THRESHOLD.
Step 3 → When you call `logger.someLevel(msg)`, Winston checks: is `someLevel`'s number <= configured threshold's number? If yes, it logs; if no, it's silently dropped.
Step 4 → Set the threshold dynamically based on `process.env.NODE_ENV` or `process.env.LOG_LEVEL` — `debug` in local dev (see everything while coding), `info` or `warn` in staging/production (reduce noise, keep only meaningful events + errors).
Step 5 → Different transports can have DIFFERENT levels too — e.g., Console transport shows `debug`, but the File transport for `error.log` only accepts `error` level, filtering even further per destination.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Winston npm levels को numeric priority देता है: `error:0, warn:1, info:2, http:3, verbose:4, debug:5, silly:6` (कम number = ज़्यादा severe)।
Step 2 → आप logger का `level` option configure करते हो — जैसे `level: 'info'`। यह एक THRESHOLD के रूप में काम करता है।
Step 3 → जब आप `logger.someLevel(msg)` call करते हो, Winston check करता है: क्या `someLevel` का number threshold से कम/बराबर है? हाँ तो log होगा, नहीं तो silently drop।
Step 4 → Threshold को `NODE_ENV`/`LOG_LEVEL` के हिसाब से dynamically set करो — local dev में `debug`, staging/production में `info`/`warn`।
Step 5 → अलग-अलग transports के अलग levels हो सकते हैं — जैसे Console `debug` दिखाए, पर `error.log` सिर्फ `error` accept करे।

---

## 🟡 Real World Example
**Amazon checkout service:** In local development, engineers set `LOG_LEVEL=debug` to see every step — cart validation, inventory check, price calculation, payment call — helpful while writing/debugging new code. In production, `LOG_LEVEL=info` is set — routine debug chatter is silenced, but business events (`info`: "Order confirmed"), warnings (`warn`: "Inventory low for SKU X"), and critical failures (`error`: "Payment gateway unreachable") are still captured. This keeps production log volume manageable (and cheap — log storage costs money at Amazon's scale) while never losing visibility into real problems.

## 🟡 Real Example Hindi mein
**Amazon checkout service:** Local development में engineers `LOG_LEVEL=debug` set करते हैं ताकि हर step दिखे — cart validation, inventory check, price calculation, payment call — नया code debug करने में मदद मिलती है। Production में `LOG_LEVEL=info` set होता है — routine debug चैटर silent हो जाता है, पर business events (`info`), warnings (`warn`), critical failures (`error`) capture होते रहते हैं। इससे production log volume manageable रहता है (storage costs बचते हैं) बिना असली problems की visibility खोए।

---

## 💻 Code Example — Basic

```javascript
// log-levels-basic.js
// npm install winston
const winston = require('winston');

// ─── 1. CREATE LOGGER AT DIFFERENT THRESHOLDS ──────────────────────────────
function createLoggerWithLevel(level) {
  return winston.createLogger({
    level, // threshold: anything at or above this severity gets logged
    format: winston.format.combine(winston.format.timestamp(), winston.format.simple()),
    transports: [new winston.transports.Console()],
  });
}

// ─── 2. TEST WITH level = 'warn' ────────────────────────────────────────────
console.log('--- Logger with level: warn ---');
const warnLogger = createLoggerWithLevel('warn');
warnLogger.error('Database connection lost');  // shown (error=0 <= warn=1)
warnLogger.warn('Memory usage at 80%');        // shown (warn=1 <= warn=1)
warnLogger.info('User logged in');             // HIDDEN (info=2 > warn=1)
warnLogger.debug('Cache lookup for key xyz');  // HIDDEN (debug=5 > warn=1)

// ─── 3. TEST WITH level = 'debug' ───────────────────────────────────────────
console.log('--- Logger with level: debug ---');
const debugLogger = createLoggerWithLevel('debug');
debugLogger.error('Database connection lost'); // shown
debugLogger.warn('Memory usage at 80%');       // shown
debugLogger.info('User logged in');            // shown (info=2 <= debug=5)
debugLogger.debug('Cache lookup for key xyz'); // shown (debug=5 <= debug=5)

// Run: node log-levels-basic.js
// Notice: the 'warn' logger silently drops info/debug lines entirely
```

## 💻 Code Example — Advanced

```javascript
// log-levels-advanced.js — environment-driven levels + per-transport level override
// npm install winston
const winston = require('winston');

// ─── 1. DECIDE LEVEL FROM ENVIRONMENT ───────────────────────────────────────
function resolveLogLevel() {
  if (process.env.LOG_LEVEL) return process.env.LOG_LEVEL; // explicit override wins
  if (process.env.NODE_ENV === 'production') return 'info'; // prod: quieter
  if (process.env.NODE_ENV === 'test') return 'warn';        // tests: minimal noise
  return 'debug'; // default (local dev): everything
}

const level = resolveLogLevel();

// ─── 2. PER-TRANSPORT LEVEL OVERRIDE ───────────────────────────────────────
const logger = winston.createLogger({
  level, // overall logger threshold
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  transports: [
    new winston.transports.Console({ level }), // console follows the global threshold
    // error.log ALWAYS only captures errors, regardless of global level —
    // useful because you NEVER want warn/info noise mixed into your error file
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    // combined.log captures everything up to the global threshold
    new winston.transports.File({ filename: 'combined.log', level }),
  ],
});

logger.info(`Logger initialized at level: ${level}`);

// ─── 3. CUSTOM LEVEL CHECK BEFORE EXPENSIVE OPERATIONS ─────────────────────
// Avoid wasting CPU building a huge debug payload if debug isn't even enabled
function logExpensiveDebugInfo(getExpensiveData) {
  if (logger.isDebugEnabled ? logger.isDebugEnabled() : logger.levels[logger.level] >= logger.levels['debug']) {
    logger.debug('Expensive debug dump', getExpensiveData()); // only computed if needed
  }
}

logExpensiveDebugInfo(() => ({ hugeObjectDump: new Array(1000).fill('x') }));

module.exports = { logger };
```

---

## 🟠 Express.js Integration

```javascript
// app.js
const express = require('express');
const { logger } = require('./log-levels-advanced');

const app = express();
app.use(express.json());

app.get('/health', (req, res) => {
  logger.debug('Health check ping received'); // noisy, only visible in dev
  res.json({ status: 'ok' });
});

app.post('/orders', (req, res) => {
  const { amount } = req.body;

  logger.info('Order request received', { amount }); // normal business flow, visible in prod

  if (amount > 100000) {
    logger.warn('Unusually large order amount', { amount }); // flag for review, not a failure
  }

  if (!amount || amount <= 0) {
    logger.error('Invalid order amount', { amount }); // genuine problem, always visible
    return res.status(400).json({ error: 'Invalid amount' });
  }

  res.status(201).json({ message: 'Order received' });
});

app.listen(3000, () => logger.info(`Server started. Log level: ${process.env.LOG_LEVEL || 'debug'}`));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Logging everything at `info` level regardless of actual severity
```javascript
// WRONG: using info for everything — can't distinguish real problems from routine events
logger.info('Payment gateway timeout!'); // this is actually an ERROR, mislabeled

// CORRECT: use the level that matches actual severity
logger.error('Payment gateway timeout!'); // now it's correctly flagged, visible in prod, alertable
```

❌ **Mistake 2:** Hardcoding log level instead of reading from environment
```javascript
// WRONG: always debug — floods production logs forever
const logger = winston.createLogger({ level: 'debug' });

// CORRECT: environment-driven
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
});
```

❌ **Mistake 3:** Using `warn` for things that aren't actually warnings
```javascript
// WRONG: logging routine successful events as warnings — causes alert fatigue
logger.warn('User logged in successfully');

// CORRECT: reserve warn for things that need attention but aren't failures yet
logger.info('User logged in successfully');
logger.warn('User attempted login with expired password reset link');
```

---

## 🧠 Tricky Interview Question

```javascript
const winston = require('winston');
const logger = winston.createLogger({
  levels: winston.config.syslog.levels, // NOTE: syslog levels, not npm levels!
  level: 'info',
  transports: [new winston.transports.Console()],
});

logger.warning('Disk almost full'); // ?
logger.warn('Disk almost full');    // ?
```
Answer: With `winston.config.syslog.levels`, the method is `logger.warning()`, NOT `logger.warn()` — syslog levels are `emerg, alert, crit, error, warning, notice, info, debug` (different names from npm's `error, warn, info, http, verbose, debug, silly`). So `logger.warning('Disk almost full')` works correctly, but `logger.warn(...)` will throw an error or silently fail depending on Winston version, because `warn` is NOT a valid method name under the syslog level set — only under the DEFAULT npm levels. This catches people who assume `warn` always exists; it depends entirely on which `levels` config the logger was created with.

---

## ⚫ Interview Questions + Answers

**Q1: List Winston's npm log levels in order of severity, highest to lowest.**
A1: `error (0) > warn (1) > info (2) > http (3) > verbose (4) > debug (5) > silly (6)`. Lower numeric value = higher severity/priority. Setting a logger's `level` to a given name shows that level and everything with a LOWER number (more severe), and hides anything with a HIGHER number (less severe).

**Q2: Why would you set `LOG_LEVEL=info` in production but `debug` in development?**
A2: In development, you want maximum visibility into what the code is doing to catch bugs quickly — `debug` shows every detail. In production, that same verbosity becomes expensive noise: huge log volumes (costly storage, slower searches), and critical errors get buried under routine chatter. `info` keeps meaningful business events (orders placed, payments processed) plus warnings/errors visible, while silencing low-value debug/verbose/silly messages.

**Q3: What's the difference between `warn` and `error` levels, and why does misusing them cause problems?**
A3: `error` means something failed and needs likely intervention (a crashed operation, an exception). `warn` means something unusual happened but the system still functioned (e.g., retrying a request, high memory usage, deprecated API used). If you log routine successes as `warn`, on-call engineers get "alert fatigue" from monitoring tools that trigger on `warn`/`error` counts, and they start ignoring real warnings. If you log real failures as `info`, they get missed entirely because dashboards filter on `warn`+ severity.

**Q4: Can different transports on the same Winston logger have different log levels? Give an example.**
A4: Yes. Each transport accepts its own `level` option that acts as an additional filter on top of (or independent from) the logger's own level. Common pattern: Console transport shows everything up to the global level (e.g., `debug` in dev), while a `File({ filename: 'error.log', level: 'error' })` transport ONLY ever writes `error`-level logs, regardless of the global setting — keeping a clean error-only file separate from the noisy combined log.

**Q5: What happens if you call `logger.debug()` when the logger's level is set to `'info'`?**
A5: Nothing gets logged/output — Winston checks `debug`'s numeric priority (5) against the configured threshold `info` (2); since 5 > 2, the message is silently filtered out before it reaches any transport. No error is thrown; the call simply does nothing. This is the intended behavior, letting you leave `logger.debug()` calls in code permanently without worrying about production noise — they only "activate" when the threshold is lowered.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any real application where you need different verbosity in dev vs prod
- You want to flag severity precisely (routine event vs warning vs failure)
- You need to filter alerts/dashboards by severity (only page on-call for `error`)

❌ Avoid when:
- A single quick script with no environment distinction — one flat log level is fine
- Levels are being used inconsistently across a team without agreed conventions (worse than no levels — misleads instead of helps)

---

## 📊 Visual Diagram
```
WINSTON NPM LOG LEVEL HIERARCHY (lower number = more severe)
──────────────────────────────────────────────────────────────

  error   (0)  ███████████████████████  always shown
  warn    (1)  ██████████████████
  info    (2)  ███████████████          ◀── typical PRODUCTION threshold
  http    (3)  ████████████
  verbose (4)  █████████
  debug   (5)  ██████                   ◀── typical DEVELOPMENT threshold
  silly   (6)  ███

  level: 'info' configured
    ──▶ error, warn, info   PASS (shown)
    ──▶ http, verbose, debug, silly   BLOCKED (hidden)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Log Level | Severity ranking for log messages | Log messages की severity ranking |
| Threshold | Configured minimum severity to display | Display के लिए minimum severity |
| npm levels | Winston's default level set | Winston का default level set |
| syslog levels | Alternate level set (emerg..debug) | दूसरा level set (emerg..debug) |
| Alert Fatigue | Ignoring alerts due to overuse | ज़्यादा alerts से ignore करने की आदत |
| Per-transport level | Different level filter per destination | हर destination का अलग level filter |

---

## ⚡ 3-Line Summary
**English:**
1. Winston's npm levels rank severity numerically — `error(0)` to `silly(6)` — lower number means more severe and always shown when the threshold is set to a less severe level.
2. Set `level` based on environment: `debug` in dev for full visibility, `info`/`warn` in production to cut noise while keeping real problems visible.
3. Use the level that matches actual severity consistently — misusing `warn`/`error` causes alert fatigue or missed real failures.

**Hindi:**
1. Winston के npm levels severity को numerically rank करते हैं — `error(0)` से `silly(6)` तक — कम number ज़्यादा severe होता है।
2. Environment के हिसाब से `level` set करो: dev में `debug` पूरी visibility के लिए, production में `info`/`warn` noise कम करने के लिए।
3. Actual severity के हिसाब से सही level use करो consistently — गलत इस्तेमाल से alert fatigue या असली failures miss हो सकते हैं।

---

## ➡️ Next Topic
**253. Centralized Logging (ELK)** — ELK/EFK stack से multiple microservices के logs को एक जगह searchable बनाना।
