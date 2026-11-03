# 125. Dark Mode Toggle
# हिंदी में: Dark Mode Toggle — Light/Dark Theme Switch बनाना

Files in this folder: [`index.html`](./index.html) (page + JS), [`style.css`](./style.css) (theme tokens + UI), `notes.md` (this file).

---

## 🔵 Simple Definition (English)
A dark mode toggle is a button that switches the whole page between a light and a dark colour theme. The best way: keep all colours in **CSS variables**, change them using a `data-theme` attribute on `<html>`, remember the choice in `localStorage`, and use `prefers-color-scheme` as the default.

## 🔵 सरल परिभाषा (Hindi)
Dark mode toggle एक button है जो पूरे page को light और dark colour theme के बीच switch करता है। सबसे अच्छा तरीका: सारे colours **CSS variables** में रखो, `<html>` पर `data-theme` attribute बदलो, user की choice `localStorage` में save करो, और default के लिए `prefers-color-scheme` use करो।

---

## 🔴 Problem it Solves
```
BEFORE (bad approach):
  - Colours hard-coded everywhere: .card { background: white; color: black; }
  - Dark mode = a second copy of every rule  -> huge, hard to maintain
  - Page loads white, then JS flips to dark   -> ugly white FLASH at night
  - Refresh forgets the user's choice
  - Ignores the phone's system dark setting

AFTER:
  - Colours defined ONCE as variables (--bg, --text, --accent)
  - A tiny attribute swap changes every variable at once
  - An inline script sets the theme BEFORE first paint -> no flash
  - localStorage remembers; prefers-color-scheme gives a smart default
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Colours हर जगह hard-code होते थे -> dark mode के लिए हर rule की दूसरी copy
  - Page पहले white load होता, फिर JS dark करता -> रात में आँखों में सफेद FLASH
  - Refresh करने पर user की choice भूल जाती
  - Phone की system dark setting ignore होती

अब:
  - Colours एक बार variables में define
  - एक attribute बदलो -> सारे colours एक साथ बदल जाते हैं
  - Inline script first paint से पहले theme set करती है -> flash नहीं
  - localStorage याद रखता है; prefers-color-scheme smart default देता है
```

---

## 🟢 How it Works — Step by Step
```
1. DEFINE TOKENS   :root { --bg: white; --text: #1c1c1e; }
                   [data-theme="dark"] { --bg: #121214; --text: #f2f2f3; }
2. USE TOKENS      body { background: var(--bg); color: var(--text); }
3. INITIAL THEME   inline <script> in <head>:
                     saved choice in localStorage?  -> use it
                     else OS prefers dark?          -> "dark"
                     else                           -> "light"
                   set <html data-theme="...">  (before body paints = no flash)
4. TOGGLE CLICK    flip data-theme, save to localStorage, update aria-pressed
5. COLOR-SCHEME    color-scheme: dark  -> browser draws native scrollbars,
                   inputs, default text colours in dark style too
6. FOLLOW OS       matchMedia('(prefers-color-scheme: dark)') "change" event
                   -> if user never chose manually, follow the OS live
```

Key trick: a CSS variable defined on `<html>` is **inherited** by every element, so changing the attribute re-computes every `var(--bg)` automatically.

## 🟢 कैसे काम करता है? (Hindi)
```
1. TOKENS बनाओ     :root में light colours, [data-theme="dark"] में dark colours
2. TOKENS use करो   background: var(--bg); color: var(--text);
3. शुरुआती theme    <head> की inline script:
                     localStorage में saved है?   -> वही use करो
                     नहीं तो OS dark माँग रहा है? -> "dark"
                     वरना                          -> "light"
                   body paint होने से पहले <html> पर data-theme set -> flash नहीं
4. Click पर         data-theme उल्टा करो, localStorage में save, aria-pressed update
5. color-scheme     scrollbar, input जैसे native controls भी dark दिखें
6. OS को follow     user ने manually नहीं चुना तो OS बदलने पर live बदलो
```

Trick: `<html>` पर defined variable हर child को inherit होता है, इसलिए attribute बदलते ही सारे `var(--bg)` अपने-आप नए value पर चले जाते हैं।

---

## 🟡 Real World Example
**YouTube, GitHub, Twitter/X and Instagram web** all offer Light / Dark / "Use device setting". They store the choice (cookie or localStorage) and apply it very early so the page never flashes white. **Gmail** and **Zomato** follow the OS dark setting on mobile. Interviewers love this problem because it tests CSS variables, inheritance, `prefers-color-scheme`, storage, accessibility and the "flash of wrong theme" detail in one small task.

