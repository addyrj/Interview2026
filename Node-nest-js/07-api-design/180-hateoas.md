# 180. HATEOAS
# हिंदी में: HATEOAS — Hypermedia As The Engine Of Application State

---

## 🔵 Simple Definition (English)
**HATEOAS** is a REST design principle where API responses include **hyperlinks** to related actions/resources (`_links`), so clients can discover what they can do NEXT just by following links in the response — instead of hardcoding every URL structure into the client beforehand. It's the "clicking links on a webpage" idea, applied to APIs.

## 🔵 सरल परिभाषा (Hindi)
**HATEOAS** एक REST design principle है जहाँ API responses में **hyperlinks** (`_links`) शामिल होते हैं related actions/resources के लिए, ताकि clients response में links follow करके जान सकें कि आगे क्या कर सकते हैं — बिना हर URL structure client में पहले से hardcode किये। यह "webpage पर links click करना" वाला idea है, APIs पर applied।

---

## 🔴 Problem it Solves
Without HATEOAS, clients must hardcode knowledge of EVERY possible URL/transition:
```
Client code: "to cancel an order, hit DELETE /orders/{id}/cancel"
Client code: "to view invoice, hit GET /orders/{id}/invoice"
```
If the backend changes a URL structure (e.g., moves cancel to a different path), EVERY client needs to update their hardcoded URLs. With HATEOAS, the server tells the client in the response WHAT actions are currently available and WHERE to find them:
```
GET /orders/5 → { ..., _links: { cancel: { href: '/orders/5/cancel', method: 'DELETE' }, invoice: {...} } }
```
If the order is already delivered, the server simply OMITS the "cancel" link — client UIs can hide the Cancel button automatically based on what links are present, without separately tracking business rules about when cancellation is allowed.

## 🔴 यह क्यों बना? (Hindi)
HATEOAS के बिना, clients को HAR possible URL/transition hardcode करनी पड़ती है:
```
Client code: "order cancel करने के लिए DELETE /orders/{id}/cancel hit करो"
Client code: "invoice देखने के लिए GET /orders/{id}/invoice hit करो"
```
अगर backend कोई URL structure बदल दे, HAR client को hardcoded URLs update करने पड़ेंगे। HATEOAS के साथ, server client को response में बता देता है कि अभी कौन से actions available हैं और कहाँ मिलेंगे:
```
GET /orders/5 → { ..., _links: { cancel: { href: '/orders/5/cancel', method: 'DELETE' }, invoice: {...} } }
```
अगर order delivered हो चुका है, server सिर्फ "cancel" link omit कर देता है — client UIs उसके according automatically Cancel button hide कर सकते हैं, business rules को separately track किये बिना।

---

## 🟢 How it Works — Step by Step

Step 1 → Every resource response includes a `_links` (or `links`) object alongside the data.
Step 2 → Each link has a `href` (URL) and often a `method` (HTTP verb) and `rel` (relationship name like "self," "cancel," "next").
Step 3 → The SET of links included is dynamic — determined by the resource's current state/business rules (e.g., only include "cancel" link if the order status allows cancellation).
Step 4 → Client-side code checks for the PRESENCE of a link rather than hardcoding a URL — `if (order._links.cancel) showCancelButton()`.
Step 5 → For collections, `_links` often include pagination navigation: `self`, `next`, `prev`, `first`, `last`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर resource response में data के साथ `_links` (या `links`) object होता है।
Step 2 → हर link में `href` (URL) और अक्सर `method` (HTTP verb) और `rel` (relationship name जैसे "self," "cancel," "next") होता है।
Step 3 → Included links का SET dynamic होता है — resource की current state/business rules से determine होता है (जैसे "cancel" link सिर्फ तब include करो जब order status cancellation allow करे)।
Step 4 → Client-side code URL hardcode करने की जगह link की PRESENCE check करता है — `if (order._links.cancel) showCancelButton()`।
Step 5 → Collections के लिए, `_links` में अक्सर pagination navigation होता है: `self`, `next`, `prev`, `first`, `last`।

