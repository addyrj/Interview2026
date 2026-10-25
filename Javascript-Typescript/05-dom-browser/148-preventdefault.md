# 148. preventDefault
# हिंदी में: preventDefault — Browser की Default Action को रोकना

---

## 🔵 Simple Definition (English)
`event.preventDefault()` tells the browser not to perform its built-in action for an event, such as following a link, submitting a form, or opening the right-click menu. Your JavaScript then takes over and decides what happens next.

## 🔵 सरल परिभाषा (Hindi)
`event.preventDefault()` browser को बताता है कि किसी event की built-in action न करे, जैसे link खोलना, form submit करना, या right-click menu दिखाना। उसके बाद JavaScript तय करता है कि आगे क्या होगा।

---

## 🔴 Problem it Solves
मान लो Razorpay के payment form में user "Pay" दबाता है। Browser का default व्यवहार है कि form सीधे server पर POST होगा और पूरा page reload होगा। पर हमें पहले card details validate करनी हैं, loader दिखाना है, और फिर API call करनी है। बिना रोके browser अपनी default action पहले ही कर देगा, और हमारा code बेकार हो जाएगा।

इसी तरह, Swiggy जैसी single-page apps में link पर click होने से पूरा page reload होगा। SPA में router को link संभालना होता है, इसलिए default navigation रोकना पड़ता है।

## 🔴 यह क्यों बना? (Hindi)
Browser में बहुत-सी events की default behaviour पहले से तय होती है: link navigation, form submission, checkbox toggle, text input, context menu, और scroll। पुराने web में यह सही था, पर modern apps को इन पर control चाहिए। `preventDefault` इसीलिए आया ताकि developer default को बदल सके और अपनी logic लिख सके।

---

## 🟢 How it Works — Step by Step

Step 1 → Event (जैसे `submit` या `click`) होता है।
Step 2 → Listener चलता है और `event.preventDefault()` call करता है।
Step 3 → Browser देखता है कि event `cancelable` है और listener `passive` नहीं है, तो default action रुक जाती है।
Step 4 → `event.defaultPrevented` अब `true` होता है, जिसे बाद के listeners भी पढ़ सकते हैं।
Step 5 → JavaScript अपनी logic चलाता है, जैसे validation, fetch, या router navigation।

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Event होता है (जैसे `submit`)।
Step 2 → Listener `event.preventDefault()` call करता है।
Step 3 → Browser default action (page reload, navigation) रोक देता है।
Step 4 → `event.defaultPrevented` अब `true` दिखाता है।
Step 5 → JavaScript अपना काम करता है, जैसे validation या API call।

---

## 🟡 Real World Example
Razorpay या Paytm के checkout में form submit होने पर पहले `preventDefault` लगता है। फिर card number validate होता है, error दिखते हैं, और सब सही हो तो `fetch` से payment API को call किया जाता है। Swiggy की web app में "Restaurant" link पर click होने पर `preventDefault` लगता है, फिर router `history.pushState` से page बदलता है, ताकि page reload न हो। Amazon जैसी sites custom right-click menu दिखाती हैं, जिसके लिए `contextmenu` event पर `preventDefault` लगता है।

## 🟡 Real Example Hindi mein
Razorpay या Paytm के checkout में form submit पर `preventDefault` लगता है। फिर card validate होता है, error दिखते हैं, और सही होने पर payment API call होती है। Swiggy में restaurant link पर click होने पर `preventDefault` लगता है, फिर router page बदलता है बिना reload के। Amazon custom right-click menu के लिए `contextmenu` event पर `preventDefault` लगाता है।

---

## 💻 Code Example — Basic
Browser-only topic है, इसलिए `node file.js` से नहीं चलेगा। नीचे पूरा HTML page है। इसे `prevent-basic.html` नाम से सेव करो और browser में खोलो। Form submit और link click दोनों पर default action रुकेगी, और log में दिखेगा।

