# 43. Structured Data (Schema.org)
# हिंदी में: Structured Data (Schema.org) — Search Engine को Page का मतलब समझाना

---

## 🔵 Simple Definition (English)
**Structured data** is machine-readable information added to a page that describes its content using the shared **Schema.org** vocabulary (Product, Recipe, Article, FAQPage, Organization...). The recommended format is **JSON-LD** inside `<script type="application/ld+json">`. Search engines use it to show **rich results** (stars, price, availability).

## 🔵 सरल परिभाषा (Hindi)
**Structured data** page में जोड़ी गई machine-readable जानकारी है, जो **Schema.org** की साझा भाषा (Product, Recipe, Article, FAQPage, Organization...) से content का वर्णन करती है। सुझाया गया format **JSON-LD** है, जो `<script type="application/ld+json">` में लिखा जाता है। Search engines इससे **rich results** (stars, price, availability) दिखाते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM:
  - Google reads text but must GUESS: is "4.5" a rating, a price or a version?
  - Is "30 min" cooking time or delivery time?
  - Plain blue links get fewer clicks

SOLUTION:
  - Explicit labels: "this is aggregateRating, ratingValue 4.5, from 1200 reviews"
  - Result: rich snippets, carousels, recipe cards, FAQ dropdowns, event info
  - Also feeds voice assistants and knowledge graphs

NOTE: structured data does not directly guarantee ranking or rich results;
it makes the page eligible and clearer.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  - Google text पढ़ता है पर अंदाज़ा लगाता है: "4.5" rating है, price या version?
  - "30 min" cooking time है या delivery time?
  - साधारण नीले links पर कम clicks

हल:
  - साफ़ labels: "यह aggregateRating है, ratingValue 4.5, 1200 reviews से"
  - नतीजा: rich snippets, recipe cards, FAQ dropdown
  - Voice assistants और knowledge graph को भी फ़ायदा

ध्यान दें: इससे rank की गारंटी नहीं, सिर्फ rich result के लिए eligibility मिलती है।
```

---

## 🟢 How it Works — Step by Step

```
THREE SYNTAXES:
  JSON-LD   (recommended by Google) - a script block, separate from HTML
  Microdata - itemscope / itemtype / itemprop attributes inside HTML
  RDFa      - property / typeof attributes

JSON-LD ANATOMY:
  {
    "@context": "https://schema.org",   <- vocabulary
    "@type": "Product",                 <- what this thing is
    "name": "...",                      <- properties of that type
    "offers": { "@type": "Offer", ... } <- nested objects
  }

