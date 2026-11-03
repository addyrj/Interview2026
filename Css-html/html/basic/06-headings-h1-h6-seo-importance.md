# 6. Headings (h1-h6) — SEO importance
# हिंदी में: Headings (h1-h6) — SEO के लिए अहमियत

---

## 🔵 Simple Definition (English)
Headings `<h1>` to `<h6>` create the **outline** of a page: `h1` is the main title, `h2` are major sections, `h3` are subsections, and so on. They tell search engines and screen readers what the page is about and how it is organised.

## 🔵 सरल परिभाषा (Hindi)
Headings `<h1>` से `<h6>` page की **रूपरेखा (outline)** बनाती हैं: `h1` मुख्य title, `h2` बड़े sections, `h3` उप-sections, इत्यादि। ये search engines और screen readers को बताती हैं कि page किस बारे में है और कैसे व्यवस्थित है।

---

## 🔴 Problem it Solves
```
WITHOUT HEADINGS (styled <p> or <div>):
  - Google cannot find the page's topic -> weaker relevance signals
  - Blind users cannot "list headings" to scan the page (like skimming visually)
  - Users face a wall of text
  - Table of contents cannot be auto-generated

WITH HEADINGS:
  - Clear hierarchy: one topic (h1) -> sections (h2) -> sub-sections (h3)
  - Screen reader: press "H" to jump heading to heading (the #1 navigation method)
  - SEO: h1/h2 text is a strong on-page relevance signal
  - Content is scannable for everyone
```

## 🔴 यह क्यों बना? (Hindi)
```
Headings के बिना (styled <p> या <div>):
  - Google को page का topic नहीं मिलता
  - नेत्रहीन users headings की list देखकर page scan नहीं कर पाते
  - Users को text की दीवार मिलती है
  - Table of contents अपने आप नहीं बन सकता

Headings के साथ:
  - साफ़ hierarchy: एक topic (h1) -> sections (h2) -> sub-sections (h3)
  - Screen reader: "H" दबाकर heading से heading पर jump
  - SEO: h1/h2 का text relevance का मज़बूत संकेत है
  - सबके लिए content scan करना आसान
```

---

## 🟢 How it Works — Step by Step

```
HEADING OUTLINE (like a book):
──────────────────────────────────────────────────────────
  <h1>Best Smartphones 2025</h1>          <- ONE per page: the main topic
    <h2>Budget Phones</h2>                <- major section
      <h3>Redmi Note 14</h3>              <- sub-section
      <h3>Realme Narzo</h3>
    <h2>Premium Phones</h2>
      <h3>iPhone 16</h3>
        <h4>Camera</h4>                   <- rarely need h5/h6
        <h4>Battery</h4>

RULES:
  1. Exactly ONE <h1> per page (HTML5 allows more, but one is the SEO best practice)
  2. Never SKIP levels downward: h2 -> h4 is bad; h3 -> h2 (going up) is fine
  3. Choose level by STRUCTURE, never by size. Size comes from CSS.
  4. Headings must contain meaningful text (not "Click here" or empty)
  5. Do not use heading tags just to make text big or bold
  6. Do not put headings inside <a> only for styling; if the card is a link, link the heading text

DEFAULT BROWSER STYLE (UA stylesheet):
  h1 2em bold | h2 1.5em | h3 1.17em | h4 1em | h5 0.83em | h6 0.67em
  All have vertical margins. Reset/override with CSS.

SEO IMPORTANCE:
  - <title> and <h1> should match the search intent (keyword naturally, not stuffed)
  - h2/h3 often become "jump to" sections and featured snippets in Google
  - Crawlers use the outline to understand topics and subtopics
  - Headings do not magically rank a page; quality content + hierarchy together help

ACCESSIBILITY:
  - Screen-reader users: headings list (VoiceOver rotor, NVDA "H" key)
  - Do not skip levels: assistive tech announces "heading level 4" and users get confused
```

## 🟢 कैसे काम करता है? (Hindi)
```
नियम:
  1. एक page में एक <h1> (सबसे अच्छा तरीका)
  2. Levels मत छोड़ो: h2 के बाद सीधे h4 नहीं
  3. Level structure के हिसाब से चुनो, size के हिसाब से नहीं; size CSS से
  4. Heading का text अर्थपूर्ण हो
  5. सिर्फ text बड़ा करने के लिए heading tag मत लगाओ

SEO:
  - <title> और <h1> user के search के हिसाब से हों (keyword natural तरीके से)
  - h2/h3 Google में section links और snippets बन सकते हैं
  - Crawler outline से topics समझता है

Accessibility:
  - Screen reader वाले users headings की list से जाते हैं; level छोड़ना भ्रमित करता है
```

