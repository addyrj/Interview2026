# 149. Custom Events
# हिंदी में: Custom Events — अपने खुद के Events बनाना और भेजना

---

## 🔵 Simple Definition (English)
Custom events are events you create yourself with a name of your choice, like `cart:add` or `order:placed`. You send them with `dispatchEvent()`, and any listener that is subscribed to that name receives them, along with your own data in `event.detail`.

## 🔵 सरल परिभाषा (Hindi)
Custom events वे events हैं जिन्हें आप अपने नाम से बनाते हैं, जैसे `cart:add` या `order:placed`। इन्हें `dispatchEvent()` से भेजा जाता है, और उस नाम को सुनने वाला हर listener उन्हें पाता है, साथ में आपका data `event.detail` में।

---

## 🔴 Problem it Solves
मान लो Swiggy की web app में product card पर "Add" दबता है। Header का cart badge उसी समय बदलना चाहिए, analytics को भी पता होना चाहिए, और mini-cart भी खुलना चाहिए। अगर card का code सीधे header, analytics और mini-cart को call करे, तो सब components एक-दूसरे पर निर्भर हो जाते हैं। एक हिस्सा बदलने पर बाकी भी टूटते हैं।

Custom events इस coupling को तोड़ते हैं। Card सिर्फ़ इतना announce करता है कि "cart में item जुड़ा", और जिसे सुनना है वह सुन ले।

## 🔴 यह क्यों बना? (Hindi)
Built-in events (click, input, submit) केवल browser के actions के लिए हैं। पर app-level घटनाएँ, जैसे "payment सफल", "cart खाली", या "session expire", किसी built-in event में फिट नहीं होतीं। Custom events इसीलिए बने ताकि developer अपने domain की घटनाओं को DOM के event system में ही भेज सके। इससे पुराना event bubbling, capture और `removeEventListener` जैसी सुविधाएँ भी मिलती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `new CustomEvent('cart:add', { detail: data, bubbles: true })` से event बनाओ।
Step 2 → `target.dispatchEvent(event)` से उसे किसी element या document पर भेजो।
Step 3 → इवेंट का नाम सुनने वाले सभी listeners (`addEventListener('cart:add', ...)`) चलते हैं।
Step 4 → हर listener `event.detail` पढ़ता है और अपना काम करता है।
Step 5 → अगर `bubbles: true` है, तो event ऊपर के parents तक भी जाता है। `cancelable: true` हो तो `dispatchEvent` का return value बताता है कि किसी ने default रोका या नहीं।

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `new CustomEvent` से नाम और data के साथ event बनाओ।
Step 2 → `dispatchEvent` से उसे element या document पर भेजो।
Step 3 → उस नाम के सभी listeners चलते हैं।
Step 4 → हर listener `event.detail` से data पढ़ता है।
Step 5 → `bubbles: true` हो तो event parents तक जाता है।

---

## 🟡 Real World Example
Swiggy के web app में "Add to cart" दबाने पर `cart:add` event भेजा जाता है। Header का badge, mini-cart और analytics तीनों उसे अलग-अलग सुनते हैं। Razorpay के checkout में `payment:success` event भेजा जाता है, जिसे पेज का UI, redirect logic और logging सभी सुनते हैं। Paytm के दूसरे tab में बदलाव हो तो server-sent events से `wallet:updated` आता है, और browser उसे custom event बनाकर पेज में फैला देता है।

## 🟡 Real Example Hindi mein
Swiggy में "Add" दबने पर `cart:add` event भेजा जाता है। Header का badge, mini-cart और analytics तीनों उसे अलग-अलग सुनते हैं, और product card को उनके बारे में कुछ पता नहीं होता। Razorpay checkout में `payment:success` event पर UI, redirect और logging सब चलते हैं। Paytm में दूसरे tab से wallet बदले, तो server से आया update custom event बनकर पेज में फैल जाता है।

---

