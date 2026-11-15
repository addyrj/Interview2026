# AWS vs Azure Compare (folders 17 plus compare tables in 02-16)
# हिंदी में: AWS और Azure की सर्विस-दर-सर्विस मैपिंग, कीमत का मॉडल, IAM बनाम Entra, और कब क्या चुनें

> Prices/limits/SLAs below are "approximate — check current docs". Retiring services are flagged.

---

## 1. Hierarchy and account model

```
AWS:   Organization -> OU -> Account -> Region -> resources (IAM per account)
Azure: Entra tenant -> Mgmt Group -> Subscription -> Resource Group -> resources (RBAC)
```
- Key difference: Azure resources live in a Resource Group; AWS has no equivalent container (tags and CloudFormation stacks are nearest). | हिंदी: Azure में हर रिसोर्स एक Resource Group में रहता है, AWS में ऐसा नहीं।
- Resource Group = lifecycle + RBAC container: deploy, tag, secure and delete related resources together.

---

## 2. Service-by-service mapping

### Compute and containers
| Need | AWS | Azure |
|------|-----|-------|
| Virtual machine | EC2 | Virtual Machines |
| Auto scaling fleet | ASG + Launch Template | VM Scale Sets |
| Managed web app | Elastic Beanstalk / App Runner | App Service |
| Functions | Lambda | Azure Functions |
| Workflow | Step Functions | Durable Functions / Logic Apps |
| Serverless containers | ECS Fargate | Container Apps / ACI |
| Kubernetes | EKS | AKS |
| Own orchestrator | ECS | N/A (closest: Container Apps) |
| Registry | ECR | ACR |
| Batch | AWS Batch | Azure Batch |

### Storage
| Need | AWS | Azure |
|------|-----|-------|
| Object store | S3 (bucket) | Blob (storage account + container) |
| Temporary access | Presigned URL | SAS token |
| Block disk | EBS | Managed Disks |
| File share | EFS | Azure Files |
| Lifecycle | Lifecycle rules | Lifecycle management policy |
| Redundancy | Standard is multi-AZ; CRR cross-region | LRS, ZRS, GRS (S3 Standard is closest to ZRS) |
| CDN | CloudFront | Azure Front Door (classic Azure CDN being retired for some SKUs) |

### Databases
| Need | AWS | Azure |
|------|-----|-------|
| Postgres/MySQL | RDS / Aurora | Flexible Server (PostgreSQL Single Server retired) |
| Key-value/document | DynamoDB | Cosmos DB |
| Global distribution | DynamoDB Global Tables, Aurora Global | Cosmos DB multi-region writes |
| Cache | ElastiCache | Azure Cache for Redis (Azure Managed Redis announced as successor) |
| Warehouse | Redshift | Synapse |
| Hadoop/Spark | EMR | HDInsight |

### Networking
| Need | AWS | Azure |
|------|-----|-------|
| Private network | VPC (regional) | VNet (regional) |
| Subnet scope | One AZ | Spans zones in region |
| Firewall | Security Group + NACL | NSG (+ Azure Firewall) |
| L4 LB | NLB | Azure Load Balancer |
| L7 LB | ALB | Application Gateway |
| DNS | Route 53 | Azure DNS + Traffic Manager |
| Peering | VPC peering / Transit Gateway | VNet peering / Virtual WAN |
| Private PaaS access | PrivateLink interface endpoint | Private Endpoint |
| Free S3-style endpoint | Gateway endpoint | Service Endpoint |
| Dedicated line | Direct Connect | ExpressRoute |
| DDoS | Shield | DDoS Protection |

### Messaging
| Need | AWS | Azure |
|------|-----|-------|
| Queue | SQS (+ DLQ, FIFO) | Service Bus (DLQ, sessions) or Queue Storage |
| Fan-out | SNS | Service Bus topics |
| Events | EventBridge | Event Grid |
| Stream | Kinesis / MSK | Event Hubs (Kafka endpoint) |
| FIFO mapping | MessageGroupId, dedup ID, visibility timeout | SessionId, MessageId + duplicate detection, lock duration |

