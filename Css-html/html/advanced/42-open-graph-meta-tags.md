# 42. Open Graph Meta Tags
# हिंदी में: Open Graph Meta Tags — Link Share करने पर Preview Card

---

## 🔵 Simple Definition (English)
**Open Graph (OG)** is a set of `<meta property="og:...">` tags in `<head>` that tell social platforms (Facebook, LinkedIn, WhatsApp, Slack, X) what **title, description, image and URL** to show when your link is shared. Twitter/X also has its own `twitter:` card tags, and falls back to OG.

## 🔵 सरल परिभाषा (Hindi)
**Open Graph (OG)** `<head>` में `<meta property="og:...">` tags का set है, जो Facebook, LinkedIn, WhatsApp, Slack, X जैसे platforms को बताता है कि link share होने पर कौन सा **title, description, image और URL** दिखाना है। X (Twitter) के अपने `twitter:` card tags भी हैं और वो OG पर fallback करता है।

---

## 🔴 Problem it Solves
```
WITHOUT OG:
  - You paste your link in WhatsApp -> plain URL or random text/image
  - Platform guesses title and picks a random image (or none)
  - Low click-through rate; looks unprofessional

WITH OG:
  - Rich card: big image + bold title + short description
  - You control what the world sees when the page is shared
  - Marketing/SEO teams care: shares drive traffic
```

## 🔴 यह क्यों बना? (Hindi)
```
OG के बिना:
  - WhatsApp में link paste करो -> सिर्फ URL या अजीब text/image
  - Platform खुद अंदाज़ा लगाता है, कभी image नहीं मिलती
  - Clicks कम, unprofessional दिखता है

OG के साथ:
  - बड़ी image + title + description वाला सुंदर card
  - Share होने पर लोग क्या देखेंगे, यह आप तय करते हैं
```

---

## 🟢 How it Works — Step by Step

```
FLOW:
  1. User pastes/shares https://yoursite.com/product/42
  2. Platform's crawler (facebookexternalhit, LinkedInBot, WhatsApp, Twitterbot)
     fetches the HTML of that URL (it does NOT run most JS!)
  3. It reads <meta property="og:*"> from <head>
  4. It builds a preview card and often CACHES it
  5. Updating tags later needs a re-scrape (Facebook Sharing Debugger,
     LinkedIn Post Inspector)

CORE TAGS:
  og:title         Title of the page (60-90 chars)
  og:description   1-2 lines (~ 150-200 chars)
  og:image         Absolute URL (https://...), recommended 1200x630 px, <5 MB
  og:url           Canonical URL of the page
  og:type          website | article | product | video.other
  og:site_name     Brand name
  og:locale        en_US / hi_IN
  og:image:alt     Description of the image

TWITTER/X:
  twitter:card     summary_large_image | summary
  twitter:title / twitter:description / twitter:image (fall back to OG if missing)

IMPORTANT:
  - Tags must be in the server-rendered HTML (SSR/SSG), because crawlers
    mostly do not execute JavaScript. A client-only SPA will show no preview.
  - Image URL must be absolute and publicly accessible.
  - <meta name="description"> is for search engines; og:description for social.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Flow:
  1. User आपका link share करता है
  2. Platform का crawler (WhatsApp, LinkedInBot, Twitterbot...) page का HTML मँगवाता है
     (ज़्यादातर JS नहीं चलाता!)
  3. <head> के og: tags पढ़ता है
  4. Preview card बनाकर अक्सर CACHE कर देता है
  5. बाद में tags बदलो तो Facebook Sharing Debugger / LinkedIn Post Inspector से re-scrape कराओ

मुख्य tags: og:title, og:description, og:image (absolute URL, 1200x630),
og:url, og:type, og:site_name

ध्यान रखो: tags server-rendered HTML में होने चाहिए (SSR/SSG)।
सिर्फ client-side SPA में preview नहीं बनेगा।
```

---

## 🟡 Real World Example
**Swiggy/Zomato restaurant link on WhatsApp:** When someone shares a restaurant page, WhatsApp shows the restaurant photo, name "Meghana Foods - Order Online" and a line about cuisine and rating: these come from `og:image`, `og:title` and `og:description` generated per restaurant. **Amazon** product links show product image and title. **Medium/Dev.to** blog posts use `og:type="article"` with author and published time.

## 🟡 Real Example Hindi mein
**WhatsApp पर Swiggy/Zomato का restaurant link:** जब कोई restaurant का page share करता है तो WhatsApp restaurant की photo, नाम "Meghana Foods - Order Online" और cuisine/rating की line दिखाता है। ये सब हर restaurant के लिए बने `og:image`, `og:title`, `og:description` से आता है। **Amazon** के product links में product की image और title दिखता है। **Medium/Dev.to** के blog posts `og:type="article"` के साथ author और published time देते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Biryani House - Order Online | Hyderabad</title>

  <!-- Normal SEO tags (for Google) -->
  <meta name="description" content="Order authentic Hyderabadi biryani online. Delivery in 30 minutes.">
  <link rel="canonical" href="https://example.com/restaurants/biryani-house">

  <!-- ───────── Open Graph (Facebook, LinkedIn, WhatsApp, Slack) ───────── -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="FoodApp">
  <meta property="og:title" content="Biryani House - Order Online">
  <meta property="og:description" content="Authentic Hyderabadi biryani, rated 4.5 by 12,000+ people. Delivery in 30 min.">
  <meta property="og:url" content="https://example.com/restaurants/biryani-house">
  <!-- Absolute URL, 1200x630 recommended (ratio 1.91:1) -->
  <meta property="og:image" content="https://example.com/images/biryani-og-1200x630.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Plate of Hyderabadi chicken biryani with raita">
  <meta property="og:locale" content="en_IN">

  <!-- ───────── Twitter / X card ───────── -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Biryani House - Order Online">
  <meta name="twitter:description" content="Authentic Hyderabadi biryani. Delivery in 30 min.">
  <meta name="twitter:image" content="https://example.com/images/biryani-og-1200x630.jpg">

  <!-- Article example (use instead of og:type website on blog posts):
  <meta property="og:type" content="article">
  <meta property="article:published_time" content="2026-01-15T09:00:00+05:30">
  <meta property="article:author" content="https://example.com/authors/aditya">
  -->
