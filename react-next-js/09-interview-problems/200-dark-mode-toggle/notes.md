# 200. Build Dark Mode Toggle
# हिंदी में: Dark Mode Toggle बनाना

> Code: [App.jsx](./App.jsx) (complete, tested with jsdom: toggle, `data-theme` attribute, localStorage save)

---

## 🔵 Simple Definition (English)
A **dark mode toggle** is a button that switches the whole app between a light and a dark theme, remembers the choice, and starts with the user's operating system preference. In React it is usually built with context, `localStorage` and CSS variables.

## 🔵 सरल परिभाषा (Hindi)
**Dark mode toggle** एक बटन है जो पूरे app को light और dark theme के बीच बदलता है, user की choice याद रखता है, और शुरुआत में user के operating system की preference इस्तेमाल करता है। React में इसे आमतौर पर context, `localStorage` और CSS variables से बनाते हैं।

---

## 🔴 Problem it Solves
Without a shared theme state, every component would need its own `isDark` prop (props drilling), the choice would reset on refresh, and colours would be hard-coded in many places. Interviewers ask this problem because it tests context, side effects, persistence and SSR thinking in one small task.

## 🔴 यह क्यों बना? (Hindi)
Shared theme state के बिना हर component को अपना `isDark` prop चाहिए होता (props drilling), refresh पर choice खो जाती, और colours कई जगह hard-code होते। Interview में यह problem इसलिए पूछी जाती है क्योंकि इसमें context, side effects, persistence और SSR की समझ एक छोटे task में परखी जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → On first render read localStorage ("theme"); if empty, use prefers-color-scheme
Step 2 → Keep the theme in useState inside a ThemeProvider (context)
Step 3 → useEffect([theme]) sets <html data-theme="dark"> and saves to localStorage
Step 4 → CSS variables change under [data-theme="dark"], so no component re-styles itself
Step 5 → toggle() flips the state; only context consumers re-render
Step 6 → useMemo on the context value avoids useless re-renders of consumers

Re-render: click → setTheme → Provider re-renders → consumers (ThemeToggle) re-render.
Children passed as {children} keep the same element identity, so React skips them.
Performance: CSS variables repaint the page once; no JS loop touches every element.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहले render में localStorage ("theme") पढ़ो; खाली हो तो prefers-color-scheme लो
Step 2 → Theme को ThemeProvider (context) के अंदर useState में रखो
Step 3 → useEffect([theme]) <html data-theme="dark"> सेट करता है और localStorage में save करता है
Step 4 → CSS variables [data-theme="dark"] में बदलते हैं, इसलिए कोई component खुद re-style नहीं होता
Step 5 → toggle() state पलटता है; सिर्फ context consumers दोबारा render होते हैं
Step 6 → Context value पर useMemo बेकार re-renders रोकता है

Re-render: click → setTheme → Provider re-render → consumers (ThemeToggle) re-render।
{children} का element वही रहता है, इसलिए React उन्हें skip कर देता है।
Performance: CSS variables से page एक बार repaint होता है; JS हर element को नहीं छूती।
```

---

## 🟡 Real World Example
**Swiggy / Zomato settings:** The "Appearance" switch changes the theme of every screen at once. Open the app tomorrow and it is still dark. A new user with a dark phone gets dark mode on the first visit, because the app reads the OS preference.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato settings:** "Appearance" switch हर screen की theme एक साथ बदल देता है। कल app खोलो तो भी dark ही रहता है। नए user का phone dark है तो पहली visit पर ही dark mode मिलता है, क्योंकि app OS preference पढ़ता है।

---

## 💻 Code Example — Basic

```jsx
// Smallest possible dark mode: one state, one class on <body>
import { useState, useEffect } from 'react';          // React hooks
import { createRoot } from 'react-dom/client';        // React 18/19 root API

