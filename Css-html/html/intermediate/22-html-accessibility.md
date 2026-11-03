# 22. HTML Accessibility (ARIA roles, alt text, label)
# हिंदी में: HTML Accessibility — हर इंसान के लिए Website

---

## 🔵 Simple Definition (English)
Accessibility (a11y) means building pages that people with disabilities (blind, low vision, deaf, motor-impaired, cognitive) can use, with screen readers, keyboards, voice control and zoom. In HTML you get most of it by using the **right semantic elements**, adding **alt text** to images, linking **labels** to inputs, and using **ARIA** only to fill gaps.

## 🔵 सरल परिभाषा (Hindi)
Accessibility (a11y) का मतलब ऐसे pages बनाना जिन्हें विकलांग लोग (नेत्रहीन, कम दृष्टि, बधिर, motor-impaired, cognitive) screen reader, keyboard, voice control और zoom से use कर सकें। HTML में ज़्यादातर यह **सही semantic elements**, images पर **alt text**, inputs से जुड़े **labels** और खाली जगह भरने के लिए **ARIA** से मिल जाता है।

---

## 🔴 Problem it Solves
```
WITHOUT ACCESSIBILITY:
  <div class="btn" onclick="buy()">Buy</div>
  <img src="chart.png">
  <input placeholder="Email">
  - Screen reader says "clickable" or "graphic" or "edit text": no idea what it is
  - Keyboard user can't Tab to the fake button or press Enter
  - Blind user can't know what the image shows
  - ~15 percent of the world has some disability; plus temporary cases (broken arm, bright sun)
  - Legal risk: ADA (US), EAA (EU, from June 2025), India's RPwD Act, GIGW guidelines

WITH ACCESSIBILITY:
  <button type="button" onclick="buy()">Buy</button>
  <img src="chart.png" alt="Sales rose 40 percent from Jan to Mar">
  <label for="email">Email</label><input id="email" type="email">
  - Screen reader: "Buy, button" / "Email, edit text" ; keyboard works for free
  - Also helps SEO, voice assistants and power users
```

## 🔴 यह क्यों बना? (Hindi)
```
ACCESSIBILITY के बिना:
  <div class="btn" onclick="buy()">Buy</div>
  <img src="chart.png">
  <input placeholder="Email">
  - Screen reader सिर्फ "clickable" या "graphic" बोलता है: क्या है, पता नहीं
  - Keyboard user नकली button तक Tab नहीं कर सकता, Enter नहीं दबा सकता
  - नेत्रहीन user image का मतलब नहीं जान सकता
  - दुनिया के ~15 प्रतिशत लोगों को कोई न कोई disability है; अस्थायी मामले भी (टूटा हाथ, तेज धूप)
  - कानूनी जोखिम: ADA (US), EAA (EU), भारत का RPwD Act, GIGW guidelines

ACCESSIBILITY के साथ:
  <button type="button" onclick="buy()">Buy</button>
  <img src="chart.png" alt="Sales rose 40 percent from Jan to Mar">
  <label for="email">Email</label><input id="email" type="email">
  - Screen reader: "Buy, button" / "Email, edit text"; keyboard मुफ़्त में काम करता है
  - SEO, voice assistants और power users को भी फ़ायदा
```

---

## 🟢 How it Works — Step by Step

