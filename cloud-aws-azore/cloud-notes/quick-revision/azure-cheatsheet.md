# Azure Cheatsheet (folders 09-16)
# हिंदी में: Azure की हर सर्विस एक-दो लाइन में, AWS के बराबर के नाम के साथ

> Format: **Service** (AWS equivalent) — gist | हिंदी hint. Prices/limits/SLAs are "approximate — check current docs".
> Source: cloud-notes 09 to 16 only. Region used in examples: centralindia.

---

## 0. Fundamentals and governance (folder 09)

- **Hierarchy** — Tenant (Entra) > Management Group > Subscription > Resource Group > Resource; same ideas as AWS, different names. | हिंदी: विचार वही, नाम और hierarchy अलग।
- **Subscription** (AWS account) — billing and access boundary. | हिंदी: बिलिंग और access की सीमा।
- **Resource Group** — lifecycle, access and billing folder; a resource lives in exactly one group, most types can be moved. | हिंदी: एक रिसोर्स सिर्फ़ एक group में।
- **Management Groups** (Organizations) — apply Policy and RBAC across many subscriptions, inherited downward. | हिंदी: कई सब्सक्रिप्शन्स पर एक साथ नियम।
- **Regions / zones** — spread across zones for HA, across regions for DR. | हिंदी: HA के लिए zones, DR के लिए regions।
- **Entra ID** (IAM directory) — identity backbone for users, apps and tokens; formerly Azure AD. | हिंदी: Azure की पहचान और लॉगिन की रीढ़।
- **RBAC** — principal + role + scope, additive and inherited. Contributor cannot grant access, Owner can. | हिंदी: कौन + रोल + स्कोप।
- **Azure Policy** (SCP/Config rules) — guardrails on resource configuration; RBAC controls user actions, Policy controls resource properties. | हिंदी: रिसोर्स बनाने के नियम।
- **Blueprints** — deprecated, planned retirement July 2026 (verify current docs); use IaC + Policy + Template Specs + Deployment Stacks. | हिंदी: Blueprints रिटायर हो रहा है।
- **Tags / naming** — tags = cost and ownership labels (enforce with Policy); name as type-workload-env-region, most names are permanent. | हिंदी: Tags खर्च और मालिक का लेबल।
- **Cost Management / SLA** — visibility, budgets, savings advice; SLA chains multiply. 99.9% allows about 43 minutes per month (approximate). | हिंदी: SLA जोड़ने पर गुणा करें।
- **CLI** — `az` and Az PowerShell are scriptable front doors to ARM. | हिंदी: az से स्क्रिप्ट चलाओ।

```bash
# RBAC: Contributor on one resource group (note 183)
az role assignment create \
  --assignee <sp-or-group-object-id> \
  --role "Contributor" \
  --resource-group rg-myapp-prod
az role assignment list --resource-group rg-myapp-prod -o table
```

---

## 1. Compute (folder 10)

- **Virtual Machines** (EC2) — full-control IaaS server; `az vm deallocate` stops compute billing. | हिंदी: EC2 जैसा पूरा-नियंत्रण वाला सर्वर।
- **VM sizes / pricing** — pick family by workload; save with Reservation or Spot (approximate — check current docs). | हिंदी: Reservation/Spot से बचत।
- **VM Scale Sets** (Auto Scaling Group) — scale out identical VMs. | हिंदी: VMs का Auto Scaling Group।
- **App Service** (Elastic Beanstalk) — managed hosting for web apps/APIs; **plan** is the billed compute shared by your apps; scale up = bigger, out = more instances. | हिंदी: Plan का बिल आता है, ऐप शेयर करते हैं।
- **Deployment slots** — deploy to a slot, verify, swap; roll back by swapping again. | हिंदी: slot में deploy, जाँचो, swap।
- **Azure Functions** (Lambda) — triggers + bindings; Consumption scales to zero with cold starts, Premium keeps pre-warmed instances. | हिंदी: Azure का Lambda।
- **ACI** (Fargate task) — quick per-second containers without orchestration. | हिंदी: बिना cluster के तुरंत container।
- **AKS** (EKS) — managed Kubernetes; simpler than EKS, EKS more AWS-native; pod identity via Workload Identity (Entra). | हिंदी: Kubernetes वही, cloud glue अलग।
- **ACR** (ECR) — private image store. | हिंदी: private image store।
- **Azure Batch** (AWS Batch) — big parallel jobs on auto-scaled VM pools. | हिंदी: बड़े parallel jobs।
- **Logic Apps** (Step Functions-like low-code) — low-code workflow engine. | हिंदी: low-code workflow।
- **Spring Apps** — retirement announced; verify dates, prefer Azure Container Apps/AKS for new Spring workloads. | हिंदी: नए काम में containers की ओर जाएँ।

