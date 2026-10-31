---

# Q118. Implement JSON.stringify
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `myStringify(value)` that converts a JS value to a JSON string (no indent/replacer needed). Follow native rules for `undefined`, functions, `NaN`, arrays and nested objects.

```javascript
myStringify({ a: 1, b: [true, null] }); // '{"a":1,"b":[true,null]}'
```

---

## 💡 Quick Concept (2 lines only)
Handle each type: primitives directly, arrays/objects recursively. `undefined`, functions and symbols are dropped in objects and become `null` in arrays.
हिंदी: हर type के हिसाब से string बनाओ — array और object के लिए recursion, और undefined/function को skip करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: handle primitives (string, number, boolean, null)
// Step 2: undefined / function / symbol -> undefined (skipped)
// Step 3: arrays and objects -> recurse and join with commas

function myStringify(value) {
  if (value === null) return 'null';                       // null stays null
  if (typeof value === 'string') return `"${value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`; // quote + escape
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : 'null'; // NaN/Infinity -> null
  if (typeof value === 'boolean') return String(value);    // true / false
  if (value === undefined || typeof value === 'function' || typeof value === 'symbol') {
    return undefined;                                      // not representable
  }
  if (typeof value.toJSON === 'function') return myStringify(value.toJSON()); // e.g. Date

  if (Array.isArray(value)) {
    const items = value.map(v => {
      const s = myStringify(v);                            // stringify each item
      return s === undefined ? 'null' : s;                 // unsupported -> null in arrays
    });
    return `[${items.join(',')}]`;                         // [a,b,c]
  }

  const pairs = [];                                        // "key":value pairs
  for (const key of Object.keys(value)) {                  // own enumerable keys only
    const s = myStringify(value[key]);                     // stringify the value
    if (s !== undefined) pairs.push(`"${key}":${s}`);      // skip unsupported values
  }
  return `{${pairs.join(',')}}`;                           // {k:v,k:v}
}

// ============================================
// TEST CASES
// ============================================

console.log(myStringify({ a: 1, b: [true, null] }));       // Expected: {"a":1,"b":[true,null]}
console.log(myStringify('hi "x"'));                        // Expected: "hi \"x\""
console.log(myStringify([undefined, () => 1, NaN]));       // Expected: [null,null,null]
console.log(myStringify({ a: undefined, b: () => 1, c: 2 })); // Expected: {"c":2}
console.log(myStringify(undefined));                       // Expected: undefined
console.log(myStringify({ d: new Date(0) }));              // Expected: {"d":"1970-01-01T00:00:00.000Z"}
console.log(myStringify({ a: [1, { b: 2 }] }) === JSON.stringify({ a: [1, { b: 2 }] })); // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
Recursion mirrors the nested shape of data, and each branch follows the JSON spec rules. `toJSON` support makes `Date` work like the native version.
हिंदी: Recursion data की nested बनावट को follow करता है और हर type के लिए JSON के नियम लगाता है।

---

## ⚡ Alternative Solution
```javascript
// Cycle-safe version: throw like native when object refers to itself
function stringifySafe(v, seen = new WeakSet()) {
  if (v && typeof v === 'object') {
    if (seen.has(v)) throw new TypeError('Converting circular structure to JSON'); // detect cycle
    seen.add(v);                                           // mark visited
  }
  return JSON.stringify(v);                                // delegate rest to native
}
const o = {}; o.self = o;
try { stringifySafe(o); } catch (e) { console.log(e.message); } // Expected: Converting circular structure to JSON
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting quotes around strings/keys, or printing undefined in arrays
`{${key}:${value}}`          // invalid JSON

// ✅ Correct: quote keys + strings, use null for unsupported array items
`"${key}":"${value}"`
```

---

## 🎯 Interview Tip (1 line)
List the rules: undefined/function skipped in objects, null in arrays, NaN -> null, circular -> TypeError.

---

## 🔗 Related Questions
→ Q119 (JSON.parse) | Q071 (deep clone) | Q078 (deep equal) | Q294 (shallow vs deep copy)
