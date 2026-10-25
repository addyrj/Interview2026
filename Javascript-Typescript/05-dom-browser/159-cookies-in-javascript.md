# 159. Cookies in JavaScript
# हिंदी में: JavaScript में Cookies — Browser में छोटे Data का Session और Tracking

---

## 🔵 Simple Definition (English)
A cookie is a small piece of text (up to about 4 KB) that the server or the page stores in the browser as `name=value` with optional attributes like `expires`, `path`, `secure` and `SameSite`. The browser sends matching cookies back with every HTTP request to that site. In JavaScript you read and write them through `document.cookie`.

## 🔵 सरल परिभाषा (Hindi)
Cookie एक छोटा text (लगभग 4 KB तक) होता है, जिसे server या page browser में `name=value` के रूप में रखते हैं, साथ में `expires`, `path`, `secure` और `SameSite` जैसे attributes। Browser उस site के हर HTTP request के साथ matching cookies वापस भेजता है। JavaScript में इन्हें `document.cookie` से पढ़ते और लिखते हैं।

> **Browser vs Node note:** `document.cookie` exists only in the browser. Node.js has no `document`, so there is no direct equivalent. On the server, cookies are **set** with a `Set-Cookie` response header and **read** from the `Cookie` request header. Express wraps this as `res.cookie()` and `req.cookies`.

---

## 🔴 Problem it Solves
HTTP is stateless: every request looks like a new visitor. Websites need to remember who you are (login), what language you chose, and whether you accepted a cookie banner. Cookies were the first standard way to store that memory. Without them, Flipkart would ask you to log in on every click.

## 🔴 यह क्यों बना? (Hindi)
HTTP stateless है: हर request एक नए visitor जैसी लगती है। Websites को याद रखना होता है कि आप कौन हैं (login), आपने कौन सी language चुनी, और cookie banner मान लिया या नहीं। इस याद के लिए cookies पहला standard तरीका बने। इनके बिना Flipkart हर click पर login माँगता।

---

## 🟢 How it Works — Step by Step

Step 1 → Server sends `Set-Cookie: theme=dark; Max-Age=3600; Path=/; SameSite=Lax` in a response
Step 2 → Browser stores the cookie for that domain (and path)
Step 3 → On every later request to a matching URL, the browser adds `Cookie: theme=dark` automatically
Step 4 → In JavaScript, `document.cookie = "..."` writes one cookie; `document.cookie` (read) returns all readable cookies as one string
Step 5 → `HttpOnly` cookies are hidden from JavaScript (only sent to the server), which protects session tokens
Step 6 → To delete, set the same name with an expiry in the past (or `Max-Age=0`)

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Server response में `Set-Cookie: theme=dark; Max-Age=3600; Path=/; SameSite=Lax` भेजता है
Step 2 → Browser उस domain (और path) के लिए cookie store करता है
Step 3 → बाद में matching URL के हर request पर browser अपने आप `Cookie: theme=dark` जोड़ता है
Step 4 → JavaScript में `document.cookie = "..."` एक cookie लिखता है; `document.cookie` (read) सारी readable cookies को एक string में देता है
Step 5 → `HttpOnly` cookies JavaScript से छिपी रहती हैं (सिर्फ़ server तक जाती हैं), इससे session tokens सुरक्षित रहते हैं
Step 6 → हटाने के लिए उसी name को past की expiry के साथ set करें (या `Max-Age=0`)

---

## 🟡 Real World Example
Flipkart keeps your login session in an `HttpOnly`, `Secure` cookie, so the JavaScript on the page cannot read the session token and an XSS bug cannot steal it directly. A separate, non-sensitive cookie stores your preferred language, which the page can read with `document.cookie` to show the right text on load. Cookie consent banners in the EU also write a cookie so the banner is not shown again.

