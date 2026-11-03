# 83. Mongoose Validation and Custom Validators
# हिंदी में: Mongoose Validation और Custom Validators

---

## 🔵 Simple Definition (English)
**Mongoose validation** checks a document against the rules in its schema before it is written. Built-in validators include `required`, `min`/`max`, `minlength`/`maxlength`, `enum` and `match`. A **custom validator** is your own function (sync or async) attached with `validate: { validator, message }`. If any rule fails, Mongoose throws a `ValidationError` that lists each failing path in `err.errors`, and nothing is sent to the database.

## 🔵 सरल परिभाषा (Hindi)
**Mongoose validation** document को database में लिखने से पहले schema के rules के विरुद्ध जाँचता है। Built-in validators में `required`, `min`/`max`, `minlength`/`maxlength`, `enum` और `match` हैं। **Custom validator** आपका अपना function (sync या async) है जो `validate: { validator, message }` से जुड़ता है। कोई rule fail हो तो Mongoose `ValidationError` throw करता है जिसमें हर failing path `err.errors` में होता है, और database को कुछ नहीं भेजा जाता।

---

## 🔴 Problem it Solves
Without validation, bad data reaches the database: negative prices, a phone number with 5 digits, a status "LOST" that no code understands. Frontend checks can be bypassed (curl, Postman, other services). Putting rules in the model means every write path (API, cron job, admin script) is protected by the same rules, and API clients get precise field-level error messages to show in the UI.

## 🔴 यह क्यों बना? (Hindi)
Validation के बिना खराब data database तक पहुँच जाता है: negative prices, 5 अंकों का phone number, "LOST" जैसा status जिसे कोई code नहीं समझता। Frontend checks को bypass किया जा सकता है (curl, Postman, दूसरी services)। नियम model में रखने से हर write path (API, cron job, admin script) उन्हीं rules से सुरक्षित रहता है, और API clients को UI में दिखाने के लिए सटीक field-level error messages मिलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare rules on schema paths: `{ type: Number, min: [1, 'Price must be >= 1'] }`. The array form `[value, message]` customises the message.
Step 2 → Built-ins: **all types** `required`; **String** `enum`, `match`, `minlength`, `maxlength`, `trim`; **Number/Date** `min`, `max`.
Step 3 → Custom validator: `validate: { validator: fn, message }`. `fn(value)` returns true/false (or a Promise for async). Use `function` (not an arrow) if you need `this` (the document).
Step 4 → Validation runs automatically before `save()` (a `pre('validate')` hook). Manually: `await doc.validate()`.
Step 5 → On failure, `ValidationError` has `.errors[path]` objects with `.message`, `.kind` (`required`, `min`, `enum`, `user defined`) and `.value`.
Step 6 → **Update validators are OFF by default.** `updateOne`/`findOneAndUpdate` skip validation unless you pass `{ runValidators: true }`. Even then, `this` inside custom validators is the query, not the document.
Step 7 → Validation runs on `insertMany` per document, but NOT on `updateMany` without `runValidators`, and never on raw `Model.collection.*` calls.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Schema paths पर rules लगाओ: `{ type: Number, min: [1, 'Price must be >= 1'] }`। Array रूप `[value, message]` message बदलता है।
Step 2 → Built-ins: **सभी types** के लिए `required`; **String** के लिए `enum`, `match`, `minlength`, `maxlength`, `trim`; **Number/Date** के लिए `min`, `max`।
Step 3 → Custom validator: `validate: { validator: fn, message }`। `fn(value)` true/false (या async के लिए Promise) लौटाता है। `this` (document) चाहिए तो arrow नहीं, `function` इस्तेमाल करो।
Step 4 → Validation `save()` से पहले अपने आप चलता है (`pre('validate')` hook)। हाथ से: `await doc.validate()`।
Step 5 → Fail होने पर `ValidationError` में `.errors[path]` objects होते हैं जिनमें `.message`, `.kind` (`required`, `min`, `enum`, `user defined`) और `.value` है।
Step 6 → **Update validators default रूप से बंद हैं।** `updateOne`/`findOneAndUpdate` तब तक validation skip करते हैं जब तक `{ runValidators: true }` न दो। तब भी custom validators में `this` document नहीं, query होता है।
Step 7 → `insertMany` में हर document का validation होता है, पर `updateMany` में `runValidators` के बिना नहीं, और raw `Model.collection.*` calls में कभी नहीं।

