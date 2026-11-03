# 30. HTML Template Tag
# हिंदी में: Template Tag — Clone होने वाला Hidden HTML

---

## 🔵 Simple Definition (English)
`<template>` holds HTML that is **parsed but not rendered**. Its content lives in an inert `DocumentFragment` (`template.content`): images do not load, scripts do not run, and it is invisible. You **clone** it with JavaScript whenever you need a new copy, for example one list item per data row.

## 🔵 सरल परिभाषा (Hindi)
`<template>` ऐसा HTML रखता है जो **parse होता है पर दिखता नहीं (render नहीं)**। इसका content एक inert `DocumentFragment` (`template.content`) में रहता है: images load नहीं होतीं, scripts नहीं चलते, और ये दिखता नहीं। जब भी नई copy चाहिए (जैसे हर data row के लिए एक list item) तब JavaScript से इसे **clone** करते हैं।

---

## 🔴 Problem it Solves
```
BEFORE <template>, to render 50 cards from JSON you had to:
  1. Build HTML with string concatenation:
       html += '<div class="card"><h3>' + item.name + '</h3></div>';
     -> ugly, error-prone, and DANGEROUS (innerHTML + user data = XSS)
  2. Or keep a hidden <div style="display:none"> with a sample card
     -> its images still download, ids duplicate, scripts run, screen readers may read it.
  3. Or build every element with createElement (very verbose).

WITH <template>:
  - Write real HTML markup once, in HTML (not in JS strings).
  - Browser parses it ONCE, then you clone it fast and fill the data with textContent (safe).
  - Nothing loads or runs until you clone and insert.
```

## 🔴 यह क्यों बना? (Hindi)
```
<template> से पहले JSON से 50 cards बनाने के लिए:
  1. String जोड़कर HTML बनाना: html += '<div>' + item.name + '</div>'
     -> भद्दा, गलती की संभावना, और खतरनाक (innerHTML + user data = XSS)
  2. या छुपा हुआ <div style="display:none"> रखना
     -> उसकी images फिर भी download होतीं, duplicate id, screen reader पढ़ सकता है।
  3. या हर element createElement से बनाना (बहुत लंबा code)।

<template> के साथ:
  - असली HTML markup एक बार HTML में लिखो (JS strings में नहीं)।
  - Browser एक बार parse करता है, आप तेज़ी से clone करके textContent से data भरते हैं (सुरक्षित)।
  - Clone और insert करने तक कुछ load/run नहीं होता।
```

---

## 🟢 How it Works — Step by Step

```
1. Write <template id="card-tpl"> ... markup ... </template> in HTML.
2. Browser parses it, but content goes into template.content (a DocumentFragment),
   NOT into the live DOM tree. It is inert and invisible.
3. In JS: const node = tpl.content.cloneNode(true);   // true = deep clone
4. Fill data:  node.querySelector('.title').textContent = item.title;   // safe from XSS
5. Insert:     container.append(node);   // fragment's children move into the page
6. Repeat steps 3-5 for each item. Use one fragment to batch inserts (fewer reflows).

IMPORTANT DETAILS:
  - Use cloneNode(true) not importNode in most cases (importNode needed for other documents).
  - After append(), the fragment is EMPTY (its children moved), so clone again for next item.
  - <template> may appear anywhere: head, body, even inside <table>/<select>
    (where normal <div> would be invalid).
  - <slot> element is used with templates in WEB COMPONENTS / Shadow DOM (topic 45).
  - Declarative Shadow DOM: <template shadowrootmode="open"> (supported in modern browsers,
    Chrome 111+, Safari 16.4+, Firefox 123+).
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. HTML में <template id="card-tpl"> ... markup ... </template> लिखो।
2. Browser इसे parse करता है, पर content live DOM में नहीं जाता,
   template.content (DocumentFragment) में रहता है। Inert और invisible।
3. JS में: const node = tpl.content.cloneNode(true);   // true = पूरी deep copy
4. Data भरो: node.querySelector('.title').textContent = item.title;   // XSS से सुरक्षित
5. Page में डालो: container.append(node);
6. हर item के लिए दोहराओ। Batch insert के लिए एक fragment use करो (reflow कम)।

ध्यान दें:
  - append() के बाद fragment खाली हो जाता है (children page में चले गए), अगला clone फिर से करो।
  - <template> <table> या <select> के अंदर भी रख सकते हैं जहाँ <div> invalid होता।
  - Web Components / Shadow DOM में <template> और <slot> साथ चलते हैं (topic 45)।
```

