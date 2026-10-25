# 264. Deploy on AWS ECS + Docker
# हिंदी में: AWS ECS और Docker से Deploy करना

---

## 🔵 Simple Definition (English)
**Docker** packages your Node.js app and everything it needs (Node runtime, dependencies, OS libraries) into a single portable **image** that runs identically anywhere. **AWS ECS (Elastic Container Service)** is a managed service that runs your Docker containers at scale — you push your image to **ECR** (Elastic Container Registry), define a **task definition** (what to run, how much CPU/memory), and ECS runs it either on **Fargate** (serverless, no servers to manage) or on EC2 instances you manage yourself (EC2 launch type).

## 🔵 सरल परिभाषा (Hindi)
**Docker** आपके Node.js app और उसकी सारी ज़रूरतों (Node runtime, dependencies, OS libraries) को एक portable **image** में package करता है जो हर जगह एक जैसा चलती है। **AWS ECS (Elastic Container Service)** एक managed service है जो आपके Docker containers को scale पर चलाती है — image को **ECR** पर push करो, एक **task definition** बनाओ (क्या चलाना है, कितना CPU/memory चाहिए), और ECS उसे **Fargate** (serverless, कोई server manage नहीं करना) या खुद manage किए EC2 instances (EC2 launch type) पर चलाता है।

---

## 🔴 Problem it Solves
```
BEFORE DOCKER (raw EC2 deploys):
  1. "Works on my machine" but fails on the server — different Node version,
     missing system library, OS-level config drift
  2. Each service needs manual setup: install Node, PM2, Nginx, dependencies
  3. Running multiple services with CONFLICTING dependency versions on one 
     EC2 box is painful (Service A needs Node 16, Service B needs Node 20)
  4. Scaling means manually launching + configuring more EC2 instances

DOCKER + ECS SOLUTION:
  1. Dockerfile defines EXACTLY the environment — same image runs identically
     on your laptop, staging, and production. No more "works on my machine."
  2. Each service is isolated in its own container — no dependency conflicts
  3. ECS handles scheduling, scaling, and restarting containers automatically
  4. Fargate removes server management ENTIRELY — no EC2 instances to patch, 
     no OS to maintain — you just describe the container and AWS runs it

STILL SOME TRADEOFFS:
  - Cold starts / image pull time can add latency vs an already-running EC2 process
  - Fargate costs more per-unit-of-compute than a fully utilized EC2 instance
  - Slightly more moving parts (ECR, task definitions, services) than plain EC2
```

## 🔴 यह क्यों बना? (Hindi)
Raw EC2 deploys में "मेरे machine पर चलता है" वाली problem आम थी — अलग Node version, missing library, OS config drift की वजह से production fail हो जाता था। कई services को एक EC2 box पर चलाना dependency conflicts लाता था। Docker इसे solve करता है — पूरा environment एक image में fix कर देता है, हर जगह identically चलती है। ECS उसके ऊपर scheduling, scaling, restart automatic कर देता है, और Fargate के साथ तो कोई EC2 instance manage करने की ज़रूरत भी नहीं पड़ती।

---

## 🟢 How it Works — Step by Step

