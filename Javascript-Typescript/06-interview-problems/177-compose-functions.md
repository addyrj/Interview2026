# 177. Compose Functions
# हिंदी में: Functions को Compose करना — एक function का output अगले का input बनाना

---

## 🔵 Simple Definition (English)
Composition joins several functions into one. `compose(f, g, h)(x)` means `f(g(h(x)))`: the rightmost function runs first, and each result is passed to the next function to its left. `pipe` does the same thing in the opposite order, left to right.

## 🔵 सरल परिभाषा (Hindi)
Composition कई functions को एक में जोड़ता है। `compose(f, g, h)(x)` का मतलब है `f(g(h(x)))`: सबसे दाएँ वाला function पहले चलता है, और हर result अपने बाईं ओर वाले function को input के रूप में मिलता है। `pipe` वही काम बाएँ से दाएँ क्रम में करता है।

---

## 🔴 Problem it Solves
**Problem Statement:** Write `compose(...fns)` that returns one function. Calling it with a value runs the functions from right to left and returns the final result. Handle an empty list by returning the input unchanged. Also write an async version that supports promise-returning steps.

When a data transformation has many steps, such as trim, validate, apply a discount and format a price, a long nested call like `format(discount(validate(trim(x))))` is hard to read and easy to get in the wrong order. Composition lists the steps once and keeps the order clear.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `compose(...fns)` लिखो जो एक function लौटाए। उसे किसी value के साथ बुलाने पर functions दाएँ से बाएँ चलें और अंतिम result लौटे। खाली list पर input को बिना बदले लौटाओ। एक async version भी लिखो जो promise लौटाने वाले steps को सँभाले।

जब किसी data के कई steps हों, जैसे trim, validate, discount और price format, तो `format(discount(validate(trim(x))))` जैसी nested calls पढ़ने में मुश्किल होती हैं और क्रम गलत होने का खतरा रहता है। Composition steps को एक बार सूची में लिखता है और क्रम साफ़ रखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Collect the functions in an array, in the order they were written.
Step 2 → Return a new function that accepts the input value.
Step 3 → Start with the input, and call the rightmost function on it.
Step 4 → Pass the result to the next function to the left, and repeat.
Step 5 → When the leftmost function has run, return its result.
Step 6 → `reduceRight` does steps 3 to 5 in one line, starting from the right end.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Functions को उसी क्रम में array में रखो जिस क्रम में लिखे गए हैं।
Step 2 → एक नया function लौटाओ जो input value लेता है।
Step 3 → Input से शुरू करो, और सबसे दाएँ वाला function उस पर चलाओ।
Step 4 → Result को उसके बाईं ओर वाले function को दो, और दोहराओ।
Step 5 → जब सबसे बाएँ वाला function चल जाए, तो उसका result लौटाओ।
Step 6 → `reduceRight` एक ही पंक्ति में step 3 से 5 करता है, दाएँ सिरे से शुरू करके।

---

## 🟡 Real World Example
Flipkart's search query goes through several steps: trim spaces, lowercase, remove stop words, then build the API URL. Razorpay's payment amount goes through validate, convert paise to rupees, apply GST, and format. Swiggy's coupon logic composes checks for minimum order value, expiry date, and user eligibility into one function.

Scenario: A user types "  Pizza Margherita  " in the search box. `compose(encodeForUrl, toLower, trim)` returns `pizza%20margherita`. The steps are listed in the order they are written, but they run from the bottom up.

## 🟡 Real Example Hindi mein
Flipkart का search query कई steps से गुज़रता है: spaces हटाना, lowercase करना, stop words हटाना, फिर API URL बनाना। Razorpay की payment amount validate होती है, paise से rupees में बदलती है, GST लगती है और format होती है। Swiggy का coupon logic minimum order value, expiry date और user eligibility की जाँच को एक function में compose करता है।

उदाहरण: User search box में "  Pizza Margherita  " लिखता है। `compose(encodeForUrl, toLower, trim)` `pizza%20margherita` लौटाता है। Steps उसी क्रम में लिखे गए हैं, पर चलते नीचे से ऊपर की ओर हैं।

---

## 💻 Code Example — Basic
```javascript
// Basic: compose runs the functions from right to left with reduceRight
function compose(...fns) {
  return (x) => fns.reduceRight((acc, fn) => fn(acc), x); // start with x, apply the last function first, then the earlier ones
}

// Sample: the search query pipeline
const trim = (s) => s.trim();                // remove spaces at both ends
const lower = (s) => s.toLowerCase();        // make it lowercase
const toUrl = (s) => s.replace(/ /g, "%20"); // replace spaces with %20 for a URL

const searchPath = compose(toUrl, lower, trim); // trim runs first, then lower, then toUrl
console.log(searchPath("  Pizza Margherita  ")); // Expected output: pizza%20margherita

// Sample: simple numbers, to see the order clearly
const double = (n) => n * 2;                 // doubles a number
const addOne = (n) => n + 1;                 // adds one
console.log(compose(double, addOne)(5));     // Expected output: 12 (addOne first: 6, then double: 12)

// Edge case: an empty compose returns the input unchanged
console.log(compose()(7));                   // Expected output: 7
```

