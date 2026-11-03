# 123. Form Styling
# हिंदी में: Form Styling

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly)

---

## 🔵 Simple Definition (English)
Form styling means making inputs, selects, textareas, checkboxes and buttons look consistent, clear and accessible: a visible focus ring, error/success states, labels tied to inputs, and good spacing, using plain CSS selectors like `:focus-visible`, `:user-invalid` and `accent-color`.

## 🔵 सरल परिभाषा (Hindi)
Form styling का मतलब inputs, selects, textareas, checkboxes और buttons को एक जैसा, साफ़ और accessible बनाना है: दिखने वाली focus ring, error/success states, input से जुड़े labels और अच्छी spacing, `:focus-visible`, `:user-invalid` और `accent-color` जैसे CSS selectors से।

---

## 🔴 Problem it Solves
```
PROBLEM: default browser form controls
  - look different on Chrome / Safari / Firefox
  - do not inherit your font (inputs use system font)
  - tiny text on iOS -> page zooms on focus
  - no feedback for errors
  - developers remove outline:none and break keyboard users

SOLUTION: a small, consistent form system with CSS variables and state selectors.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या: browser के default form controls
  - Chrome / Safari / Firefox में अलग दिखते हैं
  - आपका font inherit नहीं करते
  - iOS पर छोटा text -> focus पर page zoom हो जाता है
  - error का कोई feedback नहीं
  - developers outline:none कर देते हैं और keyboard users की दिक्कत बढ़ती है

हल: CSS variables और state selectors वाला छोटा, consistent form system।
```

---

## 🟢 How it Works — Step by Step
```
1. Structure: .field = label + control (+ hint/error); fieldset+legend for radio groups
2. Reset basics: box-sizing: border-box; font: inherit; width: 100%
3. Border + radius + padding on all text controls; resize: vertical on textarea
4. Focus: :focus-visible -> border colour + box-shadow ring (not bare outline:none)
5. Validation: HTML attrs (required, type=email, minlength) set :valid / :invalid
     :user-invalid / :user-valid = only after the user interacted
     fallback: input:invalid:not(:placeholder-shown)
6. Error text hidden by default; input:user-invalid ~ .error { display:block }
7. accent-color themes native radio/checkbox in one line
8. Mobile: font-size >= 16px stops iOS zoom
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Structure: .field = label + control (+ hint/error); radio group के लिए fieldset+legend
2. Basics: box-sizing: border-box; font: inherit; width: 100%
3. Text controls पर border + radius + padding; textarea पर resize: vertical
4. Focus: :focus-visible -> border colour + box-shadow ring (सिर्फ outline:none नहीं)
5. Validation: HTML attributes (required, type=email, minlength) से :valid / :invalid बनते हैं
     :user-invalid / :user-valid = user के छूने के बाद ही
     fallback: input:invalid:not(:placeholder-shown)
6. Error text default में छिपा; input:user-invalid ~ .error { display:block }
7. accent-color से native radio/checkbox का रंग एक line में
8. Mobile: font-size >= 16px से iOS zoom रुकता है
```

---

## 🟡 Real World Example
**Gmail / Google sign-in:** floating label, blue focus line, red error text under the field. **Amazon checkout:** inline red error with an icon for invalid pincode. **Swiggy / Zomato login:** phone input with a clear focus ring and a large button. **Instagram signup:** the Sign up button disabled until the fields are valid.

## 🟡 Real Example Hindi mein
**Gmail / Google sign-in:** floating label, नीली focus line, field के नीचे लाल error text। **Amazon checkout:** गलत pincode पर icon के साथ लाल error। **Swiggy / Zomato login:** phone input पर साफ़ focus ring और बड़ा button। **Instagram signup:** fields valid होने तक Sign up button disabled रहता है।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css). Core:

```html
<div class="field">
  <label for="email">Email</label>
  <input id="email" type="email" required placeholder="you@gmail.com">
  <small class="error">Please enter a valid email.</small>
</div>
```

```css
input {
  width: 100%; padding: 11px 12px;
  font: inherit;                       /* inherit page font */
  border: 1.5px solid #c7ccd1; border-radius: 8px;
}
input:focus-visible { outline: none; border-color: #1a73e8; box-shadow: 0 0 0 4px rgba(26,115,232,.2); }
input:user-invalid { border-color: #d93025; }          /* after interaction only */
.error { display: none; color: #d93025; }
input:user-invalid ~ .error { display: block; }
input[type="checkbox"], input[type="radio"] { accent-color: #1a73e8; }
```

---

