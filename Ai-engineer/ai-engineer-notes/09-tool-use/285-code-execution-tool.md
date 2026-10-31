---

# 285. Code Execution Tool
# हिंदी में: Code Execution Tool

---

## 🔵 Simple Definition (English)
A code execution tool lets the model write Python code and run it in a sandbox, then read the output. It gives exact results for maths, data analysis and file processing. It can be provider-hosted (OpenAI `code_interpreter`, Anthropic `code_execution`) or your own sandbox (Docker, gVisor, E2B).

## 🔵 सरल परिभाषा (Hindi)
Code execution tool में model Python code लिखता है, sandbox में चलाता है और output पढ़ता है। इससे maths, data analysis और file processing में सटीक नतीजे मिलते हैं। यह provider-hosted हो सकता है (OpenAI `code_interpreter`, Anthropic `code_execution`) या आपका अपना sandbox (Docker, gVisor, E2B)।

---

## 🔴 Problem it Solves
LLMs are bad at exact arithmetic, large table analysis and counting. They guess. Running real code gives correct, reproducible answers and lets the model process CSV/Excel files too big for the context window.

## 🔴 यह क्यों बना? (Hindi)
LLM सटीक गणित, बड़ी table के विश्लेषण और गिनती में कमज़ोर हैं; वे अंदाज़ा लगाते हैं। असली code चलाने से सही, दोहराने योग्य जवाब मिलते हैं और context window से बड़ी CSV/Excel files भी process हो जाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User asks a question needing computation or file analysis
Step 2 → Model writes Python code as a tool call
Step 3 → Sandbox runs the code (no network, limited CPU/memory/time)
Step 4 → stdout, stderr, files and return code come back
Step 5 → Model reads output; if error, it fixes the code and retries
Step 6 → Model explains the result in natural language
Step 7 → Your app logs the code + output for audit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User ऐसा सवाल पूछता है जिसमें computation या file analysis चाहिए
Step 2 → Model tool call के रूप में Python code लिखता है
Step 3 → Sandbox code चलाता है (network नहीं, CPU/memory/time सीमित)
Step 4 → stdout, stderr, files और return code लौटते हैं
Step 5 → Model output पढ़ता है; error हो तो code सुधारकर फिर चलाता है
Step 6 → Model नतीजा आसान भाषा में समझाता है
Step 7 → आपका app audit के लिए code + output log करता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: An importer uploads a CSV of 20,000 shipment lines. The model writes pandas code to group by HS code, compute total duty and flag lines where declared duty differs from the table by more than 5%. The answer: "312 lines mismatched; total underpayment 4.2 lakh". The LLM never had to read 20,000 rows in its context.

**Amazon AI**: "Plot my monthly spend by category" executes plotting code.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer 20,000 shipment lines की CSV upload करता है। Model pandas code लिखकर HS code के हिसाब से group करता है, कुल duty निकालता है और जहाँ declared duty table से 5% से ज़्यादा अलग है वे lines flag करता है। जवाब: "312 lines mismatch; कुल कम भुगतान 4.2 लाख।" LLM को 20,000 rows context में पढ़नी नहीं पड़ीं।

**Amazon AI**: "मेरा monthly खर्च category के हिसाब से plot करो" → plotting code चलता है।

---

