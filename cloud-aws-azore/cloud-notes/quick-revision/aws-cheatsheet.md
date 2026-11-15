# AWS Cheatsheet (folders 01-08)
# हिंदी में: AWS की हर सर्विस एक-दो लाइन में, इंटरव्यू से पहले तेज़ रिवीज़न के लिए

> Format: **Service** — gist | हिंदी hint. Prices/limits/SLAs are "approximate — check current docs".
> Source: cloud-notes 01 to 08 only. Region used in examples: ap-south-1.

---

## 0. Cloud basics (folder 01)

- **IaaS/PaaS/SaaS** — EC2 or Azure VM = IaaS, Beanstalk or App Service = PaaS, Microsoft 365 = SaaS; customer always keeps data, identity, config. | हिंदी: डेटा, पहचान और कॉन्फ़िग हमेशा आपकी ज़िम्मेदारी है।
- **Shared responsibility** — provider secures the data center; on EC2 you patch OS/runtime, on Lambda you own code, IAM and data. | हिंदी: बिल्डिंग प्रोवाइडर की, ताला-चाबी आपकी।
- **Region / AZ** — Region = geography, AZ = isolated data center; use 2+ AZs for HA. | हिंदी: Region इलाका है, AZ अलग डेटा सेंटर।
- **RPO / RTO** — RPO = max data you can lose, RTO = max downtime; lower values cost much more. | हिंदी: RPO = कितना डेटा खो सकते हैं, RTO = कितनी देर बंद रह सकते हैं।
- **SLA maths** — services in series multiply: 0.9995^5 = about 99.75% (approximate). | हिंदी: सीरीज़ में SLA गुणा होता है, इसलिए घटता है।
- **CapEx vs OpEx** — CapEx = upfront purchase, OpEx = pay as you go; commit (Savings Plans) for steady baseline, Spot for fault-tolerant jobs. | हिंदी: CapEx पहले का खर्च, OpEx इस्तेमाल के हिसाब से।
- **Edge / CDN POP** — content cached near users (CloudFront). | हिंदी: कंटेंट यूज़र के पास कैश होता है।

---

## 1. Compute (folders 02, 04)

- **EC2** — pay-as-you-go virtual servers; design for replacement, not repair. Stop keeps EBS, terminate deletes the instance. | हिंदी: सर्वर को ठीक करने के बजाय बदलने के हिसाब से बनाओ।
- **Instance types** — t burst, m balanced, c CPU, r memory. | हिंदी: workload देखकर family चुनो।
- **AMI / Key pair / User data** — AMI = reusable server template; key pair = public key on server, private with you (prefer SSM); user data bootstraps at first boot via cloud-init. | हिंदी: AMI सर्वर का साँचा है, user data पहली बूट पर सेटअप करता है।
- **Launch Template + ASG** — template is the versioned recipe (Launch Configurations are deprecated); ASG keeps a min-max fleet across AZs, health-checked, self-healing. | हिंदी: ASG माँग के हिसाब से इंस्टेंस घटाता-बढ़ाता है।
- **ELB (ALB / NLB / CLB)** — ALB = HTTP, path/host routing; NLB = fast TCP, static IP per AZ; CLB = legacy. Target group = health-checked pool. | हिंदी: वेब के लिए ALB, तेज़ TCP के लिए NLB, CLB नए काम में नहीं।
- **Lambda** — run code on events, pay per use (requests + GB-seconds, approximate — check current docs). | हिंदी: इवेंट पर कोड चलता है, इस्तेमाल का ही पैसा।
- **Lambda Layers / Env vars / Triggers** — layers share dependencies; env vars keep config out of code; triggers connect events to Lambda. | हिंदी: layers डिपेंडेंसी बाँटती हैं, env vars कॉन्फ़िग अलग रखते हैं।
- **Lambda concurrency / cold start** — reserved = guarantee + cap (free), provisioned = warm environments (paid); cold start = init delay, see `Init Duration` in logs. | हिंदी: cold start नए एनवायरनमेंट की शुरुआती देरी है।
- **API Gateway** — managed API front door. REST = features, HTTP = cheap/fast, WebSocket = real-time; stages = named environments; auth via JWT/IAM/Lambda authorizers. | हिंदी: Gateway पर ही auth करो।
- **ECS** — managed Docker orchestration; Cluster holds, Service maintains, Task runs; task definition = versioned JSON blueprint. | हिंदी: Cluster रखता है, Service बनाए रखती है, Task चलता है।
- **Fargate vs EC2 launch type** — Fargate = no servers to manage; EC2 = more control, cheaper at steady scale. | हिंदी: Fargate में server नहीं, EC2 में control।
- **ECR** — IAM-secured private image storage; CI pushes SHA-tagged images then rolls ECS. | हिंदी: ECR private image स्टोर है।
- **EKS** — AWS-run Kubernetes control plane; ECS for simplicity, EKS for K8s power/portability. | हिंदी: सरलता के लिए ECS, ताक़त के लिए EKS।
- **Elastic Beanstalk / App Runner / Batch** — Beanstalk: upload code, AWS builds stack; App Runner: zero-ops HTTPS containers; Batch: queued containerised jobs on scaling compute. | हिंदी: कोड दो, बाकी AWS सँभालेगा।

