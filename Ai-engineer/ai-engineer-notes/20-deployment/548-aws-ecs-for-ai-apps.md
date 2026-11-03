
---

# 548. AWS ECS for AI Apps
# हिंदी में: AI Apps के लिए AWS ECS

---

## 🔵 Simple Definition (English)
Amazon ECS (Elastic Container Service) runs your Docker containers on AWS without you managing Kubernetes. You describe the container in a **task definition**, and an ECS **service** keeps N copies running. With **Fargate** you do not manage servers at all. For AI apps, ECS is the common home for a FastAPI service that calls LLM APIs.

## 🔵 सरल परिभाषा (Hindi)
Amazon ECS AWS पर आपके Docker containers चलाता है, Kubernetes सँभालने की ज़रूरत नहीं। आप **task definition** में container describe करते हैं और ECS **service** N copies चालू रखती है। **Fargate** के साथ servers manage ही नहीं करने पड़ते। AI apps में FastAPI service (जो LLM API call करती है) के लिए ECS आम choice है।

---

## 🔴 Problem it Solves
A FastAPI app on one laptop or one EC2 box dies when the box dies, cannot scale, and secrets (API keys) sit in plain files. Teams need: restarts on crash, rolling deploys, load balancing, secrets injection, and logs, without running their own orchestrator. ECS gives all of this as a managed service.

## 🔴 यह क्यों बना? (Hindi)
एक laptop या एक EC2 box पर चलने वाला FastAPI app box के मरते ही बंद हो जाता है, scale नहीं होता, और API keys plain files में रहती हैं। ज़रूरत है: crash पर restart, rolling deploy, load balancing, secrets injection और logs, बिना अपना orchestrator चलाए। ECS यह सब managed service के रूप में देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build Docker image of FastAPI app, push to ECR (container registry)
Step 2 → Write a task definition: image, CPU/memory, port, env vars, secrets, log config
Step 3 → Create an ECS cluster (logical group; Fargate needs no EC2 nodes)
Step 4 → Create a service: desired count = 2, attach to an Application Load Balancer
Step 5 → ECS Fargate pulls image, starts tasks in private subnets
Step 6 → ALB health check hits /health; unhealthy tasks are replaced automatically
Step 7 → New release = new task definition revision; service does a rolling update
Step 8 → Secrets Manager injects OPENAI_API_KEY into the container as env var
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → FastAPI app की Docker image बनाओ, ECR (registry) में push करो
Step 2 → Task definition लिखो: image, CPU/memory, port, env, secrets, logs
Step 3 → ECS cluster बनाओ (Fargate में EC2 nodes नहीं चाहिए)
Step 4 → Service बनाओ: desired count = 2, Application Load Balancer से जोड़ो
Step 5 → Fargate image pull करके tasks private subnets में चलाता है
Step 6 → ALB /health hit करता है; unhealthy task अपने आप replace होता है
Step 7 → नया release = नई task definition revision; rolling update होता है
Step 8 → Secrets Manager API key को env var बनाकर container में डालता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: The `tariff-api` FastAPI service (HS code lookup with RAG and an LLM call) runs as an ECS Fargate service with 2 tasks of 1 vCPU / 2 GB behind an ALB. The OpenAI key lives in Secrets Manager. During month-end customs filing, a target-tracking policy scales to 6 tasks.

**Zomato-style**: A "what should I eat" chat assistant runs as an ECS service; each deploy is rolling so ongoing chats are not dropped.

## 🟡 Real Example Hindi mein
**Tariff System**: `tariff-api` FastAPI service (HS code lookup + RAG + LLM call) ECS Fargate service के रूप में चलती है: 2 tasks (1 vCPU / 2 GB), ALB के पीछे। OpenAI key Secrets Manager में है। Month-end customs filing में policy 6 tasks तक scale करती है।

**Zomato-style**: "आज क्या खाऊँ" chat assistant ECS service है; हर deploy rolling है, इसलिए चल रही chats नहीं टूटतीं।

---

## 💻 Code Example — Basic
```python
# Build an ECS task definition as a plain dict and print it (no AWS call, runs offline)
import json  # json is used to pretty print the dict
from typing import Any  # Any is used for loose dict typing


def build_task_definition(image: str, cpu: int = 1024, memory: int = 2048) -> dict[str, Any]:
    """Return a Fargate task definition for the tariff API."""
    # Fargate only accepts specific cpu/memory pairs, so we validate a few common ones
    valid: dict[int, list[int]] = {512: [1024, 2048], 1024: [2048, 3072, 4096], 2048: [4096, 8192]}
    # Raise early with a clear message instead of failing inside AWS
    if cpu not in valid or memory not in valid[cpu]:
        raise ValueError(f"Invalid Fargate combo cpu={cpu} memory={memory}")
    # Return the structure that boto3 register_task_definition expects
    return {
        "family": "tariff-api",  # name of the task family
        "networkMode": "awsvpc",  # required for Fargate
        "requiresCompatibilities": ["FARGATE"],  # run on Fargate
        "cpu": str(cpu),  # CPU units as a string
        "memory": str(memory),  # memory in MiB as a string
        "containerDefinitions": [
            {
                "name": "api",  # container name used by the service
                "image": image,  # ECR image URI
                "portMappings": [{"containerPort": 8000}],  # FastAPI port
                "environment": [{"name": "LLM_MODEL", "value": "gpt-4o-mini"}],  # plain env
                "secrets": [  # injected from Secrets Manager at start
                    {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:openai"}
                ],
                "healthCheck": {  # container level health check
                    "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
                    "interval": 30,  # seconds between checks
                    "retries": 3,  # failures before unhealthy
                },
                "stopTimeout": 60,  # seconds allowed for graceful shutdown
            }
        ],
    }


if __name__ == "__main__":  # run only when executed directly
    td = build_task_definition("123456789012.dkr.ecr.ap-south-1.amazonaws.com/tariff-api:v1")  # build
    print(json.dumps(td, indent=2)[:400])  # show the first part of the JSON
```

