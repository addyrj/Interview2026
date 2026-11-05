---

# 38. GitHub Packages
# हिंदी में: GitHub Packages (packages का अपना registry)

---

## 🔵 Simple Definition (English)
**GitHub Packages** is a package hosting service inside GitHub. It hosts npm, Maven/Gradle, NuGet, RubyGems and container images (via GHCR) next to your code, using GitHub permissions and `GITHUB_TOKEN` for authentication. (There is no native PyPI registry on GitHub Packages.)

## 🔵 सरल परिभाषा (Hindi)
**GitHub Packages** GitHub के अंदर package hosting service है। यह आपके code के पास ही npm, Maven/Gradle, NuGet, RubyGems और container images (GHCR के ज़रिए) host करती है, GitHub permissions और `GITHUB_TOKEN` से authentication के साथ। (GitHub Packages में native PyPI registry नहीं है।)

---

## 🔴 Problem it Solves
Teams need to share internal libraries (a shared TypeScript types package, an internal UI kit) without publishing them publicly on npmjs.com, and without running their own Verdaccio/Nexus server. Separate registries also mean separate users, tokens and permissions to manage. GitHub Packages reuses repo/org permissions and Actions integration.

## 🔴 यह क्यों बना? (Hindi)
Teams को internal libraries (shared TypeScript types, internal UI kit) share करनी होती हैं बिना npmjs.com पर public किए और बिना अपना Verdaccio/Nexus server चलाए। अलग registries का मतलब अलग users, tokens और permissions। GitHub Packages repo/org permissions और Actions integration दोबारा इस्तेमाल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Package name is scoped to owner: @OWNER/pkg  (npm) -- must be lowercase owner name
Step 2 → package.json: "name": "@acme/shared", "publishConfig": {"registry": "https://npm.pkg.github.com"}
Step 3 → Auth: .npmrc with //npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
Step 4 → In Actions: permissions: packages: write; token = secrets.GITHUB_TOKEN
Step 5 → npm publish -> package appears under repo/org -> Packages tab
Step 6 → Consumers add .npmrc: @acme:registry=https://npm.pkg.github.com and a token with read:packages
Step 7 → npm install @acme/shared works; visibility/permissions inherit from repo (or set separately)
Step 8 → Delete/restore versions from package settings; keep a retention policy
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Package का नाम owner से scoped होता है: @OWNER/pkg (npm) -- owner lowercase में
Step 2 → package.json: "name": "@acme/shared", "publishConfig": {"registry": "https://npm.pkg.github.com"}
Step 3 → Auth: .npmrc में //npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
Step 4 → Actions में: permissions: packages: write; token = secrets.GITHUB_TOKEN
Step 5 → npm publish -> package repo/org के Packages tab में दिखता है
Step 6 → इस्तेमाल करने वाले .npmrc में @acme:registry=https://npm.pkg.github.com और read:packages वाला token जोड़ते हैं
Step 7 → npm install @acme/shared चलता है; visibility/permissions repo से विरासत में मिलते हैं
Step 8 → package settings से versions delete/restore करो; retention policy रखो
```

---

## 🟡 Real World Example
A company has a React dashboard and a Node.js API both using shared validation schemas. They publish `@acme/shared-types` privately to GitHub Packages from a release workflow whenever a tag `v1.2.0` is pushed. The React repo installs it via `.npmrc` with a read-only token stored in Actions secrets. Docker images for the FastAPI service go to GHCR (topic 39). No extra server, billing or user management is needed, and access follows GitHub team membership.

## 🟡 Real Example Hindi mein
एक कंपनी में React dashboard और Node.js API दोनों shared validation schemas इस्तेमाल करते हैं। वे `@acme/shared-types` को private रूप से GitHub Packages पर release workflow से publish करते हैं जब tag `v1.2.0` push होता है। React repo इसे `.npmrc` और Actions secrets में रखे read-only token से install करती है। FastAPI service की Docker images GHCR (topic 39) में जाती हैं। कोई अतिरिक्त server, billing या user management नहीं; access GitHub team membership से चलता है।

---

## 💻 Code / Config Example — Basic

```json
{
  "name": "@acme/shared-types",
  "version": "1.0.0",
  "description": "Shared TypeScript types for web and api",
  "main": "index.js",
  "repository": { "type": "git", "url": "git+https://github.com/acme/shared-types.git" },
  "publishConfig": { "registry": "https://npm.pkg.github.com" },
  "files": ["index.js", "index.d.ts"]
}
```
```bash
# publish-manual.sh - manual publish from a laptop (CI is preferred)
# 1) Create a classic PAT with write:packages (and read:packages); export it, do not commit it
export NODE_AUTH_TOKEN="ghp_xxx_replace_me"          # your personal access token (placeholder)
# 2) Tell npm where the @acme scope lives and which token to send
printf '@acme:registry=https://npm.pkg.github.com\n//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}\n' > .npmrc   # note: single quotes keep ${...} literal
# 3) Publish the package
npm publish                                          # uses publishConfig.registry from package.json
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/publish-package.yml - publish on version tag, install in consumer job
name: Publish package                       # workflow name
on:
  push:
    tags: ["v*.*.*"]                        # run when a version tag like v1.2.0 is pushed
