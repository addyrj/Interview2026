# 07. Type Conversion + Type Coercion
# हिंदी में: Type Conversion (Explicit) और Type Coercion (Implicit)

---

## 🔵 Simple Definition (English)
**Type Conversion** (explicit): You manually convert a type — `Number("5")`, `String(42)`, `Boolean(0)`.
**Type Coercion** (implicit): JavaScript automatically converts types when operators force it — `"5" + 3 → "53"`, `"5" - 3 → 2`.

## 🔵 सरल परिभाषा (Hindi)
**Type Conversion** (explicit): आप खुद type बदलते हो — `Number("5")`, `String(42)`.
**Type Coercion** (implicit): JavaScript automatically types बदल देता है operators के हिसाब से — `"5" + 3 → "53"`, `"5" - 3 → 2`.

---

## 🔴 Problem it Solves
JavaScript's automatic coercion is **infamous for surprises**:
```javascript
"5" + 3    // "53" — + treats string first
"5" - 3    // 2    — - forces numbers
[] + {}    // "[object Object]" — bizarre!
[] + []    // "" — also bizarre!
false == 0 // true — loose equality + coercion
```
Understanding this prevents bugs and helps answer interview questions.

## 🔴 यह क्यों बना? (Hindi)
Implicit coercion JavaScript की design choice थी — flexibility के लिए। पर यह बहुत confusing bugs का source भी है। इसे समझना ज़रूरी है वरना `"5" + 3 = "53"` जैसे surprises आते हैं।

---

## 🟢 How it Works — Step by Step

### Explicit Conversion Rules
```
To Number:
  Number("5")      → 5
  Number("")        → 0
  Number("  3  ")   → 3    (trims whitespace)
  Number("abc")     → NaN
  Number(true)      → 1
  Number(false)     → 0
  Number(null)      → 0
  Number(undefined) → NaN
  Number([])        → 0
  Number([5])       → 5
  Number([1,2])     → NaN

To String:
  String(42)        → "42"
  String(true)      → "true"
  String(null)      → "null"
  String(undefined) → "undefined"
  String([1,2,3])   → "1,2,3"

To Boolean:
  Boolean(0)        → false   ← falsy
  Boolean("")       → false   ← falsy
  Boolean(null)     → false   ← falsy
  Boolean(undefined)→ false   ← falsy
  Boolean(NaN)      → false   ← falsy
  Boolean("0")      → true    ← non-empty string!
  Boolean([])       → true    ← empty array!
  Boolean({})       → true    ← empty object!
```

### Implicit Coercion Rules (+ operator is the trickiest)
```
+ with strings → concatenation (string wins)
  1 + "2"   → "12"
  "3" + 4   → "34"
  1 + 2 + "3" → "33" (left to right: 1+2=3, then 3+"3"="33")
  "1" + 2 + 3 → "123" (left to right: "1"+2="12", "12"+3="123")

Other math operators → numeric coercion
  "5" - 2   → 3
  "5" * 2   → 10
  "5" / 2   → 2.5
  "5" % 2   → 1

Comparison operators
  "5" > 3   → true  (string "5" coerced to 5)
  "05" == 5 → true  (loose: coercion happens)
  "05" === 5→ false (strict: no coercion)
```

## 🟢 कैसे काम करता है? (Hindi)
- `+` operator: अगर कोई एक string है तो string concatenation। `1 + "2" = "12"`
- `-`, `*`, `/`, `%`: हमेशा number बनाने की कोशिश। `"5" - 2 = 3`
- `==`: type coercion करके compare करता है — avoid करो
- `===`: कोई coercion नहीं — इसे use करो

---

## 🟡 Real World Example
**User Input from Form (always string!):**
```javascript
// Form input हमेशा string आती है
const ageInput = document.getElementById("age").value; // "25" (string)
const ageNum = Number(ageInput); // explicit: convert to number

// Bug without conversion:
const tax = ageInput * 0.18; // "25" * 0.18 = 4.5 (- coerces, works!)
const doubled = ageInput + ageInput; // "25" + "25" = "2525"! (+ concatenates)

// Always explicit convert:
const age = Number(ageInput);
const doubled2 = age + age; // 50 ✅
```

