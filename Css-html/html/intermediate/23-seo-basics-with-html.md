# 23. SEO Basics with HTML
# हिंदी में: HTML के साथ SEO की बुनियाद — Google को Page समझाना

---

## 🔵 Simple Definition (English)
SEO (Search Engine Optimization) is making your pages easy for search engines to **crawl, understand and rank**. With HTML you do this using a good `<title>`, meta description, one clear `<h1>` and heading hierarchy, semantic tags, descriptive links and image `alt`, canonical URLs, and structured data, while keeping the page fast and mobile-friendly.

## 🔵 सरल परिभाषा (Hindi)
SEO (Search Engine Optimization) का मतलब अपने pages को search engines के लिए **crawl, समझने और rank** करने में आसान बनाना है। HTML में यह अच्छे `<title>`, meta description, एक साफ़ `<h1>` और heading hierarchy, semantic tags, वर्णनात्मक links और image `alt`, canonical URLs और structured data से होता है, साथ में page तेज़ और mobile-friendly रहे।

---

## 🔴 Problem it Solves
```
WITHOUT SEO-FRIENDLY HTML:
  <div class="big">Best Pizza</div>   <div onclick="go('/menu')">click here</div>
  <img src="p1.jpg">                  <title>Untitled</title>
  - Google can't tell the main topic, or which text is a heading
  - JS-only links are not followed -> pages never discovered
  - Same content on many URLs -> duplicate content, split ranking
  - Search result shows "Untitled" with a random snippet; nobody clicks
  - Result: no organic traffic (free visitors from Google)

WITH SEO-FRIENDLY HTML:
  <title>Best Pizza in Delhi | PizzaHub</title>
  <h1>Best Pizza in Delhi</h1>
  <a href="/menu">See our pizza menu</a>   <img src="p1.jpg" alt="Margherita pizza">
  - Crawlers understand topic and structure, show a proper snippet, rank relevant pages
```

## 🔴 यह क्यों बना? (Hindi)
```
SEO-FRIENDLY HTML के बिना:
  <div class="big">Best Pizza</div>   <div onclick="go('/menu')">click here</div>
  <img src="p1.jpg">                  <title>Untitled</title>
  - Google को main topic या heading समझ नहीं आती
  - सिर्फ JS वाले links follow नहीं होते -> pages discover नहीं होते
  - एक ही content कई URLs पर -> duplicate content, ranking बँट जाती है
  - Search result में "Untitled" और random snippet; कोई click नहीं करता
  - नतीजा: organic traffic (Google से मुफ़्त visitors) नहीं

SEO-FRIENDLY HTML के साथ:
  <title>Best Pizza in Delhi | PizzaHub</title>
  <h1>Best Pizza in Delhi</h1>
  <a href="/menu">See our pizza menu</a>   <img src="p1.jpg" alt="Margherita pizza">
  - Crawlers topic और structure समझते हैं, सही snippet दिखाते हैं, relevant pages rank करते हैं
```

---

## 🟢 How it Works — Step by Step

