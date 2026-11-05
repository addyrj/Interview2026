# 341. SSH Deploy Action
# हिंदी में: SSH Deploy Action (Marketplace Action)

---

## 🔵 Simple Definition (English)
An SSH deploy action is a ready-made GitHub Actions step (for example `appleboy/ssh-action` for remote commands and `appleboy/scp-action` for file copy) that opens an SSH session to your server and runs a script, so you do not hand-write key setup shell code in every workflow.

## 🔵 सरल परिभाषा (Hindi)
SSH deploy action एक तैयार GitHub Actions step है (जैसे remote commands के लिए `appleboy/ssh-action` और file copy के लिए `appleboy/scp-action`) जो आपके server पर SSH session खोलकर script चलाता है, ताकि हर workflow में key setup का shell code हाथ से न लिखना पड़े।

---

## 🔴 Problem it Solves
Hand-written SSH steps repeat the same `mkdir ~/.ssh; chmod 600; known_hosts` boilerplate, are easy to get wrong, and are hard to reuse across repos. An action wraps this into a few inputs (`host`, `username`, `key`, `script`) and adds timeouts, proxy/jump host support and multi-host deploys.

## 🔴 यह क्यों बना? (Hindi)
हाथ से लिखे SSH steps में वही `mkdir ~/.ssh; chmod 600; known_hosts` boilerplate बार-बार आता है, गलती आसान है और repos में reuse मुश्किल। Action इसे कुछ inputs (`host`, `username`, `key`, `script`) में समेट देता है, साथ में timeouts, proxy/jump host और multi-host deploy भी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add secrets: VPS_HOST, VPS_USER, VPS_SSH_KEY (and optional PORT)
Step 2 → Use appleboy/ssh-action@<pinned> with host/username/key/script
Step 3 → The action starts a container, opens SSH, runs script lines
Step 4 → (optional) scp-action first uploads compose file / configs
Step 5 → Script pulls image, restarts, checks health
Step 6 → Action exit code = script exit code → job passes/fails
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Secrets जोड़ो: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` (और optional PORT)।
Step 2 → `appleboy/ssh-action@<pinned>` को host/username/key/script के साथ use करो।
Step 3 → Action SSH खोलकर script की lines चलाता है।
Step 4 → (optional) पहले `scp-action` से compose file / configs upload करो।
Step 5 → Script image pull, restart और health check करता है।
Step 6 → Script का exit code ही job का result बनता है।

---

## 🟡 Real World Example
A college-project startup deploys a FastAPI app to a DigitalOcean droplet. Instead of 12 lines of SSH setup, the workflow has one `ssh-action` step. They also upload `docker-compose.prod.yml` with `scp-action` so the server file always matches the repo. A teammate can understand the pipeline in one minute.

## 🟡 Real Example Hindi mein
एक college-project startup अपना FastAPI app DigitalOcean droplet पर deploy करता है। 12 lines के SSH setup की जगह workflow में एक `ssh-action` step है। साथ में `scp-action` से `docker-compose.prod.yml` upload होती है ताकि server की file हमेशा repo से मेल खाए। नया teammate एक मिनट में pipeline समझ लेता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/ssh-action-basic.yml
name: ssh-action-basic                 # workflow name
on:
  push:
    branches: [main]                   # deploy on main
jobs:
  deploy:
    runs-on: ubuntu-latest             # runner
    steps:
      - name: Deploy via ssh-action    # one step does it all
        uses: appleboy/ssh-action@v1.0.3   # example version - pin and update
        with:
          host: ${{ secrets.VPS_HOST }}          # server IP or domain
          username: ${{ secrets.VPS_USER }}      # deploy user
          key: ${{ secrets.VPS_SSH_KEY }}        # private key content
          port: 22                               # ssh port
          script: |                              # commands run on server
            cd /srv/app                          # go to app folder
            docker compose pull                  # fetch new images
            docker compose up -d                 # restart changed services
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/ssh-action-advanced.yml
name: ssh-action-advanced
on:
  push:
    branches: [main]
concurrency:
  group: deploy-prod                   # serialize deploys
  cancel-in-progress: false
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production            # protection rules + env secrets
    steps:
      - uses: actions/checkout@v4      # needed to read compose files
      - name: Upload compose + nginx config
        uses: appleboy/scp-action@v0.1.7     # example version - pin and update
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          source: "docker-compose.prod.yml,nginx/default.conf"  # files to copy
          target: /srv/app             # destination dir on server
      - name: Remote deploy
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          fingerprint: ${{ secrets.VPS_FINGERPRINT }}   # verify the host key
          command_timeout: 10m         # fail if script hangs
          envs: IMAGE_TAG              # pass this env var to the remote shell
          script_stop: true            # stop at first failing command
          script: |
            cd /srv/app
            export IMAGE_TAG                          # use the tag from the workflow
            docker compose -f docker-compose.prod.yml pull
            docker compose -f docker-compose.prod.yml up -d --remove-orphans
            sleep 8                                   # let the app boot
            curl -fsS http://127.0.0.1:3000/health    # fail job if unhealthy
            docker image prune -f                     # clean old layers
        env:
          IMAGE_TAG: sha-${{ github.sha }}            # forwarded through envs:
```

