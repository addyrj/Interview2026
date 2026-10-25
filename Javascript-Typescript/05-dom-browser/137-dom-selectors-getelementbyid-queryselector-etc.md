# 137. DOM Selectors (getElementById, querySelector etc)
# हिंदी में: DOM Selectors (getElementById, querySelector आदि)

---

## 🔵 Simple Definition (English)
DOM selectors are methods on `document` (and on elements) that find nodes in the tree. Use `getElementById` for one id, `getElementsByClassName` / `getElementsByTagName` for live lists, and `querySelector` / `querySelectorAll` for any CSS selector.

## 🔵 सरल परिभाषा (Hindi)
DOM selectors वे methods हैं जो `document` (और elements) पर होते हैं और tree में nodes ढूँढते हैं। एक id के लिए `getElementById`, live lists के लिए `getElementsByClassName` / `getElementsByTagName`, और किसी भी CSS selector के लिए `querySelector` / `querySelectorAll` इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
To change a button or a price, JavaScript first has to find that exact node. Without good selectors you would walk the whole tree by hand. Old code used different methods for different needs, and it was easy to pick a slow or wrong one (for example a live list that changes while you loop). Modern selectors give one clear way to find nodes using the same syntax as CSS, so developers can search fast and read the code easily.

## 🔴 यह क्यों बना? (Hindi)
किसी button या price को बदलने के लिए JavaScript को पहले वही node ढूँढना होता है। अच्छे selectors के बिना हमें पूरे tree में हाथ से चलना पड़ता। पुराने code में अलग-अलग needs के लिए अलग methods थे, और गलत या धीमा method चुनना आसान था। Modern selectors CSS जैसे syntax से nodes ढूँढने का एक साफ तरीका देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Pick the method based on what you need: one id, a class list, or any CSS selector.
Step 2 → `getElementById` looks up the id index and returns one element or `null`.
Step 3 → `querySelector` runs the CSS selector and returns the first match or `null`.
Step 4 → `querySelectorAll` returns a **static** NodeList: a snapshot that does not change later.
Step 5 → `getElementsByClassName` and `getElementsByTagName` return a **live** HTMLCollection that updates when the DOM changes.
Step 6 → `element.closest(selector)` walks up the ancestors, and `element.matches(selector)` checks one element.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → ज़रूरत के हिसाब से method चुनें: एक id, class की list, या कोई भी CSS selector।
Step 2 → `getElementById` id के index से एक element या `null` देता है।
Step 3 → `querySelector` CSS selector चलाकर पहला match या `null` देता है।
Step 4 → `querySelectorAll` एक **static** NodeList देता है: एक snapshot जो बाद में नहीं बदलता।
Step 5 → `getElementsByClassName` और `getElementsByTagName` एक **live** HTMLCollection देते हैं जो DOM बदलने पर अपने-आप update होता है।
Step 6 → `element.closest(selector)` ancestors में ऊपर जाकर खोजता है, और `element.matches(selector)` एक element को check करता है।

---

## 🟡 Real World Example
On a Flipkart product page, the "Add to Cart" button has `id="add-to-cart"` for a single action, so `getElementById` is the fastest choice. The product card list uses `querySelectorAll(".product-card")` to attach the same wish-list handler to all cards. When you click the heart on a card, `event.target.closest(".product-card")` finds the card that contains the heart icon. Razorpay's checkout form uses `querySelector('input[name="amount"]')` to read a value by attribute.

## 🟡 Real Example Hindi mein
Flipkart के product page पर "Add to Cart" button का `id="add-to-cart"` है, इसलिए एक action के लिए `getElementById` सबसे तेज़ है। Product cards की list में `querySelectorAll(".product-card")` से सभी cards पर wish-list handler लगाया जाता है। Heart icon पर click होने पर `event.target.closest(".product-card")` उस card को ढूँढता है जिसमें वह heart है। Razorpay के checkout form में `querySelector('input[name="amount"]')` से attribute के आधार पर value पढ़ी जाती है।

---

## 💻 Code Example — Basic
Save as `selectors-basic.html` and open it in a browser. Check the results in the DevTools Console.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                 <!-- so Hindi text displays correctly -->
  <title>DOM Selectors Basic</title>
