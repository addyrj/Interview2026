# 75. Schema Validation ($jsonSchema)
# हिंदी में: Schema Validation ($jsonSchema)

---

## 🔵 Simple Definition (English)
**Schema validation** lets the MongoDB server itself reject (or warn about) inserts and updates that don't match rules you define on a collection. The rules are set with the `validator` option, most commonly written with the **`$jsonSchema`** operator (required fields, `bsonType`, `minimum`, `pattern`, `enum`, array limits...). Two knobs control behaviour: **`validationLevel`** (`strict` = all inserts/updates, `moderate` = only documents that already valid, `off`) and **`validationAction`** (`error` = reject, `warn` = allow and log). Verified on MongoDB 8.0.4.

## 🔵 सरल परिभाषा (Hindi)
**Schema validation** से MongoDB server खुद उन inserts और updates को reject (या warn) करता है जो collection पर आपके बनाए नियमों से मेल नहीं खाते। नियम `validator` option से सेट होते हैं, जो अक्सर **`$jsonSchema`** operator से लिखे जाते हैं (required fields, `bsonType`, `minimum`, `pattern`, `enum`, array limits...)। दो knobs व्यवहार तय करते हैं: **`validationLevel`** (`strict` = सभी inserts/updates, `moderate` = सिर्फ़ वे documents जो पहले से valid हैं, `off`) और **`validationAction`** (`error` = reject, `warn` = allow और log)।

---

## 🔴 Problem it Solves
"Schemaless" means any app, script or admin console can insert `{ price: "free" }` or forget `sku`. Bad data then breaks reports, invoices and other services days later. App-level checks (Mongoose, Joi) protect only that one app; a second microservice, a shell fix-up script or a data import bypasses them. Database-level validation is the last line of defense, shared by all writers.

## 🔴 यह क्यों बना? (Hindi)
"Schemaless" का मतलब कोई भी app, script या admin console `{ price: "free" }` डाल सकता है या `sku` भूल सकता है। Bad data दिनों बाद reports, invoices और दूसरी services को तोड़ता है। App-level checks (Mongoose, Joi) सिर्फ़ उसी app को बचाते हैं; दूसरा microservice, shell fix-up script या data import उन्हें bypass कर देता है। Database-level validation सभी writers के लिए साझा आख़िरी सुरक्षा है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define the rules: `db.createCollection(name, { validator: { $jsonSchema: {...} } })` or add to an existing one with `collMod`.
Step 2 → On every insert and update MongoDB evaluates the validator against the **resulting document**.
Step 3 → `validationLevel: "strict"` (default) checks all writes; `"moderate"` skips updates to existing documents that already violate the rules (useful while cleaning legacy data); `"off"` disables.
Step 4 → `validationAction: "error"` (default) rejects the write with **error code 121 "Document failed validation"** and `errInfo.details` explaining which rule failed; `"warn"` lets the write through and logs a warning in the server log.
Step 5 → Roll out safely: start with `warn`, check logs/queries for violators (`db.coll.find({ $nor: [ { $jsonSchema: ... } ] })`), fix data, then switch to `error`.
Step 6 → Bypass only for admins with `bypassDocumentValidation: true` (needs privilege). Note: `_id`-level things like unique constraints are **indexes**, not validators.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → नियम define करो: `db.createCollection(name, { validator: { $jsonSchema: {...} } })` या मौजूदा collection पर `collMod`।
Step 2 → हर insert और update पर MongoDB validator को **नतीजे वाले document** पर चलाता है।
Step 3 → `validationLevel: "strict"` (default) सभी writes जाँचता है; `"moderate"` उन मौजूदा documents के updates छोड़ देता है जो पहले से नियम तोड़ते हैं (legacy data साफ़ करते समय काम का); `"off"` बंद।
Step 4 → `validationAction: "error"` (default) write को **error code 121 "Document failed validation"** से reject करता है और `errInfo.details` बताता है कौन सा नियम टूटा; `"warn"` write पास होने देता है और server log में warning लिखता है।
Step 5 → सुरक्षित rollout: पहले `warn`, फिर violators ढूँढो (`db.coll.find({ $nor: [ { $jsonSchema: ... } ] })`), data ठीक करो, फिर `error`।
Step 6 → सिर्फ़ admins `bypassDocumentValidation: true` से bypass कर सकते हैं (privilege चाहिए)। ध्यान: unique constraints **indexes** हैं, validator नहीं।