```bash
# Launch EC2 with IMDSv2 required and SSM profile (from note 032)
aws ec2 run-instances \
  --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --instance-type t3.micro \
  --subnet-id subnet-aaaa1111 --security-group-ids sg-aaaa1111 \
  --iam-instance-profile Name=ec2-ssm-profile \
  --metadata-options HttpTokens=required
```

```javascript
// Lambda handler (note 085), save as index.mjs, handler = index.handler
export const handler = async (event) => {
  return {
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ ok: true, ts: Date.now() }),
  };
};
```

```json
{
  "family": "api",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/api-task-role"
}
```

---

## 2. Storage and CDN (folder 02)

- **S3** — durable, scalable object storage by key over HTTPS; buckets hold objects. | हिंदी: S3 असीमित ऑब्जेक्ट स्टोरेज है, key से एक्सेस।
- **Storage classes** — pick by read frequency; Intelligent-Tiering for unknown patterns; Glacier Instant = ms access, Flexible = restore job. | हिंदी: कितना पढ़ा जाता है, उसी से क्लास चुनो।
- **Versioning** — keeps every revision; delete adds a delete marker; can only be suspended, not removed. | हिंदी: गलती वापस ठीक हो सकती है।
- **Lifecycle** — rules move/expire data automatically to save money. | हिंदी: डेटा अपने-आप सस्ते क्लास में जाता है।
- **Replication** — live copy elsewhere for DR/compliance. | हिंदी: बकेट की लाइव कॉपी दूसरी जगह।
- **Bucket policy / ACL / Block Public Access** — resource JSON rulebook; disable ACLs, keep Block Public Access ON. | हिंदी: ACL बंद, Block Public Access चालू।
- **Pre-signed URL** — time-limited direct access without public bucket. | हिंदी: बिना पब्लिक किए सीमित समय का एक्सेस।
- **S3 encryption** — encrypted at rest by default; use KMS for key control and audit. | हिंदी: चाबी पर नियंत्रण चाहिए तो KMS।
- **CloudFront (+S3 / ALB / OAC)** — edge cache; private S3 + OAC is the standard static site; lock ALB so only CloudFront reaches it. OAC replaces legacy OAI. | हिंदी: प्राइवेट S3 और CloudFront स्टैटिक साइट का स्टैंडर्ड।
- **Route 53** — DNS; routing policies (weighted for canary, latency, geolocation, failover) plus health checks. | हिंदी: DNS किस endpoint का जवाब दे, यह policy तय करती है।
- **Elastic IP** — remappable static public IPv4 owned by your account. | हिंदी: स्थायी public IP जो दूसरे रिसोर्स पर लग सकता है।

```json
{
  "Rules": [{
    "ID": "logs-tiering",
    "Status": "Enabled",
    "Filter": { "Prefix": "logs/" },
    "Transitions": [
      { "Days": 30, "StorageClass": "STANDARD_IA" },
      { "Days": 90, "StorageClass": "GLACIER" }
    ],
    "Expiration": { "Days": 365 }
  }]
}
```

```javascript
// Pre-signed upload URL, SDK v3 (note 051), save as .mjs
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
const s3 = new S3Client({ region: "ap-south-1" });
export async function uploadUrl(userId) {
  const cmd = new PutObjectCommand({
    Bucket: "my-app-uploads-prod",
    Key: `users/${userId}/avatar.png`,
    ContentType: "image/png",
  });
  return getSignedUrl(s3, cmd, { expiresIn: 300 });
}
```

---

## 3. Databases (folder 03)