```html
<!DOCTYPE html>
<!-- preventDefault ka basic demo: form submit aur link click -->
<html lang="en">
<head>
  <meta charset="UTF-8" />                                                  <!-- encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1" />  <!-- responsive -->
  <title>preventDefault Basic</title>                                      <!-- tab title -->
</head>
<body>
  <!-- Form: default submit par page reload hota (action ke hisaab se) -->
  <form id="pay-form" action="/pay" method="post">
    <label>Amount ₹ <input id="amount" type="number" value="499" /></label> <!-- amount input -->
    <button type="submit">Pay</button>                                       <!-- submit button -->
  </form>

  <!-- Link: default click par browser is URL par jaata -->
  <a id="help" href="https://example.com/help">Help page</a>

  <pre id="log"></pre>                                                       <!-- log box -->

  <script>
    const log = document.getElementById('log');                 // log element
    const print = (msg) => { log.textContent += msg + '\n'; };  // line jodne ka helper

    const form = document.getElementById('pay-form');           // form element
    form.addEventListener('submit', (event) => {                // submit hone se pehle chalega
      event.preventDefault();                                   // default page reload roko
      const amount = Number(document.getElementById('amount').value); // amount padho
      print(`Submit blocked. Amount = ${amount}`);              // JS yahan se control leta hai
    });

    const help = document.getElementById('help');              // link element
    help.addEventListener('click', (event) => {                // link click par
      event.preventDefault();                                   // navigation roko
      print('Help link blocked. Ab JS apna modal dikha sakta hai.'); // custom action
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Yeh ek realistic checkout form aur SPA link interception ka demo hai। Form submit पर validation होती है, errors दिखते हैं, और सही होने पर `fetch` से API call होती है, जिसमें timeout (AbortController) भी है। Link interception में modifier keys (Ctrl/Cmd/Shift) और middle-click को नहीं रोका जाता, ताकि नए tab वाला कामकाज चलता रहे। HTML file browser में खोलो। Demo ke liye API call fail होगी, जो error handling दिखाने के लिए है।

```html
<!DOCTYPE html>
<!-- Advanced: validated checkout form + SPA link interception -->
<html lang="en">
<head>
  <meta charset="UTF-8" />                                                 <!-- encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1" /> <!-- responsive -->
  <title>preventDefault Advanced</title>                                  <!-- tab title -->
