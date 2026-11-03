---

# 547. AWS EC2 for AI Apps
# हिंदी में: AI Apps के लिए AWS EC2

---

## 🔵 Simple Definition (English)
EC2 (Elastic Compute Cloud) gives you a virtual server on AWS that you fully control. For AI apps you rent a VM, install Docker or Python, and run your FastAPI + LangChain service on it. You pick CPU, RAM, and optionally a GPU.

## 🔵 सरल परिभाषा (Hindi)
EC2 AWS पर एक virtual server है जिस पर आपका पूरा control होता है। AI app के लिए आप VM किराये पर लेते हैं, Docker या Python install करते हैं और अपना FastAPI + LangChain service चलाते हैं। CPU, RAM और ज़रूरत हो तो GPU आप खुद चुनते हैं।

---

## 🔴 Problem it Solves
Your laptop cannot serve users 24/7. Serverless (Lambda) has timeouts and cold starts, which hurt long LLM streams. Managed platforms hide the machine, so you cannot tune the OS, run a vector DB beside the app, or attach a GPU. EC2 gives a long-running, tunable machine.

## 🔴 यह क्यों बना? (Hindi)
Laptop 24/7 users को serve नहीं कर सकता। Lambda में timeout और cold start होता है, जो लंबी LLM streams के लिए बुरा है। Managed platforms machine छुपा देते हैं, इसलिए OS tune करना, app के पास vector DB चलाना या GPU लगाना मुश्किल है। EC2 एक हमेशा चलने वाली, tunable machine देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose region + AMI (Ubuntu 22.04 / Deep Learning AMI)
Step 2 → Choose instance type (t3.medium for API-only, g5.xlarge for local models)
Step 3 → Create a security group: allow 22 (your IP only), 80/443 (public)
Step 4 → Attach an IAM role (Secrets Manager / S3 read) - no keys on disk
Step 5 → Launch, SSH in, install Docker, pull the image
Step 6 → Run the container (uvicorn behind Nginx), secrets from Secrets Manager
Step 7 → Add an Elastic IP / Load Balancer, CloudWatch logs, auto-restart (systemd or Docker restart policy)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Region + AMI चुनो (Ubuntu 22.04 / Deep Learning AMI)
Step 2 → Instance type चुनो (सिर्फ API के लिए t3.medium, local model के लिए g5.xlarge)
Step 3 → Security group बनाओ: 22 सिर्फ आपके IP से, 80/443 public
Step 4 → IAM role attach करो - disk पर keys मत रखो
Step 5 → Launch करो, SSH से जाओ, Docker install करो, image pull करो
Step 6 → Container चलाओ (Nginx के पीछे uvicorn), secrets Secrets Manager से
Step 7 → Elastic IP / Load Balancer, CloudWatch logs और auto-restart जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The API calls a hosted LLM (OpenAI/Bedrock) and a Qdrant vector DB of HS codes. One `t3.large` (2 vCPU, 8 GB) runs two Docker containers: FastAPI and Qdrant. An IAM role lets it read the API key from Secrets Manager. If the team later fine-tunes an open model for HS codes, they move only the model server to a `g5.xlarge` GPU box.

**Zomato-style**: A "dish recommender" runs on EC2 behind an ALB. A burst at dinner time triggers an Auto Scaling Group to add instances.

## 🟡 Real Example Hindi mein
**Tariff System**: API एक hosted LLM और HS codes के Qdrant vector DB को call करती है। एक `t3.large` पर दो containers चलते हैं: FastAPI और Qdrant। IAM role से API key Secrets Manager से पढ़ी जाती है। बाद में open model fine-tune हो तो सिर्फ model server GPU वाली `g5.xlarge` पर जाता है।

**Zomato-style**: "Dish recommender" ALB के पीछे EC2 पर चलता है; dinner के समय Auto Scaling Group instances बढ़ा देता है।

---

