# 7. DevOps Tools Overview
# हिंदी में: DevOps Tools का परिचय

---

## 🔵 Simple Definition (English)
DevOps tools are the software used at each stage of delivery: version control (Git), CI/CD (GitHub Actions, Jenkins), containers (Docker, Kubernetes), infrastructure as code (Terraform, Ansible), cloud (AWS), web servers (Nginx) and monitoring (Prometheus, Grafana). No single tool is "DevOps"; you chain them into a toolchain.

## 🔵 सरल परिभाषा (Hindi)
DevOps tools वे software हैं जो delivery के हर stage में इस्तेमाल होते हैं: version control (Git), CI/CD (GitHub Actions, Jenkins), containers (Docker, Kubernetes), infrastructure as code (Terraform, Ansible), cloud (AWS), web servers (Nginx) और monitoring (Prometheus, Grafana)। कोई एक tool "DevOps" नहीं है; आप इन्हें जोड़कर toolchain बनाते हैं।

---

## 🔴 Problem it Solves
Beginners get lost in hundreds of tool logos. Without a map you may learn Kubernetes before Docker, or buy a tool that duplicates what you have. A categorized overview shows which problem each tool solves and what is the minimum set for a small team.

## 🔴 यह क्यों बना? (Hindi)
Beginners सैकड़ों tool logos में खो जाते हैं। नक्शे के बिना आप Docker से पहले Kubernetes सीख लेते हैं या ऐसा tool ले लेते हैं जो आपके पास पहले से है। Category के हिसाब से overview बताता है कि कौन सा tool कौन सी problem हल करता है और छोटी team के लिए न्यूनतम set क्या है।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Source control : Git + GitHub / GitLab (code, PRs, reviews)
Step 2 -> CI/CD          : GitHub Actions, GitLab CI, Jenkins (build, test, deploy)
Step 3 -> Packaging      : Docker, container registry (GHCR, Docker Hub, ECR)
Step 4 -> Orchestration  : Docker Compose (small), Kubernetes / ECS (large)
Step 5 -> Infrastructure : Terraform (provision), Ansible (configure servers)
Step 6 -> Cloud/Hosting  : AWS (EC2, S3, RDS, ECS), VPS (DigitalOcean, Hetzner)
Step 7 -> Web/Proxy      : Nginx, Traefik, Caddy, AWS ALB
Step 8 -> Observability  : Prometheus, Grafana, Loki, CloudWatch, Sentry
Step 9 -> Security       : Trivy, Dependabot, SonarQube, Vault / AWS Secrets Manager
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> Source control : Git + GitHub / GitLab (code, PRs, reviews)
Step 2 -> CI/CD          : GitHub Actions, GitLab CI, Jenkins (build, test, deploy)
Step 3 -> Packaging      : Docker, container registry (GHCR, Docker Hub, ECR)
Step 4 -> Orchestration  : Docker Compose (छोटे के लिए), Kubernetes / ECS (बड़े के लिए)
Step 5 -> Infrastructure : Terraform (बनाने के लिए), Ansible (server configure)
Step 6 -> Cloud/Hosting  : AWS (EC2, S3, RDS, ECS), VPS (DigitalOcean, Hetzner)
Step 7 -> Web/Proxy      : Nginx, Traefik, Caddy, AWS ALB
Step 8 -> Observability  : Prometheus, Grafana, Loki, CloudWatch, Sentry
Step 9 -> Security       : Trivy, Dependabot, SonarQube, Vault / AWS Secrets Manager
```

---

## 🟡 Real World Example
**A 3-person startup (React + FastAPI + Node worker)** picks the minimum toolchain: GitHub (code + Actions), Docker + GHCR, one VPS with Docker Compose and Nginx, Uptime Kuma for alerts, Sentry for errors. Total cost: a few dollars a month. A large company like Netflix uses the same ideas at scale with Kubernetes, Spinnaker, Terraform and custom monitoring.

## 🟡 Real Example Hindi mein
**3 लोगों का startup (React + FastAPI + Node worker)** न्यूनतम toolchain चुनता है: GitHub (code + Actions), Docker + GHCR, एक VPS पर Docker Compose और Nginx, alerts के लिए Uptime Kuma, errors के लिए Sentry। कुल खर्च: महीने के कुछ dollars। Netflix जैसी बड़ी कंपनी वही विचार बड़े पैमाने पर Kubernetes, Spinnaker, Terraform और custom monitoring से करती है।

---

## 💻 Code / Config Example — Basic
A script that checks which DevOps tools are installed on a machine.

```bash
#!/usr/bin/env bash
# check-tools.sh - report which DevOps tools exist on this machine
for tool in git docker node python3 nginx terraform kubectl aws gh; do   # loop over tool names
  if command -v "$tool" >/dev/null 2>&1; then                            # is the command found in PATH?
    printf '%-10s OK   %s\n' "$tool" "$(command -v "$tool")"             # print name and path
  else
    printf '%-10s MISSING\n' "$tool"                                     # tool not installed
  fi
