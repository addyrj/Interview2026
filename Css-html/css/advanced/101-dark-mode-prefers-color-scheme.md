# 101. Dark Mode (prefers-color-scheme)
# हिंदी में: Dark Mode — User के System Theme के हिसाब से Colors बदलना

---

## 🔵 Simple Definition (English)
`prefers-color-scheme` is a **media feature** that tells your CSS whether the user's operating system or browser is set to **light** or **dark** mode. Combined with CSS variables, you can switch a whole site's colors with only a few lines. `color-scheme` tells the browser to also darken built-in UI like scrollbars and form controls.

## 🔵 सरल परिभाषा (Hindi)
`prefers-color-scheme` एक **media feature** है जो बताता है कि user का OS या browser **light** mode में है या **dark** mode में। CSS variables के साथ use करके कुछ ही lines में पूरी site के colors बदले जा सकते हैं। `color-scheme` property browser को बताती है कि scrollbar और form controls जैसे built-in UI भी dark करो।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Sites were always bright white. At night, users got blinded.
  - Developers built a separate "dark.css" and a toggle button,
    but the page still flashed white on load for dark-mode users.
  - Every color was hard-coded: #fff, #000 repeated in 500 places.

AFTER:
  - Browser tells CSS the user's preference BEFORE first paint (no flash).
  - Colors live in CSS variables; one @media block swaps them all.
  - OLED phones save battery, and eyes are less strained at night.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Sites हमेशा सफेद होती थीं; रात में आँखों को तकलीफ़ होती थी।
  - Developers अलग dark.css और toggle button बनाते थे, फिर भी load पर सफेद flash दिखता था।
  - Colors हर जगह hard-coded थे (#fff, #000), बदलना मुश्किल।

अब:
  - Browser पहले ही बता देता है कि user को क्या पसंद है (कोई flash नहीं)।
  - Colors CSS variables में रहते हैं; एक @media block सब बदल देता है।
  - OLED phone में battery बचती है और आँखों पर कम ज़ोर पड़ता है।
```

---

## 🟢 How it Works — Step by Step

```
1. User sets OS theme to Dark (macOS / Windows / Android / iOS).
2. Browser exposes it as the media feature:
      @media (prefers-color-scheme: dark) { ... }
3. You define colors as CSS variables on :root (light = default).
4. Inside the dark media query, you OVERRIDE the same variables.
5. All components use var(--bg), var(--text) → they switch automatically.
6. Add `color-scheme: light dark;` so native UI (scrollbar, inputs,
   default canvas) adapts too.

MANUAL TOGGLE (very common in interviews):
   - Put the theme on an attribute:  <html data-theme="dark">
   - CSS:   :root[data-theme="dark"] { --bg: #0f1115; ... }
   - JS:    read localStorage first, else matchMedia('(prefers-color-scheme: dark)')
   - Set the attribute in a tiny inline <head> script to avoid FOUC (flash).

NEW FEATURE:  light-dark(lightValue, darkValue)  -> one-line function for colors
   color: light-dark(#111, #eee);   /* needs color-scheme: light dark */
   Supported in all modern browsers since 2024 (Chrome 123+, Safari 17.5+, Firefox 120+).
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. User अपने OS में Dark theme चुनता है।
2. Browser इसे media feature बना देता है:
      @media (prefers-color-scheme: dark) { ... }
3. Colors को :root पर CSS variables में रखो (light = default)।
4. dark media query के अंदर उन्हीं variables को override करो।
5. सारे components var(--bg), var(--text) use करते हैं → अपने-आप बदल जाते हैं।
6. `color-scheme: light dark;` लगाओ ताकि scrollbar, inputs भी dark हो जाएँ।

MANUAL TOGGLE (interview में अक्सर पूछा जाता है):
   - Theme को attribute में रखो:  <html data-theme="dark">
   - CSS:   :root[data-theme="dark"] { --bg: #0f1115; ... }
   - JS:    पहले localStorage देखो, नहीं तो matchMedia से system preference लो।
   - <head> में छोटी inline script से attribute पहले set करो ताकि white flash न आए।

नया फ़ीचर:  light-dark(lightValue, darkValue) → एक line में दोनों colors
   color: light-dark(#111, #eee);   /* color-scheme: light dark ज़रूरी है */
```

---

## 🟡 Real World Example
**Instagram, Gmail and YouTube** follow the system theme by default and also give a manual switch in settings. When your phone is in dark mode at night, opening Gmail directly shows a dark inbox with no white flash. They store the manual choice (light / dark / system) in a cookie or localStorage and apply it before the first paint.

## 🟡 Real Example Hindi mein
**Instagram, Gmail और YouTube** default में system theme follow करते हैं और settings में manual switch भी देते हैं। रात में phone dark mode में हो तो Gmail खोलते ही dark inbox दिखता है, बिना white flash के। ये user की choice (light / dark / system) cookie या localStorage में रखते हैं और पहली paint से पहले apply करते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Tells browser the page supports both schemes (affects scrollbars, form controls) -->
  <meta name="color-scheme" content="light dark">
  <title>Dark Mode Demo</title>

  <!-- Run BEFORE paint so there is no white flash -->
  <script>
    // 1. saved choice wins, 2. else system preference
    const saved = localStorage.getItem('theme');
    const system = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.dataset.theme = saved || system;
  </script>

  <style>
    /* LIGHT = default values */
    :root {
      --bg: #ffffff;
      --surface: #f4f5f7;
      --text: #1a1a1a;
      --muted: #5f6368;
      --accent: #0b6bcb;
      --border: #dcdfe4;
      color-scheme: light;               /* native UI stays light */
    }

    /* DARK via system preference, only when user has NOT chosen manually */
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme]) {
        --bg: #0f1115;
        --surface: #1a1d23;
        --text: #e8eaed;
        --muted: #9aa0a6;
        --accent: #8ab4f8;
        --border: #2d3139;
        color-scheme: dark;
      }
    }

    /* DARK via manual toggle (data-theme set by JS) */
    :root[data-theme="dark"] {
      --bg: #0f1115;
      --surface: #1a1d23;
      --text: #e8eaed;
      --muted: #9aa0a6;
      --accent: #8ab4f8;
      --border: #2d3139;
      color-scheme: dark;
    }

    /* Everything below only uses variables, never raw colors */
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      transition: background .25s, color .25s;  /* smooth switch */
    }
    .wrap { max-width: 640px; margin: 0 auto; padding: 24px; }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-top: 16px;
    }
    .card p { color: var(--muted); }
    button, input {
      font: inherit;
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
    }
    button { background: var(--accent); color: var(--bg); border: 0; cursor: pointer; }

    /* Images: slightly dim in dark mode so they are not too bright */
    @media (prefers-color-scheme: dark) {
      img { filter: brightness(.85); }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Dark Mode Demo</h1>
    <button id="toggle">Toggle theme</button>

    <div class="card">
      <h2>Order #4821</h2>
      <p>Your package arrives tomorrow.</p>
      <input placeholder="Type here (native input follows theme)">
    </div>
  </div>

  <script>
    // Manual toggle: flip attribute + persist to localStorage
    document.getElementById('toggle').addEventListener('click', () => {
      const root = document.documentElement;
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      localStorage.setItem('theme', next);
    });
  </script>
</body>
</html>
```

```css
/* Short modern alternative using light-dark() */
:root { color-scheme: light dark; }
body {
  background: light-dark(#ffffff, #0f1115);
  color: light-dark(#1a1a1a, #e8eaed);
}
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind: set darkMode in config
// tailwind.config.js  ->  module.exports = { darkMode: 'class' }   // or 'media'
// 'media' follows system automatically; 'class' lets you toggle with <html class="dark">
<div className="bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100">
  Hello
</div>

// 2. Next.js: use the next-themes package (avoids hydration flash)
// app/providers.jsx
'use client';
import { ThemeProvider } from 'next-themes';
export default function Providers({ children }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  );
}

// 3. Toggle button
'use client';
import { useTheme } from 'next-themes';
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  return <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>Toggle</button>;
}

// 4. In app/layout.jsx add suppressHydrationWarning on <html>,
//    because next-themes changes the class before React hydrates.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you detect and style dark mode using only CSS?**
A1: Use the media query `@media (prefers-color-scheme: dark) { ... }`. The best pattern is to put colors in CSS variables on `:root` and override those variables inside the media query, so every component updates automatically.

**Q2: What does `color-scheme` do and why do we need it?**
A2: `color-scheme: light dark` tells the browser the page supports both schemes. The browser then renders default UI (scrollbars, form controls, default background and text color) in the matching theme. Without it, a dark page can still have a white scrollbar and white input boxes.

**Q3: How do you add a manual toggle that also respects system preference?**
A3: Store the theme in `data-theme` on `<html>`. On load, read `localStorage`; if nothing is saved, use `matchMedia('(prefers-color-scheme: dark)').matches`. Write CSS for `[data-theme="dark"]`. Save the choice on click. Run the script inline in `<head>` so there is no flash of the wrong theme (FOUC).

**Q4: How do you avoid the flash of wrong theme in Next.js?**
A4: The server cannot know the theme, so HTML renders with one theme and then JS switches it. Solutions: a blocking inline script in `<head>` (this is what `next-themes` injects), or storing the theme in a cookie and reading it on the server to render the correct class. Also add `suppressHydrationWarning` to `<html>`.

**Q5: Is dark mode just inverting colors? What design things should you consider?**
A5: No. `filter: invert(1)` breaks images and brand colors. Design a separate palette: avoid pure `#000` and pure `#fff` (use dark grey and off-white), reduce saturation, keep contrast ratio above 4.5:1 (WCAG), use lighter surfaces for elevation instead of shadows, and slightly dim images.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Hard-coding colors everywhere
```css
/* WRONG: need to repeat in dark media query for every rule */
.card { background: #fff; color: #000; }

/* CORRECT: variables, override once */
.card { background: var(--surface); color: var(--text); }
```

❌ **Mistake 2:** Forgetting `color-scheme`
```css
/* WRONG: dark page but white scrollbar and white <input> */
/* CORRECT */
:root { color-scheme: light dark; }
```

❌ **Mistake 3:** Setting the theme in `useEffect` (flash of white)
```jsx
// WRONG: runs AFTER first paint
useEffect(() => { document.documentElement.classList.add('dark'); }, []);
// CORRECT: blocking inline script in <head> or next-themes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| prefers-color-scheme | Media feature for user's theme | User की theme preference |
| color-scheme | Tells browser which themes page supports | Page कौन-सी themes support करता है |
| light-dark() | CSS function picking a color by theme | Theme के हिसाब से color चुनना |
| CSS variable | Reusable value `--name` | दोबारा use होने वाली value |
| FOUC | Flash of unstyled/wrong theme content | गलत theme की झलक |
| matchMedia | JS API to test media queries | JS में media query चेक करना |
| data-theme | Attribute used to switch theme manually | Manual theme switch के लिए attribute |

---

## ⚡ 3-Line Summary
**English:**
1. `@media (prefers-color-scheme: dark)` reads the user's OS theme; put colors in CSS variables and override them there.
2. Add `color-scheme: light dark` so native UI also adapts, and use `light-dark()` for short syntax.
3. For a manual toggle, use `data-theme` + localStorage and set it in a blocking script (or `next-themes`) to avoid flash.

**Hindi:**
1. `@media (prefers-color-scheme: dark)` user की OS theme पढ़ता है; colors को CSS variables में रखो और वहीं override करो।
2. `color-scheme: light dark` लगाओ ताकि native UI भी बदले; `light-dark()` से syntax छोटा होता है।
3. Manual toggle के लिए `data-theme` + localStorage use करो और blocking script (या `next-themes`) से flash रोको।

---

## ➡️ Next Topic
**102. CSS Print Styles** — Dark mode जैसे ही `@media print` भी एक media query है; invoice, ticket और resume print करने के लिए page को अलग style देना सीखेंगे।
