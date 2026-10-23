# 155. Deploy AI App (Docker + AWS)
# हिंदी में: AI ऐप को Docker और AWS पर deploy करना — FastAPI AI service, background workers (embeddings/ingestion), Postgres + pgvector, Redis को containers में पैक करना और AWS (ECS Fargate, ALB, RDS, ElastiCache, S3, SQS, Secrets Manager) पर GitHub Actions CI/CD के साथ चलाना — streaming, scaling, सुरक्षा, ख़र्च और डेटा भारत में

---

## 🔵 Simple Definition (English)
Deploying an AI application means packaging and running the **API service** (e.g., FastAPI or Node with the LLM gateway, RAG, tools and streaming), **background workers** (document ingestion, embeddings, batch jobs, evals), and **data stores** (Postgres + pgvector, Redis, S3), reliably, securely and cost-effectively.
A common AWS setup:
- **Docker images** (multi-stage, slim, non-root) pushed to **Amazon ECR**.
- **ECS on Fargate** services (API + workers), or EKS if you already run Kubernetes, behind an **Application Load Balancer** with a long idle timeout for streaming.
- **RDS/Aurora PostgreSQL with pgvector**, **ElastiCache Redis** (cache, rate limits, sessions, semantic cache), **S3** (documents), **SQS** (ingestion queue).
- **Secrets Manager / SSM Parameter Store** for API keys, and **IAM task roles** (no static AWS keys).
- LLM access via provider APIs (Anthropic, OpenAI) over NAT egress, or **Amazon Bedrock** (Claude and other models through AWS IAM, VPC endpoints and regional options).
- **CloudWatch / OpenTelemetry** for logs, metrics and traces, plus an LLM observability tool (Topic 147).
- **GitHub Actions CI/CD** with OIDC to AWS: tests plus an **eval gate**, then build, push, deploy (rolling or blue/green) and smoke test.
- **Terraform** for infrastructure as code.
Optional **GPU self-hosting** (EKS GPU nodes or SageMaker with vLLM) for open or fine-tuned models.

## 🔵 सरल परिभाषा (Hindi)
AI ऐप deploy करना = API service (FastAPI/Node — LLM gateway, RAG, tools, streaming), background workers (documents ingestion, embeddings, batch jobs, evals) और data stores (Postgres + pgvector, Redis, S3) को भरोसे, सुरक्षा और कम ख़र्च से चलाना।
AWS पर आम ढाँचा: Docker images (multi-stage, छोटी, non-root) → ECR; ECS Fargate (API + workers) या EKS, आगे ALB (streaming के लिए लंबा idle timeout); RDS Postgres + pgvector, ElastiCache Redis, S3, SQS; Secrets Manager में API keys और IAM task roles (कोई स्थायी AWS key नहीं); LLM — provider APIs (NAT से) या Amazon Bedrock; CloudWatch/OpenTelemetry + LLM observability; GitHub Actions (OIDC) — tests + eval gate → build → push → deploy → smoke test; Terraform; ज़रूरत हो तो GPU पर vLLM।

---

## 🔴 Problem it Solves
An AI prototype on a laptop (`uvicorn main:app` + a local vector DB + an API key in `.env`) fails in production:
- **Secrets leak** (keys in images or Git), with no rotation.
- **Streaming breaks** behind load balancers (60 s timeouts, buffering).
- **Ingestion blocks the API**: embedding 10,000 PDFs in the request path causes timeouts. It needs **async workers and queues**.
- **No scaling**: traffic spikes (sale day) overload a single server, and LLM rate limits cause cascading failures without retries and backpressure.
- **No reproducibility** ("works on my machine"), and no safe rollouts or rollback.
- **Compliance**: Indian BFSI and health data must stay in-region (Mumbai/Hyderabad), and traffic to external LLM APIs needs review and egress controls.
- **Cost surprises**: idle GPUs, oversized instances, no token budgets.
A disciplined deployment gives **reproducible builds, secure secrets, scalable services, safe releases, observability and controlled cost**.

