# 104. Container Queries
# हिंदी में: Container Queries — Parent की Size के हिसाब से Component बदलना

---

## 🔵 Simple Definition (English)
A **container query** (`@container`) applies styles based on the size of a **parent container**, not the browser window. You mark a parent with `container-type: inline-size`, then children can change layout when that parent becomes narrow or wide. This makes components truly reusable anywhere.

## 🔵 सरल परिभाषा (Hindi)
**Container query** (`@container`) styles को **parent container की size** के हिसाब से लगाता है, browser window के हिसाब से नहीं। Parent पर `container-type: inline-size` लगाते हैं, फिर children का layout तब बदलता है जब वो parent छोटा या बड़ा हो। इससे component कहीं भी reuse हो सकता है।

---

## 🔴 Problem it Solves
```
BEFORE (media queries only):
  A product card is placed in:
     - main area (800px wide)      -> horizontal layout looks good
     - sidebar   (250px wide)      -> same card must be vertical
  But @media (min-width: 768px) looks at the WINDOW (1400px), so
  the card in the sidebar also becomes horizontal and breaks.
  Devs wrote variants: .card--small, .card--wide, and passed props.

AFTER (container queries):
  The card asks "how wide is MY container?" and adapts itself.
  Same component works in sidebar, grid, modal, anywhere.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (सिर्फ media queries):
  Product card दो जगह लगा है:
     - main area (800px)    -> horizontal layout अच्छा लगता है
     - sidebar   (250px)    -> वही card vertical चाहिए
  पर @media (min-width: 768px) WINDOW (1400px) देखता है, इसलिए sidebar वाला card
  भी horizontal हो जाता है और टूट जाता है।
  Devs .card--small, .card--wide जैसे variants और props बनाते थे।

अब (container queries):
  Card पूछता है "मेरा container कितना चौड़ा है?" और खुद adapt होता है।
  वही component sidebar, grid, modal, कहीं भी ठीक चलता है।
```

---

## 🟢 How it Works — Step by Step

```
1. Choose the parent and declare it a query container:
       .wrapper { container-type: inline-size; }
   (optional name)  container-name: card;
   (shorthand)      container: card / inline-size;

2. Write a query that targets descendants of that container:
       @container (min-width: 400px) { .card { flex-direction: row; } }
       @container card (min-width: 400px) { ... }       /* named */

3. Browser measures the container's inline size (width in horizontal text)
   and applies the rules when the condition matches.

IMPORTANT DETAILS:
  - container-type: inline-size  -> query on width only (most common).
  - container-type: size         -> width AND height (needs explicit size).
  - The container applies "containment", so its own size can't depend on
    its children's width (layout/style/inline-size containment).
  - You cannot style the container itself with its own @container rule;
    only its descendants. Use a wrapper element.
  - Container units: cqw, cqh, cqi, cqb, cqmin, cqmax
       (1cqw = 1% of the container width) -> fluid fonts inside components.
  - Browser support: Chrome/Edge 105+, Safari 16+, Firefox 110+ (size queries).
  - Style queries (@container style(--theme: dark)) are newer; only custom
    properties in Chrome/Safari 18; Firefox limited. Check support first.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. Parent को query container घोषित करो:
       .wrapper { container-type: inline-size; }
   (नाम)      container-name: card;
   (shorthand) container: card / inline-size;

2. उस container के descendants के लिए query लिखो:
       @container (min-width: 400px) { .card { flex-direction: row; } }
       @container card (min-width: 400px) { ... }       /* named */

3. Browser container की inline size (width) नापता है और शर्त मिलने पर rules लगाता है।

ज़रूरी बातें:
  - container-type: inline-size -> सिर्फ width पर query (सबसे common)।
  - container-type: size        -> width और height दोनों (explicit size चाहिए)।
  - Container पर containment लगती है, इसलिए उसकी अपनी size children की width पर निर्भर नहीं हो सकती।
  - Container खुद को style नहीं कर सकता; सिर्फ descendants को। इसलिए wrapper element चाहिए।
  - Container units: cqw, cqh, cqi, cqb, cqmin, cqmax (1cqw = container width का 1%)।
  - Support: Chrome/Edge 105+, Safari 16+, Firefox 110+।
  - Style queries (@container style(...)) नए हैं; support सीमित, पहले check करें।
```

