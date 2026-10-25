# 161. Mongoose Schema + Model
# हिंदी में: Mongoose Schema + Model — Document Structure Define करना

---

## 🔵 Simple Definition (English)
A **Mongoose Schema** defines the shape of documents in a collection — field names, types (`String`, `Number`, `Date`, `ObjectId`, arrays, nested objects), validation rules (`required`, `min`, `max`, `match`), and defaults. A **Model** is created by compiling a schema with `mongoose.model(name, schema)` — it's the class you actually use to create, query, update, and delete documents, with the schema's rules enforced automatically.

## 🔵 सरल परिभाषा (Hindi)
**Mongoose Schema** collection के documents की shape define करता है — field names, types (`String`, `Number`, `Date`, `ObjectId`, arrays, nested objects), validation rules (`required`, `min`, `max`, `match`), और defaults। **Model** schema को `mongoose.model(name, schema)` से compile करके बनता है — यही class है जो documents create, query, update, delete करने के लिए इस्तेमाल होती है, schema के rules automatically enforce होते हैं।

---

## 🔴 Problem it Solves
Without a schema, every piece of code writing to a collection must independently remember the correct field names, types, and required fields — easy to get wrong across a large codebase, with no error until something breaks at read time. A Mongoose schema centralizes this contract in ONE place: once defined, EVERY create/update anywhere in the app is validated against it automatically, catching bugs (wrong type, missing required field, invalid enum value) immediately at write time instead of silently corrupting data.

## 🔴 यह क्यों बना? (Hindi)
Schema के बिना, collection में लिखने वाला हर code independently सही field names, types, required fields याद रखना पड़ता — बड़े codebase में गलती होना आसान, और error तब तक नहीं दिखता जब तक read time पर कुछ टूट न जाए। Mongoose schema इस contract को एक जगह centralize करता है — define करने के बाद, app में कहीं भी हर create/update automatically validate होता है, bugs write time पर ही पकड़ में आते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `new mongoose.Schema({ field: Type, ... }, options)` — define field types directly, or as objects with `{ type, required, default, ... }` for more control.
Step 2 → Supported types include: `String`, `Number`, `Boolean`, `Date`, `Buffer`, `mongoose.Schema.Types.ObjectId`, `Array`, nested sub-schemas, and `Mixed` (anything goes, use sparingly).
Step 3 → Add validators: built-in (`required`, `min`, `max`, `minlength`, `maxlength`, `match`, `enum`) or custom (`validate: { validator: fn, message: str }`).
Step 4 → Compile: `const Model = mongoose.model('ModelName', schema)` — Mongoose auto-pluralizes the name for the actual MongoDB collection (e.g., `'User'` → collection `users`).
Step 5 → Use schema options like `{ timestamps: true }` (auto `createdAt`/`updatedAt`), `{ versionKey: false }` (disable `__v`), or `strict: false` (allow extra fields not in schema).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `new mongoose.Schema({ field: Type, ... }, options)` — field types directly या `{ type, required, default }` object से define करो।
Step 2 → Supported types: `String`, `Number`, `Boolean`, `Date`, `ObjectId`, `Array`, nested sub-schemas, `Mixed`।
Step 3 → Validators add करो: built-in (`required`, `min`, `max`, `match`, `enum`) या custom (`validate: { validator, message }`)।
Step 4 → Compile करो: `mongoose.model('ModelName', schema)` — Mongoose collection name auto-pluralize करता है (`User` → `users`)।
Step 5 → Schema options: `{ timestamps: true }`, `{ versionKey: false }`, `strict: false`।

---

## 🟡 Real World Example
**Flipkart's seller-onboarding service** defines a `SellerSchema` with strict validation: `gstNumber` must match a specific regex pattern, `businessType` must be one of a fixed `enum` list (`'individual' | 'partnership' | 'private_limited'`), and `documents` is an array of sub-schemas (`{ type, url, verifiedAt }`). This schema acts as the single contract every onboarding form submission and admin edit must satisfy — malformed GST numbers or invalid business types are rejected immediately, before touching the database.

## 🟡 Real Example Hindi mein
**Flipkart की seller-onboarding service** `SellerSchema` define करती है strict validation के साथ: `gstNumber` एक specific regex pattern से match करना चाहिए, `businessType` fixed `enum` list में से एक होना चाहिए। ये schema हर onboarding form submission का single contract है — malformed GST numbers या invalid business types database तक पहुँचने से पहले ही reject हो जाते हैं।

---

## 💻 Code Example — Basic

