---

# 133. CodeExecutorAgent
# हिंदी में: CodeExecutorAgent — model का लिखा code चलाना
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`CodeExecutorAgent` executes code blocks (```python, ```sh) that it finds in incoming messages using a `CodeExecutor` (for example `LocalCommandLineCodeExecutor` or `DockerCommandLineCodeExecutor`) and returns stdout/stderr. In v0.4 it normally does not write code; another `AssistantAgent` writes it. An optional `approval_func` can allow or reject execution.

## 🔵 सरल परिभाषा (Hindi)
`CodeExecutorAgent` आने वाले messages में मिले code blocks (```python, ```sh) को `CodeExecutor` (जैसे `LocalCommandLineCodeExecutor` या `DockerCommandLineCodeExecutor`) से चलाता है और stdout/stderr लौटाता है। v0.4 में यह आम तौर पर code लिखता नहीं; code कोई `AssistantAgent` लिखता है। वैकल्पिक `approval_func` execution की अनुमति या इनकार करता है।

---

## 🔴 Problem it Solves
LLMs are bad at arithmetic, data wrangling and exact computation, but good at writing code that does it. Executing model-written code solves that, but it is the most dangerous capability in an agent system: file deletion, secret exfiltration, network calls, infinite loops. v0.4 splits 'writing' from 'executing', puts execution behind an executor interface and offers an approval hook.

## 🔴 यह क्यों बना? (Hindi)
LLMs arithmetic, data wrangling और exact computation में कमज़ोर हैं पर उसे करने वाला code अच्छा लिखते हैं। Model का लिखा code चलाने से यह हल होता है, पर यह agent system की सबसे ख़तरनाक क्षमता है: files delete होना, secrets बाहर जाना, network calls, infinite loops। v0.4 'लिखना' और 'चलाना' अलग करता है, execution को executor interface के पीछे रखता है और approval hook देता है।

---

## 🟢 How it Works

```
Step 1 -> Coder agent (LLM) writes a ```python block in its message
Step 2 -> CodeExecutorAgent extracts code blocks from the latest messages
Step 3 -> approval_func(ApprovalRequest(code, context)) -> ApprovalResponse(approved, reason)
Step 4 -> If rejected: returns 'Code execution was not approved. Reason: ...'
Step 5 -> If approved: executor.execute_code_blocks(...) in work_dir with timeout
Step 6 -> stdout/stderr + exit code returned as a message
Step 7 -> Coder reads the output, fixes errors, loop until termination
Step 8 -> max_retries_on_error (with model_client) lets the agent itself retry failed code
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Coder agent (LLM) अपने message में ```python block लिखता है
Step 2 -> CodeExecutorAgent ताज़ा messages से code blocks निकालता है
Step 3 -> approval_func(ApprovalRequest(code, context)) -> ApprovalResponse(approved, reason)
Step 4 -> reject हुआ: 'Code execution was not approved. Reason: ...' लौटता है
Step 5 -> approve हुआ: executor work_dir में timeout के साथ code चलाता है
Step 6 -> stdout/stderr + exit code message के रूप में लौटता है
Step 7 -> Coder output पढ़कर errors ठीक करता है, termination तक loop
Step 8 -> max_retries_on_error (model_client के साथ) से agent खुद failed code retry कर सकता है
```

---

## 🟡 Real World Example
**Duty calculator by code.** Ask: 'USD 500 shirt, 20 percent duty, INR rate 83.2, add 18 percent GST on duty-inclusive value.' The coder writes Python, the executor runs it and prints the exact number. This is more reliable than asking the LLM to do arithmetic in its head. In production the executor runs in Docker with no network and a read-only filesystem.

## 🟡 Real Example Hindi mein
**Code से duty calculator.** पूछिए: 'USD 500 की shirt, 20 percent duty, INR rate 83.2, duty-inclusive value पर 18 percent GST।' Coder Python लिखता है, executor चलाकर सटीक संख्या print करता है। यह LLM से दिमाग में गणित करवाने से ज़्यादा भरोसेमंद है। Production में executor Docker में चलता है: network नहीं, read-only filesystem।

---

## 💻 Code Example — Basic
Basic: a hand-written code block is passed to the agent (as if an LLM wrote it). It really executes on this machine in a temp directory, which is why `LocalCommandLineCodeExecutor` emits an unsafe-execution warning.

```python
# CodeExecutorAgent: runs ```python blocks it RECEIVES (it does not write code itself). Offline, local executor.
import asyncio, tempfile                                          # async + temp working dir
from autogen_agentchat.agents import CodeExecutorAgent            # executes code blocks from messages
from autogen_agentchat.messages import TextMessage                # input message type
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor  # runs on YOUR machine (unsafe for untrusted code)

