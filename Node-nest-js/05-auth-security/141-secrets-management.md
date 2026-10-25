# 141. Secrets Management
# हिंदी में: Secrets Management

---

## 🔵 Simple Definition (English)
**Secrets management** is the practice of securely storing, accessing, rotating, and auditing sensitive credentials (API keys, DB passwords, encryption keys, certificates) using dedicated tools (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) instead of plain env vars or config files — providing encryption at rest, access control, versioning, and automatic rotation.

## 🔵 सरल परिभाषा (Hindi)
**Secrets management** sensitive credentials (API keys, DB passwords, encryption keys) को securely store, access, rotate, और audit करने की practice है, dedicated tools (HashiCorp Vault, AWS Secrets Manager) का use करके — plain env vars या config files के बजाय — encryption at rest, access control, versioning, और automatic rotation के साथ।

---

## 🔴 Problem it Solves
Plain environment variables and `.env` files have limitations at scale: no built-in access control (anyone with server access sees everything), no audit trail (who accessed which secret, when), no automated rotation (changing a DB password means manually updating every service's config and restarting), and no encryption at rest within the storage mechanism itself. Dedicated secrets managers solve all of these: fine-grained access policies (service A can read only its own secrets), full audit logs, automatic rotation with zero-downtime secret updates, and encryption both at rest and in transit.

## 🔴 यह क्यों बना? (Hindi)
Plain environment variables और `.env` files scale पर limitations रखते हैं — कोई access control नहीं, कोई audit trail नहीं, कोई automated rotation नहीं। Dedicated secrets managers यह सब solve करते हैं — fine-grained access policies, full audit logs, automatic rotation zero-downtime के साथ, encryption at rest और in transit।

---

## 🟢 How it Works — Step by Step

Step 1 → Secrets are stored encrypted in a centralized vault/service, never in app code or config files
Step 2 → App authenticates to the secrets manager at startup using a short-lived identity (IAM role, service account token) — NOT a static credential
Step 3 → App requests specific secrets it's authorized for (`GET /secret/db-password`) — the secrets manager checks access policy before returning
Step 4 → Secrets manager returns the secret value, often with a lease/TTL (time-to-live) for dynamically-generated secrets (e.g., temporary DB credentials valid for 1 hour)
Step 5 → App caches the secret in memory for its lease duration, re-fetches before expiry
Step 6 → Rotation: secrets manager can automatically generate a NEW secret (e.g., new DB password) on a schedule, update the underlying system (DB user password), and apps fetch the new value on their next access — minimizing manual coordination
Step 7 → Every access is logged (who/what accessed which secret, when) for audit/compliance

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Secrets centralized vault में encrypted store होते हैं
Step 2 → App short-lived identity से secrets manager को authenticate करता है
Step 3 → App specific secrets request करता है, access policy check होती है
Step 4 → Secrets manager value return करता है, TTL के साथ कभी-कभी
Step 5 → App secret को memory में cache करता है lease duration तक
Step 6 → Rotation automatically नया secret generate करता है
Step 7 → हर access audit log होता है

---

## 🟡 Real World Example
**Razorpay's infrastructure (fintech, high compliance needs):** Database credentials are managed through AWS Secrets Manager with automatic 30-day rotation — when rotation triggers, Secrets Manager generates a new DB password, updates it in RDS, and all app instances automatically fetch the new credential on their next connection attempt (using the AWS SDK's secret-caching client), with zero manual intervention and zero downtime. Every secret access is logged in CloudTrail for PCI-DSS compliance audits, and access policies ensure the payment service can only read payment-related secrets, not the notification service's SMS gateway keys.

## 🟡 Real Example Hindi mein
**Razorpay का infrastructure (fintech, high compliance):** Database credentials AWS Secrets Manager से managed होते हैं automatic 30-day rotation के साथ — rotation होने पर नया password generate होता है, RDS में update होता है, apps automatically नया credential fetch करते हैं बिना downtime के। हर access CloudTrail में log होता है compliance audits के लिए।