</head>
<body>
  <h1 id="page-title">Zomato Restaurants</h1>   <!-- unique id -->
  <div class="card">Dominos</div>               <!-- first card with class "card" -->
  <div class="card">Pizza Hut</div>             <!-- second card -->
  <div class="card special">Barbeque Nation</div> <!-- third card has two classes -->
  <p data-city="Mumbai">Open now</p>            <!-- custom data attribute -->

  <script>
    // getElementById: fastest way to get ONE element by its unique id
    const title = document.getElementById("page-title");
    console.log(title.textContent);            // "Zomato Restaurants"

    // querySelector: first element that matches ANY CSS selector
    const firstCard = document.querySelector(".card");  // first element with class "card"
    console.log(firstCard.textContent);        // "Dominos"

    // querySelectorAll: ALL matches, returned as a static NodeList
    const cards = document.querySelectorAll(".card");   // NodeList with 3 items
    console.log(cards.length);                 // 3
    cards.forEach((card) => {                  // NodeList supports forEach directly
      console.log("Card:", card.textContent);  // print each card's text
    });

    // getElementsByClassName: returns a LIVE HTMLCollection
    const liveCards = document.getElementsByClassName("card"); // live list
    console.log(liveCards.length);             // 3 right now

    // Attribute selector and combined selector
    const cityText = document.querySelector('p[data-city="Mumbai"]'); // CSS attribute selector
    console.log(cityText.textContent);         // "Open now"

    // querySelector returns null when nothing matches (check before using!)
    const missing = document.querySelector("#does-not-exist");  // no such id
    console.log(missing);                      // null — no error is thrown
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `selectors-advanced.html`. It uses scoped queries, `closest`, `matches`, and an event delegation pattern.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DOM Selectors Advanced</title>
</head>
<body>
  <section id="menu">                          <!-- container we will search inside -->
    <div class="dish" data-price="299">Pizza <button class="buy">Buy</button></div>
    <div class="dish" data-price="149">Burger <button class="buy">Buy</button></div>
  </section>
  <p id="status">No dish selected</p>          <!-- text we will update -->

  <script>
    const menu = document.getElementById("menu");   // container node

    // Scoped query: search only INSIDE the menu, not the whole document
    const firstBuy = menu.querySelector(".buy");     // first buy button inside menu
    console.log("First buy button text:", firstBuy.textContent); // "Buy"

    // Get all dish prices as numbers using dataset (data-price becomes dataset.price)
    const prices = [...menu.querySelectorAll(".dish")]  // spread NodeList into a real array
      .map((dish) => Number(dish.dataset.price));       // convert string to number
    console.log("Prices:", prices);                     // [299, 149]

    // Event delegation: one listener on the parent handles all buttons
    menu.addEventListener("click", (event) => {
      // closest() walks UP from the clicked node to find the matching ancestor
      const dish = event.target.closest(".dish");       // the dish that was clicked
      if (!dish) return;                                // click was outside any dish

      // matches() checks whether a node fits a selector (true / false)
      if (event.target.matches(".buy")) {               // did we click a buy button?
        const name = dish.firstChild.textContent.trim(); // first text node is the dish name
        document.getElementById("status").textContent =  // update the status text
          `Added ${name} (₹${dish.dataset.price})`;     // show name and price
      }
    });

    // Using a static NodeList vs a live HTMLCollection
    const staticList = menu.querySelectorAll(".dish"); // snapshot: does not change
    const liveList = menu.getElementsByClassName("dish"); // live: updates on DOM change
    const newDish = document.createElement("div");       // create a new node
    newDish.className = "dish";                          // give it the class "dish"
    menu.appendChild(newDish);                           // add it to the menu
    console.log("Static:", staticList.length, "Live:", liveList.length); // 2 and 3
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Selectors run in the browser, not on the server. In Express, the server's job is to return the HTML that contains the element ids and classes your selectors rely on. Keep those ids stable, because the frontend code depends on them.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");          // import Express
const app = express();                       // create the app

// Route that returns a page with stable ids and classes for selectors to use
app.get("/restaurants", (req, res) => {      // handle GET /restaurants
  const names = ["Dominos", "Pizza Hut"];    // data from a database in real life
  const cards = names                        // build HTML from the data
    .map((n) => `<div class="card" data-name="${n}">${n}</div>`) // one card per name
    .join("");                               // join all cards into one string
  res.send(`                                 
    <!DOCTYPE html>
    <html>
      <body>
        <h1 id="page-title">Restaurants</h1> <!-- id used by getElementById on the client -->
        <div id="list">${cards}</div>        <!-- container for querySelectorAll(".card") -->
        <script src="/app.js"></script>      <!-- client script that uses the selectors -->
      </body>
    </html>
  `);
});

// Serve the client script that uses document.querySelectorAll(".card")
app.get("/app.js", (req, res) => {           // handle GET /app.js
  res.type("application/javascript");        // tell the browser it is JavaScript
  res.send(`document.querySelectorAll(".card").forEach(c => console.log(c.dataset.name));`);
});

app.listen(3000, () => console.log("http://localhost:3000/restaurants")); // start server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `querySelectorAll` to return an array
✅ Correct: It returns a NodeList. It has `forEach` but not `map` or `filter`. Convert with spread or `Array.from`.

```javascript
// Wrong — NodeList has no map method, this throws TypeError
const names = document.querySelectorAll(".card").map((c) => c.textContent);

// Right — convert to an array first
const names2 = [...document.querySelectorAll(".card")].map((c) => c.textContent);
```

❌ **Mistake 2:** Using `getElementById` with a `#` prefix
✅ Correct: `getElementById` takes the bare id. The `#` is only for CSS selectors.

```javascript
// Wrong — looks for an id literally named "#page-title", returns null
const t1 = document.getElementById("#page-title");

// Right — bare id
const t2 = document.getElementById("page-title");
```

❌ **Mistake 3:** Removing items from a live HTMLCollection while looping forward
✅ Correct: Loop backward, or convert to a static array first.

