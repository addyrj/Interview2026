# 146. Event Delegation
# हिंदी में: Event Delegation — एक Listener से कई Elements संभालना

---

## 🔵 Simple Definition (English)
Event delegation means attaching ONE event listener to a parent element and letting the event bubble up from its children. The parent then checks `event.target` to know which child was clicked. Most UI events bubble, so this works well.

## 🔵 सरल परिभाषा (Hindi)
Event delegation का मतलब है parent element पर सिर्फ़ ONE event listener लगाना। Child में होने वाला event bubble होकर parent तक आता है, और parent `event.target` देखकर पता करता है कि किस child पर click हुआ। ज़्यादातर UI events bubble करते हैं, इसलिए यह तरीका काम करता है।

---

## 🔴 Problem it Solves
Imagine Swiggy shows 500 restaurants, each with an "Add" button. If you attach a listener to every button:
- 500 listeners बनते हैं, जो memory और setup time दोनों बढ़ाते हैं।
- नए items (जैसे search results या infinite scroll से आए restaurants) को listener अपने-आप नहीं मिलता, हर नए element पर फिर से लगाना पड़ता है।
- Element हटाने पर listener की cleanup भी अलग से करनी पड़ती है, वरना memory leak हो सकता है।

Delegation इन तीनों समस्याओं को एक parent listener से हल करता है।

## 🔴 यह क्यों बना? (Hindi)
जब पेज पर सैकड़ों या हज़ारों items होते हैं, और items बार-बार बदलते या जुड़ते हैं, तो हर item पर listener लगाना महँगा और जटिल हो जाता है। Event bubbling पहले से browser में मौजूद था, तो उसी का फ़ायदा उठाकर delegation बनाया गया। इससे code छोटा रहता है और dynamic UI आसानी से चलता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Parent element (जैसे `<ul>` या `<div id="app">`) पर एक `click` listener लगाओ।
Step 2 → User किसी child के अंदर का button (या उसका text/icon) click करता है।
Step 3 → Event browser में capture phase से target तक जाता है, फिर bubble होकर ऊपर parent तक आता है।
Step 4 → Parent का handler `event.target` पढ़ता है और `closest()` से सही action वाला element ढूँढता है।
Step 5 → अगर सही element मिला तो action चलाओ; नहीं मिला तो `return` कर दो।

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Parent element पर एक `click` listener लगाओ।
Step 2 → User किसी child के अंदर का button click करता है।
Step 3 → Event target तक जाता है, फिर bubble होकर parent तक लौटता है।
Step 4 → Handler `event.target` देखता है और `closest()` से सही element निकालता है।
Step 5 → सही element मिला तो action करो, वरना कुछ मत करो।

---

## 🟡 Real World Example
Zomato या Swiggy के restaurant list में हर card पर "Add to cart" button होता है। Cart में हर item के लिए "remove" button होता है। Razorpay के checkout में saved cards की list पर "Delete" button होता है। Paytm की transaction list में हर row पर "View receipt" होता है। इन सभी जगह एक parent पर एक listener काफ़ी है, क्योंकि rows बदलती रहती हैं और पेज पर कितने भी rows आ सकते हैं।

## 🟡 Real Example Hindi mein
Zomato या Swiggy की restaurant list में हर card पर "Add" button होता है। Cart में हर item पर "remove" button होता है। Razorpay के saved cards की list में हर card पर "Delete" button होता है। Paytm की transaction list में हर row पर "View receipt" होता है। इन सब जगह एक parent पर एक listener काफ़ी है, क्योंकि rows लगातार बदलती रहती हैं।

---

## 💻 Code Example — Basic
Browser-only topic है, इसलिए `node file.js` से नहीं चलेगा। नीचे पूरा HTML page है। इसे सेव करो, जैसे `delegation-basic.html`, फिर किसी browser में double-click करके खोलो (या Chrome/Edge/Firefox में drag-and-drop करो) और button दबाओ।

