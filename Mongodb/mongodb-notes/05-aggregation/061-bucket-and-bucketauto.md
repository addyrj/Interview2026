# 61. $bucket and $bucketAuto
# हिंदी में: $bucket और $bucketAuto

---

## 🔵 Simple Definition (English)
**`$bucket`** groups documents into ranges (buckets) whose boundaries YOU define, e.g. 0-200, 200-500, 500-1000. **`$bucketAuto`** picks the boundaries automatically so that buckets have roughly equal document counts. Both are like `$group` for histograms.

## 🔵 सरल परिभाषा (Hindi)
**`$bucket`** documents को ranges (buckets) में बाँटता है जिनकी boundaries आप तय करते हैं, जैसे 0-200, 200-500, 500-1000। **`$bucketAuto`** boundaries अपने आप चुनता है ताकि हर bucket में लगभग बराबर documents हों। दोनों histograms के लिए `$group` जैसे हैं।

---

## 🔴 Problem it Solves
"How many orders are small, medium, large?" With `$group` you would have to write a `$cond`/`$switch` chain. Buckets make price bands, age groups and score ranges a one-stage job.

## 🔴 यह क्यों बना? (Hindi)
"कितने orders छोटे, मध्यम, बड़े हैं?" `$group` से इसके लिए `$cond`/`$switch` की लंबी chain लिखनी पड़ती। Buckets से price bands, age groups और score ranges एक ही stage में हो जाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `groupBy`: the expression to bucket on, e.g. `"$amount"`.
Step 2 → `boundaries`: ascending array like `[0, 200, 500, 1000]`. Each bucket is lower-inclusive and upper-exclusive: [0,200), [200,500), [500,1000).
Step 3 → `default`: bucket label for values outside the boundaries. Without it, an out-of-range value causes an ERROR.
Step 4 → `output`: accumulators per bucket (default is `count`). The bucket's `_id` is its lower bound.
Step 5 → `$bucketAuto: { groupBy, buckets: N }` makes N buckets with `_id: {min, max}`; no default needed.
Step 6 → Use `granularity` (e.g. "R5", "POWERSOF2") in `$bucketAuto` to round boundaries to preferred numbers.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `groupBy`: जिस expression पर bucket बनाना है, जैसे `"$amount"`।
Step 2 → `boundaries`: ascending array जैसे `[0, 200, 500, 1000]`। हर bucket lower-inclusive और upper-exclusive है: [0,200), [200,500), [500,1000)।
Step 3 → `default`: boundaries के बाहर की values के लिए label। इसके बिना out-of-range value पर ERROR आता है।
Step 4 → `output`: हर bucket के accumulators (default में `count`)। Bucket का `_id` उसकी lower bound होती है।
Step 5 → `$bucketAuto: { groupBy, buckets: N }` N buckets बनाता है, `_id: {min, max}` के साथ; default नहीं चाहिए।
Step 6 → `$bucketAuto` में `granularity` (जैसे "R5", "POWERSOF2") से boundaries पसंदीदा numbers पर round होती हैं।

---

## 🟡 Real World Example
**Zomato's price-range chart** on a restaurant page: "Under Rs 200 / Rs 200-500 / Above Rs 500" with counts of dishes. `$bucket` with fixed boundaries gives the bands. For analytics where the team just wants "split users into 4 equal spend groups (quartiles)", `$bucketAuto` is used.

## 🟡 Real Example Hindi mein
**Zomato का price-range chart** restaurant page पर: "Rs 200 से कम / Rs 200-500 / Rs 500 से ऊपर" और dishes की गिनती। Fixed boundaries वाला `$bucket` bands देता है। जब analytics team को "users को 4 बराबर spend groups (quartiles) में बाँटो" चाहिए, तब `$bucketAuto` चलता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4, shop.orders amounts: 450,230,120,890,310,75
db.orders.aggregate([
  { $bucket: {
      groupBy: "$amount",                          // value to bucket
      boundaries: [0, 200, 500, 1000],             // [0,200) [200,500) [500,1000)
      default: "other",                            // anything outside (>=1000 or <0)
      output: {
        n: { $sum: 1 },                            // count per bucket
        ids: { $push: "$_id" }                     // which orders fall in the bucket
      }
  } }
])
// Output (real):
// { _id: 0,   n: 2, ids: [ 3, 6 ] }               // 120 and 75
// { _id: 200, n: 3, ids: [ 1, 2, 5 ] }            // 450, 230, 310
// { _id: 500, n: 1, ids: [ 4 ] }                  // 890
```

## 💻 Code Example — Advanced

```javascript
// $bucketAuto: 3 buckets of roughly equal size
db.orders.aggregate([ { $bucketAuto: { groupBy: "$amount", buckets: 3 } } ])
// Output (real):
// { _id: { min: 75,  max: 230 }, count: 2 }
// { _id: { min: 230, max: 450 }, count: 2 }
// { _id: { min: 450, max: 890 }, count: 2 }       // last bucket's max is INCLUSIVE (890 included)

