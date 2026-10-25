# 147. Event Propagation + stopPropagation
# हिंदी में: Event Propagation और stopPropagation — Event किस क्रम में चलता है और कैसे रोका जाता है

---

## 🔵 Simple Definition (English)
When an event happens on an element, it travels through the DOM in three phases: capture (top to target), target (the element itself), and bubble (target back up to top). `event.stopPropagation()` stops the event from moving to the next element in this path.

## 🔵 सरल परिभाषा (Hindi)
जब किसी element पर event होता है, तो वह DOM में तीन phases से गुज़रता है: capture (ऊपर से target तक), target (वही element), और bubble (target से वापस ऊपर तक)। `event.stopPropagation()` event को इस रास्ते में आगे बढ़ने से रोक देता है।

---

## 🔴 Problem it Solves
Browser में एक click पर कई listeners चल सकते हैं। Example: Paytm के dropdown में "Account" पर click किया, और पेज पर एक listener है जो "बाहर click" होने पर dropdown बंद करता है। अगर वह listener पहले ही चल गया, तो dropdown खुलते ही बंद हो जाएगा। ऐसे मामलों में event का सही क्रम समझना और उसे रोकने का नियंत्रित तरीका चाहिए।

Propagation को समझे बिना developers को "click बंद क्यों नहीं हो रहा" या "click दो बार क्यों चल रहा" जैसी bugs मिलती हैं।

## 🔴 यह क्यों बना? (Hindi)
Browser को एक ही click से parent और child दोनों की logic चलानी होती है, जैसे form के अंदर का button और form का पूरा section। Event flow की तीन phases इसीलिए बनीं ताकि ऊपर के elements capture phase में पहले जान सकें, और नीचे का element पहले reaction दे सके। `stopPropagation` इसलिए आया ताकि developer तय कर सके कि event कहाँ तक जाए।

---

## 🟢 How it Works — Step by Step

Step 1 → User किसी element (जैसे button) पर click करता है।
Step 2 → CAPTURE phase: event `window` से शुरू होकर नीचे target की ओर जाता है। जिन listeners में `capture: true` है, वे यहाँ चलते हैं।
Step 3 → TARGET phase: जिस element पर click हुआ, उसके सभी listeners चलते हैं।
Step 4 → BUBBLE phase: event target से वापस ऊपर `document` और `window` तक जाता है। Default listeners यहाँ चलते हैं।
Step 5 → `stopPropagation()` call हो तो अगले elements तक event नहीं जाता, पर उसी element के बाकी listeners चल जाते हैं।

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User button पर click करता है।
Step 2 → CAPTURE: event ऊपर से नीचे target तक जाता है (जिन listeners में `capture: true` है)।
Step 3 → TARGET: उस element के सभी listeners चलते हैं।
Step 4 → BUBBLE: event नीचे से ऊपर वापस जाता है (default listeners)।
Step 5 → `stopPropagation()` event को आगे रोकता है, पर उसी element के बाकी listeners नहीं रुकते।

---

## 🟡 Real World Example
Zomato के app में restaurant card पर click करने से restaurant page खुलता है, और card के अंदर का "Add" button अलग काम करता है। अगर "Add" click पर parent card का navigation भी चल जाए, तो user गलती से restaurant page पर चला जाएगा। वहाँ `stopPropagation` काम आता है।

Razorpay checkout modal में backdrop (बाहर का dark area) click करने पर modal बंद होता है, पर modal के अंदर click करने पर नहीं। Paytm के dropdown menu में "बाहर click करने पर बंद करो" logic होता है, जिसमें toggle button पर `stopPropagation` ज़रूरी होता है।

## 🟡 Real Example Hindi mein
Zomato में restaurant card पर click करने से page खुलता है, पर card के अंदर "Add" button पर click करने से सिर्फ़ item cart में जुड़ता है। Razorpay के modal में backdrop पर click करने से modal बंद होता है, पर modal के अंदर click से नहीं। Paytm के dropdown में toggle button पर `stopPropagation` लगता है, ताकि "बाहर click" वाला listener उसी click से तुरंत dropdown बंद न कर दे।

---

## 💻 Code Example — Basic
Browser-only topic है, इसलिए `node file.js` से नहीं चलेगा। नीचे पूरा HTML page है। इसे `propagation-basic.html` नाम से सेव करो, browser में खोलो, और button दबाओ। Log में capture और bubble का क्रम दिखेगा।

