# 174. RESTful Routes Convention
# हिंदी में: RESTful Routes Convention — Standard Route Naming Pattern

---

## 🔵 Simple Definition (English)
**RESTful routes convention** is the standard mapping of 7 common actions (index, show, create, update, destroy, new, edit) to specific URL + HTTP method combinations for any resource. Following this convention consistently across ALL resources in an app makes the entire API predictable — once you know the pattern for `/users`, you automatically know it for `/products`, `/orders`, etc.

## 🔵 सरल परिभाषा (Hindi)
**RESTful routes convention** 7 common actions (index, show, create, update, destroy, new, edit) को specific URL + HTTP method combinations में map करने का standard तरीका है। किसी भी app में सारे resources पर इसे consistently follow करने से पूरा API predictable बन जाता है — एक बार `/users` का pattern समझ लिया, तो `/products`, `/orders` के लिए भी automatically पता चल जाता है।

---

## 🔴 Problem it Solves
Without a fixed convention, every developer on a team invents their own route names:
```
Developer A: GET /fetchAllUsers, POST /addUser, POST /removeUser/:id
Developer B: GET /userList, POST /user/new, DELETE /user/remove/:id
Developer C: GET /users/all, POST /users/add, GET /users/delete/:id (!! using GET to delete)
```
This creates chaos: inconsistent naming across the codebase, URLs that don't match HTTP semantics (`GET` used for deletion is dangerous — browsers/crawlers/caches may trigger it accidentally), and a steep learning curve for new team members or API consumers. The RESTful routes convention fixes this by giving every resource THE SAME 7-action blueprint.

## 🔴 यह क्यों बना? (Hindi)
Fixed convention के बिना, team का हर developer अपने route names बनाता है:
```
Developer A: GET /fetchAllUsers, POST /addUser, POST /removeUser/:id
Developer B: GET /userList, POST /user/new, DELETE /user/remove/:id
Developer C: GET /users/all, POST /users/add, GET /users/delete/:id (!! GET से delete)
```
यह chaos बनाता है: codebase में inconsistent naming, HTTP semantics से mismatch (जैसे `GET` से delete करना dangerous है — browsers/crawlers accidentally trigger कर सकते हैं), और नए team members/API consumers के लिए सीखना मुश्किल। RESTful routes convention हर resource को SAME 7-action blueprint देकर यह fix करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **index**: `GET /products` → list all products.
Step 2 → **show**: `GET /products/:id` → show one specific product.
Step 3 → **create**: `POST /products` → create a new product (body contains data).
Step 4 → **update**: `PUT /products/:id` (full) or `PATCH /products/:id` (partial) → modify a product.
Step 5 → **destroy**: `DELETE /products/:id` → delete a product. (The `new`/`edit` actions, which render HTML forms, are mostly relevant to server-rendered apps like Rails, not JSON APIs — pure REST JSON APIs usually only need these 5.)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **index**: `GET /products` → सारे products list करना।
Step 2 → **show**: `GET /products/:id` → एक specific product दिखाना।
Step 3 → **create**: `POST /products` → नया product बनाना (body में data)।
Step 4 → **update**: `PUT /products/:id` (full) या `PATCH /products/:id` (partial) → product modify करना।
Step 5 → **destroy**: `DELETE /products/:id` → product delete करना। (`new`/`edit` actions, जो HTML forms render करते हैं, मुख्यतः server-rendered apps जैसे Rails के लिए relevant हैं, JSON APIs के लिए नहीं — pure REST JSON APIs को सिर्फ ऊपर वाले 5 चाहिए होते हैं।)

---

## 🟡 Real World Example
**Swiggy's restaurant management API** follows this exact 5-route pattern for EVERY resource:
```
GET    /restaurants           (index — list restaurants)
GET    /restaurants/:id       (show — one restaurant)
POST   /restaurants           (create — new restaurant onboarding)
PATCH  /restaurants/:id       (update — change hours, menu link)
DELETE /restaurants/:id       (destroy — deactivate restaurant)

GET    /restaurants/:id/menu-items       (index — nested resource)
POST   /restaurants/:id/menu-items       (create — add menu item)
PATCH  /menu-items/:id                   (update a specific item)
DELETE /menu-items/:id                   (destroy a specific item)
```
Any engineer joining the team instantly knows how to find/add/modify ANY resource without reading custom documentation for each one.

## 🟡 Real Example Hindi mein
**Swiggy का restaurant management API** हर resource के लिए यही exact 5-route pattern follow करता है:
```
GET    /restaurants           (index — restaurants list)
GET    /restaurants/:id       (show — एक restaurant)
POST   /restaurants           (create — नया restaurant onboard)
PATCH  /restaurants/:id       (update — hours, menu link बदलना)
DELETE /restaurants/:id       (destroy — restaurant deactivate)

GET    /restaurants/:id/menu-items       (index — nested resource)
POST   /restaurants/:id/menu-items       (create — menu item add)
PATCH  /menu-items/:id                   (एक item update)
DELETE /menu-items/:id                   (एक item destroy)
```
कोई भी नया engineer बिना custom documentation पढ़े instantly जान जाता है कि किसी भी resource को कैसे find/add/modify करना है।