## 💻 Code Example — Basic
Browser-only topic है, इसलिए `node file.js` से नहीं चलेगा। नीचे पूरा HTML page है। इसे `custom-events-basic.html` नाम से सेव करो, browser में खोलो और "Add" buttons दबाओ। Button को header के बारे में कुछ नहीं पता, फिर भी badge बदलता है।

```html
<!DOCTYPE html>
<!-- Custom event ka basic demo: button event bhejta hai, header sunta hai -->
<html lang="en">
<head>
  <meta charset="UTF-8" />                                                  <!-- encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1" />  <!-- responsive -->
  <title>Custom Events Basic</title>                                      <!-- tab title -->
</head>
<body>
  <header>Cart: <span id="badge">0</span> items</header>                  <!-- header badge -->

  <!-- Product buttons: inhe pata nahin ki header kaun hai -->
  <button class="add" data-id="p1" data-name="Paneer Tikka">Add Paneer Tikka</button>
  <button class="add" data-id="p2" data-name="Garlic Naan">Add Garlic Naan</button>

  <pre id="log"></pre>                                                    <!-- log output -->

  <script>
    const badge = document.getElementById('badge');                        // header badge element
    const log = document.getElementById('log');                            // log box
    let count = 0;                                                          // cart mein kitne items

    // Har "Add" button par click: custom event bhejo, koi direct function call nahin
    document.querySelectorAll('.add').forEach((btn) => {                   // sab add buttons par
      btn.addEventListener('click', () => {                                // click par
        const evt = new CustomEvent('cart:add', {                          // naya custom event banao
          detail: { id: btn.dataset.id, name: btn.dataset.name },          // payload: data yahan
          bubbles: true,                                                   // parents tak jaaye
        });
        btn.dispatchEvent(evt);                                            // button se event bhejo
      });
    });

    // Header (document) sunta hai "cart:add" ko, bina button ko jane
    document.addEventListener('cart:add', (event) => {                     // listener document par
      count += 1;                                                          // count badhao
      badge.textContent = String(count);                                   // badge update karo
      log.textContent += `Added ${event.detail.name} (id=${event.detail.id})\n`; // log
    });
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
यह pure JavaScript है, इसलिए `node advanced-bus.js` से चलता है (Node 19+ में `CustomEvent` और `EventTarget` global हैं, और browser में भी वही API हैं)। इसमें एक typed event bus है जो `EventTarget` पर बना है। Handler errors catch होते हैं ताकि एक खराब listener पूरे bus को न तोड़े, `on()` unsubscribe function लौटाता है, और `once` option है।

```javascript
// advanced-bus.js: EventTarget + CustomEvent par bana production-style event bus
'use strict';                                                   // strict mode: galti par error

class EventBus {                                                // ek chhota event bus class
  #target = new EventTarget();                                  // andar ka EventTarget (DOM ka base)

  // Event bhejo: name aur payload (detail)
  emit(type, detail = {}) {
    if (typeof type !== 'string' || type.length === 0) {        // naam valid hai ya nahin
      throw new TypeError('event type must be a non-empty string'); // galat naam par clear error
    }
    const evt = new CustomEvent(type, { detail, cancelable: true }); // payload ke saath event banao
    const notPrevented = this.#target.dispatchEvent(evt);       // dispatch karo; false = kisi ne preventDefault kiya
    return notPrevented;                                        // caller ko batao
  }

  // Subscribe karo. Ek unsubscribe function wapas milta hai
  on(type, handler, { once = false } = {}) {                    // handler aur options
    if (typeof handler !== 'function') {                        // handler function hai?
      throw new TypeError(`handler for "${type}" must be a function`); // nahin to error
    }
    const wrapper = (evt) => {                                  // wrapper: errors catch karne ke liye
      try {
        handler(evt.detail, evt);                               // asli handler ko detail do
      } catch (err) {                                           // handler fail hua
        console.error(`[bus] handler for "${type}" failed: ${err.message}`); // log karo, bus nahin tootega
      }
    };
    this.#target.addEventListener(type, wrapper, { once });     // EventTarget par subscribe
    return () => this.#target.removeEventListener(type, wrapper); // unsubscribe function
  }
}

