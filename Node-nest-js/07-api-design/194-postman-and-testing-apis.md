# 194. Postman + Testing APIs
# हिंदी में: Postman + API Testing

---

## 🔵 Simple Definition (English)
**Postman** is a GUI tool for sending HTTP requests to your API manually and organizing them into reusable **collections** — with support for environment variables, scripted assertions (tests), and automated collection runs (via Newman/CI), making it a core tool for manually exploring, debugging, and automatically regression-testing REST APIs.

## 🔵 सरल परिभाषा (Hindi)
**Postman** एक GUI tool है जिससे आप अपने API को manually HTTP requests भेज सकते हो और उन्हें reusable **collections** में organize कर सकते हो — environment variables, scripted assertions (tests), और automated collection runs (Newman/CI से) के साथ। यह API explore, debug, और regression-test करने का core tool है।

---

## 🔴 Problem it Solves
```
PROBLEM WITHOUT POSTMAN:
  Testing an API manually means writing curl commands by hand every time
  Hard to share "how to call this endpoint" with teammates
  No easy way to chain requests (login → use token → call protected route)
  No structured way to assert responses are correct without writing a script

POSTMAN SOLUTION:
  Save requests as a Collection — shareable, versioned, organized by folder
  Environment variables ({{baseUrl}}, {{token}}) swap between dev/staging/prod
  Pre-request + test scripts (JS) to chain requests and assert responses
  Newman CLI runs entire collections in CI pipelines — automated API testing
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: हर बार manually curl commands लिखना पड़ता था
Teammates के साथ "कैसे call करें" share करना मुश्किल था
Login → token use → protected route chain करना मुश्किल था
Postman: Collections save करो, environment variables use करो, scripts से chain/assert करो
```

---

## 🟢 How it Works — Step by Step

Step 1 → Create a **Collection** — a folder of saved requests (GET/POST/PUT/DELETE) for your API
Step 2 → Define **Environments** (Dev, Staging, Prod) with variables like `{{baseUrl}}` so the same requests work across environments
Step 3 → Write **Pre-request Scripts** (JS) to set up data before a request (e.g., generate a timestamp, fetch a token)
Step 4 → Write **Tests** (JS, using `pm.test()` + `pm.expect()`) that run after the response arrives, asserting status code, body shape, response time
Step 5 → Use **Collection Runner** or the `newman` CLI to run the whole collection automatically (e.g., in CI/CD) and get a pass/fail report

## 🟢 कैसे काम करता है? (Hindi)
```
1. Collection बनाओ — saved requests का folder
2. Environments बनाओ — {{baseUrl}} जैसे variables से dev/staging/prod के बीच switch
3. Pre-request scripts से data setup करो (token fetch, timestamp generate)
4. Tests लिखो — pm.test() + pm.expect() से status/body/response time assert करो
5. Collection Runner या newman CLI से पूरा collection automatically run करो
```

---

## 🟡 Real World Example
**Amazon seller-API onboarding flow:** When a new engineer joins the Amazon Seller API team, instead of reading pages of docs and guessing curl syntax, they're handed a Postman collection with every endpoint pre-built: "Login", "Create Listing", "Update Inventory", "Get Order Status" — each with example payloads already filled in and an `{{sellerToken}}` environment variable auto-populated after running "Login" once. The whole team's regression suite also runs this SAME collection via `newman` in CI on every deploy, catching broken contracts before they reach production.

## 🟡 Real Example Hindi mein
**Amazon seller-API team:** नया engineer join करे तो उसे ready-made Postman collection मिलता है — "Login", "Create Listing", "Update Inventory" सब pre-built। Login चलाने पर `{{sellerToken}}` auto-set हो जाता है। पूरी team का regression suite यही collection `newman` से CI में run करता है हर deploy पर।

---

## 💻 Code Example — Basic

```javascript
// server.js — a simple Express API we'll test from Postman
// Run: npm install express   then  node server.js
const express = require('express');
const app = express();
app.use(express.json());

let token = null;

// Login endpoint — returns a fake token
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'admin' && password === 'secret') {
    token = 'fake-jwt-token-123';
    return res.json({ token });
  }
  res.status(401).json({ error: 'Invalid credentials' });
});

// Protected endpoint — requires the token from /login
app.get('/api/profile', (req, res) => {
  const authHeader = req.headers.authorization;  // expects "Bearer <token>"
  if (authHeader !== `Bearer ${token}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  res.json({ username: 'admin', role: 'owner' });
});

