---

# 278. Tool Use in Gemini
# हिंदी में: Gemini में Tool Use

---

## 🔵 Simple Definition (English)
Tool use in Gemini means you describe your Python functions to the model, and Gemini replies with a `function_call` (name + arguments) instead of plain text. Your code runs the function and sends the result back. With the `google-genai` SDK you can even pass a plain Python function and let the SDK do this loop for you ("automatic function calling").

## 🔵 सरल परिभाषा (Hindi)
Gemini में Tool Use का मतलब है: आप model को अपने Python functions का description देते हैं, और Gemini सीधा text देने की जगह `function_call` (नाम + arguments) लौटाता है। आपका code function चलाता है और result वापस भेजता है। `google-genai` SDK में आप सीधे Python function pass कर सकते हैं और SDK यह पूरा loop खुद चला देता है।

---

## 🔴 Problem it Solves
An LLM cannot look up live data (tariff rates, order status) and often invents numbers. Parsing free text like "call get_rate with hs=8517" is fragile. Gemini's function calling gives a structured, schema-checked way to ask your code for facts, so answers are grounded in real data.

## 🔴 यह क्यों बना? (Hindi)
LLM live data (tariff rate, order status) नहीं देख सकता और अक्सर numbers बना देता है। Free text से function name निकालना fragile है। Gemini function calling एक structured, schema-based तरीका देता है जिससे answer असली data पर आधारित रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a Python function with type hints + docstring (the description)
Step 2 → Pass it in GenerateContentConfig(tools=[fn]) (or build a FunctionDeclaration)
Step 3 → Gemini reads the user prompt and decides: answer directly OR call a tool
Step 4 → Response contains function_call: name="get_duty_rate", args={"hs_code": "8517"}
Step 5 → Your code validates args and runs the real function
Step 6 → Send result back as a function_response part
Step 7 → Gemini writes the final natural-language answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → type hints + docstring के साथ Python function लिखो
Step 2 → उसे GenerateContentConfig(tools=[fn]) में दो (या FunctionDeclaration बनाओ)
Step 3 → Gemini तय करता है: सीधे जवाब दे या tool call करे
Step 4 → Response में function_call आता है (नाम + args)
Step 5 → आपका code args check करके असली function चलाता है
Step 6 → Result को function_response part बनाकर वापस भेजो
Step 7 → Gemini final जवाब natural भाषा में लिखता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "What is the import duty on a smartphone (HS 8517)?" Gemini calls `get_duty_rate(hs_code="8517")`. Your code reads the tariff DB and returns `{"rate": 20.0}`. Gemini answers: "The basic duty is 20%." The model never guesses the number.

**Zomato AI**: "Where is my order?" becomes `get_order_status(order_id)`; Gemini explains the status politely.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "Smartphone (HS 8517) पर import duty कितनी है?" Gemini `get_duty_rate(hs_code="8517")` call करता है। आपका code DB से `{"rate": 20.0}` लौटाता है। Gemini कहता है "Basic duty 20% है।" Model कभी number अंदाज़े से नहीं बताता।

**Zomato AI**: "मेरा order कहाँ है?" → `get_order_status(order_id)` → Gemini आसान भाषा में बताता है।

---

## 💻 Code Example — Basic
```python
# Basic: simulate the Gemini function-calling loop offline (no API key needed)
# The real SDK call is shown in comments so you can swap it in later
from dataclasses import dataclass          # small containers for fake response objects
from typing import Any                     # type hint for flexible values

# Our real tool: a plain Python function with type hints and a docstring
def get_duty_rate(hs_code: str) -> dict[str, Any]:
    """Return the basic customs duty rate (percent) for an HS code."""
    rates: dict[str, float] = {"8517": 20.0, "6403": 25.0}   # tiny fake tariff table
    if hs_code not in rates:                                  # unknown code -> clear error
        return {"error": f"HS code {hs_code} not found"}
    return {"hs_code": hs_code, "rate_percent": rates[hs_code]}  # success payload

# Fake objects that look like Gemini's function_call
@dataclass
class FakeFunctionCall:
    name: str                              # which tool Gemini wants
    args: dict[str, Any]                   # arguments Gemini chose

# Registry: maps tool name -> Python callable (never trust names blindly)
TOOLS: dict[str, Any] = {"get_duty_rate": get_duty_rate}

def run_call(call: FakeFunctionCall) -> dict[str, Any]:
    """Execute a function call safely and always return a dict."""
    fn = TOOLS.get(call.name)              # look the tool up in the allow-list
    if fn is None:                         # model asked for unknown tool
        return {"error": f"unknown tool {call.name}"}
    try:
        return fn(**call.args)             # call with model-provided arguments
    except TypeError as exc:               # wrong / missing argument names
        return {"error": f"bad arguments: {exc}"}

# Real SDK equivalent (needs: pip install google-genai, GEMINI_API_KEY):
#   from google import genai
#   from google.genai import types
#   client = genai.Client()
#   resp = client.models.generate_content(
#       model="gemini-2.0-flash", contents="Duty on HS 8517?",
#       config=types.GenerateContentConfig(tools=[get_duty_rate]))
#   print(resp.text)   # SDK ran get_duty_rate automatically

call = FakeFunctionCall(name="get_duty_rate", args={"hs_code": "8517"})  # pretend Gemini said this
print(run_call(call))                                   # {'hs_code': '8517', 'rate_percent': 20.0}
print(run_call(FakeFunctionCall("get_duty_rate", {})))  # bad arguments error handled
```

