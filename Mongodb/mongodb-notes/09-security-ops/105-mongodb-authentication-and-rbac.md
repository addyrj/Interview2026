# 105. MongoDB Authentication + RBAC
# हिंदी में: MongoDB Authentication + RBAC

---

## 🔵 Simple Definition (English)
**Authentication** answers "who are you?" and **authorization** answers "what may you do?". MongoDB does authentication with mechanisms such as **SCRAM-SHA-256** (username and password, the default), x.509 certificates, LDAP and Kerberos (Enterprise) or AWS IAM. It does authorization with **RBAC** (Role-Based Access Control): you create users, give them **roles**, and each role is a set of **privileges** (an action such as `find` or `insert` on a resource such as `shop.orders`). Access control is OFF by default on a self-hosted `mongod`; you turn it on with `--auth` or `security.authorization: enabled`.

## 🔵 सरल परिभाषा (Hindi)
**Authentication** पूछता है "आप कौन हैं?" और **authorization** पूछता है "आप क्या कर सकते हैं?"। MongoDB authentication के लिए **SCRAM-SHA-256** (username और password, default), x.509 certificates, LDAP और Kerberos (Enterprise) या AWS IAM जैसे mechanisms देता है। Authorization के लिए **RBAC** (Role-Based Access Control): आप users बनाते हैं, उन्हें **roles** देते हैं, और हर role **privileges** का set है (एक action जैसे `find` या `insert`, एक resource जैसे `shop.orders` पर)। Self-hosted `mongod` पर access control default में बंद रहता है; इसे `--auth` या `security.authorization: enabled` से चालू करते हैं।

---

## 🔴 Problem it Solves
A fresh `mongod` with no auth lets anyone who can reach the port read, change or drop every database. Thousands of exposed MongoDB servers have been wiped and held for ransom exactly this way. Even inside a company, a reporting script should not be able to delete orders, and a microservice for orders should not read the payments database.

RBAC enforces the principle of **least privilege**: each person and each service gets only the access it needs, auditing shows who did what, and a leaked credential limits the damage.

## 🔴 यह क्यों बना? (Hindi)
Auth के बिना नया `mongod` हर उस व्यक्ति को, जो port तक पहुँच सके, हर database पढ़ने, बदलने या drop करने देता है। हज़ारों exposed MongoDB servers इसी तरह मिटाकर ransom माँगा गया। Company के अंदर भी, reporting script को orders delete करने की अनुमति नहीं होनी चाहिए, और orders का microservice payments database नहीं पढ़ना चाहिए।

RBAC **least privilege** सिद्धांत लागू करता है: हर व्यक्ति और service को सिर्फ उतना access जितना ज़रूरी, auditing दिखाती है किसने क्या किया, और credential leak होने पर नुकसान सीमित रहता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Start `mongod` WITHOUT auth only long enough to create the first admin (the **localhost exception** allows creating the first user when no users exist).
Step 2 → Create an admin user in the `admin` database with role `root` (or `userAdminAnyDatabase` plus others).
Step 3 → Restart with `--auth` (or `security.authorization: enabled` in `mongod.conf`). Now every command except `hello`/`ping`-type handshake requires authentication.
Step 4 → Create **application users** in the database where they are defined (the **authentication database**, `authSource`) with **built-in roles** (`read`, `readWrite`, `dbAdmin`, `clusterMonitor`, `backup`...) or **custom roles**.
Step 5 → The client connects with `mongodb://user:pass@host/db?authSource=...`; the server runs the SCRAM challenge (the password never travels in plain text) and records the user and roles on that connection.
Step 6 → On every command the server checks whether any of the user's roles grants the needed privilege. If not: `Unauthorized`.
Step 7 → Rotate passwords with `updateUser`, change access with `grantRolesToUser` / `revokeRolesFromUser`, remove with `dropUser`.
Step 8 → In replica sets/sharded clusters also set `keyFile` or x.509 for **internal** member authentication (this is separate from client users).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `mongod` को बिना auth के सिर्फ पहला admin बनाने जितनी देर चलाओ (**localhost exception** तब पहला user बनाने देता है जब कोई user नहीं हो)।
Step 2 → `admin` database में `root` role वाला admin user बनाओ (या `userAdminAnyDatabase` और बाकी roles)।
Step 3 → `--auth` (या `mongod.conf` में `security.authorization: enabled`) के साथ restart करो। अब handshake-type commands को छोड़कर हर command को authentication चाहिए।
Step 4 → **Application users** उस database में बनाओ जहाँ उन्हें define करना है (**authentication database**, `authSource`), **built-in roles** (`read`, `readWrite`, `dbAdmin`, `clusterMonitor`, `backup`...) या **custom roles** के साथ।
Step 5 → Client `mongodb://user:pass@host/db?authSource=...` से connect करता है; server SCRAM challenge चलाता है (password plain text में नहीं जाता) और उस connection पर user और roles दर्ज करता है।
Step 6 → हर command पर server जाँचता है कि user के किसी role में ज़रूरी privilege है या नहीं। नहीं तो: `Unauthorized`।
Step 7 → `updateUser` से password rotate, `grantRolesToUser` / `revokeRolesFromUser` से access बदलो, `dropUser` से हटाओ।
Step 8 → Replica sets/sharded clusters में **internal** member authentication के लिए `keyFile` या x.509 भी set करो (यह client users से अलग है)।