## 🟡 Real Example Hindi mein
Flipkart आपका login session एक `HttpOnly`, `Secure` cookie में रखता है, इसलिए page का JavaScript session token नहीं पढ़ सकता और XSS bug उसे सीधे चुरा नहीं सकता। एक अलग, गैर-संवेदनशील cookie आपकी पसंदीदा language रखती है, जिसे page `document.cookie` से पढ़कर load पर सही text दिखाता है। EU के cookie consent banner भी एक cookie लिखते हैं, ताकि banner दोबारा न दिखे।

---

## 💻 Code Example — Basic
> Browser-only (uses `document.cookie`). Cannot run with `node`. Runnable example is a self-contained HTML page.
> **How to run:** save as `cookie-basic.html`, serve with `python3 -m http.server 8000`, open `http://localhost:8000/cookie-basic.html`, click the buttons and refresh. Note: cookies set from `file://` pages are unreliable, so use the server.

```html
<!-- cookie-basic.html — full page, JS inside <script> -->
<!DOCTYPE html>
<!-- HTML5 doctype -->
<html lang="en">
<!-- Root element -->
<head>
  <!-- Head section -->
  <meta charset="UTF-8">
  <!-- UTF-8 for Hindi text -->
  <title>Cookie Basic</title>
  <!-- Tab title -->
</head>
<body>
  <!-- Visible content -->
  <h2>Language Preference (cookie)</h2>
  <!-- Heading -->
  <select id="lang">
    <!-- Dropdown to choose language -->
    <option value="en">English</option>
    <!-- English option -->
    <option value="hi">हिंदी</option>
    <!-- Hindi option -->
  </select>
  <button id="save">Save</button>
  <!-- Saves the chosen language in a cookie -->
  <button id="forget">Forget</button>
  <!-- Deletes the cookie -->
  <p id="out"></p>
  <!-- Output paragraph -->

  <script>
    // Read one cookie value by name from document.cookie
    function getCookie(name) {
      // Function takes the cookie name
      const pairs = document.cookie.split("; ");
      // document.cookie is "a=1; b=2" — split into an array of "a=1" strings
      for (const pair of pairs) {
        // Loop through each pair
        const [key, ...rest] = pair.split("=");
        // Split at the first "=" (value may contain "=")
        if (key === name) return decodeURIComponent(rest.join("="));
        // Found it: return the decoded value
      }
      return null;
      // Not found
    }

    // Write a cookie with a name, value and max age in seconds
    function setCookie(name, value, maxAgeSec) {
      // Function builds one Set-Cookie-like string
      document.cookie =
        `${name}=${encodeURIComponent(value)}; Max-Age=${maxAgeSec}; Path=/; SameSite=Lax`;
      // Path=/ makes it available on every page; SameSite=Lax limits cross-site sends
    }

    // Show the saved language on page load
    const saved = getCookie("lang");
    // Read the cookie value (null if missing)
    if (saved) document.getElementById("lang").value = saved;
    // Pre-select the saved language in the dropdown
    document.getElementById("out").textContent = "Saved language: " + (saved || "none");
    // Show what is stored right now

    document.getElementById("save").addEventListener("click", () => {
      // Handler for save button
      const lang = document.getElementById("lang").value;
      // Get the chosen language
      setCookie("lang", lang, 60 * 60 * 24 * 30);
      // Keep it for 30 days
      document.getElementById("out").textContent = "Saved language: " + lang;
      // Update the output text
    });

    document.getElementById("forget").addEventListener("click", () => {
      // Handler for forget button
      setCookie("lang", "", 0);
      // Max-Age=0 tells the browser to delete the cookie now
      document.getElementById("out").textContent = "Cookie deleted";
      // Confirm to the user
    });
  </script>
  <!-- End script -->
</body>
<!-- End body -->
</html>
<!-- End document -->
```

## 💻 Code Example — Advanced
> Cookie parsing and building are pure string logic, so this part **runs in Node.js** (`node cookie-advanced.js`). It mirrors what Express does internally: it builds a safe `Set-Cookie` header and parses an incoming `Cookie` header. It validates names, encodes values and rejects unsafe attributes.

