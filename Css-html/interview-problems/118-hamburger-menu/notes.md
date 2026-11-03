# 118. Hamburger Menu Animation
# हिंदी में: Hamburger Menu Animation (तीन lines से X)

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly, narrow the window below 700px)

---

## 🔵 Simple Definition (English)
A hamburger menu is the three-line icon that opens a hidden navigation on small screens. The animation uses CSS transitions to turn the three lines into an "X" by moving and rotating them with `transform`.

## 🔵 सरल परिभाषा (Hindi)
Hamburger menu तीन lines वाला icon है जो छोटी screens पर छिपा navigation खोलता है। Animation में CSS transition से `transform` द्वारा तीनों lines को खिसकाकर और घुमाकर "X" बनाया जाता है।

---

## 🔴 Problem it Solves
```
PROBLEM: a navbar with 6-8 links does not fit on a 375px phone.
  - wrapping links makes the header 3 rows tall
  - horizontal scroll nav is easy to miss
SOLUTION: hide the links behind one 44px icon; the icon morphs into X
so users see the state (open/closed).
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या: 375px के phone पर 6-8 links वाला navbar फिट नहीं होता।
  - links wrap हों तो header 3 rows ऊँचा हो जाता है
  - horizontal scroll वाला nav आसानी से छूट जाता है
हल: links को एक 44px icon के पीछे छिपाओ; icon X में बदलकर open/closed state दिखाता है।
```

---

## 🟢 How it Works — Step by Step
```
1. <button> holds 3 <span> lines, stacked with flex column + gap: 6px
2. Each line: 26px x 3px, white, transition on transform and opacity
3. Click -> JS toggles .is-open on the button and menu, updates aria-expanded
4. .is-open CSS:
     line 1: translateY(9px) rotate(45deg)    (9px = 3px height + 6px gap)
     line 2: opacity 0
     line 3: translateY(-9px) rotate(-45deg)
   Both outer lines meet at the middle and cross -> X
5. Menu: closed = opacity 0 + translateY(-10px) + visibility hidden;
   open  = visible, slides down
6. @media (min-width: 700px): hide the button, show links inline
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. <button> में 3 <span> lines, flex column + gap: 6px से ऊपर-नीचे
2. हर line 26px x 3px, सफेद, transform और opacity पर transition
3. Click -> JS बटन और menu पर .is-open toggle करता है, aria-expanded update करता है
4. .is-open में:
     line 1: translateY(9px) rotate(45deg)    (9px = 3px height + 6px gap)
     line 2: opacity 0
     line 3: translateY(-9px) rotate(-45deg)
   बाहर वाली दोनों lines बीच में मिलकर क्रॉस बनाती हैं -> X
5. Menu: बंद = opacity 0 + ऊपर खिसका + visibility hidden; खुला = visible, नीचे सरकता है
6. 700px से ऊपर: बटन छिपाओ, links सीधे दिखाओ
```

---

## 🟡 Real World Example
**Zomato, Swiggy, Amazon mobile web:** the three-line icon opens a drawer. **Instagram web (narrow window)** switches to icons. **Gmail** has the hamburger on the top-left to toggle the sidebar. Most use a transform-based animation (3 lines to X or arrow).

## 🟡 Real Example Hindi mein
**Zomato, Swiggy, Amazon mobile web:** तीन lines वाला icon drawer खोलता है। **Gmail** में ऊपर बाईं तरफ hamburger sidebar toggle करता है। ज़्यादातर sites में transform वाला animation (3 lines से X या तीर) होता है।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css). Core:

```html
<button class="burger" id="burger" aria-label="Toggle menu" aria-expanded="false">
  <span class="burger__line"></span>
  <span class="burger__line"></span>
  <span class="burger__line"></span>
</button>
```

```css
.burger__line { display:block; width:26px; height:3px; background:#fff; transition: transform .3s, opacity .2s; }
/* open -> X */
.burger.is-open .burger__line:nth-child(1) { transform: translateY(9px) rotate(45deg); }
.burger.is-open .burger__line:nth-child(2) { opacity: 0; }
.burger.is-open .burger__line:nth-child(3) { transform: translateY(-9px) rotate(-45deg); }
```

```js
burger.addEventListener('click', () => {
  const open = burger.classList.toggle('is-open');   // animate icon
  menu.classList.toggle('is-open', open);            // show/hide menu
  burger.setAttribute('aria-expanded', String(open)); // a11y
});
```

