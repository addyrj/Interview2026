---

# 088. Tool Use for Structured Output
# हिंदी में: Structured Output के लिए Tool Use

---

## 🔵 Simple Definition (English)
Tool use (function calling) lets a model "call a function" by returning the function name and a JSON arguments object. If you define a tool whose parameters are the data you want and you never actually run it, the arguments become your structured output. It is the "extraction through a fake function" trick.

## 🔵 सरल परिभाषा (Hindi)
Tool use (function calling) में model function का नाम और JSON arguments object लौटाकर "function call" करता है। अगर आप ऐसा tool define करो जिसके parameters वही data हों जो आपको चाहिए, और tool को कभी run ही न करो, तो arguments आपका structured output बन जाते हैं। यह "नकली function से extraction" वाली trick है।

---

## 🔴 Problem it Solves
Older models and some providers lack a native JSON-schema mode, but they all support function calling. Tool use gives a schema-bound output on almost any model, and it also lets the model choose between several output shapes (e.g. `classify_product` vs `ask_clarification`).

## 🔴 यह क्यों बना? (Hindi)
पुराने models और कुछ providers में native JSON-schema mode नहीं होता, पर function calling लगभग सबमें होती है। Tool use लगभग हर model पर schema-bound output देता है, और model को कई output shapes में से चुनने देता है (जैसे `classify_product` बनाम `ask_clarification`)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define one or more tools (name, description, parameters schema)
Step 2 → Send tools + tool_choice (auto / required / specific function)
Step 3 → Model returns tool_calls with function.name and function.arguments (JSON string)
Step 4 → json.loads(arguments) -> dict   (OpenAI gives a string, Claude gives a dict)
Step 5 → Validate with Pydantic
Step 6 → Branch on name: classify -> save result, clarify -> ask the user
Step 7 → For pure extraction, stop here (no second LLM call)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → एक या ज़्यादा tools define करो (name, description, parameters schema)
Step 2 → tools + tool_choice (auto / required / specific function) भेजो
Step 3 → Model tool_calls लौटाता है: function.name और function.arguments (JSON string)
Step 4 → json.loads(arguments) -> dict   (OpenAI string देता है, Claude dict)
Step 5 → Pydantic से validate करो
Step 6 → name पर branch करो: classify -> result save, clarify -> user से पूछो
Step 7 → सिर्फ extraction हो तो यहीं रुको (दूसरी LLM call नहीं)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Two tools: `classify_product(hs_code, duty_percent)` and `ask_clarification(question)`. For "electronics" the model picks `ask_clarification("Which electronic item?")`; for "wireless earbuds" it picks `classify_product`. A single `response_format` cannot choose between two shapes this nicely.

**Zomato-style**: Tools `place_order`, `track_order`, `refund_request`; the model routes a chat message to the right structured action.

## 🟡 Real Example Hindi mein
**Tariff System**: दो tools: `classify_product(hs_code, duty_percent)` और `ask_clarification(question)`। "electronics" पर model `ask_clarification("कौन सा electronic item?")` चुनता है; "wireless earbuds" पर `classify_product`। एक `response_format` दो shapes के बीच ऐसे नहीं चुन सकता।

**Zomato-style**: Tools `place_order`, `track_order`, `refund_request`; model chat message को सही structured action पर route करता है।

---

## 💻 Code Example — Basic
```python
# Basic: define two tools and dispatch a simulated tool call. Runs offline.
import json                                              # arguments arrive as JSON text
from typing import Any, Callable                         # type hints

tools: list[dict[str, Any]] = [                          # OpenAI tools format
    {"type": "function", "function": {
        "name": "classify_product",                      # tool 1
        "description": "Return the HS classification.",
        "parameters": {"type": "object",
                       "properties": {"hs_code": {"type": "string"},
                                      "duty_percent": {"type": "number"}},
                       "required": ["hs_code", "duty_percent"]}}},
    {"type": "function", "function": {
        "name": "ask_clarification",                     # tool 2
        "description": "Ask the user for more detail.",
        "parameters": {"type": "object",
                       "properties": {"question": {"type": "string"}},
                       "required": ["question"]}}},
]

def handle_classify(args: dict[str, Any]) -> str:
    return f"Saved {args['hs_code']} @ {args['duty_percent']}%"   # pretend DB save

def handle_clarify(args: dict[str, Any]) -> str:
    return f"Ask user: {args['question']}"                        # pretend UI prompt

HANDLERS: dict[str, Callable[[dict[str, Any]], str]] = {          # name -> function
    "classify_product": handle_classify,
    "ask_clarification": handle_clarify,
}

def dispatch(name: str, arguments: str) -> str:
    """Parse the arguments string and call the right handler."""
    try:
        args = json.loads(arguments)                     # string -> dict
        return HANDLERS[name](args)                      # route by name
    except (json.JSONDecodeError, KeyError) as exc:      # bad JSON or unknown tool/key
        return f"error: {exc!r}"

print(dispatch("classify_product", '{"hs_code": "8518.30", "duty_percent": 0}'))
print(dispatch("ask_clarification", '{"question": "Which electronic item?"}'))
print(dispatch("unknown_tool", "{}"))                    # error path demo
```

