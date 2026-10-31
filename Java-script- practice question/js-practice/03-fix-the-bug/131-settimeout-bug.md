---

# Q131. Fix setTimeout Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`setTimeout` is called with the function RESULT, so it runs immediately instead of after 100ms. Fix it.

```javascript
// BUGGY CODE:
function sayHi(name) { console.log('Hi ' + name); }

setTimeout(sayHi('Aman'), 100);   // runs now, passes undefined to setTimeout
console.log('end');
```

---

## 💡 Quick Concept (2 lines only)
`setTimeout` needs a function to call later. `fn()` calls it right now and passes its return value. Pass `fn` itself, wrapped in an arrow or with extra args.
हिंदी: setTimeout को function दो, function का result नहीं — `fn()` तुरंत चल जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function sayHi(name) { console.log('Hi ' + name); } // Step 1: target function

setTimeout(() => sayHi('Aman'), 100);               // Step 2 (FIX): wrap in arrow, runs later
setTimeout(sayHi, 200, 'Riya');                     // Step 3 (FIX alt): extra args after delay
console.log('end');                                 // sync code first

// ============================================
// TEST CASES
// ============================================

// Expected output order:
// end
// Hi Aman     (after ~100ms)
// Hi Riya     (after ~200ms)
```

---

## 🔍 Why This Works (3 lines max)
An arrow wrapper delays the call until the timer fires. Extra arguments to `setTimeout` are forwarded to the callback, avoiding the wrapper.
हिंदी: arrow wrapper call को timer तक रोकता है; extra arguments सीधे callback को मिलते हैं।

---

## ⚡ Alternative Solution
```javascript
// bind creates a deferred function too
setTimeout(sayHi.bind(null, 'Sam'), 300);  // Hi Sam after 300ms
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting 0ms to run before sync code
setTimeout(() => console.log('A'), 0);
console.log('B');
// Output: B, A
// ✅ Correct mental model: callback always waits for the call stack to clear
```

---

## 🎯 Interview Tip (1 line)
Say: "Pass a function reference, not a call — and remember the delay is a minimum, not a guarantee."

---

## 🔗 Related Questions
→ Q008 (setTimeout + closure) | Q021 (this in setTimeout) | Q121 (closure bug) | Q090 (sleep function)
