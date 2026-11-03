# 29. Logical Operators ($and, $or, $not, $nor)
# हिंदी में: Logical Operators ($and, $or, $not, $nor)

---

## 🔵 Simple Definition (English)
**Logical operators** combine multiple conditions. `$and` (all must be true), `$or` (at least one true), `$nor` (none true) each take an **array of filter documents**. `$not` is different: it **negates a single operator expression on one field** (`{ price: { $not: { $gt: 200 } } }`). Listing several fields in one filter object is already an implicit `$and`.

## 🔵 सरल परिभाषा (Hindi)
**Logical operators** कई conditions को जोड़ते हैं। `$and` (सभी सही), `$or` (कम से कम एक सही), `$nor` (कोई भी सही नहीं) — तीनों **filter documents का array** लेते हैं। `$not` अलग है: यह **एक field पर एक operator expression को उलट देता है** (`{ price: { $not: { $gt: 200 } } }`)। एक filter object में कई fields लिखना पहले से implicit `$and` है।

---

## 🔴 Problem it Solves
Real searches are rarely one condition: "veg AND under 200", "Delhi OR expensive", "not vegetarian and not out of stock". A plain filter object can express only AND across *different* fields. It cannot express OR, cannot repeat the same field key twice (JS/JSON objects overwrite duplicate keys), and cannot negate a condition. Logical operators fill these gaps.

## 🔴 यह क्यों बना? (Hindi)
असली searches में शायद ही एक condition होती है: "veg AND 200 से कम", "Delhi OR महंगी", "न veg और न out of stock"। साधारण filter object सिर्फ *अलग* fields पर AND बोल सकता है। यह OR नहीं बोल सकता, एक ही field की key दो बार नहीं लिख सकता (JS/JSON में duplicate key overwrite हो जाती है), और किसी condition को उलट नहीं सकता। Logical operators यही कमी पूरी करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Implicit AND: `{ veg: true, city: "Delhi" }` means both must hold.
Step 2 → `$and: [ {..}, {..} ]` is explicit AND. It is **required** when you need the same field/operator key twice, e.g. `{ tags: "spicy" }` and `{ tags: "starter" }`.
Step 3 → `$or: [ {..}, {..} ]` returns documents matching **any** clause. Each clause can use its own index (the planner can union index scans), so for best speed every branch should be indexed.
Step 4 → `$nor: [ {..}, {..} ]` returns documents matching **none** of the clauses (NOT-OR). It also matches documents where the clause fields are missing.
Step 5 → `$not` wraps an **operator expression**: `{ price: { $not: { $gt: 200 } } }` = price is not greater than 200 — **including** docs where `price` is missing, null or of another type.
Step 6 → Logical operators nest: `$or` inside `$and` inside `$or`. The maximum nesting depth is 100 levels.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Implicit AND: `{ veg: true, city: "Delhi" }` का मतलब दोनों सही होने चाहिए।
Step 2 → `$and: [ {..}, {..} ]` explicit AND है। जब एक ही field/operator key दो बार चाहिए, जैसे `{ tags: "spicy" }` और `{ tags: "starter" }`, तब यह **ज़रूरी** है।
Step 3 → `$or: [ {..}, {..} ]` उन documents को लौटाता है जो **कोई भी** clause match करें। हर clause अपना index इस्तेमाल कर सकता है (planner index scans का union कर सकता है), इसलिए तेज़ी के लिए हर branch पर index हो।
Step 4 → `$nor: [ {..}, {..} ]` उन documents को लौटाता है जो **कोई भी** clause match **न** करें (NOT-OR)। जिन documents में clause की field नहीं है वे भी match होते हैं।
Step 5 → `$not` एक **operator expression** को wrap करता है: `{ price: { $not: { $gt: 200 } } }` = price 200 से बड़ा नहीं है — इसमें वे docs भी आते हैं जहाँ `price` missing, null या दूसरे type की है।
Step 6 → Logical operators nest हो सकते हैं: `$or` के अंदर `$and` के अंदर `$or`। अधिकतम nesting depth 100 है।

---

## 🟡 Real World Example
**Zomato "Order Now" listing**: show restaurants that are open AND (have free delivery OR rating >= 4.5) AND are NOT on the suspended list. Query: `{ $and: [ { open: true }, { $or: [ { freeDelivery: true }, { rating: { $gte: 4.5 } } ] }, { $nor: [ { status: "suspended" } ] } ] }`. The ops team also runs a cleanup: "find dishes that are neither vegetarian nor in stock" using `$nor`.

