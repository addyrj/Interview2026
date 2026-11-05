# 106. MongoDB Security Checklist (TLS, encryption, network)
# हिंदी में: MongoDB Security Checklist (TLS, encryption, network)

---

## 🔵 Simple Definition (English)
A **MongoDB security checklist** is the set of hardening steps you apply before going to production: (1) **Authentication** (users/SCRAM, x.509), (2) **Authorization** (RBAC, least privilege), (3) **Network exposure** (`bindIp`, firewall, VPC/private endpoint), (4) **TLS** for data in transit, (5) **Encryption at rest** (WiredTiger/Enterprise, Atlas, disk-level, or Client-Side Field Level Encryption), (6) **Auditing/logging** and (7) **secrets and patching hygiene**. Thousands of databases have been ransomed because older MongoDB defaults had no auth and listened on all interfaces.

## 🔵 सरल परिभाषा (Hindi)
**MongoDB security checklist** production में जाने से पहले के hardening steps हैं: (1) **Authentication** (users/SCRAM, x.509), (2) **Authorization** (RBAC, least privilege), (3) **Network exposure** (`bindIp`, firewall, VPC/private endpoint), (4) transit में data के लिए **TLS**, (5) **Encryption at rest** (Enterprise, Atlas, disk-level या Client-Side Field Level Encryption), (6) **Auditing/logging**, और (7) **secrets और patching**। पुराने MongoDB defaults में auth नहीं था और सभी interfaces पर listen करता था, इसलिए हज़ारों databases पर ransomware हमले हुए।

---

## 🔴 Problem it Solves
A freshly installed `mongod` with no `--auth` lets **anyone who can reach the port** read, change or drop everything. Attackers scan the internet for port 27017, dump data and demand ransom. Beyond that: plain-text traffic can be sniffed, stolen disks/backups leak data, over-privileged app users turn one SQL-like bug into total loss, and nobody can tell who did what. The checklist closes each gap in layers (defense in depth).

## 🔴 यह क्यों बना? (Hindi)
बिना `--auth` वाला नया `mongod` **पोर्ट तक पहुँचने वाले किसी को भी** सब पढ़ने, बदलने या drop करने देता है। Attackers internet पर port 27017 scan करके data dump करते और फिरौती माँगते हैं। इसके अलावा plain-text traffic sniff हो सकता है, चोरी हुई disks/backups data leak करती हैं, ज़्यादा privilege वाला app user एक bug को पूरे नुकसान में बदल देता है, और पता नहीं चलता किसने क्या किया। Checklist हर gap को layers में बंद करती है (defense in depth)।

---

## 🟢 How it Works — Step by Step

Step 1 → **Network first:** bind to private IPs only (`net.bindIp: 127.0.0.1,10.0.1.5`), block 27017 in the firewall/security-group except from app servers, never expose it to `0.0.0.0/0`.
Step 2 → **Enable authentication:** `security.authorization: enabled`; create an admin user first, then per-application users.
Step 3 → **Least privilege RBAC:** give the app only `readWrite` on its own database (not `root`/`dbAdmin` on admin).
Step 4 → **TLS everywhere:** `net.tls.mode: requireTLS` with a CA-signed certificate; drivers connect with `tls=true`. Also use TLS between replica set members (`keyFile` or x.509 for internal auth).
Step 5 → **Encryption at rest:** Atlas encrypts by default; self-hosted needs Enterprise encrypted storage engine, or LUKS/EBS volume encryption; for the most sensitive fields (Aadhaar, card) use **CSFLE / Queryable Encryption** so the server never sees plaintext.
Step 6 → **Audit & monitor:** enable auditing (Enterprise/Atlas), ship logs, alert on failed logins.
Step 7 → **Hygiene:** keep MongoDB patched, store credentials in a secret manager (not git), rotate passwords, restrict `$where`/server-side JS (`security.javascriptEnabled: false`) if unused.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **पहले network:** सिर्फ private IPs पर bind करो (`net.bindIp: 127.0.0.1,10.0.1.5`), firewall/security-group में 27017 सिर्फ app servers के लिए खोलो, `0.0.0.0/0` कभी नहीं।
Step 2 → **Authentication चालू:** `security.authorization: enabled`; पहले admin user, फिर हर application के लिए अलग user।
Step 3 → **Least privilege RBAC:** app को सिर्फ अपने database पर `readWrite` दो (`root` नहीं)।
Step 4 → **हर जगह TLS:** `net.tls.mode: requireTLS` और CA-signed certificate; drivers `tls=true` से connect करें। Replica set members के बीच भी (`keyFile` या x.509)।
Step 5 → **Encryption at rest:** Atlas में default; self-hosted में Enterprise encrypted engine या LUKS/EBS volume encryption; सबसे sensitive fields (Aadhaar, card) के लिए **CSFLE / Queryable Encryption** ताकि server को plaintext दिखे ही नहीं।
Step 6 → **Audit और monitor:** auditing चालू, logs ship करो, failed logins पर alert।
Step 7 → **Hygiene:** patching, credentials secret manager में (git में नहीं), passwords rotate, ज़रूरत न हो तो server-side JS बंद।

