# 85. Express vs Fastify vs Koa vs Hapi
# हिंदी में: Express vs Fastify vs Koa vs Hapi — तुलना

---

## 🔵 Simple Definition (English)
These are the four most commonly compared Node.js web frameworks. **Express** is the oldest, most minimal, and most widely adopted. **Fastify** focuses on raw performance and schema-based validation. **Koa** (by the same team as Express) uses `async/await`-first middleware with no callbacks, aiming for a smaller, more modern core. **Hapi** is configuration-driven with built-in validation, caching, and auth, favoring convention over heavy middleware chains.

## 🔵 सरल परिभाषा (Hindi)
ये चार सबसे ज्यादा compare किए जाने वाले Node.js web frameworks हैं। **Express** सबसे पुराना, minimal, और widely adopted है। **Fastify** raw performance और schema-based validation पर focus करता है। **Koa** (Express टीम का ही) `async/await`-first middleware use करता है, callbacks नहीं। **Hapi** configuration-driven है, built-in validation, caching, auth के साथ।

---

## 🔴 Problem it Solves
```
WHY MULTIPLE FRAMEWORKS EXIST:
  Express (2010) was revolutionary but has architectural limitations
  by TODAY's standards:
  - Callback-based middleware signature (req, res, next) predates
    widespread async/await adoption
  - No built-in request/response validation or serialization
  - Middleware overhead can add latency at very high request rates

  NEWER FRAMEWORKS ADDRESS SPECIFIC GAPS:
  Fastify  → built for SPEED: schema-based JSON serialization/validation
             compiled ahead-of-time, lower per-request overhead
  Koa      → built for MODERN JS: async/await-native middleware (no
             next() callback soup), smaller core, you add what you need
  Hapi     → built for CONFIGURATION/ENTERPRISE: declarative route
             config with built-in validation (Joi), caching, auth
             plugins, less reliance on third-party middleware
```

## 🔴 यह क्यों बना? (Hindi)
```
Express (2010) revolutionary था पर आज के standards से limitations हैं:
callback-based middleware, कोई built-in validation, high load पर overhead
Fastify speed के लिए बना (schema-based validation, less overhead)
Koa modern async/await middleware के लिए बना (no callback soup)
Hapi configuration/enterprise use-case के लिए बना (built-in validation, auth)
```

---

## 🟢 How it Works — Step by Step

```
KEY ARCHITECTURAL DIFFERENCES:

EXPRESS:
  Middleware signature: (req, res, next)
  Routing: app.get(path, handler)
  Validation: NOT built-in (use express-validator, Joi, Zod manually)
  Philosophy: minimal core, add everything via middleware ecosystem

FASTIFY:
  Middleware/hooks: (request, reply) with lifecycle hooks (onRequest,
  preHandler, etc.)
  Routing: fastify.get(path, { schema }, handler) — SCHEMA is central
  Validation: BUILT-IN via JSON Schema — also used to compile a FAST
  serializer for responses (major source of its speed advantage)
  Philosophy: performance + plugin-based extensibility

KOA:
  Middleware signature: async (ctx, next) => { await next(); ... }
  Routing: NOT built-in (use koa-router or similar)
  Validation: NOT built-in
  Philosophy: tiny core (~550 lines), async/await-first, "unopinionated
  by design, compose exactly what you need"

HAPI:
  Route definition: server.route({ method, path, handler, options:
  { validate: {...} } })
  Validation: BUILT-IN via Joi, deeply integrated
  Philosophy: configuration over code, built-in auth strategies,
  caching, less dependency on external middleware packages
```

## 🟢 कैसे काम करता है? (Hindi)
```
Express: (req, res, next) middleware, कोई built-in validation नहीं
Fastify: (request, reply), JSON Schema से validation + fast serialization
Koa: async (ctx, next) middleware, tiny core, routing built-in नहीं
Hapi: configuration-driven routes, built-in Joi validation, auth, caching
```

---