## 🟡 Real Example Hindi mein
**Zomato "Order Now" listing**: ऐसे restaurants दिखाओ जो open हों AND (free delivery हो OR rating >= 4.5) AND suspended list में NOT हों। Query: `{ $and: [ { open: true }, { $or: [ { freeDelivery: true }, { rating: { $gte: 4.5 } } ] }, { $nor: [ { status: "suspended" } ] } ] }`। Ops team की cleanup में "ऐसी dishes जो न veg हैं न stock में" `$nor` से निकाली जाती हैं।

---

## 💻 Code Example — Basic (mongosh, MongoDB 8.0.4; uses seed data from topic 28)

```javascript
const d = db.getSiblingDB("food");
const names = c => JSON.stringify(c.toArray().map(x => x.name));

// $and : veg AND price < 200
print(names(d.dishes.find({ $and: [ { veg: true }, { price: { $lt: 200 } } ] })));
// ["Masala Dosa"]    (Gulab Jamun is veg but price "80" is a string, so $lt:200 doesn't match)

// $or : in Delhi OR price > 300
print(names(d.dishes.find({ $or: [ { city: "Delhi" }, { price: { $gt: 300 } } ] })));
// ["Paneer Tikka","Chicken Biryani","Gulab Jamun"]

// $not : price NOT greater than 200  (note: negates an OPERATOR, on one field)
print(names(d.dishes.find({ price: { $not: { $gt: 200 } } })));
// ["Masala Dosa","Gulab Jamun"]   -> Gulab Jamun's price is a string, so "not > 200" is TRUE for it

// $nor : neither vegetarian NOR out of stock (stock == 0)
print(names(d.dishes.find({ $nor: [ { veg: true }, { stock: 0 } ] })));
// []   -> Biryani is non-veg but stock is 0, all others are veg => nobody qualifies

// Same field twice => need $and (a plain object would overwrite the key)
print(names(d.dishes.find({ $and: [ { tags: "spicy" }, { tags: "starter" } ] })));
// ["Paneer Tikka"]
```

## 💻 Code Example — Advanced

```javascript
// 1) Nested: open AND (freeDelivery OR rating >= 4.5) AND NOT suspended
db.restaurants.find({
  $and: [
    { open: true },                                              // clause 1
    { $or: [ { freeDelivery: true }, { rating: { $gte: 4.5 } } ] }, // clause 2: OR nested in AND
    { $nor: [ { status: "suspended" } ] }                        // clause 3: NOT suspended
  ]
});

// 2) $not with regex (a classic use): names NOT starting with "P"
db.dishes.find({ name: { $not: /^P/ } });
//   -> Chicken Biryani, Masala Dosa, Gulab Jamun

// 3) $not vs $ne: $ne takes a VALUE, $not takes an OPERATOR EXPRESSION
db.dishes.find({ city: { $ne: "Delhi" } });            // value negation
db.dishes.find({ price: { $not: { $gt: 200 } } });     // operator negation

// 4) Index-friendly OR: each branch needs its own index to avoid a COLLSCAN
db.dishes.createIndex({ city: 1 });
db.dishes.createIndex({ price: 1 });
db.dishes.find({ $or: [ { city: "Delhi" }, { price: { $gt: 300 } } ] })
  .explain("queryPlanner").queryPlanner.winningPlan.stage;   // "SUBPLAN"/"OR" plan using both indexes (not COLLSCAN)

// 5) De Morgan: $nor [A,B] === $and [ {$not A}, {$not B} ] (conceptually)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Dynamic filter builder: only add clauses the client asked for
app.get('/api/restaurants', async (req, res) => {
  const { open, freeDelivery, minRating, excludeStatus } = req.query;
  const and = [];                                            // collect clauses, then join with $and
  if (open === 'true') and.push({ open: true });
  if (freeDelivery === 'true' || minRating) {
    const or = [];
    if (freeDelivery === 'true') or.push({ freeDelivery: true });
    if (minRating) or.push({ rating: { $gte: Number(minRating) } });
    and.push({ $or: or });                                   // $or must be a NON-EMPTY array
  }
  if (excludeStatus) and.push({ $nor: [{ status: excludeStatus }] });
  const filter = and.length ? { $and: and } : {};            // $and: [] is an ERROR, so guard it
  res.json(await Restaurant.find(filter).limit(50).lean());
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Duplicate keys in the filter object
```javascript
// Wrong — JS keeps only the LAST "tags"; query silently becomes { tags: "starter" }
db.dishes.find({ tags: "spicy", tags: "starter" });

