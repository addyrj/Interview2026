# 31. Date Object
# हिंदी में: Date Object — Time, Timestamp और Time Zone को संभालना

---

## 🔵 Simple Definition (English)
`Date` is a built-in object that stores one instant in time as the number of milliseconds since 1 January 1970 UTC (the "epoch"). It gives you methods to read parts (year, month, day), format, and do arithmetic on time.

## 🔵 सरल परिभाषा (Hindi)
`Date` एक built-in object है जो एक समय-बिंदु को 1 जनवरी 1970 UTC (जिसे "epoch" कहते हैं) से बीते milliseconds की संख्या के रूप में रखता है। इससे हम हिस्से (साल, महीना, दिन) पढ़ सकते हैं, format कर सकते हैं और time पर calculations कर सकते हैं।

---

## 🔴 Problem it Solves
Computers need one reliable way to store time, but humans use calendars, months, and local time zones. Without a standard, every system would store dates differently, and delivery ETAs, EMI due dates and subscription renewals would drift. `Date` gives one internal number plus helpers to read and show it.

## 🔴 यह क्यों बना? (Hindi)
Computers को time को एक भरोसेमंद तरीके से store करना होता है, जबकि इंसान calendar, महीने और local time zone इस्तेमाल करते हैं। एक standard न हो तो हर system अलग तरीके से date रखेगा, और delivery ETA, EMI due date और subscription renewal गलत हो जाएँगे। `Date` एक internal number और उसे पढ़ने-दिखाने के helpers देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → A Date stores one number: milliseconds since the epoch (UTC).
Step 2 → Getters like `getFullYear()` and `getHours()` read that number in LOCAL time.
Step 3 → UTC getters like `getUTCHours()` and `toISOString()` always use UTC.
Step 4 → Month is 0-based (January is 0), and out-of-range values roll over (day 32 becomes next month).
Step 5 → Subtracting two dates gives milliseconds; compare with `getTime()` or `<`, not `==`.

## 🟢 कैसे काम करता है? (Hindi)
चरण 1 → Date के अंदर एक number होता है: epoch (UTC) से milliseconds।
चरण 2 → `getFullYear()` और `getHours()` जैसे getters उस number को LOCAL time में पढ़ते हैं।
चरण 3 → `getUTCHours()` और `toISOString()` हमेशा UTC इस्तेमाल करते हैं।
चरण 4 → महीना 0-based है (January = 0), और out-of-range values अगले महीने में चली जाती हैं (दिन 32 = अगला महीना)।
चरण 5 → दो dates को घटाने से milliseconds मिलते हैं; तुलना के लिए `getTime()` या `<` इस्तेमाल करो, `==` नहीं।

---

## 🟡 Real World Example
Swiggy shows an ETA: the server stores the order time in UTC, and the app shows it in the user's time zone. EMI reminders and subscription renewals add days or months to a stored date.

```javascript
const placedAt = new Date("2024-03-10T08:00:00Z");   // stored in UTC on the server
const eta = new Date(placedAt.getTime() + 35 * 60 * 1000); // add 35 minutes in ms
console.log(eta.toISOString());                       // 2024-03-10T08:35:00.000Z
```

Zomato, Swiggy and Razorpay EMI systems all follow this pattern: store UTC, calculate in ms or UTC, display in local time.

## 🟡 Real Example Hindi mein
Swiggy पर ETA दिखता है। Server order का समय UTC में store करता है, और app उसे user के time zone में दिखाता है। EMI reminder या subscription renewal में stored date में दिन या महीने जोड़े जाते हैं। Zomato, Swiggy और Razorpay EMI systems यही pattern मानते हैं: UTC में store करो, ms या UTC में calculate करो, और local time में दिखाओ।

---