```
HOW SEARCH ENGINES WORK:
  1. CRAWL    Googlebot follows <a href> links, reads robots.txt and sitemap.xml
  2. RENDER   Google can run JavaScript, but later and with limits -> server-rendered
              HTML is safer and faster to index
  3. INDEX    Understands content, headings, links, images, structured data;
              picks the canonical URL
  4. RANK     Relevance + quality + speed (Core Web Vitals) + mobile + links + trust

ON-PAGE HTML CHECKLIST:
  <html lang="en">                       language of the page
  <title>   50-60 chars, unique per page, main keyword near the start, brand at end
            (the single most important on-page element; shown as blue link)
  <meta name="description" content="..."> 120-160 chars, persuasive; not a ranking
            factor but affects click-through rate
  <meta name="viewport" ...>             mobile-friendly (mobile-first indexing)
  <link rel="canonical" href="https://site.com/page">   the preferred URL; fixes duplicates
            (?utm=..., http/https, www/non-www, trailing slash)
  <meta name="robots" content="noindex">  keep a page out of search (cart, thank-you)
  <h1>      exactly one, describes the page; then h2/h3 in order (no skipping)
  Semantic: <main> <article> <nav> <header> <footer> <section>
  Links:    <a href="/pizza-menu">Pizza menu</a>   real href + descriptive text
            (not "click here"); external paid/sponsored: rel="sponsored",
            user generated: rel="ugc", untrusted: rel="nofollow"
  Images:   alt text, width/height (prevents layout shift), loading="lazy" (below
            the fold), modern formats (WebP/AVIF), descriptive file names (margherita-pizza.jpg)
  URLs:     short, readable, lowercase, hyphens: /restaurants/delhi/pizza-hub
  Open Graph + Twitter cards for social sharing (topic 15, 42)
  Structured data (JSON-LD, schema.org) for rich results: stars, price, FAQ, recipe (topic 43)
  hreflang for multi-language/region versions:
            <link rel="alternate" hreflang="hi" href="https://site.com/hi/">

TECHNICAL SEO FILES (outside HTML):
  /robots.txt   which paths crawlers may visit
  /sitemap.xml  list of URLs you want indexed

PERFORMANCE = SEO: Core Web Vitals (LCP, INP, CLS) are ranking signals.
  Optimize images, lazy load, defer scripts, avoid layout shifts.

RENDERING STRATEGY: SSR / SSG / ISR (Next.js) give crawlers full HTML immediately.
  Pure client-side rendering ships an empty <div id="root"> first, which is risky for SEO
  and for social crawlers that do not run JS.

THINGS THAT DON'T WORK: keyword stuffing, hidden text, the old <meta name="keywords">
  (ignored by Google), buying links.
```

## 🟢 कैसे काम करता है? (Hindi)

```
SEARCH ENGINES कैसे काम करते हैं:
  1. CRAWL    Googlebot <a href> links follow करता है, robots.txt और sitemap.xml पढ़ता है
  2. RENDER   Google JavaScript चला सकता है, पर बाद में और सीमाओं के साथ -> server-rendered
              HTML ज़्यादा सुरक्षित है
  3. INDEX    content, headings, links, images, structured data समझता है; canonical URL चुनता है
  4. RANK     relevance + quality + speed (Core Web Vitals) + mobile + links + trust

ON-PAGE HTML CHECKLIST:
  <html lang="en">                       page की भाषा
  <title>   50-60 characters, हर page के लिए अलग, main keyword शुरू में, brand अंत में
            (सबसे ज़रूरी on-page element)
  <meta name="description">  120-160 characters; ranking factor नहीं, पर click बढ़ाता है
  <meta name="viewport">     mobile-friendly (mobile-first indexing)
  <link rel="canonical">     पसंदीदा URL; duplicate content ठीक करता है
  <meta name="robots" content="noindex">  page को search से बाहर रखता है
  <h1>      सिर्फ एक; फिर h2/h3 क्रम में (levels मत छोड़ो)
  Semantic tags: main, article, nav, header, footer, section
  Links:    <a href="/pizza-menu">Pizza menu</a> असली href + वर्णनात्मक text
            ("click here" नहीं); paid links पर rel="sponsored", user content पर rel="ugc"
  Images:   alt text, width/height, loading="lazy", WebP/AVIF, अच्छे file names
  URLs:     छोटे, पढ़ने लायक, lowercase, hyphens: /restaurants/delhi/pizza-hub
  Structured data (JSON-LD, schema.org) से rich results: stars, price, FAQ
  hreflang से कई भाषाओं/regions के versions

PERFORMANCE = SEO: Core Web Vitals (LCP, INP, CLS) ranking signals हैं।

RENDERING: SSR / SSG / ISR (Next.js) crawlers को पूरी HTML तुरंत देते हैं।
  Pure client-side rendering पहले खाली <div id="root"> भेजता है, जो SEO और उन social
  crawlers के लिए जोखिम है जो JS नहीं चलाते।

जो काम नहीं करता: keyword stuffing, छुपा text, पुराना <meta name="keywords"> (Google ignore करता है)।
```

---

## 🟡 Real World Example
**Zomato restaurant pages:** the title is "Biryani Blues, Indiranagar, Bengaluru - Menu, Reviews & Photos", the `<h1>` is the restaurant name, and a JSON-LD `Restaurant` block provides rating and address, so Google shows stars and price range in the result. Each city/cuisine combination has a clean URL such as `/bangalore/restaurants/biryani`. **Amazon** uses a `canonical` link so the product page with 20 different `?ref=` URLs counts as one page. **Medium / blogs** use `<article>`, `<time>` and `og:image` for news and social visibility.

