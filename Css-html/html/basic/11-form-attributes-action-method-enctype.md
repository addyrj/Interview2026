# 11. Form Attributes (action, method, enctype)
# हिंदी में: Form Attributes — action, method, enctype

---

## 🔵 Simple Definition (English)
Three `<form>` attributes control submission: **`action`** = the URL that receives the data, **`method`** = HTTP verb (`get` puts data in the URL, `post` puts it in the request body), **`enctype`** = how the body is encoded (`application/x-www-form-urlencoded`, `multipart/form-data` for files, `text/plain`).

## 🔵 सरल परिभाषा (Hindi)
`<form>` के तीन attributes submission तय करते हैं: **`action`** = data जिस URL पर जाएगा, **`method`** = HTTP तरीका (`get` में data URL में, `post` में request body में), **`enctype`** = body का encoding (`application/x-www-form-urlencoded`, files के लिए `multipart/form-data`, `text/plain`)।

---

## 🔴 Problem it Solves
```
Different forms need different delivery rules:
  - Search box:  data should be IN THE URL so users can bookmark/share the results page
  - Login form:  password must NOT appear in the URL, browser history or logs
  - Upload form: binary file data cannot be written as name=value text

So the form needs knobs:
  action  -> WHERE to send
  method  -> HOW to send (URL vs body; safe vs changing data)
  enctype -> WHAT FORMAT the body uses
```

## 🔴 यह क्यों बना? (Hindi)
```
अलग forms को अलग delivery नियम चाहिए:
  - Search box: data URL में हो ताकि results page bookmark/share हो सके
  - Login form: password URL, history या logs में नहीं दिखना चाहिए
  - Upload form: binary file को name=value text में नहीं लिख सकते

इसलिए form में तीन settings हैं:
  action  -> कहाँ भेजना है
  method  -> कैसे भेजना है (URL में या body में)
  enctype -> body किस format में हो
```

---

## 🟢 How it Works — Step by Step

```
THE THREE ATTRIBUTES:
──────────────────────────────────────────────────────────
1) action="URL"
     Absolute or relative URL of the server endpoint.
     If omitted: submits to the current page URL.

2) method="get" (DEFAULT)   |   method="post"   |   method="dialog"
     GET   -> GET /search?q=pizza&city=delhi   (data appended to the URL as a query string)
              - visible, bookmarkable, cached, size-limited (~2000 chars)
              - for SAFE, READ-ONLY actions: search, filter, pagination
     POST  -> POST /login   body: email=a%40b.com&password=...
              - data in the body, not in URL/history, no practical size limit
              - for actions that CHANGE data: login, signup, payment, comment, upload
              - POST does NOT make it secure by itself: still need HTTPS!
     dialog-> closes a <dialog> element without sending

3) enctype (only matters for method="post")
     application/x-www-form-urlencoded  (DEFAULT)
         email=a%40b.com&name=Ravi+K      keys and values, URL-encoded
     multipart/form-data                  REQUIRED for <input type="file">
         body split into parts with boundary; each part has its own headers and raw bytes
     text/plain                           debugging only, not machine-reliable

   With GET the enctype is ignored.
   (Note: a plain `fetch` with a JSON body is a different path: Content-Type: application/json.)

PER-BUTTON OVERRIDES (on the submit button):
   formaction="/other"  formmethod="post"  formenctype="..."  formnovalidate  formtarget="_blank"

OTHER RELATED ATTRIBUTES ON <form>:
   target="_blank"   show the response in a new tab
   autocomplete      on | off
   novalidate        skip native validation
   accept-charset    encoding (default UTF-8)

THE REQUEST YOU WILL SEE IN DEVTOOLS (Network tab):
   GET  /search?q=pizza            -> "Query String Parameters"
   POST /login                     -> "Form Data" (urlencoded) or "Payload" (multipart boundary)
```

## 🟢 कैसे काम करता है? (Hindi)
```
1) action  = server का URL। न लिखो तो वही page।
2) method:
     GET  (default) -> data URL में: /search?q=pizza
          bookmark हो सकता है, सिर्फ पढ़ने वाले काम (search, filter) के लिए
     POST -> data body में, URL में नहीं
          login, signup, payment, upload जैसे बदलाव वाले काम के लिए
          (पर सुरक्षा के लिए HTTPS फिर भी ज़रूरी है)
3) enctype (सिर्फ POST में काम का):
     application/x-www-form-urlencoded -> default, name=value&name2=value2
     multipart/form-data               -> file upload के लिए ज़रूरी
     text/plain                        -> सिर्फ debugging

Submit button पर formaction, formmethod से form के settings override कर सकते हैं।
DevTools के Network tab में Query String या Form Data देखकर तुम इसे verify कर सकते हो।
```

---

## 🟡 Real World Example
**Amazon search vs Amazon login vs seller upload:** Typing "headphones" in Amazon's search bar sends a **GET** to `/s?k=headphones`: the URL is shareable and the Back button works. The sign-in page sends a **POST** so the password never shows in the address bar or history. When a seller uploads a product photo or a Flipkart user uploads a profile picture, the form uses **`enctype="multipart/form-data"`** because the file is binary.

