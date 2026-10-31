---

# 286. Calculator Tool
# हिंदी में: Calculator Tool (LLM को सही गणित देना)

---

## 🔵 Simple Definition (English)
A calculator tool is a small, safe function that the LLM can call to do exact arithmetic. LLMs predict tokens, they do not compute, so they often get math wrong. The tool takes an expression like `"1200 * 0.18"`, evaluates it in code, and returns the exact number to the model.

## 🔵 सरल परिभाषा (Hindi)
Calculator tool एक छोटा, safe function है जिसे LLM call कर सकता है ताकि गणित बिल्कुल सही हो। LLM tokens predict करता है, गणित compute नहीं करता, इसलिए अक्सर गलती करता है। Tool expression (जैसे `"1200 * 0.18"`) को code में evaluate करके exact number वापस देता है।

---

## 🔴 Problem it Solves
LLMs are bad at multi-digit multiplication, percentages and chained operations. A model may say `18% of 48,250 = 8,675` (wrong, it is 8,685). In tariff, billing or finance flows a wrong number is a real money bug. The naive fix, `eval(expression)`, is dangerous: a prompt-injected string like `__import__("os").system("rm -rf /")` would execute on your server.

## 🔴 यह क्यों बना? (Hindi)
LLM बड़े numbers का multiplication, percentage और chained operations में गलती करता है। Tariff या billing में गलत number = पैसे का bug। आसान तरीका `eval()` खतरनाक है, क्योंकि prompt injection से user malicious code चला सकता है। इसलिए **safe calculator tool** चाहिए जो सिर्फ़ अंकगणित allow करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define tool schema: name="calculator", param expression (string)
Step 2 → Send user question + tool schema to the LLM
Step 3 → LLM decides math is needed → returns tool_call(expression="48250*0.18")
Step 4 → Your code parses expression with ast (NOT eval) and whitelists operators
Step 5 → Result 8685.0 is sent back as a role="tool" message
Step 6 → LLM writes the final natural-language answer using the exact number
Step 7 → Tokens used = prompt + tool schema + tool call + tool result + final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tool schema बनाओ: name="calculator", param expression
Step 2 → User सवाल + schema LLM को भेजो
Step 3 → LLM बोलता है "math चाहिए" → tool_call(expression="48250*0.18")
Step 4 → आपका code ast से parse करता है (eval नहीं), सिर्फ़ allowed operators
Step 5 → Result 8685.0 role="tool" message में वापस भेजो
Step 6 → LLM exact number से final जवाब लिखता है
Step 7 → Tokens = prompt + schema + tool call + tool result + final answer
```

---

## 🟡 Real World Example
**Tariff Classification System**: Product HS code 8517.12 has a 18% customs duty plus 10% surcharge on the duty. Declared value is Rs 48,250. The LLM identifies the HS code and rate (from RAG), then calls `calculator("48250 * 0.18")` and `calculator("48250 * 0.18 * 0.10")`. The final duty is exact, auditable, and logged.

**Zomato AI**: "Split Rs 1,847 bill among 5 people with a 10% tip" is routed to the calculator tool instead of trusting the model.

## 🟡 Real Example Hindi mein
**Tariff System**: HS code 8517.12 पर 18% duty और duty पर 10% surcharge है। Declared value Rs 48,250 है। LLM RAG से rate निकालता है, फिर `calculator("48250 * 0.18")` call करता है। Final duty exact और audit-able होती है।

**Zomato AI**: "Rs 1,847 का bill 5 लोगों में 10% tip के साथ बाँटो" → calculator tool, model का अंदाज़ा नहीं।

---

## 💻 Code Example — Basic
```python
# Safe calculator using Python's ast module (pure Python, runs offline)
import ast                       # parse expression into a syntax tree
import operator                  # functions for + - * / etc.
from typing import Union         # type hint for numbers

Number = Union[int, float]       # alias: our calculator returns int or float

