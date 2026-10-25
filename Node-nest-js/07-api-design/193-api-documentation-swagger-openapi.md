# 193. API Documentation (Swagger/OpenAPI)
# हिंदी में: API Documentation (Swagger/OpenAPI)

---

## 🔵 Simple Definition (English)
**OpenAPI** (formerly called Swagger) is a standard specification format (YAML/JSON) for describing a REST API's endpoints, request/response shapes, auth, and error codes in a machine-readable way. **Swagger UI** then renders that spec into an interactive web page where developers can read the docs and even try out API calls directly from the browser.

## 🔵 सरल परिभाषा (Hindi)
**OpenAPI** (पहले Swagger कहलाता था) एक standard format (YAML/JSON) है जो REST API के endpoints, request/response shapes, auth, और error codes को machine-readable तरीके से describe करता है। **Swagger UI** उस spec को एक interactive web page में render करता है जहाँ developers docs पढ़ भी सकते हैं और browser से सीधे API call try भी कर सकते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM WITHOUT OPENAPI:
  API docs written manually in a Google Doc/Notion — goes out of date instantly
  Frontend devs guess request/response shapes, break things in production
  No single source of truth between backend code and documentation
  Can't auto-generate client SDKs or validate requests against a schema

OPENAPI SOLUTION:
  One spec file (openapi.yaml) describes EVERY endpoint precisely
  Swagger UI auto-generates interactive, always-accurate docs from it
  Can auto-generate TypeScript/client SDKs from the same spec
  Can validate incoming requests against the schema automatically
  Teams integrate it into CI — spec changes are reviewed like code
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: API docs manually लिखी जाती थीं, outdated हो जाती थीं
Frontend devs guess करते थे request/response shape — production में टूट जाता था
OpenAPI: एक spec file से हर endpoint describe होता है
Swagger UI उससे interactive docs auto-generate करता है
```

---

## 🟢 How it Works — Step by Step

Step 1 → Define your API in an `openapi.yaml`/`.json` file — paths, methods, parameters, request bodies, responses, schemas
Step 2 → OR generate it automatically from JSDoc comments above your route handlers using a library like `swagger-jsdoc`
Step 3 → Serve the spec through `swagger-ui-express` at a route like `/api-docs` — it renders an interactive page
Step 4 → Developers browse docs, see example requests/responses, and click "Try it out" to send real requests from the browser
Step 5 → CI tools can validate the spec itself, or validate real request/response payloads against it (contract testing)

## 🟢 कैसे काम करता है? (Hindi)
```
1. openapi.yaml में API describe करो — paths, methods, request/response schemas
2. या swagger-jsdoc से route handlers के ऊपर comments से auto-generate करो
3. swagger-ui-express से /api-docs पर serve करो
4. Developers interactive page पर docs देखें, "Try it out" से real request भेजें
5. CI में spec को validate भी कर सकते हैं
```

---

## 🟡 Real World Example
**Razorpay public payment API docs:** Razorpay exposes a huge public API (create order, capture payment, refund, etc.) that thousands of external merchant developers integrate with. They maintain an OpenAPI spec describing every endpoint, required fields, and error codes. This spec powers their public developer docs portal (interactive "try it" examples) AND is used internally to auto-generate official SDKs (Node.js, PHP, Python clients) — so the docs, the SDK, and the actual API are always in sync because they're generated from the same source of truth.

## 🟡 Real Example Hindi mein
**Razorpay public API docs:** हजारों external developers Razorpay API से integrate करते हैं। OpenAPI spec से हर endpoint describe होता है। यही spec public docs portal को power करता है और official SDKs (Node, PHP, Python) auto-generate करने में भी इस्तेमाल होता है — docs, SDK, और actual API हमेशा sync में रहते हैं।

---

## 💻 Code Example — Basic

```javascript
// server.js
// Run: npm install express swagger-ui-express yamljs   then  node server.js
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');

const app = express();

// Load the OpenAPI spec from a YAML file (written separately — see below)
const swaggerDocument = YAML.load('./openapi.yaml');

// Mount Swagger UI at /api-docs — renders the interactive documentation page
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// A simple real endpoint that the spec describes
app.get('/api/users/:id', (req, res) => {
  res.json({ id: req.params.id, name: 'Aditya' });
});

