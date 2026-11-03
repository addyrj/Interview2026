# 14. HTML Attributes (id, class, name, placeholder, value)
# हिंदी में: HTML Attributes — Tag को extra जानकारी देना

---

## 🔵 Simple Definition (English)
An **attribute** is extra information written inside an element's opening tag as `name="value"`. It configures or identifies the element. Key ones: `id` (unique identifier), `class` (reusable group for CSS/JS), `name` (key of a form field), `placeholder` (hint text), `value` (the data).

## 🔵 सरल परिभाषा (Hindi)
**Attribute** element के opening tag के अंदर लिखी extra जानकारी है, `name="value"` format में। ये element को configure या identify करती है। मुख्य attributes: `id` (unique पहचान), `class` (CSS/JS के लिए reusable group), `name` (form field की key), `placeholder` (hint text), `value` (असली data)।

---

## 🔴 Problem it Solves
```
WITHOUT ATTRIBUTES:
  <input>   <input>   <input>
  - Which input is email? Which is phone?
  - How does CSS target ONLY the search box?
  - What key does the server receive the data under?
  - How does a <label> connect to its input?

WITH ATTRIBUTES:
  <input id="email" class="field" name="email" placeholder="you@mail.com" value="">
  - id    -> CSS #email, JS getElementById, <label for="email">, #anchor links
  - class -> style many elements the same way (.field)
  - name  -> server receives email=...
  - placeholder -> shows hint, disappears when typing
```

## 🔴 यह क्यों बना? (Hindi)
```
ATTRIBUTES के बिना:
  <input>   <input>   <input>
  - कौन सा input email है? कौन सा phone?
  - CSS सिर्फ search box को कैसे target करे?
  - Server को data किस key से मिलेगा?
  - <label> अपने input से कैसे जुड़े?

ATTRIBUTES के साथ:
  <input id="email" class="field" name="email" placeholder="you@mail.com">
  - id    -> CSS #email, JS getElementById, <label for="email">, #anchor links
  - class -> कई elements को एक जैसा style (.field)
  - name  -> server को email=... मिलता है
  - placeholder -> hint दिखाता है, typing पर गायब
```

---

## 🟢 How it Works — Step by Step

```
SYNTAX:  <tag attribute1="value1" attribute2="value2">content</tag>

1. Attributes live ONLY in the opening tag (never in the closing tag).
2. Format: name="value". Quotes are best practice (required if value has spaces).
3. Boolean attributes (disabled, required, checked, hidden, readonly)
   mean TRUE when present. <input disabled> = <input disabled="disabled">.
   They are FALSE only when absent: disabled="false" is STILL disabled!
4. The browser parses attributes into the DOM element's properties.

THE FIVE KEY ATTRIBUTES:
──────────────────────────────────────────────────────────
id           - Must be UNIQUE in the page. One per element.
               Uses: CSS #id, JS getElementById, label for=, aria-labelledby,
               URL fragment (page.html#pricing scrolls to id="pricing").
class        - Space separated list: class="btn btn-primary large".
               Many elements can share a class; one element can have many.
               Uses: CSS .btn, JS querySelectorAll('.btn'), Tailwind utilities.
name         - Form controls only. The KEY sent to the server (email=a@b.com).
               Radio buttons with the same name form ONE group (pick one).
               Unnamed controls are NOT submitted!
placeholder  - Hint text for text-like inputs/textarea. Not a value, not a label.
value        - Current/initial data. <input value="Delhi">;
               on a button/option it is what is sent (<option value="in">India).

OTHER COMMON ONES:
  href, src, alt, title, type, for, action, method, style, lang, hidden,
  tabindex, disabled, readonly, autofocus, autocomplete, data-*, aria-*

SPECIFICITY (CSS):  #id (high)  >  .class  >  tag (low)
```

## 🟢 कैसे काम करता है? (Hindi)

```
SYNTAX:  <tag attribute1="value1" attribute2="value2">content</tag>

1. Attributes सिर्फ opening tag में होती हैं (closing tag में कभी नहीं)।
2. Format: name="value"। Quotes लगाना best practice है।
3. Boolean attributes (disabled, required, checked, hidden, readonly)
   मौजूद हों तो TRUE। disabled="false" लिखने पर भी element disabled ही रहता है!
4. Browser इन्हें DOM element की properties में बदल देता है।

पाँच मुख्य ATTRIBUTES:
──────────────────────────────────────────────────────────
id           - पूरे page में UNIQUE होनी चाहिए। CSS #id, JS getElementById,
               label for=, और #anchor links में काम आती है।
class        - Space से अलग list: class="btn btn-primary"। कई elements
               एक class share कर सकते हैं। CSS .btn, Tailwind utilities।
name         - सिर्फ form controls के लिए। Server को भेजी जाने वाली KEY।
               एक ही name वाले radio buttons एक group बनाते हैं।
               बिना name वाला control submit नहीं होता!
placeholder  - Input में हल्का hint text। यह label नहीं है, value नहीं है।
value        - Current/initial data। <option value="in"> में server को यही जाता है।

CSS Specificity:  #id (ज़्यादा)  >  .class  >  tag (कम)
```

