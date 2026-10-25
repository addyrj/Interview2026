# 102. Request Validation (express-validator / Joi / Zod)
# हिंदी में: Request Validation

---

## 🔵 Simple Definition (English)
**Request validation** checks incoming data (`req.body`, `req.params`, `req.query`) against defined rules BEFORE it reaches business logic — rejecting malformed/malicious/incomplete input early. Popular libraries: `express-validator` (middleware-based, built on `validator.js`), `Joi` (schema-based, framework-agnostic), `Zod` (TypeScript-first schema validation with type inference).

## 🔵 सरल परिभाषा (Hindi)
**Request validation** incoming data (`req.body`, `req.params`, `req.query`) को business logic तक पहुँचने से पहले defined rules के against check करता है — malformed/malicious/incomplete input को जल्दी reject करता है। Popular libraries: `express-validator`, `Joi`, `Zod`।

---

## 🔴 Problem it Solves
```
WITHOUT VALIDATION:
  app.post('/users', (req, res) => {
    // req.body could be ANYTHING — missing fields, wrong types, malicious strings
    const user = createUser(req.body);  // crashes or saves garbage data
    res.json(user);
  });
  // Client sends: { email: 123, age: "not a number", name: "<script>alert(1)</script>" }
  // → Server either crashes with a cryptic error, or saves CORRUPT/UNSAFE data

WITH VALIDATION:
  app.post('/users',
    body('email').isEmail(),
    body('age').isInt({ min: 18 }),
    body('name').trim().escape(),
    handleValidation,          // rejects with clear 400 error if any rule fails
    createUserHandler           // only reached with CLEAN, validated data
  );
```

## 🔴 यह क्यों बना? (Hindi)
बिना validation के, client से कोई भी garbage/malicious data आ सकता था — server crash हो सकता था, corrupt data save हो सकता था, या security vulnerabilities (XSS, injection) बन सकती थीं। Validation libraries ने declarative rules देकर data को business logic तक पहुँचने से पहले ही check और reject करने का तरीका दिया।

---

## 🟢 How it Works — Step by Step

Step 1 → Define validation rules for each field (type, format, length, required/optional) using the chosen library's API
Step 2 → `express-validator`: rules run AS middleware in the route chain, errors collected in `req` via `validationResult()`
Step 3 → `Joi`/`Zod`: define a SCHEMA object once, then call `.validate()`/`.parse()` on `req.body` (usually inside a small wrapper middleware)
Step 4 → If validation fails, respond with `400 Bad Request` and a clear list of errors — the route handler never runs
Step 5 → If validation passes, the (now TRUSTED and often TYPE-COERCED/sanitized) data flows to the actual business logic

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर field के लिए validation rules define करो (type, format, length, required/optional)
Step 2 → `express-validator`: rules middleware के रूप में route chain में चलते हैं, errors `validationResult()` से collect होते हैं
Step 3 → `Joi`/`Zod`: एक बार SCHEMA define करो, फिर `req.body` पर `.validate()`/`.parse()` call करो
Step 4 → Validation fail हो तो `400 Bad Request` के साथ clear error list भेजो — route handler कभी नहीं चलता
Step 5 → Validation pass हो तो trusted data business logic तक पहुँचता है

---

## 🟡 Real World Example
**Paytm payment API:** Before processing any payment, the server validates: `amount` must be a positive number with max 2 decimal places, `upiId` must match a valid UPI format regex, `currency` must be one of `['INR']` (whitelist), `customerPhone` must be a valid 10-digit Indian number. Zod schemas enforce ALL of this declaratively, rejecting bad requests with a clear 400 BEFORE any payment-processing code (which touches real money) ever runs.

## 🟡 Real Example Hindi mein
**Paytm payment API:** Payment process करने से पहले server validate करता है: `amount` positive number हो max 2 decimal places के साथ, `upiId` valid UPI format regex से match करे, `currency` whitelist में हो, `customerPhone` valid 10-digit number हो। Zod schemas यह सब declaratively enforce करते हैं, bad requests को payment-processing code चलने से पहले ही reject कर देते हैं।

---

## 💻 Code Example — Basic