```
THE BROWSER BUILDS AN "ACCESSIBILITY TREE" from the DOM:
  each element -> role (what it is) + name (what it is called) + state/value
  Screen readers (NVDA, JAWS, VoiceOver, TalkBack) read this tree, NOT the pixels.

RULE #1 OF ARIA: if a native HTML element exists, USE IT.
  <button> already has role=button, focus, Enter/Space, disabled.
  <div role="button"> has only the role: YOU must add tabindex, key handlers, etc.

1. SEMANTIC HTML (free roles + keyboard)
   header(banner) nav(navigation) main(main) aside(complementary) footer(contentinfo)
   button, a[href], h1-h6 (heading outline), ul/li, table, form controls.
   Use ONE h1, don't skip heading levels, one <main>.

2. TEXT ALTERNATIVES for images
   <img alt="Golden retriever catching a ball">   informative: describe the purpose
   <img alt="">                                    decorative: empty alt -> skipped
   (never omit alt: screen reader reads the file name "IMG_2034.jpg")
   Icon buttons: <button aria-label="Close"><svg aria-hidden="true">...</svg></button>
   Complex charts: short alt + longer description nearby / <figure><figcaption>.

3. LABELS for form controls
   <label for="email">Email</label><input id="email">    (explicit, clicking label focuses input)
   <label>Email <input></label>                           (implicit wrapping)
   Placeholder is NOT a label. Group radios: <fieldset><legend>.
   Errors: aria-describedby="err" + aria-invalid="true", message in role="alert".

4. ARIA (Accessible Rich Internet Applications) when HTML is not enough
   ROLES   : role="dialog", "alert", "tablist", "tab", "tabpanel", "menu", "status"
   PROPERTIES: aria-label, aria-labelledby, aria-describedby, aria-controls
   STATES  : aria-expanded, aria-pressed, aria-checked, aria-selected,
             aria-current="page", aria-hidden="true", aria-live="polite"
   ARIA changes ONLY what is announced. It adds NO behavior and NO styling.

5. KEYBOARD
   Everything must work with Tab, Shift+Tab, Enter, Space, Esc, arrow keys.
   tabindex="0" (in tab order)  tabindex="-1" (focusable by JS only)  never tabindex > 0.
   Visible focus ring: never `outline: none` without a replacement (:focus-visible).
   Skip link: <a href="#main" class="skip">Skip to content</a> first in body.
   Modals: trap focus, Esc closes, return focus to the opener (native <dialog> does it).

6. VISUAL
   Colour contrast: 4.5:1 for normal text, 3:1 for large text (WCAG AA).
   Don't convey info by colour alone. Allow zoom to 200%. lang="en" on <html>
   (and lang="hi" on Hindi snippets) so screen readers pick the right voice.
   Respect prefers-reduced-motion.

7. LIVE REGIONS: announce dynamic updates (toasts, "Added to cart")
   <div role="status" aria-live="polite"> or role="alert" (assertive).
   Region must exist in the DOM BEFORE the text changes.

TESTING: keyboard only; VoiceOver (Cmd+F5) / NVDA; Lighthouse and axe DevTools;
DevTools > Accessibility pane. Automated tools catch only ~30-40 percent of issues.
```

## 🟢 कैसे काम करता है? (Hindi)

```
BROWSER DOM से एक "ACCESSIBILITY TREE" बनाता है:
  हर element -> role (क्या है) + name (नाम क्या है) + state/value
  Screen readers (NVDA, JAWS, VoiceOver, TalkBack) यही tree पढ़ते हैं, pixels नहीं।

ARIA का नियम #1: अगर native HTML element मौजूद है, तो वही use करो।
  <button> में role, focus, Enter/Space, disabled सब पहले से हैं।
  <div role="button"> में सिर्फ role है: tabindex, key handlers आपको जोड़ने पड़ेंगे।

1. SEMANTIC HTML: header, nav, main, aside, footer, button, a[href], h1-h6, table।
   एक ही h1, heading levels मत छोड़ो, एक <main>।

2. IMAGES के लिए alt:
   <img alt="Golden retriever catching a ball">   जानकारी वाली: उद्देश्य बताओ
   <img alt="">                                    सजावटी: खाली alt -> छोड़ दी जाती है
   Icon button: <button aria-label="Close"><svg aria-hidden="true">...</svg></button>

3. FORM के LABELS:
   <label for="email">Email</label><input id="email">
   Placeholder label नहीं है। Radios के लिए <fieldset><legend>।
   Errors: aria-describedby + aria-invalid="true", message role="alert" में।

4. ARIA जब HTML काफ़ी न हो:
   Roles: dialog, alert, tablist, tab, tabpanel, status
   Properties: aria-label, aria-labelledby, aria-describedby, aria-controls
   States: aria-expanded, aria-pressed, aria-checked, aria-current, aria-hidden, aria-live
   ARIA सिर्फ बताई जाने वाली बात बदलता है; behavior या styling नहीं देता।

5. KEYBOARD: सब कुछ Tab, Shift+Tab, Enter, Space, Esc, arrow keys से चलना चाहिए।
   tabindex="0" tab order में; tabindex="-1" सिर्फ JS से focus; tabindex > 0 कभी नहीं।
   Focus ring कभी मत हटाओ (:focus-visible use करो)। Skip link सबसे ऊपर।

6. VISUAL: contrast 4.5:1 (normal text), 3:1 (बड़ा text)। सिर्फ रंग से जानकारी मत दो।
   <html lang="en"> ज़रूर लिखो (हिंदी हिस्से पर lang="hi")।

7. LIVE REGIONS: dynamic updates बोलने के लिए <div role="status" aria-live="polite">।
   Region DOM में पहले से होना चाहिए, फिर text बदलो।

TEST: सिर्फ keyboard से; VoiceOver/NVDA; Lighthouse और axe। Automated tools सिर्फ
~30-40 प्रतिशत problems पकड़ते हैं।
```

