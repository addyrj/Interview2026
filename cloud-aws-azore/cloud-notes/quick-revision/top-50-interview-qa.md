# Top 50 Cloud Interview Q&A (AWS + Azure)
# हिंदी में: नोट्स के Interview Q&A से चुने गए 50 सबसे ज़्यादा पूछे जाने वाले सवाल, थीम के हिसाब से

> Answers are condensed from the Interview Q&A sections of cloud-notes 01-17. Prices/limits/SLAs: "approximate — check current docs".
> Tag: [E] easy, [M] medium, [H] hard. Each answer ends with a one-line हिंदी hint.

---

## A. Fundamentals and reliability (Q1-Q7)

**Q1 [M] How does shared responsibility differ for EC2 vs Lambda?**
On EC2 you patch the OS and runtime; on Lambda the provider manages OS/runtime and you own code, IAM and data. The provider always secures the physical data center.
हिंदी: EC2 में OS आपका, Lambda में सिर्फ़ कोड, IAM और डेटा।

**Q2 [H] A public S3 bucket leaked data. Whose fault, how to prevent?**
Customer configuration. Prevent with account-level Block Public Access, least-privilege policies, Config/Security Hub rules and access reviews.
हिंदी: कॉन्फ़िग की गलती ग्राहक की, इसलिए Block Public Access चालू रखें।

**Q3 [E] IaaS vs PaaS vs SaaS examples?**
EC2/Azure VM (IaaS), Elastic Beanstalk/App Service (PaaS), Microsoft 365 (SaaS). Lambda is FaaS, a serverless flavor of PaaS. Customer always keeps data, identity and configuration.
हिंदी: IaaS में सर्वर, PaaS में प्लेटफ़ॉर्म, SaaS में पूरा सॉफ़्टवेयर।

**Q4 [H] How do you design a 99.99% web app?**
Multi-AZ at every tier, stateless apps, managed HA DB, health checks and autoscaling, safe deployments (rolling/blue-green), tested failover. Composite SLA is the product of dependencies.
हिंदी: हर लेयर पर Multi-AZ और टेस्ट किया हुआ फेलओवर।

**Q5 [H] Five services at 99.95% each in series: overall?**
About 0.9995^5 = 99.75%, roughly 22 hours downtime a year (approximate); add redundancy or reduce dependencies.
```python
print(0.9995 ** 5)
```
हिंदी: सीरीज़ में SLA गुणा होकर घटता है।

**Q6 [M] RPO vs RTO, and cost effect? Design for RPO 1 min, RTO 15 min.**
RPO = max data loss, RTO = max downtime; lower values cost sharply more. Use a cross-region async replica (or global DB), IaC for fast bring-up, health-checked DNS failover, runbook and regular failover tests.
हिंदी: RPO = कितना डेटा खो सकते हैं, RTO = कितनी देर बंद।

**Q7 [M] SLA vs SLO vs SLI? Active-active vs active-passive?**
SLA external promise, SLO internal goal, SLI measured metric. Active-active serves from all nodes (better utilisation, complex state); active-passive keeps a standby (simpler, idle cost).
हिंदी: SLA वादा, SLO लक्ष्य, SLI माप।

---

## B. IAM and identity (Q8-Q15)

**Q8 [M] IAM policy evaluation order? Is IAM regional?**
IAM is global. Explicit deny wins; otherwise an explicit allow is needed (and not limited by SCP/boundary); else implicit deny.
हिंदी: deny सबसे ऊपर, डिफ़ॉल्ट deny, IAM ग्लोबल है।

**Q9 [M] Trust policy vs permission policy?**
Trust policy says who can assume the role; permission policy says what the role can do.
```json
{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
 "Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}
```
हिंदी: कौन role ले सकता है बनाम role क्या कर सकता है।

**Q10 [M] Identity-based vs resource-based policy? Does a permission boundary grant?**
Identity policy attaches to who; resource policy attaches to the resource and names a Principal (cross-account). A boundary grants nothing: effective permissions are the intersection with the identity policy (and SCPs).
हिंदी: boundary सिर्फ़ सीमा तय करती है, अनुमति नहीं देती।

**Q11 [H] Debug AccessDenied for an ECS task reading S3.**
Check the task role (not execution role), identity policy actions/ARNs, bucket policy, KMS key policy, SCPs/boundaries; use CloudTrail and the policy simulator.
हिंदी: task role, bucket policy, KMS और SCP चारों देखें।

**Q12 [H] Give GitHub Actions deploy access without stored keys.**
OIDC provider for token.actions.githubusercontent.com plus a role whose trust policy conditions on `aud` and `sub` (repo/branch or environment); the workflow uses `aws-actions/configure-aws-credentials` with `role-to-assume` and `id-token: write`. Azure uses a federated credential on the app registration.
हिंदी: OIDC से छोटी अवधि की credentials, कोई secret नहीं।

