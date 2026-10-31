---

# Q022. this in Event Listener
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print (Node.js EventEmitter, same rule as DOM)?

```javascript
const { EventEmitter } = require('events');
const em = new EventEmitter();
em.id = 'emitter';
em.on('x', function () { console.log(this === em, this.id); });
em.on('x', () => console.log(this === em));
em.emit('x');
```

---

## 💡 Quick Concept (2 lines only)
A regular-function listener gets `this` = the object emitting the event; an arrow listener keeps the outer `this`.
हिंदी: Regular function listener में this वही object होता है जिस पर event आया; arrow में बाहर वाला this रहता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: emit calls each listener with this = emitter
// Step 2: regular function uses that this -> true, 'emitter'
// Step 3: arrow ignores it and uses module-level this -> false

const { EventEmitter } = require('events');       // import emitter class
const em = new EventEmitter();                     // create emitter
em.id = 'emitter';                                 // custom property
em.on('x', function () {
  console.log(this === em, this.id);               // this = em
});
em.on('x', () => console.log(this === em));        // this = module.exports
em.emit('x');                                      // fire event

// ============================================
// TEST CASES
// ============================================

// Output:
// true emitter
// false
//
// In the browser: button.addEventListener('click', function () {
//   console.log(this === event.currentTarget); // true
// });
```

---

## 🔍 Why This Works (3 lines max)
Event systems call listeners with `this` set to the target (DOM: `event.currentTarget`). Arrow functions cannot receive a different `this`, so they stay lexical.
हिंदी: DOM में regular listener का this वही element होता है; arrow function में यह नहीं बदलता।

---

## ⚡ Alternative Solution
```javascript
// Use the event/emitter explicitly instead of relying on this
const em = new (require('events'))();                 // standalone emitter
em.id = 'emitter';                                    // custom property
em.on('y', (payload) => console.log(payload, em.id)); // arrow + explicit reference
em.emit('y', 'data');                                 // Expected: data emitter
```

---

## ⚠️ Common Mistake
```javascript
// ❌ btn.addEventListener('click', () => this.classList.add('on'));  // this is not btn
// ✅ Use a regular function, or event.currentTarget inside the arrow
```

---

## 🎯 Interview Tip (1 line)
Say: "In listeners, this is the target for regular functions; prefer event.currentTarget with arrows."

---

## 🔗 Related Questions
→ Q019 (this arrow) | Q021 (this in setTimeout) | Q221 (event delegation) | Q310 (bubbling vs capturing)
