---

# 443. Deploy on AWS EC2
# हिंदी में: AWS EC2 पर Deploy करना

---

## 🔵 Simple Definition (English)
EC2 (Elastic Compute Cloud) is AWS's rentable virtual machine. You pick an operating system image (AMI), a size (instance type), a firewall (security group) and an SSH key, and you get a Linux server in about a minute. Deploying FastAPI on EC2 means doing the VPS recipe on AWS, plus AWS networking and IAM.

## 🔵 सरल परिभाषा (Hindi)
EC2 (Elastic Compute Cloud) AWS की किराए की virtual machine है। आप operating system image (AMI), size (instance type), firewall (security group) और SSH key चुनते हैं, और लगभग एक मिनट में Linux server मिल जाता है। EC2 पर FastAPI deploy करना यानी VPS वाली विधि AWS पर करना, साथ में AWS का networking और IAM।

---

## 🔴 Problem it Solves
Buying hardware or a fixed hosting plan is slow and inflexible. With EC2 you can create a server in any region in a minute, resize it, snapshot it, attach it to a load balancer and pay by the second. It also integrates with managed services (RDS databases, S3 files, CloudWatch logs, IAM roles) that a generic VPS lacks.

## 🔴 यह क्यों बना? (Hindi)
Hardware खरीदना या fixed hosting plan लेना धीमा और कठोर है। EC2 से आप किसी भी region में एक मिनट में server बना सकते हैं, size बदल सकते हैं, snapshot ले सकते हैं, load balancer से जोड़ सकते हैं और सेकंड के हिसाब से भुगतान करते हैं। यह managed services (RDS databases, S3 files, CloudWatch logs, IAM roles) से भी जुड़ता है जो साधारण VPS में नहीं मिलतीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose region (ap-south-1 Mumbai) and AMI (Ubuntu 24.04 LTS or Amazon Linux 2023)
Step 2 → Instance type: t3.small (2 vCPU / 2 GB) for a small API; t3.micro is free-tier eligible
Step 3 → Key pair for SSH; Security Group: 22 (only YOUR IP), 80, 443 (anywhere)
Step 4 → Attach an IAM Role (instance profile) so the app reads S3/Secrets Manager without keys
Step 5 → Launch with User Data script: installs packages, clones repo, starts the service
Step 6 → Allocate an Elastic IP (fixed address) and point DNS (Route 53) to it
Step 7 → Run the VPS recipe: venv, gunicorn/uvicorn, systemd, Nginx, certbot (topics 436, 438)
Step 8 → Add CloudWatch agent for logs and alarms; take AMI/EBS snapshots for backup
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Region चुनो (ap-south-1 Mumbai) और AMI (Ubuntu 24.04 LTS या Amazon Linux 2023)
Step 2 → Instance type: छोटे API के लिए t3.small (2 vCPU / 2 GB); t3.micro free-tier में आता है
Step 3 → SSH के लिए key pair; Security Group: 22 (सिर्फ आपका IP), 80, 443 (सब जगह से)
Step 4 → IAM Role (instance profile) जोड़ो ताकि app बिना keys के S3/Secrets Manager पढ़े
Step 5 → User Data script से launch: packages install, repo clone, service चालू
Step 6 → Elastic IP (स्थिर address) लो और DNS (Route 53) उस पर पॉइंट करो
Step 7 → VPS वाली विधि चलाओ: venv, gunicorn/uvicorn, systemd, Nginx, certbot (topics 436, 438)
Step 8 → logs और alarms के लिए CloudWatch agent; backup के लिए AMI/EBS snapshots
```

---

## 🟡 Real World Example
A startup runs a FastAPI backend on one `t3.small` in Mumbai. Nginx and the app run on the instance; PostgreSQL lives in RDS in a private subnet (so the database is managed and backed up); uploads go to S3 through the instance's IAM role. When traffic grows, they create an AMI of the configured instance, launch two copies behind an Application Load Balancer and add an Auto Scaling Group.

## 🟡 Real Example Hindi mein
एक startup Mumbai में एक `t3.small` पर FastAPI backend चलाता है। Nginx और app instance पर हैं; PostgreSQL RDS में private subnet में है (managed और backed up); uploads instance के IAM role से S3 में जाते हैं। Traffic बढ़ने पर वे configured instance का AMI बनाते हैं, Application Load Balancer के पीछे दो copies चलाते हैं और Auto Scaling Group जोड़ते हैं।

---

## 💻 Code Example — Basic
Generating the EC2 "User Data" bootstrap script from Python (this ran; the script itself was **not** executed on a server):

```python
# Basic: build the EC2 "user data" bootstrap script in Python (runs once at first boot)
from textwrap import dedent                       # remove common indentation


