# 65. $expr, $cond, $switch Expressions
# हिंदी में: $expr, $cond, $switch Expressions

---

## 🔵 Simple Definition (English)
These three bring **logic** into MongoDB. **`$cond`** is if/else (ternary) inside an aggregation expression. **`$switch`** is a multi-branch if/else-if chain with an optional default. **`$expr`** lets query operators (`$match`, `find`) use aggregation expressions, so you can compare two fields of the same document or use `$cond` in a filter.

## 🔵 सरल परिभाषा (Hindi)
ये तीनों MongoDB में **logic** लाते हैं। **`$cond`** aggregation expression के अंदर if/else (ternary) है। **`$switch`** कई branches वाली if/else-if chain है जिसमें optional default होता है। **`$expr`** query operators (`$match`, `find`) को aggregation expressions इस्तेमाल करने देता है, ताकि एक ही document के दो fields compare कर सको या filter में `$cond` लगा सको।

---

## 🔴 Problem it Solves
Normal query filters compare a field with a CONSTANT (`amount > 400`). They cannot say "amount greater than the discount limit stored in the same document" or "label an order big or small". And conditional totals (sum only delivered amounts, but keep every customer) need logic inside `$group`. These expressions provide that.

## 🔴 यह क्यों बना? (Hindi)
Normal query filters field की तुलना CONSTANT से करते हैं (`amount > 400`)। वे "amount उसी document में रखी discount limit से ज़्यादा" या "order को big/small label करो" नहीं कह सकते। और conditional totals (सिर्फ delivered का जोड़, पर हर customer रखो) के लिए `$group` के अंदर logic चाहिए। ये expressions वही देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `$cond`: `{ $cond: [ <if>, <then>, <else> ] }` or `{ $cond: { if, then, else } }`.
Step 2 → `$switch`: `{ $switch: { branches: [ { case: <bool>, then: <value> }, ... ], default: <value> } }`. First true case wins.
Step 3 → If no case matches and there is NO `default`, `$switch` throws an error.
Step 4 → `$expr`: `{ $match: { $expr: { $gt: ["$amount", "$limit"] } } }`. Field references use `$`, and both sides come from the document.
Step 5 → Conditional accumulation: `{ $sum: { $cond: [ cond, "$amount", 0 ] } }` inside `$group`.
Step 6 → Also see `$ifNull` (replace null/missing) and `$and/$or/$not` to build conditions.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `$cond`: `{ $cond: [ <if>, <then>, <else> ] }` या `{ $cond: { if, then, else } }`।
Step 2 → `$switch`: `{ $switch: { branches: [ { case: <bool>, then: <value> }, ... ], default: <value> } }`। पहला true case जीतता है।
Step 3 → अगर कोई case match न हो और `default` भी न हो तो `$switch` error देता है।
Step 4 → `$expr`: `{ $match: { $expr: { $gt: ["$amount", "$limit"] } } }`। Field reference में `$` लगता है, और दोनों तरफ document से आते हैं।
Step 5 → Conditional accumulation: `$group` के अंदर `{ $sum: { $cond: [ cond, "$amount", 0 ] } }`।
Step 6 → `$ifNull` (null/missing बदलने के लिए) और condition बनाने के लिए `$and/$or/$not` भी देखो।

---

## 🟡 Real World Example
**Zomato's loyalty tiers**: each order is labelled Platinum/Gold/Silver by amount with `$switch`; the "free delivery" flag is `$cond` on `amount >= 400`; and a finance report uses `$expr` to find orders where `amount` exceeds the `creditLimit` stored on the same document. A revenue-by-customer report sums only delivered amounts via `$cond` but still lists customers with zero delivered orders.

## 🟡 Real Example Hindi mein
**Zomato के loyalty tiers**: हर order को amount के हिसाब से Platinum/Gold/Silver `$switch` से label किया जाता है; "free delivery" flag `amount >= 400` पर `$cond` है; और finance report `$expr` से वे orders ढूँढती है जहाँ `amount` उसी document के `creditLimit` से ज़्यादा है। Revenue-by-customer report `$cond` से सिर्फ delivered amounts जोड़ती है पर zero delivered वाले customers भी दिखाती है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4, shop.orders
db.orders.aggregate([
  { $project: {
      customer: 1, amount: 1,
      size: { $cond: [ { $gte: ["$amount", 400] }, "big", "small" ] },     // if/else
      tier: { $switch: {                                                   // multi-branch
        branches: [
          { case: { $gte: ["$amount", 800] }, then: "A" },                 // first true wins
          { case: { $gte: ["$amount", 300] }, then: "B" }
        ],
        default: "C"                                                       // everything else
      } }
  } },
  { $limit: 4 }
])
// Output (real):
// { _id: 1, customer: 'Aarav', amount: 450, size: 'big',   tier: 'B' }
// { _id: 2, customer: 'Diya',  amount: 230, size: 'small', tier: 'C' }
// { _id: 3, customer: 'Aarav', amount: 120, size: 'small', tier: 'C' }
// { _id: 4, customer: 'Kabir', amount: 890, size: 'big',   tier: 'A' }
```

## 💻 Code Example — Advanced

```javascript
// $expr in $match: compare with a computed value (works the same for two fields of one doc)
db.orders.aggregate([
  { $match: { $expr: { $gt: ["$amount", { $multiply: [200, 1.5] }] } } },  // amount > 300
  { $project: { amount: 1 } }
])
// Output (real): { _id: 1, amount: 450 }  { _id: 4, amount: 890 }  { _id: 5, amount: 310 }

