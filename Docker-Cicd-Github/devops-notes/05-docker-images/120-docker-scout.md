# 120. Docker Scout
# हिंदी में: Docker Scout (Docker का अपना security और supply chain tool)

---

## 🔵 Simple Definition (English)
Docker Scout is Docker's own image analysis service. It builds an inventory of what is inside an image (an SBOM), matches it to vulnerability data, and tells you which base image update or package bump fixes the most problems.

## 🔵 सरल परिभाषा (Hindi)
Docker Scout, Docker की अपनी image analysis service है। यह image के अंदर की चीज़ों की सूची (SBOM) बनाती है, vulnerability data से मिलाती है, और बताती है कि कौन सा base image update या package bump सबसे ज़्यादा समस्याएँ ठीक करेगा।

---

## 🔴 Problem it Solves
- Raw CVE lists are long. Developers need "what do I change?", not just "what is broken?".
- Teams want policy checks ("no critical CVE, non-root user, up to date base image") tracked over time.
- Docker Hub and Docker Desktop users want scanning without installing separate tools.
- Comparing two images (old vs new) to see what changed is hard by hand.

## 🔴 यह क्यों बना? (Hindi)
- CVE की raw सूची लंबी होती है। Developer को "क्या बदलूँ?" जानना होता है, सिर्फ "क्या टूटा है?" नहीं।
- Teams policy checks ("कोई critical CVE नहीं, non-root user, base image अप-टू-डेट") समय के साथ track करना चाहती हैं।
- Docker Hub और Docker Desktop users बिना अलग tool install किए scanning चाहते हैं।
- दो images (पुरानी vs नई) की तुलना हाथ से मुश्किल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker scout quickview myorg/api:1.0.0 (or open Docker Desktop / Hub)
Step 2 → Scout indexes the image: OS packages, language packages, base image, provenance
Step 3 → It compares them with its advisory database (updated continuously)
Step 4 → quickview = summary; cves = full list; recommendations = which base image to move to
Step 5 → compare = diff between two images (new vs production)
Step 6 → In CI: docker scout cves --exit-code --only-severity critical,high fails the build
Step 7 → Policies (org level, in Docker Scout dashboard) show pass/fail per image over time
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप चलाते हैं: docker scout quickview myorg/api:1.0.0 (या Docker Desktop / Hub खोलें)
Step 2 → Scout image index करता है: OS packages, language packages, base image, provenance
Step 3 → इन्हें अपने advisory database से मिलाता है (लगातार update होता है)
Step 4 → quickview = सारांश; cves = पूरी सूची; recommendations = किस base image पर जाएँ
Step 5 → compare = दो images का अंतर (नई vs production)
Step 6 → CI में: docker scout cves --exit-code --only-severity critical,high build fail करता है
Step 7 → Policies (org स्तर पर, Scout dashboard में) हर image का pass/fail समय के साथ दिखाती हैं
```

---

## 🟡 Real World Example
A team on Docker Hub pushes `myorg/api`. Scout shows 2 critical CVEs, and its recommendation says "switch base `node:20.10` to `node:20.18-slim`: removes 2 critical, 7 high, and shrinks the image". The developer changes one line in the Dockerfile. In CI a `docker scout compare` step comments on the pull request that the new image has fewer vulnerabilities than what runs in production, so the reviewer approves quickly.

## 🟡 Real Example Hindi mein
एक team Docker Hub पर `myorg/api` push करती है। Scout 2 critical CVE दिखाता है और सुझाव देता है "base `node:20.10` से `node:20.18-slim` पर जाएँ: 2 critical और 7 high हटेंगे और image छोटी होगी"। Developer Dockerfile की एक line बदलता है। CI में `docker scout compare` step PR पर बताता है कि नई image में production वाली से कम vulnerabilities हैं, तो reviewer जल्दी approve कर देता है।

---

## 💻 Code / Config Example — Basic
```bash
# Scout ships as a Docker CLI plugin with recent Docker Desktop. Check it exists:
docker scout version

# Log in first (Docker Hub account; some features need a paid plan, check current pricing)
docker login

# One screen summary: vulnerabilities by severity + base image status
docker scout quickview myorg/api:1.0.0

# Full CVE list, only the serious ones
docker scout cves --only-severity critical,high myorg/api:1.0.0

# Ask which base image update helps most
docker scout recommendations myorg/api:1.0.0

# Analyse a LOCAL build directly from the image store (no push needed)
docker scout cves local://myorg/api:dev

# Compare a new image with the one in production
docker scout compare --to myorg/api:prod myorg/api:1.1.0

# Scan a project directory/tar as well (fs:// prefix)
docker scout cves fs://.
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/scout.yml  (example action versions: verify before use)
name: scout                                    # workflow name
on:
  pull_request:                                # run on every PR
    branches: [main]                           # targeting main
permissions:
  contents: read                               # read the repo
  pull-requests: write                         # allow Scout to comment on the PR
jobs:
  scout:
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # fetch source
      - uses: docker/setup-buildx-action@v3    # buildx builder (needed for provenance/SBOM)
      - uses: docker/login-action@v3           # log in so Scout can read your org data
        with:
          username: ${{ secrets.DOCKERHUB_USER }}      # Docker Hub user from secrets
          password: ${{ secrets.DOCKERHUB_TOKEN }}    # access TOKEN, not your password
      - name: Build image locally, do not push
        uses: docker/build-push-action@v6      # builds with buildx
        with:
          context: ./api                       # folder with Dockerfile
          load: true                           # load into local docker so Scout can see it
          tags: myorg/api:pr-${{ github.event.number }}   # temp tag for this PR
          provenance: mode=max                 # attach build provenance attestation
          sbom: true                           # attach SBOM attestation
      - name: Scout compare with production
        uses: docker/scout-action@v1           # official Scout action
        with:
          command: compare                     # compare two images
          image: myorg/api:pr-${{ github.event.number }}   # new image
          to: myorg/api:prod                   # baseline tag in the registry
          only-severities: critical,high       # focus on serious findings
          exit-code: true                      # fail job if new image is worse (check semantics for your version)
          github-token: ${{ secrets.GITHUB_TOKEN }}        # lets Scout comment on the PR