---

## 🟡 Real World Example
A **Razorpay**-style payment-link model: `amount` must be between 1 and 100000 (in INR for the demo), `phone` must match an Indian mobile pattern `^[6-9]\d{9}$`, `status` must be one of `CREATED | PAID | EXPIRED`, `discount` can never exceed `amount` (a cross-field check), and `vpa` (UPI id) must be unique among active links (async check). The API returns HTTP 400 with `{ field: message }` for each failing path, so the checkout UI can highlight the exact input.

## 🟡 Real Example Hindi mein
**Razorpay** जैसा payment-link model: `amount` 1 से 100000 के बीच (demo में INR), `phone` भारतीय mobile pattern `^[6-9]\d{9}$` से match करे, `status` `CREATED | PAID | EXPIRED` में से एक हो, `discount` कभी `amount` से ज़्यादा न हो (cross-field check), और `vpa` (UPI id) active links में unique हो (async check)। API हर failing path के लिए `{ field: message }` के साथ HTTP 400 लौटाती है, ताकि checkout UI सटीक input को highlight करे।

---

## 💻 Code Example — Basic

```javascript
// validation-basic.js — output below is real (Mongoose 9, MongoDB 8.0.4)
const mongoose = require('mongoose');

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');

  const schema = new mongoose.Schema({
    // required with a custom message + minlength
    name:  { type: String, required: [true, 'Name is required'], minlength: 2 },

    // custom sync validator; message can be a function that receives { value }
    phone: { type: String, validate: {
      validator: v => /^[6-9]\d{9}$/.test(v),                       // Indian mobile pattern
      message: p => `${p.value} is not a valid Indian mobile` } },

    // min / max with a custom message on min
    price: { type: Number, min: [1, 'Price must be >= 1'], max: 100000 },

    // CROSS-FIELD validator: needs `this`, so use a regular function (NOT an arrow)
    discount: { type: Number, validate: {
      validator: function (v) { return v <= this.price; },
      message: 'Discount cannot exceed price' } },

    // enum with custom message; {VALUE} is replaced by the offending value
    status: { type: String, enum: { values: ['PLACED', 'SHIPPED'], message: '{VALUE} is not supported' } },

    // validator on an array: at most 3 tags
    tags: { type: [String], validate: [a => a.length <= 3, 'Max 3 tags'] },
  });
  const M = mongoose.model('Val', schema);

  // Build an intentionally invalid document
  const d = new M({ name: 'A', phone: '12345', price: 0, discount: 5, status: 'LOST', tags: ['a','b','c','d'] });

  try { await d.validate(); } catch (err) {              // validate() returns a promise (validateSync is deprecated in v9)
    console.log(err.name);                               // ValidationError
    for (const [path, e] of Object.entries(err.errors))  // one entry per failing path
      console.log(path, '->', e.message, `(${e.kind})`);
  }
  // Output:
  // ValidationError
  // name -> Path `name` (`A`, length 1) is shorter than the minimum allowed length (2). (minlength)
  // phone -> 12345 is not a valid Indian mobile (user defined)
  // price -> Price must be >= 1 (min)
  // discount -> Discount cannot exceed price (user defined)
  // status -> LOST is not supported (enum)
  // tags -> Max 3 tags (user defined)
  await mongoose.disconnect();
})();
```

## 💻 Code Example — Advanced