---

## 🟡 Real World Example
A fintech startup like **Razorpay** runs MongoDB inside a private VPC subnet: no public IP, security group allows port 27017 only from the payments-service group. The app connects as user `payments_app` with `readWrite` on `payments` only, over TLS with a CA bundle. Card tokens and PAN numbers are encrypted client-side with CSFLE keys held in AWS KMS, so even a DBA or a leaked backup shows only ciphertext. A reporting user `analytics_ro` has the `read` role only. Failed-login spikes trigger a PagerDuty alert.

## 🟡 Real Example Hindi mein
**Razorpay** जैसा fintech MongoDB को private VPC subnet में चलाता है: public IP नहीं, security group port 27017 सिर्फ payments-service group को देता है। App user `payments_app` के पास सिर्फ `payments` पर `readWrite` है और connection CA bundle के साथ TLS पर है। Card tokens और PAN client-side CSFLE से encrypt होते हैं, keys AWS KMS में रहती हैं, इसलिए DBA या leak हुए backup में भी सिर्फ ciphertext दिखता है। Reporting user `analytics_ro` के पास सिर्फ `read` है। Failed-login spike पर alert जाता है।

---

## 💻 Code Example — Basic

```yaml
# /etc/mongod.conf — hardened baseline (syntax-checked; TLS files are placeholders)
net:
  port: 27017
  bindIp: 127.0.0.1,10.0.1.5     # NEVER 0.0.0.0 on a public host
  tls:
    mode: requireTLS               # reject non-TLS clients
    certificateKeyFile: /etc/ssl/mongodb.pem   # server cert + private key
    CAFile: /etc/ssl/ca.pem        # CA that signed client certs / to validate peers
security:
  authorization: enabled           # turn on RBAC (auth required)
  javascriptEnabled: false         # disable $where / $function / mapReduce JS
storage:
  dbPath: /var/lib/mongodb
```

```javascript
// users.js — run in mongosh. Verified on mongod 8.0.4 (port 27131)
const sec = db.getSiblingDB("sec");                 // application database
sec.createUser({
  user: "app",                                      // login name
  pwd: "x",                                         // use passwordPrompt() in real life!
  roles: [{ role: "readWrite", db: "sec" }]         // least privilege: only this DB
});
printjson(sec.getUser("app").roles);
// Output: [ { role: 'readWrite', db: 'sec' } ]
```

## 💻 Code Example — Advanced

```javascript
// secure-connect.js — Node driver with TLS + auth + CSFLE sketch
const { MongoClient } = require('mongodb');

const client = new MongoClient(process.env.MONGO_URI, {  // from secret manager, never hard-coded
  tls: true,                                  // encrypt traffic
  tlsCAFile: '/etc/ssl/ca.pem',               // verify server cert against our CA
  authSource: 'admin',                        // db where the user is defined
  retryWrites: true,
  serverSelectionTimeoutMS: 5000,
  // tlsAllowInvalidCertificates: true       // NEVER in production — disables validation
});

// Field-level encryption (needs Enterprise/Atlas or mongocryptd/crypt_shared) — syntax sketch
const autoEncryption = {
  keyVaultNamespace: 'encryption.__keyVault',     // collection storing wrapped data keys
  kmsProviders: { aws: { accessKeyId: '...', secretAccessKey: '...' } }, // master key in KMS
  schemaMap: {                                    // which fields to encrypt
    'pay.cards': {
      bsonType: 'object',
      properties: { pan: { encrypt: {
        bsonType: 'string',
        algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic' // deterministic = equality queries work
      } } }
    }
  }
};
// const secureClient = new MongoClient(uri, { autoEncryption }); // not executed here (needs KMS)
```

