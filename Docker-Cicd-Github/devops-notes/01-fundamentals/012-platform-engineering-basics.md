# 12. Platform Engineering Basics
# हिंदी में: Platform Engineering की बुनियादी बातें

---

## 🔵 Simple Definition (English)
**Platform engineering** is building an internal platform (an Internal Developer Platform, IDP) that gives developers self-service, standardized ways to create services, deploy, get databases and see logs, without needing deep infrastructure knowledge. The platform team treats developers as customers and the platform as a product.

## 🔵 सरल परिभाषा (Hindi)
**Platform engineering** एक internal platform (Internal Developer Platform, IDP) बनाना है जो developers को self-service और मानकीकृत तरीके देता है: नई service बनाना, deploy करना, database लेना, logs देखना, बिना गहरे infrastructure ज्ञान के। Platform team developers को ग्राहक और platform को product मानती है।

---

## 🔴 Problem it Solves
"You build it, you run it" is great, but it can overload developers: each team learns Kubernetes, Terraform, CI/CD and security separately and builds 20 different pipelines. This causes high cognitive load, duplicated work, inconsistent security and slow onboarding. Or developers file tickets to a central ops team and wait days. A platform offers a "paved road": the easy path is also the secure and standard path.

## 🔴 यह क्यों बना? (Hindi)
"You build it, you run it" बढ़िया है, लेकिन developers पर बोझ बढ़ा सकता है: हर team अलग से Kubernetes, Terraform, CI/CD और security सीखती है और 20 अलग pipelines बनती हैं। इससे cognitive load, दोहराया काम, असंगत security और धीमा onboarding होता है। या developers central ops team को tickets देकर दिनों इंतज़ार करते हैं। Platform एक "paved road" देता है: आसान रास्ता ही सुरक्षित और मानक रास्ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Talk to developers: find their biggest pains (slow setup, flaky deploys)
Step 2 -> Build "golden paths": templates for a new service (repo + Dockerfile + CI + deploy + monitoring)
Step 3 -> Offer self-service: developer picks a template in a portal / CLI / PR
Step 4 -> Platform automates: creates repo, pipeline, cloud resources, DNS, dashboards
Step 5 -> Guardrails built in: security scans, cost tags, policies (no opt-in needed)
Step 6 -> Developers deploy and run their service on the platform
Step 7 -> Platform team measures adoption, lead time, satisfaction and improves it like a product
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> Developers से बात करो: सबसे बड़ी तकलीफ़ें ढूँढो (धीमा setup, flaky deploys)
Step 2 -> "Golden paths" बनाओ: नई service के templates (repo + Dockerfile + CI + deploy + monitoring)
Step 3 -> Self-service दो: developer portal / CLI / PR से template चुनता है
Step 4 -> Platform automate करता है: repo, pipeline, cloud resources, DNS, dashboards बनाता है
Step 5 -> Guardrails पहले से: security scans, cost tags, policies (opt-in नहीं चाहिए)
Step 6 -> Developers platform पर अपनी service deploy और run करते हैं
Step 7 -> Platform team adoption, lead time, satisfaction नापकर product की तरह सुधारती है
```

---

## 🟡 Real World Example
**Spotify's Backstage** is an open-source developer portal: a developer clicks "Create new Node.js service", fills a form, and gets a repo with CI, Dockerfile, Kubernetes manifests, monitoring and docs in minutes. A company with 200 services uses the same template, so a security fix to the template can be rolled to all services.

**Your scale (solo/small team):** a "mini platform" is a GitHub **template repository** and a **reusable workflow** that every new service uses, so each new FastAPI or Node service gets CI/CD in 5 minutes.

## 🟡 Real Example Hindi mein
**Spotify का Backstage** एक open-source developer portal है: developer "Create new Node.js service" पर click करता है, form भरता है, और मिनटों में CI, Dockerfile, Kubernetes manifests, monitoring और docs वाला repo पाता है। 200 services वाली कंपनी एक ही template इस्तेमाल करती है, इसलिए template में security fix सभी services तक पहुँच सकता है।

**आपका scale (अकेले/छोटी team):** "mini platform" यानी GitHub **template repository** और **reusable workflow** जिसे हर नई service इस्तेमाल करे, ताकि हर नई FastAPI या Node service को 5 मिनट में CI/CD मिल जाए।

---

## 💻 Code / Config Example — Basic
A reusable GitHub Actions workflow owned by the "platform" repo, called by service repos with 3 lines.

```yaml
# In repo "platform": .github/workflows/node-ci.yml  (the golden path)
name: Node CI (reusable)                       # workflow name
on:
  workflow_call:                               # makes this workflow callable from other workflows
    inputs:
      node-version:                            # parameter with default
        type: string                           # value type
        default: "20"                          # default Node version
