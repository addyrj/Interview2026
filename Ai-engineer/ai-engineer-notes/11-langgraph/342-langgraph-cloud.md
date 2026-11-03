
---

# 342. LangGraph Cloud
# हिंदी में: LangGraph Cloud — Graph को Managed API की तरह Deploy करना

---

## 🔵 Simple Definition (English)
LangGraph Cloud is LangChain's managed hosting for LangGraph agents. You push your graph code and it runs as an API server with built-in persistence (checkpoints, threads, long-term store), background runs, streaming, cron jobs and scaling. Note that the product names have changed over time (LangGraph Platform, now under LangSmith Deployment), so check the current docs for exact naming.

## 🔵 सरल परिभाषा (Hindi)
LangGraph Cloud, LangChain की managed hosting है LangGraph agents के लिए। आप graph code push करते हैं और वह API server बनकर चलता है जिसमें persistence (checkpoints, threads, long-term store), background runs, streaming, cron jobs और scaling पहले से होती है। Product के नाम समय के साथ बदले हैं (LangGraph Platform, अब LangSmith Deployment), इसलिए सटीक नाम के लिए current docs देखो।

---

## 🔴 Problem it Solves
Long-running agents are hard to host: requests last minutes, runs must survive restarts, human-in-the-loop pauses last days, many users need isolated state, and you need queues, retries and streaming. Building all of this on plain FastAPI means writing a task queue, checkpoint DB and streaming layer yourself.

## 🔴 यह क्यों बना? (Hindi)
लंबे चलने वाले agents host करना कठिन है: requests मिनटों चलती हैं, restart में run बचना चाहिए, human-in-the-loop कई दिन रुकता है, कई users का state अलग चाहिए और queues, retries, streaming चाहिए। सादे FastAPI पर यह सब खुद बनाना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write your graph and a langgraph.json (same as for Studio)
Step 2 → Put the repo on GitHub (managed cloud deploys from a repo) or build a Docker image
Step 3 → Create a deployment in the LangSmith/LangGraph platform UI and set secrets (API keys)
Step 4 → The platform builds the image and runs API server + task queue + Postgres/Redis
Step 5 → You get an HTTPS endpoint and an API key (x-api-key header)
Step 6 → Client (SDK or REST) creates a thread, then starts a run on an assistant (graph)
Step 7 → Run is queued, executed by workers, checkpointed at each step
Step 8 → Stream tokens/events, or poll/join; resume after interrupts with the same thread_id
Step 9 → New git commit -> new revision; monitor via LangSmith traces
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Graph और langgraph.json लिखो (Studio जैसी ही)
Step 2 → Repo GitHub पर रखो या Docker image बनाओ
Step 3 → Platform UI में deployment बनाओ और secrets (API keys) डालो
Step 4 → Platform image build करके API server + task queue + Postgres/Redis चलाता है
Step 5 → HTTPS endpoint और API key (x-api-key header) मिलता है
Step 6 → Client (SDK/REST) thread बनाता है, फिर assistant (graph) पर run शुरू करता है
Step 7 → Run queue में जाता है, workers चलाते हैं, हर step पर checkpoint
Step 8 → Tokens/events stream करो; interrupt के बाद वही thread_id से resume
Step 9 → नया git commit = नया revision; LangSmith traces से monitoring
```

---

## 🟡 Real World Example
**Tariff Classification System**: a bulk job classifies 5,000 shipment lines. The front-end submits each as a background run on the cloud deployment and gets run ids immediately; hard cases hit `interrupt` and wait days for an officer, then resume on the same thread. FastAPI is only a thin gateway adding auth.

**Zomato AI**: an order-support agent with a 2-minute tool chain streams partial answers to the app while the platform handles retries and persistence.

## 🟡 Real Example Hindi mein
**Tariff System**: 5,000 shipment lines की bulk job। Front-end हर line को cloud deployment पर background run की तरह भेजता है और run id तुरंत पाता है; मुश्किल cases `interrupt` पर रुकते हैं, officer के जवाब के बाद उसी thread पर resume। FastAPI सिर्फ auth वाला पतला gateway है।

**Zomato AI**: Order-support agent जिसकी tool chain 2 मिनट चलती है, app को partial answers stream करता है जबकि platform retries और persistence संभालता है।

---

## 💻 Code Example — Basic
```python
# Basic: a deployment-ready langgraph.json and a tiny graph, written with pure Python
import json  # write config
from pathlib import Path  # file paths

