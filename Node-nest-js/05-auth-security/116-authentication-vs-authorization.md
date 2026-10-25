# 116. Authentication vs Authorization
# हिंदी में: Authentication vs Authorization — फर्क समझो

---

## 🔵 Simple Definition (English)
**Authentication (AuthN)** verifies WHO you are (login with email/password, OTP, biometric). **Authorization (AuthZ)** determines WHAT you're allowed to do once identified (can you access this resource? can you perform this action?). Authentication always happens first; authorization depends on the result of authentication.

## 🔵 सरल परिभाषा (Hindi)
**Authentication (AuthN)** verify करता है कि तुम कौन हो (email/password, OTP, biometric से login)। **Authorization (AuthZ)** तय करता है कि identify होने के बाद तुम क्या कर सकते हो (क्या तुम इस resource को access कर सकते हो? क्या तुम ये action कर सकते हो?)। Authentication हमेशा पहले होता है; authorization authentication के result पर depend करता है।

---

## 🔴 Problem it Solves
Without this separation, systems conflate "proving identity" with "checking permissions," leading to bugs where a logged-in user (authenticated) is wrongly allowed to perform actions beyond their role (e.g., a regular customer accessing an admin panel just because they're logged in). Separating AuthN (identity verification) from AuthZ (permission checking) as distinct layers lets you build flexible systems where identity is established once (login) but permissions can be checked repeatedly and differently per resource/action (RBAC, ABAC) without re-verifying identity each time.

## 🔴 यह क्यों बना? (Hindi)
इस separation के बिना, systems "identity prove करना" और "permissions check करना" को मिला देते हैं, जिससे bugs आते हैं जहाँ logged-in user (authenticated) को role से बाहर actions करने दिया जाता है (जैसे एक regular customer admin panel access कर ले सिर्फ इसलिए कि वो logged-in है)। AuthN (identity verification) को AuthZ (permission checking) से अलग, distinct layers के रूप में रखने से flexible systems बनाए जा सकते हैं जहाँ identity एक बार establish होती है (login) लेकिन permissions हर resource/action के लिए repeatedly और अलग-अलग check हो सकती हैं (RBAC, ABAC) identity को बार-बार verify किए बिना।

---

## 🟢 How it Works — Step by Step

Step 1 → **Authentication**: user submits credentials (email+password, OTP, social login) → server verifies them against stored data (hashed password comparison, OTP match) → issues a token/session proving identity (JWT or session cookie).
Step 2 → Every subsequent request carries this proof of identity (`Authorization: Bearer <token>` or session cookie).
Step 3 → **Authorization**: server extracts the identity from the token/session (e.g., `userId`, `role`) via an `authenticate` middleware.
Step 4 → A separate `authorize(...)` middleware checks if THIS identified user's role/permissions allow the requested action on the requested resource.
Step 5 → If authorized, the request proceeds to the business logic; if not, a `403 Forbidden` is returned (distinct from `401 Unauthorized`, which means authentication itself failed/missing).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Authentication**: user credentials submit करता है (email+password, OTP, social login) → server stored data के against verify करता है (hashed password comparison, OTP match) → identity proof करने वाला token/session issue करता है (JWT या session cookie)।
Step 2 → हर बाद की request इस identity proof को carry करती है (`Authorization: Bearer <token>` या session cookie)।
Step 3 → **Authorization**: server token/session से identity extract करता है (जैसे `userId`, `role`) एक `authenticate` middleware से।
Step 4 → एक अलग `authorize(...)` middleware check करता है कि क्या इस identified user का role/permissions requested resource पर requested action allow करते हैं।
Step 5 → Authorized होने पर, request business logic तक पहुंचती है; नहीं तो `403 Forbidden` return होता है (`401 Unauthorized` से अलग, जिसका मतलब है authentication खुद fail/missing हुई)।

---

## 🟡 Real World Example
**Swiggy Delivery Partner App vs Customer App:** Both use the SAME authentication system (phone number + OTP) — a delivery partner and a customer both successfully "log in" (authenticate) the same way. But AUTHORIZATION differs completely: a customer's token lets them view restaurant menus, place orders, and view THEIR OWN order history (`GET /orders/:id` checks `order.userId === req.user.id`). A delivery partner's token (same JWT structure, different `role: 'delivery_partner'` claim) lets them view assigned orders, mark deliveries complete, but NOT access another partner's earnings data or a customer's saved payment methods. Authentication proved who each person is; authorization decides what each can touch.

## 🟡 Real Example Hindi mein
**Swiggy Delivery Partner App vs Customer App:** दोनों SAME authentication system use करते हैं (phone number + OTP) — एक delivery partner और एक customer दोनों successfully "log in" (authenticate) same way से करते हैं। लेकिन AUTHORIZATION पूरी तरह अलग है: customer का token उन्हें restaurant menus देखने, orders place करने, और सिर्फ उनकी OWN order history देखने देता है (`GET /orders/:id` check करता है `order.userId === req.user.id`)। Delivery partner का token (same JWT structure, अलग `role: 'delivery_partner'` claim) उन्हें assigned orders देखने, deliveries complete mark करने देता है, लेकिन दूसरे partner का earnings data या customer का saved payment method access नहीं करने देता। Authentication ने prove किया कि हर व्यक्ति कौन है; authorization decide करता है कि हर कोई क्या touch कर सकता है।

---

## 💻 Code Example — Basic

```javascript
// authn-authz-basic.js
const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());
const JWT_SECRET = 'secret-key';

// ─── AUTHENTICATION: verify WHO the user is ────────────────────────────────────
function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1]; // extract Bearer token

  if (!token) {
    return res.status(401).json({ error: 'Authentication required' }); // 401 = not even logged in
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET); // verify signature + extract claims
    req.user = decoded; // attach identity to the request
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

// ─── AUTHORIZATION: check WHAT this identified user can do ───────────────────
function authorize(...allowedRoles) {
  return (req, res, next) => {
    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden: insufficient permissions' }); // 403 = identified but not allowed
    }
    next();
  };
}

// Login route — issues a JWT after verifying credentials (authentication)
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  // Mock credential check (real app: DB lookup + bcrypt.compare)
  if (username === 'rahul' && password === 'pass123') {
    const token = jwt.sign({ userId: '1', role: 'customer' }, JWT_SECRET, { expiresIn: '1h' });
    return res.json({ token });
  }
  res.status(401).json({ error: 'Invalid credentials' });
});

// Protected + role-restricted route
app.get('/admin/reports', authenticate, authorize('admin'), (req, res) => {
  res.json({ report: 'Sensitive admin data' });
});

app.listen(3000, () => console.log('Server on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// authn-authz-advanced.js — Resource-level authorization (not just role-based)
const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());
const JWT_SECRET = process.env.JWT_SECRET || 'secret-key';

// Mock database of orders
const orders = [
  { id: 'o1', userId: 'u1', total: 450 },
  { id: 'o2', userId: 'u2', total: 320 },
];

// ─── AUTHENTICATION MIDDLEWARE ─────────────────────────────────────────────────
function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token provided' });

  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

// ─── ROLE-BASED AUTHORIZATION (coarse-grained) ────────────────────────────────
function authorizeRole(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Role not permitted' });
    }
    next();
  };
}

// ─── RESOURCE-LEVEL (OWNERSHIP) AUTHORIZATION (fine-grained) ──────────────────
// A customer should only access THEIR OWN order, not just any order
function authorizeOrderOwnership(req, res, next) {
  const order = orders.find((o) => o.id === req.params.orderId);
  if (!order) return res.status(404).json({ error: 'Order not found' });

  // Admins can access any order; customers only their own
  if (req.user.role === 'admin' || order.userId === req.user.userId) {
    req.order = order; // attach for the route handler to use
    return next();
  }

  res.status(403).json({ error: 'You do not have access to this order' });
}

app.post('/login', (req, res) => {
  const { userId, role } = req.body; // simplified for demo
  const token = jwt.sign({ userId, role }, JWT_SECRET, { expiresIn: '1h' });
  res.json({ token });
});

// Customer can view only their own order; admin can view any
app.get('/orders/:orderId', authenticate, authorizeOrderOwnership, (req, res) => {
  res.json({ order: req.order });
});

// Only admins can access the reports endpoint — coarse role check
app.get('/admin/reports', authenticate, authorizeRole('admin'), (req, res) => {
  res.json({ allOrders: orders });
});

app.listen(3000, () => console.log('Advanced authN/authZ server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Login required' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid session' });
  }
};

const authorize = (...roles) => (req, res, next) =>
  roles.includes(req.user.role) ? next() : res.status(403).json({ error: 'Access denied' });

const router = express.Router();

router.get('/dashboard', authenticate, (req, res) => res.json({ user: req.user })); // any logged-in user
router.delete('/users/:id', authenticate, authorize('admin'), (req, res) => {
  res.json({ message: `User ${req.params.id} deleted` }); // admin-only action
});

app.use('/api', router);
app.listen(4000, () => console.log('App running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Returning `401` when the real problem is insufficient permissions (should be `403`)
✅ Correct: `401 Unauthorized` means "you are not authenticated at all" (missing/invalid token); `403 Forbidden` means "you ARE authenticated, but not allowed to do this." Mixing these confuses API consumers about whether to re-login or simply can't access the resource.

```javascript
// Wrong — user IS authenticated, just lacks the role; should be 403 not 401
if (req.user.role !== 'admin') return res.status(401).json({ error: 'Not allowed' });

// Right
if (req.user.role !== 'admin') return res.status(403).json({ error: 'Not allowed' });
```

❌ Mistake 2: Only checking role-based authorization, forgetting resource-level (ownership) checks
✅ Correct: A valid "customer" role check alone doesn't stop Customer A from viewing Customer B's order if the route only checks `role === 'customer'` without verifying `order.userId === req.user.userId` — this is an IDOR (Insecure Direct Object Reference) vulnerability.

```javascript
// Wrong — any customer can view ANY order by just changing the ID in the URL
app.get('/orders/:id', authenticate, authorizeRole('customer'), (req, res) => {
  res.json(orders.find(o => o.id === req.params.id)); // no ownership check!
});

// Right — verify the order actually belongs to the requesting user
app.get('/orders/:id', authenticate, authorizeRole('customer'), (req, res) => {
  const order = orders.find(o => o.id === req.params.id);
  if (order.userId !== req.user.userId) return res.status(403).json({ error: 'Forbidden' });
  res.json(order);
});
```

---

## 🧠 Tricky Interview Question

```javascript
app.get('/profile', authenticate, (req, res) => {
  res.json({ user: req.user });
});
// No authorize() middleware applied at all — just authenticate
```
Is this route "unauthorized" in a security sense? What's missing?

Answer: Technically nothing is "broken" — this route only requires that the user be AUTHENTICATED (logged in with a valid token), and it returns the identified user's OWN profile data (presumably derived from `req.user`, their own identity). There's no authorization GAP here because the route doesn't need role/permission distinctions — "view your own profile" is inherently self-scoped by `req.user`. The trick is recognizing that not every protected route needs an explicit `authorize()` middleware — some routes are correctly protected by authentication alone when the data returned is already scoped to the authenticated identity (`req.user.id`), with no cross-user access possible. Authorization middleware becomes necessary specifically when an action could affect OTHER users' data or restricted admin-level resources.

---

## ⚫ Interview Questions + Answers

Q1: What's a concrete example of authentication succeeding but authorization failing?
A1: A regular customer logs into Flipkart with correct email/password (authentication SUCCEEDS — they're a verified, real user) and receives a valid JWT. They then try to access `GET /admin/seller-payouts` (an admin-only endpoint). The server verifies their JWT is valid (authentication passes), extracts their role (`customer`), but the authorization check (`role !== 'admin'`) fails, returning `403 Forbidden`. They proved who they are; they're just not allowed to do this specific thing.

Q2: Why is HTTP status code `401` specifically named "Unauthorized" when it actually relates to authentication, not authorization?
A2: This is a well-known historical naming inconsistency in the HTTP spec (RFC 7235) — `401 Unauthorized` really means "you need to authenticate" (missing/invalid credentials), and `403 Forbidden` means "you're authenticated but not authorized for this." Despite the confusing name, the convention is universally followed: use 401 for missing/invalid auth, 403 for valid auth but insufficient permission.

Q3: What's the difference between Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC)?
A3: **RBAC** assigns permissions based on a user's ROLE (admin, customer, vendor) — simple, works well for coarse-grained permission tiers. **ABAC** grants/denies access based on arbitrary ATTRIBUTES of the user, resource, and context (e.g., "allow if user.department === resource.department AND time is between 9am-6pm AND user.clearanceLevel >= resource.sensitivityLevel") — far more flexible/granular but more complex to implement and reason about. Many real systems use a hybrid: RBAC for broad access tiers, with ABAC-like ownership checks (resource-level authorization) layered on top.

Q4: Can authorization checks happen without authentication having occurred first?
A4: No — authorization is meaningless without a known identity to check permissions against. Authorization middleware (`authorize(...)`) always relies on `req.user` (or equivalent) having already been populated by an earlier authentication step. If authentication is skipped or fails, there's no valid identity to evaluate authorization rules against, which is why `authenticate` middleware must always run BEFORE `authorize` middleware in the chain.

Q5: How do multi-factor authentication (MFA) and authorization interact?
A5: MFA strengthens the AUTHENTICATION step (requiring a second factor like OTP/biometric in addition to password) — it increases confidence that the claimed identity is genuinely who they say they are. It doesn't change authorization logic at all — once MFA-authenticated, the SAME role/permission checks apply as they would with single-factor auth. Some systems do use MFA status as an authorization ATTRIBUTE though (e.g., "allow high-value transactions only if the session was MFA-verified within the last 15 minutes"), blending the two concepts for extra-sensitive actions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any app with more than one user type/role, or any resource that shouldn't be universally accessible to all logged-in users
- APIs exposing sensitive actions (admin panels, financial transactions, user management)
- Multi-tenant systems where users must only access their own organization's/account's data

❌ Avoid when:
- Never truly "avoid" this distinction — even simple apps benefit from clearly separating "who are you" from "what can you do" logic, even if authorization is as simple as "any authenticated user can do everything" for an MVP

---

## 📊 Visual Diagram
```
AUTHENTICATION vs AUTHORIZATION:

  ┌─────────────┐        ┌──────────────────┐        ┌─────────────────┐
  │   LOGIN      │──────▶│  AUTHENTICATION   │──────▶│  AUTHORIZATION   │
  │ (credentials)│        │  "Who are you?"   │        │ "What can you do?"│
  └─────────────┘        └──────────────────┘        └─────────────────┘
                                 │                            │
                          verify password/OTP          check role/ownership
                          issue JWT/session             against requested
                                 │                       resource/action
                                 ▼                            │
                          401 if fails                  403 if fails
                       (not authenticated)          (authenticated, not allowed)
                                                             │
                                                             ▼
                                                      200 OK — proceed

EXAMPLE:
  Customer logs in ──▶ AuthN: ✅ valid JWT issued
  Customer requests /admin/reports ──▶ AuthZ: ❌ role='customer' != 'admin' ──▶ 403
  Customer requests /my-orders ──▶ AuthZ: ✅ own data, role sufficient ──▶ 200
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Authentication (AuthN) | Verifying identity | Identity verify करना |
| Authorization (AuthZ) | Checking permissions | Permissions check करना |
| 401 Unauthorized | Not authenticated | Authenticated नहीं |
| 403 Forbidden | Authenticated but not allowed | Authenticated पर allowed नहीं |
| RBAC | Role-Based Access Control | Role के आधार पर access |
| IDOR | Insecure Direct Object Reference | असुरक्षित direct object reference |
| Ownership check | Verifying resource belongs to requester | Resource requester का ही है, verify करना |

---

## ⚡ 3-Line Summary
English:
1. Authentication verifies WHO you are (login); authorization determines WHAT you can do (permissions) — authentication always happens first.
2. Use `401` for missing/invalid authentication and `403` for valid authentication but insufficient authorization.
3. Role-based checks alone aren't enough — always add resource-level ownership checks to prevent one user accessing another's data (IDOR).

Hindi:
1. Authentication verify करता है कि तुम कौन हो (login); authorization तय करता है कि तुम क्या कर सकते हो (permissions) — authentication हमेशा पहले होता है।
2. Missing/invalid authentication के लिए `401` और valid authentication पर insufficient authorization के लिए `403` use करो।
3. सिर्फ role-based checks काफी नहीं — हमेशा resource-level ownership checks जोड़ो ताकि एक user दूसरे का data access न कर सके (IDOR)।

---

## ➡️ Next Topic
**117. JWT (JSON Web Token)** — Stateless token-based authentication mechanism and its structure।
