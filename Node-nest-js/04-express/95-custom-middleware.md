# 95. Custom Middleware
# हिंदी में: Custom Middleware

---

## 🔵 Simple Definition (English)
**Custom middleware** are middleware functions you write yourself for app-specific logic — things no npm package covers exactly the way your business needs. Examples: attaching tenant info, request-ID tracing, feature flags, role-based access checks, request/response transformation specific to your domain.

## 🔵 सरल परिभाषा (Hindi)
**Custom middleware** वो middleware functions हैं जो आप खुद अपने app-specific logic के लिए लिखते हैं — वो चीज़ें जो कोई npm package exactly आपके business की तरह cover नहीं करता। Examples: tenant info attach करना, request-ID tracing, feature flags, role-based access checks, domain-specific transformation।

---

## 🔴 Problem it Solves
```
BUSINESS-SPECIFIC LOGIC that no generic package handles:
  - "Attach the logged-in restaurant's subscription tier to every request"
  - "Reject requests from cities not yet launched (feature flag by geography)"
  - "Log slow requests (>500ms) to a special alert channel"
  - "Inject a correlation ID that ties together logs across microservices"

  None of these are generic enough for npm — cors/helmet/morgan can't know
  your specific business rules. You write a small, focused function instead.

  const attachTenant = (req, res, next) => {
    req.tenant = resolveTenantFromSubdomain(req.hostname);
    next();
  };
  app.use(attachTenant);
```

## 🔴 यह क्यों बना? (Hindi)
Business-specific logic (tenant resolution, feature flags, correlation IDs, domain rules) को कोई generic npm package cover नहीं कर सकता — ये हर app के लिए अलग होते हैं। इसलिए Express ने developers को अपना custom middleware लिखने की पूरी flexibility दी, जो exact same `(req, res, next)` contract follow करता है जैसे built-in/third-party middleware।

---

## 🟢 How it Works — Step by Step

Step 1 → Define a plain function with signature `(req, res, next)` (or `(err, req, res, next)` for error handlers)
Step 2 → Inside, read from `req`, optionally mutate `req`/`res`, perform checks or side effects
Step 3 → Decide: call `next()` to continue, call `next(err)` to signal an error, or send a terminal response to end the chain
Step 4 → Register with `app.use()` (global), `app.use(path, fn)` (path-scoped), or inline in a specific route (`app.get(path, customMw, handler)`)
Step 5 → For reusable parameterized middleware, write a factory function that returns the actual middleware (closures capture config)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `(req, res, next)` signature वाला एक plain function define करो
Step 2 → अंदर `req` से पढ़ो, जरूरत पड़े तो `req`/`res` modify करो, checks/side effects करो
Step 3 → Decide करो: `next()` से continue, `next(err)` से error signal, या terminal response से chain खत्म
Step 4 → `app.use()` (global), `app.use(path, fn)` (path-scoped), या specific route में inline register करो
Step 5 → Reusable parameterized middleware के लिए factory function लिखो जो closure में config capture करके actual middleware return करे

---

## 🟡 Real World Example
**Zomato multi-city feature flags:** A custom middleware checks `req.headers['x-city']` against a list of cities where "live order tracking" is enabled. If the city isn't in the rollout list, it attaches `req.features = { liveTracking: false }` so downstream handlers can conditionally respond. This logic is entirely Zomato-specific — no generic package could know Zomato's rollout schedule.

## 🟡 Real Example Hindi mein
**Zomato multi-city feature flags:** एक custom middleware `req.headers['x-city']` को उन cities की list से check करता है जहाँ "live order tracking" enabled है। अगर city rollout list में नहीं है, तो `req.features = { liveTracking: false }` attach करता है। यह logic पूरी तरह Zomato-specific है — कोई generic package यह नहीं जान सकता।

---

## 💻 Code Example — Basic

