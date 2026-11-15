# IAM Cheatsheet: AWS IAM + Azure RBAC / Entra ID
# हिंदी में: कौन (identity) क्या (action) किस पर (resource) कर सकता है, AWS और Azure दोनों में

> Source: notes 016-020, 147 (AWS), 162 (OIDC), 182-183, 260-261 (Azure), 296 (compare).
> Pricing remarks are "approximate — check current docs".

---

## 1. Big picture

```
AWS Principal (user/role/service) --request--> AWS API
   1 Authenticate (password+MFA, access key, role session token)
   2 Authorize:
        explicit Deny  -> DENIED (always wins)
        else Allow in (identity / resource policy) and not blocked
             by SCP / permission boundary / session policy -> ALLOWED
        else implicit deny
IAM is global (not regional) and free.

Azure: principal + role + scope  (additive, inherited down the hierarchy)
       Management Group > Subscription > Resource Group > Resource
```
- हिंदी: AWS में deny सबसे ऊपर और डिफ़ॉल्ट deny; Azure में अनुमतियाँ जुड़ती जाती हैं और नीचे तक लागू होती हैं।

---

## 2. Identities

| Concept | AWS | Azure |
|---------|-----|-------|
| Human identity | IAM user / Identity Center user | Entra user |
| Grouping | IAM group | Entra group |
| Workload identity | IAM role (instance profile, ECS task role, Lambda role, IRSA) | Managed Identity (system/user-assigned), service principal |
| Workforce SSO | IAM Identity Center | Entra ID |
| Customer identity | Cognito (per MAU) | Entra External ID (formerly Azure AD B2C) |
| Cross-account/tenant | AssumeRole | Guest users / Lighthouse / service principal |

- **Users** for people, **groups** to assign permissions once to many, **roles** for temporary workloads. | हिंदी: इंसान के लिए यूज़र, बाँटने को ग्रुप, ऐप्स के लिए रोल।
- **Root user (AWS)** — lock it away, work through an admin identity. | हिंदी: रूट को ताले में रखो।
- **Entra rename** — Azure AD is now Microsoft Entra ID.
- **App registration vs service principal** — registration = global app definition; service principal = its instance in a tenant, which receives permissions.

```bash
# Create group, user, attach managed policy (note 018)
aws iam create-group --group-name devs
aws iam create-user --user-name alice
aws iam add-user-to-group --group-name devs --user-name alice
aws iam attach-group-policy --group-name devs \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

---

## 3. AWS policies (JSON)

- Statement elements: Effect, Action, Resource, optional Principal and Condition.
- **Identity policy** attaches to who; **resource policy** attaches to the resource and names a Principal (enables cross-account).
- **Trust policy** = who can assume the role; **permission policy** = what the role can do.
- **Permission boundary / SCP** never grant; effective permissions are the intersection.
- हिंदी: Trust policy बताती है कौन role ले सकता है, permission policy बताती है role क्या कर सकता है।

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadWriteOneBucketPrefix",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-app-bucket/uploads/*"
    },
    {
      "Sid": "ListOnlyThatPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-app-bucket",
      "Condition": { "StringLike": { "s3:prefix": ["uploads/*"] } }
    },
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": ["arn:aws:s3:::my-app-bucket", "arn:aws:s3:::my-app-bucket/*"],
      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
    }
  ]
}
```

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ecs-tasks.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```
(The second block is a role trust policy for an ECS task role.)

```bash
# Who am I, and test a decision without running the action (note 017)
aws sts get-caller-identity
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/dev1 \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-app-bucket/file.txt
```

---

## 4. Guardrails: SCP vs Azure Policy

| Feature | AWS | Azure |
|---------|-----|-------|
| Tool | SCP | Azure Policy (deny), RBAC deny assignments |
| Scope | Root, OU, account | Management group, subscription, RG |
| Grants access? | No | No |
| Cost | Free | Free |

- SCPs do not affect the management account. SCP allows S3 but IAM has no allow: denied, both are required.
- Deny-list (FullAWSAccess + targeted denies) is easier; allow-list is stricter.
- Azure Policy controls resource properties; RBAC controls user actions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyOutsideAllowedRegions",
      "Effect": "Deny",
      "NotAction": ["iam:*", "organizations:*", "sts:*", "support:*", "cloudfront:*", "route53:*"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": { "aws:RequestedRegion": ["ap-south-1", "us-east-1"] }
      }
    },
    {
      "Sid": "ProtectCloudTrail",
      "Effect": "Deny",
      "Action": ["cloudtrail:StopLogging", "cloudtrail:DeleteTrail"],
      "Resource": "*"
    }
  ]
}
```
- हिंदी: SCP अकाउंट की अनुमतियों की छत है, वह खुद अनुमति नहीं देती।

---

## 5. Least privilege and best practices (note 020)

- Grant only the permissions needed; start narrow and expand using Access Analyzer findings. | हिंदी: कम परमिशन, MFA, कीज़ की जगह रोल।
- MFA for humans; roles for workloads; never embed access keys in code or Docker images.
- Exposed key: deactivate, check CloudTrail, rotate, remove from history, replace with role-based access.
- Find stale credentials with the credential report.
- Azure equivalents: Conditional Access (P1), Privileged Identity Management for just-in-time admin (P2), Access Reviews (check current docs for licensing).