## 🟡 Real World Example
**Flipkart's internal tooling choice spectrum:** A customer-facing checkout API handling millions of requests/day might choose **Fastify** for its lower latency overhead and built-in JSON schema validation (reducing both bugs and response-serialization CPU cost). An internal admin dashboard backend, where developer velocity matters more than raw throughput, sticks with **Express** for its huge ecosystem (easier to find a middleware for anything) and team familiarity. A team that heavily uses async/await and wants a leaner, more "modern JS" feel without Express's legacy callback patterns might pick **Koa**. An enterprise team wanting strict, declarative input validation and built-in auth strategies out of the box (less third-party dependency risk) might pick **Hapi**.

## 🟡 Real Example Hindi mein
**Flipkart-style choices:** Customer-facing checkout API (millions requests/day) के लिए **Fastify** चुना जा सकता है (low overhead, built-in validation)। Internal admin dashboard के लिए **Express** (huge ecosystem, team familiarity)। Modern async/await feel के लिए **Koa**। Enterprise strict validation/auth के लिए **Hapi**।

---

## 💻 Code Example — Basic

```javascript
// comparison-basic.js — the SAME simple route in all four frameworks
// (illustrative — install each package separately to run individually)

// ─── EXPRESS ──────────────────────────────────────────────────────────────
const express = require('express');
const expressApp = express();
expressApp.get('/users/:id', (req, res) => {
  res.json({ id: req.params.id, framework: 'express' });
});
// expressApp.listen(3000);

// ─── FASTIFY ──────────────────────────────────────────────────────────────
const fastify = require('fastify')();
fastify.get('/users/:id', {
  schema: {
    // Schema-based validation AND fast response serialization
    response: { 200: { type: 'object', properties: { id: { type: 'string' } } } },
  },
}, async (request, reply) => {
  return { id: request.params.id, framework: 'fastify' };
});
// fastify.listen({ port: 3001 });

// ─── KOA ──────────────────────────────────────────────────────────────────
const Koa = require('koa');
const Router = require('@koa/router');
const koaApp = new Koa();
const router = new Router();
router.get('/users/:id', async (ctx) => {
  ctx.body = { id: ctx.params.id, framework: 'koa' };  // no res.json needed
});
koaApp.use(router.routes());
// koaApp.listen(3002);

// ─── HAPI ─────────────────────────────────────────────────────────────────
const Hapi = require('@hapi/hapi');
async function startHapi() {
  const hapiServer = Hapi.server({ port: 3003 });
  hapiServer.route({
    method: 'GET',
    path: '/users/{id}',
    handler: (request, h) => {
      return { id: request.params.id, framework: 'hapi' };
    },
  });
  // await hapiServer.start();
}
```

## 💻 Code Example — Advanced

```javascript
// comparison-advanced.js — validation approach comparison (the biggest
// practical differentiator between these frameworks)

// ─── EXPRESS: manual validation (needs a library, no built-in schema) ──────
const express = require('express');
const { z } = require('zod');  // example: using Zod for validation
const expressApp = express();
expressApp.use(express.json());

const createUserSchema = z.object({ name: z.string().min(1), age: z.number().min(18) });

expressApp.post('/users', (req, res) => {
  const result = createUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ error: result.error.issues });
  }
  res.status(201).json({ created: result.data });
});

// ─── FASTIFY: validation is BUILT INTO the route definition (JSON Schema) ──
const fastify = require('fastify')();

fastify.post('/users', {
  schema: {
    body: {
      type: 'object',
      required: ['name', 'age'],
      properties: {
        name: { type: 'string', minLength: 1 },
        age: { type: 'number', minimum: 18 },
      },
    },
  },
}, async (request, reply) => {
  // If validation fails, Fastify AUTOMATICALLY returns a 400 — no manual check!
  reply.code(201).send({ created: request.body });
});

// ─── HAPI: validation via Joi, built into route options ────────────────────
const Hapi = require('@hapi/hapi');
const Joi = require('joi');

async function setupHapiValidation() {
  const server = Hapi.server({ port: 3003 });
  server.route({
    method: 'POST',
    path: '/users',
    options: {
      validate: {
        payload: Joi.object({
          name: Joi.string().min(1).required(),
          age: Joi.number().min(18).required(),
        }),
      },
    },
    handler: (request, h) => {
      // Hapi AUTOMATICALLY returns 400 Bad Request if validation fails
      return h.response({ created: request.payload }).code(201);
    },
  });
}

// KEY TAKEAWAY: Fastify and Hapi have validation as a FIRST-CLASS,
// framework-integrated concept. Express requires you to wire it up
// yourself with middleware (more flexible, but more manual work).
```

