# 244. push Event
# हिंदी में: push Event (code push होने पर trigger)

---

## 🔵 Simple Definition (English)
The **`push` event** fires when commits are pushed to a branch or when a tag is pushed (also when a branch is deleted or created via push). It is the most common trigger for CI on main branches and for deploys. Filters (`branches`, `tags`, `paths`) narrow which pushes count.

## 🔵 सरल परिभाषा (Hindi)
**`push` event** तब चलता है जब किसी branch पर commits push होते हैं या कोई tag push होता है। यह main branches पर CI और deploy का सबसे आम trigger है। Filters (`branches`, `tags`, `paths`) तय करते हैं कि कौन से pushes गिने जाएँ।

---

## 🔴 Problem it Solves
Teams need an automatic action the moment code lands: run tests, build the Docker image, deploy to staging. Doing it by hand means forgotten steps and unverified code reaching production.

`push` gives an immediate, reliable hook tied to the exact commit SHA, so what you tested is exactly what you deploy.

## 🔴 यह क्यों बना? (Hindi)
Code पहुँचते ही अपने-आप काम चाहिए: tests, Docker image build, staging deploy। हाथ से करने पर steps भूल जाते हैं और बिना जाँचा code production पहुँच जाता है।

`push` तुरंत और भरोसेमंद hook देता है जो सटीक commit SHA से जुड़ा है, इसलिए जो test हुआ वही deploy होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer runs: git push origin main   (or git push origin v1.4.0)
Step 2 → GitHub receives refs: refs/heads/main  (or refs/tags/v1.4.0)
Step 3 → Push event created with payload: ref, before, after, commits[], pusher, head_commit
Step 4 → Workflows on the PUSHED commit are read; `on.push` filters evaluated
Step 5 → If matched -> run created with GITHUB_SHA = the new head commit,
         GITHUB_REF = refs/heads/main (or refs/tags/...)
