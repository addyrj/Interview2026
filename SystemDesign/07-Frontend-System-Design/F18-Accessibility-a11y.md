# F18. Accessibility (a11y)
# हिंदी में: Accessibility (सुलभता) — ऐप को ऐसा बनाना कि हर कोई इस्तेमाल कर सके: जो देख नहीं सकते (screen reader), जो mouse नहीं चला सकते (keyboard), कम रोशनी/कमज़ोर नज़र वाले, रंग-अंधता वाले, और बुज़ुर्ग

---

## 🔵 Simple Definition (English)
**Accessibility (a11y)** means designing and building products that **people with disabilities can perceive, operate and understand**: blind and low-vision users (screen readers like **NVDA, JAWS, VoiceOver, TalkBack**, zoom), motor-impaired users (keyboard only, switch devices), deaf users (captions), and people with cognitive differences.
The standard is **WCAG 2.2** (Web Content Accessibility Guidelines), levels A / **AA (usual target)** / AAA, built on 4 principles, **POUR**:
- **Perceivable**: text alternatives, captions, contrast
- **Operable**: keyboard access, focus, enough time, no seizure-inducing flashes
- **Understandable**: clear labels, predictable behaviour, error help
- **Robust**: works with assistive technologies (semantic HTML, correct ARIA)
In React Native, you use `accessibilityLabel`, `accessibilityRole`, `accessibilityState` etc., which map to VoiceOver/TalkBack.

## 🔵 सरल परिभाषा (Hindi)
Accessibility = ऐप ऐसा बनाना कि विकलांग लोग भी इसे समझ और चला सकें — न देख पाने वाले (screen reader: VoiceOver, TalkBack), सिर्फ़ keyboard वाले, कम सुनने वाले (captions), कमज़ोर नज़र या रंग-अंधता वाले।
मानक WCAG 2.2 (आम लक्ष्य AA) — 4 सिद्धांत POUR: समझ में आए (Perceivable), चलाया जा सके (Operable), समझना आसान (Understandable), assistive tools के साथ चले (Robust)।

---

## 🔴 Problem it Solves
- About **1 in 6 people globally (WHO estimate)** lives with a significant disability. India alone has tens of millions of people with disabilities, plus a large ageing population.
- Inaccessible UIs **lock out users**: an unlabeled icon button is silent to a screen reader, a custom dropdown that doesn't work with the keyboard, a red/green-only error state, a modal that traps or loses focus.
- **Legal requirements**: ADA (US), European Accessibility Act (EU, in force from 2025), and India's **Rights of Persons with Disabilities Act 2016** plus GIGW guidelines for government sites. Lawsuits against inaccessible websites are common in the US.
- Accessibility also improves **SEO, mobile usability, and UX for everyone** (captions in noisy trains, keyboard power users, large tap targets).

## 🔴 यह क्यों बना? (Hindi)
दुनिया में लगभग हर 6 में से 1 व्यक्ति किसी गंभीर विकलांगता के साथ जीता है (WHO); भारत में करोड़ों लोग, और बढ़ती बुज़ुर्ग आबादी। बिना label का icon button screen reader पर चुप रहता है, keyboard से न चलने वाला dropdown, सिर्फ़ लाल/हरे रंग से error — ये लोगों को बाहर कर देते हैं।
क़ानून भी माँगता है (US ADA, EU Accessibility Act, भारत का RPwD Act 2016 और GIGW); साथ ही a11y से SEO, mobile UX और सबका अनुभव बेहतर होता है।

---

## 🟢 How it Works — Step by Step

### How assistive tech "sees" your page

```
DOM ──► Accessibility Tree (role, name, state, value for each node) ──► Screen reader speaks:
<button aria-pressed="true">Veg only</button>   →  "Veg only, toggle button, pressed"
<div onclick=...>Veg only</div>                  →  "Veg only" (no role, not focusable, not operable) ❌
<img src="biryani.jpg">                          →  "biryani dot jpg, image" ❌
<img src="biryani.jpg" alt="Hyderabadi chicken biryani">  → meaningful ✅ ; decorative: alt="" ✅
```

### The checklist (what to say in interviews)