config = {
    "dependencies": ["."],                    # install this project's requirements
    "graphs": {"tariff": "./agent.py:graph"}, # assistant id "tariff" -> compiled graph
    "env": ".env",                            # local env file (cloud uses its secrets UI instead)
}
Path("langgraph.json").write_text(json.dumps(config, indent=2))  # write file

reqs = "langgraph\nlangchain-openai\n"  # minimal requirements.txt
Path("requirements.txt").write_text(reqs)  # write requirements
print("Files ready. Local test: `langgraph dev`; container build: `langgraph build -t tariff-agent`.")
# Never commit .env or API keys; set secrets in the deployment UI.
```

## 💻 Code Example — Advanced
```python
# Production client: call a deployed LangGraph API with the official SDK (async, typed, error handling)
# pip install langgraph-sdk
import asyncio  # async runtime
import logging  # logs
import os  # env variables
from typing import Any  # typing

from langgraph_sdk import get_client  # official SDK

log = logging.getLogger("lg-cloud")  # logger

async def classify_remote(description: str, case_id: str) -> dict[str, Any]:
    """Create a thread, run the 'tariff' assistant, wait, and return the final state."""
    client = get_client(
        url=os.environ["LANGGRAPH_URL"],          # deployment URL from the platform UI
        api_key=os.environ["LANGSMITH_API_KEY"],  # key sent as x-api-key
    )
    try:
        thread = await client.threads.create(metadata={"case_id": case_id})  # new persistent thread
        result = await client.runs.wait(  # start a run and wait for completion
            thread["thread_id"],           # which thread
            "tariff",                      # assistant / graph name from langgraph.json
            input={"desc": description, "code": "", "approved": False},  # graph input state
        )
        return {"thread_id": thread["thread_id"], "state": result}  # return ids for later resume
    except Exception as exc:  # network, auth, graph errors
        log.error("remote run failed: %s", exc)  # log
        raise  # let the caller map to HTTP error

async def stream_remote(thread_id: str, description: str) -> None:
    """Stream events from a run (useful for chat UIs)."""
    client = get_client(url=os.environ["LANGGRAPH_URL"], api_key=os.environ["LANGSMITH_API_KEY"])  # client
    async for chunk in client.runs.stream(  # async iterator of events
        thread_id, "tariff",
        input={"desc": description, "code": "", "approved": False},  # input
        stream_mode="updates",  # one event per node update
    ):
        print(chunk.event, chunk.data)  # forward to the UI in real code

if __name__ == "__main__":
    # Needs LANGGRAPH_URL and LANGSMITH_API_KEY of a real deployment, so it is not run offline.
    print(asyncio.run(classify_remote("Bluetooth headphones", "case-1")))
```

---

## 🟠 FastAPI Integration
Keep FastAPI as your own gateway (auth, rate limiting, business rules) and delegate agent execution to the deployment.

```python
import os  # env vars
from fastapi import Depends, FastAPI, Header, HTTPException  # framework
from langgraph_sdk import get_client  # SDK
from pydantic import BaseModel  # schema

app = FastAPI()  # app
client = get_client(url=os.getenv("LANGGRAPH_URL", ""), api_key=os.getenv("LANGSMITH_API_KEY"))  # shared client

def auth(x_token: str = Header(...)) -> str:
    """Very small auth check (replace with real JWT validation)."""
    if x_token != os.getenv("GATEWAY_TOKEN"):  # compare to secret
        raise HTTPException(status_code=401, detail="bad token")  # reject
    return x_token  # ok

class Req(BaseModel):
    description: str  # product text

@app.post("/classify")
async def classify(req: Req, _: str = Depends(auth)) -> dict:
    """Start a background run and return immediately with ids."""
    thread = await client.threads.create()  # new thread
    run = await client.runs.create(  # enqueue, do not wait
        thread["thread_id"], "tariff",
        input={"desc": req.description, "code": "", "approved": False},  # input
    )
    return {"thread_id": thread["thread_id"], "run_id": run["run_id"]}  # client polls later
```

---

## 🔗 LangChain / LangGraph Connection
The deployment server runs exactly the compiled graph you wrote, so no code changes are needed beyond `langgraph.json`. Persistence replaces the `MemorySaver` you used locally (the platform provides a Postgres-backed checkpointer), and traces automatically appear in LangSmith. You can also call a deployed graph from another graph using `RemoteGraph`.

```python
from langgraph.pregel.remote import RemoteGraph  # use a deployed graph like a local one

