---

# 273. Tool Definition Schema
# हिंदी में: Tool Definition Schema (Tool का नक्शा)

---

## 🔵 Simple Definition (English)
A tool definition is the "menu card" you show the model: a **name**, a **description** and a **JSON Schema** for the parameters. The model reads it to decide whether to call the tool and what arguments to send. OpenAI uses `{"type":"function","function":{name, description, parameters}}`; Claude uses `{name, description, input_schema}`; Gemini uses `function_declarations`.

## 🔵 सरल परिभाषा (Hindi)
Tool definition model को दिखाया जाने वाला "menu card" है: एक **name**, एक **description** और parameters का **JSON Schema**। Model इसे पढ़कर तय करता है कि tool call करना है या नहीं और कौन-से arguments भेजने हैं। OpenAI `{"type":"function","function":{name, description, parameters}}` use करता है; Claude `{name, description, input_schema}`; Gemini `function_declarations`।

---

## 🔴 Problem it Solves
If the definition is vague, the model picks the wrong tool, forgets required arguments, invents values ("hs_code": "electronics") or sends wrong types. Most "the agent is dumb" bugs are actually bad tool definitions. A good schema is the cheapest way to improve accuracy - no fine-tuning needed.

## 🔴 यह क्यों बना? (Hindi)
Definition अस्पष्ट हो तो model गलत tool चुनता है, ज़रूरी arguments भूल जाता है, मूल्य गढ़ लेता है ("hs_code": "electronics") या गलत type भेजता है। "Agent बेवकूफ़ है" वाले ज़्यादातर bugs असल में खराब tool definitions होते हैं। अच्छा schema accuracy बढ़ाने का सबसे सस्ता तरीका है - fine-tuning नहीं चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a clear verb_noun name: get_duty_rate (not "tool1", not "data")
Step 2 → Write a description: WHAT it does, WHEN to use it, WHEN NOT, what it returns
Step 3 → Define parameters as JSON Schema: type, description, enum, pattern, required
Step 4 → Mark required fields; set additionalProperties:false; use enums for fixed choices
Step 5 → (Optional) strict mode: OpenAI "strict": true guarantees arguments match the schema
Step 6 → Send in every request; the definition counts as input tokens
Step 7 → On the way back, STILL validate arguments in your code (Pydantic)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → साफ verb_noun नाम चुनो: get_duty_rate ("tool1" या "data" नहीं)
Step 2 → Description लिखो: क्या करता है, कब use करें, कब नहीं, क्या लौटाता है
Step 3 → Parameters JSON Schema में: type, description, enum, pattern, required
Step 4 → required fields तय करो; additionalProperties:false; fixed choices के लिए enum
Step 5 → (Optional) strict mode: OpenAI "strict": true से arguments schema से मेल खाने की गारंटी
Step 6 → हर request में भेजो; definition input tokens में गिनी जाती है
Step 7 → लौटने पर भी arguments अपने code में Pydantic से validate करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Two similar tools - `search_hs_codes(query)` (find candidates by text) and `get_duty_rate(hs_code, country)` (exact rate). Bad: both described as "tariff lookup". The model mixes them up and calls `get_duty_rate("earbuds", ...)`. Good: `get_duty_rate` says *"Use ONLY after you have a 6-digit HS code like 8518.30. Do not pass product names. Use search_hs_codes first if you only have a product name."* and the schema has `pattern: "^\\d{4}\\.\\d{2}$"`. Wrong calls drop sharply.

**Zomato-style**: `cuisine` as an enum (`north_indian`, `chinese`, ...) so the model cannot invent "desi food". **Amazon-style**: `sort_by` enum (`price_asc`, `rating_desc`).

## 🟡 Real Example Hindi mein
**Tariff System**: दो मिलते-जुलते tools - `search_hs_codes(query)` और `get_duty_rate(hs_code, country)`। खराब definition: दोनों "tariff lookup"। Model confuse होकर `get_duty_rate("earbuds", ...)` call कर देता है। अच्छी definition: *"सिर्फ तब use करो जब 8518.30 जैसा HS code मिल चुका हो। Product name मत दो। सिर्फ नाम हो तो पहले search_hs_codes।"* और schema में `pattern`। गलत calls बहुत घटते हैं।

**Zomato-style**: `cuisine` enum ताकि model "desi food" न गढ़े। **Amazon-style**: `sort_by` enum।

---