```javascript
// custom-middleware-basic.js
const express = require('express');
const app = express();

// Simple custom middleware — logs request timing
const requestTimer = (req, res, next) => {
  req.startTime = Date.now();   // attach custom property
  next();                        // continue the chain
};

// Custom middleware that checks a custom header
const requireApiVersion = (req, res, next) => {
  const version = req.headers['x-api-version'];
  if (!version) {
    return res.status(400).json({ error: 'X-API-Version header is required' });
  }
  req.apiVersion = version;
  next();
};

app.use(requestTimer);
app.use(requireApiVersion);

app.get('/api/data', (req, res) => {
  const elapsed = Date.now() - req.startTime;
  res.json({ apiVersion: req.apiVersion, elapsedMs: elapsed });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// custom-middleware-advanced.js — factory middleware, role-based access, feature flags

const express = require('express');
const app = express();
app.use(express.json());

// FACTORY PATTERN: middleware that takes config and returns the actual middleware
// Useful for reusable, parameterized logic
const requireRole = (...allowedRoles) => {
  return (req, res, next) => {
    const userRole = req.headers['x-user-role'];  // in real app, comes from JWT
    if (!allowedRoles.includes(userRole)) {
      return res.status(403).json({
        error: `Access denied. Required role: ${allowedRoles.join(' or ')}`,
      });
    }
    next();
  };
};

// Custom middleware: tenant resolution from subdomain
const resolveTenant = (req, res, next) => {
  const subdomain = req.hostname.split('.')[0];  // e.g., 'acme.myapp.com' → 'acme'
  const knownTenants = { acme: { id: 1, plan: 'pro' }, globex: { id: 2, plan: 'free' } };

  req.tenant = knownTenants[subdomain];
  if (!req.tenant) {
    return res.status(404).json({ error: 'Unknown tenant' });
  }
  next();
};

// Custom middleware: feature flag gate
const featureFlag = (flagName) => (req, res, next) => {
  const enabledFlags = req.tenant?.plan === 'pro'
    ? ['liveTracking', 'analytics', 'exportCSV']
    : ['liveTracking'];

  if (!enabledFlags.includes(flagName)) {
    return res.status(402).json({ error: `Feature "${flagName}" not available on your plan` });
  }
  next();
};

// Custom middleware: slow-request alerting (attach at the end via res.on('finish'))
const slowRequestLogger = (req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (duration > 500) {
      console.warn(`SLOW REQUEST: ${req.method} ${req.path} took ${duration}ms`);
    }
  });
  next();
};

app.use(slowRequestLogger);
app.use(resolveTenant);

app.get('/api/analytics', featureFlag('analytics'), (req, res) => {
  res.json({ tenant: req.tenant, analytics: { visits: 1000 } });
});

app.delete('/api/admin/users/:id', requireRole('admin', 'superadmin'), (req, res) => {
  res.json({ deleted: req.params.id });
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// Real-world composition of custom middleware for a Flipkart-style seller API
const express = require('express');
const app = express();
app.use(express.json());

const requireAuth = (req, res, next) => {
  if (!req.headers.authorization) return res.status(401).json({ error: 'Unauthorized' });
  req.sellerId = 'seller_123';   // decoded from JWT in real app
  next();
};

const requireVerifiedSeller = (req, res, next) => {
  const isVerified = true;  // would check DB
  if (!isVerified) return res.status(403).json({ error: 'Seller not verified' });
  next();
};

app.post('/api/products', requireAuth, requireVerifiedSeller, (req, res) => {
  res.status(201).json({ created: true, sellerId: req.sellerId, product: req.body });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Custom middleware with side effects that run on EVERY request unintentionally
```javascript
// WRONG: expensive DB call runs on every single request, even unrelated ones
app.use(async (req, res, next) => {
  req.allUsers = await db.find('users', {});  // ❌ runs globally, wasteful
  next();
});

// CORRECT: scope expensive middleware to only the routes that need it
app.get('/api/admin/users', fetchAllUsers, handler);  // only here
```

❌ **Mistake 2:** Factory middleware that forgets to actually return a function
```javascript
// WRONG: calling requireRole() returns the WRONG thing (an object/undefined), not a function
const requireRole = (role) => {
  if (role === 'admin') { /* missing return of the actual (req,res,next) fn */ }
};
app.get('/admin', requireRole('admin'), handler);  // ❌ Express error: not a function

// CORRECT: always return the (req, res, next) function from the factory
const requireRole = (role) => (req, res, next) => {
  // check logic here
  next();
};
```

---

## 🧠 Tricky Interview Question

```javascript
const makeCounter = () => {
  let count = 0;
  return (req, res, next) => {
    count++;
    req.requestNumber = count;
    next();
  };
};

const app = require('express')();
app.use(makeCounter());   // called ONCE here