</head>
<body>
  <nav>
    <a href="/restaurants" data-spa>Restaurants</a>                       <!-- SPA link: router sambhalega -->
    <a href="/orders" data-spa>Orders</a>                                  <!-- SPA link -->
  </nav>
  <h3 id="view">Home</h3>                                                  <!-- current view ka title -->

  <form id="checkout" novalidate>                                          <!-- novalidate: humari validation -->
    <input id="card" placeholder="Card (16 digits)" maxlength="19" />      <!-- card input -->
    <p id="card-error" style="color:red;"></p>                             <!-- validation error -->
    <button id="pay" type="submit">Pay ₹499</button>                       <!-- submit -->
  </form>
  <p id="status"></p>                                                      <!-- final status -->

  <script>
    'use strict';                                                          // strict mode
    const $ = (id) => document.getElementById(id);                         // helper
    const form = $('checkout');
    const cardInput = $('card');
    const cardError = $('card-error');
    const status = $('status');

    // Card validation: sirf digits, 16 length (demo; asli app mein Luhn check bhi hota hai)
    function validateCard(value) {
      const digits = value.replace(/\s+/g, '');                            // spaces hata do
      if (!/^\d{16}$/.test(digits)) return 'Card 16 digits ka hona chahiye.'; // galat format
      return '';                                                           // sab sahi, koi error nahin
    }

    form.addEventListener('submit', async (event) => {                     // submit par async handler
      event.preventDefault();                                              // page reload roko (zaroori)
      const error = validateCard(cardInput.value);                         // validation chalao
      cardError.textContent = error;                                       // error dikhao ya clear karo
      if (error) return;                                                   // galat hai to aage mat jao

      const controller = new AbortController();                            // timeout ke liye
      const timer = setTimeout(() => controller.abort(), 3000);            // 3 second baad abort
      try {
        status.textContent = 'Processing...';                              // loader jaisa message
        const res = await fetch('/api/pay', {                              // payment API call
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },                 // JSON body
          body: JSON.stringify({ amount: 499 }),                           // amount bhejo
          signal: controller.signal,                                       // timeout signal
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);                // server error
        status.textContent = 'Payment successful!';                        // success
      } catch (err) {
        status.textContent = `Payment failed: ${err.name === 'AbortError' ? 'timeout' : err.message}`; // error message
      } finally {
        clearTimeout(timer);                                               // timer saaf karo
      }
    });

    // SPA router: sirf normal left-click par preventDefault, modifier keys par nahin
    document.addEventListener('click', (event) => {
      const link = event.target.closest('a[data-spa]');                    // SPA link dhoondo
      if (!link) return;                                                   // normal link: kuch mat karo
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey) return; // new tab wale click
      event.preventDefault();                                              // page reload roko
      history.pushState({}, '', link.getAttribute('href'));                // URL badlo bina reload
      $('view').textContent = link.textContent;                            // view badlo
    });

    // Right-click par custom menu ki jagah default menu band
    document.addEventListener('contextmenu', (event) => {
      event.preventDefault();                                              // browser ka menu nahin
      status.textContent = 'Custom menu would open here';                  // apna menu dikhane ki jagah
    });
  </script>
</body>
</html>
```

---

## 🧠 Express.js Integration
`preventDefault` browser ka concept है, Express में नहीं चलता। Express का काम है page serve करना और वह API देना जिसे browser का submit handler `fetch` से call करता है। Progressive enhancement के लिए server form-encoded data भी लेता है, ताकि JavaScript बंद होने पर भी form काम करे।

```javascript
// server.js: Express server, payment page serve karta hai aur /api/pay handle karta hai
const express = require('express');                    // Express framework
const path = require('path');                          // path utilities

const app = express();                                 // Express app
const PORT = process.env.PORT || 3000;                 // port

app.use(express.json());                               // JSON body parse (fetch ke liye)
app.use(express.urlencoded({ extended: false }));      // HTML form body parse (JS band ho to)
app.use(express.static(path.join(__dirname, 'public'))); // public/ folder serve karo

// Browser ka fetch() is route par POST karega
app.post('/api/pay', (req, res) => {                   // payment endpoint
  const amount = Number(req.body.amount);              // amount body se nikalo
  if (!Number.isFinite(amount) || amount <= 0) {       // validation
    return res.status(400).json({ error: 'invalid amount' }); // 400 Bad Request
  }
  // Asli app mein yahan payment gateway call hoti hai
  res.status(201).json({ status: 'paid', amount });    // 201 Created
});

// Fallback: form JS ke bina submit ho to /pay par POST aata hai
app.post('/pay', (req, res) => {                       // HTML form ka action
  res.redirect('/?paid=1');                            // redirect karke page reload
});

