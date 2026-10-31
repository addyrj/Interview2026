---

# Q111. Implement Object.create
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `myCreate(proto, propsObject?)` that returns a new object whose prototype is `proto`, like `Object.create`.

```javascript
const animal = { speak() { return 'sound'; } };
const dog = myCreate(animal);
dog.speak(); // "sound"
```

---

## 💡 Quick Concept (2 lines only)
Make a temporary empty constructor, set its `prototype` to `proto`, and return `new` of it — the new object inherits from `proto`.
हिंदी: खाली constructor का prototype `proto` पर set करो और उससे नया object बना लो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: validate proto (object, function or null)
// Step 2: create empty function F and set F.prototype = proto
// Step 3: return new F(), then apply optional property descriptors

function myCreate(proto, props) {
  if (proto !== null && typeof proto !== 'object' && typeof proto !== 'function') {
    throw new TypeError('Object prototype may only be an Object or null'); // same as native
  }
  function F() {}                             // temporary empty constructor
  F.prototype = proto;                        // link prototype
  const obj = new F();                        // new object inherits from proto
  if (proto === null) Object.setPrototypeOf(obj, null); // new F() would fall back to Object.prototype
  if (props) Object.defineProperties(obj, props);       // optional descriptors
  return obj;                                 // done
}

// ============================================
// TEST CASES
// ============================================

const animal = { speak() { return `${this.name} makes a sound`; } }; // base object
const dog = myCreate(animal);                  // inherit from animal
dog.name = 'Bruno';                            // own property
console.log(dog.speak());                      // Expected: Bruno makes a sound
console.log(Object.getPrototypeOf(dog) === animal); // Expected: true
console.log(Object.keys(dog));                 // Expected: [ 'name' ]

const bare = myCreate(null);                   // no prototype at all
console.log(Object.getPrototypeOf(bare));      // Expected: null

const withProps = myCreate(animal, { age: { value: 3, enumerable: true } }); // descriptors
console.log(withProps.age);                    // Expected: 3
```

---

## 🔍 Why This Works (3 lines max)
`new F()` always links the new object to `F.prototype`, which we set to `proto`. The constructor does nothing, so only the link matters.
हिंदी: `new F()` हमेशा नए object को `F.prototype` से जोड़ता है, और हमने वही `proto` रखा है।

---

## ⚡ Alternative Solution
```javascript
// Modern one-liner with setPrototypeOf
function myCreate2(proto) {
  return Object.setPrototypeOf({}, proto);   // empty object, then link prototype
}
console.log(myCreate2({ hi: 1 }).hi);        // Expected: 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: copying properties — that is NOT inheritance, changes to proto won't show
const obj = { ...proto };

// ✅ Correct: link the prototype chain
const obj = Object.create(proto);
```

---

## 🎯 Interview Tip (1 line)
Explain that `Object.create(null)` gives a "pure dictionary" with no inherited keys like `toString`.

---

## 🔗 Related Questions
→ Q110 (new keyword) | Q024 (prototype chain output) | Q129 (fix prototype mutation) | Q162 (explain prototype)
