---

# Q161. Explain Closure with Example
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain what a closure is in JavaScript. Provide 5 practical examples showing different use cases. What problem does closure solve?

---

## 💡 Quick Concept (2 lines only)
A closure is a function that has access to variables from its outer (enclosing) scope, even after the outer function has returned. The inner function "closes over" the outer variables.
हिंदी: Closure = inner function जो outer function के variables को याद रखती है — outer function return होने के बाद भी।

---

## ✅ Answer / Solution

```javascript
// ============================================
// WHAT IS A CLOSURE?
// ============================================

function outer() {
  let count = 0;         // outer scope variable
  
  function inner() {     // inner function
    count++;             // accesses outer variable
    return count;
  }
  
  return inner;          // return the inner function
}

const counter = outer();  // outer() is done, but count lives on
console.log(counter());   // 1 — count is preserved in closure
console.log(counter());   // 2 — same count variable!
console.log(counter());   // 3

// WHY: inner() still references count → JS keeps count alive in memory
// This "closed over" environment = the closure

// ============================================
// 5 PRACTICAL EXAMPLES
// ============================================

// EXAMPLE 1: Data Privacy / Encapsulation
function createBankAccount(initialBalance) {
  let balance = initialBalance;  // PRIVATE — can't access directly
  
  return {
    deposit(amount)  { balance += amount; return balance; },
    withdraw(amount) {
      if (amount > balance) return 'Insufficient funds';
      balance -= amount;
      return balance;
    },
    getBalance() { return balance; }
  };
}

const account = createBankAccount(1000);
account.deposit(500);     // 1500
account.withdraw(200);    // 1300
// account.balance        // undefined — no direct access!

// EXAMPLE 2: Function Factory
function multiplier(factor) {
  return n => n * factor;   // closes over factor
}

const double = multiplier(2);
const triple = multiplier(3);
const gst    = multiplier(1.18);

console.log(double(10));  // 20
console.log(triple(10));  // 30
console.log(gst(100));    // 118

// EXAMPLE 3: Memoization (caching with closure)
function makeMemoized(fn) {
  const cache = {};  // cache lives in closure
  
  return function(n) {
    if (n in cache) return cache[n];
    cache[n] = fn(n);
    return cache[n];
  };
}

const memoFib = makeMemoized(function fib(n) {
  if (n <= 1) return n;
  return memoFib(n-1) + memoFib(n-2);
});

console.log(memoFib(40));  // Fast — cached results reused

// EXAMPLE 4: Event Handler with State
function setupClickCounter(buttonEl) {
  let clickCount = 0;  // state in closure
  
  buttonEl.addEventListener('click', function() {
    clickCount++;
    console.log(`Clicked ${clickCount} times`);
    if (clickCount === 5) console.log('Milestone: 5 clicks!');
  });
}
// Each button gets its own independent clickCount

// EXAMPLE 5: Partial Application
function partial(fn, ...presetArgs) {
  return function(...laterArgs) {
    return fn(...presetArgs, ...laterArgs);  // presetArgs in closure
  };
}

function add(a, b, c) { return a + b + c; }

const add5 = partial(add, 5);      // preset first arg = 5
const add5and10 = partial(add, 5, 10); // preset first two args

console.log(add5(3, 7));    // 15 (5+3+7)
console.log(add5and10(2));  // 17 (5+10+2)
```

---

## 🔍 Why This Works (3 lines max)
When a function is created, it captures a reference to its surrounding scope's variables — not a copy. This captured scope persists in memory as long as the inner function exists. Garbage collector keeps it alive since the inner function references it.
हिंदी: Inner function बनते वक्त outer scope का reference capture होता है — outer function खत्म हो तो भी वो reference रहता है।

---

## ⚡ Alternative Solution
```javascript
// React hooks ARE closures:
function useCounter(initial = 0) {
  let count = initial;  // closure variable
  
  return {
    getCount: () => count,
    increment: () => ++count,
    decrement: () => --count
  };
}

// useState is essentially:
function useState(initial) {
  let state = initial;
  
  const getState = () => state;
  const setState = (newVal) => {
    state = typeof newVal === 'function' ? newVal(state) : newVal;
  };
  
  return [getState, setState];
}

// useEffect cleanup is a closure:
useEffect(() => {
  const timer = setInterval(() => {
    console.log('tick');
  }, 1000);
  
  return () => clearInterval(timer);  // cleanup closes over timer
}, []);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Classic: closure captures reference, not value
function createButtons() {
  const buttons = [];
  
  for (var i = 0; i < 3; i++) {
    buttons.push(() => console.log(i));  // all close over SAME i
  }
  
  return buttons;
}

createButtons()[0]();  // 3 (not 0!)
createButtons()[1]();  // 3 (not 1!)

// ✅ Fix 1: use let (new binding per iteration)
for (let i = 0; i < 3; i++) { ... }

// ✅ Fix 2: IIFE to capture current value
for (var i = 0; i < 3; i++) {
  buttons.push(((j) => () => console.log(j))(i));  // j captures i's current value
}
```

---

## 🎯 Interview Tip (1 line)
Say: "Closure = function + lexical environment; key use cases: data privacy, memoization, event handlers, partial application — React hooks are closures."

---

## 🔗 Related Questions
→ Q006 (closure loop bug) | Q081 (debounce — closure) | Q083 (memoize — closure) | Q301 (closure real use case)