```html
<!DOCTYPE html>
<!-- HTML5 document ka declaration -->
<html lang="en">
<head>
  <meta charset="UTF-8" />                                                  <!-- Hindi/Unicode text ke liye encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1" />  <!-- mobile par sahi width -->
  <title>Event Delegation Basic</title>                                    <!-- browser tab ka title -->
</head>
<body>
  <!-- Parent list: delegation ka root, yahan ek hi listener lagega -->
  <ul id="restaurants">
    <!-- Har li mein ek button hai; data-id se restaurant pehchana jayega -->
    <li data-id="r1">Biryani House <button data-action="order">Order</button></li>
    <li data-id="r2">Dosa Corner <button data-action="order">Order</button></li>
    <li data-id="r3">Pizza Point <button data-action="order">Order</button></li>
  </ul>
  <pre id="log"></pre>  <!-- output yahan dikhega -->

  <script>
    // Ek hi listener parent (ul) par lagaya gaya hai, children par nahin
    const list = document.getElementById('restaurants'); // ul element lo
    const log = document.getElementById('log');          // log box lo

    list.addEventListener('click', (event) => {          // click bubble hokar ul tak aayega
      // event.target wo element hai jis par asli click hua (button, ya li ka text)
      const button = event.target.closest('button[data-action="order"]'); // sirf order button chahiye
      if (!button) return;                               // koi aur jagah click hua to ignore karo

      const item = button.closest('li');                 // button ka parent li dhundo
      const id = item.dataset.id;                        // data-id="r1" ko "r1" mein badlo
      log.textContent += `Order placed for ${id}\n`;     // log mein ek line jodo
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Yeh Zomato-style cart hai. Ek hi delegation root (`#app`) poore app ko handle karta hai: menu ke "+" buttons, cart ke "-" buttons, aur teardown. Dispatch table se action decide hota hai, errors catch hote hain, aur `AbortController` se listener ko cleanly hataya ja sakta hai. HTML page ko browser mein kholo.

