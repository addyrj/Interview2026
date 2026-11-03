# 117. Sticky Header
# हिंदी में: Sticky Header — Scroll पर ऊपर चिपका रहने वाला Header

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly, then scroll)

---

## 🔵 Simple Definition (English)
A sticky header stays visible at the top of the screen while the user scrolls. In CSS it is done with `position: sticky; top: 0`, which behaves like `relative` until the element reaches the offset, and then like `fixed`.

## 🔵 सरल परिभाषा (Hindi)
Sticky header scroll करते समय screen के ऊपर दिखता रहता है। CSS में यह `position: sticky; top: 0` से होता है, जो offset तक पहुँचने तक `relative` की तरह और उसके बाद `fixed` की तरह काम करता है।

---

## 🔴 Problem it Solves
```
BEFORE:
  - header scrolls away; the user must scroll all the way up to navigate
  - position:fixed removes the header from the flow -> content hides under it,
    so you add body { padding-top: 64px } and keep it in sync
  - JS scroll listeners to toggle "fixed" (janky)

NOW: position: sticky = one CSS line, stays in the flow.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - header scroll के साथ ऊपर चला जाता था; navigate करने के लिए वापस ऊपर जाना पड़ता
  - position:fixed flow से बाहर कर देता है -> content header के नीचे छिप जाता,
    तब body { padding-top: 64px } देना पड़ता
  - "fixed" toggle करने के लिए JS scroll listeners (अटक-अटक कर चलता)

अब: position: sticky = CSS की एक line, element flow में ही रहता है।
```

---

## 🟢 How it Works — Step by Step
```
1. .site-header { position: sticky; top: 0; }
   - sticks when its top edge would go above 0 of the scroll container
2. It sticks only inside its PARENT: when the parent ends, the header leaves
   (so keep the header a direct child of <body>)
3. z-index: 100 keeps it above scrolling content
4. Semi-transparent background + backdrop-filter gives the frosted look
5. JS toggles .is-scrolled after 10px to add a shadow
   (passive listener keeps scrolling smooth)
6. scroll-padding-top on <html> stops anchor links hiding under the header
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. position: sticky; top: 0 -> जब element का top edge 0 से ऊपर जाने लगे, तब चिपक जाता है
2. यह सिर्फ अपने PARENT के अंदर चिपकता है: parent खत्म तो header भी चला जाता है
   (इसलिए header को <body> का direct child रखो)
3. z-index: 100 उसे scrolling content के ऊपर रखता है
4. Semi-transparent background + backdrop-filter से frosted look
5. 10px scroll के बाद JS .is-scrolled class जोड़कर shadow देता है
   (passive listener से scroll smooth रहता है)
6. <html> पर scroll-padding-top से anchor links header के नीचे नहीं छिपते
```

---

## 🟡 Real World Example
**Amazon / Flipkart:** the search bar header stays at the top as you scroll products. **Swiggy / Zomato:** the category chip bar sticks under the main header. **Instagram web:** the top bar stays. **Gmail:** the toolbar over the mail list stays visible. Blog sites often hide the header on scroll down and show it on scroll up.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart:** products scroll करते समय search bar वाला header ऊपर रहता है। **Swiggy / Zomato:** category chips की bar मुख्य header के नीचे चिपकी रहती है। **Instagram web:** ऊपर की bar टिकी रहती है। **Gmail:** mail list के ऊपर की toolbar दिखती रहती है।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css).

```html
<header class="site-header" id="header">Logo + Nav</header>
```

```css
.site-header {
  position: sticky;  /* stick on scroll */
  top: 0;            /* REQUIRED: without an offset sticky does nothing */
  z-index: 100;      /* above content */
  background: #fff;
}
.site-header.is-scrolled { box-shadow: 0 4px 14px rgba(0,0,0,.12); }
html { scroll-padding-top: 72px; } /* anchor links clear the header */
```

```js
// Add shadow after scrolling
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
  header.classList.toggle('is-scrolled', window.scrollY > 10);
}, { passive: true });
```

---

## 🟠 React/Next.js Connection
```jsx
'use client';
import { useEffect, useState } from 'react';

export default function Header() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll); // cleanup
  }, []);

  // Tailwind: sticky top-0 z-50
  return (
    <header className={`sticky top-0 z-50 bg-white/90 backdrop-blur transition-shadow ${scrolled ? 'shadow-md' : ''}`}>
      ...
    </header>
  );
}
// In Next.js App Router, put <Header/> in app/layout.tsx as a direct child of <body>.
// Avoid overflow:hidden on ancestors: it breaks sticky.
```

---

## ⚫ Interview Questions + Answers

**Q1: `fixed` vs `sticky`?**
A1: `fixed` is removed from the flow and positioned against the viewport always. `sticky` stays in the flow and only becomes fixed-like after crossing its `top` offset, limited to its parent.

**Q2: Why is my `position: sticky` not working?**
A2: Common causes: no `top`/`bottom` offset; an ancestor has `overflow: hidden/auto/scroll`; the parent is as tall as the sticky element (no room to stick); a flex/grid child stretched by `align-items: stretch` (use `align-self: start`).

**Q3: How do you stop anchor links from hiding under a sticky header?**
A3: `scroll-padding-top` on `html` (or `scroll-margin-top` on targets) equal to the header height.

**Q4: How would you hide the header on scroll down and show it on scroll up?**
A4: Track the last `scrollY` in a scroll handler; if it increased, add a class with `transform: translateY(-100%)`, otherwise remove it. Transform is cheap (compositor only).

**Q5: Why use a passive scroll listener, or IntersectionObserver?**
A5: `{ passive: true }` promises not to call `preventDefault`, so the browser can scroll without waiting on JS. IntersectionObserver with a sentinel element avoids scroll events entirely.

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** `position: sticky` without `top`.
✅ **Correct way:** Always add `top: 0`.

❌ **Mistake 2:** `overflow-x: hidden` on `body` wrapper or ancestor.
✅ **Correct way:** Use `overflow-x: clip` or move the overflow rule to a non-ancestor.

❌ **Mistake 3:** Using `fixed` and forgetting to offset the content.
✅ **Correct way:** Prefer `sticky`, which keeps its space.

❌ **Mistake 4:** Animating `height` on scroll (causes layout thrash).
✅ **Correct way:** Animate `transform`/`box-shadow`/`opacity`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `position: sticky` | Relative until offset, then fixed-like | शर्त के बाद चिपकने वाला |
| Scroll container | Nearest scrolling ancestor | Scroll होने वाला parent |
| `scroll-padding-top` | Offset for anchor scrolling | Anchor scroll की दूरी |
| `backdrop-filter` | Blurs what is behind | पीछे का blur |
| Passive listener | Never calls preventDefault | Scroll न रोकने का वादा |
| `z-index` | Stacking order | ऊपर-नीचे का क्रम |

---

## ⚡ 3-Line Summary
**English:**
1. `position: sticky; top: 0` keeps a header in view while staying in the normal flow.
2. It fails if an ancestor has `overflow` set or if no `top` is given.
3. Add shadow with a scroll class (React: useState + useEffect) and `scroll-padding-top` for anchors.

**Hindi:**
1. `position: sticky; top: 0` header को दिखता रखता है और flow में भी रहता है।
2. Ancestor पर `overflow` हो या `top` न दिया हो तो काम नहीं करता।
3. Shadow के लिए scroll class (React: useState + useEffect) और anchors के लिए `scroll-padding-top` लगाओ।

---

## ➡️ Next Topic
**118. Hamburger Menu Animation** — mobile menu icon जो तीन lines से X में बदलता है।
