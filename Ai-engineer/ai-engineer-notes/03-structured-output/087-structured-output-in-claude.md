---

# 087. Structured Output in Claude
# हिंदी में: Claude में Structured Output

---

## 🔵 Simple Definition (English)
Claude (Anthropic) historically had no `response_format` parameter. The standard way to get structured data is **tool use**: you define a tool whose `input_schema` is your JSON Schema and force Claude to call it, then read the tool's `input` as your structured data. Newer Anthropic structured-output features exist, but tool use is the portable, long-supported method.

## 🔵 सरल परिभाषा (Hindi)
Claude (Anthropic) में पारंपरिक रूप से `response_format` parameter नहीं था। Structured data पाने का standard तरीका **tool use** है: आप ऐसा tool define करते हो जिसका `input_schema` आपका JSON Schema हो, Claude को उसे call करने पर मजबूर करते हो, और tool का `input` आपका structured data होता है। नए Anthropic structured-output features भी हैं, पर tool use portable और लंबे समय से supported तरीका है।

---

## 🔴 Problem it Solves
Developers on Claude still need JSON that code can trust. Asking in the prompt is fragile. Tool use gives a schema-shaped argument object that the model is trained to fill accurately.

## 🔴 यह क्यों बना? (Hindi)
Claude पर भी developers को ऐसा JSON चाहिए जिस पर code भरोसा कर सके। सिर्फ prompt में माँगना कमजोर तरीका है। Tool use schema वाला argument object देता है जिसे model सही भरने के लिए trained है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a tool: {"name", "description", "input_schema": <JSON Schema>}
Step 2 → Call client.messages.create(tools=[tool], tool_choice={"type":"tool","name":...})
Step 3 → Claude must respond with a content block of type "tool_use"
Step 4 → Find the block: block.type == "tool_use"
Step 5 → block.input is a Python dict that follows your schema
Step 6 → Validate with Pydantic (Model.model_validate(block.input))
Step 7 → Use the object; no need to send a tool_result because it is only extraction
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tool लिखो: {"name", "description", "input_schema": <JSON Schema>}
Step 2 → client.messages.create(tools=[tool], tool_choice={"type":"tool","name":...}) call करो
Step 3 → Claude को "tool_use" type का content block देना ही होगा
Step 4 → Block ढूँढो: block.type == "tool_use"
Step 5 → block.input एक Python dict है जो आपके schema को follow करता है
Step 6 → Pydantic से validate करो (Model.model_validate(block.input))
Step 7 → Object use करो; सिर्फ extraction है तो tool_result भेजने की ज़रूरत नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: The same `TariffResult` schema is used with Claude as a fallback provider. If OpenAI is down, the router sends the request to Claude with a `record_tariff` tool. The rest of the pipeline cannot tell the difference.

**Zomato-style**: Claude reads a long customer complaint and fills a `Complaint` tool (category, severity, refund_needed).

## 🟡 Real Example Hindi mein
**Tariff System**: Claude के साथ वही `TariffResult` schema fallback provider के रूप में use होता है। OpenAI down हो तो router request को `record_tariff` tool के साथ Claude को भेजता है। Pipeline का बाकी हिस्सा फर्क नहीं जानता।

**Zomato-style**: Claude लंबी customer complaint पढ़कर `Complaint` tool भरता है (category, severity, refund_needed)।

---

## 💻 Code Example — Basic
```python
# Basic: build the tool definition and read a (simulated) tool_use block.
# Runs offline; the real call is in the comments.
from typing import Any                                 # type hint

tariff_tool: dict[str, Any] = {                        # Anthropic tool format
    "name": "record_tariff",                           # tool name
    "description": "Record the customs classification of a product.",
    "input_schema": {                                  # plain JSON Schema (not 'parameters')
        "type": "object",
        "properties": {
            "hs_code": {"type": "string", "description": "HS code like 8518.30"},
            "duty_percent": {"type": "number"},
        },
        "required": ["hs_code", "duty_percent"],       # required keys
    },
}

# Real call (needs ANTHROPIC_API_KEY):
# resp = client.messages.create(
#     model="claude-sonnet-4-5", max_tokens=300,
#     tools=[tariff_tool],
#     tool_choice={"type": "tool", "name": "record_tariff"},   # force this tool
#     messages=[{"role": "user", "content": "Wireless earbuds"}])
simulated_content: list[dict[str, Any]] = [            # what resp.content looks like
    {"type": "tool_use", "id": "toolu_1", "name": "record_tariff",
     "input": {"hs_code": "8518.30", "duty_percent": 0.0}},
]

def extract_tool_input(content: list[dict[str, Any]], name: str) -> dict[str, Any]:
    """Find the tool_use block with the given name and return its input."""
    for block in content:                              # loop over content blocks
        if block.get("type") == "tool_use" and block.get("name") == name:
            return block["input"]                      # the structured data
    raise ValueError("Claude did not call the tool")   # nothing found

print(extract_tool_input(simulated_content, "record_tariff"))   # {'hs_code': ..., ...}
```

