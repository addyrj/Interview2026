# 58. RBAC — Role Based Access Control
# हिंदी में: RBAC — यूज़र्स को roles (admin, manager, customer) दो, और हर role को permissions दो; यूज़र वही कर सकता है जो उसके role को अनुमति है

---

## 🔵 Simple Definition (English)
**RBAC (Role-Based Access Control)** is an authorization model where **permissions are assigned to roles**, and **roles are assigned to users**. Instead of granting "user 42 can delete orders" directly, you say "role **Manager** has `order:delete`" and "user 42 is a Manager".
Related models: **ABAC** (attribute-based rules), **ReBAC** (relationship-based, like Google Docs sharing), **ACLs** (per-object lists).

## 🔵 सरल परिभाषा (Hindi)
RBAC में permissions सीधे यूज़र को नहीं, role को दी जाती हैं (जैसे Manager को "order delete" करने की अनुमति), और यूज़र को role दिया जाता है।
इससे हज़ारों यूज़र्स की अनुमतियाँ संभालना आसान हो जाता है — role बदलो, सबकी अनुमति बदल जाती है।

---

## 🔴 Problem it Solves
**Authentication** says who you are; **authorization** decides what you can do. Without a model:
- Permission checks are **scattered** (`if user.email === 'boss@x.com'`), inconsistent and buggy.
- Managing permissions **per user** for 10,000 employees is impossible.
- Onboarding and offboarding are error-prone; audits ("who can refund?") are hard.
- Missing checks → **Broken Access Control**, the **#1 risk in the OWASP Top 10 (2021)**.

RBAC gives a **central, auditable, scalable** way to manage access.

## 🔴 यह क्यों बना? (Hindi)
बिना ढाँचे के permission checks कोड में बिखरे होते हैं, हर यूज़र की अनुमति अलग से संभालना नामुमकिन है, और कहीं check छूटा तो कोई भी कुछ भी कर सकता है (OWASP की नंबर 1 समस्या)।
RBAC एक केंद्रीय, जाँचने लायक और स्केल होने वाला तरीका देता है।

---

## 🟢 How it Works — Step by Step

### The model

```
 Users ──(many-to-many)── Roles ──(many-to-many)── Permissions
   Aditya ────────────────► Admin ───────────────► user:*, order:*, refund:create
   Riya   ────────────────► Support ─────────────► order:read, refund:create (≤ ₹500)
   Karan  ────────────────► Restaurant Owner ────► menu:update (own), order:read (own)
   Neha   ────────────────► Customer ────────────► order:create, order:read (own)

Permission = resource + action:   order:read, order:cancel, menu:update, report:export
```

### Database schema

```
users(id, ...)
roles(id, name)                         'admin', 'support', 'restaurant_owner', 'customer'
permissions(id, key)                    'order:read', 'order:cancel', 'refund:create'
role_permissions(role_id, permission_id)
user_roles(user_id, role_id, scope_type, scope_id)   ← scoping: role WITHIN a tenant/restaurant
```

### Request authorization flow

```
Request: POST /restaurants/42/menu-items   (user 77)
  1. Authenticate → user 77
  2. Load roles/permissions (cache in Redis or put in JWT claims)
  3. Check permission "menu:update"           → RBAC (does any of my roles have it?)
  4. Check SCOPE/OWNERSHIP: is user 77 owner of restaurant 42?   → resource-level check
  5. Allow → proceed / Deny → 403 Forbidden
```

### RBAC alone isn't enough — ownership & scope

```
"Customer can read orders" → but only THEIR orders!
"Restaurant owner can update menu" → only THEIR restaurant!
Missing ownership checks = IDOR (Insecure Direct Object Reference):
   GET /api/orders/9002  (belongs to someone else) → returns it ❌
Always: WHERE id = $1 AND user_id = $2   (or check after fetch)
```

### RBAC vs ABAC vs ReBAC

