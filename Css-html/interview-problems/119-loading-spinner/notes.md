# 119. CSS Loading Spinner
# हिंदी में: CSS Loading Spinner

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly)

---

## 🔵 Simple Definition (English)
A loading spinner is a small animation that tells users something is in progress. In CSS it is a bordered circle where one side is coloured, rotated forever with `@keyframes` and `animation: spin 1s linear infinite`.

## 🔵 सरल परिभाषा (Hindi)
Loading spinner एक छोटा animation है जो बताता है कि कुछ काम चल रहा है। CSS में यह गोल border वाला box होता है जिसकी एक तरफ रंगीन होती है, और उसे `@keyframes` + `animation: spin 1s linear infinite` से लगातार घुमाया जाता है।

---

## 🔴 Problem it Solves
```
BEFORE: animated GIFs for spinners -> extra download, fixed colour/size, blurry
        no feedback at all -> users click twice or leave

NOW: 5 lines of CSS, any size/colour, crisp, no network request, shows the app is alive.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले: spinner के लिए animated GIF -> extra download, रंग/size fixed, धुंधला
      कोई feedback नहीं -> user दो बार click करता या चला जाता

अब: 5 lines CSS, कोई भी size/रंग, साफ़, network request नहीं, user को दिखता है कि app चल रहा है।
```

---

## 🟢 How it Works — Step by Step
```
1. Draw a circle:   width/height 48px; border-radius: 50%
2. Border track:    border: 5px solid light-grey
3. Highlight arc:   border-top-color: orange  (only one side coloured)
4. @keyframes spin { to { transform: rotate(360deg) } }
5. animation: spin .8s linear infinite
     linear   -> constant speed (ease would pause at each turn)
     infinite -> repeat forever
6. Dots: 3 elements, same bounce keyframes, animation-delay .15s apart (stagger)
7. Skeleton: gradient wider than the box (background-size 200%) slid with
   background-position -> shimmer
8. role="status" + hidden text tell screen readers "Loading..."
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. गोला बनाओ: width/height 48px; border-radius: 50%
2. Border track: border: 5px solid हल्का grey
3. Highlight arc: border-top-color: orange (सिर्फ एक side रंगीन)
4. @keyframes spin { to { transform: rotate(360deg) } }
5. animation: spin .8s linear infinite
     linear -> एक सी speed; infinite -> हमेशा दोहराओ
6. Dots: 3 elements, वही bounce keyframes, animation-delay .15s के अंतर पर
7. Skeleton: gradient को box से चौड़ा रखकर background-position से खिसकाओ -> shimmer
8. role="status" + छिपा text screen reader को "Loading..." बताता है
```

---

## 🟡 Real World Example
**Swiggy / Zomato:** the "Placing your order" button spinner, and skeleton restaurant cards while the list loads. **Instagram / LinkedIn:** shimmer skeleton feed. **Gmail:** the loading bar and spinner on first open. **Amazon:** spinner on "Add to cart".

## 🟡 Real Example Hindi mein
**Swiggy / Zomato:** "Order place हो रहा है" button में spinner, और list load होते समय skeleton restaurant cards। **Instagram / LinkedIn:** shimmer skeleton feed। **Gmail:** पहली बार खुलते समय loading bar और spinner। **Amazon:** "Add to cart" पर spinner।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css).

```html
<div class="spinner" role="status"><span class="sr-only">Loading...</span></div>
```

```css
.spinner {
  width: 48px; height: 48px;
  border: 5px solid #dfe3e8;        /* track */
  border-top-color: #e65100;        /* moving arc */
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Skeleton shimmer */
.sk {
  background: linear-gradient(90deg, #e6e8eb 25%, #f5f6f7 50%, #e6e8eb 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
@keyframes shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }
```

---

## 🟠 React/Next.js Connection
```jsx
// Tailwind ships animate-spin (keyframes rotate 360deg, 1s linear infinite)
export function Spinner() {
  return (
    <div role="status" className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-orange-600">
      <span className="sr-only">Loading...</span>
    </div>
  );
}

// Button loading state
<button disabled={pending} className="flex items-center gap-2 rounded bg-orange-600 px-4 py-2 text-white">
  {pending && <Spinner />} Place order
</button>

// Skeleton: Tailwind animate-pulse
<div className="h-4 w-3/5 animate-pulse rounded bg-gray-200" />

// Next.js App Router: app/loading.tsx is shown automatically (Suspense boundary)
// while a route segment's data loads.
export default function Loading() { return <Spinner />; }
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make a CSS spinner?**
A1: A circle with a light border and one coloured side (`border-top-color`), then `@keyframes spin { to { transform: rotate(360deg) } }` with `animation: spin 1s linear infinite`.

**Q2: Why `linear` timing for a spinner?**
A2: Default `ease` slows at start and end of each loop, which looks like a stutter. `linear` keeps constant speed so loops are seamless.

**Q3: Why animate `transform` and not `left` or `border-width`?**
A3: `transform` and `opacity` are handled by the compositor without layout or paint, so animation stays smooth even when the main thread is busy.

**Q4: How do you make a spinner accessible?**
A4: `role="status"` (or `aria-live="polite"`) with visually hidden text "Loading...", and respect `prefers-reduced-motion`. For busy regions set `aria-busy="true"`.

**Q5: Spinner vs skeleton?**
A5: Spinner for short, indeterminate waits (under ~1-2s) or button actions. Skeletons for page/content loading because they show layout and reduce perceived wait and layout shift.

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** Spinner without a fixed size, so the layout jumps when it appears.
✅ **Correct way:** Fixed `width`/`height`, or reserve space.

❌ **Mistake 2:** Using `ease` timing.
✅ **Correct way:** `linear` for continuous rotations.

❌ **Mistake 3:** Forgetting screen reader text.
✅ **Correct way:** `role="status"` plus `.sr-only` text.

❌ **Mistake 4:** Spinner that never stops on error.
✅ **Correct way:** Handle error and timeout states in the UI logic.

❌ **Mistake 5:** Animating with `border-width` or `margin`.
✅ **Correct way:** Use `transform`/`opacity`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `@keyframes` | Defines animation steps | Animation के चरण |
| `animation` | Applies keyframes to element | Animation लगाना |
| `infinite` | Repeat forever | हमेशा दोहराना |
| `linear` | Constant-speed timing | एक समान गति |
| Skeleton | Placeholder shaped like content | Content जैसा placeholder |
| Shimmer | Moving highlight on skeleton | चमकती पट्टी |
| `animation-delay` | Wait before start (stagger) | शुरू होने में देरी |

---

## ⚡ 3-Line Summary
**English:**
1. Spinner = circle with one coloured border + `rotate(360deg)` in `@keyframes`, `linear infinite`.
2. Use `animation-delay` for dots and a sliding gradient for skeleton shimmer.
3. In Tailwind use `animate-spin` / `animate-pulse`; Next.js has `loading.tsx`; add `role="status"`.

**Hindi:**
1. Spinner = एक रंगीन border वाला गोला + `@keyframes` में `rotate(360deg)`, `linear infinite`।
2. Dots के लिए `animation-delay` और skeleton shimmer के लिए खिसकता gradient use करो।
3. Tailwind में `animate-spin` / `animate-pulse`; Next.js में `loading.tsx`; `role="status"` लगाओ।

---

## ➡️ Next Topic
**120. Responsive Table** — बड़ी tables को mobile पर readable कैसे बनाएँ।
