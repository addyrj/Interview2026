# 111. Build a Responsive Navbar
# हिंदी में: Responsive Navbar बनाओ — Desktop पर Row, Mobile पर Hamburger

Files: [`index.html`](./index.html) (page) and [`style.css`](./style.css) (styles). Open `index.html` directly in a browser and resize the window.

---

## 🔵 Simple Definition (English)
A **responsive navbar** shows links in a horizontal row on wide screens and collapses them behind a **hamburger button** on small screens. It is built with Flexbox for alignment and a media query to switch layout at a breakpoint (here 768px).

## 🔵 सरल परिभाषा (Hindi)
**Responsive navbar** चौड़ी screen पर links को एक row में दिखाता है और छोटी screen पर उन्हें **hamburger button** के पीछे छुपा देता है। इसमें alignment के लिए Flexbox और layout बदलने के लिए एक media query (यहाँ 768px) use होती है।

---

## 🔴 Problem it Solves
```
- Desktop menus with 6+ links do not fit on a 375px phone: links wrap, overlap or overflow.
- Tiny tap targets make navigation hard on touch screens.
- Interviewers use this problem to test: flexbox, media queries, mobile-first thinking,
  pseudo-classes, transitions, accessibility, and JS-less interaction.
```

## 🔴 यह क्यों बना? (Hindi)
```
- 6+ links वाला desktop menu 375px के phone में नहीं समाता: links टूटते हैं या बाहर निकलते हैं।
- Touch screen पर छोटे tap targets से navigation मुश्किल होती है।
- Interview में यह problem flexbox, media queries, mobile-first सोच, pseudo-classes,
  transitions, accessibility और बिना JS के interaction परखने के लिए पूछी जाती है।
```

---

## 🟢 How it Works — Step by Step

```
1. MARKUP: <header><nav> with logo, checkbox, label (hamburger), <ul> links.
   Order matters: checkbox -> label -> ul, so sibling selectors (+ and ~) can reach them.
2. MOBILE FIRST (default CSS, no media query):
     .navbar   = flex, space-between, wrap  -> logo left, hamburger right
     .nav-links = width 100%, max-height 0, overflow hidden -> collapsed row under the logo
3. TOGGLE without JS (checkbox hack):
     .nav-toggle:checked ~ .nav-links { max-height: 400px; }   -> opens with transition
     .nav-toggle:checked + .hamburger span { ... }             -> bars become an X
   Clicking the <label for="nav-toggle"> toggles the hidden checkbox.
4. DESKTOP (@media (min-width: 768px)):
     .hamburger { display: none }
     .nav-links { display: flex; max-height: none; overflow: visible }
5. STICKY HEADER: position: sticky; top: 0; z-index: 100.
6. ACCESSIBILITY: skip link, aria-label on nav, aria-current="page", :focus-visible styles,
   prefers-reduced-motion respected.
7. WHY max-height and not height: you cannot transition to height:auto;
   max-height with a generous limit is the classic trick. (Modern: interpolate-size / grid-template-rows 0fr -> 1fr.)
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. MARKUP: <header><nav> में logo, checkbox, label (hamburger), <ul> links।
   क्रम ज़रूरी: checkbox -> label -> ul, ताकि sibling selectors (+ और ~) काम करें।
2. MOBILE FIRST (default CSS, बिना media query):
     .navbar    = flex, space-between, wrap  -> logo बाएँ, hamburger दाएँ
     .nav-links = width 100%, max-height 0, overflow hidden -> logo के नीचे collapsed
3. बिना JS के TOGGLE (checkbox hack):
     .nav-toggle:checked ~ .nav-links { max-height: 400px; }   -> transition के साथ खुलता है
     .nav-toggle:checked + .hamburger span { ... }             -> bars X बन जाते हैं
   <label for="nav-toggle"> पर click से छुपा checkbox toggle होता है।
4. DESKTOP (@media (min-width: 768px)):
     .hamburger { display: none }
     .nav-links { display: flex; max-height: none; overflow: visible }
5. STICKY HEADER: position: sticky; top: 0; z-index: 100।
6. ACCESSIBILITY: skip link, nav पर aria-label, aria-current="page", :focus-visible, reduced-motion।
7. max-height क्यों: height:auto पर transition नहीं होता; बड़ी max-height का trick पुराना और चलता है।
```

---