## 💻 Code Example — Basic
```python
# Basic: write a tool schema by hand AND generate one from Pydantic; validate sample arguments
# Runs OFFLINE.  pip install pydantic
import json                                                        # print schemas
from typing import Any, Literal                                    # type hints
from pydantic import BaseModel, Field, ValidationError             # pydantic v2

# 1) Hand-written OpenAI-style tool definition
get_duty_rate_tool: dict[str, Any] = {
    "type": "function",                                            # always "function"
    "function": {
        "name": "get_duty_rate",                                   # verb_noun, snake_case
        "description": (                                           # WHAT / WHEN / WHEN NOT / RETURNS
            "Get the import duty percent for a 6-digit HS code and origin country. "
            "Use ONLY when you already have an HS code like 8518.30; otherwise call search_hs_codes first. "
            "Returns {duty_percent: number}."
        ),
        "parameters": {                                            # JSON Schema
            "type": "object",
            "properties": {
                "hs_code": {"type": "string", "pattern": r"^\d{4}\.\d{2}$",
                            "description": "HS code in NNNN.NN format, e.g. 8518.30"},
                "country": {"type": "string", "enum": ["US", "VN", "CN", "IN"],
                            "description": "ISO-2 origin country"},
            },
            "required": ["hs_code", "country"],                    # both mandatory
            "additionalProperties": False,                         # no surprise extra fields
        },
    },
}

# 2) The SAME contract as a Pydantic model (single source of truth: schema + validation)
class DutyArgs(BaseModel):                                         # argument model
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$", description="HS code in NNNN.NN format, e.g. 8518.30")
    country: Literal["US", "VN", "CN", "IN"] = Field(description="ISO-2 origin country")

generated = DutyArgs.model_json_schema()                           # JSON Schema from the model
print(json.dumps(generated, indent=1)[:400], "...")               # preview generated schema

# 3) Validate what the model sent (always do this!)
good = '{"hs_code": "8518.30", "country": "VN"}'                   # correct arguments
bad = '{"hs_code": "earbuds", "country": "Vietnam"}'               # typical hallucination
print("good ->", DutyArgs.model_validate_json(good))               # passes
try:
    DutyArgs.model_validate_json(bad)                              # should fail
except ValidationError as exc:                                     # report which fields are wrong
    print("bad  ->", [e["loc"][0] for e in exc.errors()])          # ['hs_code', 'country']
```

## 💻 Code Example — Advanced
```python
# Production: schema registry built from Pydantic, strict mode, converters for OpenAI / Claude / Gemini
# pip install pydantic
import copy                                                        # deep copies of schemas
from typing import Any, Callable, Literal                          # hints

from pydantic import BaseModel, Field                              # pydantic v2


class ToolSpec:
    """One tool = name + description + Pydantic args model + async handler."""

    def __init__(self, name: str, description: str, args: type[BaseModel],
                 handler: Callable[..., Any]) -> None:
        self.name = name                                           # tool name
        self.description = description                             # model-facing text
        self.args = args                                           # validation model
        self.handler = handler                                     # real function

    def json_schema(self) -> dict[str, Any]:
        schema = copy.deepcopy(self.args.model_json_schema())      # base schema from pydantic
        schema.pop("title", None)                                  # titles are noise (tokens!)
        for prop in schema.get("properties", {}).values():         # strip per-field titles too
            prop.pop("title", None)
        schema["additionalProperties"] = False                     # required for OpenAI strict mode
        return schema

    def to_openai(self, strict: bool = False) -> dict[str, Any]:
        params = self.json_schema()                                # parameters block
        if strict:                                                 # strict: ALL fields must be required
            params["required"] = list(params.get("properties", {}))  # (optional ones -> nullable types)
        return {"type": "function", "function": {
            "name": self.name, "description": self.description,
            "parameters": params, **({"strict": True} if strict else {})}}

    def to_anthropic(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "input_schema": self.json_schema()}

    def to_gemini(self) -> dict[str, Any]:                         # goes inside tools=[{"function_declarations":[...]}]
        return {"name": self.name, "description": self.description, "parameters": self.json_schema()}


class SearchArgs(BaseModel):                                       # tool 1 arguments
    query: str = Field(min_length=2, max_length=200, description="Product name in plain English, e.g. 'wireless earbuds'")
    limit: int = Field(default=5, ge=1, le=10, description="Max candidates to return")


class DutyArgs(BaseModel):                                         # tool 2 arguments
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$", description="HS code NNNN.NN")
    country: Literal["US", "VN", "CN", "IN"] = Field(description="ISO-2 origin country")


async def search_hs_codes(a: SearchArgs) -> list[dict[str, str]]:  # handler stubs
    return [{"hs_code": "8518.30", "title": "Headphones and earphones"}][: a.limit]

async def get_duty_rate(a: DutyArgs) -> dict[str, float]:
    return {"duty_percent": 0.0}


REGISTRY: dict[str, ToolSpec] = {t.name: t for t in [
    ToolSpec("search_hs_codes",
             "Find candidate HS codes from a product description. Use FIRST when you only have a product name. "
             "Returns up to `limit` {hs_code, title} items.", SearchArgs, search_hs_codes),
    ToolSpec("get_duty_rate",
             "Get duty percent for an HS code (NNNN.NN) and origin country. Do NOT pass product names. "
             "Returns {duty_percent}.", DutyArgs, get_duty_rate),
]}


async def dispatch(name: str, raw_args: str) -> Any:
    """Validate then run. Unknown tool or bad args -> ValueError the caller turns into a tool message."""
    spec = REGISTRY.get(name)                                      # allow-list lookup
    if spec is None:
        raise ValueError(f"unknown tool: {name}")
    parsed = spec.args.model_validate_json(raw_args)               # raises ValidationError on bad args
    return await spec.handler(parsed)                              # run the real handler
```

