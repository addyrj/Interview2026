---

# Q274. Chain of Responsibility
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a middleware-style chain (auth -> validate -> handle) where each handler either processes the request or passes it to the next.

---

## 💡 Quick Concept (2 lines only)
A request travels through a chain of handlers; each decides to handle it or call `next()`.
हिंदी: Request handlers की कतार से गुजरता है, हर handler या तो रोकता है या आगे भेजता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Handlers are (req, next) => ...
// Step 2: A runner calls handler i, passing next = run(i+1)
// Step 3: A handler that skips next() stops the chain

function createChain(...handlers) {
  return function run(req) {
    let i = 0;                                   // current handler index
    const next = () => {                         // moves to next handler
      const h = handlers[i++];                   // pick and advance
      return h ? h(req, next) : undefined;       // end of chain returns undefined
    };
    return next();                               // start chain
  };
}

const auth = (req, next) => (req.user ? next() : 'Error: unauthenticated'); // stop if no user
const validate = (req, next) => (req.body ? next() : 'Error: empty body');  // stop if no body
const handle = (req) => `OK: saved ${req.body}`;                            // final handler

const pipeline = createChain(auth, validate, handle); // wire up the chain

// ============================================
// TEST CASES
// ============================================

console.log(pipeline({ user: 'a', body: 'data' })); // Expected: OK: saved data
console.log(pipeline({ body: 'data' }));            // Expected: Error: unauthenticated
console.log(pipeline({ user: 'a' }));               // Expected: Error: empty body
```

---

## 🔍 Why This Works (3 lines max)
Each handler gets a `next` function; calling it continues the chain, not calling it short-circuits. Sender doesn't know who finally handles it.
हिंदी: next() call करने पर chain आगे बढ़ती है, न करने पर वहीं रुक जाती है।

---

## ⚡ Alternative Solution
```javascript
// Linked-handler style
class Handler {
  setNext(h) { this.nextH = h; return h; }                         // link and return for chaining
  handle(n) { return this.nextH ? this.nextH.handle(n) : 'unhandled'; } // default: pass on
}
class Small extends Handler { handle(n) { return n < 10 ? 'small' : super.handle(n); } } // handles <10
class Big extends Handler { handle(n) { return n >= 10 ? 'big' : super.handle(n); } }    // handles >=10
const s = new Small(); s.setNext(new Big());                       // build chain
console.log(s.handle(5), s.handle(50));                            // Expected: small big
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: handler forgets to return next() result (async chains lose value)
// ✅ Correct: return next() so the final result bubbles back
```

---

## 🎯 Interview Tip (1 line)
Say Express/Koa middleware and DOM event bubbling are real-world chains of responsibility.

---

## 🔗 Related Questions
→ Q086 (Pipe) | Q085 (Compose) | Q310 (Event bubbling)
