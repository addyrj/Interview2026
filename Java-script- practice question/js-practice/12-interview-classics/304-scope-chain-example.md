---

# Q304. scope chain example
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain the scope chain with a nested-function example. Show variable lookup, shadowing, and prove that scope is lexical (decided where code is written, not where it is called).

---

## 💡 Quick Concept (2 lines only)
When a variable is not found in the current scope, JS looks outward one scope at a time (inner -> outer -> global). The chain is fixed by where functions are written.
हिंदी: Variable न मिले तो JS बाहर की scope में एक-एक करके खोजता है; chain वहीं से बनती है जहाँ function लिखा है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: inner function looks in its own scope first
// Step 2: then in the parent function's scope, then up to global
// Step 3: a closer variable with the same name shadows the outer one
// Step 4: scope is lexical — calling from elsewhere does not change the chain

const level = 'global';                    // global scope variable

function outer() {
  const level = 'outer';                   // shadows global `level` inside outer
  const outerOnly = 'outerOnly';           // exists only in outer (and its children)

  function inner() {
    const innerOnly = 'innerOnly';         // exists only in inner
    // lookup: innerOnly (own) -> outerOnly (parent) -> level (parent, shadowed) -> globalThis
    return [innerOnly, outerOnly, level];  // read from three different scopes
  }

  return inner();                          // run inner and return its result
}

function showLevel() { return level; }     // defined at global level -> sees global `level`

function caller() {
  const level = 'caller';                  // local variable in caller
  return showLevel();                      // called here, but scope is where showLevel was written
}

// ============================================
// TEST CASES
// ============================================

console.log(outer());                      // Expected: [ 'innerOnly', 'outerOnly', 'outer' ]
console.log(caller());                     // Expected: global  (lexical, NOT 'caller')
console.log(typeof outerOnly);             // Expected: undefined (not reachable from global)
console.log(typeof level);                 // Expected: string
console.log(showLevel());                  // Expected: global

// Block scope also forms a link in the chain
{
  const level = 'block';                   // shadows only inside this block
  console.log(level);                      // Expected: block
}
console.log(level);                        // Expected: global
```

---

## 🔍 Why This Works (3 lines max)
Every function remembers the scope it was created in. Lookup climbs that saved chain until the name is found, else `ReferenceError`. Parents can never see children's variables, only the reverse.
हिंदी: हर function अपनी बनने की scope याद रखता है; lookup ऊपर की तरफ़ जाता है, नीचे की तरफ़ कभी नहीं।

---

## ⚡ Alternative Solution
```javascript
// Closure view of the same idea: inner keeps access to outer variables after outer returns
function makeCounter() {
  let n = 0;                    // lives in makeCounter's scope
  return () => ++n;             // arrow keeps the scope chain alive
}
const next = makeCounter();     // makeCounter has finished
console.log(next(), next());    // 1 2  (n is still reachable via the chain)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking the caller's variables are visible (dynamic scope)
// function show() { return msg; }
// function run() { const msg = 'hi'; return show(); }
// run(); // ReferenceError: msg is not defined

// ✅ Correct: pass it as an argument or define show inside run
function run2() {
  const msg = 'hi';                   // variable in run2
  const show = () => msg;             // defined inside -> chain includes run2
  return show();                      // hi
}
console.log(run2()); // hi
```

---

## 🎯 Interview Tip (1 line)
Say: "JavaScript has lexical scoping — lookup walks outward through the scopes where functions were defined, which is also what makes closures work."

---

## 🔗 Related Questions
→ Q133 (fix scope bug) | Q161 (closure) | Q291 (var vs let vs const) | Q301 (closure real use case)
