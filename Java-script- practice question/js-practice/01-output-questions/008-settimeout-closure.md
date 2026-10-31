---

# Q008. setTimeout + Closure Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
function outer() {
  let count = 0;
  setTimeout(() => console.log('timeout', count), 0);
  count++;
  count++;
}
outer();
console.log('sync');
```

---

## 💡 Quick Concept (2 lines only)
A closure captures the variable itself, not its value at that moment; the timer callback sees the latest value when it finally runs.
हिंदी: Closure variable को याद रखता है, उस समय की value को नहीं, इसलिए callback में latest value दिखती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: outer() schedules a timer, then increments count twice
// Step 2: 'sync' prints (call stack still running)
// Step 3: timer fires later and reads count = 2

function outer() {
  let count = 0;                                     // variable in closure
  setTimeout(() => console.log('timeout', count), 0); // runs after sync code
  count++;                                           // count = 1
  count++;                                           // count = 2
}
outer();                                             // schedule timer
console.log('sync');                                 // prints first

// ============================================
// TEST CASES
// ============================================

function make() {
  let n = 10;                                        // captured variable
  const show = () => n;                              // closure reads n live
  n = 20;                                            // change after creating closure
  return show;                                       // return closure
}
console.log(make()());                               // Expected: 20

// Overall output:
// sync
// 20
// timeout 2
```

---

## 🔍 Why This Works (3 lines max)
The callback keeps a reference to `count` in its lexical scope. The timer runs only after the stack is empty, by which time count is already 2.
हिंदी: Callback बाद में चलता है, तब तक count 2 हो चुका होता है, इसलिए "timeout 2" print होता है।

---

## ⚡ Alternative Solution
```javascript
// Capture the value instead of the variable
function outer2() {
  let count = 0;                                     // original variable
  const snapshot = count;                            // copy current value
  setTimeout(() => console.log('snap', snapshot), 0); // uses the copy
  count++;                                           // does not affect snapshot
}
outer2();                                            // Expected (later): snap 0
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Expecting the callback to print the value at scheduling time (0)
// ✅ It prints the value at execution time; copy the value if you need a snapshot
```

---

## 🎯 Interview Tip (1 line)
Say: "Closures capture references (live bindings), and timers run after the call stack clears."

---

## 🔗 Related Questions
→ Q006 (closure in loop) | Q009 (setTimeout + var) | Q010 (setTimeout + let) | Q161 (explain closure)