---

## 🟡 Real World Example
**Zomato search bar + filters:** the search `<input>` has `id="search"` (so the label and JS can find it), `class="search-input"` (for styling), `name="q"` (the URL becomes `?q=pizza`), and `placeholder="Search for restaurant, cuisine or a dish"`. The sort dropdown has `<option value="rating">Rating</option>`; the server receives `sort=rating`. Filter radio buttons all share `name="cuisine"` so only one can be selected.

## 🟡 Real Example Hindi mein
**Zomato search bar + filters:** Search `<input>` में `id="search"` (label और JS ढूँढ सकें), `class="search-input"` (styling), `name="q"` (URL बनता है `?q=pizza`) और `placeholder="Search for restaurant, cuisine or a dish"`। Sort dropdown में `<option value="rating">Rating</option>`; server को `sort=rating` मिलता है। Filter radio buttons का `name="cuisine"` एक ही है, इसलिए सिर्फ एक select होगा।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Attributes Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #fafafa; padding: 20px; max-width: 520px; margin: 0 auto; }

    /* tag selector: lowest specificity */
    input, select { padding: 10px; border: 2px solid #ccc; border-radius: 6px; width: 100%; margin: 4px 0 12px; }

    /* class selector: reusable, many elements */
    .field { font-size: 15px; }
    .field--big { font-size: 18px; }

    /* id selector: one unique element, highest specificity of the three */
    #search { border-color: #e23744; }

    /* attribute selector: style by attribute presence/value */
    input[disabled] { background: #eee; cursor: not-allowed; }
    input[readonly] { background: #fffde7; }

    /* style the placeholder text itself */
    ::placeholder { color: #999; font-style: italic; }

    .btn { padding: 10px 18px; border: 0; border-radius: 6px; background: #e23744; color: #fff; cursor: pointer; }
    .btn + .btn { margin-left: 8px; }
    .btn-secondary { background: #555; }   /* second class on same element */
    pre { background: #222; color: #9f9; padding: 10px; border-radius: 6px; overflow: auto; font-size: 13px; }
  </style>
</head>
<body>
  <h1>Attributes Demo</h1>

  <!-- action + method are form attributes; GET puts the data in the URL -->
  <form action="https://example.com/search" method="get" id="demo-form">

    <!-- label's "for" must match the input's "id" -->
    <label for="search">Search</label>
    <!-- id = unique, class = styling (two classes), name = key sent to server,
         placeholder = hint, autofocus = boolean attribute, value = initial text -->
    <input id="search" class="field field--big" name="q" type="search"
           placeholder="Search restaurants, dishes..." value="" autofocus>

    <label for="city">City</label>
    <!-- value on option is what the server gets, the text is what the user sees -->
    <select id="city" class="field" name="city">
      <option value="blr" selected>Bengaluru</option>   <!-- selected = boolean -->
      <option value="del">Delhi</option>
      <option value="mum">Mumbai</option>
    </select>

    <!-- Radios sharing the SAME name = one group (only one can be chosen) -->
    <fieldset>
      <legend>Cuisine</legend>
      <label><input type="radio" name="cuisine" value="north" checked> North Indian</label>
      <label><input type="radio" name="cuisine" value="south"> South Indian</label>
    </fieldset>

    <!-- Boolean attributes: presence means true -->
    <label for="coupon">Coupon (disabled)</label>
    <input id="coupon" class="field" name="coupon" value="WELCOME50" disabled>

    <label for="ref">Referral (readonly: submitted, but not editable)</label>
    <input id="ref" class="field" name="ref" value="ADI123" readonly>

    <button class="btn" type="submit">Search</button>
    <button class="btn btn-secondary" type="button" id="show">Show attributes</button>
  </form>

  <pre id="out">Click "Show attributes"</pre>

  <script>
    // JS can read and write attributes
    const input = document.getElementById('search');
    document.getElementById('show').addEventListener('click', () => {
      document.getElementById('out').textContent =
        'id: ' + input.id + '\n' +
        'classes: ' + [...input.classList].join(', ') + '\n' +          // classList = list of classes
        'name: ' + input.getAttribute('name') + '\n' +                  // read an attribute
        'placeholder: ' + input.placeholder + '\n' +
        'value (property, live): "' + input.value + '"\n' +
        'has "disabled" on coupon? ' + document.getElementById('coupon').hasAttribute('disabled');
    });
    // setAttribute('title', 'x'), removeAttribute('disabled'), classList.add('x')
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// JSX attributes are camelCase and a few names differ (reserved words in JS):
//   class     -> className
//   for       -> htmlFor
//   maxlength -> maxLength,  tabindex -> tabIndex,  readonly -> readOnly
//   style="a:b" -> style={{ a: 'b' }}   (object, not string)
//   data-* and aria-* stay lowercase with hyphens
import { useId } from 'react';

export default function SearchBox() {
  const id = useId();                       // generates a unique id (SSR safe)
  return (
    <div>
      <label htmlFor={id}>Search</label>
      <input
        id={id}                             // unique even if component is rendered 10 times
        className="field"                   // Tailwind: className="border p-2 rounded"
        name="q"                            // still needed for native form submit / FormData
        placeholder="Search..."
        defaultValue=""                     // uncontrolled initial value
        disabled={false}                    // booleans use {true}/{false}; false REMOVES it
      />
    </div>
  );
}
// Controlled input: <input value={text} onChange={e => setText(e.target.value)} />
// (if you set value without onChange, React makes it read-only and warns)
// Hardcoding id="x" in a reusable component creates DUPLICATE ids -> use useId().
// In Next.js Server Actions, FormData is built from each field's `name`.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `id` and `class`?**
A1: `id` must be unique in the document and identifies one element; it is used for anchors, `label for`, ARIA relationships and JS lookups. `class` is reusable: many elements share it and one element can have several (`class="btn primary"`). In CSS, `#id` has higher specificity than `.class`, so prefer classes for styling and keep ids for hooks/anchors.

**Q2: What does the `name` attribute do on a form field? What if it is missing?**
A2: `name` is the key under which the value is sent (`email=a@b.com`) in the query string or body, and what `FormData` uses. A control without `name` is not submitted at all. Radio buttons with the same `name` are one group, so only one can be selected. `id` is not a replacement for `name`.

**Q3: `placeholder` vs `value` vs `label`: what is the difference?**
A3: `value` is the actual data (initial or current) and is submitted. `placeholder` is a temporary hint that is never submitted and disappears on typing; it has low contrast and vanishes, so it must not replace a `<label>` (accessibility). `<label>` is the permanent accessible name of the field.

**Q4: What are boolean attributes? Does `disabled="false"` enable an element?**
A4: Boolean attributes (`disabled`, `checked`, `required`, `readonly`, `hidden`, `autofocus`) are true when present and false when absent, regardless of value. So `disabled="false"` is still disabled. To enable it, remove the attribute (`removeAttribute('disabled')` or `el.disabled = false`). In JSX you write `disabled={false}` and React omits it.

**Q5: What is the difference between an attribute and a property?**
A5: Attributes are what you write in HTML and are stored as strings (`getAttribute`). Properties are live values on the DOM object (`el.value`, `el.checked`). They are often linked but not always: for `<input value="a">` the attribute is the initial value, while `input.value` changes as the user types. Likewise `class` attribute maps to `className`/`classList`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Duplicate ids
```html
<div id="card">A</div> <div id="card">B</div>  <!-- invalid; getElementById returns only the first -->
```
✅ **Correct way:** Use `class="card"` for repeated things, ids only for unique ones.

❌ **Mistake 2:** Missing `name` on form fields
```html
<input type="email" id="email">   <!-- not submitted! -->
```
✅ **Correct way:** `<input type="email" id="email" name="email">`

❌ **Mistake 3:** Using `placeholder` instead of a label
```html
<input placeholder="Email">   <!-- screen readers and low-vision users struggle -->
```
✅ **Correct way:** `<label for="email">Email</label> <input id="email" placeholder="you@mail.com">`

❌ **Mistake 4:** Writing `disabled="false"` or starting ids with digits/spaces
✅ **Correct way:** Omit boolean attributes to turn them off; use ids like `user-email` (letters, digits, hyphens, no spaces).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Attribute | Extra info in opening tag | Tag में अतिरिक्त जानकारी |
| id | Unique identifier | अद्वितीय पहचान |
| class | Reusable group name | दोबारा use होने वाला group नाम |
| name | Form field key sent to server | Server को भेजी जाने वाली key |
| placeholder | Hint text inside empty input | Input में hint |
| value | The data of a control | Control का data |
| Boolean attribute | True if present | मौजूद = true |
| Property | Live DOM value of an attribute | DOM object की live value |

---

## ⚡ 3-Line Summary
**English:**
1. Attributes are `name="value"` pairs in the opening tag that identify or configure an element.
2. `id` = unique, `class` = reusable, `name` = form key sent to server, `placeholder` = hint only, `value` = actual data.
3. Boolean attributes are true when present; in JSX use `className`, `htmlFor`, `useId()`.

**Hindi:**
1. Attributes opening tag में `name="value"` जोड़े हैं जो element को पहचान या configure करते हैं।
2. `id` = unique, `class` = reusable, `name` = server key, `placeholder` = सिर्फ hint, `value` = असली data।
3. Boolean attributes मौजूद हों तो true; JSX में `className`, `htmlFor`, `useId()` use करो।

---

## ➡️ Next Topic
**15. Meta Tags (charset, viewport, description, og tags)** — अब `<head>` के अंदर की attributes समझेंगे जो browser, SEO और social sharing को जानकारी देती हैं।