## 💻 Code Example — Basic
```javascript
// Date object — basic examples
// Run: node 31-date-object.js

// 1. Current date and time (changes every run, so we only print the type)
const now = new Date();                  // a Date for this exact moment
console.log(typeof now.getTime());       // number — ms since epoch

// 2. Milliseconds since the epoch (1 Jan 1970 UTC)
console.log(Date.now() > 0);             // true — Date.now() returns a number of ms
const epoch = new Date(0);               // 0 ms after the epoch
console.log(epoch.toISOString());        // 1970-01-01T00:00:00.000Z

// 3. Create a date from parts: MONTH IS 0-BASED (0 = January)
const orderDate = new Date(2024, 0, 15, 10, 30); // local time: 15 Jan 2024, 10:30
console.log(orderDate.getFullYear());    // 2024
console.log(orderDate.getMonth());       // 0 — January, not 1
console.log(orderDate.getDate());        // 15 — day of the month
console.log(orderDate.getHours());       // 10 — hour in local time

// 4. Create from an ISO string: "Z" means UTC
const utcDate = new Date("2024-03-10T08:00:00Z");
console.log(utcDate.toISOString());      // 2024-03-10T08:00:00.000Z
console.log(utcDate.getTime());          // 1710057600000 — ms since epoch

// 5. Formatting
console.log(utcDate.toISOString().slice(0, 10)); // 2024-03-10 — date part only
console.log(utcDate.toUTCString());      // Sun, 10 Mar 2024 08:00:00 GMT

// 6. Date arithmetic with UTC setters (no time-zone surprises)
const due = new Date("2024-01-30T00:00:00Z"); // 30 January
due.setUTCDate(due.getUTCDate() + 5);    // add 5 days; 35 Jan rolls into February
console.log(due.toISOString().slice(0, 10)); // 2024-02-04

// 7. Difference between two dates in days
const diffMs = new Date("2024-02-04") - new Date("2024-01-30"); // subtraction gives ms
console.log(diffMs / (1000 * 60 * 60 * 24)); // 5 — milliseconds converted to days
```

## 💻 Code Example — Advanced
```javascript
// Advanced: safe parsing, IST display, business-day math, correct comparison

// 1. Parse safely: invalid dates do not throw, they become NaN internally
function parseDateSafe(input) {
  const d = new Date(input);                    // may be an "Invalid Date"
  if (Number.isNaN(d.getTime())) {              // invalid Date has a NaN time value
    throw new RangeError(`Invalid date: ${input}`);
  }
  return d;                                     // safe to use now
}
try {
  console.log(parseDateSafe("2024-02-29T10:00:00Z").toISOString()); // 2024-02-29T10:00:00.000Z
  parseDateSafe("not-a-date");                  // fails the check
} catch (err) {
  console.log(err.message);                     // Invalid date: not-a-date
}

// 2. Show the same instant in IST (India) without changing the stored UTC value
function toISTString(date) {
  // Intl formats the same moment for a chosen time zone; IST is UTC+05:30
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",                   // the target zone
    year: "numeric", month: "short", day: "2-digit",
    hour: "2-digit", minute: "2-digit", hour12: true,
  }).format(date);
}
console.log(toISTString(new Date("2024-03-10T08:00:00Z")).includes("2024")); // true — 13:30 IST

// 3. Add business days (skip Saturday and Sunday) for delivery estimates
function addBusinessDays(startDate, days) {
  const d = new Date(startDate);                // copy, so the input is not mutated
  let added = 0;                                // business days added so far
  while (added < days) {
    d.setUTCDate(d.getUTCDate() + 1);           // move one calendar day forward (UTC)
    const weekday = d.getUTCDay();              // 0 = Sunday ... 6 = Saturday
    if (weekday !== 0 && weekday !== 6) added++; // count weekdays only
  }
  return d;                                     // new Date object
}
const friday = new Date("2024-03-08T00:00:00Z"); // 8 March 2024 is a Friday
console.log(addBusinessDays(friday, 1).toISOString().slice(0, 10)); // 2024-03-11 (Monday)

// 4. Compare dates correctly
const a = new Date("2024-01-01T00:00:00Z");
const b = new Date("2024-01-01T00:00:00Z");
console.log(a == b);                            // false — compares object references
console.log(a.getTime() === b.getTime());       // true — compares the numbers
console.log(a < new Date("2025-01-01"));        // true — < uses valueOf (the number)

// 5. ETA helper: returns a NEW Date, never mutates the input
const ETA_MINUTES = 35;                         // default preparation + delivery time
function etaFrom(orderTime, minutes = ETA_MINUTES) {
  return new Date(orderTime.getTime() + minutes * 60 * 1000); // add ms
}
console.log(etaFrom(new Date("2024-01-01T10:00:00Z")).toISOString()); // 2024-01-01T10:35:00.000Z
```

