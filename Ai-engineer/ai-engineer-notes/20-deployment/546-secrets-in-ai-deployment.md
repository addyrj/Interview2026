
---

# 546. Secrets in AI Deployment
# हिंदी में: AI Deployment में Secrets

---

## 🔵 Simple Definition (English)
Secrets are values that grant access or spend money: LLM API keys, database passwords, vector DB tokens, JWT signing keys. Secrets management means storing them in a dedicated secure place, giving each service only the ones it needs, injecting them at runtime, rotating them, and never leaking them into code, images, prompts or logs.

## 🔵 सरल परिभाषा (Hindi)
Secrets वो values हैं जिनसे access मिलता है या पैसे खर्च होते हैं: LLM API keys, database passwords, vector DB tokens, JWT signing keys। Secrets management का मतलब: उन्हें एक अलग सुरक्षित जगह रखना, हर service को सिर्फ ज़रूरी secrets देना, runtime पर inject करना, rotate करना, और code, images, prompts या logs में कभी leak न होने देना।

---

## 🔴 Problem it Solves
- An LLM API key is like a credit card: if leaked, strangers run up your bill (or abuse your account).
- Keys end up in git history, Docker layers, CI logs, screenshots and chat messages.
- A single shared key for everything means one leak is a total breach, and rotation is painful.
- Compliance requires access control and audit of who read which secret.

## 🔴 यह क्यों बना? (Hindi)
- LLM API key credit card जैसी है: leak हुई तो अजनबी आपका bill बढ़ा देते हैं (या account का दुरुपयोग करते हैं)।
- Keys git history, Docker layers, CI logs, screenshots और chat messages में पहुँच जाती हैं।
- सबके लिए एक shared key होने पर एक leak पूरा breach बन जाता है और rotation कठिन होता है।
- Compliance में access control और audit चाहिए कि किसने कौन सा secret पढ़ा।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Inventory: list every secret (LLM keys, DB password, vector DB token, JWT key)
Step 2 → Store in a secret manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault,
         HashiCorp Vault, or Kubernetes Secrets with encryption at rest)
Step 3 → Least privilege: each service identity (IAM role) can read only its own secrets
Step 4 → Inject at runtime: platform sets env vars or mounts files; code never contains them
Step 5 → Keep out of images, git (use .gitignore + secret scanning), prompts and logs
Step 6 → Separate keys per environment and per service; set provider spend limits on each key
Step 7 → Rotate on a schedule and immediately after any suspected leak; support two keys during rotation
Step 8 → Audit access, alert on unusual usage (spike in tokens, new IP), have a revoke runbook
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Inventory बनाओ: हर secret की list (LLM keys, DB password, vector DB token, JWT key)
Step 2 → Secret manager में रखो (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault,
         HashiCorp Vault, या rest पर encryption वाले Kubernetes Secrets)
Step 3 → Least privilege: हर service identity (IAM role) सिर्फ अपने secrets पढ़ सके
Step 4 → Runtime पर inject: platform env vars set करता है या files mount करता है; code में कभी नहीं
Step 5 → Images, git (.gitignore + secret scanning), prompts और logs से दूर रखो
Step 6 → हर environment और service की अलग keys; हर key पर provider का spend limit लगाओ
Step 7 → Schedule पर और शक होते ही तुरंत rotate करो; rotation के समय दो keys चलने दो
Step 8 → Access audit करो, असामान्य usage पर alert (tokens spike, नया IP), revoke runbook रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The API needs an LLM key, a Postgres password and a Qdrant token. In production they live in the cloud secret manager. The API's task role may read only those three; the ingestion worker may read only the LLM key and Qdrant token. A developer accidentally pastes the LLM key into a GitHub issue. The secret scanner alerts within minutes; the team revokes the key, issues a new one into the secret manager, and restarts the pods. Because each environment has its own key with a monthly spend cap, the blast radius is limited to staging.

