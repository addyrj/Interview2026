# 198. Tricky Coercion Questions
# हिंदी में: Tricky Coercion Questions — Type Conversion, == vs ===, null/undefined/NaN और Strict Parsing

---

## 🔵 Simple Definition (English)
Coercion means JavaScript converts a value from one type to another automatically, for example a string to a number, when an operator needs a different type. The `+` operator joins strings if either side is a string, while `-` always uses numbers. Loose equality `==` converts both sides before it compares. Interviews use these rules because small differences, such as `[] == ![]`, produce answers that look wrong at first.

## 🔵 सरल परिभाषा (Hindi)
Coercion का मतलब है कि जब कोई operator दूसरे type की value माँगता है, तो JavaScript value को अपने आप एक type से दूसरे type में बदल देता है, जैसे string से number। `+` operator अगर किसी एक side पर string हो तो दोनों को जोड़ता है, जबकि `-` हमेशा numbers इस्तेमाल करता है। Loose equality `==` तुलना से पहले दोनों sides को बदलती है। Interview में ये नियम इसलिए आते हैं क्योंकि छोटे फ़र्क, जैसे `[] == ![]`, पहली नज़र में गलत लगने वाले नतीजे देते हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Predict the output of mixed-type expressions such as `"5" + 2`, `[] + {}`, `null >= 0`, and `NaN === NaN`. Explain the rules behind each answer. Then write a strict parser that does not accept values that coercion would silently "fix".

Coercion helps in small scripts, but it causes bugs in real systems. A query value `?page=2` arrives as the string `"2"`, so `page + 1` becomes `"21"`. An empty input becomes `0`, and `"0"` is truthy. Real code needs explicit conversion and validation.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** Mixed-type expressions के output बताओ, जैसे `"5" + 2`, `[] + {}`, `null >= 0`, और `NaN === NaN`। हर जवाब के पीछे का नियम समझाओ। फिर एक strict parser लिखो जो उन values को न माने जिन्हें coercion चुपचाप "ठीक" कर देता।

Coercion छोटे scripts में मदद करता है, पर असली सिस्टम में bugs लाता है। Query `?page=2` की value string `"2"` बनकर आती है, तो `page + 1` `"21"` बन जाता है। खाली input `0` बन जाता है, और `"0"` truthy होता है। असली code में साफ़ conversion और validation चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Arithmetic `-`, `*`, `/` convert both sides to numbers.
Step 2 → `+` checks the types after conversion to primitives. If either side is a string, it concatenates.
Step 3 → Objects and arrays become primitives first, using `valueOf` and then `toString`, and `[]` becomes `""`.
Step 4 → `==` converts both sides when the types differ. `null` and `undefined` are equal only to each other.
Step 5 → `<`, `>`, `>=` convert values to numbers, except when both sides are strings, which compare alphabetically.
Step 6 → `NaN` is not equal to anything, including itself. Use `Number.isNaN` or `Object.is` to check it.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Arithmetic `-`, `*`, `/` दोनों sides को numbers में बदलते हैं।
Step 2 → `+` primitives में बदलने के बाद types देखता है। किसी एक side पर string हो तो जोड़ता है।
Step 3 → Objects और arrays पहले primitives बनते हैं, `valueOf` और फिर `toString` से, और `[]` बनता है `""`।
Step 4 → `==` जब types अलग हों तो दोनों को बदलता है। `null` और `undefined` सिर्फ एक-दूसरे के बराबर हैं।
Step 5 → `<`, `>`, `>=` values को numbers में बदलते हैं, सिवाय तब जब दोनों strings हों, तो वे alphabetically तुलना करते हैं।
Step 6 → `NaN` किसी के बराबर नहीं, खुद के भी नहीं। जाँचने के लिए `Number.isNaN` या `Object.is` इस्तेमाल करो।

---

## 🟡 Real World Example
Swiggy's filter bar sends `?minRating=4` in the URL. The server receives the string `"4"`. If the code compares `"4" > 3` it works, but `"10" > "9"` is false because strings compare alphabetically. A Razorpay API accepts `amount=500`, and a bug that treats `"500abc"` as valid would charge the wrong amount. A strict parser rejects it.

Scenario: A Flipkart sale page reads `?page=2`. The developer writes `page + 1` to get the next page and gets `"21"`. The fix is `Number(page) + 1`, after validating the value. Without validation, `?page=abc` gives `NaN` and an empty page.