```html
<!DOCTYPE html>
<!-- Advanced delegation: menu + cart ek hi root se -->
<html lang="en">
<head>
  <meta charset="UTF-8" />                                                 <!-- encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1" /> <!-- responsive width -->
  <title>Event Delegation Advanced</title>                                 <!-- tab title -->
</head>
<body>
  <!-- Ek hi root: is ke andar ke sab buttons delegation se handle honge -->
  <main id="app">
    <h3>Menu</h3>
    <section id="menu"></section>            <!-- menu yahan JS se render hoga -->
    <h3>Cart</h3>
    <ul id="cart"></ul>                      <!-- cart items yahan render honge -->
    <p>Total: ₹<span id="total">0</span></p> <!-- total amount -->
  </main>
  <button id="teardown">Stop listening</button> <!-- click karne par delegation band hoga -->

  <script>
    'use strict';                                               // strict mode: galat assignments par error
    const app = document.getElementById('app');                 // delegation root
    const menuEl = document.getElementById('menu');             // menu container
    const cartEl = document.getElementById('cart');             // cart list
    const totalEl = document.getElementById('total');           // total dikhane wala span
    const teardownBtn = document.getElementById('teardown');    // band karne wala button

    const items = [                                             // menu data (asli app mein API se aata)
      { id: 'p1', name: 'Paneer Tikka', price: 220 },
      { id: 'p2', name: 'Garlic Naan', price: 45 },
      { id: 'p3', name: 'Lassi', price: 80 },
    ];
    const cart = new Map();                                     // id -> quantity; Map ka use kiya

    // Menu render: har dish ke liye "+" button, lekin koi listener nahin lagaya
    menuEl.innerHTML = items
      .map((i) => `<div data-id="${i.id}">${i.name} ₹${i.price} <button data-action="add">+</button></div>`)
      .join('');                                                // array ko ek string bana diya

    // Dispatch table: data-action ki value ke hisaab se function chune
    const actions = {
      add: (id) => cart.set(id, (cart.get(id) ?? 0) + 1),       // quantity badhao (nahin thi to 0 se shuru)
      remove: (id) => {                                         // quantity ghatao
        const qty = cart.get(id) ?? 0;                          // current quantity
        if (qty <= 1) cart.delete(id);                          // 1 ya usse kam hai to entry hata do
        else cart.set(id, qty - 1);                             // warna ek kam karo
      },
    };

    // Cart ko DOM mein dobara banata hai (state -> UI)
    function render() {
      cartEl.innerHTML = '';                                    // purani list saaf karo
      let total = 0;                                            // total shuru se
      for (const [id, qty] of cart) {                           // Map ke har [id, qty] pair par
        const item = items.find((i) => i.id === id);            // menu se item ka data lo
        total += item.price * qty;                              // total mein jodo
        const li = document.createElement('li');                // naya li element
        li.dataset.id = id;                                     // row ki id store karo
        li.textContent = `${item.name} x${qty} `;               // text safe tarike se daalo
        li.insertAdjacentHTML('beforeend', '<button data-action="remove">-</button>'); // remove button
        cartEl.appendChild(li);                                 // cart mein jodo
      }
      totalEl.textContent = String(total);                      // total number ko string mein dikhao
    }

    // Ek hi listener poore app par. Naye elements apne-aap handle ho jaate hain
    const controller = new AbortController();                   // listener hatane ka handle
    app.addEventListener('click', (event) => {                  // click bubble hokar app tak aayega
      try {
        const btn = event.target.closest('button[data-action]'); // action wala button
        if (!btn || !app.contains(btn)) return;                 // bahar ka click ya button nahin: ignore
        const row = btn.closest('[data-id]');                   // button ka row (dish ya cart item)
        if (!row) throw new Error('row not found');             // safety check: row nahin mili to error
        const handler = actions[btn.dataset.action];            // dispatch table se function lo
        if (!handler) throw new Error(`unknown action: ${btn.dataset.action}`); // unknown action
        handler(row.dataset.id);                                // sahi action chalao
        render();                                               // UI ko nayi state se update karo
      } catch (err) {
        console.error('Click handling failed:', err.message);   // error ko console mein dikhao
      }
    }, { signal: controller.signal });                          // signal se listener baad mein hataya ja sakta hai

    teardownBtn.addEventListener('click', () => {               // teardown button par
      controller.abort();                                       // delegation listener hata do
      console.log('Delegation listener removed');               // confirm karne ke liye log
    });

    render();                                                   // pehli baar cart render (khali)
  </script>
</body>
</html>
```

---

## 🧠 Express.js Integration
Event delegation browser ka concept hai, Express server par nahin chalta. Express ka role yahan do cheezein karna hai: (1) page ko `public/` folder se serve karna, aur (2) delegated click handler jo `fetch()` call karta hai, us API endpoint ko handle karna. Neeche server code hai, aur client ka delegated handler comment mein dikhaya gaya hai.

```javascript
// server.js: Express server jo page serve karta hai aur cart API deta hai
const express = require('express');                    // Express framework load karo
const path = require('path');                          // file path banane ke liye built-in module

const app = express();                                 // Express app instance
const PORT = process.env.PORT || 3000;                 // port env se, warna 3000

app.use(express.json());                               // JSON request body parse karo (req.body)
app.use(express.static(path.join(__dirname, 'public'))); // public/index.html ko serve karo

const cart = new Map();                                // demo ke liye in-memory cart (production mein DB)

// Browser ka delegated handler is route par fetch() karega
app.post('/api/cart/:itemId', (req, res) => {          // dynamic :itemId parameter
  const { itemId } = req.params;                       // URL se item id nikalo
  const { action } = req.body;                         // body se action ('add' ya 'remove')
  if (!['add', 'remove'].includes(action)) {           // validation: sirf allowed actions
    return res.status(400).json({ error: 'invalid action' }); // 400 Bad Request
  }
  const qty = cart.get(itemId) ?? 0;                   // current quantity, nahin mili to 0
  const next = action === 'add' ? qty + 1 : Math.max(0, qty - 1); // naya quantity
  if (next === 0) cart.delete(itemId);                 // 0 ho gaya to entry hata do
  else cart.set(itemId, next);                         // warna update karo
  res.json({ itemId, quantity: next });                // JSON response
});

app.listen(PORT, () => {                               // server start
  console.log(`Server running at http://localhost:${PORT}`); // start hone ka message
});

