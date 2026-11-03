# 15. Meta Tags (charset, viewport, description, og tags)
# हिंदी में: Meta Tags — Page के बारे में छुपी हुई जानकारी

---

## 🔵 Simple Definition (English)
`<meta>` tags live inside `<head>` and give **metadata** (data about the page) to browsers, search engines and social apps. They are not shown on the page. Important ones: `charset` (text encoding), `viewport` (mobile layout), `description` (search snippet) and Open Graph `og:*` tags (link preview cards).

## 🔵 सरल परिभाषा (Hindi)
`<meta>` tags `<head>` के अंदर होते हैं और browsers, search engines और social apps को page का **metadata** (page के बारे में data) देते हैं। ये page पर दिखाई नहीं देते। ज़रूरी tags: `charset` (text encoding), `viewport` (mobile layout), `description` (search snippet) और Open Graph `og:*` (link preview card)।

---

## 🔴 Problem it Solves
```
WITHOUT META TAGS:
  - No charset      -> "â€™" garbage characters, Hindi text broken (mojibake)
  - No viewport     -> phone shows a tiny zoomed-out desktop page (980px wide)
  - No description  -> Google picks random text for the search result snippet
  - No og tags      -> WhatsApp/Twitter/LinkedIn shows a plain ugly link, no image

WITH META TAGS:
  - Correct text everywhere
  - Responsive layout on phones
  - Controlled search snippet
  - Rich preview card with title, image and description when the link is shared
```

## 🔴 यह क्यों बना? (Hindi)
```
META TAGS के बिना:
  - charset नहीं     -> अजीब characters, हिंदी text टूट जाता है
  - viewport नहीं    -> phone पर छोटा zoom-out desktop page दिखता है
  - description नहीं -> Google search result में कोई भी random text दिखाता है
  - og tags नहीं     -> WhatsApp/Twitter/LinkedIn पर सिर्फ सादा link, image नहीं

META TAGS के साथ:
  - हर जगह सही text
  - Phone पर responsive layout
  - Search snippet आपके control में
  - Link share करने पर title, image और description वाला preview card
```

---

## 🟢 How it Works — Step by Step

```
SYNTAX: <meta> is a void element (no closing tag). Two main forms:
   <meta charset="UTF-8">                      (single attribute)
   <meta name="description" content="...">     (name + content pair)
   <meta property="og:title" content="...">    (Open Graph uses property)
   <meta http-equiv="refresh" content="...">   (acts like an HTTP header)

1. charset
   <meta charset="UTF-8">
   - Must appear within the first 1024 bytes of the document; put it FIRST in <head>.
   - UTF-8 supports every language and emoji. Always use it.

2. viewport
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   - width=device-width: layout width = real screen width (not fake 980px)
   - initial-scale=1: no initial zoom
   - Do NOT add user-scalable=no or maximum-scale=1: it blocks pinch-zoom
     (accessibility failure, WCAG 1.4.4).
   - Without it, your CSS media queries do not behave as expected on phones.

3. description
   <meta name="description" content="Order food online from 1000+ restaurants.">
   - Google may use it as the snippet under the blue link (not a ranking factor).
   - Aim for roughly 120-160 characters, unique per page.

4. robots / theme-color / author
   <meta name="robots" content="noindex, nofollow">   (keep page out of Google)
   <meta name="theme-color" content="#e23744">        (mobile browser toolbar color)
   <meta name="color-scheme" content="light dark">    (opt into dark UI defaults)

5. Open Graph (Facebook protocol, used by WhatsApp, LinkedIn, Slack, etc.)
   og:title  og:description  og:image (absolute URL, ~1200x630)  og:url  og:type
   Twitter/X: twitter:card (summary_large_image), twitter:title, twitter:image
   Crawlers read the raw HTML ONLY. They do not run JavaScript,
   so client-rendered tags set later by JS will not show up.

HOW THE BROWSER USES THEM: it reads <head> during parsing, picks the encoding,
sets the layout viewport, and exposes the rest to crawlers and share dialogs.
```

## 🟢 कैसे काम करता है? (Hindi)

```
SYNTAX: <meta> void element है (closing tag नहीं)।
   <meta charset="UTF-8">
   <meta name="description" content="...">
   <meta property="og:title" content="...">

1. charset  -> <meta charset="UTF-8">
   - Document के पहले 1024 bytes में होना चाहिए; <head> में सबसे पहले लिखो।
   - UTF-8 हर भाषा और emoji सपोर्ट करता है। हमेशा यही use करो।

2. viewport -> <meta name="viewport" content="width=device-width, initial-scale=1.0">
   - width=device-width: layout की चौड़ाई = असली screen की चौड़ाई
   - user-scalable=no मत लगाओ: pinch-zoom रुक जाता है (accessibility गलती)।
   - इसके बिना media queries phone पर ठीक से काम नहीं करतीं।

3. description -> Google result के नीचे का snippet। लगभग 120-160 characters,
   हर page के लिए अलग।

4. robots / theme-color
   <meta name="robots" content="noindex"> -> page को Google से दूर रखता है
   <meta name="theme-color" content="#e23744"> -> mobile toolbar का रंग

5. Open Graph: og:title, og:description, og:image (पूरा absolute URL, ~1200x630),
   og:url, og:type। Crawlers सिर्फ raw HTML पढ़ते हैं, JavaScript नहीं चलाते।
```

