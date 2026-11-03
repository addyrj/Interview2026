# 79. CSS Animations (@keyframes)
# हिंदी में: CSS Animations — Multi-step और Looping Motion

---

## 🔵 Simple Definition (English)
A CSS animation moves an element through a sequence of styles defined in an `@keyframes` rule. You attach it with the `animation` property. Unlike a transition it needs no trigger, can have many steps, can loop forever, reverse, and pause.

## 🔵 सरल परिभाषा (Hindi)
CSS animation में आप `@keyframes` में styles का एक sequence लिखते हो, और `animation` property से उसे element पर लगाते हो। Transition से अलग, इसे trigger नहीं चाहिए, इसमें कई steps हो सकते हैं, ये हमेशा loop हो सकता है, उल्टा चल सकता है और pause हो सकता है।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Loading spinners = animated GIFs (heavy, blurry on retina, cannot recolour)
  - Complex motion = JS timers or Flash
  - Transitions only do A -> B, no loops, no mid-steps

AFTER:
  @keyframes spin { to { transform: rotate(360deg); } }
  .loader { animation: spin 1s linear infinite; }
  /* Vector, tiny, themeable, GPU-accelerated */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Loader = GIF (भारी, retina पर blur, colour नहीं बदल सकते)
  - Complex motion = JS timers या Flash
  - Transition सिर्फ A से B, loop या बीच के steps नहीं

अब:
  @keyframes से कई steps, `infinite` से loop, सब CSS में, हल्का और themeable।
```

---

## 🟢 How it Works — Step by Step

```
STEP 1: DEFINE the keyframes (the "script" of the animation)
  @keyframes pulse {
    0%   { transform: scale(1);   opacity: 1; }
    50%  { transform: scale(1.2); opacity: 0.6; }
    100% { transform: scale(1);   opacity: 1; }
  }
  from = 0%, to = 100%. If you skip 0% or 100%, the browser uses the element's current style.

STEP 2: ATTACH with `animation`
  animation: pulse 1.5s ease-in-out 0s infinite alternate both;

  The 8 sub-properties:
  animation-name             pulse
  animation-duration         1.5s (required)
  animation-timing-function  ease-in-out (applies PER keyframe step, not whole animation)
  animation-delay            0s (negative delay starts mid-way)
  animation-iteration-count  1 | 3 | infinite
  animation-direction        normal | reverse | alternate | alternate-reverse
  animation-fill-mode        none | forwards (keep end state) | backwards (apply 0% during delay) | both
  animation-play-state       running | paused (use with :hover or JS)

STEP 3: BROWSER runs it automatically on load/when class is added
  Restart an animation by removing and re-adding the class (force reflow in JS).

PERFORMANCE:
  Animate transform and opacity (compositor). Avoid top/left/width/height.
  `will-change: transform` hints the browser but use sparingly.

EVENTS: animationstart, animationiteration, animationend.

ACCESSIBILITY:
  @media (prefers-reduced-motion: reduce) { .loader { animation: none; } }
  Avoid flashing more than 3 times per second (WCAG seizure rule).

NEWER: scroll-driven animations (animation-timeline: scroll()/view()) run keyframes off scroll position.
  Support: Chrome 115+, Safari 26+, Firefox behind flag at time of writing. Use as progressive enhancement.
```

## 🟢 कैसे काम करता है? (Hindi)

```
STEP 1: @keyframes में animation की "script" लिखो
  0% पर क्या style, 50% पर क्या, 100% पर क्या। from = 0%, to = 100%।

STEP 2: `animation` property से लगाओ
  animation: pulse 1.5s ease-in-out 0s infinite alternate both;

  - animation-name: keyframes का नाम
  - animation-duration: कितना लंबा (ज़रूरी)
  - animation-timing-function: हर step के बीच speed curve
  - animation-delay: शुरू होने से पहले इंतज़ार
  - animation-iteration-count: कितनी बार (infinite = हमेशा)
  - animation-direction: normal / reverse / alternate (आगे-पीछे)
  - animation-fill-mode: forwards = अंत की state रुकी रहे
  - animation-play-state: running / paused

STEP 3: Page load पर या class लगते ही अपने आप चलता है।

