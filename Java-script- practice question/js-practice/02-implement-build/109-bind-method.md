---

# Q109. Implement Bind Method
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `Function.prototype.myBind(context, ...boundArgs)` that returns a NEW function with `this` fixed to `context` and some arguments pre-filled. It must also work with `new`.

```javascript
const hi = greet.myBind({ name: 'Aditya' }, 'Hello');
hi('!'); // "Hello Aditya!"
```

---

## 💡 Quick Concept (2 lines only)
`bind` does not run the function — it returns a wrapper that later calls the original with fixed `this` and merged arguments.
हिंदी: `bind` function को तुरंत नहीं चलाता, बल्कि पक्के `this` वाला नया function लौटाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: remember the original function (this)
// Step 2: return a wrapper that merges bound args + new args
// Step 3: if called with `new`, ignore the bound context

Function.prototype.myBind = function (context, ...boundArgs) {
  const fn = this;                               // original function

  function bound(...newArgs) {
    const isNew = this instanceof bound;         // true when called with `new`
    return fn.apply(
      isNew ? this : context,                    // `new` keeps its own this
      [...boundArgs, ...newArgs]                 // pre-filled + later args
    );
  }

  bound.prototype = Object.create(fn.prototype); // so instances inherit from original
  return bound;                                  // return the new function
};

// ============================================
// TEST CASES
// ============================================

function greet(greeting, punct) {
  return `${greeting} ${this.name}${punct}`;     // uses this.name
}

const hi = greet.myBind({ name: 'Aditya' }, 'Hello'); // bind this + 1st arg
console.log(hi('!'));                            // Expected: Hello Aditya!

const unbound = { name: 'Lost', hi };            // try to override this
console.log(unbound.hi('?'));                    // Expected: Hello Aditya?

function Person(name) { this.name = name; }      // constructor
const BoundPerson = Person.myBind({ ignored: true });
const p = new BoundPerson('Ravi');               // new ignores bound context
console.log(p.name, p instanceof Person);        // Expected: Ravi true
```

---

## 🔍 Why This Works (3 lines max)
The closure keeps `fn`, `context` and `boundArgs` alive. Arrow-free `bound` lets us detect `new` via `instanceof`, matching native behaviour.
हिंदी: Closure में original function और context सुरक्षित रहते हैं, और `new` होने पर context को ignore किया जाता है।

---

## ⚡ Alternative Solution
```javascript
// Simple version (no `new` support) using an arrow function
Function.prototype.myBind2 = function (context, ...args) {
  return (...rest) => this.apply(context, [...args, ...rest]); // arrow keeps outer `this` (the fn)
};
console.log(Math.max.myBind2(null, 3)(9, 1)); // Expected: 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to merge later arguments
return function () { return fn.apply(context, boundArgs); };

// ✅ Correct: combine bound args with new args
return function (...newArgs) { return fn.apply(context, [...boundArgs, ...newArgs]); };
```

---

## 🎯 Interview Tip (1 line)
Mention partial application (pre-filled args) and that `new` overrides bound `this` — it shows depth.

---

## 🔗 Related Questions
→ Q107 (call) | Q108 (apply) | Q088 (partial application) | Q110 (new keyword)
