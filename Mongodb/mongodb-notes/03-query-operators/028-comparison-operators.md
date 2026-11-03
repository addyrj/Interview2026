# 28. Comparison Operators ($eq, $gt, $in, $nin)
# हिंदी में: Comparison Operators ($eq, $gt, $in, $nin)

---

## 🔵 Simple Definition (English)
**Comparison operators** compare a field's value with a given value inside a query filter: `$eq` (equal), `$ne` (not equal), `$gt` / `$gte` (greater / greater-or-equal), `$lt` / `$lte` (less / less-or-equal), `$in` (matches any value in a list) and `$nin` (matches none in a list). They are written as `{ field: { $op: value } }`. `{ field: value }` is shorthand for `$eq`.

## 🔵 सरल परिभाषा (Hindi)
**Comparison operators** query filter में किसी field की value की तुलना देते गए value से करते हैं: `$eq` (बराबर), `$ne` (बराबर नहीं), `$gt` / `$gte` (बड़ा / बड़ा-या-बराबर), `$lt` / `$lte` (छोटा / छोटा-या-बराबर), `$in` (list में से कोई भी value) और `$nin` (list में से कोई नहीं)। लिखने का तरीका `{ field: { $op: value } }`। `{ field: value }` असल में `$eq` का shorthand है।

---

## 🔴 Problem it Solves
Plain equality (`{ city: "Delhi" }`) is not enough for real queries: "dishes priced between 100 and 300", "restaurants in Delhi OR Hyderabad", "everything except these cities". Without comparison operators you would fetch all documents and filter in application code, wasting network and memory and bypassing indexes. These operators run **inside the database** and can use indexes (range scans for `$gt/$lt`, multiple point lookups for `$in`).

## 🔴 यह क्यों बना? (Hindi)
सिर्फ equality (`{ city: "Delhi" }`) असली queries के लिए काफी नहीं: "100 से 300 के बीच की dishes", "Delhi या Hyderabad के restaurants", "इन cities को छोड़कर सब"। Comparison operators के बिना सारे documents लाकर application code में filter करने पड़ते — network और memory की बर्बादी और index का फायदा भी नहीं। ये operators **database के अंदर** चलते हैं और indexes इस्तेमाल कर सकते हैं (`$gt/$lt` के लिए range scan, `$in` के लिए कई point lookups)।

---

## 🟢 How it Works — Step by Step

Step 1 → You write a filter: `{ price: { $gt: 100, $lte: 320 } }` (several operators on one field are AND-ed).
Step 2 → For each document the engine reads the field and compares using **BSON comparison order**: MinKey < Null < Numbers < Symbol/String < Object < Array < BinData < ObjectId < Boolean < Date < Timestamp < Regex < MaxKey.
Step 3 → **Type bracketing**: range operators (`$gt`, `$lt`...) only match values of the **same type bracket** as the operand. `{ price: { $gt: 100 } }` never matches the string `"80"` — nor a string `"500"`.
Step 4 → `$in` / `$nin` take an **array**; `$in` is like many `$eq` joined by OR. `$in` can also contain `null` or regexes.
Step 5 → **Arrays**: if the field is an array, the comparison succeeds when **any element** satisfies it.
Step 6 → **Missing fields**: `$ne` and `$nin` **also match documents where the field is missing** (and `$eq: null` matches both null and missing).
Step 7 → With an index on the field, MongoDB scans only the matching key range, not the entire collection.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Filter लिखो: `{ price: { $gt: 100, $lte: 320 } }` (एक field पर कई operators AND होते हैं)।
Step 2 → हर document की field को **BSON comparison order** से compare किया जाता है: MinKey < Null < Numbers < String < Object < Array < BinData < ObjectId < Boolean < Date < Timestamp < Regex < MaxKey।
Step 3 → **Type bracketing**: range operators (`$gt`, `$lt`...) सिर्फ उसी type की values से match करते हैं जिस type का operand है। `{ price: { $gt: 100 } }` string `"80"` या `"500"` से कभी match नहीं करेगा।
Step 4 → `$in` / `$nin` **array** लेते हैं; `$in` कई `$eq` को OR से जोड़ने जैसा है। `$in` में `null` या regex भी हो सकते हैं।
Step 5 → **Arrays**: field array हो तो comparison तब सफल है जब **कोई एक element** शर्त पूरी करे।
Step 6 → **Missing fields**: `$ne` और `$nin` उन documents से **भी match करते हैं जहाँ field मौजूद ही नहीं** (और `$eq: null` null व missing दोनों से match होता है)।
Step 7 → Field पर index हो तो MongoDB सिर्फ matching key range scan करता है, पूरा collection नहीं।

