# 30. Math Object + Methods
# हिंदी में: Math Object और उसके Methods — Numbers को round, compare और calculate करना

---

## 🔵 Simple Definition (English)
`Math` is a built-in object with static helpers for numbers: rounding (`round`, `floor`, `ceil`, `trunc`), comparison (`max`, `min`), powers and roots (`pow`, `sqrt`), constants (`PI`, `E`) and random numbers (`random`). You never create it with `new`.

## 🔵 सरल परिभाषा (Hindi)
`Math` एक built-in object है जिसमें numbers के लिए static helpers हैं: rounding (`round`, `floor`, `ceil`, `trunc`), तुलना (`max`, `min`), घात और जड़ (`pow`, `sqrt`), constants (`PI`, `E`) और random numbers (`random`)। इसे `new` से नहीं बनाते।

---

## 🔴 Problem it Solves
Calculations appear everywhere: GST, discounts, delivery distance, pagination (`Math.ceil(total / pageSize)`), random OTPs and game dice. Without `Math`, you would write your own rounding and max logic, which often has edge-case bugs. Without knowing floating-point rules, money totals drift by a paisa.

## 🔴 यह क्यों बना? (Hindi)
GST, discount, delivery distance, pagination (`Math.ceil(total / pageSize)`), OTP और dice जैसे कामों में numbers हर जगह आते हैं। `Math` न होता तो rounding और max का अपना logic लिखना पड़ता, जिसमें edge cases की गलतियाँ होती हैं। Floating-point के नियम न पता हों तो money में एक paisa का फ़र्क आ जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Call a static method directly: `Math.round(x)`, `Math.max(a, b, c)`.
Step 2 → Rounding methods pick a direction: `round` to nearest, `floor` down, `ceil` up, `trunc` drop decimals.
Step 3 → `max` and `min` accept any number of arguments and return `NaN` if any argument is `NaN`.
Step 4 → `random` gives a float in `[0, 1)`; scale and floor it to get an integer range.
Step 5 → Floating-point rounding errors (`0.1 + 0.2`) are normal; round or use integers for money.

## 🟢 कैसे काम करता है? (Hindi)
चरण 1 → Static method सीधे call करो: `Math.round(x)`, `Math.max(a, b, c)`।
चरण 2 → Rounding methods दिशा चुनते हैं: `round` निकटतम, `floor` नीचे, `ceil` ऊपर, `trunc` decimal हटाता है।
चरण 3 → `max` और `min` कितने भी arguments ले सकते हैं; कोई argument `NaN` हो तो result `NaN` होता है।
चरण 4 → `random` `[0, 1)` में float देता है; उसे scale और floor करके integer range बनाते हैं।
चरण 5 → Floating-point की rounding errors (`0.1 + 0.2`) normal हैं; money के लिए round करो या integers में काम करो।

---

## 🟡 Real World Example
A food delivery bill: GST at 18% and a delivery fee per kilometre rounded up. Pagination on the restaurant list uses `Math.ceil`.

```javascript
const subtotal = 299;                              // item total in rupees
const gst = Math.round(subtotal * 0.18 * 100) / 100; // 53.82 — rounded to 2 decimals
const pages = Math.ceil(127 / 20);                 // 7 pages for 127 restaurants, 20 per page
const deliveryFee = Math.max(20, Math.ceil(3.2) * 8); // minimum ₹20, else ₹8 per km (rounded up)
```

Razorpay, Paytm and Zomato all rely on the same rounding rules for taxes and fees.