// ---- Demo ----
const bus = new EventBus();                                     // bus banao

const offBadge = bus.on('cart:add', (d) => {                    // header badge listener
  console.log('Badge update ->', d.count);
});
bus.on('cart:add', (d) => {                                     // analytics listener
  console.log('Analytics ->', d.itemId);
});
bus.on('order:place', () => {                                   // ek handler jo fail hota hai
  throw new Error('payment gateway down');                      // jaan-boojh kar error
});
bus.on('order:place', () => console.log('Order placed, email bhej diya')); // dusra listener chalega

bus.emit('cart:add', { itemId: 'p1', count: 1 });              // dono listeners chalenge
bus.emit('order:place', { orderId: 'o9' });                     // error log hoga, dusra listener fir bhi chalega

offBadge();                                                     // badge listener hata do
bus.emit('cart:add', { itemId: 'p2', count: 2 });               // ab sirf analytics chalega

try {
  bus.emit('', {});                                             // galat naam
} catch (err) {
  console.log('Caught:', err.name, '-', err.message);          // TypeError pakda
}
```

Is code ka expected output (node advanced-bus.js):
```
Badge update -> 1
Analytics -> p1
[bus] handler for "order:place" failed: payment gateway down
Order placed, email bhej diya
Analytics -> p2
Caught: TypeError - event type must be a non-empty string
```

---

## 🧠 Express.js Integration
Custom events browser में चलते हैं, Express में नहीं। Express का रोल यहाँ है server-side घटनाएँ भेजना। Server-Sent Events (SSE) से Express बदलाव को `event: cart:add` के नाम से भेजता है। Browser का `EventSource` उसे पाकर `CustomEvent` में बदलकर पेज पर `dispatchEvent` करता है। इससे दूसरे tab या device पर हुए बदलाव भी उसी event नाम से पेज के components तक पहुँचते हैं।

```javascript
// server.js: Express SSE endpoint + cart API jo custom event jaisa broadcast karta hai
const express = require('express');                    // Express framework
const app = express();                                 // Express app
const PORT = process.env.PORT || 3000;                 // port

app.use(express.json());                               // JSON body parse
app.use(express.static('public'));                     // public/index.html serve karo

const clients = new Set();                             // jitne browser tabs SSE se judde hain

// Browser EventSource('/events') is route se judta hai
app.get('/events', (req, res) => {                     // SSE connection
  res.set({                                            // SSE ke headers
    'Content-Type': 'text/event-stream',               // yeh stream hai
    'Cache-Control': 'no-cache',                       // cache nahin
    'Connection': 'keep-alive',                        // connection khula rakho
  });
  res.flushHeaders();                                  // headers turant bhejo
  clients.add(res);                                    // is client ko list mein daalo
  req.on('close', () => clients.delete(res));          // disconnect par list se hatao
});

// Ek named event sabhi connected clients ko bhejo
function broadcast(eventName, data) {                  // helper
  for (const client of clients) {                      // har client par
    client.write(`event: ${eventName}\n`);             // event ka naam
    client.write(`data: ${JSON.stringify(data)}\n\n`); // payload (JSON), blank line = message end
  }
}

// Cart API: server par cart update, phir sabhi tabs ko "cart:add" bhejo
app.post('/api/cart', (req, res) => {                  // cart mein item jodna
  const { itemId, name } = req.body;                   // body se data
  if (!itemId) return res.status(400).json({ error: 'itemId required' }); // validation
  broadcast('cart:add', { id: itemId, name });         // sabhi tabs ko announce karo
  res.status(201).json({ ok: true });                  // 201 Created
});

app.listen(PORT, () => {                               // server start
  console.log(`Server running at http://localhost:${PORT}`);
});