---

## 🟡 Real World Example
**Zomato's data platform** runs one MongoDB cluster with three consumers. The `orders-api` service gets `readWrite` on the `shop` database only. The analytics team's BI tool gets a custom role `orderReader` that can only `find` on `shop.orders`, so it cannot see payments or modify anything. The on-call DBA has `clusterMonitor` plus `backup`. When a contractor leaves, `dropUser` (or revoking roles) closes access in one command without touching the application's credentials. A leaked analytics password can read orders, but cannot delete them.

## 🟡 Real Example Hindi mein
**Zomato का data platform** एक MongoDB cluster पर तीन consumers चलाता है। `orders-api` service को सिर्फ `shop` database पर `readWrite` मिलता है। Analytics team के BI tool को custom role `orderReader` मिलता है जो सिर्फ `shop.orders` पर `find` कर सकता है, इसलिए वह payments नहीं देख सकता और कुछ बदल नहीं सकता। On-call DBA के पास `clusterMonitor` और `backup` है। Contractor जाए तो `dropUser` (या roles revoke) एक command में access बंद कर देता है, application के credentials छुए बिना। Analytics का password leak हो भी जाए तो orders पढ़े जा सकते हैं, delete नहीं।

---

## 💻 Code Example — Basic

```javascript
// Verified on MongoDB 8.0.4: second mongod started with --auth on port 27119.
// Step A: create the first admin (run while auth is still OFF; localhost exception)
//   mongosh --port 27119
db.getSiblingDB("admin").createUser({
  user: "root",                                   // admin username
  pwd: "RootPass#1",                              // use a long random password (or passwordPrompt())
  roles: [{ role: "root", db: "admin" }]          // superuser role
})
// Output: { ok: 1 }

// Step B: restart mongod with auth ON:
//   mongod --port 27119 --dbpath ./auth --bind_ip 127.0.0.1 --auth --fork --logpath auth.log

// Step C: unauthenticated clients are now blocked
//   mongosh --port 27119 --eval 'db.getSiblingDB("shop").orders.find().toArray()'
// Output: Unauthorized: Command find requires authentication

// Step D: connect as admin (note: # in password must be URL-encoded as %23 in a URI)
//   mongosh "mongodb://root:RootPass%231@127.0.0.1:27119/admin"
//   or:  mongosh --port 27119 -u root -p --authenticationDatabase admin   (prompts for password)

// Step E: see who you are on this connection
db.runCommand({ connectionStatus: 1 }).authInfo
// Output: { authenticatedUsers: [ { user: 'root', db: 'admin' } ],
//           authenticatedUserRoles: [ { role: 'root', db: 'admin' } ] }

// Step F: wrong password
//   mongosh "mongodb://reporter:bad@127.0.0.1:27119/shop"
// Output: MongoServerError: Authentication failed.
```

## 💻 Code Example — Advanced