```javascript
// validation-basic-express-validator.js
// npm install express express-validator
const express = require('express');
const { body, validationResult } = require('express-validator');
const app = express();
app.use(express.json());

app.post('/api/users',
  // Validation rules — chainable, each adds a check
  body('email').isEmail().withMessage('Valid email required'),
  body('age').isInt({ min: 18 }).withMessage('Age must be 18 or older'),
  body('name').trim().notEmpty().withMessage('Name is required'),

  (req, res) => {
    const errors = validationResult(req);   // collect all rule failures
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // At this point, req.body is validated — safe to proceed
    res.status(201).json({ created: true, data: req.body });
  }
);

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// validation-advanced-zod.js
// npm install express zod
const express = require('express');
const { z } = require('zod');
const app = express();
app.use(express.json());

// Define a reusable Zod schema
const createUserSchema = z.object({
  email: z.string().email('Invalid email format'),
  age: z.number().int().min(18, 'Must be 18 or older').max(120),
  name: z.string().trim().min(2, 'Name too short').max(50),
  role: z.enum(['customer', 'admin']).optional().default('customer'),
  address: z.object({
    city: z.string(),
    pincode: z.string().regex(/^\d{6}$/, 'Invalid pincode'),
  }).optional(),
});

// Generic validation middleware factory — reusable for ANY schema
const validate = (schema) => (req, res, next) => {
  const result = schema.safeParse(req.body);   // safeParse never throws
  if (!result.success) {
    return res.status(400).json({
      errors: result.error.issues.map(i => ({ path: i.path.join('.'), message: i.message })),
    });
  }
  req.body = result.data;   // replace with parsed/coerced/defaulted data
  next();
};

app.post('/api/users', validate(createUserSchema), (req, res) => {
  // req.body is now fully typed, validated, and has defaults applied
  res.status(201).json({ created: true, user: req.body });
});

// --- Joi equivalent for comparison ---
// npm install joi
const Joi = require('joi');
const orderSchema = Joi.object({
  items: Joi.array().items(Joi.object({
    productId: Joi.string().required(),
    qty: Joi.number().integer().min(1).required(),
  })).min(1).required(),
  couponCode: Joi.string().optional(),
});

const validateJoi = (schema) => (req, res, next) => {
  const { error, value } = schema.validate(req.body, { abortEarly: false });  // collect ALL errors
  if (error) {
    return res.status(400).json({ errors: error.details.map(d => d.message) });
  }
  req.body = value;
  next();
};

app.post('/api/orders', validateJoi(orderSchema), (req, res) => {
  res.status(201).json({ created: true, order: req.body });
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Real-world: validating params, query, and body together
const express = require('express');
const { z } = require('zod');
const app = express();
app.use(express.json());

const paramsSchema = z.object({ id: z.string().regex(/^\d+$/) });
const querySchema = z.object({ includeItems: z.enum(['true', 'false']).optional() });
const bodySchema = z.object({ status: z.enum(['pending', 'shipped', 'cancelled']) });

const validateRequest = ({ params, query, body } = {}) => (req, res, next) => {
  try {
    if (params) req.params = params.parse(req.params);
    if (query) req.query = query.parse(req.query);
    if (body) req.body = body.parse(req.body);
    next();
  } catch (err) {
    res.status(400).json({ error: 'Validation failed', details: err.issues });
  }
};

app.patch('/api/orders/:id',
  validateRequest({ params: paramsSchema, query: querySchema, body: bodySchema }),
  (req, res) => {
    res.json({ id: req.params.id, status: req.body.status });
  }
);

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Validating AFTER already using unvalidated data
```javascript
// WRONG: business logic runs BEFORE validation check
app.post('/users', body('email').isEmail(), async (req, res) => {
  const user = await createUser(req.body);   // ❌ runs even if email is invalid!
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });
  res.json(user);
});

// CORRECT: check validation result FIRST, before any business logic
app.post('/users', body('email').isEmail(), async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });
  const user = await createUser(req.body);
  res.json(user);
});
```

❌ **Mistake 2:** Trusting `req.query`/`req.params` without validation (only validating `req.body`)
```javascript
// WRONG: only body validated, query params used blindly
app.get('/search', (req, res) => {
  const page = req.query.page;       // could be "abc", negative, or huge — unvalidated!
  db.find().skip(page * 20);          // crashes or behaves unexpectedly
});

// CORRECT: validate query params too
const querySchema = z.object({ page: z.coerce.number().int().min(1).default(1) });
app.get('/search', validate(querySchema, 'query'), (req, res) => {
  db.find().skip((req.query.page - 1) * 20);  // safe, guaranteed valid number
});
```

---

## 🧠 Tricky Interview Question

```javascript
const schema = z.object({ age: z.number() });

app.post('/test', (req, res) => {
  const result = schema.safeParse(req.body);
  res.json({ success: result.success });
});