## 💻 Code Example — Basic
```python
# Launch one EC2 instance with boto3 (pip install boto3)
import boto3  # AWS SDK for Python

# Create an EC2 client for the Mumbai region
ec2 = boto3.client("ec2", region_name="ap-south-1")

# Startup script: runs once on first boot (installs Docker, runs the app)
USER_DATA = """#!/bin/bash
apt-get update -y
apt-get install -y docker.io
systemctl enable --now docker
docker run -d --restart unless-stopped -p 80:8000 myrepo/tariff-api:latest
"""

# Ask AWS for one instance (AMI id below is a placeholder - use a real Ubuntu AMI id)
resp = ec2.run_instances(
    ImageId="ami-0123456789abcdef0",       # placeholder AMI id
    InstanceType="t3.medium",              # 2 vCPU, 4 GB RAM
    MinCount=1,                            # launch at least 1
    MaxCount=1,                            # launch at most 1
    UserData=USER_DATA,                    # boot script
    IamInstanceProfile={"Name": "tariff-api-role"},  # role for secrets access
    TagSpecifications=[{                   # tag it so billing is traceable
        "ResourceType": "instance",
        "Tags": [{"Key": "app", "Value": "tariff-api"}],
    }],
)

# Print the new instance id
print(resp["Instances"][0]["InstanceId"])
```

## 💻 Code Example — Advanced
```python
# Production helper: launch + wait + error handling + async wrapper
import asyncio                                   # for async version
import logging                                   # structured logs
from typing import Optional                      # type hints
import boto3                                     # AWS SDK
from botocore.exceptions import ClientError      # AWS error type

logger = logging.getLogger("ec2")                # module logger


class Ec2Launcher:
    """Launches and tracks EC2 instances for an AI service."""

    def __init__(self, region: str = "ap-south-1") -> None:
        self.ec2 = boto3.client("ec2", region_name=region)   # low-level client

    def launch(self, ami: str, itype: str, user_data: str,
               sg_ids: list[str], role: str) -> str:
        """Launch one instance and return its id."""
        try:
            resp = self.ec2.run_instances(
                ImageId=ami, InstanceType=itype, MinCount=1, MaxCount=1,
                UserData=user_data, SecurityGroupIds=sg_ids,
                IamInstanceProfile={"Name": role},
                MetadataOptions={"HttpTokens": "required"},  # force IMDSv2 (security)
                BlockDeviceMappings=[{                       # bigger root disk for images
                    "DeviceName": "/dev/sda1",
                    "Ebs": {"VolumeSize": 50, "VolumeType": "gp3", "Encrypted": True},
                }],
            )
        except ClientError as exc:                            # quota, bad AMI, perms...
            logger.error("launch failed: %s", exc)
            raise
        instance_id: str = resp["Instances"][0]["InstanceId"]  # first (only) instance
        # Block until the instance is running (default waiter polls every 15s)
        self.ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
        return instance_id

    def public_ip(self, instance_id: str) -> Optional[str]:
        """Return the public IP (None if not assigned)."""
        desc = self.ec2.describe_instances(InstanceIds=[instance_id])
        return desc["Reservations"][0]["Instances"][0].get("PublicIpAddress")

    async def alaunch(self, *args: object, **kwargs: object) -> str:
        """Async version: boto3 is blocking, so run it in a worker thread."""
        return await asyncio.to_thread(self.launch, *args, **kwargs)
```

---

## 🟠 FastAPI Integration
The FastAPI app itself is what runs on EC2. Key points: bind to `0.0.0.0`, expose `/health` for the load balancer, and read secrets from the environment.

```python
# main.py - the app that runs on EC2 (uvicorn main:app --host 0.0.0.0 --port 8000)
import os                                  # read env vars
from fastapi import FastAPI                # web framework
from pydantic import BaseModel             # request validation

app = FastAPI()                            # app instance


class Query(BaseModel):
    text: str                              # user question


@app.get("/health")
async def health() -> dict[str, str]:
    """ALB / Route53 calls this to know the box is alive."""
    return {"status": "ok"}                # cheap, no LLM call


@app.post("/classify")
async def classify(q: Query) -> dict[str, str]:
    """Placeholder classify route (real LLM call omitted)."""
    model = os.getenv("MODEL_NAME", "gpt-4o-mini")   # config from env
    return {"model": model, "echo": q.text}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain code is just Python in the container. On EC2 you can use `ChatBedrock` (IAM role auth, no API key) or `ChatOpenAI` (key from Secrets Manager). LangGraph checkpoints can go to Postgres/Redis on the same VPC.

```python
# LangChain on EC2 with Bedrock - credentials come from the instance role
from langchain_aws import ChatBedrock     # pip install langchain-aws

# No API key needed: boto3 picks the IAM role automatically
llm = ChatBedrock(model_id="anthropic.claude-3-haiku-20240307-v1:0", region_name="us-east-1")
print(llm.invoke("HS code for a laptop?").content)   # one call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hard-coding keys / opening SSH to the world
✅ Correct: IAM role + SG with SSH only from your IP (or use SSM Session Manager).
```python
# Wrong
OPENAI_API_KEY = "sk-live-abc123"            # leaked via git / AMI snapshot
# Right
import os
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # injected from Secrets Manager at start
```