## 🟠 React/Next.js Connection
```jsx
'use client';
import { useState } from 'react';

export function Field({ id, label, error, ...props }) {
  return (
    <div className="grid gap-1.5">
      <label htmlFor={id} className="text-sm font-semibold">{label}</label>
      <input
        id={id}
        aria-invalid={!!error}                       // a11y + styling hook
        aria-describedby={error ? `${id}-err` : undefined}
        // Tailwind: focus ring + aria-invalid variant for error state
        className="w-full rounded-lg border border-gray-300 px-3 py-2.5
                   focus-visible:border-blue-600 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-blue-600/20
                   aria-[invalid=true]:border-red-600"
        {...props}
      />
      {error && <small id={`${id}-err`} className="text-sm text-red-600">{error}</small>}
    </div>
  );
}
// Note: React uses htmlFor (not for) and className (not class).
// Tailwind plugin @tailwindcss/forms resets native control styles.
// Use React Hook Form + Zod for validation; Next.js Server Actions for submission.
```

---

## ⚫ Interview Questions + Answers

**Q1: `:focus` vs `:focus-visible`?**
A1: `:focus` matches whenever an element has focus, including mouse clicks. `:focus-visible` matches only when the browser decides focus should be shown (keyboard use, or text inputs), so you avoid focus rings on mouse-clicked buttons while keeping them for keyboard users.

**Q2: `:invalid` vs `:user-invalid`?**
A2: `:invalid` matches immediately, so empty required fields look red on page load. `:user-invalid` matches only after the user interacted or tried to submit. It is supported in all current evergreen browsers; use `:invalid:not(:placeholder-shown)` as a fallback.

**Q3: Why is `<label for>` important?**
A3: It links the label to the input: clicking the label focuses the input, the click target is larger, and screen readers announce the label. Alternatively wrap the input inside the label.

**Q4: How do you style native checkboxes/radios easily?**
A4: `accent-color` for colour. For full custom looks use `appearance: none` plus your own pseudo-element styling, keeping the real input in the DOM.

**Q5: Why do inputs not inherit the page font, and how to fix it?**
A5: Browsers give form controls their own UA font. Use `font: inherit` on `input, select, textarea, button`.

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** `outline: none` with no replacement.
✅ **Correct way:** Provide a custom focus ring with `box-shadow`/`outline`.

❌ **Mistake 2:** Placeholder used as the label.
✅ **Correct way:** A real `<label>`; placeholder only for examples.

❌ **Mistake 3:** Input font-size under 16px on mobile.
✅ **Correct way:** At least 16px so iOS does not zoom.

❌ **Mistake 4:** Red error on first load with `:invalid`.
✅ **Correct way:** `:user-invalid` or validate on blur/submit.

❌ **Mistake 5:** Colour alone to show errors.
✅ **Correct way:** Add text/icon and `aria-invalid` plus `aria-describedby`.

❌ **Mistake 6:** Wrong `type` (text for email), so no mobile keyboard or validation.
✅ **Correct way:** Use `email`, `tel`, `number`, `inputmode` and `autocomplete`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `:focus-visible` | Focus from keyboard | Keyboard focus की state |
| `:user-invalid` | Invalid after user interaction | छूने के बाद गलत |
| `accent-color` | Themes native controls | Native controls का रंग |
| `font: inherit` | Use parent's font | Parent का font लेना |
| `fieldset/legend` | Group related controls | जुड़े controls का समूह |
| `aria-invalid` | Marks field as erroneous | Field गलत है की सूचना |
| `autocomplete` | Browser autofill hint | Autofill संकेत |

---

## ⚡ 3-Line Summary
**English:**
1. Style forms with `font: inherit`, `border-box`, consistent padding, labels tied by `for`/`id`.
2. Show a custom `:focus-visible` ring and use `:user-invalid` for errors, with text and `aria-invalid`.
3. Use `accent-color` for checkboxes/radios, 16px inputs on mobile; React: `htmlFor`, Tailwind `focus-visible:` and `aria-[invalid=true]:`.

**Hindi:**
1. Forms में `font: inherit`, `border-box`, एक जैसी padding और `for`/`id` से जुड़े labels रखो।
2. अपनी `:focus-visible` ring दिखाओ, errors के लिए `:user-invalid` + text और `aria-invalid` लगाओ।
3. Checkbox/radio के लिए `accent-color`, mobile पर 16px inputs; React में `htmlFor`, Tailwind में `focus-visible:` और `aria-[invalid=true]:`।

---

## ➡️ Next Topic
**124. CSS Button Hover Effects** — transitions से buttons को जीवंत बनाना (fill, slide, glow, ripple)।
