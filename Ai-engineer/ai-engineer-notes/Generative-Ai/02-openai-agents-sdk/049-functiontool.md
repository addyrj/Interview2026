---

# 49. FunctionTool
# हिंदी में: FunctionTool (हाथ से tool बनाना)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). Both code samples were run offline with a scripted model. Verified: manual construction, `strict_json_schema` default True, `is_enabled` hiding a tool per run, `failure_error_function`, and pydantic validation errors being returned to the model as text.

---

## 🔵 Simple Definition (2-3 lines)
`FunctionTool` is the class behind `@function_tool`. You can build it directly with a `name`, `description`, a JSON schema for the arguments (`params_json_schema`) and an async `on_invoke_tool(ctx, args_json)` callable that parses the JSON string and returns the result.

## 🔵 सरल परिभाषा (Hindi)
`FunctionTool` वह class है जिस पर `@function_tool` बना है। आप इसे सीधे `name`, `description`, arguments का JSON schema (`params_json_schema`) और एक async `on_invoke_tool(ctx, args_json)` callable देकर बना सकते हैं, जो JSON string parse करके result लौटाता है।

---

## 🔴 Problem it Solves
The decorator infers everything from a Python signature, which is not enough when the schema comes from elsewhere (an OpenAPI spec, a database of tool definitions, a plugin system), when you need custom validation and error messages, or when you need to enable or hide a tool per run. `FunctionTool` gives that control.

## 🔴 यह क्यों बना? (Hindi)
Decorator सब कुछ Python signature से निकालता है, जो तब काफ़ी नहीं जब schema कहीं और से आता हो (OpenAPI spec, tool definitions का database, plugin system), जब custom validation और error messages चाहिए, या जब tool को run के हिसाब से enable/hide करना हो। `FunctionTool` यह नियंत्रण देता है।

---

## 🟢 How it Works

```
Step 1 -> Write on_invoke(ctx: ToolContext, args_json: str) -> str
Step 2 -> Parse + validate args_json yourself (json / pydantic)
Step 3 -> Build FunctionTool(name, description,
          params_json_schema, on_invoke_tool)
Step 4 -> Optional: is_enabled, timeout_seconds, needs_approval,
          strict_json_schema, tool guardrails
Step 5 -> Agent(tools=[tool]) -> model sees the schema
Step 6 -> Model call -> SDK calls on_invoke_tool -> result back
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> on_invoke(ctx: ToolContext, args_json: str) -> str लिखो
Step 2 -> args_json को खुद parse + validate करो (json / pydantic)
Step 3 -> FunctionTool(name, description,
          params_json_schema, on_invoke_tool) बनाओ
Step 4 -> Optional: is_enabled, timeout_seconds, needs_approval,
          strict_json_schema, tool guardrails
Step 5 -> Agent(tools=[tool]) -> model को schema दिखता है
Step 6 -> Model call -> SDK on_invoke_tool चलाता है -> result वापस
```

**Constructor verified in 0.24.0:** `FunctionTool(name, description, params_json_schema, on_invoke_tool, strict_json_schema=True, is_enabled=True, tool_input_guardrails=None, tool_output_guardrails=None, needs_approval=False, timeout_seconds=None, timeout_behavior='error_as_result', timeout_error_function=None, defer_loading=False, ...)`. Fields with a leading underscore are internal; do not use them.

**Strict schema:** with the default `strict_json_schema=True` the schema must set `additionalProperties: False` and list every property in `required`. Our advanced sample has an optional `qty` with a default, so we set `strict_json_schema=False`. Otherwise keep strict on: it makes the model's JSON more reliable.

**Invocation contract:** `on_invoke_tool(ctx: ToolContext, args_json: str) -> Awaitable[Any]`. You receive the raw JSON string and must parse it. A validation error should be RETURNED as a readable string (we returned `invalid arguments: Field required` and the model got it and could retry) or raised (then it goes through the failure function).