## 💻 Code Example — Advanced
```python
# Production: manual function-calling loop with Gemini (google-genai SDK), async + error handling
import asyncio                                         # async runtime
import logging                                         # structured logs
from typing import Any                                 # type hints
from google import genai                               # Gemini SDK (pip install google-genai)
from google.genai import types                         # config / schema types

logger = logging.getLogger("gemini_tools")             # module logger
MODEL = "gemini-2.0-flash"                             # fast, cheap model with tool support
MAX_TURNS = 5                                          # hard stop to avoid infinite tool loops

# Explicit schema (use this when you want full control instead of auto-schema)
duty_decl = types.FunctionDeclaration(
    name="get_duty_rate",                              # tool name the model will emit
    description="Get basic customs duty percent for an HS code.",  # tells model WHEN to use it
    parameters=types.Schema(                           # OpenAPI-style JSON schema
        type=types.Type.OBJECT,
        properties={"hs_code": types.Schema(type=types.Type.STRING, description="4-10 digit HS code")},
        required=["hs_code"],
    ),
)
config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=[duty_decl])],   # register tool(s)
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),  # we run the loop
)

async def get_duty_rate(hs_code: str) -> dict[str, Any]:
    """Async tool body (would hit a DB in production)."""
    await asyncio.sleep(0)                              # placeholder for real async I/O
    return {"hs_code": hs_code, "rate_percent": 20.0}

async def ask_gemini(question: str) -> str:
    """Run the tool loop until Gemini returns plain text."""
    client = genai.Client()                             # reads GEMINI_API_KEY from env
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=question)])  # user turn
    ]
    for _ in range(MAX_TURNS):                          # bounded loop
        try:
            resp = await client.aio.models.generate_content(   # async call
                model=MODEL, contents=contents, config=config)
        except Exception as exc:                        # network / quota / API errors
            logger.exception("Gemini call failed")
            return f"Service error: {exc}"
        calls = resp.function_calls or []               # list of function_call objects
        if not calls:                                   # no tool needed -> final answer
            return resp.text or ""
        contents.append(resp.candidates[0].content)     # keep model turn in history
        parts: list[types.Part] = []
        for call in calls:                              # may be several parallel calls
            try:
                result = await get_duty_rate(**(call.args or {}))   # run tool
            except Exception as exc:                    # tool failure goes back to model
                result = {"error": str(exc)}
            parts.append(types.Part.from_function_response(name=call.name, response=result))
        contents.append(types.Content(role="user", parts=parts))    # send results back
    return "Stopped: too many tool turns"

if __name__ == "__main__":
    print(asyncio.run(ask_gemini("What is the duty on HS 8517?")))
```

---

## 🟠 FastAPI Integration
Expose the Gemini tool loop as an async endpoint. Create the client once and keep it reusable.

```python
# FastAPI + Gemini tool use
from fastapi import FastAPI, HTTPException            # web framework
from pydantic import BaseModel, Field                 # request validation

app = FastAPI()                                       # app instance

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)   # block empty / huge inputs

class AskResponse(BaseModel):
    answer: str                                       # final text

@app.post("/gemini/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    answer = await ask_gemini(req.question)           # from Advanced example above
    if answer.startswith("Service error"):            # surface upstream failure properly
        raise HTTPException(status_code=502, detail=answer)
    return AskResponse(answer=answer)
```

---

## 🔗 LangChain / LangGraph Connection
LangChain wraps Gemini with `ChatGoogleGenerativeAI` (package `langchain-google-genai`). `bind_tools` converts your `@tool` functions to Gemini declarations, so the same tool works with OpenAI, Claude and Gemini. In LangGraph, a `ToolNode` runs the calls.

```python
# LangChain + Gemini
from langchain_core.tools import tool                          # tool decorator
from langchain_google_genai import ChatGoogleGenerativeAI      # Gemini chat model

@tool
def get_duty_rate(hs_code: str) -> float:
    """Return basic customs duty percent for an HS code."""
    return 20.0                                                 # demo value

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")         # reads GOOGLE_API_KEY
llm_with_tools = llm.bind_tools([get_duty_rate])               # attach tools
msg = llm_with_tools.invoke("Duty for HS 8517?")               # AIMessage
print(msg.tool_calls)   # [{'name': 'get_duty_rate', 'args': {'hs_code': '8517'}, 'id': ...}]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Vague or missing docstring/description
✅ Correct: Gemini decides tool use from the description. Write when to use it.

```python
# Wrong - model cannot tell what this does
def f(x: str) -> dict: ...