## 💻 Code Example — Advanced
```javascript
// Advanced: compose with validation, multiple arguments for the first step, and an async pipeline
function compose(...fns) {
  // Guard: every item must be a function, so bad input fails early with a clear message
  for (const fn of fns) {
    if (typeof fn !== "function") throw new TypeError("compose expects only functions");
  }
  if (fns.length === 0) return (x) => x;     // no functions: identity, return the input

  return function composed(...args) {        // the composed function accepts the same args as the first (rightmost) step
    const [last, ...rest] = [...fns].reverse(); // the rightmost function runs first; rest are the earlier ones
    return rest.reduce((acc, fn) => fn(acc), last.apply(this, args)); // pass each result to the next function
  };
}

// Pipe is compose in the opposite order: left to right reads more naturally
const pipe = (...fns) => compose(...[...fns].reverse());

// Async pipeline: each step may return a promise; reduce chains them one after another
const pipeAsync = (...fns) => (input) =>
  fns.reduce((promise, fn) => promise.then(fn), Promise.resolve(input)); // start with a resolved promise

// Test 1: the leftmost function receives the result of the rightmost one
const sum = (a, b) => a + b;                 // takes two arguments
const square = (n) => n * n;                 // takes one argument
console.log(compose(square, sum)(2, 3));     // Expected output: 25 (sum first: 5, then square: 25)

// Test 2: pipe reads left to right
console.log(pipe((s) => s.trim(), (s) => s.toUpperCase())("  pizza  ")); // Expected output: PIZZA

// Test 3: async steps, each awaited in order
const fetchPrice = async (sku) => ({ sku, price: 200 }); // pretend API call
const addGst = async (item) => ({ ...item, total: item.price + item.price * 0.5 }); // 50 percent for the demo
pipeAsync(fetchPrice, addGst)("A1").then((r) => console.log(JSON.stringify(r)));
// Expected output: {"sku":"A1","price":200,"total":300}

// Time:  O(k) for k functions, each called once per run
// Space: O(k) for the reversed copy of the function list
```

### Edge Cases
- `compose()` with no functions returns the identity function, which returns its argument unchanged.
- Only the rightmost function may take several arguments; every later step receives one value.
- A thrown error in any step stops the chain, so the caller gets the error as usual.
- In the async version, a rejected step skips the rest of the chain and the final promise rejects.
- Passing a non-function, such as `compose(trim, 5)`, fails on the first call, or at creation in the advanced version.

---

## 🟠 Express.js Integration
An API response often needs the same cleanup on every route: remove internal fields, format money, and add a version. Composing these steps once gives every route the same pipeline, and each route passes its data through it.

```javascript
// Express.js: compose response transforms once, then use them on every route
const express = require("express");          // web framework
const app = express();                       // create the app

// Generic compose (same as the advanced version, without the extra checks)
const compose = (...fns) => (x) => fns.reduceRight((acc, fn) => fn(acc), x);

// Individual steps: each takes one value and returns a new value
const removeInternal = (order) => {          // drop fields the client must not see
  const { internalNotes, costPriceInPaise, ...publicOrder } = order; // destructure to split them off
  return publicOrder;                        // the rest of the fields
};
const formatMoney = (order) => ({ ...order, total: `Rs ${(order.totalPaise / 100).toFixed(2)}` }); // paise to rupees
const addVersion = (order) => ({ ...order, apiVersion: "v2" }); // mark the response version

// Runs bottom-up: removeInternal first, then formatMoney, then addVersion
const toPublicOrder = compose(addVersion, formatMoney, removeInternal);

// GET /api/orders/:id
app.get("/api/orders/:id", (req, res) => {
  const order = {                            // pretend database row
    id: req.params.id,
    totalPaise: 129900,                      // Rs 1299.00 stored in paise
    internalNotes: "VIP customer",           // must never reach the client
    costPriceInPaise: 80000,                 // internal cost, also hidden
  };
  res.json(toPublicOrder(order));            // 200 OK with the cleaned response
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Order API running");          // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Writing the steps in the order they run, instead of the order `compose` expects
✅ Correct: `compose` runs the rightmost function first. Use `pipe` if you want the list to read in the order of execution.

```javascript
// Basic compose and pipe, repeated so this block runs alone
const compose = (...fns) => (x) => fns.reduceRight((acc, fn) => fn(acc), x);
const pipe = (...fns) => (x) => fns.reduce((acc, fn) => fn(acc), x);

// Wrong: the author expects trim first, but compose runs toUpperCase first
const trimmed = (s) => s.trim();
const upper = (s) => s.toUpperCase();
console.log(compose(trimmed, upper)("  ok  ")); // Expected output: OK (upper ran first, then trim)

