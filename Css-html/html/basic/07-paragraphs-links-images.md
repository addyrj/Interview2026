# 7. Paragraphs, Links, Images
# हिंदी में: Paragraphs, Links और Images

---

## 🔵 Simple Definition (English)
`<p>` holds a paragraph of text. `<a href>` creates a **hyperlink** to another page, section, file, email or phone number. `<img src alt>` embeds an **image**. These three are the most-used content elements of the web.

## 🔵 सरल परिभाषा (Hindi)
`<p>` text का एक paragraph रखता है। `<a href>` दूसरे page, section, file, email या phone number का **hyperlink** बनाता है। `<img src alt>` **image** दिखाता है। ये तीनों web के सबसे ज़्यादा इस्तेमाल होने वाले content elements हैं।

---

## 🔴 Problem it Solves
```
- Text needs structure: without <p>, all text collapses into one line (HTML ignores plain
  line breaks and extra spaces).
- Documents needed to CONNECT: <a> is the "Hyper" in HyperText, what makes the web a web.
- Pages need visuals: <img> loads pictures; the alt attribute covers broken images,
  slow networks, screen readers and SEO image search.
```

## 🔴 यह क्यों बना? (Hindi)
```
- Text को structure चाहिए: <p> के बिना सारा text एक line में मिल जाता है
  (HTML plain line breaks और extra spaces को ignore करता है)।
- Documents को जोड़ना था: <a> वही "Hyper" है जो web को web बनाता है।
- Pages को visuals चाहिए: <img> pictures लाता है; alt attribute टूटी image, slow network,
  screen reader और image search के काम आता है।
```

---

## 🟢 How it Works — Step by Step

```
PARAGRAPHS
  <p>Text</p>        block element, default margin ~1em top and bottom
  <br>               forced line break (inside an address/poem, NOT for spacing)
  <hr>               thematic break (horizontal rule)
  <strong> <em>      importance / emphasis (semantic)   vs   <b> <i> (style only)
  <pre>              preserves spaces and line breaks (code)
  HTML COLLAPSES whitespace: many spaces/newlines = one space.

LINKS <a>
  <a href="URL">text</a>
  href forms:
    https://site.com/page    absolute URL (other site)
    /about                   root-relative (same site)
    ../img/a.png             relative path
    #section-id              jump within the page (matches an element's id)
    mailto:me@x.com          opens mail app
    tel:+911234567890        dials on phones
  Attributes:
    target="_blank"          open in a new tab
    rel="noopener noreferrer" ALWAYS with _blank for security (modern browsers imply
                              noopener, but write it anyway for older ones)
    download                 download file instead of navigating
    title                    tooltip (not reliable for a11y)
  Link text must describe the destination ("View order", not "click here").

IMAGES <img>
  <img src="cat.jpg" alt="Orange cat sleeping on a sofa" width="600" height="400">
  src      path/URL of the image (required)
  alt      text alternative (required for a11y; alt="" for purely decorative images)
  width + height   reserve space -> prevents layout shift (CLS)
  loading="lazy"   load only when near viewport (below-the-fold images)
  srcset + sizes   different image files for different screen sizes
  <img> is a VOID element: no closing tag, and an INLINE replaced element.
  Formats: JPEG (photos), PNG (transparency), SVG (icons/logos), WebP/AVIF (smaller, modern)

  <figure><img ...><figcaption>Caption</figcaption></figure>  image with a caption
  <a href="/product"><img src="p.jpg" alt="Blue shoes"></a>   image link: alt = link text
```

## 🟢 कैसे काम करता है? (Hindi)
```
PARAGRAPH:
  <p> block element है। HTML में कई spaces/newlines = एक space (collapse)।
  <br> सिर्फ line break के लिए, spacing के लिए नहीं।
  <strong>/<em> meaning देते हैं, <b>/<i> सिर्फ style।

LINK:
  href से destination तय होता है: https://... (बाहर), /about (अपनी site), #id (उसी page में),
  mailto: (email), tel: (call)।
  target="_blank" के साथ rel="noopener noreferrer" ज़रूर लिखो (security)।
  Link text साफ़ हो: "Order देखें", "यहाँ क्लिक करें" नहीं।

IMAGE:
  src = image का path, alt = image का text विकल्प (ज़रूरी)।
  width और height दो ताकि layout न उछले।
  नीचे की images में loading="lazy" लगाओ।
  Decorative image के लिए alt="" (खाली) रखो।
```

---

## 🟡 Real World Example
**Amazon product listing:** Each product tile is an `<a>` wrapping an `<img>` (with alt like "boAt Rockerz 450 Bluetooth Headphones") and a title. Below-the-fold tiles use `loading="lazy"` and `srcset` so a phone downloads a 300px image while a retina laptop gets a 600px one. External seller links open with `target="_blank" rel="noopener"`. The footer has `mailto:` and `tel:` links for support. Descriptions are `<p>` elements.

