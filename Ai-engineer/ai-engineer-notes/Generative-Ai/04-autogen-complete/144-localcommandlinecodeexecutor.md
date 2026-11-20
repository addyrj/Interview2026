---

# 144. LocalCommandLineCodeExecutor
# हिंदी में: LocalCommandLineCodeExecutor (अपनी मशीन पर code चलाने वाला executor)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`LocalCommandLineCodeExecutor` (from `autogen_ext.code_executors.local`) runs code blocks as subprocesses on the machine where your Python process runs. Parameters in 0.7.5: `timeout`, `work_dir`, `functions`, `functions_module`, `cleanup_temp_files`, `virtual_env_context`. It is easy and fast, but it is NOT a sandbox.

## 🔵 सरल परिभाषा (Hindi)
`LocalCommandLineCodeExecutor` (`autogen_ext.code_executors.local` से) code blocks को उसी मशीन पर subprocess की तरह चलाता है जहाँ आपका Python process चल रहा है। 0.7.5 में parameters: `timeout`, `work_dir`, `functions`, `functions_module`, `cleanup_temp_files`, `virtual_env_context`। यह आसान और तेज़ है, लेकिन sandbox नहीं है।

---

## 🔴 Problem it Solves
You need a quick way to run model-written code during development and tests without installing Docker. You also want to reuse trusted helper functions inside generated code and isolate Python packages in a virtualenv.

## 🔴 यह क्यों बना? (Hindi)
Development और tests के दौरान model का लिखा code जल्दी चलाने का तरीका चाहिए, बिना Docker लगाए। साथ ही generated code के अंदर भरोसेमंद helper functions दोबारा इस्तेमाल करने हैं और Python packages को virtualenv में अलग रखना है।

---

## 🟢 How it Works

```
Step 1 -> Create the executor with work_dir (use a temp dir) and timeout
Step 2 -> Optional: pass functions=[duty] so generated code can `from functions import duty`
Step 3 -> Optional: pass virtual_env_context from venv.EnvBuilder so code runs in that venv
Step 4 -> await executor.execute_code_blocks([CodeBlock(code, language)], CancellationToken())
Step 5 -> Executor saves a file, starts a subprocess, waits up to timeout
Step 6 -> Result has exit_code and output (0 ok, 1 error, 124 timeout seen in our run)
Step 7 -> Use `async with executor:` (or start/stop) so temp files are cleaned
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> work_dir (temp dir) और timeout के साथ executor बनाओ
Step 2 -> वैकल्पिक: functions=[duty] दो ताकि generated code `from functions import duty` कर सके
Step 3 -> वैकल्पिक: venv.EnvBuilder का virtual_env_context दो ताकि code उसी venv में चले
Step 4 -> await executor.execute_code_blocks([CodeBlock(code, language)], CancellationToken())
Step 5 -> Executor file सेव करता है, subprocess शुरू करता है, timeout तक इंतज़ार करता है
Step 6 -> Result में exit_code और output होता है (0 ठीक, 1 error, 124 timeout, हमारे run में दिखा)
Step 7 -> `async with executor:` (या start/stop) इस्तेमाल करें ताकि temp files साफ़ हों
```

---

## 🟡 Real World Example
**Tariff Agent in CI.** In unit tests the coder is faked and the real local executor checks that `print(2+2)` returns 4, that an infinite sleep is killed at the timeout, and that a raised `ValueError` returns exit code 1 with the traceback. Fast feedback, no Docker needed.

## 🟡 Real Example Hindi mein
**CI में Tariff Agent.** Unit tests में coder नकली होता है और असली local executor जाँचता है कि `print(2+2)` का नतीजा 4 है, अनंत sleep timeout पर मारा जाता है, और `ValueError` पर exit code 1 के साथ traceback आता है। तुरंत feedback, Docker की ज़रूरत नहीं।

---

## 💻 Code Example — Basic
Basic: run three snippets (ok, too slow, crashes) and print exit code plus the tail of the output. The observed codes were 0, 124 and 1.

```python
# Basic: LocalCommandLineCodeExecutor directly (success, timeout, error)
import asyncio  # loop
import tempfile  # temp dir
from autogen_core import CancellationToken  # token
from autogen_core.code_executor import CodeBlock  # one code block
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor  # executor

async def main() -> None:  # entry
    with tempfile.TemporaryDirectory() as d:  # work dir
        ex = LocalCommandLineCodeExecutor(work_dir=d, timeout=2)  # 2 second timeout
        for src in ["print(2+2)", "import time; time.sleep(30)", "raise ValueError('bad')"]:  # ok, slow, crash
            r = await ex.execute_code_blocks([CodeBlock(code=src, language="python")], CancellationToken())  # run
            print(r.exit_code, repr(r.output[-40:]))  # exit code 0 / 124 timeout / 1 error

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: `functions=[duty]` makes a helper importable from generated code (`from functions import duty`), and a real virtualenv is passed via `virtual_env_context`, behind a FastAPI endpoint.

```python
# Advanced: reusable functions + virtualenv + FastAPI (functions are importable inside generated code)
import tempfile  # temp dir
import venv  # create venv
from pathlib import Path  # paths
from fastapi import FastAPI  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body
from autogen_core import CancellationToken  # token
from autogen_core.code_executor import CodeBlock  # block
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor  # executor

def duty(value: float, rate: float) -> float:  # helper exposed to generated code
    """Compute duty amount."""  # description
    return value * rate  # math

app = FastAPI()  # app

class Req(BaseModel):  # body
    value: float  # value
    rate: float  # rate

