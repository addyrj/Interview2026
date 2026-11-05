# 357. Deployment Notifications (Slack, Email, Teams)
# हिंदी में: Deployment Notifications (Slack, Email, Teams)

---

## 🔵 Simple Definition (English)
Deployment notifications are automatic messages sent to Slack, Microsoft Teams or email when a pipeline starts, succeeds or fails. They tell the team what was deployed, who triggered it, which commit and where to look if it broke.

## 🔵 सरल परिभाषा (Hindi)
Deployment notifications वे automatic messages हैं जो pipeline शुरू, सफल या fail होने पर Slack, Microsoft Teams या email पर जाते हैं। ये team को बताते हैं कि क्या deploy हुआ, किसने किया, कौन सा commit और fail होने पर कहाँ देखना है।

---

## 🔴 Problem it Solves
Without notifications, people discover a failed deploy when a customer complains. Nobody knows who deployed last, so debugging starts with "who changed something?". Teams also lose an audit trail of releases. A message in the right channel gives visibility, speeds up incident response, and creates a simple history.

## 🔴 यह क्यों बना? (Hindi)
Notifications के बिना failed deploy का पता तब चलता है जब customer शिकायत करता है। किसी को नहीं पता आखिरी deploy किसने किया, तो debugging "किसने कुछ बदला?" से शुरू होती है। Releases का audit trail भी खो जाता है। सही channel में एक message visibility देता है, incident response तेज़ करता है और आसान history बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create an Incoming Webhook (Slack/Teams) or SMTP credentials
Step 2 → Store the webhook URL / password in GitHub Secrets
Step 3 → Add a notify step to the workflow (or a final "notify" job)
Step 4 → Use if: success() / failure() / always() to pick the message
Step 5 → Send JSON with commit, actor, environment, status and run link
Step 6 → The channel shows a message; failures can @mention on-call
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Incoming Webhook (Slack/Teams) या SMTP credentials बनाओ
Step 2 → Webhook URL / password GitHub Secrets में रखो
Step 3 → Workflow में notify step (या आखिरी "notify" job) जोड़ो
Step 4 → if: success() / failure() / always() से सही message चुनो
Step 5 → Commit, actor, environment, status और run link वाला JSON भेजो
Step 6 → Channel में message दिखता है; failure पर on-call को @mention कर सकते हैं
```

---

## 🟡 Real World Example
A team of 12 has a `#deployments` Slack channel. Every production deploy posts "api deployed to production: abc1234 by priya, https://github.com/.../runs/123". When a deploy fails, a red message with the run link goes to `#deployments` and the on-call engineer is pinged. A support person who sees a customer complaint at 3 PM checks the channel and sees that a release went out at 2:55 PM, which cuts diagnosis time from an hour to minutes.

## 🟡 Real Example Hindi mein
12 लोगों की team का `#deployments` Slack channel है। हर production deploy पर message आता है "api deployed to production: abc1234 by priya, link"। Deploy fail होने पर run link के साथ लाल message जाता है और on-call engineer को ping होता है। Support वाला 3 बजे customer शिकायत देखकर channel देखता है और पाता है कि 2:55 पर release गया था, जिससे diagnosis एक घंटे से मिनटों में आ जाता है।

---

## 💻 Code / Config Example — Basic

```yaml
# basic: Slack message via curl and an incoming webhook (no third-party action)
name: Notify Basic
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploying..."              # placeholder for real deploy steps
      - name: Slack notify (success)
        if: success()                         # only when previous steps passed
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}   # secret never printed
        run: |
          curl -sS -X POST -H 'Content-type: application/json' \
            --data '{"text":"Deployed '"${GITHUB_SHA::7}"' to production"}' \
            "$SLACK_WEBHOOK_URL"
```

## 💻 Code / Config Example — Advanced

```yaml
# advanced: dedicated notify job with Slack, Teams and Email
name: Deploy and Notify
on:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh                      # your real deployment script

  notify:
    needs: deploy                             # wait for deploy
    if: always()                              # run even when deploy failed
    runs-on: ubuntu-latest
    env:
      STATUS: ${{ needs.deploy.result }}      # success | failure | cancelled | skipped
      RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
    steps:
      - name: Build message
        run: |
          if [ "$STATUS" = "success" ]; then ICON="white_check_mark"; COLOR="#2eb886"
          else ICON="x"; COLOR="#d00000"; fi
          echo "ICON=$ICON" >> "$GITHUB_ENV"        # share with later steps
          echo "COLOR=$COLOR" >> "$GITHUB_ENV"

      - name: Slack (webhook, Block Kit)
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          ACTOR: ${{ github.actor }}              # passed via env, not interpolated in shell
          SHA: ${{ github.sha }}
        run: |
          jq -n --arg t ":${ICON}: *${GITHUB_REPOSITORY}* deploy *${STATUS}*" \
                --arg a "$ACTOR" --arg s "${SHA::7}" --arg u "$RUN_URL" \
            '{text:$t, attachments:[{color:"'"$COLOR"'", fields:[
               {title:"Actor",value:$a,short:true},
               {title:"Commit",value:$s,short:true},
               {title:"Run",value:$u,short:false}]}]}' \
          | curl -sS -X POST -H 'Content-type: application/json' --data @- "$SLACK_WEBHOOK_URL"

      - name: Microsoft Teams (workflow/incoming webhook, simple text card)
        env:
          TEAMS_WEBHOOK_URL: ${{ secrets.TEAMS_WEBHOOK_URL }}
        run: |
          # Teams connectors change over time: check your webhook type in Teams settings
          curl -sS -X POST -H 'Content-Type: application/json' \
            --data "{\"text\":\"${GITHUB_REPOSITORY} deploy ${STATUS}: ${RUN_URL}\"}" \
            "$TEAMS_WEBHOOK_URL"

      - name: Email on failure only
        if: env.STATUS != 'success'              # email only for problems
        uses: dawidd6/action-send-mail@v3        # third-party action, example version
        with:
          server_address: smtp.gmail.com         # SMTP server (use your provider)
          server_port: 465                       # SSL port
          secure: true                           # use TLS
          username: ${{ secrets.SMTP_USER }}     # SMTP user from secrets
          password: ${{ secrets.SMTP_PASSWORD }} # app password, not account password
          subject: "DEPLOY ${{ env.STATUS }}: ${{ github.repository }}"
          to: oncall@example.com                 # recipients
          from: CI Bot <ci@example.com>          # sender name
          body: "Run: ${{ env.RUN_URL }}"
```