## 🟡 Real Example Hindi mein
Form से आने वाली हर value string होती है। `age = "25"` करने पर `age * 2 = 50` (number coerce होता है) पर `age + age = "2525"` (string concat)। इसीलिए form inputs को `Number()` से explicit convert करो।

---

## 💻 Code Example — Basic
```javascript
// ── EXPLICIT CONVERSION ───────────────

// String → Number
console.log(Number("42"));       // 42
console.log(Number("3.14"));     // 3.14
console.log(Number(""));          // 0
console.log(Number("abc"));       // NaN
console.log(parseInt("42px"));    // 42 (stops at non-numeric)
console.log(parseFloat("3.14em")); // 3.14

// Number → String
console.log(String(42));          // "42"
console.log((42).toString());     // "42"
console.log((255).toString(16));  // "ff" (hexadecimal)
console.log((42).toString(2));    // "101010" (binary)

// Anything → Boolean
console.log(Boolean(1));          // true
console.log(Boolean(0));          // false
console.log(Boolean("hello"));    // true
console.log(Boolean(""));         // false
console.log(Boolean(null));       // false
console.log(Boolean({}));         // true (empty object is truthy!)
console.log(Boolean([]));         // true (empty array is truthy!)
console.log(!!"hello");           // true (!! = double negation = toBoolean)
console.log(!!0);                 // false

// ── IMPLICIT COERCION ────────────────

// + operator (string wins)
console.log(1 + "2");             // "12"
console.log("3" + 4 + 5);        // "345" (left to right: "34" then "345")
console.log(3 + 4 + "5");        // "75"  (3+4=7, then 7+"5"="75")

// -, *, / (force number)
console.log("10" - 5);           // 5
console.log("10" * 2);           // 20
console.log("10" / 4);           // 2.5
console.log("10" - "3");         // 7

// Unary + (quick string to number)
console.log(+"5");                // 5  (number)
console.log(+true);               // 1
console.log(+false);              // 0
console.log(+null);               // 0
console.log(+undefined);          // NaN
console.log(+"");                 // 0
```

## 💻 Code Example — Advanced
```javascript
// ── WILD TYPE COERCION EXAMPLES ──────

// [] and {} weirdness
console.log([] + []);     // "" — arrays to string ("" + "")
console.log([] + {});     // "[object Object]" — [] → "", {} → "[object Object]"
console.log({} + []);     // 0 (in some contexts) or "[object Object]" — depends on context!
// When {} is at start of statement: parsed as empty block, not object literal!

// Weird equality
console.log(false == 0);    // true — false coerces to 0
console.log(false == "");   // true — both coerce to 0
console.log(false == "0");  // false! ("0" coerces to 0, false to 0... but "0" is truthy first)
console.log(null == 0);     // false — null only == null or undefined
console.log(null == undefined); // true — special case
console.log(NaN == NaN);    // false — NaN is never equal to anything

// Comparison
console.log("10" > 9);     // true — "10" coerced to 10
console.log("10" > "9");   // false! string comparison: "1" < "9" (char codes!)
// This is why sorting numbers as strings gives wrong results

// ── ABSTRACT EQUALITY (==) ALGORITHM ──
// Steps when types differ:
// 1. null == undefined → true (special rule)
// 2. number == string → convert string to number
// 3. boolean == anything → convert boolean to number first
// 4. object == primitive → convert object (valueOf/toString)

// Why 0 == "" is true:
// "" is string, 0 is number → convert "" to number → 0 → 0 == 0 → true

// ── FORM VALIDATION REAL EXAMPLE ──────
function validateAge(input) {
  // input is always string from form
  const age = Number(input);
  
  if (isNaN(age)) {
    return { valid: false, error: "Age must be a number" };
  }
  
  if (age < 18) {
    return { valid: false, error: "Must be 18 or older" };
  }
  
  if (!Number.isInteger(age)) {
    return { valid: false, error: "Age must be a whole number" };
  }
  
  return { valid: true, age };
}

console.log(validateAge("25"));    // { valid: true, age: 25 }
console.log(validateAge("17"));    // { valid: false, error: "Must be 18 or older" }
console.log(validateAge("abc"));   // { valid: false, error: "Age must be a number" }
console.log(validateAge("25.5"));  // { valid: false, error: "Age must be a whole number" }

// ── TEMPLATE LITERAL COERCION ──────────
const price = 299;
const message = `Price: ₹${price}`; // number to string automatically
console.log(message); // "Price: ₹299"

const obj = { toString() { return "Custom Object"; } };
console.log(`${obj}`); // "Custom Object" — calls obj.toString()
```

