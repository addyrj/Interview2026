# 6. Installing MongoDB + mongosh + Atlas
# हिंदी में: MongoDB + mongosh + Atlas इंस्टॉल करना

---

## 🔵 Simple Definition (English)
Installing MongoDB means getting three things: **`mongod`** (the database server process), **`mongosh`** (the modern interactive shell/client), and optionally **MongoDB Atlas** (the fully managed cloud service, so you install nothing locally). You can run MongoDB locally (Homebrew, apt, MSI, Docker) or connect to Atlas using a `mongodb+srv://` connection string.

## 🔵 सरल परिभाषा (Hindi)
MongoDB install करने का मतलब तीन चीज़ें पाना है: **`mongod`** (database server process), **`mongosh`** (modern interactive shell/client), और optional **MongoDB Atlas** (fully managed cloud service, जिसमें local में कुछ install नहीं करना पड़ता)। MongoDB आप local (Homebrew, apt, MSI, Docker) पर चला सकते हैं या Atlas की `mongodb+srv://` connection string से connect कर सकते हैं।

---

## 🔴 Problem it Solves
Beginners often confuse "MongoDB the server" with "the shell" and the old `mongo` shell with the new `mongosh`. Running a production-grade database by hand also means handling backups, patching, replication and monitoring. Atlas removes that ops burden; a local `mongod` gives a free, offline dev environment. Knowing which piece does what saves hours of "connection refused" debugging.

## 🔴 यह क्यों बना? (Hindi)
Beginners अक्सर "MongoDB server" और "shell" को, और पुराने `mongo` shell को नए `mongosh` से confuse करते हैं। Production-grade database खुद चलाने में backups, patching, replication और monitoring भी संभालनी पड़ती है। Atlas यह ops बोझ हटा देता है; local `mongod` free, offline dev environment देता है। कौन सा हिस्सा क्या करता है यह जानने से "connection refused" debugging के घंटे बचते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install the server: macOS `brew tap mongodb/brew && brew install mongodb-community`; Ubuntu via the official apt repo; Windows via the MSI; or Docker `docker run -d -p 27017:27017 mongo`.
Step 2 → Start `mongod` (default port **27017**, default dbpath `/data/db` or `/opt/homebrew/var/mongodb` on Homebrew). Example: `brew services start mongodb-community`.
Step 3 → Install `mongosh` (the shell is a separate package: `brew install mongosh`) and connect: `mongosh` (defaults to `mongodb://127.0.0.1:27017`).
Step 4 → For Atlas: create a free M0 cluster, add a database user, add your IP to the Network Access list, copy the `mongodb+srv://...` string and run `mongosh "<string>"`.
Step 5 → Verify with `db.version()` and `db.runCommand({ ping: 1 })`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Server install करो: macOS पर `brew tap mongodb/brew && brew install mongodb-community`; Ubuntu पर official apt repo से; Windows पर MSI से; या Docker `docker run -d -p 27017:27017 mongo`।
Step 2 → `mongod` start करो (default port **27017**, default dbpath `/data/db`, Homebrew पर `/opt/homebrew/var/mongodb`)। जैसे `brew services start mongodb-community`।
Step 3 → `mongosh` install करो (shell अलग package है: `brew install mongosh`) और connect करो: `mongosh` (default `mongodb://127.0.0.1:27017`)।
Step 4 → Atlas के लिए: free M0 cluster बनाओ, database user जोड़ो, Network Access list में अपना IP जोड़ो, `mongodb+srv://...` string copy करो और `mongosh "<string>"` चलाओ।
Step 5 → `db.version()` और `db.runCommand({ ping: 1 })` से verify करो।

---

## 🟡 Real World Example
A Razorpay-style fintech startup gives every developer a local `mongod` (via Docker Compose) so tests run offline and fast, while staging and production run on an **Atlas** cluster in the Mumbai (ap-south-1) region with IP allow-listing and automated backups. The same code works in both places — only the `MONGO_URI` environment variable changes from `mongodb://localhost:27017/pay` to `mongodb+srv://user:pass@cluster0.xxxx.mongodb.net/pay`.

## 🟡 Real Example Hindi mein
Razorpay जैसा fintech startup हर developer को Docker Compose से local `mongod` देता है ताकि tests offline और तेज़ चलें, जबकि staging और production मुंबई (ap-south-1) region के **Atlas** cluster पर IP allow-list और automated backups के साथ चलते हैं। दोनों जगह वही code चलता है — सिर्फ `MONGO_URI` environment variable बदलता है: `mongodb://localhost:27017/pay` से `mongodb+srv://user:pass@cluster0.xxxx.mongodb.net/pay`।

---

## 💻 Code Example — Basic

```bash
# ---- macOS (Homebrew) ----
brew tap mongodb/brew                     # add MongoDB's official tap
brew install mongodb-community            # installs mongod (the server)
brew install mongosh                      # installs the shell separately
brew services start mongodb-community     # run mongod in the background

# ---- Check versions ----
mongod --version | head -1                # Output (this machine): db version v8.0.4
mongosh --version                         # prints the shell version

# ---- Connect to local server ----
mongosh                                   # same as mongosh mongodb://127.0.0.1:27017
```

```javascript
// Inside mongosh — verify the connection
db.version()                  // Output: '8.0.4' (your version may differ)
db.runCommand({ ping: 1 })    // Output: { ok: 1 }
db.getName()                  // Output: 'test' (default database name in mongosh)
show dbs                      // lists databases that contain data
```

## 💻 Code Example — Advanced