```javascript
// Custom role + least-privilege users. Verified on MongoDB 8.0.4 with --auth.
// Connected as root (see Basic).
const shop = db.getSiblingDB("shop");

// 1) CUSTOM ROLE: may only 'find' on shop.orders (nothing else)
shop.createRole({
  role: "orderReader",
  privileges: [
    { resource: { db: "shop", collection: "orders" }, actions: ["find"] } // privilege = resource + actions
  ],
  roles: []                                                 // no inherited roles
})
// Output: { ok: 1 }

// 2) USERS: defined in the "shop" database, so authSource must be "shop" when they log in
shop.createUser({ user: "reporter", pwd: "Rep0rt#1", roles: ["orderReader"] })       // analytics
shop.createUser({ user: "appsvc",   pwd: "App#Svc1", roles: [{ role: "readWrite", db: "shop" }] }) // app

shop.orders.insertOne({ _id: 1, total: 499 })               // sample data as root

// 3) TEST as 'reporter':
//   mongosh "mongodb://reporter:Rep0rt%231@127.0.0.1:27119/shop"
db.orders.find().toArray()
// Output: [ { _id: 1, total: 499 } ]
db.orders.insertOne({ _id: 2 })
// Output: MongoServerError[Unauthorized]: not authorized on shop to execute command { insert: "orders", ... }
db.runCommand({ connectionStatus: 1 }).authInfo.authenticatedUserRoles
// Output: [ { role: 'orderReader', db: 'shop' } ]

// 4) MAINTENANCE (as root)
shop.grantRolesToUser("reporter", [{ role: "read", db: "shop" }])  // add a role
shop.getUser("reporter").roles                                     // Output: orderReader + read
shop.updateUser("reporter", { pwd: "New#Pw2" })                     // rotate password
shop.revokeRolesFromUser("reporter", [{ role: "read", db: "shop" }])// remove a role
shop.dropUser("reporter")                                           // delete user

// 5) Inspect a role's privileges
shop.getRole("orderReader", { showPrivileges: true }).privileges
// Output: [ { resource: { db: 'shop', collection: 'orders' }, actions: [ 'find' ] } ]
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Verified against the --auth instance (port 27119): app user can write to 'shop' only.
const { MongoClient } = require('mongodb');
const express = require('express');
const app = express();
app.use(express.json());

// Credentials come from env / secret manager, never from source code
const client = new MongoClient(process.env.MONGO_URI /* e.g. mongodb://127.0.0.1:27119/shop */, {
  auth: { username: process.env.DB_USER, password: process.env.DB_PASS }, // 'appsvc' / secret
  authSource: 'shop',                           // the database where the user was created
  maxPoolSize: 20,
});

(async () => {
  await client.connect();                        // SCRAM handshake happens here
  const orders = client.db('shop').collection('orders');

  app.post('/orders', async (req, res) => {
    const r = await orders.insertOne({ total: Number(req.body.total) }); // allowed: readWrite on shop
    res.status(201).json({ id: r.insertedId });
  });

  app.listen(3000);
})();

// What happens on a forbidden action (verified):
//   client.db('other').collection('x').insertOne({a:1})  -> MongoServerError, codeName 'Unauthorized'
// Mongoose is the same: mongoose.connect(uri, { authSource: 'shop', user: 'appsvc', pass: '...' })
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running without `--auth` and binding to `0.0.0.0`
```text
# Wrong: mongod --bind_ip 0.0.0.0           (no auth, open to the internet -> ransomed within hours)
# Right: mongod --auth --bind_ip 127.0.0.1,10.0.1.5   (auth on + only needed interfaces + firewall)
```

❌ Mistake 2: Using the `root` user (or an admin user) from the application
```javascript
// Wrong: app connects as root -> an injection bug can dropDatabase() everything
new MongoClient('mongodb://root:pass@db:27017/shop?authSource=admin');
// Right: dedicated least-privilege user per service
new MongoClient('mongodb://appsvc:pass@db:27017/shop?authSource=shop');
```

❌ Mistake 3: Wrong `authSource`
✅ Correct: A user is stored in ONE database (where `createUser` ran). If you created `appsvc` in `shop` but connect with `authSource=admin`, you get `Authentication failed` even with the right password. Match `authSource` to the creation database.

❌ Mistake 4: Special characters in the URI password
✅ Correct: URL-encode them (`#` is `%23`, `@` is `%40`, `/` is `%2F`) or pass credentials through the driver `auth` option as shown above.

---

## 🧠 Tricky Interview Question

**Q:** You enabled `--auth` and created a user in database `shop` with role `readWrite` on `shop`. The app connects and gets "Authentication failed". The password is right. Why?