```javascript
// cookie-advanced.js — build Set-Cookie and parse Cookie headers (pure JS, runs in Node)

// Characters allowed in a cookie name (RFC 6265 token rules, simplified)
const NAME_RE = /^[A-Za-z0-9!#$%&'*+\-.^_`|~]+$/;
// Regex that matches valid cookie name characters

// Build a Set-Cookie header string from a name, value and options
function serializeCookie(name, value, opts = {}) {
  // opts can include maxAge, path, httpOnly, secure, sameSite
  if (!NAME_RE.test(name)) {
    // Validate the name before using it
    throw new TypeError(`Invalid cookie name: ${name}`);
    // Stop early on invalid names
  }
  const parts = [`${name}=${encodeURIComponent(value)}`];
  // Start with the encoded name=value pair (encode to avoid ";" breaking the header)
  if (opts.maxAge !== undefined) parts.push(`Max-Age=${Math.floor(opts.maxAge)}`);
  // Max-Age in seconds (preferred over Expires)
  parts.push(`Path=${opts.path || "/"}`);
  // Path defaults to "/" so the cookie is sent everywhere on the site
  if (opts.httpOnly) parts.push("HttpOnly");
  // HttpOnly hides the cookie from document.cookie
  if (opts.secure) parts.push("Secure");
  // Secure: only send over HTTPS
  const sameSite = opts.sameSite || "Lax";
  // Default to Lax (matches modern browser behavior)
  if (!["Strict", "Lax", "None"].includes(sameSite)) {
    // Only three SameSite values exist
    throw new TypeError(`Invalid SameSite: ${sameSite}`);
    // Reject anything else
  }
  if (sameSite === "None" && !opts.secure) {
    // Browsers reject SameSite=None without Secure
    throw new TypeError("SameSite=None requires Secure");
    // Explain the rule
  }
  parts.push(`SameSite=${sameSite}`);
  // Add the SameSite attribute
  return parts.join("; ");
  // Join all parts with "; " as the header format requires
}

// Parse an incoming Cookie request header into a plain object
function parseCookieHeader(header = "") {
  // header looks like "a=1; b=hello%20world"
  const out = {};
  // Empty result object
  for (const part of header.split(";")) {
    // Split on ";" to get each pair
    const idx = part.indexOf("=");
    // Find the first "=" (value may contain "=")
    if (idx < 0) continue;
    // Skip malformed parts with no "="
    const name = part.slice(0, idx).trim();
    // Left side is the name
    const raw = part.slice(idx + 1).trim();
    // Right side is the value
    if (name && out[name] === undefined) {
      // Keep the first occurrence if a name repeats
      try {
        out[name] = decodeURIComponent(raw);
        // Decode %20 and similar sequences
      } catch {
        // Malformed percent-encoding: keep the raw text
        out[name] = raw;
      }
    }
  }
  return out;
  // Return the object of cookies
}

// ---- demo ----
console.log(serializeCookie("session", "abc123", { maxAge: 3600, httpOnly: true, secure: true, sameSite: "Strict" }));
// session=abc123; Max-Age=3600; Path=/; HttpOnly; Secure; SameSite=Strict

console.log(serializeCookie("lang", "hi IN", { maxAge: 2592000 }));
// lang=hi%20IN; Max-Age=2592000; Path=/; SameSite=Lax  (space encoded)

try {
  // Try an invalid combination to show the guard works
  serializeCookie("bad", "x", { sameSite: "None" });
  // SameSite=None without Secure must throw
} catch (err) {
  console.log("Error:", err.message);
  // Prints: Error: SameSite=None requires Secure
}