## 💻 Code Example — Basic
```python
# Basic: run model-written code in a separate process with a timeout (offline)
# WARNING: a subprocess is NOT a full sandbox. Use containers/gVisor for untrusted code.
import subprocess                                       # run another process
import sys                                              # path to current Python
import tempfile                                         # temp working directory
from dataclasses import dataclass                       # result container

@dataclass
class ExecResult:
    ok: bool          # did it exit with code 0
    stdout: str       # printed output
    stderr: str       # error text

def run_python(code: str, timeout_s: float = 5.0) -> ExecResult:
    """Run code in a fresh interpreter, isolated mode, temp cwd, time-limited."""
    with tempfile.TemporaryDirectory() as tmp:          # throw-away working dir
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-c", code],     # -I = isolated mode (ignores env/user site)
                capture_output=True, text=True, timeout=timeout_s, cwd=tmp)
        except subprocess.TimeoutExpired:               # infinite loop protection
            return ExecResult(False, "", "timeout")
    return ExecResult(proc.returncode == 0, proc.stdout[:2000], proc.stderr[:2000])  # cap output

model_code = "rows=[('8517',100,20),('6403',50,25)]\nprint(sum(v*r/100 for _,v,r in rows))"
print(run_python(model_code))                           # stdout '32.5\n'
print(run_python("while True: pass", timeout_s=1))      # timeout
print(run_python("1/0"))                                # ZeroDivisionError in stderr
```

## 💻 Code Example — Advanced
```python
# Production: Anthropic hosted code execution + OpenAI code_interpreter, async, errors
import asyncio                                           # async runtime
import logging                                           # logs
from typing import Any                                   # typing
import anthropic                                         # pip install anthropic
from openai import AsyncOpenAI, APIError                 # openai>=1

logger = logging.getLogger("code_exec")

async def analyze_with_openai(question: str) -> dict[str, Any]:
    """OpenAI Responses API with the built-in code interpreter (runs on OpenAI servers)."""
    client = AsyncOpenAI()
    try:
        resp = await client.responses.create(
            model="gpt-4o-mini",
            input=question,
            tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
        )
    except APIError as exc:
        logger.exception("openai failed")
        return {"error": str(exc)}
    return {"answer": resp.output_text, "tokens": resp.usage.total_tokens if resp.usage else None}

async def analyze_with_claude(question: str) -> dict[str, Any]:
    """Anthropic code execution tool (beta header and tool version may change - check docs)."""
    client = anthropic.AsyncAnthropic()
    try:
        msg = await client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            betas=["code-execution-2025-05-22"],
            tools=[{"type": "code_execution_20250522", "name": "code_execution"}],
            messages=[{"role": "user", "content": question}],
        )
    except anthropic.APIError as exc:
        logger.exception("anthropic failed")
        return {"error": str(exc)}
    text = "".join(b.text for b in msg.content if b.type == "text")   # collect text blocks
    return {"answer": text, "tokens": msg.usage.input_tokens + msg.usage.output_tokens}

if __name__ == "__main__":
    q = "Compute the sum of squares of 1..100 using code."
    print(asyncio.run(analyze_with_openai(q)))
```

---

## 🟠 FastAPI Integration
Run the local sandbox off the event loop, because subprocess waiting would block async handling.

```python
import asyncio
from fastapi import FastAPI, HTTPException               # framework
from pydantic import BaseModel, Field                    # validation

app = FastAPI()

class CodeReq(BaseModel):
    code: str = Field(max_length=5000)                   # limit size

@app.post("/exec")
async def execute(req: CodeReq) -> dict:
    result = await asyncio.to_thread(run_python, req.code, 5.0)   # do not block loop
    if not result.ok:
        raise HTTPException(status_code=422, detail=result.stderr)
    return {"stdout": result.stdout}
# NOTE: in production only the AGENT should call this, never expose raw execution publicly.
```

---

## 🔗 LangChain / LangGraph Connection
Wrap the sandbox as a tool. LangChain's `PythonREPLTool` (langchain-experimental) runs code in-process and is unsafe for untrusted input; prefer your own sandboxed tool.