---

## 🟡 Real World Example
**Swiggy's search filters**: "Veg dishes under 200 rupees in Delhi or Hyderabad with rating above 4". The app builds `{ veg: true, price: { $lt: 200 }, city: { $in: ["Delhi", "Hyderabad"] }, rating: { $gt: 4 } }`. A compound index `{ city: 1, price: 1 }` lets MongoDB jump to the two city ranges and scan only prices below 200. "Exclude blacklisted cities" is a `$nin`. The classic bug: dishes with **no rating yet** vanish from `$gt: 4` (correct) but **appear** in `$ne: 4.5` (surprising).

## 🟡 Real Example Hindi mein
**Swiggy के search filters**: "Delhi या Hyderabad में 200 रुपये से कम की veg dishes, rating 4 से ऊपर"। App `{ veg: true, price: { $lt: 200 }, city: { $in: ["Delhi", "Hyderabad"] }, rating: { $gt: 4 } }` बनाता है। Compound index `{ city: 1, price: 1 }` से MongoDB सीधे दो city ranges पर जाकर 200 से कम prices ही scan करता है। "Blacklisted cities हटाओ" एक `$nin` है। क्लासिक bug: जिन dishes की **अभी rating नहीं है** वे `$gt: 4` से गायब होती हैं (सही), पर `$ne: 4.5` में **दिखती** हैं (चौंकाने वाला)।

---

## 💻 Code Example — Basic (mongosh, MongoDB 8.0.4, all outputs real)

```javascript
// Seed data used in topics 28-36 (4 dishes). Each line commented in the first insert.
const d = db.getSiblingDB("food");
d.dropDatabase();
d.dishes.insertMany([
 { _id:1, name:"Paneer Tikka",    price:220,  veg:true,  rating:4.5,  tags:["starter","paneer","spicy"], city:"Delhi",     stock:10, cost:150 },
 { _id:2, name:"Chicken Biryani", price:320,  veg:false, rating:4.7,  tags:["main","rice","spicy"],     city:"Hyderabad", stock:0,  cost:340 },
 { _id:3, name:"Masala Dosa",     price:120,  veg:true,                tags:["main","south"],            city:"Bengaluru", stock:25, cost:60  }, // NO rating field
 { _id:4, name:"Gulab Jamun",     price:"80", veg:true,  rating:null, tags:["dessert"],                 city:"Delhi",     stock:7,  cost:30  }  // price is a STRING, rating null
]);
const names = c => JSON.stringify(c.toArray().map(x => x.name));   // helper: print only names

print(names(d.dishes.find({ price: { $eq: 220 } })));               // ["Paneer Tikka"]  ($eq same as {price:220})
print(names(d.dishes.find({ price: { $gt: 100, $lte: 320 } })));    // ["Paneer Tikka","Chicken Biryani","Masala Dosa"]
//   -> Gulab Jamun (price "80" string) is skipped: type bracketing, strings never match numeric ranges
print(names(d.dishes.find({ city: { $in: ["Delhi", "Hyderabad"] } })));  // ["Paneer Tikka","Chicken Biryani","Gulab Jamun"]
print(names(d.dishes.find({ city: { $nin: ["Delhi"] } })));         // ["Chicken Biryani","Masala Dosa"]
print(names(d.dishes.find({ rating: { $gt: 4 } })));                // ["Paneer Tikka","Chicken Biryani"]
print(names(d.dishes.find({ rating: { $ne: 4.5 } })));              // ["Chicken Biryani","Masala Dosa","Gulab Jamun"]
//   -> Masala Dosa (rating MISSING) and Gulab Jamun (rating null) match $ne !
print(names(d.dishes.find({ rating: { $in: [null] } })));           // ["Masala Dosa","Gulab Jamun"]  (null matches missing too)
```