- **RDS** — managed relational DB; ops are AWS's, data is yours. Default to PostgreSQL. | हिंदी: ऑपरेशन्स AWS का, डेटा आपका।
- **Multi-AZ** — synchronous standby, automatic failover (HA). **Read replica** — async, scales reads, not HA. | हिंदी: Multi-AZ = HA, replica = सिर्फ़ रीड स्केल।
- **RDS backups / parameter groups / SG** — PITR from backups + logs, restore makes a NEW instance; tune via parameter groups; open DB port only from app SG. | हिंदी: रिस्टोर हमेशा नया इंस्टेंस बनाता है।
- **Aurora** — MySQL/Postgres compatible on shared 6-copy storage; up to 15 readers; start with RDS, move to Aurora when scale/failover justify cost. | हिंदी: बड़े स्केल और तेज़ फेलओवर के लिए Aurora।
- **Aurora Serverless v2** — pay per ACU used (approximate — check current docs); v1 is legacy/being retired, use v2. | हिंदी: v1 रिटायर हो रहा है, v2 इस्तेमाल करें।
- **DynamoDB** — serverless key-driven NoSQL; design around access patterns. Partition key + sort key are immutable. | हिंदी: डिज़ाइन एक्सेस पैटर्न से करो।
- **Capacity** — RCU = 4 KB read/s, WCU = 1 KB write/s, round up; on-demand = simple, provisioned = cheaper for steady load. | हिंदी: RCU 4 KB रीड, WCU 1 KB राइट।
- **GSI / LSI** — GSI any time, eventually consistent; LSI only at table creation. | हिंदी: GSI बाद में जोड़ सकते हैं, LSI नहीं।
- **Streams / DAX** — 24-hour ordered change log triggering Lambda; DAX = microsecond read cache. | हिंदी: Streams बदलाव का लॉग, DAX तेज़ कैश।
- **ElastiCache** — managed Redis/Memcached; prod Redis = replication group, Multi-AZ, TLS, private network; cluster mode shards over 16384 slots. | हिंदी: DB का लोड और लेटेंसी घटाता है।
- **DocumentDB** — MongoDB-API compatible managed DB (not real MongoDB). | हिंदी: असली MongoDB नहीं, उसकी API जैसा।
- **Neptune / Redshift / Timestream** — graph DB / columnar warehouse / serverless time-series. | हिंदी: ग्राफ़, वेयरहाउस, टाइम-सीरीज़।
- **Choosing** — match the database to the access pattern. | हिंदी: एक्सेस पैटर्न से डेटाबेस चुनो।

```bash
# RDS PostgreSQL: Multi-AZ, encrypted, private (note 060)
aws rds create-db-instance \
  --db-instance-identifier myapp-prod \
  --engine postgres \
  --db-instance-class db.t4g.medium \
  --allocated-storage 50 --storage-type gp3 \
  --master-username appadmin --manage-master-user-password \
  --multi-az --storage-encrypted \
  --no-publicly-accessible \
  --db-subnet-group-name private-db-subnets \
  --vpc-security-group-ids sg-0123456789abcdef0 \
  --backup-retention-period 7 \
  --deletion-protection
```

```python
# DynamoDB CRUD with boto3 (note 070)
import boto3
from boto3.dynamodb.conditions import Key
ddb = boto3.resource("dynamodb", region_name="ap-south-1")
t = ddb.Table("Orders")
t.put_item(Item={"userId": "u1", "orderId": "o-100", "total": 499})
print(t.query(KeyConditionExpression=Key("userId").eq("u1"))["Items"])
```

---

## 4. Networking (folder 02)

- **VPC** — isolated regional network; CIDR /16 (largest) to /28 (smallest). | हिंदी: VPC क्लाउड में आपका प्राइवेट नेटवर्क है।
- **Subnet** — AZ-bound slice; "public" only because the route table sends 0.0.0.0/0 to the IGW; 5 IPs reserved. | हिंदी: IGW का रूट ही सबनेट को public बनाता है।
- **IGW / NAT GW** — IGW two-way internet (one per VPC, free); NAT GW outbound-only for private subnets (one per AZ for HA). | हिंदी: NAT सिर्फ़ बाहर जाने देता है।
- **Security Group / NACL** — SG stateful allow-only on ENI; NACL stateless, ordered, subnet-level allow+deny. | हिंदी: SG स्टेटफुल, NACL स्टेटलेस।
- **Peering / Route tables** — peering 1:1, non-transitive, routes on both sides; longest-prefix match wins. | हिंदी: Peering transitive नहीं है।
- **VPC endpoints** — S3/DynamoDB gateway endpoints are free; interface endpoints (PrivateLink) for other services. | हिंदी: NAT खर्च बचाने के लिए endpoints।
- Details: see `vpc-cheatsheet.md`.

