# 32. Cookies vs localStorage vs sessionStorage
# हिंदी में: Cookies बनाम localStorage बनाम sessionStorage

---

## 🔵 Simple Definition (English)
All three store data in the browser, but differ in **lifetime, size, and who can read them**. **Cookies** (~4 KB) are sent to the server on every request and can be `HttpOnly` (hidden from JS) - ideal for login sessions. **localStorage** (~5 MB) persists and is JS-only. **sessionStorage** (~5 MB) lives only for one tab.

## 🔵 सरल परिभाषा (Hindi)
तीनों browser में data रखते हैं, पर **lifetime, size और कौन पढ़ सकता है** में अलग हैं। **Cookies** (~4 KB) हर request के साथ server को जाती हैं और `HttpOnly` हो सकती हैं (JS से छुपी), login session के लिए सही। **localStorage** (~5 MB) स्थायी और सिर्फ JS के लिए है। **sessionStorage** (~5 MB) सिर्फ एक tab तक रहता है।

---

## 🔴 Problem it Solves
```
HTTP IS STATELESS: the server forgets you after every request.
  Request 1: "Login as Aditya"  -> OK
  Request 2: "Show my orders"   -> "Who are you?"

Different needs, different tools:
  - Server must recognise the user on every request     -> COOKIE (auto-sent)
  - UI only needs a theme/language, server doesn't care -> localStorage
  - Temporary form/wizard state for ONE tab             -> sessionStorage

Using the wrong one causes bugs (lost login, leaked tokens) or waste
(sending 5 KB of theme data to the server on every image request).
```

## 🔴 यह क्यों बना? (Hindi)
```
HTTP stateless है: हर request के बाद server भूल जाता है कि आप कौन हैं।
  Request 1: "Aditya login"  -> OK
  Request 2: "मेरे orders दिखाओ" -> "आप कौन?"

अलग ज़रूरतें, अलग tools:
  - हर request पर server को user पहचानना है  -> COOKIE (अपने-आप जाती है)
  - सिर्फ UI के लिए theme/language, server को नहीं चाहिए -> localStorage
  - सिर्फ एक tab का अस्थायी form/wizard data  -> sessionStorage

गलत चुनने पर bugs (login खोना, token leak) या बर्बादी
(हर image request के साथ theme data server को भेजना)।
```

---

## 🟢 How it Works — Step by Step

```
COMPARISON TABLE
─────────────────────────────────────────────────────────────────────────────
                 Cookie                 localStorage        sessionStorage
─────────────────────────────────────────────────────────────────────────────
Capacity         ~4 KB each             ~5 MB               ~5 MB
Lifetime         Session or Expires/    Until cleared       Until tab closes
                 Max-Age you set
Sent to server   YES, every request     NO                  NO
                 (to matching domain)
Readable by JS   Yes, unless HttpOnly   Yes                 Yes
Set by           Server (Set-Cookie)    JS only             JS only
                 OR JS
Scope            Domain + path          Origin              Origin + single tab
                 (subdomains possible)  (all tabs)
API              document.cookie        setItem/getItem     setItem/getItem
                 (string)               (sync)              (sync)
Works in SSR     YES (server reads it)  No                  No
Typical use      Auth session, CSRF,    Theme, language,    Wizard steps, one-tab
                 consent, tracking      cached UI state     temp data
─────────────────────────────────────────────────────────────────────────────

HOW A LOGIN COOKIE FLOWS:
  1. POST /login (email, password)
  2. Server replies:  Set-Cookie: sid=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800
  3. Browser stores it.
  4. EVERY later request to that site automatically includes:  Cookie: sid=abc123
  5. Server looks up session "abc123" -> knows the user.

COOKIE ATTRIBUTES (frequent interview topic):
  Expires / Max-Age  -> persistent cookie. Without it = SESSION cookie (cleared on browser close)
  Domain / Path      -> where it is sent
  Secure             -> only over HTTPS
  HttpOnly           -> JS cannot read it (protects against XSS theft)
  SameSite=Strict|Lax|None -> controls cross-site sending (protects against CSRF);
                              None requires Secure. Lax is the default in modern browsers.
  Partitioned (CHIPS) -> per-top-site third-party cookie jar (newer, not in every browser)

SECURITY SUMMARY:
  XSS can steal anything readable by JS (localStorage, non-HttpOnly cookies).
  CSRF can abuse cookies because they auto-send -> use SameSite + CSRF tokens.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Login cookie का flow:
  1. POST /login (email, password)
  2. Server जवाब में Set-Cookie: sid=abc123; HttpOnly; Secure; SameSite=Lax भेजता है।
  3. Browser इसे सहेज लेता है।
  4. उसके बाद उस site की हर request में Cookie: sid=abc123 अपने-आप जुड़ता है।
  5. Server session देखकर user पहचान लेता है।

मुख्य फर्क (ऊपर की table का सार):
  Cookie: ~4 KB, server को हर request पर जाती है, server भी set कर सकता है, SSR में पढ़ी जाती है।
  localStorage: ~5 MB, कभी server को नहीं जाता, सभी tabs में share, स्थायी।
  sessionStorage: ~5 MB, सिर्फ एक tab, tab बंद = खत्म।

Cookie attributes: Secure (सिर्फ HTTPS), HttpOnly (JS नहीं पढ़ सकता, XSS से बचाव),
SameSite (दूसरी site से भेजना नियंत्रित, CSRF से बचाव), Expires/Max-Age (कितने समय तक)।

Security: XSS उस हर चीज़ को चुरा सकता है जो JS पढ़ सकता है (localStorage, non-HttpOnly cookie)।
CSRF cookies का दुरुपयोग कर सकता है क्योंकि वो अपने-आप जाती हैं -> SameSite + CSRF token।
```

