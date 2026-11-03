# 41. Web Accessibility (WCAG Guidelines)
# हिंदी में: Web Accessibility (WCAG) — हर इंसान के लिए Website

---

## 🔵 Simple Definition (English)
Web accessibility means building sites that people with disabilities (vision, hearing, motor, cognitive) can use, including with screen readers, keyboard only, or zoom. **WCAG** (Web Content Accessibility Guidelines) is the W3C standard, organised by four principles: **POUR**: Perceivable, Operable, Understandable, Robust, with levels A, AA, AAA. Most laws target **AA**.

## 🔵 सरल परिभाषा (Hindi)
Web accessibility का मतलब है ऐसी sites बनाना जिन्हें विकलांगता वाले लोग (दृष्टि, श्रवण, motor, cognitive) भी use कर सकें, screen reader, सिर्फ keyboard या zoom के साथ। **WCAG** W3C का standard है, जो चार सिद्धांतों पर है **POUR**: Perceivable, Operable, Understandable, Robust; levels A, AA, AAA। ज़्यादातर कानून **AA** माँगते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM:
  - Image without alt text: blind user hears "image" only
  - Light-gray text on white: low-vision users cannot read it
  - Custom dropdown built with <div>: keyboard users cannot open it
  - Video without captions: deaf users miss the content
  - Focus outline removed: keyboard user does not know where they are

WHO BENEFITS: permanent (blind), temporary (broken arm), situational
(bright sun, noisy room), and older users. ~1 in 6 people have a disability.

LEGAL: ADA (US), European Accessibility Act, India's RPwD Act and GIGW
guidelines: lawsuits against inaccessible e-commerce sites are common.
Also improves SEO.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  - Image में alt नहीं: दृष्टिहीन user को सिर्फ "image" सुनाई देता है
  - सफ़ेद पर हल्का gray text: कम दिखने वाले पढ़ नहीं पाते
  - <div> से बना dropdown: keyboard से नहीं खुलता
  - बिना captions का video: बधिर users को समझ नहीं आता
  - Focus outline हटा दी: keyboard user को पता नहीं कहाँ है

फ़ायदा: स्थायी, अस्थायी (टूटा हाथ) और परिस्थितिजन्य (तेज़ धूप) सबको।
कानून: ADA, European Accessibility Act, भारत का RPwD Act। SEO भी बेहतर होता है।
```

---

## 🟢 How it Works — Step by Step

```
WCAG 2.x: POUR PRINCIPLES

1. PERCEIVABLE  (can users sense the content?)
   - alt text for images (decorative: alt="")
   - captions/transcripts for audio and video
   - contrast: text 4.5:1 (large text 3:1), UI components 3:1
   - do not use color alone to convey meaning (add icon/text)
   - content reflows at 320px / 400% zoom; text resizable to 200%

2. OPERABLE  (can users operate it?)
   - everything works with keyboard (Tab, Shift+Tab, Enter, Space, Esc)
   - visible focus indicator
   - skip link ("Skip to main content")
   - no keyboard traps; enough time; no flashing > 3 times/sec
   - touch target size: at least 24x24 CSS px (WCAG 2.2 AA), 44px is better

3. UNDERSTANDABLE
   - <html lang="en"> set; lang="hi" on Hindi parts
   - clear labels, helpful error messages, consistent navigation

4. ROBUST
   - valid, semantic HTML; ARIA only when native HTML is not enough
   - name, role, value exposed to assistive tech

LEVELS: A (minimum) < AA (target) < AAA (enhanced)
Current versions: WCAG 2.1 and 2.2 (2.2 adds focus appearance, target size,
accessible authentication, dragging alternatives).

FIRST RULE OF ARIA: use native element (<button>) before role="button".

TESTING:
  - Keyboard only walk-through
  - Screen readers: NVDA / JAWS (Windows), VoiceOver (Mac/iOS), TalkBack
  - Lighthouse, axe DevTools, WAVE (automated finds ~30-40% of issues)
```

## 🟢 कैसे काम करता है? (Hindi)

```
POUR सिद्धांत:

1. Perceivable (महसूस हो): images पर alt, video पर captions,
   contrast 4.5:1 (बड़े text पर 3:1), सिर्फ रंग से मतलब न बताओ
2. Operable (चला सकें): सब कुछ keyboard से चले, focus दिखे,
   skip link, keyboard trap नहीं, touch target बड़ा
3. Understandable (समझ आए): <html lang>, साफ labels, मददगार error messages
4. Robust (मज़बूत): semantic HTML, ज़रूरत पर ही ARIA

Levels: A < AA (लक्ष्य) < AAA
ARIA का पहला नियम: पहले native element (<button>), फिर role।