async def main() -> None:
    with tempfile.TemporaryDirectory() as work_dir:               # isolated scratch folder, auto-deleted
        executor = LocalCommandLineCodeExecutor(work_dir=work_dir, timeout=20)  # timeout kills runaway code
        agent = CodeExecutorAgent("executor", code_executor=executor)  # no model_client -> pure executor
        code_msg = TextMessage(                                   # pretend an LLM wrote this
            content="```python\nvalue=500\nprint(value*83.2*0.20)\n```", source="coder")
        res = await agent.run(task=code_msg)                      # executes the block
        print(res.messages[-1].content)                           # stdout of the code: 8320.0

if __name__ == "__main__":
    asyncio.run(main())
    # For untrusted code use DockerCommandLineCodeExecutor (autogen_ext.code_executors.docker) -- not run here, needs Docker.
```

## 💻 Code Example — Advanced
Advanced: an `approval_func` blocklist in front of the executor, a hard timeout, request size limit and error mapping in FastAPI. The blocklist is a teaching example, not a sandbox: a determined attacker bypasses string matching. Real isolation = Docker (`DockerCommandLineCodeExecutor`, not run here, needs Docker) or a remote sandbox.

```python
# CodeExecutorAgent with an approval gate, FastAPI, error handling (offline; local executor)
import asyncio, tempfile                                          # stdlib
from fastapi import FastAPI, HTTPException                        # web
from fastapi.testclient import TestClient                         # offline test
from autogen_agentchat.agents import (ApprovalRequest, ApprovalResponse,  # approval types
                                      CodeExecutorAgent)
from autogen_agentchat.messages import TextMessage                # message type
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor  # executor

BLOCKLIST = ("os.system", "subprocess", "shutil.rmtree", "rm -rf", "requests.", "socket")  # naive guard, NOT a sandbox

def approve(req: ApprovalRequest) -> ApprovalResponse:            # called BEFORE every execution
    for bad in BLOCKLIST:                                         # reject suspicious code
        if bad in req.code:                                       # req.code = the code text, req.context = chat so far
            return ApprovalResponse(approved=False, reason=f"blocked pattern: {bad}")
    return ApprovalResponse(approved=True, reason="ok")           # allow

app = FastAPI()

@app.post("/run-code")
async def run_code(body: dict) -> dict:
    code = body.get("code", "")                                   # untrusted input (e.g. LLM output)
    if len(code) > 5000:                                          # input guard
        raise HTTPException(413, "code too long")
    with tempfile.TemporaryDirectory() as wd:                     # per-request sandbox dir
        ex = LocalCommandLineCodeExecutor(work_dir=wd, timeout=10)  # hard timeout
        agent = CodeExecutorAgent("executor", code_executor=ex, approval_func=approve)  # gate in front of executor
        msg = TextMessage(content=f"```python\n{code}\n```", source="coder")
        try:
            res = await asyncio.wait_for(agent.run(task=msg), timeout=30)
        except Exception as exc:
            raise HTTPException(500, f"executor failed: {exc}")
    return {"output": str(res.messages[-1].content).strip()}

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/run-code", json={"code": "print(500*83.2*0.2)"}).json())     # allowed
    print(c.post("/run-code", json={"code": "import subprocess\nsubprocess.run(['ls'])"}).json())  # blocked by approve()
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Code execution | Tool node / REPL tool | Code Interpreter tool (Docker option) | Code Interpreter hosted tool | CodeExecutorAgent + executor classes |
| Sandbox options | DIY | Docker flag | Hosted by OpenAI | Local, Docker, Jupyter, ACA dynamic sessions (extensions) |
| Approval hook | interrupt before node | Manual | Guardrails/approvals DIY | approval_func built in |
| Writes code itself | LLM node | Agent | Agent | Normally separate AssistantAgent |
| Timeout | Tool wrapper | Config | Tool wrapper | Executor timeout parameter |

---

## ⚠️ Common Mistakes
❌ Mistake: Using `LocalCommandLineCodeExecutor` for untrusted prompts in production. The code runs with your user's permissions.
✅ Correct: Use Docker or a remote sandbox, no network, resource limits, non-root user.

❌ Mistake: Relying on a string blocklist as the security boundary.
✅ Correct: Treat it as a speed bump. The sandbox is the boundary.

❌ Mistake: No timeout: `while True` hangs a worker.
✅ Correct: Set the executor `timeout` and wrap the agent call in `asyncio.wait_for`.

