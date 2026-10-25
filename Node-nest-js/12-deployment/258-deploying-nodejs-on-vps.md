# 258. Deploying Node.js on VPS
# हिंदी में: VPS पर Node.js App Deploy करना

---

## 🔵 Simple Definition (English)
Deploying on a **VPS (Virtual Private Server)** — like DigitalOcean, AWS Lightsail, or Hetzner — means renting a raw Linux machine, setting it up yourself: installing Node.js (via nvm), cloning your repo, installing dependencies, setting environment variables, running the app with a process manager like **PM2** so it stays alive, and securing the server with a firewall (ufw) and SSH keys. Unlike managed platforms (Heroku, Vercel), YOU own and manage the entire server.

## 🔵 सरल परिभाषा (Hindi)
**VPS (Virtual Private Server)** — जैसे DigitalOcean, AWS Lightsail, Hetzner — पर deploy करने का मतलब है एक raw Linux machine rent करना और खुद setup करना: Node.js install करना (nvm से), repo clone करना, dependencies install करना, environment variables set करना, app को **PM2** जैसे process manager से चलाना ताकि वह alive रहे, और server को firewall (ufw) और SSH keys से secure करना। Managed platforms (Heroku, Vercel) के विपरीत, पूरे server को TUM खुद manage करते हो।

---

## 🔴 Problem it Solves
```
BEFORE understanding VPS deployment:
  - Running `node server.js` directly in an SSH session → closes the
    moment you disconnect (process dies with the terminal session).
  - No auto-restart if the app crashes at 3 AM — downtime until someone
    manually SSHs in and restarts it.
  - Server exposed with EVERY port open → vulnerable to random internet
    scanning bots, brute-force SSH attacks on password auth.
  - Secrets (DB passwords, API keys) hardcoded in source code committed
    to git → leaked if repo is ever made public or breached.
  - Running Node directly on port 80/443 as root → security risk, and
    Node isn't great at handling raw TLS/SSL termination efficiently alone.

WITH PROPER VPS SETUP:
  - PM2 (or systemd) keeps the app running as a background daemon,
    auto-restarts on crash, auto-starts on server reboot.
  - ufw firewall allows ONLY needed ports (22 for SSH, 80/443 for web).
  - SSH key-based auth (not passwords) — immune to brute-force password
    attacks.
  - Environment variables in a .env file (never committed to git) for
    secrets.
  - Node runs on a high port (e.g. 3000) as a non-root user; Nginx
    (covered next) handles port 80/443 and TLS, proxying to Node.
```

## 🔴 यह क्यों बना? (Hindi)
```
VPS deployment समझने से पहले:
  - SSH session में directly `node server.js` चलाना → disconnect होते ही
    बंद हो जाता है (process terminal session के साथ मर जाता है)।
  - App crash होने पर 3 AM को कोई auto-restart नहीं — downtime जब तक कोई
    manually SSH करके restart न करे।
  - Server हर port open के साथ exposed → random internet scanning bots,
    password auth पर brute-force SSH attacks के लिए vulnerable।
  - Secrets (DB passwords, API keys) source code में hardcoded, git में
    committed → repo कभी public हुआ या breach हुआ तो leak।
  - Node को directly port 80/443 पर root से चलाना → security risk, और
    Node अकेले raw TLS/SSL termination efficiently handle नहीं करता।

PROPER VPS SETUP के साथ:
  - PM2 (या systemd) app को background daemon की तरह चलाता रखता है,
    crash पर auto-restart, server reboot पर auto-start।
  - ufw firewall सिर्फ needed ports allow करता है (22 SSH के लिए, 80/443
    web के लिए)।
  - SSH key-based auth (passwords नहीं) — brute-force password attacks
    से immune।
  - Secrets के लिए environment variables .env file में (git में कभी
    commit नहीं)।
  - Node high port (जैसे 3000) पर non-root user के रूप में चलता है;
    Nginx (next topic) port 80/443 और TLS handle करता है, Node को proxy
    करके।
```

---

## 🟢 How it Works — Step by Step

