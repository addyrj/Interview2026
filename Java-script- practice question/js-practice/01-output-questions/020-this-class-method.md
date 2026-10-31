---

# Q020. this in Class Method
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
class Btn {
  constructor() { this.label = 'OK'; }
  click() { return this.label; }
}
const b = new Btn();
console.log(b.click());
const f = b.click;
try { console.log(f()); } catch (e) { console.log(e.name); }
```

---

## 💡 Quick Concept (2 lines only)
Class methods lose `this` when detached from the instance, and class bodies run in strict mode, so `this` becomes undefined.
हिंदी: Method को instance से अलग करने पर this खो जाता है, और class strict mode में होने से this undefined हो जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: b.click() -> this = b -> 'OK'
// Step 2: const f = b.click detaches the method
// Step 3: f() has no owner -> this undefined -> TypeError

class Btn {
  constructor() { this.label = 'OK'; }             // instance property
  click() { return this.label; }                   // depends on call site
}
const b = new Btn();                               // create instance
console.log(b.click());                            // called on b
const f = b.click;                                 // detached reference
try {
  console.log(f());                                // this is undefined
} catch (e) {
  console.log(e.name);                             // error type
}

// ============================================
// TEST CASES
// ============================================

const g = b.click.bind(b);                         // bind fixes this
console.log(g());                                  // Expected: OK

// Overall output:
// OK
// TypeError
// OK
```

---

## 🔍 Why This Works (3 lines max)
`this` is decided by how a function is called, not where it is defined. A bare call `f()` in strict mode gives `this = undefined`, so `this.label` throws.
हिंदी: this इस पर निर्भर है कि function कैसे call हुआ; अकेले f() call में this undefined होता है।

---

## ⚡ Alternative Solution
```javascript
// Class field arrow function: this is bound per instance
class Btn2 {
  label = 'OK';                                    // field
  click = () => this.label;                        // arrow keeps instance this
}
const { click } = new Btn2();                      // detach safely
console.log(click());                              // Expected: OK
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Passing b.click as a callback: setTimeout(b.click, 0)  // loses this
// ✅ setTimeout(() => b.click(), 0) or b.click.bind(b)
```

---

## 🎯 Interview Tip (1 line)
Say: "Fix lost this with bind in the constructor, a class-field arrow, or an arrow wrapper at the call site."

---

## 🔗 Related Questions
→ Q018 (this regular function) | Q019 (this arrow) | Q124 (fix this binding bug) | Q165 (this 5 examples)