```bash
# VM quick start (note 191)
az group create -n rg-vm -l centralindia
az vm create -g rg-vm -n vm-api-01 \
  --image Ubuntu2204 --size Standard_B2s \
  --admin-username azureuser --generate-ssh-keys \
  --public-ip-sku Standard
az vm deallocate -g rg-vm -n vm-api-01
```

```javascript
// Azure Functions v4 model (note 197)
const { app } = require('@azure/functions');
app.http('hello', {
  methods: ['GET', 'POST'],
  authLevel: 'function',
  handler: async (request, context) => {
    const name = request.query.get('name') || 'world';
    context.log(`Hello ${name}`);
    return { status: 200, jsonBody: { message: `Hello, ${name}` } };
  },
});
```

```bash
# AKS with ACR and autoscaler (note 199)
az aks create -g rg-aks -n aks-demo --node-count 2 --node-vm-size Standard_B2s \
  --enable-managed-identity --attach-acr myacr123 \
  --enable-cluster-autoscaler --min-count 2 --max-count 4 --generate-ssh-keys
az aks get-credentials -g rg-aks -n aks-demo
```

---

## 2. Networking (folder 11)

- **VNet** (VPC) — private regional network; subnets span all zones. Details in `vpc-cheatsheet.md`. | हिंदी: AWS के VPC जैसा।
- **NSG** (SG + NACL) — free stateful allow/deny rules by priority, on subnet and/or NIC. | हिंदी: मुफ़्त stateful firewall।
- **Azure Firewall** — central managed L3-L7 firewall with FQDN rules (SKUs: Basic, Standard, Premium with TLS inspection and IDPS). | हिंदी: FQDN rules वाला central firewall।
- **Load Balancer** (NLB) — fast Layer-4 (Basic SKU retired, use Standard). **Application Gateway** (ALB) — L7 with WAF. **Front Door** (CloudFront + global LB) — global routing, CDN, WAF. | हिंदी: L4, L7 और ग्लोबल।
- **Azure DNS** (Route 53, no registrar) — public/private zones; Traffic Manager for DNS routing. | हिंदी: public/private zones host करता है।
- **VNet peering** — private link of VNets, non-transitive, create both directions. | हिंदी: दोनों तरफ बनाना पड़ता है।
- **VPN Gateway / ExpressRoute** (Site-to-Site VPN / Direct Connect) — encrypted tunnel over internet / private dedicated line. | हिंदी: VPN इंटरनेट पर, ExpressRoute निजी लाइन।
- **Private Endpoint / Service Endpoint** (PrivateLink / Gateway endpoint) — private IP for PaaS / free subnet-to-PaaS rule, no private IP. | हिंदी: Private Endpoint को private IP मिलता है।
- **DDoS Protection** (Shield) — for Azure public IPs. | हिंदी: public IPs के लिए Shield जैसा।

```bash
# Private endpoint for a storage account (note 216, trimmed)
az network private-endpoint create -g rg-demo -n pe-blob \
  --vnet-name vnet-prod --subnet pe-subnet \
  --private-connection-resource-id "$STORAGE_ID" \
  --group-id blob --connection-name conn-blob
az network private-dns zone create -g rg-demo -n privatelink.blob.core.windows.net
```

---

## 3. Databases (folder 12)

- **Azure SQL Database** — managed SQL Server in the cloud. RDS is one multi-engine service; Azure has one service per engine. | हिंदी: हर engine की अलग service।
- **Azure Database for PostgreSQL / MySQL** (RDS/Aurora) — managed with HA and PITR; for PostgreSQL use Flexible Server, the older Single Server is retired. | हिंदी: PostgreSQL में Single Server रिटायर, Flexible Server लें।
- **Cosmos DB** (DynamoDB) — global low-latency NoSQL billed in RU/s (approximate — check current docs); one engine, many APIs (NoSQL native, Mongo, Cassandra, Gremlin, Table). | हिंदी: ग्लोबल NoSQL, RU/s से बिल।
- **Consistency levels** — Strong, Bounded Staleness, Session, Consistent Prefix, Eventual; Session is the sane default. | हिंदी: ताज़गी और स्पीड का सौदा।
- **Partition key** — high cardinality, even distribution, used in filters; 429 = RU limit exceeded. | हिंदी: ऊँची cardinality वाली key चुनें।
- **Azure Cache for Redis** (ElastiCache) — sub-ms caching; Microsoft announced Azure Managed Redis as successor, check retirement dates. | हिंदी: सब-मिलीसेकंड कैश, successor की जाँच करें।
- **Synapse** (Redshift) — warehouse + lake SQL + Spark. **Data Factory** — ETL orchestration. **HDInsight** (EMR) — managed Hadoop/Spark. | हिंदी: वेयरहाउस, ETL, Hadoop।
- **Choosing** — start with Postgres, add specialised stores once a need is proven. | हिंदी: ज़रूरत साबित होने पर ही नया स्टोर।