def user_data(repo: str, app_user: str = "ubuntu") -> str:
    return dedent(f"""\
        #!/bin/bash
        set -euo pipefail
        apt-get update -y
        apt-get install -y python3-venv nginx git
        git clone {repo} /srv/app
        python3 -m venv /srv/app/.venv
        /srv/app/.venv/bin/pip install -r /srv/app/requirements.txt
        chown -R {app_user}:{app_user} /srv/app
        systemctl enable --now nginx
        """)                                      # systemd unit would be written the same way


script = user_data("https://github.com/acme/orders-api.git")
print(script.splitlines()[0])                     # shebang must be the first line
print(len(script.splitlines()), "lines")
assert "set -euo pipefail" in script              # fail fast on any error

# Output (real run, Python 3.13):
# #!/bin/bash
# 9 lines
```

Typical console/CLI commands (**not run**: no AWS account or credentials here):

```bash
# security group: SSH only from your IP, web from anywhere
aws ec2 create-security-group --group-name orders-sg --description "orders api" --vpc-id vpc-xxxx
aws ec2 authorize-security-group-ingress --group-id sg-xxxx --protocol tcp --port 22  --cidr 203.0.113.10/32
aws ec2 authorize-security-group-ingress --group-id sg-xxxx --protocol tcp --port 443 --cidr 0.0.0.0/0

# connect and inspect
ssh -i my-key.pem ubuntu@<elastic-ip>
sudo systemctl status orders-api && journalctl -u orders-api -n 50
```

## 💻 Code Example — Advanced
Launching an instance with boto3, with secure defaults (IMDSv2 required, tags, security group). It is tested **offline** with botocore's `Stubber`, which fakes the AWS reply, so the real `run_instances` API was never called:

```python
# Advanced: launch an EC2 instance with boto3 (tested offline with botocore Stubber)
import boto3                                      # AWS SDK for Python
from botocore.stub import Stubber                 # fake AWS responses for tests


def launch(ec2, user_data: str, sg_id: str, key_name: str) -> str:
    """Start one t3.small Ubuntu instance and return its instance id."""
    resp = ec2.run_instances(
        ImageId="ami-0abcdef1234567890",          # Ubuntu AMI id (differs per region!)
        InstanceType="t3.small",                  # 2 vCPU, 2 GB RAM
        MinCount=1, MaxCount=1,                   # exactly one instance
        KeyName=key_name,                         # SSH key pair name
        SecurityGroupIds=[sg_id],                 # firewall rules (80/443 open, 22 from your IP)
        UserData=user_data,                       # boto3 base64-encodes this for you
        MetadataOptions={"HttpTokens": "required"},   # IMDSv2 only (security best practice)
        TagSpecifications=[{"ResourceType": "instance",
                            "Tags": [{"Key": "Name", "Value": "orders-api"}]}],
    )
    return resp["Instances"][0]["InstanceId"]     # id like i-0123...


ec2 = boto3.client("ec2", region_name="ap-south-1",
                   aws_access_key_id="x", aws_secret_access_key="x")   # dummy creds: never real keys in code
with Stubber(ec2) as stub:                        # intercept the HTTP call
    stub.add_response("run_instances", {"Instances": [{"InstanceId": "i-0abc123"}]})
    print(launch(ec2, "#!/bin/bash\necho hi", "sg-123", "my-key"))   # i-0abc123