---

## 🟡 Real World Example
**Flipkart catalog service**: the `products` collection is written by seller uploads, an admin tool, and a price-sync service. The validator requires `name` (string, min 2 chars), `price` (number ≥ 0) and `sku` matching `^[A-Z]{3}-[0-9]{3}$`, and limits `tags` to 5 strings. A buggy sync script that sends `price: "1,299"` (a string) is stopped by the database with code 121 instead of silently corrupting the catalog.

## 🟡 Real Example Hindi mein
**Flipkart catalog service**: `products` collection में seller uploads, admin tool और price-sync service लिखती हैं। Validator ज़रूरी करता है `name` (string, कम से कम 2 chars), `price` (number ≥ 0) और `sku` जो `^[A-Z]{3}-[0-9]{3}$` से मेल खाए, और `tags` में अधिकतम 5 strings। `price: "1,299"` (string) भेजने वाली buggy sync script को database code 121 के साथ रोक देता है, catalog चुपचाप खराब नहीं होता।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4)
use t75
db.createCollection("products", {
  validator: { $jsonSchema: {
    bsonType: "object",                                   // each document must be an object
    required: ["name", "price", "sku"],                   // these three fields must exist
    properties: {
      name:  { bsonType: "string", minLength: 2 },        // string of at least 2 characters
      price: { bsonType: ["double", "int", "decimal"], minimum: 0 }, // any numeric BSON type, not negative
      sku:   { bsonType: "string", pattern: "^[A-Z]{3}-[0-9]{3}$" },  // e.g. PHN-001
      tags:  { bsonType: "array", items: { bsonType: "string" }, maxItems: 5 } // optional, <=5 strings
    }
  } },
  validationLevel: "strict",                              // check every insert and update (default)
  validationAction: "error"                               // reject violations (default)
})

db.products.insertOne({ name: "Phone", price: 999, sku: "PHN-001" })   // valid
// Output: { acknowledged: true, insertedId: ObjectId('...') }          (ObjectId differs per run)

db.products.insertOne({ name: "P", price: -5, sku: "bad" })            // violates 3 rules
// Output (real): MongoServerError: Document failed validation   (code 121)
// err.errInfo.details.schemaRulesNotSatisfied -> propertiesNotSatisfied for:
//   name  : minLength 2 not satisfied, consideredValue "P"
//   price : minimum 0, comparison failed, consideredValue -5
//   sku   : pattern not matched
```

## 💻 Code Example — Advanced

```javascript
// mongosh — rolling out validation safely on an existing collection

// 1) Switch to WARN: writes pass, violations are logged (check mongod log, "Document failed validation")
db.runCommand({ collMod: "products", validationAction: "warn" })
db.products.insertOne({ name: "Warned", price: -1, sku: "x" })       // accepted despite violating rules
db.products.countDocuments()
// Output: 2    (verified: the invalid doc was inserted in warn mode)
db.getCollectionInfos({ name: "products" })[0].options.validationAction
// Output: 'warn'

// 2) Find violators to clean up: documents that do NOT satisfy the schema
db.products.find({ $nor: [ { $jsonSchema: {
  bsonType: "object", required: ["name", "price", "sku"],
  properties: { price: { bsonType: ["double", "int", "decimal"], minimum: 0 } } } } ] })
