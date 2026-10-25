# 261. PM2 Ecosystem File
# हिंदी में: PM2 Ecosystem File — Config के through Apps Manage करना

---

## 🔵 Simple Definition (English)
The **PM2 Ecosystem File** (`ecosystem.config.js`) is a single JavaScript config file that describes how PM2 should run one or more apps — script path, instances, cluster mode, environment variables for dev/staging/production, and even remote deployment settings. Instead of typing long `pm2 start` commands with many flags every time, you define everything once in this file and run `pm2 start ecosystem.config.js --env production`.

## 🔵 सरल परिभाषा (Hindi)
**PM2 Ecosystem File** (`ecosystem.config.js`) एक JavaScript config file है जो बताती है कि PM2 को एक या ज़्यादा apps कैसे चलाना है — script path, instances, cluster mode, dev/staging/production के लिए environment variables, और remote deployment settings भी। हर बार लंबे `pm2 start` commands कई flags के साथ type करने के बजाय, सब कुछ एक बार इस file में define करो और `pm2 start ecosystem.config.js --env production` चलाओ।

---

## 🔴 Problem it Solves
```
WITHOUT ecosystem file (CLI flags every time):
  pm2 start server.js --name "api" -i max --max-memory-restart 300M \
    --env NODE_ENV=production --env PORT=3000
  
  Problems:
  1. Long, error-prone commands typed manually every deploy
  2. No single source of truth — different devs type different flags
  3. Managing MULTIPLE apps (api, worker, cron-job) needs separate commands each
  4. Switching between dev/staging/production env vars is manual and risky
  5. No built-in way to define git-based remote deployment steps

WITH ecosystem.config.js:
  pm2 start ecosystem.config.js --env production
  
  Solutions:
  1. All config (name, script, instances, env vars) version-controlled in one file
  2. Define MULTIPLE apps in the same file (apps: [...]) — one command starts all
  3. env / env_production / env_staging blocks — switch cleanly via --env flag
  4. deploy section lets `pm2 deploy production setup/update` do git-pull + 
     install + reload on a remote server automatically
  5. Checked into git — every teammate runs the exact same config
```

## 🔴 यह क्यों बना? (Hindi)
Production में अक्सर एक से ज़्यादा apps चलानी पड़ती हैं (API server, background worker, cron job), और हर environment (dev/staging/production) के लिए अलग env variables चाहिए। हर बार CLI flags टाइप करना error-prone है और अलग developers अलग तरीके से चला सकते हैं। `ecosystem.config.js` इसे एक version-controlled file में centralize करता है — पूरी team same exact config use करती है, और git-based remote deployment (`pm2 deploy`) भी इसी file से configure होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Generate a starter file: `pm2 init simple` creates a basic `ecosystem.config.js`, or you write it manually.
Step 2 → Define the `apps` array — each object describes one app: `name`, `script`, `instances`, `exec_mode` (`cluster` or `fork`), `watch`, `max_memory_restart`.
Step 3 → Add `env` (default/dev values) and `env_production` (or `env_staging`) blocks inside each app object — these are merged into `process.env` based on the `--env` flag passed at start time.
Step 4 → Run `pm2 start ecosystem.config.js` for default env, or `pm2 start ecosystem.config.js --env production` to load the `env_production` block.
Step 5 → (Optional) Add a `deploy` section describing a remote server's SSH host, git repo, branch, and deploy path — enables `pm2 deploy ecosystem.config.js production setup` (first-time setup) and `pm2 deploy ecosystem.config.js production update` (pull latest + reload) run from your local machine.
Step 6 → After any config change, re-run `pm2 start ecosystem.config.js --env production --update-env` to apply new env vars to already-running processes, then `pm2 save` to persist the updated process list.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `pm2 init simple` से एक starter file बनाओ, या manually लिखो।
Step 2 → `apps` array define करो — हर object एक app describe करता है: `name`, `script`, `instances`, `exec_mode`, `watch`, `max_memory_restart`।
Step 3 → हर app object में `env` (default/dev values) और `env_production` (या `env_staging`) blocks add करो — ये `--env` flag के हिसाब से `process.env` में merge होते हैं।
Step 4 → Default env के लिए `pm2 start ecosystem.config.js` चलाओ, या production के लिए `--env production`।
Step 5 → (Optional) `deploy` section में remote server का SSH host, git repo, branch, deploy path लिखो — इससे `pm2 deploy ecosystem.config.js production setup/update` local machine से चलाकर remote deploy कर सकते हो।
Step 6 → Config बदलने के बाद, `pm2 start ecosystem.config.js --env production --update-env` से running processes में नए env vars apply करो, फिर `pm2 save` से process list persist करो।