**`is_enabled`:** a bool or a callable `(RunContextWrapper, agent) -> bool`. We showed `tools_visible` differs for admin vs guest.

**Hindi नोट:** 90% मामलों में `@function_tool` काफ़ी है। `FunctionTool` तब लें जब schema dynamic हो या validation/enable-disable पर पूरा control चाहिए।

---

## 🟡 Real World Example
**Tariff Agent.** Customs rules for 40 countries are stored as JSON tool definitions in a database. At startup you loop over them and build one `FunctionTool` per rule with the stored schema; `is_enabled` hides export-control tools from users without clearance.

**Customer Support Agent:** auto-generate tools from an OpenAPI spec of the billing service.

## 🟡 Real Example Hindi mein
**Tariff Agent.** 40 देशों के customs नियम database में JSON tool definitions के रूप में रखे हैं। Startup पर आप उन पर loop करके हर नियम के लिए stored schema वाला एक `FunctionTool` बनाते हैं; `is_enabled` clearance-रहित users से export-control tools छिपा देता है।

**Customer Support Agent:** billing service के OpenAPI spec से tools अपने-आप बनाओ।

---

## 💻 Code Example — Basic
Runs offline. A hand-built `FunctionTool` is called by the scripted model; the printed values show the strict-schema default and no timeout.

```python
# Basic: build a FunctionTool by hand (no decorator) and call it (offline)
import asyncio                                           # async runner
import json                                              # args arrive as a JSON string
from agents import Agent, Runner, FunctionTool           # SDK
from agents.tool_context import ToolContext              # first arg of on_invoke_tool
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

async def on_invoke(ctx: ToolContext, args_json: str) -> str:   # contract: (ToolContext, str) -> result
    args = json.loads(args_json)                         # you parse + validate the JSON yourself
    code = args["code"]                                  # field defined in the schema below
    return {"6109.10": "20%"}.get(code, "unknown")       # return a string (or anything str()-able)

duty_tool = FunctionTool(                                # what @function_tool builds for you
    name="hs_duty",                                      # name the LLM calls
    description="Duty percent for an HS code.",          # shown to the LLM
    params_json_schema={                                 # JSON Schema of the arguments
        "type": "object",
        "properties": {"code": {"type": "string"}},
        "required": ["code"],
        "additionalProperties": False,                   # needed when strict_json_schema=True (default)
    },
    on_invoke_tool=on_invoke,                            # your callable
)

async def main() -> None:
    model = ScriptedModel([[function_call("hs_duty", {"code": "6109.10"}, call_id="c1")],
                           [assistant_message("20 percent")]])
    agent = Agent(name="Tariff Agent", instructions="x", model=model, tools=[duty_tool])
    res = await Runner.run(agent, "Duty?")
    print(res.final_output)
    print("strict schema:", duty_tool.strict_json_schema, "| timeout:", duty_tool.timeout_seconds)

asyncio.run(main())
```

## 💻 Code Example — Advanced
Pydantic-validated `FunctionTool` with `is_enabled` (hide per role), a custom `failure_error_function` on a decorated tool, and an invalid-arguments round trip. FastAPI + offline.

