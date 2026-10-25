# 71. Call Stack
# हिंदी में: Call Stack — JavaScript Function calls का क्रम कैसे संभालता है

---

## 🔵 Simple Definition (English)
The **call stack** is a LIFO (last in, first out) structure that tracks which function is currently running. When a function is called, a frame is pushed on top; when it returns, its frame is popped off.

## 🔵 सरल परिभाषा (Hindi)
**Call stack** एक LIFO (आख़िरी में आया, पहले निकला) structure है, जो बताता है कि अभी कौन-सा function चल रहा है। Function call होने पर उसका frame ऊपर जुड़ता है, और return होने पर वह frame हटता है।

---

## 🔴 Problem it Solves
JavaScript एक समय में एक ही काम कर सकती है। किसी function के अंदर दूसरा function call हो, फिर उसके अंदर तीसरा, तो engine को पता रखना पड़ता है कि किस function को कहाँ वापस जाना है। Call stack यही bookkeeping करता है। इसके बिना "return कहाँ जाए?" का जवाब नहीं मिलता।

## 🔴 यह क्यों बना? (Hindi)
जब Flipkart checkout में `placeOrder()` अंदर `validateCart()` call करता है, और वह `checkStock()` call करता है, तो हर function खत्म होने पर सही caller पर वापस जाना ज़रूरी है। Call stack यह क्रम सुरक्षित रखता है। बिना इसके nested function calls का कोई मतलब नहीं बनता।

---

## 🟢 How it Works — Step by Step

Step 1 → `main()` call हुआ, उसका frame stack पर push हुआ
Step 2 → `main()` के अंदर `placeOrder()` call हुआ, वह भी stack पर ऊपर push हुआ
Step 3 → `placeOrder()` ने `validate()` call किया, तो तीसरा frame जुड़ा
Step 4 → `validate()` return हुआ, उसका frame pop हुआ, control `placeOrder()` पर लौटा
Step 5 → जब सारे frames खत्म हो जाते हैं, stack खाली होता है और event loop अगला काम देखता है

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `main()` call हुआ, उसका frame stack पर गया
Step 2 → `main()` के अंदर `placeOrder()` call हुआ, वह ऊपर push हुआ
Step 3 → `placeOrder()` ने `validate()` call किया, तीसरा frame जुड़ा
Step 4 → `validate()` return हुआ, उसका frame निकला, control `placeOrder()` पर लौटा
Step 5 → सारे frames खत्म होने पर stack खाली होता है, और event loop अगला callback उठाता है

---

## 🟡 Real World Example
Swiggy पर order place करते समय: `placeOrder()` → `calculateBill()` → `applyCoupon()`। अगर `applyCoupon()` में error आए, तो stack trace में यही chain दिखती है। Developer को पता चलता है कि error किस call-path से आया। यही stack trace production debugging में सबसे ज़्यादा काम आता है।

## 🟡 Real Example Hindi mein
Swiggy पर order place करते समय: `placeOrder()` → `calculateBill()` → `applyCoupon()`। अगर `applyCoupon()` में error आए, तो stack trace में यही chain दिखती है। इससे developer को पता चलता है कि error किस रास्ते से आया। Production debugging में यही सबसे काम आता है।

---

## 💻 Code Example — Basic
```javascript
// Demo: see the call stack through nested function calls
// Run with: node 71-call-stack.js

function validateCart(items) {          // frame pushed when called from placeOrder
  console.log("validateCart: checking", items.length, "items");
  return items.length > 0;              // return pops this frame off the stack
}

function calculateTotal(items) {        // another frame pushed by placeOrder
  // reduce adds up prices; 0 is the starting value
  const total = items.reduce((sum, item) => sum + item.price, 0);
  console.log("calculateTotal:", total);
  return total;                         // frame popped after returning total
}

function placeOrder(items) {            // frame pushed when main calls it
  if (!validateCart(items)) {           // call validateCart, wait for its return
    return "Cart is empty";             // early return pops placeOrder's frame
  }
  const total = calculateTotal(items);  // call calculateTotal, wait for result
  return `Order placed, total = ${total}`; // final return from placeOrder
}

function main() {                       // bottom of the stack
  const cart = [{ name: "Pizza", price: 299 }, { name: "Coke", price: 49 }];
  console.log(placeOrder(cart));        // placeOrder is called from main
}

main();                                 // start the program: first frame pushed
// Output:
// validateCart: checking 2 items
// calculateTotal: 348
// Order placed, total = 348
```