---

## 🟠 React/Next.js Connection
```jsx
'use client';
import { useState } from 'react';

export default function Navbar() {
  const [open, setOpen] = useState(false);   // single source of truth

  return (
    <header className="relative flex h-[60px] items-center justify-between bg-red-700 px-4 text-white">
      <a href="/">Brand</a>

      <button
        className="md:hidden"
        aria-label="Toggle menu"
        aria-expanded={open}
        onClick={() => setOpen(o => !o)}
      >
        {/* Tailwind: conditional classes drive the same transform animation */}
        <span className={`block h-[3px] w-6 bg-white transition ${open ? 'translate-y-[9px] rotate-45' : ''}`} />
        <span className={`my-1.5 block h-[3px] w-6 bg-white transition ${open ? 'opacity-0' : ''}`} />
        <span className={`block h-[3px] w-6 bg-white transition ${open ? '-translate-y-[9px] -rotate-45' : ''}`} />
      </button>

      <nav className={`absolute inset-x-0 top-full bg-white text-black md:static md:flex ${open ? 'block' : 'hidden md:flex'}`}>
        ...
      </nav>
    </header>
  );
}
// Also close the menu on route change: useEffect(() => setOpen(false), [pathname]) (usePathname).
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you animate a hamburger icon into an X?**
A1: Three lines (spans or `::before/::after`); on open, rotate the top by 45deg and the bottom by -45deg after translating them to the middle, and fade the middle one.

**Q2: Why animate `transform` and `opacity` only?**
A2: They run on the compositor/GPU and do not trigger layout or paint of siblings, so animation stays at 60fps. Animating `top`, `height` or `margin` triggers layout.

**Q3: How do you make it accessible?**
A3: Use a real `<button>`, an `aria-label`, `aria-expanded` that matches the state, `aria-controls` pointing at the menu, a visible focus ring, and close on Esc. Hide a closed menu with `visibility:hidden`/`display:none` so it is not tabbable.

**Q4: Why `visibility: hidden` on the closed menu instead of just opacity 0?**
A4: With opacity 0 the links are still focusable and clickable. `visibility: hidden` removes them from interaction and from the accessibility tree, and it can still transition.

**Q5: CSS-only version?**
A5: Use a hidden checkbox plus label, with `input:checked ~ .menu` and `:checked + label .line` selectors. Works without JS but is weaker for accessibility; `:has()` can also react to state.

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** Using a `<div>` as the button.
✅ **Correct way:** A `<button type="button">` with `aria-label`.

❌ **Mistake 2:** Wrong translate distance, so the X is misaligned.
✅ **Correct way:** Distance = line height + gap (3px + 6px = 9px).

❌ **Mistake 3:** Tap target of 26px.
✅ **Correct way:** Button at least 44x44px.

❌ **Mistake 4:** `aria-expanded` never updated.
✅ **Correct way:** Update it whenever the state changes.

❌ **Mistake 5:** Menu stays open after navigating to another route.
✅ **Correct way:** Close it on route change.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hamburger | 3-line menu icon | तीन lines का menu icon |
| `transform` | Move/rotate/scale without layout | खिसकाना/घुमाना |
| `transition` | Smooth change between states | धीरे-धीरे बदलाव |
| `aria-expanded` | Tells open/closed state | खुला/बंद की सूचना |
| Touch target | Tappable area (44px min) | उँगली से दबने का क्षेत्र |
| Compositor | GPU layer handling transforms | GPU वाली layer |

---

## ⚡ 3-Line Summary
**English:**
1. Three spans in a button; on `.is-open` translate the outer two and rotate them +/-45deg, fade the middle.
2. Animate only `transform` and `opacity`, and keep `aria-expanded` in sync.
3. In React use one `open` state with Tailwind conditional classes; hide the icon at `md:`.

**Hindi:**
1. Button में तीन spans; `.is-open` पर बाहर वाली दोनों को खिसकाकर +/-45deg घुमाओ, बीच वाली fade करो।
2. सिर्फ `transform` और `opacity` animate करो, और `aria-expanded` sync रखो।
3. React में एक `open` state और Tailwind conditional classes; `md:` पर icon छिपाओ।

---

## ➡️ Next Topic
**119. CSS Loading Spinner** — `@keyframes` से घूमने वाला spinner और skeleton loader।