---

## 💻 Code Example — Basic

```javascript
// secrets-basic.js — fetching a secret from AWS Secrets Manager (conceptual, using SDK)
// Run with: node secrets-basic.js (requires AWS credentials configured + npm install @aws-sdk/client-secrets-manager)

const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

const client = new SecretsManagerClient({ region: 'ap-south-1' });  // Mumbai region

// ─── 1. FETCH A SECRET BY NAME ────────────────────────────────────────────────
async function getSecret(secretName) {
  try {
    const command = new GetSecretValueCommand({ SecretId: secretName });
    const response = await client.send(command);

    // Secret can be a string or binary — most commonly a JSON string
    if (response.SecretString) {
      return JSON.parse(response.SecretString);
    }
    throw new Error('Secret is binary, not supported in this example');
  } catch (err) {
    console.error(`Failed to fetch secret ${secretName}:`, err.message);
    throw err;  // fail fast — don't let the app start with missing secrets
  }
}

// ─── 2. USAGE ───────────────────────────────────────────────────────────────────
async function main() {
  const dbCreds = await getSecret('prod/razorpay/db-credentials');
  console.log('DB host:', dbCreds.host);
  console.log('Password exists?', !!dbCreds.password);  // never log the actual value
}

main().catch(() => process.exit(1));
```

## 💻 Code Example — Advanced

```javascript
// secrets-advanced.js — caching layer with TTL + automatic refresh on rotation

class SecretsCache {
  constructor(secretsClient, ttlMs = 5 * 60 * 1000) {
    this.client = secretsClient;
    this.ttlMs = ttlMs;        // how long to trust a cached value before re-fetching
    this.cache = new Map();     // secretName -> { value, fetchedAt }
  }

  async get(secretName) {
    const cached = this.cache.get(secretName);
    const now = Date.now();

    // Return cached value if still within TTL (avoids hammering the secrets manager)
    if (cached && now - cached.fetchedAt < this.ttlMs) {
      return cached.value;
    }

    // Fetch fresh value (handles rotation: new password after rotation gets picked up)
    const value = await this.fetchFromManager(secretName);
    this.cache.set(secretName, { value, fetchedAt: now });
    return value;
  }

  async fetchFromManager(secretName) {
    const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');
    const command = new GetSecretValueCommand({ SecretId: secretName });
    const response = await this.client.send(command);
    return JSON.parse(response.SecretString);
  }

  // Called when a DB connection fails with an auth error — forces immediate refetch
  // instead of waiting for TTL, handling the edge case where rotation just happened
  invalidate(secretName) {
    this.cache.delete(secretName);
  }
}

// ─── USAGE: DB CONNECTION WITH AUTO-RETRY ON ROTATION ────────────────────────
async function connectWithRotationHandling(secretsCache, mysql) {
  let creds = await secretsCache.get('prod/db-credentials');

  try {
    return await mysql.createConnection({
      host: creds.host,
      user: creds.username,
      password: creds.password,
    });
  } catch (err) {
    if (err.code === 'ER_ACCESS_DENIED_ERROR') {
      // Password might have just rotated — invalidate cache and retry ONCE
      secretsCache.invalidate('prod/db-credentials');
      creds = await secretsCache.get('prod/db-credentials');
      return mysql.createConnection({ host: creds.host, user: creds.username, password: creds.password });
    }
    throw err;
  }
}

module.exports = { SecretsCache, connectWithRotationHandling };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app initializing secrets before accepting traffic
const express = require('express');
const { SecretsManagerClient } = require('@aws-sdk/client-secrets-manager');
const { SecretsCache } = require('./secrets-advanced');

const app = express();
const secretsClient = new SecretsManagerClient({ region: 'ap-south-1' });
const secretsCache = new SecretsCache(secretsClient);

let dbPool;

// Initialize secrets + DB connection BEFORE starting to accept HTTP traffic
async function bootstrap() {
  const dbCreds = await secretsCache.get('prod/db-credentials');
  const mysql = require('mysql2/promise');
  dbPool = mysql.createPool({
    host: dbCreds.host,
    user: dbCreds.username,
    password: dbCreds.password,
    database: dbCreds.dbName,
  });

  app.get('/health', (req, res) => res.json({ status: 'ok' }));

  app.get('/orders', async (req, res) => {
    try {
      const [rows] = await dbPool.execute('SELECT * FROM orders LIMIT 10');
      res.json(rows);
    } catch (err) {
      res.status(500).json({ error: 'Query failed' });
    }
  });

  app.listen(3000, () => console.log('Server ready, secrets loaded'));
}

bootstrap().catch((err) => {
  console.error('Failed to bootstrap app (secrets unavailable):', err.message);
  process.exit(1);  // never run with a broken secrets connection
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Fetching secrets on EVERY request instead of caching
```javascript
// WRONG: hits the secrets manager API on every single request — slow, costly, rate-limited
app.get('/orders', async (req, res) => {
  const creds = await getSecret('prod/db-credentials');  // network call every request!
  // ...
});

