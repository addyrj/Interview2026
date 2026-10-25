# 175. API Versioning (/api/v1/)
# हिंदी में: API Versioning — बिना Breaking Changes के API Evolve करना

---

## 🔵 Simple Definition (English)
**API versioning** is the practice of labeling your API (`/api/v1/`, `/api/v2/`) so you can change/improve it over time WITHOUT breaking existing clients (mobile apps, partner integrations) that still depend on the old behavior. Old clients keep hitting `v1`, new clients use `v2`, both run side by side until `v1` is deprecated.

## 🔵 सरल परिभाषा (Hindi)
**API versioning** अपने API को label (`/api/v1/`, `/api/v2/`) करने का तरीका है ताकि समय के साथ change/improve कर सको बिना existing clients (mobile apps, partner integrations) को break किए जो अभी भी पुराने behavior पर depend करते हैं। पुराने clients `v1` hit करते रहते हैं, नए clients `v2` use करते हैं, दोनों साथ चलते हैं जब तक `v1` deprecate ना हो।

---

## 🔴 Problem it Solves
Imagine Flipkart's mobile app (version 5.2, already installed on millions of phones) calls `GET /products/:id` and expects `{ price: 500 }` (a number). The backend team wants to change `price` to an object `{ amount: 500, currency: 'INR' }` for a new multi-currency feature. If they just change the existing endpoint:
```
Old app expects: data.price = 500        (number)
New response is: data.price = { amount: 500, currency: 'INR' }  (object)
Result: Old app crashes trying to do arithmetic on an object, or displays "[object Object]"
```
Millions of users with the old app version would see broken product pages. API versioning solves this: the new shape only exists under `/api/v2/products/:id`; `/api/v1/products/:id` keeps returning the old shape until the old app is phased out.

## 🔴 यह क्यों बना? (Hindi)
Flipkart का mobile app (version 5.2, millions phones पर installed) `GET /products/:id` call करता है और `{ price: 500 }` (number) expect करता है। Backend team multi-currency feature के लिए `price` को object `{ amount: 500, currency: 'INR' }` में बदलना चाहती है। अगर existing endpoint सीधे बदल दिया जाये:
```
पुराना app expect करता है: data.price = 500        (number)
नया response है: data.price = { amount: 500, currency: 'INR' }  (object)
Result: पुराना app arithmetic करते वक़्त crash, या "[object Object]" दिखाता है
```
Millions users पुराने app version के साथ broken product pages देखेंगे। API versioning इसे solve करता है: नया shape सिर्फ `/api/v2/products/:id` में है; `/api/v1/products/:id` पुराना shape तब तक देता रहता है जब तक पुराना app phase out ना हो।

---

## 🟢 How it Works — Step by Step

Step 1 → Choose a versioning strategy: **URI path** (`/api/v1/...` — most common, simple, visible), **header** (`Accept: application/vnd.myapp.v2+json`), or **query param** (`?version=2` — least preferred).
Step 2 → Set up versioned routers in your Express app, each pointing to its own set of route handlers/controllers.
Step 3 → When introducing a breaking change, create a NEW version's router/controller rather than mutating the old one.
Step 4 → Keep both versions running in parallel; document a deprecation timeline for the old version (e.g., "v1 will be removed on 2027-01-01").
Step 5 → Monitor traffic on the old version (via logs/metrics) to know when it's safe to fully retire it.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Versioning strategy चुनो: **URI path** (`/api/v1/...` — सबसे common, simple, visible), **header** (`Accept: application/vnd.myapp.v2+json`), या **query param** (`?version=2` — least preferred)।
Step 2 → Express app में versioned routers setup करो, हर एक अपने route handlers/controllers की तरफ point करता है।
Step 3 → Breaking change लाते वक़्त पुराने version को mutate करने की जगह NEW version का router/controller बनाओ।
Step 4 → दोनों versions parallel में चलाओ; पुराने version के लिए deprecation timeline document करो (जैसे "v1 2027-01-01 को remove होगा")।
Step 5 → पुराने version पर traffic monitor करो (logs/metrics से) ताकि पता चले कब पूरी तरह retire करना safe है।

---

## 🟡 Real World Example
**Razorpay's Payment Gateway API** maintains `v1` for merchants who integrated years ago and `v2` with improved webhook signatures and richer error codes for newer merchants. Razorpay documents EXACTLY what changed between versions, gives a migration guide, and only deprecates `v1` after giving merchants months of advance notice (since breaking payment integrations would be catastrophic for businesses relying on it). This is a textbook case of why versioning with a deprecation policy — not silent breaking changes — is critical in production fintech systems.