# Whitelist: only these operators are allowed (everything else is rejected)
OPS = {
    ast.Add: operator.add,       # +
    ast.Sub: operator.sub,       # -
    ast.Mult: operator.mul,      # *
    ast.Div: operator.truediv,   # /
    ast.Pow: operator.pow,       # **
    ast.Mod: operator.mod,       # %
    ast.USub: operator.neg,      # unary minus, e.g. -5
}

def _eval(node: ast.AST) -> Number:
    """Recursively evaluate a node from the syntax tree."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value                          # a plain number like 48250
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left = _eval(node.left)                    # evaluate left side
        right = _eval(node.right)                  # evaluate right side
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")  # stop 9**9**9 style DoS
        return OPS[type(node.op)](left, right)     # apply allowed operator
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))  # handle -x
    raise ValueError(f"unsupported expression: {type(node).__name__}")  # reject names, calls

def calculator(expression: str) -> str:
    """Tool entry point: returns a string result or an error string."""
    try:
        tree = ast.parse(expression, mode="eval")  # parse as a single expression
        result = _eval(tree.body)                  # evaluate safely
        return str(round(result, 6))               # round to avoid 0.1+0.2 noise
    except ZeroDivisionError:
        return "error: division by zero"           # tell the LLM what went wrong
    except (ValueError, SyntaxError) as exc:
        return f"error: {exc}"                     # invalid or unsafe input

print(calculator("48250 * 0.18"))                  # 8685.0
print(calculator("(48250 * 0.18) * 0.10"))         # 868.5
print(calculator("1/0"))                           # error: division by zero
print(calculator("__import__('os').system('ls')")) # error: unsupported expression: Call
```

## 💻 Code Example — Advanced
```python
# Production: Decimal precision + OpenAI tool loop + async + error handling
import ast, json, operator, asyncio
from decimal import Decimal, InvalidOperation   # exact decimal math (money!)
from typing import Any, Callable
from openai import AsyncOpenAI                  # openai>=1.x async client

client = AsyncOpenAI()                          # reads OPENAI_API_KEY from env

# Decimal-based whitelist so 0.1 + 0.2 == 0.3 exactly
OPS: dict[type, Callable[..., Decimal]] = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.USub: operator.neg,
}

def _eval(node: ast.AST) -> Decimal:
    """Evaluate AST using Decimal so money math is exact."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Decimal(str(node.value))          # str() avoids float artefacts
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")   # anything else is rejected

def safe_calc(expression: str) -> dict[str, Any]:
    """Return a structured result so the LLM can read success/failure."""
    if len(expression) > 200:                    # guard: limit input size
        return {"ok": False, "error": "expression too long"}
    try:
        value = _eval(ast.parse(expression, mode="eval").body)
        return {"ok": True, "result": str(value.quantize(Decimal("0.01")))}
    except (ValueError, SyntaxError, InvalidOperation, ZeroDivisionError) as exc:
        return {"ok": False, "error": str(exc) or type(exc).__name__}

# Tool schema sent to the model (this costs input tokens on EVERY call)
TOOLS: list[dict[str, Any]] = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Exact arithmetic. Use for any math. Operators: + - * / and parentheses.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "e.g. 48250*0.18"}},
            "required": ["expression"],
        },
    },
}]

async def ask_with_calculator(question: str) -> str:
    """Run one tool-calling loop (max 3 rounds) and return the final answer."""
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "You are a tariff assistant. Use calculator for all math."},
        {"role": "user", "content": question},
    ]
    for _ in range(3):                           # hard cap prevents infinite loops
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=TOOLS, max_tokens=300,
        )
        msg = resp.choices[0].message            # assistant message
        if not msg.tool_calls:                   # no tool needed -> final answer
            return msg.content or ""
        messages.append(msg)                     # keep the assistant tool_calls turn
        for call in msg.tool_calls:              # run every requested tool
            try:
                args = json.loads(call.function.arguments)   # arguments arrive as JSON text
                out = safe_calc(args["expression"])
            except (json.JSONDecodeError, KeyError) as exc:
                out = {"ok": False, "error": f"bad arguments: {exc}"}
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(out)})
    return "Could not finish within 3 rounds."