# Output (real run, Python 3.13):
# i-0abc123
```

Real-world version: create the client without hardcoded keys (`boto3.client("ec2", region_name="ap-south-1")`); boto3 finds credentials from environment variables, `~/.aws/credentials` or an IAM role. Then wait for it with `ec2.get_waiter("instance_running").wait(InstanceIds=[iid])`. The AMI id above is a placeholder; real ids differ per region.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| AWS SDK | `boto3` | `@aws-sdk/client-ec2` (v3) |
| Credentials | env / profile / IAM role | same chain |
| Call style | `ec2.run_instances(...)` | `await client.send(new RunInstancesCommand(...))` |
| Waiters | `get_waiter("instance_running")` | `waitUntilInstanceRunning` |
| Infra as code | CDK in Python, Pulumi, Terraform | CDK in TS, Pulumi, Terraform |

```python
# Python way — boto3 client, synchronous call
import boto3
ec2 = boto3.client("ec2", region_name="ap-south-1")
# resp = ec2.describe_instances()          # real call (needs credentials)
```
```javascript
// JavaScript way — AWS SDK v3, command objects + await
import { EC2Client, DescribeInstancesCommand } from "@aws-sdk/client-ec2";
const client = new EC2Client({ region: "ap-south-1" });
// const resp = await client.send(new DescribeInstancesCommand({}));
```

Key difference: boto3 is a blocking library (inside `async def` routes use `run_in_threadpool` or `aioboto3`), while the JS SDK is promise-based by nature.

---

## 🟠 FastAPI Connection
On EC2 the app is the same FastAPI project, but credentials come from the instance's **IAM role**, not from keys in code or `.env`. Use boto3 normally and it picks up temporary credentials from the instance metadata service (IMDSv2). Put the load balancer's health check on `/health`. Read secrets from AWS Secrets Manager or SSM Parameter Store at startup.

```python
# FastAPI example — S3 presigned upload URL; no AWS keys in code because EC2 has an IAM role
import boto3
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool   # boto3 is blocking

app = FastAPI()

@app.get("/upload-url")
async def upload_url(name: str) -> dict[str, str]:
    s3 = boto3.client("s3")                                  # credentials come from the role
    url = await run_in_threadpool(                           # do not block the event loop
        s3.generate_presigned_url, "put_object",
        Params={"Bucket": "orders-uploads", "Key": name}, ExpiresIn=300,
    )
    return {"url": url}
```
(Not run: it needs AWS credentials and a real bucket.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Opening port 22 (or 5432, 8000) to `0.0.0.0/0`
✅ Correct: SSH from your IP only (or use SSM Session Manager); keep DB and app ports private

```bash
# Wrong
aws ec2 authorize-security-group-ingress --group-id sg-1 --protocol tcp --port 22 --cidr 0.0.0.0/0
# Right
aws ec2 authorize-security-group-ingress --group-id sg-1 --protocol tcp --port 22 --cidr 203.0.113.10/32
```

❌ Mistake 2: Hardcoding or committing AWS access keys
✅ Correct: IAM role on the instance; boto3 picks it up automatically

```python
# Wrong
s3 = boto3.client("s3", aws_access_key_id="AKIA...", aws_secret_access_key="...")
# Right
s3 = boto3.client("s3")      # role credentials, rotated automatically
```

❌ Mistake 3: Using the auto-assigned public IP and no backups
✅ Correct: Elastic IP (or a load balancer + DNS) and regular snapshots/AMIs

```text
Wrong:  stop/start the instance -> public IP changes -> DNS breaks
Right:  Elastic IP attached, EBS snapshots scheduled (Data Lifecycle Manager)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (instance is t3.micro, you are in the CPU-credit "standard" mode)
import boto3
ec2 = boto3.client("ec2", region_name="ap-south-1",
                   aws_access_key_id="x", aws_secret_access_key="x")
