---

# Q230. Copy to Clipboard
# Category: DOM Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a `copyToClipboard(text)` function that returns a Promise resolving to `true` on success. Use the modern Clipboard API with a fallback for older browsers.

---

## 💡 Quick Concept (2 lines only)
`navigator.clipboard.writeText(text)` is the modern async way (needs HTTPS and a user gesture); the fallback uses a hidden textarea with `execCommand('copy')`.
हिंदी: Modern तरीका `navigator.clipboard.writeText` है, पुराने browsers के लिए textarea + `execCommand` fallback।

---

## ✅ Answer / Solution

```html
<input id="src" value="Hello Clipboard">
<button id="copyBtn">Copy</button>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Try navigator.clipboard (secure context only)
// Step 2: On failure/missing, use hidden textarea fallback
// Step 3: Return true/false

async function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {   // modern API available?
    try {
      await navigator.clipboard.writeText(text);         // write text
      return true;                                       // success
    } catch (err) {
      console.warn('Clipboard API failed:', err.name);   // permission denied etc.
    }
  }
  const ta = document.createElement('textarea');         // fallback element
  ta.value = text;                                       // put text inside
  ta.style.position = 'fixed';                           // avoid page scroll jump
  ta.style.opacity = '0';                                // hide it
  document.body.appendChild(ta);                         // must be in DOM
  ta.select();                                           // select the text
  let ok = false;                                        // result flag
  try {
    ok = document.execCommand('copy');                   // legacy copy
  } catch (e) {
    ok = false;                                          // not supported
  }
  document.body.removeChild(ta);                         // cleanup
  return ok;                                             // report result
}

document.getElementById('copyBtn').addEventListener('click', async () => { // user gesture
  const value = document.getElementById('src').value;    // text to copy
  const ok = await copyToClipboard(value);               // copy
  console.log(ok ? 'Copied!' : 'Copy failed');           // feedback
});

// ============================================
// TEST CASES
// ============================================

// Test 1: click Copy, then paste anywhere     -> Expected: "Hello Clipboard"
// Test 2: copyToClipboard('abc') from console -> Expected: may reject/false (needs focus + gesture)
// Test 3: await copyToClipboard('')           -> Expected: true (empty string copied)
// Test 4: await navigator.clipboard.readText() after click -> Expected: "Hello Clipboard" (permission prompt)
```

---

## 🔍 Why This Works (3 lines max)
The Clipboard API is async and permission-gated, so we wrap it in try/catch. If unavailable, a temporary selected textarea lets `execCommand('copy')` work. Returning a boolean lets the UI show feedback.
हिंदी: पहले modern API try करते हैं, fail हो तो textarea fallback; result true/false में मिलता है।

---

## ⚡ Alternative Solution
```javascript
// Minimal modern-only version
const copy = (t) => navigator.clipboard.writeText(t).then(() => true, () => false); // resolve true/false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: calling on page load (no user gesture) or on http:// -> rejected
navigator.clipboard.writeText('x');

// ✅ Correct: call inside a click handler on HTTPS/localhost and handle the Promise
```

---

## 🎯 Interview Tip (1 line)
Say: "Clipboard API needs secure context + user gesture and returns a Promise; execCommand is deprecated and kept only as fallback."

---

## 🔗 Related Questions
→ Q231 (dark mode toggle) | Q237 (localStorage wrapper) | Q205 (timeout a promise)
