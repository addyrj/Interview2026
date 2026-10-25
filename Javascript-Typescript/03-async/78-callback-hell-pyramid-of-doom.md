# 78. Callback Hell (Pyramid of Doom)
# हिंदी में: Callback Hell (Pyramid of Doom) — nested callbacks की दलदल

---

## 🔵 Simple Definition (English)
**Callback hell** (or pyramid of doom) is code where several dependent async steps are nested inside each other's callbacks. The code moves right with every step, becomes hard to read, and error handling gets repeated or missed.

## 🔵 सरल परिभाषा (Hindi)
**Callback hell** (जिसे pyramid of doom भी कहते हैं) वह code है जिसमें कई dependent async steps एक-दूसरे के callback के अंदर nested होते हैं। हर step के साथ code दाईं ओर खिसकता है, पढ़ना मुश्किल होता है, और error handling बार-बार दोहराना पड़ता है या छूट जाता है।

---

## 🔴 Problem it Solves
यह समस्या खुद callback pattern से पैदा हुई। जब अगला step पिछले step के result पर निर्भर होता है, तो उसे पिछले callback के अंदर ही लिखना पड़ता था। इसे सुधारने के लिए हमें sequencing का ऐसा तरीका चाहिए था जो flat हो, और error एक ही जगह पकड़ा जाए।

## 🔴 यह क्यों बना? (Hindi)
Flipkart checkout में सोचो: user लाओ → उसका cart लाओ → cart के products लाओ → price calculate करो → order बनाओ → email भेजो। हर step अगले पर निर्भर है। Callbacks में यह छह स्तर गहरा pyramid बन जाता है। इसी दर्द ने promises और async/await को जन्म दिया।

---

## 🟢 How it Works — Step by Step

Step 1 → पहला async step शुरू होता है और उसका callback एक दूसरा async step शुरू करता है
Step 2 → हर अगला step पिछले callback के अंदर nested होता है, इसलिए indentation बढ़ती है
Step 3 → हर स्तर पर `if (err)` दोहराना पड़ता है
Step 4 → Refactor में हर step को नाम वाला function बनाकर सिर्फ उसका नाम chain किया जाता है
Step 5 → Promise या async/await में यही chain flat दिखती है, और error एक `catch` में आता है

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पहला async step शुरू होता है, उसका callback दूसरा step शुरू करता है
Step 2 → हर अगला step पिछले callback के अंदर nested होता है, इसलिए indentation बढ़ती है
Step 3 → हर स्तर पर `if (err)` दोहराना पड़ता है
Step 4 → Refactor में हर step नाम वाला function बनता है, और उसे नाम से chain किया जाता है
Step 5 → Promise या async/await में chain flat दिखती है, और error एक `catch` में आता है

---

## 🟡 Real World Example
एक purana Node.js service जो payment के लिए सीधे callbacks लिखता था: user verify → wallet check → debit → ledger entry → SMS भेजना। हर step के अंदर अगला step और हर जगह error check। जब एक step का error छूट गया, तो wallet debit हो गया पर ledger नहीं बना। Refactor करके flat async/await लिखने के बाद यह bug आसानी से दिखा और ठीक हुआ।

## 🟡 Real Example Hindi mein
एक पुरानी payment service में callbacks से: user verify → wallet check → debit → ledger → SMS, हर step के अंदर अगला step। एक जगह error छूट गया, तो wallet debit हो गया पर ledger नहीं बना। Flat async/await में refactor करने पर यह bug साफ़ दिखा और ठीक हुआ।

---

## 💻 Code Example — Basic
```javascript
// Demo: a pyramid of callbacks, then the same flow refactored into flat named steps
// Run with: node 78-callback-hell-pyramid-of-doom.js

// Fake async step: calls cb(null, value) after `ms` milliseconds
function step(name, ms, cb) {
  setTimeout(() => cb(null, `${name} ok`), ms); // success result after a delay
}

// ── PYRAMID VERSION: each step nested inside the previous callback ──
step("verify user", 10, (err, a) => {          // level 1
  if (err) return console.log("error");        // error check repeated at each level
  console.log(a);
  step("load cart", 10, (err2, b) => {         // level 2 (indented one more)
    if (err2) return console.log("error");
    console.log(b);
    step("price cart", 10, (err3, c) => {      // level 3
      if (err3) return console.log("error");
      console.log(c);
      console.log("pyramid finished");         // the final line is buried deep
    });
  });
});

// ── FLAT VERSION: name each step, then call them in a clear sequence ──
function verifyUser(cb) { step("verify user", 10, cb); } // wrapper with a name
function loadCart(cb) { step("load cart", 10, cb); }     // wrapper with a name
function priceCart(cb) { step("price cart", 10, cb); }   // wrapper with a name

// Still callbacks, but the nesting is shallow and each function has one job
verifyUser((err, a) => {
  if (err) return console.log("error");
  loadCart((err2, b) => {
    if (err2) return console.log("error");
    priceCart((err3, c) => {
      if (err3) return console.log("error");
      console.log("flat finished", a, b, c);   // one place to read the final result
    });
  });
});
```