print(ec2.meta.region_name)
print(type(ec2).__name__)
```
Answer: The first line prints `ap-south-1`; the second prints `EC2` because boto3 builds the client class dynamically from the service model (the class name is the service's, not `Client`). Creating the client makes **no network call**, so it works offline with dummy keys. The tricky AWS part in the comment: `t3`/`t2` instances are *burstable*. They earn CPU credits while idle and spend them under load. When credits run out in standard mode the CPU is throttled to the baseline (about 20% for t3.micro), so a load test that looks fine for 10 minutes can suddenly slow down. In t3 the default is "unlimited" mode, which keeps speed but bills extra.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a Security Group and a Network ACL?
A1: A security group is a stateful firewall attached to the instance (return traffic is allowed automatically; allow rules only). A network ACL is a stateless firewall at the subnet level (rules for both directions, with allow and deny). Most apps use only security groups.

Q2: How do you give an EC2 app access to S3 securely?
A2: Attach an IAM role with a least-privilege policy (for example `s3:PutObject` on one bucket) through an instance profile. The SDK reads temporary credentials from the instance metadata service. No access keys are stored anywhere.

Q3: Public IP vs Elastic IP?
A3: A normal public IP is released when the instance stops. An Elastic IP is a static address you own until you release it and can re-attach to another instance. Behind a load balancer you do not need one on each instance.

Q4: How would you scale this?
A4: Make the instance stateless (sessions in Redis, files in S3, DB in RDS), create an AMI or launch template, run several instances in an Auto Scaling Group behind an Application Load Balancer with `/health` checks, and scale on CPU or request count.

Q5: EC2 vs Lambda vs ECS?
A5: EC2 gives full OS control and predictable cost for steady load but you patch and scale it. Lambda is pay-per-request with no servers but has time limits and cold starts. ECS/Fargate runs containers without managing servers and is the usual middle path.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a full Linux server with control over everything
- Steady traffic where reserved or savings-plan pricing is cheaper than per-request
- Long-running processes, WebSockets or background workers

❌ Avoid when:
- Spiky or very low traffic (Lambda or Cloud Run is cheaper)
- You do not want to patch OS and manage servers (use ECS Fargate, App Runner)
- You want a simple Git-push deploy (use Render or Railway)

---

## 📊 Visual Diagram
```
 Internet -> Route 53 (DNS) -> Elastic IP / ALB
                                   |
                  +------ VPC ------------------------------+
                  |  public subnet:   EC2 (Nginx + FastAPI)  |  <- Security Group 80/443
                  |       | IAM role                         |
                  |  private subnet:  RDS PostgreSQL         |  <- only EC2's SG allowed
                  +------------------------------------------+
                          |            |
                         S3       CloudWatch (logs, alarms)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AMI | Machine image used to start an instance | instance शुरू करने की image |
| Security Group | Instance firewall | instance का firewall |
| IAM Role | Permissions given to a service | service को दी गई permissions |
| Elastic IP | Static public IP | स्थिर public IP |
| User Data | Script run at first boot | पहली बार boot पर चलने वाली script |
| EBS | Block disk attached to EC2 | EC2 से जुड़ी disk |
| ALB | Application load balancer | traffic बाँटने वाला load balancer |

---

## ⚡ 3-Line Summary
English: EC2 is a rentable Linux server on AWS: pick an AMI, size, security group and IAM role. Bootstrap with user data, then run the usual VPS stack (systemd, Nginx). Use roles instead of keys and Elastic IPs plus snapshots for reliability.
Hindi: EC2 AWS पर किराए का Linux server है: AMI, size, security group और IAM role चुनो। User data से bootstrap करो, फिर सामान्य VPS stack (systemd, Nginx) चलाओ। Keys की जगह roles और भरोसे के लिए Elastic IP व snapshots इस्तेमाल करो।

---

## ➡️ Next Topic
**444. Deploy on AWS Lambda** — no servers at all: AWS runs your code only when a request arrives.
