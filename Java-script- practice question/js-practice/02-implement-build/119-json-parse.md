---

# Q119. Implement JSON.parse (Basic)
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `myParse(str)` that converts a JSON string into a JS value: objects, arrays, strings, numbers, `true`, `false`, `null`. Throw `SyntaxError` for bad input. (Do not use `JSON.parse` or `eval`.)

```javascript
myParse('{"a":[1,2,{"b":null}]}'); // { a: [1, 2, { b: null }] }
```

---

## 💡 Quick Concept (2 lines only)
Write a small recursive-descent parser: keep an index `i`, look at the current character, and call the right function (object, array, string, number, literal).
हिंदी: एक index रखकर character देखो और object, array, string या number के हिसाब से सही function बुलाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: keep position i and helper to skip whitespace
// Step 2: parseValue looks at the current char and dispatches
// Step 3: objects/arrays call parseValue recursively

function myParse(str) {
  let i = 0;                                              // current position
  const fail = () => { throw new SyntaxError(`Unexpected token ${str[i] ?? 'end'} at position ${i}`); }; // error helper
  const ws = () => { while (i < str.length && /\s/.test(str[i])) i++; }; // skip whitespace

  function parseValue() {
    ws();                                                 // ignore spaces
    const c = str[i];                                     // current char
    if (c === '{') return parseObject();                  // object
    if (c === '[') return parseArray();                   // array
    if (c === '"') return parseString();                  // string
    if (str.startsWith('true', i)) { i += 4; return true; }   // literal true
    if (str.startsWith('false', i)) { i += 5; return false; } // literal false
    if (str.startsWith('null', i)) { i += 4; return null; }   // literal null
    return parseNumber();                                 // else must be number
  }

  function parseString() {
    i++;                                                  // skip opening quote
    let out = '';                                         // collected characters
    const esc = { n: '\n', t: '\t', r: '\r', b: '\b', f: '\f', '"': '"', '\\': '\\', '/': '/' }; // escapes
    while (str[i] !== '"') {                              // until closing quote
      if (i >= str.length) fail();                        // string never closed
      if (str[i] === '\\') {                              // escape sequence
        i++;
        if (str[i] === 'u') { out += String.fromCharCode(parseInt(str.slice(i + 1, i + 5), 16)); i += 5; continue; } // \uXXXX
        if (!(str[i] in esc)) fail();                     // unknown escape
        out += esc[str[i++]];                             // mapped char
      } else out += str[i++];                             // normal char
    }
    i++;                                                  // skip closing quote
    return out;
  }

  function parseNumber() {
    const m = /^-?\d+(\.\d+)?([eE][+-]?\d+)?/.exec(str.slice(i)); // number pattern
    if (!m) fail();                                       // not a number
    i += m[0].length;                                     // move past it
    return Number(m[0]);                                  // convert text to number
  }

  function parseArray() {
    i++;                                                  // skip [
    const arr = [];                                       // result
    ws();
    if (str[i] === ']') { i++; return arr; }              // empty array
    while (true) {
      arr.push(parseValue());                             // read one item
      ws();
      if (str[i] === ',') { i++; continue; }              // next item
      if (str[i] === ']') { i++; return arr; }            // end of array
      fail();                                             // anything else is invalid
    }
  }

  function parseObject() {
    i++;                                                  // skip {
    const obj = {};                                       // result
    ws();
    if (str[i] === '}') { i++; return obj; }              // empty object
    while (true) {
      ws();
      if (str[i] !== '"') fail();                         // keys must be strings
      const key = parseString();                          // read key
      ws();
      if (str[i++] !== ':') fail();                       // colon required
      obj[key] = parseValue();                            // read value
      ws();
      if (str[i] === ',') { i++; continue; }              // next pair
      if (str[i] === '}') { i++; return obj; }            // end of object
      fail();
    }
  }

  const result = parseValue();                            // parse whole input
  ws();
  if (i < str.length) fail();                             // junk after value
  return result;
}

// ============================================
// TEST CASES
// ============================================

console.log(myParse('{"a":[1,2,{"b":null}]}'));   // Expected: { a: [ 1, 2, { b: null } ] }
console.log(myParse(' [true, false, -3.5e1] '));  // Expected: [ true, false, -35 ]
console.log(myParse('"he said \\"hi\\""'));       // Expected: he said "hi"
console.log(myParse('{}'), myParse('[]'));        // Expected: {} []
try { myParse('{"a":}'); } catch (e) { console.log(e.name); } // Expected: SyntaxError
try { myParse('[1,2'); } catch (e) { console.log(e.name); }   // Expected: SyntaxError
```

---

## 🔍 Why This Works (3 lines max)
JSON grammar is recursive, so one function per grammar rule maps neatly to code. The index `i` moves forward only, giving O(n) time.
हिंदी: JSON की बनावट recursive है, इसलिए हर नियम के लिए एक function बनाना आसान रहता है।

---

## ⚡ Alternative Solution
```javascript
// Cheating-but-valid for interviews: validate with a reviver-free native call
// (shown only to explain what the native one returns)
const data = JSON.parse('{"x":[1,2]}');
console.log(data.x.length); // Expected: 2
// Real interviews expect the parser above (or a tokenizer + stack version).
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using eval — runs arbitrary code, huge security hole
const data = eval('(' + str + ')');

// ✅ Correct: parse character by character (or JSON.parse in real code)
const data = myParse(str);
```

---

## 🎯 Interview Tip (1 line)
Say "recursive descent: one function per JSON type, plus clear SyntaxError on bad input"; never use `eval`.

---

## 🔗 Related Questions
→ Q118 (JSON.stringify) | Q071 (deep clone) | Q190 (template engine) | Q197 (URL parser)