## 💻 Code Example — Advanced
```javascript
// Goal: run a list of error-first async tasks one after another,
// stop at the first error, and collect all results in order.

// series(tasks, finalCb): each task is a function (cb) => void
function series(tasks, finalCb) {
  const results = [];                          // results in the same order as tasks
  let index = 0;                               // position of the next task to run

  function next(err, value) {                  // one callback handles every step
    if (err) return finalCb(err);              // stop at the first error, skip the rest
    if (index > 0) results.push(value);        // store the result of the previous task
    if (index === tasks.length) {              // all tasks done
      return finalCb(null, results);           // deliver the full list of results
    }
    const task = tasks[index++];               // take the next task and advance
    task(next);                                // run it; it will call next when done
  }

  next(null);                                  // kick off the first task
}

// Helper: make a fake async task that succeeds or fails after `ms`
const task = (name, ms, fail = false) => (cb) => {
  setTimeout(() => {
    if (fail) return cb(new Error(`${name} failed`)); // error-first failure
    cb(null, `${name} ok`);                    // error-first success
  }, ms);
};

// Success case: all three steps run in order, results collected
series([task("user", 10), task("cart", 10), task("order", 10)], (err, results) => {
  if (err) return console.log("series error:", err.message);
  console.log("results:", results);             // [ 'user ok', 'cart ok', 'order ok' ]
});

// Failure case: second step fails, third never runs
series([task("user", 10), task("payment", 10, true), task("email", 10)], (err) => {
  console.log("stopped with:", err.message);    // payment failed
});
```

---

## 🟠 Express.js Integration
Express में callback hell अक्सर route handler के अंदर कई DB/API calls को nested callbacks में लिखने से आती है। नीचे का route पहले callbacks से nested रूप में दिखाया गया है, फिर async/await से flat रूप में। इसमें Express का कोई खास feature नहीं, सिर्फ normal async structure का फर्क है।

```javascript
const express = require("express");          // web framework
const app = express();

// Fake async data sources (callback style, for illustration)
const getUser = (id, cb) => setTimeout(() => cb(null, { id, name: "Aditya" }), 5);
const getOrders = (uid, cb) => setTimeout(() => cb(null, [{ id: 1, uid }]), 5);

// ── PYRAMID: route with nested callbacks ──
app.get("/pyramid/:id", (req, res) => {
  getUser(req.params.id, (err, user) => {    // level 1
    if (err) return res.status(500).end();
    getOrders(user.id, (err2, orders) => {   // level 2
      if (err2) return res.status(500).end();
      res.json({ user, orders });            // response buried inside two callbacks
    });
  });
});

// ── FLAT: same logic with promise wrappers and async/await ──
const getUserP = (id) => new Promise((res, rej) => getUser(id, (e, v) => (e ? rej(e) : res(v))));
const getOrdersP = (uid) => new Promise((res, rej) => getOrders(uid, (e, v) => (e ? rej(e) : res(v))));

app.get("/flat/:id", async (req, res, next) => {
  try {
    const user = await getUserP(req.params.id);   // step 1, flat
    const orders = await getOrdersP(user.id);     // step 2, flat
    res.json({ user, orders });                   // response at the same indentation level
  } catch (err) {
    next(err);                                    // one error path for the whole route
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** हर level पर error check छोड़ देना
✅ **Correct:** हर async step के बाद error जाँचो, या `series` जैसा helper इस्तेमाल करो जो पहली error पर रुक जाए।

```javascript
// Wrong: second step error is ignored; the code keeps using undefined data
getUser(1, (err, user) => {
  getOrders(user.id, (err2, orders) => {   // user may be undefined if getUser failed
    console.log(orders.length);            // crash, far from the real cause
  });
});

// Right: check each step's error before using its result
getUser(1, (err, user) => {
  if (err) return console.log("user error", err.message);
  getOrders(user.id, (err2, orders) => {
    if (err2) return console.log("orders error", err2.message);
    console.log(orders.length);
  });
});
```

❌ **Mistake 2:** Independent async कामों को भी एक-एक करके nest करना
✅ **Correct:** जो काम एक-दूसरे पर निर्भर नहीं हैं, उन्हें साथ चलाओ (Promise.all)।

```javascript
// Wrong: user and product are independent, but they run one after another
getUser(1, (e1, user) => {
  getProduct(9, (e2, product) => {       // could have started at the same time
    console.log(user, product);
  });
});

// Right (with promise wrappers): run both at once
// const [user, product] = await Promise.all([getUserP(1), getProductP(9)]);
```

❌ **Mistake 3:** Refactor करते समय callbacks को promise में बदलकर भी error handling दो जगह छोड़ देना
✅ **Correct:** Promise chain में एक `catch` या `try/catch` पूरे flow को संभाले।

```javascript
// Wrong: the first promise error is never caught
getUserP(1).then((user) => getOrdersP(user.id)).then((orders) => console.log(orders));
// unhandled rejection if getUserP fails

