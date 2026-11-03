# 20. Array Update Operators — $push, $pull, $addToSet, $pop
# हिंदी में: Array Update Operators — $push, $pull, $addToSet, $pop

---

## 🔵 Simple Definition (English)
Array operators modify array fields in place: **`$push`** appends an element (duplicates allowed), **`$addToSet`** appends only if absent (set semantics), **`$pull`** removes all elements matching a value or condition, **`$pop`** removes the first (`-1`) or last (`1`) element. Modifiers like `$each`, `$position`, `$slice`, `$sort` extend `$push`.

## 🔵 सरल परिभाषा (Hindi)
Array operators array fields को वहीं बदलते हैं: **`$push`** element जोड़ता है (duplicates चलते हैं), **`$addToSet`** सिर्फ़ तब जोड़ता है जब पहले से न हो (set जैसा), **`$pull`** value या condition से match होने वाले सभी elements हटाता है, **`$pop`** पहला (`-1`) या आख़िरी (`1`) element हटाता है। `$each`, `$position`, `$slice`, `$sort` जैसे modifiers `$push` को बढ़ाते हैं।

---

## 🔴 Problem it Solves
Without them you would read the whole array into the app, change it, and write it back – slow and racy. These operators mutate arrays atomically on the server: add a cart item, add a unique tag, remove a wishlist entry, keep the last N notifications.

## 🔴 यह क्यों बना? (Hindi)
इनके बिना पूरा array app में पढ़ना, बदलना और वापस लिखना पड़ता – धीमा और race-prone। ये operators server पर arrays atomically बदलते हैं: cart item जोड़ना, unique tag जोड़ना, wishlist entry हटाना, आख़िरी N notifications रखना।

---

## 🟢 How it Works — Step by Step

Step 1 → `$push: {arr: v}` appends v at the end (creates the array if the field is missing).
Step 2 → `$addToSet: {arr: v}` checks for an equal element first; adds only if not present.
Step 3 → `$pull: {arr: v | condition}` removes every element equal to v or matching the query condition (`{$in: [...]}`, `{qty: {$lt: 2}}`).
Step 4 → `$pop: {arr: 1}` removes the last element, `-1` the first.
Step 5 → Use `$each` to add many values at once; `$push` with `$slice` caps array length; `$position` inserts at an index.
Step 6 → Applying these on a non-array field errors.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `$push: {arr: v}` v को अंत में जोड़ता है (field न हो तो array बनाता है)।
Step 2 → `$addToSet: {arr: v}` पहले equal element देखता है; न हो तभी जोड़ता है।
Step 3 → `$pull: {arr: v | condition}` v के बराबर या query condition (`{$in: [...]}`, `{qty: {$lt: 2}}`) से match हर element हटाता है।
Step 4 → `$pop: {arr: 1}` आख़िरी element हटाता है, `-1` पहला।
Step 5 → कई values एक साथ जोड़ने के लिए `$each`; `$push` के साथ `$slice` array length सीमित करता है; `$position` index पर insert करता है।
Step 6 → Non-array field पर लगाने से error आता है।

---

## 🟡 Real World Example
Swiggy's cart: `$push` adds an item line; `$pull: {items: {sku: "X"}}` removes it when the customer taps remove. User interests use `$addToSet` so tapping "Biryani" twice stores it once. The notification inbox uses `$push` with `$each` + `$slice: -50` to keep only the latest 50 alerts.

## 🟡 Real Example Hindi mein
Swiggy cart: `$push` item line जोड़ता है; ग्राहक remove दबाए तो `$pull: {items: {sku: "X"}}` हटाता है। User interests `$addToSet` से रखे जाते हैं ताकि "Biryani" दो बार दबाने पर एक बार ही store हो। Notification inbox `$push` + `$each` + `$slice: -50` से सिर्फ़ ताज़ा 50 alerts रखता है।

---

## 💻 Code Example — Basic

```javascript
// mongod 8.0.4, database "mh"
db.a.insertOne({ _id: 1, t: ["x", "y", "x"] })

db.a.updateOne({ _id: 1 }, { $push: { t: "z" } })       // append "z"
db.a.updateOne({ _id: 1 }, { $addToSet: { t: "z" } })   // "z" already there -> no change
db.a.findOne().t
// Output: [ 'x', 'y', 'x', 'z' ]       <- $push allowed the duplicate x, addToSet skipped z

db.a.updateOne({ _id: 1 }, { $pull: { t: "x" } })       // removes BOTH x
db.a.findOne().t                                         // Output: [ 'y', 'z' ]

db.a.updateOne({ _id: 1 }, { $pop: { t: 1 } })          // remove last element
db.a.findOne().t                                         // Output: [ 'y' ]
```

## 💻 Code Example — Advanced

