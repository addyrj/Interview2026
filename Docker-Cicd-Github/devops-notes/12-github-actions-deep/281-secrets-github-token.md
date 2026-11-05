# 281. secrets.GITHUB_TOKEN
# हिंदी में: secrets.GITHUB_TOKEN (हर run का automatic token)

---

## 🔵 Simple Definition (English)
`GITHUB_TOKEN` is a short-lived access token GitHub creates automatically for each workflow run (more precisely, per job). You do not store it; you read it as `${{ secrets.GITHUB_TOKEN }}` or `${{ github.token }}`. It acts as the "GitHub Actions" app and expires when the job ends. Its power is controlled with the `permissions:` key.

## 🔵 सरल परिभाषा (Hindi)
`GITHUB_TOKEN` एक छोटी अवधि का access token है जो GitHub हर workflow run (असल में हर job) के लिए अपने-आप बनाता है। इसे store नहीं करना पड़ता; `${{ secrets.GITHUB_TOKEN }}` या `${{ github.token }}` से पढ़ते हैं। यह "GitHub Actions" app की तरह काम करता है और job खत्म होते ही expire हो जाता है। इसकी ताकत `permissions:` key से तय होती है।

---

## 🔴 Problem it Solves
Workflows often need to call the GitHub API: comment on a PR, create a release, push to GHCR, label issues, push a tag. Before, people created Personal Access Tokens (PATs) that were long-lived, tied to a person, and broad. A leaked PAT gave full account access. `GITHUB_TOKEN` is scoped to one repo, expires automatically and needs no maintenance.

## 🔴 यह क्यों बना? (Hindi)
Workflows को अक्सर GitHub API call करनी होती है: PR पर comment, release बनाना, GHCR में push, issues label करना, tag push करना। पहले लोग Personal Access Tokens (PAT) बनाते थे जो लंबी अवधि के, किसी व्यक्ति से जुड़े और broad होते थे। PAT leak होने पर पूरे account का access चला जाता था। `GITHUB_TOKEN` एक repo तक सीमित है, अपने-आप expire होता है और maintenance नहीं माँगता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job starts; GitHub installs the "GitHub Actions" app on the repo for this run
Step 2 → A token is minted with permissions from permissions: (or repo default)
Step 3 → It is exposed as secrets.GITHUB_TOKEN / github.token
Step 4 → actions/checkout uses it by default to clone the repo
Step 5 → Your steps pass it as Authorization: Bearer ... or GH_TOKEN env for `gh`
Step 6 → Job ends -> token expires (max 24 hours anyway)
```

Key limits: events created with this token (a push, a PR) do NOT trigger new workflow runs (except `workflow_dispatch` and `repository_dispatch`), preventing infinite loops. Fork PRs receive a read-only token.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Job शुरू होता है; GitHub इस run के लिए repo पर "GitHub Actions" app install करता है
Step 2 → permissions: (या repo default) के अनुसार token बनता है
Step 3 → यह secrets.GITHUB_TOKEN / github.token के रूप में मिलता है
Step 4 → actions/checkout इसे default में repo clone के लिए use करता है
Step 5 → आपके steps इसे Authorization: Bearer ... या `gh` के लिए GH_TOKEN env में देते हैं
Step 6 → Job खत्म -> token expire (वैसे भी अधिकतम 24 घंटे)
```

मुख्य सीमाएँ: इस token से बने events (push, PR) नए workflow runs trigger नहीं करते (`workflow_dispatch` और `repository_dispatch` को छोड़कर), ताकि infinite loops न बनें। Fork PRs को read-only token मिलता है।

---

## 🟡 Real World Example
On every merge to `main`, your pipeline builds an image and pushes it to `ghcr.io/owner/my-api` using `GITHUB_TOKEN` with `packages: write`. It also posts a PR comment with the preview URL using `pull-requests: write`, and creates a GitHub Release on version tags with `contents: write`. No PAT, no human credential involved.

## 🟡 Real Example Hindi mein
`main` पर हर merge में आपका pipeline image build करके `GITHUB_TOKEN` (`packages: write` के साथ) से `ghcr.io/owner/my-api` में push करता है। यह `pull-requests: write` से PR पर preview URL का comment भी करता है, और version tags पर `contents: write` से GitHub Release बनाता है। कोई PAT या इंसानी credential नहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/token-basic.yml
name: token-basic                      # workflow name
on:
  pull_request:                        # runs on PRs

permissions:                           # restrict token for ALL jobs in this workflow
  contents: read                       # clone code only
  pull-requests: write                 # allow commenting on PRs

jobs:
  comment:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # uses github.token automatically
      - name: Comment using gh CLI
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}     # gh reads GH_TOKEN
        run: |
          gh pr comment "${{ github.event.pull_request.number }}" \
            --body "CI passed for ${GITHUB_SHA::7}"   # posts a PR comment