---

## 🟡 Real World Example
**Razorpay's payments stack** has three distinct processes defined in one `ecosystem.config.js`: `payments-api` (cluster mode, 4 instances, handles HTTP requests), `webhook-worker` (fork mode, 1 instance, processes a Redis queue of bank webhook callbacks), and `reconciliation-cron` (fork mode, runs nightly settlement checks). Each app has its own `env_production` block with different `DATABASE_URL` and `REDIS_URL` pointing to production infra, versus `env` (default) pointing to local dev containers. The on-call engineer runs `pm2 start ecosystem.config.js --env production` once, and all three services come up correctly configured — no manual flag juggling, no risk of the webhook worker accidentally connecting to the dev database.

## 🟡 Real Example Hindi mein
**Razorpay के payments stack** में एक `ecosystem.config.js` में तीन अलग processes define हैं: `payments-api` (cluster mode, 4 instances, HTTP requests handle करता है), `webhook-worker` (fork mode, 1 instance, bank webhook callbacks की Redis queue process करता है), और `reconciliation-cron` (fork mode, रोज़ रात settlement checks चलाता है)। हर app का अपना `env_production` block है जिसमें production infra के `DATABASE_URL` और `REDIS_URL` हैं, जबकि `env` (default) local dev containers की तरफ point करता है। On-call engineer सिर्फ एक बार `pm2 start ecosystem.config.js --env production` चलाता है, और तीनों services सही config के साथ up हो जाती हैं — कोई manual flag juggling नहीं, और webhook worker गलती से dev database से connect होने का risk नहीं।

---

## 💻 Code Example — Basic

```javascript
// ecosystem.config.js — basic single-app setup
module.exports = {
  apps: [
    {
      name: 'zomato-api',              // name shown in `pm2 list`
      script: './server.js',           // entry file to run
      instances: 1,                    // start with just 1 instance (fork mode)
      exec_mode: 'fork',                // 'fork' = single process, 'cluster' = multi-core
      watch: false,                     // true would restart on file changes (dev only!)
      env: {                            // default env vars (used if no --env flag passed)
        NODE_ENV: 'development',
        PORT: 3000,
        DATABASE_URL: 'mongodb://localhost:27017/zomato_dev',
      },
      env_production: {                 // used only when --env production is passed
        NODE_ENV: 'production',
        PORT: 8080,
        DATABASE_URL: process.env.PROD_DB_URL,  // read real secret from shell env, not hardcoded
      },
    },
  ],
};
```

```bash
# Running the basic ecosystem file
pm2 start ecosystem.config.js                     # uses the default `env` block
pm2 start ecosystem.config.js --env production     # uses `env_production` block instead
pm2 list                                            # verify it's running with the right name
```

## 💻 Code Example — Advanced

