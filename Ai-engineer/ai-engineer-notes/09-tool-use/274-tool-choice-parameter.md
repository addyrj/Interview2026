---

# 274. Tool Choice Parameter
# हिंदी में: Tool Choice Parameter (Tool कब और कौन-सा चलेगा)

---

## 🔵 Simple Definition (English)
`tool_choice` is a request setting that controls whether the model may, must, or must not call a tool. Modes: **auto** (model decides), **required/any** (must call some tool), **specific tool** (must call this exact tool), **none** (no tool calls). It is the steering wheel of tool use.

## 🔵 सरल परिभाषा (Hindi)
`tool_choice` request की एक setting है जो तय करती है कि model tool call कर सकता है, करना ही होगा, या बिल्कुल नहीं कर सकता। Modes: **auto** (model तय करे), **required/any** (कोई न कोई tool ज़रूर), **specific tool** (यही tool ज़रूर), **none** (कोई tool नहीं)। यह tool use का steering wheel है।

---

## 🔴 Problem it Solves
With the default `auto`, the model might answer from memory instead of calling your lookup tool (hallucinated duty rate), or call a tool when you wanted plain text. For structured extraction you want a guaranteed JSON object every time. In a multi-step flow you may want "step 1 must be classification, no chit-chat". `tool_choice` makes the behaviour deterministic.

## 🔴 यह क्यों बना? (Hindi)
Default `auto` में model tool न बुलाकर अपनी याददाश्त से जवाब दे सकता है (गढ़ी हुई duty rate), या जहाँ सादा text चाहिए वहाँ tool बुला सकता है। Structured extraction में हर बार guaranteed JSON चाहिए। Multi-step flow में "step 1 में classification ही होगा" चाहिए। `tool_choice` से behaviour deterministic बनता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide the intent: free choice? force a tool? forbid tools?
Step 2 → Set the parameter in the request (format differs per provider)
Step 3 → auto     : model may answer in text OR call tool(s)
Step 4 → required : model must call at least one tool (OpenAI "required", Claude "any", Gemini "ANY")
Step 5 → specific : model must call exactly that tool (arguments still model-generated)
Step 6 → none     : tools are visible but cannot be called (useful for the final "summarize" turn)
Step 7 → Beware: forcing a tool every loop turn = infinite loop; switch back to auto/none after step 1
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Intent तय करो: खुली छूट? एक tool force करना? tools बंद करना?
Step 2 → Request में parameter सेट करो (format हर provider में अलग)
Step 3 → auto     : model text दे सकता है या tool बुला सकता है
Step 4 → required : कम से कम एक tool ज़रूर (OpenAI "required", Claude "any", Gemini "ANY")
Step 5 → specific : ठीक वही tool ज़रूर (arguments फिर भी model बनाता है)
Step 6 → none     : tools दिखते हैं पर बुला नहीं सकता (आखिरी "summarize" turn के लिए)
Step 7 → सावधान: हर loop turn में force करने से infinite loop; step 1 के बाद auto/none पर लौटो
```

---

## 🟡 Real World Example
**Tariff Classification System**: An extraction endpoint must always return `{hs_code, confidence}`. Define a tool `submit_classification` and set `tool_choice` to that tool: the model is forced to produce arguments in that schema - no prose. For the chat assistant: turn 1 uses `auto`; if the user asks "what is the duty on X?" we force `get_duty_rate` (policy: never answer rates from memory); the last turn uses `none` to produce the explanation.

**Zomato-style**: "Track my order" intent detected -> force `get_order_status`. **Amazon-style**: Return-policy question -> `none` (answer from the provided policy text, no search).

## 🟡 Real Example Hindi mein
**Tariff System**: Extraction endpoint को हमेशा `{hs_code, confidence}` लौटाना है। `submit_classification` tool बनाओ और `tool_choice` उसी पर रखो: model schema में arguments देने पर मजबूर है, कोई prose नहीं। Chat assistant में: turn 1 `auto`; user "X पर duty कितनी?" पूछे तो `get_duty_rate` force (policy: rate कभी याददाश्त से नहीं); आखिरी turn `none` ताकि समझाने वाला text बने।

**Zomato-style**: "Order track करो" intent मिला -> `get_order_status` force। **Amazon-style**: Return-policy सवाल -> `none` (दिए गए policy text से जवाब, search नहीं)।

---

## 💻 Code Example — Basic
```python
# Basic: translate one intent into each provider's tool_choice format + simulate model behaviour
# Runs OFFLINE (pure Python).
from typing import Any, Literal                                    # type hints