---

## 🟠 Express.js Integration

```javascript
// Since Express lacks built-in schema validation/serialization,
// here's the typical production pattern to approximate what
// Fastify/Hapi give you out of the box, using middleware:

const express = require('express');
const { z } = require('zod');
const app = express();
app.use(express.json());

// Reusable validation middleware factory (common Express pattern)
function validateBody(schema) {
  return (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ error: result.error.issues });
    }
    req.body = result.data;  // use the parsed/validated data
    next();
  };
}

const orderSchema = z.object({
  items: z.array(z.object({ productId: z.string(), qty: z.number().positive() })),
  addressId: z.string(),
});

app.post('/orders', validateBody(orderSchema), (req, res) => {
  // req.body is now GUARANTEED to match orderSchema
  res.status(201).json({ order: req.body });
});

app.listen(3000);
// This shows Express's PHILOSOPHY: minimal core + compose exactly
// what you need via middleware, vs Fastify/Hapi's "batteries included"
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Choosing a framework based ONLY on raw benchmark numbers
```javascript
// WRONG reasoning: "Fastify is 2x faster in benchmarks, so we MUST switch"
// Real-world API performance is usually dominated by DATABASE queries,
// network latency, and business logic — NOT framework routing overhead.
// Framework choice should weigh: team familiarity, ecosystem/middleware
// availability, validation needs, and ACTUAL measured bottlenecks in
// YOUR app — not synthetic "hello world" benchmarks.
```

❌ **Mistake 2:** Mixing Express middleware directly into Koa or Fastify expecting it to work
```javascript
// WRONG: Express middleware uses (req, res, next) signature
// Koa middleware uses async (ctx, next) — DIFFERENT signature entirely
// Fastify uses (request, reply) with its own hook system
// You CANNOT drop an `app.use(expressMiddleware)` into Koa/Fastify directly —
// each framework has its own middleware/plugin ecosystem and adapters
// are needed (and not all Express middleware has a direct equivalent)
```

---

## 🧠 Tricky Interview Question

**Q: A team claims "Fastify is always faster than Express for any API." Is this claim accurate?**

**Answer:** Not entirely. Fastify is generally faster in RAW ROUTING + SERIALIZATION benchmarks (its JSON Schema compilation for request/response gives real measurable gains, especially for routes that return deeply-structured objects frequently). BUT: (1) if your app's latency is dominated by database queries, external API calls, or heavy business logic, framework overhead is often a tiny fraction of total response time — switching frameworks won't meaningfully help. (2) Express with well-optimized middleware (minimal middleware count, efficient body-parsing limits) can perform very competitively for typical CRUD APIs. (3) Migration cost (rewriting middleware, retraining the team, losing access to Express-specific packages) often outweighs the raw framework-level speed gain unless you're operating at extreme scale where every millisecond of overhead matters (e.g., ultra-high-throughput, low-latency trading/ad-tech systems).

---

## ⚫ Interview Questions + Answers

**Q1: What are the key differentiators between Express, Fastify, Koa, and Hapi?**
A1: Express — minimal, oldest, huge ecosystem, callback-style `(req, res, next)` middleware, no built-in validation. Fastify — performance-focused, JSON Schema-driven validation AND fast serialization, plugin encapsulation model. Koa — tiny core, async/await-native `(ctx, next)` middleware (no callback soup), routing not built-in. Hapi — configuration-driven routes, built-in Joi validation, auth strategies, and caching, less reliant on third-party middleware.

**Q2: Why is Fastify generally considered faster than Express for raw throughput?**
A2: Fastify compiles JSON Schema definitions AHEAD OF TIME into highly optimized serialization functions, reducing the CPU cost of converting JS objects to JSON responses — a significant overhead source at high request rates. It also has a leaner internal routing/middleware (hooks) implementation with less per-request overhead than Express's more general-purpose middleware chain design.

**Q3: What problem does Koa's `async (ctx, next)` middleware signature solve compared to Express's `(req, res, next)`?**
A3: Express's `next()`-based callback style predates widespread async/await adoption, making error handling in async code awkward (you must manually catch and call `next(err)`). Koa's middleware is `async` by design — you simply `await next()` and can use normal `try/catch` for error handling, resulting in cleaner, more linear-looking async code without callback-style control flow.

**Q4: Why might an enterprise team prefer Hapi over Express?**
A4: Hapi provides built-in, declarative request validation (via Joi), authentication strategies, caching, and route configuration as first-class framework features — reducing the need to pull in and configure many separate third-party packages (each with its own update/security-maintenance burden). This appeals to enterprise teams prioritizing consistency, auditability, and reduced third-party dependency surface area over Express's "assemble it yourself" flexibility.

**Q5: If you were choosing a framework for a brand-new high-throughput public API today, what factors would you weigh beyond raw benchmarks?**
A5: (1) Team's existing familiarity (migration/learning cost). (2) Ecosystem availability for specific needs (auth, ORMs, observability integrations). (3) Built-in validation/serialization needs (Fastify/Hapi reduce boilerplate here). (4) Actual profiling of where YOUR latency comes from (often DB/network, not framework). (5) Long-term maintenance and community/security-update track record. Raw synthetic benchmark numbers should be one input among several, not the deciding factor alone.

---

## 🔷 When to Use + When Not to Use
✅ **Use Express when:** you want the biggest ecosystem, team familiarity, and maximum flexibility.

✅ **Use Fastify when:** raw performance and built-in schema validation/serialization matter (high-throughput APIs).

✅ **Use Koa when:** you want a tiny, modern, async/await-first core and are comfortable composing your own routing/stack.

✅ **Use Hapi when:** you want configuration-driven routes with built-in validation/auth/caching, minimizing third-party dependencies.

❌ **Avoid switching frameworks** purely based on hype or micro-benchmarks without profiling your actual bottleneck first.

---

## 📊 Visual Diagram

```
FRAMEWORK COMPARISON AT A GLANCE:
──────────────────────────────────────────────────────

              Middleware Style    Built-in Validation   Philosophy
