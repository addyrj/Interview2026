# 382. ECS Task Definition
# हिंदी में: ECS Task Definition (container का blueprint)

---

## 🔵 Simple Definition (English)
A task definition is a versioned JSON blueprint that tells ECS how to run one or more containers together: image, CPU and memory, ports, environment variables, secrets, logging, health check and IAM roles. Every change creates a new numbered revision.

## 🔵 सरल परिभाषा (Hindi)
Task definition एक versioned JSON blueprint है जो ECS को बताता है कि एक या ज़्यादा containers साथ कैसे चलाने हैं: image, CPU और memory, ports, environment variables, secrets, logging, health check और IAM roles। हर बदलाव एक नया numbered revision बनाता है।

---

## 🔴 Problem it Solves
- `docker run` flags typed by hand differ per server; nobody remembers them.
- You need an immutable, reviewable record of exactly how a release runs.
- Rollback needs "go back to the previous settings", not just the previous image.

## 🔴 यह क्यों बना? (Hindi)
- हाथ से लिखे `docker run` flags हर server पर अलग होते हैं; किसी को याद नहीं रहते।
- एक immutable, reviewable record चाहिए कि release कैसे चल रहा है।
- Rollback का मतलब सिर्फ पुरानी image नहीं, पुरानी settings पर लौटना भी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write taskdef.json (family name = "api")
Step 2 → aws ecs register-task-definition -> returns api:1
Step 3 → Change image/env -> register again -> api:2 (api:1 stays unchanged)
Step 4 → Service points to api:2 -> ECS starts tasks from that revision
Step 5 → Rollback = point service to api:1
Step 6 → Old revisions can be deregistered (they become INACTIVE, not deleted)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → taskdef.json लिखो (family name = "api")
Step 2 → aws ecs register-task-definition -> api:1 मिलता है
Step 3 → image/env बदलो -> फिर register -> api:2 (api:1 वैसी ही रहती है)
Step 4 → Service api:2 पर point करती है -> ECS उसी revision से tasks चलाता है
Step 5 → Rollback = service को api:1 पर point करना
Step 6 → पुराने revisions deregister हो सकते हैं (INACTIVE होते हैं, delete नहीं)
```

---

## 🟡 Real World Example
An e-commerce API task has two containers: `api` (Node.js, 512 CPU units / 1024 MiB) and a `datadog-agent` sidecar. The environment has `NODE_ENV`, while `DATABASE_URL` and `JWT_SECRET` come from Secrets Manager. When the team doubled memory after an out-of-memory kill, it was just revision 41 -> 42; the diff in git shows exactly what changed.

## 🟡 Real Example Hindi mein
E-commerce API task में दो containers हैं: `api` (Node.js, 512 CPU units / 1024 MiB) और एक `datadog-agent` sidecar। Environment में `NODE_ENV` है, जबकि `DATABASE_URL` और `JWT_SECRET` Secrets Manager से आते हैं। Out-of-memory kill के बाद memory दोगुनी की गई तो बस revision 41 -> 42 बना; git diff में दिख जाता है क्या बदला।

---

## 💻 Code / Config Example — Basic

```json
{
  "family": "api",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/myapp-api:4f2a9c1d8e3b",
      "essential": true,
      "portMappings": [{ "containerPort": 3000, "protocol": "tcp" }]
    }
  ]
}
```

```bash
# register-basic.sh
aws ecs register-task-definition --cli-input-json file://taskdef.json   # creates api:N (JSON has no comments, so notes are here)
# family = name shared by all revisions; cpu 256 + memory 512 is a valid Fargate size combination
# executionRoleArn = lets ECS pull the image from ECR
```

## 💻 Code / Config Example — Advanced
Production: logs, secrets, health check, non-root, read-only filesystem, ulimits, stop timeout. (JSON cannot hold comments; each field is explained below the block.)

```json
{
  "family": "api",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "runtimePlatform": { "cpuArchitecture": "X86_64", "operatingSystemFamily": "LINUX" },
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/api-task-role",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/myapp-api:4f2a9c1d8e3b",
      "essential": true,
      "user": "1000:1000",
      "readonlyRootFilesystem": true,
      "stopTimeout": 30,
      "portMappings": [{ "containerPort": 3000, "protocol": "tcp" }],
      "environment": [
        { "name": "NODE_ENV", "value": "production" },
        { "name": "PORT", "value": "3000" }
      ],
      "secrets": [
        { "name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:prod/api/db-AbCdEf" },
        { "name": "JWT_SECRET", "valueFrom": "arn:aws:ssm:ap-south-1:123456789012:parameter/prod/api/jwt" }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "wget -qO- http://127.0.0.1:3000/health || exit 1"],
        "interval": 30, "timeout": 5, "retries": 3, "startPeriod": 40
      },
      "ulimits": [{ "name": "nofile", "softLimit": 65536, "hardLimit": 65536 }],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/api",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