---

## 💻 Code Example — Basic

```javascript
// basic-restful-routes.js
// Install: npm install express

const express = require('express');
const router = express.Router();

let restaurants = [{ id: 1, name: 'Spice Hub', city: 'Bangalore' }];

// INDEX: GET /restaurants
router.get('/restaurants', (req, res) => {
  res.status(200).json({ data: restaurants });
});

// SHOW: GET /restaurants/:id
router.get('/restaurants/:id', (req, res) => {
  const r = restaurants.find(x => x.id === Number(req.params.id));
  if (!r) return res.status(404).json({ error: 'Not found' });
  res.status(200).json({ data: r });
});

// CREATE: POST /restaurants
router.post('/restaurants', express.json(), (req, res) => {
  const newR = { id: restaurants.length + 1, ...req.body };
  restaurants.push(newR);
  res.status(201).json({ data: newR });
});

// UPDATE: PATCH /restaurants/:id
router.patch('/restaurants/:id', express.json(), (req, res) => {
  const r = restaurants.find(x => x.id === Number(req.params.id));
  if (!r) return res.status(404).json({ error: 'Not found' });
  Object.assign(r, req.body);
  res.status(200).json({ data: r });
});

// DESTROY: DELETE /restaurants/:id
router.delete('/restaurants/:id', (req, res) => {
  restaurants = restaurants.filter(x => x.id !== Number(req.params.id));
  res.status(204).send();
});

module.exports = router;
```

## 💻 Code Example — Advanced

```javascript
// advanced-restful-routes.js — generic RESTful router factory for any Mongoose model

const express = require('express');

// Reusable function that generates the 5 standard RESTful routes for ANY model
function createRestfulRouter(Model) {
  const router = express.Router();

  // INDEX with pagination
  router.get('/', async (req, res, next) => {
    try {
      const { page = 1, limit = 20 } = req.query;
      const items = await Model.find()
        .skip((page - 1) * limit)
        .limit(Number(limit));
      const total = await Model.countDocuments();
      res.status(200).json({ data: items, meta: { page: Number(page), limit: Number(limit), total } });
    } catch (err) { next(err); }
  });

  // SHOW
  router.get('/:id', async (req, res, next) => {
    try {
      const item = await Model.findById(req.params.id);
      if (!item) return res.status(404).json({ error: 'Not found' });
      res.status(200).json({ data: item });
    } catch (err) { next(err); }
  });

  // CREATE
  router.post('/', async (req, res, next) => {
    try {
      const item = await Model.create(req.body);
      res.status(201).location(`${req.baseUrl}/${item.id}`).json({ data: item });
    } catch (err) { next(err); }
  });

  // UPDATE (partial)
  router.patch('/:id', async (req, res, next) => {
    try {
      const item = await Model.findByIdAndUpdate(req.params.id, req.body, {
        new: true, runValidators: true,
      });
      if (!item) return res.status(404).json({ error: 'Not found' });
      res.status(200).json({ data: item });
    } catch (err) { next(err); }
  });

  // DESTROY
  router.delete('/:id', async (req, res, next) => {
    try {
      const item = await Model.findByIdAndDelete(req.params.id);
      if (!item) return res.status(404).json({ error: 'Not found' });
      res.status(204).send();
    } catch (err) { next(err); }
  });

  return router;
}

module.exports = { createRestfulRouter };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { createRestfulRouter } = require('./advanced-restful-routes');
const Restaurant = require('./models/Restaurant');
const MenuItem = require('./models/MenuItem');

const app = express();
app.use(express.json());

// One factory function generates consistent RESTful routes for EVERY resource
app.use('/api/v1/restaurants', createRestfulRouter(Restaurant));
app.use('/api/v1/menu-items', createRestfulRouter(MenuItem));

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using GET requests to perform destructive actions
✅ Correct: Never use GET for anything that modifies data — it breaks caching assumptions and is dangerous (prefetchers/crawlers can trigger it).

```javascript
// Wrong
router.get('/products/delete/:id', ...); // GET deleting data!

// Right
router.delete('/products/:id', ...);
```

❌ Mistake 2: Mixing singular and plural resource names inconsistently
✅ Correct: Pick plural nouns consistently for collections (`/users`, `/products`) across the whole API.

```javascript
// Wrong (inconsistent)
app.get('/user', ...);       // singular here
app.get('/products', ...);   // plural here