```javascript
// mongoose-schema-basic.js
// npm install mongoose
const mongoose = require('mongoose');

// Schema with various field types and validation
const productSchema = new mongoose.Schema({
  name: { type: String, required: [true, 'Product name is required'], trim: true },
  price: { type: Number, required: true, min: [0, 'Price cannot be negative'] },
  category: { type: String, enum: ['electronics', 'fashion', 'grocery'], default: 'electronics' },
  inStock: { type: Boolean, default: true },
  tags: [String], // array of strings
  rating: { type: Number, min: 0, max: 5 },
}, {
  timestamps: true, // adds createdAt + updatedAt automatically
});

const Product = mongoose.model('Product', productSchema); // collection name: "products"

async function main() {
  await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/flipkart_demo');

  // Valid document
  const product = await Product.create({ name: 'Wireless Mouse', price: 599, tags: ['electronics', 'accessory'] });
  console.log('Created:', product.name, product.createdAt);

  // Invalid document — triggers multiple validation errors
  try {
    await Product.create({ name: '', price: -10, category: 'furniture' }); // invalid name, price, category
  } catch (err) {
    console.log('Validation errors:');
    Object.values(err.errors).forEach((e) => console.log(' -', e.message));
  }

  await mongoose.disconnect();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// mongoose-schema-advanced.js — nested sub-schemas, custom validators, schema options
const mongoose = require('mongoose');

// Sub-schema for embedded documents (no separate Model needed)
const addressSchema = new mongoose.Schema({
  street: String,
  city: { type: String, required: true },
  pincode: { type: String, match: [/^\d{6}$/, 'Pincode must be exactly 6 digits'] },
}, { _id: false }); // _id: false avoids generating a useless ObjectId for each embedded address

const sellerSchema = new mongoose.Schema({
  name: { type: String, required: true },
  gstNumber: {
    type: String,
    required: true,
    match: [/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/, 'Invalid GST number format'],
  },
  businessType: {
    type: String,
    enum: { values: ['individual', 'partnership', 'private_limited'], message: '{VALUE} is not a valid business type' },
  },
  address: addressSchema, // embedded sub-document
  documents: [{
    type: { type: String, enum: ['pan', 'gst', 'bank_proof'] },
    url: String,
    verified: { type: Boolean, default: false },
  }],
  // CUSTOM VALIDATOR — e.g., must have at least one verified document before activation
  isActive: {
    type: Boolean,
    default: false,
    validate: {
      validator: function (value) {
        if (value === true) {
          return this.documents.some((doc) => doc.verified);
        }
        return true;
      },
      message: 'Seller cannot be activated without at least one verified document',
    },
  },
}, { strict: true, versionKey: false }); // strict: reject unknown fields; versionKey: false disables __v

const Seller = mongoose.model('Seller', sellerSchema);

async function run() {
  await mongoose.connect(process.env.MONGO_URI);

  try {
    const seller = await Seller.create({
      name: 'Ramesh Traders',
      gstNumber: '22AAAAA0000A1Z5',
      businessType: 'partnership',
      address: { city: 'Bengaluru', pincode: '560001' },
      documents: [{ type: 'pan', url: 'https://...', verified: true }],
      isActive: true, // allowed because a verified document exists
    });
    console.log('Seller activated:', seller.isActive);

    // This should fail custom validation — trying to activate with no verified docs
    await Seller.create({
      name: 'Unverified Co',
      gstNumber: '22AAAAA0000A1Z5',
      documents: [{ type: 'pan', url: 'https://...', verified: false }],
      isActive: true,
    });
  } catch (err) {
    console.error('Validation failed:', err.message);
  } finally {
    await mongoose.disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express route relying entirely on schema validation for input safety
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

app.post('/api/products', async (req, res) => {
  try {
    const product = await Product.create(req.body); // schema validates req.body automatically
    res.status(201).json(product);
  } catch (err) {
    if (err.name === 'ValidationError') {
      const messages = Object.values(err.errors).map((e) => e.message);
      return res.status(400).json({ errors: messages });
    }
    res.status(500).json({ error: 'Server error' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming `strict: false` or default behavior silently drops unknown fields safely
✅ Correct: By default (`strict: true`), Mongoose SILENTLY DROPS fields not defined in the schema during save — it doesn't error, which can confuse developers expecting validation errors. Check your schema includes every field you intend to persist.
```javascript
// Schema only has { name: String }
await Product.create({ name: 'Pen', color: 'blue' }); // "color" is silently dropped, not an error!
```

❌ Mistake 2: Using `Number`/`String` as both the type shorthand AND expecting object-style options to apply
```javascript
// Wrong — this just sets type, no validation applied
price: Number

// Right — use object form when you need validation/defaults
price: { type: Number, required: true, min: 0 }
```

---

## 🧠 Tricky Interview Question

```javascript
const schema = new mongoose.Schema({ name: String });
const Model = mongoose.model('Thing', schema);