```javascript
// Wrong — the live list shrinks as you remove, so items are skipped
const items = document.getElementsByClassName("item");
for (let i = 0; i < items.length; i++) items[i].remove(); // skips every other item

// Right — static snapshot, nothing shifts
[...document.querySelectorAll(".item")].forEach((el) => el.remove());
```

---

## 🧠 Tricky Interview Question
The page has three elements `<div class="item">` in a row. Run this in the console.

```javascript
const items = document.getElementsByClassName("item"); // live HTMLCollection, length 3

for (let i = 0; i < items.length; i++) {  // i increases, length keeps changing
  items[i].remove();                      // remove the element at index i
}

console.log(items.length);                // ?
console.log(document.querySelectorAll(".item").length); // ?
```

Answer: The output is `1` and then `1`. Here is why. At `i = 0`, the first item is removed, so the live list now has 2 items and the old second item moves to index 0. At `i = 1`, the code removes the old third item (which is now at index 1), so the list has 1 item left. At `i = 2`, the condition `2 < 1` is false and the loop stops. One item remains, which is the old second item. A live HTMLCollection is re-evaluated on each access, so the loop index and the list length get out of sync. A static NodeList from `querySelectorAll` would have removed all three.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `querySelector` and `querySelectorAll`?
A1: `querySelector` returns the first matching element or `null`. `querySelectorAll` returns a static NodeList of all matches, or an empty NodeList if none match. Both accept any CSS selector.

Q2: What is the difference between a live HTMLCollection and a static NodeList?
A2: A live collection (from `getElementsByClassName`, `getElementsByTagName`, `children`) updates automatically when the DOM changes. A static NodeList (from `querySelectorAll`) is a fixed snapshot taken at the moment of the call.

Q3: Which selector is the fastest?
A3: `getElementById` is usually the fastest because the browser keeps an index of ids. Class and tag lookups are also quick. Complex CSS selectors take more time, but the difference is small for normal pages. Choose clarity first, and use `getElementById` when you need one known id.

Q4: What does `closest()` do?
A4: `element.closest(selector)` starts at the element itself and walks up through its ancestors, returning the first one that matches the selector, or `null`. It is the standard way to find the card or row that contains a clicked button.

Q5: Can you scope a query to part of the page?
A5: Yes. Call `querySelector` or `querySelectorAll` on an element instead of `document`. For example, `menu.querySelector(".buy")` searches only inside `menu`, which is faster and avoids matching elements elsewhere on the page.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need one element by a known id: use `getElementById`
- You need any complex match (attribute, nested, pseudo-class): use `querySelector` / `querySelectorAll`
- You need to find the ancestor of a clicked node: use `closest()`

❌ Avoid when:
- You are repeatedly querying the same node inside a loop; cache it in a variable first
- You search the whole document when a scoped query on a container is enough
- A framework (React refs, Vue template refs) gives you a better way to reference elements

---

## 📊 Visual Diagram
```
document
 └── body
      ├── h1#page-title             <── getElementById("page-title")
      ├── div.card  "Dominos"       <── querySelector(".card")  (first match only)
      ├── div.card  "Pizza Hut"     <─┐
      └── div.card.special          <─┴── querySelectorAll(".card")  → static NodeList [3]
                                    <── getElementsByClassName("card") → LIVE list [3]

element.closest(".card")  ── walks UP ──►  div.card (or null)
element.matches(".card")  ── checks SELF ──►  true / false
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| getElementById | Finds one element by unique id | Unique id से एक element |
| querySelector | First element matching a CSS selector | CSS selector से पहला match |
| querySelectorAll | Static NodeList of all matches | सभी matches की static NodeList |
| HTMLCollection | Live list that updates with DOM | DOM के साथ बदलने वाली live list |
| NodeList | List of nodes (static for querySelectorAll) | Nodes की list |
| closest() | Walks up to nearest matching ancestor | सबसे पास वाला matching ancestor |
| matches() | Checks if an element fits a selector | Element selector से मेल खाता है या नहीं |
| Scoped query | Searching inside a specific container | किसी container के अंदर खोजना |

---

## ⚡ 3-Line Summary
**English:**
1. Use `getElementById` for one id, and `querySelector` / `querySelectorAll` for any CSS selector.
2. `querySelectorAll` gives a static NodeList; `getElementsByClassName` gives a live HTMLCollection that can shift under your loop.
3. Scope queries to a container and use `closest()` to find the parent card of a clicked element.

**Hindi:**
1. एक id के लिए `getElementById`, और किसी भी CSS selector के लिए `querySelector` / `querySelectorAll` इस्तेमाल करें।
2. `querySelectorAll` static NodeList देता है; `getElementsByClassName` live HTMLCollection देता है जो loop के बीच बदल सकता है।
3. Query को container तक सीमित रखें, और clicked element का parent card ढूँढने के लिए `closest()` इस्तेमाल करें।

---

## ➡️ Next Topic
**138. DOM Manipulation (createElement, appendChild, innerHTML)** — अब सीखेंगे कि मिले हुए nodes को कैसे बनाएँ, जोड़ें और बदलें।