## 💻 Code Example — Advanced
```python
# Production: OpenAI tool calling, forced/required choice, Pydantic validation, async.
import asyncio
import json
from typing import Union
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

client = AsyncOpenAI()

class Classify(BaseModel):                               # shape 1
    hs_code: str
    duty_percent: float = Field(ge=0, le=100)

class Clarify(BaseModel):                                # shape 2
    question: str

def to_tool(name: str, desc: str, model: type[BaseModel]) -> dict:
    """Build an OpenAI tool definition from a Pydantic model."""
    return {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": model.model_json_schema(), "strict": False}}

TOOLS = [to_tool("classify_product", "Classify when product is clear.", Classify),
         to_tool("ask_clarification", "Ask when product is vague.", Clarify)]

async def route(text: str) -> Union[Classify, Clarify, None]:
    """Let the model choose between two output shapes."""
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            tools=TOOLS,
            tool_choice="required",                      # must call one of the tools
            max_tokens=200,
        )
    except OpenAIError as exc:
        print("API error:", exc)
        return None
    calls = resp.choices[0].message.tool_calls or []     # may be empty on failure
    if not calls:
        return None
    call = calls[0]                                      # take the first call
    try:
        data = json.loads(call.function.arguments)       # JSON string -> dict
        if call.function.name == "classify_product":
            return Classify.model_validate(data)
        return Clarify.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        print("Bad tool arguments:", exc)
        return None

if __name__ == "__main__":
    print(asyncio.run(route("electronics")))             # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/smart-classify")
async def smart_classify(text: str) -> dict:
    out = await route(text)                              # tool-use router
    if out is None:
        raise HTTPException(status_code=502, detail="No valid tool call")
    kind = "classification" if isinstance(out, Classify) else "clarification"
    return {"type": kind, "data": out.model_dump()}      # client branches on `type`
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_tools = llm.bind_tools([Classify, Clarify])          # Pydantic classes become tools
msg = llm_tools.invoke("electronics")                    # AIMessage
print(msg.tool_calls)                                    # [{'name': 'Clarify', 'args': {...}}]
# LangGraph: conditional edge reads msg.tool_calls[0]["name"] to pick the next node.
# (with_structured_output(Union-like) is built on exactly this mechanism.)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating `arguments` as a dict on OpenAI
✅ Correct: It is a JSON string; parse it.

```python
# Wrong: call.function.arguments["hs_code"]   # TypeError
# Right: json.loads(call.function.arguments)["hs_code"]
```

❌ Mistake 2: Using `tool_choice="auto"` for extraction
✅ Correct: Use `"required"` or a specific function so a tool call always happens.

```python
# Wrong: tool_choice="auto"   -> model may answer in plain text, tool_calls is None
# Right: tool_choice={"type": "function", "function": {"name": "classify_product"}}
```

---

## 🧠 Tricky Interview Question

**Q**: "Native Structured Outputs exists. Why would you still use tool use?"

**Answer**: (1) Choosing between multiple output shapes (a union) — the model picks the tool. (2) Providers/models without native schema mode. (3) Real agent loops where the function *is* executed afterwards. (4) Portability across OpenAI, Claude and Gemini with the same pattern. Downside: a bit more token overhead and parsing steps; for a single fixed shape on OpenAI, native `parse()` is simpler.

---

## ⚫ Interview Questions + Answers

Q1: What is a tool call?
A1: The model's request to run a named function with JSON arguments; your code decides whether and how to run it.

Q2: How does tool use produce structured output?
A2: The arguments follow the tool's parameter schema, so you read them as your data and skip executing anything.

Q3: What does `tool_choice="required"` do?
A3: Forces the model to call at least one tool, preventing plain-text answers.

Q4: What if arguments JSON is invalid?
A4: Catch `JSONDecodeError`/`ValidationError`; retry with the error or fall back. With `strict: True` on OpenAI tools, arguments are guaranteed to match the schema.

Q5: How do you let the model return a list of items through tools?
A5: Either wrap the list in an object (`{"items": [...]}`) or allow parallel tool calls so each item is one call; the wrapper is more predictable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple possible output types
- Provider lacks native schema mode
- Agent workflows

❌ Avoid when:
- One fixed shape on a model with native strict mode
- You want the smallest prompt (tool definitions add tokens)

---

## 📊 Visual Diagram
```
 user: "electronics"
        │
        ▼
 ┌────────────── LLM sees tools ──────────────┐
 │ classify_product(hs_code, duty_percent)    │
 │ ask_clarification(question)                │
 └───────────────────┬────────────────────────┘
                     ▼ picks one
   tool_calls: [ask_clarification {"question": "Which item?"}]
                     ▼
        validate ─► branch ─► UI / DB
```

---

## 💰 Cost Impact
Every tool definition is input tokens on every call (~80-200 tokens each). Two tools = ~300 tokens extra. Output is small (just arguments).
Optimise: few tools with short descriptions, remove unused tools per request, prompt caching for the tools block, route cheap requests to `gpt-4o-mini`/Haiku.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool / function calling | Model requests a function | Model का function request |
| tool_choice | Controls tool use | Tool use नियंत्रण |
| arguments | JSON inputs for the tool | Tool के inputs |
| Union output | One of several shapes | कई shapes में से एक |
| Strict tool | Arguments guaranteed to match | Arguments की guarantee |

---

## ⚡ 3-Line Summary
English: Tool use turns function arguments into structured output, even if you never run the function. It shines when the model must choose between several shapes. Parse, validate and use `tool_choice` to force a call.
Hindi: Tool use में function के arguments ही structured output बन जाते हैं, भले function कभी run न हो। जब model को कई shapes में से चुनना हो तब यह बेहतरीन है। Parse, validate करो और call force करने के लिए `tool_choice` use करो।

---

## ➡️ Next Topic
**089. Parsing LLM Output** — what to do when you only have raw text: regex, JSON extraction and LangChain output parsers.
