# 124. CSS Button Hover Effects
# हिंदी में: CSS Button Hover Effects

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly)

---

## 🔵 Simple Definition (English)
Hover effects give visual feedback when the pointer is over a button. With `:hover`, `:active`, `:focus-visible` and `transition`, you can change colour, move, scale, glow or fill the button smoothly, and the effect should be matched by keyboard focus and press states.

## 🔵 सरल परिभाषा (Hindi)
Hover effects pointer के button पर आने पर visual feedback देते हैं। `:hover`, `:active`, `:focus-visible` और `transition` से button का रंग, position, size, glow या fill आराम से बदला जा सकता है, और यही feedback keyboard focus और press state में भी होना चाहिए।

---

## 🔴 Problem it Solves
```
PROBLEM: a flat button gives no hint that it is clickable or that the click registered.
  - users double-click or hesitate
  - abrupt colour jumps feel cheap
  - hover-only effects break on touch screens and keyboards

SOLUTION: transition-based states: hover (can click), focus (keyboard), active (clicked).
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या: सपाट button बताता नहीं कि वो click हो सकता है या click हो गया।
  - users दो बार click करते हैं या झिझकते हैं
  - अचानक रंग बदलना सस्ता लगता है
  - सिर्फ hover वाले effects touch और keyboard पर काम नहीं करते

हल: transition वाली states: hover (click हो सकता है), focus (keyboard), active (click हुआ)।
```

---

## 🟢 How it Works — Step by Step
```
1. Base .btn: set the resting style + transition on specific properties
   (transform, box-shadow, background-color, color) - not "all"
2. :hover changes a value -> transition animates between the two
3. LIFT       translateY(-3px) + bigger shadow
4. SLIDE FILL ::before layer (translateX(-101%)) slides to 0 on hover; text above via z-index
5. OUTLINE    transparent bg + coloured text -> solid on hover
6. GLOW       box-shadow with blur radius in the brand colour
7. ARROW      icon span translateX(6px) when the parent is hovered
8. UNDERLINE  ::after scaleX(0) -> scaleX(1)
9. GRADIENT   gradients cannot transition, so make it 200% wide and animate background-position
10. RIPPLE    JS inserts a circle at the click position; keyframes scale + fade
11. :active   scale(.97) = pressed. :focus-visible = ring for keyboard
12. @media (hover: hover) wraps hover-only effects so touch devices don't get "stuck" hover
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Base .btn: सामान्य style + खास properties पर transition ("all" नहीं)
2. :hover कोई value बदलता है -> transition दोनों के बीच animate करता है
3. LIFT       translateY(-3px) + बड़ी shadow
4. SLIDE FILL ::before layer (translateX(-101%)) hover पर 0 पर आती है; text z-index से ऊपर
5. OUTLINE    transparent background + रंगीन text -> hover पर solid
6. GLOW       brand रंग की blur वाली box-shadow
7. ARROW      parent hover पर icon translateX(6px)
8. UNDERLINE  ::after scaleX(0) -> scaleX(1)
9. GRADIENT   gradient transition नहीं होता, इसलिए 200% चौड़ा रखकर background-position animate करो
10. RIPPLE    JS click की जगह एक circle डालता है; keyframes से बड़ा होकर fade
11. :active   scale(.97) = दबा हुआ। :focus-visible = keyboard ring
12. @media (hover: hover) से hover effects सिर्फ hover वाले devices पर, touch पर "अटके" नहीं
```

---

## 🟡 Real World Example
**Zomato / Swiggy:** the red "Order now" / "Add" button gets a darker shade and slight lift on hover. **Amazon:** the yellow "Add to Cart" darkens on hover and shows a focus ring on Tab. **Instagram:** Follow button changes shade on hover and press. **Gmail:** the Compose button gains a shadow on hover.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy:** लाल "Order now" / "Add" button hover पर गहरा होता है और थोड़ा ऊपर उठता है। **Amazon:** पीला "Add to Cart" hover पर गहरा होता है और Tab पर focus ring दिखती है। **Instagram:** Follow button hover और press पर shade बदलता है। **Gmail:** Compose button hover पर shadow पाता है।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css). Core:

```html
<button class="btn b-lift" type="button">Lift + shadow</button>
```

```css
.btn {
  padding: 13px 22px; border: 2px solid #e23744; border-radius: 10px;
  background: #e23744; color: #fff; cursor: pointer;
  transition: transform .2s ease, box-shadow .2s ease;   /* specific properties only */
}
@media (hover: hover) {                                    /* touch devices skip hover */
  .btn:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(226,55,68,.35); }
}
.btn:active { transform: scale(.97); }                     /* pressed */
.btn:focus-visible { outline: 3px solid #fbbc04; outline-offset: 3px; }  /* keyboard */
```