```javascript
// ecosystem.config.js — multiple apps + multiple environments + deploy section
module.exports = {
  apps: [
    {
      // ─── App 1: Main API server (cluster mode, all cores) ───────────────
      name: 'payments-api',
      script: './src/server.js',
      instances: 'max',                 // 'max' = one instance per CPU core
      exec_mode: 'cluster',              // cluster mode for load balancing
      max_memory_restart: '400M',        // restart an instance if it exceeds 400MB
      env: {
        NODE_ENV: 'development',
        PORT: 4000,
        REDIS_URL: 'redis://localhost:6379',
      },
      env_staging: {
        NODE_ENV: 'staging',
        PORT: 4000,
        REDIS_URL: process.env.STAGING_REDIS_URL,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 4000,
        REDIS_URL: process.env.PROD_REDIS_URL,
        instances: 8,                    // override instance count specifically for prod
      },
    },
    {
      // ─── App 2: Background worker (fork mode, single instance) ──────────
      name: 'webhook-worker',
      script: './src/worker.js',
      instances: 1,                      // workers usually don't need cluster mode
      exec_mode: 'fork',
      autorestart: true,                 // restart if it crashes
      max_restarts: 10,                  // give up after 10 rapid restarts (avoid crash loop)
      env_production: {
        NODE_ENV: 'production',
        QUEUE_NAME: 'webhook-events-prod',
      },
    },
    {
      // ─── App 3: Nightly cron job (runs once, PM2 keeps it registered) ───
      name: 'reconciliation-cron',
      script: './src/cron/reconcile.js',
      instances: 1,
      exec_mode: 'fork',
      cron_restart: '0 2 * * *',          // PM2 restarts this process daily at 2 AM
      autorestart: false,                 // don't restart on normal exit, only via cron schedule
    },
  ],

  // ─── Deploy section — git-based remote deployment ──────────────────────
  deploy: {
    production: {
      user: 'deploy',                                        // SSH user on remote server
      host: ['prod-server-1.razorpay.internal'],               // can list multiple hosts
      ref: 'origin/main',                                      // git branch/ref to deploy
      repo: 'git@github.com:razorpay/payments-service.git',    // git repo URL
      path: '/var/www/payments-service',                       // deploy directory on server
      'post-deploy':                                            // runs after each `pm2 deploy update`
        'npm install && pm2 reload ecosystem.config.js --env production',
    },
    staging: {
      user: 'deploy',
      host: ['staging-server.razorpay.internal'],
      ref: 'origin/develop',
      repo: 'git@github.com:razorpay/payments-service.git',
      path: '/var/www/payments-service-staging',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env staging',
    },
  },
};
```

```bash
# Advanced usage commands

# First-time remote setup (creates folders, clones repo) — run once per server
pm2 deploy ecosystem.config.js production setup

# Every subsequent deploy — git pull + npm install + pm2 reload, all remote, from your laptop
pm2 deploy ecosystem.config.js production update

# Start all 3 apps locally with production env
pm2 start ecosystem.config.js --env production

# Apply only to one app from the file
pm2 start ecosystem.config.js --only webhook-worker --env production

# Reload with updated env vars without restarting from scratch
pm2 start ecosystem.config.js --env production --update-env
pm2 save
```

---

## 🟠 Express.js Integration

```javascript
// src/server.js — the Express app referenced by `script` in ecosystem.config.js
const express = require('express');
const app = express();
app.use(express.json());

// Env vars injected by PM2's env_production / env_staging blocks are read normally
const PORT = process.env.PORT || 3000;
const REDIS_URL = process.env.REDIS_URL;

console.log(`Starting in ${process.env.NODE_ENV} mode, Redis at ${REDIS_URL}`);

app.get('/health', (req, res) => {
  // Useful to confirm which env the running instance actually loaded
  res.json({ env: process.env.NODE_ENV, port: PORT, pid: process.pid });
});

app.post('/payments', (req, res) => {
  const { amount, orderId } = req.body;
  if (!amount || !orderId) {
    return res.status(400).json({ error: 'amount and orderId required' });
  }
  // ... process payment, publish event to webhook-worker via Redis queue ...
  res.status(201).json({ status: 'processing', orderId });
});

app.listen(PORT, () => console.log(`payments-api up on ${PORT}, pid ${process.pid}`));
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Hardcoding secrets directly inside `ecosystem.config.js` and committing it to git
```javascript
// WRONG — DATABASE_URL with real password checked into version control
env_production: {
  DATABASE_URL: 'mongodb://admin:SuperSecret123@prod-db:27017/app',  // leaked secret!
}

