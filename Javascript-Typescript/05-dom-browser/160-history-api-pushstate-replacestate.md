# 160. History API (pushState, replaceState)
# हिंदी में: History API — URL बदलना और Back Button को Control करना

---

## 🔵 Simple Definition (English)
The History API (`window.history`) lets JavaScript change the browser's URL and session history without reloading the page. `pushState` adds a new entry, `replaceState` changes the current entry, and the `popstate` event tells you when the user presses Back or Forward.

## 🔵 सरल परिभाषा (Hindi)
History API (`window.history`) JavaScript को page reload किए बिना browser का URL और session history बदलने देता है। `pushState` नई entry जोड़ता है, `replaceState` मौजूदा entry बदलता है, और `popstate` event बताता है कि user ने Back या Forward दबाया।

> **Browser-only note:** `window.history` and `location` exist only in the browser. Node.js has no URL bar or history. On the server side, the equivalent job is done by routing (Express `app.get("/path")`) which decides what to send for each URL.

---

## 🔴 Problem it Solves
Before this API, every navigation (even clicking a product on Amazon) meant a full page reload: white flash, lost scroll position, and re-downloaded HTML. Single-page apps (React, Angular, Vue) render views in JavaScript, but users still expect real URLs that can be shared, bookmarked, and used with the Back button. The History API bridges that gap.

## 🔴 यह क्यों बना? (Hindi)
इससे पहले हर navigation (Amazon पर product click करना भी) पूरे page reload का मतलब था: सफ़ेद flash, scroll position खो जाना, और HTML फिर से download होना। Single-page apps (React, Angular, Vue) views को JavaScript में render करते हैं, लेकिन users को अब भी असली URLs चाहिए जो share, bookmark और Back button के साथ काम करें। History API यही खाई भरता है।

---

## 🟢 How it Works — Step by Step

Step 1 → User clicks a link, and JavaScript calls `event.preventDefault()` so the browser does not reload
Step 2 → `history.pushState(stateObj, "", "/new-path")` changes the URL bar and adds a history entry
Step 3 → JavaScript renders the new view from the URL (for example, show the product page)
Step 4 → User presses Back, the browser fires `popstate` with the saved `state`, and JavaScript renders the previous view
Step 5 → `history.replaceState(...)` changes the current entry without adding a new one (good for filters)
Step 6 → Important: `pushState` does **not** fire `popstate`. Only Back, Forward and `history.go()` do

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → User link पर click करता है, और JavaScript `event.preventDefault()` call करता है ताकि browser reload न करे
Step 2 → `history.pushState(stateObj, "", "/new-path")` URL bar बदलता है और history entry जोड़ता है
Step 3 → JavaScript URL के हिसाब से नया view render करता है (जैसे product page दिखाना)
Step 4 → User Back दबाता है, browser saved `state` के साथ `popstate` fire करता है, और JavaScript पिछला view render करता है
Step 5 → `history.replaceState(...)` बिना नई entry जोड़े मौजूदा entry बदलता है (filters के लिए अच्छा)
Step 6 → ज़रूरी: `pushState` `popstate` **fire नहीं** करता। सिर्फ़ Back, Forward और `history.go()` करते हैं

---

## 🟡 Real World Example
Flipkart's product list: when you apply a filter like "Price: Low to High", the page calls `replaceState` to put `?sort=price-asc` in the URL, so refreshing keeps the filter. When you open a product, the app calls `pushState("/product/123")`, so Back returns to the list with the same filter and scroll. Zomato's restaurant page works the same way.

## 🟡 Real Example Hindi mein
Flipkart की product list: जब आप "Price: Low to High" filter लगाते हैं, तो page `replaceState` से URL में `?sort=price-asc` डालता है, ताकि refresh करने पर filter बना रहे। Product खोलने पर app `pushState("/product/123")` call करता है, इसलिए Back दबाने पर वही filter और scroll वाली list वापस आती है। Zomato का restaurant page भी इसी तरह काम करता है।

---