remote = RemoteGraph("tariff", url="https://your-deployment.example.com", api_key="lsv2_...")  # illustrative URL/key
# result = await remote.ainvoke({"desc": "headphones", "code": "", "approved": False})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Secrets in the repo
✅ Correct: Use the platform's secrets/env settings.
```python
# Wrong: OPENAI_API_KEY = "sk-..." in agent.py
# Right: os.environ["OPENAI_API_KEY"] set in the deployment secrets
```

❌ Mistake 2: Using the sync wait for hour-long runs
✅ Correct: Create a background run and poll or use webhooks.
```python
# Wrong: await client.runs.wait(...)   # HTTP timeout for long human-in-the-loop flows
# Right: run = await client.runs.create(...); later: await client.runs.join(thread_id, run_id)
```

❌ Mistake 3: Exposing the platform API key to browsers
✅ Correct: Call it only from your backend gateway.

---

## 🧠 Tricky Interview Question

**Q**: "Why not just deploy the graph inside FastAPI with a SQLite checkpointer? When does managed cloud win?"

**Answer**: FastAPI + SQLite works for small, single-instance apps. It breaks when you need multiple replicas (SQLite file is local), runs longer than request timeouts, queues and retries, human pauses lasting days, streaming at scale, and cron jobs. The platform gives a task queue, Postgres persistence and horizontal scaling out of the box. Trade-offs: vendor cost, less control over infrastructure, and data residency; a self-hosted container of the same server is the middle path. Decide by traffic, run duration and compliance.

---

## ⚫ Interview Questions + Answers

Q1: What is LangGraph Cloud?
A1: A managed service that deploys LangGraph graphs as scalable APIs with built-in persistence and queues.

Q2: What file configures the deployment?
A2: `langgraph.json`, listing dependencies, graphs and env.

Q3: What are threads and runs?
A3: A thread is a persistent conversation/state container; a run is one execution of a graph on a thread.

Q4: How do you handle a human approval that takes two days?
A4: Use `interrupt` (or `interrupt_before`); state is checkpointed, the run stops, and later you resume on the same thread with the human's input.

Q5: How do you move from local dev to production safely?
A5: Test with `langgraph dev`, add evaluations in LangSmith, deploy a staging revision, load-test, then promote. Keep secrets in the platform, keep a gateway for auth, version graphs, and monitor traces, latency and cost. Have a self-hosted fallback or rollback revision.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long-running, stateful, multi-user agents with human-in-the-loop
- You do not want to build queues and checkpoint storage

❌ Avoid when:
- A simple stateless endpoint is enough
- Strict data-residency rules forbid managed hosting (self-host instead)

---

## 📊 Visual Diagram
```
 Client ─► FastAPI gateway (auth) ─► LangGraph deployment
                                      ┌─────────────────────────┐
                                      │ API server              │
                                      │  ├─ task queue/workers  │
                                      │  ├─ Postgres checkpoints│
                                      │  └─ streaming, cron     │
                                      └────────────┬────────────┘
                                                   ▼
                                    LangSmith traces / evaluation
```

---

## 💰 Cost Impact
Two cost lines: the platform fee (plans and prices change; check the current pricing page) and the LLM tokens your graph uses. Managed hosting saves engineering time but adds a recurring fee, so compare with self-hosting on your own cloud. Optimise tokens exactly as in any graph: small state, cheap models in routine nodes, capped retries (`recursion_limit`), caching repeated questions. Avoid keeping runs idle at interrupts if the plan bills by active compute; check the billing details.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Deployment | A hosted graph API | Hosted graph API |
| Assistant | Named graph + config | Graph + config का नाम |
| Thread | Persistent state container | State रखने वाला thread |
| Run | One execution | एक बार का execution |
| Background run | Run without waiting | बिना इंतज़ार वाला run |
| Cron job | Scheduled run | निर्धारित समय पर run |
| RemoteGraph | Call a deployed graph | Deployed graph को call करना |

---

## ⚡ 3-Line Summary
English: LangGraph Cloud hosts your compiled graph as an API with queues, Postgres checkpoints, streaming and cron. Configure with `langgraph.json`, call with the SDK, and keep FastAPI as the auth gateway. Names and pricing change, so check current docs.
Hindi: LangGraph Cloud आपके compiled graph को API की तरह host करता है: queues, Postgres checkpoints, streaming और cron के साथ। `langgraph.json` से configure करो, SDK से call करो और FastAPI को auth gateway रखो। नाम और pricing बदलते हैं, current docs देखो।

---

## ➡️ Next Topic
**343. Common LangGraph Patterns** — reusable designs like ReAct loop, router, reflection, plan-and-execute and human approval.