```
┌──────────┬────────────────────────────────────────┬──────────────────────────────────────┐
│ Model    │ Decision based on                      │ Example                              │
├──────────┼────────────────────────────────────────┼──────────────────────────────────────┤
│ RBAC     │ user's roles → permissions             │ "Managers can approve leave"         │
│ ABAC     │ attributes of user, resource, action,  │ "Support can refund if amount ≤ 500  │
│          │ environment (time, IP, region)         │ AND order.city == agent.city"        │
│ ReBAC    │ relationships graph                    │ "Can view doc if editor of the folder│
│          │ (Google Zanzibar, OpenFGA, SpiceDB)    │ containing it" (Google Drive)        │
│ ACL      │ list of who can do what per object     │ file permissions, S3 object ACLs     │
└──────────┴────────────────────────────────────────┴──────────────────────────────────────┘
In practice: RBAC for coarse permissions + ownership checks + a few ABAC rules.
```

### Design principles

```
✓ Deny by default — explicit allow only
✓ Least privilege — give the minimum needed
✓ Check on the SERVER for every request (UI hiding is just UX)
✓ Centralize: one authorize() function / policy layer, not ad-hoc ifs
✓ Separation of duties — the person who creates a payout can't approve it
✓ Audit log of permission changes and sensitive actions
✓ Role explosion warning: 300 roles = unmanageable → use permissions + scopes/attributes
```

### Where permissions live at runtime
```
Option A: in the JWT ("role": "support", "perms": [...])  → fast, but stale until token expires
Option B: lookup per request (cache in Redis, invalidate on change) → fresh, small overhead
Option C: policy engine (OPA, Cerbos, Casbin, OpenFGA) → externalized policies, consistent across services
```

## 🟢 कैसे काम करता है? (Hindi)
1. Permissions बनाओ (`order:read`, `menu:update`), उन्हें roles में डालो, और roles यूज़र्स को दो।
2. हर request पर: यूज़र पहचानो → उसके roles/permissions देखो → ज़रूरी permission है या नहीं जाँचो।
3. सिर्फ़ role काफ़ी नहीं — ownership भी जाँचो (ग्राहक सिर्फ़ अपने orders, मालिक सिर्फ़ अपना रेस्टोरेंट), वरना IDOR bug।
4. Default में मना (deny), सिर्फ़ ज़रूरी अनुमति दो (least privilege), और check हमेशा सर्वर पर।
5. जटिल नियम (जैसे ₹500 तक refund) के लिए ABAC; Google Docs जैसी sharing के लिए ReBAC।

---

## 🟡 Real World Example

**AWS IAM** — policies (permissions) attached to roles, users and groups, with conditions (ABAC: tags, IP, MFA). EC2 instances "assume a role" instead of storing keys.

**Zomato/Swiggy partner apps** — restaurant owners, managers and staff have different roles scoped to their own restaurant. Support agents can issue refunds up to a limit, with higher amounts escalating to supervisors (RBAC + ABAC).

**Google Zanzibar** — Google's global authorization system (Drive, YouTube, Calendar) is relationship-based (ReBAC). It inspired open-source OpenFGA, SpiceDB and Permify.

**IDOR bugs in real apps** — many bug bounties (including at Indian startups) were simply changing `/orders/123` to `/orders/124` and seeing another customer's address and phone number. RBAC said "customer can read orders", but there was no ownership check.

## 🟡 Real Example Hindi में
AWS IAM में roles और policies होती हैं; EC2 मशीन keys की जगह role लेती है। Zomato partner ऐप में मालिक, मैनेजर, स्टाफ़ के अलग roles, सिर्फ़ अपने रेस्टोरेंट तक सीमित; support एक सीमा तक ही refund कर सकता है।
कई ऐप्स में `/orders/123` को `/orders/124` करते ही दूसरे ग्राहक का पता दिख जाता था — role था, पर ownership check नहीं था।

---

## 🟠 My Stack Example