Mode = Literal["auto", "required", "specific", "none"]             # our provider-neutral modes


def tool_choice_for(provider: str, mode: Mode, name: str | None = None) -> dict[str, Any] | str:
    """Return the exact value to put in the request for each provider."""
    if provider == "openai":                                       # Chat Completions format
        if mode == "specific":                                     # force one function
            return {"type": "function", "function": {"name": name}}
        return {"auto": "auto", "required": "required", "none": "none"}[mode]   # plain strings
    if provider == "anthropic":                                    # Messages API format
        if mode == "specific":
            return {"type": "tool", "name": name}                  # force one tool
        return {"type": {"auto": "auto", "required": "any", "none": "none"}[mode]}  # "any" = must use a tool
    if provider == "gemini":                                       # function_calling_config
        cfg: dict[str, Any] = {"mode": {"auto": "AUTO", "required": "ANY", "specific": "ANY", "none": "NONE"}[mode]}
        if mode == "specific":                                     # ANY + one allowed name = forced tool
            cfg["allowed_function_names"] = [name]
        return {"function_calling_config": cfg}
    raise ValueError(f"unknown provider {provider}")               # defensive


def fake_model(mode: Mode, name: str | None, wants_tool: bool) -> str:
    """Tiny simulation of what each mode forces."""
    if mode == "none":
        return "TEXT (tools not allowed)"                          # never a tool
    if mode == "specific":
        return f"TOOL_CALL {name}"                                 # always that tool
    if mode == "required":
        return "TOOL_CALL <any>"                                   # some tool, never plain text
    return "TOOL_CALL <chosen>" if wants_tool else "TEXT"          # auto: model decides


for p in ("openai", "anthropic", "gemini"):                        # show formats side by side
    print(p.ljust(10), tool_choice_for(p, "specific", "get_duty_rate"))
print(tool_choice_for("anthropic", "required"))                    # {'type': 'any'}
for m in ("auto", "required", "specific", "none"):                 # show behaviours
    print(m.ljust(9), "->", fake_model(m, "get_duty_rate", wants_tool=False))
```

## 💻 Code Example — Advanced
```python
# Production: policy-driven tool_choice per step, forced structured output, async, safe loop
# pip install "openai>=1"
import json                                                        # parse arguments
import logging                                                     # logs
from typing import Any                                             # hints

from openai import AsyncOpenAI, APIError                           # client + error

logger = logging.getLogger("tariff.toolchoice")                    # logger
client = AsyncOpenAI(timeout=30, max_retries=2)                    # key from env

CLASSIFY_TOOL: dict[str, Any] = {                                  # "extraction tool": schema = desired output
    "type": "function",
    "function": {
        "name": "submit_classification",
        "description": "Submit the final HS classification for the product.",
        "parameters": {
            "type": "object",
            "properties": {
                "hs_code": {"type": "string", "pattern": r"^\d{4}\.\d{2}$"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["hs_code", "confidence"],
            "additionalProperties": False,
        },
    },
}
DUTY_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_duty_rate",
        "description": "Get duty percent for HS code NNNN.NN and ISO-2 country. Always use this; never quote rates from memory.",
        "parameters": {
            "type": "object",
            "properties": {"hs_code": {"type": "string"}, "country": {"type": "string"}},
            "required": ["hs_code", "country"],
        },
    },
}


async def extract_classification(product: str) -> dict[str, Any]:
    """Forced single tool => guaranteed structured output (no prose)."""
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=100,
            messages=[{"role": "user", "content": f"Classify: {product}"}],
            tools=[CLASSIFY_TOOL],
            tool_choice={"type": "function", "function": {"name": "submit_classification"}},  # force
            parallel_tool_calls=False,                             # exactly one call
        )
        call = resp.choices[0].message.tool_calls[0]               # forced => always present
        return json.loads(call.function.arguments)                 # still validate with Pydantic in real code
    except (APIError, IndexError, TypeError, json.JSONDecodeError) as exc:
        logger.error("forced extraction failed: %s", exc)          # log
        return {"hs_code": None, "confidence": 0.0, "error": "extraction_failed"}


def choice_for_step(step: int, user_text: str) -> Any:
    """Policy: rate questions force the lookup on step 0; later steps go back to auto; final = none."""
    asks_rate = any(w in user_text.lower() for w in ("duty", "rate", "tariff %"))   # simple intent check
    if step == 0 and asks_rate:
        return {"type": "function", "function": {"name": "get_duty_rate"}}   # never answer from memory
    return "auto"                                                  # never keep forcing -> loops