---

## 🟡 Real World Example
**Amazon:** login session = `HttpOnly Secure` cookie (server must know you on every page request, even for server-rendered pages). The "cookie consent" choice is also a cookie. **Swiggy:** selected city/theme/guest-cart = `localStorage`. **A bank-style multi-step KYC form** = `sessionStorage` so the draft vanishes when the tab closes (shared computer safety). **Instagram:** `sessionid` cookie for auth, `csrftoken` cookie for CSRF defence, and localStorage for UI preferences.

## 🟡 Real Example Hindi mein
**Amazon:** login session = `HttpOnly Secure` cookie (server को हर page request पर आपको पहचानना है, server-rendered pages में भी)। "Cookie consent" का choice भी एक cookie है। **Swiggy:** चुना हुआ city/theme/guest-cart = `localStorage`। **Bank जैसा multi-step KYC form** = `sessionStorage` ताकि tab बंद होते ही draft मिट जाए (shared computer की सुरक्षा)। **Instagram:** auth के लिए `sessionid` cookie, CSRF बचाव के लिए `csrftoken` cookie, और UI preferences के लिए localStorage।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cookies vs Storage</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="page">
    <h1>Cookie vs localStorage vs sessionStorage</h1>
    <p class="note">Note: cookies may not work when the file is opened as file:// in some browsers.
       Run with a local server, e.g. <code>npx serve</code> or <code>python3 -m http.server</code>.</p>

    <div class="row">
      <button id="save">Save "name=Aditya" in all three</button>
      <button id="show">Read all three</button>
      <button id="wipe">Delete all three</button>
    </div>

    <pre id="out">Click a button...</pre>
  </main>

  <script>
    // ---------- COOKIE HELPERS (document.cookie is one awkward string) ----------
    function setCookie(name, value, days) {
      const d = new Date();
      d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);       // expiry date
      // encodeURIComponent protects ; and = characters. SameSite=Lax is a safe default.
      // 'Secure' is added automatically on https pages. HttpOnly can NOT be set from JS.
      document.cookie = name + '=' + encodeURIComponent(value) +
        '; expires=' + d.toUTCString() + '; path=/; SameSite=Lax' +
        (location.protocol === 'https:' ? '; Secure' : '');
    }
    function getCookie(name) {
      // document.cookie looks like: "a=1; b=2; name=Aditya"
      const match = document.cookie.split('; ').find(row => row.startsWith(name + '='));
      return match ? decodeURIComponent(match.split('=')[1]) : null;
    }
    function deleteCookie(name) {
      // delete = set an expiry date in the past (path must match)
      document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    }

    const out = document.getElementById('out');

    document.getElementById('save').onclick = () => {
      setCookie('name', 'Aditya', 7);              // 7 days, sent to server on every request
      localStorage.setItem('name', 'Aditya');       // forever, JS only
      sessionStorage.setItem('name', 'Aditya');     // this tab only
      out.textContent = 'Saved in all three. Now refresh, then close the tab and reopen.';
    };

    document.getElementById('show').onclick = () => {
      out.textContent =
        'cookie         : ' + getCookie('name') + '\n' +
        'localStorage   : ' + localStorage.getItem('name') + '\n' +
        'sessionStorage : ' + sessionStorage.getItem('name') + '\n\n' +
        'raw document.cookie: "' + document.cookie + '"\n' +
        '(Open DevTools > Application > Cookies and Network > Headers to see the Cookie header.)';
    };

    document.getElementById('wipe').onclick = () => {
      deleteCookie('name');
      localStorage.removeItem('name');
      sessionStorage.removeItem('name');
      out.textContent = 'Deleted from all three.';
    };
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #222; }
.page { max-width: 640px; margin: 0 auto; padding: 24px 16px; }
.note { background: #fff8e1; padding: 10px 12px; border-radius: 8px; font-size: 14px; }

.row { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }   /* wraps on small screens */
button { padding: 8px 12px; border: 0; border-radius: 6px; background: #1e88e5; color: #fff; cursor: pointer; }

pre { background: #212121; color: #a5d6a7; padding: 16px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; }
code { background: #eee; padding: 1px 4px; border-radius: 4px; }
```

Server side (Node/Express) - the secure way to set an auth cookie:

```js
// JS cannot read or steal this cookie because of httpOnly
res.cookie("sid", sessionId, {
  httpOnly: true,       // hidden from document.cookie
  secure: true,         // HTTPS only
  sameSite: "lax",      // CSRF protection
  maxAge: 7 * 24 * 60 * 60 * 1000,
  path: "/",
});
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js App Router: cookies are readable on the SERVER, so no flash of wrong content
import { cookies } from "next/headers";

export default async function Page() {
  const cookieStore = await cookies();               // async in Next 15; sync in older versions
  const theme = cookieStore.get("theme")?.value ?? "light";
  return <main className={theme === "dark" ? "dark bg-black text-white" : "bg-white"}>...</main>;
}

// Server Action / Route Handler: set an HttpOnly auth cookie
"use server";
import { cookies } from "next/headers";
export async function login(formData) {
  // ...verify user...
  (await cookies()).set("sid", "token", { httpOnly: true, secure: true, sameSite: "lax", path: "/" });
}
```
- Since localStorage is invisible to the server, a theme stored there causes a **flash of wrong theme** on SSR. Store theme in a **cookie** to render correctly on the server (or use `next-themes` which injects a script).
- Auth libraries (NextAuth/Auth.js, Clerk) use HttpOnly cookies. Middleware in Next.js can read cookies to protect routes.
- Client libs: `js-cookie` (browser), `useLocalStorage` hook (see topic 31).

---

## ⚫ Interview Questions + Answers

Q1: Main differences between cookies, localStorage and sessionStorage?
A1: Cookies: ~4 KB, expire by date, sent with every HTTP request, can be HttpOnly, readable on server. localStorage: ~5 MB, never expires, client-only, shared across tabs. sessionStorage: ~5 MB, cleared when the tab closes, per-tab.

Q2: Where should you store an auth token?
A2: In an `HttpOnly; Secure; SameSite` cookie. JS (and XSS) cannot read it. localStorage tokens are stolen by any XSS. Cookie tradeoff: needs CSRF protection (SameSite, tokens).

Q3: What do `HttpOnly`, `Secure`, `SameSite` do?
A3: HttpOnly blocks JS access (XSS mitigation). Secure sends only on HTTPS. SameSite (Strict/Lax/None) restricts cross-site sending (CSRF mitigation); `None` needs `Secure`.

Q4: How do you delete a cookie?
A4: Set it again with the same name, domain and path but an expired date (or `Max-Age=0`). The server does this via `Set-Cookie`.

Q5: What are third-party cookies and why are they being phased out?
A5: Cookies set by a domain other than the one in the address bar (ads, trackers, embedded widgets). Browsers (Safari, Firefox) block them by default for privacy; Chrome has changed its plans several times, so check the current status. Alternatives: first-party cookies, Storage Access API, partitioned cookies (CHIPS).

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: Putting everything in cookies (they travel with every request, slowing it).
✅ Correct way: Cookies only for what the server needs; UI state in localStorage.

❌ Mistake 2: Keeping JWT/session ids in localStorage.
✅ Correct way: HttpOnly Secure SameSite cookie.

❌ Mistake 3: Cookie not deleting because `path`/`domain` differs from when it was set.
✅ Correct way: Delete with the identical path and domain.

❌ Mistake 4: Using `SameSite=None` without `Secure`, so the browser rejects it.
✅ Correct way: `SameSite=None; Secure`, only when cross-site is truly needed.

❌ Mistake 5: Assuming sessionStorage is shared across tabs.
✅ Correct way: It is per tab; use localStorage + `storage` event or BroadcastChannel to share.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cookie | Small data sent with each request | हर request के साथ जाने वाला छोटा data |
| Set-Cookie | Header to create a cookie | Cookie बनाने वाला header |
| HttpOnly | Hidden from JavaScript | JS से छुपा |
| Secure | HTTPS only | सिर्फ HTTPS |
| SameSite | Limits cross-site sending | दूसरी site से भेजना सीमित |
| Session cookie | Deleted when browser closes | Browser बंद होने पर खत्म |
| CSRF | Forged request using your cookie | आपकी cookie से नकली request |
| XSS | Injected script attack | Injected script हमला |

---

## ⚡ 3-Line Summary
English: Cookies talk to the server (small, auto-sent, can be HttpOnly), while localStorage and sessionStorage are client-only and bigger.
localStorage persists across tabs and restarts; sessionStorage dies with the tab.
Use HttpOnly cookies for auth, localStorage for preferences, sessionStorage for temporary per-tab state.

Hindi: Cookies server से बात करती हैं (छोटी, अपने-आप जाती हैं, HttpOnly हो सकती हैं), जबकि localStorage और sessionStorage सिर्फ client में और बड़े हैं।
localStorage tabs और restart के पार रहता है; sessionStorage tab के साथ खत्म।
Auth के लिए HttpOnly cookie, preferences के लिए localStorage, अस्थायी per-tab state के लिए sessionStorage।

---

## ➡️ Next Topic
**33. HTML Forms — Multipart + File Upload** — Browser से server तक data भेजने का अगला कदम: files (photo, PDF) upload कैसे होती हैं।

---