// Browser side (public/index.html mein):
// const es = new EventSource('/events');                                  // SSE se judo
// es.addEventListener('cart:add', (msg) => {                              // server event suno
//   const detail = JSON.parse(msg.data);                                  // JSON padho
//   document.dispatchEvent(new CustomEvent('cart:add', { detail, bubbles: true })); // page par failaao
// });
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `bubbles: true` भूल जाना और parent पर listener को उम्मीद करना।
✅ Correct: Custom event default में bubble नहीं करता। Parent या document तक जाने के लिए `bubbles: true` दो।

```javascript
// Wrong: bubbles default false, document tak nahin pahunchega
btn.dispatchEvent(new CustomEvent('cart:add', { detail: { id: 'p1' } }));
document.addEventListener('cart:add', () => console.log('never runs'));

// Right: bubbles true
btn.dispatchEvent(new CustomEvent('cart:add', { detail: { id: 'p1' }, bubbles: true }));
document.addEventListener('cart:add', () => console.log('runs now'));
```

❌ Mistake 2: Payload को `detail` के बजाय सीधे options में देना।
✅ Correct: Custom data हमेशा `detail` में जाता है। बाकी keys ignore हो जाती हैं।

```javascript
// Wrong: id ignored, event.id undefined hoga
const evt = new CustomEvent('cart:add', { id: 'p1' });

// Right: data detail mein
const evt2 = new CustomEvent('cart:add', { detail: { id: 'p1' } });
console.log(evt2.detail.id); // 'p1'
```

❌ Mistake 3: `new Event()` से `detail` भेजना।
✅ Correct: सादा `Event` में `detail` property नहीं होती। Payload के लिए `CustomEvent` इस्तेमाल करो।

```javascript
// Wrong: Event mein detail support nahin hai
const e = new Event('cart:add', { detail: { id: 'p1' } });
console.log(e.detail); // undefined

// Right: CustomEvent
const e2 = new CustomEvent('cart:add', { detail: { id: 'p1' } });
console.log(e2.detail); // { id: 'p1' }
```

---

## 🧠 Tricky Interview Question
नीचे Node.js में `EventTarget` पर दो listeners हैं। दोनों events भेजे गए हैं। Output क्या होगा?

```javascript
const target = new EventTarget();                              // ek event target
target.addEventListener('ping', (e) => {                       // listener A
  console.log('A', e.detail);
});
target.addEventListener('ping', (e) => {                       // listener B
  e.preventDefault();                                          // default rokne ki koshish
  console.log('B', e.detail);
});

// Pehla event: cancelable nahin
const r1 = target.dispatchEvent(new CustomEvent('ping', { detail: 1 }));
// Doosra event: cancelable true
const r2 = target.dispatchEvent(new CustomEvent('ping', { detail: 2, cancelable: true }));

console.log(r1, r2);                                           // dispatchEvent ke return values
```

Answer: Output hoga:
```
A 1
B 1
A 2
B 2
true false
```
- पहला event `cancelable` नहीं था, इसलिए `preventDefault()` का कोई असर नहीं हुआ। इसलिए `dispatchEvent` का return `true` रहा।
- दूसरा event `cancelable: true` था। Listener B ने `preventDefault()` call किया, इसलिए `dispatchEvent` `false` लौटाता है।
- दोनों listeners हर event पर चलते हैं। `preventDefault` दूसरे listeners को नहीं रोकता।
- Custom event का data `detail` में ही मिलता है, जो 1 और 2 है।
(इसे node में चलाकर verify किया गया है।)

---

## ⚫ Interview Questions + Answers

Q1: Custom event कैसे बनाते और भेजते हैं?
A1: `new CustomEvent(name, { detail, bubbles, cancelable })` से event बनाते हैं और `target.dispatchEvent(event)` से भेजते हैं।

Q2: `CustomEvent` और `Event` में क्या फ़र्क है?
A2: `CustomEvent` में `detail` property होती है जिसमें आप कोई भी data रख सकते हैं। सादा `Event` में `detail` नहीं होता।

