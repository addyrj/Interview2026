---

# 145. DockerCommandLineExecutor
# हिंदी में: DockerCommandLineExecutor (container के अंदर code चलाना)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`DockerCommandLineCodeExecutor` (from `autogen_ext.code_executors.docker`) runs generated code inside a Docker container. Constructor parameters in 0.7.5: `image`, `container_name`, `timeout`, `work_dir`, `bind_dir`, `auto_remove`, `stop_container`, `device_requests`, `functions`, `functions_module`, `extra_volumes`, `extra_hosts`, `init_command`, `delete_tmp_files`. Note: the class name is `DockerCommandLineCodeExecutor` (with `Code`).

## 🔵 सरल परिभाषा (Hindi)
`DockerCommandLineCodeExecutor` (`autogen_ext.code_executors.docker` से) generated code को Docker container के अंदर चलाता है। 0.7.5 के constructor parameters: `image`, `container_name`, `timeout`, `work_dir`, `bind_dir`, `auto_remove`, `stop_container`, `device_requests`, `functions`, `functions_module`, `extra_volumes`, `extra_hosts`, `init_command`, `delete_tmp_files`। ध्यान दें: class का नाम `DockerCommandLineCodeExecutor` है (बीच में `Code`)।

---

## 🔴 Problem it Solves
Local execution gives model-written code your user's full permissions. A container adds a boundary: separate filesystem, resource limits and (if you choose) no network. It also lets you pin an image with known packages so results are reproducible.

## 🔴 यह क्यों बना? (Hindi)
Local execution में model का code आपके user की पूरी permissions के साथ चलता है। Container एक दीवार जोड़ता है: अलग filesystem, resource limits और (चाहें तो) network बंद। साथ ही image पिन करके packages तय कर सकते हैं ताकि नतीजे दोहराए जा सकें।

---

## 🟢 How it Works

```
Step 1 -> Install and start Docker (and the Python docker package if the import asks for it)
Step 2 -> Create DockerCommandLineCodeExecutor(image=..., timeout=..., work_dir=...)
Step 3 -> await executor.start() (or `async with`) pulls the image if needed and starts the container
Step 4 -> work_dir is bind-mounted; code files are written there
Step 5 -> execute_code_blocks runs the file inside the container with a timeout
Step 6 -> await executor.stop() stops (and, with auto_remove, deletes) the container
Step 7 -> Reuse one container across many blocks to avoid slow cold starts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Docker install करके चालू करो (और import माँगे तो Python का docker package भी)
Step 2 -> DockerCommandLineCodeExecutor(image=..., timeout=..., work_dir=...) बनाओ
Step 3 -> await executor.start() (या `async with`) ज़रूरत हो तो image pull करके container शुरू करता है
Step 4 -> work_dir bind-mount होती है; code files वहीं लिखी जाती हैं
Step 5 -> execute_code_blocks file को container के अंदर timeout के साथ चलाता है
Step 6 -> await executor.stop() container रोकता है (auto_remove हो तो हटा भी देता है)
Step 7 -> धीमे cold start से बचने के लिए कई blocks में एक ही container दोबारा इस्तेमाल करो
```

---

## 🟡 Real World Example
**Tariff Agent in production.** Customers upload CSV invoices and ask 'total duty by HS chapter?'. The coder writes pandas code; it runs in a container started at application startup (FastAPI lifespan), with a pinned image and a timeout. If the code misbehaves it can only damage the container.

## 🟡 Real Example Hindi mein
**Production में Tariff Agent.** Customers CSV invoices upload करके पूछते हैं 'HS chapter के हिसाब से कुल duty?'। Coder pandas code लिखता है; वह application startup (FastAPI lifespan) पर शुरू हुए container में चलता है, pinned image और timeout के साथ। code गड़बड़ करे तो नुकसान सिर्फ़ container का होता है।

---

## 💻 Code Example — Basic
Basic: `async with DockerCommandLineCodeExecutor(...)` and one block. NOT RUN: this machine has no Docker daemon. When the script was executed it failed with `RuntimeError: Failed to connect to Docker. Please ensure Docker is installed and running.` which is the expected, documented failure.

```python
# Basic: DockerCommandLineCodeExecutor  (NOT RUN here: needs a running Docker daemon)
import asyncio  # loop
from autogen_core import CancellationToken  # token
from autogen_core.code_executor import CodeBlock  # block
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor  # container executor

async def main() -> None:  # entry
    async with DockerCommandLineCodeExecutor(image="python:3-slim", timeout=30, work_dir="coding") as ex:  # starts + stops container
        r = await ex.execute_code_blocks([CodeBlock(code="print(1000*0.25)", language="python")], CancellationToken())  # run inside container
        print(r.exit_code, r.output)  # result

if __name__ == "__main__":  # script guard
    asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: one shared container created in a FastAPI lifespan and stopped on shutdown. NOT RUN (needs Docker); the file was syntax-checked and imported (the import `autogen_ext.code_executors.docker` succeeds), but no container was ever started.

```python
# Advanced: Docker executor in a FastAPI lifespan with a reused container (NOT RUN: needs Docker)
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator  # type
from fastapi import FastAPI, HTTPException  # web
from pydantic import BaseModel  # body
from autogen_core import CancellationToken  # token
from autogen_core.code_executor import CodeBlock  # block
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor  # executor

executor: DockerCommandLineCodeExecutor | None = None  # one shared container

@asynccontextmanager  # lifespan = startup + shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # signature
    global executor  # assign module var
    executor = DockerCommandLineCodeExecutor(image="python:3-slim", timeout=30, work_dir="coding", auto_remove=True, stop_container=True)  # config
    await executor.start()  # start container once
    yield  # app serves requests
    await executor.stop()  # always stop container

