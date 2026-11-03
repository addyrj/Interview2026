# 66. Date and String Operators in Aggregation
# हिंदी में: Aggregation में Date और String Operators

---

## 🔵 Simple Definition (English)
**Date operators** (`$year`, `$month`, `$dayOfWeek`, `$hour`, `$dateToString`, `$dateTrunc`, `$dateAdd`, `$dateDiff`, `$dateFromString`) and **string operators** (`$concat`, `$trim`, `$toUpper`, `$split`, `$substrCP`, `$strLenCP`, `$regexMatch`, `$replaceAll`) are expressions you use inside stages like `$project`, `$addFields`, `$group` and `$match` (via `$expr`) to extract, reshape and compare date/text values **inside the database**, before the result ever reaches your app. Tested on MongoDB 8.0.4 (`$dateTrunc`, `$dateAdd`, `$dateDiff` need 5.0+).

## 🔵 सरल परिभाषा (Hindi)
**Date operators** (`$year`, `$month`, `$dayOfWeek`, `$hour`, `$dateToString`, `$dateTrunc`, `$dateAdd`, `$dateDiff`, `$dateFromString`) और **string operators** (`$concat`, `$trim`, `$toUpper`, `$split`, `$substrCP`, `$strLenCP`, `$regexMatch`, `$replaceAll`) ऐसे expressions हैं जो `$project`, `$addFields`, `$group` और `$match` (`$expr` के ज़रिए) जैसे stages के अंदर इस्तेमाल होते हैं — ताकि date/text values को database के अंदर ही निकाला, बदला और compare किया जा सके, app तक पहुँचने से पहले। (`$dateTrunc`, `$dateAdd`, `$dateDiff` के लिए MongoDB 5.0+ चाहिए।)

---

## 🔴 Problem it Solves
Dates are stored in **UTC** as BSON Date. If you pull 10 lakh orders into Node.js just to bucket them by "day in IST" or to build a display label, you waste network, memory and CPU. Without these operators you also hit classic bugs: a 2 AM IST order (which is 20:30 UTC of the previous day) lands in the wrong day's report. Date/string operators let the server do bucketing, timezone conversion, trimming, case-folding and parsing in one pipeline, and let `$group` aggregate on the computed key.