// Conditional sum: every customer is kept, only delivered amounts are added
db.orders.aggregate([
  { $group: { _id: "$customer",
      delivered: { $sum: { $cond: [ { $eq: ["$status", "delivered"] }, "$amount", 0 ] } } } },
  { $sort: { _id: 1 } }
])
// Output (real):
// { _id: 'Aarav', delivered: 450 }   // order 3 (cancelled, 120) ignored
// { _id: 'Diya',  delivered: 540 }
// { _id: 'Kabir', delivered: 890 }
// { _id: 'Meera', delivered: 0 }     // kept with 0 (a $match would have dropped Meera)

// $expr also works in find() (Node driver)
const rows = await db.collection("orders").find({ $expr: { $gt: ["$amount", 300] } }).toArray();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/orders/labelled (Mongoose; the pipeline body was verified in mongosh on mongod 8.0.4)
app.get("/api/orders/labelled", async (req, res) => {
  const rows = await Order.aggregate([
    { $project: {
        customer: 1, amount: 1,
        freeDelivery: { $gte: ["$amount", 400] },                      // plain boolean expression
        tier: { $switch: { branches: [ { case: { $gte: ["$amount", 800] }, then: "A" },
                                       { case: { $gte: ["$amount", 300] }, then: "B" } ],
                           default: "C" } }
    } }
  ]);
  res.json(rows);
});
// Mongoose find() with $expr also works: Order.find({ $expr: { $gt: ["$amount", 300] } })
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Comparing two fields without `$expr`
```javascript
db.orders.find({ amount: { $gt: "$limit" } })              // Wrong — compares with the literal STRING "$limit"
db.orders.find({ $expr: { $gt: ["$amount", "$limit"] } })  // Right
```

❌ Mistake 2: `$switch` without `default`
```javascript
// Wrong — a value matching no case throws: "$switch could not find a matching branch for an input, and no default was specified."
// Right — always add default
```

❌ Mistake 3: Using query syntax inside `$cond`
```javascript
{ $cond: [ { amount: { $gt: 400 } }, "big", "small" ] }      // Wrong — query syntax is invalid here (real error: "Expression $gt takes exactly 2 arguments")
{ $cond: [ { $gt: ["$amount", 400] }, "big", "small" ] }     // Right — aggregation syntax
```

---

## 🧠 Tricky Interview Question
Q: In `{ $cond: [ "$vip", "yes", "no" ] }` what happens if `vip` is missing, `0` or `null`?
Answer: `$cond` uses truthiness: `false`, `0`, `null`, `undefined` and a MISSING field are all treated as false, so the result is `"no"`. Any other value (including the string `"false"` and empty string) is true. Also, `$cond` evaluates only the chosen branch, so a per-document division like `$divide: ["$amount", 0]` in the unused branch will not raise an error (verified; a constant `$divide: [1, 0]` does fail at pipeline-optimization time).

---

## ⚫ Interview Questions + Answers

Q1: Why do we need `$expr`?
A1: Query operators compare fields to constants. `$expr` lets you use aggregation expressions: field-to-field comparisons, computed values and conditionals.

Q2: `$cond` vs `$switch`?
A2: `$cond` is a two-way choice (can be nested); `$switch` reads better for three or more branches and supports `default`.

Q3: Does `$expr` use indexes?
A3: Equality and range comparisons between a field and a constant can use indexes in recent versions, but field-to-field comparisons generally cannot. Check `explain()`.

Q4: How do you make a conditional count?
A4: `{ $sum: { $cond: [ <test>, 1, 0 ] } }` inside `$group`. (`$sum` with `$cond` is the classic pivot trick.)

Q5: How to default missing values?
A5: `{ $ifNull: ["$field", 0] }`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Labelling, tiering, flags in `$project`/`$set`
- Conditional sums/counts in `$group`
- Field-to-field comparison filters

❌ Avoid when:
- A simple filter on a constant works (`$match: { amount: { $gt: 400 } }` uses indexes better)
- Complex logic belongs in application code

---

## 📊 Visual Diagram
```
 amount ─► $cond  >= 400 ? "big" : "small"

 amount ─► $switch
            ├─ >= 800 ──► "A"
            ├─ >= 300 ──► "B"
            └─ default ─► "C"

 find({ $expr: { $gt: ["$amount", "$limit"] } })
        └─ both sides read from the SAME document
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$cond` | If/else expression | If/else expression |
| `$switch` | Multi-branch conditional | कई branches वाला conditional |
| `$expr` | Use expressions in queries | Query में expressions इस्तेमाल |
| `default` | Fallback branch | Fallback branch |
| Truthiness | What counts as true | क्या true माना जाता है |
| `$ifNull` | Replace null/missing | Null/missing बदलना |

---

## ⚡ 3-Line Summary
English:
1. `$cond` = if/else, `$switch` = chain with `default`, `$expr` = expressions inside queries.
2. Use `$sum` + `$cond` for conditional totals that keep every group.
3. Compare two fields only with `$expr`; always give `$switch` a `default`.

Hindi:
1. `$cond` = if/else, `$switch` = `default` वाली chain, `$expr` = queries के अंदर expressions।
2. हर group रखते हुए conditional totals के लिए `$sum` + `$cond` इस्तेमाल करो।
3. दो fields की तुलना सिर्फ `$expr` से; `$switch` में `default` हमेशा दो।

---

## ➡️ Next Topic
**66. Date and String Operators in Aggregation** — `$dateToString`, `$year`, `$concat`, `$substr` and friends.