## 🟡 Real Example Hindi mein
**Amazon search, login और seller upload:** Amazon के search bar में "headphones" लिखने पर `/s?k=headphones` पर **GET** जाता है: URL share हो सकता है और Back button काम करता है। Sign-in page **POST** भेजता है ताकि password address bar या history में न दिखे। जब seller product की photo upload करता है या कोई user profile picture लगाता है, तब form में **`enctype="multipart/form-data"`** होता है क्योंकि file binary होती है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Form Attributes: action, method, enctype</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f4f4f4; padding: 20px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); max-width: 960px; margin: 0 auto; }

    form { background: #fff; border-radius: 10px; padding: 16px; border: 2px solid #ddd; }
    form h2 { margin: 0 0 10px; font-size: 18px; }
    .get  { border-color: #1a73e8; }        /* blue = GET */
    .post { border-color: #e53935; }        /* red = POST */
    .file { border-color: #2e7d32; }        /* green = multipart */

    label { display: block; margin: 8px 0 4px; font-weight: 600; font-size: 14px; }
    input[type=text], input[type=password], input[type=file] { width: 100%; padding: 8px; border: 1px solid #bbb; border-radius: 6px; font: inherit; }
    button { margin-top: 12px; padding: 10px 14px; border: 0; border-radius: 6px; background: #232f3e; color: #fff; cursor: pointer; font: inherit; }
    code { background: #eee; padding: 1px 5px; border-radius: 4px; }

    #log { max-width: 960px; margin: 20px auto; background: #111; color: #9f9; padding: 14px; border-radius: 8px;
           font-family: monospace; font-size: 13px; white-space: pre-wrap; min-height: 90px; }
  </style>
</head>
<body>
  <h1>See what each attribute sends</h1>
  <p>Submit each form, then read the log at the bottom. (A JS handler prevents the real request so this file works offline; the log shows what the browser would send.)</p>

  <div class="grid">

    <!-- 1. GET: data appended to the URL -->
    <form class="get" action="/search" method="get" data-mode="get">
      <h2>1. Search (GET)</h2>
      <label for="q">Query</label>
      <input id="q" name="q" type="text" value="headphones">
      <label for="city">City</label>
      <input id="city" name="city" type="text" value="Delhi">
      <button type="submit">Search</button>
    </form>

    <!-- 2. POST + default enctype: data in the body -->
    <form class="post" action="/login" method="post" data-mode="post">
      <h2>2. Login (POST)</h2>
      <label for="u">Email</label>
      <input id="u" name="email" type="text" value="aditya@example.com">
      <label for="p">Password</label>
      <input id="p" name="password" type="password" value="secret123">
      <button type="submit">Sign in</button>
      <!-- formaction overrides the form's action for THIS button only -->
      <button type="submit" formaction="/forgot" formmethod="get" formnovalidate>Forgot password?</button>
    </form>

    <!-- 3. POST + multipart: required for files -->
    <form class="file" action="/upload" method="post" enctype="multipart/form-data" data-mode="multipart">
      <h2>3. Upload (multipart)</h2>
      <label for="t">Title</label>
      <input id="t" name="title" type="text" value="My photo">
      <label for="f">Photo</label>
      <input id="f" name="photo" type="file" accept="image/*">
      <button type="submit">Upload</button>
    </form>
  </div>

  <pre id="log">Submit a form to see the request...</pre>

  <script>
    // Intercept all three forms and print an approximation of the HTTP request
    document.querySelectorAll("form").forEach(form => {
      form.addEventListener("submit", e => {
        e.preventDefault();                                   // no real navigation (demo only)
        const submitter = e.submitter;                        // the button that was clicked
        const method = (submitter?.formMethod || form.method).toUpperCase();
        const action = submitter?.getAttribute("formaction") || form.getAttribute("action");
        const data = new FormData(form);                      // all named fields
        const log = document.getElementById("log");

        if (method === "GET") {
          // URLSearchParams builds the query string exactly like the browser does
          const qs = new URLSearchParams(data).toString();
          log.textContent = `GET ${action}?${qs}\n(No body. Data is visible in the URL.)`;
        } else if (form.enctype === "multipart/form-data") {
          const parts = [...data].map(([k, v]) =>
            `--boundary\nContent-Disposition: form-data; name="${k}"` +
            (v instanceof File ? `; filename="${v.name || ""}"\nContent-Type: ${v.type || "application/octet-stream"}` : "") +
            `\n\n${v instanceof File ? "<binary bytes>" : v}`).join("\n");
          log.textContent = `POST ${action}\nContent-Type: multipart/form-data; boundary=boundary\n\n${parts}\n--boundary--`;
        } else {
          log.textContent = `POST ${action}\nContent-Type: application/x-www-form-urlencoded\n\n${new URLSearchParams(data)}\n(Body, not in URL.)`;
        }
      });
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. In React SPAs you usually intercept submit and use fetch/axios. action/method are then
//    only a progressive-enhancement fallback.
async function onSubmit(e) {
  e.preventDefault();
  const fd = new FormData(e.currentTarget);

  // Files: send FormData directly; the browser sets multipart + boundary.
  //        DO NOT set Content-Type manually, or the boundary will be missing.
  await fetch("/api/upload", { method: "POST", body: fd });

  // JSON instead of form encoding:
  await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(Object.fromEntries(fd)),
  });
}

// 2. Next.js App Router Server Actions: `action` accepts a FUNCTION.
//    Next/React handle the POST and the encoding (multipart/form-data) for you.
export default function Page() {
  async function login(formData) {
    "use server";
    const email = formData.get("email");      // runs on the server
  }
  return (
    <form action={login}>
      <input name="email" type="email" />
      <button>Sign in</button>
    </form>
  );
}

// 3. Search form that updates the URL (GET behaviour) in Next.js:
//    <form action="/search"> <input name="q" /> </form>   -> /search?q=...
//    (Next.js <Form> from next/form prefetches and does client-side navigation.)

// 4. Next.js Route Handlers (app/api/upload/route.js): `const fd = await request.formData()`
```

---

## ⚫ Interview Questions + Answers

**Q1: Difference between GET and POST in forms?**
A1: **GET** appends data to the URL query string: visible, bookmarkable, cacheable, size-limited, should be **idempotent/read-only** (search, filters). **POST** sends data in the request body: not in URL/history, larger payloads, used to **create or change** data (login, payments, uploads). Neither is secure without HTTPS; POST just avoids exposing data in the URL.

**Q2: What does `action` do and what if I omit it?**
A2: `action` is the URL that handles the submission. If omitted, the form submits to the **current page URL** (the same document). In SPAs, you usually keep it empty/absent and handle `onSubmit` with JavaScript.

**Q3: When do you need `enctype="multipart/form-data"`?**
A3: Whenever the form has `<input type="file">` and uses POST. The default urlencoded format would send only the file *name*, not its contents. Multipart splits the body into parts with a boundary so binary data can be included. It is ignored for GET.

**Q4: What is the default `method` and default `enctype`?**
A4: Default method is **GET**; default enctype is **`application/x-www-form-urlencoded`**. So a form with neither attribute sends a GET to the current URL with a query string.

**Q5: How do you change the destination of a specific submit button, and how do you send JSON from a form?**
A5: Use `formaction`, `formmethod`, `formenctype` on that `<button>`/`<input type="submit">`. A native form cannot send JSON; instead intercept `submit`, build the object (`Object.fromEntries(new FormData(form))`) and `fetch` with `Content-Type: application/json`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Login form using GET (password in the URL)
```html
<!-- WRONG --> <form action="/login" method="get">
<!-- ✅ Correct way --> <form action="/login" method="post">
```

❌ **Mistake 2:** File input without multipart
```html
<!-- WRONG: server receives only the filename -->
<form method="post"><input type="file" name="photo"></form>
<!-- ✅ Correct way -->
<form method="post" enctype="multipart/form-data"><input type="file" name="photo"></form>
```

❌ **Mistake 3:** Setting `Content-Type: multipart/form-data` manually in `fetch`
```js
// WRONG: boundary missing, server cannot parse
fetch("/up", { method: "POST", headers: { "Content-Type": "multipart/form-data" }, body: fd });
// ✅ Correct way: let the browser set it
fetch("/up", { method: "POST", body: fd });
```

❌ **Mistake 4:** Using GET for actions that change data (deletes, payments), or assuming POST = secure
```html
<!-- ✅ Correct way: POST (or DELETE via fetch) for changes, plus HTTPS and CSRF protection -->
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| action | URL that receives the form | Data जिस URL पर जाए |
| method | HTTP verb: get/post | भेजने का तरीका |
| GET | Data in URL query string | Data URL में |
| POST | Data in request body | Data body में |
| enctype | Body encoding format | Body का encoding |
| urlencoded | Default `a=1&b=2` format | Default name=value format |
| multipart/form-data | Format for file uploads | File upload का format |
| Query string | `?q=pizza&city=delhi` part | URL का ?... हिस्सा |
| formaction | Per-button action override | Button-wise action |
| Idempotent | Same result if repeated | बार-बार करने पर वही नतीजा |

---

## ⚡ 3-Line Summary
**English:**
1. `action` = where to send; `method` = GET (data in URL, read-only use) or POST (data in body, changes data).
2. `enctype` = body format; default is urlencoded, files need `multipart/form-data`.
3. Never put passwords in GET, never set multipart Content-Type by hand in fetch; POST still needs HTTPS.

**Hindi:**
1. `action` = कहाँ भेजना; `method` = GET (data URL में, सिर्फ पढ़ने के लिए) या POST (data body में, बदलाव के लिए)।
2. `enctype` = body का format; default urlencoded है, files के लिए `multipart/form-data`।
3. Password कभी GET में नहीं; fetch में multipart Content-Type हाथ से मत लगाओ; POST के साथ भी HTTPS ज़रूरी।

---

## ➡️ Next Topic
**12. Input Types (text, email, password, checkbox, radio, file, date)** — `<input>` ke alag-alag types aur har type ka khaas behaviour।
