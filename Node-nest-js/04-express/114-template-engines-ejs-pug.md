# 114. Template Engines (EJS, Pug)
# हिंदी में: Template Engines — Server-Side HTML Rendering

---

## 🔵 Simple Definition (English)
A **template engine** (EJS, Pug, Handlebars) lets you generate dynamic HTML on the server by embedding variables, loops, and conditionals inside template files, which Express compiles and renders into final HTML sent to the browser — used for traditional server-rendered web apps (not SPAs).

## 🔵 सरल परिभाषा (Hindi)
एक **template engine** (EJS, Pug, Handlebars) server पर dynamic HTML generate करने देता है, variables, loops, और conditionals को template files के अंदर embed करके, जिन्हें Express compile करके final HTML में render करता है और browser को भेजता है — traditional server-rendered web apps (SPAs नहीं) के लिए use होता है।

---

## 🔴 Problem it Solves
Building HTML strings manually via string concatenation (`'<h1>' + user.name + '</h1>'`) is error-prone, hard to read, vulnerable to XSS if not escaped properly, and doesn't scale to complex pages with loops/conditionals. Template engines provide a clean, HTML-like (or shorthand, in Pug's case) syntax for embedding dynamic data, automatic escaping to prevent XSS, template inheritance/partials (reusable headers/footers), and separation of view logic from route/business logic.

## 🔴 यह क्यों बना? (Hindi)
HTML strings को manually string concatenation से बनाना (`'<h1>' + user.name + '</h1>'`) error-prone है, पढ़ना मुश्किल है, properly escape न करने पर XSS vulnerable है, और loops/conditionals वाले complex pages के लिए scale नहीं करता। Template engines एक clean, HTML-जैसा (या Pug के case में shorthand) syntax देते हैं dynamic data embed करने के लिए, automatic escaping XSS रोकने के लिए, template inheritance/partials (reusable headers/footers), और view logic को route/business logic से separate करना।

---

## 🟢 How it Works — Step by Step

Step 1 → Set the view engine: `app.set('view engine', 'ejs')` and the views directory: `app.set('views', './views')`.
Step 2 → Create template files (`.ejs`, `.pug`) with placeholders for dynamic data, e.g., `<h1><%= user.name %></h1>` in EJS.
Step 3 → In a route handler, call `res.render('templateName', { data })`, passing the data object the template needs.
Step 4 → Express locates the template engine registered for the file extension, compiles the template string, injecting the passed data into placeholders.
Step 5 → The compiled, fully-formed HTML string is sent as the response body with `Content-Type: text/html` — the browser just renders plain HTML, with zero knowledge that a template engine was involved.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → View engine set करो: `app.set('view engine', 'ejs')` और views directory: `app.set('views', './views')`।
Step 2 → Template files (`.ejs`, `.pug`) बनाओ dynamic data के placeholders के साथ, जैसे EJS में `<h1><%= user.name %></h1>`।
Step 3 → Route handler में, `res.render('templateName', { data })` call करो, template को ज़रूरी data object pass करते हुए।
Step 4 → Express file extension के लिए registered template engine locate करता है, template string compile करता है, passed data को placeholders में inject करता है।
Step 5 → Compiled, fully-formed HTML string response body के रूप में `Content-Type: text/html` के साथ भेजा जाता है — browser सिर्फ plain HTML render करता है, उसे पता नहीं चलता कि template engine involved था।

---

## 🟡 Real World Example
**IRCTC booking confirmation page (server-rendered):** After a train ticket booking, IRCTC's server renders a confirmation page using a template engine, injecting dynamic data: `<%= booking.pnr %>`, `<%= booking.trainName %>`, a loop over `<% booking.passengers.forEach(p => { %> <tr><td><%= p.name %></td></tr> <% }) %>` to list all passengers. This is server-rendered (not a React SPA) partly for compatibility with low-end devices and slow networks across India, and partly because the page is mostly static/display-only after generation — no need for client-side JS framework overhead. The template also uses a shared `header.ejs`/`footer.ejs` partial included across all pages for consistent branding.

## 🟡 Real Example Hindi mein
**IRCTC booking confirmation page (server-rendered):** Train ticket booking के बाद, IRCTC का server template engine से confirmation page render करता है, dynamic data inject करते हुए: `<%= booking.pnr %>`, `<%= booking.trainName %>`, और सभी passengers list करने के लिए loop `<% booking.passengers.forEach(p => { %> <tr><td><%= p.name %></td></tr> <% }) %>`। ये server-rendered है (React SPA नहीं) partly compatibility के लिए low-end devices और slow networks (across India) के साथ, और partly क्योंकि page mostly static/display-only है generate होने के बाद — client-side JS framework overhead की ज़रूरत नहीं। Template एक shared `header.ejs`/`footer.ejs` partial भी use करता है सभी pages पर consistent branding के लिए।

---

## 💻 Code Example — Basic