## 💻 Code Example — Advanced
```python
# Production helper: register a revision and update the service, with error handling and async wrapper
import asyncio  # to run blocking boto3 calls in a thread
import logging  # structured logging for deploys
from typing import Any  # loose typing for AWS responses

import boto3  # AWS SDK for Python
from botocore.exceptions import BotoCoreError, ClientError  # AWS error types

logger = logging.getLogger("deploy")  # module logger


class EcsDeployer:
    """Deploys a new image to an existing ECS service."""

    def __init__(self, cluster: str, service: str, region: str = "ap-south-1") -> None:
        self.cluster = cluster  # ECS cluster name
        self.service = service  # ECS service name
        self.ecs = boto3.client("ecs", region_name=region)  # ECS client

    def deploy(self, task_def: dict[str, Any]) -> str:
        """Register task definition and roll the service to it. Returns the new ARN."""
        try:
            # Register a new revision of the task definition
            resp = self.ecs.register_task_definition(**task_def)
            arn: str = resp["taskDefinition"]["taskDefinitionArn"]  # new revision ARN
            # Point the service to the new revision; ECS does a rolling update
            self.ecs.update_service(
                cluster=self.cluster,
                service=self.service,
                taskDefinition=arn,
                deploymentConfiguration={
                    "deploymentCircuitBreaker": {"enable": True, "rollback": True},  # auto rollback
                    "minimumHealthyPercent": 100,  # never drop below current capacity
                    "maximumPercent": 200,  # allow double capacity during rollout
                },
            )
            logger.info("deployed %s", arn)  # log success
            return arn  # return ARN for audit
        except (ClientError, BotoCoreError) as exc:
            logger.error("deploy failed: %s", exc)  # log the failure
            raise  # let CI mark the job as failed

    async def deploy_async(self, task_def: dict[str, Any]) -> str:
        """Async wrapper: boto3 is blocking, so use a worker thread."""
        return await asyncio.to_thread(self.deploy, task_def)  # do not block the event loop

    async def wait_stable(self, timeout_s: int = 600) -> None:
        """Wait until the service reaches steady state."""
        waiter = self.ecs.get_waiter("services_stable")  # built-in waiter
        # Waiter polls every 15s by default; run it in a thread
        await asyncio.wait_for(
            asyncio.to_thread(waiter.wait, cluster=self.cluster, services=[self.service]),
            timeout=timeout_s,  # hard stop so CI never hangs
        )
```

---

## 🟠 FastAPI Integration
ECS runs your FastAPI container, so the app must expose `/health`, read config from env vars, and log to stdout (the `awslogs` driver ships it to CloudWatch). Bind to `0.0.0.0`.

```python
# FastAPI app prepared for ECS
import os  # read env vars set by the task definition
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # request validation

app = FastAPI()  # create the app


class Query(BaseModel):  # request body
    text: str  # product description


@app.get("/health")  # ALB and ECS call this
async def health() -> dict[str, str]:
    return {"status": "ok"}  # cheap, no LLM call


@app.post("/classify")  # main business route
async def classify(q: Query) -> dict[str, str]:
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")  # model chosen by task definition
    return {"model": model, "hs_code": "8517.13"}  # placeholder result for the example

# Container command: uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔗 LangChain / LangGraph Connection
A LangGraph workflow is just Python code inside the container. Keep the compiled graph at module level so it builds once per task. For long agent runs, use a checkpointer backed by RDS or DynamoDB, because tasks are stateless and can be replaced at any time.

```python
# LangGraph graph compiled once at container start
from langgraph.graph import StateGraph, END  # graph builder
from typing import TypedDict  # state schema


class State(TypedDict):  # graph state
    text: str  # input
    code: str  # output


def classify_node(state: State) -> State:  # one node
    return {"text": state["text"], "code": "8517.13"}  # stub, replace with LLM call


g = StateGraph(State)  # create graph
g.add_node("classify", classify_node)  # add node
g.set_entry_point("classify")  # start here
g.add_edge("classify", END)  # finish
graph = g.compile()  # compile once; reused by every request
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting API keys in the task definition environment
```python
# Wrong: visible to anyone who can describe the task definition
env = [{"name": "OPENAI_API_KEY", "value": "sk-live-..."}]
# Correct: reference Secrets Manager, ECS injects at start
secrets = [{"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:openai"}]
```