**Answer:** The user's identity is the pair **(username, authentication database)**. The user was created in `shop`, but the connection string has no `authSource` (it defaults to the database in the URI path, or `admin` if no database is given) or points to `admin`, so the server looks for `appsvc@admin`, which does not exist. Fix: add `?authSource=shop`. A second subtlety: a user created in `shop` can be granted roles on OTHER databases (`{ role: "read", db: "reports" }`), but still must authenticate against `shop`. Also check that special characters in the password are URL-encoded.

---

## ⚫ Interview Questions + Answers

Q1: Is MongoDB secure by default?
A1: A self-hosted install is not: access control is disabled and (before 3.6) it bound to all interfaces. You must enable authorization, restrict `bindIp`, and enable TLS. Atlas enables authentication and TLS by default and requires an IP access list.

Q2: What is SCRAM and which versions are used?
A2: Salted Challenge Response Authentication Mechanism: the client proves it knows the password without sending it. MongoDB supports SCRAM-SHA-1 and SCRAM-SHA-256 (default for new users since 4.0; SHA-256 is stronger).

Q3: Built-in roles you should know?
A3: `read`, `readWrite` (per DB); `dbAdmin`, `userAdmin`, `dbOwner`; `readAnyDatabase`, `readWriteAnyDatabase`, `userAdminAnyDatabase` (admin DB); `clusterMonitor`, `clusterAdmin`; `backup`, `restore`; `root` (superuser).

Q4: What is the localhost exception?
A4: When access control is on but no users exist, connections from localhost may create the first user (only). Once any user exists, the exception closes. This lets you bootstrap securely.

Q5: How do you grant "can only read one collection"?
A5: Create a custom role with a privilege on `{ db, collection }` and actions `["find"]`, then assign it to the user (`createRole` + `createUser`). Built-in roles are database-wide, so custom roles are how you narrow further.

---

## 🔷 When to Use + When Not to Use
✅ Always use authentication and RBAC when:
- Any environment other than a throw-away laptop container
- Multiple services or teams share one cluster
- You need audit trails and least privilege (compliance: PCI, SOC 2, DPDP)

❌ Avoid:
- Sharing one super-admin account between people and apps
- Embedding passwords in git; use secret managers or x.509 / IAM-based auth instead
- Relying on authentication alone: pair it with network restrictions and TLS (note 106)

---

## 📊 Visual Diagram
```
AUTHENTICATION  ───►  AUTHORIZATION (RBAC)
──────────────────────────────────────────────────────
 client                       mongod  --auth
   │  1. connect + SCRAM      ┌──────────────────────────────┐
   ├─────────────────────────►│ lookup user (name + authDB)  │
   │  2. challenge/response   │ verify password (no plaintext)│
   │◄────────────────────────►└─────────────┬────────────────┘
   │                                        │ user → roles → privileges
   │  3. command: insert shop.orders        ▼
   ├────────────────────────────►  role 'readWrite@shop'    ► allowed
   │                               role 'orderReader@shop'  ► find only → Unauthorized for insert
   │
 privilege = { resource: {db, collection}, actions: [find, insert, ...] }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Authentication | Proving identity | पहचान साबित करना |
| Authorization | Checking permissions | अनुमति जाँचना |
| RBAC | Permissions grouped into roles | Roles में बँटी अनुमतियाँ |
| SCRAM-SHA-256 | Default password mechanism | Default password mechanism |
| authSource | DB where the user is defined | जिस DB में user बना है |
| Privilege | Actions on a resource | Resource पर actions |
| Custom role | Role you define yourself | खुद बनाया role |
| Localhost exception | Bootstrap first user | पहला user बनाने की छूट |

---

## ⚡ 3-Line Summary
English:
1. Turn on `--auth`; users authenticate with SCRAM and are authorized through roles made of privileges.
2. Give every service a dedicated least-privilege user (built-in or custom role); never use `root` in apps.
3. `authSource` must match where the user was created; URL-encode special characters in passwords.

Hindi:
1. `--auth` चालू करो; users SCRAM से authenticate होते हैं और privileges से बने roles से authorize होते हैं।
2. हर service को अलग least-privilege user दो (built-in या custom role); apps में `root` कभी मत इस्तेमाल करो।
3. `authSource` वही होना चाहिए जहाँ user बना; password के special characters URL-encode करो।

---

## ➡️ Next Topic
**106. MongoDB Security Checklist (TLS, encryption, network)** — locking down the wire, the disk and the network.

---
> Verified on MongoDB 8.0.4 (mongosh + Node driver 7.x against a `--auth` instance). Error text and ObjectIds can differ slightly by version.