if __name__ == "__main__":
    print(safe_calc("48250*0.18"))               # works offline
    # print(asyncio.run(ask_with_calculator("Duty at 18% on Rs 48250?")))  # needs API key
```

---

## 🟠 FastAPI Integration
Expose the calculator both as a direct endpoint (for testing) and inside a chat endpoint that lets the LLM call it.

```python
from fastapi import FastAPI, HTTPException      # web framework
from pydantic import BaseModel, Field           # request validation (pydantic v2)

app = FastAPI()                                 # create app

class CalcRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=200)   # reject empty / huge input

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

@app.post("/tools/calculator")
async def calc_route(req: CalcRequest) -> dict:
    """Direct tool endpoint: handy for unit tests and dashboards."""
    result = safe_calc(req.expression)          # from the advanced example
    if not result["ok"]:
        raise HTTPException(status_code=422, detail=result["error"])  # bad expression
    return result

@app.post("/ask")
async def ask_route(req: AskRequest) -> dict:
    """LLM decides when to call the calculator."""
    try:
        answer = await ask_with_calculator(req.question)
    except Exception as exc:                    # network / rate-limit errors
        raise HTTPException(status_code=502, detail=f"LLM failed: {exc}")
    return {"answer": answer}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.tools import tool           # decorator that builds schema from type hints
from langchain_openai import ChatOpenAI         # chat model wrapper
from langgraph.prebuilt import create_react_agent  # ready-made tool-calling agent

@tool
def calculator(expression: str) -> str:
    """Exact arithmetic. Input like '48250*0.18'."""   # docstring = tool description for LLM
    return str(safe_calc(expression))           # reuse our safe evaluator

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)   # temperature 0 for deterministic tool use
agent = create_react_agent(llm, [calculator])   # LangGraph agent loop
result = agent.invoke({"messages": [("user", "Duty at 18% on Rs 48250?")]})
print(result["messages"][-1].content)           # final answer
```
LangChain also ships `LLMMathChain` / `numexpr` based tools, but writing your own `@tool` keeps control over safety.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `eval()` on model output
✅ Correct: Parse with `ast` and whitelist operators.

```python
# Wrong — remote code execution if the model (or an injected doc) emits malicious text:
result = eval(expression)

# Right — only arithmetic nodes are allowed:
result = _eval(ast.parse(expression, mode="eval").body)
```

❌ Mistake 2: Returning a Python traceback or raising from the tool
✅ Correct: Return a short error string the LLM can understand and retry.

```python
# Wrong — crashes the whole request:
def calculator(expression: str) -> float:
    return _eval(ast.parse(expression, mode="eval").body)   # ZeroDivisionError escapes

# Right — structured error goes back to the model:
def calculator(expression: str) -> str:
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as exc:
        return f"error: {exc}"