```html
<!DOCTYPE html>
<!-- Event propagation ka basic demo -->
<html lang="en">
<head>
  <meta charset="UTF-8" />                                                  <!-- encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1" />  <!-- responsive width -->
  <title>Propagation Basic</title>                                         <!-- tab ka title -->
</head>
<body>
  <!-- Teen nested elements: outer > middle > button -->
  <div id="outer" style="padding:20px; background:#eef;">     <!-- sabse bahar wala div -->
    <div id="middle" style="padding:20px; background:#dfd;">   <!-- beech wala div -->
      <button id="btn">Pay ₹499</button>                       <!-- andar ka button (target) -->
    </div>
  </div>
  <pre id="log"></pre>                                         <!-- log dikhane ke liye -->

  <script>
    const log = document.getElementById('log');                // log box lo
    const print = (msg) => { log.textContent += msg + '\n'; }; // ek line jodne ka helper

    // capture: true = CAPTURE phase (window se neeche target ki taraf) mein chalega
    document.addEventListener('click', () => print('capture: document'), true);
    document.getElementById('outer').addEventListener('click', () => print('capture: outer'), true);

    // Default (bubble) listeners: BUBBLE phase (target se upar ki taraf) mein chalte hain
    document.getElementById('middle').addEventListener('click', () => print('bubble: middle'));
    document.getElementById('outer').addEventListener('click', () => print('bubble: outer'));
    document.getElementById('btn').addEventListener('click', (e) => {   // button par listener
      print(`target: button (eventPhase=${e.eventPhase})`);             // 2 = AT_TARGET
    });
    document.addEventListener('click', () => print('bubble: document')); // sabse upar wala bubble listener
  </script>
</body>
</html>
```

Button par click karne ka expected log:
```
capture: document
capture: outer
target: button (eventPhase=2)
bubble: middle
bubble: outer
bubble: document
```

## 💻 Code Example — Advanced
यह एक practical modal और dropdown demo है। Dropdown का toggle `stopPropagation` इस्तेमाल करता है ताकि "बाहर click" वाला listener उसी click से dropdown बंद न करे। Modal का backdrop सिर्फ़ तब बंद होता है जब `event.target` backdrop ही हो। Escape key भी काम करता है, और `once` option से पहला click ही track होता है। HTML page को browser में खोलो।

```html
<!DOCTYPE html>
<!-- Advanced: modal + dropdown with correct propagation handling -->
<html lang="en">
<head>
  <meta charset="UTF-8" />                                                 <!-- encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1" /> <!-- responsive -->
  <title>Propagation Advanced</title>                                     <!-- tab title -->
  <style>
    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: none; }  /* poori screen ka dark layer */
    .overlay.open { display: flex; align-items: center; justify-content: center; }      /* open hone par dikhe */
    .card { background: #fff; padding: 24px; border-radius: 8px; min-width: 260px; }     /* modal box */
  </style>
</head>
<body>
  <button id="open-btn">Open Payment</button>              <!-- modal kholne ka button -->
  <div id="dropdown-wrap">
    <button id="menu-toggle">Account ▾</button>            <!-- dropdown toggle -->
    <ul id="menu" hidden>                                  <!-- dropdown; hidden = chhupa -->
      <li>Profile</li>
      <li>Orders</li>
    </ul>
  </div>

  <div id="overlay" class="overlay">                       <!-- modal ka backdrop -->
    <div id="card" class="card">                           <!-- modal ka box -->
      <h3>Pay ₹499 to Razorpay Demo</h3>
      <p>Dark area par click karo to band hoga. Escape bhi kaam karega.</p>
      <button id="close-btn">Close</button>
    </div>
  </div>

  <p id="status">Status: ready</p>                         <!-- status message -->

  <script>
    'use strict';                                            // strict mode: galti par error
    const $ = (id) => document.getElementById(id);           // chhota helper
    const required = ['open-btn', 'menu-toggle', 'menu', 'dropdown-wrap', 'overlay', 'close-btn', 'status'];
    for (const id of required) {                             // zaroori elements hain ya nahin, check karo
      if (!$(id)) throw new Error(`Missing element: #${id}`); // na ho to clear error
    }

    const overlay = $('overlay');                            // modal backdrop
    const menu = $('menu');                                  // dropdown menu
    const status = $('status');                              // status text

    function openModal() {                                   // modal dikhao
      overlay.classList.add('open');
      status.textContent = 'Status: modal open';
    }
    function closeModal() {                                  // modal chhupao
      overlay.classList.remove('open');
      status.textContent = 'Status: modal closed';
    }

    // Modal open: once true = yeh listener sirf pehli baar chalega (welcome message ke liye)
    $('open-btn').addEventListener('click', () => {
      openModal();                                           // modal kholo
    });
    $('open-btn').addEventListener('click', () => {
      status.textContent += ' (first open tracked)';         // pehli baar ka extra note
    }, { once: true });                                      // baad ke clicks par ye nahin chalega

    // Backdrop click: sirf tab band karo jab target khud backdrop ho (card ke andar click par nahin)
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal();                // backdrop par hi click hua
    });
    $('close-btn').addEventListener('click', closeModal);    // close button
    document.addEventListener('keydown', (e) => {            // Escape key se bhi band
      if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal();
    });

    // Dropdown toggle: stopPropagation zaroori hai
    $('menu-toggle').addEventListener('click', (e) => {
      e.stopPropagation();                                   // yeh click document tak na jaye
      menu.hidden = !menu.hidden;                            // open/close toggle karo
    });
    // "Bahar click" listener: dropdown band karta hai
    document.addEventListener('click', (e) => {
      if (!$('dropdown-wrap').contains(e.target)) {          // click dropdown ke bahar hai?
        menu.hidden = true;                                  // to dropdown band
      }
    });
  </script>