Testing: सिर्फ keyboard से घूमो, VoiceOver/NVDA चलाओ,
Lighthouse और axe से जाँचो (automatic tools सब नहीं पकड़ते)।
```

---

## 🟡 Real World Example
**Gmail:** fully keyboard operable (j/k to move, `c` to compose), every icon button has an `aria-label`, and errors are announced via live regions. **Amazon checkout:** each form field has a visible `<label>`, error text is linked with `aria-describedby`, and focus moves to the first error on failed submit. **Zomato:** a "Veg only" toggle is a real `<input type="checkbox" role="switch">` so screen readers say "Veg only, switch, off".

## 🟡 Real Example Hindi mein
**Gmail:** पूरा keyboard से चलता है (j/k से move, `c` से compose), हर icon button पर `aria-label` है, और errors live regions से सुनाए जाते हैं। **Amazon checkout:** हर field का दिखने वाला `<label>` है, error text `aria-describedby` से जुड़ा है, और submit fail होने पर focus पहली error पर जाता है। **Zomato** का "Veg only" toggle असली `<input type="checkbox" role="switch">` है, इसलिए screen reader बोलता है "Veg only, switch, off"।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Accessible Page Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; line-height: 1.5; color: #1a1a1a; margin: 0; }

    /* Skip link: hidden until focused by keyboard */
    .skip-link { position: absolute; left: -999px; top: 0; background: #000; color: #fff; padding: 8px 12px; }
    .skip-link:focus { left: 0; z-index: 10; }

    header, main { max-width: 640px; margin: 0 auto; padding: 16px; }

    /* Visible focus for keyboard users (never remove without replacement) */
    :focus-visible { outline: 3px solid #1a73e8; outline-offset: 2px; }

    /* Good contrast: #1a1a1a on #fff = ~17:1 ; #595959 on #fff = 7:1 */
    .muted { color: #595959; }

    /* Large enough touch target */
    button, input[type="text"], input[type="email"] { min-height: 44px; padding: 8px 12px; font: inherit; }
    button { background: #1a73e8; color: #fff; border: 0; border-radius: 6px; cursor: pointer; }

    label { display: block; font-weight: 600; margin-top: 12px; }
    .error { color: #b00020; margin: 4px 0 0; }      /* not color alone: has text + icon */
    input[aria-invalid="true"] { border: 2px solid #b00020; }

    /* Visually hidden but available to screen readers */
    .sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }

    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>

  <header>
    <!-- Landmark + labelled nav -->
    <nav aria-label="Primary">
      <a href="/">Home</a> | <a href="/menu" aria-current="page">Menu</a>
    </nav>
  </header>

  <main id="main" tabindex="-1">
    <h1>Order food</h1>

    <!-- Informative image: meaningful alt. Decorative image: alt="" -->
    <img src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" width="120" height="80" alt="Plate of vegetable biryani">
    <p class="muted">Delivery in 30 minutes.</p>

    <!-- Icon-only button needs an accessible name -->
    <button type="button" aria-label="Add to cart">
      <span aria-hidden="true">+</span>
    </button>

    <form id="f" novalidate>
      <label for="email">Email</label>
      <input id="email" name="email" type="email" autocomplete="email"
             aria-describedby="email-err" required>
      <!-- aria-live: announced when text changes -->
      <p id="email-err" class="error" role="alert"></p>
      <button type="submit">Place order</button>
    </form>

    <!-- Native disclosure is keyboard + screen reader accessible by default -->
    <details>
      <summary>Allergy information</summary>
      <p>Contains nuts and dairy.</p>
    </details>
  </main>

  <script>
    const form = document.getElementById('f');
    const email = document.getElementById('email');
    const err = document.getElementById('email-err');

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!email.validity.valid) {
        // Error text + aria-invalid + move focus to problem field
        err.textContent = 'Error: please enter a valid email like name@example.com';
        email.setAttribute('aria-invalid', 'true');
        email.focus();
      } else {
        err.textContent = '';
        email.removeAttribute('aria-invalid');
        alert('Order placed');
      }
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
import { useId, useRef, useEffect } from 'react';

// 1. useId gives unique ids for label/aria linking (SSR safe)
function Field({ label, error, ...props }) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id}>{label}</label>   {/* htmlFor, not "for" */}
      <input id={id} aria-invalid={!!error} aria-describedby={error ? id + '-e' : undefined} {...props} />
      {error && <p id={id + '-e'} role="alert">{error}</p>}
    </div>
  );
}

// 2. Icon button
<button aria-label="Close dialog" onClick={close}><XIcon aria-hidden="true" /></button>

// 3. Route change focus management (SPA): move focus to h1 after navigation
function Page() {
  const h1 = useRef(null);
  useEffect(() => { h1.current?.focus(); }, []);
  return <h1 ref={h1} tabIndex={-1}>Orders</h1>;
}

// 4. Tailwind helpers: sr-only, focus-visible:ring-2, motion-reduce:transition-none
<button className="focus-visible:ring-2 focus-visible:ring-blue-600 motion-reduce:transition-none">Save</button>

// 5. Tools: eslint-plugin-jsx-a11y (built into Next.js lint), @axe-core/react,
//    React Testing Library queries by role (getByRole) encourage accessible markup.
// 6. Modals: use native <dialog> or a library (Radix UI, React Aria, Headless UI)
//    that handle focus trap, Esc and aria for you.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is WCAG and what are its four principles?**
A1: WCAG is the W3C standard for web accessibility. Its principles are POUR: Perceivable (users can sense content), Operable (usable with keyboard/other inputs), Understandable (clear, predictable), Robust (works with assistive tech). Conformance levels are A, AA (common legal target), AAA.

**Q2: What colour contrast is required for AA?**
A2: 4.5:1 for normal text, 3:1 for large text (18pt or 14pt bold) and for UI components and graphical objects. Check with DevTools or a contrast checker.

**Q3: When should you use ARIA?**
A3: Only when native HTML cannot express the semantics. The first rule of ARIA: prefer native elements (`<button>`, `<nav>`, `<dialog>`). Wrong ARIA is worse than none: `role="button"` on a div still needs tabindex and key handling.

**Q4: How do you make a custom modal accessible?**
A4: Use `role="dialog"` with `aria-modal="true"` and `aria-labelledby` (or the native `<dialog>` with `showModal()`), move focus inside on open, trap Tab within, close on Esc, and return focus to the trigger on close. Make background inert.

**Q5: How do you test accessibility?**
A5: Automated (Lighthouse, axe, WAVE) catch roughly a third of issues; then manual: keyboard-only navigation, screen reader (VoiceOver, NVDA), 200% zoom, contrast, and reduced-motion checks. Add jsx-a11y lint and axe in CI.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Removing the focus outline
```css
/* WRONG */
*:focus { outline: none; }
/* CORRECT */
:focus-visible { outline: 3px solid #1a73e8; outline-offset: 2px; }
```

❌ **Mistake 2:** Clickable div
```html
<!-- WRONG: not focusable, no role -->
<div onclick="buy()">Buy</div>
<!-- CORRECT -->
<button type="button" onclick="buy()">Buy</button>
```

❌ **Mistake 3:** Placeholder as the only label
```html
<!-- WRONG: label disappears while typing -->
<input placeholder="Email">
<!-- CORRECT -->
<label for="e">Email</label><input id="e" type="email">
```

❌ **Mistake 4:** Wrong alt text
```html
<!-- WRONG -->
<img src="logo.png" alt="image">
<!-- CORRECT: describe purpose; decorative -> empty alt -->
<img src="logo.png" alt="Swiggy home"> <img src="line.png" alt="">
```

❌ **Mistake 5:** `<html>` without `lang`
✅ **Correct way:** `<html lang="en">`, and `lang="hi"` on Hindi content.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WCAG | W3C accessibility standard | Accessibility का मानक |
| POUR | Perceivable, Operable, Understandable, Robust | चार सिद्धांत |
| ARIA | Attributes adding semantics for assistive tech | Assistive tech के लिए attributes |
| Screen reader | Reads screen aloud | स्क्रीन पढ़कर सुनाने वाला software |
| Contrast ratio | Text vs background difference | Text-background का अंतर |
| Focus indicator | Shows keyboard position | Keyboard कहाँ है यह दिखाना |
| Skip link | Jump past navigation | Navigation छोड़कर आगे जाना |
| Landmark | Semantic region (nav, main) | Page का semantic हिस्सा |
| Live region | Announces dynamic changes | बदलाव की घोषणा |

---

## ⚡ 3-Line Summary
**English:**
1. WCAG's POUR principles (Perceivable, Operable, Understandable, Robust) at level AA are the practical target.
2. Use semantic HTML first: labels, alt text, headings, landmarks, real buttons, visible focus, 4.5:1 contrast, and keyboard support.
3. Test with keyboard, screen reader and axe/Lighthouse; in React use jsx-a11y, `useId`, Radix/React Aria, and `sr-only`/`focus-visible` in Tailwind.

**Hindi:**
1. WCAG के POUR सिद्धांत और level AA व्यावहारिक लक्ष्य हैं।
2. पहले semantic HTML: label, alt, headings, landmarks, असली button, दिखने वाला focus, 4.5:1 contrast, keyboard support।
3. Keyboard, screen reader और axe/Lighthouse से test करो; React में jsx-a11y, `useId`, Radix/React Aria, Tailwind में `sr-only`/`focus-visible`।

---

## ➡️ Next Topic
**42. Open Graph Meta Tags** — अब सीखें कि link share करने पर WhatsApp/LinkedIn पर सुंदर preview कैसे दिखे।