// Output: [ { name: 'Warned', price: -1, sku: 'x', tags: [ 'a' ] } ]  (verified; price -1 breaks minimum) -> fix or delete it
// (the tags field appears because step 3 below was run in our test before this query; yours may not have it)

// 3) MODERATE: new inserts are strict, but updating an already-invalid doc is allowed
db.runCommand({ collMod: "products", validationAction: "error", validationLevel: "moderate" })
db.products.updateOne({ name: "Warned" }, { $set: { tags: ["a"] } })
// Output: succeeds (verified) - legacy invalid doc may still be edited under 'moderate'

// 4) Strict array and type rules are enforced on new inserts
db.products.insertOne({ name: "Phone2", price: 1, sku: "PHN-002", tags: [1] })   // tags must be strings
// Output: MongoServerError: Document failed validation (code 121)
db.products.insertOne({ name: "ok", price: "1", sku: "PHN-003" })                 // price is a string
// Output: MongoServerError: Document failed validation (code 121)

// 5) Switch back to strict once data is clean
db.runCommand({ collMod: "products", validationLevel: "strict" })

// 6) Admin bypass (privileged), e.g. for a one-off import:
//    db.runCommand({ insert: "products", documents: [...], bypassDocumentValidation: true })
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

// Mongoose validates in the app BEFORE sending; the DB validator is the second line of defence.
const Product = mongoose.model('P', new Schema({
  name:  { type: String, required: true, minlength: 2 },
  price: { type: Number, required: true, min: 0 }
}));

const app = express();
app.use(express.json());

app.post('/p', async (req, res) => {
  try {
    res.status(201).json(await Product.create(req.body));
  } catch (e) {
    if (e.name === 'ValidationError') return res.status(400).json({ error: e.message });   // Mongoose validation
    if (e.code === 121) return res.status(400).json({ error: 'Rejected by DB validator', details: e.errInfo?.details }); // server validator
    res.status(500).json({ error: 'Server error' });
  }
});
// Real output for POST {"name":"P","price":-1}:
// 400 {"error":"P validation failed: name: Path `name` (`P`, length 1) is shorter than the minimum allowed length (2)., price: Path `price` (-1) is less than minimum allowed value (0)."}