jobs:
  ci:
    runs-on: ubuntu-latest                     # runner
    steps:
      - uses: actions/checkout@v4              # code
      - uses: actions/setup-node@v4            # Node
        with:
          node-version: ${{ inputs.node-version }}   # use the input
          cache: npm                           # cache
      - run: npm ci                            # install
      - run: npm test                          # test
```

```yaml
# In any service repo: .github/workflows/ci.yml
name: CI                                       # workflow name
on:
  pull_request:                                # run on PRs
jobs:
  call-platform:
    uses: your-org/platform/.github/workflows/node-ci.yml@main   # example path; pin to a tag in production
    with:
      node-version: "20"                       # override input if needed
```

## 💻 Code / Config Example — Advanced
A golden-path build + deploy workflow with guardrails built in: scan, immutable tag, environment approval. Services only pass inputs.

```yaml
# In repo "platform": .github/workflows/service-deploy.yml
name: Service deploy (reusable)                 # golden path for build + scan + deploy
on:
  workflow_call:
    inputs:
      image-name:                               # image to build, e.g. api
        type: string                            # value type
        required: true                          # must be passed
      environment:                              # staging or production
        type: string                            # value type
        required: true                          # must be passed
    secrets:
      VPS_SSH_KEY:                              # secret passed from the caller
        required: true                          # must be passed
      VPS_HOST:                                 # server address
        required: true                          # must be passed
permissions:
  contents: read                                # minimal token rights
  packages: write                               # push image
jobs:
  build-scan:
    runs-on: ubuntu-latest                      # runner
    steps:
      - uses: actions/checkout@v4               # code
      - run: docker build -t local/${{ inputs.image-name }}:scan .   # build locally for scan
      - uses: aquasecurity/trivy-action@0.24.0  # guardrail: image scan (example version)
        with:
          image-ref: local/${{ inputs.image-name }}:scan   # image to scan
          severity: CRITICAL                    # fail only on critical
          exit-code: "1"                        # fail the job when found
      - uses: docker/login-action@v3            # registry login
        with:
          registry: ghcr.io                     # host
          username: ${{ github.actor }}         # user
          password: ${{ secrets.GITHUB_TOKEN }} # token
      - uses: docker/build-push-action@v6       # build and push the real image
        with:
          context: .                            # context
          push: true                            # publish
          tags: ghcr.io/${{ github.repository_owner }}/${{ inputs.image-name }}:${{ github.sha }}   # immutable tag
  deploy:
    needs: build-scan                           # after scan and push
    runs-on: ubuntu-latest                      # runner
    environment: ${{ inputs.environment }}      # approval rules come from the environment
    steps:
      - name: Deploy over SSH                   # label
        env:
          KEY: ${{ secrets.VPS_SSH_KEY }}       # passed-in secret
          HOST: ${{ secrets.VPS_HOST }}         # passed-in host
        run: |                                  # shell script
          set -euo pipefail                     # strict mode
          install -m 600 /dev/null k            # key file, owner-only
          printf '%s\n' "$KEY" > k              # write key
          ssh -i k -o StrictHostKeyChecking=accept-new deploy@"$HOST" "cd /opt/app && IMAGE_TAG=${GITHUB_SHA} docker compose up -d"   # roll out
          rm -f k                               # cleanup