app.listen(3000, () => console.log('Docs at http://localhost:3000/api-docs'));
```

```yaml
# openapi.yaml — the spec file referenced above
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /api/users/{id}:
    get:
      summary: Get a user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                type: object
                properties:
                  id: { type: string }
                  name: { type: string }
        '404':
          description: User not found
```

## 💻 Code Example — Advanced

```javascript
// advanced-swagger-jsdoc.js
// Generates the OpenAPI spec DIRECTLY from JSDoc comments above routes,
// so docs stay next to the code instead of a separate hand-maintained file.
// Run: npm install express swagger-jsdoc swagger-ui-express
const express = require('express');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const app = express();
app.use(express.json());

// swagger-jsdoc options: tells it WHERE to scan for @openapi comments
const options = {
  definition: {
    openapi: '3.0.0',
    info: { title: 'Orders API', version: '1.0.0' },
    components: {
      securitySchemes: {
        bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
      },
    },
  },
  apis: ['./advanced-swagger-jsdoc.js'],  // files to scan for JSDoc annotations
};

const spec = swaggerJsdoc(options);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(spec));

/**
 * @openapi
 * /api/orders:
 *   post:
 *     summary: Create a new order
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [itemId, quantity]
 *             properties:
 *               itemId: { type: string }
 *               quantity: { type: integer, minimum: 1 }
 *     responses:
 *       201:
 *         description: Order created
 *       400:
 *         description: Invalid input
 */
app.post('/api/orders', (req, res) => {
  const { itemId, quantity } = req.body;
  // Validate before trusting input — spec documents this contract too
  if (!itemId || !quantity || quantity < 1) {
    return res.status(400).json({ error: 'Invalid order payload' });
  }
  res.status(201).json({ orderId: 'ord_123', itemId, quantity });
});

app.listen(3000, () => console.log('Docs at http://localhost:3000/api-docs'));
```

---

## 🟠 Express.js Integration

```javascript
// Full Express app wiring Swagger docs alongside versioned REST routes
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const swaggerJsdoc = require('swagger-jsdoc');

const app = express();
app.use(express.json());

const spec = swaggerJsdoc({
  definition: { openapi: '3.0.0', info: { title: 'Zomato-like API', version: '2.1.0' } },
  apis: ['./routes/*.js'],  // scan all route files for @openapi comments
});

// Serve raw JSON spec too — useful for client SDK generators / Postman import
app.get('/api-docs.json', (req, res) => res.json(spec));

// Serve interactive UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(spec));

const router = express.Router();
/**
 * @openapi
 * /api/restaurants/{id}/menu:
 *   get:
 *     summary: Get restaurant menu
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema: { type: string }
 *     responses:
 *       200:
 *         description: Menu list
 */
router.get('/api/restaurants/:id/menu', (req, res) => {
  res.json({ restaurantId: req.params.id, items: [] });
});

