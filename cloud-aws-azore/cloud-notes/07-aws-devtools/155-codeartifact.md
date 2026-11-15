# 155. CodeArtifact
# AWS: AWS CodeArtifact
# Azure: Azure Artifacts
# हिंदी में: कोडआर्टिफैक्ट - प्राइवेट npm/pip/Maven पैकेज रजिस्ट्री

---

## 🔵 Simple Definition
CodeArtifact is a managed package repository supporting npm, PyPI, Maven, NuGet and others. It can proxy public registries and host private packages.
हिंदी: कंपनी के अपने npm/pip पैकेज रखने और npmjs जैसे पब्लिक पैकेज को कैश करने की जगह।

## 🔴 Why it Exists
Avoid dependency outages and supply-chain surprises; share internal libraries privately.

## 🟢 How it Works
```
Domain
 |-- repo "internal" (upstream: "npm-store")
 |-- repo "npm-store" (external connection: npmjs)
npm install --> internal --> (miss) --> npm-store --> npmjs, then cached
```

## 💻 Code / Config Example
```bash
# AWS CLI v2: create domain + repos
aws codeartifact create-domain --domain mycorp
aws codeartifact create-repository --domain mycorp --repository npm-store
aws codeartifact associate-external-connection --domain mycorp \
  --repository npm-store --external-connection public:npmjs
aws codeartifact create-repository --domain mycorp --repository internal \
  --upstreams repositoryName=npm-store

# Point npm at it (token valid 12h by default)
aws codeartifact login --tool npm --domain mycorp --repository internal
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CodeArtifact | Azure Artifacts |
| Formats | npm, PyPI, Maven, NuGet, Swift, etc. | npm, NuGet, Maven, PyPI, Universal |
| Upstream proxy | Yes | Yes (upstream sources) |
| Auth | IAM auth token | PAT / Entra token |

## ⚠️ Common Mistakes
❌ Token expiry breaks CI. ✅ Run `aws codeartifact login` or get-authorization-token in each build.
❌ Publishing internal names that exist on npmjs (dependency confusion). ✅ Use scoped packages (@mycorp/x) and package origin controls.

## ⚫ Interview Q&A
Q1 [Easy]: What is a domain? A1: Grouping of repos sharing encryption and storage.
Q2 [Medium]: What are upstreams? A2: Repos queried in order when a package is missing locally.
Q3 [Hard]: Prevent dependency confusion? A3: Package origin controls blocking publish/upstream for internal package names.

## ✅ Quick Checklist
□ Scoped package names
□ CI fetches fresh token
□ Upstream proxy for public deps

## ⚡ 1-Line Summary
CodeArtifact is a private, caching package registry | कोडआर्टिफैक्ट आपकी प्राइवेट पैकेज रजिस्ट्री और कैश है।

## ➡️ Next: AWS CDK - Infra as Code