## 🟡 Real Example Hindi mein
Swiggy के filter bar में URL में `?minRating=4` जाता है। Server को string `"4"` मिलती है। `"4" > 3` काम करता है, पर `"10" > "9"` false है, क्योंकि strings alphabetically तुलना होती हैं। Razorpay API `amount=500` लेता है, और अगर `"500abc"` को valid माना गया तो गलत रकम कटेगी। Strict parser उसे reject करता है।

उदाहरण: Flipkart की sale page `?page=2` पढ़ती है। Developer अगला page पाने के लिए `page + 1` लिखता है और `"21"` मिलता है। ठीक करने के लिए validation के बाद `Number(page) + 1` करो। Validation के बिना `?page=abc` से `NaN` और खाली page आती है।

---

## 💻 Code Example — Basic
```javascript
// Run with: node file.js
const { inspect } = require("util");               // inspect shows strings with quotes, NaN, and so on
const show = (expr, value) => console.log(expr.padEnd(18), "=>", inspect(value)); // print expression and result

// 1. Arithmetic and plus: - always converts, + joins strings if one side is a string
show('"5" - 2', "5" - 2);                          // Expected output: 3 (both become numbers)
show('"5" + 2', "5" + 2);                          // Expected output: '52' (string concatenation)
show('"5" * "2"', "5" * "2");                      // Expected output: 10
show("true + 1", true + 1);                        // Expected output: 2 (true becomes 1)
show("null + 1", null + 1);                        // Expected output: 1 (null becomes 0)
show("undefined + 1", undefined + 1);              // Expected output: NaN (undefined becomes NaN)

// 2. Empty values and loose equality
show('"" == 0', "" == 0);                          // Expected output: true (both become 0)
show('"0" == false', "0" == false);                // Expected output: true (both become 0)
show('"" == false', "" == false);                  // Expected output: true (both become 0)

// 3. Objects and arrays become strings first
show("[] + []", [] + []);                          // Expected output: '' (two empty strings)
show("[] + {}", [] + {});                          // Expected output: '[object Object]'
show("({}) + []", ({}) + []);                      // Expected output: '[object Object]' (parentheses make it an expression)
show("[1, 2] + [3]", [1, 2] + [3]);                // Expected output: '1,23' ("1,2" + "3")
show("+[]", +[]);                                  // Expected output: 0 ([] -> "" -> 0)
show("+{}", +{});                                  // Expected output: NaN ({} -> "[object Object]" -> NaN)
show("[] == ![]", [] == ![]);                      // Expected output: true (see the tricky question)
show("[0] == false", [0] == false);                // Expected output: true ("0" == false)

// 4. null, undefined, NaN
show("null == 0", null == 0);                      // Expected output: false (null equals only null and undefined)
show("null >= 0", null >= 0);                      // Expected output: true (relational compare converts null to 0)
show("null > 0", null > 0);                        // Expected output: false
show("undefined == null", undefined == null);      // Expected output: true
show("NaN == NaN", NaN == NaN);                    // Expected output: false
show("Object.is(NaN, NaN)", Object.is(NaN, NaN));  // Expected output: true
show("typeof null", typeof null);                  // Expected output: 'object' (a long-standing JavaScript bug)

// 5. Relational comparison: strings compare alphabetically, mixed types compare as numbers
show('"10" < "9"', "10" < "9");                    // Expected output: true (string comparison: "1" < "9")
show('"10" < 9', "10" < 9);                        // Expected output: false (number comparison: 10 < 9)
```

