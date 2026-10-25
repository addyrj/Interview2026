# 263. Deploy on AWS EC2
# हिंदी में: AWS EC2 पर Node.js App Deploy करना

---

## 🔵 Simple Definition (English)
**AWS EC2 (Elastic Compute Cloud)** gives you a virtual server (VM) in the cloud that you fully control, like renting a Linux computer by the hour. To deploy a Node.js app on EC2, you launch an instance, open the right network ports (security groups), SSH in, install Node/PM2/Nginx, and run your app — then optionally put a Load Balancer in front of multiple such instances to scale and stay available if one fails.

## 🔵 सरल परिभाषा (Hindi)
**AWS EC2 (Elastic Compute Cloud)** cloud में एक virtual server (VM) देता है जिसे आप पूरी तरह control करते हैं — जैसे घंटे के hisaab से एक Linux computer rent करना। EC2 पर Node.js app deploy करने के लिए: instance launch करो, सही network ports खोलो (security groups), SSH से connect करो, Node/PM2/Nginx install करो, और app चलाओ — फिर optionally कई instances के आगे एक Load Balancer लगाओ scaling और availability के लिए।

---

## 🔴 Problem it Solves
```
BEFORE CLOUD (physical/dedicated servers):
  1. Buy physical server hardware — expensive, slow to provision (weeks)
  2. Fixed capacity — can't scale up during a sale, can't scale down after
  3. You manage hardware failures, power, networking, physical security
  4. Scaling means buying MORE physical machines — capital expense, lead time

EC2 SOLUTION:
  1. Launch a virtual server in MINUTES, pay only for what you use (per hour/second)
  2. Scale UP (bigger instance type) or OUT (more instances) on demand
  3. AWS manages the physical hardware, networking, power, data center security
  4. Combine with Elastic IP (static public IP) + Load Balancer for 
     production-grade availability across multiple instances/availability zones

STILL A PROBLEM EC2 ALONE DOESN'T SOLVE:
  - YOU still manage the OS, patches, Node.js version, PM2, Nginx config
  - YOU still manage scaling logic (or use Auto Scaling Groups)
  - This is why managed services (ECS/Lambda, covered next) exist — 
    they take over more of this operational burden, at some cost of control
```

## 🔴 यह क्यों बना? (Hindi)
Physical servers खरीदना expensive और slow था — scaling के लिए weeks लगते थे, और capacity हमेशा fixed रहती थी (sale के समय ज़्यादा traffic नहीं संभाल पाते, बाद में wasted capacity)। EC2 इसे solve करता है — मिनटों में virtual server launch करो, usage के हिसाब से pay करो, ज़रूरत पड़ने पर scale up/out करो। लेकिन EC2 पर अभी भी OS, Node version, PM2, Nginx — सब कुछ आपको खुद manage करना पड़ता है, इसलिए आगे ECS/Lambda जैसी managed services भी हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Launch an EC2 instance**: go to AWS Console → EC2 → "Launch Instance" → pick an AMI (Amazon Machine Image, e.g. Ubuntu 22.04) → pick an instance type (e.g. `t3.medium` for a small Node API) → create/select a key pair (`.pem` file for SSH).
Step 2 → **Configure Security Group** (a virtual firewall): open inbound rules for port 22 (SSH, restricted to your IP), port 80 (HTTP), port 443 (HTTPS). Never leave 22 open to `0.0.0.0/0` in production.
Step 3 → **SSH into the instance**: `ssh -i mykey.pem ubuntu@<public-ip>` using the key pair downloaded at launch.
Step 4 → **Install Node.js, PM2, Nginx**: `sudo apt update`, install Node via NodeSource repo or `nvm`, `npm install -g pm2`, `sudo apt install nginx`.
Step 5 → **Deploy your app**: `git clone` your repo, `npm install`, `pm2 start ecosystem.config.js --env production`, `pm2 save`, `pm2 startup`.
Step 6 → **Configure Nginx as a reverse proxy**: Nginx listens on port 80/443 (public) and forwards requests to your Node app running on, say, port 3000 — Node itself should NOT be exposed directly to the internet.
Step 7 → **Assign an Elastic IP**: a static public IP so your domain's DNS A record doesn't break if the instance restarts (a regular public IP changes on stop/start).
Step 8 → **(For scale) Add an Application Load Balancer (ALB)**: launch 2+ EC2 instances across different Availability Zones, register them as targets behind an ALB. The ALB health-checks each instance and distributes traffic — if one instance dies, traffic automatically routes to the healthy ones.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **EC2 instance launch करो**: AWS Console → EC2 → "Launch Instance" → AMI चुनो (जैसे Ubuntu 22.04) → instance type चुनो (जैसे छोटे Node API के लिए `t3.medium`) → key pair बनाओ/चुनो (SSH के लिए `.pem` file)।
Step 2 → **Security Group configure करो** (virtual firewall): port 22 (SSH, सिर्फ अपने IP के लिए), port 80 (HTTP), port 443 (HTTPS) के inbound rules खोलो। Production में 22 को कभी `0.0.0.0/0` के लिए open मत छोड़ो।
Step 3 → **SSH से connect करो**: `ssh -i mykey.pem ubuntu@<public-ip>`, launch के समय download हुई key का use करके।
Step 4 → **Node.js, PM2, Nginx install करो**: `sudo apt update`, NodeSource या `nvm` से Node install करो, `npm install -g pm2`, `sudo apt install nginx`।
Step 5 → **App deploy करो**: `git clone`, `npm install`, `pm2 start ecosystem.config.js --env production`, `pm2 save`, `pm2 startup`।
Step 6 → **Nginx को reverse proxy की तरह configure करो**: Nginx port 80/443 (public) पर listen करता है और requests को Node app (port 3000) पर forward करता है — Node को सीधे internet पर expose नहीं करना चाहिए।
Step 7 → **Elastic IP assign करो**: static public IP, ताकि domain का DNS A record instance restart होने पर ना टूटे (normal public IP stop/start पर बदल जाता है)।
Step 8 → **(Scale के लिए) Application Load Balancer (ALB) add करो**: अलग Availability Zones में 2+ EC2 instances launch करो, उन्हें ALB के targets की तरह register करो। ALB हर instance को health-check करता है और traffic distribute करता है — एक instance मरे तो traffic automatically healthy instances पर जाता है।

