# 138. DOM Manipulation (createElement, appendChild, innerHTML)
# हिंदी में: DOM Manipulation (createElement, appendChild, innerHTML)

---

## 🔵 Simple Definition (English)
DOM manipulation means creating, inserting, changing, and removing nodes in the page. The main tools are `createElement` (make a node), `appendChild` / `append` (insert it), `innerHTML` (set markup as a string), and `remove()` (delete it).

## 🔵 सरल परिभाषा (Hindi)
DOM manipulation का मतलब है page में nodes बनाना, जोड़ना, बदलना और हटाना। मुख्य tools हैं `createElement` (node बनाना), `appendChild` / `append` (जोड़ना), `innerHTML` (string में markup देना), और `remove()` (हटाना)।

---

## 🔴 Problem it Solves
A page is rarely fixed. A food app shows a new list of restaurants after every search, a chat app adds new messages, and a cart adds rows. Writing all of this as a new HTML page each time is impossible. DOM manipulation lets JavaScript build new UI pieces on the fly and place them exactly where needed, without reloading the page.

## 🔴 यह क्यों बना? (Hindi)
Page कभी fixed नहीं रहता। Food app हर search के बाद नए restaurants दिखाता है, chat app नए messages जोड़ता है, और cart में नई rows आती हैं। हर बार पूरा HTML नए सिरे से लिखना संभव नहीं है। DOM manipulation से JavaScript तुरंत नए UI हिस्से बनाकर सही जगह पर रख सकता है, बिना page reload किए।

---

## 🟢 How it Works — Step by Step

Step 1 → `document.createElement("li")` creates a new element node in memory. It is not visible yet.
Step 2 → Set its content with `textContent` (safe text) or child nodes.
Step 3 → Set attributes and classes with `className`, `setAttribute`, or `dataset`.
Step 4 → Insert it into the tree with `parent.appendChild(node)` (adds as last child) or `append()` (accepts many nodes and strings).
Step 5 → Use `DocumentFragment` to build many nodes off-screen, then insert them once. This causes only one reflow.
Step 6 → Remove with `node.remove()` or replace with `parent.replaceChild(new, old)`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `document.createElement("li")` memory में एक नया element node बनाता है। वह अभी दिखता नहीं।
Step 2 → `textContent` (safe text) या child nodes से content भरें।
Step 3 → `className`, `setAttribute` या `dataset` से attributes और classes दें।
Step 4 → `parent.appendChild(node)` (आखिरी child के रूप में जोड़ता है) या `append()` (कई nodes और strings ले सकता है) से tree में डालें।
Step 5 → कई nodes को off-screen बनाने के लिए `DocumentFragment` लें, फिर एक बार में डालें। इससे सिर्फ एक reflow होता है।
Step 6 → `node.remove()` से हटाएँ या `parent.replaceChild(new, old)` से बदलें।

---

## 🟡 Real World Example
On Swiggy's restaurant list, when a user scrolls to the bottom, the app fetches 20 more restaurants from the API. For each restaurant the frontend creates a card with `createElement`, fills it with name and rating, collects all cards in a `DocumentFragment`, and appends the fragment once to the list. Amazon's search results page and Flipkart's product grid use the same idea. Paytm's transaction history adds rows the same way.

## 🟡 Real Example Hindi mein
Swiggy की restaurant list में user जब नीचे scroll करता है, तो app API से 20 और restaurants लाता है। हर restaurant के लिए frontend `createElement` से एक card बनाता है, नाम और rating भरता है, सारे cards को एक `DocumentFragment` में रखता है, और फिर उस fragment को एक बार list में जोड़ता है। Amazon के search results और Flipkart के product grid में भी यही तरीका है। Paytm की transaction history में rows इसी तरह जुड़ती हैं।

---

