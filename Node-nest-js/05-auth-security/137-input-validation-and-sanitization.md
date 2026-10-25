# 137. Input Validation + Sanitization
# हिंदी में: Input Validation + Sanitization

---

## 🔵 Simple Definition (English)
**Input validation** checks that incoming data matches expected shape/type/constraints (e.g., email must look like an email, age must be a positive number) and REJECTS invalid data. **Sanitization** cleans/transforms input to remove or neutralize dangerous content (trimming whitespace, stripping HTML tags, escaping special characters) rather than rejecting it outright.

## 🔵 सरल परिभाषा (Hindi)
**Input validation** check करता है कि incoming data expected shape/type/constraints से match करता है (जैसे email valid format में हो) और invalid data को REJECT करता है। **Sanitization** input को clean/transform करता है ताकि dangerous content हटे या neutral हो जाए (whitespace trim, HTML tags strip, special characters escape) — reject करने के बजाय।

---

## 🔴 Problem it Solves
Without validation, an API blindly trusts whatever the client sends — `age: "abc"` could crash downstream logic expecting a number, `email: "not-an-email"` corrupts your user database, a negative `price: -500` breaks business logic, and malicious payloads (`<script>`, SQL fragments, oversized strings) can cause security vulnerabilities or crashes. Validation + sanitization act as the first line of defense at the API boundary — "never trust client input" — catching bad data before it reaches business logic or the database.

## 🔴 यह क्यों बना? (Hindi)
Validation के बिना API blindly client से आए data को trust करती है — `age: "abc"` downstream logic को crash कर सकता है, invalid email database corrupt कर सकता है, negative price business logic तोड़ सकता है, malicious payloads security vulnerabilities बना सकते हैं। Validation + sanitization API boundary पर पहली defense line है — "client input को कभी trust मत करो।"

---

## 🟢 How it Works — Step by Step

Step 1 → Define a schema describing expected shape of request data (using Joi, Zod, Yup, or express-validator)
Step 2 → At the API boundary (middleware, before controller), validate `req.body`/`req.query`/`req.params` against the schema
Step 3 → If validation fails → return `400 Bad Request` with clear field-level error messages, STOP processing
Step 4 → If validation passes → optionally sanitize fields (trim strings, normalize email case, strip unexpected HTML)
Step 5 → Use type coercion carefully (schema libraries can auto-convert `"25"` string to `25` number) but validate the ORIGINAL intent, not just loosely accept anything
Step 6 → Whitelist allowed fields explicitly (`stripUnknown: true`) — reject/ignore unexpected extra fields client might send (mass assignment protection)
Step 7 → Validate at EVERY layer where trust boundaries cross — not just HTTP input, but also before DB writes if data could arrive from multiple paths

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Schema define करो expected data shape का
Step 2 → API boundary पर request data को schema के against validate करो
Step 3 → Validation fail होने पर `400` के साथ field-level errors दो
Step 4 → Pass होने पर fields sanitize करो (trim, normalize)
Step 5 → Type coercion carefully use करो
Step 6 → Allowed fields explicitly whitelist करो (mass assignment से बचाव)
Step 7 → हर trust boundary पर validate करो

---

## 🟡 Real World Example
**Zomato restaurant registration form:** Restaurant name must be 3-100 chars (trimmed), email must be valid format (lowercased, trimmed), phone must match Indian 10-digit pattern, FSSAI license number must match a specific regex format, cuisine type must be from an allowed enum list (not arbitrary text), opening hours must be valid time ranges. Joi/Zod schema validates ALL of this in one place before the registration logic even runs — rejecting malformed submissions with clear "which field, what's wrong" error messages instead of letting bad data corrupt the restaurant database or crash downstream order-matching logic.

## 🟡 Real Example Hindi mein
**Zomato restaurant registration form:** Restaurant name 3-100 chars का हो, email valid format में हो, phone 10-digit pattern match करे, FSSAI license number specific regex match करे, cuisine type allowed enum से हो। Joi/Zod schema यह सब एक जगह validate करती है registration logic चलने से पहले।

---

## 💻 Code Example — Basic