app.listen(3000, () => console.log('API running on port 3000'));

/*
  In Postman:
  1. POST http://localhost:3000/api/login  body: { "username": "admin", "password": "secret" }
     Test script (Postman "Tests" tab):
       pm.test("Status is 200", () => pm.response.to.have.status(200));
       pm.environment.set("token", pm.response.json().token);  // save token for next request

  2. GET http://localhost:3000/api/profile  header: Authorization: Bearer {{token}}
     Test script:
       pm.test("Returns admin profile", () => {
         pm.expect(pm.response.json().username).to.eql("admin");
       });
*/
```

## 💻 Code Example — Advanced

```javascript
// newman-runner.js
// Running a Postman collection programmatically via Newman in CI
// Run: npm install newman   then  node newman-runner.js
const newman = require('newman');

// Export your Postman collection as collection.json (Postman > ... > Export)
newman.run({
  collection: require('./collection.json'),       // the exported collection file
  environment: require('./dev-environment.json'), // exported environment with baseUrl etc.
  reporters: ['cli'],                              // print results to terminal
  iterationCount: 1,                                // run once (can repeat for load-style runs)
}, (err, summary) => {
  if (err) {
    console.error('Collection run failed to execute:', err);
    process.exit(1);
  }
  // summary.run.failures contains any failed assertions
  if (summary.run.failures.length > 0) {
    console.error(`${summary.run.failures.length} test(s) failed`);
    summary.run.failures.forEach((f) => {
      console.error(`- ${f.error.test}: ${f.error.message}`);
    });
    process.exit(1);  // non-zero exit fails the CI pipeline
  }
  console.log('All Postman tests passed!');
});
```

---

## 🟠 Express.js Integration

```javascript
// Express app designed with Postman-friendly conventions:
// consistent error shape + a /health endpoint Postman/CI can ping first
const express = require('express');
const app = express();
app.use(express.json());

// Health check — first request in most Postman collections / CI pipelines
app.get('/health', (req, res) => res.json({ status: 'ok', uptime: process.uptime() }));

// Consistent success/error response shape makes writing pm.test() assertions predictable
app.get('/api/orders/:id', (req, res) => {
  const order = { id: req.params.id, status: 'delivered' };
  if (!order) {
    return res.status(404).json({ success: false, error: 'Order not found' });
  }
  res.json({ success: true, data: order });
});

// Error-handling middleware ensures EVERY error follows the same shape,
// so one Postman test script can validate error responses across all endpoints
app.use((err, req, res, next) => {
  res.status(err.status || 500).json({ success: false, error: err.message });
});