console.log(parseCookieHeader("theme=dark; lang=hi%20IN; empty=; bad"));
// { theme: 'dark', lang: 'hi IN', empty: '' }  ("bad" has no "=" so it is skipped)
```

---

## 🟠 Express.js Integration
Express uses `res.cookie()` to write a `Set-Cookie` header and `req.cookies` (from the `cookie-parser` middleware) to read the `Cookie` header. Sensitive session data goes in an `HttpOnly` cookie, while preferences can be readable by the page.

```javascript
// server.js — npm i express cookie-parser, then node server.js
const express = require("express");
// Import Express
const cookieParser = require("cookie-parser");
// Middleware that parses the Cookie header into req.cookies

const app = express();
// Create the app
app.use(cookieParser());
// Fill req.cookies on every request
app.use(express.json());
// Parse JSON bodies
app.use(express.static("public"));
// Serve cookie-basic.html

// Login: set a secure session cookie that JavaScript cannot read
app.post("/login", (req, res) => {
  // Route for login (credentials check omitted for brevity)
  res.cookie("session", "server-generated-token", {
    // Set the cookie named "session"
    httpOnly: true,
    // JS cannot read it, protects against XSS theft
    secure: true,
    // Send only over HTTPS (use false locally if not on https)
    sameSite: "strict",
    // Do not send on cross-site requests (CSRF defense)
    maxAge: 60 * 60 * 1000,
    // Expires in one hour (Express uses milliseconds here)
    path: "/",
    // Available on every route
  });
  res.json({ ok: true });
  // Tell the client login succeeded
});

// Protected route reads the cookie from the request
app.get("/api/me", (req, res) => {
  // Route needs the session cookie
  const session = req.cookies.session;
  // Read the cookie value sent by the browser
  if (!session) return res.status(401).json({ error: "Not logged in" });
  // No cookie means not logged in
  res.json({ loggedIn: true });
  // Cookie present: report logged in (verify the token in a real app)
});

// Logout: clear the cookie
app.post("/logout", (req, res) => {
  // Route for logout
  res.clearCookie("session", { path: "/" });
  // Tell the browser to delete the session cookie
  res.json({ ok: true });
  // Confirm logout
});

app.listen(3000, () => console.log("Server on http://localhost:3000"));
// Start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `document.cookie = "a=1"` replaces all cookies.
✅ Correct: Each assignment sets or updates **one** cookie. Other cookies stay.

```javascript
// Wrong — assuming this erases everything
document.cookie = "theme=dark";
document.cookie = "lang=hi";
// Developer thinks only "lang=hi" is left. Wrong.

// Right — read the full string to see all cookies
console.log(document.cookie); // "theme=dark; lang=hi"
```

❌ Mistake 2: Forgetting `Path` when deleting, so the cookie is not removed.
✅ Correct: A cookie is identified by name, domain and path. Delete it with the same `Path` (and `Domain`) it was set with.

```javascript
// Wrong — set with Path=/ (from any page), but the delete on /checkout/ has no Path
// so the browser uses the default path "/checkout", which does not match the cookie
document.cookie = "lang=hi; Path=/";
document.cookie = "lang=; Max-Age=0";      // on /checkout/ this does NOT delete the Path=/ cookie

// Right — match the original path
document.cookie = "lang=; Max-Age=0; Path=/";
```

❌ Mistake 3: Putting session tokens in a non-HttpOnly cookie, so any script can read them.
✅ Correct: Use `HttpOnly; Secure; SameSite` for session cookies, and keep non-sensitive preferences in readable cookies.

---

## 🧠 Tricky Interview Question
What is printed in the browser console? Assume the page starts with no cookies.

```javascript
// Tricky cookie code (run in a browser console on http://localhost)
document.cookie = "theme=dark; Path=/";
// First write: one cookie

document.cookie = "lang=hi; Path=/";
// Second write: another cookie

console.log(document.cookie);
// Print all readable cookies

document.cookie = "theme=; Max-Age=0; Path=/";
// Delete only the theme cookie

console.log(document.cookie);
// Print again
```

