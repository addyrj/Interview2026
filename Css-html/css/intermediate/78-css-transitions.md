# 78. CSS Transitions
# हिंदी में: CSS Transitions — बदलाव को Smooth बनाना

---

## 🔵 Simple Definition (English)
A CSS transition animates a property from its old value to its new value over a set time, instead of changing instantly. You write `transition: property duration timing-function delay;` on the element, and the browser tweens between states when something (hover, focus, class change) changes the value.

## 🔵 सरल परिभाषा (Hindi)
CSS transition किसी property को पुरानी value से नई value तक कुछ समय में धीरे-धीरे बदलता है, एकदम से नहीं। Element पर `transition: property duration timing-function delay;` लिखते हो, और जब hover, focus या class बदलने से value बदलती है, तो browser बीच के steps खुद भर देता है।

---

## 🔴 Problem it Solves
```
BEFORE TRANSITIONS:
  - Hover on a button: colour jumps instantly, feels harsh and cheap
  - Smooth effects needed jQuery .animate() or setInterval loops
  - JS animation runs on the main thread, can lag

AFTER:
  .btn { background: #ff5a5f; transition: background 0.3s ease; }
  .btn:hover { background: #e0484d; }
  /* Declarative, 1 line, browser optimizes it, can run on the compositor */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Button पर hover करो तो colour एकदम बदलता था, rough लगता था
  - Smooth effect के लिए jQuery .animate() या setInterval लिखना पड़ता था
  - JS animation main thread पर चलता है, lag कर सकता है

अब:
  सिर्फ एक line `transition` और browser बाकी सब खुद संभालता है।
```

---

## 🟢 How it Works — Step by Step

```
THE 4 SUB-PROPERTIES (shorthand: transition: all-in-one):

  transition-property        which property: color, transform, opacity, all
  transition-duration        how long: 0.3s or 300ms (REQUIRED, default is 0s = no effect)
  transition-timing-function speed curve: ease, linear, ease-in, ease-out, ease-in-out,
                             cubic-bezier(0.4, 0, 0.2, 1), steps(4)
  transition-delay           wait before starting: 0.1s

SHORTHAND:
  transition: transform 0.3s ease-out 0s;
  Multiple:   transition: transform 0.3s, opacity 0.3s;

HOW THE BROWSER DECIDES:
  1. Element has start state (e.g. opacity: 1)
  2. A change happens (:hover, class added by JS, media query)
  3. Browser sees a transition is defined for that property
  4. It interpolates frame-by-frame (about 60 times/sec) from old to new
  5. Reverse change plays the transition back
  NOTE: transition is read from the DESTINATION state.
        Put `transition` on the base rule if you want both in and out animated.
        Put it only on :hover if you want only the hover-in animated.

WHAT CAN BE ANIMATED:
  Only properties with a computable midpoint: colours, lengths, percentages, transform, opacity,
  box-shadow, filter.
  Cannot: display (none to block), auto values (height: auto), visibility is a discrete exception
  (it flips at the end/start).
  New (limited support): transition-behavior: allow-discrete and @starting-style
  allow display/overlay transitions. Chrome 117+/Safari 17.4+/Firefox 129+.

PERFORMANCE:
  Cheap (compositor, GPU):   transform, opacity
  Expensive (layout/paint):  width, height, margin, top, left, box-shadow
  Always prefer transform + opacity.

EVENTS: transitionend fires per property when done (JS).

ACCESSIBILITY: respect users who get motion sick:
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
```

## 🟢 कैसे काम करता है? (Hindi)

```
4 पार्ट्स:
  transition-property        कौन सी property (color, transform, opacity, all)
  transition-duration        कितना समय (0.3s) ← ज़रूरी, default 0s है यानी कोई effect नहीं
  transition-timing-function speed का curve (ease, linear, ease-in-out, cubic-bezier)
  transition-delay           शुरू होने से पहले इंतज़ार

STEPS:
  1. Element की शुरुआती state है (जैसे opacity: 1)
  2. कुछ बदलता है (:hover, JS से class, media query)
  3. Browser देखता है कि इस property पर transition लिखा है
  4. पुरानी से नई value तक हर frame में थोड़ा-थोड़ा बदलता है
  5. वापस बदलाव हो तो उल्टा animate होता है

याद रखो: transition को base rule में लिखो तो hover-in और hover-out दोनों smooth होते हैं।
सिर्फ :hover में लिखो तो सिर्फ अंदर जाते समय animate होगा।

Performance: transform और opacity सबसे सस्ते हैं। width/height/margin animate करने से layout बार-बार चलता है।
`display: none` से `block` और `height: auto` animate नहीं होते।
```

---