Step 1 → Spin up a VPS instance (DigitalOcean Droplet / AWS Lightsail / Hetzner Cloud) running Ubuntu LTS, note its public IP address.
Step 2 → Generate an SSH key pair locally (`ssh-keygen`), add the public key to the VPS during creation (or via `ssh-copy-id`), then disable password-based SSH login for security.
Step 3 → SSH into the server, update packages (`apt update && apt upgrade`), create a non-root user with sudo privileges (never run the app as root).
Step 4 → Install **nvm** (Node Version Manager) as that non-root user, then install the required Node.js version through it (keeps Node version independent of OS package manager, easy to upgrade).
Step 5 → Clone your git repo onto the server (or use `scp`/CI deployment), run `npm install --production` to install only production dependencies.
Step 6 → Create a `.env` file on the server (NEVER committed to git) with production secrets (DB URL, JWT secret, API keys).
Step 7 → Install **PM2** globally (`npm install -g pm2`), start the app with `pm2 start server.js --name my-app`, then run `pm2 startup` + `pm2 save` so PM2 resurrects the app automatically after a server reboot.
Step 8 → Configure the firewall (`ufw`): allow SSH (22), HTTP (80), HTTPS (443); deny everything else; enable it.
Step 9 → (Next topic) Put Nginx in front of the Node app as a reverse proxy, handling port 80/443 and TLS.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक VPS instance spin up करो (DigitalOcean Droplet / AWS Lightsail / Hetzner Cloud), Ubuntu LTS चलाते हुए, public IP address note करो।
Step 2 → Locally एक SSH key pair generate करो (`ssh-keygen`), public key को VPS creation के समय add करो (या `ssh-copy-id` से), फिर security के लिए password-based SSH login disable करो।
Step 3 → Server में SSH करो, packages update करो (`apt update && apt upgrade`), एक non-root user बनाओ sudo privileges के साथ (app को कभी root से मत चलाओ)।
Step 4 → उस non-root user के रूप में **nvm** (Node Version Manager) install करो, फिर उससे required Node.js version install करो (Node version OS package manager से independent रहता है, upgrade करना easy है)।
Step 5 → अपना git repo server पर clone करो (या `scp`/CI deployment use करो), `npm install --production` चलाओ सिर्फ production dependencies install करने के लिए।
Step 6 → Server पर एक `.env` file बनाओ (git में कभी commit नहीं) production secrets के साथ (DB URL, JWT secret, API keys)।
Step 7 → **PM2** globally install करो (`npm install -g pm2`), app को `pm2 start server.js --name my-app` से start करो, फिर `pm2 startup` + `pm2 save` चलाओ ताकि server reboot के बाद भी PM2 app को automatically resurrect करे।
Step 8 → Firewall configure करो (`ufw`): SSH (22), HTTP (80), HTTPS (443) allow करो; बाकी सब deny करो; enable करो।
Step 9 → (Next topic) Nginx को Node app के आगे reverse proxy की तरह लगाओ, port 80/443 और TLS handle करने के लिए।

---

## 🟡 Real World Example
**A small Indian fintech startup (Razorpay-style early stage)** deploys their Node.js payment-webhook-processor service on a Hetzner VPS during their bootstrapped phase (before moving to Kubernetes later at scale). DevOps runs: creates an Ubuntu 22.04 droplet, locks SSH to key-only auth, creates a `deploy` user, installs Node 20 via nvm, clones the repo via a deploy key, sets `.env` with `RAZORPAY_WEBHOOK_SECRET` and `DATABASE_URL`, starts the app with `pm2 start index.js --name webhook-processor -i 2` (2 cluster instances for the 2 vCPUs), and runs `pm2 save` + `pm2 startup` so the service survives server reboots during routine maintenance windows. `ufw` is configured to allow only 22, 80, 443 — blocking the thousands of daily bot scan attempts on other ports.

