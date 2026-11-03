# 45. Shadow DOM Basics
# हिंदी में: Shadow DOM — Component के अंदर छिपा हुआ अलग DOM

---

## 🔵 Simple Definition (English)
**Shadow DOM** is a browser feature that attaches a separate, **encapsulated DOM tree** to an element (the *host*). Styles and markup inside the shadow root do not leak out, and outside page styles do not leak in. It is one of the three Web Components standards, along with **Custom Elements** and **HTML templates**.

## 🔵 सरल परिभाषा (Hindi)
**Shadow DOM** browser का feature है जो किसी element (*host*) से एक अलग, **encapsulated DOM tree** जोड़ता है। Shadow root के अंदर के styles और markup बाहर नहीं निकलते, और बाहर के page styles अंदर नहीं आते। यह Web Components के तीन standards में से एक है, बाकी दो हैं **Custom Elements** और **HTML templates**।

---

## 🔴 Problem it Solves
```
PROBLEM (global CSS and DOM):
  - A widget's `.title { color: red }` accidentally restyles the whole site
  - Site CSS `button { ... }` breaks the third-party widget you embed
  - document.querySelector('.btn') can grab internal parts of a widget
  - Class-name collisions (hence BEM, CSS Modules, naming hacks)

SOLUTION:
  - Real browser-level encapsulation: scoped CSS and scoped DOM
  - Reusable widgets (video player, chat bubble, payment button) that work
    on any site without style conflicts

NATIVE EXAMPLES: <video controls>, <input type="range">, <details> have
their internals in a (user-agent) shadow tree.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या (global CSS और DOM):
  - किसी widget का `.title { color: red }` पूरी site को बदल देता है
  - Site का `button { ... }` आपके embed किए widget को बिगाड़ देता है
  - document.querySelector('.btn') widget के अंदरूनी हिस्से पकड़ लेता है
  - Class नामों का टकराव (इसीलिए BEM, CSS Modules)

हल:
  - Browser-level encapsulation: CSS और DOM दोनों scoped
  - Video player, chat widget, payment button जैसे reusable parts जो किसी भी site पर बिना टकराव चलें

असली उदाहरण: <video controls> और <input type="range"> के अंदरूनी हिस्से shadow tree में हैं।
```

---

## 🟢 How it Works — Step by Step

```
LIGHT DOM (normal)               SHADOW DOM (encapsulated)

 <my-card>   <-- host element     #shadow-root (open)
   "Hello"   <-- light children      <style> ... </style>   (scoped!)
                                      <div class="card">
                                        <slot></slot>   <-- light children appear here
                                      </div>

STEPS:
  1. Pick a host:     const host = document.querySelector('#box');
  2. Attach a root:   const root = host.attachShadow({ mode: 'open' });
       mode 'open'   -> host.shadowRoot gives access from outside JS
       mode 'closed' -> host.shadowRoot is null (not real security)
  3. Fill it:         root.innerHTML = '<style>p{color:red}</style><p>Hi</p>';
  4. The <style> applies ONLY inside root. Page CSS does not reach inside.

WHAT CROSSES THE BOUNDARY:
  - Inherited properties (color, font-family, line-height...) DO inherit in
  - CSS custom properties (--brand: blue) DO pass in -> theming API
  - ::part(name)  lets outside CSS style elements that have part="name"
  - <slot>        projects the host's light DOM children into the shadow tree
  - :host / :host(.class) / :host-context()   style the host from inside
  - ::slotted(span) styles slotted light-DOM nodes from inside
  - Events: bubble out; with composed:true they cross the boundary.
    From outside, event.target is retargeted to the host.

CUSTOM ELEMENT + SHADOW DOM:
  class MyCard extends HTMLElement {
    constructor(){ super(); this.attachShadow({mode:'open'}); }
    connectedCallback(){ this.shadowRoot.innerHTML = `...`; }
  }
  customElements.define('my-card', MyCard);   // name must contain a hyphen

DECLARATIVE SHADOW DOM:
  <div><template shadowrootmode="open"> ... </template></div>
  Allows server-rendered shadow DOM (supported in current major browsers).

LIMITS: document.querySelector cannot see inside; forms and a11y need care;
global CSS (Tailwind classes) will not style shadow content.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Light DOM = normal DOM। Shadow DOM = host element से जुड़ा अलग tree।

Steps:
  1. Host चुनो: const host = document.querySelector('#box')
  2. Root जोड़ो: host.attachShadow({ mode: 'open' })
       open   -> host.shadowRoot से बाहर से access
       closed -> shadowRoot null (यह असली security नहीं है)
  3. अंदर content डालो: root.innerHTML = '<style>p{color:red}</style><p>Hi</p>'
  4. <style> सिर्फ root के अंदर लगता है, बाहर का CSS अंदर नहीं आता।

Boundary के पार क्या जाता है:
  - Inherited properties (color, font-family) अंदर जाती हैं
  - CSS variables (--brand) अंदर जाते हैं -> theming का तरीका
  - ::part() से बाहर का CSS चुने हुए अंदरूनी हिस्सों को style कर सकता है
  - <slot> host के children को shadow tree में दिखाता है
  - :host और ::slotted() अंदर से host/slotted को style करते हैं
  - Events बाहर आते हैं (composed: true चाहिए); बाहर से event.target host दिखता है।

Custom element का नाम hyphen वाला होना चाहिए (my-card)।
सीमा: Tailwind जैसी global CSS shadow के अंदर नहीं लगती।
```

