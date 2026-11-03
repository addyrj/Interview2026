
---

# 545. Environment Variables for AI
# हिंदी में: AI के लिए Environment Variables

---

## 🔵 Simple Definition (English)
Environment variables are named settings that live outside your code and are read at runtime (`os.environ`). For AI apps they hold model names, API endpoints, timeouts, token limits, feature flags and (carefully) credentials. The same code image then runs in dev, staging and production with different settings.

## 🔵 सरल परिभाषा (Hindi)
Environment variables वो named settings हैं जो आपके code के बाहर रहती हैं और runtime पर पढ़ी जाती हैं (`os.environ`)। AI apps में इनमें model names, API endpoints, timeouts, token limits, feature flags और (सावधानी से) credentials होते हैं। इससे वही code image dev, staging और production में अलग settings के साथ चलती है।

---

## 🔴 Problem it Solves
- Hardcoded model names, URLs and keys mean a code change and redeploy for every config tweak.
- Keys committed to git leak (public repos are scanned within minutes).
- Different environments (dev uses a cheap model, prod uses a better one) need different values.
- 12-factor apps keep config separate from code.

## 🔴 यह क्यों बना? (Hindi)
- Hardcoded model names, URLs और keys का मतलब हर config बदलाव पर code change और redeploy।
- Git में commit हुई keys leak होती हैं (public repos मिनटों में scan हो जाते हैं)।
- अलग environments को अलग values चाहिए (dev में सस्ता model, prod में बेहतर)।
- 12-factor apps config को code से अलग रखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide settings: LLM_MODEL, LLM_TIMEOUT_S, MAX_OUTPUT_TOKENS, QDRANT_URL, LOG_LEVEL, ...
Step 2 → Define them in one typed settings class (pydantic-settings) with defaults and validation
Step 3 → Local dev: values from a git-ignored .env file
Step 4 → Docker/Compose: `env_file` or `environment:` injects values into the container
Step 5 → Production: platform injects them (ECS task definition, Kubernetes ConfigMap for config,
         Secret/secret manager for credentials)
Step 6 → App starts, validates settings; if a required one is missing, fail fast with a clear error
Step 7 → Provide .env.example (fake values) so teammates know the required names
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Settings तय करो: LLM_MODEL, LLM_TIMEOUT_S, MAX_OUTPUT_TOKENS, QDRANT_URL, LOG_LEVEL, ...
Step 2 → सब एक typed settings class (pydantic-settings) में defaults और validation के साथ
Step 3 → Local dev: git-ignored .env file से values
Step 4 → Docker/Compose: `env_file` या `environment:` से container में values जाती हैं
Step 5 → Production: platform inject करता है (ECS task definition, config के लिए Kubernetes ConfigMap,
         credentials के लिए Secret/secret manager)
Step 6 → App start पर settings validate करता है; ज़रूरी वाली missing हो तो साफ error के साथ fail fast
Step 7 → .env.example (नकली values) दो ताकि teammates को ज़रूरी नाम पता हों
```

---

## 🟡 Real World Example
**Tariff Classification System**:
- Dev: `LLM_MODEL=small-cheap-model`, `MAX_OUTPUT_TOKENS=200`, `USE_MOCK_LLM=true` so tests cost nothing.
- Staging: real model, low rate limits.
- Prod: `LLM_MODEL=<better model>`, `LLM_TIMEOUT_S=20`, `DAILY_TOKEN_BUDGET=50000000`, `CACHE_TTL_S=86400`.
During a provider incident, ops flips `LLM_MODEL` to a fallback model by changing one variable and restarting, with no code change.

**Amazon-style AI**: `FEATURE_NEW_RANKER=false` lets the team enable a new reranker per environment.

## 🟡 Real Example Hindi mein
**Tariff Classification System**:
- Dev: `LLM_MODEL=small-cheap-model`, `MAX_OUTPUT_TOKENS=200`, `USE_MOCK_LLM=true` ताकि tests मुफ्त चलें।
- Staging: असली model, कम rate limits।
- Prod: `LLM_MODEL=<बेहतर model>`, `LLM_TIMEOUT_S=20`, `DAILY_TOKEN_BUDGET=50000000`, `CACHE_TTL_S=86400`।
Provider incident में ops एक variable बदलकर `LLM_MODEL` को fallback model पर कर देता है और restart, code change के बिना।

**Amazon-style AI**: `FEATURE_NEW_RANKER=false` से team हर environment में नया reranker चालू/बंद कर सकती है।

---

## 💻 Code Example — Basic
```python
# Basic: read env vars with defaults and validation (stdlib only)
import os                                              # environment access

def get_int(name: str, default: int) -> int:
    """Read an integer env var, with a clear error if it is not a number."""
    raw = os.environ.get(name)                         # None if missing
    if raw is None:
        return default                                 # use default
    try:
        return int(raw)                                # convert
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc

def require(name: str) -> str:
    """Read a required env var or fail fast."""
    value = os.environ.get(name, "").strip()           # empty counts as missing
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value

if __name__ == "__main__":
    os.environ["MAX_OUTPUT_TOKENS"] = "300"            # simulate config
    print(get_int("MAX_OUTPUT_TOKENS", 200))           # 300
    print(get_int("LLM_TIMEOUT_S", 20))                # 20 (default)
    try:
        require("LLM_API_KEY")                         # not set in this demo
    except RuntimeError as exc:
        print("error:", exc)                           # clear failure message
```

## 💻 Code Example — Advanced
```python
# Advanced: typed settings with pydantic-settings (pip install pydantic-settings)
from functools import lru_cache                        # cache settings object
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """All config in one validated place."""
    model_config = SettingsConfigDict(
        env_file=".env",                               # local dev file (git-ignored)
        env_prefix="TARIFF_",                          # TARIFF_LLM_MODEL, TARIFF_QDRANT_URL, ...
        extra="ignore",                                # ignore unrelated variables
    )

    env: str = "dev"                                   # dev | staging | prod
    llm_model: str = "small-model"                     # placeholder model id
    llm_api_key: SecretStr = SecretStr("")             # SecretStr hides value in repr/logs
    llm_timeout_s: float = Field(20.0, gt=0, le=120)   # bounded timeout
    max_output_tokens: int = Field(300, ge=1, le=4096) # cost guard
    daily_token_budget: int = Field(1_000_000, ge=0)
    qdrant_url: str = "http://qdrant:6333"
    use_mock_llm: bool = False

    @field_validator("env")
    @classmethod
    def valid_env(cls, v: str) -> str:
        if v not in {"dev", "staging", "prod"}:
            raise ValueError("env must be dev, staging or prod")
        return v

    def check_production(self) -> None:
        """Extra rules that only apply in prod."""
        if self.env == "prod":
            if self.use_mock_llm:
                raise ValueError("mock LLM must not be used in prod")
            if not self.llm_api_key.get_secret_value():
                raise ValueError("TARIFF_LLM_API_KEY is required in prod")

@lru_cache
def get_settings() -> Settings:
    s = Settings()                                     # reads env + .env, validates
    s.check_production()                               # fail fast at startup
    return s

if __name__ == "__main__":
    import os
    os.environ["TARIFF_MAX_OUTPUT_TOKENS"] = "250"
    s = get_settings()
    print(s.max_output_tokens, s.llm_api_key)          # 250 and ********** (masked)
```
Note: variable names follow `env_prefix` plus the field name (case-insensitive by default).

---

## 🟠 FastAPI Integration
Inject settings with `Depends(get_settings)`. Tests can override the dependency with `app.dependency_overrides`.

```python
# FastAPI: settings as a dependency
from fastapi import Depends, FastAPI

app = FastAPI()

@app.get("/limits")
async def limits(s: Settings = Depends(get_settings)) -> dict[str, object]:
    # Return only non-secret config, never the API key
    return {"env": s.env, "model": s.llm_model, "max_output_tokens": s.max_output_tokens}

@app.post("/classify")
async def classify(q: str, s: Settings = Depends(get_settings)) -> dict[str, str]:
    if s.use_mock_llm:                                 # free path for dev/tests
        return {"answer": "8507.60 (mock)"}
    # real call uses s.llm_model, s.llm_timeout_s, max_tokens=s.max_output_tokens
    return {"answer": "..."}

# In tests:
# app.dependency_overrides[get_settings] = lambda: Settings(use_mock_llm=True)
```

---

## 🔗 LangChain / LangGraph Connection
- LangChain integrations read standard variables on their own (for example provider API key variables such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
- LangSmith tracing is switched by environment variables (for example `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`; check current docs for exact names). Turn it off for sensitive environments.
- Build your LLM object from your own Settings, so model, timeout and max tokens are configurable.

```python
# LangChain model built from settings (illustrative; needs langchain-openai or another provider)
# from langchain_openai import ChatOpenAI
# s = get_settings()
# llm = ChatOpenAI(model=s.llm_model, timeout=s.llm_timeout_s, max_tokens=s.max_output_tokens,
#                  api_key=s.llm_api_key.get_secret_value())
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Committing `.env`
```python
# Wrong: .env in git history (rotating the key is now mandatory)
# Right: .gitignore contains ".env"; commit .env.example with fake values
```

❌ Mistake 2: Reading env vars everywhere with silent defaults
```python
# Wrong: typo gives a silent default, bug found in production
timeout = int(os.getenv("LLM_TIMEOUT", "20"))   # real name was LLM_TIMEOUT_S
# Right: one Settings class, validated at startup, fail fast
```