## 💻 Code Example — Advanced

```javascript
// 1) Range on dates / ObjectIds works the same way (BSON order)
db.orders.find({ createdAt: { $gte: ISODate("2026-01-01"), $lt: ISODate("2026-02-01") } }); // half-open range = January

// 2) $in with many ids (use for "fetch these N documents")
db.dishes.find({ _id: { $in: [1, 3] } });          // two point lookups on the _id index

// 3) Compare against ARRAY fields: matches if ANY element satisfies ALL sub-conditions on SAME or DIFFERENT elements
db.scores.find({ marks: { $gt: 90, $lt: 95 } });   // {marks:[95, 80]}? 95 satisfies $gt, 80 satisfies $lt => MATCHES! (use $elemMatch to force same element, topic 32)

// 4) Explain: confirm index range scan
db.dishes.createIndex({ price: 1 });
db.dishes.find({ price: { $gt: 100, $lte: 320 } }).explain("queryPlanner").queryPlanner.winningPlan.stage;
// "FETCH" with inputStage "IXSCAN" and indexBounds [[100, 320]]  (numbers bracket only)

// 5) $in vs $or on the same field: equivalent; $in is shorter and optimised
db.dishes.find({ $or: [{ city: "Delhi" }, { city: "Hyderabad" }] });  // same as $in above
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Build a filter safely from query-string params: /api/dishes?minPrice=100&maxPrice=300&cities=Delhi,Hyderabad
app.get('/api/dishes', async (req, res) => {
  const { minPrice, maxPrice, cities } = req.query;
  const filter = {};
  if (minPrice || maxPrice) {
    filter.price = {};
    if (minPrice) filter.price.$gte = Number(minPrice);   // Number()! query params are STRINGS
    if (maxPrice) filter.price.$lte = Number(maxPrice);   // else "300" string never matches numeric prices
  }
  if (cities) filter.city = { $in: cities.split(',') };   // comma list -> array for $in
  const dishes = await Dish.find(filter).sort({ price: 1 }).limit(50).lean();
  res.json(dishes);
});
// Mongoose casts for you if the schema says price: Number (strings like "300" become 300),
// but the raw driver does NOT cast. Also beware NoSQL injection: ?price[$gt]= is parsed by Express as an object;
// sanitize with express-mongo-sanitize or validate types.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Comparing against the wrong type
```javascript
// Wrong — price stored as number, but query uses string from req.query
db.dishes.find({ price: { $gt: "100" } });   // only matches STRING prices greater than "100"