## 💻 Code Example — Advanced
```javascript
// toPositiveInt: strict parsing for query params or form input; coercion would be too loose here
function toPositiveInt(value) {
  if (typeof value !== "string" && typeof value !== "number") return null; // reject arrays, objects, null, undefined
  const text = String(value).trim();                // "  12 " becomes "12"; trim removes surrounding spaces
  if (!/^\d+$/.test(text)) return null;             // digits only: rejects "1e3", "12abc", "3.5", "-1", ""
  const n = Number(text);                           // safe to convert now, because the text is only digits
  return Number.isSafeInteger(n) && n > 0 ? n : null; // must be a safe integer greater than zero
}

// Test the parser on tricky inputs
const inputs = ["12", " 7 ", "0", "12abc", "", "3.5", "1e3", null, undefined, 42, [5], "-1"];
console.log(JSON.stringify(inputs.map((v) => toPositiveInt(v)))); // Expected output: [12,7,null,null,null,null,null,null,null,42,null,null]

// Money: Symbol.toPrimitive chooses the answer for each hint that JavaScript asks for
class Money {
  constructor(paise) { this.paise = paise; }        // store integer paise to avoid floating-point errors
  [Symbol.toPrimitive](hint) {                      // JavaScript calls this when it needs a primitive
    if (hint === "string") return `₹${(this.paise / 100).toFixed(2)}`; // template literals and String() ask for "string"
    return this.paise / 100;                        // "number" (>, *) and "default" (+) use rupees as a number
  }
}
const price = new Money(1250);                      // Rs 12.50
console.log(`${price}`);                            // Expected output: ₹12.50 (hint "string")
console.log(price + 1);                             // Expected output: 13.5 (hint "default")
console.log(price > 10, price * 2);                 // Expected output: true 25 (hint "number")

// Time:  O(n) for the regex test on a string of length n
// Space: O(n) for the trimmed copy of the input
```

### Edge Cases
```javascript
// Edge 1: Number() and parseInt() treat text differently
console.log(Number(""), Number(" "), Number("12px"), parseInt("12px", 10)); // Expected output: 0 0 NaN 12

// Edge 2: Boolean coercion: only these values are falsy: false, 0, -0, 0n, "", null, undefined, NaN
console.log(Boolean(""), Boolean("0"), Boolean([]), Boolean(NaN)); // Expected output: false true true false

// Edge 3: template literals call toString on arrays, which joins them with commas
console.log(`${[1, [2, 3]]}`);                     // Expected output: 1,2,3
```

---

## 🟠 Express.js Integration
Express gives every query value as a string, or as an array if the key repeats (`?page=1&page=2`). The route below uses the strict parser instead of `Number` or `+`, so `?page=abc`, `?page=1e3`, and repeated keys all fall back to the default.

```javascript
// Express.js: GET /api/products?page=2&limit=10 parses query strings strictly
const express = require("express");               // web framework (install with: npm i express)
const app = express();                            // create the app

// Strict parser from the advanced section: digits only, safe integer, greater than zero
function toPositiveInt(value) {
  if (typeof value !== "string" && typeof value !== "number") return null; // arrays and objects are rejected
  const text = String(value).trim();              // remove surrounding spaces
  if (!/^\d+$/.test(text)) return null;           // digits only
  const n = Number(text);                         // convert the digits to a number
  return Number.isSafeInteger(n) && n > 0 ? n : null; // safe and positive, or null
}

app.get("/api/products", (req, res) => {          // handler for the product list
  const page = toPositiveInt(req.query.page) ?? 1;   // invalid or missing page becomes 1
  const limit = toPositiveInt(req.query.limit) ?? 20; // invalid or missing limit becomes 20
  const offset = (page - 1) * limit;              // now safe to do arithmetic on the numbers
  // Wrong: req.query.page + 1 would give "21" for page "2"
  res.json({ page, limit, offset });              // send the parsed values back for checking
});

app.listen(3000, () => console.log("Products API on 3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Treating the string `"0"` as false in an `if` check
✅ Correct: any non-empty string is truthy, including `"0"`. Convert to a number first, then compare.

```javascript
// Wrong: "0" is a non-empty string, so it is truthy
const limit = "0";                                  // a query value
if (limit) console.log("apply limit");              // Expected output: apply limit (wrong!)

// Right: convert to a number and compare
if (Number(limit) > 0) console.log("apply limit");  // no output here
else console.log("no limit");                        // Expected output: no limit
```

❌ **Mistake 2:** Adding a number to a query string value
✅ Correct: `+` concatenates when one side is a string. Convert with `Number` or a strict parser first.

```javascript
// Wrong: the query value is a string, so + joins the text
const page = "2";                                   // req.query.page is always a string
console.log(page + 1);                              // Expected output: 21