STEPS:
  1. Pick the right type from schema.org (Product, Recipe, Article, FAQPage,
     LocalBusiness, BreadcrumbList, Event, JobPosting, Organization...)
  2. Fill required + recommended properties (check Google's docs per type)
  3. Data MUST match what the user can see on the page (else penalty)
  4. Add JSON-LD in <head> or <body>
  5. Validate:
       - Google Rich Results Test
       - Schema Markup Validator (validator.schema.org)
       - Search Console > Enhancements report
  6. Google crawls, and may show rich results (not guaranteed)

COMMON TYPES:
  Product + Offer + AggregateRating  -> price, stars, stock in search
  Recipe                             -> image, time, calories
  Article / NewsArticle              -> headline, author, date
  FAQPage                            -> Q&A (Google now shows these rarely, only for some sites)
  BreadcrumbList                     -> breadcrumb path in result
  Organization / LocalBusiness       -> logo, address, phone, hours
```

## 🟢 कैसे काम करता है? (Hindi)

```
तीन syntax: JSON-LD (सुझाया गया), Microdata, RDFa

JSON-LD की बनावट:
  "@context": "https://schema.org"  -> vocabulary
  "@type": "Product"                -> यह चीज़ क्या है
  बाकी: उस type की properties, nested objects

Steps:
  1. सही type चुनो (Product, Recipe, Article, FAQPage, LocalBusiness...)
  2. ज़रूरी और सुझाई गई properties भरो
  3. Data वही हो जो user को page पर दिखता है (वरना penalty)
  4. <script type="application/ld+json"> जोड़ो
  5. Google Rich Results Test और validator.schema.org से जाँचो
  6. Google crawl करता है और rich result दिखा सकता है (गारंटी नहीं)
```

---

## 🟡 Real World Example
**Amazon/Flipkart product page in Google:** the search result shows price, "In stock", and a star rating with review count: that comes from `Product`, `Offer` and `AggregateRating` JSON-LD. **Zomato/Swiggy restaurants** use `Restaurant` (a LocalBusiness subtype) with address, opening hours and cuisine, so Google shows them in local results and maps. **News sites** use `NewsArticle` to qualify for Top Stories.

## 🟡 Real Example Hindi mein
**Google में Amazon/Flipkart का product page:** result में price, "In stock" और reviews की संख्या के साथ stars दिखते हैं; ये `Product`, `Offer` और `AggregateRating` JSON-LD से आता है। **Zomato/Swiggy restaurants** `Restaurant` (LocalBusiness का subtype) के साथ पता, खुलने का समय और cuisine देते हैं, इसलिए Google local results और maps में दिखाता है। **News sites** `NewsArticle` से Top Stories के लिए eligible होती हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wireless Headphones - Product Page</title>

  <!-- JSON-LD #1: Product with offer and rating -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Wireless Headphones X200",
    "image": ["https://example.com/img/x200-1x1.jpg", "https://example.com/img/x200-4x3.jpg"],
    "description": "Over-ear Bluetooth headphones with 40 hours battery life.",
    "sku": "X200-BLK",
    "brand": { "@type": "Brand", "name": "SoundCo" },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.5",
      "reviewCount": "1243"
    },
    "offers": {
      "@type": "Offer",
      "url": "https://example.com/p/x200",
      "priceCurrency": "INR",
      "price": "2999.00",
      "availability": "https://schema.org/InStock",
      "itemCondition": "https://schema.org/NewCondition"
    }
  }
  </script>

  <!-- JSON-LD #2: Breadcrumbs -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
      { "@type": "ListItem", "position": 2, "name": "Audio", "item": "https://example.com/audio" },
      { "@type": "ListItem", "position": 3, "name": "Headphones X200" }
    ]
  }
  </script>
</head>
<body>
  <!-- Visible content MUST match the structured data -->
  <nav aria-label="Breadcrumb">Home &gt; Audio &gt; Headphones X200</nav>
  <h1>Wireless Headphones X200</h1>
  <p>Rating: 4.5 / 5 (1243 reviews)</p>
  <p>Price: ₹2,999 - In stock</p>

  <!-- Same data using Microdata (alternative syntax, do not duplicate both in real pages) -->
  <div itemscope itemtype="https://schema.org/Product">
    <span itemprop="name">Wireless Headphones X200</span>
    <div itemprop="offers" itemscope itemtype="https://schema.org/Offer">
      <meta itemprop="priceCurrency" content="INR">
      <span itemprop="price" content="2999.00">₹2,999</span>
    </div>
  </div>

  <script>
    // Read and print every JSON-LD block (also verifies the JSON is valid)
    document.querySelectorAll('script[type="application/ld+json"]').forEach((s, i) => {
      try { console.log('JSON-LD', i, JSON.parse(s.textContent)['@type']); }
      catch (e) { console.error('Invalid JSON-LD', i, e); }
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js App Router: render JSON-LD as a script in a Server Component
// app/products/[id]/page.jsx
export default async function Product({ params }) {
  const p = await getProduct(params.id);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: p.name,
    image: p.images,
    offers: {
      '@type': 'Offer',
      priceCurrency: 'INR',
      price: p.price,
      availability: p.inStock ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
    },
  };

  return (
    <section>
      {/* Escape "<" so data containing "</script>" cannot break out (XSS safety) */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />
      <h1>{p.name}</h1>
    </section>
  );
}

// Type safety: `schema-dts` package gives TypeScript types for Schema.org
// import type { Product, WithContext } from 'schema-dts';
// const jsonLd: WithContext<Product> = { ... };

// Generate it on the server (SSR/SSG) so crawlers see it in the HTML.
// Google can render JS, but server output is more reliable.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is structured data and Schema.org?**
A1: Structured data is explicit, machine-readable markup describing page content. Schema.org is the shared vocabulary of types and properties (Product, Article...) supported by Google, Bing, Yahoo and others. It helps search engines understand content and show rich results.

**Q2: JSON-LD vs Microdata vs RDFa?**
A2: Microdata and RDFa add attributes inline to HTML elements. JSON-LD is a separate JSON block in a script tag. Google recommends JSON-LD because it is easier to write, maintain, and generate from data, and does not clutter the markup.

**Q3: Does structured data improve rankings?**
A3: Not directly. It is not a ranking factor by itself, but it makes you eligible for rich results, which raise click-through rate, and helps engines understand the page. Rich results are never guaranteed.

**Q4: What are the rules for valid structured data?**
A4: Markup must reflect content visible to users, use correct types with required properties, be valid JSON, and not be misleading (fake reviews break guidelines and can cause manual actions). Validate with Rich Results Test and Schema Markup Validator.

**Q5: How do you add it in Next.js safely?**
A5: Render a `<script type="application/ld+json">` in a Server Component with `JSON.stringify` of an object, escaping `<` to prevent script injection from user data. Use `schema-dts` for typing.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Marked-up data not visible on the page
✅ **Correct way:** Only mark up what users can actually see (price, rating).

❌ **Mistake 2:** Invalid JSON (trailing comma, single quotes)
```json
{ "name": "X", }   // WRONG: trailing comma
{ "name": "X" }    // CORRECT
```

❌ **Mistake 3:** Price as text with symbol
```json
"price": "Rs. 2,999"   // WRONG
"price": "2999.00", "priceCurrency": "INR"   // CORRECT
```

❌ **Mistake 4:** Fake or self-serving reviews
✅ **Correct way:** Use genuine ratings from real users only.

❌ **Mistake 5:** Putting unsanitised user text in JSON-LD via `dangerouslySetInnerHTML`
✅ **Correct way:** Escape `<` as `<`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured data | Machine-readable page info | Machine के लिए पढ़ने योग्य जानकारी |
| Schema.org | Shared vocabulary of types | Types की साझा शब्दावली |
| JSON-LD | JSON script-based format | Script में JSON format |
| Microdata | Inline HTML attributes format | HTML attributes वाला format |
| Rich result | Enhanced search listing | Stars/price वाला search result |
| @type | Kind of thing described | चीज़ का प्रकार |
| @context | Vocabulary URL | शब्दावली का URL |
| Rich Results Test | Google's validation tool | Google का जाँच tool |

---

## ⚡ 3-Line Summary
**English:**
1. Structured data describes your content to search engines using Schema.org types, best written as JSON-LD.
2. It makes pages eligible for rich results (price, stars, recipe, breadcrumbs); it matches visible content and is validated with Rich Results Test.
3. In Next.js render JSON-LD from a Server Component, escape `<`, and type it with `schema-dts`.

**Hindi:**
1. Structured data Schema.org types से search engines को content समझाता है; सबसे अच्छा JSON-LD में।
2. इससे rich results (price, stars, recipe, breadcrumbs) की eligibility मिलती है; data दिखने वाले content से मेल खाए और Rich Results Test से जाँचो।
3. Next.js में Server Component से JSON-LD render करो, `<` escape करो, और `schema-dts` से type दो।

---

## ➡️ Next Topic
**44. HTML Security (XSS, Content Security Policy)** — अब सीखें कि user के input और scripts से site को हमलों से कैसे बचाएँ।
