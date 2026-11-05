# 340. Deploy to VPS (SSH)
# हिंदी में: VPS पर SSH से Deploy करना

---

## 🔵 Simple Definition (English)
Deploying to a VPS over SSH means the CI job connects to your server with an SSH key, pulls the new image, restarts containers (usually with Docker Compose) and checks health. It is the simplest "push-button" CD with no orchestrator.

## 🔵 सरल परिभाषा (Hindi)
VPS पर SSH deploy का मतलब है कि CI job SSH key से आपके server से connect होकर नई image pull करता है, containers restart करता है (आमतौर पर Docker Compose से) और health check करता है। यह बिना orchestrator का सबसे सरल "एक click" CD है।

---

## 🔴 Problem it Solves
Manual deploys mean logging into the server, running commands from memory, forgetting `pull`, or leaving the app half-updated. It is slow, error-prone, and only one person knows how. A scripted SSH deploy is repeatable, logged in Actions history, and can roll back automatically.

## 🔴 यह क्यों बना? (Hindi)
Manual deploy में server पर login करके commands याद से चलाने पड़ते हैं, `pull` भूल जाते हैं या app आधा update रह जाता है। यह धीमा, गलती-प्रवण है और सिर्फ एक व्यक्ति को आता है। Script वाला SSH deploy repeatable है, Actions history में log होता है और अपने आप rollback कर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a dedicated deploy user + SSH keypair on the VPS
Step 2 → Put the public key in ~/.ssh/authorized_keys (restricted)
Step 3 → Store private key, host, user, known_hosts in GitHub secrets
Step 4 → Job writes the key to ~/.ssh with chmod 600
Step 5 → ssh runs: docker compose pull && up -d --remove-orphans
Step 6 → Health check curl; on failure, redeploy previous tag
Step 7 → docker image prune removes old layers
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → VPS पर अलग deploy user और SSH keypair बनाओ।
Step 2 → Public key को `~/.ssh/authorized_keys` में डालो।
Step 3 → Private key, host, user और known_hosts GitHub secrets में रखो।
Step 4 → Job key को `~/.ssh` में लिखकर `chmod 600` करता है।
Step 5 → ssh से `docker compose pull && up -d --remove-orphans` चलता है।
Step 6 → Health check `curl` से; fail हो तो पिछला tag दोबारा deploy।
Step 7 → `docker image prune` पुरानी layers हटाता है।

---

## 🟡 Real World Example
A solo founder runs a Node.js API and React app on a Hetzner/DigitalOcean VPS behind Nginx. Every merge to `main` builds the image to GHCR, then the deploy job SSHes in as user `deploy`, sets `TAG=sha-ab12cd3`, and recreates only the changed containers. Downtime is a few seconds; if `/health` fails, the script restores the previous tag.

## 🟡 Real Example Hindi mein
एक solo founder का Node.js API और React app Hetzner/DigitalOcean VPS पर Nginx के पीछे चलता है। `main` पर हर merge में image GHCR पर build होती है, फिर deploy job `deploy` user से SSH करता है, `TAG=sha-ab12cd3` set करता है और सिर्फ बदले containers दोबारा बनाता है। `/health` fail हो तो पिछला tag वापस आ जाता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/deploy-vps.yml (basic, plain ssh)
name: deploy-vps                       # workflow name
on:
  workflow_dispatch:                   # manual button for the basic example
jobs:
  deploy:
    runs-on: ubuntu-latest             # runner
    steps:
      - name: Setup SSH key            # write private key and trust the host
        run: |                         # multi-line shell
          mkdir -p ~/.ssh              # create ssh dir
          echo "${{ secrets.VPS_SSH_KEY }}" > ~/.ssh/id_ed25519   # private key
          chmod 600 ~/.ssh/id_ed25519  # ssh refuses keys with open permissions
          echo "${{ secrets.VPS_KNOWN_HOSTS }}" > ~/.ssh/known_hosts  # pinned host key
      - name: Deploy over SSH          # run commands on the server
        run: |
          ssh -i ~/.ssh/id_ed25519 ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} \
            "cd /srv/app && docker compose pull && docker compose up -d"
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy-vps-advanced.yml (build -> push -> deploy -> health -> rollback)
name: deploy-vps-advanced
on:
  push:
    branches: [main]                   # deploy on merge
permissions:
  contents: read
  packages: write                      # push to GHCR