// Right: with pipe, the order you write is the order that runs
console.log(pipe(trimmed, upper)("  ok  "));    // Expected output: OK (trim first, then upper)
console.log(JSON.stringify(pipe(trimmed, upper)("  ok  "))); // Expected output: "OK"
```

❌ **Mistake 2:** Passing an array of functions instead of spreading them
✅ Correct: `compose(...fns)` takes separate arguments. If you pass an array, it becomes one function value, and calling it fails.

```javascript
// Basic compose, repeated so this block runs alone
const compose = (...fns) => (x) => fns.reduceRight((acc, fn) => fn(acc), x);

// Wrong: the whole array is treated as a single function
const steps = [(x) => x + 1, (x) => x * 2];
try {
  console.log(compose(steps)(3));            // compose receives one array, not two functions
} catch (err) {
  console.log(err.name);                     // Expected output: TypeError
}

// Right: spread the array into separate arguments
console.log(compose(...steps)(3));           // Expected output: 7 (double first: 6, then add one: 7)
```

---

## 🧠 Tricky Interview Question
```javascript
// Advanced compose and pipe, so this block runs alone
function compose(...fns) {
  if (fns.length === 0) return (x) => x;     // identity
  return function composed(...args) {
    const [last, ...rest] = [...fns].reverse();
    return rest.reduce((acc, fn) => fn(acc), last.apply(this, args));
  };
}
const pipe = (...fns) => compose(...[...fns].reverse());

const f = (x) => x + "f";
const g = (x) => x + "g";
const h = (x) => x + "h";
console.log(compose(f, g, h)(""));           // ?
console.log(pipe(f, g, h)(""));              // ?
console.log(compose()(5));                   // ?
console.log(compose(Math.max)(2, 9, 4));     // ?
```
Answer:
```
hgf      ← h runs first (adds "h"), then g adds "g", then f adds "f"
fgh      ← pipe reads left to right, so f runs first
5        ← an empty compose is the identity, so the input comes back unchanged
9        ← the only function is the rightmost one, so it receives all three arguments
```
Explain the direction: compose is right to left, and the first (rightmost) function may take many arguments, but the others take one value each.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `compose` and `pipe`?**
A1: They use the same steps in opposite order. `compose(f, g)(x)` is `f(g(x))`, and `pipe(f, g)(x)` is `g(f(x))`.

**Q2: Why use `reduceRight` for compose?**
A2: It walks the array from the right end, so the rightmost function runs first. Each result becomes the accumulator for the next step.

**Q3: How does the async version differ from the sync one?**
A3: It starts with `Promise.resolve(input)` and chains each step with `.then`. Every step waits for the previous promise, so plain values and promises both work.

**Q4: What happens when a step throws?**
A4: In the sync version the error bubbles up to the caller. In the async version the chain rejects, and later steps are skipped.

**Q5: What is the time complexity?**
A5: O(k) for k functions, since each one is called once per input. Creating the composed function copies the array, which is also O(k).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A value goes through several small, reusable transformations
- The same pipeline is shared between routes, components, or tests
- You want each step testable on its own

❌ Avoid when:
- There is one or two steps; a plain expression is clearer
- Steps need a shared mutable state, which makes the order matter in hidden ways
- The team finds point-free style hard to read; name the intermediate values instead

---

## 📊 Visual Diagram
```
compose(toUrl, lower, trim)("  Pizza Margherita  ")

step 1  trim   : "  Pizza Margherita  " -> "Pizza Margherita"
step 2  lower  : "Pizza Margherita"     -> "pizza margherita"
step 3  toUrl  : "pizza margherita"     -> "pizza%20margherita"

Order of writing:  toUrl, lower, trim   (read right to left to see the run order)
Order of running:  trim -> lower -> toUrl
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Composition | Joining functions so one output feeds the next input | Functions को जोड़कर output को अगले input में देना |
| Pipe | Composition that reads left to right | बाएँ से दाएँ पढ़ा जाने वाला composition |
| Identity | A function that returns its input unchanged | Input को बिना बदले लौटाने वाला function |
| reduceRight | Array method that folds from the right end | Array को दाएँ सिरे से समेटने वाला method |
| Point-free style | Writing functions without naming the input | Input का नाम लिए बिना function लिखना |
| Accumulator | The value carried from one reduce step to the next | Reduce के हर step में आगे ले जाई जाने वाली value |

---

## ⚡ 3-Line Summary
English:
1. `compose` runs functions from right to left, so each result feeds the function on its left.
2. Use `pipe` when you want the code to read in the order it runs.
3. For promise-returning steps, chain with `.then` so each step waits for the previous one.

Hindi:
1. `compose` functions को दाएँ से बाएँ चलाता है, ताकि हर result उसके बाईं ओर वाले function को मिले।
2. जब code उसी क्रम में पढ़ा जाए जिस क्रम में चलता है, तो `pipe` इस्तेमाल करो।
3. Promise लौटाने वाले steps के लिए `.then` से chain करो, ताकि हर step पिछले का इंतज़ार करे।

---

## ➡️ Next Topic
**178. Flatten Object (nested to flat)** — composition builds pipelines from functions; the next problem applies a similar step-by-step transform to an object, turning nested keys into dotted keys.