// Client side (public/index.html ke script mein), delegated handler ka hissa:
// app.addEventListener('click', async (e) => {
//   const btn = e.target.closest('button[data-action]');             // action button
//   const row = btn?.closest('[data-id]');                           // item ki row
//   if (!btn || !row) return;                                        // galat click ignore
//   await fetch(`/api/cart/${row.dataset.id}`, {                     // server ko call
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },               // JSON bhej rahe hain
//     body: JSON.stringify({ action: btn.dataset.action }),          // action bhejo
//   });
// });
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Har child par alag listener lagana, jab parent kaafi ho.
✅ Correct: Parent par ek hi listener lagao aur `event.target` se child pehchano.

```javascript
// Wrong: har item par listener, naye items ko listener nahin milega
document.querySelectorAll('#menu button').forEach((btn) => {
  btn.addEventListener('click', handleAdd);       // 500 buttons = 500 listeners
});

// Right: ek hi listener parent par, naye buttons apne-aap cover honge
document.getElementById('menu').addEventListener('click', (e) => {
  const btn = e.target.closest('button');         // button dhoondo, chahe jo bhi ho
  if (btn) handleAdd(btn);                        // sirf button ke liye action
});
```

❌ Mistake 2: `event.target` ko hamesha seedha button samajhna.
✅ Correct: `closest()` se button dhoondo, kyunki click `<span>` ya icon par bhi ho sakta hai.

```javascript
// Wrong: agar button ke andar <span> hai to click target SPAN hoga, BUTTON nahin
menu.addEventListener('click', (e) => {
  if (e.target.tagName === 'BUTTON') add(e.target); // span click par yeh kuch nahin karega
});

// Right: closest() button ko dhoondhta hai, chahe target koi bhi andar ka element ho
menu.addEventListener('click', (e) => {
  const btn = e.target.closest('button');          // parent chain mein button dhoondo
  if (btn) add(btn);                               // mil gaya to action chalao
});
```

❌ Mistake 3: `focus`, `blur`, `mouseenter` जैसे events पर delegation लगाना।
✅ Correct: ये events bubble नहीं करते। इनके bubbling वाले versions `focusin`, `focusout` इस्तेमाल करो।

```javascript
// Wrong: focus bubble nahin karta, parent par kuch nahin pakdega
form.addEventListener('focus', (e) => highlight(e.target)); // kaam nahin karega

// Right: focusin bubble karta hai, delegation chalega
form.addEventListener('focusin', (e) => highlight(e.target)); // sahi
```

---

## 🧠 Tricky Interview Question
Neeche HTML page hai. Click programmatically karke `span` par trigger kiya gaya hai. Output kya hoga?

```html
<ul id="list">
  <li data-id="7"><span>Pizza</span></li>   <!-- span ke andar text -->
</ul>
<script>
  const list = document.getElementById('list');        // parent ul
  list.addEventListener('click', (e) => {              // ek listener ul par
    console.log(
      e.target.tagName,                                // asli click kis element par hua
      e.currentTarget.tagName,                         // listener kis element par laga
      e.target.closest('li').dataset.id                // row ki id
    );
  });
  list.querySelector('span').click();                  // span par programmatic click
</script>
```

Answer: Output hoga `SPAN UL 7`.
- `e.target` वही element है जिस पर click dispatch हुआ, यानी `SPAN`।
- `e.currentTarget` वह element है जिस पर listener लगा है, यानी `UL`। बहुत लोग यहाँ `SPAN` सोचते हैं, जो गलत है।
- `click()` एक bubbling event बनाता है, इसलिए वह `span` से ऊपर `ul` तक पहुँचता है और वहाँ listener चलता है।
- `closest('li')` parent chain में `li` ढूँढता है और `data-id` "7" देता है।
(इसे jsdom में चलाकर verify किया गया है।)

---

## ⚫ Interview Questions + Answers

