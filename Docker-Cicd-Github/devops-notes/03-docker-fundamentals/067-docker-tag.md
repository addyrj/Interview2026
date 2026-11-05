# 67. docker tag
# हिंदी में: docker tag (Image को नाम और version देना)

---

## 🔵 Simple Definition (English)
`docker tag SOURCE TARGET` creates an additional name (alias) for an existing image. It does not copy data; both names point to the same image ID. A full name looks like `registry/namespace/repo:tag`.

## 🔵 सरल परिभाषा (Hindi)
`docker tag SOURCE TARGET` किसी मौजूदा image को एक और नाम (alias) देता है। इससे data copy नहीं होता; दोनों नाम एक ही image ID को point करते हैं। पूरा नाम ऐसा दिखता है: `registry/namespace/repo:tag`।

---

## 🔴 Problem it Solves
An image built as `myapp` has no version and no registry address. You could not tell which build is in production, could not roll back, and could not push to GHCR or ECR (the registry host is part of the name). Tags solve versioning (`1.4.2`, git SHA), environment promotion (`staging` to `prod`) and routing to the right registry.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ `myapp` नाम की image में न version होता है न registry का पता। तब यह पता नहीं चलता कि production में कौन सा build है, rollback नहीं हो सकता, और GHCR/ECR पर push भी नहीं हो सकता (registry host नाम का हिस्सा है)। Tags versioning (`1.4.2`, git SHA), environment promotion (`staging` से `prod`) और सही registry तक पहुँचाने की समस्या हल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Image exists locally with ID (e.g. 3f2a9c1d7b44)
Step 2 → docker tag myapp:latest ghcr.io/addyrj/myapp:1.4.2
Step 3 → Docker adds a new reference in its local image store (no layer copy)
Step 4 → docker images shows two rows with the SAME IMAGE ID
Step 5 → docker push uses the name's registry part to decide where to upload
Step 6 → docker rmi on one name only removes that tag; layers stay while another tag exists
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image local में है, ID जैसे 3f2a9c1d7b44
Step 2 → docker tag myapp:latest ghcr.io/addyrj/myapp:1.4.2
Step 3 → Docker local image store में नया reference जोड़ता है (layers copy नहीं होतीं)
Step 4 → docker images में दो rows दिखती हैं, IMAGE ID एक ही
Step 5 → docker push नाम के registry हिस्से से तय करता है कहाँ upload करना है
Step 6 → docker rmi एक नाम हटाता है; दूसरा tag रहने तक layers रहती हैं
```

---

## 🟡 Real World Example
A Swiggy-like team builds one image per commit, tags it with the git SHA (`api:9fceb02`) for traceability, and also with the semver `api:2.7.0` when a release is cut. After QA passes in staging, the same image (same digest) is re-tagged `api:prod` and pushed, so what was tested is exactly what runs. On your VPS you can roll back by running `api:2.6.3` again in seconds.

## 🟡 Real Example Hindi mein
Swiggy जैसी team हर commit पर एक image बनाती है, traceability के लिए git SHA (`api:9fceb02`) tag लगाती है, और release पर semver `api:2.7.0` भी। Staging में QA pass होने पर वही image (वही digest) `api:prod` से re-tag होकर push होती है, यानी जो test हुआ वही चलता है। VPS पर rollback के लिए `api:2.6.3` दोबारा चला दो, कुछ seconds लगते हैं।

---

## 💻 Code / Config Example — Basic
```bash
# ---- Basic tagging ----
docker build -t myapp .                                   # build image, default tag is "latest"
docker tag myapp:latest myapp:1.0.0                       # add version tag (same image ID)
docker tag myapp:latest addyrj/myapp:1.0.0                # Docker Hub style name: user/repo:tag
docker tag myapp:latest ghcr.io/addyrj/myapp:1.0.0        # GHCR style name: host/user/repo:tag
docker images | grep myapp                                # confirm all names share one IMAGE ID
docker rmi myapp:1.0.0                                    # remove only this alias; image stays
docker image inspect --format '{{.RepoTags}}' myapp:latest  # list every tag pointing to this image
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# tag-release.sh -- tag one build with SHA, semver and moving tags, then push all
set -euo pipefail                                # fail fast on errors/undefined variables
REGISTRY="ghcr.io/addyrj"                        # registry + namespace (example, change)
APP="api"                                        # repository name
VERSION="${1:?usage: tag-release.sh 1.4.2}"      # semver is mandatory first argument
SHA="$(git rev-parse --short=7 HEAD)"            # short commit id for traceability
docker build -t "$APP:build" .                   # build once with a temporary local name
for T in "$VERSION" "${VERSION%.*}" "$SHA"; do   # e.g. 1.4.2, 1.4, 9fceb02
  docker tag "$APP:build" "$REGISTRY/$APP:$T"    # attach each tag to the same image
  docker push "$REGISTRY/$APP:$T"                # push each tag (layers upload only once)