## 🔴 यह क्यों बना? (Hindi)
Laptop का AI prototype (`uvicorn` + local vector DB + `.env` में API key) production में टूटता है: keys image/Git में leak; load balancer पर streaming टूटे (60 सेकंड timeout, buffering); 10,000 PDFs का embedding request के अंदर — timeouts (async workers + queue चाहिए); sale वाले दिन एक server बैठ जाए, LLM rate limits पर बिना retry/backpressure के सब गिरे; "मेरे laptop पर चलता है", सुरक्षित rollout/rollback नहीं; भारत के BFSI/health डेटा को Mumbai/Hyderabad में रखना और बाहरी LLM APIs पर egress नियंत्रण; बेकार GPUs और बड़े instances से ख़र्च।
अनुशासित deployment = दोहराने लायक builds, सुरक्षित secrets, scale होने वाली services, सुरक्षित releases, निगरानी और नियंत्रित ख़र्च।

---

## 🟢 How it Works — Step by Step

### Reference architecture (AWS, ap-south-1 Mumbai)

```
Users (RN app / Next.js web)
   │ HTTPS
   ▼
CloudFront (static web) + AWS WAF ──► ALB (HTTPS, idle timeout 300 s for SSE)
                                         │
                       ┌─────────────────┴──────────────────┐
                       ▼                                    ▼
              ECS Fargate: ai-api (FastAPI,       ECS Fargate: ai-worker (SQS consumers:
              uvicorn workers, streaming)          ingestion, embeddings, batch jobs, evals)
                 │   │   │   │                             │      │
     ┌───────────┘   │   │   └──────────┐                  │      │
     ▼               ▼   ▼              ▼                  ▼      ▼
 RDS Postgres     ElastiCache   Secrets Manager        S3 (docs)  SQS (+ DLQ)
 + pgvector       Redis         (LLM keys, DB creds)
 (Multi-AZ)       (cache, rate
                   limits)
     │
 Private subnets; outbound to LLM providers via NAT Gateway (egress allow-list) or Amazon Bedrock via VPC endpoint
 Observability: CloudWatch Logs/Metrics, OTel → X-Ray/Grafana, LLM tracing (LangSmith/Langfuse, PII-redacted)
 Optional GPU tier: EKS GPU node group / SageMaker endpoint running vLLM for fine-tuned open models
```

### Containerization best practices

```
Multi-stage Dockerfile: build deps in builder stage; slim runtime (python:3.12-slim / distroless)
Pin dependency versions (uv/poetry lock), no secrets in image, non-root user, read-only filesystem where possible
Healthcheck endpoint (/healthz liveness, /readyz readiness checks DB/Redis connectivity — not the LLM provider)
Graceful shutdown: handle SIGTERM, stop accepting new streams, finish in-flight within deregistration delay
Workers: separate image entrypoint (same codebase), concurrency via async or processes
Local dev: docker compose (api, worker, postgres+pgvector, redis, localstack optional)
```

### Configuration & secrets

```
Secrets Manager / SSM → injected into ECS task definitions as secrets (env at runtime), rotated
IAM task roles for S3/SQS/Bedrock access (least privilege); no long-lived AWS keys anywhere
Separate environments (dev/staging/prod) with separate accounts or at least separate keys & budgets
Feature flags/remote config for model routing, degraded modes, kill switches (Topic 151)
```

### Scaling & resilience

```
API: autoscale on CPU + concurrent requests/streams (ALB RequestCountPerTarget); streaming is I/O-bound →
     async workers handle many concurrent streams per task
Workers: autoscale on SQS queue depth/age; DLQ for poison messages; idempotent jobs
DB: RDS Multi-AZ, read replica for heavy retrieval if needed, connection pooling (RDS Proxy/pgbouncer)
LLM limits: client-side rate limiting (Redis token bucket) + retries with backoff + provider fallback;
     priority queue for live chat vs background jobs
Deploys: rolling or blue/green (CodeDeploy) with health checks; deregistration delay ≥ max stream length
     (or accept stream interruption with client reconnect/resume — Topic 154)
```