app = FastAPI(lifespan=lifespan)  # app

class Req(BaseModel):  # body
    code: str  # python source

@app.post("/run")  # endpoint
async def run(req: Req) -> dict[str, object]:  # handler
    if executor is None:  # not started
        raise HTTPException(503, "executor not ready")  # unavailable
    r = await executor.execute_code_blocks([CodeBlock(code=req.code, language="python")], CancellationToken())  # run in container
    return {"exit": r.exit_code, "out": r.output[-2000:]}  # cap output size
```

**Verification status:** parameter list read from the installed package (autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13)). Neither example was run successfully: they need a running Docker daemon and the `python:3-slim` image (not run -- needs Docker). Treat exact output and timing as unverified.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Containerised code run | Your own sandbox tool | Docker-based code interpreter option | Hosted tool (provider sandbox) | DockerCommandLineCodeExecutor |
| Image control | You | Fixed by CrewAI | Provider-managed | image=... (you choose) |
| Lifecycle | You | Per call | Provider | start()/stop() or async with |
| Resource limits | Docker flags you set | Limited | Provider limits | Set via Docker/image; device_requests for GPUs |
| Mounts | You | Limited | None | work_dir/bind_dir/extra_volumes |
| Needs daemon | Yes if Docker | Yes | No | Yes |

---

## ⚠️ Common Mistakes
❌ Mistake: Starting a container for every request.
✅ Correct: Start once in the app lifespan and reuse it; cold start can cost seconds.

❌ Mistake: Leaving `auto_remove` / `stop_container` off and leaking containers.
✅ Correct: Use `async with` or call `stop()` in a `finally` / lifespan shutdown.

❌ Mistake: Mounting your home directory or Docker socket into the container.
✅ Correct: Mount only a throwaway work dir; never mount secrets or `/var/run/docker.sock`.

❌ Mistake: Assuming the container has no network by default.
✅ Correct: Docker allows network by default; restrict it (network mode, firewall) if the code should not call out.

---

## 🧠 Tricky Interview Question
Docker executor works on your laptop but fails in CI with 'Failed to connect to Docker'. Why, and what are the options?

Answer: CI runners often have no Docker socket (or you are inside a container without Docker-in-Docker). Options: enable the runner's Docker service or Docker-in-Docker, use a remote Docker host, or run unit tests with the local executor and a faked coder while keeping Docker tests for an integration stage that is allowed to start containers. Make the choice injectable (`executor` passed into your function) so the same code is testable both ways.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is the class name and module?
A1: `DockerCommandLineCodeExecutor` in `autogen_ext.code_executors.docker`.

Q2: [Medium] How do you ensure the container is cleaned up?
A2: Use `async with`, or call `stop()` in a finally block; set `auto_remove=True` and `stop_container=True`.

Q3: [Hard] Why reuse one container?
A3: Image pull and startup take seconds; a shared container amortises that. Files from earlier blocks stay in work_dir, so isolate users with separate dirs or containers.

Q4: [Hard] Is Docker enough for hostile code?
A4: It is a strong step up from local but containers share the host kernel. For hostile multi-tenant code add gVisor/Firecracker-style isolation, no network, read-only root and resource limits.

Q5: [System Design] Design a code-analysis service for many customers.
A5: Gateway authenticates and rate-limits; a pool of pre-warmed containers per tenant tier; work dirs per job; CPU/memory/time quotas; network off; stdout/size caps; audit logs; results streamed back; cleanup job destroys containers.

---

## 💰 Cost Impact
Docker adds infrastructure cost (container CPU/RAM, image storage) not token cost. Token cost is as in topic 143. A reused container saves startup latency per request. Do not quote latency numbers without measuring on your hardware. Tips: small images, pre-pulled images, one container per worker. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Code comes from an LLM or users.
- You need reproducible packages (pinned image).
- You can run Docker in your deployment.

❌ Avoid when:
- Environment has no Docker (use another sandbox).
- Tiny trusted scripts where overhead is not worth it.
- Hostile multi-tenant code with no extra isolation.

---

## 📊 Visual Diagram
```
 FastAPI app
   | lifespan startup: executor.start()
   v
 +----------------- Docker host ------------------+
 |  container (image=python:3-slim)               |
 |    /workspace  <--- bind mount: work_dir       |
 |    run file with timeout                       |
 +-------------------------+----------------------+
   ^                       | exit_code + output
   |                       v
 request -> execute_code_blocks()  -> response
   | lifespan shutdown: executor.stop()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Docker image | Template for a container | container का template |
| container | Isolated running instance | अलग चलता हुआ instance |
| bind mount | Host folder shared into container | host folder जो container में दिखता है |
| auto_remove | Delete container when stopped | रुकने पर container हटाना |
| lifespan | FastAPI startup/shutdown hook | FastAPI का startup/shutdown hook |
| cold start | Slow first start | पहली बार का धीमा शुरू होना |
| not run | Written but needs Docker to execute | लिखा है पर चलाने के लिए Docker चाहिए |

---

## ⚡ 3-Line Summary
English: The Docker executor runs generated code inside a container for isolation.
Start it once (lifespan) and always stop it; mount only a throwaway work dir.
These examples were not run here because there is no Docker daemon.
Hindi: Docker executor generated code को isolation के लिए container के अंदर चलाता है।
इसे एक बार शुरू करें (lifespan) और हमेशा stop करें; सिर्फ़ फेंकने लायक work dir mount करें।
इन examples को यहाँ नहीं चलाया गया क्योंकि Docker daemon नहीं था।

---

## ➡️ Next Topic
146. Code Execution Safety -- layered defences: approvals, deny-lists, timeouts, output caps, audit.

---
