# 91. Middleware in Express.js
# हिंदी में: Middleware — Request और Response के बीच का Layer

---

## 🔵 Simple Definition (English)
**Middleware** is a function that runs between an incoming request and the final route handler. It has access to `req`, `res`, and `next`. Calling `next()` passes control to the next middleware; not calling it ends the chain. Middleware can: modify request/response objects, log, authenticate, validate, handle errors, or short-circuit the request (send a response early). Express apps are essentially a chain of middleware functions.

Signature: `function(req, res, next) {}`

## 🔵 सरल परिभाषा (Hindi)
**Middleware** एक function है जो incoming request और final route handler के बीच run होता है। इसके पास `req`, `res`, और `next` होता है। `next()` call करने से अगले middleware को control जाता है; नहीं call किया तो chain रुक जाती है। Middleware कर सकता है: req/res modify, logging, authentication, validation, error handling, या early response भेजना। Express app basically middleware functions की chain है।

---

## 🔴 Problem it Solves
```
WITHOUT MIDDLEWARE:
  Every route must repeat the same code:

  app.get('/users', (req, res) => {
    // Check auth token — 10 lines
    // Parse and validate JSON — 5 lines
    // Log request — 3 lines
    const users = await User.find();
    res.json(users);
  });

  app.post('/users', (req, res) => {
    // Check auth token — 10 lines (SAME AS ABOVE!)
    // Parse and validate JSON — 5 lines (SAME!)
    // Log request — 3 lines (SAME!)
    const user = await User.create(req.body);
    res.json(user);
  });
  → 500 routes × repeated code = nightmare

WITH MIDDLEWARE:
  app.use(parseJSON);     // runs for ALL routes
  app.use(logRequest);    // runs for ALL routes
  app.use(authenticate);  // runs for ALL routes

  app.get('/users', (req, res) => {
    // JUST the business logic! Auth + logging already done
    const users = await User.find();
    res.json(users);
  });
```

---

## 🟢 Types of Middleware

```
MIDDLEWARE TYPES:
──────────────────────────────────────────────────────────

1. APPLICATION-LEVEL   → app.use() or app.METHOD()
   app.use(cors())
   app.use('/api', rateLimiter)

2. ROUTER-LEVEL        → router.use()
   const router = express.Router();
   router.use(authenticate);

3. ERROR-HANDLING      → 4 parameters: (err, req, res, next)
   app.use((err, req, res, next) => {
     res.status(500).json({ error: err.message });
   });

4. BUILT-IN            → express.json(), express.static()
   app.use(express.json());
   app.use(express.static('public'));

5. THIRD-PARTY         → cors, morgan, helmet, multer
   app.use(cors());
   app.use(morgan('dev'));
```

---

## 🟡 Real World Example
**Razorpay API:** Every API request needs: (1) Parse JSON body, (2) Log request for audit trail, (3) Verify API key / JWT, (4) Check rate limit (max 1000 req/min per key), (5) Validate request body schema. With middleware: each concern is a separate function in the chain. If auth fails → middleware sends 401 and stops chain (never reaches route handler). If rate limit exceeded → 429 response. Route handler only runs when all middleware passes — clean separation of concerns.

---

## 💻 Code Example — Basic

```javascript
// middleware-basics.js
const express = require('express');
const app = express();

// ─── 1. APPLICATION-LEVEL MIDDLEWARE ──────────────────────────────────────────
// Built-in: parses JSON request body into req.body
app.use(express.json());

// Built-in: parses URL-encoded form data
app.use(express.urlencoded({ extended: true }));

// ─── 2. CUSTOM MIDDLEWARE — request logger ────────────────────────────────────
const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  // Log when response finishes (res.on('finish'))
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.originalUrl} ${res.statusCode} ${duration}ms`);
    // Output: [2024-01-15T10:30:00] GET /api/users 200 45ms
  });

  next();  // MUST call next() or request hangs!
};
app.use(requestLogger);

// ─── 3. CUSTOM MIDDLEWARE — authentication ────────────────────────────────────
const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({  // short-circuit: no next() call
      error: 'Missing or invalid Authorization header',
    });
  }

  const token = authHeader.split(' ')[1];  // "Bearer <token>"

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;  // attach user data to req for later middleware/routes
    next();              // all good → proceed to route handler
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
};

// ─── 4. ROUTE-SPECIFIC MIDDLEWARE ────────────────────────────────────────────
// Middleware only runs for specific routes/methods
app.get('/public', (req, res) => {
  res.json({ message: 'No auth needed' });  // no authenticate middleware
});