app.use(router);
app.listen(3000, () => console.log('API + docs running on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Letting the spec drift from actual code (manually maintained YAML that nobody updates after endpoint changes)
✅ Correct: Prefer `swagger-jsdoc` style generation co-located with route code, or contract-test the spec against real responses in CI.

```javascript
// Wrong — spec lives in a totally separate file nobody remembers to update
// openapi.yaml edited manually, months out of sync with routes.js

// Right — docs live as comments right above the route they describe
/**
 * @openapi
 * /api/users:
 *   get: ...
 */
app.get('/api/users', handler);
```

❌ Mistake 2: Exposing `/api-docs` (with "Try it out" live requests) on a production server without auth, letting anyone probe internal endpoints or fire real mutating requests.
✅ Correct: Disable Swagger UI in production, or gate it behind admin auth; serve it only in dev/staging.

❌ Mistake 3: Describing response schemas that don't match what the API actually returns (e.g., omitting error response schemas) — misleads API consumers.
✅ Correct: Document EVERY status code your endpoint can realistically return (200, 400, 401, 404, 500), not just the happy path.

---

## 🧠 Tricky Interview Question

**Question:** Your OpenAPI spec says a field `email` is `required: true` in the request body schema, but your Express handler doesn't actually validate it — a request without `email` still succeeds with a 201. Is this a documentation bug or a code bug?

Answer: **Both — but it's a serious code bug primarily.** The spec's `required: true` is a *contract promise* to every API consumer that your server WILL reject requests missing `email`. If the actual code doesn't enforce it, consumers (and auto-generated client validators) will build logic assuming the server validates it, while in reality malformed data silently gets through. In interviews, the key insight expected is: **OpenAPI documents an intended contract, but does NOT automatically enforce it** — unless you explicitly wire in request validation middleware (e.g., `express-openapi-validator`) that validates incoming requests against the same spec, the spec and the real behavior can diverge dangerously.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between Swagger and OpenAPI?
A1: "Swagger" was the original name of both the specification and the tooling. In 2015 the specification was donated to the Linux Foundation and renamed **OpenAPI Specification (OAS)**; "Swagger" now refers mainly to the tooling ecosystem (Swagger UI, Swagger Editor, swagger-jsdoc) that implements/consumes the OpenAPI spec. People still use the terms interchangeably in conversation.

Q2: How can you generate the OpenAPI spec without hand-writing a huge YAML file?
A2: Use `swagger-jsdoc`, which scans JSDoc-style `@openapi` comment blocks placed directly above route handlers and compiles them into a spec object — keeping documentation physically next to the code it describes, reducing drift. Alternatively, some frameworks (like NestJS with `@nestjs/swagger`) generate the spec automatically from decorators on controllers/DTOs.

Q3: What can you DO with an OpenAPI spec besides rendering docs?
A3: Generate client SDKs in multiple languages (via `openapi-generator`), validate incoming requests/outgoing responses against the schema at runtime (`express-openapi-validator`), import directly into Postman/Insomnia for testing, run contract tests in CI to catch breaking API changes, and generate mock servers for frontend development before the backend is ready.

Q4: Should you expose Swagger UI in production?
A4: Generally no, or only behind authentication. It exposes your full API surface (including internal/admin routes if not carefully scoped) and the "Try it out" feature lets anyone fire real requests against production if the routes aren't protected elsewhere. Common practice: enable it only in `development`/`staging` environments, or protect `/api-docs` with the same auth as sensitive routes.

Q5: How does OpenAPI help frontend/backend teams work in parallel?
A5: The backend team can write the OpenAPI spec first (API-first design) and generate a mock server from it immediately. The frontend team then builds against that mock using the exact documented shapes, while the backend team implements the real logic behind the same contract. When both are done, integration is smooth because both sides agreed on the contract upfront rather than discovering mismatches at integration time.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building a public or multi-team API where documentation accuracy matters
- You want auto-generated client SDKs or want to enable contract testing
- Frontend and backend teams need to work in parallel against an agreed contract

❌ Avoid when:
- A tiny internal API with 2-3 endpoints used only by one team that talks directly to the backend devs — overhead may not be worth it
- Rapid prototyping phase where the API shape changes every hour — maintain docs once it stabilizes

---

## 📊 Visual Diagram
```
OPENAPI WORKFLOW
──────────────────────────────────────────
  Route code with @openapi JSDoc comments
                │
                ▼
         swagger-jsdoc scans & builds
                │
                ▼
         openapi spec (JSON object)
          /            \
         ▼              ▼
   Swagger UI        openapi-generator
   (interactive       (client SDKs:
    docs at           TS/Python/Java)
    /api-docs)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OpenAPI Spec | Machine-readable API description | Machine-readable API description |
| Swagger UI | Interactive docs renderer | Interactive docs render करने वाला tool |
| swagger-jsdoc | Generates spec from code comments | Code comments से spec बनाने वाला tool |
| Contract testing | Validating real API against spec | Real API को spec से validate करना |
| API-first design | Writing spec before implementation | Implementation से पहले spec लिखना |

---

## ⚡ 3-Line Summary
English:
1. OpenAPI (Swagger) is a machine-readable spec format describing your API's endpoints, schemas, and errors.
2. `swagger-ui-express` + `swagger-jsdoc` let you generate interactive docs directly from route-level comments, keeping docs in sync with code.
3. Never expose live "Try it out" Swagger UI unauthenticated in production.

Hindi:
1. OpenAPI (Swagger) machine-readable spec format है जो API के endpoints, schemas, errors describe करता है।
2. `swagger-jsdoc` से route comments से docs auto-generate होती हैं, code के साथ sync रहती हैं।
3. Production में Swagger UI को unauthenticated मत रखो।

---

## ➡️ Next Topic
**194. Postman + Testing APIs** — Using Postman/collections to manually and automatically test the APIs you just documented.