```javascript
// $each + $position: insert several values at the front
db.a.updateOne({ _id: 1 }, { $push: { t: { $each: ["p", "q"], $position: 0 } } })
db.a.findOne().t                                         // Output: [ 'p', 'q', 'y' ]

// $addToSet with $each: adds only the missing values
db.a.updateOne({ _id: 1 }, { $addToSet: { t: { $each: ["p", "n"] } } })
db.a.findOne().t                                         // Output: [ 'p', 'q', 'y', 'n' ]   (p skipped, n added)

// $pull with $in: remove several values
db.a.updateOne({ _id: 1 }, { $pull: { t: { $in: ["p", "q"] } } })
db.a.findOne().t                                         // Output: [ 'y', 'n' ]

// Capped list: keep last 3 only
db.a.updateOne({ _id: 1 }, { $push: { t: { $each: ["1", "2", "3"], $slice: -3 } } })
// array becomes the last 3 elements: [ '1', '2', '3' ]  ($slice -3 keeps the tail)

// $pull from array of documents by condition
db.orders.updateOne({ _id: 1 }, { $pull: { items: { sku: "A1" } } })
```
(All Output lines were executed on mongod 8.0.4, including `$slice: -3`; a `$push` of a bare array added one nested element, as warned below.)

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Wishlist endpoints
app.post('/wishlist/:uid', async (req, res) => {
  await User.updateOne({ _id: req.params.uid }, { $addToSet: { wishlist: req.body.productId } }); // unique add
  res.sendStatus(204);
});
app.delete('/wishlist/:uid/:pid', async (req, res) => {
  await User.updateOne({ _id: req.params.uid }, { $pull: { wishlist: req.params.pid } });         // remove
  res.sendStatus(204);
});
// Mongoose: array schema type [String]; doc.wishlist.push() + save() uses $push under the hood.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `$push` where uniqueness is required
```javascript
db.a.updateOne({_id:1}, {$push: {tags: "a"}})        // Wrong: duplicates accumulate
db.a.updateOne({_id:1}, {$addToSet: {tags: "a"}})    // Right
```

❌ Mistake 2: Passing an array without `$each`
```javascript
db.a.updateOne({_id:1}, {$push: {t: ["m","n"]}})          // Wrong: pushes ONE nested array element
db.a.updateOne({_id:1}, {$push: {t: {$each: ["m","n"]}}}) // Right: pushes two elements
```

❌ Mistake 3: Unbounded `$push`
✅ Correct: Use `$slice` or a separate collection; arrays grow toward the 16 MB document limit.

---

## 🧠 Tricky Interview Question
Q: `$pull: { t: "x" }` on `["x","y","x"]` – how many x are removed?
Answer: Both. `$pull` removes ALL matching elements, giving `["y"]` (plus whatever else). `$pop` removes only one end element. Verified above: after pull the array was `['y','z']`.

---

## ⚫ Interview Questions + Answers

Q1: `$push` vs `$addToSet`?
A1: `$push` always appends; `$addToSet` appends only when the exact value is absent.

Q2: Does `$addToSet` check objects field order?
A2: Yes – embedded documents must match exactly, including field order.

Q3: How to remove by index?
A3: Set element to null with `$unset: {"t.1": 1}` then `$pull: {t: null}`; or use `$pop` for ends.

Q4: How to keep latest N items?
A4: `$push` with `$each` and `$slice: -N` (add `$sort` to order by a field first).

Q5: Update one element in an array of objects?
A5: Positional `$`, filtered positional `$[id]` with `arrayFilters`, or `$[]` for all.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small bounded lists: tags, cart items, recent activity

❌ Avoid when:
- Arrays can grow unbounded or are queried heavily by element (use a separate collection)

---

## 📊 Visual Diagram
```
t = [x, y, x]
$push z        → [x, y, x, z]
$addToSet z    → [x, y, x, z]   (no change, z exists)
$pull x        → [y, z]         (all x gone)
$pop 1         → [y]            (last removed)
$pop -1        → removes first
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| $push | Append element | Element जोड़ना |
| $addToSet | Append if absent | न हो तो जोड़ना |
| $pull | Remove matches | Matches हटाना |
| $pop | Remove first/last | पहला/आख़िरी हटाना |
| $each | Apply to many values | कई values पर लागू |
| $slice | Limit array length | Array length सीमित |

---

## ⚡ 3-Line Summary
English:
1. `$push` appends, `$addToSet` appends uniquely, `$pull` removes all matches, `$pop` removes an end.
2. Use `$each` for multiple values and `$slice` to bound arrays.
3. Keep arrays bounded; very large lists belong in their own collection.

Hindi:
1. `$push` जोड़ता है, `$addToSet` unique जोड़ता है, `$pull` सभी matches हटाता है, `$pop` एक छोर हटाता है।
2. कई values के लिए `$each` और array सीमित रखने के लिए `$slice` इस्तेमाल करो।
3. Arrays bounded रखो; बहुत बड़ी lists अपनी अलग collection में रखो।

---

## ➡️ Next Topic
**21. Positional Operators and arrayFilters**