---

## 🟡 Real World Example
**PayPal's REST API** is one of the most well-known real-world implementations of HATEOAS. A payment resource response includes `links` like `self`, `approve` (for the payer to approve), `execute` (to finalize), `capture`, `refund` — and WHICH of these appear depends on the payment's current state (e.g., `refund` only appears once a payment is already captured). This lets PayPal's client SDKs follow the links dynamically instead of each SDK team hardcoding payment-flow logic that could drift out of sync with backend changes.

## 🟡 Real Example Hindi mein
**PayPal का REST API** HATEOAS का एक well-known real-world implementation है। Payment resource response में `links` होते हैं जैसे `self`, `approve` (payer के approve करने के लिए), `execute` (finalize करने के लिए), `capture`, `refund` — और इनमें से कौन दिखेगा यह payment की current state पर depend करता है (जैसे `refund` सिर्फ तब दिखेगा जब payment पहले से captured हो)। यह PayPal के client SDKs को links dynamically follow करने देता है, ना कि हर SDK team अपना payment-flow logic hardcode करे जो backend changes से out of sync हो सकता है।

---

## 💻 Code Example — Basic

```javascript
// basic-hateoas.js
// Install: npm install express

const express = require('express');
const app = express();

let orders = [{ id: 1, status: 'PLACED', total: 1500 }];

app.get('/orders/:id', (req, res) => {
  const order = orders.find(o => o.id === Number(req.params.id));
  if (!order) return res.status(404).json({ success: false, error: 'Not found' });

  // Build links based on the order's CURRENT state
  const links = {
    self: { href: `/orders/${order.id}`, method: 'GET' }, // always present
  };

  if (order.status === 'PLACED') {
    // Can only cancel if not yet shipped
    links.cancel = { href: `/orders/${order.id}/cancel`, method: 'POST' };
  }
  if (order.status === 'DELIVERED') {
    // Can only request a refund after delivery
    links.refund = { href: `/orders/${order.id}/refund`, method: 'POST' };
  }

  res.json({ success: true, data: order, _links: links }); // links tell the client what's possible NOW
});

app.listen(3000);
```

## 💻 Code Example — Advanced

```javascript
// advanced-hateoas.js — collection-level links (pagination) + reusable link builder

const express = require('express');
const app = express();
const Order = require('./models/Order');

// Reusable function: builds links for a SINGLE order based on its state + permissions
function buildOrderLinks(order, req) {
  const base = `${req.protocol}://${req.get('host')}/api/v1/orders/${order.id}`;
  const links = { self: { href: base, method: 'GET' } };

  const allowedTransitions = {
    PLACED: ['cancel'],
    SHIPPED: ['track'],
    DELIVERED: ['refund', 'review'],
  };

  (allowedTransitions[order.status] || []).forEach((action) => {
    links[action] = { href: `${base}/${action}`, method: action === 'track' ? 'GET' : 'POST' };
  });

  return links;
}

app.get('/api/v1/orders', async (req, res, next) => {
  try {
    const page = Number(req.query.page) || 1;
    const limit = Number(req.query.limit) || 20;
    const [orders, total] = await Promise.all([
      Order.find().skip((page - 1) * limit).limit(limit),
      Order.countDocuments(),
    ]);

    const baseUrl = `${req.protocol}://${req.get('host')}/api/v1/orders`;
    const totalPages = Math.ceil(total / limit);

    res.json({
      success: true,
      data: orders.map(order => ({ ...order.toObject(), _links: buildOrderLinks(order, req) })),
      _links: {
        self: { href: `${baseUrl}?page=${page}&limit=${limit}` },
        next: page < totalPages ? { href: `${baseUrl}?page=${page + 1}&limit=${limit}` } : null,
        prev: page > 1 ? { href: `${baseUrl}?page=${page - 1}&limit=${limit}` } : null,
      },
      meta: { page, limit, total, totalPages },
    });
  } catch (err) {
    next(err);
  }
});

