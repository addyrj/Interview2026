# 3. Semantic HTML (header, footer, main, section, article, nav, aside)
# हिंदी में: Semantic HTML — Tags जो अपना मतलब खुद बताते हैं

---

## 🔵 Simple Definition (English)
**Semantic HTML** means using tags that describe the **meaning/role** of the content (`<nav>` = navigation, `<article>` = standalone content, `<footer>` = footer) instead of generic boxes like `<div>`. Browsers, search engines and screen readers all understand the page better.

## 🔵 सरल परिभाषा (Hindi)
**Semantic HTML** का मतलब है ऐसे tags use करना जो content का **अर्थ/role** बताएं (`<nav>` = navigation, `<article>` = स्वतंत्र content, `<footer>` = footer), सिर्फ `<div>` नहीं। इससे browsers, search engines और screen readers page को बेहतर समझते हैं।

---

## 🔴 Problem it Solves
```
BEFORE HTML5 (div soup):
  <div id="header"> <div id="nav"> <div class="main"> <div class="footer">
  - Every site invented its own class names; machines could not tell
    which div is the navigation and which is the footer
  - Screen-reader users could not jump to "main content" or "navigation"
  - Google had to guess what was important

AFTER HTML5 (semantic tags):
  <header> <nav> <main> <article> <aside> <footer>
  - Built-in meaning, built-in accessibility landmarks
  - Cleaner, more readable code, better SEO
```

## 🔴 यह क्यों बना? (Hindi)
```
HTML5 से पहले (div soup):
  <div id="header"> <div id="nav"> <div class="main"> <div class="footer">
  - हर site अपने class names बनाती थी; machine नहीं समझ पाती थी कि कौन सा div navigation है
  - Screen reader वाले user "main content" पर सीधे jump नहीं कर पाते थे
  - Google को अंदाज़ा लगाना पड़ता था कि क्या ज़रूरी है

HTML5 के बाद (semantic tags):
  <header> <nav> <main> <article> <aside> <footer>
  - अर्थ और accessibility landmarks built-in
  - साफ़ और पढ़ने में आसान code, बेहतर SEO
```

---

## 🟢 How it Works — Step by Step

```
SEMANTIC LAYOUT MAP:
──────────────────────────────────────────────────────────
  ┌────────────────────────── <header> ────────────────────────┐
  │  logo            <nav> Home | Shop | Cart </nav>           │
  ├──────────────────────────────┬─────────────────────────────┤
  │ <main>                       │ <aside>                     │
  │   <section> Hero </section>  │   Ads, related links,       │
  │   <article> Blog post        │   author bio                │
  │     <header><h2>..</h2></header>                           │
  │     <p>..</p>                │                             │
  │     <footer>Author</footer>  │                             │
  │   </article>                 │                             │
  ├──────────────────────────────┴─────────────────────────────┤
  └────────────────────────── <footer> ────────────────────────┘

WHEN TO USE WHICH:
  <header>   Intro/top of page OR of a section/article (logo, title, nav)
  <nav>      MAIN groups of navigation links (menu, breadcrumbs, pagination)
  <main>     The dominant content; ONLY ONE visible per page
  <section>  A thematic group of content WITH a heading (e.g., "Features")
  <article>  Self-contained, re-usable on its own (blog post, product card, comment, tweet)
  <aside>    Side info loosely related (sidebar, pull-quote, ads)
  <footer>   Footer of page/section (copyright, links, author)
  <figure> + <figcaption>  image with caption
  <time datetime="2025-01-01">  machine-readable date

QUICK TEST:
  "Would this make sense if copy-pasted alone into an RSS reader?" -> <article>
  "Is it a group of related content that needs a heading?"        -> <section>
  "Just need a box for styling?"                                  -> <div>

ACCESSIBILITY (implicit ARIA landmarks):
  header(site-level)=banner, nav=navigation, main=main, aside=complementary,
  footer(site-level)=contentinfo, section(with name)=region
```

## 🟢 कैसे काम करता है? (Hindi)
```
कौन सा tag कब:
  <header>   Page या section का ऊपरी हिस्सा (logo, title, nav)
  <nav>      मुख्य navigation links (menu, breadcrumbs)
  <main>     Page का मुख्य content; पूरे page में सिर्फ एक
  <section>  एक topic का group, जिसका heading हो (जैसे "Features")
  <article>  खुद में पूरा content (blog post, product card, comment)
  <aside>    साइड की जानकारी (sidebar, ads, related links)
  <footer>   Page/section का footer (copyright, links)

Quick test:
  अकेले copy करने पर भी समझ आए -> <article>
  Related content का group जिसे heading चाहिए -> <section>
  सिर्फ styling के लिए box चाहिए -> <div>

Screen reader इन tags को "landmarks" बनाकर user को सीधे main/nav पर jump कराता है।
```

---