Performance: transform और opacity animate करो।
Accessibility: prefers-reduced-motion में animation बंद करो।
```

---

## 🟡 Real World Example
**Swiggy / Zomato / LinkedIn skeleton loaders:** When the restaurant list loads, you see grey placeholder cards with a shimmering light band sweeping across. That is a `@keyframes` animation moving a gradient background-position, looped `infinite`. Instagram's story ring rotates a gradient the same way, and Gmail's top progress bar slides continuously while the inbox loads. Zomato's "pull to refresh" spinner is a rotating SVG with `animation: spin 1s linear infinite`.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato / LinkedIn skeleton loaders:** Restaurant list load होते समय grey placeholder cards दिखते हैं जिन पर चमकती हुई patti बार-बार गुज़रती है। ये `@keyframes` है जो gradient का background-position हिलाता है, `infinite` loop में। Instagram की story ring और Gmail की top loading bar भी ऐसे ही चलती हैं। Zomato का refresh spinner एक rotating SVG है: `animation: spin 1s linear infinite`.

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Animations Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 24px; background: #fafafa; }
    h2 { margin: 32px 0 12px; }

    /* 1. SPINNER: rotate forever with constant speed */
    @keyframes spin {
      to { transform: rotate(360deg); }          /* `from` is implicit (current style) */
    }
    .spinner {
      width: 40px; height: 40px;
      border: 4px solid #ddd;
      border-top-color: #ff5a5f;                 /* one coloured side makes the motion visible */
      border-radius: 50%;
      animation: spin 0.9s linear infinite;      /* linear = no easing, smooth loop */
    }

    /* 2. PULSE: multi-step keyframes, alternate direction */
    @keyframes pulse {
      0%   { transform: scale(1);   box-shadow: 0 0 0 0 rgba(255, 90, 95, 0.6); }
      70%  { transform: scale(1.05); box-shadow: 0 0 0 16px rgba(255, 90, 95, 0); }
      100% { transform: scale(1);   box-shadow: 0 0 0 0 rgba(255, 90, 95, 0); }
    }
    .live-btn {
      background: #ff5a5f; color: #fff; border: 0;
      padding: 12px 24px; border-radius: 999px; font-size: 1rem;
      animation: pulse 2s ease-out infinite;
    }

    /* 3. SKELETON SHIMMER: animate background-position of a gradient */
    @keyframes shimmer {
      from { background-position: 200% 0; }
      to   { background-position: -200% 0; }
    }
    .skeleton {
      height: 18px; margin-bottom: 10px; border-radius: 6px;
      background: linear-gradient(90deg, #e5e5e5 25%, #f5f5f5 50%, #e5e5e5 75%);
      background-size: 200% 100%;                /* gradient wider than box so it can slide */
      animation: shimmer 1.4s linear infinite;
    }
    .skeleton.short { width: 60%; }

    /* 4. ENTRANCE: fill-mode both keeps start state during delay and end state after */
    @keyframes slide-up {
      from { opacity: 0; transform: translateY(24px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .toast {
      background: #323232; color: #fff; padding: 12px 18px; border-radius: 8px;
      width: fit-content;
      animation: slide-up 0.5s ease-out 0.3s both;   /* delay 0.3s, then stay visible */
    }

    /* 5. BOUNCING DOTS: same keyframes, staggered with negative delays */
    @keyframes bounce {
      0%, 80%, 100% { transform: translateY(0); }
      40%           { transform: translateY(-12px); }
    }
    .dots span {
      display: inline-block; width: 12px; height: 12px; margin-right: 6px;
      background: #1a73e8; border-radius: 50%;
      animation: bounce 1.2s ease-in-out infinite;
    }
    .dots span:nth-child(2) { animation-delay: 0.15s; }
    .dots span:nth-child(3) { animation-delay: 0.30s; }

    /* 6. PAUSE ON HOVER */
    .spinner.pausable:hover { animation-play-state: paused; }

    /* 7. ACCESSIBILITY: stop decorative motion for users who ask */
    @media (prefers-reduced-motion: reduce) {
      .spinner, .live-btn, .skeleton, .dots span { animation: none; }
    }
  </style>
</head>
<body>
  <h1>CSS Animations</h1>

  <h2>1. Spinner (hover to pause)</h2>
  <div class="spinner pausable" role="status" aria-label="Loading"></div>

  <h2>2. Pulse button</h2>
  <button class="live-btn">Go Live</button>

  <h2>3. Skeleton shimmer</h2>
  <div class="skeleton"></div>
  <div class="skeleton"></div>
  <div class="skeleton short"></div>

  <h2>4. Toast entrance</h2>
  <div class="toast">Order placed successfully</div>

  <h2>5. Typing dots</h2>
  <div class="dots"><span></span><span></span><span></span></div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Plain CSS animation in a component (Next.js: import './Spinner.css' or CSS Module)
export function Spinner() {
  return <div className="spinner" role="status" aria-label="Loading" />;
}

// 2. Skeleton screen while data loads (very common in Next.js loading.js)
// app/restaurants/loading.js  <- Next.js shows this automatically during Suspense
export default function Loading() {
  return (
    <>
      <div className="skeleton" />
      <div className="skeleton" />
    </>
  );
}

// 3. Tailwind built-ins: animate-spin, animate-pulse, animate-bounce, animate-ping
<div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-rose-500" />
<div className="h-4 w-3/4 animate-pulse rounded bg-gray-200" />   {/* skeleton */}

// 4. Custom keyframes in tailwind.config.js (v3)
// theme: { extend: {
//   keyframes: { 'slide-up': { from: { opacity: 0, transform: 'translateY(24px)' }, to: { opacity: 1, transform: 'none' } } },
//   animation: { 'slide-up': 'slide-up 0.5s ease-out both' } } }
<div className="animate-slide-up">Toast</div>

// 5. Restart an animation in React: change the `key` so the element remounts
<div key={messageId} className="toast">{message}</div>

// 6. For orchestrated, exit, or gesture animations use Framer Motion; CSS keyframes
//    are best for simple loops and loaders.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between CSS transitions and CSS animations?**
A1: Transitions animate from state A to B when a property changes (needs a trigger), with only two endpoints. Animations use `@keyframes` with any number of steps, can start automatically, loop (`infinite`), alternate, delay, pause, and fill. Choose transitions for hover/focus feedback, animations for loaders, attention effects, and multi-step sequences.

**Q2: Explain `animation-fill-mode`.**
A2: It controls what styles apply before and after the animation runs. `none`: element returns to its normal style when done. `forwards`: keeps the last keyframe's styles. `backwards`: applies the first keyframe during the delay. `both`: does both. Without `forwards`, an entrance animation snaps back to the original (often invisible) state at the end.

**Q3: How do you make an animation loop and alternate back and forth?**
A3: `animation-iteration-count: infinite` loops it forever, and `animation-direction: alternate` plays forward then backward each cycle. Example: `animation: pulse 1s ease-in-out infinite alternate`. Note that `alternate` reverses the easing too.

**Q4: How do you keep animations performant and accessible?**
A4: Animate `transform` and `opacity` only, so work stays on the compositor and avoids layout and paint. Use `will-change` sparingly. For accessibility, wrap decorative motion in `@media (prefers-reduced-motion: reduce)` to disable it, avoid rapid flashing (more than 3 flashes per second), and give users a way to pause long-running motion.

**Q5: Where does `animation-timing-function` apply, and how do you make a spinner look smooth?**
A5: The timing function applies between each pair of keyframes, not over the whole animation. With the default `ease`, a rotating spinner would slow at each keyframe boundary. Use `linear` for constant motion (spinners, marquees). For bouncy or natural motion use `ease-in-out` or `cubic-bezier`, and you can override per keyframe: `50% { animation-timing-function: ease-out; ... }`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Typo or mismatch between keyframes name and `animation-name`
```css
/* WRONG: animation silently does nothing */
@keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
.box { animation: fade-in 1s; }     /* name does not match */