// RIGHT — read from the server's own environment/secrets manager, config file stays generic
env_production: {
  DATABASE_URL: process.env.PROD_DB_URL,   // set this on the server via .bashrc, systemd env, or Secrets Manager
}
```

❌ **Mistake 2:** Forgetting `--env production` and silently running with dev defaults
```bash
# WRONG — no --env flag, app silently uses the `env` (dev) block in production!
pm2 start ecosystem.config.js

# RIGHT — always explicit about which environment you're targeting
pm2 start ecosystem.config.js --env production
```

❌ **Mistake 3:** Using `pm2 restart` for config changes instead of reload + update-env
```bash
# WRONG — restart doesn't necessarily re-read updated env vars correctly, and causes downtime
pm2 restart ecosystem.config.js

# RIGHT — reload for zero downtime, --update-env to actually apply new env values
pm2 reload ecosystem.config.js --env production --update-env
```

---

## 🧠 Tricky Interview Question

**Q: You define `instances: 'max'` in the base app config but also set `instances: 8` inside `env_production`. You run `pm2 start ecosystem.config.js --env staging` on an 8-core machine, and staging has no `instances` override. How many instances actually start?**

```javascript
module.exports = {
  apps: [{
    name: 'api',
    script: './server.js',
    instances: 'max',                 // base-level setting
    env_staging: { NODE_ENV: 'staging' },         // no instances override here
    env_production: { NODE_ENV: 'production', instances: 8 },  // overrides base
  }],
};
```

**Answer:** With `--env staging`, PM2 merges the base app config with the `env_staging` block. Since `env_staging` doesn't override `instances`, the base-level `instances: 'max'` applies — so it starts **8 instances** (one per core on an 8-core machine) purely by coincidence matching the production override value, but for a different reason: `'max'` dynamically detects CPU count, while production's `instances: 8` is a hard-coded number that only applies when `--env production` is used. This distinction matters — if the production server had 16 cores instead, `'max'` would use all 16, but the hardcoded `env_production.instances: 8` would still cap it at 8 regardless of actual core count.

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between `env`, `env_staging`, and `env_production` blocks in an ecosystem file?**
A1: `env` holds default environment variables applied when PM2 starts the app with no `--env` flag. `env_staging` and `env_production` (or any custom name you choose) are additional blocks merged ON TOP of `env` when you pass the matching `--env <name>` flag — e.g., `pm2 start ecosystem.config.js --env production` merges `env_production` values over the base `env` values, letting you keep shared defaults and override only what differs per environment (like `DATABASE_URL`, `PORT`, log levels).

**Q2: How does the `deploy` section in ecosystem.config.js differ from running PM2 commands manually over SSH?**
A2: The `deploy` section automates the entire git-based deployment workflow from your local machine: `pm2 deploy production setup` SSHes in, clones the repo, and sets up the directory structure once; `pm2 deploy production update` SSHes in, does `git fetch` + `git reset` to the target ref, runs the `post-deploy` hook (typically `npm install && pm2 reload`), all without you manually SSH-ing in and typing each command yourself. It standardizes deploys so every team member deploys the exact same way.

**Q3: Why would you put a worker process and an API server in the same ecosystem.config.js instead of separate files?**
A3: Keeping them in one file under the `apps` array means a single `pm2 start ecosystem.config.js --env production` command brings up the entire service topology correctly configured and consistently — there's one source of truth for how all related processes should run together, version-controlled alongside the code. You can still target just one app with `--only <app-name>` when you need to restart/reload a single service without touching the others.

**Q4: What does `cron_restart` do in an app's config, and when would you use it instead of a system crontab?**
A4: `cron_restart: '0 2 * * *'` tells PM2 to restart that specific app on a cron schedule (here, 2 AM daily) — useful for apps that are meant to run once and exit, like a nightly reconciliation job. Using PM2's `cron_restart` instead of a plain OS crontab entry means the job's logs, restart history, and failure monitoring are unified with the rest of your PM2-managed services (visible in `pm2 list`, `pm2 logs`), rather than scattered across separate cron logs.

**Q5: If you change `instances` from 2 to 4 in the ecosystem file, does simply re-running `pm2 start ecosystem.config.js` apply the change to an already-running app?**
A5: Yes — PM2 detects the app is already running under that name and applies the new config, scaling the cluster to the new instance count (this effectively does a reload-like operation). However, best practice is to explicitly use `pm2 reload ecosystem.config.js --env production` after config changes so it's clear you're doing a controlled rolling update, and to follow with `pm2 save` so the new instance count is captured in the resurrection snapshot for the next server reboot.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You're running more than one PM2-managed process (API + worker + cron) and want them defined together
- You need different configuration (ports, DB URLs, instance counts) across dev/staging/production
- You want git-based "push to deploy" without a full CI/CD pipeline or container platform
- You want the PM2 process config version-controlled and reviewable in pull requests

❌ Avoid when:
- You have exactly one trivial app and a single environment — a plain `pm2 start server.js -i max` is simpler and the ecosystem file adds no value
- Your deployment already goes through CI/CD + Docker/Kubernetes — the `deploy` section's git-pull model conflicts with and duplicates that pipeline
- Secrets management requirements mean env vars must come from a vault at runtime, not a config file at all (then env vars should be injected by the orchestrator/systemd, not `ecosystem.config.js`)

---

## 📊 Visual Diagram
```
ecosystem.config.js STRUCTURE
──────────────────────────────────────────────────────────