app.get('/private', authenticate, (req, res) => {
  // authenticate runs first — if it calls next(), we reach here
  res.json({ message: `Hello, ${req.user.email}` });
});

// ─── 5. MIDDLEWARE CHAIN ──────────────────────────────────────────────────────
const validateAge = (req, res, next) => {
  const { age } = req.body;
  if (!age || age < 18) {
    return res.status(400).json({ error: 'Must be 18 or older' });
  }
  next();
};

const validateEmail = (req, res, next) => {
  const { email } = req.body;
  if (!email || !email.includes('@')) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  next();
};

// Multiple middleware in array — runs in order
app.post('/register', [validateAge, validateEmail], (req, res) => {
  // Reaches here only if both validations pass
  res.json({ message: 'Registered!' });
});

// ─── 6. ERROR-HANDLING MIDDLEWARE (4 params — MUST be last!) ─────────────────
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err.message);

  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    error: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  });
});

app.listen(3000, () => console.log('Server running'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-middleware.js — Production-ready middleware setup

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');

const app = express();

// ─── 1. SECURITY MIDDLEWARE (first!) ──────────────────────────────────────────
// helmet: sets 15+ security HTTP headers
app.use(helmet());
// Sets: X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security, etc.

// CORS: control which origins can access the API
app.use(cors({
  origin: (origin, callback) => {
    const allowed = [
      'https://myapp.com',
      'https://admin.myapp.com',
      process.env.NODE_ENV === 'development' ? 'http://localhost:3000' : null,
    ].filter(Boolean);

    if (!origin || allowed.includes(origin)) {
      callback(null, true);   // allow
    } else {
      callback(new Error('CORS not allowed'));  // block
    }
  },
  credentials: true,   // allow cookies in cross-origin requests
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
}));

// ─── 2. RATE LIMITING ────────────────────────────────────────────────────────
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 1000,                   // 1000 requests per window per IP
  standardHeaders: true,       // Return rate limit info in `RateLimit-*` headers
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later' },
});
app.use('/api', globalLimiter);

// Stricter limiter for auth endpoints (prevent brute force)
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,  // only 10 login attempts per 15 min
  skipSuccessfulRequests: true,  // don't count successful logins
  message: { error: 'Too many login attempts' },
});

// ─── 3. BODY PARSING ─────────────────────────────────────────────────────────
app.use(express.json({ limit: '10mb' }));  // reject bodies > 10MB
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// ─── 4. REQUEST LOGGING ──────────────────────────────────────────────────────
if (process.env.NODE_ENV !== 'test') {
  app.use(morgan('combined'));  // Apache-style logs in production
  // morgan('dev') for development (colored output)
}

// ─── 5. CUSTOM: Request ID (trace requests through logs) ─────────────────────
const { v4: uuidv4 } = require('uuid');
app.use((req, res, next) => {
  req.requestId = req.headers['x-request-id'] || uuidv4();
  res.setHeader('x-request-id', req.requestId);  // echo back to client
  next();
});

// ─── 6. ROUTES ───────────────────────────────────────────────────────────────
const authRouter = require('./routes/auth');
const userRouter = require('./routes/users');

app.use('/api/auth', authLimiter, authRouter);  // auth limiter only for auth routes
app.use('/api/users', authenticate, userRouter);  // auth required for all user routes

// ─── 7. 404 HANDLER (after all routes) ───────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({
    error: `Cannot ${req.method} ${req.path}`,
    requestId: req.requestId,
  });
});

// ─── 8. GLOBAL ERROR HANDLER (last middleware, 4 params) ─────────────────────
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;  // vs programming errors (bugs)
  }
}

app.use((err, req, res, next) => {
  err.statusCode = err.statusCode || 500;

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const errors = Object.values(err.errors).map(e => e.message);
    return res.status(400).json({ error: 'Validation failed', details: errors });
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({ error: 'Invalid token' });
  }
  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({ error: 'Token expired' });
  }

  // Duplicate key (MongoDB/MySQL)
  if (err.code === 11000 || err.code === 'ER_DUP_ENTRY') {
    return res.status(409).json({ error: 'Resource already exists' });
  }

  // Operational errors (our AppError) — safe to expose message
  if (err.isOperational) {
    return res.status(err.statusCode).json({ error: err.message, requestId: req.requestId });
  }

  // Programming errors (bugs) — don't expose details
  console.error('PROGRAMMING ERROR:', err);
  return res.status(500).json({ error: 'Something went wrong', requestId: req.requestId });
});