---

## 🟡 Real World Example
**Amazon:** the very first Tab press shows a "Skip to main content" link; the search box has a label (visually hidden), product images have descriptive `alt`, and the cart icon has `aria-label="3 items in cart"`. **Swiggy / Zomato:** when you add a dish, a live region (`role="status"`) announces "Added Margherita to cart" to screen readers while sighted users see a toast. **Gmail:** nearly everything is operable by keyboard shortcuts, and unread rows expose state through ARIA (`aria-selected`, `role="row"`).

## 🟡 Real Example Hindi mein
**Amazon:** पहली Tab press पर "Skip to main content" link दिखता है; search box का label (visually hidden) है, product images में वर्णनात्मक `alt` है और cart icon पर `aria-label="3 items in cart"` है। **Swiggy / Zomato:** dish add करने पर live region (`role="status"`) screen reader को "Added Margherita to cart" बोलता है, जबकि दिखने वाले users को toast दिखता है। **Gmail:** लगभग सब कुछ keyboard shortcuts से चलता है, और ARIA (`aria-selected`, `role="row"`) से unread rows की state बताई जाती है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<!-- lang tells screen readers which voice/pronunciation to use -->
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Accessibility Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; line-height: 1.5; color: #1a1a1a; }

    /* Skip link: hidden until focused with the keyboard */
    .skip { position: absolute; left: -999px; background: #000; color: #fff; padding: 8px 12px; z-index: 10; }
    .skip:focus { left: 8px; top: 8px; }

    /* Visually hidden but available to screen readers (for labels) */
    .sr-only { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

    header, main, footer { max-width: 640px; margin: 0 auto; padding: 16px; }
    header { display: flex; justify-content: space-between; align-items: center; }
    nav a { margin-right: 12px; color: #0b57d0; }              /* contrast: #0b57d0 on white is about 6.5:1 */
    nav a[aria-current="page"] { font-weight: bold; text-decoration: underline; }

    /* Clear focus ring for keyboard users (only when using keyboard) */
    :focus-visible { outline: 3px solid #ff9800; outline-offset: 2px; }

    button, input { font: inherit; padding: 10px 14px; border-radius: 6px; border: 2px solid #767676; }
    button { background: #b3261e; color: #fff; border-color: #b3261e; cursor: pointer; }   /* white on #b3261e is about 6.5:1 */
    button[aria-pressed="true"] { background: #1b5e20; border-color: #1b5e20; }
    label { display: block; margin: 12px 0 4px; font-weight: 600; }
    .error { color: #b3261e; font-size: 14px; margin: 4px 0 0; }
    input[aria-invalid="true"] { border-color: #b3261e; }

    details { margin: 12px 0; }
    .toast { background: #e8f5e9; padding: 8px 12px; border-radius: 6px; min-height: 40px; margin-top: 12px; }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
  </style>
</head>
<body>
  <!-- 1. Skip link: first focusable element -->
  <a class="skip" href="#main">Skip to main content</a>

  <header>
    <strong>FoodApp</strong>
    <!-- 2. Landmark + name; aria-current marks the current page -->
    <nav aria-label="Main">
      <a href="#" aria-current="page">Home</a>
      <a href="#">Orders</a>
    </nav>
    <!-- 3. Icon button: no visible text, so aria-label gives it a name; svg is decorative -->
    <button type="button" aria-label="Cart, 3 items">
      <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M7 18a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm10 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM1 2v2h2l3.6 7.6-1.4 2.4A2 2 0 0 0 7 17h12v-2H7.4l1.1-2h7.5a2 2 0 0 0 1.7-1l3.6-6.5A1 1 0 0 0 20.5 4H5.2l-.9-2z"/></svg>
    </button>
  </header>

  <main id="main" tabindex="-1">   <!-- tabindex=-1 lets the skip link move focus here -->
    <h1>Checkout</h1>

    <!-- 4. Images: informative vs decorative -->
    <img alt="Margherita pizza with basil and mozzarella" width="120" height="80"
         src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='80'%3E%3Crect width='120' height='80' fill='%23ffcc80'/%3E%3C/svg%3E">
    <img alt="" width="20" height="20"
         src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20'%3E%3Ccircle cx='10' cy='10' r='8' fill='%23ccc'/%3E%3C/svg%3E">
    <!-- the second image is purely decoration: empty alt makes screen readers skip it -->

    <!-- 5. Form with real labels, hints and error handling -->
    <form id="f" novalidate>
      <label for="email">Email address</label>
      <input id="email" name="email" type="email" autocomplete="email"
             aria-describedby="email-hint email-err" required>
      <div id="email-hint" class="sr-only">We send the order receipt here.</div>
      <p id="email-err" class="error" role="alert"></p>   <!-- role=alert announces when text is added -->

      <fieldset>
        <legend>Payment method</legend>
        <label><input type="radio" name="pay" value="upi" checked> UPI</label>
        <label><input type="radio" name="pay" value="cod"> Cash on delivery</label>
      </fieldset>

      <!-- 6. Toggle button: aria-pressed communicates on/off state -->
      <p><button type="button" id="tip" aria-pressed="false">Add Rs 20 tip</button></p>

      <button type="submit">Place order</button>
    </form>

    <!-- 7. Native disclosure: accessible with no ARIA -->
    <details>
      <summary>Cancellation policy</summary>
      <p>You can cancel within 60 seconds.</p>
    </details>

    <!-- 8. Live region: announces updates without moving focus -->
    <div class="toast" role="status" aria-live="polite" id="toast"></div>
  </main>

  <footer><p>&copy; 2026 FoodApp</p></footer>

  <script>
    const email = document.getElementById('email');
    const err = document.getElementById('email-err');
    const toast = document.getElementById('toast');
    const tip = document.getElementById('tip');

    document.getElementById('f').addEventListener('submit', (e) => {
      e.preventDefault();
      if (!email.validity.valid) {
        email.setAttribute('aria-invalid', 'true');                    // state
        err.textContent = 'Enter a valid email like name@example.com'; // announced via role=alert
        email.focus();                                                 // move focus to the problem
      } else {
        email.removeAttribute('aria-invalid');
        err.textContent = '';
        toast.textContent = 'Order placed successfully';               // announced politely
      }
    });

    tip.addEventListener('click', () => {
      const on = tip.getAttribute('aria-pressed') === 'true';
      tip.setAttribute('aria-pressed', String(!on));                   // update the state for AT
      tip.textContent = on ? 'Add Rs 20 tip' : 'Tip added';
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// JSX attribute names: htmlFor (for), aria-* stay as written, tabIndex, role as is.
import { useId, useState } from 'react';

export function EmailField({ error }) {
  const id = useId();                                   // unique id for label <-> input
  return (
    <div>
      <label htmlFor={id}>Email</label>
      <input
        id={id}
        type="email"
        aria-invalid={!!error}                          // booleans become "true"/"false"
        aria-describedby={error ? `${id}-err` : undefined}
      />
      {error && <p id={`${id}-err`} role="alert">{error}</p>}
    </div>
  );
}

// Icon-only button
<button aria-label="Close dialog" onClick={close}><XIcon aria-hidden="true" /></button>

// next/image requires alt (decorative: alt="")
<Image src="/pizza.jpg" alt="Margherita pizza" width={400} height={300} />

// Next.js: <Link> renders <a> (good); don't use <div onClick> for navigation.
// Route change announcements: Next.js App Router has a built-in route announcer.
// Move focus to <h1> or main on route change in custom SPA routers.

// Accessible component libraries: Radix UI, React Aria, Headless UI, shadcn/ui
// handle focus traps, roles, keyboard for modals, menus, tabs, comboboxes.
// Tailwind: "sr-only" class, "focus-visible:ring-2", "motion-reduce:transition-none".
// Lint: eslint-plugin-jsx-a11y catches missing alt, label, bad roles. Test with
// @testing-library (getByRole, getByLabelText) which mirrors how assistive tech sees the page.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is web accessibility and why does it matter?**
A1: Designing and coding sites so everyone, including people with visual, hearing, motor and cognitive disabilities, can perceive, operate and understand them using tools like screen readers, keyboards, switches and zoom. It matters for inclusion, legal compliance (ADA, EAA, RPwD/GIGW), larger audience, and it improves SEO, usability and code quality for everyone.

**Q2: What is the first rule of ARIA?**
A2: Do not use ARIA if a native HTML element already provides the semantics and behavior. `<button>` beats `<div role="button">` because the native element has keyboard support, focus and the right role built in. ARIA only changes what assistive technology announces; it adds no behavior. Bad ARIA is worse than no ARIA.

**Q3: How do you write good `alt` text? When should `alt` be empty?**
A3: Describe the purpose of the image in context, short and without "image of". For decorative images (backgrounds, dividers, icons next to text that already says the same thing) use `alt=""` so screen readers skip it. Never leave `alt` out because the file name would be read. For linked images describe the destination; for charts give the key insight plus a longer description nearby.

**Q4: How do you make a form accessible?**
A4: Each control needs a programmatic label (`<label for>` matching the `id`, or wrapping). Use `fieldset`/`legend` for groups, proper `type` and `autocomplete`, don't rely on placeholder or colour alone, mark required fields, link hints and errors with `aria-describedby`, set `aria-invalid`, announce errors using `role="alert"` and move focus to the first error. Ensure keyboard operation and sufficient contrast.

**Q5: What are `aria-label`, `aria-labelledby` and `aria-describedby`?**
A5: `aria-label` gives an element a text name directly (good for icon buttons). `aria-labelledby` points to the id(s) of existing visible elements that provide the name (takes priority over `aria-label`). `aria-describedby` points to elements giving extra description (hints, errors) that is read after the name. Native `<label>` and visible text are preferred when possible.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Clickable divs
```html
<div class="btn" onclick="save()">Save</div>
```
✅ **Correct way:** `<button type="button" onclick="save()">Save</button>`

❌ **Mistake 2:** Missing or useless alt, or placeholder as the only label
```html
<img src="logo.png"> <img src="x.png" alt="image"> <input placeholder="Name">
```
✅ **Correct way:** `<img src="logo.png" alt="FoodApp">`, `alt=""` for decoration, and `<label for="name">Name</label>`.

❌ **Mistake 3:** Removing the focus outline
```css
*:focus { outline: none; }
```
✅ **Correct way:** Style it: `:focus-visible { outline: 3px solid #ff9800; outline-offset: 2px; }`

❌ **Mistake 4:** Low-contrast grey text, or information by colour only (red = error with no text/icon)
✅ **Correct way:** Check 4.5:1 contrast and add text or icons to colour cues.

❌ **Mistake 5:** `aria-hidden="true"` on focusable elements, or `tabindex="5"`
✅ **Correct way:** Never hide focusable content from AT; use only `tabindex="0"` or `"-1"`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| a11y | Short for accessibility | Accessibility का संक्षिप्त रूप |
| Screen reader | Software that reads the page aloud | Page को बोलकर पढ़ने वाला software |
| ARIA | Attributes that add roles/states for AT | Roles/states देने वाले attributes |
| alt text | Text alternative for an image | Image का text विकल्प |
| Accessibility tree | Tree of roles/names AT reads | AT जो tree पढ़ता है |
| Landmark | Region like nav/main/footer | Page का क्षेत्र |
| WCAG | Web Content Accessibility Guidelines | Accessibility के मानक |
| Live region | Area whose updates are announced | जिसके बदलाव बोले जाते हैं |
| Focus management | Controlling where keyboard focus is | Keyboard focus का नियंत्रण |

---

## ⚡ 3-Line Summary
**English:**
1. Accessibility means everyone can use your site; start with semantic HTML, real `<button>`/`<a>`, `alt` on images and `<label>` on inputs.
2. Use ARIA only when native HTML cannot do the job, and remember it changes announcements, not behavior; keep keyboard focus visible and contrast at 4.5:1.
3. In React use `htmlFor`, `useId`, `aria-*`, jsx-a11y lint and libraries like Radix/React Aria; test with keyboard and a screen reader.

**Hindi:**
1. Accessibility का मतलब हर कोई आपकी site use कर सके; semantic HTML, असली `<button>`/`<a>`, images पर `alt` और inputs पर `<label>` से शुरू करो।
2. ARIA सिर्फ तब use करो जब native HTML काफ़ी न हो; यह announcements बदलता है, behavior नहीं; keyboard focus दिखे और contrast 4.5:1 रहे।
3. React में `htmlFor`, `useId`, `aria-*`, jsx-a11y lint और Radix/React Aria जैसी libraries use करो; keyboard और screen reader से test करो।

---

## ➡️ Next Topic
**23. SEO Basics with HTML** — accessibility और SEO साथ चलते हैं: semantic HTML से search engines को भी page समझ आता है।