---

## 🟡 Real World Example
**A Flipkart-style seller dashboard backend** running on EC2: the team launches two `t3.large` EC2 instances in different Availability Zones (`ap-south-1a` and `ap-south-1b`) for redundancy. Each runs the Node app via PM2 in cluster mode behind local Nginx. An Application Load Balancer sits in front of both instances, health-checking `/health` every 10 seconds. During a regional AZ outage affecting `ap-south-1a`, the ALB automatically stops routing traffic to that instance (failed health checks) and sends 100% of traffic to the healthy instance in `ap-south-1b` — sellers never notice the AZ issue. When traffic grows, the team adds a third EC2 instance and registers it with the same ALB target group — horizontal scaling without any code change.

## 🟡 Real Example Hindi mein
**Flipkart-style seller dashboard backend** EC2 पर चलता है: team दो `t3.large` EC2 instances अलग-अलग Availability Zones में launch करती है (`ap-south-1a` और `ap-south-1b`) redundancy के लिए। हर एक PM2 cluster mode में Node app चलाता है, local Nginx के पीछे। एक Application Load Balancer दोनों instances के आगे है, हर 10 seconds में `/health` check करता है। `ap-south-1a` में regional AZ outage के दौरान, ALB automatically उस instance पर traffic भेजना बंद कर देता है (health check fail) और पूरा traffic healthy instance (`ap-south-1b`) पर भेज देता है — sellers को AZ issue का पता भी नहीं चलता। Traffic बढ़ने पर, team तीसरा EC2 instance add करती है और उसे same ALB target group में register करती है — बिना code change के horizontal scaling।

---

## 💻 Code Example — Basic

```bash
# basic-ec2-setup.sh — commands run over SSH after launching an EC2 instance

# 1. Update package lists
sudo apt update && sudo apt upgrade -y

# 2. Install Node.js 20.x via NodeSource (recommended over apt's default old version)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v   # verify installation

# 3. Install PM2 globally
sudo npm install -g pm2

# 4. Install Nginx (will act as reverse proxy)
sudo apt install -y nginx
sudo systemctl enable nginx     # start on boot
sudo systemctl start nginx

# 5. Clone the app and install dependencies
git clone https://github.com/myorg/zomato-api.git
cd zomato-api
npm install --production

# 6. Start with PM2 and persist across reboot
pm2 start ecosystem.config.js --env production
pm2 save
pm2 startup        # run the sudo command it prints to enable systemd service
```