</body>
</html>
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: सोचना कि `stopPropagation` उसी element के बाकी listeners भी रोक देता है।
✅ Correct: `stopPropagation` सिर्फ़ आगे के elements तक जाने से रोकता है। उसी element के बाकी listeners चलते हैं। उन्हें भी रोकने के लिए `stopImmediatePropagation()` इस्तेमाल करो।

```javascript
// Wrong: dono listeners chalenge, kyunki stopPropagation same element ko nahin rokta
btn.addEventListener('click', (e) => { e.stopPropagation(); console.log('A'); });
btn.addEventListener('click', () => console.log('B')); // B bhi chalega

// Right: stopImmediatePropagation same element ke baaki listeners bhi rokta hai
btn.addEventListener('click', (e) => { e.stopImmediatePropagation(); console.log('A'); });
btn.addEventListener('click', () => console.log('B')); // ab B nahin chalega
```

❌ Mistake 2: Bug ठीक करने के लिए हर जगह `stopPropagation` लगा देना।
✅ Correct: `stopPropagation` parent या document के listeners को चुपचाप तोड़ देता है (जैसे analytics, "click outside" logic)। पहले सोचो कि क्या target check (`e.target === overlay`) से काम चल सकता है।

```javascript
// Wrong: card par stopPropagation, ab overlay ka close logic kabhi chalega hi nahin
card.addEventListener('click', (e) => e.stopPropagation());
overlay.addEventListener('click', closeModal); // card ke andar click par bhi NAHIN chalega, bug

// Right: target check se backdrop click ko pehchano, koi propagation nahin rokni
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeModal();        // sirf backdrop par hi band
});
```

❌ Mistake 3: `removeEventListener` में `capture` flag भूल जाना।
✅ Correct: `addEventListener` में `capture: true` दिया हो, तो `removeEventListener` में भी वही flag देना होगा, वरना listener हटेगा नहीं।

```javascript
// Wrong: capture flag nahin diya, listener hatega nahin
el.addEventListener('click', handler, true);
el.removeEventListener('click', handler);       // galat: capture flag match nahin hua

// Right: same capture value
el.addEventListener('click', handler, true);
el.removeEventListener('click', handler, true); // sahi: listener hat jayega
```

---

## 🧠 Tricky Interview Question
नीचे code है। Button पर click करने से कौन-से logs print होंगे, और किस क्रम में?

```html
<div id="outer">
  <button id="btn">Click</button>
</div>
<script>
  const outer = document.getElementById('outer');     // parent div
  const btn = document.getElementById('btn');         // button (target)

  outer.addEventListener('click', () => console.log('outer bubble'));                  // default: bubble
  outer.addEventListener('click', () => console.log('outer capture'), { capture: true }); // capture
  btn.addEventListener('click', (e) => {               // pehla listener button par
    console.log('btn');
    e.stopPropagation();                               // aage bubble nahin hoga
  });
  btn.addEventListener('click', () => console.log('btn second')); // dusra listener, same element
  document.addEventListener('click', () => console.log('document')); // bubble listener upar

  btn.click();                                         // programmatic click
</script>
```

Answer: Output hoga:
```
outer capture
btn
btn second
```
- `outer capture` पहले चलता है क्योंकि capture phase में event ऊपर से नीचे target की ओर जाता है। `outer` पर `capture: true` वाला listener target से पहले चलता है।
- फिर target (`btn`) के listeners चलते हैं। `btn` पहला listener `stopPropagation` call करता है, पर उसी element का दूसरा listener (`btn second`) फिर भी चलता है, क्योंकि `stopPropagation` same element को नहीं रोकता।
- `outer bubble` और `document` नहीं चलते, क्योंकि event bubble phase में ऊपर जाने से पहले ही रुक गया।
(इसे jsdom में चलाकर verify किया गया है।)