module.exports = { app, AppError };
```

---

## 🟠 Express.js Integration

```javascript
// Express middleware execution flow
const express = require('express');
const app = express();

// Visualizing the middleware chain:

//  Request: POST /api/users
//     │
//     ▼
//  app.use(helmet)            → adds security headers
//     │
//     ▼
//  app.use(cors)              → handles CORS preflight
//     │
//     ▼
//  app.use(express.json)      → parses body into req.body
//     │
//     ▼
//  app.use(rateLimiter)       → checks request count
//     │
//     ▼
//  app.use(requestLogger)     → logs request
//     │
//     ▼
//  app.post('/api/users',
//    authenticate,            → verifies JWT
//    validateBody,            → validates schema
//    (req, res) => {          → route handler (FINALLY!)
//      createUser(req.body)
//    }
//  )
//     │
//     ▼
//  app.use(errorHandler)     → catches any thrown errors

// KEY INSIGHT: app.use(middleware) with no path = runs for ALL routes
// app.use('/api', middleware) = runs for routes starting with /api
// app.get('/users', middleware, handler) = runs for only GET /users

// Router-level middleware (modular routes):
const router = express.Router();

router.use((req, res, next) => {
  // Runs for all routes in this router
  console.log('Router middleware:', req.path);
  next();
});

router.get('/', (req, res) => res.json({ users: [] }));
router.post('/', (req, res) => res.json({ created: true }));

app.use('/api/users', router);
// GET /api/users → router middleware + GET '/' handler
// POST /api/users → router middleware + POST '/' handler
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `next()` — request hangs
```javascript
// WRONG: middleware that forgets to call next()
app.use((req, res, next) => {
  console.log('Logged!');
  // next() not called → request hangs forever, client times out
});

// CORRECT:
app.use((req, res, next) => {
  console.log('Logged!');
  next();  // ALWAYS call next() unless you send a response
});
```

❌ **Mistake 2:** Error handler with wrong signature
```javascript
// WRONG: Error handler with 3 params — Express treats it as regular middleware!
app.use((err, res, next) => {  // ← only 3 params!
  res.status(500).json({ error: err.message });
});
// Express requires EXACTLY 4 params for error handlers

// CORRECT:
app.use((err, req, res, next) => {  // ← 4 params (err, req, res, next)
  res.status(500).json({ error: err.message });
});
```

❌ **Mistake 3:** Middleware order wrong
```javascript
// WRONG: Route defined before body parsing middleware
app.post('/data', (req, res) => {
  console.log(req.body);  // undefined! body not parsed yet
  res.json({ ok: true });
});
app.use(express.json());  // too late!

// CORRECT: Body parsing before routes
app.use(express.json());  // FIRST
app.post('/data', (req, res) => {
  console.log(req.body);  // { key: 'value' } ✅
  res.json({ ok: true });
});
```

---

## 🧠 Tricky Interview Question

**Q: What happens if you call `next()` AND `res.json()` in a middleware?**

```javascript
app.use((req, res, next) => {
  next();               // pass to next middleware
  res.json({ ok: true }); // also send response
});
```

**Answer:** This causes "Cannot set headers after they are sent to the client" error — because if the next middleware also sends a response, you'd be trying to send two responses. Node.js throws this error. The fix: always `return next()` or `return res.json()`, never both. Pattern: `if (error) return res.status(400).json({...}); next();`

---

## ⚫ Interview Questions + Answers

**Q1: What is middleware in Express.js and what can it do?**
A1: Middleware is a function with `(req, res, next)` signature that runs in the request-response cycle. It can: (1) Execute any code, (2) Modify `req` and `res` objects (add `req.user`, set headers), (3) End the request-response cycle (send a response), (4) Call `next()` to pass control to the next middleware. If `next()` is not called and no response is sent, the request hangs. Common uses: authentication, logging, body parsing, rate limiting, CORS, error handling.

**Q2: What is the difference between `app.use()` and `app.get()`?**
A2: `app.use(path, fn)` — matches ALL HTTP methods (GET, POST, PUT, DELETE, etc.) and path prefix matching (e.g., `/api` matches `/api/users`, `/api/orders`). If no path given, matches all routes. Used for middleware (auth, logging, etc.). `app.get(path, fn)` — matches only GET requests with exact path matching. Used for defining specific routes. Key difference: `app.use('/api', fn)` runs for `GET /api/users`; `app.get('/api', fn)` does NOT run for `GET /api/users` (exact match only).