Answer: The first log prints `theme=dark; lang=hi`, because each assignment adds or updates one cookie and does not overwrite the whole jar. After the delete, the second log prints `lang=hi`, since only the `theme` cookie was expired. The delete works because it uses the same name and the same `Path=/`. If the page had set a `HttpOnly` cookie, neither log would show it, which is the protection that `HttpOnly` provides.

---

## ⚫ Interview Questions + Answers

Q1: What is the size limit of a cookie?
A1: Roughly 4 KB per cookie (name plus value plus attributes), and browsers limit the number of cookies per domain.

Q2: What does `HttpOnly` do?
A2: It hides the cookie from `document.cookie` and JavaScript. The browser still sends it with requests, which protects tokens against XSS theft.

Q3: What is the difference between `Max-Age` and `Expires`?
A3: `Max-Age` is a number of seconds from now and is preferred. `Expires` is an absolute date. If both are present, `Max-Age` wins.

Q4: What does `SameSite` protect against?
A4: It controls whether cookies are sent on cross-site requests. `Strict` and `Lax` reduce CSRF risk. `None` allows cross-site sending but requires `Secure`.

Q5: How is a cookie different from localStorage?
A5: Cookies are sent to the server on every matching request and have expiry and HttpOnly support. localStorage is never sent automatically and is not available to the server.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a session identifier that the server reads on each request
- You need server-side visibility into a preference (theme, language) at first render
- You need HttpOnly protection for sensitive values

❌ Avoid when:
- You store large data (the limit is about 4 KB and it is sent with every request)
- You store secrets in readable cookies (use HttpOnly or no cookie at all)
- You have a cross-site third-party setup without understanding SameSite and Secure

---

## 📊 Visual Diagram
```
Server                              Browser
  |  Set-Cookie: session=abc;        |
  |    HttpOnly; Secure; Max-Age=3600|
  |--------------------------------->|  stores cookie for example.com
  |                                  |
  |  GET /api/me                     |  automatically adds:
  |  Cookie: session=abc             |  Cookie: session=abc
  |<---------------------------------|
  |  200 OK { loggedIn: true }       |
  |--------------------------------->|

JavaScript on page:  document.cookie  -> does NOT show "session" (HttpOnly)
                                       -> shows "lang=hi" (not HttpOnly)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cookie | Small named value stored by browser | Browser में रखा गया छोटा named value |
| Set-Cookie | Response header that creates a cookie | Cookie बनाने वाला response header |
| Max-Age | Lifetime in seconds | सेकंड में cookie की उम्र |
| HttpOnly | Hides cookie from JavaScript | JavaScript से cookie छिपाता है |
| Secure | Send cookie only over HTTPS | सिर्फ़ HTTPS पर cookie भेजना |
| SameSite | Controls cross-site sending | Cross-site भेजने को नियंत्रित करना |
| document.cookie | JavaScript interface to cookies | Cookies तक JavaScript का रास्ता |

---

## ⚡ 3-Line Summary
English: Cookies are small named values that the browser stores and sends with every matching request.
English: `document.cookie` reads and writes them, but `HttpOnly` keeps session tokens away from JavaScript.
English: Use `Secure`, `SameSite` and matching `Path` on delete; Node/Express uses `res.cookie` and `req.cookies` instead of `document`.
Hindi: Cookies छोटे named values हैं जिन्हें browser रखता है और हर matching request के साथ भेजता है।
Hindi: `document.cookie` इन्हें पढ़ता और लिखता है, लेकिन `HttpOnly` session tokens को JavaScript से दूर रखता है।
Hindi: `Secure`, `SameSite` और delete के समय सही `Path` रखें; Node/Express में `document` की जगह `res.cookie` और `req.cookies` use होते हैं।

---

## ➡️ Next Topic
160. History API (pushState, replaceState): cookies and storage keep data, but the History API controls the URL and the Back button in single-page apps. It builds on this topic because the same site-level state is used to restore a page after navigation.