---

## 🟠 My Stack Integration
- Put the notify job at the end of the same workflow that deploys your Node/FastAPI/React app to the VPS.
- Include environment name, image tag, version and the Nginx domain in the message.
- Also notify from the server on host-level problems (disk full, certificate expiry) using the same webhook from cron.
- On AWS, use SNS (to email/Slack via Chatbot) for CodeDeploy or CloudWatch alarms.

```bash
# server-side cron helper: alert when disk usage exceeds 85 percent (cron every 10 min)
USAGE=$(df / --output=pcent | tail -1 | tr -dc '0-9')                      # numeric percent
if [ "$USAGE" -gt 85 ]; then
  curl -sS -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"Disk on $(hostname) is ${USAGE}% full\"}" "$SLACK_WEBHOOK_URL"
fi
```

Security: webhook URLs are secrets (anyone with the URL can post to your channel). Store them in Secrets, rotate if leaked, never echo them, and pass untrusted values (branch names, commit messages, PR titles) through `env:` and `jq --arg` instead of building JSON or shell strings by hand, to avoid injection.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Notify step uses `if: success()` only, so failures are silent.
✅ Correct: Use a separate notify job with `if: always()` and read `needs.<job>.result`.

❌ Mistake 2: Putting `${{ github.event.head_commit.message }}` directly inside a `run:` script.
✅ Correct: Map it to an `env:` variable first; commit messages can contain shell metacharacters.

❌ Mistake 3: Alert fatigue, a message on every PR push.
✅ Correct: Notify on production deploys and failures; keep the rest quiet or in a separate channel.

❌ Mistake 4: Hard-coding the webhook URL in the repo.
✅ Correct: Store it as a secret.

❌ Mistake 5: Messages without a link to the run.
✅ Correct: Always include the run URL, commit and actor.

---

## 🧠 Tricky Interview Question
Your Slack notify step is the last step of the deploy job, but when the deploy fails you never get a message. Why?

Answer: By default a step runs only if all previous steps succeeded (`if: success()`). When an earlier step fails, later steps are skipped. Add `if: failure()` or `if: always()` to the notify step, or better, use a separate job with `needs` and `if: always()`, and check the `needs.<job>.result`. Note that a cancelled workflow is not a failure; use `cancelled()` when you want that case too.

---

## ⚫ Interview Questions + Answers

Q1: What do `success()`, `failure()`, `always()` and `cancelled()` do?
A1: They are status check functions for `if:`; `always()` runs regardless, `failure()` when a previous step failed, `cancelled()` when the run was cancelled.

Q2: How do you send the result of a job to another job?
A2: Use `needs.<job_id>.result` or job outputs.

Q3: Webhook vs a marketplace action?
A3: A `curl` webhook has no dependencies and no supply-chain risk; actions add convenience but should be pinned to a version or SHA.

Q4: Where would you send critical alerts?
A4: To a paging tool (PagerDuty, Opsgenie) for on-call; Slack for information.

Q5: How do you avoid leaking secrets in notifications?
A5: Never include env dumps, tokens or full logs; GitHub masks secrets in logs but not in text you reformat.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one person needs to know about production changes.
- You want a visible release history and quick failure awareness.

❌ Avoid when:
- It would spam: noisy channels get muted and real failures are missed.
- The message needs sensitive data; link to the run instead.

---

## 📊 Visual Diagram
```
 [build] -> [deploy] ----------------------+
                                           v
                                    [notify job]  if: always()
                                           |
                       +-------------------+-------------------+
                       v                   v                   v
                  Slack webhook      Teams webhook        Email (SMTP)
                  #deployments       Release channel      only on failure
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Webhook | URL that accepts posted messages | message स्वीकार करने वाला URL |
| `always()` | Run step regardless of status | status की परवाह किए बिना चलाना |
| SMTP | Protocol to send email | email भेजने का protocol |
| Alert fatigue | Ignoring too many alerts | बहुत alerts से ध्यान हटना |
| On-call | Engineer responsible now | अभी ज़िम्मेदार engineer |

---

## ⚡ 3-Line Summary
English: Send a message to Slack, Teams or email at the end of each deploy with status, commit, actor and run link.
Use a separate notify job with `if: always()` so failures are reported.
Treat webhook URLs as secrets and avoid injecting untrusted text into scripts.
Hindi: हर deploy के अंत में status, commit, actor और run link के साथ Slack, Teams या email भेजो।
अलग notify job `if: always()` के साथ रखो ताकि failures भी report हों।
Webhook URL को secret मानो और untrusted text को scripts में सीधे मत डालो।

---

## ➡️ Next Topic
**358. Deployment Status Badge** — showing live pipeline status on your README.