```

---

## 🟠 My Stack Integration
- Create three **template repos**: `template-node-api`, `template-fastapi`, `template-react-nginx`, each with Dockerfile, `.dockerignore`, CI calling the reusable workflow, `docker-compose.yml`, `/health` endpoint and `RUNBOOK.md`.
- **VPS:** a `deploy.sh` and a standard `/opt/<service>` layout so every service deploys the same way.
- **Nginx:** one shared config pattern: `server_name <service>.example.com` proxying to `127.0.0.1:<port>`; generate it from a template.
- **AWS:** a Terraform module `app-service` (ECR repo + ECS service + ALB rule + log group) used by each service.

```yaml
# Standard service file every template ships: service.yaml (your own convention)
name: orders-api                               # service name
owner: team-backend                            # who gets paged
tier: 2                                        # importance level
runtime: node                                  # node | fastapi | react
port: 3000                                     # container port
healthcheck: /health                           # path used by Nginx, compose and uptime checks
slo: "99.5"                                    # monthly availability target
```
Security: central templates are a big lever: patch the template once (non-root user, scans, pinned actions) and every new service starts safe. Also protect the platform repo itself (required reviews), since it runs with powerful secrets.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Building a platform nobody asked for.
✅ Correct: Start from developer pain; treat platform as a product with users and feedback.

❌ Mistake 2: Forcing everyone onto the platform with no escape.
✅ Correct: Make the golden path the easiest option; allow exceptions with reasons.

❌ Mistake 3: Platform team becomes a ticket queue again.
✅ Correct: Offer self-service; platform team builds tools, not manual approvals.

❌ Mistake 4: Over-engineering (Backstage + Kubernetes + service mesh) for 3 services.
✅ Correct: Start with templates and reusable workflows.

---

## 🧠 Tricky Interview Question
**"How is platform engineering different from a DevOps team? Isn't it just renamed ops?"**

Answer: A traditional "DevOps team" often becomes a service desk: developers file tickets, the team does the work. A platform team builds self-service products, so developers do the work themselves safely, with the platform team measuring adoption, onboarding time and developer satisfaction. Success is fewer tickets, not more. DevOps remains the culture; platform engineering is a way to scale it by reducing cognitive load.

---

## ⚫ Interview Questions + Answers

Q1: What is an Internal Developer Platform (IDP)?
A1: A set of tools, templates and APIs built by a platform team that lets developers self-serve infrastructure, deploys, environments and observability.

Q2: What is a golden path?
A2: An opinionated, supported, pre-built way to do a common task (new service, deploy, database) which is secure and standard by default. Developers can deviate but lose support.

Q3: Name tools used for platform engineering.
A3: Backstage (portal), Terraform/Crossplane (infrastructure), Argo CD (GitOps), reusable CI workflows, Helm templates, Port, Humanitec.

Q4: How do you measure platform success?
A4: Onboarding time for new service/developer, deployment frequency, lead time, ticket volume to platform team, adoption rate and developer satisfaction surveys.

Q5: What is cognitive load and why does it matter?
A5: The mental effort developers need for tasks outside their product (infra, security, pipelines). High load slows delivery and causes errors; platforms reduce it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- 10+ developers or many services with repeated infrastructure needs.
- Teams reinvent pipelines and security differently.

❌ Avoid (heavy platform) when:
- Solo developer or tiny team: use template repos and shared workflows only.
- You have no capacity to maintain the platform like a product.

---

## 📊 Visual Diagram
```
 Developers (customers)
      |  "I need a new API + DB"
      v
 +---------------- Internal Developer Platform ----------------+
 |  Portal / CLI  ->  Golden path templates                    |
 |  (self-service)   [repo][CI/CD][infra][monitoring][security]|
 +---------------------------+---------------------------------+
                             v
        Terraform / GitHub Actions / Docker / Kubernetes / AWS
                             v
                  Running, observable, secure service
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IDP | Internal Developer Platform | Developers का आंतरिक platform |
| Golden path | Supported, easy, standard route | समर्थित, आसान, मानक रास्ता |
| Self-service | Do it yourself without tickets | बिना ticket खुद करना |
| Cognitive load | Mental effort required | मानसिक बोझ |
| Guardrail | Built-in safety rule | पहले से बना सुरक्षा नियम |
| Template repo | Starter repo for new projects | नए projects का starter repo |

---

## ⚡ 3-Line Summary
English: Platform engineering builds self-service golden paths for developers.
It reduces cognitive load and bakes in security and standards.
Treat the platform as a product; start small with templates and reusable workflows.

Hindi: Platform engineering developers के लिए self-service golden paths बनाता है।
यह cognitive load घटाता है और security व standards पहले से जोड़ता है।
Platform को product मानें; templates और reusable workflows से छोटी शुरुआत करें।

---

## ➡️ Next Topic
**13. GitOps - What + Why** — a way to make Git the single source of truth for deployments, often the engine inside a platform.