## 🟡 Real Example Hindi mein
**Amazon product listing:** हर product tile एक `<a>` है जिसमें `<img>` (alt जैसे "boAt Rockerz 450 Bluetooth Headphones") और title है। नीचे की tiles में `loading="lazy"` और `srcset` होता है, जिससे phone 300px की image download करता है और retina laptop 600px की। बाहरी seller links `target="_blank" rel="noopener"` से खुलते हैं। Footer में support के लिए `mailto:` और `tel:` links हैं। Descriptions `<p>` में होती हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Paragraphs, Links, Images</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 680px; margin: 0 auto; padding: 24px; line-height: 1.7; color: #222; }

    p { margin: 0 0 1em; max-width: 65ch; }           /* readable line length */
    a { color: #1a73e8; }                              /* link color */
    a:hover { text-decoration: none; }                 /* underline off on hover */
    a:focus-visible { outline: 3px solid #fbbc04; }    /* visible keyboard focus */

    /* Responsive image: never overflow its container */
    img { max-width: 100%; height: auto; display: block; border-radius: 8px; }

    /* Product card = image link */
    .product { display: inline-block; text-decoration: none; color: inherit;
               border: 1px solid #ddd; border-radius: 10px; padding: 12px; width: 220px; }
    .product:hover { box-shadow: 0 4px 12px rgba(0,0,0,.15); }
    .product img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; }
    .price { color: #b12704; font-weight: bold; }       /* Amazon-style price red */
    figure { margin: 24px 0; }
    figcaption { font-size: 14px; color: #666; margin-top: 6px; }
    section { margin-bottom: 28px; }
  </style>
</head>
<body>
  <h1>Paragraphs, Links, Images</h1>

  <section>
    <h2>Paragraphs</h2>
    <p>HTML collapses     extra   spaces
       and line breaks into a single space.</p>
    <p>Use <strong>strong</strong> for importance and <em>em</em> for emphasis.
       Use <code>br</code> only for real line breaks:<br>
       like this second line of an address.</p>
    <hr>   <!-- thematic break -->
    <pre>
preserved   spacing
   in pre tag</pre>
  </section>

  <section>
    <h2>Links</h2>
    <ul>
      <!-- absolute external link in new tab, with security rel -->
      <li><a href="https://developer.mozilla.org" target="_blank" rel="noopener noreferrer">MDN Web Docs (new tab)</a></li>
      <!-- in-page link: jumps to element with id="images" -->
      <li><a href="#images">Jump to Images section</a></li>
      <!-- email and phone -->
      <li><a href="mailto:support@example.com?subject=Help">Email support</a></li>
      <li><a href="tel:+911234567890">Call +91 12345 67890</a></li>
      <!-- download attribute (works for same-origin files) -->
      <li><a href="data:text/plain;charset=utf-8,Hello%20from%20HTML" download="hello.txt">Download hello.txt</a></li>
    </ul>
  </section>

  <section id="images">
    <h2>Images</h2>

    <!-- 1. Informative image: meaningful alt, width/height prevent layout shift -->
    <figure>
      <img src="https://picsum.photos/id/237/600/300"
           alt="Black puppy sitting on a wooden floor"
           width="600" height="300" loading="lazy">
      <figcaption>Figure 1: A real image with alt text and a caption.</figcaption>
    </figure>

    <!-- 2. Decorative image: empty alt, screen readers skip it -->
    <img src="https://picsum.photos/id/10/600/100" alt="" width="600" height="100" loading="lazy">

    <!-- 3. Image inside a link: alt describes the DESTINATION/PRODUCT -->
    <p></p>
    <a class="product" href="#images">
      <img src="https://picsum.photos/id/1/300/300" alt="Laptop on a desk with a notebook" width="300" height="300" loading="lazy">
      <div>Work Laptop Bundle</div>
      <div class="price">Rs 49,999</div>
    </a>

    <!-- 4. Broken image: alt text appears instead (why alt matters) -->
    <p>Broken image example:
      <img src="missing-file.png" alt="[alt text shown because the file failed to load]" style="display:inline">
    </p>
  </section>
</body>
</html>
```

(The picsum.photos demo images need internet. Replace with your own files if offline.)

---

## 🟠 React/Next.js Connection

```jsx
// 1. Links: use next/link for internal navigation; plain <a> for external
import Link from "next/link";
<Link href="/orders">My orders</Link>
<a href="https://mdn.io" target="_blank" rel="noopener noreferrer">MDN</a>

// 2. Images: next/image gives lazy loading, responsive srcset, WebP/AVIF and prevents CLS
import Image from "next/image";
<Image
  src="/shoes.jpg"          // local file in /public, or remote (allow domain in next.config)
  alt="Blue running shoes"  // still REQUIRED
  width={600}
  height={400}
  priority                  // for the LCP / hero image: disables lazy loading
/>

// 3. JSX differences: className, self-closing <img />, htmlFor, camelCase attrs
<img src={product.img} alt={product.name} className="rounded-lg w-full" />

// 4. Tailwind responsive image + line-length:
<p className="max-w-prose leading-7 text-gray-700">...</p>
<img className="w-full h-auto object-cover rounded-lg" src="/a.jpg" alt="" />

// 5. dangerouslySetInnerHTML for CMS paragraphs: sanitize first (XSS).
```

---

## ⚫ Interview Questions + Answers

**Q1: Why is the `alt` attribute important?**
A1: It is the **text alternative** for an image: screen readers read it, it shows when the image fails to load, and search engines use it to understand the image (image SEO). Informative images need a descriptive alt; decorative images get `alt=""` so assistive tech skips them. Never omit the attribute (readers may read the file name).

**Q2: What does `target="_blank"` do and why add `rel="noopener noreferrer"`?**
A2: It opens the link in a new tab. Without `noopener`, the new page gets a `window.opener` reference and could redirect your page (**reverse tabnabbing**). Modern browsers treat `_blank` as `noopener` by default, but writing it keeps older browsers safe. `noreferrer` also hides the referrer URL.

**Q3: Difference between `<strong>`/`<em>` and `<b>`/`<i>`?**
A3: `<strong>` = strong importance, `<em>` = stress emphasis; both have meaning for assistive tech. `<b>` and `<i>` are for stylistic offsets (keywords, foreign terms, thoughts) without added importance. All four render bold/italic by default, but you should choose by meaning.

**Q4: How do you make images responsive and avoid layout shift?**
A4: Set `width` and `height` attributes (browser computes aspect ratio before load), then CSS `max-width: 100%; height: auto`. Use `srcset`/`sizes` or `<picture>` for different resolutions, `loading="lazy"` for off-screen images, and modern formats (WebP/AVIF). In Next.js use `next/image`.

**Q5: Relative vs absolute vs root-relative URL?**
A5: **Absolute**: full URL (`https://site.com/a.png`). **Relative**: from the current file (`../img/a.png`, `a.png`). **Root-relative**: from the domain root (`/img/a.png`). Root-relative is robust for site-internal links; relative is good for portable folders; absolute is needed for external resources.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Missing or useless alt
```html
<!-- WRONG --> <img src="p.jpg"> <img src="p.jpg" alt="image">
<!-- ✅ Correct way --> <img src="p.jpg" alt="Red Nike running shoe, side view">
```

❌ **Mistake 2:** Using `<br><br>` for paragraph spacing
```html
<!-- WRONG --> Line one<br><br>Line two
<!-- ✅ Correct way --> <p>Line one</p><p>Line two</p>  <!-- spacing via CSS margin -->
```

❌ **Mistake 3:** "Click here" links
```html
<!-- WRONG --> <a href="/pricing">Click here</a> to see pricing
<!-- ✅ Correct way --> See our <a href="/pricing">pricing plans</a>
```

❌ **Mistake 4:** `_blank` without rel; width/height omitted
```html
<!-- ✅ Correct way -->
<a href="https://ext.com" target="_blank" rel="noopener noreferrer">External</a>
<img src="a.jpg" alt="..." width="600" height="400">
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `<p>` | Paragraph block | Paragraph |
| `<a href>` | Hyperlink | Link |
| `<img>` | Embedded image (void element) | Image |
| alt | Text alternative for image | Image का text विकल्प |
| href | Link destination | Link का पता |
| rel="noopener" | Prevents tabnabbing | सुरक्षा के लिए rel |
| srcset | Multiple image sizes | अलग-अलग size की images |
| Lazy loading | Load when needed | ज़रूरत पर load |
| CLS | Layout shift metric | Layout उछलने का माप |
| Void element | Tag with no closing tag | बिना closing tag वाला element |

---

## ⚡ 3-Line Summary
**English:**
1. `<p>` for text blocks, `<a href>` for links (descriptive text, `rel="noopener"` with `_blank`), `<img>` for images.
2. Always write a meaningful `alt`, set `width`/`height`, and lazy-load below-the-fold images.
3. HTML collapses whitespace: use `<p>` and CSS for spacing, not `<br>` or repeated spaces.

**Hindi:**
1. text के लिए `<p>`, links के लिए `<a href>` (साफ़ text, `_blank` के साथ `rel="noopener"`), images के लिए `<img>`।
2. हमेशा अर्थपूर्ण `alt`, `width`/`height` दो और नीचे की images lazy-load करो।
3. HTML whitespace collapse करता है: spacing के लिए `<p>` और CSS, `<br>` या extra spaces नहीं।

---

## ➡️ Next Topic
**8. Lists (ul, ol, dl)** — content ko items ki list mein kaise likhte hain: bulleted, numbered aur description lists।
