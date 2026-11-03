
# 428. Langfuse Setup
# हिंदी में: Langfuse Setup

---

## 🔵 Simple Definition (English)
Setting up Langfuse means: pick cloud or self-hosted, create a project, get a public and secret API key, install the SDK, set environment variables, and send a first trace. After that every instrumented call shows up in the dashboard.

## 🔵 सरल परिभाषा (Hindi)
Langfuse setup का मतलब: cloud या self-hosted चुनो, project बनाओ, public और secret API key लो, SDK install करो, environment variables set करो और पहला trace भेजो। उसके बाद हर instrumented call dashboard में दिखता है।

---

## 🔴 Problem it Solves
Teams often add tracing late and wire keys inconsistently: keys hard-coded in source, dev and prod traces mixed, traces silently not sent because of a wrong host. A clean, repeatable setup avoids leaked secrets, mixed environments and "why is my dashboard empty" debugging.

## 🔴 यह क्यों बना? (Hindi)
Teams tracing देर से जोड़ती हैं और keys अलग-अलग तरह से लगाती हैं: source में hard-coded keys, dev और prod traces मिले हुए, ग़लत host की वजह से traces चुपचाप नहीं जाते। साफ़ और repeatable setup से leaked secrets, mixed environments और "dashboard खाली क्यों है" वाली debugging बचती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose: Langfuse Cloud (sign up) or self-host (Docker Compose / Kubernetes per official docs)
Step 2 → Create an organization and a project (one project per environment is a good habit)
Step 3 → Project settings -> create API keys: public key (pk-lf-...) and secret key (sk-lf-...)
Step 4 → pip install langfuse
Step 5 → Set env vars: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST (base URL of your server/region)
Step 6 → Verify with auth_check(), then send a first trace using @observe
Step 7 → Open the UI, confirm the trace, add tags/user ids, then add flush on shutdown
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → चुनो: Langfuse Cloud (sign up) या self-host (official docs के अनुसार Docker Compose / Kubernetes)
Step 2 → Organization और project बनाओ (हर environment के लिए अलग project अच्छा रहता है)
Step 3 → Project settings -> API keys बनाओ: public key (pk-lf-...) और secret key (sk-lf-...)
Step 4 → pip install langfuse
Step 5 → Env vars set करो: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
Step 6 → auth_check() से verify करो, फिर @observe से पहला trace भेजो
Step 7 → UI में trace देखो, tags/user ids जोड़ो और shutdown पर flush जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three projects: `tariff-dev`, `tariff-staging`, `tariff-prod`, each with its own key pair stored in a secret manager (not in git). The deploy pipeline injects the right keys per environment. The first smoke test sends a trace named `startup-check` so the team knows tracing works before real traffic.

**Zomato AI**: The ordering-assistant service and the review-summary service use separate projects so cost and error dashboards stay clean.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन projects: `tariff-dev`, `tariff-staging`, `tariff-prod`, हर एक की अपनी key pair secret manager में (git में नहीं)। Deploy pipeline हर environment के लिए सही keys inject करती है। पहला smoke test `startup-check` नाम का trace भेजता है ताकि असली traffic से पहले पता चले कि tracing चल रहा है।

**Zomato AI**: Ordering-assistant और review-summary services अलग projects use करती हैं ताकि cost और error dashboards साफ़ रहें।

---

## 💻 Code Example — Basic
```python
# Pure-Python config check: verify Langfuse env vars exist before starting the app
import os  # read environment variables
from typing import Optional  # optional type hint

REQUIRED = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST")  # needed settings


def missing_vars() -> list[str]:
    """Return the names of required variables that are not set."""
    return [name for name in REQUIRED if not os.getenv(name)]  # collect missing ones


def key_looks_valid(public_key: Optional[str]) -> bool:
    """Public keys normally start with 'pk-lf-'."""
    return bool(public_key) and public_key.startswith("pk-lf-")  # simple format check


if __name__ == "__main__":
    gaps = missing_vars()  # check settings
    if gaps:
        print("Missing:", ", ".join(gaps))  # tell the user what to set
    else:
        print("Config present. Public key format ok:", key_looks_valid(os.getenv("LANGFUSE_PUBLIC_KEY")))  # report
```

## 💻 Code Example — Advanced
```python
# Production setup: verify credentials at startup, trace a smoke test, flush on shutdown (SDK v3 style; check your version)
import asyncio  # async usage
import logging  # logging
import os  # env access

from langfuse import Langfuse, observe  # client + decorator

logger = logging.getLogger("tariff.setup")  # logger


def init_langfuse() -> Langfuse:
    """Create a client and verify credentials; fail fast with a clear message."""
    for name in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"):  # required keys
        if not os.getenv(name):  # missing
            raise RuntimeError(f"{name} is not set")  # stop early
    client = Langfuse(host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"))  # explicit host
    try:
        ok = client.auth_check()  # network call that validates keys
    except Exception as exc:  # network or auth error
        logger.error("Langfuse unreachable: %s", exc)  # log
        raise  # propagate
    if not ok:  # credentials rejected
        raise RuntimeError("Langfuse credentials rejected")  # fail
    return client  # ready


@observe(name="startup-check")  # first trace
def smoke_test() -> str:
    return "ok"  # trivial body


async def startup() -> None:
    """Async startup hook for a web service."""
    client = await asyncio.to_thread(init_langfuse)  # blocking auth in thread
    await asyncio.to_thread(smoke_test)  # emit one trace
    await asyncio.to_thread(client.flush)  # make sure it is sent
```
Token usage: setup itself spends no tokens. The first real LLM call will then report input/output tokens in the trace.

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager  # lifespan helper
from fastapi import FastAPI  # web framework
from langfuse import get_client  # shared client (v3)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await startup()  # run init + smoke test (from the advanced example)
    yield  # app serves requests here
    get_client().flush()  # send pending traces on shutdown