## 🟡 Real Example Hindi mein
**YouTube, GitHub, Twitter/X और Instagram web** में Light / Dark / "Device setting follow करो" option होता है। ये choice cookie या localStorage में रखते हैं और page बहुत जल्दी apply करते हैं ताकि सफेद flash न दिखे। **Gmail** और **Zomato** mobile पर OS की dark setting follow करते हैं। Interview में ये सवाल इसलिए आता है क्योंकि इसमें CSS variables, inheritance, `prefers-color-scheme`, storage, accessibility और "wrong theme flash" सब एक साथ test होते हैं।

---

## 💻 Live Code Example

Open `index.html` directly in a browser (it loads `style.css` from the same folder). Both files are in this folder; the core parts are below.

```html
<!-- index.html (important parts) -->
<!-- 1. Tell browser both schemes are supported -->
<meta name="color-scheme" content="light dark">

<!-- 2. NO-FLASH script: in <head>, before CSS paints the body -->
<script>
  (function () {
    try {
      var saved = localStorage.getItem('theme');                       // user's earlier choice
      var system = matchMedia('(prefers-color-scheme: dark)').matches  // OS preference
        ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', saved || system);
    } catch (e) {
      document.documentElement.setAttribute('data-theme', 'light');    // storage blocked
    }
  })();
</script>

<!-- 3. The toggle: a real <button>, with aria-pressed for screen readers -->
<button id="theme-toggle" class="toggle" type="button"
        aria-label="Toggle dark mode" aria-pressed="false">
  <span class="toggle__thumb" aria-hidden="true"></span>
</button>

<script>
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');

  btn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);          // swaps all variables
    localStorage.setItem('theme', next);            // remember it
    btn.setAttribute('aria-pressed', next === 'dark');
  });
</script>
```

```css
/* style.css (important parts) */

/* Light tokens = default */
:root, [data-theme="light"] {
  color-scheme: light;     /* native scrollbars/inputs in light style */
  --bg: #ffffff;
  --text: #1c1c1e;
  --surface: #f5f5f7;
  --accent: #2563eb;
}

/* Dark tokens: SAME names, new values */
[data-theme="dark"] {
  color-scheme: dark;
  --bg: #121214;
  --text: #f2f2f3;
  --surface: #1e1e22;
  --accent: #60a5fa;
}

/* Components only know variable names, never real colours */
body {
  background: var(--bg);
  color: var(--text);
  transition: background-color 0.3s, color 0.3s;   /* smooth switch */
}

/* Switch thumb slides when aria-pressed="true" */
.toggle__thumb { transition: transform 0.3s; }
.toggle[aria-pressed="true"] .toggle__thumb { transform: translateX(24px); }

/* Respect reduced-motion users */
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
```

Pure-CSS fallback (no JS, only follows the OS):
```css
:root { --bg: #fff; --text: #111; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #121214; --text: #f2f2f3; }   /* OS dark -> dark tokens */
}
```

Modern shortcut (`light-dark()`, supported in all current evergreen browsers since 2024; needs `color-scheme` set):
```css
:root { color-scheme: light dark; }
body { background: light-dark(#fff, #121214); color: light-dark(#111, #eee); }
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Next.js: use the "next-themes" library (most common solution)
// app/providers.jsx
'use client';
import { ThemeProvider } from 'next-themes';

export default function Providers({ children }) {
  // attribute="data-theme" -> sets <html data-theme="dark">
  // defaultTheme="system" -> follow the OS until user chooses
  return (
    <ThemeProvider attribute="data-theme" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  );
}

// 2. Toggle component
'use client';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);       // avoid hydration mismatch
  if (!mounted) return null;                   // server does not know the theme

  return (
    <button
      aria-pressed={resolvedTheme === 'dark'}
      onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
    >
      {resolvedTheme === 'dark' ? 'Light' : 'Dark'} mode
    </button>
  );
}

// 3. layout.jsx needs suppressHydrationWarning on <html>,
//    because next-themes edits the attribute before React hydrates:
// <html lang="en" suppressHydrationWarning>

// 4. Tailwind: set darkMode to class (v3) or a custom variant (v4)
// tailwind.config.js (v3): module.exports = { darkMode: 'class' }
<div className="bg-white text-black dark:bg-zinc-900 dark:text-zinc-100">
  Card
</div>
// Tailwind v4: @custom-variant dark (&:where([data-theme=dark], [data-theme=dark] *));
```

The no-flash inline script from `index.html` is exactly what `next-themes` injects for you.

---

## ⚫ Interview Questions + Answers

**Q1: How do you implement dark mode in CSS?**
A1: Define colours as CSS custom properties on `:root`, override the same variables under `[data-theme="dark"]` (or inside `@media (prefers-color-scheme: dark)`), and make every component use `var(--name)`. Switching the theme then means changing one attribute, not rewriting rules.

