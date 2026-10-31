---

# Q229. Smooth Scroll
# Category: DOM Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
Make anchor links (`<a href="#section">`) scroll smoothly to their target. Also add a "Back to top" button that scrolls up smoothly. Respect users who prefer reduced motion.

---

## 💡 Quick Concept (2 lines only)
`element.scrollIntoView({ behavior: 'smooth' })` or `window.scrollTo({ top: 0, behavior: 'smooth' })` animates scrolling natively.
हिंदी: `behavior: 'smooth'` देने से browser खुद animation के साथ scroll करता है।

---

## ✅ Answer / Solution

```html
<nav>
  <a href="#about">About</a>
  <a href="#contact">Contact</a>
</nav>
<section id="about" style="height:800px">About</section>
<section id="contact" style="height:800px">Contact</section>
<button id="topBtn">Back to top</button>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Check user motion preference
// Step 2: Intercept clicks on in-page anchors
// Step 3: scrollIntoView smoothly; wire the top button

const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; // motion pref
const behavior = reduce ? 'auto' : 'smooth';             // pick behavior

document.querySelectorAll('a[href^="#"]').forEach((link) => { // all in-page links
  link.addEventListener('click', (e) => {                // on click
    const id = link.getAttribute('href').slice(1);       // "about"
    const target = document.getElementById(id);          // target section
    if (!target) return;                                 // no match -> default behavior
    e.preventDefault();                                  // stop instant jump
    target.scrollIntoView({ behavior, block: 'start' }); // animate scroll
    history.pushState(null, '', '#' + id);               // keep URL in sync
  });
});

document.getElementById('topBtn').addEventListener('click', () => { // top button
  window.scrollTo({ top: 0, behavior });                 // smooth scroll to top
});

// ============================================
// TEST CASES
// ============================================

// Test 1: click "Contact" link -> Expected: page animates to #contact, URL ends with #contact
// Test 2: click "Back to top"  -> Expected: window.scrollY gradually becomes 0
// Test 3: window.scrollTo({ top: 500, behavior: 'smooth' }) in console
//         -> Expected: animated scroll to 500px
```

---

## 🔍 Why This Works (3 lines max)
The browser handles the animation; we only prevent the default jump and request smooth behavior. `matchMedia` honours accessibility settings. `pushState` keeps the URL shareable.
हिंदी: Default jump रोककर smooth scroll माँगते हैं, और reduced-motion वालों के लिए instant रखते हैं।

---

## ⚡ Alternative Solution
```css
/* Pure CSS: no JS needed */
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting preventDefault — default jump happens, smooth is skipped
link.addEventListener('click', () => target.scrollIntoView({ behavior: 'smooth' }));

// ✅ Correct: call e.preventDefault() first (see above) or use CSS scroll-behavior
```

---

## 🎯 Interview Tip (1 line)
Say: "CSS scroll-behavior is simplest; JS gives control (offset, callbacks), and I'd respect prefers-reduced-motion for accessibility."

---

## 🔗 Related Questions
→ Q226 (infinite scroll) | Q284 (requestAnimationFrame) | Q189 (SPA router)
