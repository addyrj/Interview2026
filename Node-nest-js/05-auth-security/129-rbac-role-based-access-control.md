# 129. RBAC — Role Based Access Control
# हिंदी में: RBAC — Role आधारित Access Control

---

## 🔵 Simple Definition (English)
**RBAC (Role-Based Access Control)** is an authorization model where permissions are assigned to **roles** (like `admin`, `editor`, `customer`), and users get access by being assigned one or more roles — not by giving permissions directly to each user. It answers: "What role does this user have, and what can that role do?"

## 🔵 सरल परिभाषा (Hindi)
**RBAC** एक authorization model है जहाँ permissions सीधे users को नहीं, बल्कि **roles** (जैसे `admin`, `editor`, `customer`) को assign होती हैं, और users को role assign करके access मिलती है। यह जवाब देता है: "इस user का role क्या है, और वो role क्या कर सकता है?"

---

## 🔴 Problem it Solves
Without RBAC, every API endpoint needs manual checks like `if (user.email === 'admin@zomato.com')` — hardcoded, unmanageable at scale. As an app grows (Zomato has customers, delivery partners, restaurant owners, support staff, admins), managing per-user permissions becomes impossible — thousands of users, each needing individual permission checks. RBAC solves this by grouping permissions into roles once, then just assigning roles to users. Adding a new admin = assign `admin` role, not writing new permission logic.

## 🔴 यह क्यों बना? (Hindi)
RBAC के बिना हर API endpoint में manual check लिखना पड़ता जैसे `if (user.email === 'admin@zomato.com')` — hardcoded और scale नहीं होता। App बढ़ने पर (Zomato में customers, delivery partners, restaurant owners, support staff, admins) per-user permissions manage करना impossible हो जाता है। RBAC permissions को roles में group करता है एक बार, फिर users को सिर्फ role assign करना होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define roles: `admin`, `restaurant_owner`, `delivery_partner`, `customer`
Step 2 → Define permissions per role: `admin` → [create, read, update, delete all], `restaurant_owner` → [manage own restaurant, view own orders], `customer` → [place order, view own orders]
Step 3 → Store role on the User model (e.g., `user.role = 'restaurant_owner'`) or many-to-many (user can have multiple roles)
Step 4 → On login, embed role in JWT payload: `{ userId, role: 'restaurant_owner' }`
Step 5 → Create middleware `authorize(['admin', 'restaurant_owner'])` that checks `req.user.role` against allowed list
Step 6 → Apply middleware to routes: `router.delete('/restaurant/:id', authenticate, authorize(['admin']), deleteRestaurant)`
Step 7 → If role not in allowed list → 403 Forbidden

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Roles define करो: `admin`, `restaurant_owner`, `delivery_partner`, `customer`
Step 2 → हर role के permissions define करो
Step 3 → User model पर role store करो
Step 4 → Login पर JWT में role embed करो
Step 5 → Middleware बनाओ जो `req.user.role` check करे
Step 6 → Routes पर middleware apply करो
Step 7 → Role allowed list में न हो तो 403 Forbidden दो

---

## 🟡 Real World Example
**Zomato's internal dashboard:** `admin` can ban any restaurant, `restaurant_owner` can only edit their own menu and view their own orders (not other restaurants'), `delivery_partner` can only update delivery status of orders assigned to them, `support_agent` can view (read-only) any order for troubleshooting but cannot delete anything. Each role has a fixed set of allowed actions — adding a new support agent is just `user.role = 'support_agent'`, no custom code needed.

## 🟡 Real Example Hindi mein
**Zomato का internal dashboard:** `admin` किसी भी restaurant को ban कर सकता है, `restaurant_owner` सिर्फ अपना menu edit कर सकता है और अपने orders देख सकता है, `delivery_partner` सिर्फ assigned orders का delivery status update कर सकता है, `support_agent` किसी भी order को read-only देख सकता है पर delete नहीं कर सकता।

---

## 💻 Code Example — Basic