### CI/CD pipeline

```
PR: lint, type-check, unit tests, contract tests, prompt-size checks, OFFLINE EVALS (smoke set) gate
main: build image → scan (ECR scan/Trivy) → push to ECR (tag = git SHA) → deploy to staging →
      full eval suite + load test (streaming) → manual/auto approval → deploy prod (blue/green)
      → smoke tests → monitor error rate, TTFT, cost → auto-rollback on alarms
Auth: GitHub Actions OIDC → assume deploy role (no stored AWS keys)
IaC: Terraform modules for VPC, ECS, ALB, RDS, Redis, SQS, IAM; plan on PR, apply on merge
```

### Cost & compliance

```
Right-size Fargate tasks; Savings Plans for steady load; scale workers to zero when queue empty
Token budgets & dashboards per feature/tenant (Topic 153); alarms on daily LLM spend
Data residency: keep DB, S3, logs, vector index in ap-south-1/ap-south-2; review what leaves the region
  (prompts to LLM providers) → DPAs, zero-retention options, or Bedrock regional models where available
Encryption: KMS at rest (RDS, S3, Redis), TLS in transit; audit with CloudTrail
```

## 🟢 कैसे काम करता है? (Hindi)
1. ढाँचा (Mumbai): CloudFront + WAF → ALB (SSE के लिए 300 सेकंड idle timeout) → ECS Fargate पर ai-api (FastAPI streaming) और ai-worker (SQS से ingestion, embeddings, batch, evals) → RDS Postgres + pgvector (Multi-AZ), ElastiCache Redis, Secrets Manager, S3, SQS + DLQ; private subnets, बाहर LLM providers तक NAT (egress allow-list) या VPC endpoint से Bedrock; ज़रूरत हो तो EKS/SageMaker पर vLLM GPU।
2. Containers: multi-stage Dockerfile, छोटी image, versions pin, image में कोई secret नहीं, non-root user; `/healthz` और `/readyz` (DB/Redis जाँचे, LLM provider नहीं); SIGTERM पर नए streams बंद करके चलते पूरे करो; workers उसी codebase की अलग entrypoint; local के लिए docker compose।
3. Secrets Manager/SSM से runtime पर secrets, IAM task roles (S3/SQS/Bedrock), कोई स्थायी AWS key नहीं; dev/staging/prod अलग keys और budgets; model routing और kill switches के लिए flags।
4. Scaling: API CPU + concurrent streams पर (streaming I/O-bound, async से एक task कई streams), workers SQS queue गहराई पर, DLQ, idempotent jobs; RDS Proxy/pgbouncer; LLM सीमाओं के लिए Redis token bucket + backoff + fallback; deploy blue/green और deregistration delay ≥ सबसे लंबा stream।
5. CI/CD: PR पर lint, tests, prompt आकार, offline evals; main पर build → scan → ECR (git SHA tag) → staging → पूरे evals + streaming load test → prod blue/green → smoke → alarms पर auto-rollback; GitHub OIDC; Terraform; ख़र्च — सही आकार, queue ख़ाली तो workers शून्य, LLM ख़र्च alarms; डेटा ap-south-1/2 में, बाहर जाने वाले prompts की समीक्षा, KMS encryption, CloudTrail।

---

## 🟡 Real World Example

**Amazon Bedrock** — enterprises (including Indian banks, insurers and IT services firms) often access Claude and other models through Bedrock for IAM-based access, VPC networking, consolidated billing, regional options and existing AWS compliance programs, deploying their RAG services on ECS or EKS around it.

**ECS Fargate for API + workers** — a very common pattern for startups' AI backends: no servers to manage, separate services for streaming APIs and queue-driven ingestion workers, autoscaling on request count and queue depth, and RDS Postgres with pgvector for retrieval.

**Streaming behind ALB** — teams regularly hit the ALB default 60 s idle timeout and Nginx buffering when first deploying chat streaming. Raising timeouts, disabling buffering and adding heartbeats are standard production fixes (Topic 154).