## 🟡 Real Example Hindi mein
Food delivery bill में GST 18% लगता है और delivery fee प्रति km के हिसाब से ऊपर round होती है। `Math.ceil(127 / 20)` से 127 restaurants के लिए 7 pages बनते हैं। `Math.max(20, ...)` ensure करता है कि fee कभी ₹20 से कम न हो। Razorpay, Paytm और Zomato टैक्स और fee के लिए यही rules इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```javascript
// Math object — basic examples
// Run: node 30-math-object.js

// 1. Rounding family
console.log(Math.round(4.5));    // 5 — .5 rounds toward +infinity
console.log(Math.round(4.4));    // 4 — normal nearest rounding
console.log(Math.round(-4.5));   // -4 — toward +infinity, so not -5
console.log(Math.floor(4.9));    // 4 — always down
console.log(Math.floor(-4.1));   // -5 — "down" means more negative
console.log(Math.ceil(4.1));     // 5 — always up
console.log(Math.trunc(-4.9));   // -4 — just drop the decimal part

// 2. Min and max
console.log(Math.max(3, 9, 1));  // 9 — largest of the arguments
console.log(Math.min(3, 9, 1));  // 1 — smallest of the arguments
const scores = [72, 95, 88];     // an array of numbers
console.log(Math.max(...scores)); // 95 — spread the array into arguments
console.log(Math.max());         // -Infinity — no arguments gives -Infinity
console.log(Math.max(1, NaN));   // NaN — one NaN makes the whole result NaN

// 3. Powers, roots, absolute value, sign
console.log(Math.pow(2, 10));    // 1024 — 2 to the power 10
console.log(2 ** 10);            // 1024 — the ** operator does the same
console.log(Math.sqrt(144));     // 12 — square root
console.log(Math.cbrt(27));      // 3 — cube root
console.log(Math.abs(-7.5));     // 7.5 — absolute value
console.log(Math.sign(-3));      // -1 — returns -1, 0 or 1

// 4. Constants
console.log(Math.PI);            // 3.141592653589793
console.log(Math.E);             // 2.718281828459045

// 5. Random numbers
const r = Math.random();         // float in [0, 1), never exactly 1
console.log(r >= 0 && r < 1);    // true — always true
const dice = Math.floor(Math.random() * 6) + 1; // integer from 1 to 6
console.log(dice >= 1 && dice <= 6); // true — always true

// 6. Floating-point surprise and a fix
console.log(0.1 + 0.2);                      // 0.30000000000000004 — binary float error
console.log(Number((0.1 + 0.2).toFixed(2))); // 0.3 — rounded to 2 decimals
```

## 💻 Code Example — Advanced
```javascript
// Advanced: money math, GST, discounts, secure OTP, input validation — production-style

// 1. Store money as integer paise to avoid float errors
const PAISE_PER_RUPEE = 100;             // conversion constant
function rupeesToPaise(rupees) {
  // Math.round removes float noise (19.99 * 100 = 1998.9999...) before storing
  return Math.round(rupees * PAISE_PER_RUPEE);
}
console.log(rupeesToPaise(19.99));       // 1999

// 2. Round to 2 decimals for display (Math.round alone works only on whole numbers)
function roundTo2(value) {
  // EPSILON nudges values like 1.005 that are stored slightly low
  return Math.round((value + Number.EPSILON) * 100) / 100;
}
console.log(roundTo2(2.345));            // 2.35
console.log(roundTo2(1.005));            // 1.01

// 3. GST calculation (18%) with rounding at each money step
function billWithGST(subtotalRupees, gstRate = 0.18) {
  const gst = roundTo2(subtotalRupees * gstRate); // GST amount rounded to paise
  return { subtotal: subtotalRupees, gst, total: roundTo2(subtotalRupees + gst) };
}
console.log(billWithGST(299));           // { subtotal: 299, gst: 53.82, total: 352.82 }

// 4. Clamp a value between a min and a max using Math.min and Math.max
function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max); // first raise to min, then cap at max
}
// Percentage discount that can never go below 0% or above 50% (business rule)
function applyDiscount(price, percent) {
  const safePercent = clamp(percent, 0, 50);    // keep percent in range
  return roundTo2(price * (1 - safePercent / 100)); // discounted price rounded
}
console.log(applyDiscount(500, 20));     // 400
console.log(applyDiscount(500, 90));     // 250 — capped at 50%

// 5. Secure random for OTP: Math.random is predictable, so use crypto
const crypto = require("crypto");        // built-in Node module
function generateOTP(digits = 6) {
  const min = 10 ** (digits - 1);        // smallest 6-digit number: 100000
  const max = 10 ** digits;              // exclusive upper bound: 1000000
  return crypto.randomInt(min, max).toString(); // unbiased, cryptographically secure
}
const otp = generateOTP();               // e.g. "482913"
console.log(otp.length === 6);           // true

// 6. Validate numeric input before doing math
function safeSqrt(x) {
  // reject NaN, Infinity, strings and negative numbers with a clear error
  if (typeof x !== "number" || !Number.isFinite(x) || x < 0) {
    throw new RangeError(`safeSqrt needs a finite non-negative number, got ${x}`);
  }
  return Math.sqrt(x);                   // safe to take the root now
}
try {
  console.log(safeSqrt(16));             // 4
  console.log(safeSqrt(-1));             // throws RangeError
} catch (err) {
  console.log(err.message);              // safeSqrt needs a finite non-negative number, got -1
}
```