```javascript
// rbac-basic.js
// Run with: node rbac-basic.js

// ─── 1. DEFINE ROLES AND THEIR PERMISSIONS ───────────────────────────────────
const ROLE_PERMISSIONS = {
  admin: ['create', 'read', 'update', 'delete'],          // full access
  restaurant_owner: ['create', 'read', 'update'],          // no delete
  delivery_partner: ['read', 'update_status'],             // limited
  customer: ['read', 'create_order'],                       // very limited
};

// ─── 2. SIMULATED USERS ───────────────────────────────────────────────────────
const users = [
  { id: 1, name: 'Rahul', role: 'admin' },
  { id: 2, name: 'Priya', role: 'restaurant_owner' },
  { id: 3, name: 'Amit', role: 'customer' },
];

// ─── 3. PERMISSION CHECK FUNCTION ─────────────────────────────────────────────
function hasPermission(user, action) {
  const permissions = ROLE_PERMISSIONS[user.role] || [];   // get role's permissions
  return permissions.includes(action);                     // check if action allowed
}

// ─── 4. TEST ───────────────────────────────────────────────────────────────────
console.log(hasPermission(users[0], 'delete'));        // true  (admin can delete)
console.log(hasPermission(users[1], 'delete'));        // false (owner cannot delete)
console.log(hasPermission(users[2], 'create_order'));  // true  (customer can order)
console.log(hasPermission(users[2], 'delete'));        // false (customer cannot delete)
```

## 💻 Code Example — Advanced

```javascript
// rbac-advanced.js — Hierarchical roles + resource-level ownership check

// ─── 1. ROLE HIERARCHY (higher role inherits lower role's permissions) ──────
const ROLE_HIERARCHY = {
  super_admin: ['admin'],              // super_admin includes everything admin has
  admin: ['restaurant_owner'],         // admin includes restaurant_owner perms
  restaurant_owner: ['delivery_partner'],
  delivery_partner: [],
  customer: [],
};

const BASE_PERMISSIONS = {
  super_admin: ['manage_billing', 'manage_admins'],
  admin: ['delete_restaurant', 'ban_user'],
  restaurant_owner: ['edit_menu', 'view_own_orders'],
  delivery_partner: ['update_delivery_status'],
  customer: ['place_order', 'view_own_orders'],
};

// Resolve all permissions for a role, including inherited ones (recursive)
function getAllPermissions(role, visited = new Set()) {
  if (visited.has(role)) return [];              // avoid infinite loop on cycles
  visited.add(role);

  let perms = [...(BASE_PERMISSIONS[role] || [])];
  const inherited = ROLE_HIERARCHY[role] || [];
  for (const parentRole of inherited) {
    perms = perms.concat(getAllPermissions(parentRole, visited));
  }
  return [...new Set(perms)];                    // dedupe
}

function hasPermission(role, permission) {
  return getAllPermissions(role).includes(permission);
}

// ─── 2. RESOURCE-LEVEL OWNERSHIP CHECK (RBAC + ownership) ────────────────────
// Even with role permission, restaurant_owner should only edit THEIR restaurant
async function canEditRestaurant(user, restaurantId, RestaurantModel) {
  // Step 1: role-level check
  if (!hasPermission(user.role, 'edit_menu')) {
    return { allowed: false, reason: 'Role does not have edit_menu permission' };
  }

  // admin can edit any restaurant (bypass ownership)
  if (user.role === 'admin' || user.role === 'super_admin') {
    return { allowed: true };
  }

  // restaurant_owner can only edit their own
  const restaurant = await RestaurantModel.findById(restaurantId);
  if (!restaurant) return { allowed: false, reason: 'Restaurant not found' };

  if (String(restaurant.ownerId) !== String(user.id)) {
    return { allowed: false, reason: 'Not the owner of this restaurant' };
  }

  return { allowed: true };
}

// ─── 3. EXPRESS AUTHORIZE MIDDLEWARE FACTORY ──────────────────────────────────
function authorize(...allowedRoles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    // Check if user's role (or any inherited role chain) matches allowed roles
    const userRole = req.user.role;
    if (!allowedRoles.includes(userRole)) {
      return res.status(403).json({ error: 'Forbidden: insufficient role' });
    }
    next();
  };
}

function requirePermission(permission) {
  return (req, res, next) => {
    if (!req.user) return res.status(401).json({ error: 'Not authenticated' });
    if (!hasPermission(req.user.role, permission)) {
      return res.status(403).json({ error: `Forbidden: missing permission '${permission}'` });
    }
    next();
  };
}

module.exports = { hasPermission, getAllPermissions, authorize, requirePermission, canEditRestaurant };
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const jwt = require('jsonwebtoken');
const { authorize, requirePermission, canEditRestaurant } = require('./rbac-advanced');

const app = express();
app.use(express.json());

// Authentication middleware: verify JWT and attach user (with role) to req
function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token provided' });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;   // { userId, role }
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

// Only admin can delete any restaurant
app.delete('/restaurants/:id', authenticate, authorize('admin', 'super_admin'), async (req, res) => {
  await Restaurant.findByIdAndDelete(req.params.id);
  res.json({ message: 'Restaurant deleted' });
});

// restaurant_owner (own restaurant) or admin can edit menu
app.put('/restaurants/:id/menu', authenticate, requirePermission('edit_menu'), async (req, res) => {
  const check = await canEditRestaurant(req.user, req.params.id, Restaurant);
  if (!check.allowed) {
    return res.status(403).json({ error: check.reason });
  }
  await Restaurant.findByIdAndUpdate(req.params.id, { menu: req.body.menu });
  res.json({ message: 'Menu updated' });
});

// Only customer role can place an order
app.post('/orders', authenticate, authorize('customer'), async (req, res) => {
  const order = await Order.create({ ...req.body, customerId: req.user.userId });
  res.status(201).json(order);
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Checking role in frontend only, not backend
```javascript
// WRONG: Hiding "Delete" button in UI is not security — API still accepts the request
// Frontend: if (user.role === 'admin') showDeleteButton();
// Backend route has no role check at all!