```
Note: for PRs from forks the token is read-only, so this comment step fails there.

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/publish-image.yml
name: publish-image                    # workflow name
on:
  push:
    branches: [main]                   # publish from main
    tags: ["v*"]                       # and from version tags

permissions: {}                        # start with NOTHING at workflow level

jobs:
  build-push:
    runs-on: ubuntu-latest
    permissions:                       # grant only what this job needs
      contents: read                   # checkout
      packages: write                  # push to GHCR
    steps:
      - uses: actions/checkout@v4      # example version
      - name: Login to GHCR
        uses: docker/login-action@v3   # example version
        with:
          registry: ghcr.io            # GitHub Container Registry
          username: ${{ github.actor }}          # user name for the login
          password: ${{ secrets.GITHUB_TOKEN }}  # the automatic token
      - name: Build and push
        uses: docker/build-push-action@v6        # example version
        with:
          context: .                   # Dockerfile in repo root
          push: true                   # push after build
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}   # image name:tag

  release:
    if: startsWith(github.ref, 'refs/tags/v')    # only for tags
    needs: build-push
    runs-on: ubuntu-latest
    permissions:
      contents: write                  # needed to create a release
    steps:
      - name: Create release
        env:
          GH_TOKEN: ${{ github.token }}          # same token via github context
        run: gh release create "$GITHUB_REF_NAME" --repo "$GITHUB_REPOSITORY" --generate-notes
        # --generate-notes builds notes from merged PRs
```
Not run locally (no Docker); YAML parsed. GHCR image names must be lowercase; for mixed-case owner names add a lowercase step.

---

## 🟠 My Stack Integration
Use GHCR as the registry for Node.js/FastAPI images with just `GITHUB_TOKEN`; then the VPS pulls with a read-only PAT (or `docker login` using a fine-grained token that only has `read:packages`). For AWS, don't use `GITHUB_TOKEN`; use OIDC (`id-token: write`) to assume an IAM role.

```yaml
# snippet: VPS pulls the image pushed with GITHUB_TOKEN
      - name: Pull on VPS
        env:
          GHCR_READ: ${{ secrets.GHCR_READ_TOKEN }}    # read:packages token for the server
        run: |
          ssh deploy@"${{ secrets.VPS_HOST }}" \
            "echo '$GHCR_READ' | docker login ghcr.io -u ${{ github.repository_owner }} --password-stdin && \
             cd /srv/app && IMAGE_TAG=$GITHUB_SHA docker compose pull && docker compose up -d"
```
(The token is placed in the remote command line here for brevity; in production send it via stdin or a pre-configured docker credential on the VPS.)

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Leaving default permissions as read-write for everything.
✅ Correct: Set `permissions:` at workflow level (`contents: read`) and elevate per job.

❌ Mistake 2: Expecting a push made by the workflow to trigger another workflow.
✅ Correct: Use a GitHub App token or PAT for that, or `workflow_dispatch` explicitly.

❌ Mistake 3: Using `GITHUB_TOKEN` to access another repository.
✅ Correct: It is scoped to the current repo only; use a GitHub App token or fine-grained PAT.

❌ Mistake 4: Printing or uploading the token (e.g., in an artifact of `.git/config`).
✅ Correct: `actions/checkout` persists credentials by default; set `persist-credentials: false` when you upload the workspace.

---

## 🧠 Tricky Interview Question
Your release workflow creates a tag with `GITHUB_TOKEN`, and a separate workflow `on: push: tags` never runs. Why, and how do you fix it?

Answer: Events created by `GITHUB_TOKEN` intentionally do not trigger other workflows, to avoid recursive runs. Fix by using a GitHub App installation token or a fine-grained PAT for the tag push, or call the second workflow via `workflow_call` / `workflow_dispatch` (which are allowed).

---

## ⚫ Interview Questions + Answers

Q1: Do you need to create `GITHUB_TOKEN`?
A1: No, it is generated per job automatically.

Q2: How do you limit it?
A2: `permissions:` at workflow or job level; once any permission is specified, the unspecified ones become `none`. Org/repo setting can make the default read-only.

Q3: Difference from a PAT?
A3: GITHUB_TOKEN is repo-scoped, auto-expiring, not tied to a person; PAT is long-lived, user-scoped.

Q4: Is it the same as `github.token`?
A4: Yes, same value.

Q5: Which permission for OIDC to AWS?
A5: `id-token: write` (separate from GITHUB_TOKEN usage but configured in the same `permissions:` block).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Checkout, GHCR push, PR comments, releases, labels in the same repo.

❌ Avoid when:
- Cross-repo access, triggering follow-up workflows, or cloud auth (use App token / PAT / OIDC).

---

## 📊 Visual Diagram
```
 job starts
    |
    v
 GitHub mints token  (scopes = permissions: block)
    |
    +--> actions/checkout   (contents: read)
    +--> docker login ghcr  (packages: write)
    +--> gh pr comment      (pull-requests: write)
    |
 job ends --> token EXPIRES
 events created by token -x-> do not trigger new workflows
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GITHUB_TOKEN | Auto-generated per-job token | हर job का automatic token |
| permissions | Scope settings for the token | Token की अनुमतियाँ |
| PAT | Personal access token, long-lived | लंबी अवधि वाला personal token |
| GHCR | GitHub Container Registry (ghcr.io) | GitHub का container registry |
| Least privilege | Grant only needed access | जितना ज़रूरी उतना access |

---

## ⚡ 3-Line Summary
English: `GITHUB_TOKEN` is an automatic, short-lived, repo-scoped token for each job.
Control it with `permissions:`; start from none or read-only.
It cannot trigger other workflows or reach other repos.

Hindi: `GITHUB_TOKEN` हर job का automatic, छोटी अवधि वाला, repo-scoped token है।
इसे `permissions:` से control करो; none या read-only से शुरू करो।
यह दूसरे workflows trigger नहीं कर सकता और दूसरी repos तक नहीं पहुँचता।

---

## ➡️ Next Topic
**282. Artifact Upload + Download** — how jobs hand build outputs (bundles, test reports) to each other and to humans.