function App() {
  const [dark, setDark] = useState(false);            // false = light theme

  useEffect(() => {
    document.body.classList.toggle('dark', dark);     // add/remove the "dark" class on <body>
  }, [dark]);                                         // run only when dark changes

  return (
    <button onClick={() => setDark((d) => !d)}>       {/* functional update: always correct */}
      {dark ? 'Light mode' : 'Dark mode'}             {/* label shows the next action */}
    </button>
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Production version (same as App.jsx): context + persistence + OS preference + CSS variables
import { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';

const ThemeContext = createContext(null);             // shared theme state

function getInitialTheme() {
  if (typeof window === 'undefined') return 'light';  // no DOM on server
  const saved = window.localStorage.getItem('theme'); // user's earlier choice
  if (saved === 'light' || saved === 'dark') return saved; // validate stored value
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; // OS
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getInitialTheme);    // lazy initial state: runs once
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme); // CSS hook
    window.localStorage.setItem('theme', theme);                // persist
  }, [theme]);
  const toggle = useCallback(() => setTheme((t) => (t === 'dark' ? 'light' : 'dark')), []);
  const value = useMemo(() => ({ theme, toggle }), [theme, toggle]); // stable reference
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);                        // nearest provider
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>');
  return ctx;
}
```

```css
/* CSS variables: components never mention "dark" */
:root { --bg: #fff; --fg: #111; }
[data-theme="dark"] { --bg: #121212; --fg: #f5f5f5; }
body { background: var(--bg); color: var(--fg); }
```

---

## 🟠 Next.js Connection
On the server there is no `localStorage` or `window`, so the first HTML is always rendered with a default theme. If the saved theme is `dark`, the user sees a white flash (FOUC) until React runs. Two fixes: (1) store the theme in a **cookie** and read it in the Server Component, or (2) run a tiny inline script before paint that sets `data-theme`. The popular `next-themes` library does (2) for you.

```jsx
// app/layout.jsx (Server Component): read the theme cookie on the server, no flash
import { cookies } from 'next/headers';               // server-only API

export default async function RootLayout({ children }) {
  const theme = (await cookies()).get('theme')?.value ?? 'light'; // Next.js 15: cookies() is async
  return (
    <html lang="en" data-theme={theme}>               {/* correct theme in the very first HTML */}
      <body>{children}</body>
    </html>
  );
}

// ThemeToggle must be a Client Component ('use client') and write document.cookie on click.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Reading `localStorage` directly in render (crashes on the server, causes hydration mismatch)
✅ **Correct:** Guard with `typeof window` or read inside `useEffect`

```jsx
// Wrong: ReferenceError on the server in Next.js
const [theme] = useState(localStorage.getItem('theme'));
// Right: guard and use lazy init
const [theme] = useState(() => (typeof window === 'undefined' ? 'light' : localStorage.getItem('theme') ?? 'light'));
```

❌ **Mistake 2:** Passing `isDark` through props to every component
✅ **Correct:** Put it in context and style with CSS variables

```jsx
// Wrong: props drilling through 5 levels
<Header isDark={isDark}><Menu isDark={isDark} /></Header>
// Right: any component reads useTheme(); most need nothing at all because CSS handles colours
```

❌ **Mistake 3:** Creating a new context value object every render
✅ **Correct:** Wrap it in `useMemo`

```jsx
// Wrong: new object each render → every consumer re-renders even if theme did not change
<ThemeContext.Provider value={{ theme, toggle }}>
// Right
const value = useMemo(() => ({ theme, toggle }), [theme, toggle]);
```

---

## 🧠 Tricky Interview Question

```jsx
// Next.js client component, rendered on the server first
function Banner() {
  const theme = typeof window !== 'undefined' ? localStorage.getItem('theme') : 'light';
  return <p>Theme: {theme}</p>;
}
```
**Answer:** There is no crash, but there is a **hydration mismatch**. The server renders "Theme: light". If the browser has `dark` saved, the first client render produces "Theme: dark", and React warns that server and client HTML differ. The first render must match the server. Read the stored value after mount (in `useEffect`) or from a cookie on the server.

---

## ⚫ Interview Questions + Answers

Q1: How do you build dark mode in React?
A1: Keep the theme in a context provider, save it in `localStorage`, apply it as a `data-theme` attribute on `<html>`, and define colours as CSS variables per theme. Components just use the variables.

Q2: Why CSS variables instead of conditional classes in each component?
A2: Changing one attribute updates every colour with a single style recalculation. No component re-renders just for colours, so it is faster and simpler.

Q3: How do you respect the user's OS setting?
A3: Use `window.matchMedia('(prefers-color-scheme: dark)')` as the fallback when nothing is saved. You can also listen for its `change` event to follow the OS live.

Q4: How do you avoid the white flash on reload in Next.js?
A4: The server cannot read `localStorage`, so use a cookie (read in the layout) or an inline blocking script that sets `data-theme` before paint. `next-themes` implements this.

Q5: Why use `useMemo` and `useCallback` here?
A5: A context value that changes identity re-renders all consumers. `useMemo` keeps the value object stable between renders where the theme did not change, and `useCallback` keeps `toggle` stable.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Many components need the same theme and you want one source of truth
- You want persistence and OS preference support
- Colours are defined as design tokens

❌ **Avoid when:**
- The site has only one theme (extra code for no value)
- Only CSS is needed: `@media (prefers-color-scheme: dark)` alone works without any JS
- You would store large objects in context (use a state library)

---

## 📊 Visual Diagram

```
  localStorage ──┐
  OS preference ─┴─► getInitialTheme() ─► useState(theme)
                                              │
        click ─► toggle() ─► setTheme ────────┤
                                              ▼
                         useEffect([theme]) ─► <html data-theme="dark">
                                              └► localStorage.setItem
                                              ▼
              CSS: [data-theme="dark"] { --bg: #121212 }  → whole page recolours
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Theme | Set of colours for the UI | UI के colours का set |
| prefers-color-scheme | CSS/JS media query for the OS theme | OS की theme पूछने वाली media query |
| CSS variable | `--name` value reused in CSS | CSS में दोबारा इस्तेमाल होने वाली value |
| Context | Way to share state without props | Props के बिना state share करना |
| FOUC | Flash of unstyled/wrong-theme content | गलत theme की झलक |
| Hydration mismatch | Server HTML differs from client render | Server और client HTML में अंतर |
| Lazy initial state | `useState(fn)` runs fn only once | useState में function, जो एक ही बार चलता है |

---

## ⚡ 3-Line Summary
**English:**
1. Store the theme in context, save it in `localStorage`, and apply it as `data-theme` on `<html>`.
2. Use CSS variables so a single attribute change recolours the whole app without re-rendering components.
3. In Next.js use a cookie or an inline script to avoid the flash and hydration mismatch.

**Hindi:**
1. Theme को context में रखो, `localStorage` में save करो, और `<html>` पर `data-theme` की तरह लगाओ।
2. CSS variables इस्तेमाल करो ताकि एक attribute बदलने से पूरा app बिना components re-render किए recolour हो जाए।
3. Next.js में flash और hydration mismatch से बचने के लिए cookie या inline script इस्तेमाल करो।

---

## ➡️ Next Topic
**201. Build Shopping Cart** — अब state management की असली practice: `useReducer`, context, derived totals और persistence के साथ Amazon जैसा cart।
