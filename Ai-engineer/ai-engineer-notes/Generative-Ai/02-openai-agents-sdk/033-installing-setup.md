---

# 33. Installing + Setup
# हिंदी में: Install और Setup
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13.3, fastapi 0.163.0, pydantic 2.14.3). Both code examples were run offline with `agents.testing.ScriptedModel` (no API key). Real model calls are not run, they need `OPENAI_API_KEY`.

---

## 🔵 Simple Definition (2-3 lines)
Setup means installing the package (`pip install openai-agents`), importing it as `agents`, giving it a key (`OPENAI_API_KEY` env var or `set_default_openai_key`) and checking it works with a tiny smoke test. Do this inside a virtual environment with the version pinned.

## 🔵 सरल परिभाषा (Hindi)
Setup का मतलब है package install करना (`pip install openai-agents`), उसे `agents` नाम से import करना, key देना (`OPENAI_API_KEY` env var या `set_default_openai_key`) और एक छोटे smoke test से जाँचना कि सब चल रहा है। यह सब virtual environment में करें और version pin करें।

---

## 🔴 Problem it Solves
Most "the SDK does not work" tickets are setup bugs: wrong package name (`openai_agents` vs `openai-agents`), old Python, key missing in the server but present on a laptop, tracing trying to upload with no key, or an unpinned upgrade that changes behaviour. A repeatable setup with a smoke test and fail-fast config removes these.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर "SDK नहीं चल रहा" की शिकायतें setup की गलतियाँ होती हैं: गलत package नाम (`openai_agents` बनाम `openai-agents`), पुराना Python, laptop पर key है पर server पर नहीं, key न होने पर tracing upload की कोशिश करना, या बिना pin किए upgrade से behaviour बदल जाना। दोहराने योग्य setup, smoke test और fail-fast config इन्हें खत्म करते हैं।

---

## 🟢 How it Works

```
Step 1 -> python -m venv .venv && source .venv/bin/activate     (isolated env, Python 3.10+)
Step 2 -> pip install openai-agents                              (pip name has a hyphen)
Step 3 -> pip freeze > requirements.txt  (pin: openai-agents==0.24.0)
Step 4 -> export OPENAI_API_KEY=...      (or set_default_openai_key(key) in code)
Step 5 -> import agents                  (import name is "agents")
Step 6 -> smoke test: Agent + Runner with a scripted model (no key needed)
Step 7 -> FastAPI lifespan: configure once at startup, fail fast, expose /health
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> python -m venv .venv && source .venv/bin/activate     (अलग env, Python 3.10+)
Step 2 -> pip install openai-agents                              (pip नाम में hyphen है)
Step 3 -> pip freeze > requirements.txt  (pin: openai-agents==0.24.0)
Step 4 -> export OPENAI_API_KEY=...      (या code में set_default_openai_key(key))
Step 5 -> import agents                  (import नाम "agents" है)
Step 6 -> smoke test: scripted model के साथ Agent + Runner (key नहीं चाहिए)
Step 7 -> FastAPI lifespan: startup पर एक बार configure, fail fast, /health दें
```

**Verified facts (0.24.0):**
- Package metadata says `Requires-Python: >=3.10`. We ran 3.13.3.
- Optional extras exist, for example `openai-agents[voice]`, `[litellm]`, `[redis]`, `[sqlalchemy]`, `[realtime]`, `[viz]` (check `pip show` / package metadata for the full list).
- Config helpers confirmed in the installed package: `set_default_openai_key(key, use_for_tracing=True)`, `set_default_openai_client(client, use_for_tracing=True)`, `set_default_openai_api("chat_completions" | "responses")`, `set_tracing_disabled(bool)`, `set_tracing_export_api_key(str)`, `enable_verbose_stdout_logging()`.
- Creating `Agent(name=...)` does NOT need a key. The error appears only when a run needs the model: `OpenAIError: Missing credentials ...`. Without a key the SDK also logs `OPENAI_API_KEY is not set, skipping trace export`.

**Connect to what you know:** it is like `langchain-openai` reading `OPENAI_API_KEY` from env. Use the same secret manager (AWS Secrets Manager, GCP Secret Manager, Vault) you already use for FastAPI services, never commit the key.

---