app = FastAPI(lifespan=lifespan)  # attach lifespan


@app.get("/health/tracing")
async def tracing_health() -> dict:
    try:
        ok = get_client().auth_check()  # quick credentials check
    except Exception:  # unreachable or invalid
        ok = False  # report unhealthy
    return {"langfuse": "ok" if ok else "down"}  # health payload
```

---

## 🔗 LangChain / LangGraph Connection
After setup, pass the Langfuse handler as a callback; no change to chain code is needed.

```python
from langfuse.langchain import CallbackHandler  # v3 import path
from langchain_openai import ChatOpenAI  # LLM wrapper

handler = CallbackHandler()  # picks up keys from env
chain_llm = ChatOpenAI(model="gpt-4o-mini")  # model
chain_llm.invoke("Hello", config={"callbacks": [handler]})  # first LangChain trace
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hard-coding keys in source code
✅ Correct: Environment variables or a secret manager.
```python
# Wrong
Langfuse(public_key="pk-lf-abc", secret_key="sk-lf-xyz")
# Right
Langfuse()  # reads LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST from env
```

❌ Mistake 2: Wrong host/region so traces go nowhere
✅ Correct: Set LANGFUSE_HOST to the URL of the region or server where the project was created, then run auth_check().
```python
# Wrong: project created in another region, host left as default -> auth fails
# Right: LANGFUSE_HOST=<your project's base URL>; assert client.auth_check()
```

---

## 🧠 Tricky Interview Question
**Q**: "Tracing works locally but no traces appear from your short-lived Cloud Run job. Why?"

**Answer**: The SDK sends events in a background batch. If the process exits before the batch is sent, events are lost. Call `flush()` (or `shutdown()`) before exit, and keep a short flush interval for serverless. Also verify the env vars exist in the deployed environment and the container has outbound network access to the Langfuse host.

---

## ⚫ Interview Questions + Answers

Q1: What credentials does the Langfuse SDK need?
A1: A public key, a secret key and the host URL of your Langfuse instance.

Q2: How do you verify the setup?
A2: Call `auth_check()`, send a smoke-test trace, and confirm it in the UI.

Q3: Why separate projects per environment?
A3: Keeps dev noise out of prod dashboards, allows different retention and access control, and limits blast radius of leaked keys.

Q4: What does `flush()` do?
A4: Forces the SDK to send queued events immediately; essential for scripts and serverless.

Q5: How would you roll out Langfuse with zero risk to latency?
A5: Rely on async batching, set short timeouts, wrap tracing so failures are swallowed and logged, sample high-volume endpoints, and load-test before enabling in prod. Treat tracing as best effort: the request must succeed even if Langfuse is down.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You are moving from prints and logs to real LLM observability
- You need an environment-separated, repeatable setup

❌ Avoid when:
- You only run a one-off notebook (simple logging may be enough)
- Policy forbids any external trace export and you cannot self-host

---

## 📊 Visual Diagram
```
 1. Sign up / self-host
 2. Create project  --> keys: pk-lf-... , sk-lf-...
 3. export LANGFUSE_PUBLIC_KEY / SECRET_KEY / HOST
 4. pip install langfuse
 5. auth_check()  --> True
 6. @observe function runs  --> trace in UI
 7. flush() on shutdown
```

---

## 💰 Cost Impact
Setup adds no LLM tokens. Cloud has free and paid tiers (check current pricing); self-hosting costs servers and maintenance. Once live, per-trace cost and token views help you cut spend. Optimise tracing volume with sampling and by truncating large inputs (full 50-page documents inside every trace increase storage cost).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Public key | Identifies the project | Project की पहचान |
| Secret key | Authenticates the SDK | SDK का authentication |
| Host | URL of Langfuse server | Server का URL |
| auth_check | Validate credentials | Credentials जाँचना |
| Flush | Send queued events | Queue के events भेजना |
| Project | Container for traces | Traces का container |
| Environment | dev / staging / prod | dev / staging / prod |

---

## ⚡ 3-Line Summary
English: Create a project, get public/secret keys, install the SDK and set env vars. Verify with auth_check and a smoke-test trace. Flush on shutdown and keep one project per environment.
Hindi: Project बनाओ, public/secret keys लो, SDK install करो और env vars set करो। auth_check और smoke-test trace से verify करो। Shutdown पर flush करो और हर environment के लिए अलग project रखो।

---

## ➡️ Next Topic
**429. Langfuse Tracing** — nested spans, generations, user and session tracking in depth.