// CORRECT: fetch once at startup / cache with TTL, refresh only periodically or on rotation
const creds = await secretsCache.get('prod/db-credentials');  // cached, refreshed on TTL expiry
```

❌ Mistake 2: Using the SAME static secret across all environments/services
```javascript
// WRONG: one shared "master" API key used by every microservice and environment
// If leaked anywhere, ALL services across ALL environments are compromised

// CORRECT: unique secrets per service AND per environment, scoped by access policy
// prod/payment-service/db-credentials
// prod/notification-service/sms-gateway-key
// staging/payment-service/db-credentials  (different value than prod!)
```

---

## 🧠 Tricky Interview Question

```javascript
// A secrets manager rotates the DB password every 24 hours automatically.
// The app caches the DB password in memory with NO TTL/expiry logic at all,
// fetched once at startup and never refreshed.
// What happens roughly 24 hours after the app starts?
```
Answer: The app's cached password becomes **stale** — the secrets manager has rotated the actual DB password, but the app keeps trying to connect with the OLD cached value. New DB connection attempts start failing with authentication errors (existing already-open connections in a pool may continue working until they're recycled, but new connections fail). This causes a **partial outage** that's hard to debug because "nothing changed in the app" — the root cause is an external rotation the app wasn't designed to react to. The fix: implement TTL-based cache refresh (as in the advanced example) AND retry-on-auth-failure logic that invalidates the cache and re-fetches, so rotation is handled gracefully without a deploy or restart.

---

## ⚫ Interview Questions + Answers

Q1: What's the key difference between a secrets manager and simply using environment variables?
A1: Env vars are static values injected at process start — no built-in rotation, access control, or audit logging; anyone with access to the running process/container can read them all. A secrets manager provides: centralized encrypted storage, fine-grained IAM-based access policies (which service/role can read which specific secret), automatic rotation (can regenerate secrets AND update the underlying system like a DB), full audit trails of every access, and versioning (roll back to a previous secret value if needed).

Q2: How does automatic secret rotation avoid downtime when a database password changes?
A2: The secrets manager coordinates BOTH sides: it generates a new password, updates it in the actual database (so the new password now works), while the OLD password often remains valid for a brief overlap window (or existing connections using it simply aren't killed immediately). Apps fetch the new secret value either proactively (on their next cache-refresh cycle) or reactively (on an auth failure, triggering an immediate re-fetch). This overlap/graceful handling avoids a hard cutover moment where every app instance would fail simultaneously.

Q3: What is "dynamic secrets" (a feature of tools like HashiCorp Vault) and how does it differ from static secrets?
A3: Dynamic secrets are generated ON-DEMAND, per-request/per-lease, with a short TTL — e.g., Vault can create a brand-new, unique database user/password combination valid for exactly 1 hour, specifically for one app instance's request. When the lease expires, Vault automatically revokes that specific credential. This drastically limits the blast radius of a leaked credential (it expires soon and was never shared across multiple consumers) compared to static secrets that are long-lived and often shared across many app instances.

Q4: Why is "least privilege" important when designing secrets access policies?
A4: Each service/role should be able to access ONLY the specific secrets it needs, nothing more. If the notification service is compromised (e.g., via a vulnerable dependency), an attacker with access to its secrets should NOT also get the payment service's DB credentials just because they happened to be stored in the same system without proper access scoping. Least privilege limits the blast radius of any single compromise — a core security principle applied specifically to secrets management.

Q5: What should an application do if it fails to fetch a required secret at startup?
A5: Fail fast — log a clear error indicating which secret failed and why (network issue, access denied, secret doesn't exist), then exit the process (`process.exit(1)`) rather than starting in a broken/insecure state (e.g., falling back to a hardcoded default password, or running with a null DB connection that fails mysteriously later). This makes configuration problems visible immediately in deployment logs/health checks rather than manifesting as confusing runtime errors under production load.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Production systems, especially regulated industries (fintech, healthcare) needing audit trails and rotation.
- Multiple services/teams needing different, scoped access to different secrets.

❌ Avoid when:
- Small personal projects or early-stage prototypes where the operational overhead of running/integrating a full secrets manager outweighs the benefit — `.env` + careful discipline may suffice temporarily, with a plan to migrate as the project grows.

---

## 📊 Visual Diagram

```
SECRETS MANAGEMENT FLOW:
──────────────────────────────────────────────────────────

  App starts
       │
       ▼
  Authenticate to Secrets Manager (IAM role / service identity)
       │
       ▼
  Request secret: "prod/db-credentials"
       │
       ▼
  Secrets Manager checks access policy
       │
       ├─ Authorized ──► Returns secret (encrypted in transit) ──► App caches (TTL)
       │
       └─ Not authorized ──► 403 Access Denied

  ROTATION (background, automatic):
  Secrets Manager generates new password
       │
       ▼
  Updates password in actual DB
       │
       ▼
  App's next fetch (TTL expiry or auth-failure retry) gets NEW value
       │
       ▼
  Old connections drain naturally, new connections use new password
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Secrets manager | Dedicated service for storing/rotating secrets | Secrets store/rotate करने वाली dedicated service |
| Dynamic secrets | Short-lived, on-demand generated credentials | Short-lived, on-demand generated credentials |
| Secret rotation | Periodically replacing a secret value | Secret value को periodically replace करना |
| Least privilege | Minimal necessary access per service | हर service को minimal ज़रूरी access |
| TTL (Time To Live) | Duration a cached value is trusted | Cached value trust होने की duration |
| Audit trail | Log of who accessed what secret, when | किसने कब कौन सा secret access किया, उसका log |

---

## ⚡ 3-Line Summary
English:
1. Secrets management uses dedicated tools (Vault, AWS Secrets Manager) for encrypted storage, access control, rotation, and audit logging of sensitive credentials.
2. Apps authenticate with short-lived identities, fetch and cache secrets with a TTL, and handle rotation gracefully via retry-on-auth-failure logic.
3. Fail fast at startup if secrets are unavailable, and scope access per service following least privilege.

Hindi:
1. Secrets management dedicated tools (Vault, AWS Secrets Manager) से sensitive credentials का encrypted storage, access control, rotation, audit logging करती है।
2. Apps short-lived identities से authenticate करते हैं, secrets को TTL के साथ cache करते हैं, rotation को retry logic से handle करते हैं।
3. Secrets unavailable होने पर startup पर fail fast करो, हर service को least privilege access दो।

---

## ➡️ Next Topic
**142. OWASP Top 10 for Node.js** — Web application security का सबसे महत्वपूर्ण checklist।
