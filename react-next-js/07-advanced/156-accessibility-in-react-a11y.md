# 156. Accessibility in React (a11y)
# हिंदी में: React में Accessibility (a11y) — हर इंसान के लिए usable UI

---

## 🔵 Simple Definition (English)
**Accessibility (a11y)** means building your app so that everyone can use it, including people who use screen readers, keyboards only, voice control, zoom, or who have colour blindness or motor difficulties. In React this mostly means using semantic HTML, labels, focus management and ARIA only when needed.

## 🔵 सरल परिभाषा (Hindi)
**Accessibility (a11y)** का मतलब है अपना app ऐसे बनाना कि हर कोई उसे इस्तेमाल कर सके, जिनमें screen reader, सिर्फ keyboard, voice control या zoom इस्तेमाल करने वाले लोग और रंग-अंधता या हाथों की दिक्कत वाले लोग भी शामिल हैं। React में इसका मतलब ज़्यादातर semantic HTML, labels, focus management और ज़रूरत पड़ने पर ही ARIA इस्तेमाल करना है।

---

## 🔴 Problem it Solves

Many apps are built with `<div onClick>` everywhere. A mouse user sees a button, but a keyboard user cannot Tab to it, and a screen reader says nothing useful. Modals trap nobody, focus gets lost after a route change, form errors are only red text, and images have no description. About 1 in 6 people worldwide lives with some disability, and in many countries accessibility is also a legal requirement (for example the ADA in the US and EN 301 549 in the EU; India's RPwD Act and GIGW guidelines apply to government sites). Good accessibility also helps everyone: keyboard power users, people on bright sunlight, and SEO.

## 🔴 यह क्यों बना? (Hindi)
कई apps हर जगह `<div onClick>` से बनाए जाते हैं। Mouse user को बटन दिखता है, पर keyboard user उस पर Tab नहीं कर सकता और screen reader कुछ काम का नहीं बोलता। Modals में focus नहीं बँधता, route बदलने पर focus खो जाता है, form के errors सिर्फ लाल text होते हैं, और images का कोई विवरण नहीं होता। दुनिया में लगभग हर 6 में से 1 व्यक्ति किसी न किसी disability के साथ जीता है, और कई देशों में accessibility कानूनी ज़रूरत भी है (जैसे अमेरिका में ADA, EU में EN 301 549; भारत में RPwD Act और सरकारी sites के लिए GIGW guidelines)। अच्छी accessibility सबकी मदद करती है: keyboard power users, तेज़ धूप में फोन चलाने वाले, और SEO।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Use semantic HTML first: button, a, nav, main, h1-h6, ul/li, label, form
Step 2 → Every form control gets a label (label htmlFor / id, or aria-label)
Step 3 → Everything clickable must work with keyboard: Tab, Enter, Space, Esc, arrows
Step 4 → Images: meaningful alt text; decorative images alt=""
Step 5 → Manage focus: move focus into a modal, trap it there, restore it on close
Step 6 → Announce dynamic changes: aria-live regions, role="alert" for errors
Step 7 → Use ARIA only to fill gaps (role, aria-expanded, aria-controls); no ARIA is better than bad ARIA
Step 8 → Check colour contrast (WCAG AA: 4.5:1 for normal text) and do not rely on colour alone
Step 9 → Test: eslint-plugin-jsx-a11y, axe (jest-axe, Storybook a11y), keyboard only, a real screen reader

WCAG principles (POUR):  Perceivable · Operable · Understandable · Robust
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहले semantic HTML इस्तेमाल करो: button, a, nav, main, h1-h6, ul/li, label, form
Step 2 → हर form control को label दो (label htmlFor / id, या aria-label)
Step 3 → जो भी click होता है वह keyboard से भी चले: Tab, Enter, Space, Esc, arrows
Step 4 → Images: मतलब वाला alt text; सजावटी images के लिए alt=""
Step 5 → Focus संभालो: modal खुलने पर focus अंदर ले जाओ, वहीं बाँधो, बंद होने पर वापस लौटाओ
Step 6 → बदलावों की घोषणा करो: aria-live regions, errors के लिए role="alert"
Step 7 → ARIA सिर्फ कमी पूरी करने के लिए (role, aria-expanded, aria-controls); गलत ARIA से बेहतर है ARIA न होना
Step 8 → रंग का contrast जाँचो (WCAG AA: सामान्य text के लिए 4.5:1) और सिर्फ रंग पर निर्भर मत रहो
Step 9 → टेस्ट करो: eslint-plugin-jsx-a11y, axe (jest-axe, Storybook a11y), सिर्फ keyboard से, असली screen reader से

WCAG के सिद्धांत (POUR):  Perceivable · Operable · Understandable · Robust
```

---

## 🟡 Real World Example
**IRCTC / Swiggy checkout form.** A user with a screen reader opens the address form. If inputs have only placeholder text, the reader says "edit text, blank" with no idea what to type. With proper `<label>`s it says "Pincode, edit text". When the pincode is wrong, an error appears in `role="alert"`, so it is announced immediately. When the "Add address" modal opens, focus moves to its first field, Tab stays inside it, Esc closes it, and focus returns to the "Add address" button. A keyboard-only user can order food without touching the mouse.

## 🟡 Real Example Hindi mein
**IRCTC / Swiggy का checkout form।** Screen reader वाला user address form खोलता है। अगर inputs में सिर्फ placeholder है तो reader बोलता है "edit text, blank" और पता नहीं चलता क्या लिखना है। सही `<label>` हों तो वह बोलता है "Pincode, edit text"। Pincode गलत हो तो error `role="alert"` में आता है, इसलिए तुरंत सुनाई देता है। "Add address" modal खुलने पर focus उसके पहले field पर जाता है, Tab modal के अंदर ही रहता है, Esc से बंद होता है, और focus वापस "Add address" बटन पर लौटता है। सिर्फ keyboard वाला user mouse छुए बिना खाना order कर सकता है।

---

## 💻 Code Example — Basic

```jsx
// Basic accessible form: semantic HTML + labels + error announcement
import { useState, useId } from 'react';                  // useId makes unique, SSR-safe ids

export function PincodeForm({ onSubmit }) {
  const [pin, setPin] = useState('');                     // controlled input value
  const [error, setError] = useState('');                 // validation message
  const id = useId();                                     // unique id so label and input connect
  const errorId = `${id}-error`;                          // id for the error text

  function handleSubmit(e) {
    e.preventDefault();                                   // keep the page from reloading
    if (!/^\d{6}$/.test(pin)) {                           // Indian pincode = 6 digits
      setError('Pincode must be 6 digits');
      return;
    }
    setError('');
    onSubmit(pin);                                        // valid: tell the parent
  }

  return (
    <form onSubmit={handleSubmit} noValidate>             {/* a real form: Enter key submits */}
      <label htmlFor={id}>Pincode</label>                 {/* visible label tied to the input */}
      <input
        id={id}                                           // target of the label
        inputMode="numeric"                               // numeric keyboard on phones
        autoComplete="postal-code"                        // lets the browser autofill
        value={pin}
        onChange={(e) => setPin(e.target.value)}
        aria-invalid={error ? 'true' : 'false'}           // tells assistive tech the field is invalid
        aria-describedby={error ? errorId : undefined}    // reads the error with the field
      />
      {error && <p id={errorId} role="alert">{error}</p>} {/* announced immediately */}
      <button type="submit">Check delivery</button>       {/* real button: focusable, Enter/Space work */}
    </form>
  );
}
```

```jsx
// The classic mistake and its fix side by side
// WRONG: div acting as a button: no focus, no keyboard, no role
// <div className="btn" onClick={addToCart}>Add</div>

// RIGHT: a real button gets all of that for free
// <button type="button" onClick={addToCart}>Add</button>
```

## 💻 Code Example — Advanced

```jsx
// Accessible modal dialog: focus moves in, is trapped, Esc closes, focus returns
import { useEffect, useRef, useId } from 'react';
import { createPortal } from 'react-dom';                 // render outside the app root (avoids z-index/overflow issues)

export function Modal({ open, onClose, title, children }) {
  const dialogRef = useRef(null);                         // the dialog element
  const lastFocused = useRef(null);                       // who had focus before opening
  const titleId = useId();                                // links dialog to its title

  useEffect(() => {
    if (!open) return;                                    // do nothing while closed
    lastFocused.current = document.activeElement;         // remember the opener (for restore)
    const dialog = dialogRef.current;
    const selector = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const focusables = () => Array.from(dialog.querySelectorAll(selector)); // fresh list each time
    (focusables()[0] || dialog).focus();                  // move focus INTO the dialog

    function onKeyDown(e) {
      if (e.key === 'Escape') { onClose(); return; }      // Esc closes
      if (e.key !== 'Tab') return;                        // only handle Tab for the trap
      const items = focusables();
      if (items.length === 0) { e.preventDefault(); return; }
      const first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {   // Shift+Tab on first → wrap to last
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) { // Tab on last → wrap to first
        e.preventDefault(); first.focus();
      }
    }
    document.addEventListener('keydown', onKeyDown);      // listen while open
    document.body.style.overflow = 'hidden';              // stop background scrolling
    return () => {
      document.removeEventListener('keydown', onKeyDown); // cleanup listener
      document.body.style.overflow = '';                  // restore scroll
      lastFocused.current?.focus?.();                     // return focus to the opener
    };
  }, [open, onClose]);                                    // onClose should be stable (useCallback) in the parent

  if (!open) return null;                                 // closed: render nothing
  return createPortal(
    <div className="backdrop" onClick={onClose}>          {/* click outside closes (mouse convenience only) */}
      <div
        ref={dialogRef}
        role="dialog"                                     // announces "dialog"
        aria-modal="true"                                 // tells screen readers the rest is inert
        aria-labelledby={titleId}                         // dialog name comes from the title
        tabIndex={-1}                                     // focusable by script as fallback
        onClick={(e) => e.stopPropagation()}              // clicks inside do not close it
      >
        <h2 id={titleId}>{title}</h2>
        {children}
        <button type="button" onClick={onClose}>Close</button>
      </div>
    </div>,
    document.body
  );
}
// Tip: the native <dialog> element with showModal() gives focus trap, Esc and inert background
// for free in modern browsers, and is often the best choice.
```

```jsx
// Live region: announce "added to cart" to screen readers without moving focus
import { useState } from 'react';

export function CartButton({ item }) {
  const [message, setMessage] = useState('');             // text announced by the live region
  return (
    <>
      <button type="button" onClick={() => setMessage(`${item} added to cart`)}>
        Add {item}
      </button>
      {/* The region must exist in the DOM BEFORE the text changes to be announced reliably */}
      <p role="status" aria-live="polite" className="sr-only">{message}</p>
    </>
  );
}
```

---

## 🟠 Next.js Connection

Next.js helps with accessibility in several ways, but not automatically for everything:

- **Route announcer:** the App Router and Pages Router include a built-in route announcer that tells screen readers the new page title after client-side navigation. Give every page a unique `<title>` through the `metadata` export so it is meaningful.
- **`next/link`** renders a real `<a href>`, which keeps links keyboard and screen-reader friendly. Do not wrap a `<button>` in a link or use `router.push` on a div.
- **`next/image`** requires the `alt` prop. Use `alt=""` for decorative images.
- **ESLint:** `eslint-config-next` includes some `jsx-a11y` rules by default (a limited subset).
- **Server Components** render semantic HTML on the server, so content is available even before JavaScript loads.

```jsx
// app/layout.jsx : landmarks + skip link (a Server Component, no client JS needed)
export const metadata = { title: { default: 'FoodApp', template: '%s | FoodApp' } }; // unique page titles

export default function RootLayout({ children }) {
  return (
    <html lang="en">                                       {/* lang helps screen readers pronounce text */}
      <body>
        <a href="#main" className="skip-link">Skip to main content</a> {/* first Tab stop for keyboard users */}
        <header><nav aria-label="Main">{/* links */}</nav></header>      {/* landmark: navigation */}
        <main id="main" tabIndex={-1}>{children}</main>                  {/* landmark: main content */}
        <footer>{/* footer content */}</footer>
      </body>
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Clickable `div` or `span` instead of a real button or link
✅ **Correct:** Use `<button>` for actions and `<a>`/`<Link>` for navigation

```jsx
// Wrong: not focusable, no Enter/Space, no role
<div onClick={handleDelete}>Delete</div>

// Right
<button type="button" onClick={handleDelete}>Delete</button>
```

❌ **Mistake 2:** Placeholder used as the label, and missing or useless `alt`
✅ **Correct:** Visible labels, and meaningful (or empty) alt text

```jsx
// Wrong
<input placeholder="Email" />                      // disappears on typing; not a reliable label
<img src="/pizza.jpg" alt="image" />               // "image" says nothing

// Right
<label htmlFor="email">Email</label>
<input id="email" type="email" autoComplete="email" />
<img src="/pizza.jpg" alt="Margherita pizza with fresh basil" />
<img src="/divider.svg" alt="" />                  // decorative: skipped by screen readers
```

❌ **Mistake 3:** Removing the focus outline, and using ARIA that contradicts the element
✅ **Correct:** Keep a visible focus style, and do not add redundant or wrong roles

```jsx
// Wrong
// CSS: button:focus { outline: none; }               ← keyboard users lose their place
<button role="link" aria-label="">Buy</button>        // wrong role + empty label

// Right
// CSS: button:focus-visible { outline: 3px solid #1a73e8; outline-offset: 2px; }
<button type="button">Buy now</button>                // native semantics are enough
```

---

## 🧠 Tricky Interview Question

```jsx
function Toast({ message }) {
  return message ? <div role="alert">{message}</div> : null;   // rendered only when message exists
}
```
A screen-reader user sometimes does NOT hear the toast. Why, and what is the fix?

**Answer:** Live regions are announced when their **content changes inside a container that already exists** in the accessibility tree. Here the whole element is added together with its text, and some screen reader and browser combinations skip it (`role="alert"` is the most reliable of the live roles, but behaviour is inconsistent when the node is inserted fresh). The robust pattern is to render an always-present container (`<div role="status" aria-live="polite">`) and only change its text. Also, auto-dismissing toasts that disappear in 3 seconds can be too fast to read, so give users control over timing (WCAG 2.2.1 Timing Adjustable).

---

## ⚫ Interview Questions + Answers

Q1: What is the first rule of ARIA?
A1: Do not use ARIA if a native HTML element already provides the semantics. A `<button>` beats `<div role="button" tabIndex={0}>` plus key handlers. ARIA only changes what assistive tech is told; it adds no behaviour (no keyboard support, no focus).

Q2: How do you make a custom component such as a dropdown or tabs accessible?
A2: Use the right role and state attributes (`role="tablist"`, `aria-selected`, `aria-expanded`, `aria-controls`), support the expected keyboard patterns from the WAI-ARIA Authoring Practices (arrows, Home/End, Esc), manage focus, and test with a screen reader. Often it is easier to use an accessible headless library such as Radix UI, React Aria or Headless UI.

Q3: How do you manage focus in a single-page app?
A3: When content changes without a page load, move focus deliberately: into a modal on open and back to the trigger on close, to the new page heading (or `main`) after route change, and to the first invalid field after a failed submit. Use `ref.current.focus()` in an effect, and `tabIndex={-1}` to make non-interactive elements focusable by script.

Q4: How do you test accessibility in React?
A4: Combine layers: `eslint-plugin-jsx-a11y` for static checks, `jest-axe` or Storybook's a11y addon for automated axe rules, RTL queries by role/label (if `getByRole` finds it, it is exposed properly), Lighthouse or axe DevTools in the browser, and manual checks with keyboard and a screen reader (NVDA, VoiceOver). Automated tools catch only a portion of problems (commonly cited around 30-40%).

Q5: What are the WCAG levels and the colour contrast rule?
A5: WCAG has conformance levels A, AA and AAA, and most laws and companies target AA. For AA, normal text needs a contrast ratio of at least 4.5:1 with its background (3:1 for large text and UI components). Never use colour alone to convey meaning; add text or icons.

---

## 🔷 When to Use + When Not to Use
✅ **Use (always) when:**
- Building any interactive UI: forms, menus, modals, tables, carousels
- Making public or government, e-commerce, banking apps (often a legal need)
- Creating design-system components that many teams reuse

❌ **Avoid:**
- Adding ARIA everywhere "just in case" (wrong ARIA is worse than none)
- Treating a11y as a final-week task (fixes become expensive)
- Relying only on automated tools and skipping keyboard and screen-reader checks

**Re-render and performance note:** a11y features are cheap. `aria-*` attributes and labels do not cause extra renders by themselves. Focus management uses effects and refs, which do not trigger re-renders. Live regions that update on every keystroke can flood screen readers, so debounce announcements. Semantic HTML also means less JavaScript (a native `<button>` or `<dialog>` replaces custom key handling).

---

## 📊 Visual Diagram

```
   Your React JSX                 Browser                Assistive technology
   ──────────────                 ───────                ────────────────────
   <button>Add</button>   ──►  DOM  ──►  Accessibility tree  ──►  Screen reader:
   <label for=..>               (HTML)    role: button            "Add, button"
   <input aria-invalid>                   name: "Add"
                                          state: invalid
   Keyboard: Tab → focus order follows DOM order
             Enter/Space → activates button;  Esc → closes dialog

   Modal focus flow:
   [Open button] ─click─► [Focus in dialog] ─Tab loops inside─► ─Esc/Close─► [Focus back on Open button]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| a11y | Short for accessibility (a + 11 letters + y) | Accessibility का छोटा रूप |
| ARIA | Attributes that add accessibility semantics | Accessibility के अर्थ जोड़ने वाले attributes |
| Screen reader | Software reading the UI aloud | UI को बोलकर सुनाने वाला software |
| Semantic HTML | Elements that carry meaning (button, nav) | मतलब वाले HTML elements |
| Focus trap | Keeping Tab inside a dialog | Tab को dialog के अंदर ही रखना |
| Live region | Area whose changes are announced | जिस हिस्से के बदलाव सुनाए जाएँ |
| WCAG | Web Content Accessibility Guidelines | Web accessibility के दिशानिर्देश |
| Landmark | Page region (main, nav) for quick jumping | Page का हिस्सा जिस पर सीधे जा सकें |
| Contrast ratio | Brightness difference of text and background | Text और background की चमक का अंतर |

---

## ⚡ 3-Line Summary
**English:**
1. Accessibility means everyone can use your UI: keyboard, screen reader, zoom and good contrast.
2. Use semantic HTML and labels first, manage focus in modals and route changes, and add ARIA only to fill gaps.
3. Test with eslint-plugin-jsx-a11y, axe, RTL role queries, and by hand; in Next.js set unique page titles and use `next/link`.

**Hindi:**
1. Accessibility का मतलब है कि हर कोई आपका UI चला सके: keyboard, screen reader, zoom और अच्छा contrast।
2. पहले semantic HTML और labels इस्तेमाल करो, modals और route बदलने पर focus संभालो, और ARIA सिर्फ कमी भरने के लिए जोड़ो।
3. eslint-plugin-jsx-a11y, axe, RTL role queries और हाथ से टेस्ट करो; Next.js में हर page का अलग title रखो और `next/link` इस्तेमाल करो।

---

## ➡️ Next Topic
**157. Internationalization (i18n)** — Accessible app को सब भाषाओं के users तक पहुँचाना अगला कदम है: translations, तारीख, मुद्रा के format और RTL भाषाएँ कैसे संभालें, खासकर Hindi और English वाले भारतीय apps में।