## 🟡 Real World Example
**Tariff Agent service.** The customs portal team deploys the Tariff Agent in a container. The Dockerfile pins `openai-agents==0.24.0`, the key arrives from the secret manager as an env var, a lifespan hook builds the agent once, `/health` tells Kubernetes the app is ready, and a CI smoke test with a scripted model runs on every pull request without spending tokens.

**Research Agent / Customer Support:** same setup, only different instructions and tools.

## 🟡 Real Example Hindi mein
**Tariff Agent service.** Customs portal team Tariff Agent को container में deploy करती है। Dockerfile में `openai-agents==0.24.0` pin है, key secret manager से env var बनकर आती है, lifespan hook agent एक बार बनाता है, `/health` Kubernetes को बताता है कि app तैयार है, और हर pull request पर scripted model वाला CI smoke test बिना token खर्च किए चलता है।

**Research Agent / Customer Support:** setup वही, बस instructions और tools अलग।

---

## 💻 Code Example — Basic
Checks Python, package version, key presence (never prints the key) and runs a smoke test. Runs offline.

```python
# Basic: verify the OpenAI Agents SDK install and read config safely (runs offline)
import os                                                # read environment variables
import sys                                               # Python version check
from importlib.metadata import version, PackageNotFoundError  # installed package version

import agents                                            # the import name is "agents", not "openai_agents"
from agents import Agent, Runner, set_tracing_disabled   # core pieces we will smoke-test
from agents.testing import ScriptedModel, assistant_message  # offline fake model for the smoke test

def check_install() -> dict[str, str]:                   # collect facts about this environment
    try:
        sdk_version: str = version("openai-agents")      # the pip name has a hyphen
    except PackageNotFoundError:                         # package missing -> clear message
        raise SystemExit("run: pip install openai-agents")
    return {
        "python": sys.version.split()[0],                # SDK needs Python 3.10+
        "openai-agents": sdk_version,                    # pinned in requirements.txt in production
        "OPENAI_API_KEY": "set" if os.environ.get("OPENAI_API_KEY") else "missing",  # never print the key itself
    }

def smoke_test() -> str:                                 # prove Agent + Runner work end to end
    set_tracing_disabled(True)                           # no key needed for this offline test
    model = ScriptedModel([[assistant_message("pong")]])  # one scripted turn
    agent = Agent(name="Ping", instructions="Reply pong.", model=model)  # smallest possible agent
    result = Runner.run_sync(agent, "ping")              # blocking call is fine in a plain script
    return str(result.final_output)                      # "pong"

if __name__ == "__main__":
    for key, value in check_install().items():           # print the environment report
        print(f"{key:15} {value}")
    print("smoke test:", smoke_test())                   # pong -> SDK installed correctly
    print("exports Agent:", hasattr(agents, "Agent"))    # True
```

## 💻 Code Example — Advanced
FastAPI lifespan configures the SDK once, supports an app-specific secret name, a tracing switch, a configurable model name, fails fast with 503 when credentials are missing, and exposes `/health`. Runs offline via `TestClient`. Real model name placeholder `<your model name>` is not run, it needs a key.