```javascript
// validation-basic.js — using Joi
// Run with: node validation-basic.js (npm install joi)

const Joi = require('joi');

// ─── 1. DEFINE SCHEMA ──────────────────────────────────────────────────────────
const restaurantSchema = Joi.object({
  name: Joi.string().trim().min(3).max(100).required(),
  email: Joi.string().trim().lowercase().email().required(),
  phone: Joi.string().pattern(/^[6-9]\d{9}$/).required()   // Indian mobile pattern
    .messages({ 'string.pattern.base': 'Phone must be a valid 10-digit Indian number' }),
  cuisine: Joi.string().valid('north-indian', 'south-indian', 'chinese', 'italian').required(),
  rating: Joi.number().min(0).max(5).default(0),
});

// ─── 2. VALIDATE SAMPLE INPUT ──────────────────────────────────────────────────
const validInput = {
  name: '  Spice Garden  ',   // extra whitespace — will be trimmed
  email: 'CONTACT@SPICEGARDEN.COM',  // will be lowercased
  phone: '9876543210',
  cuisine: 'north-indian',
};

const { error, value } = restaurantSchema.validate(validInput);
if (error) {
  console.log('Validation failed:', error.details[0].message);
} else {
  console.log('Validated + sanitized:', value);
  // { name: 'Spice Garden', email: 'contact@spicegarden.com', phone: '9876543210', cuisine: 'north-indian', rating: 0 }
}

// ─── 3. INVALID INPUT EXAMPLE ──────────────────────────────────────────────────
const invalidInput = { name: 'A', email: 'not-an-email', phone: '123', cuisine: 'mexican' };
const result = restaurantSchema.validate(invalidInput, { abortEarly: false });
console.log('Errors:', result.error.details.map((d) => d.message));
// ['"name" length must be at least 3 characters long', '"email" must be a valid email', ...]
```

## 💻 Code Example — Advanced

```javascript
// validation-advanced.js — Zod with custom refinements + sanitization helpers

const { z } = require('zod');  // npm install zod
const sanitizeHtml = require('sanitize-html');

// ─── 1. CUSTOM SANITIZATION TRANSFORM ──────────────────────────────────────────
const sanitizedString = (maxLen) =>
  z
    .string()
    .trim()
    .max(maxLen)
    .transform((val) => sanitizeHtml(val, { allowedTags: [], allowedAttributes: {} }));
    // strips ALL HTML tags — safe plain text only

// ─── 2. COMPLEX SCHEMA WITH CROSS-FIELD VALIDATION ───────────────────────────
const orderSchema = z
  .object({
    customerId: z.string().uuid('Invalid customer ID format'),
    items: z
      .array(
        z.object({
          productId: z.string().min(1),
          quantity: z.number().int().positive().max(50),  // max 50 units per item
        })
      )
      .min(1, 'Order must have at least 1 item')
      .max(20, 'Order cannot exceed 20 different items'),
    deliveryAddress: sanitizedString(200),
    specialInstructions: sanitizedString(500).optional(),
    scheduledFor: z.coerce.date().optional(),   // coerces string → Date
  })
  .refine(
    // Cross-field validation: scheduled time must be in the future
    (data) => !data.scheduledFor || data.scheduledFor > new Date(),
    { message: 'Scheduled delivery time must be in the future', path: ['scheduledFor'] }
  );

// ─── 3. SAFE PARSE (doesn't throw, returns result object) ───────────────────
function validateOrder(input) {
  const result = orderSchema.safeParse(input);
  if (!result.success) {
    // Flatten Zod errors into field-level messages
    const fieldErrors = result.error.flatten().fieldErrors;
    return { valid: false, errors: fieldErrors };
  }
  return { valid: true, data: result.data };
}

// ─── 4. TEST ───────────────────────────────────────────────────────────────────
const testOrder = {
  customerId: '550e8400-e29b-41d4-a716-446655440000',
  items: [{ productId: 'p1', quantity: 2 }],
  deliveryAddress: '<b>123 MG Road</b>, Bangalore',  // HTML will be stripped
  specialInstructions: 'Ring the bell <script>alert(1)</script>',  // script stripped
};

console.log(validateOrder(testOrder));
// { valid: true, data: { ..., deliveryAddress: '123 MG Road, Bangalore', specialInstructions: 'Ring the bell ' } }

module.exports = { orderSchema, validateOrder };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — generic validation middleware factory
const express = require('express');
const { orderSchema } = require('./validation-advanced');

const app = express();
app.use(express.json());

// Generic middleware factory: validates req.body against any Zod schema
function validateBody(schema) {
  return (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({
        error: 'Validation failed',
        details: result.error.flatten().fieldErrors,
      });
    }
    req.validatedBody = result.data;  // sanitized + validated data, use this downstream
    next();
  };
}

app.post('/orders', validateBody(orderSchema), async (req, res) => {
  // req.validatedBody is guaranteed clean: trimmed, sanitized, type-correct
  const order = await Order.create(req.validatedBody);
  res.status(201).json(order);
});

// Query param validation example (e.g., pagination)
const { z } = require('zod');
const paginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

app.get('/orders', (req, res) => {
  const result = paginationSchema.safeParse(req.query);
  if (!result.success) {
    return res.status(400).json({ error: 'Invalid pagination params' });
  }
  const { page, limit } = result.data;
  res.json({ page, limit, orders: [] });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Validating only on the frontend, trusting the API blindly
```javascript
// WRONG: frontend form has HTML5 "required" and pattern attributes — but API has none
// Attacker bypasses frontend entirely using curl/Postman directly against the API
app.post('/orders', async (req, res) => {
  await Order.create(req.body);  // no server-side validation at all!
});

