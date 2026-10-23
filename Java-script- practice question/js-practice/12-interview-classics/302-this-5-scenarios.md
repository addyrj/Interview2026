---

# Q302. `this` — 5 Scenarios
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Explain and demonstrate `this` in 5 different scenarios:
1. Global context
2. Method call
3. Plain function call
4. Arrow function
5. Constructor (`new`)

Also show `call`, `apply`, `bind`.

---

## 💡 Quick Concept (2 lines only)
`this` refers to the execution context — it's determined by HOW a function is called, not where it's written (except arrow functions which use lexical `this`).
हिंदी: `this` execution context है — कैसे function call हुआ उस पर depend करता है (arrow function में lexical है)।

---

## ✅ Answer / Solution

```javascript
// ============================================
// 5 THIS SCENARIOS
// ============================================

// SCENARIO 1: Global context
console.log(this);          // window (browser) / {} (Node.js module)
function globalFn() {
  console.log(this);        // window (non-strict) / undefined (strict mode)
}
globalFn();

// SCENARIO 2: Method call (object before the dot)
const person = {
  name: 'Arjun',
  greet() {
    console.log(this.name);  // this = person (obj before the dot)
  }
};
person.greet();   // 'Arjun' ✅

// DETACHED method — loses context:
const greet = person.greet;
greet();          // undefined (strict) / '' (non-strict) — no object!

// SCENARIO 3: Plain function call
function showThis() {
  console.log(this);
}
showThis();         // window (non-strict) / undefined (strict)

'use strict';
function strictFn() {
  console.log(this);  // undefined in strict mode
}
strictFn();

// SCENARIO 4: Arrow function (lexical this — inherits from outer scope)
const obj = {
  name: 'Priya',
  
  // Regular method — this = obj ✅
  greetRegular() {
    console.log(this.name);  // 'Priya'
  },
  
  // Arrow — this = outer scope (NOT obj!) ❌
  greetArrow: () => {
    console.log(this.name);  // undefined — arrow doesn't bind obj
  },
  
  // Arrow inside regular method — this = obj ✅
  greetDelayed() {
    setTimeout(() => {
      console.log(this.name);  // 'Priya' — arrow inherits this from greetDelayed
    }, 100);
  }
};

obj.greetRegular();  // 'Priya'
obj.greetArrow();    // undefined (arrow = lexical, no obj binding)
obj.greetDelayed();  // 'Priya' (arrow inherits from method's this)

// SCENARIO 5: Constructor with new
function Person(name) {
  this.name = name;  // this = new empty object
  // implicitly returns this
}

const user = new Person('Arjun');
console.log(user.name);  // 'Arjun'

class Animal {
  constructor(type) {
    this.type = type;   // this = new instance
  }
  speak() {
    console.log(`${this.type} speaks`);
  }
}
const cat = new Animal('Cat');
cat.speak();  // 'Cat speaks'

// ============================================
// call / apply / bind
// ============================================

function introduce(greeting, punctuation) {
  console.log(`${greeting}, I'm ${this.name}${punctuation}`);
}

const arjun = { name: 'Arjun' };
const priya = { name: 'Priya' };

introduce.call(arjun, 'Hello', '!');    // "Hello, I'm Arjun!"
introduce.apply(priya, ['Hi', '.']);    // "Hi, I'm Priya."
const greetArjun = introduce.bind(arjun, 'Hey');
greetArjun('?');  // "Hey, I'm Arjun?"

// ============================================
// TEST CASES
// ============================================

// Tricky: class method passed as callback
class Counter {
  constructor() { this.count = 0; }
  
  increment() { this.count++; console.log(this.count); }
  
  start() {
    setInterval(this.increment, 1000);         // ❌ loses this!
    setInterval(this.increment.bind(this), 1000); // ✅ bind fixes it
    setInterval(() => this.increment(), 1000);    // ✅ arrow fixes it
  }
}
```

---

## 🔍 Why This Works (3 lines max)
`this` is dynamic in regular functions — set at call time by 4 rules (global, method, new, explicit). Arrow functions have no own `this` — they look up `this` from the enclosing lexical scope at definition time. `bind/call/apply` explicitly set `this`.
हिंदी: Regular function में `this` runtime पर decide होती है; arrow function में lexical scope से आती है।

---

## ⚡ Alternative Solution
```javascript
// THIS PRIORITY ORDER (highest to lowest):
// 1. new keyword            → new obj
// 2. call/apply/bind        → explicit first arg
// 3. Method call (obj.fn()) → obj
// 4. Default                → undefined (strict) / window (non-strict)
// (Arrow always uses lexical — never follows these rules)

// Tricky: chained methods
const obj2 = {
  value: 42,
  getValue() { return this.value; },
  getDouble() { return this.getValue() * 2; }  // this.getValue() = method call — works!
};
console.log(obj2.getDouble());  // 84

// VERY TRICKY: returned method
function makeObj() {
  return {
    name: 'test',
    getName: function() { return this.name; }
  };
}
const o = makeObj();
console.log(o.getName());             // 'test'
const fn = o.getName;
console.log(fn());                    // undefined — detached!
console.log(fn.call(o));             // 'test' — explicitly bound
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: arrow function as object method
const btn = {
  label: 'Submit',
  click: () => {
    console.log(this.label);  // undefined! — arrow this = outer scope
  }
};
btn.click();  // undefined

// ✅ Correct: use regular function for methods
const btn2 = {
  label: 'Submit',
  click() {
    console.log(this.label);  // 'Submit' ✅
  }
};

// ❌ Wrong: setTimeout without binding
class Timer {
  start() {
    setTimeout(function() {
      this.tick();  // TypeError! — this = undefined in strict
    }, 1000);
  }
}

// ✅ Fixes:
// Arrow: setTimeout(() => this.tick(), 1000)
// Bind:  setTimeout(this.tick.bind(this), 1000)
```

---

## 🎯 Interview Tip (1 line)
Say: "new > call/apply/bind > method call > default; arrow always lexical — never use arrow as object methods, do use arrow in callbacks inside methods."

---

## 🔗 Related Questions
→ Q018 (this in regular function) | Q019 (this in arrow) | Q023 (call/apply/bind) | Q165 (this deep dive)