## 💻 Code Example — Advanced
```python
# Production: Anthropic async client + forced tool + Pydantic validation.
# pip install anthropic pydantic
import asyncio                                         # runner
from typing import Optional
import anthropic                                       # SDK
from pydantic import BaseModel, Field, ValidationError

client = anthropic.AsyncAnthropic()                    # reads ANTHROPIC_API_KEY

class TariffResult(BaseModel):
    hs_code: str = Field(description="HS code like 8518.30")
    duty_percent: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)

TOOL = {                                               # schema derived from Pydantic
    "name": "record_tariff",
    "description": "Record the customs classification of a product.",
    "input_schema": TariffResult.model_json_schema(),  # reuse the model
}

async def classify(product: str) -> Optional[TariffResult]:
    """Force Claude to return TariffResult through tool use."""
    try:
        resp = await client.messages.create(
            model="claude-sonnet-4-5",                 # any current Claude model
            max_tokens=400,                            # cap output tokens
            temperature=0,
            system="You are a customs tariff classifier.",
            tools=[TOOL],
            tool_choice={"type": "tool", "name": "record_tariff"},   # forced
            messages=[{"role": "user", "content": product}],
        )
    except anthropic.APIError as exc:                  # network, rate limit, overloaded
        print("Anthropic error:", exc)
        return None
    print("tokens:", resp.usage.input_tokens, resp.usage.output_tokens)
    for block in resp.content:                         # find the tool call
        if block.type == "tool_use":
            try:
                return TariffResult.model_validate(block.input)   # validate dict
            except ValidationError as exc:
                print("Invalid:", exc.error_count(), "errors")
                return None
    return None                                        # no tool_use block

if __name__ == "__main__":
    print(asyncio.run(classify("Wireless earbuds")))   # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/classify-claude", response_model=TariffResult)
async def classify_claude(product: str) -> TariffResult:
    result = await classify(product)                   # Claude via tool use
    if result is None:
        raise HTTPException(status_code=502, detail="Claude returned no valid result")
    return result
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
structured = llm.with_structured_output(TariffResult)   # uses tool calling underneath
result = structured.invoke("Wireless earbuds")          # TariffResult
# Because both ChatOpenAI and ChatAnthropic support with_structured_output,
# a LangGraph router can swap providers without changing downstream nodes.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not forcing the tool (`tool_choice` omitted)
✅ Correct: Force it, or Claude may reply in plain text.

```python
# Wrong: tools=[TOOL]  (Claude may just chat)
# Right: tools=[TOOL], tool_choice={"type": "tool", "name": "record_tariff"}
```

❌ Mistake 2: Reading `resp.content[0].text`
✅ Correct: Find the `tool_use` block and read `.input`.

```python
# Wrong: data = json.loads(resp.content[0].text)   # AttributeError
# Right: data = next(b.input for b in resp.content if b.type == "tool_use")
```

---

## 🧠 Tricky Interview Question

**Q**: "You forced a tool with `tool_choice`, yet Claude's output is missing a required field once in a thousand calls. Is that a bug?"

**Answer**: Not a bug in the API; tool input is model-generated and the schema is guidance, not a hard grammar guarantee (unless you use Anthropic's strict/structured-output feature where available). Always validate with Pydantic, retry on failure, and put the schema constraints (enums, required) clearly. Also check `stop_reason == "max_tokens"`, which truncates tool input.

---

## ⚫ Interview Questions + Answers

Q1: How do you get JSON from Claude?
A1: Define a tool with an `input_schema`, force it with `tool_choice`, read the `tool_use` block's `input`.

Q2: What is the schema key name in Anthropic tools?
A2: `input_schema` (OpenAI uses `parameters`).

Q3: What is prefill and can it help?
A3: You can start the assistant message with `{` so Claude continues with JSON. It works for simple cases but tool use is safer. (Some newest models restrict prefill; check docs.)

Q4: Why validate after tool use?
A4: To guard against missing/wrong fields and apply business rules; schema adherence is high but not mathematically guaranteed in every mode.

Q5: How do you build a provider-agnostic classifier?
A5: Keep one Pydantic model; write thin adapters (OpenAI `parse`, Claude tool use) that return that model; route with a LangChain/LangGraph node or a simple function, with fallbacks on errors and shared validation after.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You use Claude models and need JSON
- Multi-provider fallback
- Long documents where Claude's large context helps

❌ Avoid when:
- The task is free text (no need for tools)
- You need a hard grammar guarantee and a provider offers it natively (consider that option)

---

## 📊 Visual Diagram
```
 TariffResult ─► input_schema ─► tools=[record_tariff]
                                   │ tool_choice = that tool
 user text ───────────────────────►▼
                              ┌──────────┐
                              │  Claude  │
                              └────┬─────┘
                                   ▼
        content: [ {type: "tool_use", input: {...}} ]
                                   ▼
                   TariffResult.model_validate(input)
```

---

## 💰 Cost Impact
The tool definition (name, description, schema) counts as input tokens on every call (about 100-300 tokens, plus a small system overhead for tool use). Output is only the arguments, so it is compact.
Optimise: use prompt caching on the tools + system prefix (cache reads are much cheaper), pick a smaller Claude model (Haiku class) for extraction, cap `max_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool use | Model calls a function with arguments | Model का function call |
| input_schema | JSON Schema of tool arguments | Arguments का schema |
| tool_choice | Force or allow tool calls | Tool call force करना |
| tool_use block | Content block with the arguments | Arguments वाला block |
| Prefill | Start of assistant reply you provide | Reply की शुरुआत खुद देना |

---

## ⚡ 3-Line Summary
English: With Claude, structured output is done via tool use: define `input_schema`, force the tool, read `block.input`. Validate with Pydantic afterwards. Prompt caching makes the tool definition cheap.
Hindi: Claude में structured output tool use से होता है: `input_schema` define करो, tool force करो, `block.input` पढ़ो। बाद में Pydantic से validate करो। Prompt caching से tool definition सस्ती हो जाती है।

---

## ➡️ Next Topic
**088. Tool Use for Structured Output** — the general technique (also on OpenAI) and when it beats native modes.
