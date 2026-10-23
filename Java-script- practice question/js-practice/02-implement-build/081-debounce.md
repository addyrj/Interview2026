---

# Q081. Implement Debounce
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `debounce(fn, delay)` function.
Debounce should delay invoking `fn` until after `delay` milliseconds have passed since the last time it was called. If called again before delay ends, reset the timer.

```javascript
const debouncedSearch = debounce(searchAPI, 300);
input.addEventListener('input', debouncedSearch);
// searchAPI only called 300ms after user STOPS typing
```

---

## 💡 Quick Concept (2 lines only)
Debounce delays execution until a pause — clears and resets the timer on each call. Used for search inputs, resize handlers — "wait until user stops."
हिंदी: Debounce बार-बार calls को delay करता है — last call के 300ms बाद ही function run होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function debounce(fn, delay) {
  let timerId;  // Step 1: store timer id to cancel previous call
  
  return function(...args) {    // Step 2: return wrapper function
    clearTimeout(timerId);      // Step 3: cancel previous timer (if any)
    
    timerId = setTimeout(() => {  // Step 4: set new timer
      fn.apply(this, args);       // Step 5: call original fn with correct this + args
    }, delay);
  };
}

// ============================================
// TEST CASES
// ============================================

const log = debounce((msg) => console.log(msg), 300);

log('a');   // Timer set for 300ms
log('b');   // Timer reset — 'a' never fires
log('c');   // Timer reset — 'b' never fires
// After 300ms of silence:
// Expected: 'c'   ← only the last call runs

// Immediate execution version:
function debounceImmediate(fn, delay) {
  let timerId;
  return function(...args) {
    const callNow = !timerId;        // call immediately if no timer running
    clearTimeout(timerId);
    timerId = setTimeout(() => {
      timerId = null;                // reset after delay
    }, delay);
    if (callNow) fn.apply(this, args);  // execute on leading edge
  };
}
```

---

## 🔍 Why This Works (3 lines max)
Each call clears the previous `setTimeout` and creates a new one. Only the LAST call's timer isn't cancelled — it runs after the delay. `this` and `args` are captured and forwarded so the debounced function works as a method too.
हिंदी: हर call पिछला timer cancel करती है और नया set करती है — सिर्फ last call का timer complete होता है।

---

## ⚡ Alternative Solution
```javascript
// More complete version with cancel + flush:
function debounce(fn, delay) {
  let timerId;
  
  const debounced = function(...args) {
    clearTimeout(timerId);
    timerId = setTimeout(() => fn.apply(this, args), delay);
  };
  
  debounced.cancel = () => clearTimeout(timerId);  // cancel pending call
  debounced.flush = function(...args) {             // execute immediately
    clearTimeout(timerId);
    fn.apply(this, args);
  };
  
  return debounced;
}

// Usage with cancel:
const search = debounce(callAPI, 300);
search('react');
search.cancel();  // cancel pending call
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not preserving 'this' context
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(function() {
      fn(...args);  // ❌ lost 'this' — use fn.apply(this, args)
    }, delay);
  };
}

// ✅ Correct: use arrow function in setTimeout (captures outer 'this')
// OR use fn.apply(this, args)
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);  // arrow preserves this
  };
}
```

---

## 🎯 Interview Tip (1 line)
Say: "Debounce = trailing edge delay; real-world: search bar, window resize, form validation — 'fire after user stops.'"

---

## 🔗 Related Questions
→ Q082 (throttle) | Q083 (memoize) | Q181 (search with debounce) | Q308 (debounce real use case)