</head>
<body>
  <h1>Biryani House</h1>
  <p>Open this page's source (View Source) to see the OG tags.
     Paste the deployed URL into the Facebook Sharing Debugger or
     LinkedIn Post Inspector to preview the card.</p>

  <script>
    // Quick helper: print all OG tags of this page to the console
    document.querySelectorAll('meta[property^="og:"], meta[name^="twitter:"]')
      .forEach(m => console.log(m.getAttribute('property') || m.getAttribute('name'), '=>', m.content));
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js App Router: export metadata (server-rendered into <head>)
// app/restaurants/[slug]/page.jsx
export async function generateMetadata({ params }) {
  const r = await fetch(`https://api.example.com/restaurants/${params.slug}`).then(x => x.json());
  return {
    title: `${r.name} - Order Online`,
    description: r.tagline,
    openGraph: {
      title: r.name,
      description: r.tagline,
      url: `https://example.com/restaurants/${params.slug}`,
      siteName: 'FoodApp',
      images: [{ url: r.image, width: 1200, height: 630, alt: r.name }],
      type: 'website',
    },
    twitter: { card: 'summary_large_image', title: r.name, images: [r.image] },
  };
}

// Dynamic image generated at build/request time:
// app/restaurants/[slug]/opengraph-image.jsx using next/og ImageResponse

// Set metadataBase in the root layout so relative image URLs become absolute:
// export const metadata = { metadataBase: new URL('https://example.com') };

// Pages Router: use <Head> from 'next/head':
// <Head><meta property="og:title" content="..." /></Head>

// React SPA (Vite/CRA): crawlers do not run JS, so use react-helmet only with
// SSR/prerender, or serve OG from the server.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is Open Graph and why use it?**
A1: A protocol (created by Facebook) using `<meta property="og:*">` tags to control how a page appears when shared on social platforms and messengers: title, description, image, URL, type. It improves link previews and click-through.

**Q2: Which OG tags are essential and what image size is recommended?**
A2: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`. Image should be an absolute https URL, around 1200x630 px (1.91:1), under about 5 MB, with `og:image:alt`.

**Q3: Why does my OG preview not show in a React SPA?**
A3: Social crawlers generally fetch raw HTML and do not execute JavaScript. If tags are added client-side with JS, crawlers never see them. Render tags on the server using SSR/SSG (Next.js metadata API), or prerender.

**Q4: `meta name="description"` vs `og:description`?**
A4: The meta description is used by search engines for snippets. `og:description` is used by social platforms. If OG tags are missing, many platforms fall back to the meta description, but explicit tags are better.

**Q5: You changed the OG image but the old one still shows. Why?**
A5: Platforms cache scraped data. Use Facebook Sharing Debugger ("Scrape Again") or LinkedIn Post Inspector, or change the image URL (cache busting like `?v=2`).

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Relative image URL
```html
<!-- WRONG -->
<meta property="og:image" content="/img/og.jpg">
<!-- CORRECT -->
<meta property="og:image" content="https://example.com/img/og.jpg">
```

❌ **Mistake 2:** Using `name` instead of `property`
```html
<!-- WRONG: OG uses property -->
<meta name="og:title" content="Hi">
<!-- CORRECT -->
<meta property="og:title" content="Hi">
```

❌ **Mistake 3:** Tags injected only by client JS
✅ **Correct way:** Render in server HTML (Next.js `metadata` / `generateMetadata`).

❌ **Mistake 4:** Tiny or wrongly sized image (cropped or ignored)
✅ **Correct way:** 1200x630 JPG/PNG/WebP, important content centered.

❌ **Mistake 5:** Image on localhost or behind login
✅ **Correct way:** Must be public over https, reachable by the crawler.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Open Graph | Meta tags for share previews | Share preview के लिए meta tags |
| og:image | Preview image URL | Preview की image |
| og:title | Preview headline | Preview का शीर्षक |
| Twitter Card | X-specific preview tags | X के लिए preview tags |
| Crawler/Bot | Fetches HTML for preview | Preview के लिए HTML मँगाने वाला bot |
| Canonical URL | Preferred URL of a page | Page का मुख्य URL |
| Scrape cache | Stored preview data | Saved preview data |
| SSR | HTML rendered on server | Server पर बना HTML |

---

## ⚡ 3-Line Summary
**English:**
1. Open Graph meta tags control the title, description and image shown when your link is shared.
2. Use absolute https image URLs (1200x630), `property="og:*"`, plus `twitter:card`, in server-rendered HTML.
3. In Next.js use `metadata`/`generateMetadata` and `opengraph-image`; refresh caches with Facebook Debugger or LinkedIn Inspector.

**Hindi:**
1. Open Graph meta tags तय करते हैं कि link share होने पर कौन सा title, description और image दिखे।
2. Absolute https image URL (1200x630), `property="og:*"` और `twitter:card` को server-rendered HTML में रखो।
3. Next.js में `metadata`/`generateMetadata` और `opengraph-image` use करो; cache Facebook Debugger या LinkedIn Inspector से refresh करो।

---

## ➡️ Next Topic
**43. Structured Data (Schema.org)** — अब सीखें कि Google को page का मतलब कैसे समझाएँ ताकि search में rich results (stars, price) दिखें।