# Right - clear name, typed params, docstring
def get_duty_rate(hs_code: str) -> dict:
    """Return basic customs duty percent for an HS code like '8517'."""
    ...
```

❌ Mistake 2: Running model-chosen function names without an allow-list, or looping forever
✅ Correct: Use a registry dict and a MAX_TURNS limit.

```python
# Wrong
result = globals()[call.name](**call.args)   # arbitrary code execution risk!

# Right
fn = TOOLS.get(call.name)
if fn is None:
    result = {"error": "unknown tool"}
```

---

## 🧠 Tricky Interview Question
**Q**: "You enabled automatic function calling, but your tool needs an auth token per user and must be logged for audit. The SDK keeps hiding the calls. What do you do?"

**Answer**: Automatic function calling runs your Python callables inside the SDK, so you cannot inject per-request context or audit each call cleanly. Disable it (`AutomaticFunctionCallingConfig(disable=True)`), declare tools with `FunctionDeclaration`, and run the loop yourself. Then you can log every call, pass the user's token via closure/context, enforce permissions, add timeouts, and cap turns. Automatic mode is great for prototypes; manual mode is for production.

---

## ⚫ Interview Questions + Answers

Q1: What does Gemini return when it wants to use a tool?
A1: A `function_call` part with `name` and `args`. In the SDK it is available as `response.function_calls`. The model does not execute anything; your code does.

Q2: What is automatic function calling in google-genai?
A2: You pass Python functions in `tools=[...]`; the SDK builds the schema from type hints and docstring, calls the function when Gemini asks, sends the result back and returns the final text. It saves boilerplate.

Q3: How do you send a tool result back to Gemini?
A3: Append the model's content to history, then add a user-role content with `types.Part.from_function_response(name=..., response={...})`. The `name` must match the call. Then call `generate_content` again.

Q4: How does Gemini handle parallel function calls?
A4: One response may contain multiple function calls. Run them (with `asyncio.gather` if independent) and return all responses in the same next turn, one part per call.

Q5: (Hard) How would you make Gemini tool use safe and reliable in production?
A5: Use manual loop; validate args with Pydantic; allow-list tools; timeouts and retries per tool; return errors as data so the model can recover; cap turns; log token usage and each call; keep tools read-only unless a human approves writes; use `tool_config` function-calling mode (`ANY`) with `allowed_function_names` when you must force a tool.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The answer needs live or private data (tariff DB, order status)
- You want structured arguments, not parsed text
- You already use Google Cloud / Gemini models

❌ Avoid when:
- A simple prompt answers the question (extra round trip costs tokens)
- Tools have side effects and no approval step exists
- You need identical behaviour across vendors without an abstraction like LangChain

---

## 📊 Visual Diagram
```
User question
     |
     v
+-----------+  function_call(get_duty_rate, hs=8517)  +-------------+
|  Gemini   | ------------------------------------->  | Your code   |
|  model    | <-------------------------------------  | runs tool   |
+-----------+   function_response({rate: 20.0})       +-------------+
     |
     v
"Basic duty is 20%"   (final answer)
```

---

## 💰 Cost Impact
- Each tool declaration is added to the input prompt, so 10 tools with long descriptions can cost hundreds of tokens on EVERY call.
- A tool round trip = 2 model calls (call + final answer); the second call re-sends history.
- Optimise: send only relevant tools per request, keep descriptions short, use Flash models for routing, cap `max_output_tokens`, return small tool results (not full DB rows), and read `resp.usage_metadata` for prompt/candidate token counts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| function_call | Model's request to run a tool | Model की tool चलाने की माँग |
| FunctionDeclaration | Schema describing a tool | Tool का schema/विवरण |
| function_response | Tool result sent back | Tool का नतीजा वापस भेजना |
| Automatic function calling | SDK runs the loop for you | SDK खुद loop चलाता है |
| genai.Client | Entry point of google-genai | Gemini SDK का client |
| Allow-list | Only permitted tools can run | सिर्फ़ मंज़ूर tools चलें |

---

## ⚡ 3-Line Summary
English: Gemini returns a function_call; your code runs the tool and sends back a function_response. The google-genai SDK can automate this, but production code should use a manual, bounded, logged loop. Tool schemas cost tokens on every request, so keep them lean.
Hindi: Gemini function_call देता है; आपका code tool चलाकर function_response भेजता है। SDK इसे automate कर सकता है, पर production में manual, सीमित और logged loop बेहतर है। Tool schemas हर request में tokens खाते हैं, इसलिए छोटे रखें।

---

## ➡️ Next Topic
**279. Tool Use in LangChain** — one tool interface that works across OpenAI, Claude and Gemini.