**Data residency in India** — with AWS regions in Mumbai (ap-south-1) and Hyderabad (ap-south-2), Indian companies keep databases, documents, embeddings and logs in-country to align with RBI and sectoral data-localization expectations and the DPDP Act, reviewing which data is sent to external model providers.

## 🟡 Real Example Hindi में
भारतीय बैंक, insurance और IT कंपनियाँ अक्सर Claude और दूसरे models Amazon Bedrock से इस्तेमाल करती हैं — IAM, VPC, एक बिल, क्षेत्रीय विकल्प, AWS compliance — और RAG services ECS/EKS पर; startups में ECS Fargate पर streaming API और queue वाले ingestion workers अलग services + RDS Postgres/pgvector बहुत आम।
पहली बार chat streaming deploy करते समय ALB का 60 सेकंड timeout और Nginx buffering आम समस्या — timeouts बढ़ाना, buffering बंद, heartbeats; AWS Mumbai (ap-south-1) और Hyderabad (ap-south-2) में DB, documents, embeddings, logs भारत में रखकर RBI और DPDP के अनुसार, और बाहरी model providers को जाने वाले डेटा की समीक्षा।

---

## 🟠 My Stack Example

### Dockerfile (FastAPI AI API, multi-stage, non-root)
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project       # deps into /app/.venv

FROM python:3.12-slim
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
RUN useradd -r -u 10001 appuser
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')"
# Many concurrent streams per task: async app + multiple uvicorn workers
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--timeout-graceful-shutdown", "60"]
```

### docker-compose for local dev (api + worker + pgvector + redis)
```yaml
services:
  api:
    build: .
    env_file: .env.local                     # local only; never commit real keys
    ports: ["8000:8000"]
    depends_on: [db, redis]
  worker:
    build: .
    command: ["python", "-m", "src.worker"]  # SQS/Redis-queue consumer for ingestion & embeddings
    env_file: .env.local
    depends_on: [db, redis]
  db:
    image: pgvector/pgvector:pg16
    environment: { POSTGRES_PASSWORD: dev, POSTGRES_DB: app }
    ports: ["5432:5432"]
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### Health/readiness + graceful shutdown (FastAPI)
```python
@app.get("/healthz")
async def healthz(): return {"ok": True}                         # liveness: process up

@app.get("/readyz")
async def readyz():
    await db.execute("SELECT 1"); await redis.ping()             # readiness: deps reachable (not the LLM provider)
    return {"ready": True}

@app.on_event("shutdown")
async def shutdown():
    accepting_streams.clear()                                    # stop new streams; in-flight finish within grace period
```

### Terraform sketch: ECS service with secrets, ALB idle timeout, autoscaling
```hcl
resource "aws_lb" "ai" {
  name               = "ai-alb"
  load_balancer_type = "application"
  subnets            = var.public_subnets
  idle_timeout       = 300                                       # SSE streaming
}

resource "aws_ecs_task_definition" "api" {
  family                   = "ai-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  task_role_arn            = aws_iam_role.api_task.arn           # least-privilege access to S3/SQS/Bedrock
  execution_role_arn       = aws_iam_role.exec.arn
  container_definitions = jsonencode([{
    name  = "api", image = "${var.ecr_repo}:${var.image_tag}", portMappings = [{ containerPort = 8000 }]
    secrets = [
      { name = "ANTHROPIC_API_KEY", valueFrom = aws_secretsmanager_secret.anthropic.arn },
      { name = "DATABASE_URL",      valueFrom = aws_secretsmanager_secret.db_url.arn }
    ]
    environment = [{ name = "APP_ENV", value = "prod" }, { name = "AWS_REGION", value = "ap-south-1" }]
    logConfiguration = { logDriver = "awslogs", options = { awslogs-group = "/ecs/ai-api", awslogs-region = "ap-south-1", awslogs-stream-prefix = "api" } }
  }])
}

resource "aws_appautoscaling_policy" "api_requests" {
  name               = "ai-api-requests"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.ai.arn_suffix}/${aws_lb_target_group.api.arn_suffix}"
    }
    target_value = 200
  }
}
```