**Q13 [M] How do you handle an exposed access key?**
Deactivate, review CloudTrail for misuse, rotate, remove from history, and replace with role-based access.
हिंदी: पहले बंद करें, फिर लॉग देखें, फिर बदलें।

**Q14 [M] Azure: Contributor vs Owner; control plane vs data plane; additive roles?**
Owner can assign roles, Contributor cannot. Control plane (Actions) manages resources; data plane (DataActions) accesses content (Contributor does not give blob data access). Reader at subscription + Contributor at one RG = Contributor there, Reader elsewhere.
हिंदी: RBAC जुड़ता जाता है, और data plane अलग होता है।

**Q15 [H] Managed identity: system vs user-assigned? App still gets 403 after role assignment?**
System-assigned is 1:1 with the resource and deleted with it; user-assigned is standalone and shareable (good for blue/green slots). 403: propagation takes minutes, tokens are cached (up to ~24h), also check scope, data vs control plane role, and target firewall.
हिंदी: असाइनमेंट के बाद थोड़ा इंतज़ार और सही scope देखें।

---

## C. Networking (Q16-Q23)

**Q16 [E] What makes a subnet public? Why does AWS reserve 5 IPs?**
A route 0.0.0.0/0 to the Internet Gateway (plus public IPs). Reserved: network address, VPC router, DNS, future use, broadcast. Azure also reserves 5 per subnet.
हिंदी: IGW का रूट ही सबनेट को public बनाता है।

**Q17 [E] VPC CIDR limits; is VPC zonal or regional? Subnet?**
/16 (largest) to /28 (smallest) for IPv4. VPC is regional; each subnet lives in exactly one AZ. In Azure, VNet is regional and subnets span zones.
हिंदी: VPC regional, subnet एक AZ में।

**Q18 [E] Security Group vs NACL (and Azure NSG)?**
SG: instance/ENI level, stateful, allow-only. NACL: subnet level, stateless, allow + deny, numbered rules, first match wins. NSG: stateful allow+deny by priority, on subnet or NIC.
हिंदी: SG स्टेटफुल, NACL स्टेटलेस।

**Q19 [H] Site works for some clients but connections hang. NACL issue?**
Likely missing ephemeral return ports; allow 1024-65535 (Linux about 32768-60999, Windows 49152-65535).
हिंदी: लौटने वाले ports भी खोलने पड़ते हैं।

**Q20 [M] How do private instances reach the internet? NAT bill is huge, what now?**
Route 0.0.0.0/0 to a NAT Gateway in a public subnet (one per AZ). To cut the bill: find top talkers via Flow Logs, add S3/DynamoDB gateway endpoints (free) and interface endpoints for ECR/Secrets, keep traffic same-AZ, cache dependencies.
हिंदी: AWS सर्विस के लिए endpoints लगाकर NAT खर्च घटाएँ।

**Q21 [M] Is peering transitive? Peering vs Transit Gateway; 10 VPCs need full connectivity?**
No. Peering is simple, cheap, 1:1; TGW is hub-and-spoke with transitive routing and VPN/DX support (hourly + per-GB). Full mesh of 10 needs 45 peerings; use TGW (Azure: Virtual WAN / hub VNet).
हिंदी: कई नेटवर्क हों तो hub-and-spoke।

**Q22 [M] Private Endpoint vs Service Endpoint (Azure)?**
Private Endpoint gives a private IP per resource, reachable from on-prem. Service Endpoint keeps the public IP and just restricts access to your subnet. Prefer Private Endpoint for on-prem reach, per-resource granularity, or fully disabling public access.
हिंदी: Private Endpoint = अपना private IP।

**Q23 [M] Which route wins when several match? Fixed IP for a partner allow-list?**
Longest prefix match. For a fixed IP use NLB (static Elastic IP per AZ) or Global Accelerator; ALB IPs change.
हिंदी: सबसे specific रूट जीतता है।

---

## D. Compute, containers, serverless (Q24-Q32)

**Q24 [E] Stop vs terminate EC2? On-Demand vs Reserved vs Spot?**
Stop keeps EBS and can restart; terminate deletes the instance (root volume deleted by default). Spot is deep discount with a 2-minute interruption notice; Reserved/Savings Plans need 1-3 year commitment.
हिंदी: Stop में डेटा बचता है, terminate में नहीं।

**Q25 [H] Scale a stateful app (sessions, local uploads).**
Externalise state: sessions in Redis/ElastiCache, files in S3, DB in RDS; instances become disposable; use connection draining.
हिंदी: state बाहर रखो, इंस्टेंस डिस्पोज़ेबल बनाओ।