### Schema (Postgres)
```sql
CREATE TABLE roles (id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE permissions (id SERIAL PRIMARY KEY, key TEXT UNIQUE NOT NULL);
CREATE TABLE role_permissions (role_id INT REFERENCES roles, permission_id INT REFERENCES permissions, PRIMARY KEY (role_id, permission_id));
CREATE TABLE user_roles (
  user_id BIGINT REFERENCES users, role_id INT REFERENCES roles,
  scope_type TEXT NOT NULL DEFAULT 'global',     -- 'global' | 'restaurant' | 'org'
  scope_id BIGINT,                               -- e.g. restaurant id
  PRIMARY KEY (user_id, role_id, scope_type, scope_id)
);
```

### Node.js — central authorization middleware
```js
// load & cache permissions per user (invalidate on role change)
async function getPermissions(userId) {
  const key = `perms:${userId}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);
  const { rows } = await pool.query(`
    SELECT p.key, ur.scope_type, ur.scope_id
    FROM user_roles ur JOIN role_permissions rp ON rp.role_id = ur.role_id
    JOIN permissions p ON p.id = rp.permission_id WHERE ur.user_id = $1`, [userId]);
  await redis.set(key, JSON.stringify(rows), { EX: 300 });
  return rows;
}

// can(user, 'menu:update', { type: 'restaurant', id: 42 })
async function can(userId, perm, scope) {
  const perms = await getPermissions(userId);
  return perms.some((p) => p.key === perm &&
    (p.scope_type === 'global' || (scope && p.scope_type === scope.type && String(p.scope_id) === String(scope.id))));
}

const authorize = (perm, scopeFn) => async (req, res, next) =>
  (await can(req.user.id, perm, scopeFn?.(req))) ? next() : res.status(403).json({ error: 'FORBIDDEN' });

app.put('/api/v1/restaurants/:rid/menu-items/:id', authenticate,
  authorize('menu:update', (req) => ({ type: 'restaurant', id: req.params.rid })),
  updateMenuItem);

// ownership check (customer reads ONLY own order) — enforce in the query
app.get('/api/v1/orders/:id', authenticate, async (req, res) => {
  const isStaff = await can(req.user.id, 'order:read:any');
  const { rows: [o] } = await pool.query(
    isStaff ? 'SELECT * FROM orders WHERE id=$1' : 'SELECT * FROM orders WHERE id=$1 AND user_id=$2',
    isStaff ? [req.params.id] : [req.params.id, req.user.id]);
  if (!o) return res.status(404).end();          // 404, not 403 → don't reveal existence
  res.json(o);
});
```

### ABAC rule example (refund limit)
```js
async function canRefund(agent, order, amount) {
  if (await can(agent.id, 'refund:create:unlimited')) return true;
  return (await can(agent.id, 'refund:create')) && amount <= 500 && order.city_id === agent.city_id;
}
```

### FastAPI — dependency-based permissions
```python
def require(perm: str):
    async def checker(user = Depends(current_user)):
        if perm not in await get_permissions(user["id"]):
            raise HTTPException(status_code=403, detail="FORBIDDEN")
        return user
    return checker

@app.post("/refunds")
async def create_refund(body: RefundIn, user = Depends(require("refund:create"))):
    ...