## 🟡 Real Example Hindi mein
**Razorpay का Payment Gateway API** `v1` उन merchants के लिए maintain करता है जो साल पहले integrate कर चुके, और `v2` improved webhook signatures और richer error codes के साथ नए merchants के लिए। Razorpay versions के बीच EXACT changes document करता है, migration guide देता है, और `v1` को तभी deprecate करता है जब merchants को महीनों advance notice दे दिया हो (क्योंकि payment integrations तोड़ना businesses के लिए catastrophic होगा)। यह textbook example है कि versioning + deprecation policy — ना कि silent breaking changes — production fintech systems में क्यों critical है।

---

## 💻 Code Example — Basic

```javascript
// basic-versioning.js
// Install: npm install express

const express = require('express');
const app = express();
app.use(express.json());

// --- Version 1 router: price is a plain number ---
const v1Router = express.Router();
v1Router.get('/products/:id', (req, res) => {
  res.status(200).json({ id: req.params.id, name: 'Phone', price: 20000 }); // old shape
});

// --- Version 2 router: price is a structured currency object ---
const v2Router = express.Router();
v2Router.get('/products/:id', (req, res) => {
  res.status(200).json({
    id: req.params.id,
    name: 'Phone',
    price: { amount: 20000, currency: 'INR' }, // new shape, non-breaking for v2 clients
  });
});

// Mount both versions side by side under distinct URL prefixes
app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);

app.listen(3000, () => console.log('Versioned API on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-versioning.js — header-based versioning + deprecation warnings + shared logic

const express = require('express');
const app = express();
app.use(express.json());

// Shared business logic reused across versions -- avoid duplicating DB queries per version
async function getProductData(id) {
  // pretend DB call
  return { id, name: 'Phone', priceInPaise: 2000000 };
}

// Middleware: extract version from a custom header, default to latest if absent
function versionMiddleware(req, res, next) {
  const versionHeader = req.headers['x-api-version']; // e.g. "1" or "2"
  req.apiVersion = versionHeader ? Number(versionHeader) : 2; // default to latest
  next();
}

// Middleware: warn clients still using a deprecated version
function deprecationWarning(deprecatedVersion, sunsetDate) {
  return (req, res, next) => {
    if (req.apiVersion === deprecatedVersion) {
      res.set('Deprecation', 'true');
      res.set('Sunset', sunsetDate); // RFC 8594 style header telling clients when it'll be removed
      console.warn(`Deprecated v${deprecatedVersion} hit: ${req.originalUrl}`); // log for migration tracking
    }
    next();
  };
}

app.use(versionMiddleware);
app.use(deprecationWarning(1, '2027-01-01'));

app.get('/api/products/:id', async (req, res, next) => {
  try {
    const product = await getProductData(req.params.id); // ONE shared data-fetch path

    // Transform the SAME underlying data differently per version -- logic lives in one place
    if (req.apiVersion === 1) {
      return res.status(200).json({
        id: product.id,
        name: product.name,
        price: product.priceInPaise / 100, // old shape: plain rupee number
      });
    }

    // v2 (and beyond): richer, structured shape
    res.status(200).json({
      id: product.id,
      name: product.name,
      price: { amount: product.priceInPaise / 100, currency: 'INR' },
    });
  } catch (err) {
    next(err);
  }
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Mounting multiple real versioned route files (typical production layout)
app.use('/api/v1', require('./routes/v1'));
app.use('/api/v2', require('./routes/v2'));

// Redirect unversioned requests to the latest stable version for convenience
app.use('/api/products', (req, res) => {
  res.redirect(307, `/api/v2/products${req.url}`); // 307 preserves method + body
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Making a breaking change to an existing version instead of creating a new one
✅ Correct: Any change that could break existing clients' parsing logic (renamed/removed field, changed type, changed status code meaning) requires a new version.

```javascript
// Wrong -- silently changes v1's response shape
app.get('/api/v1/products/:id', (req, res) => {
  res.json({ price: { amount: 500, currency: 'INR' } }); // breaks old clients expecting a number!
});

