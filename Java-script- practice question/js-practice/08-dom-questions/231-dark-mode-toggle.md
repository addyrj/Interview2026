---

# Q231. Dark Mode Toggle
# Category: DOM Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
Build a dark mode toggle that: uses the system preference by default, remembers the user's choice in `localStorage`, and applies the theme via a `data-theme` attribute on `<html>`.

---

## 💡 Quick Concept (2 lines only)
Set `data-theme` on `document.documentElement`, style with CSS variables, and persist the choice in `localStorage`.
हिंदी: `data-theme` attribute बदलो, CSS variables से colors बदलो, और choice `localStorage` में save करो।

---

## ✅ Answer / Solution

```html
<button id="themeBtn">Toggle theme</button>
<style>
  :root { --bg: #fff; --fg: #111; }
  :root[data-theme="dark"] { --bg: #111; --fg: #eee; }
  body { background: var(--bg); color: var(--fg); }
</style>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Decide initial theme (saved > system)
// Step 2: applyTheme sets attribute + saves
// Step 3: Button toggles; listen to system changes if user has no saved choice

const KEY = 'theme';                                     // storage key
const root = document.documentElement;                   // <html> element
const media = window.matchMedia('(prefers-color-scheme: dark)'); // system pref

function getSaved() {
  try { return localStorage.getItem(KEY); }              // read saved value
  catch (e) { return null; }                             // storage blocked
}

function applyTheme(theme, save = true) {
  root.setAttribute('data-theme', theme);                // trigger CSS variables
  if (save) {
    try { localStorage.setItem(KEY, theme); }            // remember choice
    catch (e) { /* ignore */ }                           // storage blocked
  }
}

applyTheme(getSaved() || (media.matches ? 'dark' : 'light'), false); // initial theme

document.getElementById('themeBtn').addEventListener('click', () => { // toggle
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; // flip
  applyTheme(next);                                      // apply + save
});

media.addEventListener('change', (e) => {                // OS theme changed
  if (!getSaved()) applyTheme(e.matches ? 'dark' : 'light', false); // follow only if no saved choice
});

// ============================================
// TEST CASES
// ============================================

// Test 1: first visit, OS dark -> root.dataset.theme // Expected: "dark"
// Test 2: click button         -> root.dataset.theme // Expected: "light", localStorage.theme === "light"
// Test 3: reload page          -> Expected: still "light" (saved choice wins)
// Test 4: localStorage.removeItem('theme'); reload -> Expected: follows OS setting
```

---

## 🔍 Why This Works (3 lines max)
CSS variables re-evaluate when the attribute changes, so one attribute switches the whole page. Saved value overrides system preference. try/catch protects against blocked storage.
हिंदी: एक attribute बदलने से पूरा theme बदल जाता है, और saved choice system preference से ऊपर रहती है।

---

## ⚡ Alternative Solution
```javascript
// classList version (class "dark" on body)
document.body.classList.toggle('dark');                  // flip class
localStorage.setItem('dark', document.body.classList.contains('dark')); // save boolean as string
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: applying theme after load -> white flash (FOUC)
window.addEventListener('load', () => applyTheme(getSaved()));

// ✅ Correct: run a tiny inline script in <head> before first paint
```

---

## 🎯 Interview Tip (1 line)
Say: "Use CSS variables + data-theme, respect prefers-color-scheme, persist in localStorage, and set theme in head to avoid flash."

---

## 🔗 Related Questions
→ Q237 (localStorage wrapper) | Q195 (local storage wrapper) | Q230 (copy to clipboard)