## 🟡 Real Example Hindi mein
**Zomato restaurant pages:** title होता है "Biryani Blues, Indiranagar, Bengaluru - Menu, Reviews & Photos", `<h1>` restaurant का नाम, और JSON-LD `Restaurant` block rating और address देता है, इसलिए Google result में stars और price range दिखते हैं। हर शहर/cuisine के लिए साफ़ URL जैसे `/bangalore/restaurants/biryani`। **Amazon** `canonical` link use करता है ताकि 20 अलग `?ref=` URLs वाला product page एक ही page गिना जाए। **Medium / blogs** `<article>`, `<time>` और `og:image` use करते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">   <!-- language of the page -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- 1. TITLE: unique, 50-60 chars, keyword first, brand last -->
  <title>Best Margherita Pizza in Delhi - Order Online | PizzaHub</title>

  <!-- 2. DESCRIPTION: shown as the snippet; 120-160 chars, call to action -->
  <meta name="description" content="Order fresh wood-fired Margherita pizza in Delhi. 30-minute delivery, 50 percent off on your first order. Browse the full PizzaHub menu now.">

  <!-- 3. CANONICAL: the one true URL for this content -->
  <link rel="canonical" href="https://pizzahub.example/delhi/margherita-pizza">

  <!-- 4. ROBOTS: default is index,follow. For private pages use: noindex, nofollow -->
  <meta name="robots" content="index, follow, max-image-preview:large">

  <!-- 5. Language alternates (hreflang) -->
  <link rel="alternate" hreflang="en" href="https://pizzahub.example/delhi/margherita-pizza">
  <link rel="alternate" hreflang="hi" href="https://pizzahub.example/hi/delhi/margherita-pizza">

  <!-- 6. Open Graph for social sharing -->
  <meta property="og:title" content="Best Margherita Pizza in Delhi | PizzaHub">
  <meta property="og:description" content="Wood-fired Margherita delivered in 30 minutes.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://pizzahub.example/delhi/margherita-pizza">
  <meta property="og:image" content="https://pizzahub.example/img/margherita-1200x630.jpg">

  <!-- 7. STRUCTURED DATA (JSON-LD) for rich results -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Margherita Pizza",
    "image": "https://pizzahub.example/img/margherita.jpg",
    "description": "Wood-fired pizza with tomato, mozzarella and basil.",
    "aggregateRating": { "@type": "AggregateRating", "ratingValue": "4.6", "reviewCount": "1280" },
    "offers": { "@type": "Offer", "priceCurrency": "INR", "price": "299", "availability": "https://schema.org/InStock" }
  }
  </script>

  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; line-height: 1.6; color: #222; }
    header, main, footer { max-width: 760px; margin: 0 auto; padding: 16px; }
    nav a { margin-right: 14px; color: #b3261e; }
    img { max-width: 100%; height: auto; border-radius: 8px; }
    figure { margin: 0; }
    figcaption { font-size: 13px; color: #666; }
    .breadcrumb { font-size: 14px; color: #666; }
  </style>
</head>
<body>
  <header>
    <!-- 8. Semantic nav with real, crawlable links -->
    <nav aria-label="Main">
      <a href="/">Home</a>
      <a href="/delhi/menu">Delhi menu</a>
      <a href="/offers">Offers</a>
    </nav>
    <!-- 9. Breadcrumbs help users and Google understand the hierarchy -->
    <nav aria-label="Breadcrumb" class="breadcrumb">
      <a href="/">Home</a> &rsaquo; <a href="/delhi">Delhi</a> &rsaquo; <span aria-current="page">Margherita Pizza</span>
    </nav>
  </header>

  <main>
    <article>
      <!-- 10. ONE h1 that matches the page topic -->
      <h1>Best Margherita Pizza in Delhi</h1>
      <p>Updated <time datetime="2026-11-02">2 November 2026</time></p>

      <!-- 11. Image: descriptive alt, size attributes, lazy load below the fold -->
      <figure>
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='760' height='300'%3E%3Crect width='760' height='300' fill='%23ffcc80'/%3E%3C/svg%3E"
             alt="Wood-fired Margherita pizza with fresh basil and mozzarella"
             width="760" height="300">
        <figcaption>Our signature Margherita, baked at 400 degrees.</figcaption>
      </figure>

      <p>Our pizza uses San Marzano tomatoes and fresh mozzarella...</p>

      <!-- 12. Heading hierarchy: h2 under h1, h3 under h2 (no skipping) -->
      <h2>Why customers love it</h2>
      <p>Thin crust, rich sauce and 30-minute delivery across Delhi.</p>

      <h2>Related pizzas</h2>
      <ul>
        <!-- 13. DESCRIPTIVE anchor text, not "click here" -->
        <li><a href="/delhi/farmhouse-pizza">Farmhouse pizza in Delhi</a></li>
        <li><a href="/delhi/paneer-tikka-pizza">Paneer tikka pizza in Delhi</a></li>
        <!-- 14. External sponsored link must be labeled -->
        <li><a href="https://partner.example/deal" rel="sponsored noopener" target="_blank">Partner deal</a></li>
      </ul>
    </article>
  </main>

  <footer><p>&copy; 2026 PizzaHub</p></footer>
</body>
</html>
```

```text
# robots.txt (place at site root: /robots.txt)
User-agent: *
Disallow: /cart
Disallow: /checkout
Sitemap: https://pizzahub.example/sitemap.xml
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js App Router: metadata API outputs title, description, canonical, OG tags
// in the SERVER-RENDERED HTML (crawlers see it immediately).
// app/[city]/[slug]/page.tsx
export async function generateMetadata({ params }) {
  const p = await getProduct(params.slug);
  return {
    title: `${p.name} in ${p.city} - Order Online | PizzaHub`,
    description: p.summary,
    alternates: { canonical: `https://pizzahub.example/${params.city}/${params.slug}`,
                  languages: { hi: `/hi/${params.city}/${params.slug}` } },
    openGraph: { title: p.name, images: [p.image] },
    robots: { index: true, follow: true },
  };
}

export default async function Page({ params }) {
  const p = await getProduct(params.slug);           // data fetched on the server
  const jsonLd = { '@context': 'https://schema.org', '@type': 'Product', name: p.name };
  return (
    <main>
      <h1>{p.name}</h1>                               {/* one h1 */}
      <script type="application/ld+json"
              dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />
      <Image src={p.image} alt={p.alt} width={760} height={300} priority />   {/* LCP image */}
      <Link href="/delhi/menu">Delhi menu</Link>      {/* renders crawlable <a href> */}
    </main>
  );
}

// File conventions: app/sitemap.ts, app/robots.ts generate sitemap.xml and robots.txt.
// Rendering: SSG/ISR for catalog pages, SSR for personalized ones; avoid CSR-only for SEO.
// Pitfalls: <div onClick={() => router.push('/x')}> is NOT crawlable; use <Link>.
// next/image gives lazy loading, responsive sizes and CLS protection.
// next/font avoids font layout shift. Measure with Lighthouse / Search Console.
```

---

## ⚫ Interview Questions + Answers

**Q1: Which HTML elements matter most for SEO?**
A1: `<title>` (strongest on-page signal), one descriptive `<h1>` plus a logical h2-h6 hierarchy, `<meta name="description">` (for snippets and clicks), semantic landmarks, meaningful `<a href>` links with descriptive anchor text, image `alt`, `<link rel="canonical">`, `lang`, the viewport meta and structured data (JSON-LD). Content quality and speed matter as much as markup.

**Q2: What is a canonical URL and why use it?**
A2: `<link rel="canonical" href="...">` tells search engines which URL is the preferred version when the same or very similar content is reachable at multiple URLs (query params, `http` vs `https`, `www`, trailing slashes, filters/sort). It consolidates ranking signals into one URL and prevents duplicate-content dilution. It is a hint, not a command.

**Q3: Is client-side rendering (React SPA) bad for SEO? How does Next.js help?**
A3: Google can execute JavaScript, but rendering is deferred and less reliable, and many other crawlers and social scrapers do not run JS, so CSR pages may be indexed late or incompletely and give empty link previews. Next.js offers SSR, SSG and ISR, which send complete HTML (with metadata, headings and content) in the first response, so crawlers and users see content immediately, and it improves Core Web Vitals.

**Q4: What do `noindex`, `nofollow`, `rel="sponsored"` and `robots.txt` do?**
A4: `noindex` (meta robots) asks search engines not to include the page in results; `nofollow` asks them not to follow the page's links (or one link via `rel`). `rel="sponsored"` marks paid links, `rel="ugc"` marks user-generated links. `robots.txt` controls which paths crawlers may **crawl**, but blocking crawling does not remove an already known URL from the index; to keep a page out use `noindex` (and allow crawling so the tag can be seen).

**Q5: Does `<meta name="keywords">` help? What are common SEO mistakes?**
A5: No. Google has ignored it for years. Common mistakes: multiple or missing `<h1>`, duplicate titles/descriptions, keyword stuffing, "click here" links, links built only with JS, images without `alt`, slow pages, blocking CSS/JS in `robots.txt`, no canonical, and no mobile-friendly layout. Focus on useful content, clear structure and speed.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Same or missing title and description on all pages
```html
<title>My App</title>   <!-- every route in a React SPA -->
```
✅ **Correct way:** Unique, descriptive per page (`generateMetadata` in Next.js).

❌ **Mistake 2:** Multiple `<h1>` or using headings for styling, skipping levels
```html
<h1>Logo</h1> <h1>Pizza</h1> <h4>Small text</h4>
```
✅ **Correct way:** One `<h1>` for the topic; use CSS for size; keep h2, h3 in order.

❌ **Mistake 3:** Non-crawlable navigation
```jsx
<div onClick={() => router.push('/menu')}>Menu</div>
```
✅ **Correct way:** `<Link href="/menu">Pizza menu</Link>` or `<a href="/menu">`.

❌ **Mistake 4:** Images without `alt`/dimensions, huge unoptimized hero images
✅ **Correct way:** `alt`, `width`/`height`, WebP/AVIF, `loading="lazy"` (but not on the LCP hero image).

❌ **Mistake 5:** `noindex` left on production, or blocking the whole site in robots.txt
✅ **Correct way:** Check staging vs production config before launch; verify in Search Console.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SEO | Optimizing to rank in search | Search में rank सुधारना |
| Crawler / Googlebot | Bot that discovers pages | Pages ढूँढने वाला bot |
| Indexing | Storing page in search database | Page को search database में रखना |
| Canonical URL | Preferred URL for duplicate content | मुख्य/पसंदीदा URL |
| Meta description | Snippet text under the title | Title के नीचे का snippet |
| Structured data | Machine-readable info (JSON-LD) | Machine के पढ़ने लायक जानकारी |
| sitemap.xml | List of URLs to crawl | Crawl के लिए URLs की सूची |
| Core Web Vitals | Speed/UX metrics (LCP, INP, CLS) | Speed और UX के मापदंड |
| Anchor text | Visible text of a link | Link का दिखने वाला text |

---

## ⚡ 3-Line Summary
**English:**
1. HTML SEO basics: unique `<title>` and description, one `<h1>` with ordered headings, semantic tags, crawlable `<a href>` links, image `alt`, canonical and `lang`.
2. Add JSON-LD structured data, sitemap.xml and robots.txt, and keep pages fast (Core Web Vitals) and mobile friendly.
3. Use Next.js SSR/SSG with `generateMetadata` and `<Link>` instead of client-only rendering so crawlers see full HTML.

**Hindi:**
1. HTML SEO basics: अलग `<title>` और description, एक `<h1>` और क्रम में headings, semantic tags, crawl हो सकने वाले `<a href>` links, image `alt`, canonical और `lang`।
2. JSON-LD structured data, sitemap.xml और robots.txt जोड़ो, और pages तेज़ व mobile-friendly रखो।
3. सिर्फ client-side rendering की जगह Next.js SSR/SSG, `generateMetadata` और `<Link>` use करो ताकि crawlers को पूरी HTML दिखे।

---

## ➡️ Next Topic
**24. data- Attributes** — HTML elements में अपना custom data रखना, जिसे JavaScript और CSS दोनों पढ़ सकते हैं।