module.exports = app;
```

---

## 🟠 Express.js Integration

```javascript
// Action endpoints that the _links actually point to -- must enforce the SAME business rules
// that determined whether the link was shown in the first place
app.post('/api/v1/orders/:id/cancel', async (req, res, next) => {
  try {
    const order = await Order.findById(req.params.id);
    if (!order) return res.status(404).json({ success: false, error: 'Not found' });

    if (order.status !== 'PLACED') {
      // Defense in depth: even if a client somehow calls this without seeing the link, re-validate
      return res.status(409).json({ success: false, error: { code: 'CANNOT_CANCEL', message: 'Order already shipped' } });
    }

    order.status = 'CANCELLED';
    await order.save();
    res.json({ success: true, data: order, _links: buildOrderLinks(order, req) });
  } catch (err) {
    next(err);
  }
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Including a link for an action that's actually not allowed in the current state
✅ Correct: Links must reflect REAL current permissions/state — showing a "cancel" link for an already-delivered order is misleading and will cause a confusing error when clicked.

```javascript
// Wrong -- always includes cancel link regardless of state
links.cancel = { href: `/orders/${id}/cancel` };

// Right -- conditionally include based on actual business rules
if (order.status === 'PLACED') links.cancel = { href: `/orders/${id}/cancel` };
```

❌ Mistake 2: Relying ONLY on the presence of a link for security, without re-validating server-side
✅ Correct: Links are a UX/discoverability convenience, NOT a security boundary — always re-check permissions/state on the server when the linked action is actually invoked.

```javascript
// Wrong -- trusts that if the client is calling this, it must be allowed (no re-check)
app.post('/orders/:id/cancel', (req, res) => { /* just cancels, no status check */ });

// Right -- re-validates even though the link implied it should be allowed
app.post('/orders/:id/cancel', (req, res) => { if (order.status !== 'PLACED') return res.status(409)...; });
```

---

## 🧠 Tricky Interview Question

```javascript
// Does HATEOAS mean the client should hardcode NO URLs at all, not even the entry point?
```
Answer: Correct in the PURIST interpretation — true HATEOAS means the client only hardcodes ONE entry-point URL (e.g., the API root `/`), and discovers EVERY other URL by following links returned in responses, treating the API like a state machine navigated via hypermedia (similar to a human browsing a website by clicking links, never typing URLs directly). In practice, almost no production REST API implements this strictly — most "RESTful" APIs (including Razorpay, Stripe) use some HATEOAS-like link fields for discoverability/UX but still document and let clients rely on known URL patterns. Few real systems achieve "Level 3" of the Richardson Maturity Model (full HATEOAS).

---

## ⚫ Interview Questions + Answers

Q1: What problem does HATEOAS actually solve in practice, if most APIs don't fully implement it?
A1: Even partial HATEOAS (conditional action links based on state) is valuable for: (1) reducing client-side business logic duplication (client doesn't need to independently know "orders can only be cancelled while status=PLACED" — it just checks if the link exists), (2) decoupling URL structure from client hardcoding, letting backend change paths without breaking clients that follow links, (3) self-documenting APIs where the response itself reveals available next actions.

Q2: What is the Richardson Maturity Model, and where does HATEOAS fit?
A2: It's a model ranking REST API maturity in 4 levels: Level 0 (single URI, one HTTP method, essentially RPC-over-HTTP), Level 1 (multiple resource URIs), Level 2 (proper HTTP verbs + status codes — where MOST "RESTful" APIs sit today), Level 3 (HATEOAS — hypermedia-driven, fully discoverable). Most real-world APIs stop at Level 2; true Level 3 is rare because of the added complexity for marginal practical benefit in most use cases.

Q3: How does HATEOAS relate to API versioning?
A3: In theory, a fully HATEOAS-driven client is MORE resilient to backend changes because it follows links rather than hardcoding URLs — so some non-breaking structural changes don't require a new version at all. However, it doesn't eliminate the need for versioning entirely — changes to the DATA SHAPE within a resource, or removed/renamed fields, still require versioning regardless of how discoverable the URLs are.

Q4: What's a common format/standard for structuring HATEOAS links (`_links`)?
A4: **HAL (Hypertext Application Language)** is a popular convention: `_links` object with `rel` names as keys, each holding `{ href, method, title }`. Other standards include JSON:API's `links` object and Siren. These standardize HOW links are structured so generic client libraries can parse them without API-specific knowledge.

Q5: Does HATEOAS make an API harder or easier to test/consume for simple clients (e.g., a quick mobile app integration)?
A5: It can make SIMPLE, fixed-workflow clients slightly more complex initially (parsing/following links instead of just hitting known URLs), but it pays off for COMPLEX, evolving systems with many state-dependent actions (payment flows, order lifecycles) — where hardcoding every business rule client-side would be more error-prone and harder to keep in sync with backend logic changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Complex resource lifecycles with many state-dependent actions (payments, order workflows) where showing only valid "next steps" matters.
- Building a hypermedia-driven API intended for long-term evolvability with minimal client coupling to URL structure.

❌ Avoid when:
- Simple CRUD APIs with a small, fixed, well-documented set of endpoints — the overhead of full hypermedia isn't justified.
- Internal microservices where you control both client and server and can coordinate changes directly (no discoverability pressure).

---

## 📊 Visual Diagram
```
HATEOAS RESPONSE:
──────────────────────────────────────────────
GET /orders/5
{
  "data": { "id": 5, "status": "PLACED", "total": 1500 },
  "_links": {
    "self":   { "href": "/orders/5", "method": "GET" },
    "cancel": { "href": "/orders/5/cancel", "method": "POST" }   ← only present because status=PLACED
  }
}

If status were "DELIVERED" instead:
  "_links": {
    "self":   { "href": "/orders/5", "method": "GET" },
    "refund": { "href": "/orders/5/refund", "method": "POST" }   ← cancel link GONE, refund APPEARS
  }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HATEOAS | Hypermedia-driven API navigation | Hypermedia-driven API navigation |
| _links | Object holding related action URLs | Related action URLs का object |
| rel | Relationship name of a link | Link का relationship name |
| HAL | A standard format for hypermedia links | Hypermedia links का standard format |
| Richardson Maturity Model | REST maturity ranking (0-3) | REST maturity ranking |

---

## ⚡ 3-Line Summary
English:
1. HATEOAS embeds hyperlinks (`_links`) in API responses so clients discover available next actions dynamically, instead of hardcoding URLs.
2. Links should be conditionally included based on the resource's actual current state/permissions — and the server must still re-validate on the actual action endpoint.
3. Few real APIs implement full HATEOAS (Level 3 maturity); most stop at proper verbs/status codes (Level 2), using partial link-based hints where it adds real value.

Hindi:
1. HATEOAS API responses में hyperlinks (`_links`) embed करता है ताकि clients dynamically available next actions discover करें, URLs hardcode करने की जगह।
2. Links को resource की actual current state/permissions के आधार पर conditionally include करना चाहिए — और server को actual action endpoint पर भी फिर से validate करना चाहिए।
3. कम ही real APIs full HATEOAS (Level 3) implement करते हैं; ज्यादातर proper verbs/status codes (Level 2) पर रुकते हैं, जहाँ value हो वहाँ partial link-based hints use करते हैं।

---

## ➡️ Next Topic
**181. GraphQL with Node.js** — Flexible query language के साथ Node.js API बनाना, REST के alternative के रूप में।