---

## 🟡 Real World Example
**Zomato / Swiggy restaurant card:** On the home page the card sits in a wide grid (image on the left, details on the right). In the "Similar restaurants" sidebar the very same card is narrow, so image goes on top and the rating wraps below. With container queries, one `RestaurantCard` component handles both without a `variant` prop.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy restaurant card:** Home page पर card चौड़े grid में है (image बाएँ, details दाएँ)। "Similar restaurants" sidebar में वही card पतला है, तो image ऊपर और rating नीचे आ जाती है। Container queries से एक ही `RestaurantCard` component बिना `variant` prop के दोनों जगह चलता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Container Queries Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f4f4f5; margin: 0; padding: 20px; }

    /* Page layout: main (wide) + sidebar (narrow) */
    .page { display: grid; grid-template-columns: 1fr 260px; gap: 20px; max-width: 1000px; margin: auto; }

    /* 1. DECLARE the container. Wrapper, not the card itself. */
    .card-slot {
      container-type: inline-size;   /* watch my width */
      container-name: card;          /* optional name */
    }

    /* 2. DEFAULT (narrow) layout: vertical stack */
    .card {
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #fff;
      border: 1px solid #e4e4e7;
      border-radius: 12px;
      padding: 12px;
    }
    .card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; border-radius: 8px; background: #fca5a5; }
    .card h3 { margin: 0; font-size: 1rem; }
    .card p  { margin: 4px 0 0; color: #52525b; font-size: .9rem; }
    .card .rating { background: #16a34a; color: #fff; padding: 2px 8px; border-radius: 6px; font-size: .8rem; }

    /* 3. WIDE container: horizontal layout (based on container, not window) */
    @container card (min-width: 420px) {
      .card { flex-direction: row; align-items: center; }
      .card img { width: 160px; flex-shrink: 0; }
      .card h3 { font-size: 1.25rem; }
    }

    /* 4. VERY wide: show extra info */
    .extra { display: none; }
    @container card (min-width: 640px) {
      .extra { display: block; margin-top: 8px; }
    }

    /* Container query units: heading scales with container width */
    .fluid-title { font-size: clamp(1rem, 4cqi, 1.75rem); }

    /* Fallback if the browser has no container query support */
    @supports not (container-type: inline-size) {
      .card { flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="page">
    <main>
      <h2>Main (wide)</h2>
      <div class="card-slot">
        <article class="card">
          <img alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
          <div>
            <h3 class="fluid-title">Biryani House <span class="rating">4.5</span></h3>
            <p>North Indian &middot; 30 min</p>
            <p class="extra">Free delivery above &#8377;199. Open till midnight.</p>
          </div>
        </article>
      </div>
    </main>

    <aside>
      <h2>Sidebar (narrow)</h2>
      <div class="card-slot">
        <!-- SAME markup, different container width -> different layout -->
        <article class="card">
          <img alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
          <div>
            <h3 class="fluid-title">Biryani House <span class="rating">4.5</span></h3>
            <p>North Indian &middot; 30 min</p>
            <p class="extra">Free delivery above &#8377;199. Open till midnight.</p>
          </div>
        </article>
      </div>
    </aside>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. One component, no "variant" or "isSidebar" prop needed.
export function RestaurantCard({ r }) {
  return (
    <div className="card-slot">          {/* container wrapper */}
      <article className="card">
        <img src={r.img} alt={r.name} />
        <div><h3>{r.name}</h3><p>{r.cuisine}</p></div>
      </article>
    </div>
  );
}
/* card.module.css uses  container-type: inline-size  on .card-slot
   and  @container (min-width: 420px) { ... }  on .card */

// 2. Tailwind v4 has built-in container query variants:
<div className="@container">
  <div className="flex flex-col @md:flex-row @lg:gap-6">...</div>
</div>
// For Tailwind v3 use the plugin: @tailwindcss/container-queries
//   <div className="@container"> <div className="@md:flex-row"> ...

// 3. Next.js Server Components: no JS is needed, so zero hydration cost,
//    unlike ResizeObserver or useMediaQuery hooks which need 'use client'.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between media queries and container queries?**
A1: Media queries look at the viewport (window, device, user preferences). Container queries look at the size of a specific ancestor container. So a component adapts to the space it is given, which is what matters for reusable components.

**Q2: How do you set up a container query?**
A2: (1) On the parent set `container-type: inline-size` (and optionally `container-name`). (2) Write `@container (min-width: 400px) { .child { ... } }`. The shorthand is `container: name / inline-size`.

**Q3: Why can't an element query itself?**
A3: To avoid infinite loops. If an element's size changed because of a query that depends on its own size, the browser could loop. So a container only affects its descendants, and it applies size containment so its inline size does not depend on its children.

**Q4: What are container query units?**
A4: `cqw`, `cqh`, `cqi`, `cqb`, `cqmin`, `cqmax` are percentage units relative to the container's width, height, inline size, block size etc. Example: `font-size: clamp(1rem, 4cqi, 2rem)` for fluid text inside a component.

**Q5: When should you still use media queries?**
A5: For page-level concerns: overall layout (sidebar collapsing), user preferences (`prefers-color-scheme`, `prefers-reduced-motion`), print, hover capability. Use container queries for component-level layout. They are often used together.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Trying to style the container itself in its own query
```css
/* WRONG: .box is the container and the target */
.box { container-type: inline-size; }
@container (min-width: 400px) { .box { padding: 2rem; } }  /* does nothing */

/* CORRECT: add a child or wrapper */
@container (min-width: 400px) { .box > .inner { padding: 2rem; } }
```

❌ **Mistake 2:** Forgetting that the container can collapse to zero width
```css
/* container-type: inline-size makes the element ignore its content's width.
   An inline element or a shrink-to-fit flex item can become 0 wide. */
/* CORRECT: give it a real width (block element, width: 100%, flex: 1) */
.card-slot { container-type: inline-size; width: 100%; }
```

❌ **Mistake 3:** Using `container-type: size` without a fixed height
```css
/* WRONG: height collapses to 0 */
/* CORRECT: use inline-size unless you really need height queries */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| @container | Rule applying styles by container size | Container की size पर rule |
| container-type | Declares an element as query container | Element को container बनाना |
| container-name | Names a container for targeting | Container का नाम |
| inline-size | Width in horizontal writing mode | Horizontal में width |
| cqi / cqw | Units relative to container size | Container के सापेक्ष units |
| containment | Isolation limiting layout dependency | Layout का isolation |

---

## ⚡ 3-Line Summary
**English:**
1. `@container` styles children based on a parent's size, so components adapt to where they are placed.
2. Set `container-type: inline-size` on a wrapper, then use `@container (min-width: ...)` on descendants.
3. Use media queries for page-level layout and container queries for reusable components; supported in all modern browsers.

**Hindi:**
1. `@container` parent की size के हिसाब से children को style करता है, इसलिए component अपनी जगह के हिसाब से बदलता है।
2. Wrapper पर `container-type: inline-size` लगाओ, फिर descendants पर `@container (min-width: ...)` लिखो।
3. Page-level layout के लिए media query और reusable components के लिए container query use करो; सभी modern browsers में चलता है।

---

## ➡️ Next Topic
**105. CSS Nesting (new feature)** — अब CSS में Sass जैसा nesting native लिखना सीखेंगे, ताकि इन @container और media rules को selector के अंदर ही रखा जा सके।