---

## 🟠 Express.js Integration
A delivery-fee endpoint uses `Math` for distance (haversine formula), a minimum fee and rounding up the kilometres.

```javascript
const express = require("express");          // import Express
const app = express();                       // create the app
app.use(express.json());                     // parse JSON bodies
const EARTH_RADIUS_KM = 6371;                // mean radius of Earth

app.post("/api/delivery-fee", (req, res) => {
  const { lat1, lon1, lat2, lon2 } = req.body ?? {}; // coordinates from the client
  // Validate that all four values are numbers before doing trigonometry
  if ([lat1, lon1, lat2, lon2].some(v => typeof v !== "number")) {
    return res.status(400).json({ error: "coordinates must be numbers" });
  }
  const toRad = d => (d * Math.PI) / 180;    // degrees to radians
  const dLat = toRad(lat2 - lat1);           // difference in latitude
  const dLon = toRad(lon2 - lon1);           // difference in longitude
  // Haversine formula: great-circle distance between two points
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  const km = 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(a)); // distance in km
  // Minimum fee ₹20; otherwise ₹8 per km, with the km rounded UP
  const fee = Math.max(20, Math.ceil(km) * 8);
  res.json({ km: Number(km.toFixed(2)), fee }); // send distance and fee
});

app.listen(3000);                            // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `Math.round` to round halves away from zero
✅ Correct: `Math.round` rounds `.5` toward +infinity, so negative halves go toward zero. Use a sign-aware helper for refunds or debits.

```javascript
// Wrong
console.log(Math.round(-2.5));          // -2 — but many people expect -3

// Right: round the absolute value, then restore the sign
const roundHalfAway = x => Math.sign(x) * Math.round(Math.abs(x));
console.log(roundHalfAway(-2.5));       // -3
```

❌ Mistake 2: Passing an array to `Math.max`
✅ Correct: `Math.max` takes separate arguments. Spread the array.

```javascript
// Wrong
console.log(Math.max([1, 5, 3]));       // NaN — the array becomes "1,5,3", which is not a number

// Right
console.log(Math.max(...[1, 5, 3]));    // 5
```

❌ Mistake 3: Using `Math.random` for passwords, tokens or OTPs
✅ Correct: `Math.random` is not cryptographically secure. Use `crypto.randomInt` or `crypto.randomBytes`.

```javascript
// Wrong
const otpWeak = Math.floor(Math.random() * 900000) + 100000; // predictable sequence

// Right
const crypto = require("crypto");
const otpStrong = crypto.randomInt(100000, 1000000); // secure 6-digit number
```

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: what will each console.log print?
console.log(Math.round(-2.5));                  // (1)
console.log(Math.max());                        // (2)
console.log(Math.max([1, 5, 3]));               // (3)
console.log(Math.round(2.5), Math.round(-0.4)); // (4)
console.log(0.1 * 3, 0.3 === 0.1 * 3);          // (5)
```
Answer:
```
-2                          ← (1) .5 rounds toward +infinity: -2.5 becomes -2
-Infinity                   ← (2) no arguments: Math.max starts from -Infinity
NaN                         ← (3) the array is converted to the string "1,5,3", which is NaN
3 -0                        ← (4) round(2.5) is 3; round(-0.4) is -0, shown as -0 by console.log
0.30000000000000004 false   ← (5) 0.1 * 3 is not exactly 0.3 in binary floating point
```
Explanation: `Math.round` rounds ties toward positive infinity, which is why `-2.5` becomes `-2`. `Math.max` with no arguments returns `-Infinity` because that is the starting value of the search. An array is not spread automatically, so `Math.max` sees one argument that converts to `NaN`. `-0` is a real value in JavaScript; it is printed as `-0` when logged. Binary floating point cannot store 0.1 or 0.3 exactly, so comparisons with `===` can fail.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `Math.floor`, `Math.ceil`, `Math.round` and `Math.trunc`?
A1: `floor` goes to the next lower integer, `ceil` to the next higher, `round` to the nearest (ties toward +infinity), and `trunc` removes the decimal part (toward zero). For `-4.5`: floor -5, ceil -4, round -4, trunc -4.