```bash
# Cosmos DB account, database, container (note 221)
az cosmosdb create -n myapp-cosmos -g rg-app \
  --default-consistency-level Session \
  --locations regionName=centralindia failoverPriority=0 isZoneRedundant=False
az cosmosdb sql database create -a myapp-cosmos -g rg-app -n appdb
az cosmosdb sql container create -a myapp-cosmos -g rg-app -d appdb \
  -n orders --partition-key-path /userId --throughput 400
```

---

## 4. Storage (folder 13)

- **Blob Storage** (S3) — durable object storage; bucket = container (inside a storage account), presigned = SAS. | हिंदी: टिकाऊ ऑब्जेक्ट स्टोरेज, Azure का S3।
- **Blob tiers** — colder tier = cheaper storage, costlier access; Archive is offline (rehydrate takes hours); automate with lifecycle management policy. | हिंदी: ठंडा tier सस्ता स्टोरेज, महँगा एक्सेस।
- **Azure Files** (EFS) — managed SMB/NFS shares. **Queue Storage** (SQS-like) — cheap queue. **Table Storage** — cheap key-value NoSQL. | हिंदी: शेयर, क्यू और key-value।
- **ADLS Gen2** — Blob + real folders for analytics. | हिंदी: analytics के लिए असली फ़ोल्डर।
- **Storage account setup** — pick redundancy and security at creation. | हिंदी: बनाते समय redundancy सही चुनें।
- **SAS tokens** (presigned URL) — prefer user delegation SAS (signed by Entra, revocable); short expiry. | हिंदी: SAS = Azure का presigned URL।
- **Replication** — LRS (one datacenter), ZRS (across zones), GRS/GZRS (secondary region), RA-GRS adds read access to secondary. | हिंदी: कितनी विफलता झेलनी है, उसी से चुनें।
- **Azure CDN** — classic Azure CDN from Edgio is being retired for some SKUs; Front Door recommended for new builds (check dates). | हिंदी: नए काम के लिए Front Door।

```bash
# User delegation SAS (note 240)
az storage blob generate-sas --account-name myappstore --container-name uploads \
  --name photo.png --permissions r --expiry 2026-12-31T00:00Z \
  --https-only --auth-mode login --as-user --full-uri
```

---

## 5. Messaging (folder 14)

- **Service Bus** (SQS + SNS) — reliable queues and topics; sessions, transactions, duplicate detection, DLQ. | हिंदी: queue और pub/sub ब्रोकर।
- **Queues vs topics** — queues load-balance work; topics fan out. | हिंदी: Queue काम बाँटती है, Topic सबको भेजता है।
- **Event Hubs** (Kinesis / MSK) — high-throughput stream with Kafka endpoint; shard = partition. | हिंदी: बड़े पैमाने की इवेंट स्ट्रीम।
- **Event Grid** (EventBridge) — routes "something happened" events to handlers; bus = topic, rule = subscription. | हिंदी: इवेंट्स को सही handler तक।
- **Notification Hubs** — push to all mobile platforms. **SignalR Service** — offloads real-time connection scaling. | हिंदी: push और रीयल-टाइम।
- **Pattern rule** — queue, topic, event, stream, realtime: match service to pattern. | हिंदी: पैटर्न से सर्विस चुनें।

```javascript
// Service Bus send/receive (note 243), prefer Managed Identity in prod
const { ServiceBusClient } = require("@azure/service-bus");
async function main() {
  const client = new ServiceBusClient(process.env.SERVICEBUS_CONNECTION_STRING);
  const sender = client.createSender("orders");
  await sender.sendMessages({ body: { orderId: 42 }, messageId: "order-42" });
  const receiver = client.createReceiver("orders");
  const msgs = await receiver.receiveMessages(1, { maxWaitTimeInMs: 5000 });
  for (const m of msgs) {
    await receiver.completeMessage(m);
  }
  await client.close();
}
main().catch(console.error);
```

