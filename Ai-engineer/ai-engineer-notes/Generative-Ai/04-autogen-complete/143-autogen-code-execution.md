---

# 143. AutoGen Code Execution
# हिंदी में: AutoGen Code Execution (agent से code लिखवाकर चलाना)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
AutoGen can let one agent write code and another run it. `CodeExecutorAgent` scans incoming messages for markdown code blocks (for example ```python), runs them through a `CodeExecutor` and replies with exit code and output. Executors live in `autogen_ext.code_executors` (local, Docker and others).

## 🔵 सरल परिभाषा (Hindi)
AutoGen में एक agent code लिख सकता है और दूसरा उसे चला सकता है। `CodeExecutorAgent` आने वाले messages में markdown code blocks (जैसे ```python) खोजता है, `CodeExecutor` से चलाता है और exit code व output के साथ जवाब देता है। Executors `autogen_ext.code_executors` में हैं (local, Docker आदि)।

---

## 🔴 Problem it Solves
LLMs are bad at exact arithmetic, data crunching and verifying their own output. If they can run code they compute the answer, see errors and fix themselves. Without an executor the model only prints code the user must copy and run.

## 🔴 यह क्यों बना? (Hindi)
LLM सटीक गणित, data processing और अपने output की जाँच में कमज़ोर हैं। अगर वे code चला सकें तो जवाब निकालते हैं, errors देखते हैं और खुद ठीक करते हैं। Executor के बिना model सिर्फ़ code छापता है जिसे user को copy करके चलाना पड़ता है।

---

## 🟢 How it Works

```
Step 1 -> Coder (AssistantAgent) writes a ```python block in its reply
Step 2 -> CodeExecutorAgent extracts code blocks from the last message
Step 3 -> Optional approval_func can reject the code (see 146)
Step 4 -> The CodeExecutor writes the file in work_dir and runs it with a timeout
Step 5 -> Agent replies with exit code + output text
Step 6 -> Coder reads the output and either fixes the code or says TERMINATE
Step 7 -> Team termination condition stops the loop
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Coder (AssistantAgent) अपने जवाब में ```python block लिखता है
Step 2 -> CodeExecutorAgent आखिरी message से code blocks निकालता है
Step 3 -> वैकल्पिक approval_func code को reject कर सकता है (देखें 146)
Step 4 -> CodeExecutor file को work_dir में लिखकर timeout के साथ चलाता है
Step 5 -> Agent exit code + output text के साथ जवाब देता है
Step 6 -> Coder output पढ़कर code सुधारता है या TERMINATE कहता है
Step 7 -> Team की termination condition loop रोकती है
```

---

## 🟡 Real World Example
**Tariff Agent.** 'Compute 25% duty on a USD 1000 invoice.' The coder writes `print(1000 * 0.25)`, the executor runs it and returns `250.0`, the coder confirms and writes TERMINATE. The number is computed, not guessed, and the run log proves it.

## 🟡 Real Example Hindi mein
**Tariff Agent.** 'USD 1000 के invoice पर 25% duty निकालो।' Coder `print(1000 * 0.25)` लिखता है, executor चलाकर `250.0` लौटाता है, coder पुष्टि करके TERMINATE लिखता है। संख्या अंदाज़े से नहीं, गणना से आई और run log उसका सबूत है।

---

## 💻 Code Example — Basic
Basic: `CodeExecutorAgent` with a local executor and no model client, so it only executes. We hand it a message containing a python block and print its reply.

```python
# Basic: CodeExecutorAgent runs a ```python block found in a message
import asyncio  # event loop
import tempfile  # throwaway work dir
from autogen_core import CancellationToken  # cancel token
from autogen_agentchat.agents import CodeExecutorAgent  # agent that executes code blocks
from autogen_agentchat.messages import TextMessage  # chat message
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor  # runs code on THIS machine (dev only)

async def main() -> None:  # entry
    with tempfile.TemporaryDirectory() as d:  # code files are written here
        executor = LocalCommandLineCodeExecutor(work_dir=d, timeout=10)  # 10s limit per block
        agent = CodeExecutorAgent("executor", code_executor=executor)  # no model_client => only executes
        code = "```python\nprint(1000 * 0.25)\n```"  # what an LLM would have written
        res = await agent.on_messages([TextMessage(content=code, source="coder")], CancellationToken())  # feed the message
        print(res.chat_message.content)  # exit code + output

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: coder plus executor in a `RoundRobinGroupChat` behind FastAPI, a fresh temp directory per request, termination on TERMINATE or message cap, and error handling. The coder is a scripted fake; the executor is real and ran code on this machine.