---

## 🟡 Real World Example
**Zomato / Swiggy restaurant list:** the API returns 20 restaurants as JSON. In a vanilla-JS version you define one `<template>` for a restaurant card (image, name, rating, ETA) and clone it 20 times, filling each with data. **Gmail** style inbox rows, **Instagram** comment lists and "load more" feeds, and **notification toasts** use the same pattern. Frameworks like React/Vue do this for you with components; `<template>` is the native browser version of the same idea.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy restaurant list:** API 20 restaurants का JSON देती है। Vanilla JS में restaurant card (image, name, rating, ETA) का एक `<template>` बनाते हैं और 20 बार clone करके हर एक में data भरते हैं। **Gmail** inbox rows, **Instagram** comments और "load more" feeds, और **notification toasts** भी यही pattern हैं। React/Vue components यही काम आपके लिए करते हैं; `<template>` उसी idea का native browser version है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Template Demo</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="page">
    <h1>Restaurants near you</h1>
    <button id="add">Load more</button>
    <ul id="list" class="list"></ul>
  </main>

  <!-- TEMPLATE: parsed but NOT rendered. Image will NOT download until cloned.
       Even the broken-looking src is harmless here. -->
  <template id="card-tpl">
    <li class="card">
      <img class="card__img" alt="" width="64" height="64">
      <div class="card__body">
        <h2 class="card__name"></h2>
        <p class="card__meta"></p>
      </div>
      <span class="card__rating"></span>
    </li>
  </template>

  <script>
    // Sample data (normally from fetch('/api/restaurants'))
    const data = [
      { name: 'Biryani House',  cuisine: 'Biryani, Mughlai', eta: 30, rating: 4.4 },
      { name: 'Pizza Corner',   cuisine: 'Pizza, Italian',   eta: 25, rating: 4.1 },
      { name: 'Dosa Plaza <b>', cuisine: 'South Indian',     eta: 20, rating: 4.6 }, // tag stays as text = XSS safe
    ];

    const tpl  = document.getElementById('card-tpl');
    const list = document.getElementById('list');

    function render(items) {
      const frag = document.createDocumentFragment();     // batch all cards, 1 DOM insert

      items.forEach((item, i) => {
        // 1. clone the template content (deep copy)
        const node = tpl.content.cloneNode(true);

        // 2. fill the clone using textContent (never innerHTML with user data)
        node.querySelector('.card__name').textContent = item.name;
        node.querySelector('.card__meta').textContent = item.cuisine + ' • ' + item.eta + ' min';
        node.querySelector('.card__rating').textContent = '★ ' + item.rating;

        // 3. set the image only now (so it loads only for real cards)
        const img = node.querySelector('.card__img');
        img.src = 'https://picsum.photos/seed/food' + (list.children.length + i) + '/64/64';
        img.alt = item.name;

        frag.append(node);
      });

      list.append(frag);   // single insertion
    }

    render(data);
    document.getElementById('add').addEventListener('click', () => render(data));
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #222; }
.page { max-width: 520px; margin: 0 auto; padding: 24px 16px; }