## 🟡 Real Example Hindi mein
**एक छोटा Indian fintech startup (Razorpay-style early stage)** अपनी Node.js payment-webhook-processor service को Hetzner VPS पर deploy करता है bootstrapped phase में (बाद में scale पर Kubernetes पर जाने से पहले)। DevOps यह करता है: Ubuntu 22.04 droplet बनाता है, SSH को key-only auth पर lock करता है, एक `deploy` user बनाता है, nvm से Node 20 install करता है, deploy key से repo clone करता है, `.env` में `RAZORPAY_WEBHOOK_SECRET` और `DATABASE_URL` set करता है, app को `pm2 start index.js --name webhook-processor -i 2` से start करता है (2 vCPUs के लिए 2 cluster instances), और `pm2 save` + `pm2 startup` चलाता है ताकि routine maintenance windows में server reboots के बाद भी service survive करे। `ufw` सिर्फ 22, 80, 443 allow करने के लिए configure है — बाकी ports पर daily हज़ारों bot scan attempts को block करते हुए।

---

## 💻 Code Example — Basic

```bash
# vps-initial-setup.sh
# Basic VPS provisioning script — run as root right after creating the server.
# Usage: ssh root@<server-ip> then paste/run this script (or save & chmod +x it)

#!/bin/bash
set -e  # exit immediately if any command fails

# ─── 1. UPDATE SYSTEM PACKAGES ─────────────────────────────────────────────
apt update && apt upgrade -y          # refresh package list, upgrade existing packages

# ─── 2. CREATE A NON-ROOT USER (never run apps as root) ────────────────────
adduser --disabled-password --gecos "" deploy   # create user "deploy" without interactive prompts
usermod -aG sudo deploy                          # give deploy sudo privileges

# ─── 3. SET UP SSH KEY AUTH FOR THE NEW USER ───────────────────────────────
mkdir -p /home/deploy/.ssh                                   # create .ssh dir for new user
cp ~/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys  # reuse the key you used to log in as root
chown -R deploy:deploy /home/deploy/.ssh                     # fix ownership
chmod 700 /home/deploy/.ssh                                  # restrict folder permissions
chmod 600 /home/deploy/.ssh/authorized_keys                  # restrict file permissions

# ─── 4. DISABLE PASSWORD SSH LOGIN AND ROOT LOGIN (security hardening) ────
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd   # apply SSH config changes

# ─── 5. SETUP FIREWALL (ufw) — only allow SSH, HTTP, HTTPS ────────────────
ufw allow OpenSSH   # allow SSH (port 22) so we don't lock ourselves out
ufw allow 80/tcp    # allow HTTP
ufw allow 443/tcp   # allow HTTPS
ufw --force enable  # enable firewall without interactive confirmation prompt

echo "Basic VPS hardening complete. Now log out and SSH back in as 'deploy' user."
```

```bash
# install-node-and-app.sh
# Run this AS THE "deploy" USER (not root) after basic setup above.
# Installs Node via nvm, clones repo, installs deps, sets up PM2.

#!/bin/bash
set -e

# ─── 1. INSTALL NVM (Node Version Manager) ─────────────────────────────────
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc   # reload shell so the `nvm` command becomes available

# ─── 2. INSTALL A SPECIFIC NODE VERSION VIA NVM ────────────────────────────
nvm install 20       # install Node.js v20 LTS
nvm use 20            # switch to it
nvm alias default 20  # make it the default for future shell sessions

# ─── 3. CLONE THE APPLICATION REPO ─────────────────────────────────────────
git clone git@github.com:myorg/my-node-app.git ~/my-node-app
cd ~/my-node-app

# ─── 4. INSTALL PRODUCTION DEPENDENCIES ONLY ───────────────────────────────
npm install --production    # skips devDependencies (test/lint tools) to keep it lean

# ─── 5. CREATE .env FILE (never committed to git — add to .gitignore!) ────
cat > .env << 'EOF'
NODE_ENV=production
PORT=3000
DATABASE_URL=postgres://user:pass@localhost:5432/mydb
JWT_SECRET=super-secret-change-me
EOF

# ─── 6. INSTALL PM2 GLOBALLY AND START THE APP ─────────────────────────────
npm install -g pm2                         # install PM2 process manager globally
pm2 start server.js --name my-node-app     # start app under PM2, named for easy management
pm2 startup                                # generates a systemd command to run — copy & execute it as instructed
pm2 save                                   # persist current process list so it resurrects after reboot

echo "App deployed and running under PM2. Check with: pm2 status"
```

## 💻 Code Example — Advanced

