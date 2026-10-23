---

# Q301. Closure Real Use Case
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain closures with 3 real-world use cases. Implement:
1. A counter factory
2. A private data pattern
3. A function with "memory"

---

## 💡 Quick Concept (2 lines only)
A closure is a function that "remembers" the variables from its outer scope even after the outer function has returned. Inner function + outer scope variables = closure.
हिंदी: Closure वो function है जो outer scope के variables को याद रखता है — outer function return होने के बाद भी।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — 3 Real Use Cases
// ============================================

// ─── USE CASE 1: Counter Factory ─────────────────────────────
function createCounter(start = 0, step = 1) {
  let count = start;  // private to this closure
  
  return {
    increment() { count += step; return count; },
    decrement() { count -= step; return count; },
    reset()     { count = start; return count; },
    getCount()  { return count; }
  };
}

const counter1 = createCounter(0, 1);
const counter2 = createCounter(10, 5);  // independent counter

console.log(counter1.increment());  // 1
console.log(counter1.increment());  // 2
console.log(counter2.increment());  // 15 (independent)
console.log(counter1.getCount());   // 2 (not affected by counter2)

// ─── USE CASE 2: Private Data (encapsulation) ─────────────────
function createUser(name, password) {
  // password is PRIVATE — can never be accessed directly
  let _password = password;
  let loginAttempts = 0;
  
  return {
    getName() { return name; },
    login(pwd) {
      loginAttempts++;
      if (loginAttempts > 3) return 'Account locked!';
      return _password === pwd ? 'Welcome!' : 'Wrong password';
    },
    getAttempts() { return loginAttempts; }
    // No way to read _password directly!
  };
}

const user = createUser('Arjun', 'secret123');
console.log(user.getName());          // 'Arjun'
console.log(user.login('wrong'));      // 'Wrong password'
console.log(user.login('secret123')); // 'Welcome!'
// console.log(user._password);       // undefined — truly private!

// ─── USE CASE 3: Memoize / Function with Memory ──────────────
function makeMultiplier(factor) {
  // factor is "remembered" by the returned function
  return function(number) {
    return number * factor;
  };
}

const double = makeMultiplier(2);
const triple = makeMultiplier(3);
const taxCalc = makeMultiplier(1.18);  // GST calculator

console.log(double(5));    // 10
console.log(triple(5));    // 15
console.log(taxCalc(100)); // 118

// ============================================
// TEST CASES
// ============================================

// React real use case — event handlers in loops:
function setupButtons() {
  const buttons = ['Home', 'About', 'Contact'];
  
  return buttons.map((name, index) => {
    // Each button handler "closes over" its own name and index
    return {
      name,
      onClick: () => console.log(`Clicked: ${name} (index ${index})`)
    };
  });
}

const btns = setupButtons();
btns[0].onClick();  // 'Clicked: Home (index 0)'
btns[2].onClick();  // 'Clicked: Contact (index 2)'
```

---

## 🔍 Why This Works (3 lines max)
When `createCounter` returns, its `count` variable normally would be garbage collected. But the returned functions (increment/decrement) still reference `count` — so JS keeps it alive in a "closure." Each `createCounter` call creates an independent closure.
हिंदी: Outer function return होने के बाद भी inner function variables को याद रखती है — यही closure है।

---

## ⚡ Alternative Solution
```javascript
// Closure in React (hooks under the hood):
function useState(initial) {
  let state = initial;  // closure over this variable
  
  function getState() { return state; }
  function setState(newValue) { state = newValue; }
  
  return [getState, setState];
}

// Closure for event listener cleanup:
function setupSearch(inputEl, onSearch) {
  let debounceTimer;
  
  const handler = (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => onSearch(e.target.value), 300);
  };
  
  inputEl.addEventListener('input', handler);
  
  // Return cleanup — handler closes over debounceTimer
  return () => {
    inputEl.removeEventListener('input', handler);
    clearTimeout(debounceTimer);  // can access debounceTimer via closure
  };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Classic closure bug in var loops:
const funcs = [];
for (var i = 0; i < 3; i++) {
  funcs.push(() => console.log(i));  // all close over SAME i
}
funcs[0]();  // 3 (not 0!)
funcs[1]();  // 3 (not 1!)

// ✅ Fix with let (new binding per iteration):
for (let i = 0; i < 3; i++) {
  funcs.push(() => console.log(i));
}
funcs[0]();  // 0 ✅

// ❌ Wrong: thinking closure captures VALUE (it captures REFERENCE)
let x = 1;
const fn = () => console.log(x);
x = 5;
fn();  // 5, not 1 — closure sees current value of x, not value at capture time
```

---

## 🎯 Interview Tip (1 line)
Say: "Closure = function + its outer scope; used for: private data, factory functions, memoization, event handlers — fundamental to React hooks."

---

## 🔗 Related Questions
→ Q006 (closure loop var) | Q161 (closure explained deep) | Q081 (debounce uses closure) | Q083 (memoize uses closure)