done
```

## 💻 Code / Config Example — Advanced
One compose file showing toolchain pieces: app, Nginx proxy and monitoring (example images and tags, update them).

```yaml
# docker-compose.yml - app + proxy + monitoring on one VPS
services:                                        # all containers
  api:                                           # FastAPI or Node app
    image: ghcr.io/you/api:1.0.0                 # built by CI, stored in GHCR (replace "you")
    restart: unless-stopped                      # auto restart
    env_file: .env                               # secrets from server file
    expose:
      - "8000"                                   # reachable by other containers only, not published
    networks: [web]                              # shared network
  nginx:                                         # reverse proxy
    image: nginx:1.27-alpine                     # small official image (example tag)
    restart: unless-stopped                      # auto restart
    ports:
      - "80:80"                                  # HTTP
      - "443:443"                                # HTTPS
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro   # config from Git, read-only
    depends_on: [api]                            # start after api
    networks: [web]                              # same network
  prometheus:                                    # metrics collector
    image: prom/prometheus:v2.53.0               # example tag
    restart: unless-stopped                      # auto restart
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro   # scrape config
    networks: [web]                              # same network
  grafana:                                       # dashboards
    image: grafana/grafana:11.1.0                # example tag
    restart: unless-stopped                      # auto restart
    ports:
      - "127.0.0.1:3001:3000"                    # reachable only via SSH tunnel or Nginx auth
    networks: [web]                              # same network
networks:
  web: {}                                        # default bridge network named web
```

---

## 🟠 My Stack Integration
| Need | Recommended pick for you | Alternative |
|------|--------------------------|-------------|
| Code + CI/CD | GitHub + Actions | GitLab CI, Jenkins |
| Containers | Docker + Compose | Podman |
| Registry | GHCR | Docker Hub, AWS ECR |
| Reverse proxy | Nginx | Caddy, Traefik |
| TLS | Let's Encrypt (certbot) | AWS ACM |
| IaC | Terraform (AWS) | Pulumi, CloudFormation |
| Config mgmt | Ansible (VPS hardening) | cloud-init |
| Monitoring | Prometheus + Grafana, Uptime Kuma | CloudWatch, Datadog |
| Errors | Sentry | Rollbar |
| Secrets | GitHub Secrets, AWS Secrets Manager | Vault |

```yaml
# Dependabot keeps your tool/dependency versions current - .github/dependabot.yml
version: 2                                       # config schema version
updates:
  - package-ecosystem: npm                       # watch npm packages
    directory: "/"                               # package.json location
    schedule:
      interval: weekly                           # check weekly
  - package-ecosystem: github-actions            # watch action versions in workflows
    directory: "/"                               # workflows live under .github
    schedule:
      interval: weekly                           # check weekly
  - package-ecosystem: docker                    # watch Dockerfile base images
    directory: "/"                               # Dockerfile location
    schedule:
      interval: weekly                           # check weekly