```python
# Advanced: FastAPI startup that configures the SDK from env and fails fast (runs offline via TestClient)
import os                                                # environment config
from contextlib import asynccontextmanager               # lifespan helper
from typing import AsyncIterator                         # type of the lifespan generator

from fastapi import FastAPI, HTTPException, Request      # web framework
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # response schema
from openai import OpenAIError                           # raised when credentials are missing
from agents import (Agent, Runner, set_default_openai_key,
                    set_tracing_disabled, AgentsException)  # SDK config helpers
from agents.testing import ScriptedModel, assistant_message  # offline model for the demo

class Health(BaseModel):                                 # /health response
    sdk_ready: bool
    model: str
    key_source: str                                      # where the key came from, never the key

def make_model(name: str):                               # real model name in prod, scripted fake in tests
    if os.environ.get("USE_FAKE_MODEL") == "1":          # test switch
        return ScriptedModel([[assistant_message("ok")]] * 5)
    return name                                          # a plain string is resolved by the SDK default provider

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]: # runs once at startup/shutdown
    key = os.environ.get("MY_APP_OPENAI_KEY")            # app-specific secret name (from a secret manager)
    if key:
        set_default_openai_key(key, use_for_tracing=True)  # SDK-wide default key, also used for traces
        app.state.key_source = "MY_APP_OPENAI_KEY"
    else:
        app.state.key_source = "OPENAI_API_KEY env (SDK default)"  # SDK reads this itself
    if os.environ.get("DISABLE_TRACING") == "1":         # compliance switch
        set_tracing_disabled(True)
    app.state.model_name = os.environ.get("AGENT_MODEL", "<your model name>")  # config, not code
    app.state.agent = Agent(name="Tariff Agent", instructions="Be brief.",
                            model=make_model(app.state.model_name))
    yield                                                # app serves requests here

app = FastAPI(lifespan=lifespan)                         # attach lifespan

@app.get("/health", response_model=Health)               # readiness probe
async def health(request: Request) -> Health:
    return Health(sdk_ready=True, model=request.app.state.model_name,
                  key_source=request.app.state.key_source)

@app.get("/ask")                                         # one agent run
async def ask(request: Request, q: str) -> dict[str, str]:
    try:
        r = await Runner.run(request.app.state.agent, q, max_turns=3)  # cap loop cost
    except OpenAIError as exc:                           # missing/invalid credentials
        raise HTTPException(503, f"LLM not configured: {type(exc).__name__}")
    except AgentsException as exc:                       # any SDK failure
        raise HTTPException(502, type(exc).__name__)
    return {"answer": str(r.final_output)}

if __name__ == "__main__":
    os.environ["DISABLE_TRACING"] = "1"                  # no key in this demo
    os.environ.pop("OPENAI_API_KEY", None)               # simulate a missing key
    with TestClient(app) as c:                           # "with" runs the lifespan
        print(c.get("/health").json())                   # readiness JSON
        print(c.get("/ask", params={"q": "hi"}).status_code, c.get("/ask", params={"q": "hi"}).json())  # 503 no key
    os.environ["USE_FAKE_MODEL"] = "1"                   # now use the scripted model
    with TestClient(app) as c:
        print(c.get("/ask", params={"q": "hi"}).json())  # {'answer': 'ok'}
```

Terminal commands (not Python, run in your shell):