Step 6 → Job runs `actions/checkout` which by default checks out GITHUB_SHA
```

Important behaviours:
- **One push = at most one run per workflow**, even with many commits (but pushing more than 3 new branches/tags at once may not trigger events for all; GitHub limits it).
- **Tag push is a separate event** from the branch push; both can happen in one `git push`.
- **Merging a PR** creates a push event on the base branch (that is how "deploy on merge" works).
- **Deleting a branch** also fires `push` (with `deleted: true`); guard with `if: github.event.deleted == false`.
- Pushes made with the default `GITHUB_TOKEN` do not trigger further workflows.
- Pushes with commit message containing `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]` or `[actions skip]` skip workflows.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Developer `git push origin main` (या `git push origin v1.4.0`) चलाता है।
Step 2 → GitHub को refs मिलते हैं: `refs/heads/main` (या `refs/tags/v1.4.0`)।
Step 3 → Push event payload के साथ बनता है: ref, before, after, commits[], pusher, head_commit।
Step 4 → Push किए गए commit के workflows पढ़े जाते हैं; `on.push` filters जाँचे जाते हैं।
Step 5 → Match होने पर run बनता है: `GITHUB_SHA` = नया head commit, `GITHUB_REF` = `refs/heads/main` (या tag)।
Step 6 → `actions/checkout` default रूप से `GITHUB_SHA` checkout करता है।

ध्यान दें: एक push = हर workflow का अधिकतम एक run; tag push अलग event है; PR merge होने पर base branch पर push event बनता है (इसी से "merge पर deploy" चलता है); branch delete भी `push` fire करता है; commit message में `[skip ci]` हो तो workflows skip होते हैं।

---

## 🟡 Real World Example
A Swiggy-like team: every merge to `main` triggers `push`. The workflow runs tests, builds `swiggy-orders:<sha7>`, pushes to ECR, and deploys to staging. When QA signs off, the release manager runs `git tag v3.8.0 && git push origin v3.8.0`; that **tag push** triggers the production workflow, which reuses the same tested image (re-tagged), so no rebuild occurs. A hotfix branch `hotfix/*` also runs the full pipeline but never deploys to production directly.

## 🟡 Real Example Hindi mein
Swiggy जैसी team: `main` पर हर merge `push` trigger करता है। Workflow tests चलाता है, `swiggy-orders:<sha7>` बनाता है, ECR में push करता है और staging पर deploy करता है। QA की मंज़ूरी के बाद release manager `git tag v3.8.0 && git push origin v3.8.0` चलाता है; यह **tag push** production workflow चलाता है जो वही tested image (नया tag लगाकर) इस्तेमाल करता है, rebuild नहीं होता। `hotfix/*` branch पर भी पूरी pipeline चलती है पर सीधे production deploy कभी नहीं होता।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/push-basic.yml
name: Push Basic                      # Workflow name
on:
  push:                               # Fire on git push
    branches:                         # Only these branches
      - main                          # Production branch
      - develop                       # Integration branch
jobs:
  test:
    runs-on: ubuntu-latest            # Runner
    steps:
      - uses: actions/checkout@v4     # Checks out the pushed commit (GITHUB_SHA)
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci                   # Install
      - run: npm test                 # Test
      - run: |                        # Show what the push event gave us
          echo "Branch: ${{ github.ref_name }}"            # main or develop
          echo "SHA:    ${{ github.sha }}"                 # Full commit SHA
          echo "Pusher: ${{ github.event.pusher.name }}"   # Who pushed
          echo "Commits in push: ${{ toJson(github.event.commits.*.message) }}"   # Messages array
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/push-advanced.yml
name: Push Advanced                   # Branch, tag and path aware pipeline
on:
  push:
    branches:
      - main                          # Merge to main -> staging
      - "hotfix/**"                   # Hotfix branches get CI
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"       # Version tags -> production
    paths-ignore:
      - "**.md"                       # Ignore docs-only pushes
      - ".vscode/**"                  # Ignore editor config
permissions:
  contents: read                      # Read-only token
concurrency:
  group: push-${{ github.ref }}       # One run per ref
  cancel-in-progress: ${{ !startsWith(github.ref, 'refs/tags/') }}   # Cancel old branch runs but never a tag/prod run
jobs:
  ci:
    if: github.event.deleted == false # Ignore branch-delete pushes
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0              # Full history if you need changelog/diff
      - name: Detect changed files in this push   # Compare before and after SHAs
        run: |
          echo "before=${{ github.event.before }}"   # Previous tip of the branch
          echo "after=${{ github.event.after }}"     # New tip
          git diff --name-only "${{ github.event.before }}" "${{ github.sha }}" || true   # Not valid for new branches (before is all zeros)
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm test
  deploy-staging:
    needs: ci
    if: github.ref == 'refs/heads/main'                  # Only main branch
    runs-on: ubuntu-24.04
    environment: staging
    steps:
      - run: echo "deploy ${{ github.sha }} to staging"
  deploy-prod:
    needs: ci
    if: startsWith(github.ref, 'refs/tags/v')            # Only version tags
    runs-on: ubuntu-24.04
    environment: production           # Manual approval gate
    steps:
      - run: echo "deploy tag ${{ github.ref_name }} to production"
```

---

## 🟠 My Stack Integration
Your standard flow for Node.js + FastAPI + React on a VPS:

| Action by you | Event | Result |
|---|---|---|
| Merge PR into `main` | `push` branch | Test, build images, deploy to staging VPS |
| `git tag v1.2.0 && git push --tags` | `push` tag | Production deploy (VPS or ECS) with approval |
| Push to `hotfix/*` | `push` branch | CI only, then PR to main |

```yaml
# .github/workflows/stack-push.yml
name: Stack Push
on:
  push:
    branches: [main]
    tags: ["v*"]
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-24.04
    outputs:
      version: ${{ steps.v.outputs.version }}      # Version string for later jobs
    steps:
      - uses: actions/checkout@v4
      - id: v
        run: |
          if [[ "$GITHUB_REF" == refs/tags/* ]]; then echo "version=${GITHUB_REF_NAME}" >> "$GITHUB_OUTPUT"   # v1.2.0
          else echo "version=sha-${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"; fi                                   # sha-abc1234
      - run: echo "build api/web images tagged ${{ steps.v.outputs.version }}"   # Real build in later topics
  deploy:
    needs: build
    runs-on: ubuntu-24.04
    environment: ${{ startsWith(github.ref, 'refs/tags/') && 'production' || 'staging' }}   # Env by ref type
    steps:
      - run: echo "ssh VPS and docker compose up with ${{ needs.build.outputs.version }}"
```

Security: restrict who can push to `main` and create tags (branch protection and tag protection / rulesets). A push trigger on a branch anyone can create can leak secrets if the workflow uses them; keep deploy secrets in environments limited to `main` and `v*` tags. Do not build from user-controlled branch names in shell without quoting: use `"${GITHUB_REF_NAME}"` via env.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying on every `push` of every branch.
✅ Correct: Limit `branches: [main]` and use tags/environments for production.

❌ Mistake 2: Using `git diff before after` on first push of a new branch; `before` is `0000000...`.
✅ Correct: Handle the zero SHA, or use `tj-actions/changed-files`/`dorny/paths-filter` (review them first) or `git diff origin/main...HEAD`.

❌ Mistake 3: Shallow checkout (default `fetch-depth: 1`) then running `git log`/`git describe`.
✅ Correct: `fetch-depth: 0` when you need history or tags.

❌ Mistake 4: Workflow pushes a commit (e.g. version bump) with `GITHUB_TOKEN` and expects another workflow to run.
✅ Correct: By design it won't; use a PAT/App token only if you truly need chaining, and guard against infinite loops.

---

## 🧠 Tricky Interview Question
"You run `git push origin main v2.0.0` in one command. Your workflow has `on: push: branches: [main], tags: ['v*']`. How many runs happen and what is `github.ref` in each?"

Answer: Two runs. Branch push and tag push are separate ref updates, each creating its own push event: one with `github.ref = refs/heads/main`, another with `github.ref = refs/tags/v2.0.0`, both pointing at the same SHA. If both trigger a deploy job you could deploy twice, so use `if:` conditions per ref type and a shared `concurrency` group to serialize. (If the two refs were pushed together, GitHub still emits separate events.)

---

## ⚫ Interview Questions + Answers

Q1: What commit does a push-triggered run build?
A1: `GITHUB_SHA`, the head commit of the pushed ref.

Q2: How do you skip CI for a commit?
A2: Put `[skip ci]` (or `[ci skip]`, `[no ci]`, `[skip actions]`, `[actions skip]`) in the commit message.

Q3: How do you run only when `src/` changes?
A3: `paths: ["src/**"]` under `on.push`.

Q4: Does `push` fire on PR merges?
A4: Yes, merging creates a push to the base branch.

Q5: How do you prevent running on branch deletion?
A5: `if: github.event.deleted == false` (the push event payload has `deleted`).

---

## 🔷 When to Use + When Not to Use
✅ Use `push` when:
- Deploying after merge to a fixed branch or on release tags.
- Running post-merge checks (build artifacts, publish images).

❌ Avoid `push` alone when:
- You need to validate code before merge: use `pull_request`.
- Fork contributions are expected: forks push to their own repos, not yours.

---

## 📊 Visual Diagram

```
 developer laptop
   git push origin main      git push origin v1.4.0
          |                          |
          v                          v
  refs/heads/main            refs/tags/v1.4.0
          |                          |
          +-----------+--------------+
                      v
             GitHub: PUSH event(s)
        payload: ref, before, after, commits[]
                      |
          filters: branches / tags / paths
                      |
            +---------+----------+
            v                    v
      run (ref=main)       run (ref=tag)
      -> staging deploy    -> production deploy (approval)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| push | Event when commits/tags are pushed | commits/tag push होने का event |
| ref | Branch or tag reference | branch या tag का संदर्भ |
| SHA | Unique commit id | commit की अद्वितीय पहचान |
| before / after | Branch tip before and after push | push से पहले और बाद का tip |
| Tag | Named pointer to a commit (release) | commit का नाम (release) |
| skip ci | Message flag to skip workflows | workflows छोड़ने का flag |

---

## ⚡ 3-Line Summary
English: `push` runs a workflow when commits or tags are pushed, using the pushed commit SHA.
Filter by branches, tags and paths; a branch push and a tag push are separate events.
Use it for post-merge CI and for deploys on main or version tags.

Hindi: `push` commits या tags push होने पर workflow चलाता है और push किए गए commit SHA का इस्तेमाल करता है।
Branches, tags और paths से filter करें; branch push और tag push अलग events हैं।
इसे merge के बाद CI और main या version tags पर deploy के लिए इस्तेमाल करें।

---

## ➡️ Next Topic
**245. pull_request Event** — validating code before it merges, with fork safety and activity types.

---