## 💻 Code Example — Basic
> Browser-only (uses `window.history` and `window.location`). Cannot run with `node`. Runnable example is a self-contained HTML page with a tiny router.
> **How to run:** save as `history-basic.html`, serve with `python3 -m http.server 8000`, open `http://localhost:8000/history-basic.html`, click the links, then use the browser Back and Forward buttons. Note: a plain static server returns 404 for `/about` on refresh; that is solved in the Express section.

```html
<!-- history-basic.html — full page, JS inside <script> -->
<!DOCTYPE html>
<!-- HTML5 doctype -->
<html lang="en">
<!-- Root element -->
<head>
  <!-- Head section -->
  <meta charset="UTF-8">
  <!-- UTF-8 for Hindi text -->
  <title>History Basic</title>
  <!-- Tab title -->
</head>
<body>
  <!-- Visible content -->
  <nav>
    <!-- Navigation bar -->
    <a href="/" data-link>Home</a> |
    <!-- data-link marks links handled by our router -->
    <a href="/menu" data-link>Menu</a> |
    <!-- Link to the menu view -->
    <a href="/cart" data-link>Cart</a>
    <!-- Link to the cart view -->
  </nav>
  <main id="view"></main>
  <!-- The area we replace on each navigation -->

  <script>
    // Map each path to the HTML that should be shown
    const routes = {
      // Object of route paths to content
      "/": "<h2>Welcome to Zomato-style home</h2>",
      // Home view
      "/menu": "<h2>Menu: Butter Chicken ₹320</h2>",
      // Menu view
      "/cart": "<h2>Your cart: 2 items</h2>",
      // Cart view
    };

    // Draw the view for the current URL path
    function render(path) {
      // Function that updates the main area
      document.getElementById("view").innerHTML =
        routes[path] || "<h2>404 — Page not found</h2>";
      // Use the matching view or a 404 message
    }

    // Move to a new path without reloading the page
    function navigate(path) {
      // Function used by link clicks
      history.pushState({ path }, "", path);
      // Add a new entry and change the URL bar (state is saved for popstate)
      render(path);
      // Draw the new view
    }

    // Intercept clicks on links that have data-link
    document.addEventListener("click", (event) => {
      // Listen for clicks anywhere on the page
      const link = event.target.closest("a[data-link]");
      // Find the nearest link marked for our router
      if (!link) return;
      // Ignore other clicks
      event.preventDefault();
      // Stop the browser from doing a full page load
      navigate(new URL(link.href).pathname);
      // Convert href to a path and navigate to it
    });

    // Runs when user presses Back or Forward
    window.addEventListener("popstate", (event) => {
      // popstate gives the saved state object (may be null)
      render(location.pathname);
      // Draw the view for the URL the browser now shows
    });

    render(location.pathname);
    // Draw the view for the URL the page was opened with
  </script>
  <!-- End script -->
</body>
<!-- End body -->
</html>
<!-- End document -->
```

## 💻 Code Example — Advanced
> The core logic is pure JavaScript, so the state-handling part **runs in Node.js** (`node history-advanced.js`). It simulates a browser `history` stack (push, replace, back, forward) with the same rules as the real API, which makes the behavior easy to test. In the browser you would use `window.history` directly.