---

## 🟡 Real World Example
**Amazon / Instagram link in WhatsApp:** when you paste an Instagram post link into WhatsApp, a card appears with the photo, caption and site name. That card is built from `og:title`, `og:description`, `og:image` in the page's `<head>`. **Zomato** sets a unique `description` per restaurant page, so Google shows "Order from Biryani Blues, Indiranagar..." under the search result. And every site on your phone uses `viewport` so it does not appear as a tiny desktop page.

## 🟡 Real Example Hindi mein
**Amazon / Instagram link WhatsApp में:** जब आप Instagram post का link WhatsApp में paste करते हो तो photo, caption और site name वाला card दिखता है। यह card page के `<head>` के `og:title`, `og:description`, `og:image` से बनता है। **Zomato** हर restaurant page के लिए अलग `description` रखता है, इसलिए Google में "Order from Biryani Blues, Indiranagar..." दिखता है। और phone पर हर site `viewport` की वजह से छोटे desktop page की तरह नहीं दिखती।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- 1. Encoding: first thing in <head>, within first 1024 bytes -->
  <meta charset="UTF-8">

  <!-- 2. Mobile layout: layout width = device width. Do NOT disable zoom. -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- 3. Page title (not a meta tag but the most important SEO element) -->
  <title>Biryani Blues - Order Online | FoodApp</title>

  <!-- 4. Search snippet, ~150 chars, unique per page -->
  <meta name="description" content="Order hot Hyderabadi biryani online from Biryani Blues. Fast delivery in 30 minutes, live tracking and 50% off on your first order.">

  <!-- 5. Robots: index and follow are the defaults; shown here for learning -->
  <meta name="robots" content="index, follow">

  <!-- 6. Browser UI color (mobile Chrome address bar) and color scheme -->
  <meta name="theme-color" content="#e23744">
  <meta name="color-scheme" content="light dark">

  <!-- 7. Open Graph: link preview in WhatsApp, LinkedIn, Slack, Facebook.
        image must be an ABSOLUTE https URL, recommended 1200x630 -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="FoodApp">
  <meta property="og:title" content="Biryani Blues - Order Online">
  <meta property="og:description" content="Hot Hyderabadi biryani delivered in 30 minutes.">
  <meta property="og:image" content="https://example.com/images/biryani-1200x630.jpg">
  <meta property="og:image:alt" content="A plate of Hyderabadi chicken biryani">
  <meta property="og:url" content="https://example.com/restaurants/biryani-blues">

  <!-- 8. Twitter/X card: falls back to og tags for title/description/image -->
  <meta name="twitter:card" content="summary_large_image">

  <!-- 9. Canonical URL helps avoid duplicate content (a <link>, shown for completeness) -->
  <link rel="canonical" href="https://example.com/restaurants/biryani-blues">

  <style>
    /* Simple styling so the demo page looks fine */
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; line-height: 1.6; }
    code { background: #f1f1f1; padding: 2px 6px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>नमस्ते! Biryani Blues 🍗</h1>
  <p>Hindi text and the emoji render correctly because of <code>&lt;meta charset="UTF-8"&gt;</code>.</p>
  <p>Open DevTools, then Elements, then <code>&lt;head&gt;</code> to see all meta tags.</p>
  <p>Shrink the window or use mobile emulation: the page fits because of the <code>viewport</code> tag.</p>
</body>
</html>
```

```css
/* Meta tags are HTML, but viewport pairs with CSS like this: */
.container { width: min(100% - 2rem, 1100px); margin-inline: auto; }
@media (max-width: 600px) { .container { font-size: 16px; } }
/* Without the viewport meta, this 600px query would never match on a phone,
   because the phone pretends to be ~980px wide. */
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js App Router: DO NOT hand-write <meta> in components.
// Export a metadata object (static) or generateMetadata (dynamic).
// Next.js puts charset and viewport in by default and renders tags on the SERVER,
// so social crawlers can read them.

// app/restaurants/[slug]/page.tsx
export async function generateMetadata({ params }) {
  const r = await getRestaurant(params.slug);       // fetch data
  return {
    title: `${r.name} - Order Online`,
    description: r.summary,
    openGraph: {
      title: r.name,
      description: r.summary,
      images: [{ url: r.image, width: 1200, height: 630 }],
      type: 'website',
    },
    twitter: { card: 'summary_large_image' },
    robots: { index: true, follow: true },
  };
}

// app/layout.tsx : viewport is its own export in Next.js 14+
export const viewport = { width: 'device-width', initialScale: 1, themeColor: '#e23744' };

// Plain React (Vite/CRA, client-only): use a library such as react-helmet-async,
// BUT crawlers that do not run JS will still see the empty index.html.
// That is one big reason to use Next.js (SSR/SSG) for SEO and share cards.
// Pages Router: <Head><title>...</title><meta name="description" content="..." /></Head>
```

---

## ⚫ Interview Questions + Answers

**Q1: Why is `<meta charset="UTF-8">` important and where should it go?**
A1: It tells the browser how to decode bytes into characters. Without it the browser may guess wrong and show garbage for non-English text or special symbols. It must be within the first 1024 bytes, so put it as the first child of `<head>`, before `<title>` or anything with text. UTF-8 covers all languages and emoji.

**Q2: What does the viewport meta tag do and what should you avoid in it?**
A2: On mobile, browsers by default render pages in a virtual ~980px wide viewport and shrink it down. `width=device-width, initial-scale=1` makes the layout width equal the real device width so responsive CSS and media queries work. Avoid `user-scalable=no` and `maximum-scale=1`, because they stop users from zooming, which harms accessibility.

**Q3: What are Open Graph tags and why do they matter?**
A3: Open Graph (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`) is a protocol from Facebook that social platforms and chat apps read to build a link preview card. Image should be an absolute URL, around 1200x630. Crawlers do not execute JavaScript, so tags must be in the server-rendered HTML (Next.js `metadata` handles this).