### Security, monitoring, devtools
| Need | AWS | Azure |
|------|-----|-------|
| Workload identity | IAM role | Managed identity |
| Secrets | Secrets Manager | Key Vault |
| Keys | KMS | Key Vault / Managed HSM |
| Audit log | CloudTrail | Activity Log |
| Metrics/logs | CloudWatch / Logs Insights | Azure Monitor / KQL in Log Analytics |
| APM/tracing | X-Ray | Application Insights |
| Notify | SNS | Action Groups |
| Guardrails | SCP | Azure Policy / deny assignments |
| Posture/threats | Security Hub / GuardDuty | Defender for Cloud / Defender |
| CI/CD | CodePipeline / CodeBuild / CodeDeploy | Azure Pipelines |
| Git | CodeCommit (closed to new customers 2024, verify) | Azure Repos (available) |
| IaC native | CloudFormation / CDK | ARM / Bicep |
| API front door | API Gateway | API Management |

हिंदी: मोटा नियम: नाम अलग, विचार वही; bucket = container, presigned = SAS, SG = NSG, role = managed identity।

---

## 3. Pricing-model notes (note 297)

```
On-demand (flexible, highest)
  -> Commitment: Savings Plans / Reserved (AWS) | Reservations / Savings Plan (Azure)
  -> Spot (AWS Spot | Azure Spot VMs): cheap, can be evicted
Monitor: Budgets + alerts + tags/cost allocation
```
| Feature | AWS | Azure |
|---------|-----|-------|
| Analysis | Cost Explorer | Cost Management |
| Commitment | Savings Plans / RI | Reservations / Savings Plan |
| Spot | Spot Instances | Spot VMs |
| Free tier | 12-month + always-free (approximate — check current docs) | Free account credit + always-free (approximate — check current docs) |
| Egress | Charged outbound | Charged outbound |
| License saver | BYOL | Azure Hybrid Benefit |
| Serverless billing | Requests + GB-seconds (approximate — check current docs) | Executions + GB-seconds (approximate — check current docs) |
| NoSQL billing | DynamoDB on-demand/provisioned | Cosmos RU/s (approximate — check current docs) |

- Cut compute cost: rightsizing, commitments, Spot for fault-tolerant jobs, scale-to-zero, shutdown schedules.
- Hidden costs: data egress, cross-AZ/region traffic, NAT gateways, log ingestion, idle load balancers and disks.
- Azure `az vm deallocate` stops compute billing.
- हिंदी: छुपे खर्च: egress, NAT, लॉग इनजेशन, खाली पड़े लोड बैलेंसर और डिस्क।

```bash
# Monthly budget alert on both clouds (note 297; Azure flags vary by CLI version)
aws budgets create-budget --account-id 123456789012 \
  --budget '{"BudgetName":"monthly","BudgetLimit":{"Amount":"50","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}'
az consumption budget create --budget-name monthly --amount 50 \
  --category cost --time-grain monthly \
  --start-date 2026-12-01 --end-date 2027-12-01
```

---

## 4. IAM vs Entra ID + RBAC (note 296)

| Feature | AWS | Azure |
|---------|-----|-------|
| Directory | Per account (Identity Center for SSO) | Entra tenant (shared by subscriptions) |
| Permissions | JSON policies (allow/deny) | RBAC roles at scope (+ deny assignments) |
| Workload identity | IAM role | Managed identity / service principal |
| Customer auth | Cognito | Entra External ID / B2C |
| Cross-account | AssumeRole | Cross-tenant/Lighthouse, guest users |
| Just-in-time admin | Temporary role sessions | PIM (P2) |
| Unused access | Access Analyzer | Access Reviews |
| Price | IAM free | Entra Free tier; P1/P2 paid (approximate — check current docs) |

- Evaluation: AWS explicit deny wins, otherwise needs an allow (plus SCP/boundary limits). Azure RBAC is additive allow at inherited scopes; deny assignments and Policy are guardrails.
- IAM role equivalent = managed identity plus an RBAC role assignment.
- हिंदी: AWS में JSON policy, Azure में scope पर role assignment। Full detail: `iam-cheatsheet.md`.