EXPRESS    →  (req, res, next)    ❌ (use 3rd party)     Minimal, huge ecosystem
FASTIFY    →  (request, reply)    ✅ JSON Schema          Performance-first
KOA        →  async (ctx, next)   ❌ (use 3rd party)     Tiny, modern core
HAPI       →  config-based route  ✅ Joi                  Convention/enterprise

   SPEED (raw benchmarks, typical ordering):
   Fastify  >  Koa  ≈  Express  >  Hapi
   (actual production impact usually SMALL vs DB/network latency)

   ECOSYSTEM SIZE:
   Express  >>  Koa  >  Fastify  >  Hapi
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSON Schema | Declarative validation/serialization spec | Declarative validation/serialization spec |
| Hooks (Fastify) | Lifecycle extension points | Lifecycle extension points |
| ctx (Koa) | Combined request/response context object | Combined request/response context object |
| Joi (Hapi) | Schema validation library | Schema validation library |
| Plugin encapsulation | Fastify's scoped plugin isolation model | Fastify का scoped plugin isolation model |

---

## ⚡ 3-Line Summary
English:
1. Express is minimal with the biggest ecosystem; Fastify prioritizes raw performance via built-in JSON Schema validation/serialization; Koa offers a tiny async/await-native core; Hapi favors configuration-driven routes with built-in validation/auth.
2. Framework-level performance differences usually matter less than database/network latency in real production APIs — profile before switching.
3. Choose based on team familiarity, ecosystem needs, and built-in feature requirements (validation, auth, caching) rather than synthetic benchmarks alone.

Hindi:
1. Express minimal है सबसे बड़े ecosystem के साथ; Fastify built-in JSON Schema validation/serialization से performance पर focus करता है; Koa tiny async/await-native core देता है; Hapi configuration-driven routes और built-in validation/auth पसंद करता है।
2. Real production APIs में framework-level performance difference अक्सर database/network latency से कम matter करता है — switch करने से पहले profile करो।
3. Team familiarity, ecosystem needs, और built-in features (validation, auth, caching) के आधार पर चुनो, सिर्फ synthetic benchmarks पर नहीं।

---

## ➡️ Next Topic
**86. Express Routing Basics** — Deep dive into route definitions, parameters, query strings, and route matching patterns in Express।