---

## ⚫ Interview Questions + Answers

Q1: Event propagation की तीन phases कौन-सी हैं?
A1: Capture (window से target तक नीचे), target (जिस element पर event हुआ), और bubble (target से वापस window तक ऊपर)।

Q2: `stopPropagation` और `stopImmediatePropagation` में क्या फ़र्क है?
A2: `stopPropagation` आगे के elements तक event को रोकता है, पर उसी element के बाकी listeners चलते हैं। `stopImmediatePropagation` उसी element के बाकी listeners भी रोक देता है।

Q3: `preventDefault` और `stopPropagation` में क्या फ़र्क है?
A3: `stopPropagation` event के आगे जाने को रोकता है। `preventDefault` browser की default action (जैसे link navigation या form submit) को रोकता है। दोनों एक-दूसरे की जगह नहीं लेते।

Q4: `addEventListener` का तीसरा argument (`capture`) क्या करता है?
A4: `true` देने पर listener capture phase में चलता है। Default `false` है, यानी bubble phase में चलता है। Options object (`{ capture, once, passive, signal }`) भी दिया जा सकता है।

Q5: Modal या dropdown में "बाहर click" logic कैसे लिखें बिना bugs के?
A5: Document पर click listener लगाओ और `container.contains(e.target)` से check करो। Toggle button पर `stopPropagation` लगाओ ताकि उसी click से dropdown तुरंत बंद न हो। वैकल्पिक तरीका target check ही है।

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Nested element पर click का बाहर वाले parent पर असर नहीं चाहिए (जैसे inline buttons in clickable cards)
- Dropdown toggle जैसी किसी एक click को "बाहर click" logic से अलग रखना है
- एक ही element पर दूसरे listeners को रोकना है (`stopImmediatePropagation`)
- Capture phase में जल्दी पकड़ना हो (`capture: true`)

❌ Avoid when:
- केवल बाहर के element को पता चलना है कि क्या हुआ (analytics, logging): इससे data खो जाता है
- Bug छिपाने के लिए (पहले root cause ढूँढो)
- Delegation के साथ: parent पर listener चाहिए तो child का `stopPropagation` उसे तोड़ देगा
- Target check से काम चल सकता है: तो propagation को छूने की ज़रूरत नहीं

---

## 📊 Visual Diagram
```
  window
    │   ── CAPTURE (↓) ──  capture listeners chalte hain (capture: true)
    ▼
  document
    ▼
  div#outer          (capture: outer)
    ▼
  div#middle
    ▼
  button  ◀── TARGET (yahan click hua)
    │   ── BUBBLE (↑) ──  default listeners chalte hain
    ▲
  div#middle          (bubble: middle)
    ▲
  div#outer           (bubble: outer)
    ▲
  document            (bubble: document)
    ▲
  window

  stopPropagation() bubble ke raste ko rok deta hai
  (same element ke baaki listeners nahin rukte)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Capture Phase | Window se target tak event का नीचे जाना | कैप्चर फ़ेज़ |
| Target Phase | जिस element पर event हुआ, वहाँ का चरण | टारगेट फ़ेज़ |
| Bubble Phase | Target से window तक event का ऊपर आना | बबल फ़ेज़ |
| `stopPropagation()` | आगे के elements तक event जाने से रोकना | प्रसार रोकना |
| `stopImmediatePropagation()` | उसी element के बाकी listeners भी रोकना | तुरंत प्रसार रोकना |
| `eventPhase` | Event किस phase में है (1, 2, 3) | फ़ेज़ नंबर |
| `capture` option | Listener को capture phase में चलाना | कैप्चर विकल्प |

---

## ⚡ 3-Line Summary
English: Events travel in three phases: capture (top to target), target, and bubble (target back to top).
`stopPropagation()` stops the event from moving to other elements, but not the other listeners on the same element.
Use `stopImmediatePropagation()` for same-element listeners, and prefer target checks over stopping propagation.

Hindi: Events तीन phases में चलते हैं: capture (ऊपर से target तक), target, और bubble (target से ऊपर तक)।
`stopPropagation()` event को दूसरे elements तक जाने से रोकता है, पर उसी element के बाकी listeners नहीं रुकते।
Same element के listeners रोकने के लिए `stopImmediatePropagation()` लो, और जहाँ संभव हो target check को प्राथमिकता दो।

---

## ➡️ Next Topic
148. preventDefault (हिंदी: preventDefault)। Propagation से event का रास्ता नियंत्रित होता है, और अगला topic बताता है कि browser की default action (जैसे link navigation, form submit) को कैसे रोका जाए।