```bash
python -m venv .venv                 # create isolated environment
source .venv/bin/activate            # activate it (Windows: .venv\Scripts\activate)
pip install openai-agents            # install the SDK
pip show openai-agents               # confirm version
export OPENAI_API_KEY="..."          # key from your secret manager, never commit it
python n33_0.py                      # smoke test from the basic example
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| pip package | `langgraph` (+ `langchain-openai` for models) | `crewai` | `openai-agents` | `autogen-agentchat` + `autogen-ext[openai]` |
| Import name | `langgraph` | `crewai` | `agents` | `autogen_agentchat` |
| Install weight | Medium (langchain-core dependency) | Heavy (many dependencies) | Light | Medium (split into packages) |
| Key config | Model object reads env | Env vars / LLM object | env var or `set_default_openai_key` | Model client argument |
| Tracing setup | LangSmith env vars | Optional integrations | On by default, needs key to export | OpenTelemetry opt-in |
| Offline test model | Fake chat models | Mock LLM | `ScriptedModel` / custom `Model` | `ReplayChatCompletionClient` |

---

## ⚠️ Common Mistakes
❌ Mistake 1: `pip install openai_agents` or `import openai_agents`.
✅ Correct: `pip install openai-agents`, then `import agents`.

❌ Mistake 2: Hard-coding the key in source or committing `.env`.
✅ Correct: Env var or secret manager; use `set_default_openai_key` only with a value read from the secret store.

❌ Mistake 3: Not pinning the version (SDK changes fast).
✅ Correct: `openai-agents==0.24.0` (or a tested range) in `requirements.txt`, upgrade deliberately with a test run.

❌ Mistake 4: Leaving tracing on in an environment without a key or with data you cannot export.
✅ Correct: `set_tracing_disabled(True)` or configure `set_tracing_export_api_key` / a custom processor.

❌ Mistake 5: Discovering a missing key on the first user request.
✅ Correct: Validate config in the FastAPI lifespan and return 503 with a clear message.

---

## 🧠 Tricky Interview Question
Your agent works on your laptop but every request returns a 500 in staging, and logs say `OPENAI_API_KEY is not set, skipping trace export`. Where do you look?

**Answer:** That log line is only the tracing warning, it is not the crash. First check the real exception: with no key a run raises `openai.OpenAIError: Missing credentials`. Likely causes: the secret is not mounted as an env var in the container, the app reads a different variable name than the platform provides, or the key is set after the process imported and built the client. Fix: read the secret in the lifespan, call `set_default_openai_key` (or pass a client with `set_default_openai_client`), return 503 from a readiness check instead of 500, and add a CI smoke test with `ScriptedModel` so install problems are caught separately from credential problems.

---

## ⚫ Interview Questions + Answers

**Q1:** What is the pip name and the import name of the OpenAI Agents SDK?

**A1:** `pip install openai-agents`, `import agents`.

**Q2:** How do you give the SDK an API key?

**A2:** Set `OPENAI_API_KEY` in the environment (default), or call `set_default_openai_key(key)`, or pass your own `AsyncOpenAI` client via `set_default_openai_client`.

**Q3:** Does creating an `Agent` need a key?

**A3:** No. We verified `Agent(name="x")` works without a key. The failure happens at `Runner.run` when the model is called.

**Q4:** How do you test installation in CI without spending tokens?

**A4:** Use `agents.testing.ScriptedModel` with `assistant_message(...)` and call `Runner.run_sync`. Disable tracing with `set_tracing_disabled(True)`.

**Q5:** Design the configuration for a multi-environment FastAPI deployment.

**A5:** Model name, tracing switch and key source come from env/secret manager, loaded once in the lifespan; a `/health` readiness endpoint reports SDK readiness and key source (never the key); the agent factory takes the model so tests inject a scripted model; version pinned in `requirements.txt`; secrets rotated without code change.

---

## 💰 Cost Impact
Setup itself costs nothing, but wrong setup can: tracing uploads add network work per run, an unpinned upgrade can change default models or behaviour, and a missing `max_turns` cap lets a bug burn tokens. Smoke tests with `ScriptedModel` cost 0 tokens (the scripted model reports 0 usage). Per-run token cost depends on the real model (approximate, from public pricing at time of writing, verify); measure with `result.context_wrapper.usage`.

**Tips:** pin versions, put the model name in config, set `max_turns` in the endpoint, use scripted models in CI, use a cheap model in dev.

---

## 🔷 When to Use
✅ Use when:
- You start any SDK project (a clean venv plus smoke test is the first commit)
- You deploy to containers/Kubernetes (lifespan + health check)
- You need to run CI without API keys

❌ Avoid when:
- You are tempted to set keys inside agent modules or notebooks that get committed
- You rely on a floating `latest` version in production

---

## 📊 Visual Diagram
```
 requirements.txt (openai-agents==0.24.0)
        |
 pip install  -->  import agents
        |
 secret manager --> env OPENAI_API_KEY  (or set_default_openai_key)
        |
 FastAPI lifespan: configure once, build Agent, set tracing
        |
   +----+-----------------+
   | /health (readiness)  |--> 200 sdk_ready / key_source
   | /ask  Runner.run     |--> 503 if credentials missing
   +----------------------+
 CI: ScriptedModel smoke test (0 tokens)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| venv | Isolated Python environment | अलग Python वातावरण |
| pin | Fix an exact package version | package का version तय करना |
| `set_default_openai_key` | SDK-wide API key setter | SDK के लिए default key |
| lifespan | FastAPI startup/shutdown hook | startup/shutdown hook |
| smoke test | Tiny test that proves the basics work | बुनियादी जाँच वाला छोटा test |
| ScriptedModel | Fake model for offline tests | offline test वाला नकली model |

---

## ⚡ 3-Line Summary
English: Install with `pip install openai-agents`, import `agents`, pin the version.
Give the key through env or `set_default_openai_key`, never in source.
Configure once in a FastAPI lifespan and keep an offline smoke test.

Hindi: `pip install openai-agents` से install करें, `agents` import करें, version pin करें।
Key env या `set_default_openai_key` से दें, source में कभी नहीं।
FastAPI lifespan में एक बार configure करें और offline smoke test रखें।

---

## ➡️ Next Topic
**#34 Agent Class, Complete** - setup is done, now we go through every field of `Agent` (instructions, tools, output_type, model_settings, hooks) and what each does.

---
