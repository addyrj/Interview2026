# 19. HTML5 New Elements
# हिंदी में: HTML5 के नए Elements — Semantic, Interactive और Media

---

## 🔵 Simple Definition (English)
HTML5 (2014, now the "HTML Living Standard") added many elements that give **meaning** and **built-in behavior** without JavaScript: semantic layout tags (`header`, `nav`, `main`, `section`, `article`, `aside`, `footer`), content tags (`figure`, `figcaption`, `time`, `mark`), interactive tags (`details`, `summary`, `dialog`), form helpers (`datalist`, `progress`, `meter`, `output`) and media tags (`audio`, `video`, `canvas`, `svg`).

## 🔵 सरल परिभाषा (Hindi)
HTML5 (2014, अब "HTML Living Standard") ने कई elements जोड़े जो बिना JavaScript के **अर्थ** और **built-in behavior** देते हैं: semantic layout tags (`header`, `nav`, `main`, `section`, `article`, `aside`, `footer`), content tags (`figure`, `figcaption`, `time`, `mark`), interactive tags (`details`, `summary`, `dialog`), form helpers (`datalist`, `progress`, `meter`, `output`) और media tags (`audio`, `video`, `canvas`, `svg`)।

---

## 🔴 Problem it Solves
```
BEFORE HTML5 (HTML 4 era):
  <div id="header"> <div id="nav"> <div class="article"> <div id="footer">
  - "div soup": no meaning, bad for SEO, screen readers, maintenance
  - Video/audio needed the Flash plugin (not on iPhones, insecure, dead in 2020)
  - Accordions, modals, autocomplete, progress bars needed jQuery plugins
  - Drawing graphics needed Flash too

WITH HTML5:
  <header> <nav> <article> <footer>      -> meaningful structure
  <video controls src="a.mp4">           -> native video, no plugin
  <details><summary>FAQ</summary>...     -> accordion with zero JS
  <dialog>                               -> native modal with focus handling
  <input list="cities"><datalist>        -> native autocomplete
```

## 🔴 यह क्यों बना? (Hindi)
```
HTML5 से पहले (HTML 4 का दौर):
  <div id="header"> <div id="nav"> <div class="article"> <div id="footer">
  - "div soup": कोई अर्थ नहीं, SEO, screen readers और maintenance के लिए खराब
  - Video/audio के लिए Flash plugin चाहिए था (iPhone पर नहीं, असुरक्षित, 2020 में खत्म)
  - Accordion, modal, autocomplete, progress bar के लिए jQuery plugins
  - Graphics बनाने के लिए भी Flash

HTML5 के साथ:
  <header> <nav> <article> <footer>      -> अर्थपूर्ण structure
  <video controls src="a.mp4">           -> native video, plugin नहीं
  <details><summary>FAQ</summary>...     -> बिना JS का accordion
  <dialog>                               -> focus handling के साथ native modal
  <input list="cities"><datalist>        -> native autocomplete
```

---

## 🟢 How it Works — Step by Step

```
GROUP 1: SEMANTIC STRUCTURE (see topic 03)
  header  nav  main  section  article  aside  footer
  - Same look as div by default (block), but carry meaning
  - Screen readers expose them as landmarks (banner, navigation, main, ...)

GROUP 2: CONTENT / TEXT-LEVEL
  figure + figcaption  -> image/diagram/code with a caption
  time datetime="2026-11-02"  -> machine-readable date
  mark     -> highlighted text (search match)
  address  -> contact info for nearest article/body
  abbr     -> abbreviation with title
  wbr      -> optional line-break point in long words
  picture/source -> responsive images (topic 34)

GROUP 3: INTERACTIVE (built-in behavior, zero JS)
  details + summary -> toggle open/close (add `open` attribute to default-open;
                       name="group" makes an exclusive accordion in modern browsers)
  dialog  -> modal/non-modal popup. JS: dialog.showModal() / dialog.close().
             showModal() gives backdrop (::backdrop), focus trap, Esc to close.
             Supported in all modern browsers since 2022.
  popover attribute -> popovers without JS (newer: Baseline 2024)

GROUP 4: FORM ENHANCEMENTS
  datalist (autocomplete suggestions), progress (task progress), meter (a gauge
  within a known range), output (calculation result)
  New input types: email, url, tel, number, range, date, time, color, search
  New attributes: required, placeholder, pattern, autofocus, min/max

GROUP 5: MEDIA AND GRAPHICS
  audio, video, track (subtitles), canvas (2D bitmap by JS), inline svg

GROUP 6: OTHER
  template (inert HTML to clone), slot (web components), data (value for machines)

HTML5 ALSO ADDED APIs (not elements): localStorage, Geolocation, Drag and Drop,
Web Workers, History API.

REMOVED/OBSOLETE: <center>, <font>, <marquee>, <frame>, <big>, <strike>, <acronym>.
Presentation belongs in CSS.

BROWSER SUPPORT: all of the above are widely supported in evergreen browsers;
check caniuse.com for `popover` and the `details name=` exclusive accordion if you
must support older versions.
```