```
1. Semantic HTML first: <button>, <a href>, <nav>, <main>, <header>, <ul>/<li>, <label>, <table>,
   headings in order (h1 → h2 → h3). "No ARIA is better than bad ARIA."
2. Names for everything interactive: visible label, aria-label for icon-only buttons, alt text for images
3. Keyboard: everything works with Tab / Shift+Tab / Enter / Space / Esc / arrow keys; visible focus ring
   (:focus-visible), logical tab order, no keyboard traps, "Skip to main content" link
4. Focus management: modals move focus inside, trap it, return focus on close; route changes move focus
   to the new page heading; don't lose focus when content re-renders
5. Colour & contrast: text ≥ 4.5:1 (large text ≥ 3:1), UI components ≥ 3:1; never colour alone for meaning
6. Forms: <label for>, required + aria-invalid + aria-describedby error messages, errors announced,
   autocomplete attributes (autocomplete="one-time-code" for OTP)
7. Dynamic content: aria-live="polite" for toasts/cart updates, role="alert" for urgent errors,
   aria-busy for loading regions
8. Motion: respect prefers-reduced-motion; no flashing > 3 per second
9. Zoom & reflow: works at 200% zoom and 320 px width; don't disable pinch zoom; relative units (rem)
10. Media: captions for video, transcripts for audio
11. Touch targets ≥ 24×24 px (WCAG 2.2 AA minimum); 44–48 px recommended on mobile
12. Language: <html lang="hi"> or lang="en"; lang attribute on mixed-language snippets for correct pronunciation
```

### ARIA rules of thumb

```
- Use native elements when possible (they bring keyboard + roles for free)
- If building custom widgets (combobox, tabs, menu, dialog), follow WAI-ARIA Authoring Practices patterns
- ARIA changes semantics only — it doesn't add behaviour (role="button" still needs tabindex + key handlers)
- Common attributes: aria-label, aria-labelledby, aria-describedby, aria-expanded, aria-controls,
  aria-selected, aria-pressed, aria-current="page", aria-live, aria-hidden="true" (decorative)
- Never aria-hidden on focusable elements
```

### Testing a11y

```
Automated (catches ~30–40% of issues): axe-core (jest-axe, @axe-core/playwright), Lighthouse, eslint-plugin-jsx-a11y
Manual: keyboard-only walkthrough, screen reader (VoiceOver macOS/iOS, NVDA Windows, TalkBack Android),
        zoom 200%, high contrast / dark mode, colour-blindness simulators
Include users with disabilities in usability testing; add a11y acceptance criteria to tickets
```

### React Native accessibility

```
accessible, accessibilityLabel, accessibilityHint, accessibilityRole="button|header|link|image|switch",
accessibilityState={{ disabled, selected, checked, expanded }}, accessibilityValue, accessibilityLiveRegion
(Android), AccessibilityInfo.announceForAccessibility(), importantForAccessibility, hitSlop for larger targets,
respect AccessibilityInfo.isReduceMotionEnabled() and font scaling (allowFontScaling, maxFontSizeMultiplier)
(RN 0.71+ also supports aria-* and role props aliases)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Browser DOM से accessibility tree बनाता है (role, नाम, state); screen reader वही बोलता है — `<button>` बोलेगा "button", पर `<div onclick>` कुछ नहीं; image का `alt` नहीं तो file का नाम बोलेगा।
2. सबसे पहले सही HTML: button, a, nav, main, label, headings क्रम में; icon वाले बटन पर `aria-label`; सजावटी image पर `alt=""`।
3. Keyboard से सब चले (Tab, Enter, Space, Esc, arrows), focus ring दिखे; modal खुले तो focus अंदर, बंद हो तो वापस; route बदले तो नए heading पर focus।
4. Contrast कम से कम 4.5:1, सिर्फ़ रंग से मतलब नहीं (error में icon + text भी); form errors `aria-invalid` + `aria-describedby`; toast/cart बदलाव `aria-live` से घोषित।
5. Motion कम करने की setting मानो, 200% zoom पर चले, touch target बड़े (44–48 px); RN में `accessibilityLabel/Role/State`; जाँच: axe/Lighthouse + keyboard + VoiceOver/TalkBack से हाथ से।

---

## 🟡 Real World Example

**Domino's Pizza v. Robles (US, 2019)** — the US Supreme Court declined to hear Domino's appeal, leaving in place a ruling that its website and app had to be accessible to a blind user under the ADA. It's a landmark case that pushed companies to prioritize a11y.

**Apple / Google** — VoiceOver and TalkBack are built in, and both platforms review accessibility in their own apps. Apple's Human Interface Guidelines and Material Design specify contrast, touch targets and labels.

**GOV.UK and India's GIGW** — government digital services must meet accessibility standards. GOV.UK's design system is a well-known accessible component reference.

**GitHub, Shopify Polaris, Atlassian design systems** — bake a11y into components (focus management, ARIA patterns, contrast tokens), so every product team gets accessible defaults (Topic F20).

## 🟡 Real Example Hindi में
Domino's v. Robles (US, 2019) — Supreme Court ने Domino's की अपील सुनने से मना किया; एक नेत्रहीन यूज़र के लिए website/app accessible बनाना ज़रूरी रहा — इसके बाद कंपनियों ने a11y को गंभीरता से लिया।
भारत में सरकारी साइटों के लिए GIGW दिशानिर्देश; Apple/Google में VoiceOver/TalkBack built-in; GitHub, Shopify Polaris जैसे design systems हर component में a11y पहले से डालते हैं।

---

## 🟠 My Stack Example

### Accessible icon button, toggle and live cart update (React)
```tsx
<button type="button" aria-label="Add Paneer Tikka to cart" onClick={add}>
  <PlusIcon aria-hidden="true" />