Q2: Why is `Math.random()` not safe for security?
A2: It uses a pseudo-random generator whose future output can be predicted from observed values. For OTPs, tokens and passwords, use `crypto.randomInt` or `crypto.randomBytes`.

Q3: How do you get a random integer between `min` and `max` inclusive?
A3: `Math.floor(Math.random() * (max - min + 1)) + min`. For security-sensitive cases, use `crypto.randomInt(min, max + 1)`, because its upper bound is exclusive.

Q4: Why does `Math.max()` return `-Infinity`?
A4: The result is the largest value among the arguments. With no arguments, the mathematical identity for max is negative infinity, so the function returns it. Similarly `Math.min()` returns `Infinity`.

Q5: How do you avoid money bugs with floating-point numbers?
A5: Store money as integers (paise or cents) and convert only for display. Round after each multiplication, for example with `Math.round`, and keep the final value in a fixed decimal form.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Rounding or flooring numbers for pagination, UI and totals
- Comparing several numbers with `Math.max` and `Math.min`
- Clamping user input into a valid range

❌ Avoid when:
- Money math needs exact decimals; use integer paise or a decimal library
- You need secure randomness; use `crypto`
- You expect `Math.round` to behave like school rounding for negative halves

---

## 📊 Visual Diagram
```
  Number line:   -5    -4.5    -4    -3    -2.5    -2    ...
  floor(-4.5)  →  -5    (down)
  ceil(-4.5)   →  -4    (up)
  round(-4.5)  →  -4    (ties toward +infinity)
  trunc(-4.5)  →  -4    (drop decimals, toward zero)

  Random:  Math.random() ∈ [0, 1)
           × 6        ∈ [0, 6)
           floor      ∈ {0..5}
           + 1        ∈ {1..6}   ← dice
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `Math.round` | Nearest integer, ties toward +infinity | निकटतम पूर्णांक |
| `Math.floor` / `Math.ceil` | Round down / up | नीचे / ऊपर round करना |
| `Math.trunc` | Remove the decimal part | Decimal हटाना |
| Floating point | Binary approximation of decimals | Decimal की binary approximation |
| `EPSILON` | Smallest difference between 1 and the next float | सबसे छोटा float अंतर |
| Clamp | Keep a value in a min–max range | Range में सीमित रखना |
| CSPRNG | Cryptographically secure random generator | सुरक्षित random generator |

---

## ⚡ 3-Line Summary
**English:**
1. `Math` gives you `round`, `floor`, `ceil`, `trunc`, `max`, `min`, `pow`, `sqrt` and `random` without any import.
2. Know the rules: `round` ties go toward +infinity, `max()` is `-Infinity`, and arrays must be spread.
3. Store money as integers and use `crypto` for anything security related.

**Hindi:**
1. `Math` बिना import के `round`, `floor`, `ceil`, `trunc`, `max`, `min`, `pow`, `sqrt` और `random` देता है।
2. नियम जानो: `round` के ties +infinity की तरफ़ जाते हैं, `max()` का result `-Infinity` है, और array को spread करना पड़ता है।
3. Money को integers में रखो, और security से जुड़े काम के लिए `crypto` इस्तेमाल करो।

---

## ➡️ Next Topic
**31. Date Object** — Dates, timestamps और time zones। Money के बाद time calculations सबसे ज़्यादा interview में पूछे जाते हैं, और ETA या due date के लिए `Math` और `Date` साथ चलते हैं।