## 🟢 कैसे काम करता है? (Hindi)

```
GROUP 1: SEMANTIC STRUCTURE (topic 03 देखो)
  header  nav  main  section  article  aside  footer
  - Default में div जैसे (block), पर अर्थ के साथ
  - Screen readers इन्हें landmarks की तरह पढ़ते हैं

GROUP 2: CONTENT / TEXT-LEVEL
  figure + figcaption  -> caption वाली image/diagram/code
  time datetime="2026-11-02"  -> machine-readable तारीख
  mark     -> highlighted text (search match)
  address  -> contact जानकारी
  abbr     -> संक्षिप्त रूप title के साथ

GROUP 3: INTERACTIVE (बिना JS के behavior)
  details + summary -> खुलने-बंद होने वाला toggle (`open` से default खुला)
  dialog  -> modal/popup। JS: dialog.showModal() / dialog.close()।
             showModal() backdrop, focus trap और Esc से बंद करना देता है।
             सभी modern browsers में 2022 से supported।

GROUP 4: FORM ENHANCEMENTS
  datalist (autocomplete suggestions), progress (काम की प्रगति),
  meter (तय range में gauge), output (calculation का result)
  नए input types: email, url, tel, number, range, date, time, color, search

GROUP 5: MEDIA और GRAPHICS
  audio, video, track (subtitles), canvas (JS से 2D drawing), inline svg

GROUP 6: दूसरे
  template (clone करने के लिए inert HTML), slot, data

HTML5 ने APIs भी जोड़ीं: localStorage, Geolocation, Drag and Drop, Web Workers।

OBSOLETE: <center>, <font>, <marquee>, <frame>, <big>, <strike>।
Styling का काम CSS का है।
```

---

