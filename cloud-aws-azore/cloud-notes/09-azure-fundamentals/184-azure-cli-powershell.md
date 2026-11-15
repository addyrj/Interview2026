# 184. Azure CLI + PowerShell
# AWS: AWS CLI + AWS Tools for PowerShell
# Azure: Azure CLI (az) + Azure PowerShell (Az module)
# हिंदी में: टर्मिनल से Azure चलाने के दो औज़ार - az और PowerShell

---

## 🔵 Simple Definition
`az` is a cross-platform CLI (Python-based) with verb-noun-less commands; Az PowerShell is a module with cmdlets like `New-AzResourceGroup`.
az कमांड-लाइन टूल है और PowerShell के Az cmdlets स्क्रिप्टिंग के लिए हैं; दोनों से Azure मैनेज होता है।

---

## 🔴 Why it Exists
Portal clicks are not repeatable. CLI/PowerShell make deployments scriptable, reviewable and CI-friendly.

---

## 🟢 How it Works
```
az login -> token cached in ~/.azure
az <group> <subgroup> <command> --args  -> ARM REST API
Output: -o json | table | tsv | yaml ; filter with --query (JMESPath)
```
Also available in Azure Cloud Shell (browser, already logged in).

---

## 💻 Code / Config Example
```bash
az login                                  # browser; use --use-device-code on a VPS
az account set --subscription "<sub-id>"
az group create -n rg-demo -l centralindia
az appservice plan create -g rg-demo -n plan-demo --sku B1 --is-linux
az webapp create -g rg-demo -p plan-demo -n my-unique-app-123 --runtime "NODE:20-lts"
# Query with JMESPath
az webapp list -g rg-demo --query "[].{name:name,state:state}" -o table
az group delete -n rg-demo --yes --no-wait
```
```powershell
Connect-AzAccount
New-AzResourceGroup -Name rg-demo -Location centralindia
Get-AzWebApp -ResourceGroupName rg-demo | Select Name, State
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| CLI | `aws` | `az` |
| PowerShell | AWS.Tools.* | Az module |
| Query | `--query` (JMESPath) | `--query` (JMESPath) |
| Login | `aws configure` / SSO | `az login` |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Running against the wrong subscription.
✅ Correct: `az account show` first, or pass `--subscription` explicitly.

❌ Mistake: Using `az login` with a user account in CI.
✅ Correct: OIDC (`azure/login`) or a managed identity (`az login --identity`).

---

## ⚫ Interview Q&A
Q1: [Easy] How do you log in on a headless server?
A1: `az login --use-device-code` or a service principal / managed identity.

Q2: [Medium] How to pick only names in table form?
A2: `--query "[].name" -o tsv` or a projection with `-o table`.

Q3: [Hard] CLI vs Bicep/Terraform?
A3: CLI is imperative and not idempotent by default for everything; Bicep/Terraform are declarative with state/what-if, better for infra; CLI suits glue scripts.

---

## ✅ Quick Checklist
□ Correct subscription set
□ `--query`/`-o` used for scripting
□ No credentials in scripts

---

## ⚡ 1-Line Summary
az and Az PowerShell are scriptable front doors to ARM. | az और PowerShell Azure को स्क्रिप्ट से चलाने के रास्ते हैं।

## ➡️ Next: Azure Cost Management