permissions:
  contents: read                            # read code
  packages: write                           # allow publishing to GitHub Packages
jobs:
  publish:                                  # job id
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - uses: actions/checkout@v4           # get code (example version)
      - uses: actions/setup-node@v4         # Node and registry auth
        with:
          node-version: 20                  # example LTS
          registry-url: https://npm.pkg.github.com   # writes .npmrc using NODE_AUTH_TOKEN
          scope: "@acme"                    # which scope maps to this registry (owner name lowercase)
      - run: npm ci                         # install dependencies
      - run: npm test                       # do not publish broken code
      - name: Verify tag matches package.json version   # guard against mismatched release
        run: |                              # shell
          PKG_VERSION=$(node -p "require('./package.json').version")   # read version
          test "v$PKG_VERSION" = "${GITHUB_REF_NAME}"                  # must equal pushed tag
      - run: npm publish                    # publish to GitHub Packages
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}   # built-in token; no PAT needed
  consume:                                  # job 2: demonstrate installing a private package
    needs: publish                          # after publish
    runs-on: ubuntu-latest                  # hosted runner
    permissions:
      contents: read                        # read code
      packages: read                        # read private packages
    steps:
      - uses: actions/setup-node@v4         # Node and registry auth
        with:
          node-version: 20                  # example LTS
          registry-url: https://npm.pkg.github.com   # registry for the scope
          scope: "@acme"                    # scope mapping
      - run: npm view @acme/shared-types version      # query the registry
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}   # token with packages: read
```
Not published or installed against a real GitHub account here. Replace `acme` with your lowercase owner name. Cross-repo access for the consumer's GITHUB_TOKEN requires package access settings ("Manage Actions access") or a PAT.

---

## 🟠 My Stack Integration
Use GitHub Packages for shared Node/React libraries; use GHCR for Docker images of FastAPI/Node; use PyPI (or a private index) for Python libs since GitHub Packages has no PyPI registry. In consuming repos and Docker builds, pass the token with a BuildKit secret instead of baking `.npmrc` into the image:

```dockerfile
# Dockerfile (Node API installing a private @acme package)
# syntax=docker/dockerfile:1
FROM node:20-alpine AS deps
# example base image tag, update as needed
WORKDIR /app
# working directory inside the image
COPY package.json package-lock.json ./
# copy dependency manifests only (better layer cache)
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci --omit=dev
# mount the .npmrc secret only for this command; it is NOT stored in any image layer
FROM node:20-alpine
# final small runtime image
WORKDIR /app
# working directory
COPY --from=deps /app/node_modules ./node_modules
# take installed modules from the deps stage (no token inside)
COPY . .
# copy the application source
USER node
# run as non-root
CMD ["node", "server.js"]
# start command
```
Build: `docker build --secret id=npmrc,src=$HOME/.npmrc -t api .` (Dockerfile parsed by a script, image not built locally.)
Security: use fine-grained/least-privilege tokens (`read:packages` for consumers), never commit `.npmrc` with a token, prefer `GITHUB_TOKEN` in Actions, and restrict package visibility to the org.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Capital letters in the owner scope (`@Acme/pkg`).
✅ Correct: Scope must be the lowercase owner name.

❌ Mistake 2: Committing `.npmrc` containing a real token.
✅ Correct: Use `${NODE_AUTH_TOKEN}` placeholder, inject the token at run time, and add `.npmrc` handling to `.gitignore` if it holds secrets.

❌ Mistake 3: Missing `permissions: packages: write` (or read) in the workflow.
✅ Correct: Declare permissions explicitly; default token may be read-only.

❌ Mistake 4: Publishing the same version twice (GitHub Packages does not allow overwriting a version).
✅ Correct: Bump the version for each publish; automate with tags.

---

## 🧠 Tricky Interview Question
`npm install @acme/shared-types` works on your laptop but fails with 404 in the GitHub Actions of a different repo using `GITHUB_TOKEN`. Why?

Answer: A 404 (not 403) is how GitHub hides private packages the token cannot see. The `GITHUB_TOKEN` of repo B has access only to B's own packages by default. Fix: in the package's settings, add repo B under "Manage Actions access" (or inherit access from the repo), or use a fine-grained PAT/GitHub App token with `read:packages`; also ensure `.npmrc` maps the scope to `https://npm.pkg.github.com`.