---

## 🟠 React/Next.js Connection
```jsx
// Form data always comes as strings
function OrderForm() {
  const handleSubmit = (e) => {
    e.preventDefault();
    const form = new FormData(e.target);

    // Always explicit convert — never trust implicit coercion
    const quantity = Number(form.get("quantity"));  // string → number
    const price = parseFloat(form.get("price"));    // string → float
    const agreed = form.get("agreed") === "true";   // string → boolean

    if (isNaN(quantity) || quantity < 1) {
      alert("Invalid quantity");
      return;
    }

    const total = quantity * price; // safe: both are numbers
    console.log(`Order: ${quantity} items @ ₹${price} = ₹${total}`);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="quantity" type="number" />
      <input name="price" type="number" step="0.01" />
      <button type="submit">Order</button>
    </form>
  );
}

// URL/query params (also strings!)
// Next.js
import { useSearchParams } from "next/navigation";

function ProductList() {
  const params = useSearchParams();
  const page = Number(params.get("page")) || 1; // string → number, default 1
  const limit = Number(params.get("limit")) || 10;
  // ...
}

// API response — validate types before using
app.post("/order", (req, res) => {
  const amount = Number(req.body.amount); // explicit, always
  if (isNaN(amount) || amount <= 0) {
    return res.status(400).json({ error: "Invalid amount" });
  }
  // safe to use amount now
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Relying on `+` for number addition with user input
```javascript
// WRONG:
const a = prompt("Enter number:"); // "5" (string)
const b = prompt("Enter number:"); // "3" (string)
const sum = a + b; // "53"! (string concatenation)

// CORRECT:
const sum = Number(a) + Number(b); // 8 ✅
```

❌ **Mistake 2:** Using `==` instead of `===`
```javascript
// WRONG (unexpected):
if (userInput == false) { /* runs for "", 0, null, false, undefined */ }

// CORRECT (predictable):
if (userInput === false) { /* only for literal false */ }
if (!userInput) { /* for all falsy values explicitly */ }
```

❌ **Mistake 3:** Sorting numbers as strings
```javascript
// WRONG:
const nums = [10, 9, 2, 100, 21];
nums.sort(); // ["10", "100", "2", "21", "9"] — string sort!

// CORRECT:
nums.sort((a, b) => a - b); // [2, 9, 10, 21, 100] ✅
// a - b: if negative, a comes first (ascending)
```

---

## 🧠 Tricky Interview Output Question
```javascript
console.log(1 + "2" + 3);
console.log(1 + 2 + "3");
console.log(+"3" + +"4");
console.log(true + true + "1");
console.log("5" - "2");
console.log(null + 1);
console.log(undefined + 1);
```
**Answer:**
```
"123"   ← 1+"2"="12", "12"+3="123"
"33"    ← 1+2=3, 3+"3"="33"
7       ← +"3"=3, +"4"=4, 3+4=7 (unary+ converts to number)
"21"    ← true+true=2, 2+"1"="21"
3       ← "-" forces number: 5-2=3
1       ← null=0, 0+1=1
NaN     ← undefined=NaN, NaN+1=NaN
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between type conversion and type coercion?**
A1: Type conversion (explicit) is when you manually convert a type using `Number()`, `String()`, `Boolean()`, `parseInt()`, etc. Type coercion (implicit) is when JavaScript automatically converts types when operators require it — like `+` with a string triggering string concatenation, or `-` forcing numeric conversion. Coercion is often surprising; explicit conversion is always preferred.