## 🟡 Real World Example
**Swiggy restaurant list page:** The top bar with logo, location and cart is a `<header>` containing a `<nav>`. The list of restaurants is inside `<main>`, each restaurant card is an `<article>` (it makes sense on its own: name, rating, cuisine). Filters on the side are an `<aside>`. The bottom links (About, Careers, Terms) sit in a `<footer>`. A screen-reader user can press one key to jump straight to `<main>` and skip the header.

## 🟡 Real Example Hindi mein
**Swiggy restaurant list:** ऊपर logo, location और cart वाला bar `<header>` है जिसमें `<nav>` है। Restaurants की list `<main>` में है, हर restaurant card एक `<article>` है (नाम, rating, cuisine; अकेले भी समझ आता है)। Filters `<aside>` में हैं। नीचे About, Careers, Terms के links `<footer>` में हैं। Screen reader वाला user एक key दबाकर सीधे `<main>` पर जा सकता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Semantic Layout - Food Delivery</title>
  <style>
    /* Reset so sizes are predictable */
    * { box-sizing: border-box; margin: 0; }
    body { font-family: system-ui, sans-serif; color: #222; }

    /* Landmarks styled by tag name -- no div classes needed */
    body > header {                      /* site-level header */
      display: flex; justify-content: space-between; align-items: center;
      padding: 12px 24px; background: #fc8019; color: #fff;  /* Swiggy-orange */
    }
    nav a { color: #fff; margin-left: 16px; text-decoration: none; font-weight: 600; }
    nav a:hover { text-decoration: underline; }

    /* Two-column page body: main (wide) + aside (narrow) */
    .page { display: grid; grid-template-columns: 1fr 260px; gap: 24px;
            max-width: 1000px; margin: 24px auto; padding: 0 16px; }

    section { margin-bottom: 24px; }
    article { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-top: 12px; }
    article header h3 { font-size: 18px; }
    article footer { margin-top: 8px; font-size: 13px; color: #666; }
    aside { background: #fff6ed; padding: 16px; border-radius: 8px; height: fit-content; }
    body > footer { background: #222; color: #ccc; text-align: center; padding: 20px; }

    /* Stack on small screens */
    @media (max-width: 700px) { .page { grid-template-columns: 1fr; } }
  </style>
</head>
<body>

  <!-- Site header: banner landmark -->
  <header>
    <strong>🍔 FoodFast</strong>
    <!-- Main navigation: aria-label distinguishes multiple navs -->
    <nav aria-label="Main">
      <a href="#">Home</a><a href="#">Offers</a><a href="#">Cart</a>
    </nav>
  </header>

  <div class="page">
    <!-- Only ONE main per page: skip-link target for keyboard users -->
    <main>
      <!-- section = themed group, has its own heading -->
      <section aria-labelledby="top-picks">
        <h2 id="top-picks">Top Restaurants near you</h2>

        <!-- article = self-contained card, reusable anywhere -->
        <article>
          <header><h3>Burger Barn</h3></header>
          <p>American, Fast Food - 4.3 rating</p>
          <footer>Delivery in <time datetime="PT30M">30 min</time></footer>
        </article>

        <article>
          <header><h3>Pizza Palace</h3></header>
          <p>Italian, Pizza - 4.5 rating</p>
          <footer>Delivery in <time datetime="PT25M">25 min</time></footer>
        </article>
      </section>

      <section aria-labelledby="offers">
        <h2 id="offers">Today's Offers</h2>
        <!-- figure + figcaption: image with caption (emoji used as demo image) -->
        <figure>
          <p style="font-size:48px">🎉</p>
          <figcaption>50% off on your first order</figcaption>
        </figure>
      </section>
    </main>

    <!-- aside: related but not core content -->
    <aside>
      <h2>Filters</h2>
      <p>Veg only, Rating 4+, Fast delivery</p>
    </aside>
  </div>

  <!-- Site footer: contentinfo landmark -->
  <footer>
    <p>&copy; 2025 FoodFast. <a href="#" style="color:#fc8019">Terms</a></p>
  </footer>

</body>
</html>
```

Try it: install the browser extension "Landmarks" or open Chrome DevTools -> Accessibility tab to see the landmark roles.

---

## 🟠 React/Next.js Connection

```jsx
// Semantic tags work exactly the same in JSX. Use them in layouts:
export default function Layout({ children }) {
  return (
    <>
      <header className="flex items-center justify-between p-4 bg-orange-500 text-white">
        <Logo />
        <nav aria-label="Main">
          <Link href="/">Home</Link>
          <Link href="/cart">Cart</Link>
        </nav>
      </header>

      <main id="content" className="max-w-5xl mx-auto p-4">{children}</main>

      <footer className="bg-gray-900 text-gray-300 p-6 text-center">...</footer>
    </>
  );
}

// A reusable component should usually render an <article> if it stands alone:
function RestaurantCard({ r }) {
  return (
    <article className="border rounded-lg p-4">
      <h3>{r.name}</h3>
      <p>{r.cuisine}</p>
    </article>
  );
}

// Tailwind utilities do not care about the tag; style semantic tags directly:
// <nav className="flex gap-4"> -- no extra div needed.
// Anti-pattern in React codebases: <div onClick> everywhere instead of <button>/<a>/<nav>.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is semantic HTML and why use it?**
A1: Using elements that convey meaning (`<nav>`, `<article>`, `<button>`) rather than generic `<div>`/`<span>`. Benefits: **accessibility** (landmarks, roles for screen readers), **SEO** (crawlers identify main content and structure), **maintainability** (readable code), and **free built-in behaviour** (a `<button>` is focusable and keyboard-activatable).

**Q2: Difference between `<section>`, `<article>` and `<div>`?**
A2: `<article>` is self-contained and independently distributable (blog post, comment, product card). `<section>` is a thematic grouping, usually with a heading (a chapter of a page). `<div>` has no meaning; use it only when you need a styling/JS hook and no semantic tag fits.

**Q3: Can a page have multiple `<header>` and `<footer>`?**
A3: Yes. `<header>`/`<footer>` can appear inside `<article>` or `<section>` as that section's header/footer. Only the site-level ones (direct child of `<body>`) become the `banner`/`contentinfo` landmarks. But a page may have only **one visible `<main>`**, and `<main>` cannot be inside `<header>`, `<footer>`, `<nav>`, `<aside>` or `<article>`.

**Q4: When use `<nav>`? Should every group of links be a `<nav>`?**
A4: No. `<nav>` is for **major navigation blocks** (main menu, breadcrumbs, table of contents, pagination). A few links in a footer don't need `<nav>`. If you have more than one `<nav>`, label each with `aria-label` ("Main", "Breadcrumb") so screen readers can distinguish them.

**Q5: Does semantic HTML improve SEO directly?**
A5: Google does not give a "ranking boost" for the tag names alone, but semantic structure helps crawlers understand hierarchy and main content, improves accessibility signals and user experience (which affect ranking indirectly), and is required for rich results. It is a best practice, not a magic trick.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Div soup
```html
<!-- WRONG -->
<div class="header"><div class="nav"><div class="link">Home</div></div></div>
<!-- ✅ Correct way -->
<header><nav><a href="/">Home</a></nav></header>
```

❌ **Mistake 2:** `<section>` used as a generic wrapper (no heading)
```html
<!-- WRONG: just for styling -->
<section class="wrapper">...</section>
<!-- ✅ Correct way: use div for styling-only wrappers -->
<div class="wrapper">...</div>
```

❌ **Mistake 3:** Multiple `<main>` or `<main>` nested in `<article>`
```html
<!-- ✅ Correct way: exactly one main, direct child of body (or a layout wrapper) -->
<body><header>..</header><main>..</main><footer>..</footer></body>
```

❌ **Mistake 4:** Clickable div instead of button/link
```html
<!-- WRONG: not focusable, no keyboard support, no role -->
<div onclick="buy()">Buy</div>
<!-- ✅ Correct way -->
<button type="button" onclick="buy()">Buy</button>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Semantic | Tag that describes its meaning | अर्थ बताने वाला tag |
| Landmark | Region screen readers can jump to | Screen reader का jump point |
| `<header>` | Intro/top of page or section | ऊपरी हिस्सा |
| `<nav>` | Major navigation links | Navigation links |
| `<main>` | Main unique content (one per page) | मुख्य content |
| `<section>` | Thematic group with heading | Topic का group |
| `<article>` | Self-contained content | स्वतंत्र content |
| `<aside>` | Side/tangential content | साइड की जानकारी |
| `<footer>` | Footer of page/section | नीचे का हिस्सा |
| Div soup | Overusing div for everything | हर जगह div का इस्तेमाल |

---

## ⚡ 3-Line Summary
**English:**
1. Semantic tags (`header`, `nav`, `main`, `section`, `article`, `aside`, `footer`) describe what content is, not how it looks.
2. They give accessibility landmarks, better SEO understanding and cleaner code for free.
3. Use `<div>`/`<span>` only when no semantic tag fits; only one `<main>` per page.

**Hindi:**
1. Semantic tags बताते हैं कि content क्या है, कैसा दिखता है यह नहीं।
2. इनसे accessibility landmarks, बेहतर SEO और साफ़ code मुफ़्त में मिलता है।
3. `<div>`/`<span>` तभी use करो जब कोई semantic tag फ़िट न बैठे; page में सिर्फ एक `<main>`।

---

## ➡️ Next Topic
**4. Non-Semantic HTML (div, span)** — ab dekhte hain ki `div` aur `span` kab sahi hain aur kab nahi।