// CORRECT: ALWAYS validate server-side — frontend validation is just UX, not security
app.post('/orders', validateBody(orderSchema), async (req, res) => {
  await Order.create(req.validatedBody);
});
```

❌ Mistake 2: Not stripping unknown fields (mass assignment vulnerability)
```javascript
// WRONG: blindly passing entire req.body to a DB create call
app.post('/users', async (req, res) => {
  const user = await User.create(req.body);
  // Attacker sends { name: 'x', email: 'x@x.com', role: 'admin', isVerified: true }
  // If the model accepts these fields, attacker just made themselves an admin!
});

// CORRECT: whitelist exact fields via schema, discard anything else
const userSchema = z.object({ name: z.string(), email: z.string().email() }).strict();
// .strict() rejects extra unknown keys; or explicitly pick fields before DB write
const { name, email } = req.validatedBody;
await User.create({ name, email, role: 'customer' });  // role set server-side, not from input
```

---

## 🧠 Tricky Interview Question

```javascript
const Joi = require('joi');
const schema = Joi.object({ age: Joi.number().required() });

const result = schema.validate({ age: '25' });  // age sent as STRING from form
console.log(result.error);          // ?
console.log(result.value);          // ?
```
Answer: `result.error` is `undefined` (validation PASSES) and `result.value.age` becomes the **number** `25`, not the string `'25'`. By default, Joi (like Zod with `z.coerce`) performs **type coercion** — it tries to convert compatible types (numeric strings → numbers) before validating, which is often desirable for form/query-string data (always strings in HTTP). The gotcha: if you want STRICT type checking with no coercion, you must explicitly set `convert: false` in Joi's validate options, otherwise `"25"`, `25`, and even `" 25 "` might all pass as valid numbers — surprising if you expected only true JS numbers to pass.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between validation and sanitization, and should you do both?
A1: Validation checks if data meets rules and REJECTS it (400 error) if not — it's a gatekeeper. Sanitization TRANSFORMS data to remove/neutralize problems (trim whitespace, strip HTML, normalize case) without necessarily rejecting the request. Best practice: do both — validate structure/type/business rules AND sanitize potentially dangerous content (especially free-text fields that end up rendered as HTML later). They're complementary, not alternatives.

Q2: What is a "mass assignment" vulnerability and how does input validation prevent it?
A2: Mass assignment happens when an API blindly accepts and saves ALL fields from a request body to a database model, allowing attackers to set fields they shouldn't control (e.g., `role: 'admin'`, `isVerified: true`, `price: 0`). Validation schemas prevent this by explicitly whitelisting ONLY the expected fields (e.g., `.strict()` in Zod, or `stripUnknown: true` in Joi) — any extra/unexpected field is rejected or silently dropped, and sensitive fields (role, permissions) are set server-side, never taken from client input.

Q3: Where should validation happen — middleware, controller, or model/DB layer?
A3: Primarily in a dedicated MIDDLEWARE layer at the API boundary (before the controller runs) — this keeps controllers clean and ensures validation happens consistently before any business logic. However, defense-in-depth suggests ALSO having basic constraints at the DB/model layer (e.g., Mongoose schema types, SQL `NOT NULL`/`CHECK` constraints) as a last-resort safety net, in case data ever enters through another path (migrations, internal scripts, admin tools) that bypasses the HTTP middleware.

Q4: How do you handle validation errors in a way that's useful to API consumers but doesn't leak internal details?
A4: Return `400 Bad Request` with a structured error response listing WHICH field failed and WHY in user-friendly terms (e.g., `{ field: 'email', message: 'must be a valid email address' }`) — this helps legitimate clients fix their request. Avoid leaking internal schema implementation details, stack traces, or database column names in error messages, which could help attackers understand your system's internals. Use libraries' built-in `.messages()` (Joi) or custom error maps (Zod) to control exactly what's exposed.

Q5: Should numeric string coercion (e.g., `"25"` → `25`) be enabled by default in your validation schemas?
A5: It depends on the source: query strings and form-urlencoded bodies are ALWAYS strings over HTTP, so coercion (`z.coerce.number()`) is usually desirable and expected there — rejecting `?page=2` because `"2"` isn't a strict number would be bad UX. For JSON request bodies, where the client CAN send a true JSON number, you may prefer stricter typing (no coercion) to catch client bugs early. Choose coercion rules deliberately per input source rather than applying one blanket policy everywhere.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any endpoint accepts client-controlled input (body, query, params, headers) — validate at every single API boundary, no exceptions.
- Fields will later be rendered as HTML, used in queries, or stored permanently — sanitize in addition to validating.

❌ Avoid when:
- Never skip it entirely. The only nuance is choosing strictness (coercion vs strict types) appropriately per input source — not whether to validate at all.

---

## 📊 Visual Diagram

```
VALIDATION + SANITIZATION PIPELINE:
──────────────────────────────────────────────────────────

  Client request body:
    { name: '  <b>Rahul</b>  ', age: '25', role: 'admin' }
       │
       ▼
  1. SCHEMA VALIDATION (Zod/Joi)
     - name: string, required         ✓ (after trim)
     - age: number (coerced from "25") ✓
     - role: NOT in schema             → stripped/rejected
       │
       ▼
  2. SANITIZATION
     - name: trim whitespace → 'Rahul' (HTML tags stripped)
     - age: '25' → 25 (number)
       │
       ▼
  3. CLEAN DATA passed to controller:
     { name: 'Rahul', age: 25 }
     (role field silently discarded — mass assignment blocked)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Validation | Checking data against rules, rejecting invalid | Rules के against data check करना |