## 💻 Code Example — Basic
Save as `manipulation-basic.html` and open it in a browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DOM Manipulation Basic</title>
</head>
<body>
  <ul id="menu">                              <!-- empty list we will fill with JavaScript -->
    <li>Existing item</li>                    <!-- one item already in the HTML -->
  </ul>
  <button id="add">Add dish</button>          <!-- button that adds a new dish -->

  <script>
    const menu = document.getElementById("menu");  // parent node that will hold new items
    const addBtn = document.getElementById("add"); // button node

    // Create a new <li> element (it exists only in memory until we insert it)
    const li = document.createElement("li");       // make the node
    li.textContent = "Pizza";                      // safe text content (no HTML parsing)
    menu.appendChild(li);                          // insert as the last child of menu

    // append() can take several nodes and plain strings in one call
    menu.append("Plain text item", document.createElement("li")); // add text + empty li

    // innerHTML replaces ALL children of an element with parsed markup
    const box = document.createElement("div");     // a container we are about to fill
    box.innerHTML = "<strong>Bold</strong> and <em>italic</em>"; // parse this HTML
    document.body.appendChild(box);                // show the container on the page

    // Remove a node from the tree
    const firstLi = menu.firstElementChild;        // the "Existing item" li
    firstLi.remove();                              // delete it from the page

    // Event listener that creates a new dish on each click
    addBtn.addEventListener("click", () => {       // run when the button is clicked
      const item = document.createElement("li");   // new li each time
      item.textContent = `Dish #${menu.children.length + 1}`; // numbered text
      menu.appendChild(item);                      // add to the list
    });

    console.log("Items now:", menu.children.length); // count current li elements
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `manipulation-advanced.html`. It renders a list of dishes safely with a DocumentFragment, `textContent`, and event delegation for the delete buttons.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DOM Manipulation Advanced</title>
</head>
<body>
  <ul id="dish-list"></ul>                   <!-- container where dishes will be rendered -->

  <script>
    // Data as it might come from an API (note the "<img>" text: it must NOT run as HTML)
    const dishes = [
      { id: 1, name: "Paneer <img src=x onerror=alert(1)>", price: 249 }, // malicious-looking text
      { id: 2, name: "Dal Makhani", price: 199 },                          // normal dish
      { id: 3, name: "Naan", price: 39 },                                 // normal dish
    ];

    const list = document.getElementById("dish-list"); // container node

    function renderDishes(items) {               // render an array of dishes into the list
      const fragment = document.createDocumentFragment(); // off-screen container, not in the page yet

      for (const dish of items) {                // one loop turn per dish
        const li = document.createElement("li"); // create the row
        li.dataset.id = dish.id;                 // store the id in data-id (accessible as dataset.id)

        const nameSpan = document.createElement("span"); // span for the name
        nameSpan.textContent = dish.name;        // textContent escapes HTML: the text is shown as-is

        const price = document.createElement("small"); // small element for price
        price.textContent = ` ₹${dish.price}`;   // price text with a leading space

        const del = document.createElement("button"); // delete button
        del.textContent = "Remove";              // button label
        del.className = "remove";                // class used by event delegation below

        li.append(nameSpan, price, del);         // add all three children in one call
        fragment.appendChild(li);                // collect the row in the fragment
      }

      list.replaceChildren(fragment);            // clear old rows and insert everything in ONE step
    }

    renderDishes(dishes);                        // first render

    // Event delegation: ONE listener on the list handles all delete buttons
    list.addEventListener("click", (event) => {  // listen for clicks inside the list
      const btn = event.target.closest(".remove"); // find the remove button, if any
      if (!btn) return;                          // ignore clicks on other parts
      const row = btn.closest("li");             // the row that contains this button
      const id = Number(row.dataset.id);         // read data-id and convert to number
      console.log("Removing dish id", id);       // log for debugging
      row.remove();                              // remove the row from the page
    });

    // Compare: innerHTML is convenient but dangerous with user data
    const note = document.createElement("p");    // create a paragraph
    note.textContent = "<b>Safe</b>";            // shown literally as text
    document.body.appendChild(note);            // add it to the page
  </script>
</body>
</html>
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Building HTML strings with user data and `innerHTML` (XSS risk)
✅ Correct: Create elements and set `textContent`, so user text is never parsed as HTML.

```javascript
const comment = "<img src=x onerror=alert('hacked')>";  // user-supplied input

// Wrong — the browser parses the tag and runs the onerror code
list.innerHTML += `<li>${comment}</li>`;

// Right — text is inserted as text
const li = document.createElement("li");   // safe new element
li.textContent = comment;                  // shown literally, nothing runs
list.appendChild(li);
```

❌ **Mistake 2:** Forgetting that `appendChild` moves an existing node
✅ Correct: A node can be in only one place. Appending it again moves it, it does not copy it.

```javascript
// Wrong — expects two items, but the same node moved, so only one li exists
const item = document.createElement("li");
list.appendChild(item);
list.appendChild(item);       // moves the same node to the end, count is still 1

// Right — clone to make a second copy
list.appendChild(item.cloneNode(true)); // true = copy children too
```

❌ **Mistake 3:** Appending in a loop directly to the live page
✅ Correct: Use a DocumentFragment (or build a string once) so the browser reflows only once.

```javascript
// Wrong — each appendChild can trigger layout work
for (const d of dishes) list.appendChild(makeRow(d));

// Right — one insertion into the page
const frag = document.createDocumentFragment();
for (const d of dishes) frag.appendChild(makeRow(d));
list.appendChild(frag);
```