module.exports = {
  apps: [
     ┌─────────────────────────────┐
     │ payments-api (cluster, 8x)  │──▶ env (dev) ──▶ env_staging ──▶ env_production
     ├─────────────────────────────┤        (merged based on --env flag passed)
     │ webhook-worker (fork, 1x)   │
     ├─────────────────────────────┤
     │ reconciliation-cron (fork)  │──▶ cron_restart: '0 2 * * *'
     └─────────────────────────────┘
  ],
  deploy: {
     production ──▶ SSH host + git repo + post-deploy hook
     staging    ──▶ SSH host + git repo + post-deploy hook
  }
}

COMMAND FLOW:
  Local machine                         Remote server
  ─────────────                         ──────────────
  pm2 deploy ... production update
        │  (SSH)
        ▼
                                   git fetch && git reset --hard origin/main
                                   npm install
                                   pm2 reload ecosystem.config.js --env production
                                          │
                                          ▼
                                   payments-api, webhook-worker, reconciliation-cron
                                   all reloaded with production env vars
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ecosystem File | PM2's JS config file for apps | PM2 का config file |
| apps array | List of app definitions in the file | Apps की list |
| env / env_production | Environment-specific variable blocks | Environment के हिसाब से variables |
| exec_mode | 'fork' or 'cluster' | Process चलाने का mode |
| instances | Number of process copies to run | कितने process instances |
| deploy section | Git-based remote deploy config | Remote deploy की config |
| post-deploy | Hook run after git pull on remote | Git pull के बाद चलने वाला hook |
| cron_restart | Scheduled restart via cron expression | Cron schedule से restart |
| --update-env | Flag to re-apply env vars on reload | Env vars फिर से apply करना |
| pm2 deploy | CLI command for remote deployment | Remote deployment command |

---

## ⚡ 3-Line Summary
**English:**
1. `ecosystem.config.js` centralizes PM2 app configuration — script, instances, cluster mode, and per-environment variables — in one version-controlled file.
2. `env`, `env_staging`, `env_production` blocks let one file serve multiple environments cleanly, selected via `--env <name>` at start time.
3. The `deploy` section automates git-based remote deployment (`pm2 deploy production update`), running git pull + install + reload on the remote server from your local machine.

**Hindi:**
1. `ecosystem.config.js` PM2 app की पूरी config — script, instances, cluster mode, environment variables — एक version-controlled file में centralize करता है।
2. `env`, `env_staging`, `env_production` blocks से एक ही file कई environments को serve करती है, `--env <name>` flag से select होता है।
3. `deploy` section git-based remote deployment automate करता है — local machine से `pm2 deploy production update` चलाकर remote server पर git pull + install + reload होता है।

---

## ➡️ Next Topic
**262. Zero Downtime Deployment** — `pm2 reload`, blue-green deployment, graceful shutdown, और health-check-gated traffic switching।