Field notes: `user` runs as non-root; `readonlyRootFilesystem` blocks writes (mount a tmp volume if your app writes); `stopTimeout` gives the app 30 s after SIGTERM to finish requests; `secrets` are injected at start using the execution role (it needs `secretsmanager:GetSecretValue` / `ssm:GetParameters`); `taskRoleArn` is what your code uses (S3, SQS); `awslogs-group` must already exist or the execution role needs `logs:CreateLogGroup` (set `awslogs-create-group: "true"` to auto create); the health check command needs `wget` in the image (alpine has busybox wget). `startPeriod` ignores failures while booting.

---

## 🟠 My Stack Integration
FastAPI version: change port and command, and add a Nginx sidecar only if you need it. In ECS, containers in the same task share `localhost`.

```yaml
# mapping your compose service to a task definition fragment (explanatory YAML, not a registered file)
# FastAPI container
name: api                          # container name referenced by the service and ALB
image: ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com/myapp-fastapi:TAG   # your image
portMappings: [{containerPort: 8000}]   # uvicorn --host 0.0.0.0 --port 8000
command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]   # overrides CMD
# resource tip: workers x ~150 MB + overhead must fit in task memory
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Invalid Fargate CPU/memory pairs (e.g. cpu 256 with memory 4096).
✅ Correct: Use allowed combinations (256 CPU: 512/1024/2048 MiB; 512: 1-4 GiB; 1024: 2-8 GiB; check AWS docs for current table).

❌ Mistake 2: Putting secrets in `environment`.
✅ Correct: Use `secrets` with `valueFrom`; they do not appear in the console as plaintext.

❌ Mistake 3: Mixing up execution role and task role.
✅ Correct: Execution = pull/logs/secrets at startup. Task = app runtime permissions.

❌ Mistake 4: Hard-coded `latest` tag in the task definition.
✅ Correct: Register a new revision per image tag in CI.

❌ Mistake 5: No `stopTimeout` handling in app code (no SIGTERM handler).
✅ Correct: Handle SIGTERM, drain connections, then exit.

---

## 🧠 Tricky Interview Question
Task keeps stopping with exit code 137 about a minute after start. CPU is low. What is it?

Answer: 137 = SIGKILL, typically the container exceeded its memory limit (OOM kill; check `OutOfMemoryError: Container killed due to memory usage`). Node/Python used more than the task or container memory. Raise `memory`, set Node's `--max-old-space-size` below the limit, or fix a leak. Alternatively failing health checks cause ECS to kill it, which also shows in stopped reason.

---

## ⚫ Interview Questions + Answers

Q1: Why does each change create a new revision?
A1: Revisions are immutable; it gives audit trail, atomic rollback, and safe rollout.

Q2: `memory` vs `memoryReservation`?
A2: `memory` is a hard limit (container killed above it). `memoryReservation` is a soft limit used for placement. On Fargate the task-level memory is the bound.

Q3: How do two containers talk inside a task?
A3: Via `localhost` in awsvpc mode (shared network namespace), or `links`/volumes for files.

Q4: What does `essential: true` mean?
A4: If that container stops, ECS stops the whole task. Sidecars like log routers may be `false`.

Q5: How do you update only the image in CI?
A5: Describe the current definition, change `containerDefinitions[].image`, strip read-only fields, register, update service (see topic 386).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything that runs on ECS (service or one-off task)

❌ Avoid when:
- Single-container hobby deploys where Copilot / App Runner may be easier (App Runner abstracts this away)

---

## 📊 Visual Diagram
```
 family "api"
  rev 40 --> rev 41 --> rev 42 (current)
                         |
   +---------------------v----------------------+
   | cpu 512 / mem 1024 / awsvpc                |
   | container api  : image, ports, env, secrets|
   | container side : log router (optional)     |
   | roles: execution (pull), task (app)        |
   +--------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Family | Name grouping revisions | Revisions का नाम |
| Revision | One immutable version | एक अपरिवर्तनीय version |
| essential | Container whose death stops the task | जिसके बंद होने पर task बंद |
| Execution role | Pull images and secrets | Image और secrets लाने वाला role |
| Task role | App's AWS permissions | App की AWS permissions |
| Sidecar | Helper container in the same task | साथ चलने वाला helper container |

---

## ⚡ 3-Line Summary
English: A task definition is the immutable, versioned recipe for running containers on ECS.
Put secrets in `secrets`, logs in awslogs, and use two separate IAM roles.
CI registers a new revision per image tag; rollback is pointing back to an old one.

Hindi: Task definition ECS पर containers चलाने की immutable, versioned recipe है।
Secrets को `secrets` में, logs awslogs में रखो, और दो अलग IAM roles इस्तेमाल करो।
CI हर image tag पर नया revision बनाता है; rollback का मतलब पुराने revision पर लौटना है।

---

## ➡️ Next Topic
383. ECS Service: how revisions are kept running, balanced and updated.