❌ Mistake 3: Treating env vars as a vault
✅ Correct: Env vars can leak via crash dumps, `docker inspect`, `/proc`, debug endpoints and logs. For production secrets prefer a secret manager (next topic), with the platform injecting values at runtime.

---

## 🧠 Tricky Interview Question

**Q**: "You changed `TARIFF_LLM_MODEL` in your deployment config but the running pods still use the old model. Why?"

**Answer**: Environment variables are read when the process starts, and your code caches settings (for example with `lru_cache` or module-level constants). Changing the config of a running container does nothing; you need a new rollout (restart) so processes start with the new environment. In Kubernetes, changing a ConfigMap does not restart pods automatically when it is used as env vars (mounted files can update, env vars cannot); trigger a rollout (`kubectl rollout restart`) or include a config hash annotation in the deployment. If you need live changes without restart, use a feature-flag or config service with polling instead.

---

## ⚫ Interview Questions + Answers

Q1: What is an environment variable?
A1: A key-value setting provided by the operating system or container to a process. In Python read it with `os.environ` or `os.getenv`.

Q2: Why not hardcode the API key?
A2: Code gets shared, committed and logged. A leaked key lets others spend your money. Keep keys outside code and rotate them if exposed.

Q3: What does `.env.example` do?
A3: It documents which variables the app needs, with fake values, and is safe to commit. New developers copy it to `.env`.

Q4: Why fail fast on missing config?
A4: A clear startup error is better than an obscure failure at the first request in production, at 2 am.

Q5 (Hard): Design config management for dev, staging and prod with secrets, feature flags and auditability.
A5: Non-secret config as typed settings from environment variables, versioned in git as per-environment manifests (ConfigMaps or task definitions) and applied by CI/CD. Secrets in a secret manager with IAM-scoped access, injected at runtime, rotated, and never logged. Feature flags in a flag service so they change without redeploy and have targeting and audit logs. Validate everything at startup (pydantic), expose a redacted `/config` for debugging, and log the config version or hash with each deploy so you can reproduce incidents.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Values change per environment (model, URLs, limits)
- You follow containers and 12-factor practices

❌ Avoid (use something else) when:
- Values are highly sensitive: use a secret manager
- Large or structured config (prompt templates, long lists): use files or a config service, versioned in git
- Settings that must change at runtime without restart: use feature flags

---

## 📊 Visual Diagram
```
 Dev laptop         Compose           Kubernetes / ECS
 .env file    --->  env_file     --->  ConfigMap (plain config)
 (git-ignored)      environment:       Secret / Secrets Manager (keys)
        \               |                      /
         \              v                     /
          +---->  process env (os.environ)  <+
                        |
                        v
              Settings (pydantic): validate, defaults, mask secrets
                        |
          +-------------+-------------+
          v                           v
     FastAPI Depends()          LangChain model (model, timeout, max_tokens)
```

---

## 💰 Cost Impact
- Env-based config lets you control cost without code changes: switch to a cheaper model, lower `MAX_OUTPUT_TOKENS`, shorten `LLM_TIMEOUT_S`, raise `CACHE_TTL_S`.
- Example (illustrative): cutting `MAX_OUTPUT_TOKENS` from 800 to 300 where answers rarely need more can cut output tokens by up to about 60% on long-tail responses, since output tokens usually cost more than input tokens.
- `USE_MOCK_LLM=true` in dev and CI avoids token spend in tests.
- Per-environment budgets (`DAILY_TOKEN_BUDGET`) limit damage from bugs in staging.
- Prices vary by provider; check current pricing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment variable | Setting passed to a process | Process को दी जाने वाली setting |
| `.env` | Local file of variables | Local variables की file |
| 12-factor app | Config in env, not code | Config environment में, code में नहीं |
| Settings class | Typed, validated config object | Typed और validated config object |
| Fail fast | Stop at startup if config is bad | खराब config पर शुरुआत में ही रुकना |
| ConfigMap | Kubernetes object for plain config | Kubernetes में सामान्य config का object |
| SecretStr | Type that hides secret values | Secret values छिपाने वाला type |

---

## ⚡ 3-Line Summary
English: Keep model names, URLs, limits and flags in environment variables, loaded into one typed, validated settings class. Fail fast on missing values and never commit `.env`. Use a secret manager for real credentials in production.
Hindi: Model names, URLs, limits और flags को environment variables में रखो और एक typed, validated settings class में load करो। Missing values पर fail fast करो और `.env` कभी commit मत करो। Production में असली credentials के लिए secret manager use करो।

---

## ➡️ Next Topic
**546. Secrets in AI Deployment** — how to store, inject and rotate API keys safely.