concurrency:
  group: deploy-production             # never run two deploys at once
  cancel-in-progress: false            # let a running deploy finish
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.vars.outputs.tag }}   # pass tag to deploy job
    steps:
      - uses: actions/checkout@v4
      - id: vars
        run: echo "tag=sha-${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # short SHA tag
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/myorg/api:${{ steps.vars.outputs.tag }}
  deploy:
    needs: build                       # wait for the image
    runs-on: ubuntu-latest
    environment: production            # approvals + environment secrets
    steps:
      - name: Prepare SSH
        run: |
          install -m 700 -d ~/.ssh                        # ssh dir with 700
          echo "${{ secrets.VPS_SSH_KEY }}" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          echo "${{ secrets.VPS_KNOWN_HOSTS }}" > ~/.ssh/known_hosts
      - name: Deploy with rollback
        env:
          TAG: ${{ needs.build.outputs.tag }}          # new tag
        run: |
          ssh -o BatchMode=yes ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} \
            "TAG=$TAG bash -s" <<'REMOTE'
          set -euo pipefail                           # stop on any error
          cd /srv/app                                 # app directory
          PREV=$(cat .current_tag 2>/dev/null || echo latest)  # remember old tag
          TAG=$TAG docker compose pull api            # fetch new image
          TAG=$TAG docker compose up -d api           # recreate container
          for i in 1 2 3 4 5 6; do                    # wait up to ~30 s
            if curl -fsS http://127.0.0.1:3000/health >/dev/null; then
              echo "$TAG" > .current_tag              # record success
              docker image prune -f                   # clean dangling layers
              exit 0
            fi
            sleep 5
          done
          echo "health failed, rolling back to $PREV"
          TAG=$PREV docker compose up -d api          # restore old version
          exit 1                                      # mark the job failed
          REMOTE
```

---

## 🟠 My Stack Integration
Server prep (run once as root on the VPS):

```bash
# create a non-root deploy user in the docker group
adduser --disabled-password --gecos "" deploy        # no password login
usermod -aG docker deploy                            # may run docker
install -d -o deploy -g deploy /srv/app              # app directory
# on your laptop: key used ONLY for CI
ssh-keygen -t ed25519 -f ./gha_deploy -C "gha-deploy" -N ""
# add the public key (optionally restricted to one source/command)
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
cat gha_deploy.pub >> /home/deploy/.ssh/authorized_keys
# capture the host key for the VPS_KNOWN_HOSTS secret
ssh-keyscan -t ed25519 your.vps.ip
```

Nginx stays on the host (or in compose) and proxies `127.0.0.1:3000` (Node.js) and `:8000` (FastAPI); the React build is served from the `web` container. Note: the `docker` group is effectively root, so keep this key tightly guarded.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `StrictHostKeyChecking=no`, which allows man-in-the-middle.
✅ Correct: Store the real host key in a `known_hosts` secret.

❌ Mistake 2: Deploying as root with a password-protected-less key.
✅ Correct: Dedicated `deploy` user, key-only SSH, `PermitRootLogin no`.

❌ Mistake 3: No health check, so a crash-looping container counts as "success".
✅ Correct: Probe `/health` and roll back on failure.

❌ Mistake 4: Two deploys racing.
✅ Correct: Use `concurrency` with a fixed group.

---

## 🧠 Tricky Interview Question
The workflow is green but users still see the old version. Name three causes.

Answer: (1) `up -d` ran with an unchanged mutable tag and no `pull`; (2) the SSH command ran in the wrong directory/compose project, so another stack was updated; (3) Nginx or a CDN is caching, or Nginx still points at the old container IP because upstream is resolved only at startup. Verify with `docker ps` image IDs and a version endpoint.

---

## ⚫ Interview Questions + Answers

Q1: Why a dedicated deploy key?
A1: It limits blast radius and can be revoked independently of personal keys.

Q2: How do you get zero-downtime on one VPS?
A2: Blue-green with two compose services behind Nginx upstream, switch after health passes; or `docker rollout`-style plugins.

Q3: Why `set -euo pipefail` in the remote script?
A3: To stop immediately on error, on unset variables and on failed pipes, so a failed pull does not continue to restart.

Q4: How to keep secrets (DB URL) safe?
A4: Keep `.env` on the server with chmod 600; the pipeline sends only the image tag.

Q5: Biggest risk of SSH deploys?
A5: A leaked CI key gives server access. Mitigate with a restricted user, firewall allow-list, environment approvals and key rotation.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One or a few VPS servers, small team.
- You want simple, cheap, understandable CD.

❌ Avoid when:
- You need autoscaling and self-healing (ECS/Kubernetes).
- Many servers (use Ansible or an orchestrator).
- Servers are not reachable from GitHub runners (use self-hosted runner).

---

## 📊 Visual Diagram
```
 push main
    │
    ▼
 build job ──► registry (ghcr.io/myorg/api:sha-ab12cd3)
    │
    ▼
 deploy job ── ssh (ed25519, known_hosts) ──► VPS (user: deploy)
                                               │ docker compose pull
                                               │ docker compose up -d
                                               ▼
                                        health check /health
                                          ok │        │ fail
                                             ▼        ▼
                                       prune old    rollback PREV
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSH key | Public/private login keypair | बिना password का login |
| known_hosts | Trusted server fingerprints | भरोसेमंद server की पहचान |
| Rollback | Return to last good version | पिछले सही version पर लौटना |
| Health check | Probe that the app is alive | app चालू है या नहीं जाँच |
| Concurrency | Limit parallel runs | एक समय में एक run |
| Environment | Deployment target with rules | deploy का target और नियम |

---

## ⚡ 3-Line Summary
English: SSH deploy pulls the new tag and restarts compose on the VPS. Use a restricted deploy user, pinned host key, health check and rollback. Keep app secrets on the server.
Hindi: SSH deploy VPS पर नया tag pull करके compose restart करता है। Restricted user, pinned host key, health check और rollback रखो। App secrets server पर रखो।

---

## ➡️ Next Topic
**341. SSH Deploy Action** - replace the hand-written ssh scripts with a maintained marketplace action.