---

## 🧠 Tricky Interview Question
Run this in the console on an empty page (`<ul id="list"></ul>`).

```javascript
const list = document.getElementById("list");     // empty ul

const li = document.createElement("li");          // create one li
li.textContent = "A";                             // give it text

list.appendChild(li);                             // insert it
list.appendChild(li);                             // insert the SAME node again
console.log(list.children.length);                // ?

const frag = document.createDocumentFragment();   // make a fragment
frag.append("X", "Y");                            // add two text nodes
list.appendChild(frag);                           // insert the fragment
console.log(list.textContent);                    // ?
console.log(frag.childNodes.length);              // ?
```

Answer: The first output is `1`, because `appendChild` moves a node that is already in the tree, so the second call does not add a second `li`. The second output is `AXY`, because `list` contains the `li` with text "A", then two text nodes "X" and "Y" from the fragment, and `textContent` joins them. The third output is `0`, because inserting a DocumentFragment moves its children into the target and leaves the fragment empty. Many developers expect the fragment to keep its children, but it does not.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `appendChild` and `append`?
A1: `appendChild` takes exactly one node and returns it. `append` takes several nodes or strings, and it returns nothing. Strings become text nodes automatically with `append`.

Q2: What is `innerHTML` and why is it risky?
A2: `innerHTML` sets or reads the markup inside an element. When you set it, the browser parses the string as HTML and can run scripts or event handler attributes. If the string contains untrusted user input, this causes XSS (cross-site scripting). Use `textContent` for text.

Q3: What is a DocumentFragment?
A3: A lightweight, off-screen container node. You add children to it, then insert it into the page once. Its children move into the target, and the fragment is left empty. It reduces repeated reflows.

Q4: What is the difference between `remove()` and `removeChild()`?
A4: `node.remove()` removes the node from its parent directly. `parent.removeChild(node)` needs the parent reference and is older. Both delete the node from the tree but keep the node object in memory if you still hold a reference.

Q5: What does `cloneNode(true)` do?
A5: It creates a copy of a node. With `true` it also copies all descendants and attributes. With `false` only the node itself is copied. The copy does not keep event listeners added with `addEventListener`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Adding small, dynamic UI pieces like toasts, badges, or list rows
- Building many elements at once (use DocumentFragment)
- Showing user-generated text (use `textContent`)

❌ Avoid when:
- Building large UI trees by hand; a framework like React handles this more safely and efficiently
- Inserting untrusted HTML with `innerHTML`; use `textContent` or a sanitizer like DOMPurify
- Doing the same work for every item when a single parent event listener is enough (use delegation)

---

## 📊 Visual Diagram
```
Step 1: create (memory only)       Step 2: append (now in page)

  li = createElement("li")          ul#list
  li.textContent = "Pizza"            ├── li "Existing"
                                      └── li "Pizza"   <── appendChild(li)

DocumentFragment (off-screen)
  frag ── li "Dal" ── li "Naan"  ──► list.appendChild(frag)  (one reflow)
                                    frag is now EMPTY
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| createElement | Makes a new element node in memory | Memory में नया element node बनाता है |
| appendChild | Adds a node as the last child | आखिरी child के रूप में जोड़ता है |
| append | Adds several nodes or strings | कई nodes या strings जोड़ता है |
| innerHTML | Gets or sets markup inside an element | Element के अंदर का markup पढ़ना या लिखना |
| textContent | Gets or sets plain text safely | Plain text सुरक्षित तरीके से पढ़ना/लिखना |
| DocumentFragment | Off-screen container for batch inserts | Batch insert के लिए off-screen container |
| remove() | Deletes a node from the tree | Node को tree से हटाना |
| XSS | Attack where injected HTML runs scripts | Injected HTML से script चलने का हमला |

---

## ⚡ 3-Line Summary
**English:**
1. Create nodes with `createElement`, fill them with `textContent`, and insert with `append` / `appendChild`.
2. Avoid `innerHTML` with user data, because it can run injected scripts (XSS).
3. Batch many inserts with a DocumentFragment, and remember that appending an existing node moves it.

**Hindi:**
1. `createElement` से nodes बनाएँ, `textContent` से भरें, और `append` / `appendChild` से डालें।
2. User data के साथ `innerHTML` से बचें, क्योंकि इससे injected script चल सकता है (XSS)।
3. कई inserts को DocumentFragment से batch करें, और याद रखें कि पहले से मौजूद node को append करने पर वह move होता है।

---

## ➡️ Next Topic
**139. innerHTML vs textContent vs innerText** — अब सीखेंगे कि text और markup को पढ़ने-लिखने वाले तीनों properties में क्या फर्क है।