---

## 5. When to choose which (note 298)

```
Microsoft shop (AD, M365, .NET, SQL Server)?  -> lean Azure
Startup / Linux / open-source / widest services? -> lean AWS
Existing credits, partner or customer mandate?  -> follow that
Else: team skill + cost + region/compliance decides
```
| Factor | AWS | Azure |
|--------|-----|-------|
| Strength | Service breadth, maturity | Enterprise/Microsoft integration, hybrid |
| Identity | IAM | Entra ID with M365 SSO |
| Hybrid | Outposts | Arc, Azure Stack |
| Startups | Credits programs, community | Credits programs (check current terms) |

```yaml
# Decision matrix (score 1-5, weight by importance)
criteria:
  team_skills:        { aws: 4, azure: 2, weight: 5 }
  existing_ecosystem: { aws: 2, azure: 5, weight: 4 }
  required_services:  { aws: 5, azure: 4, weight: 4 }
  compliance_region:  { aws: 4, azure: 4, weight: 3 }
  cost_credits:       { aws: 3, azure: 4, weight: 3 }
# total = sum(score * weight) per cloud; pick higher, then validate with a PoC
```
- Defend to a CTO: weighted criteria, PoC results, TCO including people and egress, exit strategy, risk (lock-in, compliance).
- Mistakes: choosing from a blog benchmark (run a PoC instead); ignoring talent availability.
- हिंदी: ब्रांड नहीं, स्किल, इकोसिस्टम और ज़रूरत देखकर चुनें, फिर PoC से साबित करें।

---

## 6. Multi-cloud and cloud-agnostic (notes 299-300)

| Layer | AWS | Azure |
|-------|-----|-------|
| Hybrid/multi mgmt | EKS Anywhere, Outposts | Azure Arc |
| Neutral IaC | Terraform | Terraform |
| Native IaC | CloudFormation | Bicep/ARM |
| Run containers | EKS / ECS | AKS / Container Apps |
| Database | RDS PostgreSQL | Flexible Server PostgreSQL |
| Object storage | S3 | Blob (use adapter) |

- Multi-cloud pros: resilience, compliance, best-of-breed, avoiding lock-in. Cons: complexity, skills, security surface, egress cost.
- Easiest to port: containers, Postgres/MySQL, Redis, Kafka-compatible streams. Portability costs extra code and skips managed-service advantages (DynamoDB, Cosmos, Lambda triggers).
- Common layer: Terraform + containers/Kubernetes + OpenTelemetry + OIDC SSO.
- हिंदी: मल्टी-क्लाउड रेजिलिएंस देता है, पर जटिलता भी बढ़ाता है।

```javascript
// storage adapter: pick implementation by env (note 300)
async function makeStorage() {
  if (process.env.CLOUD === "aws") {
    const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
    const s3 = new S3Client({});
    return { put: (key, body) => s3.send(new PutObjectCommand({ Bucket: process.env.BUCKET, Key: key, Body: body })) };
  }
  const { BlobServiceClient } = require("@azure/storage-blob");
  const { DefaultAzureCredential } = require("@azure/identity");
  const c = new BlobServiceClient(process.env.BLOB_URL, new DefaultAzureCredential())
    .getContainerClient(process.env.CONTAINER);
  return { put: (key, body) => c.getBlockBlobClient(key).upload(body, Buffer.byteLength(body)) };
}
module.exports = { makeStorage };
```

---

## 7. Gotchas that interviewers like

- Subnets: AWS subnet = one AZ, Azure subnet spans zones. Both reserve 5 IPs per subnet.
- Public subnet in AWS = route to IGW; in Azure there is no such label (public IP + NSG/route decide; default outbound access being phased out, check docs).
- SG allow-only vs NSG allow+deny with priority; NACL is stateless, NSG is stateful.
- Contributor in Azure does not grant blob data access; need a data-plane role such as Storage Blob Data Reader.
- Retiring/closed: CodeCommit (AWS), Forecast (AWS), Blueprints (Azure), Spring Apps (Azure), classic Azure CDN SKUs. Verify in current docs.