❌ Mistake 2: Running tasks in public subnets with no health check, or using `latest` tag
```python
# Wrong: image tag changes silently, rollback impossible
image = "tariff-api:latest"
# Correct: immutable tag (git SHA) so each revision is reproducible
image = "123456789012.dkr.ecr.ap-south-1.amazonaws.com/tariff-api:9f3c2ab"
```

---

## 🧠 Tricky Interview Question
**Q**: "You deploy a new image and ECS keeps starting and killing tasks forever. The container runs fine locally. What do you check?"

**Answer**: Usually the ALB or container health check fails, so ECS kills the task and starts another (a crash loop). Causes: (1) app binds to `127.0.0.1` instead of `0.0.0.0`; (2) health check path wrong or requires auth; (3) startup is slow (loading a model or index) and the `healthCheckGracePeriodSeconds` is too short; (4) the task runs out of memory and is OOM-killed (check stopped reason). Fix the root cause and keep the deployment circuit breaker on, so a bad release rolls back automatically.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a task definition and a service in ECS?
A1: A task definition is the blueprint (image, CPU, memory, ports, env). A service keeps a desired number of tasks running from that blueprint and replaces failed ones.

Q2: What is Fargate?
A2: A serverless compute mode for ECS: you pay per vCPU and memory per second and do not manage EC2 instances.

Q3: When would you choose ECS on EC2 over Fargate for AI?
A3: When you need GPUs, very large memory, or cheaper steady capacity (reserved or spot instances). Fargate does not offer GPUs, so local model inference usually goes to ECS on EC2 GPU nodes or SageMaker.

Q4: How do you do a zero-downtime deploy on ECS?
A4: Rolling update with `minimumHealthyPercent=100`, `maximumPercent=200`, ALB health checks, connection draining, and a deployment circuit breaker with rollback.

Q5: Design secure, cost-efficient ECS hosting for a tariff LLM API with spiky traffic.
A5: Private subnets for tasks, ALB in public subnets, NAT or VPC endpoints for egress, Secrets Manager for keys, task IAM role with least privilege, target-tracking autoscaling on CPU and ALB request count per target, Fargate Spot for non-critical workers, CloudWatch alarms on 5xx and latency, and a token budget per request to bound LLM cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have a containerized FastAPI/LangChain API and want managed ops
- You want AWS-native IAM, ALB, CloudWatch integration
- You do not need Kubernetes features

❌ Avoid when:
- A tiny prototype (Railway/Render is faster)
- You need GPUs on Fargate (not supported)
- Your team already standardised on Kubernetes

---

## 📊 Visual Diagram
```
 Client
   │
   ▼
┌───────────────┐   health /health   ┌──────────────────────────┐
│ ALB (public)  │───────────────────▶│ ECS Service (Fargate)    │
└───────────────┘                    │  Task 1: FastAPI :8000   │
                                     │  Task 2: FastAPI :8000   │
                                     └───────┬──────────────────┘
                                             │ secrets
                          ┌──────────────────┴───────┐
                          ▼                          ▼
                  Secrets Manager            LLM API / Bedrock
 ECR image ──▶ Task Definition revision ──▶ rolling update
```

---

## 💰 Cost Impact
Illustrative Fargate pricing (check current AWS pricing): roughly $0.04 per vCPU-hour and $0.004 per GB-hour in common regions. One task of 1 vCPU / 2 GB is about $0.048 per hour, so two tasks always on cost roughly $70 per month. This is small compared with LLM token cost: 100K requests/day at 700 tokens each on gpt-4o-mini (illustrative $0.15/1M input, $0.60/1M output) is only a few dollars to tens of dollars per day. Token usage is not changed by ECS, but infrastructure waste is. Optimise: right-size CPU/memory (the API is I/O bound, so small tasks are fine), use autoscaling, Fargate Spot for workers, Savings Plans for the baseline, and cache LLM answers to cut tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ECS | AWS container orchestration service | AWS का container service |
| Fargate | Serverless container compute | बिना server वाला compute |
| Task definition | Blueprint of a container group | Container का blueprint |
| Service | Keeps N tasks running | N tasks चालू रखने वाला |
| ECR | Docker image registry | Image रखने की जगह |
| ALB | Application Load Balancer | Traffic बाँटने वाला |
| Circuit breaker | Auto rollback of bad deploy | खराब deploy का auto rollback |

---

## ⚡ 3-Line Summary
English: ECS runs your FastAPI container as a managed service with rolling deploys and health checks. Fargate removes server management; secrets come from Secrets Manager. Tune autoscaling and caching because LLM tokens, not compute, dominate cost.
Hindi: ECS आपका FastAPI container managed service की तरह चलाता है, rolling deploy और health checks के साथ। Fargate में server manage नहीं करना पड़ता; secrets Secrets Manager से आते हैं। Autoscaling और caching tune करो क्योंकि cost में LLM tokens ज़्यादा होते हैं।

---

## ➡️ Next Topic
**549. AWS Lambda for AI (Light)** — when a serverless function is a lighter alternative to a always-on ECS service.