// Right
app.get('/users', ...);
app.get('/products', ...);
```

---

## 🧠 Tricky Interview Question

```javascript
// You have: GET /users/:id/posts/:postId/comments
// A client requests GET /users/5/posts/999/comments, but post 999 belongs to user 7, not user 5.
// What should the API return, and why?
```
Answer: It should return **404 Not Found** (treating the combination as "not found" in this scope), NOT the comments of post 999. The route implies a scoping relationship — comments must belong to a post that belongs to the specified user. The handler must explicitly verify `post.userId === req.params.id` before returning data; otherwise it's an authorization/data-leak bug (returning data that doesn't match the claimed hierarchy, or worse, leaking another user's data).

---

## ⚫ Interview Questions + Answers

Q1: What are the 7 traditional RESTful actions (as popularized by Rails)?
A1: index (list), show (single item), new (render create form — HTML apps only), create (POST to save), edit (render update form — HTML apps only), update (PUT/PATCH to save changes), destroy (DELETE). JSON APIs typically implement only index, show, create, update, destroy since "new" and "edit" are about rendering HTML forms, which a JSON API's frontend (React/Vue) handles client-side.

Q2: How do you represent a resource's sub-action that isn't a plain CRUD operation, e.g., "mark order as delivered"?
A2: Model it either as an update to the resource's state (`PATCH /orders/:id` with `{status: 'DELIVERED'}`) or as a nested action resource (`POST /orders/:id/deliveries`, treating "delivery" as a created record/event). The second is better when the action itself needs its own metadata (timestamp, delivered-by, location) and audit trail.

Q3: Should route parameter names match the resource name, e.g., `:userId` vs generic `:id`?
A3: For nested routes, using descriptive names like `:userId` and `:postId` (rather than reusing generic `:id` for both) avoids ambiguity and makes middleware/handler code clearer, especially in deeply nested routes (`/users/:userId/posts/:postId/comments/:commentId`).

Q4: Why is `PUT /products` (without an ID) generally invalid?
A4: PUT replaces a SPECIFIC resource at a known URI — it requires an identifier (`/products/5`). `PUT /products` (the collection, no ID) is ambiguous: should it replace the ENTIRE collection? Some APIs do support this for bulk-replace semantics, but it's non-standard and should be used carefully/documented explicitly if implemented.

Q5: How do you keep nested routes from getting too deep (e.g., `/a/:id/b/:id/c/:id/d/:id`)?
A5: Best practice caps nesting at 1-2 levels. Beyond that, "promote" deeper resources to top-level with a filter query param instead: e.g., instead of `/users/:id/posts/:id/comments/:id/likes`, use `/likes?commentId=X`. This keeps URLs manageable and avoids coupling deeply unrelated resources into one URL chain.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Designing any CRUD-centric HTTP API — applies uniformly to all resources.
- You want a generator/factory pattern (as shown above) to reduce boilerplate across many resources.

❌ Avoid when:
- An action genuinely doesn't map to CRUD at all (e.g., complex business workflows, batch jobs) — model those as explicit action endpoints rather than forcing them into index/show/create/update/destroy.

---

## 📊 Visual Diagram
```
RESTFUL ROUTES BLUEPRINT (applies to EVERY resource):
──────────────────────────────────────────────────────
  Action    HTTP Method   URL                 Purpose
  ──────    ───────────   ──────────────────  ────────────────────
  index     GET           /products           list all
  show      GET           /products/:id       get one
  create    POST          /products           create new
  update    PATCH/PUT     /products/:id       modify existing
  destroy   DELETE        /products/:id       remove
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | List all resources | सारे resources list |
| Show | Get a single resource | एक resource get |
| Create | Add a new resource | नया resource add |
| Update | Modify a resource | Resource modify |
| Destroy | Delete a resource | Resource delete |
| Nested route | Sub-resource under parent | Parent के अंदर sub-resource |

---

## ⚡ 3-Line Summary
English:
1. The RESTful routes convention maps index/show/create/update/destroy to GET/GET/POST/PATCH-PUT/DELETE consistently.
2. Following this blueprint for every resource makes the whole API predictable and reduces per-resource documentation needs.
3. Keep nesting shallow (1-2 levels) and always verify ownership/scoping on nested routes to avoid data leaks.

Hindi:
1. RESTful routes convention index/show/create/update/destroy को GET/GET/POST/PATCH-PUT/DELETE में consistently map करता है।
2. हर resource के लिए इस blueprint को follow करने से पूरा API predictable बनता है और documentation की ज़रूरत कम होती है।
3. Nesting shallow रखो (1-2 levels) और nested routes पर हमेशा ownership/scoping verify करो data leak से बचने के लिए।

---

## ➡️ Next Topic
**175. API Versioning (/api/v1/)** — API को बिना breaking changes के evolve करने की strategy।