## 💻 Code Example — Advanced
```javascript
// Goal: detect how deep the stack can go, and handle stack overflow safely

// 1. Recursive function that adds one frame per call (no base case on purpose)
function recurse(n) {
  return recurse(n + 1);                // every call pushes a new frame
}

// 2. Catch the overflow instead of letting the process crash
function safeRecurse() {
  try {
    recurse(0);                         // will eventually exceed the stack limit
  } catch (err) {                       // V8 throws a RangeError on overflow
    console.log("Stack overflow caught:", err instanceof RangeError); // true
    console.log("Message:", err.message); // Maximum call stack size exceeded
  }
}
safeRecurse();

// 3. Safe alternative for deep work: iterative loop uses no extra frames
function sumTo(n) {
  let total = 0;                        // accumulator lives in one frame only
  for (let i = 1; i <= n; i++) {        // loop, not recursion
    total += i;                         // add current number
  }
  return total;                         // single frame, safe for any n in range
}
console.log("sumTo(100000) =", sumTo(100000)); // 5000050000

// 4. Recursion is fine when depth is small and bounded (e.g., tree traversal)
function depthOf(node) {
  if (!node || !node.children || node.children.length === 0) {
    return 1;                           // base case: leaf node, stop recursing
  }
  // Recurse into each child and take the maximum depth found
  return 1 + Math.max(...node.children.map(depthOf));
}

const menuTree = {                      // small, bounded structure
  name: "Menu",
  children: [{ name: "Pizza", children: [{ name: "Cheese" }] }, { name: "Drinks" }],
};
console.log("Menu depth:", depthOf(menuTree)); // 3
```

---

## 🟠 Express.js Integration
Express में हर middleware और route handler एक-दूसरे को call करते हैं। `next()` call होने पर अगला middleware उसी call chain में जुड़ता है। यह direct recursion नहीं है, पर stack की ही तरह काम करता है। नीचे का example दिखाता है कि sync throw को Express अपने error handler तक कैसे पहुँचाता है। ध्यान दो: async function में throw हुआ error call stack से बाहर निकल जाता है, इसलिए उसे `try/catch` + `next(err)` से पकड़ना पड़ता है।

```javascript
const express = require("express");     // web framework
const app = express();

// Route handler: sync throw is caught by Express while its frame is still on the stack
app.get("/cart/total", (req, res) => {
  const items = req.query.items ? req.query.items.split(",") : []; // parse query string
  if (items.length === 0) {
    throw new Error("Cart is empty");   // sync throw: Express catches it in this call chain
  }
  res.json({ count: items.length });    // normal response
});

// Async handler: throw after await is NOT on the stack, so pass errors to next() manually
app.get("/cart/coupon", async (req, res, next) => {
  try {
    const code = req.query.code;        // coupon code from the URL
    if (!code) throw new Error("Missing code");
    res.json({ applied: code });        // success response
  } catch (err) {
    next(err);                          // route the error to the error-handling middleware
  }
});

// Error handler (4 arguments) is the last frame that receives errors
app.use((err, req, res, next) => {
  res.status(400).json({ error: err.message }); // send a clean JSON error response
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Infinite recursion लिखना, जिसमें base case नहीं है
✅ **Correct:** हर recursive function में एक साफ़ base case रखो, और depth bounded हो।

```javascript
// Wrong: no base case, stack grows until RangeError
function countDown(n) {
  console.log(n);
  return countDown(n - 1);             // never stops
}

// Right: base case stops the recursion
function countDownSafe(n) {
  if (n <= 0) return;                  // base case
  console.log(n);
  countDownSafe(n - 1);
}
countDownSafe(3); // 3, 2, 1
```

❌ **Mistake 2:** सोचना कि `try/catch` async error को भी पकड़ लेगा
✅ **Correct:** `await` के बाद का error अलग stack में होता है। उसे `await` के साथ `try/catch` में रखो।

```javascript
// Wrong: the catch never sees the async error
function loadCoupon() {
  try {
    setTimeout(() => { throw new Error("Coupon API failed"); }, 0);
  } catch (err) {
    console.log("caught", err.message); // never runs
  }
}

// Right: await the promise inside try
async function loadCouponRight() {
  try {
    await Promise.reject(new Error("Coupon API failed"));
  } catch (err) {
    console.log("caught", err.message); // caught Coupon API failed
  }
}
loadCouponRight();
```

❌ **Mistake 3:** Stack trace पर भरोसा करके async origin ढूँढना
✅ **Correct:** Async callbacks के stack trace में अक्सर सिर्फ callback दिखता है, original caller नहीं। Error को शुरू में ही context के साथ wrap करो।

---

## 🧠 Tricky Interview Question
```javascript
function f() {
  try {
    console.log("inside try");
    return "from try";                 // return value is decided here
  } finally {
    console.log("finally runs");       // finally runs BEFORE the frame is popped
  }
}