// Right: convert to a number before doing arithmetic
console.log(Number(page) + 1);                      // Expected output: 3
```

---

## 🧠 Tricky Interview Question
```javascript
console.log([] == ![]);                             // ?
console.log(null == 0, null >= 0, null > 0);        // ?
console.log([] + null + 1);                         // ?
console.log(typeof NaN, NaN === NaN, Object.is(NaN, NaN)); // ?
```
Answer:
```
true
false true false
null1
number false true
```
`![]` is `false`, because an array is an object and objects are truthy, so `!` gives `false`. Then `[] == false` converts `false` to `0` and `[]` to `""`, which becomes `0`, so `0 == 0` is `true`. For `null`, loose equality never converts it to a number, so `null == 0` is false, but `>=` converts it to `0`, so `null >= 0` is true. `[] + null` is `"" + null`, which is `"null"`, and then `"null" + 1` is `"null1"`. `NaN` never equals itself, but `Object.is` compares it as the same value.

---

## ⚫ Interview Questions + Answers

**Q1: Why is `"5" - 2` equal to 3, but `"5" + 2` equal to `"52"`?**
A1: `-` always converts operands to numbers. `+` concatenates when either operand is a string after conversion to a primitive, so the number 2 becomes the text "2".

**Q2: What is the difference between `==` and `===`?**
A2: `===` compares type and value with no conversion. `==` converts the operands first, following a set of rules. Use `===` unless you need the specific `null`/`undefined` check `x == null`.

**Q3: Why is `null == 0` false but `null >= 0` true?**
A3: The `==` rules say `null` is equal only to `undefined` and `null`, so no conversion happens. Relational operators convert `null` to `0`, so `0 >= 0` is true and `0 > 0` is false.

**Q4: How do you check whether a value is NaN?**
A4: `Number.isNaN(value)` is the safe choice, because the global `isNaN` converts its argument first, so `isNaN("abc")` is true. `Object.is(value, NaN)` also works.

**Q5: How do you parse a number from user input strictly?**
A5: Check the type, trim the text, test it against a pattern such as `^\d+$`, convert with `Number`, and then check that the result is a safe integer in range. `parseInt("12px")` returns 12, which hides the mistake.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You convert query strings, form fields, or environment variables to numbers
- You want `null` and `undefined` treated the same with `value == null`
- You design a custom type and need control over conversion with `Symbol.toPrimitive`

❌ Avoid when:
- You rely on implicit coercion in business logic, such as money or quantity
- You use `==` for general comparisons; use `===` by default
- You use `parseInt` on user input without a pattern check; it ignores the rest of the text

---

## 📊 Visual Diagram
```
Expression            Steps                                   Result
"5" - 2       -> "5" -> 5, 5 - 2                              3
"5" + 2       -> one side is string -> "5" + "2"              '52'
[] + {}       -> "" + "[object Object]"                       '[object Object]'
[] == ![]     -> ![] = false -> [] == false -> "" == 0 -> 0 == 0    true
null == 0     -> null only equals null/undefined              false
null >= 0     -> null -> 0, so 0 >= 0                         true
NaN === NaN   -> NaN never equals anything                    false
"10" < "9"    -> both strings: compare characters              true
"10" < 9      -> string vs number: "10" -> 10                  false
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coercion | Automatic type conversion by an operator | Operator द्वारा अपने आप type बदलना |
| Truthy / falsy | Value that counts as true or false in `if` | `if` में true या false माने जाने वाली value |
| Loose equality | `==`, converts before comparing | `==`, तुलना से पहले बदलना |
| Strict equality | `===`, no conversion | `===`, बिना बदले तुलना |
| ToPrimitive | Turns an object into a primitive | Object को primitive बनाना |
| NaN | "Not a Number", never equal to itself | "Number नहीं", खुद के बराबर भी नहीं |
| Symbol.toPrimitive | A hook to control object conversion | Object conversion को नियंत्रित करने का hook |

---

## ⚡ 3-Line Summary
English:
1. `-` converts to numbers, while `+` concatenates when either side is a string.
2. `==` converts before comparing, so prefer `===` and use `== null` only for `null` or `undefined`.
3. Parse untrusted input strictly with a pattern, `Number`, and range checks, never with implicit coercion.

Hindi:
1. `-` numbers में बदलता है, जबकि `+` किसी एक side पर string हो तो जोड़ता है।
2. `==` तुलना से पहले बदलता है, इसलिए `===` इस्तेमाल करो और `== null` सिर्फ `null` या `undefined` जाँचने के लिए।
3. Untrusted input को pattern, `Number` और range checks से सख्ती से parse करो, implicit coercion से नहीं।

---

## ➡️ Next Topic
**199. Build Infinite Scroll** — now that you can convert and validate values such as `page` and `limit`, the next topic builds an infinite scroll that loads the next page when the user nears the bottom.