---

## 6. Security and monitoring (folder 15)

- **Defender for Cloud** (Security Hub) — scores and fixes posture. **Defender** plans (GuardDuty) detect live threats. **Sentinel** — cloud-native SIEM + SOAR. | हिंदी: स्थिति, हमले और SIEM।
- **Key Vault** (Secrets Manager + KMS) — audited safe for secrets, keys, certs; enable soft delete and purge protection. | हिंदी: secrets, keys और certs की तिजोरी।
- **Entra ID / Managed identities** (IAM role) — secretless auth for Azure resources. See `iam-cheatsheet.md`. | हिंदी: बिना सीक्रेट के लॉगिन।
- **Azure Monitor** (CloudWatch) — metrics, logs, alerts; action groups = notify targets. **Log Analytics** — KQL central log store. | हिंदी: मेट्रिक्स, लॉग्स, अलर्ट।
- **Application Insights** (X-Ray) — APM for traces and errors; workspace-based, classic is retired. | हिंदी: ऐप की परफ़ॉर्मेंस और एरर।
- **Activity Log** (CloudTrail) — who did what to which resource. **Diagnostic Settings** — pipe resource logs somewhere queryable. | हिंदी: किसने क्या बदला।
- **Advisor / Service Health** — free best-practice and savings tips / personalised outage feed. **Cost alerts + Pricing Calculator** — warn early / estimate before deploy. | हिंदी: डिप्लॉय से पहले खर्च का अंदाज़ा।

```bash
# Key Vault + RBAC for a managed identity (note 254)
az keyvault create -g rg-demo -n kv-demo-12345 -l centralindia --enable-rbac-authorization true
az keyvault secret set --vault-name kv-demo-12345 -n DB-PASSWORD --value 's3cr3t'
az role assignment create --assignee <managed-identity-object-id> \
  --role "Key Vault Secrets User" \
  --scope $(az keyvault show -n kv-demo-12345 --query id -o tsv)
```

---

## 7. Developer tools (folder 16)

- **Azure DevOps** — Boards, Repos, Pipelines, Artifacts in one suite; Azure Repos stays active in notes while CodeCommit is closed to new customers. | हिंदी: प्लानिंग से डिप्लॉय तक सब एक जगह।
- **Pipelines** — YAML (`azure-pipelines.yml`) build and release. **Boards** — backlog/sprints. **Artifacts** — private package registry. | हिंदी: YAML से ऑटोमैटिक बिल्ड।
- **DevOps vs GitHub Actions** — Actions for GitHub-centric teams, DevOps for full-suite needs. | हिंदी: GitHub में कोड हो तो Actions।
- **ARM / Bicep / Terraform** — ARM = JSON; Bicep compiles to ARM, Azure-only, no state; Terraform is multi-cloud with state. | हिंदी: Bicep पढ़ने में आसान।
- **SDKs** — typed clients, one passwordless auth chain (`DefaultAzureCredential`). | हिंदी: एक ही सुरक्षित लॉगिन से सारी सर्विस।
- **Deploy recipes** — Node on App Service; FastAPI needs a Gunicorn/Uvicorn startup command; AKS for containers at scale; React on Static Web Apps (CDN, built-in CI/CD, PR previews). | हिंदी: FastAPI के लिए स्टार्टअप कमांड ज़रूरी।
- **API Management** (API Gateway) — managed gateway with policies and portal. **App Insights for Node.js** — APM on Azure Monitor. | हिंदी: पॉलिसी और पोर्टल वाला गेटवे।

```bicep
// App Service plan + app with managed identity (note 276, trimmed)
param location string = resourceGroup().location
param appName string
resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: 'plan-${appName}'
  location: location
  kind: 'linux'
  sku: { name: 'B1' }
  properties: { reserved: true }
}
```

```yaml
# azure-pipelines.yml (note 271, trimmed)
trigger:
  branches:
    include: [main]
pool:
  vmImage: ubuntu-latest
steps:
  - task: NodeTool@0
    inputs:
      versionSpec: '20.x'
  - script: |
      npm ci
      npm test
    displayName: Install and test
```

---

## Quick reminders
- Retiring/closed in notes: Blueprints (deprecated), Spring Apps (retirement announced), classic Azure CDN SKUs (Edgio), Azure Cache for Redis (successor announced), PostgreSQL Single Server (retired), Load Balancer Basic SKU (retired). Verify in current docs.
- हिंदी: नया प्रोजेक्ट शुरू करने से पहले जाँचें कि सर्विस रिटायर तो नहीं हो रही।