## 🟡 Real World Example
**Amazon, Flipkart and Swiggy mobile web** show the logo plus a menu icon; tapping it opens a list of categories. On desktop the same links sit in a row (Amazon's dark top bar with hover highlight in orange is the model for this exercise).

## 🟡 Real Example Hindi mein
**Amazon, Flipkart और Swiggy की mobile web** पर logo और menu icon दिखता है; tap करने पर categories की list खुलती है। Desktop पर वही links एक row में होते हैं (Amazon की dark top bar और orange hover इस exercise का model है)।

---

## 💻 Live Code Example

Full files: `index.html` and `style.css` in this folder. Key parts:

```html
<!-- Order matters: checkbox, then label, then the list -->
<input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="Toggle menu">
<label for="nav-toggle" class="hamburger" aria-hidden="true"><span></span><span></span><span></span></label>
<ul class="nav-links"> ... </ul>
```

```css
/* Mobile: collapsed list */
.nav-links { width: 100%; max-height: 0; overflow: hidden; transition: max-height .3s ease; }
/* Open when checkbox is checked */
.nav-toggle:checked ~ .nav-links { max-height: 400px; }

/* Desktop: row of links, no hamburger */
@media (min-width: 768px) {
  .hamburger { display: none; }
  .nav-links { display: flex; width: auto; max-height: none; overflow: visible; }
}
```

Note: the checkbox hack hides the menu with `overflow: hidden`, but the links stay in the tab order while closed. For production, prefer a `<button aria-expanded>` + a few lines of JS (shown in the React section) so closed links are not focusable.

---

## 🟠 React/Next.js Connection

```jsx
'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function Navbar() {
  const [open, setOpen] = useState(false);          // menu state
  return (
    <header className="sticky top-0 z-50 bg-slate-800">
      <nav className="mx-auto flex max-w-5xl flex-wrap items-center justify-between px-4" aria-label="Main">
        <Link href="/" className="py-4 text-xl font-bold text-white">ShopEasy</Link>

        <button
          className="md:hidden text-white"   // hidden from 768px up
          aria-expanded={open}
          aria-controls="menu"
          onClick={() => setOpen(o => !o)}
        >
          {open ? 'Close' : 'Menu'}
        </button>

        {/* hidden on mobile unless open; always flex from md up */}
        <ul id="menu" className={`${open ? 'block' : 'hidden'} w-full md:flex md:w-auto md:gap-2`}>
          <li><Link href="/products" className="block px-3 py-3 text-white hover:text-amber-300">Products</Link></li>
          <li><Link href="/deals" className="block px-3 py-3 text-white hover:text-amber-300">Deals</Link></li>
        </ul>
      </nav>
    </header>
  );
}
// Tip: close the menu on route change with usePathname() + useEffect.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you build a hamburger menu without JavaScript?**
A1: Use the checkbox hack: a hidden `<input type="checkbox">`, a `<label for>` as the hamburger, and CSS `:checked ~ .menu` to open it. Drawback: accessibility is weaker (closed links stay focusable and there is no `aria-expanded`), so for production use a `<button>` with `aria-expanded` and a little JS.

**Q2: Why mobile-first, and how do you choose the breakpoint?**
A2: Write simple mobile CSS as default and add features with `min-width` queries. It ships less override code and performs better on phones. Choose the breakpoint where the content breaks (when links stop fitting), not from a device name; 768px is a common starting point.

**Q3: How do you animate the menu opening, since `height: auto` does not transition?**
A3: Transition `max-height` from 0 to a safe large value, or use `grid-template-rows: 0fr` to `1fr` with an inner `overflow: hidden` child (smooth, exact height). Newer: `interpolate-size: allow-keywords` (Chromium) lets `height: auto` transition.

**Q4: How do you keep the navbar fixed at the top?**
A4: `position: sticky; top: 0` keeps it in flow and sticks on scroll (parent must not have `overflow: hidden`). `position: fixed` removes it from flow, so you must add top padding to the body. Always set `z-index`.

**Q5: What accessibility features should a navbar have?**
A5: `<nav aria-label>`, a skip link, `aria-current="page"` for the active link, button with `aria-expanded` and `aria-controls`, visible `:focus-visible`, keyboard support (Esc to close), tap targets at least 44px, and `prefers-reduced-motion`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `display: none` for the closed menu and then wanting a transition
```css
/* WRONG: display cannot animate (without @starting-style) */
.nav-links { display: none; }
/* CORRECT: animate max-height / grid rows / transform, or use JS state */
```

❌ **Mistake 2:** Desktop-first with `max-width` overrides everywhere
```css
/* WRONG: lots of resets for mobile */
/* CORRECT: mobile base styles, then @media (min-width: 768px) { ... } */
```

❌ **Mistake 3:** Forgetting the viewport meta tag
```html
<!-- WRONG: phone renders at 980px width and media queries never match -->
<!-- CORRECT -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Navbar | Navigation bar of links | Navigation की पट्टी |
| Hamburger | Three-line menu icon | तीन लाइन वाला menu icon |
| Breakpoint | Width where layout changes | Layout बदलने की width |
| Checkbox hack | CSS-only toggle using :checked | बिना JS toggle |
| Sticky | Sticks to edge when scrolling | Scroll पर चिपका रहना |
| aria-expanded | Tells screen readers open/closed | खुला/बंद की सूचना |
| Skip link | Jump to main content link | मुख्य content पर कूदने की link |

---

## ⚡ 3-Line Summary
**English:**
1. Mobile-first: collapsed menu by default, then a `min-width: 768px` media query turns links into a flex row.
2. A checkbox + label + sibling selectors gives a no-JS toggle; a button with `aria-expanded` is the accessible production choice.
3. Use `position: sticky`, `max-height` transition, and `:focus-visible` for a polished navbar.

**Hindi:**
1. Mobile-first: default में menu collapsed, फिर `min-width: 768px` media query links को flex row बना देती है।
2. Checkbox + label + sibling selectors से बिना JS toggle होता है; production में `aria-expanded` वाला button बेहतर है।
3. `position: sticky`, `max-height` transition और `:focus-visible` से navbar polished बनता है।

---

## ➡️ Next Topic
**112. Build a Card Component** — Navbar के नीचे का content: image, title, text और button वाला reusable card, grid और hover effects के साथ।