app.listen(3000, () => console.log('API on port 3000 — see collection.json for Postman tests'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hardcoding URLs/tokens inside individual requests instead of using environment variables
✅ Correct: Use `{{baseUrl}}`, `{{token}}` — switching environments (dev/staging/prod) then needs zero request edits.

```
// Wrong
GET http://staging-api.example.com/api/users/123
Header: Authorization: Bearer abc123xyz

// Right
GET {{baseUrl}}/api/users/{{userId}}
Header: Authorization: Bearer {{token}}
```

❌ Mistake 2: Not chaining requests — manually copy-pasting a token from the login response into every other request by hand.
✅ Correct: Use a test script on the login request: `pm.environment.set("token", pm.response.json().token);` so every subsequent request auto-uses it via `{{token}}`.

❌ Mistake 3: Treating Postman only as a manual clicking tool and never running the collection in CI — regressions slip into production undetected.
✅ Correct: Export the collection + environment as JSON, run via `newman` in your CI pipeline on every PR/deploy.

---

## 🧠 Tricky Interview Question

**Question:** Your Postman collection has a "Login" request followed by a "Get Profile" request that uses `{{token}}`. In the **Collection Runner**, you run the whole collection, but "Get Profile" fails with 401 every time, even though running it manually right after Login works fine. Why?

Answer: The most common cause is an **environment/scope mismatch**: `pm.environment.set()` sets the variable on the currently selected **environment**, but if the Collection Runner is executed with a DIFFERENT environment selected (or no environment at all, falling back to **globals**), the token saved during the run never reaches "Get Profile" because it's looking it up in the wrong scope, or the variable was set only as a **local/collection** variable that doesn't persist between separate runner iterations correctly. The fix is to make sure the test script's variable scope (`pm.environment` vs `pm.collectionVariables` vs `pm.globals`) matches what's actually selected when the Collection Runner executes, and that order-of-execution (Login MUST run before Get Profile within that run) is respected — Collection Runner runs requests top-to-bottom by default, so folder/request ordering matters.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a Postman Collection and an Environment?
A1: A **Collection** is a saved, organized set of requests (the "what" — endpoints, methods, bodies). An **Environment** is a set of key-value variables (`baseUrl`, `token`, `apiKey`) that get substituted into collection requests using `{{variable}}` syntax, letting the SAME collection run against dev, staging, or production just by switching the active environment.

Q2: How do you chain requests in Postman (e.g., use a login token in later requests)?
A2: In the "Tests" (or "Post-response") script of the login request, extract data from the response and save it to a variable: `pm.environment.set("token", pm.response.json().token)`. Later requests then reference `{{token}}` in their headers/body, and Postman substitutes the saved value automatically.

Q3: What is Newman and why is it used?
A3: Newman is Postman's command-line collection runner. It takes an exported `collection.json` (and optionally an `environment.json`) and runs every request + its test scripts headlessly, printing pass/fail results and returning a non-zero exit code on failure — which makes it ideal for wiring Postman test suites into CI/CD pipelines so API regressions are caught automatically on every deploy.

Q4: How do you write an assertion/test in Postman?
A4: In the request's "Tests" tab, use the `pm` API: `pm.test("description", () => { pm.expect(pm.response.code).to.eql(200); })`, or shorthand helpers like `pm.response.to.have.status(200)`. These run after the response arrives and show green/red pass/fail indicators in the Postman UI, and feed into Newman's CI reports the same way.

Q5: Besides manual testing, what else is Postman used for?
A5: Automated regression testing (via Newman/CI), API documentation (Postman can publish collections as browsable docs, similar to Swagger), mock servers (simulate an API before the real backend exists, useful for frontend dev), monitoring (scheduled runs that alert if a production API starts failing), and importing OpenAPI specs directly to auto-generate a collection.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Manually exploring/debugging an API during development
- Building a shareable, versioned set of example requests for a team
- Running automated API regression tests in CI via Newman
- Mocking an API for frontend development before backend is ready

❌ Avoid when:
- You need deep, code-level unit/integration tests of business logic (use Jest/Mocha instead — Postman tests the HTTP contract, not internal code paths)
- Extremely simple internal scripts where a one-off curl command is faster than maintaining a collection

---

## 📊 Visual Diagram
```
POSTMAN WORKFLOW
──────────────────────────────────────────
  Collection (saved requests)
   ├─ Login          → Test script: save {{token}}
   ├─ Get Profile    → uses {{token}} from environment
   └─ Create Order   → uses {{token}}
          │
          ▼
   Environment (Dev / Staging / Prod)
   { baseUrl, token, apiKey }
          │
          ▼
   Collection Runner (manual)  OR  Newman CLI (automated/CI)
          │
          ▼
   Pass/Fail Report → fails CI build if any pm.test() fails
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Collection | Saved group of API requests | Saved API requests का group |
| Environment | Set of variables per stage | हर stage के लिए variables का set |
| Pre-request Script | JS run before request fires | Request भेजने से पहले चलने वाला JS |
| Test Script | JS assertions after response | Response के बाद चलने वाले assertions |
| Newman | CLI runner for collections | Collections चलाने का CLI tool |
| Collection Runner | GUI tool to run whole collection | पूरा collection चलाने का GUI tool |

---

## ⚡ 3-Line Summary
English:
1. Postman organizes API requests into Collections with Environment variables for switching between dev/staging/prod.
2. Test scripts (`pm.test`, `pm.expect`) assert response correctness and can chain data (like tokens) between requests.
3. Newman runs Postman collections headlessly in CI, turning manual API checks into automated regression tests.

Hindi:
1. Postman API requests को Collections में organize करता है, Environment variables से dev/staging/prod switch होता है।
2. Test scripts response correctness assert करते हैं और requests के बीच data (जैसे token) chain करते हैं।
3. Newman CI में collections headlessly run करता है — manual checks automated regression tests बन जाते हैं।

---

## ➡️ Next Topic
**195. Callbacks in Node.js** — Moving from API design into core async patterns, starting with the original async primitive: callbacks.