@app.post("/exec")  # endpoint
async def run(req: Req) -> dict[str, object]:  # handler
    with tempfile.TemporaryDirectory() as d:  # per-request dir
        builder = venv.EnvBuilder(with_pip=False)  # venv builder (no pip: fast)
        builder.create(Path(d) / "venv")  # actually create the venv on disk
        env = builder.ensure_directories(Path(d) / "venv")  # context object with bin paths
        ex = LocalCommandLineCodeExecutor(work_dir=d, timeout=15, functions=[duty], virtual_env_context=env)  # inject helper + venv
        async with ex:  # start/stop lifecycle
            src = f"from functions import duty\nprint(duty({req.value}, {req.rate}))"  # LLM-like code using helper
            r = await ex.execute_code_blocks([CodeBlock(code=src, language="python")], CancellationToken())  # run
    return {"exit": r.exit_code, "out": r.output.strip()}  # response

print(TestClient(app).post("/exec", json={"value": 1000, "rate": 0.25}).json())  # try
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing. This executor executed real subprocesses on the author's machine; the constructor signature above was read from the installed package.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Local execution | Your own tool | Local code tool | Your own function tool | LocalCommandLineCodeExecutor |
| Isolation | None unless you add | Docker mode available | Hosted sandbox only for hosted tool | None (use Docker executor for isolation) |
| Timeout | Your code | max_execution_time | Tool-level timeout | timeout parameter (exit code 124 seen) |
| Helper functions | Import normally | Tools | function_tool | functions=[...] exposed as `functions` module |
| Virtualenv | Your code | Not built in | Not built in | virtual_env_context |
| Cleanup | You | You | You | cleanup_temp_files, async with |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming local means safe because code is 'only a test'.
✅ Correct: The subprocess has your user permissions: it can read your SSH keys and delete files. Treat it as untrusted code run on your laptop.

❌ Mistake: Not setting a timeout.
✅ Correct: Always set `timeout`; one `while True` blocks the run.

❌ Mistake: Passing functions without type hints or docstrings.
✅ Correct: Helper functions are copied into a module; give them hints and docstrings and keep them side-effect free.

❌ Mistake: Creating the venv with pip for every request.
✅ Correct: Build a venv once at startup and reuse its context; the demo uses `with_pip=False` only to stay fast.

---

## 🧠 Tricky Interview Question
A user prompt makes the coder write code that reads ~/.aws/credentials and prints it. The local executor ran it. What should have prevented this?

Answer: Local execution has no isolation by design. Defences: never run untrusted code with LocalCommandLineCodeExecutor on a host that has secrets; use the Docker executor with no network and no mounted secrets, drop privileges, add an `approval_func` or static deny-list (necessary but bypassable), redact outputs, and keep an audit log. Treat the deny-list as a speed bump and the container boundary as the real control.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does the timeout do?
A1: Kills the code after N seconds; in our run a sleeping script returned exit code 124 and 'Timeout' in the output.

Q2: [Medium] What does the `functions` parameter do?
A2: Makes the given Python functions importable in generated code as `from functions import name`.

Q3: [Hard] Why use a virtual environment with the local executor?
A3: So installed packages are separated from the host environment; pass `virtual_env_context` from `venv.EnvBuilder`.

Q4: [Hard] Is a deny-list of dangerous strings enough?
A4: No. Attackers can obfuscate (`__import__('o'+'s')`). It is a quick filter, not a security boundary.

Q5: [System Design] When do you move from local to Docker executor?
A5: As soon as code comes from users or an LLM that sees user text, or the host holds secrets. Local is for unit tests and trusted internal scripts only.

---

## 💰 Cost Impact
The executor itself costs no tokens. Cost comes from the coder loop: every failed run adds the traceback to the history. Tip: truncate tracebacks (`r.output[-500:]`), cap retries, and prefer deterministic helper functions (`functions=`) over regenerating the same code each time. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Local development and unit tests.
- Trusted internal code where you control the input.
- You need fast feedback without Docker.

❌ Avoid when:
- Anything handling untrusted prompts or user-supplied code.
- A host that has production credentials.
- Multi-tenant servers.

---

## 📊 Visual Diagram
```
 generated code
      |
      v
 +-------------------------------+
 | LocalCommandLineCodeExecutor  |
 |  work_dir (temp)              |
 |  timeout=N                    |
 |  functions -> functions.py    |
 |  venv context (optional)      |
 +---------------+---------------+
                 | subprocess (YOUR user, YOUR machine)
                 v
      exit_code 0 / 1 / 124   +   output text
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| subprocess | Child OS process | child OS process |
| timeout | Time limit before kill | kill से पहले समय सीमा |
| exit code 124 | Value seen when the timeout fired | timeout लगने पर दिखा मान |
| functions module | Helper functions exposed to generated code | generated code को दिखने वाले helper functions |
| virtual_env_context | Context of a venv to run code in | जिस venv में code चलेगा उसका context |
| work_dir | Folder for generated files | generated files का folder |
| CancellationToken | Lets callers cancel a run | run रद्द करने का token |

---

## ⚡ 3-Line Summary
English: Local executor runs generated code as a subprocess on your machine.
It supports timeout, helper functions and virtualenvs, and returns exit_code + output.
It is not a sandbox: use it for development only.
Hindi: Local executor generated code को आपकी मशीन पर subprocess की तरह चलाता है।
इसमें timeout, helper functions और virtualenv हैं, और यह exit_code + output लौटाता है।
यह sandbox नहीं है: सिर्फ़ development में इस्तेमाल करें।

---

## ➡️ Next Topic
145. DockerCommandLineExecutor -- run the same code inside a container for real isolation.

---