---

## 5. Messaging (folder 05)

- **SQS** — buffers and decouples work. Standard = scale, at-least-once; FIFO = order + dedup (name ends `.fifo`). | हिंदी: services के बीच काम को buffer करता है।
- **Visibility timeout / DLQ / long polling** — hides in-flight messages; DLQ quarantines poison messages (set on the SQS queue, not on Lambda); long polling cuts cost and empty calls. | हिंदी: DLQ ख़राब messages को अलग रखता है।
- **SNS** — one message fans out to many subscribers; filters pick each subscriber's part. | हिंदी: एक message कई subscribers तक।
- **SNS + SQS fan-out** — SNS fans out, SQS buffers each consumer; new consumer = new queue subscribed. | हिंदी: बाँटो SNS से, सहेजो SQS में।
- **EventBridge** — routes events to targets by pattern/schedule rules; archive/replay. | हिंदी: pattern देखकर सही target तक भेजता है।
- **Kinesis Data Streams** — ordered, replayable, shard-based. **Firehose** — no-code delivery to storage. | हिंदी: KDS रीप्ले-योग्य, Firehose बिना कोड डिलीवरी।
- **MSK** — managed Kafka, AWS handles brokers. | हिंदी: ब्रोकर-संचालन AWS का।
- **Pattern rule** — queue for work, topic for fan-out, bus for routing, stream for replay. | हिंदी: काम के लिए क्यू, बाँटने को SNS, रूटिंग को EventBridge, रीप्ले को Kinesis।

```python
# SQS DLQ with redrive policy (note 114)
import boto3, json
sqs = boto3.client("sqs", region_name="ap-south-1")
dlq_url = sqs.create_queue(QueueName="orders-dlq")["QueueUrl"]
dlq_arn = sqs.get_queue_attributes(QueueUrl=dlq_url,
          AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
sqs.create_queue(QueueName="orders", Attributes={
    "RedrivePolicy": json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": "3"})})
```

---

## 6. Security and monitoring (folder 06)

- **IAM** — authenticate then authorize; global and free; explicit deny wins. See `iam-cheatsheet.md`. | हिंदी: पहचान जाँचो, फिर कम-से-कम अनुमति दो।
- **Shield / WAF** — Shield absorbs DDoS at the edge; WAF filters malicious HTTP requests. | हिंदी: Shield DDoS रोकता है, WAF बुरे HTTP रिक्वेस्ट।
- **Secrets Manager** — encrypted, audited, rotating secrets (per-secret cost). **Parameter Store** — cheap hierarchical config/SecureString. | हिंदी: .env नहीं, Secrets Manager इस्तेमाल करो।
- **KMS** — managed keys, envelope encryption (data key encrypted by KMS key). **ACM** — free auto-renewing TLS certs. | हिंदी: डेटा की चाबी KMS में सुरक्षित।
- **CloudTrail** — who did what (API audit log). **CloudWatch** — metrics, logs, alarms, dashboards. **Config** — resource state history + compliance rules. | हिंदी: CloudTrail = किसने किया, CloudWatch = कैसा चल रहा है।
- **GuardDuty / Security Hub / Inspector / Macie** — agentless threat detection / single findings pane / CVE scanning / PII in S3. | हिंदी: हमले, पैनल, कमजोरी, संवेदनशील डेटा।
- **VPC Flow Logs** — who talked to whom, not what they said (no DNS/metadata traffic). | हिंदी: कौन किससे जुड़ा, क्या बोला नहीं।
- **Organizations + SCP** — many accounts, one tree; SCP is a permission ceiling and does not grant access. | हिंदी: SCP अकाउंट की अनुमतियों की छत है।
- **Cost Explorer / Budgets / Trusted Advisor** — where money goes / warn before overspend / built-in account health check. | हिंदी: खर्च कहाँ, चेतावनी, हेल्थ चेकअप।