```

❌ Mistake 3: Using float for money
✅ Correct: Use `Decimal` (see advanced example).

---

## 🧠 Tricky Interview Question

**Q**: "Your calculator tool is safe from `eval`, yet an attacker still takes your server down with it. How?"

**Answer**: Denial of service through resource-heavy expressions, e.g. `9**9**9**9` or a 5 MB expression string. `ast` whitelisting blocks code execution but not CPU/memory exhaustion. Fixes: limit expression length, cap exponents, forbid `**` entirely if not needed, run the tool with a timeout (`asyncio.wait_for` or a subprocess), and rate-limit the endpoint.

---

## ⚫ Interview Questions + Answers

Q1: Why do LLMs need a calculator tool? (Easy)
A1: LLMs predict the next token from patterns; they do not run arithmetic. Large numbers, percentages and chained operations produce plausible but wrong answers. A tool gives exact results.

Q2: Why not use `eval()`? (Easy)
A2: `eval` executes arbitrary Python. Model output can be influenced by user input or injected documents, so it is a remote code execution risk. Use `ast.parse` with an operator whitelist.

Q3: How does the tool result get back to the model? (Medium)
A3: After the model returns `tool_calls`, you append the assistant message, then one `{"role": "tool", "tool_call_id": ..., "content": ...}` message per call, and call the API again. The model then writes the final answer.

Q4: When would you use `Decimal` instead of `float`? (Medium)
A4: For money, duty, tax. `0.1 + 0.2` is `0.30000000000000004` in float. Decimal gives exact base-10 results and controlled rounding with `quantize`.

Q5: Design a calculator tool for 1M requests per day with safety and low cost. (Hard)
A5: Pure-Python AST evaluator (no LLM cost for the math itself), input length and exponent limits, per-call timeout, structured `{ok, result|error}` output, a hard loop cap (3 rounds), cache identical expressions with `functools.lru_cache`, a short tool description (fewer schema tokens), and gpt-4o-mini with `temperature=0`. Add metrics for tool-call count and error rate; alert if the model keeps sending invalid expressions (prompt needs improvement).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any money, duty, tax, discount, unit conversion math
- Chained arithmetic or large numbers
- Results must be auditable

❌ Avoid when:
- Trivial math like `2 + 2` in a chat with no financial stakes (extra round trip costs tokens and latency)
- You need symbolic math or statistics (use sympy/numpy tool instead)

---

## 📊 Visual Diagram
```
User: "Duty at 18% on Rs 48250?"
        │
        ▼
   ┌─────────┐  tool_call: calculator("48250*0.18")
   │   LLM   │ ───────────────────────────────┐
   └─────────┘                                 ▼
        ▲                              ┌───────────────┐
        │  role=tool: "8685.0"         │ ast evaluator │
        └──────────────────────────────│  (whitelist)  │
                                       └───────────────┘
        │
        ▼
"Duty is Rs 8,685."
```

---

## 💰 Cost Impact
A calculator call adds a second LLM round trip: the tool schema (~80 tokens), the tool call (~30 output tokens) and the tool result plus history are re-sent as input. Roughly 250-400 extra tokens per question, about $0.00006 on gpt-4o-mini. The math itself costs zero tokens.

Optimize: keep the description short, send the tool only when the query contains numbers (simple regex gate), cache identical expressions, use `max_tokens`, and prefer gpt-4o-mini. A wrong money answer costs far more than the extra tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool call | Model asks your code to run a function | Model का function चलाने का अनुरोध |
| AST | Syntax tree of parsed code | Code का tree रूप |
| Whitelist | Only allowed operations are accepted | सिर्फ़ अनुमत operators |
| Decimal | Exact base-10 number type | सटीक दशमलव type |
| Prompt injection | Malicious text steering the model | Model को भटकाने वाला text |
| Tool schema | JSON description of a tool | Tool का JSON विवरण |

---

## ⚡ 3-Line Summary
English: LLMs cannot do reliable arithmetic, so give them a calculator tool. Never use `eval`; parse with `ast`, whitelist operators, use `Decimal` for money and return errors as strings. Cost is small (about 300 extra tokens) compared with the risk of a wrong number.
Hindi: LLM भरोसेमंद गणित नहीं कर सकता, इसलिए calculator tool दो। `eval` कभी नहीं, `ast` + whitelist + पैसे के लिए `Decimal` और errors string में लौटाओ। Extra cost सिर्फ़ ~300 tokens है, गलत number का नुकसान कहीं ज़्यादा है।

---

## ➡️ Next Topic
**287. Database Query Tool** — letting the LLM fetch tariff rates from SQL safely (read-only, parameterised queries).