---

## 🟡 Real World Example
**YouTube/Twitter embeds and chat widgets (Intercom-style):** a third-party chat bubble placed on your Swiggy-like site must not inherit your site's `button` styles and your CSS must not break it, so such widgets render inside a shadow root. **YouTube's own web app** is built with Polymer/Lit web components. Browsers themselves use it: the native `<video>` controls. **Salesforce Lightning** and **Adobe Spectrum** ship design systems as Web Components.

## 🟡 Real Example Hindi mein
**YouTube/Twitter embeds और chat widgets (Intercom जैसे):** आपकी Swiggy जैसी site पर रखा third-party chat bubble आपके `button` styles नहीं लेना चाहिए और आपका CSS उसे बिगाड़ना नहीं चाहिए, इसलिए ऐसे widgets shadow root में render होते हैं। **YouTube का web app** खुद Polymer/Lit web components से बना है। Browser खुद भी इसे use करता है: native `<video>` के controls। **Salesforce Lightning** और **Adobe Spectrum** अपने design systems Web Components में देते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shadow DOM Demo</title>
  <style>
    /* GLOBAL page CSS: tries to style every button and p */
    body { font-family: system-ui, sans-serif; padding: 20px; color: #333; }
    button { background: crimson; color: white; padding: 12px 20px; border: 0; }
    p { font-size: 22px; }

    /* Theming variable defined outside: it CROSSES the shadow boundary */
    profile-card { --accent: #1976d2; }
    profile-card.alt { --accent: #2e7d32; }

    /* ::part lets the outside style an exposed internal element */
    profile-card::part(avatar) { border: 3px solid orange; }
  </style>
</head>
<body>
  <h2>Normal DOM (global CSS applies)</h2>
  <button>Normal button (crimson from page CSS)</button>
  <p>Normal paragraph (22px from page CSS)</p>

  <h2>Shadow DOM component</h2>
  <!-- Light DOM children go into the <slot>s -->
  <profile-card>
    <span slot="name">Aditya R.</span>
    <span slot="role">Frontend Developer</span>
  </profile-card>

  <profile-card class="alt">
    <span slot="name">Priya S.</span>
    <span slot="role">Designer</span>
  </profile-card>

  <p id="out" style="font-size:14px"></p>

  <script>
    // Custom Element + Shadow DOM
    class ProfileCard extends HTMLElement {
      constructor() {
        super();
        // Create the shadow root ('open' = reachable via this.shadowRoot)
        this.attachShadow({ mode: 'open' });
      }

      connectedCallback() {
        // Template is scoped: these styles never leak out
        this.shadowRoot.innerHTML = `
          <style>
            /* :host styles the <profile-card> element itself */
            :host { display: block; margin: 12px 0; max-width: 320px;
                    border: 1px solid #ccc; border-radius: 10px; padding: 12px;
                    font-family: inherit; }
            /* Uses --accent from outside, with a fallback */
            h3 { margin: 0 0 4px; color: var(--accent, #555); }
            /* This 'button' rule affects ONLY the shadow tree, page CSS does not reach here */
            button { background: var(--accent, #555); color: #fff; border: 0;
                     padding: 6px 12px; border-radius: 6px; cursor: pointer; }
            /* Style slotted light-DOM content from inside */
            ::slotted([slot="role"]) { color: #666; font-size: 14px; }
            .avatar { width: 40px; height: 40px; border-radius: 50%;
                      background: #ddd; display: inline-block; }
          </style>
          <div class="avatar" part="avatar"></div>
          <h3><slot name="name">Unknown</slot></h3>
          <div><slot name="role"></slot></div>
          <button id="follow">Follow</button>
        `;

        this.shadowRoot.getElementById('follow').addEventListener('click', () => {
          // composed:true lets the event cross the shadow boundary
          this.dispatchEvent(new CustomEvent('follow', { bubbles: true, composed: true,
            detail: this.querySelector('[slot="name"]').textContent }));
        });
      }
    }

    // Name MUST contain a hyphen
    customElements.define('profile-card', ProfileCard);

    // Listen from outside
    document.addEventListener('follow', (e) => {
      document.getElementById('out').textContent = 'Followed: ' + e.detail;
    });

    // Encapsulation check: outside querySelector cannot see inside the shadow tree
    console.log('Outside sees inner button?', document.querySelector('#follow')); // null
    console.log('Via shadowRoot:', document.querySelector('profile-card').shadowRoot.querySelector('#follow'));
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. React does NOT use Shadow DOM; it uses the Virtual DOM + normal DOM.
//    Style scoping in React is by convention: CSS Modules, Tailwind, CSS-in-JS.

// 2. Using a Web Component inside React (React 19 supports custom elements fully;
//    older versions need refs for events/properties):
import './profile-card.js';           // registers <profile-card>

export default function App() {
  return (
    <profile-card class="alt">          {/* use "class" for custom elements in React 18 */}
      <span slot="name">Aditya R.</span>
    </profile-card>
  );
}

// 3. Wrapping a custom event in React 18:
// useEffect(() => { el.addEventListener('follow', handler); return () => el.removeEventListener('follow', handler); }, []);

// 4. Next.js: custom elements need the browser's customElements API, so
//    define them in a Client Component ('use client') / useEffect, or use
//    dynamic(() => import('./define'), { ssr: false }).

// 5. Render a React app INSIDE a shadow root (isolate widget CSS):
import { createRoot } from 'react-dom/client';
const host = document.getElementById('widget');
const shadow = host.attachShadow({ mode: 'open' });
const mount = document.createElement('div');
shadow.appendChild(mount);
createRoot(mount).render(<App />);   // styles must be injected into the shadow root

// 6. Tailwind classes do not reach into a shadow root unless you inject the
//    compiled CSS into it (adoptedStyleSheets or a <style>/<link> inside).
// 7. Libraries: Lit (lightweight Web Components), Stencil, react-shadow.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is Shadow DOM and why does it exist?**
A1: A browser feature that attaches an isolated DOM subtree to an element, giving real encapsulation of markup and CSS. It prevents style and ID/class collisions and lets reusable components work on any page. It is part of Web Components with Custom Elements and `<template>`.

**Q2: Open vs closed shadow root?**
A2: With `mode: 'open'`, JavaScript can reach the tree through `element.shadowRoot`. With `'closed'`, `shadowRoot` returns `null`. Closed is not a security boundary (can be bypassed), so open is the common choice.

**Q3: How can you style a shadow DOM component from outside?**
A3: Inherited properties (color, font) pass through; CSS custom properties pass through (theming); `::part()` styles elements the author exposed with the `part` attribute; slotted light-DOM content is styled by the page itself. Normal selectors cannot reach inside.

**Q4: What is a `<slot>`?**
A4: A placeholder inside a shadow tree where the host's light-DOM children are rendered (composition). Named slots (`slot="name"`) route specific children. Fallback content inside `<slot>` shows when nothing is provided.

**Q5: Do events cross the shadow boundary?**
A5: Most UI events (click) are composed and cross it, but are retargeted so that `event.target` seen outside is the host. Custom events must set `composed: true` (and `bubbles: true`) to escape.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Custom element name without a hyphen
```js
// WRONG
customElements.define('card', Card);
// CORRECT
customElements.define('my-card', Card);
```

❌ **Mistake 2:** Expecting page or Tailwind CSS to style shadow content
✅ **Correct way:** Use CSS variables, `::part()`, or inject the stylesheet into the shadow root.

❌ **Mistake 3:** Custom events that never leave the component
```js
// WRONG
this.dispatchEvent(new CustomEvent('follow'));
// CORRECT
this.dispatchEvent(new CustomEvent('follow', { bubbles: true, composed: true }));
```

❌ **Mistake 4:** Using `document.querySelector` to find inner nodes
✅ **Correct way:** `host.shadowRoot.querySelector(...)`.

❌ **Mistake 5:** Thinking `closed` mode protects secrets
✅ **Correct way:** Never put secrets in front-end DOM; treat it as encapsulation only.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shadow DOM | Encapsulated DOM tree | छिपा हुआ अलग DOM tree |
| Shadow host | Element holding the shadow root | Shadow root वाला element |
| Shadow root | Root of the shadow tree | Shadow tree की जड़ |
| Light DOM | Normal DOM children | सामान्य DOM children |
| Slot | Insertion point for light DOM | Light DOM डालने की जगह |
| :host | Selects host from inside | अंदर से host चुनता है |
| ::part() | Style exposed inner element | अंदर के चुने हिस्से को style |
| Custom Element | User-defined HTML tag | खुद का बनाया HTML tag |
| composed | Event crosses shadow boundary | Event का boundary पार करना |
| Web Components | Custom elements + Shadow DOM + template | Reusable components का standard |

---

## ⚡ 3-Line Summary
**English:**
1. Shadow DOM gives an element its own encapsulated DOM and CSS, created with `attachShadow()`.
2. Only inherited properties, CSS variables, `::part()` and slots cross the boundary; events need `composed: true`.
3. React does not use it, but can host web components or mount into a shadow root; Tailwind CSS must be injected inside.

**Hindi:**
1. Shadow DOM element को अपना encapsulated DOM और CSS देता है, `attachShadow()` से बनता है।
2. सिर्फ inherited properties, CSS variables, `::part()` और slots boundary पार करते हैं; events के लिए `composed: true` चाहिए।
3. React इसे use नहीं करता पर web components चला सकता है या shadow root में mount कर सकता है; Tailwind CSS अंदर inject करनी पड़ती है।

---

## ➡️ Next Topic
**46. What is CSS + How it Works** — HTML advanced पूरा। अब CSS की शुरुआत: browser CSS को कैसे पढ़कर page को style करता है।