---

## 🟠 React/Next.js Connection
```jsx
// Tailwind: all states are variants, no CSS file needed
export function Button({ children, ...props }) {
  return (
    <button
      className="rounded-xl bg-red-600 px-5 py-3 font-semibold text-white
                 transition duration-200
                 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-red-600/40
                 active:scale-95
                 focus-visible:outline focus-visible:outline-4 focus-visible:outline-yellow-400
                 disabled:cursor-not-allowed disabled:opacity-60
                 motion-reduce:transition-none motion-reduce:hover:transform-none"
      {...props}
    >
      {children}
    </button>
  );
}
// Tailwind's hover: variant already uses @media (hover: hover) in v4 (v3: enable hoverOnlyWhenSupported).
// Variants with class-variance-authority (shadcn/ui) -> <Button variant="outline" />.
// Framer Motion: <motion.button whileHover={{ y: -3 }} whileTap={{ scale: .97 }} />
```

---

## ⚫ Interview Questions + Answers

**Q1: Why not `transition: all`?**
A1: It animates every changing property, including layout ones like width or padding, which hurts performance and causes unexpected animations. List only what you animate.

**Q2: Which properties are cheap to animate?**
A2: `transform` and `opacity` (compositor only). `box-shadow`, `background-color` and `color` trigger paint but are fine for small elements. Avoid animating `width`, `height`, `margin`, `top/left` (layout).

**Q3: Order of link/button state pseudo-classes?**
A3: LVHFA: `:link`, `:visited`, `:hover`, `:focus`, `:active`. Because they have equal specificity, later rules win, so `:active` must come after `:hover`.

**Q4: How do you handle hover on touch devices?**
A4: Touch devices can leave `:hover` stuck after a tap. Wrap hover styles in `@media (hover: hover)`, and make sure the effect is never the only way to discover information.

**Q5: How do you animate a gradient on hover?**
A5: Gradients (`background-image`) are not interpolated. Make the gradient wider (`background-size: 200%`) and transition `background-position`, or use an overlay `::before` with `opacity`, or register `@property` custom properties for colours (newer, check support).

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** `transition: all .3s` on everything.
✅ **Correct way:** `transition: transform .2s, box-shadow .2s`.

❌ **Mistake 2:** `:hover` only, no `:focus-visible`.
✅ **Correct way:** Give keyboard users the same cue.

❌ **Mistake 3:** Putting `transition` only on `:hover`, so the un-hover snaps back instantly.
✅ **Correct way:** Put `transition` on the base state.

❌ **Mistake 4:** `outline: none` to hide the focus ring.
✅ **Correct way:** Replace it with your own visible ring.

❌ **Mistake 5:** Slow, long effects (above ~300ms) that make the UI laggy.
✅ **Correct way:** 150-300ms, and honour `prefers-reduced-motion`.

❌ **Mistake 6:** `<div>` styled like a button.
✅ **Correct way:** Use `<button>`; for navigation use `<a>`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `:hover` | Pointer over element | Pointer ऊपर होना |
| `:active` | While being pressed | दबे रहने की state |
| `:focus-visible` | Keyboard focus | Keyboard focus |
| `transition` | Smooth change over time | समय के साथ धीरे बदलाव |
| `@media (hover: hover)` | Device can hover | Hover वाले devices |
| Ripple | Circle expanding from click | Click से फैलता गोला |
| `transform-origin` | Pivot point of transform | Transform का केंद्र |
| Compositor | GPU animation layer | GPU वाली layer |

---

## ⚡ 3-Line Summary
**English:**
1. Put `transition` on the base state, animate specific properties (`transform`, `box-shadow`, colours), not `all`.
2. Pair `:hover` with `:focus-visible` and `:active`; wrap hover in `@media (hover: hover)`.
3. In React/Tailwind use `hover:`, `active:`, `focus-visible:`, `motion-reduce:` variants or Framer Motion `whileHover`.

**Hindi:**
1. `transition` base state पर लगाओ, खास properties (`transform`, `box-shadow`, colours) animate करो, `all` नहीं।
2. `:hover` के साथ `:focus-visible` और `:active` दो; hover को `@media (hover: hover)` में रखो।
3. React/Tailwind में `hover:`, `active:`, `focus-visible:`, `motion-reduce:` variants या Framer Motion `whileHover` use करो।

---

## ➡️ Next Topic
**125. Dark Mode Toggle** — `prefers-color-scheme`, CSS variables और theme switch button।