// Correct: ALWAYS enforce authorization server-side too
app.delete('/restaurants/:id', authenticate, authorize('admin'), deleteHandler);
```

❌ Mistake 2: Storing role as a free-text string without validation
```javascript
// Wrong: any string accepted, typos cause silent security holes
user.role = req.body.role;  // attacker sends role: 'admin ' (trailing space) → bypass!

// Right: validate against an enum/whitelist
const VALID_ROLES = ['admin', 'restaurant_owner', 'delivery_partner', 'customer'];
if (!VALID_ROLES.includes(req.body.role)) {
  throw new Error('Invalid role');
}
```

---

## 🧠 Tricky Interview Question

```javascript
// What is wrong with this authorize middleware?
function authorize(role) {
  return (req, res, next) => {
    if (req.user.role === role) {
      next();
    }
    // no else branch!
  };
}
app.delete('/admin/users/:id', authenticate, authorize('admin'), deleteUser);
```
Answer: If `req.user.role !== role`, the middleware calls neither `next()` nor sends a response — the request **hangs forever** (client waits until timeout). This is a classic Express middleware bug: every code path must either call `next()` or end the response (`res.send/json/status().end()`). Correct version must have an `else` that returns `res.status(403).json({ error: 'Forbidden' })`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Authentication and Authorization (RBAC)?
A1: Authentication answers "who are you?" (login, verifying identity via password/JWT). Authorization (RBAC) answers "what are you allowed to do?" (checking role/permissions after identity is confirmed). Authentication happens first (middleware like `authenticate`), authorization happens after (middleware like `authorize`). A user can be authenticated (valid JWT) but still unauthorized (role lacks permission) for a specific action.

Q2: How do you store roles — on the User document, or a separate junction table?
A2: Simple apps: store role directly as a string field on User (`user.role = 'admin'`) — fast, simple, works when a user has exactly one role. Complex apps needing multiple roles per user (e.g., a user is both `restaurant_owner` AND `delivery_partner`): use a many-to-many junction table (`user_roles`) linking users to roles, or store an array `user.roles = ['admin', 'support']`. SQL systems often use a `roles` table + `user_roles` pivot table for normalization and auditability.

Q3: Should role be included in the JWT payload?
A3: Yes, commonly — it avoids a DB lookup on every request just to check the role. Trade-off: if a user's role changes (e.g., demoted from admin), the old JWT still has the old role until it expires — this is why JWTs should have short expiry (15 min) with refresh tokens, or you maintain a token-blacklist/version check for immediate revocation when role changes.

Q4: How does RBAC differ from ABAC (Attribute-Based Access Control)?
A4: RBAC grants access based on a fixed role (`admin` can delete anything). ABAC grants access based on dynamic attributes/context (user department = requester's department, time of day, resource owner = requester, IP location). RBAC is simpler and faster to implement/audit but coarse-grained. ABAC is more flexible/fine-grained but more complex to reason about and test. Many real systems use RBAC for broad strokes + ABAC-style ownership checks (like `canEditRestaurant` above) for fine-grained rules — this hybrid is very common in production.

Q5: How do you handle a user with multiple roles in RBAC?
A5: Store `user.roles = ['restaurant_owner', 'delivery_partner']` (array). Permission check becomes: does ANY of the user's roles have this permission? `roles.some(role => hasPermission(role, action))`. In JWT, embed the array: `{ userId, roles: [...] }`. Middleware checks `req.user.roles.includes(requiredRole)` or checks permission union across all roles. Be careful: combining roles can create unintended permission combinations — audit the union carefully.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have a fixed, well-defined set of user types (admin, editor, viewer) with mostly static permissions.
- You need simple, auditable access control that's easy to explain to non-technical stakeholders.
- Enterprise apps, admin dashboards, SaaS platforms with tiered access.

❌ Avoid when:
- Permissions depend heavily on dynamic context (resource owner, time, location, department) — ABAC or a hybrid fits better.
- You have an extremely large number of fine-grained, per-resource permissions — RBAC role explosion becomes unmanageable (use ABAC/policy engines like OPA/Casbin instead).

---

## 📊 Visual Diagram

```
RBAC FLOW:
──────────────────────────────────────────────────────────

  User logs in
       │
       ▼
  JWT issued: { userId: 42, role: 'restaurant_owner' }
       │
       ▼
  Request: DELETE /restaurants/5
       │
       ▼
  authenticate middleware
    → verifies JWT → req.user = { userId: 42, role: 'restaurant_owner' }
       │
       ▼
  authorize(['admin']) middleware
    → req.user.role = 'restaurant_owner'
    → 'restaurant_owner' NOT in ['admin']
    → 403 Forbidden ❌
       │
  (if role WAS 'admin')
       ▼
  next() called → controller runs → restaurant deleted ✅