---

## 🟠 Express.js Integration
Express does not handle dates itself. Your route parses incoming date strings, validates them, and stores or returns UTC ISO strings so that server and client agree.

```javascript
const express = require("express");           // import Express
const app = express();                        // create the app
app.use(express.json());                      // parse JSON bodies

app.post("/api/orders", (req, res) => {
  const { items = [], scheduledFor } = req.body ?? {}; // request fields
  const createdAt = new Date();               // server time, stored as UTC internally
  // scheduledFor is optional: parse it only when present
  const slot = scheduledFor ? new Date(scheduledFor) : null;
  if (slot && Number.isNaN(slot.getTime())) { // invalid date string from the client
    return res.status(400).json({ error: "scheduledFor is not a valid date" });
  }
  res.status(201).json({
    createdAt: createdAt.toISOString(),       // always send UTC ISO text
    scheduledFor: slot ? slot.toISOString() : null, // null when not scheduled
    itemCount: items.length,                  // number of items in the order
  });
});

app.listen(3000);                             // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that months start at 0
✅ Correct: `new Date(2024, 0, 15)` is 15 January. Month 1 means February.

```javascript
// Wrong
const feb = new Date(2024, 1, 15);      // this is 15 February, not January
console.log(feb.getMonth());            // 1

// Right
const jan = new Date(2024, 0, 15);      // January
console.log(jan.getMonth());            // 0
```

❌ Mistake 2: Relying on the machine's time zone for date-only strings
✅ Correct: `"2024-01-15"` (date only) is parsed as UTC. `"2024-01-15T00:00"` (no Z) is parsed as LOCAL time. Pick one format and always write the zone.

```javascript
// Wrong: the result depends on where the code runs
const local = new Date("2024-01-15T00:00");
console.log(local.toISOString());       // different output in IST vs UTC machines

// Right: explicit UTC
const utc = new Date("2024-01-15T00:00:00Z");
console.log(utc.toISOString());         // 2024-01-15T00:00:00.000Z — always the same
```

❌ Mistake 3: Mutating a shared Date and comparing with `==`
✅ Correct: `setDate` changes the object in place, so copy first. Compare with `getTime()`.

```javascript
// Wrong
const start = new Date("2024-01-10T00:00:00Z");
const end = start;                      // same object, not a copy
end.setUTCDate(end.getUTCDate() + 5);   // also changes start!
console.log(start == end);              // true only because they are the same object

// Right
const start2 = new Date("2024-01-10T00:00:00Z");
const end2 = new Date(start2);          // copy
end2.setUTCDate(end2.getUTCDate() + 5);  // only end2 changes
console.log(start2.getTime() === end2.getTime()); // false
```

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: what will each console.log print? (deterministic across time zones)
const d = new Date(2024, 0, 31);        // 31 January 2024, local midnight
d.setMonth(1);                          // change month to February; day 31 does not exist
console.log(d.getMonth());              // (1)
console.log(d.getDate());               // (2)

console.log(new Date(2024, 0, 1).getMonth());     // (3)
console.log(new Date(2024, 12, 1).getFullYear()); // (4)
```
Answer:
```
2                ← (1) February 31 overflows into March, so the month becomes March (index 2)
2                ← (2) 2024 is a leap year: Feb has 29 days, so Feb 31 = March 2
0                ← (3) month index 0 is January
2025             ← (4) month 12 overflows into January of the next year
```
Explanation: `setMonth(1)` does not refuse an invalid day. It rolls the date forward, and 31 February 2024 becomes 2 March 2024 (February has 29 days in a leap year). The `getMonth()` index for March is 2. Month 12 is not valid for a month index, so it rolls into January 2025. The months are zero-based, which is the most common source of confusion.