```javascript
// template-basic.js
const express = require('express');
const path = require('path');

const app = express();

app.set('view engine', 'ejs'); // npm install ejs — tells Express to use EJS templates
app.set('views', path.join(__dirname, 'views')); // directory where .ejs files live

app.get('/greet/:name', (req, res) => {
  // res.render looks for views/greet.ejs and passes { name } into it
  res.render('greet', { name: req.params.name });
});

app.listen(3000, () => console.log('Server on port 3000 — visit /greet/Rahul'));

/*
views/greet.ejs content:
<!DOCTYPE html>
<html>
<head><title>Greeting</title></head>
<body>
  <h1>Hello, <%= name %>!</h1>
  <!-- <%= %> auto-escapes HTML to prevent XSS; <%- %> renders raw (unescaped) HTML -->
</body>
</html>
*/
```

## 💻 Code Example — Advanced

```javascript
// template-advanced.js — Partials, loops, conditionals, layout pattern
const express = require('express');
const path = require('path');

const app = express();
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Mock data representing a Zomato-style order history page
app.get('/orders/:userId', async (req, res, next) => {
  try {
    const orders = [
      { id: 1, restaurant: 'Punjabi Dhaba', total: 450, status: 'delivered' },
      { id: 2, restaurant: 'South Spice', total: 320, status: 'preparing' },
    ]; // normally fetched from DB

    res.render('orders', {
      userName: 'Rahul Sharma',
      orders,
      hasOrders: orders.length > 0,
    });
  } catch (err) {
    next(err);
  }
});

app.listen(3000, () => console.log('Server on port 3000 — visit /orders/123'));

/*
views/partials/header.ejs:
<header><h2>Zomato Order History</h2></header>

views/orders.ejs:
<!DOCTYPE html>
<html>
<head><title>Orders</title></head>
<body>
  <%- include('partials/header') %>  <!-- include a reusable partial -->

  <h3>Hi, <%= userName %></h3>

  <% if (hasOrders) { %>
    <table>
      <% orders.forEach(order => { %>
        <tr>
          <td><%= order.restaurant %></td>
          <td>₹<%= order.total %></td>
          <td class="status-<%= order.status %>"><%= order.status %></td>
        </tr>
      <% }) %>
    </table>
  <% } else { %>
    <p>No orders yet. Start exploring restaurants!</p>
  <% } %>
</body>
</html>
*/
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const path = require('path');
const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public'))); // CSS/JS assets alongside templates

// Rendering with error handling and locals shared across all templates
app.use((req, res, next) => {
  res.locals.currentYear = new Date().getFullYear(); // available in ALL templates automatically
  next();
});

app.get('/product/:id', async (req, res, next) => {
  try {
    const product = await Product.findById(req.params.id); // Mongoose query
    if (!product) {
      return res.status(404).render('404', { message: 'Product not found' });
    }
    res.render('product-detail', { product });
  } catch (err) {
    next(err);
  }
});

app.listen(4000, () => console.log('Server-rendered app running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using unescaped output (`<%- %>` in EJS) for user-supplied data
✅ Correct: Always use the auto-escaping output tag (`<%= %>`) for any data that originated from user input — unescaped output is an XSS vector if the data contains `<script>` tags.

```ejs
<!-- Wrong — renders raw HTML, if comment.text contains <script>, it executes! -->
<p><%- comment.text %></p>

<!-- Right — auto-escapes HTML entities, script tags become harmless text -->
<p><%= comment.text %></p>
```

❌ Mistake 2: Putting business logic (DB queries, calculations) inside the template file
✅ Correct: Templates should only handle presentation — fetch and process data in the route handler/controller, then pass the already-prepared data to `res.render()`.

```javascript
// Wrong — template does the data fetching (hard to test, mixes concerns)
// views/orders.ejs: <% const orders = await db.query(...) %>  ❌ doesn't even work with sync templates!

// Right — route handler prepares data, template just displays it
app.get('/orders', async (req, res) => {
  const orders = await Order.find({ userId: req.user.id });
  res.render('orders', { orders }); // template only loops and displays
});
```

---

## 🧠 Tricky Interview Question

```javascript
// views/test.ejs: <h1><%= name %></h1>
app.get('/test', (req, res) => {
  res.render('test', { name: '<script>alert("XSS")</script>' });
});
```
What actually gets sent to the browser — does the script execute?

Answer: The script does NOT execute. EJS's `<%= %>` tag automatically HTML-escapes the interpolated value, converting `<script>alert("XSS")</script>` into its escaped entity form: `&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;`. When the browser renders this, it displays the LITERAL TEXT `<script>alert("XSS")</script>` on the page (visible as text, not executed as a script) rather than executing it. This is EJS's built-in XSS protection via its default escaping output tag. If the developer had instead used `<%- name %>` (the unescaped/raw output tag), the script WOULD execute, since the raw HTML (including the `<script>` tag) would be injected directly into the page — this is exactly why `<%- %>` should only ever be used for trusted, pre-sanitized HTML (like a partial include), never raw user input.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between a template engine (EJS/Pug) and a frontend framework (React/Vue)?
A1: Template engines render HTML entirely on the SERVER — the browser receives complete, static HTML for that request; any further interaction requires a full page reload or separate client-side JS. Frontend frameworks like React render (and re-render) in the BROWSER using a virtual DOM, enabling rich client-side interactivity (SPA behavior) without full page reloads, typically fetching data via API calls rather than receiving pre-rendered HTML. Template engines suit simpler, content-heavy, SEO-friendly pages; SPA frameworks suit highly interactive apps.

Q2: Why does EJS have both `<%= %>` and `<%- %>` tags, and when would you use `<%- %>`?
A2: `<%= %>` escapes HTML special characters (`<`, `>`, `&`, `"`) in the output — safe default for any dynamic/user-controlled data, preventing XSS. `<%- %>` outputs raw, unescaped HTML — necessary when intentionally injecting trusted HTML content, most commonly for `include()`-ing partial templates (`<%- include('partials/header') %>`) where the "data" is actually pre-rendered trusted HTML from your own template files, not user input.