```javascript
// history-advanced.js — simulated History stack with browser rules; run: node history-advanced.js

// Simulates window.history so the rules can be tested in Node
class HistoryStack {
  // Class that models the session history
  constructor(startPath = "/") {
    // Constructor takes the first URL path
    this.entries = [{ path: startPath, state: null }];
    // Array of history entries, each with a path and a state object
    this.index = 0;
    // Index of the current entry
    this.listeners = [];
    // Callbacks registered for popstate
  }
  get current() {
    // Getter returns the current entry
    return this.entries[this.index];
    // Entry at the current index
  }
  onPopState(fn) {
    // Register a popstate-like listener
    this.listeners.push(fn);
    // Store the callback
  }
  pushState(state, path) {
    // Like history.pushState: adds an entry, does NOT fire popstate
    this.entries = this.entries.slice(0, this.index + 1);
    // Drop any forward entries (same as real browsers)
    this.entries.push({ path, state });
    // Add the new entry at the end
    this.index += 1;
    // Move the pointer to the new entry
  }
  replaceState(state, path) {
    // Like history.replaceState: change current entry, no new entry
    this.entries[this.index] = { path, state };
    // Overwrite the current slot in place
  }
  go(delta) {
    // Like history.go(n): n can be negative (back) or positive (forward)
    const next = this.index + delta;
    // Target index
    if (next < 0 || next >= this.entries.length) return;
    // Ignore moves outside the stack, like the browser does
    this.index = next;
    // Move to the target entry
    for (const fn of this.listeners) fn({ state: this.current.state });
    // Fire popstate only for traversal (back, forward, go)
  }
  back() {
    // Shortcut for go(-1)
    this.go(-1);
  }
  forward() {
    // Shortcut for go(1)
    this.go(1);
  }
}

// ---- demo ----
const h = new HistoryStack("/");
// Start at home
h.onPopState((e) => console.log("popstate ->", h.current.path, e.state));
// Log each traversal event

h.pushState({ page: "menu" }, "/menu");
// Go to menu (no popstate here)
h.pushState({ page: "cart" }, "/cart");
// Go to cart (no popstate here)
console.log("after push:", h.current.path);
// Prints /cart

h.replaceState({ sort: "price" }, "/menu?sort=price");
// Change the current entry only (cart becomes a filtered menu)
console.log("after replace:", h.current.path, h.current.state);
// Prints the new path and state

h.back();
// Trigger popstate: prints the previous entry
h.back();
// Go back again to "/"
h.back();
// Already at start: nothing happens
console.log("final index:", h.index, "entries:", h.entries.length);
// Shows index 0 and 3 entries
```

---

## 🟠 Express.js Integration
Client-side routing only works if the server returns the same HTML page for every route. If a user refreshes `/menu`, the server must send `index.html` (the "history API fallback"), and let the browser-side router draw the view. API routes must come **before** the fallback.

```javascript
// server.js — npm i express, then node server.js
const express = require("express");
// Import Express
const path = require("path");
// Import path helper for safe file paths

const app = express();
// Create the app

app.use(express.static(path.join(__dirname, "public")));
// Serve real files (CSS, JS, images) from the public folder

app.get("/api/menu", (req, res) => {
  // API route — must be defined BEFORE the fallback
  res.json([{ name: "Butter Chicken", price: 320 }]);
  // Return sample menu data as JSON
});

// Fallback: any other GET returns the app shell so the client router can take over
app.get("*", (req, res) => {
  // "*" matches every path that no earlier route handled
  res.sendFile(path.join(__dirname, "public", "history-basic.html"));
  // Send the single HTML file; the browser router reads location.pathname
});

app.listen(3000, () => console.log("Open http://localhost:3000/menu"));
// Start the server; refreshing /menu now works
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `pushState` to fire `popstate`, so the view never updates.
✅ Correct: `pushState` does not fire `popstate`. Render the view yourself right after calling it.

```javascript
// Wrong — the view is never drawn
window.addEventListener("popstate", () => render(location.pathname));
history.pushState({}, "", "/menu"); // no popstate fires here

// Right — render after pushing, and use popstate for Back/Forward only
history.pushState({}, "", "/menu");
render("/menu");
```

❌ Mistake 2: Forgetting `preventDefault` on links, so every click causes a full page load.
✅ Correct: Call `event.preventDefault()` in the click handler before changing the URL.

```javascript
// Wrong — the browser reloads the page anyway
link.addEventListener("click", () => navigate("/menu"));

// Right — stop the default navigation first
link.addEventListener("click", (e) => {
  e.preventDefault();  // no reload
  navigate("/menu");   // handled by our router
});
```

❌ Mistake 3: Putting huge objects in `state`, which is stored by the browser.
✅ Correct: Keep `state` small (ids and flags). The browser limits its size, and it is lost on a hard reload in some cases.

---

## 🧠 Tricky Interview Question
What is printed? Assume the code runs in a browser on `http://localhost/` with a page that has no other scripts.