app.get('/', (req, res) => res.json({ n: req.requestNumber }));
app.listen(3000);
// If you call GET / three times, what sequence of n values do you get?
```
Answer: `1`, `2`, `3` — the counter correctly increments across requests. This works because `makeCounter()` is called ONCE at startup, creating ONE closure over `count`. The returned middleware function is registered once, but Express invokes that SAME function instance for every incoming request — so `count` persists in memory between requests (it's a classic JS closure, shared across calls). This is different from creating a NEW middleware instance per request (which would reset `count` to 0 every time) — a subtle but important distinction interviewers like to probe.

---

## ⚫ Interview Questions + Answers

Q1: What's the "factory middleware" pattern, and why is it useful?
A1: It's a function that takes CONFIGURATION arguments and RETURNS the actual `(req, res, next)` middleware function, using a closure to remember the config. Example: `requireRole('admin')` returns a middleware tailored to check for the 'admin' role specifically. This lets you write ONE reusable middleware implementation and parameterize it per-route instead of duplicating near-identical logic.

Q2: How do you share data computed in one custom middleware with a LATER middleware or route handler?
A2: Attach it as a property on the `req` object (e.g., `req.tenant = {...}`, `req.user = {...}`). Since `req` is passed by reference through the entire chain for that SINGLE request, any middleware/handler later in the chain can read those properties. This is the standard Express pattern for passing computed context downstream.

Q3: What's the risk of placing an expensive custom middleware (e.g., a DB call) with `app.use()` globally?
A3: It runs on EVERY request to the server, even for routes that don't need that data — wasting DB connections/CPU and adding latency to unrelated endpoints (like health checks or static assets). Best practice: scope expensive middleware to only the specific routes/routers that actually need it, using `router.use()` on a sub-router or passing it directly as a route-specific middleware argument.

Q4: Can custom middleware be async? What do you need to be careful about?
A4: Yes, middleware functions can be `async` — Express just calls them, it doesn't care about the return value, only whether `next()` was called. The catch: if an async middleware throws (its promise rejects) without being wrapped in try/catch, Express does NOT automatically catch it — the request will hang. You must wrap the logic in try/catch and call `next(err)` on failure, or use a helper wrapper utility.

Q5: How would you write custom middleware that only applies to a SUBSET of routes without repeating it in every `app.get()` call?
A5: Use `app.use(path, middleware)` to scope it by a path PREFIX (e.g., `app.use('/api/admin', requireAdmin)` applies to all routes under `/api/admin/*`), or mount it on a dedicated `express.Router()` instance via `router.use(middleware)` and only use that router for the relevant feature's routes. Both avoid repeating the middleware reference on every individual route definition.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Logic is specific to your business domain (tenant resolution, feature flags, role checks, custom tracing)
- You need reusable, parameterized checks across multiple routes (factory middleware pattern)

❌ Avoid when:
- A well-maintained npm package already solves the exact generic problem (don't reinvent CORS/security headers/logging)
- The logic is truly one-off and only used in a single route — sometimes inlining it directly in the handler is clearer than extracting unnecessary middleware

---

## 📊 Visual Diagram
```
  CUSTOM MIDDLEWARE PATTERNS
  ─────────────────────────────────────────
  Simple middleware:
    (req, res, next) => { ...; next(); }

  Factory middleware (parameterized, reusable):
    requireRole('admin')
         │
         ▼
    returns → (req, res, next) => { check role==='admin'; next(); }
         │
         ▼
    app.get('/admin', requireRole('admin'), handler)

  Shared state across chain (via req mutation):
    resolveTenant → req.tenant = {...}
         │
         ▼
    featureFlag('analytics') reads req.tenant → allow/deny
         │
         ▼
    handler reads req.tenant → business logic
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom middleware | App-specific, self-written middleware | App-specific, खुद लिखा middleware |
| Factory middleware | Function returning a configured middleware | Configured middleware return करने वाला function |
| Closure | Captured variables persisting across calls | Calls के बीच persist होने वाले captured variables |
| Scoped middleware | Applied only to specific routes/paths | सिर्फ specific routes/paths पर apply |

---

## ⚡ 3-Line Summary
English: 1. Custom middleware implements app-specific logic (tenant resolution, feature flags, role checks) that no generic package covers. 2. The factory pattern (`fn(config) => (req,res,next) => {...}`) lets you reuse parameterized middleware across routes. 3. Scope expensive custom middleware to only the routes that need it, not globally, to avoid wasted work.
Hindi: 1. Custom middleware app-specific logic implement करता है जो कोई generic package cover नहीं करता। 2. Factory pattern से parameterized middleware कई routes में reuse हो सकता है। 3. Expensive custom middleware को सिर्फ जरूरी routes पर scope करो, globally नहीं।

---

## ➡️ Next Topic
**96. Error Handling Middleware** — The 4-parameter error middleware pattern and centralized error handling strategy.