### GitHub Actions: test + eval gate → build → ECR → ECS deploy (OIDC, no stored AWS keys)
```yaml
name: deploy-ai-api
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  test-and-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --frozen && uv run pytest -q
      - run: uv run python evals/run.py --dataset evals/smoke.jsonl --gate faithfulness=0.9   # offline eval gate
        env: { ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY_CI }} }
  deploy:
    needs: test-and-eval
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123456789012:role/gha-deploy, aws-region: ap-south-1 }
      - uses: aws-actions/amazon-ecr-login@v2
        id: ecr
      - run: |
          IMAGE=${{ steps.ecr.outputs.registry }}/ai-api:${{ github.sha }}
          docker build -t $IMAGE . && docker push $IMAGE
          echo "IMAGE=$IMAGE" >> $GITHUB_ENV
      - uses: aws-actions/amazon-ecs-render-task-definition@v1
        id: td
        with: { task-definition: infra/task-def-api.json, container-name: api, image: ${{ env.IMAGE }} }
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with: { task-definition: ${{ steps.td.outputs.task-definition }}, service: ai-api, cluster: prod, wait-for-service-stability: true }
```

### Calling Claude via Amazon Bedrock (alternative to direct API)
```python
from anthropic import AnthropicBedrock
bedrock_client = AnthropicBedrock(aws_region="ap-south-1")      # IAM task role credentials; check model availability/regional profiles
msg = bedrock_client.messages.create(model=os.environ["BEDROCK_CLAUDE_MODEL_ID"], max_tokens=400,
                                     messages=[{"role": "user", "content": "Summarize this refund policy in 3 bullets: ..."}])
```