| Sanitization | Cleaning/transforming input to remove danger | Input को clean/transform करना |
| Schema | Structured definition of expected data shape | Expected data shape की structured definition |
| Mass assignment | Accepting unintended fields from client | Unintended fields client से accept करना |
| Type coercion | Auto-converting compatible types | Compatible types auto-convert करना |
| Whitelist | Explicitly allowed set of fields/values | Explicitly allowed fields/values का set |

---

## ⚡ 3-Line Summary
English:
1. Validation rejects malformed data at the API boundary; sanitization cleans/transforms input to neutralize dangerous content.
2. Use schema libraries (Joi, Zod) to define expected shapes, whitelist fields explicitly to prevent mass assignment, and return clear 400 errors.
3. Always validate server-side regardless of frontend validation — frontend checks are UX only, never a security boundary.

Hindi:
1. Validation malformed data को API boundary पर reject करता है; sanitization input को clean करता है dangerous content हटाने के लिए।
2. Joi/Zod जैसी schema libraries use करो, fields explicitly whitelist करो mass assignment रोकने के लिए।
3. हमेशा server-side validate करो — frontend validation सिर्फ UX है, security boundary नहीं।

---

## ➡️ Next Topic
**138. HTTPS in Node.js** — TLS/SSL से encrypted connections setup करना Node server में।