```bash
# Quick audit commands (mongosh)
# 1) Who am I and what can I do?
#    db.runCommand({connectionStatus: 1, showPrivileges: true})
# 2) Is auth really on? An unauthenticated client should fail:
#    mongosh --port 27017 --eval 'db.getSiblingDB("shop").orders.find()'  -> "requires authentication"
# 3) Is the port publicly visible?   nmap -p 27017 <public-ip>   (should be filtered/closed)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose connect with credentials from env, TLS and a least-privilege user
const mongoose = require('mongoose');
const express = require('express');
const helmet = require('helmet');           // HTTP header hardening (app layer)

async function boot() {
  await mongoose.connect(process.env.MONGO_URI, {  // mongodb+srv://app:***@cluster/db
    tls: true,
    tlsCAFile: process.env.MONGO_CA,
    autoIndex: false,                       // don't let the app create indexes in prod (needs more privileges)
    maxPoolSize: 20,
  });
  const app = express();
  app.use(helmet());
  app.use(express.json({ limit: '100kb' })); // limit body size
  app.listen(3000);
}
boot();
// .env is in .gitignore; production reads secrets from AWS Secrets Manager / Vault.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running without auth and with `bindIp: 0.0.0.0`
```yaml
# Wrong
net: { bindIp: 0.0.0.0 }
# (no security.authorization)
# Right
net: { bindIp: 127.0.0.1,10.0.1.5 }
security: { authorization: enabled }
```
❌ Mistake 2: App connects as an admin/root user.
✅ Correct: create `readWrite` on one DB per service; a bug or injection then can't drop other databases.

❌ Mistake 3: `tlsAllowInvalidCertificates=true` left in production "because it fixed the error". It disables man-in-the-middle protection. ✅ Install the proper CA.

❌ Mistake 4: Committing the connection string with the password to git. ✅ Use env vars / secret managers and rotate leaked creds immediately.

---

## 🧠 Tricky Interview Question
**Q:** You enabled `security.authorization: enabled` on a server that already has data but no users. What happens, and how do you create the first user?

**Answer:** Thanks to the **localhost exception**, a client connecting from the **same machine** (localhost) can create the *first* user in the `admin` database even though auth is enabled and nobody is logged in. Once that first user exists, the exception closes. Remote clients get "requires authentication" immediately. So the safe flow is: start with auth enabled, connect locally, create a `userAdminAnyDatabase` user, then reconnect with credentials and create app users. Existing data is untouched; it just becomes protected.

---

## ⚫ Interview Questions + Answers

Q1: What are the three A's of MongoDB security?
A1: Authentication (who are you: SCRAM-SHA-256, x.509, LDAP, Kerberos), Authorization (what may you do: RBAC roles), Auditing (record what happened). Network/TLS and encryption complete the picture.

Q2: TLS vs encryption at rest — what does each protect?
A2: TLS protects data **in transit** between client/server or between members. Encryption at rest protects **stored files/backups** from disk theft. CSFLE protects fields even from the DB server and admins (data **in use**).

Q3: What is the principle of least privilege here?
A3: Each user gets only the roles/DBs it needs: `read` for reporting, `readWrite` on one DB for the service, custom roles for finer actions (e.g., only `find` and `insert` on one collection).

Q4: Why is `$where` / server-side JavaScript a risk?
A4: It executes attacker-influenced JS inside the server (injection, DoS with infinite loops). Disable with `javascriptEnabled: false` unless needed, and prefer `$expr`.

Q5: How do replica set members authenticate each other?
A5: Via a shared `keyFile` (simple) or x.509 certificates (stronger). Both also enable internal RBAC when `authorization` is on.

---

## 🔷 When to Use + When Not to Use
✅ Apply the full checklist when:
- Any environment with real data, any internet-reachable network, and every production cluster

✅ Lighter setup acceptable when:
- Disposable local dev DB on `127.0.0.1` only (still never expose the port)

❌ Never:
- Expose unauthenticated MongoDB to the internet, even temporarily

---

## 📊 Visual Diagram
```
DEFENSE IN DEPTH
──────────────────────────────────────────────
 Internet ─▶ [Firewall / SG] ─▶ [VPC private subnet]
                 only app SG        │ bindIp=10.0.1.5
                                    ▼
 App ──TLS──▶ [ mongod ]──▶ authN (SCRAM/x509)
                  │            └▶ authZ (RBAC: readWrite on 1 DB)
                  │──▶ audit log ──▶ SIEM / alerts
                  ▼
        encrypted disk (at rest)   +   CSFLE fields (PAN, Aadhaar)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SCRAM | Default password auth mechanism | Default password authentication |
| RBAC | Role-based access control | Role के आधार पर access |
| TLS | Encryption of network traffic | Network traffic encryption |
| bindIp | Interfaces mongod listens on | mongod किन IPs पर सुनता है |
| CSFLE | Client-side field level encryption | Client-side field encryption |
| keyFile | Shared secret for replica members | Members की आपसी authentication |
| Localhost exception | Create first user locally | पहला user local से बनाना |

---

## ⚡ 3-Line Summary
English:
1. Lock down in layers: private network, authentication, least-privilege roles, TLS, encryption at rest and auditing.
2. Never expose an unauthenticated `mongod`; app users get `readWrite` on their own DB only.
3. Use CSFLE for ultra-sensitive fields and keep secrets out of git.

Hindi:
1. Layers में सुरक्षा: private network, authentication, least-privilege roles, TLS, encryption at rest और auditing।
2. बिना authentication वाला `mongod` कभी expose मत करो; app user को सिर्फ अपने DB पर `readWrite` दो।
3. बहुत sensitive fields के लिए CSFLE और secrets को git से बाहर रखो।

---

## ➡️ Next Topic
**107. NoSQL Injection + Prevention** — How `{ "$ne": null }` bypasses logins and how to stop it.