// Right
db.dishes.find({ $and: [ { tags: "spicy" }, { tags: "starter" } ] });
// or for arrays: db.dishes.find({ tags: { $all: ["spicy", "starter"] } });
```

❌ Mistake 2: Passing an empty array
✅ Correct: `$and: []`, `$or: []`, `$nor: []` throw "must be a nonempty array". Build the filter conditionally.

❌ Mistake 3: Using `$not` where you meant `$nor` (or `$ne`)
```javascript
db.dishes.find({ $not: { veg: true } });   // ERROR: $not cannot be top-level; it needs a field
db.dishes.find({ $nor: [ { veg: true } ] });   // Right: top-level negation
```

❌ Mistake 4: Assuming `$not: {$gt: 200}` only returns numbers <= 200
✅ Correct: it also returns missing/null/other-type values (see Gulab Jamun with string price in the real run).

---

## 🧠 Tricky Interview Question

```javascript
db.dishes.find({ $nor: [ { veg: true }, { stock: 0 } ] })
// dishes: Paneer(veg,stock10) Biryani(non-veg,stock0) Dosa(veg,25) Jamun(veg,7)
```
Answer: Returns **nothing** (verified: `[]`). `$nor` returns documents that fail **every** clause: not veg AND stock not 0. Biryani fails the veg clause (good) but matches `stock: 0` (so it is excluded). All others are veg. A common wrong answer is "Biryani" — mixing up `$nor` with `$or` on negations. Remember `$nor [A,B]` = `NOT A AND NOT B`.

---

## ⚫ Interview Questions + Answers

Q1: When do you need an explicit `$and`?
A1: When the same field or the same operator must appear twice (e.g. two `$or` clauses, or `tags: "a"` and `tags: "b"`), because object keys must be unique. For different fields the implicit AND of a normal filter object is enough.

Q2: How does `$or` use indexes?
A2: Each branch is planned independently; if **every** branch can use an index, MongoDB unions the index scans (OR stage). If any branch has no usable index, the whole query becomes a collection scan.

Q3: Difference between `$not` and `$nor`?
A3: `$not` negates one operator expression on one field (`{ f: { $not: {...} } }`). `$nor` is a top-level operator taking an array of whole filters and returns documents matching none of them.

Q4: Does `$not` match documents without the field?
A4: Yes. `{ price: { $not: { $gt: 200 } } }` matches docs with price <= 200 and also docs where price is missing, null or a non-numeric type.

Q5: What is the evaluation order inside `$and` / `$or`?
A5: The query planner decides; do not rely on order or short-circuiting. Put selective, indexed conditions in the query shape (compound index) rather than counting on clause order.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need OR across different fields (`$or`), or the same field key twice (`$and`)
- Excluding multiple conditions at once (`$nor`)
- Negating an operator or regex (`$not`)

❌ Avoid when:
- A single `$in` covers it (`$or` on one field is longer and no faster)
- Branches are unindexed on a large collection (full scan)
- A `$all`/`$in` array operator expresses the intent more clearly

---

## 📊 Visual Diagram
```
  { A, B }                 implicit AND         ──►  A ∧ B
  { $and:[A,B] }           explicit AND         ──►  A ∧ B  (needed for repeated keys)
  { $or:[A,B] }            union                ──►  A ∨ B  (each branch can use its own index)
  { $nor:[A,B] }           none of them         ──►  ¬A ∧ ¬B
  { f: { $not: {op} } }    negate one operator  ──►  ¬(f op)   (matches missing f too)

  Venn:  [ A (  A∩B  ) B ]
  $or  = whole union   $and = overlap only   $nor = everything OUTSIDE both circles
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$and` | All conditions true | सभी conditions सही |
| `$or` | Any condition true | कोई एक condition सही |
| `$nor` | No condition true | कोई condition सही नहीं |
| `$not` | Negate one operator expression | एक operator expression उलटो |
| Implicit AND | Multiple fields in one object | एक object में कई fields = AND |
| Clause | One filter document inside the array | Array के अंदर एक filter document |
| De Morgan | ¬(A∨B) = ¬A∧¬B | De Morgan का नियम |

---

## ⚡ 3-Line Summary
English:
1. `$and`, `$or`, `$nor` take non-empty arrays of filters; `$not` negates a single operator on one field.
2. Use explicit `$and` when keys repeat; `$or` is fast only if every branch is indexed.
3. `$not`/`$nor` also match documents with missing fields, so check results carefully.

Hindi:
1. `$and`, `$or`, `$nor` filters के non-empty array लेते हैं; `$not` एक field के एक operator को उलटता है।
2. Keys दोहराई जाएँ तो explicit `$and` लो; `$or` तभी तेज़ है जब हर branch पर index हो।
3. `$not`/`$nor` missing fields वाले documents से भी match करते हैं, इसलिए results ध्यान से जाँचो।

---

## ➡️ Next Topic
**30. Element Operators ($exists, $type)** — querying by field presence and data type.