```hcl
# CloudWatch alarm on ALB 5xx to SNS (note 138, Terraform)
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "api-5xx"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "HTTPCode_Target_5XX_Count"
  statistic           = "Sum"
  period              = 60
  evaluation_periods  = 5
  datapoints_to_alarm = 3
  threshold           = 10
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
}
```

---

## 7. Developer tools (folder 07)

- **CodeCommit** — IAM-integrated Git; AWS stopped onboarding new customers in July 2024, so check current docs; most teams use GitHub. | हिंदी: नए ग्राहकों के लिए बंद, GitHub चुनें।
- **CodeBuild / CodeDeploy / CodePipeline** — pay-per-minute containerised builds (buildspec.yml) / safe rollouts with rollback / chains build-test-deploy. Note: deprecated GitHub OAuth source, use CodeConnections. | हिंदी: बिल्ड, डिप्लॉय और पाइपलाइन।
- **CodeArtifact** — private caching package registry. | हिंदी: प्राइवेट पैकेज रजिस्ट्री।
- **CloudFormation / CDK / SAM** — declarative stacks with rollback / infra as real code over CloudFormation / shorthand CloudFormation for serverless. | हिंदी: कोड से इंफ्रा बनाओ।
- **X-Ray** — follows one request across services. **SDK** — signed, retried AWS calls. | हिंदी: X-Ray पूरा रास्ता और देरी दिखाता है।
- **GitHub Actions + OIDC** — swap GitHub JWT for temporary AWS credentials, no stored keys. | हिंदी: कीज़ की जगह OIDC।
- **Deploy recipes** — Node/FastAPI: build, push to ECR, update ECS service; React: sync to private S3, CloudFront, invalidate index.html. | हिंदी: build, push, update।

```yaml
# buildspec.yml (note 152, trimmed)
version: 0.2
env:
  variables:
    REPO: 111122223333.dkr.ecr.ap-south-1.amazonaws.com/my-api
phases:
  install:
    runtime-versions:
      nodejs: 20
  pre_build:
    commands:
      - npm ci
      - npm test
  build:
    commands:
      - docker build -t $REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION .
  post_build:
    commands:
      - docker push $REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION
```

```yaml
# CloudFormation (note 157)
AWSTemplateFormatVersion: "2010-09-09"
Description: Private S3 bucket for uploads
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prod]
    Default: dev
Resources:
  UploadBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      BucketName: !Sub "my-uploads-${Env}-${AWS::AccountId}"
Outputs:
  BucketArn:
    Value: !GetAtt UploadBucket.Arn
```

---

## 8. AI services (folder 08)

- **Bedrock** — pay-per-token LLM API inside AWS; model IDs change, check the console. | हिंदी: AWS के अंदर token के हिसाब से LLM API।
- **SageMaker** — train and host custom ML models. | हिंदी: अपने मॉडल train और host करो।
- **Rekognition / Textract** — image and video analysis / scanned documents to structured data. | हिंदी: इमेज और दस्तावेज़ की समझ।
- **Comprehend / Translate** — sentiment, entities, PII from text / pay-per-character translation. | हिंदी: टेक्स्ट से sentiment और अनुवाद।
- **Polly / Transcribe** — text to speech / audio to searchable text. | हिंदी: टेक्स्ट से आवाज़ और आवाज़ से टेक्स्ट।
- **Personalize** — managed recommendations from click data. | हिंदी: क्लिक डेटा से सुझाव।
- **Forecast** — closed to new customers; AWS points to SageMaker Canvas / SageMaker AI for new forecasting (check current status). | हिंदी: नए ग्राहकों के लिए बंद, पहले availability जाँचें।

```python
# Bedrock Converse (note 166); model id is an example, check console for current ids
import boto3
client = boto3.client("bedrock-runtime", region_name="us-east-1")
resp = client.converse(
    modelId="anthropic.claude-3-haiku-20240307-v1:0",
    messages=[{"role": "user", "content": [{"text": "Explain ECS in one line"}]}],
    inferenceConfig={"maxTokens": 200, "temperature": 0.2},
)
print(resp["output"]["message"]["content"][0]["text"])
```

---

## Quick reminders
- Retiring/closed: CodeCommit (no new customers), Forecast (closed to new customers), Aurora Serverless v1 (legacy), Launch Configurations (deprecated), CLB (legacy). Verify in current docs.
- हिंदी: कोई भी सर्विस चुनने से पहले उसकी availability और retirement की स्थिति ज़रूर जाँचें।