// Create the collection WITH a server-side validator from Node (e.g. in a migration script):
async function createValidated(db) {
  await db.createCollection('products', {
    validator: { $jsonSchema: { bsonType: 'object', required: ['name', 'price'],
      properties: { price: { bsonType: ['double', 'int'], minimum: 0 } } } }
  });
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using JS type names instead of BSON type names
```javascript
// Wrong — $jsonSchema in MongoDB uses bsonType; "type" is JSON-schema type and doesn't know int/decimal/objectId/date
properties: { price: { type: "number" }, createdAt: { type: "date" } }   // "date" is not a JSON Schema type
// Right
properties: { price: { bsonType: ["double", "int", "decimal"] }, createdAt: { bsonType: "date" } }
```

❌ Mistake 2: Using `bsonType: "int"` for money/price fields
```javascript
// Wrong — verified in mongosh: { price: 10 } is stored as int32 and passes, but { price: 10.5 } (double) is rejected,
// and a Python/Java client sending 10.0 as a double is rejected too
price: { bsonType: "int" }
// Right — accept every numeric type you really use (or Decimal128 for money): bsonType: ["double","int","long","decimal"]
```
✅ Also: forgetting `additionalProperties: false` when you want to forbid unknown fields (and then you must list `_id` in `properties`), and flipping to `error` on a big dirty collection without first running in `warn`.

---

## 🧠 Tricky Interview Question

You change an existing collection's validator with `collMod`. Do existing documents that violate the new rules get rejected or removed?

Answer: No. Validation only runs on **inserts and updates**, never retroactively. Existing invalid documents stay in place and are still readable. With `validationLevel: "strict"`, any later **update** to such a document must produce a valid result (otherwise error 121) — so you can't even change an unrelated field until you fix the invalid one. With `"moderate"`, updates to already-invalid documents are skipped from validation (we verified updating the "Warned" doc succeeded), while new inserts and updates to valid docs are still checked.

---

## ⚫ Interview Questions + Answers

Q1: How is `$jsonSchema` different from Mongoose schema validation?
A1: Mongoose validates in the Node app and only for writes that go through Mongoose. `$jsonSchema` is enforced by `mongod` for every client (shell, other services, imports). Use both: Mongoose for friendly errors, the DB validator as the safety net.

Q2: What error does a failed validation return?
A2: `MongoServerError` with `code: 121` ("Document failed validation") and, since 5.0, `errInfo.details` listing `schemaRulesNotSatisfied`, the failing property, operator and `consideredValue`.

Q3: `validationLevel` strict vs moderate?
A3: `strict` applies to all inserts and updates. `moderate` applies to inserts and to updates of documents that already satisfy the validator; existing invalid docs can still be updated. `off` disables validation.

Q4: How do you add validation to an existing collection?
A4: `db.runCommand({ collMod: "products", validator: { $jsonSchema: {...} }, validationLevel: "moderate", validationAction: "warn" })`, check violators with `$nor: [{ $jsonSchema }]`, fix, then tighten to strict/error.

Q5: Can a validator enforce uniqueness or cross-document rules?
A5: No. It checks one document at a time. Uniqueness needs a unique index; cross-document consistency needs application logic or transactions. You can compare fields within the same document using `$expr` in a query validator.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- Several services write to the same collection
- Critical financial/identity data where wrong type = real loss
- During/after a migration to enforce the new `schemaVersion`

❌ Avoid / be careful:
- Early prototyping with a rapidly changing shape (use `warn`)
- Overly strict rules on rarely-needed optional fields (blocks legitimate writes)
- Expecting it to replace unique indexes or business-rule checks

---

## 📊 Visual Diagram
```
 insert / update
       │
       ▼
 ┌───────────────────────────┐
 │ validator ($jsonSchema)   │
 │  required? bsonType?      │
 │  min / pattern / enum?    │
 └───────┬───────────┬───────┘
     valid        invalid
       │               │
       ▼               ▼ validationAction
   written        "error" -> reject (code 121)
                  "warn"  -> write + log warning

 validationLevel: strict (all) | moderate (valid docs only) | off
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| validator | Rule set attached to a collection | Collection से जुड़े नियम |
| `$jsonSchema` | JSON-Schema-based rule operator | JSON Schema वाला operator |
| bsonType | BSON type name (string, int, date...) | BSON type का नाम |
| validationLevel | Which writes are checked | कौन से writes जाँचे जाएँ |
| validationAction | Reject or just warn | Reject या सिर्फ़ warn |
| Error 121 | Document failed validation | Validation fail होने का error |
| `collMod` | Modify collection options | Collection options बदलना |

---

## ⚡ 3-Line Summary
English:
1. `$jsonSchema` validators make `mongod` reject (error 121) or warn about documents that break your rules, for every client.
2. Roll out with `validationAction: "warn"` / `validationLevel: "moderate"`, clean violators with `$nor: [$jsonSchema]`, then enforce strictly.
3. Use `bsonType` (not `type`), remember validation is not retroactive and cannot replace unique indexes.

Hindi:
1. `$jsonSchema` validators हर client के लिए `mongod` से नियम तोड़ने वाले documents को reject (error 121) या warn कराते हैं।
2. `validationAction: "warn"` / `validationLevel: "moderate"` से rollout करो, `$nor: [$jsonSchema]` से violators साफ़ करो, फिर strict करो।
3. `bsonType` इस्तेमाल करो (`type` नहीं), याद रखो validation पीछे की तरफ़ लागू नहीं होता और unique index की जगह नहीं ले सकता।

---

## ➡️ Next Topic
**76. Tree Structures in MongoDB** — parent reference, child references, materialized path and `$graphLookup`.