## 🟡 Real World Example
**Amazon product card / Instagram like button:** On Amazon, hovering a product card lifts it slightly with a soft shadow (`transform: translateY(-4px)` + `box-shadow`) over 200ms. On Instagram web the heart icon scales up and changes colour when liked, a transition on `transform` and `color`. Gmail's side menu items also fade their background on hover over about 150ms. None of these use JavaScript for the effect, only CSS transitions triggered by `:hover` or a class toggle.

## 🟡 Real Example Hindi mein
**Amazon product card / Instagram like button:** Amazon पर product card पर hover करने से वो हल्का ऊपर उठता है और shadow आती है (`transform: translateY(-4px)` + `box-shadow`), लगभग 200ms में। Instagram web में heart icon like करने पर बड़ा होता है और colour बदलता है। Gmail के side menu में hover पर background धीरे से fade होता है। इनमें effect के लिए JavaScript नहीं, सिर्फ CSS transition है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Transitions Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f4f4f4; padding: 24px; }
    h2 { margin-top: 32px; }

    /* 1. BUTTON: colour change with smooth feel */
    .btn {
      background: #ff5a5f;
      color: #fff;
      border: 0;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      /* Put transition on the BASE rule so hover-in and hover-out are both smooth */
      transition: background-color 0.25s ease, transform 0.15s ease;
    }
    .btn:hover  { background: #e0484d; }
    .btn:active { transform: scale(0.96); }          /* press feedback */
    .btn:focus-visible { outline: 3px solid #1a73e8; outline-offset: 2px; }

    /* 2. CARD LIFT: transform + box-shadow (shadow is paint-heavy; keep it small) */
    .card {
      width: 260px;
      background: #fff;
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                  box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card:hover {
      transform: translateY(-6px);                  /* lift up */
      box-shadow: 0 12px 24px rgba(0,0,0,0.18);
    }

    /* 3. DELAY + STAGGER: three dots appear one after another */
    .dots span {
      display: inline-block;
      width: 14px; height: 14px;
      margin-right: 6px;
      background: #1a73e8;
      border-radius: 50%;
      opacity: 0.2;
      transition: opacity 0.4s ease;
    }
    .dots:hover span { opacity: 1; }
    .dots:hover span:nth-child(2) { transition-delay: 0.15s; }
    .dots:hover span:nth-child(3) { transition-delay: 0.3s; }

    /* 4. HEIGHT AUTO TRICK: animate max-height instead (height:auto cannot animate) */
    .panel {
      max-height: 0;
      overflow: hidden;
      background: #fff;
      transition: max-height 0.35s ease;
    }
    .panel.open { max-height: 200px; }               /* must be >= real content height */
    .panel p { margin: 12px; }

    /* 5. Respect reduced-motion users */
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { transition-duration: 0.01ms !important; }
    }
  </style>
</head>
<body>
  <h1>CSS Transitions</h1>

  <h2>1. Button (hover, press)</h2>
  <button class="btn">Add to Cart</button>

  <h2>2. Card lift (hover)</h2>
  <div class="card"><h3>Echo Dot</h3><p>Rs. 4,499</p></div>

  <h2>3. Staggered dots (hover the dots)</h2>
  <div class="dots"><span></span><span></span><span></span></div>

  <h2>4. Accordion panel (click)</h2>
  <button class="btn" id="toggle">Toggle details</button>
  <div class="panel" id="panel"><p>Free delivery on orders above Rs. 499.</p></div>

  <script>
    // Class toggle triggers the transition
    document.getElementById('toggle').addEventListener('click', () => {
      document.getElementById('panel').classList.toggle('open');
    });
  </script>
</body>
</html>
```

```css
/* Timing function cheat sheet */
.ease        { transition-timing-function: ease; }          /* slow-fast-slow (default) */
.linear      { transition-timing-function: linear; }        /* constant speed */
.ease-in     { transition-timing-function: ease-in; }       /* slow start */
.ease-out    { transition-timing-function: ease-out; }      /* slow end (best for UI entering) */
.steps       { transition-timing-function: steps(4, end); } /* 4 jumps, sprite-like */
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. State -> className -> CSS transition does the animation
function Accordion({ children }) {
  const [open, setOpen] = React.useState(false);
  return (
    <>
      <button onClick={() => setOpen(o => !o)}>Details</button>
      <div className={`panel ${open ? 'open' : ''}`}>{children}</div>
    </>
  );
}

// 2. Unmounting problem: when React removes an element, it vanishes instantly,
//    so no exit transition. Solutions: keep it mounted and toggle a class,
//    or use react-transition-group / Framer Motion (AnimatePresence).
import { CSSTransition } from 'react-transition-group';
<CSSTransition in={show} timeout={300} classNames="fade" unmountOnExit>
  <Modal />
</CSSTransition>
/* .fade-enter { opacity: 0 } .fade-enter-active { opacity: 1; transition: opacity 300ms } */

// 3. Tailwind has transition utilities
<button className="bg-rose-500 hover:bg-rose-600 transition-colors duration-300 ease-in-out
                   hover:-translate-y-1 transition-transform motion-reduce:transition-none">
  Order Now
</button>
// transition / transition-colors / transition-transform, duration-150..1000,
// ease-in / ease-out / ease-in-out, delay-100, motion-reduce:

// 4. Next.js: page transitions need extra work (App Router has no built-in exit animation).
//    Use Framer Motion or the View Transitions API (Chrome 111+, Safari 18+) for route changes.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a CSS transition and what are its four properties?**
A1: A transition smoothly interpolates a property between two values over time. The four parts are `transition-property` (what), `transition-duration` (how long, required), `transition-timing-function` (speed curve), and `transition-delay` (wait). Shorthand: `transition: opacity 0.3s ease 0.1s`.

**Q2: What is the difference between transition and animation?**
A2: A transition needs a trigger (hover, class change) and only goes from state A to state B (and back). An animation (`@keyframes`) can run automatically, has multiple steps, can loop, alternate, pause, and does not need a trigger. Use transitions for simple state changes, animations for complex or looping motion.

**Q3: Which properties are good to animate for performance, and why?**
A3: `transform` and `opacity`. They can be handled on the compositor (GPU) without triggering layout or paint on the main thread. Animating `width`, `height`, `top`, `left`, or `margin` forces layout every frame, which can drop below 60fps. Use `transform: translate/scale` in place of `top/left/width`.

**Q4: Why does my hover transition work only one way, and where should the `transition` property go?**
A4: The browser uses the transition defined on the element's destination state. If `transition` is only inside `:hover`, the hover-in animates, but un-hover uses the base state (no transition), so it snaps back. Put `transition` on the base selector to animate both directions. You can also deliberately set different values in each state (fast in, slow out).

**Q5: Can you transition `display: none` to `block` or `height: auto`? How do you work around it?**
A5: Classically no: those values are discrete or non-numeric. Workarounds: animate `opacity` plus `visibility`, animate `max-height` to a large number, or use `grid-template-rows: 0fr` to `1fr` (supported in modern browsers). Newer option: `transition-behavior: allow-discrete` with `@starting-style` (Chrome 117+, Safari 17.4+, Firefox 129+). Always check support before relying on it.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `transition: all`
```css
/* WRONG: animates everything, including layout properties; unexpected side effects */
.card { transition: all 0.3s; }

/* CORRECT: list exactly what should animate */
.card { transition: transform 0.3s, box-shadow 0.3s; }
```

❌ **Mistake 2:** Forgetting the duration
```css
/* WRONG: default duration is 0s, so nothing animates */
.btn { transition: background-color; }

/* CORRECT */
.btn { transition: background-color 0.3s; }
```

❌ **Mistake 3:** Animating `width`/`height`/`top`/`left` for movement
```css
/* WRONG: triggers layout on every frame */
.menu { left: -300px; transition: left 0.3s; }  .menu.open { left: 0; }

/* CORRECT: transform is GPU-friendly */
.menu { transform: translateX(-100%); transition: transform 0.3s; }
.menu.open { transform: translateX(0); }
```

❌ **Mistake 4:** Ignoring reduced-motion preferences
```css
/* CORRECT: provide an opt-out */
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| transition | Smooth change between two states | दो states के बीच smooth बदलाव |
| duration | Time the transition takes | कितनी देर लगेगी |
| timing-function | Speed curve (ease, linear, cubic-bezier) | Speed का curve |
| delay | Wait before start | शुरू होने से पहले का इंतज़ार |
| compositor | GPU layer that handles transform/opacity | GPU वाली layer |
| `transitionend` | JS event when transition finishes | Transition खत्म होने का event |
| `cubic-bezier()` | Custom easing curve | अपना बनाया easing curve |
| `prefers-reduced-motion` | User setting to reduce animation | कम animation चाहने की setting |

---

## ⚡ 3-Line Summary
**English:**
1. `transition: property duration timing delay` animates a property between two states when a trigger (hover, class, media query) changes it.
2. Put it on the base selector for two-way smoothness; prefer `transform` and `opacity`, avoid `transition: all`.
3. It cannot animate `display` or `height: auto` classically; use max-height, grid rows 0fr/1fr, or `@starting-style` where supported.

**Hindi:**
1. `transition: property duration timing delay` दो states के बीच बदलाव को smooth करता है, trigger जैसे hover, class या media query से।
2. Base selector में लिखो ताकि आना-जाना दोनों smooth हों; `transform` और `opacity` use करो, `transition: all` से बचो।
3. `display` और `height: auto` classically animate नहीं होते; max-height, grid rows 0fr/1fr या `@starting-style` (जहाँ support हो) use करो।

---

## ➡️ Next Topic
**79. CSS Animations (@keyframes)** — Transition सिर्फ A से B जाता है। जब multi-step, looping या automatic motion चाहिए (loader, skeleton, pulse), तब keyframes चाहिए।