```bash
aws iam generate-credential-report
aws iam get-credential-report --query Content --output text | base64 -d | head
```

---

## 6. CI/CD without stored keys: OIDC federation

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike": { "token.actions.githubusercontent.com:sub": "repo:my-org/my-api:ref:refs/heads/main" }
    }
  }]
}
```
```yaml
permissions:
  id-token: write
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: ap-south-1
```
- Check `aud` = sts.amazonaws.com and `sub` restricted to repo and ref (or environment). For prod, use a GitHub Environment with reviewers: `sub` = `repo:ORG/REPO:environment:production`.
- Azure side: federated credential on the app registration (subject = repo/branch/environment), login with `azure/login` using client-id, tenant-id, subscription-id.
- हिंदी: OIDC में छोटी अवधि की credentials मिलती हैं, कोई secret रखना या घुमाना नहीं पड़ता।

```bash
az ad app federated-credential create --id <app-object-id> --parameters '{
  "name":"gha-main","issuer":"https://token.actions.githubusercontent.com",
  "subject":"repo:myorg/myrepo:ref:refs/heads/main","audiences":["api://AzureADTokenExchange"]}'
```

---

## 7. Azure RBAC

- Role assignment = who + role + scope. Additive: Reader at subscription plus Contributor at one RG means Contributor in that RG, Reader elsewhere.
- **Owner** can also assign roles; **Contributor** manages resources but cannot grant access.
- **Control plane** (`Actions`) manages resources; **data plane** (`DataActions`) accesses content like blobs or secrets. Contributor does not grant blob data access.
- Deny assignments are mostly system-managed; use Policy for guardrails.
- हिंदी: RBAC = कौन + कौन-सा रोल + किस स्कोप पर।

```bash
az role assignment create \
  --assignee <sp-or-group-object-id> \
  --role "Contributor" \
  --resource-group rg-myapp-prod
```

```json
{
  "Name": "VM Operator",
  "IsCustom": true,
  "Description": "Start/stop/restart VMs",
  "Actions": [
    "Microsoft.Compute/virtualMachines/read",
    "Microsoft.Compute/virtualMachines/start/action",
    "Microsoft.Compute/virtualMachines/restart/action",
    "Microsoft.Compute/virtualMachines/deallocate/action"
  ],
  "NotActions": [],
  "AssignableScopes": ["/subscriptions/<subscription-id>"]
}
```

---

## 8. Managed identities (the Azure IAM role)

- Azure-managed Entra identity for a resource; tokens without secrets. AWS parallel: role attached to EC2/ECS/Lambda (STS temp credentials via IMDS).
- **System-assigned** = 1:1 with the resource, deleted with it. **User-assigned** = standalone, shareable, good for blue/green slots and pre-provisioned RBAC.
- 403 after role assignment? Propagation takes minutes and tokens are cached (up to ~24h); also check scope, data-plane vs control-plane role, target firewall.
- हिंदी: Managed Identity = बिना पासवर्ड वाला सुरक्षित लॉगिन।

```bash
az webapp identity assign -g rg-prod -n api-prod
PRINCIPAL=$(az webapp identity show -g rg-prod -n api-prod --query principalId -o tsv)
az role assignment create --assignee-object-id "$PRINCIPAL" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-prod/providers/Microsoft.Storage/storageAccounts/stprod001"
```
```javascript
// DefaultAzureCredential: managed identity in Azure, `az login` locally (note 261)
const { DefaultAzureCredential } = require("@azure/identity");
const { BlobServiceClient } = require("@azure/storage-blob");
const svc = new BlobServiceClient(
  "https://stprod001.blob.core.windows.net",
  new DefaultAzureCredential()
);
```

---

## 9. Entra ID: validate a JWT in Node (note 260)

```javascript
// npm i jose
const { createRemoteJWKSet, jwtVerify } = require("jose");
const tenant = process.env.TENANT_ID;
const jwks = createRemoteJWKSet(new URL(`https://login.microsoftonline.com/${tenant}/discovery/v2.0/keys`));
async function verify(token) {
  const { payload } = await jwtVerify(token, jwks, {
    issuer: `https://login.microsoftonline.com/${tenant}/v2.0`,
    audience: process.env.API_CLIENT_ID,
  });
  return payload;
}
module.exports = { verify };
```
- Secretless Node API: SPA uses auth code + PKCE; API validates JWT via JWKS; API reaches Azure resources via Managed Identity; CI deploys with federated OIDC.
- Entra pricing: Free tier; P1/P2 paid features (approximate — check current docs).

---

## 10. Debug "AccessDenied" checklist
- AWS ECS task reading S3: task role (not execution role), identity policy actions/ARNs, bucket policy, KMS key policy, SCPs/boundaries; use CloudTrail and the policy simulator.
- Azure: right scope, right plane (data vs control), propagation delay, resource firewall.
- हिंदी: पहले देखें कौन-सा रोल लग रहा है, फिर पॉलिसी, फिर SCP/Policy की रोक।