---

## ⚫ Interview Questions + Answers

Q1: Why are months 0-based in JavaScript Date?
A1: The API follows the old Java `Date` design, where months index into an array of month names. It is a historical choice, so always remember `0 = January` and `11 = December`.

Q2: What is the difference between `Date.now()` and `new Date().getTime()`?
A2: Both return milliseconds since the epoch. `Date.now()` returns the number directly and does not create a Date object, so it is slightly faster for timestamps.

Q3: Why should you store dates in UTC or ISO strings?
A3: UTC is the same everywhere, so servers in different regions agree. ISO 8601 strings sort correctly as text and are easy to parse. Convert to local time only at display time.

Q4: Is `Date` mutable? How do you avoid mutation bugs?
A4: Yes. Methods like `setDate` and `setUTCDate` change the object in place. Copy with `new Date(original)` before changing it. For larger apps, libraries such as date-fns or Luxon, or the newer Temporal API where available, make immutable date handling easier.

Q5: What does `new Date("not a date")` return?
A5: It does not throw. It returns an "Invalid Date" object whose `getTime()` is `NaN`. Check with `Number.isNaN(d.getTime())`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Storing timestamps (`createdAt`, `updatedAt`) in UTC
- Measuring durations with `getTime()` differences
- Showing dates to users with `Intl.DateTimeFormat` and a `timeZone`

❌ Avoid when:
- You need calendar math across many time zones and DST rules; use a dedicated library
- You parse user-typed dates without a fixed format; validate first
- You compare Date objects with `==`; compare `getTime()` values instead

---

## 📊 Visual Diagram
```
  Epoch (UTC)                                       Now
  1970-01-01T00:00:00Z ──────────────────────────► 1710057600000 ms
                                                     │
              ┌──────────────────────────────────────┤
              ▼                                      ▼
   toISOString()                        getHours()  (local time)
   2024-03-10T08:00:00.000Z             depends on the machine zone
              │
              ▼  Intl.DateTimeFormat(timeZone: "Asia/Kolkata")
   display: 10 Mar 2024, 01:30 pm  (IST = UTC + 05:30)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Epoch | 1 Jan 1970 00:00 UTC, the zero point | Time का शून्य बिंदु |
| Timestamp | Milliseconds since the epoch | Epoch से ms की गिनती |
| UTC | Coordinated Universal Time, the standard reference | मानक समय (UTC) |
| ISO 8601 | Standard text format like `2024-03-10T08:00:00Z` | मानक date text format |
| Time zone | Region-specific offset from UTC | Region का समय अंतर |
| Invalid Date | A Date object whose time is `NaN` | गलत date object |
| Intl.DateTimeFormat | Formats a date for a locale and time zone | Locale के हिसाब से format |

---

## ⚡ 3-Line Summary
**English:**
1. `Date` stores one number: milliseconds since the epoch in UTC.
2. Months are 0-based, and out-of-range values roll over; copy Dates before changing them.
3. Store and calculate in UTC or ms, and convert to a time zone only for display.

**Hindi:**
1. `Date` के अंदर एक number है: UTC epoch से milliseconds।
2. Months 0-based हैं, और out-of-range values आगे roll होती हैं; Date बदलने से पहले उसकी copy बनाओ।
3. UTC या ms में store और calculate करो, और time zone सिर्फ़ display के समय लागू करो।

---

## ➡️ Next Topic
**32. JSON (parse, stringify)** — Date objects को API में भेजने के लिए JSON में बदलना और वापस लेना। ISO strings वही format हैं जिसे JSON में `Date` भेजता है, इसलिए यह अगला सही topic है।