```bash
# Start your OWN mongod on a custom port with a custom data folder
mkdir -p ~/mongo-dev/db                   # folder that will hold data files
mongod --port 27111 \                     # listen on a non-default port
       --dbpath ~/mongo-dev/db \          # where data files are stored
       --bind_ip 127.0.0.1 \              # accept local connections only (safe default)
       --fork \                           # run in background (macOS/Linux)
       --logpath ~/mongo-dev/mongod.log   # required when using --fork

# Run a one-off command without opening the interactive shell
mongosh --port 27111 --quiet --eval 'db.runCommand({ ping: 1 })'   # Output: { ok: 1 }

# Atlas connection (cannot be run offline; syntax only)
# mongosh "mongodb+srv://cluster0.xxxx.mongodb.net/shop" --username appUser

# Clean shutdown of your own mongod
mongosh --port 27111 --quiet --eval 'db.getSiblingDB("admin").shutdownServer()'
```

> Verified locally: mongod v8.0.4 started with `--fork` on a custom port and answered `ping`. Atlas steps (cluster creation, IP allow-list, `mongodb+srv`) need an Atlas account and were NOT run here.

---

## 🟠 Express.js / Mongoose Integration

```javascript
// db.js — same code works for local mongod and Atlas; only the URI differs
const mongoose = require('mongoose');

async function connect() {
  // e.g. mongodb://127.0.0.1:27017/shop  OR  mongodb+srv://user:pass@cluster0.xxxx.mongodb.net/shop
  await mongoose.connect(process.env.MONGO_URI); // reads URI from environment, never hard-code passwords
  console.log('Mongo connected');                // runs only if the server is reachable
}
module.exports = connect;
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Typing `mongosh` before `mongod` is running
```bash
# Wrong — "MongoServerSelectionError: connect ECONNREFUSED 127.0.0.1:27017"
mongosh
# Right — start the server first, then connect
brew services start mongodb-community && mongosh
```

❌ Mistake 2: Using Atlas without allow-listing your IP or with special characters unescaped in the password
✅ Correct: Add your IP under Network Access, and URL-encode characters like `@` or `#` in passwords (`p@ss` -> `p%40ss`).

❌ Mistake 3: Using `--bind_ip 0.0.0.0` with no authentication
✅ Correct: Keep `127.0.0.1`, or enable auth (`--auth`) before exposing the port.

---

## 🧠 Tricky Interview Question
Q: You installed `mongodb-community` but typing `mongosh` says "command not found". Why?
Answer: Since MongoDB 5.0 the legacy `mongo` shell is deprecated, and `mongosh` is a **separate download/package** from the server. Installing the server does not guarantee the shell on every platform (on Homebrew you run `brew install mongosh`). `mongod` (server) and `mongosh` (client) are different binaries.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `mongod` and `mongosh`?
A1: `mongod` is the database server daemon that stores data and serves requests. `mongosh` is a client shell (Node.js-based REPL) that connects to it. You can stop the shell without stopping the database.

Q2: What is the default MongoDB port?
A2: 27017. Sharded `mongos` also uses 27017 by default; config servers use 27019 and shard servers 27018 when started with those roles.

Q3: What is `mongodb+srv://`?
A3: A connection string scheme that uses a DNS SRV record to discover all cluster hosts and automatically enables TLS. Atlas uses it so you do not list every replica member manually.

Q4: Why use Atlas instead of self-hosting?
A4: Managed backups, automatic failover, scaling, monitoring and security patches. Trade-off: cost and less control over the host.

Q5: How do you verify a MongoDB connection is alive?
A5: `db.runCommand({ ping: 1 })` returns `{ ok: 1 }`; `db.version()` shows the server version.

---

## 🔷 When to Use + When Not to Use
✅ Use local `mongod` when:
- Developing or running tests offline and cheaply
- You need full control over config/versions

✅ Use Atlas when:
- You want managed backups, HA and scaling with minimal ops

❌ Avoid when:
- Exposing a self-hosted `mongod` publicly without auth, TLS and firewall rules
- Using Atlas free tier (M0) for serious production load (shared, limited)

---

## 📊 Visual Diagram
```
INSTALL OPTIONS
──────────────────────────────────────────────
  Your App / mongosh / Compass
          │  (connection string)
          ▼
  ┌───────────────────┐       ┌────────────────────────┐
  │ mongodb://        │       │ mongodb+srv://         │
  │ 127.0.0.1:27017   │       │ cluster0.xxxx.mongodb  │
  └─────────┬─────────┘       └───────────┬────────────┘
            ▼                             ▼
   local mongod (you run it)     Atlas cluster (managed)
   dbpath: data files            replica set + backups
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mongod | Database server process | Database server process |
| mongosh | Interactive MongoDB shell | Interactive shell client |
| Atlas | Managed cloud MongoDB | Managed cloud MongoDB |
| dbpath | Folder of data files | Data files का folder |
| SRV string | `mongodb+srv://` discovery URI | DNS से hosts खोजने वाली URI |
| bind_ip | Interfaces mongod listens on | कौन से network address पर सुनना है |

---

## ⚡ 3-Line Summary
English:
1. `mongod` is the server, `mongosh` is the shell, Atlas is the managed cloud option.
2. Default port is 27017; start the server before connecting.
3. Switch between local and Atlas just by changing the connection string.

Hindi:
1. `mongod` server है, `mongosh` shell है, Atlas managed cloud option है।
2. Default port 27017 है; connect करने से पहले server start करो।
3. Local और Atlas के बीच बदलने के लिए सिर्फ connection string बदलो।

---

## ➡️ Next Topic
**7. MongoDB Compass + Atlas Basics** — The GUI tool and the Atlas web console for browsing and managing data.
