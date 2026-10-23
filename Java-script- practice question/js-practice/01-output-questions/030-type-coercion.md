---

# Q030. Type Coercion Output (Tricky)
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following expressions output? These are classic JS type coercion traps asked in interviews.

```javascript
console.log(1 + '2');
console.log('3' - 1);
console.log(true + true);
console.log([] + []);
console.log([] + {});
console.log({} + []);
console.log(+'');
console.log(+null);
console.log(+undefined);
console.log(+false);
```

---

## 💡 Quick Concept (2 lines only)
`+` is overloaded — numeric addition OR string concatenation (if either operand is a string). `-` is always numeric. JS converts types using ToPrimitive rules.
हिंदी: `+` string है तो concatenate करता है, number है तो add; `-` हमेशा numeric — JS automatic type convert करता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

console.log(1 + '2');      // '12'   — number + string = string concat
console.log('3' - 1);      // 2      — '-' is arithmetic: '3' → 3, then 3-1=2
console.log(true + true);  // 2      — true → 1, 1+1=2
console.log([] + []);      // ''     — [].toString()='', ''+''=''
console.log([] + {});      // '[object Object]'  — {}→'[object Object]'
console.log({} + []);      // 0      — {} as statement (empty block)! +[] = +''/'' = 0
                            // BUT: ({}) + [] = '[object Object]' (if {} is expression)
console.log(+'');           // 0      — unary + converts '' to 0
console.log(+null);         // 0      — null → 0
console.log(+undefined);    // NaN    — undefined → NaN
console.log(+false);        // 0      — false → 0, true → 1

// More tricky:
console.log(null + 1);     // 1      — null → 0
console.log(undefined + 1);// NaN    — undefined → NaN
console.log('' + 0);       // '0'    — '' is string, so concat
console.log(0 + '');       // '0'    — '' is string, so concat
console.log(1 - '2');      // -1     — '-' is arithmetic: '2' → 2
console.log('5' * '3');    // 15     — '*' is arithmetic: both convert to number
console.log(true + false); // 1      — true→1, false→0
```

---

## 🔍 Why This Works (3 lines max)
`+` converts to primitive: if either side is a string, do string concat; otherwise numeric add. `-`, `*`, `/` are always numeric — they coerce both operands to numbers. `[]` converts to `''`, `{}` converts to `'[object Object]'`.
हिंदी: `+` में string होने पर concatenate होता है; arithmetic operators हमेशा numeric convert करते हैं।

---

## ⚡ Alternative Solution
```javascript
// Coercion cheatsheet:
// String conversion:
String(null)      // 'null'
String(undefined) // 'undefined'
String(true)      // 'true'
String(false)     // 'false'
String([])        // ''
String([1,2])     // '1,2'
String({})        // '[object Object]'

// Number conversion:
Number('')        // 0
Number(' ')       // 0
Number('3')       // 3
Number('3a')      // NaN
Number(null)      // 0
Number(undefined) // NaN
Number(true)      // 1
Number(false)     // 0
Number([])        // 0  ([] → '' → 0)
Number(['5'])     // 5  (['5'] → '5' → 5)
Number({})        // NaN

// Boolean conversion (falsy values):
Boolean(0)        // false
Boolean('')       // false
Boolean(null)     // false
Boolean(undefined)// false
Boolean(NaN)      // false
Boolean(false)    // false
// Everything else is truthy: Boolean([]), Boolean({}) = true!
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: {} + [] is '[object Object]' (actually 0)
// When {} is at START of statement, it's a BLOCK, not an object!
{} + []  // → +[] → +''/'' → 0 (in console)
// BUT
({}) + []  // → '[object Object]' (as expression)

// ❌ Wrong: thinking [] is falsy
if ([]) console.log('truthy');  // prints 'truthy'! [] is truthy!
if ([] == false) console.log('coerces to false'); // also prints! ([] → '' → 0 == false → 0)
// Empty array is truthy BUT loosely equals false — this is the weird part

// ❌ Wrong: checking value with ==
'0' == false   // true (both become 0)
'0' === false  // false (different types)
0 == ''        // true (both become 0)
0 === ''       // false (different types)
```

---

## 🎯 Interview Tip (1 line)
Say: "String wins in `+`; `-`/`*`/`/` force numbers; `null → 0`; `undefined → NaN`; `[] → ''`; `{} → '[object Object]'` — use `===` to avoid all this."

---

## 🔗 Related Questions
→ Q027 (== vs ===) | Q028 (null == undefined) | Q029 (NaN comparison) | Q031 (string+number) | Q033 ([] + [])