---

## 🟡 Real World Example
**Amazon product page:** The product name is the page's single `<h1>`. Sections like "About this item", "Product information", "Customer reviews" are `<h2>`s, and individual review titles are `<h3>`s. Google picks up the `<h1>` and `<h2>`s to understand the product page, and blind shoppers jump from "Customer reviews" to "Product information" by heading. Blogs like Medium and the BBC also use one h1 (the story title) with h2 subheads.

## 🟡 Real Example Hindi mein
**Amazon product page:** Product का नाम page का एकमात्र `<h1>` है। "About this item", "Product information", "Customer reviews" जैसे sections `<h2>` हैं और हर review का title `<h3>` है। Google `<h1>` और `<h2>` से product page को समझता है, और नेत्रहीन खरीदार headings से "Customer reviews" से "Product information" पर पहुँच जाते हैं। Medium और BBC जैसे blogs में भी एक h1 (story का title) और h2 subheadings होते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Title and h1 should align on topic but need not be identical -->
  <title>Best Smartphones 2025 - Buying Guide</title>
  <meta name="description" content="Compare the best budget and premium smartphones of 2025.">
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 0 auto; padding: 24px; line-height: 1.6; color: #222; }

    /* Style by LEVEL (structure) but override size via classes when design needs it */
    h1 { font-size: 2rem; margin: 0 0 16px; color: #1a73e8; }
    h2 { font-size: 1.5rem; margin: 32px 0 8px; border-bottom: 2px solid #eee; padding-bottom: 4px; }
    h3 { font-size: 1.15rem; margin: 20px 0 4px; }

    /* WRONG-LOOKING-RIGHT pattern: visually small but semantically h2 */
    .eyebrow { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; color: #777; }

    /* Hidden-but-readable heading for screen readers (visually-hidden utility) */
    .sr-only {
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
    }
    .toc a { display: block; color: #1a73e8; text-decoration: none; margin: 4px 0; }
    .toc .l3 { margin-left: 16px; font-size: 0.95rem; }   /* indent h3 entries */
  </style>
</head>
<body>

  <header>
    <!-- Exactly one h1: the page topic -->
    <h1>Best Smartphones 2025</h1>
    <p class="eyebrow">Updated January 2025</p>
  </header>

  <!-- Auto-generated table of contents (built from headings by JS below) -->
  <nav aria-label="Table of contents" class="toc" id="toc">
    <strong>On this page</strong>
  </nav>

  <main id="article">
    <!-- Hidden heading gives the intro a landmark label without changing design -->
    <h2 class="sr-only">Introduction</h2>
    <p>We tested 30 phones. Here are the winners in each price range.</p>

    <h2 id="budget">Budget Phones</h2>
    <h3 id="redmi">Redmi Note 14</h3>
    <p>Great battery and display for the price.</p>
    <h3 id="narzo">Realme Narzo</h3>
    <p>Fast charging champion.</p>

    <h2 id="premium">Premium Phones</h2>
    <h3 id="iphone">iPhone 16</h3>
    <p>Best camera and long software support.</p>
  </main>

  <script>
    // Build a table of contents from the heading outline (proves headings = structure)
    const toc = document.getElementById("toc");
    document.querySelectorAll("#article h2[id], #article h3[id]").forEach(h => {
      const a = document.createElement("a");
      a.href = "#" + h.id;                         // jump link
      a.textContent = h.textContent;               // heading text
      if (h.tagName === "H3") a.className = "l3";  // indent sub-sections
      toc.appendChild(a);
    });

    // Outline check: log levels and warn on skipped levels
    let prev = 0;
    document.querySelectorAll("h1,h2,h3,h4,h5,h6").forEach(h => {
      const lvl = +h.tagName[1];
      if (prev && lvl > prev + 1) console.warn("Skipped heading level before:", h.textContent);
      prev = lvl;
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Component libraries often render the wrong level. Make heading level a prop:
function Heading({ level = 2, children, className }) {
  const Tag = `h${level}`;               // "h1" ... "h6"
  return <Tag className={className}>{children}</Tag>;
}
<Heading level={2} className="text-2xl font-bold">Budget Phones</Heading>

// 2. Next.js App Router: one h1 per page.tsx; layout.tsx should NOT contain an h1.
export default function Page() {
  return (
    <main>
      <h1 className="text-3xl font-bold">Best Smartphones 2025</h1>
      ...
    </main>
  );
}

// 3. Tailwind: separate meaning from look. Tailwind's preflight removes default heading
//    sizes, so you must add classes (text-3xl etc.) -- choose the TAG for structure:
<h2 className="text-sm uppercase tracking-wide text-gray-500">Related</h2>

// 4. Next.js metadata title (in <head>) complements the h1 for SEO:
export const metadata = { title: "Best Smartphones 2025 | PhoneGuide" };

// 5. Auto TOC in MDX/Markdown blogs: rehype-slug + rehype-autolink-headings add ids to headings.
```

---

## ⚫ Interview Questions + Answers

**Q1: How many `<h1>` tags should a page have?**
A1: Best practice: **one** `<h1>` representing the main topic. HTML5 technically allows several, but the "document outline algorithm" was never implemented by browsers or screen readers, so multiple h1s do not create separate outlines. Google says multiple h1s will not harm, but one clear h1 is simplest for users and assistive tech.

**Q2: Why are headings important for SEO?**
A2: They help crawlers understand the topic and structure, giving relevance signals (especially h1/h2 text), and enable rich result features like "jump to" links and featured snippets. They also improve readability and dwell time. They don't rank pages alone and keyword-stuffing them hurts.

**Q3: Can I skip heading levels, e.g., h1 then h3?**
A3: Avoid it. It breaks the outline and confuses screen-reader users who navigate by level. Going back **up** (h3 to h2) is normal. Use CSS to change the look; never pick a heading level for its default size.

**Q4: Difference between `<title>`, `<h1>` and `<header>`?**
A4: `<title>` (in `<head>`) is the name shown in the tab and search results. `<h1>` is the visible main heading on the page. `<header>` is a **sectioning container** (logo, nav, intro); it is not a heading. They should relate but can differ in wording.

**Q5: How do you make a heading visually hidden but available to screen readers?**
A5: Use a **visually-hidden/sr-only** CSS utility (absolute position, 1px size, clipped, overflow hidden). Do not use `display: none` or `visibility: hidden`, as they remove it from the accessibility tree. Tailwind provides `sr-only`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using headings for size
```html
<!-- WRONG -->
<h4>Big words I want small</h4>
<!-- ✅ Correct way -->
<h2 class="text-small">Section name</h2>   <!-- level by structure, size by CSS -->
```

❌ **Mistake 2:** Skipping levels or multiple conflicting h1s
```html
<!-- WRONG --> <h1>Shop</h1><h3>Deals</h3><h1>Cart</h1>
<!-- ✅ Correct way --> <h1>Shop</h1><h2>Deals</h2><h2>Cart</h2>
```

❌ **Mistake 3:** Empty or logo-only h1; styling `<p><strong>` as headings
```html
<!-- WRONG -->
<p><strong>Features</strong></p>
<!-- ✅ Correct way -->
<h2>Features</h2>
```

❌ **Mistake 4:** Keyword stuffing
```html
<!-- WRONG --> <h1>Cheap phone best phone buy phone online phone</h1>
<!-- ✅ Correct way --> <h1>Best Budget Smartphones in India</h1>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Heading | h1-h6 title for a section | Section का शीर्षक |
| Outline | Hierarchy built from headings | Headings से बनी रूपरेखा |
| h1 | Main page title | मुख्य title |
| Hierarchy | Parent-child levels | ऊपर-नीचे का क्रम |
| Snippet | Search result preview | Search में दिखने वाला अंश |
| sr-only | Visually hidden, screen-reader visible | सिर्फ screen reader के लिए |
| Keyword stuffing | Overusing keywords | ज़बरदस्ती keywords भरना |
| Rotor | Screen-reader heading/landmark list | Screen reader की सूची |

---

## ⚡ 3-Line Summary
**English:**
1. `h1`-`h6` build the page outline: one `h1`, then `h2` sections, `h3` sub-sections, no skipped levels.
2. Search engines and screen readers rely on headings to understand and navigate the page.
3. Pick the level by structure and control size with CSS; never use headings just for looks.

**Hindi:**
1. `h1`-`h6` page की रूपरेखा बनाते हैं: एक `h1`, फिर `h2` sections, `h3` sub-sections, कोई level न छूटे।
2. Search engines और screen readers headings से page समझते और navigate करते हैं।
3. Level structure से चुनो और size CSS से; headings को सिर्फ दिखावे के लिए मत लगाओ।

---

## ➡️ Next Topic
**7. Paragraphs, Links, Images** — ab headings ke neeche ka content: `<p>`, `<a>` aur `<img>` sahi tareeke se kaise likhein।