```
Security: tools themselves are attack surface. Pin versions, update regularly, restrict ports (Grafana/Prometheus never open to the internet without auth), and keep tokens least-privilege.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Learning Kubernetes first.
✅ Correct: Order: Linux, Git, Docker, CI/CD, Compose, cloud, then Terraform and Kubernetes.

❌ Mistake 2: Adopting many tools for a tiny project.
✅ Correct: Start with the smallest toolchain that solves today's problems.

❌ Mistake 3: Tools without ownership or docs.
✅ Correct: Every tool has an owner and a short runbook.

❌ Mistake 4: Exposing monitoring dashboards publicly.
✅ Correct: Bind to localhost or put behind VPN/authentication.

---

## 🧠 Tricky Interview Question
**"Jenkins or GitHub Actions? Which would you pick and why?"**

Answer: It depends. For a team already on GitHub with simple pipelines, GitHub Actions: no server to maintain, huge marketplace, tight PR integration. Jenkins fits when you need full control, self-hosted runners at large scale, many legacy plugins or air-gapped networks, at the cost of maintaining the server, plugins and security patches. Good answer: state trade-offs, not a brand preference.

---

## ⚫ Interview Questions + Answers

Q1: Group DevOps tools by category.
A1: Version control, CI/CD, containers and orchestration, IaC and config management, cloud, proxy/web server, monitoring and logging, security.

Q2: Terraform vs Ansible?
A2: Terraform provisions infrastructure (create EC2, VPC, RDS) declaratively with state. Ansible configures servers (install packages, copy files) agentlessly via SSH. They are often used together.

Q3: Docker vs Kubernetes?
A3: Docker packages and runs containers on one host. Kubernetes orchestrates many containers across many nodes (scheduling, scaling, self-healing).

Q4: What is the difference between Prometheus and Grafana?
A4: Prometheus collects and stores metrics and fires alerts; Grafana visualizes data from Prometheus and other sources as dashboards.

Q5: Minimum toolchain for a small app on a VPS?
A5: Git/GitHub, GitHub Actions, Docker + Compose, Nginx + Let's Encrypt, a registry (GHCR), and a simple uptime and log monitor.

---

## 🔷 When to Use + When Not to Use
✅ Use a tool when:
- It solves a pain you actually have now.
- Your team can operate it (updates, backups, security).

❌ Avoid when:
- It is chosen only because it is popular ("resume-driven development").
- The managed alternative costs less than your time to run it.

---

## 📊 Visual Diagram
```
 CODE        BUILD/TEST     PACKAGE      DEPLOY        RUN            WATCH
+-----+     +----------+   +--------+   +-------+   +---------+   +------------+
| Git |---->| GitHub   |-->| Docker |-->| Compose|->| VPS/AWS |-->| Prometheus |
|GitHub|    | Actions  |   | + GHCR |   | / K8s |   | + Nginx |   | Grafana    |
+-----+     +----------+   +--------+   +-------+   +----+----+   | Sentry     |
                                 ^                         |       +------+-----+
                  Terraform / Ansible (infra as code)------+              |
                                 ^________ feedback ____________________|
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Toolchain | Tools chained across the lifecycle | Lifecycle भर जुड़े tools |
| Registry | Storage for container images | Container images का भंडार |
| Orchestration | Managing many containers automatically | कई containers का automatic प्रबंधन |
| IaC | Infrastructure defined in code | Code में infrastructure |
| Observability | Metrics, logs and traces to understand systems | System समझने के लिए metrics, logs, traces |
| Reverse proxy | Server forwarding requests to apps | Requests को apps तक भेजने वाला server |

---

## ⚡ 3-Line Summary
English: DevOps tools are organized by lifecycle stage: Git, CI/CD, Docker, IaC, cloud, proxy, monitoring.
You chain a small toolchain, not buy everything.
Learn in order: Linux, Git, Docker, CI/CD, then cloud, Terraform, Kubernetes.

Hindi: DevOps tools lifecycle stage के हिसाब से बँटे हैं: Git, CI/CD, Docker, IaC, cloud, proxy, monitoring।
छोटा toolchain जोड़ें, सब कुछ न खरीदें।
क्रम से सीखें: Linux, Git, Docker, CI/CD, फिर cloud, Terraform, Kubernetes।

---

## ➡️ Next Topic
**8. Infrastructure as Code (IaC)** — the tool category that turns servers into versioned files.