```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

@tool
def python_sandbox(code: str) -> str:
    """Run Python code in a sandbox and return stdout. Use for exact maths and data analysis."""
    r = run_python(code)
    return r.stdout if r.ok else f"ERROR: {r.stderr}"

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [python_sandbox])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `exec()` or an in-process REPL on model-written code
✅ Correct: Run in an isolated process or container with no secrets, no network, time and memory limits.

```python
# Wrong
exec(llm_code)                       # can read env vars, delete files, steal secrets
# Right
result = run_python(llm_code, timeout_s=5)
```

❌ Mistake 2: Returning huge stdout back into the prompt
✅ Correct: Truncate and summarise outputs.

```python
# Wrong
return proc.stdout                   # might be 5 MB
# Right
return proc.stdout[:2000]
```

---

## 🧠 Tricky Interview Question
**Q**: "Your code interpreter agent works in demo but a user tricks it into printing environment variables including the API key. How did that happen and how do you prevent it?"

**Answer**: The sandbox shared the host environment (a plain subprocess or exec inherited env vars). Prevent with: separate container/microVM with an empty environment, no mounted credentials, no network egress (or allow-listed), read-only filesystem except a temp dir, CPU/memory/time limits, non-root user, and short-lived instances. Never put secrets where model-written code can reach. Also log code and outputs for audit.

---

## ⚫ Interview Questions + Answers

Q1: Why use code execution instead of asking the LLM to calculate?
A1: Code is exact and deterministic; LLM arithmetic is probabilistic and can be wrong.

Q2: What is a sandbox?
A2: An isolated environment with restricted CPU, memory, filesystem and network, so untrusted code cannot harm the host.

Q3: What should you return from the tool?
A3: stdout and a short error, truncated. Include the return code or an explicit ERROR prefix so the model can fix its code.

Q4: Hosted vs self-hosted code execution?
A4: Hosted is easy and maintained by the provider, but data leaves your infra and costs per container. Self-hosted gives control and privacy but you must secure it.

Q5: (Hard) Design a safe data-analysis agent for customer CSVs.
A5: Upload file to an ephemeral microVM; mount read-only; no network; resource limits; pre-installed pandas; model writes code, sandbox returns stdout/plots; cap iterations; truncate outputs; scan generated files; destroy sandbox after; log everything; validate that numeric claims in the final answer match tool output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Exact calculations, statistics, charts
- Files too large for the context window

❌ Avoid when:
- Simple lookups (a normal tool is cheaper and safer)
- You cannot provide real isolation

---

## 📊 Visual Diagram
```
 Question + file
      |
      v
   [LLM] --writes code--> +-------------------+
      ^                   |  SANDBOX          |
      |                   |  no net, limits   |
      |<--stdout/stderr---|  python + pandas  |
      |                   +-------------------+
      v
  Explained answer
```

---

## 💰 Cost Impact
- Output tokens for generated code, plus input tokens for each retry (history grows).
- Hosted containers may be billed per session or per time (check current pricing).
- Optimise: cap iterations (3-5), truncate outputs, give the schema of the data (column names, 5 sample rows) instead of the whole file, reuse a container across turns, and use a cheaper model for simple scripts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sandbox | Isolated run environment | अलग सुरक्षित वातावरण |
| code_interpreter | OpenAI hosted Python tool | OpenAI का hosted Python tool |
| code_execution | Anthropic hosted tool | Anthropic का hosted tool |
| Egress | Outbound network traffic | बाहर जाने वाला network traffic |
| stdout / stderr | Normal / error output | सामान्य / error output |
| microVM | Lightweight virtual machine | हल्की virtual machine |

---

## ⚡ 3-Line Summary
English: Code execution lets the model write and run Python for exact results and big-file analysis. Safety depends on a true sandbox: no secrets, no network, strict limits. Truncate outputs and cap retries to control tokens.
Hindi: Code execution से model सटीक नतीजों और बड़ी file analysis के लिए Python लिखकर चलाता है। सुरक्षा असली sandbox पर निर्भर है: secrets नहीं, network नहीं, सख़्त limits। Outputs छोटे रखें और retries सीमित, ताकि tokens काबू में रहें।

---

## ➡️ Next Topic
**286. Calculator Tool** — the simplest safe tool for exact maths without full code execution.