```javascript
// validation-advanced.js — async validators and update validators
const mongoose = require('mongoose');

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');

  const schema = new mongoose.Schema({
    name: String,
    price: { type: Number, min: [1, 'Price must be >= 1'] },
    username: { type: String, validate: {
      // ASYNC validator: hits the DB. Fine for UX, but NOT a race-proof uniqueness guarantee
      validator: async function (v) { return !(await mongoose.models.Val.exists({ username: v })); },
      message: 'Username taken' } },
  });
  const M = mongoose.model('Val', schema);
  await M.deleteMany({});

  // 1) ASYNC validator in action
  await M.create({ name: 'Ok', username: 'raj' });
  try { await M.create({ name: 'Ok2', username: 'raj' }); }
  catch (e) { console.log(e.errors.username.message); }
  // Output: Username taken

  // 2) UPDATE VALIDATORS ARE OFF BY DEFAULT — the classic trap
  const ok = await M.create({ name: 'Zed', price: 10 });
  await M.updateOne({ _id: ok._id }, { price: -5 });     // no error!
  console.log('without runValidators price =', (await M.findById(ok._id)).price);
  // Output: without runValidators price = -5      <- invalid data got in

  // 3) Turn them on per call
  try { await M.updateOne({ _id: ok._id }, { price: -5 }, { runValidators: true }); }
  catch (e) { console.log('with runValidators:', e.message); }
  // Output: with runValidators: Validation failed: price: Price must be >= 1

  // 4) Or turn them on globally for all update operations (recommended)
  mongoose.set('runValidators', true);

  // 5) For uniqueness, rely on a unique INDEX (race-safe), not on the async validator
  // schema.path('username').index({ unique: true });  -> duplicate => error code 11000
  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
mongoose.set('runValidators', true);                    // validate on updateOne/findOneAndUpdate as well

const Link = mongoose.model('PaymentLink', new mongoose.Schema({
  amount: { type: Number, required: true, min: 1, max: 100000 },
  phone:  { type: String, match: [/^[6-9]\d{9}$/, 'Invalid mobile number'] },   // match = regex shortcut
  status: { type: String, enum: ['CREATED', 'PAID', 'EXPIRED'], default: 'CREATED' },
}));

const app = express();
app.use(express.json());

// Convert ValidationError into a clean { field: message } map for the frontend
function formatValidation(err) {
  return Object.fromEntries(Object.entries(err.errors).map(([k, v]) => [k, v.message]));
}

app.post('/api/links', async (req, res) => {
  try {
    res.status(201).json(await Link.create({ amount: req.body.amount, phone: req.body.phone }));
  } catch (err) {
    if (err.name === 'ValidationError') return res.status(400).json({ errors: formatValidation(err) });
    res.status(500).json({ error: 'Server error' });
  }
});

app.patch('/api/links/:id', async (req, res) => {
  try {
    // runValidators is already global; `new` is replaced by returnDocument in Mongoose 9
    const doc = await Link.findByIdAndUpdate(req.params.id, { status: req.body.status }, { returnDocument: 'after' });
    doc ? res.json(doc) : res.sendStatus(404);
  } catch (err) {
    if (err.name === 'ValidationError') return res.status(400).json({ errors: formatValidation(err) });
    res.status(400).json({ error: err.message });
  }
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming updates are validated
```javascript
// Wrong — price -5 gets saved (tested above)
await Product.updateOne({ _id }, { price: -5 });

// Right
await Product.updateOne({ _id }, { price: -5 }, { runValidators: true });
// or mongoose.set('runValidators', true) once at startup
```

❌ Mistake 2: Arrow function in a validator that needs `this`
```javascript
// Wrong — `this` is not the document in an arrow function
validate: { validator: v => v <= this.price }