// Client sends: POST /test  Body: { "age": "25" }  (age as a STRING, not number)
// Does validation succeed or fail?
```
Answer: It FAILS (`success: false`). Even though `"25"` LOOKS like a valid age, Zod's `z.number()` performs STRICT type checking by default — it does NOT coerce a string to a number automatically. JSON itself preserves type information (unlike query strings), so `"25"` really is a string in the parsed JSON body, and Zod rejects it as a type mismatch. To accept and auto-convert string numbers, you'd need `z.coerce.number()` explicitly, which is commonly needed for QUERY STRING validation (where everything genuinely arrives as strings) but less expected for JSON bodies where clients should send proper types.

---

## ⚫ Interview Questions + Answers

Q1: What's the architectural difference between `express-validator` and schema-based libraries like Joi/Zod?
A1: `express-validator` is MIDDLEWARE-CENTRIC — validation rules are expressed as a chain of Express middleware functions (`body('email').isEmail()`) that run IN the route definition itself, with errors collected via `validationResult(req)`. Joi/Zod are SCHEMA-CENTRIC — you define a schema object ONCE (reusable across routes/contexts, even outside Express), then call `.validate()`/`.parse()` on data explicitly. Schema-based approaches are often considered cleaner for complex nested validation and are framework-agnostic (reusable in non-Express contexts like a CLI tool or another framework).

Q2: Why is Zod particularly popular in TypeScript projects specifically?
A2: Zod provides automatic TYPE INFERENCE — once you define a schema with `z.object({...})`, you can derive a TypeScript type from it via `z.infer<typeof schema>`, giving you a SINGLE SOURCE OF TRUTH for both runtime validation AND compile-time types. This eliminates the common problem of maintaining a TypeScript interface AND a separate validation schema that can drift out of sync.

Q3: What does "sanitization" mean in request validation, and give an example?
A3: Sanitization TRANSFORMS input data to a safe/normalized form, distinct from just validating it's correct. Examples: `.trim()` removes whitespace, `.escape()` HTML-escapes strings to prevent XSS when later rendered, `.toLowerCase()` normalizes emails for consistent lookups, `.toInt()` converts a numeric string to an actual number. `express-validator` explicitly separates "validators" (checks) from "sanitizers" (transforms) but lets you chain both.

Q4: How would you validate that a request body's data type matches EXACTLY, vs allowing type coercion?
A4: Zod by default is STRICT about types — `z.number()` rejects a string like `"25"` even if it looks numeric. To explicitly ALLOW coercion, use `z.coerce.number()`, which attempts `Number(value)` before validating. This distinction matters: for JSON bodies, strict typing usually makes sense (clients should send correct types); for QUERY STRINGS (always strings in HTTP), coercion is often necessary and expected.

Q5: Where in the middleware chain should validation middleware be placed, and why?
A5: Validation middleware should run EARLY — right after body-parsing middleware (`express.json()`) but BEFORE any authentication/authorization or business logic that assumes well-formed data. This "fail fast" principle avoids wasting resources (DB calls, auth checks) on requests that are malformed anyway, and gives clients immediate, clear feedback about what's wrong with their request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any endpoint accepting client input (body, query, params) — essentially ALWAYS in production APIs
- You need consistent, centralized validation rules reusable across multiple routes

❌ Avoid when:
- Over-validating internal, trusted service-to-service calls where the schema is already guaranteed by a shared contract (though even then, defensive validation is often still worth the small overhead)
- Duplicating validation that's ALSO strictly enforced at the database layer AND unlikely to ever receive untrusted input (rare — validation is cheap insurance)

---

## 📊 Visual Diagram
```
  REQUEST VALIDATION FLOW
  ─────────────────────────────────────────
  Incoming Request
       │
       ▼
  express.json()  → req.body populated (raw, untrusted)
       │
       ▼
  Validation middleware (Zod/Joi/express-validator)
       │
    ┌──┴──┐
  VALID   INVALID
    │       │
    ▼       ▼
  next()   res.status(400).json({ errors: [...] })
    │       (chain stops — business logic never runs)
    ▼
  Business logic / Controller
  (receives CLEAN, trusted, often type-coerced data)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Validation | Checking data against rules | Rules के against data check करना |
| Sanitization | Transforming data to safe form | Data को safe form में transform करना |
| Schema | Declarative shape/rules definition | Declarative shape/rules definition |
| `safeParse`/`validate` | Non-throwing validation call | बिना throw किए validation call |
| Fail fast | Reject invalid input immediately | Invalid input immediately reject करना |

---

## ⚡ 3-Line Summary
English: 1. Request validation (express-validator/Joi/Zod) checks input shape/type/format BEFORE business logic runs, rejecting bad data with a clear 400 error. 2. Zod offers TypeScript type inference from schemas; Joi/express-validator are framework patterns without that built-in type link. 3. Validate `req.body`, `req.params`, AND `req.query` — not just the body — since all are untrusted client input.
Hindi: 1. Request validation business logic से पहले input shape/type/format check करता है, bad data को clear 400 error से reject करता है। 2. Zod schemas से TypeScript types infer करता है। 3. सिर्फ body नहीं, `req.params` और `req.query` भी validate करो — सब untrusted client input हैं।

---

## ➡️ Next Topic
**103. Response Methods (json, send, status, redirect)** — All the ways to send responses back to clients in Express.
