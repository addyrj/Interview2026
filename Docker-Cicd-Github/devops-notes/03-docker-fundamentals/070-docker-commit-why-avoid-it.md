# 70. docker commit (why avoid it)
# हिंदी में: docker commit (इसे क्यों avoid करें)

---

## 🔵 Simple Definition (English)
`docker commit CONTAINER IMAGE:TAG` saves a container's current writable layer as a new image layer, producing a new image from a modified running or stopped container. It works, but it creates unreproducible "snowflake" images, so it is discouraged in favour of a Dockerfile.

## 🔵 सरल परिभाषा (Hindi)
`docker commit CONTAINER IMAGE:TAG` container की मौजूदा writable layer को नई image layer के रूप में save करके एक नई image बनाता है। यह चलता है, पर इससे ऐसी "snowflake" images बनती हैं जिन्हें दोबारा बनाया नहीं जा सकता, इसलिए Dockerfile को प्राथमिकता दी जाती है।

---

## 🔴 Problem it Solves
Sometimes you configure something interactively inside a container (install a package, tweak a config) and want to capture that state quickly: for a demo, a one-off debugging snapshot, or evidence of a compromised container for forensics. `commit` answers that. The problem is the opposite side: using it as a build method hides what is inside the image, so nobody can review, rebuild or patch it.

## 🔴 यह क्यों बना? (Hindi)
कभी आप container के अंदर interactive तरीके से कुछ configure करते हो (package install, config बदलना) और उस state को जल्दी capture करना होता है: demo, एक बार का debugging snapshot, या compromised container का forensic सबूत। `commit` यही करता है। समस्या उल्टी तरफ है: इसे build method बनाने पर image के अंदर क्या है यह छुप जाता है, कोई review, rebuild या patch नहीं कर सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start container from base image (docker run -it ubuntu bash)
Step 2 → Change things manually (apt install, edit files)
Step 3 → docker commit -m "msg" -a "author" <container> myimg:v1
Step 4 → Docker takes the writable layer (what docker diff shows) as a new layer
Step 5 → New image = base layers + this layer, new image ID, with commit message in history
Step 6 → Volumes are NOT included; running processes/memory are NOT saved
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Base image से container चलाओ (docker run -it ubuntu bash)
Step 2 → हाथ से बदलाव करो (apt install, files edit)
Step 3 → docker commit -m "msg" -a "author" <container> myimg:v1
Step 4 → Docker writable layer (जो docker diff दिखाता है) को नई layer बना देता है
Step 5 → नई image = base layers + यह layer, नया image ID, history में commit message
Step 6 → Volumes save नहीं होते; चलते processes/memory भी save नहीं होते
```

---

## 🟡 Real World Example
A new DevOps hire installs `curl`, `vim` and edits `/etc/nginx/nginx.conf` inside a running container to fix an urgent issue, then commits it as `nginx:fixed` and deploys. Six months later the base image has a critical CVE, but no one remembers what was changed, there is no Dockerfile, and the image cannot be rebuilt on a newer base. The team loses a day reverse-engineering with `docker history`. A Dockerfile in Git would have taken 5 minutes. Legit use: a security team commits a compromised container to `evidence:case42` and then analyses it offline.

## 🟡 Real Example Hindi mein
एक नया DevOps engineer urgent issue में running container के अंदर `curl`, `vim` install करके `/etc/nginx/nginx.conf` edit करता है, फिर `nginx:fixed` नाम से commit करके deploy कर देता है। छह महीने बाद base image में critical CVE आता है, पर किसी को याद नहीं क्या बदला था, Dockerfile नहीं है, और नई base पर rebuild नहीं हो सकता। टीम का एक दिन `docker history` से reverse-engineer करने में जाता है। Git में Dockerfile होता तो 5 मिनट लगते। सही उपयोग: security team compromised container को `evidence:case42` commit करके offline analyse करती है।

---

## 💻 Code / Config Example — Basic
```bash
# ---- Basic docker commit (learning / forensics only) ----
docker run -it --name tmp alpine:3.20 sh              # start interactive container (example tag)
# inside the container:  apk add --no-cache curl && exit   # make a manual change, then leave
docker diff tmp                                       # review what will be captured (see topic 69)
docker commit -m "add curl" -a "addyrj" tmp alpine-curl:v1  # create image; -m message, -a author
docker history alpine-curl:v1                         # last row shows your commit message and size
docker run --rm alpine-curl:v1 curl --version         # verify the new image has curl
docker rm tmp                                         # remove the original container
```

## 💻 Code / Config Example — Advanced
The correct, reproducible replacement: put the same change in a Dockerfile.

```dockerfile
# Dockerfile -- reproducible version of "alpine + curl", reviewable in Git
# pinned base image (example tag, update regularly)
FROM alpine:3.20
# link image to its source repo
LABEL org.opencontainers.image.source="https://github.com/addyrj/demo"
# install curl, create non-root user in one layer
RUN apk add --no-cache curl \
    && addgroup -S app && adduser -S app -G app