Input names (`host`, `username`, `key`, `fingerprint`, `envs`, `script_stop`, `command_timeout`) are from the action's README at the time of writing; re-check the README for your pinned version.

---

## 🟠 My Stack Integration
Keep the rollback inside a script stored on the server so the workflow stays tiny:

```bash
#!/usr/bin/env bash
# /srv/app/deploy.sh - called by ssh-action: ./deploy.sh sha-ab12cd3
set -euo pipefail                                  # stop on first error
cd /srv/app                                        # app dir
NEW="$1"                                           # new tag from the workflow
OLD=$(cat .current_tag 2>/dev/null || echo "")     # last good tag
export TAG="$NEW"                                  # compose reads ${TAG}
docker compose pull api web                        # fetch images
docker compose up -d api web                       # recreate
sleep 8                                            # boot time
if curl -fsS http://127.0.0.1:3000/health >/dev/null; then
  echo "$NEW" > .current_tag                       # remember good version
else
  echo "unhealthy, rolling back to $OLD"
  [ -n "$OLD" ] && TAG="$OLD" docker compose up -d api web   # restore
  exit 1                                           # fail the job
fi
```

Workflow script then becomes one line: `/srv/app/deploy.sh sha-${{ github.sha }}`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `@master` / unpinned action version.
✅ Correct: Pin a version tag, or better a full commit SHA, for third-party actions that handle your SSH key.

❌ Mistake 2: Pasting the private key with wrong line breaks (`invalid format`).
✅ Correct: Paste the whole key including BEGIN/END lines; keep a trailing newline.

❌ Mistake 3: Secrets echoed in script (`echo $DB_URL`).
✅ Correct: Never print secrets; GitHub masks only exact matches.

❌ Mistake 4: Assuming env vars from the workflow exist on the server.
✅ Correct: Forward them with `envs:` or pass as script arguments.

---

## 🧠 Tricky Interview Question
Is it safe to give a third-party action your SSH private key?

Answer: It is a trust decision. The action runs with your key, so a compromised version could steal it. Reduce risk: pin to a full commit SHA, review the source, restrict the key to a low-privilege user and source IP, use environment-scoped secrets with required reviewers, and consider a plain `ssh` step (your own code) for high-value servers.

---

## ⚫ Interview Questions + Answers

Q1: ssh-action vs plain ssh?
A1: The action is shorter and has options (timeouts, fingerprint, proxy). Plain ssh has zero third-party trust but more boilerplate.

Q2: How do you pass dynamic values?
A2: `envs:` for environment variables, or inline `${{ }}` expressions in `script` (careful with injection from untrusted inputs).

Q3: How to deploy to several servers?
A3: `host: "ip1,ip2"` (comma list, check README), or a matrix job with one host per run.

Q4: Why `fingerprint`?
A4: It pins the server's host key to prevent man-in-the-middle during the connection.

Q5: How to reach a private server?
A5: Use `proxy_host` (bastion), a VPN/Tailscale step, or a self-hosted runner inside the network.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small/medium teams with a few VPS servers.
- You want compact, readable workflows.

❌ Avoid when:
- Strict supply-chain policy forbids unreviewed actions.
- You can use SSM/ECS/Kubernetes without SSH at all.

---

## 📊 Visual Diagram
```
 workflow
   │
   ├─ scp-action ──► /srv/app/docker-compose.prod.yml
   │                 /srv/app/nginx/default.conf
   │
   └─ ssh-action ──► [ VPS ]  cd /srv/app
                              ./deploy.sh sha-xxxx
                                 pull → up -d → curl /health
                                         │ fail → rollback → exit 1
                                         ▼
                                 job result (green / red)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ssh-action | Action that runs remote commands | remote commands चलाने वाला action |
| scp-action | Action that copies files | files copy करने वाला action |
| Fingerprint | Hash of server host key | server key का hash |
| Bastion | Jump server to reach private hosts | बीच का jump server |
| Pinning | Locking action to a fixed version/SHA | version fix करना |
| Script injection | Untrusted text run as code | बाहरी text का code बन जाना |

---

## ⚡ 3-Line Summary
English: ssh-action and scp-action remove SSH boilerplate. Pin versions, verify the fingerprint, keep logic in a server-side script. Treat the key as high value.
Hindi: ssh-action और scp-action SSH boilerplate हटाते हैं। Version pin करो, fingerprint verify करो, logic server-side script में रखो। Key को कीमती मानो।

---

## ➡️ Next Topic
**342. Deploy to AWS EC2** - deploy to EC2 instances, including keyless access with AWS SSM.