```javascript
// server.js — a production-aware Node.js app ready for PM2 cluster mode
// Run (after setup above): pm2 start server.js --name my-app -i max

const express = require('express');
require('dotenv').config(); // loads variables from .env into process.env

const app = express();
app.use(express.json());

// Read config from environment, with sane fallbacks for local dev
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

// Health check endpoint — PM2/load balancers can poll this to confirm liveness
app.get('/health', (req, res) => {
  res.json({ status: 'ok', pid: process.pid, env: NODE_ENV }); // pid helps verify cluster mode is spreading load
});

app.get('/orders/:id', (req, res) => {
  res.json({ orderId: req.params.id, servedBy: process.pid }); // shows WHICH cluster worker handled this
});

// ─── GRACEFUL SHUTDOWN — important for PM2 restarts to not drop requests ───
const server = app.listen(PORT, () => {
  console.log(`Worker ${process.pid} listening on port ${PORT} in ${NODE_ENV} mode`);
});

// PM2 sends SIGINT on restart/stop — handle it to drain connections cleanly
process.on('SIGINT', () => {
  console.log(`Worker ${process.pid} received SIGINT, shutting down gracefully...`);
  server.close(() => {
    console.log(`Worker ${process.pid} closed all connections, exiting.`);
    process.exit(0);
  });
  // Force-exit if graceful shutdown takes too long (avoid hanging forever)
  setTimeout(() => process.exit(1), 10000);
});
```

```javascript
// ecosystem.config.js — PM2 config file for production-grade process management
// Run: pm2 start ecosystem.config.js --env production

module.exports = {
  apps: [
    {
      name: 'my-node-app',          // process name shown in `pm2 status`
      script: 'server.js',           // entry file
      instances: 'max',              // cluster mode: one worker per CPU core
      exec_mode: 'cluster',          // enables Node's built-in cluster module under the hood
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      max_memory_restart: '300M',    // auto-restart a worker if it exceeds 300MB (leak protection)
      error_file: './logs/err.log',  // separate error log file
      out_file: './logs/out.log',    // separate stdout log file
      merge_logs: true,              // merge logs from all cluster workers into one timeline
      autorestart: true,             // restart automatically on crash
      watch: false,                  // disable file-watching in production (dev-only feature)
    },
  ],
};
```

---

## 🟠 Express.js Integration

```javascript
// Production-ready Express app structure for VPS deployment,
// reading config from environment and logging appropriately per environment.

const express = require('express');
const morgan = require('morgan');
require('dotenv').config();

const app = express();

// Use detailed logs locally, concise combined logs in production (less noisy, log-rotation friendly)
app.use(morgan(process.env.NODE_ENV === 'production' ? 'combined' : 'dev'));
app.use(express.json());

// Trust the reverse proxy (Nginx, set up in the next topic) for correct client IPs
app.set('trust proxy', 1); // important: without this, req.ip shows Nginx's IP, not the real client's

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.get('/orders/:id', (req, res) => {
  res.json({ orderId: req.params.id });
});

// Centralized error handler — crucial so PM2 doesn't see unhandled crashes
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`App running on port ${PORT}`));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Running the app directly with `node server.js` over SSH without a process manager
```bash
# WRONG — process dies the moment the SSH session disconnects or the terminal closes
ssh deploy@server
node server.js   # Ctrl+C or connection drop = app is DOWN

# CORRECT — use PM2 so the process survives independently of your SSH session
pm2 start server.js --name my-app
pm2 save           # persists process list across reboots
```

❌ **Mistake 2:** Running the Node app as the root user
```bash
# WRONG — running production app as root means any security vulnerability
# in your app or a dependency gives an attacker FULL root access to the server
sudo node server.js

# CORRECT — always run as a dedicated non-root user with limited permissions
su deploy
pm2 start server.js --name my-app
```

❌ **Mistake 3:** Committing `.env` with real secrets to git
```bash
# WRONG — .env with production DB password/JWT secret gets pushed to GitHub
git add .env
git commit -m "add env config"   # secrets now in git history FOREVER (even if deleted later)

# CORRECT — .env in .gitignore, secrets set directly on the server or via a
# secrets manager (AWS Secrets Manager, Doppler, Vault)
echo ".env" >> .gitignore
# On the server, create .env manually or via a secure deployment pipeline
```

❌ **Mistake 4:** Leaving ALL firewall ports open (default on many fresh VPS images)
```bash
# WRONG — no firewall configured, every port scannable/attackable by bots
# (ufw inactive by default on many fresh Ubuntu images)