const doc = new Model({ name: 'Test', extraField: 'surprise' });
console.log(doc.extraField); // ???
console.log(doc.toObject()); // ???
```
Answer: `doc.extraField` is `undefined` — accessing it directly doesn't error, but Mongoose never assigned it because it's not in the schema (default `strict: true` mode ignores unknown fields when constructing a document). `doc.toObject()` similarly won't include `extraField`. This is different from the native MongoDB driver, which would have stored `extraField` as-is. Only with `strict: false` on the schema would Mongoose preserve and save arbitrary extra fields.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between the shorthand type syntax (`name: String`) and the object syntax (`name: { type: String, required: true }`)?
A1: Shorthand (`name: String`) just declares the TYPE with no additional rules. The object syntax lets you ALSO specify validators (`required`, `min`, `max`, `match`, `enum`), a `default` value, `unique` index creation, and more. Use shorthand only for simple, unconstrained fields; use object syntax whenever you need validation or defaults.

Q2: How does Mongoose derive the actual MongoDB collection name from a Model name?
A2: By default, Mongoose takes the model name (e.g., `'User'`), lowercases it, and pluralizes it using a built-in pluralization library — `'User'` → collection `users`, `'Category'` → `categories`. You can override this with the third argument to `mongoose.model(name, schema, collectionName)` if you need an exact custom collection name.

Q3: What is the difference between built-in validators and custom validators?
A3: Built-in validators (`required`, `min`, `max`, `minlength`, `maxlength`, `match`, `enum`) cover common constraints declaratively. Custom validators (`validate: { validator: fn, message: str }`) let you write ARBITRARY logic — e.g., checking a field's value against another field on the same document (`this.otherField`), or an async check against the database — for rules too complex for the built-ins to express.

Q4: What does `{ _id: false }` do on a sub-schema, and when would you use it?
A4: By default, EVERY schema (including nested/embedded sub-schemas) automatically gets its own `_id` field (an `ObjectId`). For sub-documents embedded purely as structured data (like an `address` object that will never be queried/referenced independently), this extra `_id` is wasted overhead. Setting `{ _id: false }` on the sub-schema disables auto-generating an `_id` for each embedded instance.

Q5: Why would a field validation pass at the schema level but still fail to persist correctly in the database?
A5: Common causes: (1) validation only runs on `.save()`/`.create()` by default — direct query-based updates (`updateOne`) skip it unless `runValidators: true` is passed; (2) `strict: true` (default) silently drops fields not in the schema, which can look like "data loss" rather than a validation failure; (3) async custom validators that aren't properly awaited/returned can pass incorrectly if written wrong.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a single source of truth for document structure, validation, and defaults, enforced on every write
- Modeling nested/embedded data structures (addresses, line items) within a parent document
- You need custom business-rule validation beyond simple type checks

❌ Avoid when:
- You genuinely need per-document arbitrary, unpredictable shapes with zero validation overhead — use `strict: false` sparingly, or go closer to the native driver

---

## 📊 Visual Diagram
```
SCHEMA → MODEL COMPILATION
──────────────────────────────────────────────
  new mongoose.Schema({
    name: { type: String, required: true },
    price: { type: Number, min: 0 },
    address: addressSchema,       ◄── nested sub-schema
  }, { timestamps: true })
         │
         ▼
  mongoose.model('Product', schema)
         │
         ▼
  Product Model  ──▶  collection: "products" (auto-pluralized)
         │
         ├── Product.create({...})     → validates → inserts
         ├── Product.find({...})       → queries
         └── Product.updateOne({...})  → skips validation unless runValidators: true
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Document structure blueprint | Document structure का blueprint |
| Model | Compiled, usable interface | Compiled, usable interface |
| required | Field must be present | Field ज़रूरी है |
| enum | Fixed set of allowed values | Fixed values का set |
| strict mode | Drops fields not in schema | Schema में न हो तो field drop |
| sub-schema | Nested embedded document structure | Nested embedded document structure |
| runValidators | Enables validation on queries | Queries पर validation enable |

---

## ⚡ 3-Line Summary
English:
1. A Mongoose Schema defines field types, validators, and defaults; a Model is the compiled, usable interface built from it.
2. By default, unknown fields are silently dropped (`strict: true`), and validators only run automatically on `.save()`/`.create()`, not on query-based updates.
3. Use object-syntax fields (`{ type, required, min, enum }`) and custom validators for real-world business rules beyond basic type checks.

Hindi:
1. Mongoose Schema field types, validators, defaults define करती है; Model उससे compiled, usable interface है।
2. Default में unknown fields silently drop होते (`strict: true`), validators सिर्फ `.save()`/`.create()` पर automatically चलते हैं।
3. Real-world business rules के लिए object-syntax fields और custom validators इस्तेमाल करो।

---

## ➡️ Next Topic
**162. Mongoose CRUD** — Create, Read, Update, Delete patterns with Mongoose Models, including query chaining and lean queries.