**Q2: What is `prefers-color-scheme` and how is it different from a toggle?**
A2: It is a media feature that reports the OS/browser theme (`light` or `dark`). It is automatic but the user cannot override it per site. A toggle gives manual control. Best UX: default to `prefers-color-scheme`, let the toggle override, and save the override in `localStorage`.

**Q3: How do you avoid the "flash of wrong theme" (FOUC)?**
A3: Apply the theme **before first paint**: put a tiny blocking inline script in `<head>` that reads `localStorage` / the media query and sets `data-theme` on `<html>`. If you wait for `DOMContentLoaded` or a React `useEffect`, the page paints in light mode first and flickers. In SSR frameworks, `next-themes` injects that script.

**Q4: What does the `color-scheme` property do?**
A4: It tells the browser which schemes an element supports, so native UI (scrollbars, form controls, default canvas and text colours) switches too. Without it, a dark page can still have white scrollbars and a light `<input>` background. Set `color-scheme: dark` in the dark theme (or `<meta name="color-scheme" content="light dark">`).

**Q5: How do you make the toggle accessible?**
A5: Use a real `<button>` (keyboard support free), add an accessible name (`aria-label`), expose state with `aria-pressed` (or use `role="switch"` with `aria-checked`), keep a visible `:focus-visible` outline, make sure both themes pass WCAG contrast (4.5:1 for text), and respect `prefers-reduced-motion` for the transition.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Setting the theme in `DOMContentLoaded` or `useEffect` (white flash on load)
✅ **Correct way:** Inline script in `<head>` that sets `data-theme` before the body renders.

❌ **Mistake 2:** Using pure black `#000` background with pure white `#fff` text (harsh, eye strain)
✅ **Correct way:** Use dark grey (`#121214`) and off-white (`#f2f2f3`); keep contrast high but not extreme.

❌ **Mistake 3:** Hard-coding colours in components (`color: #333`), so they stay dark in dark mode
✅ **Correct way:** Every colour must come from a token: `color: var(--text)`.

❌ **Mistake 4:** Forgetting `color-scheme`, so scrollbars and inputs stay light
✅ **Correct way:** Add `color-scheme: dark` under the dark theme.

❌ **Mistake 5:** Storing the choice but ignoring the OS setting (or the reverse)
✅ **Correct way:** `saved || system`, and follow OS changes live while the user has no saved choice.

❌ **Mistake 6:** Using `<div onclick>` as the toggle with no label or state
✅ **Correct way:** `<button aria-pressed>` with an accessible name.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSS variable (custom property) | `--name: value`, read with `var(--name)` | CSS का variable |
| Design token | Named colour/size reused across UI | Reusable named value |
| `data-theme` | Attribute on `<html>` that selects the theme | Theme चुनने वाला attribute |
| `prefers-color-scheme` | Media query for OS light/dark setting | OS की theme setting |
| `color-scheme` | Makes native UI follow the theme | Native controls की theme |
| `light-dark()` | CSS function picking one of two colours | दो colours में से चुनता है |
| `localStorage` | Browser key-value storage that persists | Browser में स्थायी storage |
| FOUC / flash | Wrong theme visible before JS runs | गलत theme की झलक |
| `aria-pressed` | Announces toggle on/off state | Toggle की state बताता है |
| `matchMedia` | JS API to test/listen to media queries | JS में media query |

---

## ⚡ 3-Line Summary
**English:**
1. Put all colours in CSS variables and override them with `[data-theme="dark"]`; components only use `var(--token)`.
2. Set the theme in an inline `<head>` script (saved choice, else `prefers-color-scheme`) to prevent the white flash; save clicks in `localStorage`.
3. Add `color-scheme`, a real `<button>` with `aria-pressed`, and good contrast; in Next.js use `next-themes`.

**Hindi:**
1. सारे colours CSS variables में रखो और `[data-theme="dark"]` से override करो; components सिर्फ `var(--token)` use करें।
2. `<head>` की inline script में theme set करो (saved choice, वरना `prefers-color-scheme`) ताकि सफेद flash न हो; click पर `localStorage` में save करो।
3. `color-scheme`, `aria-pressed` वाला असली `<button>` और अच्छा contrast रखो; Next.js में `next-themes` use करो।

---

## ➡️ Next Topic
**Interview Problems complete (125/125).** Next: revise with the quick-revision cheatsheets (`quick-revision/css-cheatsheet.md`), then re-build problems 111-125 from memory without looking, timing yourself to 20 minutes each, because that is how live-coding rounds feel.