// Right
db.dishes.find({ price: { $gt: 100 } });
```

❌ Mistake 2: Expecting `$ne` / `$nin` to ignore documents missing the field
✅ Correct: they match documents where the field is **absent or null**. Add `{ field: { $exists: true } }` if you only want documents that have it.

❌ Mistake 3: Passing a non-array to `$in`
```javascript
db.dishes.find({ city: { $in: "Delhi" } });   // Error: $in needs an array
db.dishes.find({ city: { $in: ["Delhi"] } }); // Right
```

❌ Mistake 4: Writing the same operator key twice in one object
✅ Correct: `{ price: { $gt: 1 }, price: { $lt: 9 } }` — the second `price` overwrites the first in JS. Use `{ price: { $gt: 1, $lt: 9 } }`.

---

## 🧠 Tricky Interview Question

```javascript
db.dishes.find({ rating: { $ne: 4.5 } })   // dishes: rating 4.5, 4.7, missing, null
```
Answer: Returns **three** documents (4.7, missing, null) — only the one with `4.5` is excluded. `$ne` is "not equal", and a missing field or `null` is certainly "not 4.5". Verified output: `["Chicken Biryani","Masala Dosa","Gulab Jamun"]`. Related trap: `{ rating: { $gt: 4 } }` returns only the two numeric ratings; null and missing are never "greater than 4" because of type bracketing. Also, `$ne` cannot use an index efficiently (it must scan nearly the whole index).

---

## ⚫ Interview Questions + Answers

Q1: What is type bracketing in comparisons?
A1: Range operators (`$gt`, `$lt`, `$gte`, `$lte`) only compare values within the same BSON type bracket (all numbers together, all strings together...). So `{ x: { $gt: 5 } }` never returns a document where `x` is the string "9". `$eq`/`$in` match by exact type/value (numeric types like int/long/double compare equal by value).

Q2: Difference between `$in` and `$or`?
A2: For one field they are equivalent; `$in` is shorter, and the optimiser treats it as multiple index point lookups. `$or` is needed when different fields are involved.

Q3: What does `{ field: null }` match?
A3: Documents where the field is `null` **or missing**. To match only explicit null use `{ field: { $type: "null" } }`; to match only missing use `{ field: { $exists: false } }`.

Q4: How do comparison operators behave on array fields?
A4: The condition is true if **any element** meets it. With multiple conditions on one array field (`{ $gt:90, $lt:95 }`) different elements may satisfy different conditions; use `$elemMatch` to require one element to satisfy all.

Q5: Can `$nin` / `$ne` use indexes?
A5: They can use an index but are not selective (they match almost everything), so the planner often scans the full index or collection. Prefer positive conditions (`$in`) when possible.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Filtering by ranges (price, date, age) or by sets (`$in` for ids, cities, statuses)
- You want the database (and indexes) to do the filtering

❌ Avoid when:
- Using `$ne`/`$nin` as the main selective filter on a big collection (slow, low selectivity)
- Stored types are inconsistent (strings and numbers mixed): fix the data first (`$type` can find the bad ones)
- A huge `$in` list (tens of thousands) — use a join/lookup or batch the ids

---

## 📊 Visual Diagram
```
 BSON sort order (low ─────────────────────────────────────► high)
 MinKey < Null < NUMBERS < STRINGS < Object < Array < BinData < ObjectId < Bool < Date < ... < MaxKey

 { price: { $gt: 100 } }  looks ONLY in the NUMBERS bracket:
      NUMBERS:  80  120  220  320      → matches 120,220,320
      STRINGS: "80" "500"              → never matched by $gt:100 (different bracket)

 $in  [a,b,c]  = field==a OR field==b OR field==c
 $nin [a,b,c]  = NOT(any of those)  → includes docs where field is missing!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$eq` / `$ne` | Equal / not equal | बराबर / बराबर नहीं |
| `$gt`,`$gte`,`$lt`,`$lte` | Range comparisons | Range तुलना |
| `$in` / `$nin` | In / not in a list | List में / list में नहीं |
| Type bracketing | Range ops compare same-type values only | Range ops सिर्फ same type compare करते हैं |
| BSON order | Cross-type sort order | अलग types का sort क्रम |
| Selectivity | How much a filter narrows results | Filter कितना narrow करता है |
| Index bounds | Key range scanned in an index | Index में scan होने वाली range |

---

## ⚡ 3-Line Summary
English:
1. Comparison operators (`$eq $ne $gt $gte $lt $lte $in $nin`) filter by value or range inside the database and can use indexes.
2. Range operators obey type bracketing: strings never match numeric ranges; `$ne`/`$nin` also match missing/null fields.
3. Convert query-string values with `Number()` and use `$in` for sets instead of looping.

Hindi:
1. Comparison operators (`$eq $ne $gt $gte $lt $lte $in $nin`) database के अंदर value या range से filter करते हैं और index इस्तेमाल कर सकते हैं।
2. Range operators type bracketing मानते हैं: string कभी numeric range से match नहीं होता; `$ne`/`$nin` missing/null fields से भी match करते हैं।
3. Query-string values को `Number()` से बदलो और sets के लिए loop की जगह `$in` लो।

---

## ➡️ Next Topic
**29. Logical Operators ($and, $or, $not, $nor)** — combining conditions.