# CORRECT — explicitly allow only what's needed, deny everything else
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status   # verify: should show only 22, 80, 443 as ALLOW
```

---

## 🧠 Tricky Interview Question

**Q: You deployed with `pm2 start server.js --name app`, it works fine, but after the VPS reboots for a scheduled maintenance update, the app is DOWN and nobody restarted it manually. What went wrong, and what's the single command that would have prevented this?**

```bash
pm2 start server.js --name app   # app is running... until reboot
# (reboot happens)
# pm2 list  →  shows NOTHING. The app is gone!
```

Answer: `pm2 start` only keeps the app running while PM2's own daemon is alive — but PM2 itself is NOT automatically configured to start on boot by default. You need to run `pm2 startup` (which generates and installs a systemd service for PM2 itself, tied to your OS) AND `pm2 save` (which snapshots the CURRENT list of running processes so that when PM2 restarts after reboot, via systemd, it knows to resurrect exactly these apps). Forgetting `pm2 save` after `pm2 startup` is the most common gotcha — `pm2 startup` alone just means PM2's daemon restarts after reboot, but with an EMPTY process list, so your app still doesn't come back unless you'd saved the list beforehand.

---

## ⚫ Interview Questions + Answers

**Q1: Why use nvm instead of installing Node.js via `apt install nodejs`?**
A1: The OS package manager (`apt`) often ships an outdated Node.js version and ties the Node version to the OS's release cycle, making upgrades painful and sometimes requiring sudo for every change. `nvm` (Node Version Manager) lets you install and switch between multiple Node versions as a regular user, matches exactly what your app was developed/tested against (important since Node has breaking changes between major versions), and makes upgrading or rolling back trivial (`nvm install 22`, `nvm use 20`) without touching system packages.

**Q2: What is the difference between using PM2 and using systemd directly to manage a Node.js process?**
A2: **systemd** is Linux's native service manager — works for ANY process (not just Node), very reliable, integrates deeply with OS boot sequence, but configuring cluster mode / zero-downtime reloads / log management requires writing more boilerplate unit files and extra tooling. **PM2** is Node-specific — built-in cluster mode (`-i max` spreads across CPU cores using Node's cluster module), zero-downtime reloads (`pm2 reload`), built-in log management and monitoring dashboard (`pm2 monit`), and simpler commands for common Node workflows. Many teams use PM2 ON TOP of systemd — `pm2 startup` actually generates a systemd service that starts the PM2 daemon on boot, combining both.

**Q3: Why should you run the Node.js app on a non-privileged port like 3000 instead of directly on port 80/443?**
A3: Ports below 1024 (including 80 for HTTP, 443 for HTTPS) are "privileged ports" on Linux and historically require root privileges to bind to — running your app as root is a major security risk since any vulnerability gives an attacker root access. Instead, Node runs on an unprivileged port (3000, 5000, etc.) as a non-root user, and a reverse proxy like Nginx (covered in the next topic) binds to 80/443 (it can do so safely with capability-based permissions) and forwards traffic internally to the Node process.

**Q4: What's the security benefit of disabling SSH password authentication in favor of SSH keys?**
A4: Password authentication is vulnerable to brute-force attacks — bots constantly scan the internet trying common username/password combos against port 22. SSH keys use asymmetric cryptography (a private key you keep locally, a public key on the server) — there's no password to guess, and brute-forcing a 2048+ bit key is computationally infeasible. Disabling `PasswordAuthentication` in `/etc/ssh/sshd_config` means even if someone knows (or guesses) a valid username, they cannot get in without the actual private key file.

**Q5: What's the risk of NOT setting `max_memory_restart` or similar memory limits in a PM2 production config?**
A5: If the Node app has a memory leak (e.g., an unbounded cache, event listeners not cleaned up, or a growing array never cleared), its memory usage climbs indefinitely until it either crashes the process (`Out of Memory` kill by the OS) or, worse, starves OTHER processes on the same VPS (the OS's OOM killer might kill an unrelated critical process like the database or Nginx instead). Setting `max_memory_restart: '300M'` in PM2's ecosystem config makes PM2 proactively restart the worker once it crosses that threshold, trading a brief restart for preventing system-wide instability.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want full control over the server environment (custom system dependencies, specific OS packages, cost control at scale).
- Budget-conscious early-stage startups where a $5-20/month VPS is cheaper than managed PaaS pricing at your traffic level.
- You need to run multiple apps/services on one machine with fine-grained resource control.

❌ Avoid when:
- Your team has no DevOps/sysadmin bandwidth to handle security patching, monitoring, and incident response — a managed platform (Render, Railway, Heroku, Vercel) trades some cost/control for operational simplicity.
- You need automatic multi-region scaling/load balancing out of the box — that's easier on managed cloud services or Kubernetes than hand-rolled on a single VPS.

---

## 📊 Visual Diagram
```
VPS DEPLOYMENT ARCHITECTURE:
──────────────────────────────────────────────────────────────

  Developer's Laptop
        │  git push / scp / CI deploy
        ▼
  ┌─────────────────────────────────────────────────┐
  │           VPS (Ubuntu, Hetzner/DO/Lightsail)      │
  │                                                    │
  │  ufw firewall: ALLOW 22(SSH), 80, 443 only         │
  │                                                    │
  │  SSH (key-only auth) ──────► deploy user (non-root)│
  │                                                    │
  │   nvm ──► Node.js v20                              │
  │                                                    │
  │   .env (secrets, NOT in git)                       │
  │                                                    │
  │   ┌───────────────────────────────────────────┐   │
  │   │  PM2 (process manager / daemon)             │  │
  │   │   ├── Worker 1 (cluster) : port 3000        │  │
  │   │   ├── Worker 2 (cluster) : port 3000        │  │
  │   │   └── auto-restart on crash / reboot        │  │
  │   └───────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────┘
        ▲
        │  (next topic: Nginx reverse-proxies 80/443 → 3000)
        │
    [ Internet Users ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| VPS | Rented virtual Linux server you fully manage | Rented virtual Linux server जिसे पूरी तरह तुम manage करते हो |
| nvm | Node Version Manager — install/switch Node versions | Node versions install/switch करने का tool |
| PM2 | Node.js process manager with clustering/auto-restart | Clustering/auto-restart वाला process manager |
| ufw | Uncomplicated Firewall — simple Linux firewall tool | Simple Linux firewall tool |
| SSH Key | Cryptographic key pair for secure server login | Server login के लिए cryptographic key pair |
| systemd | Linux's native service/process manager | Linux का native service manager |
| .env file | File holding environment variables/secrets | Environment variables/secrets वाली file |
| Cluster Mode | Running multiple app instances across CPU cores | CPU cores के across multiple app instances चलाना |
| Graceful Shutdown | Finishing in-flight requests before process exits | Process exit से पहले in-flight requests finish करना |

---

## ⚡ 3-Line Summary
**English:**
1. Deploying on a VPS means manually installing Node (via nvm), securing the server (SSH keys, ufw firewall, non-root user), and running the app with PM2 for auto-restart and clustering.
2. Secrets live in a `.env` file on the server, never committed to git; the app runs on a non-privileged port, with Nginx (next topic) handling 80/443.
3. `pm2 startup` + `pm2 save` together ensure the app survives server reboots — forgetting either one is the most common production outage cause.

**Hindi:**
1. VPS पर deploy करने का मतलब है manually Node install करना (nvm से), server secure करना (SSH keys, ufw firewall, non-root user), और PM2 से app चलाना auto-restart और clustering के लिए।
2. Secrets server पर `.env` file में रहते हैं, git में कभी commit नहीं; app non-privileged port पर चलता है, Nginx (next topic) 80/443 handle करता है।
3. `pm2 startup` + `pm2 save` दोनों मिलकर ensure करते हैं कि app server reboots survive करे — किसी एक को भूलना सबसे common production outage cause है।

---

## ➡️ Next Topic
**259. Nginx + Node.js Setup** — Nginx को reverse proxy की तरह लगाना, SSL/TLS (Let's Encrypt/certbot), load balancing multiple Node instances के across।