---

## ⚫ Interview Questions + Answers

Q1: Which package types does GitHub Packages support?
A1: npm, RubyGems, Apache Maven, Gradle, NuGet, and containers (ghcr.io). No native PyPI registry.

Q2: How is authentication done in Actions?
A2: Use `secrets.GITHUB_TOKEN` with `permissions: packages: write` to publish or `packages: read` to install.

Q3: Why scoped names for npm?
A3: GitHub requires `@owner/name` so packages are tied to a user or org and namespace collisions are avoided.

Q4: How to avoid leaking a token into a Docker image?
A4: Use BuildKit secret mounts (`--mount=type=secret`) or multi-stage builds, never `ARG`/`COPY .npmrc` into the final image.

Q5: GitHub Packages vs npmjs.com?
A5: Packages is private-by-default with GitHub permissions and good for internal libs; npmjs.com is for public distribution and has the larger ecosystem.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Sharing private libraries inside an org
- You want CI-integrated, permission-aware hosting without extra servers

❌ Avoid when:
- You need a public package with huge reach (use npmjs.com / PyPI)
- Python packages (no registry), or polyglot proxy/caching needs (use Artifactory/Nexus/CodeArtifact)

---

## 📊 Visual Diagram
```
 repo: acme/shared-types
   |  git tag v1.2.0
   v
 Actions (packages: write, GITHUB_TOKEN)
   |  npm publish
   v
 [ npm.pkg.github.com ]  @acme/shared-types@1.2.0   (private to org)
   ^                      ^
   | npm install          | npm install
 acme/web (React)       acme/api (Node)  -- .npmrc: @acme:registry=https://npm.pkg.github.com
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Server storing packages | packages का भंडार |
| Scope | `@owner` namespace prefix | namespace |
| publishConfig | package.json target registry setting | publish की registry setting |
| .npmrc | npm config file with registry/token | npm config file |
| packages: write | Workflow permission to publish | publish की अनुमति |
| BuildKit secret | Build-time secret not stored in layers | build के समय का गुप्त मान |

---

## ⚡ 3-Line Summary
English: GitHub Packages hosts npm, Maven, NuGet, Ruby packages (and images via GHCR) inside GitHub.
Publish from Actions with `GITHUB_TOKEN` and `packages: write`; consumers map the `@scope` in `.npmrc`.
Never bake tokens into images or commits.
Hindi: GitHub Packages npm, Maven, NuGet, Ruby packages (और GHCR से images) GitHub के अंदर host करता है।
Actions से `GITHUB_TOKEN` और `packages: write` के साथ publish करो; consumers `.npmrc` में `@scope` map करते हैं।
Tokens को images या commits में कभी मत डालो।

---

## ➡️ Next Topic
**39. GitHub Container Registry (GHCR)**: the container-image side of GitHub Packages, used to ship your FastAPI/Node Docker images to the VPS.

---