// Node driver: price bands with revenue per band
const bands = await db.collection("orders").aggregate([
  { $bucket: {
      groupBy: "$amount",
      boundaries: [0, 200, 500, 1000],
      default: "1000+",
      output: { orders: { $sum: 1 }, revenue: { $sum: "$amount" } }
  } }
]).toArray();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/stats/price-bands (Mongoose)
app.get("/api/stats/price-bands", async (req, res) => {
  const bands = await Order.aggregate([
    { $bucket: { groupBy: "$amount", boundaries: [0, 200, 500, 1000], default: "other",
                 output: { n: { $sum: 1 } } } }
  ]);
  res.json(bands.map(b => ({ from: b._id, count: b.n })));   // _id is the lower bound (or "other")
});
// The same pipeline was run in mongosh on mongod 8.0.4 (see Basic example output).
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `default` and a value outside the boundaries
```javascript
// Wrong — amount 890 with boundaries [0,500] -> error "$switch could not find a matching branch..."
db.orders.aggregate([{ $bucket: { groupBy: "$amount", boundaries: [0, 500] } }])
// Right — add default or widen boundaries
db.orders.aggregate([{ $bucket: { groupBy: "$amount", boundaries: [0, 500], default: "500+" } }])
```

❌ Mistake 2: Unsorted or too-short boundaries
✅ Boundaries must be ascending and have at least two values, all of the same type.

❌ Mistake 3: Expecting boundary value in the lower bucket
✅ 200 falls in [200,500), not [0,200).

---

## 🧠 Tricky Interview Question
Q: In `$bucketAuto` with 3 buckets, is the upper value of each bucket inclusive?
Answer: No, each bucket is [min, max) except the LAST one, whose max is inclusive. That is why 230 appears as `max` of bucket 1 but belongs to bucket 2, and 890 (the max) is included in the last. Also bucket counts can be unequal if there are many duplicate values, because equal values are never split across buckets.

---

## ⚫ Interview Questions + Answers

Q1: `$bucket` vs `$bucketAuto`?
A1: `$bucket` uses your boundaries; `$bucketAuto` picks boundaries for evenly distributed counts.

Q2: What is the `_id` of a `$bucket` output document?
A2: The inclusive lower boundary of the bucket (or the `default` label).

Q3: What happens to out-of-range values?
A3: They go to `default`, or the stage errors if none is given.

Q4: Can bucket on an expression?
A4: Yes, `groupBy` accepts any expression, e.g. `{ $year: "$ts" }` or `{ $size: "$items" }`.

Q5: Equivalent to `$group`?
A5: A `$group` with a `$switch` on ranges.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Histograms, price bands, age groups, score ranges
- Quantile-like splits (`$bucketAuto`)

❌ Avoid when:
- Categories are discrete (use `$group`)
- You need exact percentiles (use `$percentile`, 7.0+)

---

## 📊 Visual Diagram
```
 amount axis:  0 ─────── 200 ─────────── 500 ─────────── 1000
 buckets:     [   0    ) [      200      ) [      500      )
 orders:       120, 75     450, 230, 310      890
 result:       n=2         n=3                n=1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$bucket` | Manual range grouping | Manual range grouping |
| `$bucketAuto` | Automatic equal-count ranges | अपने आप बराबर-गिनती ranges |
| `boundaries` | Ascending range edges | Ranges की सीमाएँ |
| `default` | Bucket for out-of-range | Range के बाहर वाला bucket |
| Lower-inclusive | Includes lower edge | निचली सीमा शामिल |
| `granularity` | Round edges to series | Edges को series पर round करना |

---

## ⚡ 3-Line Summary
English:
1. `$bucket` groups by your ranges; `$bucketAuto` picks ranges for equal counts.
2. Buckets are [lower, upper); always set `default` for out-of-range values.
3. `_id` is the lower bound (or `{min, max}` for auto).

Hindi:
1. `$bucket` आपकी ranges से group करता है; `$bucketAuto` बराबर counts वाली ranges खुद चुनता है।
2. Buckets [lower, upper) होते हैं; range के बाहर की values के लिए `default` ज़रूर दो।
3. `_id` lower bound होती है (auto में `{min, max}`)।

---

## ➡️ Next Topic
**62. $count, $sortByCount** — quick counting stages.