---

## 🟠 FastAPI Integration
Serve your tool catalogue for debugging/documentation and keep schemas in one registry shared by the agent and the API. FastAPI already generates JSON Schema from Pydantic, so the *same* models can power both HTTP routes and LLM tools.

```python
# FastAPI: expose the registry + call a tool directly (for testing)
from fastapi import FastAPI, HTTPException                         # framework
from pydantic import ValidationError                               # validation error

app = FastAPI()                                                    # app

@app.get("/tools")                                                 # list tools in OpenAI format
async def list_tools(provider: Literal["openai", "anthropic", "gemini"] = "openai") -> list[dict[str, Any]]:
    conv = {"openai": lambda t: t.to_openai(), "anthropic": lambda t: t.to_anthropic(), "gemini": lambda t: t.to_gemini()}
    return [conv[provider](t) for t in REGISTRY.values()]          # schema for each provider

@app.post("/tools/{name}/call")                                    # direct call (admin/testing only)
async def call_tool(name: str, payload: dict[str, Any]) -> Any:
    import json                                                    # local import keeps snippet short
    try:
        return await dispatch(name, json.dumps(payload))           # validate + run
    except (ValueError, ValidationError) as exc:                   # bad tool/args -> 422
        raise HTTPException(status_code=422, detail=str(exc)) from exc
```

---

## 🔗 LangChain / LangGraph Connection
LangChain builds the definition for you. `@tool` uses the function name, **docstring** (description) and **type hints** (schema); `args_schema=PydanticModel` gives full control. `convert_to_openai_tool(tool)` shows the exact dict that will be sent.

```python
# LangChain: see the generated definition
from langchain_core.tools import tool                              # decorator
from langchain_core.utils.function_calling import convert_to_openai_tool  # converter
from pydantic import BaseModel, Field                              # schema

class DutyArgs2(BaseModel):                                        # explicit schema
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$", description="HS code NNNN.NN")
    country: str = Field(description="ISO-2 origin country")

@tool(args_schema=DutyArgs2)                                       # name = function name
def get_duty_rate(hs_code: str, country: str) -> str:
    """Get import duty percent for an HS code. Use only with a real HS code, not a product name."""
    return "0%"                                                    # real lookup here

print(convert_to_openai_tool(get_duty_rate))                       # exactly what the model will see
# llm.bind_tools([get_duty_rate]) works for OpenAI, Anthropic, Gemini with the same tool object
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Vague name and description
```python
# Wrong
{"name": "lookup", "description": "Looks up stuff", "parameters": {...}}

# Right
{"name": "get_duty_rate",
 "description": "Get import duty percent for an HS code (NNNN.NN) and country. Not for product names."}
```

❌ Mistake 2: Free-text string where an enum belongs
```python
# Wrong -- model sends "Vietnam", "VN", "vn", "VNM" ...
props = {"country": {"type": "string"}}