```javascript
// Tricky History code (browser console)
window.addEventListener("popstate", () => {
  console.log("popstate fired");
  // Runs only for Back, Forward or history.go
});

history.pushState({ step: 1 }, "", "/step1");
// Adds an entry, no popstate

console.log("path:", location.pathname);
// Prints the new path right away

history.back();
// Goes back to "/" and fires popstate
```

Answer: The output is `path: /step1` followed by `popstate fired`. The first line appears because `pushState` changes `location.pathname` synchronously, so the URL is updated right after the call. `pushState` itself does **not** fire `popstate`, so nothing prints during the push. The `popstate fired` line appears only when `history.back()` moves the user to the previous entry. The rule to remember: popstate is for traversal (Back, Forward, go), not for pushes.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `pushState` and `replaceState`?
A1: `pushState` adds a new history entry, so Back returns to the old URL. `replaceState` overwrites the current entry, so no extra Back step is created.

Q2: When does the `popstate` event fire?
A2: On Back, Forward, and `history.go()`. It does not fire for `pushState` or `replaceState`.

Q3: Why does refreshing a SPA route return 404 on a static server?
A3: The server has no file at `/menu`. The fix is a fallback that returns `index.html` for unknown paths (like `app.get("*")` in Express).

Q4: Can you store an object in history state?
A4: Yes, if it is serializable with the structured clone algorithm (plain objects, arrays, Dates, Maps). Functions and DOM nodes cannot be stored.

Q5: What is `history.scrollRestoration`?
A5: A property set to `"auto"` (default) or `"manual"`. Setting it to `"manual"` lets your SPA restore scroll position itself, which matters when content is rendered by JavaScript.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You build a single-page app and need real, shareable URLs
- You want filters or tabs reflected in the URL with `replaceState`
- You need the Back button to return to the same view state

❌ Avoid when:
- A simple multi-page site is enough (normal links are simpler and better for SEO)
- You need to change the URL without any state (use `replaceState` carefully, or a router library)
- You store secrets or large data in `state`

---

## 📊 Visual Diagram
```
Start:           pushState("/menu")        pushState("/cart")
[ "/" ]    --->    [ "/", "/menu" ]   --->   [ "/", "/menu", "/cart" ]   <- current = "/cart"

replaceState("/menu?sort=price") on "/cart":
[ "/", "/menu", "/menu?sort=price" ]        <- same length, current entry overwritten

User presses Back (popstate fires, render() draws the previous URL):
[ "/", "/menu", "/menu?sort=price" ]  index moves from 2 to 1  -> "/menu"

Server (Express): GET /menu -> app.get("*") -> index.html -> browser router draws /menu
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| history.pushState | Adds a new history entry and changes the URL | नई history entry जोड़ना और URL बदलना |
| history.replaceState | Changes the current entry without adding one | मौजूदा entry बदलना, नई न जोड़ना |
| popstate | Event fired on Back, Forward, go | Back/Forward पर आने वाला event |
| state | Small data saved with a history entry | History entry के साथ रखा छोटा data |
| SPA | Single-page app that renders views in JS | JS से views बनाने वाली single-page app |
| History fallback | Server sends index.html for unknown paths | अज्ञात paths पर index.html भेजना |
| scrollRestoration | Controls automatic scroll restore | Scroll position अपने आप वापस लाने की setting |

---

## ⚡ 3-Line Summary
English: The History API changes the URL and history without a page reload, using `pushState` and `replaceState`.
English: `popstate` fires only on Back, Forward or `go`, so render the view yourself after a push.
English: SPAs need an Express fallback that returns `index.html` for every route that is not an API.
Hindi: History API page reload के बिना URL और history बदलता है, `pushState` और `replaceState` से।
Hindi: `popstate` सिर्फ़ Back, Forward या `go` पर चलता है, इसलिए push के बाद view खुद render करें।
Hindi: SPA के लिए Express में fallback चाहिए जो API के अलावा हर route पर `index.html` भेजे।

---

## ➡️ Next Topic
161. URL + URLSearchParams: once you can change the URL, the next step is building and reading it safely. `URL` and `URLSearchParams` are the standard tools for query strings, and they are used together with `pushState` for filters.