**Q4: Does `<meta name="description">` improve Google ranking?**
A4: Not directly; Google does not use it as a ranking factor. But Google often shows it as the snippet, so a good unique description improves click-through rate. Google may also ignore it and generate its own snippet from page content. Keep it about 120-160 characters, unique per page.

**Q5: What is the difference between `name`, `property` and `http-equiv` in meta tags?**
A5: `name` + `content` is the standard way for general metadata (description, viewport, robots, theme-color). `property` + `content` is used by Open Graph (and RDFa) tags like `og:title`. `http-equiv` simulates an HTTP response header (for example `refresh` or `content-security-policy`), though real headers are preferred. `charset` is a standalone attribute.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Missing viewport tag
```html
<head><title>My site</title></head>   <!-- phone shows a zoomed-out desktop page -->
```
✅ **Correct way:** `<meta name="viewport" content="width=device-width, initial-scale=1.0">`

❌ **Mistake 2:** Disabling zoom
```html
<meta name="viewport" content="width=device-width, user-scalable=no, maximum-scale=1">
```
✅ **Correct way:** Leave zoom enabled; it is an accessibility requirement.

❌ **Mistake 3:** Relative `og:image` or the same tags on every page
```html
<meta property="og:image" content="/img/cover.png">   <!-- crawlers may not resolve this -->
```
✅ **Correct way:** Use the full `https://...` URL and generate unique title/description/image per page (`generateMetadata` in Next.js).

❌ **Mistake 4:** Putting `<meta charset>` late in `<head>` or setting tags only via client-side JS
✅ **Correct way:** First in `<head>`, and render SEO/OG tags on the server so crawlers can see them.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metadata | Data about the page | Page के बारे में data |
| charset | Character encoding (UTF-8) | Text encoding |
| viewport | Visible area/layout width on a device | Device पर दिखने वाला area |
| description | Search result snippet text | Search snippet |
| Open Graph (og) | Tags for link preview cards | Link preview के tags |
| robots | Instructions for crawlers | Crawlers के लिए निर्देश |
| canonical | Preferred URL of a page | Page का मुख्य URL |
| theme-color | Browser toolbar color on mobile | Mobile toolbar का रंग |

---

## ⚡ 3-Line Summary
**English:**
1. `<meta>` tags in `<head>` give metadata to browsers, search engines and social apps; they are invisible on the page.
2. Always include `charset="UTF-8"` first and `viewport` (`width=device-width, initial-scale=1`); add `description` and `og:*` for SEO and share cards.
3. In Next.js use the `metadata` / `generateMetadata` API so tags are server-rendered and crawlers can read them.

**Hindi:**
1. `<head>` के `<meta>` tags browsers, search engines और social apps को metadata देते हैं; page पर दिखते नहीं।
2. हमेशा सबसे पहले `charset="UTF-8"` और `viewport` रखो; SEO और share card के लिए `description` और `og:*` जोड़ो।
3. Next.js में `metadata` / `generateMetadata` use करो ताकि tags server पर बनें और crawlers पढ़ सकें।

---

## ➡️ Next Topic
**16. HTML Comments** — code में notes कैसे लिखें जो browser में दिखें नहीं, और उन्हें कब use करना चाहिए।