button { padding: 8px 14px; border: 0; border-radius: 6px; background: #e23744; color: #fff; cursor: pointer; }

.list { list-style: none; margin: 16px 0 0; padding: 0; display: grid; gap: 12px; }

.card {
  display: flex;               /* image | text | rating in a row */
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, .1);
}
.card__img { border-radius: 8px; object-fit: cover; background: #ddd; }
.card__body { flex: 1; min-width: 0; }   /* min-width:0 lets long text truncate instead of overflow */
.card__name { margin: 0; font-size: 16px; }
.card__meta { margin: 2px 0 0; color: #666; font-size: 13px; }
.card__rating { background: #2e7d32; color: #fff; padding: 2px 8px; border-radius: 6px; font-size: 13px; }
```

---

## 🟠 React/Next.js Connection

```jsx
// React component = the "template", props = the data. React also escapes text automatically (like textContent).
function RestaurantCard({ name, cuisine, eta, rating, img }) {
  return (
    <li className="flex items-center gap-3 rounded-xl bg-white p-3 shadow">
      <img src={img} alt={name} width={64} height={64} className="rounded-lg object-cover" />
      <div className="min-w-0 flex-1">
        <h2 className="text-base font-semibold">{name}</h2>
        <p className="text-sm text-gray-500">{cuisine} • {eta} min</p>
      </div>
      <span className="rounded bg-green-700 px-2 text-sm text-white">★ {rating}</span>
    </li>
  );
}

export default function List({ items }) {
  // .map() = cloning the template once per item. key helps React track items.
  return <ul className="grid gap-3">{items.map((r) => <RestaurantCard key={r.id} {...r} />)}</ul>;
}
```
- JSX replaces `<template>` + `cloneNode` in app code. Raw `<template>` still matters for **Web Components** (`customElements.define` + shadow DOM) and for **Declarative Shadow DOM** in SSR.
- React escapes `{value}`; `dangerouslySetInnerHTML` is the equivalent of the unsafe `innerHTML` route.

---

## ⚫ Interview Questions + Answers

Q1: What is `<template>` and how is it different from a hidden `div`?
A1: `<template>` content is parsed but inert: not rendered, images/scripts/media do not load or run, and it is not in the live DOM or accessibility tree. A `display:none` div is still in the DOM, loads its images, runs its scripts and keeps duplicate ids.

Q2: How do you use a template in JavaScript?
A2: `tpl.content.cloneNode(true)` to deep-clone the fragment, fill data (textContent/attributes), then `parent.append(clone)`.

Q3: Why `textContent` instead of `innerHTML` when filling?
A3: `innerHTML` parses data as HTML, so untrusted input (`<img onerror=...>`) causes XSS. `textContent` treats it as plain text.

Q4: Where can `<template>` be placed?
A4: Almost anywhere: head, body, and in places with restricted content models like `<table>`, `<tbody>`, `<select>`, `<colgroup>`.

Q5: How is `<template>` related to Web Components?
A5: Custom elements often clone a template into their shadow root. `<slot>` inside lets consumers project content. Declarative Shadow DOM (`<template shadowrootmode="open">`) lets SSR output shadow trees without JS.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: Appending `tpl` directly or reading `tpl.children` (it is always empty).
✅ Correct way: Use `tpl.content`.

❌ Mistake 2: Using `cloneNode()` without `true`, getting an empty fragment.
✅ Correct way: `cloneNode(true)` for a deep copy.

❌ Mistake 3: Reusing the same fragment after `append()`.
✅ Correct way: Clone again per item.

❌ Mistake 4: Filling data with `innerHTML` and untrusted input.
✅ Correct way: `textContent` / `setAttribute`, or sanitize.

❌ Mistake 5: Duplicate `id`s inside the template that get cloned many times.
✅ Correct way: Use classes (or data attributes) inside templates.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `<template>` | Inert, unrendered HTML holder | न दिखने वाला HTML ढाँचा |
| `template.content` | The DocumentFragment inside | Template के अंदर का fragment |
| DocumentFragment | Lightweight DOM container | हल्का DOM container |
| cloneNode(true) | Deep copy of a node | पूरी deep copy |
| Inert | Not rendered, not active | निष्क्रिय |
| XSS | Script injection attack | Script injection हमला |
| `<slot>` | Placeholder in shadow DOM | Shadow DOM में जगह |
| Declarative Shadow DOM | Shadow root via HTML only | सिर्फ HTML से shadow root |

---

## ⚡ 3-Line Summary
English: `<template>` stores HTML that is parsed but not rendered, and its content is inert until cloned.
Clone with `tpl.content.cloneNode(true)`, fill with `textContent`, then append (batch via a fragment).
It is the native version of components, safer and cleaner than string-concatenated HTML.

Hindi: `<template>` ऐसा HTML रखता है जो parse होता है पर render नहीं, और clone होने तक निष्क्रिय रहता है।
`tpl.content.cloneNode(true)` से clone करें, `textContent` से data भरें, फिर append करें (fragment से batch में)।
ये components का native रूप है, string जोड़े HTML से ज़्यादा सुरक्षित और साफ।

---

## ➡️ Next Topic
**31. Web Storage (localStorage, sessionStorage)** — UI बनाना सीख लिया; अब user का data browser में कैसे सहेजें (theme, cart, tokens)।

---