## 🟡 Real World Example
**Amazon / Flipkart FAQ and returns policy:** FAQ items use `<details><summary>` style accordions. **Swiggy order tracking:** a `<progress>` or styled progress shows delivery progress, and `<time datetime>` shows the ETA. **Gmail-style compose popups and confirm dialogs** now are often built on `<dialog>`. **Instagram / news article pages:** `<article>` contains `<figure><img><figcaption>Photo credit</figcaption></figure>`, with `<time>` for the publish date, `<aside>` for related posts, and a `<video>` for reels.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart FAQ और returns policy:** FAQ items में `<details><summary>` accordions होते हैं। **Swiggy order tracking:** `<progress>` या styled progress से delivery की प्रगति दिखती है, और `<time datetime>` से ETA। **Gmail जैसे compose popups और confirm dialogs** अब अक्सर `<dialog>` पर बनते हैं। **Instagram / news article pages:** `<article>` में `<figure><img><figcaption>Photo credit</figcaption></figure>`, publish date के लिए `<time>`, related posts के लिए `<aside>` और reels के लिए `<video>` होता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML5 New Elements Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; background: #f6f6f6; line-height: 1.6; }

    /* Semantic layout, styled like any other block */
    header, footer { background: #e23744; color: #fff; padding: 14px 20px; }
    nav a { color: #fff; margin-right: 14px; text-decoration: none; }
    .layout { display: grid; grid-template-columns: 1fr 220px; gap: 20px; max-width: 900px; margin: 20px auto; padding: 0 16px; }
    @media (max-width: 640px) { .layout { grid-template-columns: 1fr; } }  /* stack on mobile */

    article, aside { background: #fff; padding: 16px; border-radius: 8px; }
    section { margin-top: 20px; }
    h2 { margin-top: 0; }

    figure { margin: 0 0 12px; }
    figure svg { max-width: 100%; height: auto; border-radius: 6px; }
    figcaption { font-size: 13px; color: #666; margin-top: 4px; }

    mark { background: #fff176; padding: 0 2px; }

    /* details/summary: style the accordion */
    details { border: 1px solid #ddd; border-radius: 6px; padding: 8px 12px; margin: 8px 0; }
    summary { cursor: pointer; font-weight: 600; }
    details[open] { background: #fffbea; }          /* style the opened state */

    /* dialog: native modal and its backdrop */
    dialog { border: 0; border-radius: 10px; padding: 20px; max-width: 360px; }
    dialog::backdrop { background: rgba(0,0,0,.5); }

    progress, meter { width: 100%; }
    button { background: #e23744; color: #fff; border: 0; padding: 8px 14px; border-radius: 6px; cursor: pointer; }
  </style>
</head>
<body>

  <!-- HEADER + NAV landmarks -->
  <header>
    <strong>FoodNews</strong>
    <nav aria-label="Main"><a href="#top">Home</a><a href="#faq">FAQ</a></nav>
  </header>

  <div class="layout">
    <!-- MAIN: unique primary content (only one per page) -->
    <main id="top">
      <!-- ARTICLE: self-contained piece (blog, news, product) -->
      <article>
        <h2>Best Biryani in Hyderabad</h2>
        <!-- TIME: machine-readable date -->
        <p>Published <time datetime="2026-11-02">2 November 2026</time> by Aditya</p>

        <!-- FIGURE + FIGCAPTION: media with caption (inline SVG used so the demo has no external image) -->
        <figure>
          <svg viewBox="0 0 300 120" role="img" aria-label="Colored rectangles">
            <rect width="300" height="120" fill="#ffcc80"/><circle cx="150" cy="60" r="40" fill="#e23744"/>
          </svg>
          <figcaption>Fig 1. A plate of biryani (illustration)</figcaption>
        </figure>

        <!-- MARK: highlight search term -->
        <p>The <mark>dum</mark> style keeps the rice and meat sealed while cooking.</p>

        <!-- SECTION: thematic group with its own heading -->
        <section id="faq">
          <h2>FAQ</h2>
          <!-- DETAILS / SUMMARY: accordion with zero JS -->
          <details open>
            <summary>How long does delivery take?</summary>
            <p>Usually 30 to 40 minutes.</p>
          </details>
          <details>
            <summary>Can I cancel?</summary>
            <p>Yes, within 60 seconds of placing the order.</p>
          </details>
        </section>

        <!-- PROGRESS / METER / OUTPUT -->
        <section>
          <h2>Order status</h2>
          <label for="p">Delivery progress</label>
          <progress id="p" value="70" max="100">70%</progress>   <!-- task completion -->

          <label for="m">Battery of delivery partner</label>
          <meter id="m" min="0" max="100" low="20" high="80" optimum="100" value="45">45%</meter>
          <!-- meter = a measurement in a known range; progress = a task moving to done -->
        </section>

        <!-- DATALIST: native autocomplete suggestions -->
        <section>
          <label for="city">Choose a city</label>
          <input id="city" list="cities" placeholder="Start typing...">
          <datalist id="cities">
            <option value="Hyderabad"></option><option value="Bengaluru"></option><option value="Delhi"></option>
          </datalist>
        </section>

        <!-- DIALOG: native modal -->
        <section>
          <button id="open">Open dialog</button>
          <dialog id="dlg" aria-labelledby="dlg-title">
            <h2 id="dlg-title">Confirm order</h2>
            <p>Place order for Rs 249?</p>
            <!-- form method="dialog" closes the dialog when a button is clicked: no JS needed -->
            <form method="dialog">
              <button value="cancel">Cancel</button>
              <button value="ok">Confirm</button>
            </form>
          </dialog>
        </section>
      </article>
    </main>

    <!-- ASIDE: tangentially related content -->
    <aside>
      <h2>Related</h2>
      <ul><li>Top 10 Dosa spots</li><li>Street food guide</li></ul>
      <!-- ADDRESS: contact info -->
      <address>Contact: <a href="mailto:hi@example.com">hi@example.com</a></address>
    </aside>
  </div>

  <footer>&copy; 2026 FoodNews</footer>

  <script>
    // dialog needs one line of JS to open as a modal (focus trap + backdrop + Esc included)
    const dlg = document.getElementById('dlg');
    document.getElementById('open').addEventListener('click', () => dlg.showModal());
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// All HTML5 elements are valid in JSX. Use them instead of div wrappers:
export default function Page() {
  return (
    <>
      <header><nav aria-label="Main">...</nav></header>
      <main>
        <article>
          <h1>Title</h1>
          <time dateTime="2026-11-02">2 Nov 2026</time>   {/* dateTime camelCase */}
          <figure>
            <img src="/biryani.jpg" alt="Hyderabadi biryani" />
            <figcaption>Photo: Aditya</figcaption>
          </figure>
        </article>
        <aside>...</aside>
      </main>
      <footer>...</footer>
    </>
  );
}

// <dialog> in React: control through a ref (React has no built-in open prop sync)
function Confirm() {
  const ref = useRef(null);
  return (
    <>
      <button onClick={() => ref.current?.showModal()}>Open</button>
      <dialog ref={ref}>
        <form method="dialog"><button>Close</button></form>
      </dialog>
    </>
  );
}

// <details> works without JS; for controlled state use onToggle={e => ...}.
// Tailwind: "open:bg-yellow-50" styles details[open]; "backdrop:bg-black/50" styles ::backdrop.
// UI libraries (Radix, Headless UI) build accessible modals/accordions; native
// dialog/details are now a lightweight alternative.
// In Next.js layouts, <header>/<main>/<footer> in app/layout.tsx give every page landmarks.
```

---

## ⚫ Interview Questions + Answers

**Q1: Name some new elements introduced in HTML5 and why they matter.**
A1: Semantic: `header`, `nav`, `main`, `section`, `article`, `aside`, `footer`; content: `figure`, `figcaption`, `time`, `mark`; interactive: `details`, `summary`, `dialog`; forms: `datalist`, `progress`, `meter`, `output`; media: `audio`, `video`, `canvas`. They add meaning (SEO, accessibility) and built-in behavior (no Flash or heavy JS plugins).

**Q2: What is the difference between `<progress>` and `<meter>`?**
A2: `<progress>` shows how far a task has advanced toward completion (upload, delivery, loading); it can be indeterminate when `value` is omitted. `<meter>` shows a scalar measurement within a known range (disk usage, battery, rating) and supports `low`, `high`, `optimum` to color it as good/bad.

**Q3: How does `<dialog>` work and what do you get for free?**
A3: `dialog.showModal()` opens it as a modal in the top layer with a `::backdrop`, traps focus inside, makes the rest of the page inert and closes on Esc. `dialog.show()` opens non-modal. `dialog.close(returnValue)` closes it; a `<form method="dialog">` closes on submit. It is supported in all modern browsers; you still need to label it (`aria-labelledby`) and manage returning focus where needed.

**Q4: Which old elements are obsolete in HTML5 and what replaces them?**
A4: `<center>`, `<font>`, `<big>`, `<strike>`, `<marquee>`, `<frame>/<frameset>`, `<acronym>`. Styling moved to CSS (`text-align`, `font-*`, `text-decoration`, animations), `<acronym>` became `<abbr>`, and frames were replaced by `<iframe>`/modern layouts.

**Q5: Is `<section>` the same as `<div>`? When use which?**
A5: No. `<section>` is a thematic grouping that should have a heading and appears in the document outline (and becomes a "region" landmark if it has an accessible name). `<div>` has no meaning and is just a styling/layout wrapper. Use `article` for self-contained content, `section` for chapters of a page, and `div` when you only need a hook for CSS or JS.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Replacing all `<div>` with `<section>` blindly
```html
<section class="wrapper"><section class="row">...</section></section>
```
✅ **Correct way:** Use `section`/`article` only for meaningful content groups with headings; keep `div` for pure layout.

❌ **Mistake 2:** Multiple `<main>` elements or `<main>` inside `<article>`
✅ **Correct way:** One visible `<main>` per page, as a direct child of body-level layout.

❌ **Mistake 3:** Using `<progress>` for a static value or `<meter>` for loading
✅ **Correct way:** progress = task completion, meter = measurement in a range.

❌ **Mistake 4:** Building a custom modal with divs and forgetting focus trap, Esc, backdrop
✅ **Correct way:** Use native `<dialog>` + `showModal()` or a tested library.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Semantic element | Tag that describes its meaning | अर्थ बताने वाला tag |
| figure / figcaption | Media with caption | Caption वाला media |
| details / summary | Native accordion | बिना JS का accordion |
| dialog | Native modal/popup | Native popup |
| progress | Task progress bar | काम की प्रगति |
| meter | Gauge in a known range | तय range में gauge |
| datalist | Autocomplete suggestions for input | Autocomplete सुझाव |
| Landmark | Region screen readers can jump to | Screen reader का navigation क्षेत्र |

---

## ⚡ 3-Line Summary
**English:**
1. HTML5 added semantic tags, interactive elements (`details`, `dialog`), form helpers and native media, replacing div soup and Flash.
2. Native elements give accessibility and behavior for free, so use them before reaching for a JS library.
3. Removed presentational tags (`center`, `font`) belong to CSS; in React use the same elements with `dateTime`, refs for `dialog`.

**Hindi:**
1. HTML5 ने semantic tags, interactive elements (`details`, `dialog`), form helpers और native media जोड़े, जिससे div soup और Flash खत्म हुए।
2. Native elements में accessibility और behavior मुफ़्त मिलता है, इसलिए JS library से पहले इन्हें use करो।
3. `center`, `font` जैसे presentational tags का काम CSS का है; React में वही elements use करो, `dateTime` और `dialog` के लिए ref के साथ।

---

## ➡️ Next Topic
**20. Audio + Video Tags** — HTML5 के सबसे बड़े बदलाव, native media, को detail में: controls, sources, subtitles और autoplay के नियम।