Q3: `dispatchEvent` का return value क्या बताता है?
A3: यह `false` तब होता है जब event `cancelable` था और किसी listener ने `preventDefault()` call किया। बाकी मामलों में `true`।

Q4: Custom events को `on`/`off` जैसे pattern में कैसे सुरक्षित रखते हैं?
A4: `addEventListener` का wrapper लिखो जो errors catch करे, और `removeEventListener` के लिए वही reference रखो। `once` या `AbortController` के `signal` से भी listener हटाया जा सकता है।

Q5: Custom events का नाम कैसा रखना चाहिए?
A5: Namespace के साथ, जैसे `cart:add`, `payment:success`। इससे built-in events (click, change) से टकराव नहीं होता और कोड पढ़ने में आसान रहता है।

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Components को एक-दूसरे से loosely coupled रखना है (publisher नहीं जानता कौन सुन रहा है)
- Domain की घटना announce करनी है, जैसे "cart बदला", "login हुआ"
- Web Components या micro-frontends के बीच communication करनी है
- एक ही घटना पर कई अलग काम चलाने हैं

❌ Avoid when:
- सीधा function call ही साफ़ और आसान है (एक ही file, एक ही caller)
- Data flow इतना जटिल है कि event chain पढ़ना मुश्किल हो (debugging कठिन होती है)
- बड़े state को बार-बार भेजना है। ऐसे में state store (जैसे Redux, Zustand) बेहतर है
- Server के बीच communication: उसके लिए SSE, WebSocket या message queue देखो

---

## 📊 Visual Diagram
```
  Product button (publisher)
     │
     │ new CustomEvent('cart:add', { detail, bubbles: true })
     │ button.dispatchEvent(evt)
     ▼
  ┌────────────────────────────────────────────┐
  │ DOM bubble path: button → div → body → document │
  └────────────────────────────────────────────┘
     │                 │                 │
     ▼                 ▼                 ▼
  Header badge     Mini-cart        Analytics
  (listens on      (listens on      (listens on
   document)        document)        document)
     │
     └─ each reads event.detail ─> { id, name }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `CustomEvent` | अपने नाम और payload वाला event | अपना event |
| `detail` | CustomEvent में data रखने की property | Data का डिब्बा |
| `dispatchEvent()` | Event को target पर भेजना | Event भेजना |
| `bubbles` | Event parents तक जाए या नहीं | ऊपर जाए या नहीं |
| `cancelable` | Event की default action रोकी जा सके | रोकने योग्य |
| `EventTarget` | वह object जिस पर listeners लग सकते हैं | Listener का आधार |
| SSE (Server-Sent Events) | Server से browser को एक तरफ़ा stream | Server से लगातार संदेश |

---

## ⚡ 3-Line Summary
English: A custom event is created with `new CustomEvent(name, { detail })` and sent with `dispatchEvent()`.
Listeners read `event.detail`, and `bubbles: true` lets it reach parents; `dispatchEvent` returns `false` only when a cancelable event was prevented.
Use it to decouple components, with namespaced names like `cart:add`.

Hindi: Custom event `new CustomEvent(name, { detail })` से बनता है और `dispatchEvent()` से भेजा जाता है।
Listeners `event.detail` पढ़ते हैं, `bubbles: true` से event parents तक जाता है, और `dispatchEvent` `false` तभी लौटाता है जब cancelable event रोका गया हो।
इसे components को अलग रखने के लिए इस्तेमाल करो, और नाम `cart:add` जैसे namespace के साथ रखो।

---

## ➡️ Next Topic
150. Mouse Events + Keyboard Events (हिंदी: Mouse Events और Keyboard Events)। अब जब आप अपने events बना सकते हैं, तो अगला topic browser के असली user input events को समझाता है, यानी mouse, pointer और keyboard से आने वाले events, उनके properties और सही इस्तेमाल।