**Q26 [M] ALB vs NLB vs CLB; client IP behind ALB?**
ALB: path/host routing (HTTP). NLB: raw TCP/UDP, static IP, can preserve source IP. CLB: legacy. Behind ALB read `X-Forwarded-For`.
हिंदी: ALB वेब के लिए, NLB तेज़ TCP के लिए।

**Q27 [M] Lambda cold start: measure and fix?**
Measure `Init Duration` in the CloudWatch REPORT line or X-Ray. Fix with small bundle, arm64, init outside handler, memory tuning, provisioned concurrency; or move to Fargate if traffic is steady.
हिंदी: cold start नए एनवायरनमेंट की देरी है।

**Q28 [M] Lambda reserved vs provisioned concurrency; 200 req/s at 300 ms?**
Reserved = guarantee + cap (free); provisioned = warm environments (paid). 200 x 0.3 = 60 concurrent, so reserve above that with headroom and check account limits.
```python
print(200 * 0.3)
```
हिंदी: concurrency = req/s x सेकंड प्रति रिक्वेस्ट।

**Q29 [H] Lambda vs ECS Fargate vs VPS?**
Lambda for event-driven, spiky, short jobs; Fargate for long-running containers with steady traffic; VPS for cheapest steady low-scale load with full control.
हिंदी: spiky के लिए Lambda, steady के लिए Fargate।

**Q30 [M] ECS Fargate vs EC2; ECS vs EKS?**
Fargate has no instances to manage; EC2 for GPUs, daemon workloads, very large tasks or cheaper bin-packing. ECS is simpler; EKS for Kubernetes ecosystem and portability (adds control-plane fee).
हिंदी: सरलता के लिए ECS, K8s ताक़त के लिए EKS।

**Q31 [M] Azure Functions Consumption vs Premium? App Service plan scale up vs out?**
Consumption scales to zero but has cold starts and limits; Premium keeps pre-warmed instances and VNet integration at higher cost. Up = larger instance, out = more instances; you pay per plan instance, apps share it.
हिंदी: Plan का बिल, ऐप शेयर करते हैं।

**Q32 [M] App Service rollback and DB migrations with slot swaps? AKS vs EKS pod identity?**
Roll back by swapping slots again; use backward-compatible (expand/contract) migrations. EKS uses IRSA/Pod Identity; AKS uses Workload Identity federated with Entra. Both are conformant Kubernetes.
हिंदी: swap से रोलबैक, migration backward-compatible रखें।

---

## E. Storage and CDN (Q33-Q38)

**Q33 [M] S3 storage classes: unknown access pattern; 5 TB logs read in first 7 days?**
Intelligent-Tiering for unknown patterns. Logs: Standard for 30 days, lifecycle to Standard-IA/Glacier, then expire per compliance; batch tiny objects.
हिंदी: पैटर्न पता न हो तो Intelligent-Tiering।

**Q34 [M] S3 versioning: delete behaviour, disable, protect from admin deletion?**
Delete adds a delete marker; versioning can only be suspended; protect with Object Lock (needs versioning), MFA Delete and restrictive IAM/SCP.
हिंदी: delete marker से डेटा वापस आ सकता है।

**Q35 [M] Pre-signed URLs: restrict upload, revoke?**
Sign Content-Type for PUT; pre-signed POST with `content-length-range` for size limits. Cannot revoke one URL: delete the object, change the key, or deny via bucket policy.
हिंदी: URL अलग से रद्द नहीं होता।

**Q36 [M] CloudFront OAC vs OAI?**
OAC supports SSE-KMS, all Regions, dynamic methods, uses service principal + SourceArn; OAI is legacy. With SSE-KMS the key policy must allow `cloudfront.amazonaws.com`.
हिंदी: OAC नया तरीका है, OAI पुराना।

**Q37 [M] Azure Blob tiers, Archive cost, and SAS revocation?**
Archive is offline: rehydrate takes hours (standard) and incurs fees. Automate with lifecycle policy. Leaked service SAS: delete/modify the stored access policy, else rotate the account key; prefer short expiry and user delegation SAS.
हिंदी: Archive से पढ़ने में घंटे लगते हैं।

**Q38 [M] Azure LRS/ZRS/GRS and S3 equivalence?**
LRS one datacenter; ZRS across zones; RA-GRS adds read access to secondary. S3 Standard is multi-AZ in a region (closest to ZRS); cross-region needs CRR (like GRS).
हिंदी: ZRS = कई zones में कॉपी।

---

## F. Databases (Q39-Q44)

**Q39 [M] RDS Multi-AZ vs read replica; minute of errors during failover?**
Multi-AZ = synchronous, HA, standby not readable. Read replica = async, scales reads, manual promotion. Reduce impact with connection pool retries, short timeouts, endpoint DNS, RDS Proxy.
हिंदी: Multi-AZ HA के लिए, replica रीड स्केल के लिए।