Q1: Event delegation क्या है और इसका फ़ायदा क्या है?
A1: Parent पर एक listener लगाकर children के events को bubbling से handle करना। फ़ायदा: कम listeners, memory बचती है, और dynamically जुड़े नए elements अपने-आप cover हो जाते हैं।

Q2: `event.target` और `event.currentTarget` में क्या फ़र्क है?
A2: `event.target` वह element है जहाँ event शुरू हुआ (असली click), जबकि `event.currentTarget` वह element है जिस पर listener लगा है। Delegation में दोनों अक्सर अलग होते हैं।

Q3: `closest()` का use delegation में क्यों होता है?
A3: `closest(selector)` खुद से शुरू करके ऊपर की parent chain में matching element ढूँढता है। इससे button के अंदर के icon या text पर click होने पर भी सही button मिलता है।

Q4: कौन-से events bubble नहीं करते?
A4: `focus`, `blur`, `load` (images/scripts पर), `mouseenter`, `mouseleave`, `scroll` (element पर)। इनके लिए `focusin`/`focusout` या `mouseover`/`mouseout` जैसे bubbling versions इस्तेमाल होते हैं।

Q5: Delegation का listener कैसे हटाया जाए?
A5: `addEventListener` के options में `{ signal }` पास करो और बाद में `controller.abort()` call करो। यह सबसे साफ़ तरीका है। `removeEventListener` के लिए वही function reference चाहिए।

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- बहुत सारे similar children हैं (lists, tables, grids, menus)
- Children dynamically add या remove होते हैं
- एक ही तरह का action कई items पर लागू होता है
- Memory और setup time कम करना है

❌ Avoid when:
- Event bubble नहीं करता (focus, blur, load, mouseenter)
- सिर्फ़ एक-दो elements पर listener है, वहाँ delegation का फ़ायदा नहीं
- Root बहुत ऊपर (जैसे `document`) है और हर click पर unnecessary काम होता है। Root को जितना हो सके पास रखो
- Event को children तक पहुँचने से पहले रोकना हो (इसके लिए capture phase देखो, अगले topic में)

---

## 📊 Visual Diagram
```
   User clicks <button> inside <li>
                 │
                 ▼
   ┌──────────────────────────────────────────┐
   │ <ul id="menu">   ◀── ONE listener here    │
   │   <li data-id="r1">                       │
   │     Biryani House                         │
   │     <button data-action="order">  ◀ target│
   │   </li>                                   │
   └──────────────────────────────────────────┘
                 │
     event bubbles UP from button → li → ul
                 │
                 ▼
   ul handler:
     const btn = event.target.closest('button[data-action]')
     const row = btn.closest('li')           → data-id = "r1"
     run action for "r1"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event Delegation | Parent पर एक listener, children के events handle करता है | Event Delegation |
| Event Bubbling | Event target से ऊपर parents तक जाता है | Event Bubbling |
| `event.target` | Element जहाँ असली event हुआ | असली निशाना |
| `event.currentTarget` | Element जिस पर listener लगा है | Listener वाला element |
| `closest(selector)` | ऊपर की chain में matching element ढूँढता है | सबसे पास वाला मिलता element |
| `AbortController` | `signal` के ज़रिए listener हटाने का तरीका | Listener बंद करने का स्विच |
| Dispatch Table | action name -> function का map | Action और function की सूची |

---

## ⚡ 3-Line Summary
English: Event delegation uses one listener on a parent to handle clicks on many children.
It works because events bubble, and `event.target.closest()` finds the right item.
It keeps memory low and automatically covers elements added later.

Hindi: Event delegation में parent पर एक listener लगाया जाता है जो कई children के clicks संभालता है।
यह इसलिए चलता है क्योंकि events bubble होते हैं, और `closest()` सही item ढूँढता है।
इससे memory कम लगती है और बाद में जुड़े elements भी अपने-आप काम करते हैं।

---

## ➡️ Next Topic
147. Event Propagation + stopPropagation (हिंदी: Event Propagation और stopPropagation)। Delegation को समझने के लिए capture और bubble phases जानना ज़रूरी है। अगला topic यही बताता है कि event किस क्रम में चलता है और उसे कहाँ रोका जा सकता है।