Q3: What are "partials" in template engines and why are they useful?
A3: Partials are reusable template fragments (e.g., `header.ejs`, `footer.ejs`, `navbar.ejs`) that can be included inside other templates via `include()`. They let you avoid duplicating common markup (navigation, footers, meta tags) across dozens of pages — update the partial once, and every page using it reflects the change, similar to a React component but for server-rendered templates.

Q4: Can you mix a template-engine-rendered frontend with a JSON REST API in the same Express app?
A4: Yes — it's common for the same Express app to serve `res.render()` HTML pages for traditional routes (`/dashboard`, `/profile`) while also exposing `res.json()` API endpoints (`/api/products`) consumed by a mobile app or AJAX calls from the same rendered pages. There's no conflict; `res.render` and `res.json` are just different response-sending methods on the same `res` object.

Q5: What's a key performance/architecture trade-off of server-side template rendering vs. client-side rendering?
A5: Server-side rendering (template engines) does the HTML-generation work on the SERVER for every request — this means server CPU scales with traffic, and the response includes fully-formed content (good for SEO, fast initial paint, works on low-end devices without heavy JS). Client-side rendering (SPA) shifts rendering work to the BROWSER after an initial JS bundle download — server load is lighter (mostly serving JSON via API), but initial load can be slower (JS parse/execute time) and SEO requires extra effort (SSR frameworks like Next.js bridge this gap).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building traditional server-rendered websites (content sites, admin dashboards, email templates, confirmation pages)
- SEO matters heavily and you want fully-formed HTML on first response without client-side JS execution
- Supporting low-end devices/slow networks where shipping a heavy JS bundle is undesirable

❌ Avoid when:
- Building a highly interactive SPA (dashboards with live updates, drag-and-drop, complex client state) — a frontend framework (React/Vue) is far better suited
- The app is purely a backend API consumed by a separate frontend/mobile app — no HTML rendering needed at all, template engines are irrelevant

---

## 📊 Visual Diagram
```
TEMPLATE ENGINE RENDERING FLOW:

  Browser ── GET /orders/123 ──▶ Express route handler
                                        │
                                  fetch data from DB
                                        │
                                        ▼
                          res.render('orders', { orders, userName })
                                        │
                                        ▼
                     Template Engine (EJS) compiles orders.ejs
                     injecting data into <%= %> / <% %> placeholders
                                        │
                                        ▼
                         Fully-formed HTML string generated
                                        │
                                        ▼
  Browser ◀── 200 OK, Content-Type: text/html ────────────
       (browser just renders plain HTML — no idea EJS was involved)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Template Engine | Tool for generating dynamic HTML server-side | Server-side dynamic HTML tool |
| EJS | Embedded JavaScript templating | Embedded JS templating engine |
| Pug | Indentation-based template engine | Indentation-based template engine |
| res.render() | Renders a view with data, sends HTML | View को data से render करना |
| Partial | Reusable template fragment | Reusable template fragment |
| Auto-escaping | Converts HTML entities to prevent XSS | XSS रोकने के लिए HTML entities convert करना |

---

## ⚡ 3-Line Summary
English:
1. Template engines (EJS, Pug) generate dynamic HTML on the server by injecting data into template files via `res.render()`.
2. Always use the auto-escaping output syntax (`<%= %>` in EJS) for user-controlled data to prevent XSS; use raw output only for trusted partials.
3. Suited for content-heavy, SEO-friendly, server-rendered pages; SPAs with heavy interactivity are better built with React/Vue.

Hindi:
1. Template engines (EJS, Pug) server पर dynamic HTML generate करते हैं, data को template files में `res.render()` से inject करके।
2. User-controlled data के लिए हमेशा auto-escaping output syntax (`<%= %>` EJS में) use करो XSS रोकने के लिए; raw output सिर्फ trusted partials के लिए।
3. Content-heavy, SEO-friendly, server-rendered pages के लिए सही; heavy interactivity वाले SPAs के लिए React/Vue बेहतर है।

---

## ➡️ Next Topic
**115. Express Error Handling — Best Practices** — Centralized error-handling middleware, async error catching, and operational vs programmer errors।