```

### Policy engine option (Casbin)
```
# model.conf
[request_definition] r = sub, obj, act
[policy_definition]  p = sub, obj, act
[role_definition]    g = _, _
[matchers]           m = g(r.sub, p.sub) && keyMatch2(r.obj, p.obj) && r.act == p.act
# policy.csv
p, admin, /api/*, *
p, support, /api/orders/:id, GET
g, user:77, support
```

### Frontend (Next.js / React Native) — UX only, server still enforces
```tsx
const { data: me } = useQuery({ queryKey: ['me'], queryFn: getMe });   // includes permissions[]
const canEditMenu = me?.permissions.includes('menu:update');
{canEditMenu && <Button onPress={openEditor}>Edit menu</Button>}
// Next.js middleware can redirect non-admins from /admin, but API routes MUST check again.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is RBAC and why use it?**
A1: An authorization model where permissions (resource:action) are grouped into roles, and users get roles. It simplifies management (change a role and every holder updates), supports least privilege and separation of duties, makes audits easy ("who has refund:create?"), and centralizes authorization logic instead of scattering ad-hoc checks.

**Q2: What's the difference between authentication and authorization?**
A2: Authentication verifies identity: who are you (password, OTP, OIDC, passkey)? It fails with 401. Authorization decides what an authenticated identity may do: may this user cancel this order? It fails with 403. RBAC, ABAC and ReBAC are authorization models.

**Q3: What is IDOR and how does RBAC relate to it?**
A3: Insecure Direct Object Reference: an endpoint uses an ID from the request (`/orders/124`) without checking that the user is allowed to access that specific object, so users can read or modify others' data by changing IDs. RBAC answers "can customers read orders?" but not "is this their order?". Prevent IDOR with ownership or scope checks on every resource access, ideally in the query itself (`WHERE id=? AND user_id=?`), plus non-guessable IDs as defence in depth.

**Q4: RBAC vs ABAC vs ReBAC — when to use which?**
A4: RBAC for clear, stable job functions with coarse permissions (admin, support, customer). It's simple and auditable, but gets "role explosion" for fine-grained rules. ABAC for rules depending on attributes and context (amount ≤ 500, same region, working hours, device trust). It's flexible but harder to audit. ReBAC for permissions derived from relationships and hierarchies (documents in shared folders, org trees, social sharing), as in Google Zanzibar or OpenFGA. Real systems often combine RBAC with ownership and some ABAC conditions.

**Q5: Should you put roles/permissions inside the JWT?**
A5: Putting the role, or a small set of permissions, in the JWT avoids per-request lookups and works well for coarse checks. But claims become stale until the token expires, so a revoked admin keeps access for up to 15 minutes, and tokens grow large with many permissions. Use short token lifetimes, keep fine-grained or frequently changing permissions in a cached lookup (Redis with invalidation on change), and always perform resource-level ownership checks server-side.

---

## 🔷 Trade-offs
✅ Advantages:
- Simple mental model, easy admin and audit, scalable to many users, least privilege.

❌ Disadvantages:
- Role explosion for fine-grained or contextual rules.
- Doesn't handle ownership/relationships by itself (need extra checks or ReBAC).
- Permissions in tokens can be stale; caches need invalidation.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Authorization | Deciding what user can do | अनुमति तय करना |
| Role | Named set of permissions | अनुमतियों का समूह |
| Permission | Allowed action on resource | किसी काम की अनुमति |
| Least privilege | Minimum necessary access | कम से कम ज़रूरी अनुमति |
| IDOR | Accessing others' objects by ID | ID बदलकर दूसरे का डेटा |
| ABAC | Attribute-based access control | गुणों पर आधारित अनुमति |
| ReBAC | Relationship-based access control | रिश्तों पर आधारित अनुमति |
| Scope | Context where role applies (tenant) | role कहाँ लागू है |
| Policy engine | Central rule evaluator (OPA, Casbin) | नियम जाँचने वाला इंजन |
| Separation of duties | Split critical tasks between people | ज़रूरी काम अलग लोगों में |

---

## ⚡ 3-Line Summary
**English:**
1. RBAC: users → roles → permissions (resource:action); deny by default, least privilege, enforce on the server.
2. Always add ownership/scope checks (prevent IDOR); use ABAC for contextual rules, ReBAC for sharing hierarchies.
3. Centralize checks (middleware/policy engine), cache permissions with invalidation, audit sensitive actions.

**Hindi:**
1. RBAC: यूज़र → role → permissions; default में मना, कम से कम अनुमति, check सर्वर पर।
2. हमेशा ownership/scope जाँचो (IDOR रोको); संदर्भ वाले नियम के लिए ABAC, sharing के लिए ReBAC।
3. Checks एक जगह रखो, permissions cache करो, ज़रूरी कामों का audit log रखो।

---

## ➡️ Next Topic Suggestion
**59. Rate Limiting** — Even authorized users (and bots) can overload your API. Next: why and where to rate limit, the key algorithms at a glance, 429 responses, and a distributed limiter with Redis.