❌ Mistake: Putting secrets in environment variables visible to executed code.
✅ Correct: Run with a minimal environment; pass only what the code needs.

---

## 🧠 Tricky Interview Question
The model writes `import os; print(os.environ)` and your executor prints API keys into the transcript, which then goes to the next LLM call and your logs. How do you prevent it?

Answer: Layered defence: (1) run code in a container with a clean environment, so the keys are not there; (2) no network egress; (3) approval_func rejects obviously dangerous code and, for sensitive flows, requires human approval; (4) post-filter executor output for secret patterns before it re-enters the context or logs; (5) least-privilege credentials; (6) audit every execution with code hash, user and output size. The root fix is that secrets never exist inside the sandbox.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `CodeExecutorAgent` do?
A1: Finds code blocks in messages, runs them with the given executor and returns the output. It can optionally use a model client (to write code and reflect), but its core job is execution.

Q2: [Medium] Which executors exist?
A2: In `autogen-ext`: local command line, Docker command line, Jupyter, and Azure container apps dynamic sessions (extras may be needed). Local is unsafe for untrusted code.

Q3: [Hard] What is `approval_func` for?
A3: A sync or async callable receiving `ApprovalRequest(code, context)` and returning `ApprovalResponse(approved, reason)`; a gate for policy or human approval.

Q4: [Hard] How do you limit runaway code?
A4: Executor `timeout`, container CPU/memory limits, `asyncio.wait_for`, and a maximum number of coder-executor iterations.

Q5: [System Design] Design a data-analysis agent that is safe for multi-tenant SaaS.
A5: Per-request ephemeral Docker container (or a remote sandbox service), no network, read-only mounted dataset copy, CPU/memory/time limits, non-root user, output size limit, approval policy engine, code and output audit log, and a coder-executor loop capped at N iterations with cost tracking per tenant.

---

## 💰 Cost Impact
The executor spends no tokens, but the coder-executor loop does: each failed run adds code plus a traceback to the context and triggers another LLM call. Typical pattern: 1 call to write the code, 0-3 repair calls. Formula: `loop_cost = (1 + retries) * (history_tokens * in_price + code_tokens * out_price)`. Tips: truncate long tracebacks and stdout before they return to the model, cap retries, and prefer a precise tool (`get_tariff_rate`) over generated code when a deterministic function exists. Infrastructure cost: a container start per request can add latency; reuse warm pools. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Exact computation, data analysis, file transformations.
- Agents that verify their own code by running it.
- With Docker or remote sandbox and approval policy.

❌ Avoid when:
- Untrusted users with the local executor.
- Simple lookups that a typed tool can do.
- Environments that cannot run containers and have no other sandbox.

---

## 📊 Visual Diagram
```
 user --> Coder(LLM) --"```python ...```"--> CodeExecutorAgent
                                                 |
                                       approval_func(code)?
                                          |            |
                                       rejected      approved
                                          |            v
                              "not approved: reason"  Executor (Docker / local, timeout)
                                          |            |
                                          +------> stdout / stderr / exit code
                                                       |
                                       Coder reads output, fixes code, repeats until done
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CodeExecutor | Interface that runs code blocks | code blocks चलाने वाला interface |
| LocalCommandLineCodeExecutor | Runs code on the host (unsafe) | host पर code चलाता है (असुरक्षित) |
| DockerCommandLineCodeExecutor | Runs inside a container | container के अंदर चलाता है |
| approval_func | Gate before execution | execution से पहले की अनुमति |
| sandbox | Isolated environment | अलग-थलग वातावरण |
| work_dir | Directory for code files | code files की directory |
| timeout | Max run time | अधिकतम चलने का समय |
| exfiltration | Stealing data out | डेटा चुराकर बाहर भेजना |

---

## ⚡ 3-Line Summary
English: CodeExecutorAgent runs code blocks written by another agent and returns the output.
Local execution is unsafe: use Docker/remote sandbox, timeouts, approval_func and clean environments.
A string blocklist is not a security boundary; the sandbox is.
Hindi: CodeExecutorAgent दूसरे agent के लिखे code blocks चलाकर output लौटाता है।
Local execution असुरक्षित है: Docker/remote sandbox, timeouts, approval_func और साफ़ environment इस्तेमाल करें।
String blocklist security boundary नहीं है; sandbox है।

---

## ➡️ Next Topic
134. MultimodalConversableAgent -- the v0.2 name for vision agents, and the v0.4 way (MultiModalMessage).

---