</button>

<button type="button" aria-pressed={vegOnly} onClick={() => setVegOnly(!vegOnly)}>Veg only</button>

<div aria-live="polite" className="sr-only">{lastAdded && `${lastAdded} added. Cart has ${count} items.`}</div>
```
```css
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
:focus-visible { outline: 3px solid #1a73e8; outline-offset: 2px; }   /* never remove focus without replacement */
@media (prefers-reduced-motion: reduce) { * { animation-duration: .01ms !important; transition-duration: .01ms !important; } }
```

### Accessible form with errors (OTP login)
```tsx
<form onSubmit={submit} noValidate>
  <label htmlFor="phone">Mobile number</label>
  <input id="phone" type="tel" inputMode="numeric" autoComplete="tel-national" required
         aria-invalid={!!errors.phone} aria-describedby={errors.phone ? 'phone-err' : undefined} />
  {errors.phone && <p id="phone-err" role="alert">Enter a valid 10-digit mobile number</p>}

  <label htmlFor="otp">OTP</label>
  <input id="otp" inputMode="numeric" autoComplete="one-time-code" maxLength={6} />
  <button type="submit">Verify</button>
</form>
```

### Modal dialog: use native <dialog> (focus trap + Esc built in) or a tested library
```tsx
function ConfirmDialog({ open, onClose, onConfirm }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const opener = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (open) { opener.current = document.activeElement as HTMLElement; ref.current?.showModal(); }
    else { ref.current?.close(); opener.current?.focus(); }          // return focus to trigger
  }, [open]);
  return (
    <dialog ref={ref} aria-labelledby="dlg-title" onClose={onClose}>
      <h2 id="dlg-title">Remove item from cart?</h2>
      <button onClick={onConfirm}>Remove</button>
      <button onClick={onClose} autoFocus>Cancel</button>
    </dialog>
  );
}
// Libraries: Radix UI, React Aria (Adobe), Headless UI — accessible primitives (combobox, menu, tabs)
```

### Focus on route change (SPA)
```tsx
// After navigation, move focus to the main heading so screen readers announce the new page
useEffect(() => { document.querySelector<HTMLElement>('main h1')?.focus(); }, [pathname]);
// <h1 tabIndex={-1}>Your orders</h1>
```

### Automated checks in tests & CI
```ts
// Component test (Vitest/Jest + jest-axe)
import { axe } from 'jest-axe';
it('cart drawer has no a11y violations', async () => {
  const { container } = render(<CartDrawer open items={items} />);
  expect(await axe(container)).toHaveNoViolations();
});
// E2E (Playwright)
import AxeBuilder from '@axe-core/playwright';
const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
expect(results.violations).toEqual([]);
```

### React Native
```tsx
<Pressable
  onPress={() => addToCart(item.id)}
  accessibilityRole="button"
  accessibilityLabel={`Add ${item.name}, ${item.price} rupees`}
  accessibilityHint="Adds this item to your cart"
  accessibilityState={{ disabled: !item.available }}
  hitSlop={12}                                            // bigger touch target
  style={{ minHeight: 48, minWidth: 48 }}>
  <Text allowFontScaling maxFontSizeMultiplier={1.8}>ADD</Text>
</Pressable>