# Right
props = {"country": {"type": "string", "enum": ["US", "VN", "CN", "IN"]}}
```

❌ Mistake 3: Skipping server-side validation because "the schema says so". Without `strict` mode the model can still break the schema; with strict mode, the *values* can still be wrong (valid format, wrong HS code). Validate and check business rules.

❌ Mistake 4: Too many tools (30+) with overlapping descriptions - accuracy drops and tokens rise. Group, route, or send only relevant tools.

---

## 🧠 Tricky Interview Question

**Q**: "You marked `limit` as optional with default 5 and turned on OpenAI `strict: true`. The API rejects your schema. Why?"

**Answer**: In OpenAI **strict structured outputs**, every property must be listed in `required`, and `additionalProperties` must be `false`; "optional" is expressed as a nullable type, e.g. `"type": ["integer", "null"]`, and your code applies the default when it receives `null`. Some JSON Schema keywords (like `default`, and several validators such as `minLength`/`pattern` on older versions) are limited in strict mode, so keep the schema simple and enforce the rest with Pydantic after the call. Lesson: strict mode guarantees *shape*, not *truth* or business validity.

---

## ⚫ Interview Questions + Answers

Q1: What are the three parts of a tool definition?
A1: `name`, `description`, and parameter schema (`parameters` in OpenAI/Gemini, `input_schema` in Claude).

Q2: Why is the description so important?
A2: It is the only information the model has about when to use the tool. State purpose, when to use, when not to, input format examples, and what it returns. Changing a description often fixes wrong tool selection.

Q3: Why use `enum`?
A3: It limits the model to valid values, removing spelling and format variations, and makes validation trivial.

Q4: How do OpenAI and Claude formats differ?
A4: OpenAI: `{"type":"function","function":{"name","description","parameters"}}`, results go back as `role:"tool"`. Claude: `{"name","description","input_schema"}`, request comes as a `tool_use` content block and result goes as a `tool_result` block in a user message. Gemini: `function_declarations`. LangChain hides these differences.

Q5 (Hard): How do you keep schema/description token cost low with 40 tools while keeping accuracy?
A5: Two-stage routing: a cheap classifier (or embedding similarity on tool descriptions) selects the 5-8 relevant tools per request; remove `title` fields and verbose examples from schemas; share enum values; keep descriptions about 1-3 sentences; use provider prompt caching for the stable tool block (tools first in the prompt); group tools into sub-agents (a LangGraph supervisor with specialist agents holding 5-8 tools each). Measure with an eval set: tool-selection accuracy and arguments accuracy before/after.

---

## 🔷 When to Use + When Not to Use
✅ Write a careful schema when:
- A tool has arguments with constraints (formats, ranges, enums)
- Multiple tools look similar (needs "when to use / not use")
- You need structured extraction (a tool whose only job is the schema)

❌ Avoid when:
- Overloading one tool with many modes (`action: "search"|"delete"|...`) - split into separate tools
- Putting secrets, long docs or business rules in descriptions (costly tokens; use code)
- Allowing free-form SQL/shell as an argument

---

## 📊 Visual Diagram
```
 Tool definition (what the model sees)          Model output (what you get)
┌──────────────────────────────────────┐       ┌───────────────────────────────────┐
│ name: get_duty_rate                  │       │ tool_calls:                       │
│ description: Use ONLY with HS code.. │ ────► │  name: get_duty_rate              │
│ parameters (JSON Schema):            │       │  arguments: {"hs_code":"8518.30", │
│   hs_code: string, pattern NNNN.NN   │       │              "country":"VN"}      │
│   country: enum [US,VN,CN,IN]        │       └─────────────┬─────────────────────┘
│ required: [hs_code, country]         │                     ▼
└──────────────────────────────────────┘        Pydantic validate  ─► run handler
```

---

## 💰 Cost Impact
- Every definition is input tokens on EVERY call. A tool with a 60-word description and 3 parameters is about 120-200 tokens. 10 tools = ~1,500 tokens; 1M calls/month on gpt-4o-mini = 1.5B tokens x $0.15/1M = about $225/month just for tool definitions.
- Reduce: strip `title`, short descriptions, enums instead of long prose, send only relevant tools, prompt caching (cached input is cheaper on supported providers).
- Better definitions reduce wrong calls and retries, which saves far more than the tokens they cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSON Schema | Standard way to describe JSON shape | JSON की बनावट बताने का standard |
| description | Text telling the model when/how to use a tool | Tool कब/कैसे use हो |
| required | Fields that must be present | अनिवार्य fields |
| enum | Fixed list of allowed values | तय मूल्यों की सूची |
| strict mode | Provider guarantees schema-valid arguments | Schema-सही arguments की गारंटी |
| input_schema | Claude's name for the parameter schema | Claude में parameters schema |
| additionalProperties | Allow/deny extra keys | अतिरिक्त keys की अनुमति |

---

## ⚡ 3-Line Summary
English: A tool definition is name + description + JSON Schema, and it decides how well the model picks tools and arguments. Use clear names, "when to use / not use" text, enums and patterns, and generate schemas from Pydantic. Still validate in code; definitions cost input tokens on every call.
Hindi: Tool definition = name + description + JSON Schema, और यही तय करती है कि model सही tool और arguments चुनेगा या नहीं। साफ नाम, "कब use करें / नहीं" text, enums और patterns रखो और Pydantic से schema बनाओ। फिर भी code में validate करो; definitions हर call में input tokens खाती हैं।

---

## ➡️ Next Topic
**274. Tool Choice Parameter** - forcing, allowing or forbidding tool calls with `tool_choice` (`auto`, `required`, specific tool, `none`).
