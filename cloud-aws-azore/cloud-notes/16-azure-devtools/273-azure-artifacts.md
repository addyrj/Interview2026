---

# 273. AZURE ARTIFACTS
# AWS: CodeArtifact
# Azure: Azure Artifacts
# हिंदी में: एज़्योर आर्टिफैक्ट्स

---

## 🔵 Simple Definition (2 lines)
Azure Artifacts is a private package registry (feeds) for npm, PyPI (Python), NuGet, Maven and Universal packages, with upstream proxying of public registries.
हिंदी: Artifacts आपके प्राइवेट पैकेज (npm, pip आदि) स्टोर करने वाला रजिस्ट्री है।

---

## 🔴 Why it Exists (2 lines)
Share internal libraries safely and protect builds from public registry outages or malicious packages by caching upstream.

---

## 🟢 How it Works
```
Feed (org or project scoped)
  ├─ your published packages  (npm publish / twine upload)
  └─ upstream sources: npmjs, PyPI -> saved copy on first use
Developers/pipelines pull only from the feed (.npmrc / pip index-url)
Permissions: Reader | Collaborator | Contributor | Owner
```

---

## 💻 Code / Config Example
```ini
# .npmrc  (project root)
registry=https://pkgs.dev.azure.com/acme/shop-api/_packaging/shop-feed/npm/registry/
always-auth=true
```
```yaml
# In a pipeline: authenticate and publish an npm package
steps:
  - task: npmAuthenticate@0
    inputs:
      workingFile: .npmrc
  - script: npm ci && npm publish
```
```bash
# Python: publish with twine (after pipx/pip install twine)
python -m build
twine upload --repository-url https://pkgs.dev.azure.com/acme/shop-api/_packaging/shop-feed/pypi/upload/ dist/*
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CodeArtifact | Artifacts |
| Formats | npm, PyPI, Maven, NuGet, others | npm, PyPI, NuGet, Maven, Cargo, Universal |
| Upstream | External connections | Upstream sources |
| Pricing | Storage + requests | Some free storage then per GB (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Developers also pulling straight from public registry.
✅ Correct: Only the feed in .npmrc/pip config; upstream through feed.

❌ Mistake: Using personal PAT in CI.
✅ Correct: Use the pipeline's build identity with Feed access.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What are feeds?
A1: Containers for packages with permissions and upstream settings.

Q2: [Medium] Why upstream sources?
A2: Cache public packages so builds survive outages and you control what versions enter.

Q3: [Hard] How to prevent dependency confusion?
A3: Use scoped npm packages, one feed as the sole registry, and upstream behavior that blocks public versions of internal names.

---

## ✅ Quick Checklist
□ One feed per team/product
□ Pipeline identity has Contributor on feed
□ Retention policy for old versions

---

## ⚡ 1-Line Summary
Artifacts = private package registry with public cache | Artifacts = आपकी प्राइवेट पैकेज लाइब्रेरी।

## ➡️ Next: Azure DevOps vs GitHub Actions

---