# drop root privileges
USER app
# image behaves like the curl command
ENTRYPOINT ["curl"]
# default argument, overridable at run
CMD ["--version"]
```
```bash
# Forensics use of commit: preserve a suspicious container for later analysis
docker pause suspicious-api                        # freeze processes so state does not change
docker commit --pause=false suspicious-api evidence:case42   # snapshot filesystem without double pausing
docker save evidence:case42 | gzip > case42.tar.gz # export to a file for offline analysis
docker kill suspicious-api                         # stop the compromised container
```
Dockerfile checked by a simple instruction/syntax script; `commit` commands not run locally (no daemon). `--pause` is a real `docker commit` flag (default true).

---

## 🟠 My Stack Integration
Your deploy path should be Git, then Dockerfile, then CI build, then registry, then VPS. `commit` has no place in that chain, but it helps in incident response on the VPS.

```yaml
# .github/workflows/build.yml -- the proper replacement for "commit on the server"
name: build                                   # workflow name
on: [push]                                    # run on every push
jobs:                                         # jobs list
  image:                                      # job id
    runs-on: ubuntu-latest                    # runner
    steps:                                    # steps
      - uses: actions/checkout@v4             # get code (example version)
      - run: docker build -t ghcr.io/addyrj/api:${{ github.sha }} .   # reproducible build from Dockerfile
```
Hotfix on production? Fix the Dockerfile or code in Git, push, let CI build and tag a new version. Use `commit` only to freeze a compromised container, then redeploy clean.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Building production images by `commit` after manual setup.
✅ Correct: Write a Dockerfile; every change reviewed in Git.

❌ Mistake 2: Committing a container that holds secrets, tokens or `.env`, then pushing it.
✅ Correct: Inspect with `docker diff`/`history`; never push committed images publicly; scan with Trivy.

❌ Mistake 3: Expecting volume data or running processes to be saved.
✅ Correct: Commit captures only the filesystem layer; back up volumes separately.

❌ Mistake 4: Committing over and over, growing layers (each commit adds a layer, deleted files still take space).
✅ Correct: Rebuild from Dockerfile with multi-stage and cleanup in the same `RUN`.

---

## 🧠 Tricky Interview Question
You `docker commit` a container where you ran `rm -rf /var/cache/*` after installing 400 MB of packages. The new image is still 400 MB bigger. Why?

Answer: Layers are additive. The installation data already exists in the base-plus-previous layers or the earlier writable changes; deletions are stored as whiteouts in a later layer and do not shrink earlier layers. Only a rebuild with install and cleanup inside the same `RUN` instruction (or multi-stage build) removes the data from the final image.

---

## ⚫ Interview Questions + Answers

Q1: What does `docker commit` save and not save?
A1: Saves the container's filesystem changes (writable layer), plus optional config changes via `--change`. It does not save volumes, memory or running processes.

Q2: Why is it considered bad practice for production?
A2: It is not reproducible, not reviewable, hides changes, cannot be easily updated for CVEs, and grows layers.

Q3: Valid uses?
A3: Forensics of compromised containers, quick demos/training, debugging snapshots, capturing a manual proof-of-concept before writing the Dockerfile.

Q4: What does `--change` do?
A4: Applies Dockerfile instructions like `CMD`, `ENV`, `EXPOSE`, `ENTRYPOINT` to the committed image, e.g. `--change 'CMD ["nginx","-g","daemon off;"]'`.

Q5: Alternative to commit for reproducibility?
A5: Dockerfile + CI build, or `docker buildx` with cache; for infrastructure-level provisioning use Ansible/Terraform scripts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Preserving a compromised container for forensics.
- Taking a temporary debug snapshot.
- Prototyping before writing a Dockerfile.

❌ Avoid when:
- Producing images for staging or production.
- Anything others must rebuild or audit.
- Environments with compliance/SBOM requirements.

---

## 📊 Visual Diagram
```
  BAD:   base image --run--> container --manual edits--> docker commit --> mystery image
                                  (no record in Git)

  GOOD:  Git (Dockerfile) --> CI docker build --> registry --> VPS pull
             reviewed             reproducible       tagged      identical bytes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Snowflake image | Unique, unreproducible image | अद्वितीय, दोबारा न बनने वाली image |
| Reproducible build | Same input gives same image | वही input, वही image |
| Forensics | Evidence analysis after incident | घटना के बाद सबूत जाँच |
| Whiteout | Deleted-file marker in layer | हटाई file का marker |
| `--change` | Apply Dockerfile instruction on commit | Commit पर Dockerfile instruction लगाना |
| Immutable infra | Replace, don't patch servers | Patch नहीं, replace |

---

## ⚡ 3-Line Summary
English: `docker commit` turns a container's changes into an image. It is fine for forensics and quick demos but breaks reproducibility. Use Dockerfile and CI for everything real.
Hindi: `docker commit` container के बदलावों को image बना देता है। Forensics और quick demo के लिए ठीक है पर reproducibility तोड़ता है। असली काम के लिए Dockerfile और CI इस्तेमाल करो।

---

## ➡️ Next Topic
**71. Dockerfile: Complete Guide** — commit का सही विकल्प: image बनाने की पूरी recipe, instruction by instruction।
