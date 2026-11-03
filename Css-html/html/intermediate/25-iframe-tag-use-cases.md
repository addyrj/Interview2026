# 25. iframe Tag + Use Cases
# हिंदी में: iframe Tag — Page के अंदर दूसरा Page

---

## 🔵 Simple Definition (English)
`<iframe>` (inline frame) embeds **another complete HTML page inside your page**. The embedded page has its own DOM, its own CSS and its own JavaScript, isolated from the parent. YouTube videos, Google Maps and payment forms are the common examples.

## 🔵 सरल परिभाषा (Hindi)
`<iframe>` (inline frame) आपके page के अंदर **एक दूसरा पूरा HTML page** दिखाता है। Embedded page का अपना DOM, अपना CSS और अपना JavaScript होता है, parent से अलग। YouTube video, Google Maps और payment form इसके common examples हैं।

---

## 🔴 Problem it Solves
```
BEFORE iframe:
  - You want to show a YouTube video / Google Map / Razorpay payment form on your site.
  - You cannot copy their HTML, CSS and JS into your page (CSS clashes, security risk,
    you cannot maintain Google's code).
  - Linking to another site takes the user away from your page.

WITH iframe:
  - One tag: <iframe src="https://www.youtube.com/embed/ID"></iframe>
  - Third-party code runs in its OWN sandbox. Its CSS cannot break your layout.
  - User stays on your page.
```

## 🔴 यह क्यों बना? (Hindi)
```
iframe से पहले:
  - आपको अपनी site पर YouTube video / Google Map / payment form दिखाना है।
  - दूसरी site का HTML, CSS, JS अपने page में copy नहीं कर सकते (CSS टकराएगी,
    security risk, और Google का code maintain नहीं हो सकता)।
  - सिर्फ link देने से user आपकी site छोड़ देता है।

iframe के साथ:
  - एक tag से दूसरा page अंदर आ जाता है।
  - Third-party code अपने sandbox में चलता है, आपका layout नहीं बिगाड़ता।
  - User आपके ही page पर रहता है।
```

---

## 🟢 How it Works — Step by Step

```
1. Browser parses your HTML and finds <iframe src="...">.
2. It creates a NEW "browsing context" (a nested window with its own document).
3. It makes a separate network request for the src URL.
4. The child page loads with its own DOM, CSS, JS (separate window / document objects).
5. The iframe box is laid out like a replaced element (like <img>), default 300x150px.
6. Parent and child can talk only via:
   - window.postMessage()  (safe, cross-origin allowed)
   - direct DOM access ONLY if same-origin

KEY ATTRIBUTES:
  src        -> URL to embed
  title      -> REQUIRED for accessibility (screen readers announce it)
  width/height
  loading="lazy"  -> load only when near viewport
  sandbox    -> restrict what the embedded page can do
  allow      -> permissions policy (fullscreen; camera; payment)
  referrerpolicy -> how much referrer info to send
  srcdoc     -> inline HTML string instead of a URL

SANDBOX VALUES (empty sandbox = everything blocked):
  allow-scripts   allow-same-origin   allow-forms   allow-popups   allow-modals

SECURITY (the server decides whether it CAN be framed):
  X-Frame-Options: DENY | SAMEORIGIN
  Content-Security-Policy: frame-ancestors 'self' https://partner.com
  -> This is how sites prevent CLICKJACKING. Many sites (Gmail, Instagram login)
     refuse to load inside your iframe.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. Browser HTML पढ़ते हुए <iframe src="..."> देखता है।
2. वो एक नया "browsing context" बनाता है (अलग window + अलग document)।
3. src URL के लिए अलग network request जाती है।
4. Child page अपने DOM, CSS, JS के साथ load होता है।
5. iframe एक replaced element की तरह है (जैसे <img>), default size 300x150px।
6. Parent और child आपस में बात कर सकते हैं:
   - window.postMessage() से (सुरक्षित, cross-origin में भी चलता है)
   - सीधे DOM access सिर्फ same-origin में

ज़रूरी attributes: src, title (accessibility के लिए ज़रूरी), loading="lazy",
sandbox (embedded page की powers कम करता है), allow, srcdoc।

Server भी तय करता है कि उसे frame किया जा सकता है या नहीं
(X-Frame-Options / frame-ancestors) — इससे clickjacking रुकती है।
इसीलिए कई sites आपके iframe में खुलती ही नहीं।
```

---