## 🔴 यह क्यों बना? (Hindi)
Dates BSON Date के रूप में **UTC** में store होती हैं। अगर 10 लाख orders Node.js में खींचकर सिर्फ "IST के हिसाब से दिन" में group करो या display label बनाओ, तो network, memory और CPU बर्बाद होता है। ऊपर से classic bug: रात 2 बजे (IST) का order UTC में पिछले दिन 20:30 होता है, तो गलत दिन की report में चला जाता है। ये operators server पर ही bucketing, timezone conversion, trimming, case-folding और parsing कर देते हैं, और `$group` computed key पर aggregate कर सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Pick the stage: `$project`/`$addFields` to compute new fields, `$group` to bucket by a computed `_id`, `$match` + `$expr` to filter on a computed value.
Step 2 → Reference fields with `"$field"` and call the operator: `{ $year: "$placedAt" }`.
Step 3 → For timezone-aware work pass the long form: `{ $hour: { date: "$placedAt", timezone: "Asia/Kolkata" } }` (default timezone is UTC).
Step 4 → Truncate/bucket with `$dateTrunc` (`unit: "month"`) or format with `$dateToString` (`format: "%Y-%m-%d"`).
Step 5 → Do arithmetic with `$dateAdd` / `$dateSubtract` / `$dateDiff` (never subtract millis by hand — DST and month lengths bite).
Step 6 → For text: `$trim` → `$toUpper`/`$toLower` → `$split` → `$arrayElemAt`, or `$concat` with `$toString` for numbers. `*CP` variants count Unicode code points (use them, not the old byte-based `$substr`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Stage चुनो: नए fields के लिए `$project`/`$addFields`, computed `_id` से bucket करने के लिए `$group`, computed value पर filter के लिए `$match` + `$expr`।
Step 2 → Fields को `"$field"` से refer करो और operator लगाओ: `{ $year: "$placedAt" }`।
Step 3 → Timezone चाहिए तो long form: `{ $hour: { date: "$placedAt", timezone: "Asia/Kolkata" } }` (default UTC है)।
Step 4 → `$dateTrunc` (`unit: "month"`) से bucket या `$dateToString` (`format: "%Y-%m-%d"`) से format करो।
Step 5 → Arithmetic के लिए `$dateAdd` / `$dateSubtract` / `$dateDiff` — millis खुद घटाना नहीं, DST और महीनों की लंबाई गड़बड़ करती है।
Step 6 → Text के लिए: `$trim` → `$toUpper`/`$toLower` → `$split` → `$arrayElemAt`, या `$concat` + `$toString`। `*CP` वाले variants Unicode code points गिनते हैं (पुराने byte-based `$substr` की जगह यही लो)।

---

## 🟡 Real World Example
**Swiggy's daily-revenue dashboard**: orders are stored with `placedAt` in UTC. Finance wants revenue per **IST calendar day**. A midnight-to-5:30-AM IST order must count for the IST day, not the UTC day. They `$group` on `$dateToString` with `timezone: "Asia/Kolkata"`. Customer names come from user input with stray spaces and mixed case, so the notification service builds `"Hi " + first name` using `$trim` + `$split`.

## 🟡 Real Example Hindi mein
**Swiggy का daily-revenue dashboard**: orders में `placedAt` UTC में है। Finance को **IST calendar day** के हिसाब से revenue चाहिए। रात 12 से सुबह 5:30 (IST) के order को IST वाले दिन में गिनना है, UTC वाले में नहीं। वे `$dateToString` पर `timezone: "Asia/Kolkata"` के साथ `$group` करते हैं। Customer names user input से आते हैं (extra spaces, mixed case), इसलिए notification service `$trim` + `$split` से "Hi " + first name बनाती है।

---

## 💻 Code Example — Basic

```javascript
// mongosh — seed data (run on MongoDB 8.0.4 in our test)
use t66                                   // switch to a test database
db.orders.insertMany([                    // 4 sample orders; placedAt is stored in UTC
  { _id: 1, customer: "  Aditya Ranjan ", city: "Bengaluru", placedAt: ISODate("2026-01-15T20:30:00Z"), amount: 450 },
  { _id: 2, customer: "priya sharma",     city: "Mumbai",    placedAt: ISODate("2026-01-15T08:10:00Z"), amount: 320 },
  { _id: 3, customer: "Rahul Verma",      city: "Bengaluru", placedAt: ISODate("2026-02-03T13:00:00Z"), amount: 780 },
  { _id: 4, customer: "Neha Singh",       city: "Delhi",     placedAt: ISODate("2026-02-20T23:45:00Z"), amount: 150 }
])

// 1) Date parts. $hour with a timezone converts before extracting.
db.orders.aggregate([
  { $project: {
      y:   { $year: "$placedAt" },                 // year in UTC
      m:   { $month: "$placedAt" },                 // month 1-12
      dow: { $dayOfWeek: "$placedAt" },             // 1 = Sunday ... 7 = Saturday
      hrIST: { $hour: { date: "$placedAt", timezone: "Asia/Kolkata" } } // hour in IST
  } }
])
// Output (order 1): { _id: 1, y: 2026, m: 1, dow: 5, hrIST: 2 }   <- 20:30 UTC = 02:00 IST next day
// order 2: hrIST 13, order 3: hrIST 18, order 4: hrIST 5

// 2) String cleanup: trim, upper-case, first name, 3-letter code, label
db.orders.aggregate([
  { $project: {
      name:  { $trim: { input: "$customer" } },                       // removes leading/trailing spaces
      up:    { $toUpper: { $trim: { input: "$customer" } } },          // upper-case after trim
      first: { $arrayElemAt: [ { $split: [ { $trim: { input: "$customer" } }, " " ] }, 0 ] }, // split on space, take [0]
      cityCode: { $toUpper: { $substrCP: ["$city", 0, 3] } },         // first 3 code points
      len:   { $strLenCP: "$city" },                                  // length in characters
      label: { $concat: ["$city", " - Rs ", { $toString: "$amount" }] } // numbers must be $toString'd
  } },
  { $limit: 1 }
])
// Output: { _id: 1, name: 'Aditya Ranjan', up: 'ADITYA RANJAN', first: 'Aditya',
//           cityCode: 'BEN', len: 9, label: 'Bengaluru - Rs 450' }
```

## 💻 Code Example — Advanced

```javascript
// mongosh — timezone-correct daily revenue + monthly truncation + date math + regex/parse

// 1) Revenue per IST calendar day. Order 1 (20:30 UTC Jan 15) becomes Jan 16 in IST.
db.orders.aggregate([
  { $group: {
      _id:   { $dateToString: { format: "%Y-%m-%d", date: "$placedAt", timezone: "Asia/Kolkata" } }, // bucket key
      total: { $sum: "$amount" },                    // revenue in that IST day
      n:     { $sum: 1 }                             // order count
  } },
  { $sort: { _id: 1 } }                              // chronological
])
// Output:
// [ { _id: '2026-01-15', total: 320, n: 1 },
//   { _id: '2026-01-16', total: 450, n: 1 },        <- shifted by timezone!
//   { _id: '2026-02-03', total: 780, n: 1 },
//   { _id: '2026-02-21', total: 150, n: 1 } ]        <- 23:45 UTC Feb 20 = Feb 21 IST

// 2) Monthly buckets with $dateTrunc (5.0+) - returns a real Date, easier to chart/sort than a string
db.orders.aggregate([
  { $group: { _id: { $dateTrunc: { date: "$placedAt", unit: "month" } }, total: { $sum: "$amount" } } },
  { $sort: { _id: 1 } }
])
// Output: [ { _id: ISODate('2026-01-01T00:00:00.000Z'), total: 770 },
//           { _id: ISODate('2026-02-01T00:00:00.000Z'), total: 930 } ]

// 3) Date arithmetic: due date = placedAt + 7 days, and age in days at a reference date
db.orders.aggregate([
  { $match: { _id: 1 } },
  { $project: { _id: 0,
      dueAt:   { $dateAdd:  { startDate: "$placedAt", unit: "day", amount: 7 } },
      ageDays: { $dateDiff: { startDate: "$placedAt", endDate: ISODate("2026-02-01T00:00:00Z"), unit: "day" } }
  } }
])
// Output: [ { dueAt: ISODate('2026-01-22T20:30:00.000Z'), ageDays: Long('17') } ]

// 4) Regex test, replace, and parse a non-ISO date string
db.orders.aggregate([
  { $match: { _id: 2 } },
  { $project: { _id: 0,
      hasSharma: { $regexMatch: { input: "$customer", regex: /SHARMA/i } },                  // case-insensitive test
      fixed:     { $replaceAll: { input: "$customer", find: " ", replacement: "_" } },        // all occurrences
      d:         { $dateFromString: { dateString: "15/03/2026", format: "%d/%m/%Y" } }        // dd/mm/yyyy -> Date
  } }
])
// Output: [ { hasSharma: true, fixed: 'priya_sharma', d: ISODate('2026-03-15T00:00:00.000Z') } ]
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Tested with mongoose + express against mongod 8.0.4
const express = require('express');
const mongoose = require('mongoose');

const Order = mongoose.model('Order', new mongoose.Schema({
  city: String, amount: Number, placedAt: Date   // Date type -> stored as BSON Date (UTC)
}));

const app = express();

// GET /daily  -> revenue per IST day. Mongoose does NOT cast inside aggregate(), so pass real Dates/ObjectIds.
app.get('/daily', async (req, res) => {
  const rows = await Order.aggregate([
    { $group: {
        _id: { $dateToString: { format: '%Y-%m-%d', date: '$placedAt', timezone: 'Asia/Kolkata' } },
        total: { $sum: '$amount' }
    } },
    { $sort: { _id: 1 } }
  ]);
  res.json(rows);
});
// Real output with 3 seeded orders: [{"_id":"2026-01-16","total":150},{"_id":"2026-02-01","total":70}]
// (an order at 20:30Z and one at 02:00Z on the next UTC day both fall on 16 Jan IST)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Grouping by `$dayOfMonth` / string slices in UTC and calling it "IST day"
```javascript
// Wrong — UTC day, orders after 18:30 UTC land on the wrong IST day
{ $group: { _id: { $dayOfMonth: "$placedAt" }, total: { $sum: "$amount" } } }
// Right — pass the timezone, and include year+month so days of different months don't merge
{ $group: { _id: { $dateToString: { format: "%Y-%m-%d", date: "$placedAt", timezone: "Asia/Kolkata" } }, total: { $sum: "$amount" } } }
```

❌ Mistake 2: Using `$concat` with a number, or `$match` with a function on a field and expecting an index
```javascript
// Wrong — $concat only accepts strings; a number gives an error
{ $concat: ["Rs ", "$amount"] }
// Right
{ $concat: ["Rs ", { $toString: "$amount" }] }
```
✅ Also remember: `$match: { $expr: { $eq: [{ $month: "$placedAt" }, 1] } }` cannot use an index on `placedAt`. Prefer a range filter `{ placedAt: { $gte: ISODate("2026-01-01"), $lt: ISODate("2026-02-01") } }` first, then compute.

---

## 🧠 Tricky Interview Question

Order 1 has `placedAt = 2026-01-15T20:30:00Z`. What does `{ $dayOfMonth: "$placedAt" }` return, and what does it return with `timezone: "Asia/Kolkata"`?

Answer: Without a timezone it returns `15` (UTC). With `Asia/Kolkata` (UTC+05:30) the local time is `2026-01-16 02:00`, so it returns `16`. The stored value never changes — timezone only affects how the operator **reads** the instant. Also note that `$dayOfWeek` is 1-based with **Sunday = 1** (our test gave `5` = Thursday for 15 Jan 2026), unlike JavaScript's `getDay()` where Sunday = 0.

---

## ⚫ Interview Questions + Answers

Q1: How are dates stored in MongoDB and why does timezone matter in aggregation?
A1: As a 64-bit count of milliseconds since epoch (UTC). There is no timezone stored. Date operators default to UTC, so for local business days you pass `timezone: "Asia/Kolkata"` (Olson name or offset like `"+05:30"`); the Olson name handles DST correctly.

Q2: `$dateToString` vs `$dateTrunc` for bucketing?
A2: `$dateToString` returns a string (good for labels/JSON). `$dateTrunc` (5.0+) returns a real Date rounded down to a unit (`day`, `week`, `month`, ...) with `binSize`, `timezone` and `startOfWeek` options — better for sorting, `$merge` into reports or time-series joins.

Q3: Why prefer `$dateAdd`/`$dateDiff` over arithmetic on milliseconds?
A3: Months have different lengths and some timezones have DST, so "+30 days" or "+1 month" is not a fixed number of ms. These operators respect the unit and timezone. (`{$add: ["$date", 86400000]}` works for fixed durations but is easy to get wrong.)

Q4: `$substr` vs `$substrBytes` vs `$substrCP`?
A4: `$substr` is deprecated alias of `$substrBytes` (counts UTF-8 bytes, can cut a Hindi/emoji character in half and error). `$substrCP` counts Unicode code points — the safe choice for text like "बेंगलुरु".

Q5: Can a date/string expression use an index?
A5: Not when wrapped around the field (`$expr` with `$month`). Filter on the raw field with a range first (index-friendly), then compute. A `$project`/`$group` after the `$match` has no index concern.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reports bucketed by day/week/month in a business timezone
- Cleaning/normalising text on the fly (trim, case, split) before grouping or joining
- Computing due dates, ages, SLA breaches inside the pipeline

❌ Avoid when:
- The computed value is queried constantly — store it (Computed Pattern, see note 72) or index the raw field
- You need full-text/linguistic search (use a text/Atlas Search index, not regex over every document)
- Filtering large collections with `$expr` + date functions as the first stage (collection scan)

---

## 📊 Visual Diagram
```
DATE / STRING OPERATORS IN A PIPELINE
──────────────────────────────────────────────
 placedAt (UTC) 2026-01-15T20:30Z
        │  $dateToString + timezone "Asia/Kolkata"
        ▼
   "2026-01-16"  ──► $group _id ──► $sum amount
                                        │
   "  Aditya Ranjan "                   ▼
        │ $trim → $split → [0]       { _id:'2026-01-16', total:450 }
        ▼
     "Aditya"  ──► $concat("Hi ", ...) ──► "Hi Aditya"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$dateToString` | Format a Date as text (with timezone) | Date को text में बदलना |
| `$dateTrunc` | Round a Date down to a unit | Date को unit तक round down |
| `$dateDiff` | Difference between two Dates in a unit | दो Dates का अंतर |
| `$split` | Split string into array | String को array में तोड़ना |
| `$substrCP` | Substring by Unicode code points | Code points से substring |
| `$regexMatch` | Boolean regex test | Regex से true/false जाँच |
| Olson timezone | Name like Asia/Kolkata, DST-aware | Timezone का नाम |

---

## ⚡ 3-Line Summary
English:
1. Date and string operators let the pipeline bucket, format, parse and clean values on the server instead of in app code.
2. Dates are UTC; always pass `timezone: "Asia/Kolkata"` for business-day reports, and use `$dateAdd`/`$dateDiff` for date math.
3. Filter on the raw indexed field first; wrapping a field in `$expr` date/string functions kills index use.

Hindi:
1. Date और string operators pipeline को server पर ही bucket, format, parse और clean करने देते हैं, app code में नहीं।
2. Dates UTC में होती हैं; business-day report के लिए हमेशा `timezone: "Asia/Kolkata"` दो, और date math के लिए `$dateAdd`/`$dateDiff` लो।
3. पहले raw indexed field पर filter करो; field को `$expr` के date/string functions में लपेटने से index काम नहीं करता।

---

## ➡️ Next Topic
**67. Pipeline Performance Optimization** — `$match` early, indexes in pipelines, `explain`, `allowDiskUse` and the optimizer's reordering.