// Right: one catch at the end covers every step
getUserP(1)
  .then((user) => getOrdersP(user.id))
  .then((orders) => console.log(orders))
  .catch((err) => console.log("failed:", err.message));
```

---

## 🧠 Tricky Interview Question
```javascript
function step(name, cb) {
  setTimeout(() => cb(null, name), 0);      // result comes later, asynchronously
}

try {
  step("A", (err, a) => {
    step("B", (err2, b) => {
      throw new Error("boom in B");          // thrown inside a timer callback
    });
  });
  console.log("try finished");
} catch (e) {
  console.log("caught:", e.message);         // is this line ever printed?
}
```
**Answer:** `try finished` छपता है, पर `caught: boom in B` कभी नहीं। `try` block केवल उसी sync call stack को cover करता है जो उसके अंदर चला। `step` का callback बाद में timer queue से चलता है, उस समय `try` कब का खत्म हो चुका है। `boom in B` एक uncaught exception बन जाता है, और Node process error के साथ बंद हो जाता है (exit code 1)। यही कारण है कि callback-based nested code में error handling हर level पर ज़रूरी है।

---

## ⚫ Interview Questions + Answers

Q1: Callback hell क्या है?
A1: Dependent async steps को एक-दूसरे के callback के अंदर nest करना। इससे code दाईं ओर बढ़ता है, पढ़ना कठिन होता है, और error handling बिखर जाता है।

Q2: Callback hell को कैसे सुधारें?
A2: हर step को नाम वाला function बनाकर flat रखें, helper (जैसे `series`) से tasks को sequence में चलाएँ, या promises और async/await इस्तेमाल करें।

Q3: Callback hell में error handling क्यों मुश्किल है?
A3: हर level पर अलग `if (err)` चाहिए, और कोई error ऊपर के `try/catch` तक नहीं पहुँचता, क्योंकि callback बाद में अलग stack पर चलता है।

Q4: Promises callback hell को कैसे हल करते हैं?
A4: Promise chain में हर step `then` में flat रहता है, और error एक `catch` तक bubble करता है। `async/await` इसे sync जैसा पढ़ने लायक बनाता है।

Q5: क्या हर nested callback बुरा है?
A5: नहीं। एक या दो स्तर का nesting ठीक है, खासकर event listeners या array callbacks में। Problem तब है जब dependent async steps गहराई में जाते रहें।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- पुराने callback-style APIs के साथ काम करना हो, तो उन्हें promise wrapper में लपेटो
- एक-दो स्तर की nesting सरल और स्पष्ट हो
- Helper (जैसे `series`) से tasks को क्रम में चलाना हो

❌ Avoid when:
- नया code लिखा जा रहा हो, वहाँ async/await इस्तेमाल करो
- Independent कामों को एक-एक करके nest करना हो (Promise.all बेहतर है)
- कई स्तरों तक dependent steps हों, जिनमें error handling बिखरता हो

---

## 📊 Visual Diagram
```
PYRAMID (hard to read):                  FLAT (easy to read):

getUser(cb1) {                           const user   = await getUser();
  if (err) ...                           const orders = await getOrders(user.id);
  getOrders(cb2) {                       const cart   = await getCart(user.id);
    if (err) ...
    getCart(cb3) {                       try { ... } catch (err) { /* one place */ }
      if (err) ...
      ...
    }
  }
}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Callback hell | Deep nesting of callbacks | Callbacks का गहरा nesting |
| Pyramid of doom | Visual name for the rightward staircase | Indentation की सीढ़ी |
| Sequencing | Running steps one after another | कामों को एक-एक करके चलाना |
| Flatten | Remove nesting by naming steps | Nesting हटाकर सीधा लिखना |
| Error propagation | Passing error up to one handler | Error को एक जगह तक पहुँचाना |
| Refactor | Rewrite code without changing behavior | व्यवहार बदले बिना code सुधारना |
| Unhandled rejection | Promise error with no catch | बिना catch वाला promise error |

---

## ⚡ 3-Line Summary
**English:**
1. Callback hell तब बनता है जब dependent async steps एक-दूसरे के callback के अंदर nested हों।
2. इसे नाम वाले functions, `series` जैसे helper, या promises और async/await से flat करो।
3. Error handling एक जगह रखो, और independent कामों को `Promise.all` से साथ चलाओ।

**Hindi:**
1. Callback hell तब बनता है जब dependent async steps एक-दूसरे के callback के अंदर nested हों।
2. इसे नाम वाले functions, `series` जैसे helper, या promises और async/await से flat करो।
3. Error handling एक जगह रखो, और independent कामों को `Promise.all` से साथ चलाओ।

---

## ➡️ Next Topic
**79. Promises — Complete Guide** — Promise कैसे बनता है, `then/catch/finally` कैसे chain होते हैं, और `Promise.all` व `race` कब काम आते हैं।