// Right -- keep v1 as-is, add the new shape under v2
app.get('/api/v2/products/:id', (req, res) => {
  res.json({ price: { amount: 500, currency: 'INR' } });
});
```

❌ Mistake 2: Versioning everything, even non-breaking additive changes
✅ Correct: Adding a NEW optional field to a response is NOT a breaking change for most clients (they ignore unknown fields) — doesn't require a new version. Reserve versioning for actual breaking changes (removed fields, changed types, changed required params, changed status code semantics).

---

## 🧠 Tricky Interview Question

```javascript
// A mobile app's older version only reads res.body.price as a Number.
// The backend adds a NEW field res.body.discountedPrice without touching `price`.
// Does this require a new API version?
```
Answer: **No.** This is an additive, backward-compatible change — the old `price` field is untouched, and old clients simply won't look at (and will safely ignore) the new `discountedPrice` field since JSON parsers don't error on unexpected extra fields. Versioning is needed only for changes that BREAK existing client assumptions: removing/renaming a field, changing a field's type, changing required request parameters, or changing status code behavior.

---

## ⚫ Interview Questions + Answers

Q1: What are the three common ways to version an API, and their trade-offs?
A1: **URI path** (`/api/v1/`): simple, visible, cacheable per-version, but "pollutes" the URL and implies the resource itself has versions (debatable semantically). **Header-based** (`Accept-Version` or custom header): keeps URLs clean, more RESTfully "correct" since the resource identity doesn't change, but harder to test manually (can't just click a link) and less visible/discoverable. **Query param** (`?version=2`): simple but easy to forget, and mixes version info with actual query filters — least recommended.

Q2: How long should you support an old API version before removing it?
A2: Depends on the client base: public APIs with third-party integrations need months (sometimes years) of notice; internal APIs where you control all clients can deprecate much faster (days/weeks) since you can coordinate the migration directly. Always communicate a clear sunset date, monitor actual traffic on the old version, and don't remove it until traffic is near-zero or the deadline has definitively passed with adequate warning.

Q3: Should the database schema also be versioned alongside the API?
A3: Not usually in lockstep — database schema evolution is typically handled via migrations that are backward-compatible at each step (additive columns, not immediately dropping old ones), independent of API version numbers. The API layer's job is to transform the SAME underlying data into whichever shape the requested version expects, as shown in the advanced example.

Q4: What HTTP response headers communicate API deprecation to clients?
A4: `Deprecation: true` (or a date) signals the endpoint/version is deprecated. `Sunset: <date>` (RFC 8594) tells clients exactly when it will stop being available. Clients/SDKs can programmatically detect these and log warnings, prompting developers to migrate before the hard cutoff.

Q5: Is it ever acceptable to NOT version an API at all?
A5: For very early-stage internal APIs with a single consumer you fully control (e.g., your own frontend, deployed together with the backend in the same release), strict versioning can be overkill — you can coordinate breaking changes via synchronized deploys. But the moment there are multiple independent clients (mobile apps users don't auto-update, third-party integrations), versioning becomes necessary.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple independent clients (mobile apps, partners, other services) consume your API and can't all upgrade simultaneously.
- You anticipate breaking changes (field renames, type changes, removed endpoints) over the API's lifetime.

❌ Avoid when:
- A single tightly-coupled frontend/backend deployed together — coordinate breaking changes via synchronized releases instead of maintaining parallel versions.
- The change is purely additive/non-breaking — don't bump versions unnecessarily.

---

## 📊 Visual Diagram
```
VERSIONED API COEXISTENCE:
──────────────────────────────────────────────
  Old mobile app (v5.2) ──▶ /api/v1/products/5 ──▶ { price: 20000 }
  New mobile app (v6.0) ──▶ /api/v2/products/5 ──▶ { price: { amount: 20000, currency: 'INR' } }

  Both routers call the SAME underlying data layer,
  just shape the response differently per version.

  Timeline:
  v1 launched ───────────── v2 launched ───── deprecation notice ───── v1 sunset/removed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Versioning | Labeling API iterations | API के versions को label करना |
| Breaking change | Change that breaks existing clients | Existing clients तोड़ने वाला change |
| Deprecation | Marking a version for future removal | Future removal के लिए mark करना |
| Sunset date | Date a version stops working | Version बंद होने की date |
| Backward compatible | Doesn't break old clients | पुराने clients को नहीं तोड़ता |

---

## ⚡ 3-Line Summary
English:
1. API versioning (`/api/v1/`, `/api/v2/`) lets you evolve your API without breaking existing clients that can't upgrade instantly.
2. Only breaking changes (removed/renamed fields, type changes) require a new version; additive changes don't.
3. Communicate deprecation clearly (headers, docs, sunset dates) and share the underlying data logic across versions, only differing in response shaping.

Hindi:
1. API versioning (`/api/v1/`, `/api/v2/`) तुम्हें existing clients तोड़े बिना API evolve करने देता है।
2. सिर्फ breaking changes (removed/renamed fields, type changes) को नया version चाहिए; additive changes को नहीं।
3. Deprecation clearly communicate करो (headers, docs, sunset dates) और versions के बीच data logic share करो, सिर्फ response shape अलग हो।

---

## ➡️ Next Topic
**176. Pagination — Cursor vs Offset** — Large datasets को efficiently page करने के दो approaches।