async def chat(user_text: str, max_steps: int = 4) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]
    for step in range(max_steps):
        last = step == max_steps - 1                               # last round: no more tools
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=[DUTY_TOOL], temperature=0,
            tool_choice="none" if last else choice_for_step(step, user_text),
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:
            return msg.content or ""
        for c in msg.tool_calls:                                   # run tools (stub result)
            messages.append({"role": "tool", "tool_call_id": c.id, "content": json.dumps({"duty_percent": 0})})
    return "Stopped"
```

---

## 🟠 FastAPI Integration
Expose intent-specific endpoints: `/extract` forces a schema tool (deterministic JSON), `/chat` uses auto with a policy. Different `tool_choice` per route keeps behaviour predictable and testable.

```python
# FastAPI: forced extraction route + auto chat route
from fastapi import FastAPI, HTTPException                         # framework
from pydantic import BaseModel, Field                              # validation

app = FastAPI()                                                    # app

class ProductReq(BaseModel):                                       # input
    product: str = Field(min_length=2, max_length=300)

class ChatReq(BaseModel):                                          # chat input
    text: str = Field(min_length=2, max_length=1000)

@app.post("/extract")                                              # always structured
async def extract(req: ProductReq) -> dict[str, Any]:
    data = await extract_classification(req.product)               # forced tool
    if data.get("error"):                                          # failed safely
        raise HTTPException(status_code=502, detail="extraction failed")
    return data

@app.post("/chat")                                                 # policy-driven
async def chat_route(req: ChatReq) -> dict[str, str]:
    return {"answer": await chat(req.text)}
```

---

## 🔗 LangChain / LangGraph Connection
`bind_tools(tools, tool_choice=...)` accepts a tool name (force that tool), `"any"`/`"required"` (force some tool), `"auto"`, or `"none"` for most providers - LangChain translates it. `with_structured_output(Schema)` is the same idea: it forces a schema tool (or JSON mode) under the hood.

```python
# LangChain: forcing a tool
from langchain_core.tools import tool                              # decorator
from langchain_openai import ChatOpenAI                            # model

@tool
def get_duty_rate(hs_code: str, country: str) -> str:
    """Get import duty percent for an HS code and ISO-2 country."""
    return "0%"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
forced = llm.bind_tools([get_duty_rate], tool_choice="get_duty_rate")   # must call this tool
anyone = llm.bind_tools([get_duty_rate], tool_choice="required")        # must call some tool
# forced.invoke("Duty for 8518.30 from VN?").tool_calls  -> always non-empty

# LangGraph: in a ReAct loop the agent node uses auto; use a separate "extract" node with a forced
# tool for the structured result, and route to END after it (no loop).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forcing a tool on every turn of an agent loop
```python
# Wrong -- model must call a tool again after getting the result => never reaches a final answer
while True:
    resp = call(messages, tool_choice="required")

# Right -- force only the first step, then auto; final step "none"
tool_choice = {"type": "function", "function": {"name": "get_duty_rate"}} if step == 0 else "auto"
```

❌ Mistake 2: Using the wrong format for the provider
```python
# Wrong -- OpenAI string sent to Claude
client.messages.create(..., tool_choice="required")      # 400 error: Claude expects {"type": "any"}

# Right
client.messages.create(..., tool_choice={"type": "any"})
```

❌ Mistake 3: Assuming a forced tool means correct arguments. The tool is called, but arguments can still be wrong/hallucinated - validate.

❌ Mistake 4: Forcing a tool when the user's message does not need it (e.g. "hi") - the model invents arguments to satisfy the demand. Use an intent check first.

---

## 🧠 Tricky Interview Question

**Q**: "With Claude you set `tool_choice={'type':'tool','name':'submit_classification'}` and also enabled extended thinking. The request fails. What is going on?"

**Answer**: With Claude extended thinking, forced tool use (`any` or a specific `tool`) is **not supported**; only `auto` or `none` work, because forcing a tool would constrain the model's reasoning flow. (Also, when you force a tool, the response may start directly with the `tool_use` block and skip text.) Options: keep thinking and use `auto` with a clear instruction to call the tool, or drop thinking and force the tool for pure extraction, or run two calls (reason first with thinking, then a cheap forced-tool call that formats the result). Always check the provider docs for such feature combinations - these restrictions change over time.