console.log(f());                      // what will be printed, and in what order?
```
**Answer:** पहले `inside try`, फिर `finally runs`, और आख़िर में `from try`। `return` का value तय हो जाता है, पर `finally` block उसी frame के अंदर पहले चलता है। Frame तभी pop होता है जब `finally` खत्म हो। अगर `finally` में `return` लिख दो, तो वही value बदल जाएगी। यही stack frame lifecycle का असली रूप है।

```javascript
// Bonus: a return inside finally overrides the earlier return value
function g() {
  try {
    return "try value";
  } finally {
    return "finally value";           // this wins and the try value is discarded
  }
}
console.log(g());                      // finally value
```

---

## ⚫ Interview Questions + Answers

Q1: Call stack क्या है और यह LIFO क्यों है?
A1: Call stack वह structure है जो बताता है कि कौन-सा function अभी चल रहा है और उसे खत्म होने पर किस caller पर लौटना है। आखिरी call सबसे पहले खत्म होती है, इसलिए यह Last In, First Out है।

Q2: Stack overflow कब होता है?
A2: जब recursion या nested calls इतने गहरे हो जाएँ कि stack की limit पार हो। V8 इसे `RangeError: Maximum call stack size exceeded` के रूप में throw करता है। Fix: base case सही करो, या loop/iteration का इस्तेमाल करो।

Q3: क्या async callback call stack पर सीधे चलता है?
A3: नहीं। Async callback तभी stack पर आता है जब call stack पूरी तरह खाली हो और event loop उसे queue से उठाए। इसलिए callback के stack में उसका original caller नहीं होता।

Q4: `try/catch` और call stack का क्या संबंध है?
A4: `try/catch` केवल उसी call stack के sync frames में थ्रो हुए errors को पकड़ता है। Timer या promise callback में बाद में होने वाला error उस `try` के stack से बाहर होता है, इसलिए उसे अलग से handle करना पड़ता है।

Q5: Recursion कब इस्तेमाल करें और कब loop?
A5: Tree, nested menu या graph जैसी bounded structures में recursion साफ़ और सही है। बहुत बड़े या unbounded input के लिए loop बेहतर है, क्योंकि उसमें हर step पर नया frame नहीं जुड़ता और overflow का खतरा नहीं रहता।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Nested function calls की flow और debugging समझनी हो
- Tree या nested data पर recursion करना हो, जिसकी depth छोटी और bounded हो
- Stack trace पढ़कर error का origin खोजना हो

❌ Avoid when:
- Recursion की depth अनजान या बहुत बड़ी हो (loop इस्तेमाल करो)
- Async callbacks से sync-style `try/catch` की उम्मीद हो
- एक ही function के अंदर बहुत गहरी chain हो, जिससे stack trace पढ़ना मुश्किल हो

---

## 📊 Visual Diagram
```
Program starts:

  push main()           stack: [ main ]
  push placeOrder()     stack: [ main | placeOrder ]
  push validateCart()   stack: [ main | placeOrder | validateCart ]
  pop  validateCart()   stack: [ main | placeOrder ]        (returned true)
  push calculateTotal() stack: [ main | placeOrder | calculateTotal ]
  pop  calculateTotal() stack: [ main | placeOrder ]
  pop  placeOrder()     stack: [ main ]
  pop  main()           stack: [ ]   <- empty, event loop can run callbacks
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Call stack | Tracks currently running functions | चल रहे functions का रिकॉर्ड |
| Stack frame | Data for one function call | एक function call की जानकारी |
| LIFO | Last in, first out | आख़िरी में आया, पहले निकला |
| Stack overflow | Too many nested frames | Stack की सीमा पार होना |
| Stack trace | List of frames shown in an error | Error के समय का call-path |
| RangeError | Error thrown on stack overflow | Stack overflow का error type |
| Base case | Condition that stops recursion | Recursion रोकने की शर्त |

---

## ⚡ 3-Line Summary
**English:**
1. Call stack LIFO structure है जो बताता है कि कौन-सा function अभी चल रहा है और return कहाँ जाना है।
2. हर call एक frame push करता है और return पर frame pop होता है; बहुत गहरी recursion stack overflow देती है।
3. Async callbacks तभी stack पर आते हैं जब stack खाली हो, इसलिए उनके errors को `await` और `next(err)` से handle करो।

**Hindi:**
1. Call stack एक LIFO structure है जो बताता है कि अभी कौन-सा function चल रहा है और return कहाँ जाना है।
2. हर call एक frame push करता है और return पर frame pop होता है; बहुत गहरी recursion stack overflow देती है।
3. Async callbacks तभी stack पर आते हैं जब stack खाली हो, इसलिए उनके errors को `await` और `next(err)` से संभालो।

---

## ➡️ Next Topic
**72. Web APIs** — देखेंगे कि timers, network और file I/O call stack से बाहर कैसे चलते हैं, और runtime उन्हें कैसे संभालता है।
