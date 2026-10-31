---

# Q296. call stack vs event loop
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the call stack, what is the event loop, and how do they work together? Demonstrate stack order (LIFO), a stack overflow, and how the loop schedules microtasks and macrotasks.

---

## 💡 Quick Concept (2 lines only)
The call stack runs one function at a time (LIFO). The event loop watches the stack and, when empty, pushes the next callback from the microtask queue, then the macrotask queue.
हिंदी: Call stack एक बार में एक function चलाता है; event loop stack खाली होने पर queue से अगला callback भेजता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: nested calls are pushed on the stack and popped in reverse (LIFO)
// Step 2: infinite recursion overflows the stack -> RangeError
// Step 3: async callbacks wait in queues until the stack is empty

function c() { console.log('c runs (top of stack)'); } // innermost function
function b() { console.log('b start'); c(); console.log('b end'); } // calls c
function a() { console.log('a start'); b(); console.log('a end'); } // calls b

function recurse() { recurse(); } // never returns -> grows stack until limit

// ============================================
// TEST CASES
// ============================================

try {
  recurse();                                 // keep pushing frames
} catch (e) {
  console.log('overflow caught:', e instanceof RangeError); // Expected: overflow caught: true
}

console.log('script start');                                  // sync
a();                                                          // see stack order below
setTimeout(() => console.log('timeout (macrotask)'), 0);      // goes to macrotask queue
Promise.resolve().then(() => console.log('promise (microtask)')); // goes to microtask queue
console.log('script end');                                    // sync

// Expected output (in order):
// overflow caught: true
// script start
// a start
// b start
// c runs (top of stack)
// b end
// a end
// script end
// promise (microtask)
// timeout (macrotask)
```

---

## 🔍 Why This Works (3 lines max)
`a -> b -> c` push in order and pop in reverse, so "b end" prints after "c". `setTimeout` and `.then` only register callbacks; the event loop runs them once the stack is empty, microtasks first. Too many frames means `RangeError`.
हिंदी: Stack LIFO चलता है; event loop खाली stack देखकर पहले microtask फिर macrotask चलाता है।

---

## ⚡ Alternative Solution
```javascript
// Fix a deep recursion overflow by using a loop (no stack growth)
function sumTo(n) {
  let total = 0;                       // accumulator
  for (let i = 1; i <= n; i++) total += i; // iterate instead of recurse
  return total;                        // result
}
console.log(sumTo(1000000)); // 500000500000 (recursion version would overflow)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking setTimeout(fn, 0) runs immediately
setTimeout(() => console.log('timer'), 0);
console.log('after');   // prints BEFORE timer

// ❌ Wrong: blocking the stack freezes everything (UI, timers)
// while (true) {}      // nothing else can ever run

// ✅ Correct: split heavy work into chunks with setTimeout / workers
```

---

## 🎯 Interview Tip (1 line)
Say: "Stack runs sync code LIFO; the event loop moves queued callbacks onto it when empty — microtasks always before the next macrotask."

---

## 🔗 Related Questions
→ Q016 (microtask vs macrotask) | Q017 (event loop order) | Q163 (explain event loop) | Q295 (sync vs async)