### Ingestion worker consuming SQS (idempotent, DLQ-backed)
```python
import boto3, json
sqs = boto3.client("sqs", region_name="ap-south-1")
def run_worker():
    while True:
        resp = sqs.receive_message(QueueUrl=INGEST_Q, MaxNumberOfMessages=5, WaitTimeSeconds=20, VisibilityTimeout=300)
        for m in resp.get("Messages", []):
            evt = json.loads(m["Body"])                                  # {"doc_id": "...", "version": 7}
            try:
                ingest_document(evt["doc_id"], evt["version"])          # parse → chunk → embed → upsert (skip if version already indexed)
                sqs.delete_message(QueueUrl=INGEST_Q, ReceiptHandle=m["ReceiptHandle"])
            except Exception:
                log.exception("ingest failed")                           # message reappears; after maxReceiveCount → DLQ
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you deploy a RAG chatbot backend on AWS?**
A1: Containerize the FastAPI API and the ingestion workers (multi-stage Docker, non-root, health and readiness endpoints) and push them to ECR. Run them as separate ECS Fargate services in private subnets: the API behind an ALB with a long idle timeout for SSE streaming, and workers consuming an SQS queue (with a DLQ) to parse, chunk and embed documents from S3. Use RDS PostgreSQL with pgvector (Multi-AZ, RDS Proxy) for retrieval, ElastiCache Redis for caching and rate limits, and Secrets Manager for LLM keys with IAM task roles. Call LLMs via provider APIs through NAT, or via Bedrock. Add CloudWatch, OTel and LLM tracing, Terraform for infrastructure, and GitHub Actions with OIDC, an eval gate and blue/green deploys.

**Q2: How do you manage secrets and credentials securely?**
A2: Never bake secrets into images or commit them to Git. Store provider API keys and database credentials in Secrets Manager or SSM Parameter Store, inject them into ECS tasks at runtime via task-definition secrets, and rotate them. Use IAM task roles for AWS resource access (S3, SQS, Bedrock) with least privilege, and GitHub Actions OIDC to assume deploy roles instead of storing AWS keys. Keep separate keys per environment with spending limits, and audit access with CloudTrail.

**Q3: What changes when deploying streaming AI endpoints?**
A3: The ALB and any proxies must not cut long-lived connections: raise idle timeouts (e.g., 300 s), disable buffering and compression for event streams, and send heartbeats. Use async servers that hold many concurrent streams per task, and scale on concurrent requests rather than only CPU. Set the deregistration delay and graceful shutdown so deploys don't kill active streams (or make clients reconnect and resume), and load-test with realistic concurrent streams. Monitor TTFT and stream error rates.

**Q4: How do you handle background AI workloads like document ingestion?**
A4: Decouple them from the request path. Uploads go to S3 and an event or API message goes to SQS. Autoscaled worker services consume messages idempotently (version checks), parse, chunk, embed in batches with retries and backoff for provider limits, and upsert into the vector store. Failed messages go to a DLQ after max retries, with alerting. Use batch APIs for large offline jobs to cut cost, scale workers on queue depth (to zero when idle), and expose ingestion status to users.

**Q5: How do you ensure safe releases of AI changes?**
A5: Treat prompts, model choices, retrieval settings and code as one versioned release. Run unit tests, prompt-size checks and an offline eval smoke suite on PRs, then deploy to staging for full evals and a streaming load test. Release to production with blue/green or canary plus feature flags (model routing, degraded modes), monitor error rates, TTFT, groundedness, feedback and cost after deploy, and roll back automatically on alarms. Keep previous image tags and prompt versions ready, and log the release version on every trace.

---

## 🔷 Trade-offs
✅ ECS Fargate: no server management, simple scaling — ❌ less control than EKS; GPU support limited (use EKS/SageMaker for GPUs).
✅ Bedrock: IAM, VPC, compliance, billing consolidation — ❌ model/feature availability may lag direct APIs; regional differences.
✅ Direct provider APIs: newest features — ❌ egress, separate vendor agreements & residency review.
✅ Self-hosted GPUs: control & residency — ❌ cost, capacity planning, MLOps burden.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Docker image | Packaged app + dependencies | पैक किया हुआ ऐप |
| ECR | AWS container registry | AWS image भंडार |
| ECS Fargate | Serverless container runtime | बिना server के containers |
| ALB idle timeout | Max idle connection time | ख़ाली कनेक्शन का समय |
| Secrets Manager | Managed secret storage | secrets का सुरक्षित भंडार |
| IAM task role | Per-task AWS permissions | task की AWS अनुमति |
| SQS + DLQ | Queue + dead-letter queue | कतार + असफल संदेश कतार |
| OIDC deploy | Keyless CI auth to AWS | बिना key का CI login |
| Blue/green deploy | Switch traffic between versions | versions के बीच traffic बदलना |
| Amazon Bedrock | AWS managed model access | AWS से models तक पहुँच |

---

## ⚡ 3-Line Summary
**English:**
1. Package API + workers as slim non-root Docker images; run on ECS Fargate (or EKS) behind an ALB tuned for streaming; data in RDS+pgvector, Redis, S3; async ingestion via SQS+DLQ.
2. Secure & scale: Secrets Manager + IAM roles + OIDC CI, private subnets & egress control, autoscale on requests/queue depth, rate-limit & fall back for LLM providers or use Bedrock.
3. Ship safely: Terraform IaC, CI with tests + eval gates, blue/green deploys with streaming-aware draining, observability & cost alarms, and data residency in ap-south-1/2.

**Hindi:**
1. API + workers की छोटी non-root Docker images; ECS Fargate + streaming के लिए tuned ALB; RDS+pgvector, Redis, S3; SQS से async ingestion।
2. सुरक्षा और scale: Secrets Manager + IAM roles + OIDC, private subnets, requests/queue पर autoscale, LLM सीमाओं पर fallback या Bedrock।
3. सुरक्षित release: Terraform, tests + evals वाला CI, blue/green, निगरानी और ख़र्च alarms, डेटा भारत (ap-south-1/2) में।

---

## ➡️ Next Topic Suggestion
**🎉 AI Engineering complete!** Next: **01. How to Answer a Backend System Design Round** in `11-Interview-Playbook/`. You've learned the material; now learn how to present it under interview pressure with a step-by-step framework.