// Announce async results
AccessibilityInfo.announceForAccessibility('Order placed. Arriving in 30 minutes');
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make a custom dropdown/combobox accessible?**
A1: Prefer a native `<select>` or a proven accessible library (React Aria, Radix, Headless UI). If building one, follow the WAI-ARIA combobox pattern: the input has `role="combobox"`, `aria-expanded`, `aria-controls` pointing at the listbox and `aria-activedescendant` for the highlighted option; the listbox has `role="listbox"` and options have `role="option"` with `aria-selected`. Support the keyboard (arrows to move, Enter to select, Esc to close, typing to filter, Tab to leave), keep focus on the input, announce result counts with a live region, and ensure contrast and visible focus.

**Q2: What's your a11y checklist for a new feature?**
A2: Semantic HTML and a heading structure. Accessible names for all controls (labels, alt text, aria-label for icon buttons). Full keyboard operability with visible focus and logical order. Focus management for dialogs and route changes. Colour contrast meeting AA, and no colour-only meaning. Labeled forms with associated, announced errors. Live regions for dynamic updates. Respect for reduced motion. Support for zoom and reflow plus adequate touch targets. Then testing with axe/Lighthouse, keyboard-only use and a real screen reader.

**Q3: When should you use ARIA?**
A3: Only when native HTML can't express the semantics or state: custom widgets (tabs, comboboxes, tree views), live regions, describing relationships (`aria-describedby`, `aria-controls`) and states (`aria-expanded`, `aria-pressed`, `aria-current`). The first rule of ARIA is to use a native element if one exists, because ARIA doesn't add keyboard behaviour or focusability, and incorrect ARIA can make things worse than none. Follow the WAI-ARIA Authoring Practices patterns.

**Q4: How do you handle accessibility in an infinite scroll feed or SPA?**
A4: Use `role="feed"` with article items, `aria-busy` while loading, and polite announcements for new content without moving focus. Provide a "Load more" alternative and keyboard paths to skip past the feed (to the footer). Keep focus stable when content is inserted, and restore position on back navigation. In SPAs, on route change update the document title and move focus to the main heading (or announce the new page) so screen-reader users know navigation happened.

**Q5: How do you test accessibility at scale?**
A5: Combine automated checks (eslint-plugin-jsx-a11y in the editor, jest-axe in unit tests, axe-core in Playwright E2E and Lighthouse CI on PRs) with manual testing (keyboard-only, VoiceOver, NVDA, TalkBack, zoom, contrast tools) on critical flows. Build accessible components into the design system so teams inherit them, add a11y acceptance criteria to tickets, train engineers and designers, run periodic audits, and include users with disabilities in research.

---

## 🔷 Trade-offs
✅ Larger audience, legal compliance, better SEO and UX for everyone.
❌ Extra design/dev/testing effort — cheapest when built into the design system from day one, expensive to retrofit.
❌ Automated tools catch only a fraction → manual testing still required.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| a11y | Accessibility (11 letters between a and y) | सुलभता |
| WCAG | Web accessibility guidelines | वेब सुलभता नियम |
| Screen reader | Software reading UI aloud | स्क्रीन पढ़कर सुनाने वाला |
| Accessibility tree | Semantic tree for assistive tech | सहायक tools का पेड़ |
| ARIA | Attributes adding semantics | अर्थ जोड़ने वाले attributes |
| Accessible name | What AT announces for an element | element का बोला जाने वाला नाम |
| Focus management | Controlling keyboard focus | keyboard focus संभालना |
| Contrast ratio | Text vs background luminance ratio | रंगों का अंतर अनुपात |
| Live region | Announces dynamic updates | बदलाव की घोषणा |
| Reduced motion | User preference for less animation | कम animation की पसंद |

---

## ⚡ 3-Line Summary
**English:**
1. a11y = usable by everyone (screen reader, keyboard, low vision); target WCAG 2.2 AA using POUR principles.
2. Semantic HTML first, accessible names, keyboard + visible focus, focus management, contrast, labeled forms, live regions, reduced motion.
3. Test with axe/Lighthouse + keyboard + real screen readers; bake it into the design system; in RN use accessibilityRole/Label/State.

**Hindi:**
1. a11y = सबके लिए इस्तेमाल लायक; WCAG 2.2 AA लक्ष्य, POUR सिद्धांत।
2. सही HTML, हर control का नाम, keyboard + focus, contrast, form labels, live regions, कम motion।
3. axe/Lighthouse + keyboard + असली screen reader से जाँच; design system में डालो; RN में accessibilityRole/Label/State।

---

## ➡️ Next Topic Suggestion
**F19. Internationalization (i18n)** — Indian apps must speak Hindi, Tamil, Bengali and more, plus handle ₹ formatting, dates and plurals. Next: i18n architecture, translations, locale formatting, RTL, and loading translations efficiently.