// Right
validate: { validator: function (v) { return v <= this.price; } }
```

❌ Mistake 3: Async "uniqueness" validator instead of a unique index
✅ Correct: two concurrent requests can both pass the async check, then both insert. Always back uniqueness with `unique: true` index and handle error code 11000.

---

## 🧠 Tricky Interview Question

**Q:** `required: true` on a String field: does `name: ''` pass? What about `name: null`, `name: undefined`, and for a Number field `age: 0`?

**Answer:** For String, `required` fails on `undefined`, `null` and the **empty string** `''` (Mongoose treats an empty string as missing for strings). For Number, `0` **passes** (it is a valid number, `required` only fails for `null`/`undefined`/`NaN`). For arrays, `required` passes even when the array is empty unless you add your own length validator. Mongoose also will not run validators (other than `required`) when the value is `undefined`, so `min`/custom validators only run on provided values.

---

## ⚫ Interview Questions + Answers

Q1: When does validation run?
A1: Automatically before `save()` (and `create`), per document in `insertMany`, and when you call `validate()` manually. It does not run on update queries unless `runValidators: true` is set, and not on `bulkWrite` / `Model.collection` raw writes.

Q2: How do you write a cross-field validator?
A2: Use `validate: { validator: function (v) { ... this.otherField ... } }` with a regular function so `this` is the document. In update validators `this` is the query, so cross-field checks need `context`-aware tricks or doing the check in app code / `pre('findOneAndUpdate')` hook.

Q3: What is in a `ValidationError`?
A3: `err.name === 'ValidationError'`, `err.message`, and `err.errors`, an object keyed by path where each entry has `message`, `kind`, `path`, `value`. Use it to build field-level API errors.

Q4: Are Mongoose validators a substitute for database-level validation?
A4: No. They only protect writes that go through Mongoose. For defence in depth add MongoDB `$jsonSchema` validation on the collection (topic 75) so other clients/services cannot write invalid data.

Q5: Difference between `unique` and a validator?
A5: `unique` creates a database index and the failure is a driver error code 11000 at write time; a validator is an application-level check that throws `ValidationError` before the write. Only the index is race-safe.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need field-level rules shared by every code path writing through the model
- You want friendly error messages for API clients
- Business rules are simple and local to a document (ranges, formats, cross-field)

❌ Avoid / supplement when:
- The rule needs DB-wide consistency (uniqueness, referential checks): use indexes/transactions
- Many writers bypass Mongoose: add `$jsonSchema` validation in MongoDB
- Heavy validation involving external services: do it in the service layer, not in model validators

---

## 📊 Visual Diagram
```
MONGOOSE VALIDATION FLOW
──────────────────────────────────────────────────────
  doc.save() / Model.create()
        │
        ▼
  cast types ("25" → 25)  ──fail──► CastError
        │
        ▼
  run validators (required, min, enum, match, custom)
        │            │
      all pass     any fail
        │            ▼
        │      ValidationError { errors: { path: {message, kind} } }
        ▼
  send to MongoDB ──► unique index ──fail──► MongoServerError 11000

  updateOne / findOneAndUpdate:
     validators SKIPPED unless { runValidators: true }  ⚠
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Validator | Function/rule checking a value | Value जाँचने वाला function/rule |
| ValidationError | Error listing failing paths | Failing paths की सूची वाली error |
| `runValidators` | Enable validation on updates | Updates पर validation चालू करना |
| `kind` | Type of failure (min, enum...) | Failure का प्रकार |
| Cross-field | Rule depending on other fields | दूसरे fields पर निर्भर rule |
| Async validator | Validator returning a Promise | Promise लौटाने वाला validator |
| `$jsonSchema` | Server-side validation rules | Server-side validation rules |

---

## ⚡ 3-Line Summary
English:
1. Declare rules in the schema (`required`, `min`, `enum`, `match`, custom `validate`) and catch `ValidationError.errors` per field.
2. Update queries skip validators unless `runValidators: true` (set it globally).
3. Use regular functions for `this`-based validators and unique indexes (not async validators) for uniqueness.

Hindi:
1. Rules schema में लिखो (`required`, `min`, `enum`, `match`, custom `validate`) और हर field के लिए `ValidationError.errors` पकड़ो।
2. Update queries validators skip करती हैं जब तक `runValidators: true` न हो (global रूप से set करो)।
3. `this` वाले validators के लिए regular functions और uniqueness के लिए unique indexes (async validators नहीं) इस्तेमाल करो।

---

## ➡️ Next Topic
**84. Mongoose Middleware (hooks)** — `pre`/`post` hooks for save, find, update and aggregate.