ROLE → PERMISSION MAPPING:
  admin             → [create, read, update, delete]
  restaurant_owner  → [create, read, update]        (own resources only)
  delivery_partner  → [read, update_status]
  customer          → [read, create_order]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Role | A named group of permissions | Permissions का named group |
| Permission | A specific allowed action | एक specific allowed action |
| Authorization | Checking what user can do | User क्या कर सकता है, check करना |
| Role hierarchy | Roles inheriting other roles' perms | Role का दूसरे role से inherit |
| Ownership check | Resource belongs to requester | Resource requester का ही है |
| 403 Forbidden | Authenticated but not allowed | Authenticated पर allowed नहीं |

---

## ⚡ 3-Line Summary
English:
1. RBAC assigns permissions to roles, then roles to users — avoiding per-user hardcoded permission logic.
2. Implement via an `authorize(['role1','role2'])` Express middleware checking `req.user.role` after authentication.
3. Combine RBAC with ownership/resource-level checks for real-world fine-grained security (role alone isn't always enough).

Hindi:
1. RBAC permissions को roles को assign करता है, फिर roles users को — per-user hardcoded logic से बचने के लिए।
2. `authorize(['role1','role2'])` middleware से implement करो जो authentication के बाद `req.user.role` check करे।
3. RBAC के साथ ownership check भी combine करो — सिर्फ role काफी नहीं होता real-world में।

---

## ➡️ Next Topic
**130. ABAC — Attribute Based Access Control** — Dynamic, context-aware authorization beyond fixed roles।