**Q40 [M] Aurora vs RDS; migrate live RDS Postgres to Aurora?**
Aurora: faster failover, auto-scaling storage, up to 15 readers, but costlier and less portable. Migrate by creating an Aurora read replica cluster from RDS, waiting for lag near zero, stopping writes, promoting, switching endpoint.
हिंदी: पहले RDS, ज़रूरत पर Aurora।

**Q41 [H] DynamoDB throttled but usage low? WCU for 200 writes/s of 3 KB?**
Hot partition: fix key design (write sharding `userId#0..N`) rather than raise capacity. 3 WCU per write x 200 = 600 WCU. RCU = 4 KB reads, WCU = 1 KB writes.
```python
import math
print(math.ceil(3 / 1) * 200)
```
हिंदी: throttling का कारण hot partition है।

**Q42 [M] GSI vs LSI?**
GSI can be added later, eventually consistent only; LSI only at table creation. A starved GSI can throttle base-table writes.
हिंदी: GSI बाद में जुड़ सकता है।

**Q43 [M] Cosmos DB: RU, consistency levels, 429 errors, partition key?**
A 1 KB point read is about 1 RU. Levels: Strong, Bounded Staleness, Session (default), Consistent Prefix, Eventual. 429 = RU limit: check hot partition, raise RU/s or autoscale, fix key, retry with backoff. Key: high cardinality, even distribution, in query filters; hierarchical keys for a huge tenant.
हिंदी: Session सबसे सही डिफ़ॉल्ट है।

**Q44 [M] Redis cache-aside and cache stampede?**
App checks cache, on miss reads DB and fills cache. Prevent stampede with request coalescing/locks, jittered TTLs or refresh-ahead.
हिंदी: एक ही worker cache दोबारा भरे।

---

## G. Messaging (Q45-Q47)

**Q45 [M] SQS standard vs FIFO; visibility timeout; DLQ gotcha?**
Standard = scale, at-least-once (make handlers idempotent); FIFO = order + dedup, name ends `.fifo`, MessageGroupId orders. Visibility timeout hides in-flight messages (ChangeMessageVisibility for long jobs). Configure DLQ on the SQS queue, keep source visibility timeout >= function timeout.
हिंदी: duplicates संभव हैं, इसलिए idempotent लिखें।

**Q46 [M] SQS vs SNS vs EventBridge vs Kinesis?**
Queue for work (pull), topic for fan-out (push), bus for content-based routing/schedules/replay, stream for ordered replay. SNS + SQS gives durable fan-out.
हिंदी: काम के लिए क्यू, बाँटने को SNS।

**Q47 [M] Azure Service Bus vs SQS; Event Hubs vs Kinesis; Event Grid vs Service Bus?**
Service Bus adds topics, sessions, transactions (FIFO maps: MessageGroupId to SessionId, visibility timeout to lock duration). Event Hubs partition = Kinesis shard, and has a Kafka endpoint. Event Grid = lightweight fact notifications; Service Bus = commands/work.
हिंदी: नाम अलग, पैटर्न वही।

---

## H. Security, monitoring, ops, cost (Q48-Q50)

**Q48 [M] CloudTrail vs CloudWatch vs Config; alert on root login?**
CloudTrail = who did what; CloudWatch = metrics/logs/alarms; Config = resource state history/compliance. Root login: trail to CloudWatch Logs, metric filter on `userIdentity.type=Root`, alarm to SNS (or EventBridge rule).
हिंदी: CloudTrail = किसने किया।

**Q49 [M] Secrets Manager vs Parameter Store; Key Vault protection; envelope encryption?**
Secrets Manager has rotation and cross-account sharing (per-secret cost); Parameter Store is cheaper config. Key Vault: Managed Identity access, soft delete and purge protection, private endpoints. Envelope encryption: data key encrypts data, KMS key encrypts the data key.
हिंदी: .env नहीं, Secrets Manager या Key Vault।

**Q50 [M] How to cut cloud cost, and hidden costs? When choose AWS vs Azure?**
Rightsizing, commitments, Spot for fault-tolerant jobs, scale-to-zero, shutdown schedules. Hidden: egress, cross-AZ/region traffic, NAT gateways, log ingestion, idle LBs and disks. Choose by ecosystem, skills and compliance, then PoC: Microsoft shop leans Azure, startup/Linux/open-source leans AWS.
हिंदी: ब्रांड नहीं, स्किल और ज़रूरत देखकर चुनें, फिर PoC करें।

---

## Bonus one-liners
- Retiring/closed (verify in current docs): CodeCommit (no new customers), Forecast, Blueprints, Spring Apps, classic Azure CDN SKUs.
- हिंदी: जवाब में हमेशा trade-off बताएँ, सिर्फ़ सर्विस का नाम नहीं।