```javascript
// server.js — the app itself listens on an internal port, NOT exposed directly to the internet
const express = require('express');
const app = express();
app.get('/health', (req, res) => res.send('ok'));           // used by Nginx/ALB health checks
app.get('/', (req, res) => res.json({ message: 'Zomato API running on EC2' }));
app.listen(3000, '127.0.0.1', () => console.log('App listening on localhost:3000 only'));
// Binding to 127.0.0.1 (not 0.0.0.0) means only Nginx on the SAME machine can reach it directly
```

## 💻 Code Example — Advanced

```nginx
# /etc/nginx/sites-available/zomato-api — reverse proxy config
server {
    listen 80;                               # Nginx listens on public port 80
    server_name api.zomato-clone.com;        # your domain

    location / {
        proxy_pass http://127.0.0.1:3000;    # forward requests to the Node app
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;       # needed for WebSocket support
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;                   # preserve original Host header
        proxy_set_header X-Real-IP $remote_addr;        # pass real client IP to Node
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    location /health {
        proxy_pass http://127.0.0.1:3000/health;      # dedicated health check path
        access_log off;                                 # don't spam logs with health pings
    }
}
```

```bash
# advanced-ec2-ops.sh — security group, Elastic IP, and ALB setup via AWS CLI

# 1. Create a security group allowing only necessary ports
aws ec2 create-security-group --group-name zomato-api-sg --description "Zomato API SG"
aws ec2 authorize-security-group-ingress --group-name zomato-api-sg \
  --protocol tcp --port 22 --cidr <YOUR_IP>/32          # SSH only from your IP
aws ec2 authorize-security-group-ingress --group-name zomato-api-sg \
  --protocol tcp --port 80 --cidr 0.0.0.0/0              # HTTP from anywhere
aws ec2 authorize-security-group-ingress --group-name zomato-api-sg \
  --protocol tcp --port 443 --cidr 0.0.0.0/0              # HTTPS from anywhere

# 2. Allocate and associate an Elastic IP (static public IP, survives instance stop/start)
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id i-0abcd1234 --allocation-id eipalloc-0abcd1234

# 3. Create a target group and Application Load Balancer for multi-instance scaling
aws elbv2 create-target-group --name zomato-targets --protocol HTTP --port 80 \
  --vpc-id vpc-0abcd1234 --health-check-path /health
aws elbv2 register-targets --target-group-arn <TG_ARN> \
  --targets Id=i-0abcd1234 Id=i-0efgh5678         # register BOTH EC2 instances

aws elbv2 create-load-balancer --name zomato-alb --subnets subnet-aaa subnet-bbb \
  --security-groups sg-0abcd1234

aws elbv2 create-listener --load-balancer-arn <ALB_ARN> --protocol HTTP --port 80 \
  --default-actions Type=forward,TargetGroupArn=<TG_ARN>
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app reporting instance metadata, useful when behind an ALB
const express = require('express');
const os = require('os');
const app = express();

// Health check endpoint — the ALB target group pings THIS path to decide if the instance is healthy
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', hostname: os.hostname(), pid: process.pid });
});

// Trust the X-Forwarded-For header set by Nginx/ALB to get the real client IP
app.set('trust proxy', true);

app.get('/whoami', (req, res) => {
  res.json({ clientIp: req.ip, instance: os.hostname() }); // req.ip now reflects real client, not the LB
});

app.listen(3000, '127.0.0.1', () => console.log(`Instance ${os.hostname()} ready`));
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Leaving SSH (port 22) open to the entire internet
```bash
# WRONG — anyone can attempt to SSH-brute-force your server
aws ec2 authorize-security-group-ingress --group-name zomato-api-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

# RIGHT — restrict SSH to your office/VPN IP, or better, use AWS Systems Manager Session Manager
aws ec2 authorize-security-group-ingress --group-name zomato-api-sg \
  --protocol tcp --port 22 --cidr 203.0.113.45/32
```

❌ **Mistake 2:** Binding the Node app directly to `0.0.0.0` and exposing its port publicly
```javascript
// WRONG — Node app directly reachable on the internet at :3000, bypassing Nginx's
// rate limiting, TLS termination, and header sanitization
app.listen(3000, '0.0.0.0');
// and the security group allows inbound on port 3000 from 0.0.0.0/0