/* CORRECT */
.box { animation: fadeIn 1s both; }
```

❌ **Mistake 2:** Entrance animation snaps back at the end
```css
/* WRONG: base style is opacity:0, so after the animation ends the card
   jumps back to invisible */
.card { opacity: 0; animation: fadeIn 0.5s; }

/* CORRECT: keep the final keyframe state */
.card { opacity: 0; animation: fadeIn 0.5s forwards; }
```

❌ **Mistake 3:** Animating layout properties
```css
/* WRONG: janky, runs layout every frame */
@keyframes move { from { left: 0 } to { left: 300px } }

/* CORRECT */
@keyframes move { from { transform: translateX(0) } to { transform: translateX(300px) } }
```

❌ **Mistake 4:** Infinite animations with no reduced-motion fallback
```css
/* CORRECT */
@media (prefers-reduced-motion: reduce) { .loader { animation: none; } }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `@keyframes` | Defines the steps of an animation | Animation के steps की script |
| `animation` | Shorthand to attach keyframes | Keyframes लगाने का shorthand |
| iteration-count | How many times it plays (`infinite`) | कितनी बार चलेगा |
| direction | normal, reverse, alternate | चलने की दिशा |
| fill-mode | Styles before/after running | Animation से पहले/बाद की style |
| play-state | running or paused | चल रहा है या रुका |
| skeleton | Placeholder UI while loading | Loading के समय का placeholder |
| compositor | GPU layer for transform/opacity | GPU वाली layer |

---

## ⚡ 3-Line Summary
**English:**
1. Define steps in `@keyframes`, attach with `animation: name duration timing delay count direction fill-mode`.
2. Unlike transitions, animations need no trigger and can loop, alternate, pause, and have many steps.
3. Animate only `transform`/`opacity`, use `forwards` to keep the end state, and honour `prefers-reduced-motion`.

**Hindi:**
1. `@keyframes` में steps लिखो, `animation: name duration timing delay count direction fill-mode` से लगाओ।
2. Transition से अलग, animation को trigger नहीं चाहिए, loop, alternate, pause और कई steps हो सकते हैं।
3. सिर्फ `transform`/`opacity` animate करो, end state रखने के लिए `forwards` use करो, और `prefers-reduced-motion` का सम्मान करो।

---

## ➡️ Next Topic
**80. CSS Transform (translate, rotate, scale, skew)** — Animations में हमने बार-बार `transform` use किया। अब समझते हैं कि वो असल में क्या-क्या कर सकता है।
