---

# Q294. Shallow vs Deep Copy
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain shallow copy vs deep copy in JavaScript. Implement both. What methods create shallow copies? How do you deep copy an object?

---

## 💡 Quick Concept (2 lines only)
Shallow copy: top-level properties copied, nested objects still share reference. Deep copy: completely independent clone — no shared references at any level.
हिंदी: Shallow copy में nested objects का reference share होता है; deep copy में completely independent copy बनती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — Shallow vs Deep Copy
// ============================================

const original = {
  name: 'Arjun',
  address: { city: 'Mumbai', pin: '400001' },  // nested object
  hobbies: ['coding', 'chess']                 // nested array
};

// ─── SHALLOW COPY METHODS ──────────────────────────────────────

// Method 1: Object.assign()
const shallow1 = Object.assign({}, original);

// Method 2: Spread operator
const shallow2 = { ...original };

// Method 3: Array.from() / slice() (for arrays)
const arr = [1, [2, 3], [4, 5]];
const shallowArr = [...arr];          // or arr.slice()

// PROBLEM with shallow copy:
shallow1.name = 'Priya';        // ✅ doesn't affect original
shallow1.address.city = 'Delhi'; // ❌ AFFECTS original! (shared reference)

console.log(original.name);          // 'Arjun'  ← unaffected
console.log(original.address.city);  // 'Delhi'  ← CHANGED! (shallow copy problem)

// ─── DEEP COPY METHODS ─────────────────────────────────────────

// Method 1: JSON.parse(JSON.stringify()) — simple but has limitations
const deep1 = JSON.parse(JSON.stringify(original));
deep1.address.city = 'Pune';
console.log(original.address.city);  // 'Mumbai' ← unaffected ✅

// Method 2: structuredClone() — modern, recommended (Node 17+, modern browsers)
const deep2 = structuredClone(original);
deep2.address.city = 'Bangalore';
console.log(original.address.city);  // 'Mumbai' ← unaffected ✅

// ============================================
// TEST CASES
// ============================================

const user = {
  id: 1,
  profile: { name: 'Arjun', role: 'admin' },
  scores: [100, 200, 300]
};

// Shallow copy test:
const shallowUser = { ...user };
shallowUser.id = 99;                      // primitive — safe
shallowUser.profile.name = 'Priya';      // MUTATES original.profile.name!
shallowUser.scores.push(400);            // MUTATES original.scores!

console.log(user.id);               // 1     ← unaffected (primitive)
console.log(user.profile.name);     // 'Priya' ← MUTATED (reference shared)
console.log(user.scores);           // [100,200,300,400] ← MUTATED

// Deep copy test:
const deepUser = structuredClone(user);
deepUser.profile.name = 'Raj';
deepUser.scores.push(500);

console.log(user.profile.name);  // 'Priya' ← unaffected
console.log(user.scores);        // [100,200,300,400] ← unaffected
```

---

## 🔍 Why This Works (3 lines max)
Shallow copy creates a new object but nested objects still point to same memory. Deep copy recursively copies every level so no references are shared. `structuredClone` is the modern standard; JSON trick fails for functions/Date/undefined.
हिंदी: Shallow copy new object बनाता है पर nested references share होते हैं; deep copy हर level completely copy करता है।

---

## ⚡ Alternative Solution
```javascript
// Manual deep clone (handles more types):
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (obj instanceof Map) return new Map([...obj.entries()].map(([k, v]) => [k, deepClone(v)]));
  
  const cloned = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  return cloned;
}

// Comparison of deep copy methods:
// JSON.parse/stringify: simple, fast, but loses: functions, undefined, Date, Map, Set, Infinity, NaN
// structuredClone: handles Date, Map, Set, ArrayBuffer — but not functions
// lodash _.cloneDeep: handles everything, external dependency
// Manual recursive: full control, handles everything you code for
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: JSON.stringify with functions, Date, undefined
const obj = {
  name: 'Arjun',
  fn: () => 'hello',           // functions are DROPPED
  date: new Date(),             // becomes string, not Date object
  undef: undefined,             // undefined is DROPPED
  num: NaN                      // becomes null
};

const cloned = JSON.parse(JSON.stringify(obj));
// cloned = { name: 'Arjun', date: '2024-...', num: null }
// fn and undef are GONE

// ✅ Use structuredClone for objects with Date/Map/Set
// ✅ Use lodash _.cloneDeep for objects with functions

// ❌ Wrong: spreading nested objects to "deep clone"
const deep = { ...obj, address: { ...obj.address } };
// Only 2 levels deep — any deeper nesting is still shallow!
```

---

## 🎯 Interview Tip (1 line)
Say: "Spread/Object.assign = shallow (nested refs shared); use structuredClone() for deep copy; JSON trick loses functions/Date/undefined."

---

## 🔗 Related Questions
→ Q071 (deep clone object) | Q078 (deep equal) | Q128 (reference vs value bug) | Q260 (structuredClone)
