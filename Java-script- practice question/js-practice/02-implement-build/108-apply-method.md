---

# Q108. Implement Apply Method
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `Function.prototype.myApply(context, argsArray)` that works like `apply`: calls the function with `this = context` and arguments taken from an array.

```javascript
Math.max.myApply(null, [1, 5, 3]); // 5
```

---

## 💡 Quick Concept (2 lines only)
Same trick as `call`: attach function to the context, invoke it, delete it. Only difference — arguments arrive as ONE array.
हिंदी: `apply` बिल्कुल `call` जैसा है, फर्क बस इतना कि arguments एक array में आते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: default context to globalThis, wrap primitives
// Step 2: attach function under a Symbol key
// Step 3: spread the args array (or none) and call

Function.prototype.myApply = function (context, argsArray) {
  context = context == null ? globalThis : Object(context); // handle null/undefined/primitive
  const key = Symbol('fn');                  // unique temporary key
  context[key] = this;                       // store the function on context
  const result = argsArray == null
    ? context[key]()                         // no args given
    : context[key](...argsArray);            // spread array into arguments
  delete context[key];                       // cleanup
  return result;                             // return the function result
};

// ============================================
// TEST CASES
// ============================================

console.log(Math.max.myApply(null, [1, 5, 3]));       // Expected: 5

function intro(city, job) {
  return `${this.name} - ${city} - ${job}`;           // uses this.name
}
console.log(intro.myApply({ name: 'Aditya' }, ['Delhi', 'Dev'])); // Expected: Aditya - Delhi - Dev

function whoAmI() { return this.id; }
console.log(whoAmI.myApply({ id: 42 }));              // Expected: 42

console.log(intro.apply({ name: 'Native' }, ['X', 'Y'])); // Expected: Native - X - Y
```

---

## 🔍 Why This Works (3 lines max)
Calling `context[key](...)` makes `this` the context. The spread operator turns the array into separate arguments, and `delete` leaves the object untouched.
हिंदी: Spread array को अलग-अलग arguments बना देता है और delete से object साफ़ रहता है।

---

## ⚡ Alternative Solution
```javascript
// Using Reflect.apply — shortest
Function.prototype.myApply2 = function (context, args = []) {
  return Reflect.apply(this, context, args); // native does the same job
};
console.log(Math.min.myApply2(null, [4, 2, 8])); // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: passing the array as a single argument
context[key](argsArray);     // function receives ONE array argument

// ✅ Correct: spread it
context[key](...argsArray);
```

---

## 🎯 Interview Tip (1 line)
Say: "call takes args one by one, apply takes an array — a = array, c = comma."

---

## 🔗 Related Questions
→ Q107 (call) | Q109 (bind) | Q023 (call/apply/bind output)