## 🟡 Real World Example
**Zomato / Swiggy restaurant page:** The "Location" section shows a Google Map of the restaurant. That map is a Google Maps `<iframe>`. **YouTube embeds** on blog posts, **Razorpay / Stripe checkout** inside Amazon-like shopping sites (card fields live in the payment provider's iframe so the merchant never touches raw card numbers), and **Disqus comments** are all iframes. **Gmail** itself sends `X-Frame-Options: SAMEORIGIN`, so you cannot embed Gmail in your site.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy restaurant page:** "Location" section में restaurant का Google Map दिखता है, वो Google Maps का `<iframe>` है। Blog में **YouTube video**, shopping site पर **Razorpay / Stripe checkout** (card fields payment provider के iframe में रहते हैं, इसलिए merchant के पास raw card number कभी नहीं आता), और **Disqus comments** सब iframe हैं। **Gmail** `X-Frame-Options: SAMEORIGIN` भेजता है, इसलिए आप Gmail को अपनी site में embed नहीं कर सकते।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>iframe Demo</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="page">
    <h1>iframe Use Cases</h1>

    <!-- 1. YouTube embed: responsive 16:9 wrapper -->
    <section>
      <h2>1. YouTube video</h2>
      <div class="video-wrap">
        <!-- title is mandatory for screen readers; loading=lazy defers load -->
        <iframe
          src="https://www.youtube.com/embed/dQw4w9WgXcQ"
          title="Sample YouTube video player"
          loading="lazy"
          allow="accelerometer; encrypted-media; picture-in-picture"
          allowfullscreen></iframe>
      </div>
    </section>

    <!-- 2. Google Map embed (restaurant location style) -->
    <section>
      <h2>2. Map</h2>
      <iframe
        class="map"
        src="https://www.openstreetmap.org/export/embed.html?bbox=77.19%2C28.60%2C77.25%2C28.64&amp;layer=mapnik"
        title="Map of central Delhi"
        loading="lazy"></iframe>
    </section>

    <!-- 3. srcdoc + sandbox: run UNTRUSTED html safely (like a code playground) -->
    <section>
      <h2>3. Sandboxed srcdoc</h2>
      <!-- empty sandbox: no scripts, no forms, no popups. The alert below will NOT run -->
      <iframe
        class="sandboxed"
        title="Sandboxed preview"
        sandbox
        srcdoc="<h3 style='font-family:sans-serif'>Hello from srcdoc</h3><script>alert('blocked')</script>"></iframe>
    </section>

    <!-- 4. postMessage: parent talks to child -->
    <section>
      <h2>4. postMessage</h2>
      <button id="send">Send message to iframe</button>
      <iframe
        id="child"
        class="sandboxed"
        title="Message receiver"
        sandbox="allow-scripts"
        srcdoc="<p id='out' style='font-family:sans-serif'>Waiting...</p>
        <script>
          // child listens for messages from the parent
          window.addEventListener('message', function (e) {
            document.getElementById('out').textContent = 'Got: ' + e.data;
          });
        </script>"></iframe>
    </section>
  </main>

  <script>
    // parent sends a message; '*' is OK here only because content is our own srcdoc.
    // In production ALWAYS pass the exact target origin instead of '*'.
    document.getElementById('send').addEventListener('click', function () {
      document.getElementById('child').contentWindow.postMessage('Hello child!', '*');
    });
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }

body { font-family: system-ui, sans-serif; margin: 0; background: #f6f7f9; }
.page { max-width: 760px; margin: 0 auto; padding: 24px 16px; }
section { margin-bottom: 32px; }

/* Responsive 16:9 video: modern way using aspect-ratio */
.video-wrap { width: 100%; aspect-ratio: 16 / 9; }
.video-wrap iframe { width: 100%; height: 100%; border: 0; border-radius: 8px; }

/* Fixed-height iframes */
.map { width: 100%; height: 300px; border: 0; border-radius: 8px; }
.sandboxed { width: 100%; height: 120px; border: 2px dashed #999; border-radius: 8px; background: #fff; }

/* iframe default is display:inline, which leaves a gap below it. Use block. */
iframe { display: block; }

button { padding: 8px 14px; margin-bottom: 8px; cursor: pointer; }
```

(Older trick: `padding-bottom: 56.25%` wrapper with absolutely positioned iframe. `aspect-ratio` is supported in all modern browsers since 2021.)

---

## 🟠 React/Next.js Connection

```jsx
// React: iframe is just JSX. Note camelCase props: allowFullScreen, referrerPolicy
export default function YouTubeEmbed({ id, title }) {
  return (
    <div className="aspect-video w-full">   {/* Tailwind: aspect-ratio 16/9 */}
      <iframe
        className="h-full w-full rounded-lg"
        src={`https://www.youtube.com/embed/${id}`}
        title={title}
        loading="lazy"
        allowFullScreen
      />
    </div>
  );
}

// Listening for postMessage inside a component (ALWAYS check origin + cleanup)
import { useEffect } from "react";
function PaymentFrame() {
  useEffect(() => {
    const onMsg = (e) => {
      if (e.origin !== "https://pay.example.com") return; // security check
      console.log("payment result", e.data);
    };
    window.addEventListener("message", onMsg);
    return () => window.removeEventListener("message", onMsg);
  }, []);
  return <iframe title="Pay" src="https://pay.example.com/checkout" />;
}
```
Next.js: if your own site must not be framed, set headers in `next.config.js` (`X-Frame-Options: DENY` or CSP `frame-ancestors 'none'`). `next/image` does not apply to iframes; use `loading="lazy"` yourself.

---

## ⚫ Interview Questions + Answers

Q1: What is an iframe and why use it?
A1: It embeds another HTML document in a nested browsing context with its own DOM, CSS and JS. Use it for third-party widgets (YouTube, Maps, payment, ads) when you want isolation from your page.

Q2: What is the `sandbox` attribute?
A2: It restricts an embedded page. Empty `sandbox` blocks scripts, forms, popups, and treats the page as a unique origin. You then re-enable features with tokens like `allow-scripts`, `allow-forms`. Warning: `allow-scripts` + `allow-same-origin` together on same-origin content lets the child remove its own sandbox.

Q3: What is clickjacking and how do you stop it?
A3: An attacker frames your site invisibly and tricks the user into clicking. Prevent it with `X-Frame-Options: DENY/SAMEORIGIN` or CSP `frame-ancestors`. That is also why some sites refuse to load in your iframe.

Q4: How do parent and iframe communicate across origins?
A4: Same-origin pages can access each other via `contentWindow` / `window.parent`. Cross-origin must use `window.postMessage(data, targetOrigin)`, and the receiver must verify `event.origin`.

Q5: What are the downsides of iframes?
A5: Extra network requests and memory, slower page load, poor SEO attribution (content belongs to the other URL), accessibility problems without `title`, awkward responsive sizing, and cookies/storage partitioning limits. Use `loading="lazy"` and only when isolation is really needed.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: Missing `title` attribute on iframe.
✅ Correct way: Always add a descriptive `title`; screen readers use it to announce the frame.

❌ Mistake 2: Embedding untrusted content without `sandbox`.
✅ Correct way: Use `sandbox` with only the minimal tokens needed.

❌ Mistake 3: `postMessage(data, '*')` and not checking `event.origin`.
✅ Correct way: Give the exact origin when sending and validate `event.origin` when receiving.

❌ Mistake 4: Fixed `width="800"` iframes that overflow on mobile.
✅ Correct way: `width: 100%` with `aspect-ratio` (or fixed height), and `display: block`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| iframe | Embedded nested page | Page के अंदर page |
| Browsing context | Window-like container with own document | अलग window/document |
| sandbox | Restricts iframe powers | iframe की powers सीमित करना |
| srcdoc | Inline HTML for iframe | URL की जगह सीधा HTML |
| postMessage | Safe cross-window messaging | Windows के बीच सुरक्षित message |
| X-Frame-Options | Header that blocks framing | Framing रोकने वाला header |
| Clickjacking | Tricking clicks via hidden frame | छुपे frame से click चुराना |
| Same-origin | Same protocol + host + port | एक ही origin |

---

## ⚡ 3-Line Summary
English: `<iframe>` embeds an isolated page inside yours, ideal for YouTube, Maps and payment widgets.
Always give it a `title`, use `loading="lazy"`, and lock it down with `sandbox`.
Use `postMessage` (with origin checks) to talk across origins; servers block framing with `X-Frame-Options` / CSP.

Hindi: `<iframe>` आपके page में एक अलग isolated page दिखाता है, YouTube, Maps, payment के लिए बढ़िया।
हमेशा `title` दें, `loading="lazy"` लगाएँ, और `sandbox` से उसकी powers सीमित करें।
Cross-origin बातचीत `postMessage` (origin check के साथ) से होती है; server `X-Frame-Options` / CSP से framing रोकता है।

---

## ➡️ Next Topic
**26. canvas Tag Basics** — iframe दूसरे pages embed करता है; अब देखेंगे कि JavaScript से सीधे pixels कैसे draw करें (charts, games, image editing)।

---