```

```bash
# Quick CI gate in any pipeline that has the Scout CLI plugin
docker scout cves --exit-code --only-severity critical myorg/api:${GIT_SHA}   # non-zero exit if a critical CVE exists
```

---

## 🟠 My Stack Integration
- **Docker Hub users:** Scout is built into Hub and Docker Desktop, so images pushed there are analysed automatically after enabling the repo.
- **Node.js / FastAPI:** Scout reads language package manifests and suggests dependency upgrades as well as base image changes.
- **React:** scan the final `nginx:alpine` runtime image; it is small and clean.
- **GHCR / ECR / VPS:** Scout can analyse images in other registries after integration, or you can run `docker scout cves local://` on the build machine. If you do not use Docker Hub, Trivy (note 119) is often simpler.

```yaml
# docker-compose.yml fragment: label images so Scout/other tools show source info
services:
  api:                                         # Node.js / FastAPI service
    image: myorg/api:${GIT_SHA}                # SHA tag, so Scout results map to a commit
    labels:
      org.opencontainers.image.source: "https://github.com/myorg/api"   # link back to repo
      org.opencontainers.image.revision: "${GIT_SHA}"                   # exact commit
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming Scout is free for everything.
✅ Correct: Features and repo counts depend on your Docker plan. Check current limits; keep Trivy as a free fallback.

❌ Mistake 2: Running `docker scout` before `docker login` or without the plugin and thinking it is broken.
✅ Correct: Run `docker scout version`, then `docker login`.

❌ Mistake 3: Only reading CVE counts and ignoring "recommendations".
✅ Correct: Base image upgrades fix many CVEs with a single line change.

❌ Mistake 4: Using the account password in CI.
✅ Correct: Create an access token with minimal scope and store it in GitHub Secrets.

---

## 🧠 Tricky Interview Question
Scout says your image has a CRITICAL CVE in a package that your app never calls. Do you still fix it?

Answer: Usually yes, because exploitability changes (new code, other containers in the same image) and compliance tools count it. But prioritise by reachability: if no fix exists, record a VEX statement or documented exception with expiry; if a fix exists (often just a base image bump), apply it. Scout's recommendation view shows the cheapest fix first.

---

## ⚫ Interview Questions + Answers

Q1: What does Docker Scout do beyond listing CVEs?
A1: It recommends base image updates, compares images, tracks policies and supports SBOM/provenance data.

Q2: How do you see the CVEs of an image that is not pushed yet?
A2: `docker scout cves local://myorg/api:dev` reads the local image store.

Q3: How is Scout different from Trivy?
A3: Trivy is a standalone open source scanner usable anywhere. Scout is a Docker service integrated with Hub/Desktop that adds recommendations and policy tracking, with plan-based limits.

Q4: What does `docker scout compare` help with?
A4: It shows the diff between two images (packages added, CVEs fixed or introduced), useful in pull request reviews.

Q5: Why use `provenance` and `sbom` flags when building?
A5: They attach attestations describing how and from what the image was built, which Scout and other tools can read to give better results.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your images are on Docker Hub and your team uses Docker Desktop.
- You want upgrade recommendations and policy dashboards.
- You need PR comments comparing vulnerabilities.

❌ Avoid when:
- You need a fully open source tool with no account (use Trivy/Grype).
- You are in an air-gapped network that cannot reach Docker services.

---

## 📊 Visual Diagram
```
 docker build / push
        |
        v
  +-------------+     SBOM + provenance      +------------------+
  | Image       | -------------------------> | Docker Scout     |
  | (layers)    |                            | index + advisory |
  +-------------+                            +------------------+
                                                 |      |      |
                                      quickview  |  cves|  recommendations
                                                 v      v      v
                                           summary   list   "use node:20.18-slim"
                                                 \      |      /
                                                  v     v     v
                                            Policy: PASS / FAIL  -> PR comment / CI gate
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Docker Scout | Docker's image analysis service | Docker की image विश्लेषण service |
| Quickview | One screen summary of an image | image का संक्षिप्त सारांश |
| Recommendation | Suggested base image/package change | सुझाया गया बदलाव |
| Policy | Rule the image must meet | नियम जिसे image को पूरा करना है |
| Attestation | Signed statement about a build | build के बारे में प्रमाणित बयान |
| Provenance | Record of where/how image was built | image कहाँ और कैसे बनी इसका रिकॉर्ड |

---

## ⚡ 3-Line Summary
English: Scout analyses images, lists CVEs and recommends the best base image fix.
English: `quickview`, `cves`, `recommendations` and `compare` are the key commands.
English: Plan limits apply; keep Trivy as an open source alternative.
Hindi: Scout images को जाँचता है, CVE बताता है और सबसे अच्छा base image सुधार सुझाता है।
Hindi: `quickview`, `cves`, `recommendations` और `compare` मुख्य commands हैं।
Hindi: Plan की सीमाएँ हैं; open source विकल्प के रूप में Trivy रखें।

---

## ➡️ Next Topic
**121. SBOM — Software Bill of Materials** — the inventory list Scout and Trivy build from: what exactly is inside your image, as a file you can store and audit.