**Q2: When does the + operator do addition vs concatenation?**
A2: If either operand is a string, `+` concatenates. If both are numbers (or can be coerced to numbers), it adds. Order matters due to left-to-right evaluation: `1 + 2 + "3"` = `"33"` (3 + "3") but `"1" + 2 + 3` = `"123"` ("1"+"2"="12", "12"+"3"="123"). The unary `+` (like `+"5"`) converts a value to a number.

**Q3: What are all the falsy values in JavaScript?**
A3: `false`, `0`, `-0`, `0n` (BigInt zero), `""` (empty string), `null`, `undefined`, `NaN`. Everything else is truthy — including `"0"`, `[]`, `{}`, `function(){}`. The most common interview trick is that `"0"`, `[]`, and `{}` are truthy despite looking "empty".

**Q4: Why does `[] + {}` give `"[object Object]"`?**
A4: When the `+` operator is applied to non-primitives, they're converted to primitives. `[]` calls `.toString()` → `""`. `{}` calls `.toString()` → `"[object Object]"`. Then `"" + "[object Object]"` = `"[object Object]"`. If `{}` is at the start of a statement, the engine may parse it as an empty block, giving different results.

**Q5: Why should you always use === instead of ==?**
A5: `===` (strict equality) compares value AND type — no coercion. `==` (loose equality) applies type coercion before comparing, leading to many non-intuitive results like `0 == false` (true), `"" == false` (true), `null == undefined` (true), `null == 0` (false). The coercion rules are complex and error-prone; `===` is predictable.

---

## 🔷 Trade-offs / When to Use
✅ Explicit conversion always preferred:
- `Number()`, `String()`, `Boolean()` for user input
- `parseInt()` / `parseFloat()` for strings that might have units

✅ Implicit coercion acceptable when:
- Template literals: `${value}` automatically to string — fine
- Boolean context: `if (value)` — using truthiness intentionally

❌ Avoid:
- `==` (use `===` always)
- Relying on `+` for numbers when either value might be a string
- Sorting without a comparator function

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type Conversion | Explicit/manual type change | Manual type बदलना |
| Type Coercion | Implicit/automatic type change | Automatic type बदलना |
| parseInt | String to integer | String से integer |
| parseFloat | String to decimal number | String से decimal |
| Falsy | Values that become false | false बनने वाली values |
| Truthy | Values that become true | true बनने वाली values |
| Unary + | `+val` — convert to number | Number में बदलने का shortcut |
| NaN | Not a Number | Invalid number result |

---

## ⚡ 3-Line Summary
**English:**
1. Explicit conversion (`Number()`, `String()`, `Boolean()`) is predictable; use it especially for user input.
2. Implicit coercion happens automatically — `+` with a string always concatenates, `-/*//` always coerces to number.
3. Always use `===`, never `==` — coercion in `==` is complex and leads to bugs like `0 == false` being true.

**Hindi:**
1. Explicit conversion (`Number()`, `String()`) predictable है — user input के लिए हमेशा यही use करो।
2. Implicit coercion automatic — `+` string के साथ concat करता है, `-/*//` number बनाता है।
3. हमेशा `===` use करो — `==` में coercion होता है जो `0 == false` को true बना देता है।

---

## ➡️ Next Topic
**08. Operators** — Arithmetic, comparison, logical, assignment operators और unary operators की पूरी guide।