app.listen(PORT, () => {                               // server start
  console.log(`Server running at http://localhost:${PORT}`); // start message
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `addEventListener` के handler में `return false` से default रोकने की उम्मीद करना।
✅ Correct: `return false` केवल inline `onclick` attributes में काम करता है। `addEventListener` में `event.preventDefault()` ही इस्तेमाल करो।

```javascript
// Wrong: return false se navigation nahin rukegi
link.addEventListener('click', () => {
  return false;                              // addEventListener mein yeh kuch nahin karta
});

// Right: preventDefault call karo
link.addEventListener('click', (event) => {
  event.preventDefault();                    // ab navigation sach mein ruk jayegi
});
```

❌ Mistake 2: `passive: true` listener के अंदर `preventDefault` लगाना।
✅ Correct: `passive: true` का मतलब है कि listener वादा करता है कि वह default नहीं रोकेगा। ऐसे में `preventDefault` ignore होता है। जब preventDefault चाहिए, तो `passive` मत लगाओ।

```javascript
// Wrong: passive true par preventDefault ignore hoga (browser warning deta hai)
el.addEventListener('touchmove', (e) => {
  e.preventDefault();                        // kaam nahin karega
}, { passive: true });

// Right: passive ko hata do jab default rokna ho
el.addEventListener('touchmove', (e) => {
  e.preventDefault();                        // ab sach mein scroll rukega
}, { passive: false });
```

❌ Mistake 3: Form submit रोकने के बाद भी `async` फ़ंक्शन में `preventDefault` देर से लगाना।
✅ Correct: `preventDefault` हमेशा handler के सबसे पहले line में लगाओ, किसी `await` से पहले। `await` के बाद लगाने पर submit पहले ही हो चुका होता है।

```javascript
// Wrong: await se pehle hi form submit ho sakta hai, preventDefault late hai
form.addEventListener('submit', async (e) => {
  await validate();                          // yahan tak browser ne default kar diya hoga
  e.preventDefault();                        // bahut late
});

// Right: sabse pehle preventDefault
form.addEventListener('submit', async (e) => {
  e.preventDefault();                        // pehle roko
  await validate();                          // phir async kaam karo
});
```

---

## 🧠 Tricky Interview Question
नीचे link है और तीन listeners हैं। Click पर console में क्या आएगा, और `location.hash` क्या होगा?

```html
<a id="a" href="#section">Go</a>
<script>
  const a = document.getElementById('a');                              // link element
  a.addEventListener('click', (e) => {                                  // listener 1
    console.log('listener 1');
    return false;                                                      // yeh kuch nahin karega
  });
  a.addEventListener('click', (e) => {                                  // listener 2
    e.preventDefault();                                                // navigation roko
    console.log('listener 2', e.defaultPrevented);
  });
  a.addEventListener('click', (e) => {                                  // listener 3
    console.log('listener 3', e.defaultPrevented);
  });
  a.click();                                                           // programmatic click
  console.log('hash =', JSON.stringify(location.hash));                 // URL ka hash
</script>
```

Answer: Output hoga:
```
listener 1
listener 2 true
listener 3 true
hash = ""
```
- Sabhi तीनों listeners चलते हैं, क्योंकि `preventDefault` केवल default action रोकता है, दूसरे listeners को नहीं।
- `return false` से कुछ नहीं होता। `addEventListener` के handler में `return false` default को नहीं रोकता; उसका कोई असर नहीं होता। Default रोकने का काम सिर्फ़ listener 2 का `preventDefault` करता है।
- Listener 2 `e.preventDefault()` call करता है, इसलिए `#section` पर navigation नहीं होता और `location.hash` खाली रहता है।
- Listener 3 को `defaultPrevented` `true` दिखता है, क्योंकि event की state पहले से बदल चुकी है।
- अगर listener 2 में `preventDefault` न होता, तो browser `#section` पर navigate कर देता (URL में hash जुड़ जाता)।
(इसे jsdom में चलाकर verify किया गया है।)

---

## ⚫ Interview Questions + Answers

Q1: `preventDefault` और `stopPropagation` में क्या फ़र्क है?
A1: `preventDefault` browser की default action (link, submit, context menu) रोकता है। `stopPropagation` event को DOM में आगे के elements तक जाने से रोकता है। दोनों अलग काम हैं और दोनों एक साथ लग सकते हैं।

Q2: `event.defaultPrevented` किस काम का है?
A2: यह `true` दिखाता है कि कोई पहले listener `preventDefault` call कर चुका है। दूसरे code को पता चल जाता है कि default action पहले ही रोका जा चुका है।

Q3: कौन-से events cancelable नहीं होते, और उन पर `preventDefault` काम क्यों नहीं करता?
A3: `scroll`, `load`, `focus`, `blur` जैसे कई events non-cancelable होते हैं। `event.cancelable` से check कर सकते हैं। Non-cancelable events पर `preventDefault` बिना error के ignore हो जाता है।

Q4: SPA में link click पर `preventDefault` क्यों लगाते हैं?
A4: ताकि browser full page reload न करे। Router `history.pushState` से URL बदलता है और view अपडेट करता है। पर Ctrl/Cmd click या middle click को नहीं रोकना चाहिए, क्योंकि वे नए tab में खोलते हैं।

Q5: Form को JavaScript से submit करने के बाद भी server पर form data क्यों भेजा जा सकता है?
A5: Form submit को रोककर `fetch` से data भेजा जा सकता है। इससे page reload नहीं होता और response को JS में handle किया जा सकता है। Server को JSON और form-encoded दोनों संभालने चाहिए ताकि JS बंद होने पर भी काम हो।

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Form submit को validation या async API call के लिए रोकना है
- SPA में internal links पर router से navigation करना है
- Custom context menu, drag-drop, या keyboard shortcut बनाना है
- Browser की default behaviour (जैसे "Space से scroll") बदलनी है

❌ Avoid when:
- केवल कोई और listener रोकना है (वह `stopPropagation` या `stopImmediatePropagation` का काम है)
- `passive: true` listener में default रोकना चाहिए (ignore होगा)
- Accessibility ख़राब करना: link को `<div>` बना कर keyboard से न पहुँचने देना
- Native behaviour सही है: normal link और form के लिए बेवजह JS न लगाओ

---

## 📊 Visual Diagram
```
  User action (click / submit / right-click)
              │
              ▼
  Event dispatched to target element
              │
              ▼
  Listener runs ─── event.preventDefault() ?
              │                    │
              │ NO                 │ YES (cancelable && !passive)
              ▼                    ▼
  Browser default action      Default action CANCELLED
  (navigate / submit /        event.defaultPrevented = true
   open menu)                 JS takes over (validate / fetch / router)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `preventDefault()` | Browser की default action रोकना | Default action रोकना |
| `defaultPrevented` | Default रुका है या नहीं, यह बताने वाला flag | Default रुका या नहीं |
| `cancelable` | क्या event की default action रोकी जा सकती है | रोकने योग्य event |
| `passive` option | Listener का वादा कि वह default नहीं रोकेगा | निष्क्रिय listener |
| Default Action | Browser का built-in व्यवहार (navigate, submit) | Browser का अपना काम |
| `history.pushState` | URL बदलना बिना page reload के | बिना reload URL बदलना |
| Progressive Enhancement | JS बंद होने पर भी basic काम करना | धीरे-धीरे बढ़ाया गया काम |

---

## ⚡ 3-Line Summary
English: `event.preventDefault()` stops the browser's default action, such as navigation, form submit, or context menu.
It only works on cancelable events and listeners that are not `passive`; `return false` does nothing in `addEventListener`.
Call it first in the handler, and use it with a target check so modifier-key clicks still open new tabs.

Hindi: `event.preventDefault()` browser की default action (navigation, form submit, context menu) को रोकता है।
यह केवल cancelable events और non-passive listeners पर काम करता है; `addEventListener` में `return false` कुछ नहीं करता।
Handler की शुरुआत में इसे लगाओ, और modifier keys वाले clicks के लिए target check रखो ताकि नए tab वाला काम चलता रहे।

---

## ➡️ Next Topic
149. Custom Events (हिंदी: Custom Events)। अब तक हमने browser के built-in events देखे। अगला topic बताता है कि अपने खुद के events कैसे बनाएँ, dispatch करें, और उन्हें components के बीच communication के लिए कैसे इस्तेमाल करें।