❌ Mistake 2: Running uvicorn in a terminal (dies on logout) with no restart
✅ Correct: Docker `--restart unless-stopped` or a systemd unit.
```python
# Wrong: python main.py &   -> dies on reboot
# Right: docker run -d --restart unless-stopped ...   (survives crash and reboot)
```

---

## 🧠 Tricky Interview Question
**Q**: "Your EC2 FastAPI app is fine at 9 AM, but at peak every stream drops after 60 seconds and CPU is only 20%. Why?"

**Answer**: CPU is not the limit. The ALB idle timeout defaults to 60 s, and LLM streams that go quiet longer get cut. Raise the ALB idle timeout, send SSE keep-alive comments, and check Nginx `proxy_read_timeout` and `proxy_buffering off`. Also check uvicorn worker count and the OS file-descriptor limit.

---

## ⚫ Interview Questions + Answers

Q1: What is an AMI?
A1: Amazon Machine Image: a template (OS + preinstalled software) used to launch instances.

Q2: Why attach an IAM role instead of access keys?
A2: Role credentials are temporary and auto-rotated, never stored on disk, and cannot leak through git or snapshots.

Q3: When EC2 vs Lambda for an LLM API?
A3: EC2 for long streams, steady traffic, local models, sidecar DBs. Lambda for spiky, short, low-volume calls where cold starts are fine.

Q4: How do you make an EC2 deployment highly available?
A4: Multiple instances across AZs in an Auto Scaling Group behind an ALB with health checks; stateless app, state in RDS/Redis.

Q5: How would you cut EC2 cost for a GPU inference service?
A5: Right-size, use Savings Plans for the baseline, Spot instances for batch/fault-tolerant work, schedule scale-down off-hours, quantize the model to fit a smaller GPU, and move simple traffic to a hosted API.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need full control (OS, GPU, sidecar vector DB)
- Long-lived streaming connections
- Steady traffic where reserved pricing wins

❌ Avoid when:
- Tiny/spiky traffic (Lambda or Railway is cheaper to operate)
- Team has no ops capacity (use ECS Fargate / App Runner)

---

## 📊 Visual Diagram
```
 Internet
    │
    ▼
 [Route53] → [ALB :443]  (health check /health)
                 │
        ┌────────┴────────┐
        ▼                 ▼
   EC2 (AZ-a)         EC2 (AZ-b)
   ┌──────────┐       ┌──────────┐
   │ Nginx    │       │ Nginx    │
   │ FastAPI  │       │ FastAPI  │
   └────┬─────┘       └────┬─────┘
        └──── IAM role ────┴──→ Secrets Manager / S3 / Bedrock
```

---

## 💰 Cost Impact
EC2 is billed per second of runtime, independent of tokens, so token cost (LLM API) is a separate line. A typical tariff query uses ~800 input + 200 output tokens; the server cost per request falls as utilization rises. Prices below are illustrative; check the AWS pricing page.

| Option | Rough idea | Note |
|--------|-----------|------|
| t3.medium on-demand | tens of USD / month | API-only service |
| g5.xlarge GPU | hundreds of USD / month | only if you self-host a model |
| Spot | large discount | can be interrupted |

Optimise: right-size, Savings Plans, stop dev boxes at night, cache LLM answers so the same box serves more users.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EC2 | Virtual server on AWS | AWS पर virtual server |
| AMI | Machine image template | Machine की template image |
| Security Group | Virtual firewall | Virtual firewall |
| IAM Role | Temporary permissions for a resource | Resource को अस्थायी permissions |
| ASG | Auto Scaling Group | अपने आप instances घटाने-बढ़ाने वाला group |
| ALB | Application Load Balancer | Traffic बाँटने वाला balancer |

---

## ⚡ 3-Line Summary
English: EC2 is a rentable VM where you run your containerized FastAPI AI app. Secure it with IAM roles and tight security groups, and put it behind a load balancer. Choose it for control, GPUs and streaming; avoid it if you do not want to manage servers.
Hindi: EC2 किराये की VM है जहाँ आप अपना containerized FastAPI AI app चलाते हैं। IAM role और सख्त security group से secure करें और load balancer के पीछे रखें। Control, GPU और streaming के लिए चुनें; server manage नहीं करना हो तो न चुनें।

---

## ➡️ Next Topic
**557. Health Checks for AI** — how the load balancer decides an instance is alive, and why AI apps need smarter checks than "port is open".