```python
# Advanced: coder + executor team behind FastAPI (scripted fake coder; real executor, local sandbox for dev)
import tempfile  # temp work dir
from fastapi import FastAPI, HTTPException  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor  # executor
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent  # agents
from autogen_agentchat.teams import RoundRobinGroupChat  # team
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination  # stop rules

app = FastAPI()  # app

class Req(BaseModel):  # body
    value: float  # invoice value

@app.post("/duty")  # endpoint
async def duty(req: Req) -> dict[str, object]:  # typed
    script = f"```python\nprint({req.value} * 0.25)\n```"  # code the fake coder will 'write'
    coder = AssistantAgent("coder", ReplayChatCompletionClient([script, "Result received. TERMINATE"]))  # scripted LLM
    with tempfile.TemporaryDirectory() as d:  # isolated dir per request
        ex = LocalCommandLineCodeExecutor(work_dir=d, timeout=10)  # local executor
        runner = CodeExecutorAgent("runner", code_executor=ex)  # executes blocks
        team = RoundRobinGroupChat([coder, runner], termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(6))  # loop coder->runner->coder
        try:  # protect
            res = await team.run(task="compute 25% duty")  # run
        except Exception as e:  # any failure
            raise HTTPException(500, f"team failed: {e}")  # report
    outs = [m.content for m in res.messages if m.source == "runner"]  # executor outputs
    return {"runner_output": outs, "stop": res.stop_reason}  # response

print(TestClient(app).post("/duty", json={"value": 1000}).json())  # try it
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing. The executor really executed Python locally (LocalCommandLineCodeExecutor, development only: it runs code on your machine without isolation; see 144-146).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Code execution | Tool node calling your sandbox | Code Interpreter tool (Docker-based, optional) | Hosted code-interpreter tool or your own tool | CodeExecutorAgent + CodeExecutor (local, Docker, others) |
| Who writes code | Any LLM node | Agent with allow_code_execution | Model via tool | AssistantAgent writes, CodeExecutorAgent runs |
| Sandboxing | You provide | Docker mode | Hosted sandbox when using hosted tool | DockerCommandLineCodeExecutor |
| Retry on error | Graph loop | Agent retry | Model loop with tool errors | Round-robin loop; max_retries_on_error on agent with model client |
| Approval gate | interrupt | human_input | Tool approvals | approval_func parameter |
| Stop condition | Edge to END | max_iter | max_turns | TextMentionTermination('TERMINATE') | MaxMessageTermination |

---

## ⚠️ Common Mistakes
❌ Mistake: Using LocalCommandLineCodeExecutor in production on user-supplied prompts.
✅ Correct: Use `DockerCommandLineCodeExecutor` (144/145) or another isolated sandbox for anything untrusted.

❌ Mistake: Using the current directory as work_dir.
✅ Correct: Use a temporary directory (`tempfile.TemporaryDirectory()`); AutoGen warns that using `.` is deprecated and it can overwrite your files.

❌ Mistake: No termination condition on the coder/executor loop.
✅ Correct: Add `TextMentionTermination('TERMINATE') | MaxMessageTermination(n)` or the loop can burn tokens forever.

❌ Mistake: Forgetting that the executor only runs fenced code blocks.
✅ Correct: Tell the coder in its system message to always answer with a fenced ```python block.

---

## 🧠 Tricky Interview Question
The coder keeps producing code that fails with ModuleNotFoundError. What do you change?

Answer: The executor runs in an environment you control, so the model cannot assume packages. Options: pre-install packages in the Docker image or a virtualenv (`virtual_env_context`), tell the coder in its system message which libraries exist, allow it to emit a shell block with `pip install` only in a sandbox you can throw away, and add a retry limit so repeated failure stops with a clear error. Never let it pip-install on your host.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does CodeExecutorAgent do?
A1: It finds fenced code blocks in incoming messages, runs them with a configured CodeExecutor and replies with the result.

Q2: [Medium] Which languages can the local executor run?
A2: Python and shell variants by default (check `supported_languages` on the agent in your version); other languages need the right toolchain.

Q3: [Hard] Why is a coder/executor loop usually better than asking for the final number directly?
A3: The executor gives ground truth (stdout, errors). The coder can fix mistakes using real feedback instead of guessing.

Q4: [Hard] How do you stop runaway code?
A4: Executor `timeout`, output size caps, approval function, Docker resource limits, and team termination conditions.

Q5: [System Design] Design a code-running data assistant for customers.
A5: API gateway -> per-request container (Docker or microVM) with CPU/memory/time limits and no network -> executor agent -> output truncation and redaction -> audit log of code + result -> human approval for anything that writes data.

---

## 💰 Cost Impact
Each loop iteration re-sends the growing conversation (code plus output) to the coder: input tokens grow roughly linearly per turn. Long outputs are the main hidden cost, so truncate stdout. Formula: `cost = sum over turns of (history_tokens * in_price) + code_tokens * out_price`. Tip: cap turns, keep prints short. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Exact computation, data transformation or validation is needed.
- The model must test its own output.
- You have an isolated sandbox.

❌ Avoid when:
- Untrusted input and only a local executor.
- A plain lookup tool would do (cheaper, safer).
- No way to bound time, memory and network.

---

## 📊 Visual Diagram
```
 task --> [ coder AssistantAgent ] --writes--> ```python ...```
                    ^                               |
                    |                               v
         output / error text            [ CodeExecutorAgent ]
                    |                               |
                    +------ exit code + stdout <----+
                                        |
                              [ CodeExecutor: work_dir, timeout ]
 stop when coder says TERMINATE or message cap reached
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| CodeExecutorAgent | Agent that runs code blocks | code blocks चलाने वाला agent |
| CodeExecutor | Backend that actually runs code | code असल में चलाने वाला backend |
| code block | Fenced ```python section in a message | message में ```python वाला हिस्सा |
| work_dir | Directory where code files are written | जहाँ code files लिखी जाती हैं |
| timeout | Max seconds per block | प्रति block अधिकतम सेकंड |
| TERMINATE | Convention word to stop the loop | loop रोकने का convention शब्द |
| sandbox | Isolated environment | अलग-थलग environment |

---

## ⚡ 3-Line Summary
English: A coder agent writes fenced code; CodeExecutorAgent runs it and returns output.
The loop gives the model real feedback so it can fix its own mistakes.
Local executor is for development; use Docker or another sandbox in production.
Hindi: Coder agent fenced code लिखता है; CodeExecutorAgent उसे चलाकर output लौटाता है।
Loop model को असली feedback देता है ताकि वह अपनी गलतियाँ सुधार सके।
Local executor सिर्फ़ development के लिए है; production में Docker या दूसरा sandbox इस्तेमाल करें।

---

## ➡️ Next Topic
144. LocalCommandLineCodeExecutor -- the dev-time executor in detail: timeouts, functions, virtualenvs.

---