done
docker tag "$APP:build" "$REGISTRY/$APP:latest"  # moving tag, only for humans/dev, not for prod deploy
docker push "$REGISTRY/$APP:latest"              # push the moving tag
docker image inspect --format '{{index .RepoDigests 0}}' "$REGISTRY/$APP:$VERSION"  # print immutable digest to log
```
This script was syntax-checked with `bash -n` only; it needs Docker and a registry login to run.

---

## 🟠 My Stack Integration
Use one naming convention for all three apps so CI, Compose and Nginx deploys stay predictable.

```yaml
# docker-compose.prod.yml (on VPS) -- tags come from an env variable set by the deploy script
services:                                         # all containers of the stack
  api:                                            # FastAPI service
    image: ghcr.io/addyrj/api:${API_TAG}          # exact version, e.g. 9fceb02 (never latest in prod)
    restart: unless-stopped                       # restart after crash/reboot
  web:                                            # React build served by nginx
    image: ghcr.io/addyrj/web:${WEB_TAG}          # separate tag per service
    ports:                                        # published ports
      - "80:80"                                   # public HTTP, Nginx inside container
  node-worker:                                    # Node.js background worker
    image: ghcr.io/addyrj/worker:${WORKER_TAG}    # independent versioning
```
Rollback = set `API_TAG` to the previous SHA and run `docker compose up -d`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `latest` in production and assuming it means "newest".
✅ Correct: `latest` is only the default tag. Pin SHA or semver.

❌ Mistake 2: Uppercase letters or spaces in repository names (`MyApp`), which fail.
✅ Correct: Repository names must be lowercase; tags allow letters, digits, `_`, `.`, `-` (max 128 chars).

❌ Mistake 3: Forgetting the registry host and pushing to Docker Hub by accident.
✅ Correct: Always include `ghcr.io/...` or the ECR URI in the target name.

❌ Mistake 4: Thinking `docker tag` makes a backup copy.
✅ Correct: It is only a pointer; deleting the last tag leaves untagged layers that prune removes.

---

## 🧠 Tricky Interview Question
You tagged `api:1.0` yesterday, rebuilt today with changes and pushed `api:1.0` again. A server that pulled yesterday restarts its container. Which code runs?

Answer: Yesterday's, because the running container is bound to the old image ID it started from, and a restart does not re-pull. Tags are mutable pointers. Even a new `docker pull` would change the pointer, which is why overwriting version tags is dangerous. Use a new tag for every build or deploy by digest.

---

## ⚫ Interview Questions + Answers

Q1: Does `docker tag` duplicate image data?
A1: No. It only adds another name/reference to the same image ID.

Q2: What are the parts of a full image name?
A2: `registry-host[:port]/namespace/repository:tag`. If the host is omitted Docker assumes Docker Hub, if the tag is omitted it assumes `latest`.

Q3: How do you promote staging to production safely?
A3: Pull the tested image by digest or SHA, re-tag it as `prod`/release version and push. No rebuild, so the artifact is identical.

Q4: How can two tags point to one image?
A4: Each tag is an entry in the repository's tag-to-digest map; multiple entries can reference the same digest.

Q5: What is a dangling image?
A5: An image with no tag (`<none>:<none>`), usually left when a tag moved to a newer build. Clean with `docker image prune`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Preparing an image for push to a registry.
- Versioning releases and enabling rollback.
- Promoting the same artifact between environments.

❌ Avoid when:
- You rely on `latest` for deployment decisions.
- You want to change image content (tag cannot; rebuild instead).
- You overwrite release tags that others already pulled.

---

## 📊 Visual Diagram
```
                 IMAGE ID 3f2a9c1d7b44  (one set of layers)
                          ^
     +--------------------+----------------------+---------------------+
     |                    |                      |                     |
 myapp:latest   ghcr.io/addyrj/api:1.4.2   ...api:9fceb02      ...api:prod
   (alias)            (release)               (commit)          (environment)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tag | Label after colon on image name | Image नाम के बाद का label |
| Alias | Extra name for same image | Same image का दूसरा नाम |
| Image ID | Local short hash of image config | Image की local पहचान |
| Semver | MAJOR.MINOR.PATCH version | Version numbering नियम |
| Immutable tag | Tag never reassigned | जो tag कभी बदला नहीं जाता |
| Dangling | Image without any tag | बिना tag वाली image |

---

## ⚡ 3-Line Summary
English: `docker tag` adds another name to an image without copying data. Names carry registry, repo and version, so tags enable push, rollback and promotion. Never rely on `latest` in production.
Hindi: `docker tag` बिना data copy किए image को नया नाम देता है। नाम में registry, repo और version होता है, इसलिए tags से push, rollback और promotion संभव होता है। Production में `latest` पर निर्भर मत रहो।

---

## ➡️ Next Topic
**68. docker cp** — अब देखेंगे चलते या रुके container से files को host पर कैसे निकालें या अंदर डालें, debugging में काम आता है।