Step 1 → **Write a Dockerfile**: describes the base image (e.g., `node:20-alpine`), copies app code, installs dependencies, and defines the start command.
Step 2 → **Use multi-stage builds**: one stage installs dependencies and builds the app (including devDependencies, TypeScript compilation etc.), a second, smaller final stage copies only the built output + production dependencies — resulting in a much smaller final image.
Step 3 → **Build and tag the image**: `docker build -t myapp:v1 .` then `docker push` it to **ECR** (AWS's private Docker registry), after authenticating via `aws ecr get-login-password`.
Step 4 → **Create a Task Definition**: a JSON blueprint describing which container image to run, how much CPU/memory to allocate, port mappings, environment variables, and logging configuration (CloudWatch Logs).
Step 5 → **Create an ECS Service**: tells ECS to keep N copies ("tasks") of that task definition running at all times, optionally behind an Application Load Balancer, with auto-scaling rules based on CPU/memory or request count.
Step 6 → **Choose launch type**: **Fargate** — AWS manages the underlying compute entirely, you just pay per vCPU/memory-second the task uses; or **EC2 launch type** — ECS schedules containers onto EC2 instances that YOU provision and manage (more control, often cheaper at sustained high utilization, but you manage the instances).
Step 7 → **Auto-scaling**: configure an ECS Service Auto Scaling policy (target tracking on CPU%, memory%, or ALB request count) so ECS automatically adds/removes tasks as load changes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Dockerfile लिखो**: base image बताओ (जैसे `node:20-alpine`), app code copy करो, dependencies install करो, start command define करो।
Step 2 → **Multi-stage builds use करो**: एक stage dependencies install करता है और app build करता है (devDependencies, TypeScript compile सहित), दूसरा छोटा final stage सिर्फ built output + production dependencies copy करता है — नतीजा: बहुत छोटी final image।
Step 3 → **Image build और tag करो**: `docker build -t myapp:v1 .` फिर उसे **ECR** (AWS की private Docker registry) पर push करो, `aws ecr get-login-password` से authenticate करके।
Step 4 → **Task Definition बनाओ**: एक JSON blueprint जो बताता है कौन सी container image चलानी है, कितना CPU/memory, port mappings, environment variables, और logging config (CloudWatch Logs)।
Step 5 → **ECS Service बनाओ**: ECS को बताओ कि उस task definition के N copies ("tasks") हमेशा चलते रहने चाहिए, optionally Application Load Balancer के पीछे, CPU/memory या request count के आधार पर auto-scaling rules के साथ।
Step 6 → **Launch type चुनो**: **Fargate** — AWS पूरा underlying compute manage करता है, आप सिर्फ task के use किए vCPU/memory-second के हिसाब से pay करते हो; या **EC2 launch type** — ECS containers को खुद provision किए EC2 instances पर schedule करता है (ज़्यादा control, sustained high utilization पर अक्सर सस्ता, पर instances खुद manage करने पड़ते हैं)।
Step 7 → **Auto-scaling**: ECS Service Auto Scaling policy configure करो (CPU%, memory%, या ALB request count पर target tracking) ताकि load बदलने पर ECS automatically tasks add/remove करे।

---

## 🟡 Real World Example
**A Paytm-style notification microservice** is Dockerized and deployed on ECS Fargate. During normal hours it runs 3 tasks (containers) handling SMS/push notification dispatch. The team configures ECS Service Auto Scaling to track CPU utilization — during a festival sale when notification volume spikes 10x, ECS automatically scales from 3 to 15 tasks within minutes, each task getting its own isolated container with the exact same image (no config drift). After the sale ends, ECS scales back down to 3 tasks, and the team only pays for the extra Fargate compute-seconds actually used during the spike — no idle EC2 instances sitting around the rest of the year. Compare this to the old EC2 setup, where the team had to manually launch extra instances before every known sale and remember to terminate them afterward.

## 🟡 Real Example Hindi mein
**Paytm-style notification microservice** Dockerize होकर ECS Fargate पर deploy होता है। Normal hours में 3 tasks (containers) SMS/push notification dispatch handle करते हैं। Team ECS Service Auto Scaling को CPU utilization track करने के लिए configure करती है — festival sale के दौरान जब notification volume 10x बढ़ता है, ECS automatically 3 से 15 tasks तक minutes में scale कर जाता है, हर task अपना isolated container, exact same image के साथ (कोई config drift नहीं)। Sale खत्म होने पर ECS वापस 3 tasks पर scale down कर देता है, और team सिर्फ spike के दौरान actually use हुए extra Fargate compute-seconds का pay करती है — साल भर idle EC2 instances नहीं बैठे रहते। पुराने EC2 setup से compare करो, जहाँ team को हर known sale से पहले manually extra instances launch करनी पड़ती थीं और बाद में terminate करना याद रखना पड़ता था।

---

## 💻 Code Example — Basic

```dockerfile
# Dockerfile — basic single-stage build for a Node.js Express app
FROM node:20-alpine                   # lightweight base image with Node 20 installed

WORKDIR /app                          # all subsequent commands run from /app inside the container

COPY package*.json ./                 # copy only package files first (better Docker layer caching)
RUN npm install --production          # install only production dependencies

COPY . .                              # copy the rest of the app code

EXPOSE 3000                           # document which port the container listens on

CMD ["node", "server.js"]             # command to run when the container starts
```

```javascript
// server.js — the app the Dockerfile runs
const express = require('express');
const app = express();

app.get('/health', (req, res) => res.status(200).send('ok'));  // for ECS health checks

app.get('/', (req, res) => {
  res.json({ message: 'Running inside a Docker container on ECS', pid: process.pid });
});

// IMPORTANT: bind to 0.0.0.0 inside a container, not 127.0.0.1 —
// the container's network namespace needs this to accept traffic from outside itself
app.listen(3000, '0.0.0.0', () => console.log('App listening on 0.0.0.0:3000'));
```

```bash
# Build and run locally to test before pushing to ECR
docker build -t notification-service:v1 .            # build the image from the Dockerfile
docker run -p 3000:3000 notification-service:v1       # run it locally, map container port to host
curl http://localhost:3000/health                      # verify it responds
```

## 💻 Code Example — Advanced

```dockerfile
# Dockerfile — multi-stage build: smaller, more secure final image
# ─── STAGE 1: build ──────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci                              # installs exact versions from package-lock.json (incl. devDeps)
COPY . .
RUN npm run build                       # e.g. TypeScript compile, or bundling step

# ─── STAGE 2: production — only what's needed to RUN the app ───
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --omit=dev                   # install ONLY production dependencies, smaller node_modules

COPY --from=builder /app/dist ./dist    # copy ONLY the compiled output from the builder stage
                                         # devDependencies, source TS files, test files never reach
                                         # the final image — smaller size, smaller attack surface

# Run as a non-root user — security best practice, don't run containers as root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', r => process.exit(r.statusCode===200?0:1))"
  # Docker-level health check — ECS reads this too when deciding container health

CMD ["node", "dist/server.js"]
```

```json
// task-definition.json — ECS Fargate task definition
{
  "family": "notification-service",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "notification-service",
      "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/notification-service:v1",
      "portMappings": [{ "containerPort": 3000, "protocol": "tcp" }],
      "environment": [
        { "name": "NODE_ENV", "value": "production" },
        { "name": "QUEUE_URL", "value": "https://sqs.ap-south-1.amazonaws.com/123456789012/notify-queue" }
      ],
      "secrets": [
        { "name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:db-url" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/notification-service",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

```bash
# advanced-ecs-deploy.sh — push to ECR and deploy to ECS

# 1. Authenticate Docker to ECR
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com

# 2. Build, tag, and push the image
docker build -t notification-service:v1 .
docker tag notification-service:v1 123456789012.dkr.ecr.ap-south-1.amazonaws.com/notification-service:v1
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/notification-service:v1

# 3. Register the new task definition revision
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 4. Update the ECS service to use the new task definition (rolling deploy, zero downtime)
aws ecs update-service --cluster my-cluster --service notification-service \
  --task-definition notification-service --force-new-deployment

# 5. Set up auto-scaling based on CPU utilization
aws application-autoscaling register-scalable-target \
  --service-namespace ecs --resource-id service/my-cluster/notification-service \
  --scalable-dimension ecs:service:DesiredCount --min-capacity 3 --max-capacity 20
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app written to behave well inside an ECS Fargate container
const express = require('express');
const app = express();
app.use(express.json());

// ECS health check hits this via the task definition's healthCheck command
app.get('/health', (req, res) => res.status(200).json({ status: 'healthy' }));

// Read secrets injected by ECS from Secrets Manager (via "secrets" in task-definition.json)
const dbUrl = process.env.DATABASE_URL;

app.post('/notifications', async (req, res) => {
  const { userId, message } = req.body;
  if (!userId || !message) return res.status(400).json({ error: 'userId and message required' });
  // ... push to SQS queue for async processing by a worker task ...
  res.status(202).json({ status: 'queued' });
});

// Graceful shutdown — ECS sends SIGTERM when stopping a task (e.g., during a deploy or scale-in)
const server = app.listen(3000, '0.0.0.0', () => console.log('Listening on 0.0.0.0:3000'));
process.on('SIGTERM', () => {
  console.log('ECS is stopping this task, draining connections...');
  server.close(() => process.exit(0));
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Binding the app to `127.0.0.1` inside a container
```javascript
// WRONG — inside Docker, 127.0.0.1 only accepts traffic from WITHIN the container itself;
// ECS/the load balancer can never reach it, health checks fail, task never becomes healthy
app.listen(3000, '127.0.0.1');

// RIGHT — bind to 0.0.0.0 so the container accepts traffic from outside its own namespace
app.listen(3000, '0.0.0.0');
```

❌ **Mistake 2:** Copying `node_modules` and dev dependencies into the final production image
```dockerfile
# WRONG — single stage, includes devDependencies, test files, source TS — bloated, slower pulls,
# larger attack surface
FROM node:20
COPY . .
RUN npm install                 # installs devDependencies too!
CMD ["node", "server.js"]

# RIGHT — multi-stage build, final image has only production deps + compiled output
FROM node:20-alpine AS builder
COPY . .
RUN npm ci && npm run build
FROM node:20-alpine
COPY --from=builder /app/dist ./dist
RUN npm ci --omit=dev
CMD ["node", "dist/server.js"]
```

❌ **Mistake 3:** Hardcoding secrets as plain environment variables in the task definition
```json
// WRONG — DATABASE_URL with credentials visible in plain text in the task definition JSON
{ "environment": [{ "name": "DATABASE_URL", "value": "mongodb://admin:pass123@prod-db" }] }

// RIGHT — reference AWS Secrets Manager / SSM Parameter Store; ECS injects the real value at runtime
{ "secrets": [{ "name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:...:db-url" }] }
```

---

## 🧠 Tricky Interview Question

**Q: You update your ECS service's task definition with a new image and run `aws ecs update-service --force-new-deployment`. During the deploy, do all old tasks get killed before new ones start, like a naive EC2 restart?**

**Answer:** No — by default, ECS performs a **rolling deployment** governed by the service's `deploymentConfiguration` (`minimumHealthyPercent` and `maximumPercent`). With typical defaults (`minimumHealthyPercent: 100`, `maximumPercent: 200`), ECS first launches NEW tasks with the updated task definition (potentially doubling task count temporarily), waits for them to pass their health checks and register as healthy in the target group, and only THEN starts draining and stopping the OLD tasks — one batch at a time. This means, just like PM2's `reload` or a Kubernetes rolling deployment, there is no moment where zero healthy tasks are serving traffic, as long as your health check endpoint is correctly configured and your app handles `SIGTERM` gracefully to drain in-flight requests during the old task's shutdown.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between the ECS Fargate launch type and the EC2 launch type?**
A1: With the **Fargate** launch type, AWS manages the underlying compute entirely — you specify CPU/memory per task and AWS provisions the infrastructure behind the scenes; you never see or manage an EC2 instance, and you pay per vCPU/memory-second each task actually uses. With the **EC2 launch type**, YOU provision and manage a fleet of EC2 instances (an "ECS cluster" of EC2 instances running the ECS agent), and ECS schedules containers ("tasks") onto those instances, similar to how Kubernetes schedules pods onto nodes. EC2 launch type gives more control and can be cheaper at high, sustained utilization (since you're not paying Fargate's per-task premium), but you're back to managing instance patching and capacity.

**Q2: Why use a multi-stage Dockerfile instead of a single-stage one?**
A2: A multi-stage build separates the "build environment" (which needs devDependencies, compilers, source files, build tools) from the "runtime environment" (which only needs the compiled output and production dependencies). The final stage only copies what's needed to RUN the app (`COPY --from=builder`), discarding everything else. This produces a significantly smaller final image (faster to push/pull/deploy), reduces the attack surface (no dev tools or source maps in production), and keeps build-time secrets/tools out of the shipped image entirely.

**Q3: What is ECR and why do you need it before deploying to ECS?**
A3: **ECR (Elastic Container Registry)** is AWS's private Docker image registry — similar to Docker Hub but integrated with AWS IAM permissions and within your AWS account/region. ECS task definitions reference a container image by its registry URL, so you must build your Docker image, tag it with your ECR repository's URI, and `docker push` it to ECR before ECS can pull and run it. Using ECR (vs a public registry) keeps your proprietary application images private and benefits from fast, same-region image pulls.

**Q4: How does ECS auto-scaling work, and how is it different from EC2 Auto Scaling Groups?**
A4: ECS Service Auto Scaling adjusts the **number of running tasks (containers)** for a service based on a target-tracking metric (e.g., keep average CPU utilization at 50% — scale out if above, scale in if below), or based on custom CloudWatch metrics like ALB request count per target. This operates at the container/task level. EC2 Auto Scaling Groups, in contrast, adjust the number of underlying EC2 INSTANCES (virtual machines) based on similar metrics. On Fargate, you only need ECS Service Auto Scaling since there's no EC2 fleet to manage. On the EC2 launch type, you may need BOTH — an EC2 Auto Scaling Group to ensure enough instance capacity exists, AND ECS Service Auto Scaling to decide how many task copies to run on that capacity.

**Q5: What's the main operational difference between deploying on raw EC2 (topic 263) versus ECS + Docker?**
A5: On raw EC2, you SSH in, manually install Node/PM2/Nginx, and manage the OS and runtime environment directly on a persistent server — you own patching, dependency management, and process supervision (PM2). With ECS + Docker, the application and its entire runtime environment are packaged into an immutable image; ECS handles scheduling, restarting failed containers, rolling deployments, and (with Fargate) removes the underlying server entirely from your responsibility. The tradeoff is added complexity (Dockerfiles, ECR, task definitions, services) in exchange for consistency ("works the same everywhere"), easier horizontal scaling, and less day-to-day server maintenance.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want consistent environments across dev/staging/production ("works on my machine" eliminated)
- You're running multiple microservices with different, possibly conflicting dependency requirements
- You want Fargate's serverless container model to avoid managing EC2 instances at all
- Your workload benefits from fast, automated horizontal auto-scaling

❌ Avoid when:
- You have a single, simple app and the team has no Docker/container experience — raw EC2 + PM2 may ship faster initially
- Workload is extremely steady and already well-utilized on EC2 — Fargate's per-task pricing premium may cost more than a fully-utilized EC2 fleet
- You need low-level OS access or kernel-level customization that containers restrict

---

## 📊 Visual Diagram
```
DOCKER + ECS FARGATE DEPLOYMENT FLOW
──────────────────────────────────────────────────────────

  Dockerfile ──▶ docker build ──▶ image (local)
                                       │
                                       ▼
                              docker push to ECR
                                       │
                                       ▼
                        ┌───────────────────────────┐
                        │   ECS Task Definition      │   (CPU, memory, image URI, env, secrets)
                        └─────────────┬───────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │      ECS Service           │   (desired count, auto-scaling policy)
                        └─────────────┬───────────────┘
              ┌───────────────┬───────┴───────┬───────────────┐
              ▼               ▼               ▼               ▼
         ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
         │ Task 1   │    │ Task 2   │    │ Task 3   │    │ Task N   │   <- Fargate: no EC2 to manage
         │(container)│   │(container)│   │(container)│   │(container)│
         └─────────┘    └─────────┘    └─────────┘    └─────────┘
              └───────────────┴───────────────┴───────────────┘
                                      │
                                      ▼
                         Application Load Balancer
                                      │
                                      ▼
                                   Internet

  Rolling deploy: new tasks start + pass health check BEFORE old tasks are stopped
  Auto-scaling: CPU% / request-count metric → ECS adds/removes tasks automatically
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Docker Image | Packaged app + runtime environment | App + environment का package |
| Dockerfile | Recipe to build an image | Image बनाने की recipe |
| Multi-stage Build | Separate build and runtime stages | Build और runtime अलग stages |
| ECR | AWS's private Docker registry | AWS की private Docker registry |
| ECS | AWS container orchestration service | AWS container orchestration |
| Task Definition | Blueprint describing a container run | Container चलाने का blueprint |
| Fargate | Serverless container compute | Serverless container compute |
| ECS Service | Keeps N tasks running, handles deploys | N tasks चलाए रखता है |
| Auto Scaling | Automatically adjust task/instance count | Automatic task count adjust |
| Rolling Deployment | Gradual task replacement | धीरे-धीरे tasks replace करना |

---

## ⚡ 3-Line Summary
**English:**
1. Docker packages a Node.js app and its entire runtime environment into a portable image, eliminating "works on my machine" problems.
2. ECS runs these images at scale via task definitions and services, on Fargate (serverless, no EC2 to manage) or the EC2 launch type (more control).
3. ECS handles rolling deployments and auto-scaling automatically based on health checks and CPU/memory/request metrics, unlike manual EC2 management.

**Hindi:**
1. Docker एक Node.js app और उसका पूरा runtime environment एक portable image में package करता है, "मेरे machine पर चलता है" वाली problem खत्म करता है।
2. ECS इन images को scale पर चलाता है task definitions और services के through, Fargate पर (serverless, कोई EC2 manage नहीं) या EC2 launch type पर (ज़्यादा control)।
3. ECS rolling deployments और auto-scaling automatically handle करता है health checks और CPU/memory/request metrics के आधार पर, manual EC2 management के विपरीत।

---

## ➡️ Next Topic
**265. AWS Lambda + Node.js** — Serverless functions, cold starts, API Gateway integration, और event-driven Node.js architecture।