**Zomato-style AI**: Separate keys per microservice mean the recommendation service's leak does not expose the support bot's key.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: API को LLM key, Postgres password और Qdrant token चाहिए। Production में ये cloud secret manager में हैं। API की task role सिर्फ यही तीन पढ़ सकती है; ingestion worker सिर्फ LLM key और Qdrant token। Developer गलती से LLM key को GitHub issue में paste कर देता है। Secret scanner मिनटों में alert देता है; team key revoke करती है, secret manager में नई key डालती है और pods restart करती है। हर environment की अलग key और monthly spend cap होने से नुकसान सिर्फ staging तक सीमित रहता है।

**Zomato-style AI**: हर microservice की अलग key होने से recommendation service की leak support bot की key को expose नहीं करती।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny secret scanner for files/strings (pure Python)
import re                                              # regex matching

# Illustrative patterns (real scanners such as gitleaks or trufflehog have many more)
PATTERNS: dict[str, re.Pattern[str]] = {
    "generic_api_key": re.compile(r"(?i)(api[_-]?key|secret|token)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    "sk_style_key": re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    "private_key": re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
}

def scan(text: str) -> list[str]:
    """Return names of patterns that match."""
    return [name for name, pat in PATTERNS.items() if pat.search(text)]

def redact(text: str) -> str:
    """Replace matches with [REDACTED] (use before logging)."""
    for pat in PATTERNS.values():
        text = pat.sub("[REDACTED]", text)             # mask each match
    return text

if __name__ == "__main__":
    sample = 'API_KEY = "abcd1234abcd1234abcd"\nprint("hi")'
    print(scan(sample))                                # ['generic_api_key']
    print(redact(sample))                              # key replaced
```

## 💻 Code Example — Advanced
```python
# Advanced: pluggable secret provider with cache + safe logging
# Real providers: boto3 (AWS Secrets Manager), google-cloud-secret-manager, azure-keyvault-secrets.
import asyncio                                         # async API
import logging                                         # logging
import os                                              # env var provider
import time                                            # TTL cache
from typing import Protocol

log = logging.getLogger("secrets")

class SecretNotFound(Exception):
    """Raised when a secret is missing."""

class SecretProvider(Protocol):
    async def get(self, name: str) -> str: ...         # any backend implements this

class EnvProvider:
    """Reads secrets from environment variables (platform-injected)."""
    async def get(self, name: str) -> str:
        value = os.environ.get(name, "")
        if not value:
            raise SecretNotFound(name)                 # name only, never the value
        return value

class FilesProvider:
    """Reads mounted secret files, e.g. /run/secrets/NAME (Docker/Kubernetes)."""
    def __init__(self, base: str = "/run/secrets") -> None:
        self.base = base
    async def get(self, name: str) -> str:
        try:
            with open(f"{self.base}/{name}", encoding="utf-8") as fh:
                return fh.read().strip()               # strip trailing newline
        except FileNotFoundError as exc:
            raise SecretNotFound(name) from exc

class CachedSecrets:
    """Cache secrets briefly so rotation is picked up without restart."""
    def __init__(self, providers: list[SecretProvider], ttl_s: float = 300.0) -> None:
        self.providers = providers                     # tried in order
        self.ttl_s = ttl_s
        self._cache: dict[str, tuple[float, str]] = {} # name -> (expiry, value)
        self._lock = asyncio.Lock()

    async def get(self, name: str) -> str:
        now = time.monotonic()
        hit = self._cache.get(name)
        if hit and hit[0] > now:
            return hit[1]                              # still fresh
        async with self._lock:                         # avoid thundering herd
            for provider in self.providers:
                try:
                    value = await provider.get(name)
                except SecretNotFound:
                    continue                           # try next provider
                self._cache[name] = (now + self.ttl_s, value)
                log.info("secret loaded name=%s", name)  # log the NAME only
                return value
        raise SecretNotFound(name)

async def main() -> None:
    os.environ["LLM_API_KEY"] = "demo-not-a-real-key"
    secrets = CachedSecrets([FilesProvider("/nonexistent"), EnvProvider()])
    key = await secrets.get("LLM_API_KEY")
    print("loaded, length:", len(key))                 # never print the value itself
    try:
        await secrets.get("MISSING")
    except SecretNotFound as exc:
        print("missing:", exc)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Load secrets once at startup (lifespan), keep them in `app.state` or a cached dependency, and never return them in responses. Use constant-time comparison when you verify incoming API keys.

```python
# FastAPI: secrets via lifespan + safe API-key check
import hmac
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import Depends, FastAPI, Header, HTTPException, Request

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    secrets = CachedSecrets([EnvProvider()])           # swap in a cloud provider in prod
    app.state.secrets = secrets
    app.state.service_key = await secrets.get("SERVICE_API_KEY")   # fail fast if missing
    yield

app = FastAPI(lifespan=lifespan)

async def require_key(request: Request, x_api_key: str = Header(default="")) -> None:
    expected: str = request.app.state.service_key
    if not hmac.compare_digest(x_api_key.encode(), expected.encode()):  # timing-safe
        raise HTTPException(status_code=401, detail="unauthorized")

@app.post("/classify", dependencies=[Depends(require_key)])
async def classify(q: str) -> dict[str, str]:
    return {"answer": "mock"}                          # LLM key is used server-side only
```
Never send LLM provider keys to browsers or mobile apps: call the LLM from your backend, and give clients your own short-lived tokens.

---

## 🔗 LangChain / LangGraph Connection
- Pass keys explicitly from your secret provider into the model constructor (`api_key=...`), or set the provider env var at process start from the secret manager.
- Use `SecretStr` types (LangChain integrations do) so keys do not appear in `repr` or logs.
- LangSmith traces can capture prompts and outputs: do not put secrets in prompts, and mask or disable tracing for sensitive chains.
- Tools given to agents should receive credentials from server-side config, not from the model's arguments.

```python
# LangChain: build the model with a key from the secret provider (illustrative)
# key = await secrets.get("LLM_API_KEY")
# llm = ChatOpenAI(model=settings.llm_model, api_key=key)       # any provider integration works similarly
# A tool that calls an internal API:
# @tool
# def get_duty(hs: str) -> str:
#     headers = {"Authorization": f"Bearer {TARIFF_SERVICE_TOKEN}"}   # from config, not from the LLM
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A key in code or in the Docker image
```dockerfile
# Wrong: stays in image layers and history forever
ENV LLM_API_KEY=sk-live-...
# Right: injected at runtime by the platform
# docker run -e LLM_API_KEY ...   or  secrets: in compose / Kubernetes Secret
```

❌ Mistake 2: Logging full requests or settings objects
```python
# Wrong: prints headers or config including keys
logger.info("config=%s headers=%s", settings.model_dump(), request.headers)
# Right: log names and counts, redact everything else
logger.info("loaded secret name=%s", "LLM_API_KEY")
```

❌ Mistake 3: Deleting the key from the repo and calling it done
✅ Correct: Anything committed is compromised. Revoke and rotate the key first; history cleanup comes second.

---

## 🧠 Tricky Interview Question

**Q**: "Your LLM bill jumps 20x overnight. No deploy happened and error rates are normal. What do you do and what would have prevented it?"

**Answer**: Likely a leaked or abused API key. Immediate steps: check the provider's usage dashboard by key and time, **revoke or rotate the key now** (stop the spend first, investigate after), issue a new key into the secret manager, restart or reload services, and find the leak source (public repo, CI logs, client-side code, a shared notebook). Prevention: keys only server-side, per-service and per-environment keys, provider spend caps and usage alerts, secret scanning in CI and pre-commit, short rotation periods, per-tenant rate limits in your own API, and anomaly alerts on tokens per minute.

---

## ⚫ Interview Questions + Answers

Q1: What is a secret manager?
A1: A service that stores secrets encrypted, controls who can read them with IAM, audits access, and supports rotation and versions. Examples: AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault.

Q2: Why are env vars not perfect for secrets?
A2: They can leak through crash dumps, process listings, `docker inspect`, debug pages and child processes. They are convenient and common, but a secret manager with runtime injection (or mounted files) is safer.

Q3: What is key rotation and why do it?
A3: Replacing a secret with a new one on a schedule or after exposure. It limits how long a stolen key remains useful. Support two valid keys during the switch to avoid downtime.

Q4: How do you stop secrets entering git?
A4: `.gitignore` for `.env`, pre-commit hooks and CI scanning (gitleaks, trufflehog, GitHub secret scanning), and developer education. If one slips in, revoke immediately.

Q5 (Hard): Design secret handling for a multi-tenant platform where tenants bring their own LLM API keys.
A5: Encrypt tenant keys with envelope encryption: a per-tenant data key protected by a master key in a KMS; store only ciphertext in your database. Decrypt in memory just-in-time for each call, never log or return it, and restrict the decrypt permission to the gateway service role. Offer key validation on submit, masked display (last 4 characters), rotation and delete endpoints, audit logs for each use, and per-tenant rate limits. Isolate by tenant so one bug cannot read another's key, and consider letting enterprise tenants use their own KMS key.

---

## 🔷 When to Use + When Not to Use
✅ Use a secret manager when:
- Production and staging, any real key or password
- Multiple services, teams or environments
- You need audit, rotation and access control

❌ Avoid when:
- Over-engineering a local toy project: a git-ignored `.env` is fine (still rotate if leaked)
- Putting non-secret config (model names, limits) in the vault: use normal env config

---

## 📊 Visual Diagram
```
 Developer laptop: .env (git-ignored)        CI: secret scanning blocks leaks
                                                   |
 Secret manager (encrypted, versioned, audited) <--+-- rotate / revoke
        |  IAM: api-role -> {LLM_KEY, DB_PASS, QDRANT_TOKEN}
        |       worker-role -> {LLM_KEY, QDRANT_TOKEN}
        v
 Platform injects at runtime (env var or mounted file)
        |
        v
 +------------------+     server-side only     +----------------+
 | FastAPI service  | -----------------------> | LLM provider   |
 | (key in memory)  |                          | spend cap/key  |
 +------------------+                          +----------------+
   Never: image layers, git, prompts, logs, browsers
```

---

## 💰 Cost Impact
- A leaked LLM key is a direct cost risk. Example (illustrative): an attacker running 10M tokens per hour at an illustrative $1 per 1M tokens burns about $240 per day, and much more with expensive models.
- Controls that protect budget: separate keys with provider spend limits, usage alerts, per-tenant rate limits and token budgets in your API, short key lifetimes.
- Secret managers have small fees (for example per secret per month and per API call; check your cloud's current pricing). Cache secrets with a TTL to avoid paying for a fetch on every request.
- Secrets themselves use no tokens, but never put them in prompts: that wastes tokens and leaks data to the provider and logs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Secret | Value granting access or spend | Access या खर्च देने वाली value |
| Secret manager | Secure store for secrets | Secrets का सुरक्षित भंडार |
| Rotation | Replacing a secret regularly | Secret को नियमित बदलना |
| Revoke | Disable a key immediately | Key को तुरंत बंद करना |
| Least privilege | Only the access that is needed | सिर्फ ज़रूरी access |
| Envelope encryption | Data key protected by a master key | Master key से सुरक्षित data key |
| Secret scanning | Finding leaked keys in code | Code में leak हुई keys खोजना |

---

## ⚡ 3-Line Summary
English: Store secrets in a secret manager, inject them at runtime, give each service only what it needs, and use separate keys per environment. Never put them in code, images, prompts or logs. Rotate regularly and revoke at once after any leak.
Hindi: Secrets को secret manager में रखो, runtime पर inject करो, हर service को सिर्फ ज़रूरी secrets दो और हर environment की अलग keys रखो। उन्हें code, images, prompts या logs में कभी मत डालो। नियमित rotate करो और leak होते ही तुरंत revoke करो।

---

## ➡️ Next Topic
**548. AWS ECS for AI Apps** — where these images, env vars and secrets are deployed on a managed container service.