---

## ⚫ Interview Questions + Answers

Q1: What are the usual `tool_choice` values in OpenAI?
A1: `"auto"` (default when tools are given), `"none"`, `"required"`, or `{"type":"function","function":{"name":"..."}}` to force one function.

Q2: How do you guarantee structured JSON from a model using tools?
A2: Define a tool whose parameters schema is the desired output, force it with `tool_choice`, and read `tool_calls[0].function.arguments`. Or use native structured output / `with_structured_output`.

Q3: What is the Claude equivalent of OpenAI `required`?
A3: `{"type": "any"}`. A specific tool is `{"type": "tool", "name": "..."}`; `{"type": "none"}` disables tools; `{"type": "auto"}` lets the model decide. There is also `disable_parallel_tool_use: true` to limit to one call.

Q4: When would you use `none`?
A4: When tools must stay visible in the prompt (so the conversation format stays valid, history contains tool calls) but you want a plain-text final answer, e.g. after the max step count, or on a "summarize" turn.

Q5 (Hard): Design the tool_choice policy for a support agent with read tools and one dangerous write tool.
A5: Read tools: `auto`. Write tool: never force it. Expose it only after an explicit confirmation state in your own graph; at that state use a *specific* forced call with arguments built from validated, confirmed fields (or generate arguments by the model and verify them against the confirmed values in code). Before confirmation, exclude the write tool from `tools` entirely (stronger than `none`, because the model cannot even see it). Keep a step limit, log every forced call, and return to `auto` afterwards. Test that prompt-injection text cannot move the graph into the confirmed state.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need guaranteed structured output (force a schema tool)
- A policy says "always look it up" (force the lookup tool)
- Final answer turn must be text (`none`)
- Classification/routing step must pick a tool

❌ Avoid when:
- Open conversation where the model should decide (use `auto`)
- Every loop turn (infinite loop)
- Provider/feature combos that disallow it (e.g. forced tool + extended thinking on Claude)

---

## 📊 Visual Diagram
```
 tool_choice      model may reply with text?   must call a tool?   which tool?
 ───────────────  ──────────────────────────   ─────────────────   ───────────
 auto             yes                          no (decides)        model picks
 required / any   no                           yes                 model picks
 specific tool    no                           yes                 exactly that one
 none             yes (only text)              no (forbidden)      -

 Agent loop policy:
   step 0: specific (get_duty_rate)  ─► tool result ─► step 1..n-1: auto ─► last: none ─► final text
```

---

## 💰 Cost Impact
- `tool_choice` itself adds a few tokens. Forced tools save money by removing wasted rounds: a forced call returns the structured result in ONE request instead of "text -> retry -> parse failed -> retry".
- Forcing the lookup prevents costly wrong answers (a wrong duty rate has real-money impact).
- `none` on the last turn prevents extra tool rounds (each round re-sends the whole history: 1,500 tokens x $0.15/1M = $0.000225 on gpt-4o-mini).
- Optimize: force + `max_tokens` small for extraction (e.g. 100), `parallel_tool_calls=False` when only one call is wanted, cheap model for forced extraction.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tool_choice | Setting controlling tool calling | Tool calling का नियंत्रण |
| auto | Model decides | Model तय करे |
| required / any | Must call some tool | कोई tool ज़रूर |
| Forced tool | Must call a named tool | नाम वाला tool ज़रूर |
| none | Tools disabled for this turn | इस turn tools बंद |
| parallel_tool_calls | Allow several calls in one turn | एक turn में कई calls |
| Extraction tool | Tool used only to get structured output | सिर्फ structured output के लिए tool |

---

## ⚡ 3-Line Summary
English: `tool_choice` decides if the model may, must, or must not call tools: auto, required/any, specific, none (formats differ per provider). Force a schema tool for guaranteed JSON and force lookups by policy, but never force on every loop turn. Always validate arguments.
Hindi: `tool_choice` तय करता है कि model tool बुला सकता है, बुलाना ही होगा, या नहीं बुला सकता: auto, required/any, specific, none (format provider के हिसाब से अलग)। Guaranteed JSON के लिए schema tool force करो और policy से lookup force करो, पर हर loop turn में force मत करो। Arguments हमेशा validate करो।

---

## ➡️ Next Topic
**275. Parallel Tool Calls** - when the model asks for several tools in one turn and how to run them concurrently and return all results correctly.