// RIGHT — bind to localhost only, let Nginx be the sole public-facing entry point
app.listen(3000, '127.0.0.1');
// security group only opens 80/443, never 3000, to the public internet
```

❌ **Mistake 3:** Not using an Elastic IP, then losing the public IP after a stop/start
```bash
# WRONG — instance public IP is 54.1.2.3 today, but after `aws ec2 stop-instances` +
# `start-instances`, AWS assigns a NEW public IP — your DNS A record now points nowhere
# (no Elastic IP allocated)

# RIGHT — allocate an Elastic IP and associate it once; it stays the same across restarts
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id i-0abcd1234 --allocation-id eipalloc-xxxx
```

---

## 🧠 Tricky Interview Question

**Q: You have two EC2 instances behind an Application Load Balancer. One instance's PM2 process crashes but the EC2 instance itself (the VM) stays running. Will the ALB automatically stop sending it traffic?**

**Answer:** Yes — but only because of the **health check**, not because the ALB inspects PM2 or the OS directly. The ALB's target group periodically calls the configured health check path (e.g., `/health`) over HTTP. If the Node process crashed, nothing is listening on that port anymore — the health check request fails (connection refused / timeout), and the ALB marks that target "unhealthy" after the configured threshold of consecutive failures. It then stops routing new traffic to that instance until health checks start passing again. Meanwhile, PM2 (if configured with auto-restart, which is default) should restart the crashed process within seconds — once it's back up and `/health` responds 200 again, the ALB marks it healthy and resumes sending traffic. This is exactly why BOTH PM2 (process-level recovery) and ALB health checks (traffic-level routing decisions) matter together — PM2 heals the process, the ALB protects users from the window while it's down.

---

## ⚫ Interview Questions + Answers

**Q1: What is a Security Group in AWS, and how is it different from a traditional firewall?**
A1: A Security Group is a virtual, stateful firewall attached to EC2 instances (or other resources) at the network interface level. It controls inbound and outbound traffic via allow-rules (there's no explicit "deny" rule needed — anything not allowed is denied by default). "Stateful" means if you allow inbound traffic on a port, the corresponding outbound response is automatically allowed too, without a separate rule. Unlike a traditional on-prem firewall that's a single shared physical/software appliance, each EC2 instance (or group of instances) can have its own Security Group(s), making per-service network isolation easy to configure.

**Q2: Why should Node.js not be directly exposed to the internet, with Nginx in front of it instead?**
A2: Nginx handles things Node.js doesn't do well or at all out of the box: TLS/SSL termination (HTTPS), serving static files efficiently, request buffering against slow clients, rate limiting, gzip/brotli compression, and acting as a single stable entry point if you later run multiple Node processes or need to proxy to different services by path. It also adds a layer of isolation — if Node crashes or misbehaves, Nginx can serve a maintenance page or route around it, and the Node process never needs root privileges to bind to privileged ports (80/443), since Nginx handles those and proxies internally to Node's unprivileged port.

**Q3: What's the difference between scaling up (vertical) and scaling out (horizontal) on EC2, and which does an ALB help with?**
A3: **Scaling up (vertical)** means moving to a bigger EC2 instance type (e.g., `t3.medium` → `t3.xlarge`) — more CPU/RAM on the same single machine, but there's a ceiling, and it usually requires a brief restart. **Scaling out (horizontal)** means adding MORE EC2 instances running the same app, splitting traffic between them — this is what an Application Load Balancer enables, distributing requests across multiple instances and allowing near-unlimited scaling, plus redundancy (if one instance dies, others keep serving).

**Q4: What happens to an EC2 instance's public IP address when you stop and start it, and why does that matter for deployment?**
A4: By default, AWS releases the instance's public IPv4 address when you stop it, and assigns a brand new one when you start it again — unless you've attached an Elastic IP. This matters because your domain's DNS record (or any client hardcoded with the IP) would point to a now-invalid address after a stop/start cycle. An Elastic IP is a static public IP you allocate and associate with the instance; it stays the same regardless of stop/start, so your DNS configuration remains valid.

**Q5: What are the main cost/scaling tradeoffs of deploying on raw EC2 instances versus using a managed service like AWS Lambda or ECS Fargate?**
A5: Raw EC2 gives maximum control (choose OS, install anything, SSH access) and can be cost-effective for steady, predictable load, but YOU are responsible for patching the OS, scaling logic (or configuring Auto Scaling Groups yourself), high availability setup, and you pay for the instance whether it's busy or idle. Managed services like Lambda (pay per invocation, scales to zero) or ECS Fargate (pay per container task, no OS to manage) remove most operational burden and can be cheaper for spiky/intermittent workloads, but you give up some control (can't SSH into a Lambda function) and may pay a premium per-unit-of-compute compared to a fully-utilized EC2 instance under constant heavy load.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need full control over the OS, installed software, or need specific system-level configuration
- Workload is steady/predictable enough that a continuously-running instance is cost-effective
- You're comfortable managing patching, security groups, and scaling yourself (or via Auto Scaling Groups)

❌ Avoid when:
- Traffic is highly spiky or unpredictable and you'd rather pay-per-use (consider Lambda/Fargate)
- You want zero server/OS management burden (container orchestration or serverless fits better)
- Your team is small and doesn't want to own infrastructure operations (patching, security group auditing, OS-level monitoring)

---

## 📊 Visual Diagram
```
EC2 DEPLOYMENT ARCHITECTURE
──────────────────────────────────────────────────────────

                       Internet
                           │
                           ▼
                 ┌───────────────────┐
                 │  Application Load  │   <- health-checks /health every N seconds
                 │  Balancer (ALB)    │
                 └─────────┬──────────┘
                ┌───────────┴───────────┐
                ▼                       ▼
     ┌─────────────────────┐  ┌─────────────────────┐
     │ EC2 Instance (AZ-1a) │  │ EC2 Instance (AZ-1b) │
     │ ┌──────────────────┐│  │ ┌──────────────────┐│
     │ │ Nginx :80/:443    ││  │ │ Nginx :80/:443    ││
     │ │   │ proxy_pass    ││  │ │   │ proxy_pass    ││
     │ │   ▼               ││  │ │   ▼               ││
     │ │ PM2 cluster       ││  │ │ PM2 cluster       ││
     │ │ (Node, :3000,     ││  │ │ (Node, :3000,     ││
     │ │  127.0.0.1 only)  ││  │ │  127.0.0.1 only)  ││
     │ └──────────────────┘│  │ └──────────────────┘│
     │ Security Group:      │  │ Security Group:      │
     │  22(you), 80, 443    │  │  22(you), 80, 443    │
     └──────────────────────┘  └──────────────────────┘

  If AZ-1a instance fails health check → ALB routes 100% traffic to AZ-1b
  Elastic IP (optional, for single-instance setups) keeps public IP stable across restarts
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EC2 | Virtual server in AWS cloud | AWS का virtual server |
| AMI | Base OS image for an instance | Instance की base image |
| Security Group | Virtual firewall for an instance | Virtual firewall |
| Elastic IP | Static public IP address | Static public IP |
| Reverse Proxy | Server forwarding requests to app | Request forward करने वाला server |
| ALB | Load balancer distributing HTTP traffic | HTTP traffic बाँटने वाला balancer |
| Target Group | Set of instances behind an ALB | ALB के पीछे instances का group |
| Availability Zone | Isolated data center location | अलग-अलग data center location |
| Horizontal Scaling | Adding more instances | ज़्यादा instances जोड़ना |
| Vertical Scaling | Bigger instance (more CPU/RAM) | बड़ा instance |

---

## ⚡ 3-Line Summary
**English:**
1. Deploying on EC2 means launching a virtual server, opening the right security group ports, and installing Node/PM2/Nginx yourself.
2. Nginx should sit in front of Node as a reverse proxy; Node binds only to localhost, never directly exposed to the internet.
3. An Elastic IP keeps your public address stable, and an Application Load Balancer across multiple instances/AZs gives scaling and automatic failover.

**Hindi:**
1. EC2 पर deploy करने का मतलब है virtual server launch करना, सही security group ports खोलना, और Node/PM2/Nginx खुद install करना।
2. Nginx को Node के आगे reverse proxy की तरह रखना चाहिए; Node सिर्फ localhost पर bind होता है, कभी सीधे internet पर expose नहीं होता।
3. Elastic IP से public address stable रहता है, और कई instances/AZs के आगे Application Load Balancer से scaling और automatic failover मिलता है।

---

## ➡️ Next Topic
**264. Deploy on AWS ECS + Docker** — Node app को Dockerize करना, ECR, ECS task definitions, और Fargate पर serverless containers।