**Q3: What is the order of middleware execution in Express?**
A3: Middleware runs in the ORDER it's registered with `app.use()`. First-registered = first-executed. This matters: (1) `express.json()` must be before any route that needs `req.body`, (2) `cors()` + `helmet()` should be first for security, (3) Error handler middleware MUST be last (must have 4 params), (4) Logging middleware early so it logs all requests including those that fail auth. Wrong order = subtle bugs (undefined req.body, CORS errors, etc.).

**Q4: How do you create a custom authentication middleware?**
A4: Extract token from `Authorization: Bearer <token>` header, verify with `jwt.verify(token, secret)`. If valid: attach decoded user to `req.user = decoded`, call `next()`. If invalid/missing: send `res.status(401).json({ error: '...' })` WITHOUT calling `next()`. Then add to protected routes: `app.get('/protected', authenticate, handler)` or protect all routes in a router with `router.use(authenticate)`. Never call both `next()` and `res.json()` — one or the other.

**Q5: What is the error handling middleware signature and why does it need 4 params?**
A5: Error handling middleware: `(err, req, res, next)` — exactly 4 parameters. The first param `err` is the Error object passed from `next(err)` or thrown in async code (with express-async-errors). Express specifically checks for 4-param functions to identify error handlers. With only 3 params, Express treats it as regular middleware and skips it when errors occur. Must be registered LAST (`app.use` after all routes). For async errors: use `try/catch` + `next(err)`, or `express-async-errors` package which auto-wraps async route handlers.

---

## 📊 Visual Diagram

```
MIDDLEWARE CHAIN:
────────────────────────────────────────────────────────────────

  HTTP Request
  POST /api/users
  Authorization: Bearer <token>
  Body: { name: "Rahul", email: "rahul@example.com" }
       │
       ▼
  ┌─────────────────────────────────────────────────────────┐
  │  1. helmet()                                            │
  │     → Sets security headers                             │
  │     → Calls next()                                      │
  └──────────────────────────┬──────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │  2. cors()                                              │
  │     → Checks Origin header                              │
  │     → Allowed? next() : 403 response (chain stops!)     │
  └──────────────────────────┬──────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │  3. express.json()                                      │
  │     → Parses body → req.body = { name, email }          │
  │     → Calls next()                                      │
  └──────────────────────────┬──────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │  4. rateLimiter()                                       │
  │     → Checks request count                              │
  │     → Under limit? next() : 429 response (chain stops!) │
  └──────────────────────────┬──────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │  5. authenticate()                                      │
  │     → Verifies JWT → req.user = { id, email, role }     │
  │     → Valid? next() : 401 response (chain stops!)        │
  └──────────────────────────┬──────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │  6. ROUTE HANDLER: POST /api/users                      │
  │     → Business logic runs here                          │
  │     → Sends response                                    │
  └─────────────────────────────────────────────────────────┘
           If any middleware throws → error handler runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Middleware | Function in req-res pipeline | Request-Response pipeline का function |
| `next()` | Pass control to next middleware | अगले middleware को control दो |
| Error middleware | 4-param middleware for errors | Error handle करने का middleware |
| `req.body` | Parsed request body | Parse किया हुआ request body |
| `req.user` | Custom prop added by auth middleware | Auth middleware का attach किया user |
| Short-circuit | Send response early, skip rest | Early response, chain आगे नहीं |
| Router-level | Middleware for a specific router | Specific router के लिए middleware |

---

## ⚡ 3-Line Summary
**English:**
1. Middleware is a function `(req, res, next)` in the request pipeline — call `next()` to continue the chain, or `res.json()` to short-circuit; order matters (body parsing must be before routes).
2. Types: application-level (`app.use`), route-specific (array in route), error-handling (4-param, registered last), built-in (`express.json`, `express.static`), third-party (`cors`, `helmet`, `morgan`).
3. Production pattern: security (helmet+cors) → body parsing → rate limiting → logging → auth → routes → 404 handler → error handler.

**Hindi:**
1. Middleware function `(req, res, next)` है — `next()` से chain continue, `res.json()` से short-circuit; order matter करता है।
2. Types: application-level, route-specific, error-handling (4 params, last), built-in, third-party।
3. Production order: security → body parsing → rate limiting → logging → auth → routes → 404 → error handler।

---

## ➡️ Next Topic
**92. Express Router** — Modular route organization with `express.Router()`।