```python
# Advanced: FunctionTool with custom validation, is_enabled, needs_approval-free errors, FastAPI (offline)
import json                                              # parse args
from fastapi import FastAPI                              # web
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel, ValidationError          # validation
from agents import Agent, Runner, FunctionTool, RunContextWrapper, function_tool  # SDK
from agents.tool_context import ToolContext              # tool ctx
from agents.testing import ScriptedModel, assistant_message, function_call  # fake LLM

class DutyArgs(BaseModel):                               # single source of truth for schema + validation
    code: str
    qty: int = 1

async def invoke(ctx: ToolContext, raw: str) -> str:
    try:
        a = DutyArgs.model_validate_json(raw)            # strict validation of the LLM's JSON
    except ValidationError as e:                         # return a readable error so the LLM can self-correct
        return "invalid arguments: " + e.errors()[0]["msg"]
    return json.dumps({"code": a.code, "duty_pct": 20, "qty": a.qty})

def admin_only(ctx: RunContextWrapper[dict], agent) -> bool:   # is_enabled callable: hide tool from the LLM per run
    return ctx.context.get("role") == "admin"

duty = FunctionTool(
    name="hs_duty", description="Duty for an HS code.",
    params_json_schema={**DutyArgs.model_json_schema(), "additionalProperties": False},  # reuse pydantic schema
    on_invoke_tool=invoke,
    strict_json_schema=False,                            # needed because 'qty' has a default (not in 'required')
    is_enabled=admin_only,                               # dynamic visibility
)

@function_tool(failure_error_function=lambda ctx, e: f"tool failed safely: {type(e).__name__}")  # custom error text
def flaky(x: int) -> str:
    """Always fails (demo)."""
    raise RuntimeError("db down")

app = FastAPI()

@app.post("/ask/{role}")
async def ask(role: str) -> dict:
    model = ScriptedModel([[assistant_message("ok")]])
    agent = Agent[dict](name="Tariff Agent", instructions="x", model=model, tools=[duty, flaky])
    await Runner.run(agent, "hi", context={"role": role})
    return {"tools_visible": [t.name for t in model.calls[0].tools]}

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/ask/admin").json(), c.post("/ask/guest").json())   # is_enabled in action
    m = ScriptedModel([[function_call("flaky", {"x": 1}, call_id="1")], [assistant_message("handled")]])
    import asyncio
    r = asyncio.run(Runner.run(Agent(name="a", instructions="x", model=m, tools=[flaky]), "q"))
    print([i.output for i in r.new_items if i.type == "tool_call_output_item"])
    m2 = ScriptedModel([[function_call("hs_duty", {"qty": "many"}, call_id="1")], [assistant_message("retry")]])
    r2 = asyncio.run(Runner.run(Agent[dict](name="a", instructions="x", model=m2, tools=[duty]), "q", context={"role": "admin"}))
    print([i.output for i in r2.new_items if i.type == "tool_call_output_item"])
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Manual tool class | `StructuredTool.from_function` | `BaseTool` subclass | `FunctionTool(...)` | `FunctionTool` / `BaseTool` |
| Schema source | pydantic `args_schema` | pydantic `args_schema` | `params_json_schema` (any JSON Schema) | pydantic / signature |
| Dynamic enable | Bind tools per call | Per-agent tool lists | `is_enabled` bool/callable | Choose tools when creating agent |
| Timeouts | Via Runnable config | Tool-level options vary | `timeout_seconds`, `timeout_behavior` | Cancellation tokens |
| Approval gate | Interrupts / human-in-the-loop | `human_input` | `needs_approval` | User-proxy / approval handlers |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Strict schema with an optional field that has a default.
✅ Correct: Either list it in `required` (nullable) or set `strict_json_schema=False`.

❌ Mistake 2: Letting `json.loads` crash on bad model JSON with a stack trace.
✅ Correct: Validate with pydantic and return a short readable error string.

❌ Mistake 3: Returning non-serialisable objects.
✅ Correct: Return a string (or JSON string); the result is stringified for the model.

❌ Mistake 4: Using underscore-prefixed constructor fields.
✅ Correct: They are SDK internals and can change; stick to the public parameters.

❌ Mistake 5: Doing blocking I/O inside the async `on_invoke_tool`.
✅ Correct: Use async clients or `asyncio.to_thread`; blocking stalls the whole event loop.

---

## 🧠 Tricky Interview Question
The model keeps sending `qty` as the string `'many'` and your tool crashes with a 500 in production. The SDK has validation, so why did it crash, and what is the robust fix?

**Answer:** With a hand-built `FunctionTool` the SDK does NOT validate against your pydantic type; it hands you the raw JSON string and you own parsing. A decorated `@function_tool` validates for you, but a manual one only validates if you do it. Fix: parse with `Model.model_validate_json` in a try/except and return a short error such as `invalid arguments: qty must be an integer` so the model self-corrects on the next turn (we reproduced the round trip). Also keep `strict_json_schema=True` where possible so providers constrain generation, set a `timeout_seconds`, cap `max_turns` so a persistent bad-argument loop ends, and log validation failures as a metric for prompt/tool-description fixes.

---

## ⚫ Interview Questions + Answers

**Q1:** What is `FunctionTool` and when would you build it manually?

**A1:** The class `@function_tool` produces. Build it manually for dynamic schemas (OpenAPI, DB-defined tools), custom validation/error handling or runtime enablement.

**Q2:** What is the signature of `on_invoke_tool`?

**A2:** `async (ctx: ToolContext, args_json: str) -> Any`. You parse the JSON string yourself.

**Q3:** What does `strict_json_schema=True` require?

**A3:** `additionalProperties: False` and all properties in `required`; it makes model arguments more reliable. Disable only when you need optional fields.

**Q4:** How do you hide a tool for some users?

**A4:** `is_enabled` as a callable of `(RunContextWrapper, agent)`; we showed `['hs_duty','flaky']` for admin and `['flaky']` for guest.

**Q5:** Design a plugin system where teams register tools at runtime.

**A5:** Registry of `(name, JSON schema, handler)` loaded from config; wrap each in `FunctionTool` with pydantic validation and timeouts; namespace names; per-tenant `is_enabled`; `needs_approval` for write scopes; schema tests in CI; trace every call; version tool definitions so evals can pin them.

---

## 💰 Cost Impact
Each tool's name, description and schema are sent in every request, so verbose schemas cost tokens on every turn (estimate tens to a few hundred tokens per tool; measure with a tokenizer). Keep descriptions tight, drop unused properties, and use `is_enabled` to avoid sending irrelevant tools. Validation errors you return cost an extra model turn, so good descriptions that reduce bad arguments save money.

---

## 🔷 When to Use
✅ Use when:
- Schema comes from an external source
- Custom validation or error messages are required
- Per-run enable/disable, timeouts, approvals
- Wrapping a third-party SDK as a tool

❌ Avoid when:
- Plain Python functions where the decorator already works
- Complicated schemas the model keeps getting wrong (simplify the tool)

---

## 📊 Visual Diagram
```
  external schema (OpenAPI / DB)        Python function
            |                                  |
            v                                  v
  params_json_schema  +  on_invoke_tool(ctx, args_json)
            \                |
             +----> FunctionTool(name, description, ...)
                          |
                 is_enabled(ctx, agent)? --no--> hidden from model
                          | yes
                          v
                Agent(tools=[tool]) --> LLM sees schema
                          |
                  tool call JSON --> on_invoke_tool --> parse/validate
                          |                              |
                       result string  <---- or readable error string
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FunctionTool | Class representing a callable tool | callable tool को दर्शाने वाली class |
| params_json_schema | JSON Schema of tool arguments | tool arguments का JSON Schema |
| on_invoke_tool | Async callable that runs the tool | tool चलाने वाला async callable |
| is_enabled | Bool/callable to show or hide tool | tool दिखाने/छिपाने का bool/callable |
| Strict schema | Closed, fully-required schema | बंद, पूरी तरह required schema |

---

## ⚡ 3-Line Summary
English: `FunctionTool` is the explicit form of `@function_tool`: schema plus an async invoke function that parses JSON.
Use it for dynamic schemas, custom validation, timeouts and per-run enabling.
Return readable errors so the model can fix its arguments.

Hindi: `FunctionTool`, `@function_tool` का स्पष्ट रूप है: schema और JSON parse करने वाला async invoke function।
Dynamic schemas, custom validation, timeouts और per-run enabling के लिए इस्तेमाल करें।
पढ़ने योग्य errors लौटाएँ ताकि model अपने arguments सुधार सके।

---

## ➡️ Next Topic
**#50 FileSearchTool** - the first hosted tool: retrieval over OpenAI vector stores without writing your own RAG pipeline.

---
