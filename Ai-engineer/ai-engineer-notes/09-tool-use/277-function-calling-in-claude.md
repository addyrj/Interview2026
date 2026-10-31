---

# 277. Function Calling in Claude
# हिंदी में: Claude में Function Calling (Tool Use)

---

## 🔵 Simple Definition (English)
In Claude's API, function calling is called **tool use**. You describe tools with a name, description, and JSON `input_schema`. When Claude needs one, it stops with `stop_reason: "tool_use"` and returns a `tool_use` content block (id, name, input). You run the function and reply with a `tool_result` block, then Claude writes the final answer.

## 🔵 सरल परिभाषा (Hindi)
Claude के API में function calling को **tool use** कहते हैं। आप tools को name, description और JSON `input_schema` से बताते हैं। Claude को ज़रूरत हो तो वो `stop_reason: "tool_use"` के साथ रुकता है और `tool_use` content block (id, name, input) देता है। आप function चलाकर `tool_result` block से जवाब देते हैं, फिर Claude final जवाब लिखता है।

---

## 🔴 Problem it Solves
- LLMs cannot fetch live data or take actions by themselves (duty rates, databases, APIs).
- Parsing free text like "call get_duty(speakers)" is fragile.
- Tool use gives a structured, schema-checked contract between model and code.

## 🔴 यह क्यों बना? (Hindi)
- LLM खुद live data नहीं ला सकता या actions नहीं ले सकता (duty rates, databases, APIs)।
- "call get_duty(speakers)" जैसा free text parse करना कमज़ोर तरीका है।
- Tool use model और code के बीच structured, schema-वाला अनुबंध देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define tools: [{"name", "description", "input_schema": {JSON schema}}]
Step 2 → client.messages.create(model, max_tokens, tools=tools, messages=[user question])
Step 3 → Response: content = [text?, tool_use{id, name, input}], stop_reason = "tool_use"
Step 4 → Append the assistant response content to messages as-is
Step 5 → Run your function with block.input
Step 6 → Append a USER message: [{"type":"tool_result","tool_use_id": id,"content": "...", "is_error": false}]
Step 7 → Call again; stop_reason "end_turn" means a final text answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tools define करो: [{"name", "description", "input_schema": {JSON schema}}]
Step 2 → client.messages.create(model, max_tokens, tools=tools, messages=[user सवाल])
Step 3 → Response: content = [text?, tool_use{id, name, input}], stop_reason = "tool_use"
Step 4 → Assistant response का content जस का तस messages में जोड़ो
Step 5 → block.input से अपना function चलाओ
Step 6 → USER message जोड़ो: [{"type":"tool_result","tool_use_id": id,"content": "...", "is_error": false}]
Step 7 → फिर call करो; stop_reason "end_turn" का मतलब final text जवाब
```

---

## 🟡 Real World Example
**Tariff Classification System**: User: "What is the duty on a Bluetooth speaker?" Claude calls `get_duty({"product": "bluetooth speaker"})`. Your function queries the tariff DB and returns `{"hs_code": "8518.22", "duty_percent": 20}`. Claude then writes "Bluetooth speakers fall under HS 8518.22 with 20% duty."
**Zomato AI**: Claude calls `search_restaurants({"cuisine": "biryani", "max_price": 300})`.

## 🟡 Real Example Hindi mein
**Tariff System**: User: "Bluetooth speaker पर duty कितनी है?" Claude `get_duty({"product": "bluetooth speaker"})` बुलाता है। आपका function tariff DB से `{"hs_code": "8518.22", "duty_percent": 20}` लौटाता है। फिर Claude लिखता है "Bluetooth speakers HS 8518.22 में आते हैं, duty 20%।"
**Zomato AI**: Claude `search_restaurants({"cuisine": "biryani", "max_price": 300})` बुलाता है।

---

## 💻 Code Example — Basic
```python
# Basic: simulate Claude's tool-use message shapes with a fake client (no API key, runnable)
from typing import Any, Dict, List

TOOLS: List[Dict[str, Any]] = [{
    "name": "get_duty",
    "description": "Get import duty percent and HS code for a product.",
    "input_schema": {"type": "object",
                     "properties": {"product": {"type": "string"}},
                     "required": ["product"]},
}]

def get_duty(product: str) -> Dict[str, Any]:
    return {"hs_code": "8518.22", "duty_percent": 20} if "speaker" in product.lower() else {"error": "not found"}

def fake_claude(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pretend model: first turn asks for a tool; after a tool_result, answers."""
    last = messages[-1]
    if last["role"] == "user" and isinstance(last["content"], str):
        return {"stop_reason": "tool_use", "content": [
            {"type": "tool_use", "id": "toolu_01", "name": "get_duty", "input": {"product": "speaker"}}]}
    result = last["content"][0]["content"]                      # tool_result text
    return {"stop_reason": "end_turn", "content": [{"type": "text", "text": f"Result: {result}"}]}

def run(question: str) -> str:
    messages: List[Dict[str, Any]] = [{"role": "user", "content": question}]
    for _ in range(5):                                          # loop guard
        resp = fake_claude(messages)
        messages.append({"role": "assistant", "content": resp["content"]})   # step 4
        if resp["stop_reason"] != "tool_use":
            return "".join(b["text"] for b in resp["content"] if b["type"] == "text")
        results = []
        for block in resp["content"]:
            if block["type"] == "tool_use":
                out = get_duty(**block["input"])                # step 5
                results.append({"type": "tool_result", "tool_use_id": block["id"],
                                "content": str(out), "is_error": "error" in out})
        messages.append({"role": "user", "content": results})   # step 6: results go in a USER message
    return "step limit"

if __name__ == "__main__":
    print(run("Duty on a Bluetooth speaker?"))
```

## 💻 Code Example — Advanced
```python
# Production Claude tool loop: async, parallel tools, errors, token tracking
import asyncio
import json
from typing import Any

import anthropic  # pip install anthropic

client = anthropic.AsyncAnthropic()      # reads ANTHROPIC_API_KEY
MODEL = "claude-sonnet-4-5"              # use the model id your account has access to
MAX_STEPS = 6

TOOLS: list[dict[str, Any]] = [{
    "name": "get_duty",
    "description": "Get import duty percent and HS code for ONE product. "
                   "Call it once per product; do not guess duty rates.",
    "input_schema": {
        "type": "object",
        "properties": {"product": {"type": "string", "description": "Product name"}},
        "required": ["product"],
    },
}]

async def get_duty(product: str) -> dict[str, Any]:
    await asyncio.sleep(0.05)                                  # replace with a real lookup
    return {"product": product, "hs_code": "8518.22", "duty_percent": 20}

REGISTRY = {"get_duty": get_duty}

async def run_tool(block: Any) -> dict[str, Any]:
    """Execute one tool_use block and return a tool_result block (never raises)."""
    try:
        out = await asyncio.wait_for(REGISTRY[block.name](**block.input), timeout=5)
        return {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(out)}
    except KeyError:
        return {"type": "tool_result", "tool_use_id": block.id,
                "content": f"Unknown tool {block.name}", "is_error": True}
    except Exception as exc:                                   # tool failure goes back to Claude
        return {"type": "tool_result", "tool_use_id": block.id,
                "content": f"{type(exc).__name__}: {exc}", "is_error": True}

async def ask(question: str) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    in_tok = out_tok = 0
    for _ in range(MAX_STEPS):
        try:
            resp = await client.messages.create(
                model=MODEL, max_tokens=600, tools=TOOLS, messages=messages,
                system="You answer customs questions. Use tools for any duty or HS code.")
        except anthropic.RateLimitError:
            return {"error": "rate limited, retry later"}
        except anthropic.APIError as exc:
            return {"error": f"api error: {exc}"}
        in_tok += resp.usage.input_tokens
        out_tok += resp.usage.output_tokens
        messages.append({"role": "assistant", "content": resp.content})   # keep all blocks
        if resp.stop_reason != "tool_use":                                 # final answer
            text = "".join(b.text for b in resp.content if b.type == "text")
            return {"answer": text, "input_tokens": in_tok, "output_tokens": out_tok}
        tool_blocks = [b for b in resp.content if b.type == "tool_use"]
        results = await asyncio.gather(*(run_tool(b) for b in tool_blocks))  # parallel tools
        messages.append({"role": "user", "content": list(results)})         # ALL results in ONE user message
    return {"error": "step limit reached"}

if __name__ == "__main__":
    print(asyncio.run(ask("Duty on speakers and on headphones?")))   # needs ANTHROPIC_API_KEY
```

---

## 🟠 FastAPI Integration
Create the async client once, expose one endpoint, and return token usage.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Q(BaseModel):
    question: str = Field(min_length=3, max_length=1500)

@app.post("/claude/ask")
async def claude_ask(q: Q) -> dict:
    result = await ask(q.question)
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result
```

---

## 🔗 LangChain / LangGraph Connection
`langchain_anthropic.ChatAnthropic` supports `bind_tools`, so you write tools once with `@tool` and use them with OpenAI or Claude. The response is an `AIMessage` with `tool_calls`; LangGraph's `ToolNode` and `create_react_agent` run the loop for you.

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def get_duty(product: str) -> str:
    """Get import duty percent and HS code for ONE product."""
    return f"{product}: HS 8518.22, duty 20%"

agent = create_react_agent(ChatAnthropic(model="claude-sonnet-4-5"), [get_duty])
out = agent.invoke({"messages": [("user", "Duty on speakers?")]})
print(out["messages"][-1].content)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending the tool result as a separate `assistant` or `tool` role message (that is OpenAI style).
✅ Correct: In Claude, tool results go in a `user` message as `tool_result` blocks.

```python
# Wrong (OpenAI shape)
messages.append({"role": "tool", "tool_call_id": id, "content": "..."})
# Right (Claude shape)
messages.append({"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": id, "content": "..."}]})
```

❌ Mistake 2: Dropping the assistant's `tool_use` block from history (API error: tool_result without matching tool_use).
✅ Correct: Append `resp.content` unchanged before the results.

❌ Mistake 3: Putting tool_result blocks after text in the same message (tool_result blocks must come first), or splitting parallel results across several messages.
✅ Correct: One user message, all tool_result blocks first.

---

## 🧠 Tricky Interview Question
**Q**: "Claude returned `stop_reason: 'max_tokens'` while it was writing a tool call, and your code crashed on missing keys in `input`. What happened?"

**Answer**: The response was cut off mid-tool-call, so the `input` JSON is incomplete. Never execute a tool block when `stop_reason == "max_tokens"`. Detect it, retry with a larger `max_tokens` (tool arguments count as output), and keep tool schemas small. Always validate `input` against your schema before running, and treat model-produced arguments as untrusted input.

---

## ⚫ Interview Questions + Answers

Q1: What are the three parts of a Claude tool definition?
A1: `name`, `description`, and `input_schema` (JSON Schema). Description quality strongly affects when Claude uses the tool.

Q2: How do you know Claude wants to use a tool?
A2: `stop_reason == "tool_use"` and a `tool_use` content block with `id`, `name`, and `input`.

Q3: How do OpenAI and Claude differ in tool results?
A3: OpenAI: separate message `role: "tool"` with `tool_call_id`. Claude: a `user` message with `tool_result` blocks referencing `tool_use_id`. OpenAI arguments arrive as a JSON string; Claude gives a parsed object in `input`.

Q4: How do you force or disable tool use?
A4: `tool_choice`: `{"type": "auto"}` (default), `{"type": "any"}` (must use some tool), `{"type": "tool", "name": "get_duty"}` (specific tool), and `{"type": "none"}`. `disable_parallel_tool_use: true` can be added to limit to one tool.

Q5: How would you control cost and reliability for a Claude tool-using service?
A5: Short, precise tool descriptions (they cost input tokens every call), prompt caching for the stable system prompt + tools, small tool results, step limits, validate inputs, retries with backoff for 429/5xx, `is_error` results so Claude can recover, parallel tools for independent calls, and token tracking from `usage`. Use a smaller model (Haiku-class) for simple routing and a larger one for hard reasoning.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Claude needs live data or actions
- You need structured arguments (also good for structured extraction)
- Building agents

❌ Avoid when:
- A static prompt answers the question
- You can retrieve the data before the call and include it (simpler and cheaper)
- Tools would let the model take unsafe actions without confirmation

---

## 📊 Visual Diagram
```
 You ── messages + tools ──────────────► Claude
 You ◄─ stop_reason "tool_use" ───────── Claude  [text?, tool_use{id, name, input}]
 You: run get_duty(input)
 You ── user: [tool_result{tool_use_id}] ► Claude
 You ◄─ stop_reason "end_turn" ────────── Claude  [text: final answer]
```

---

## 💰 Cost Impact
- Tool definitions are input tokens on every request (about 100-300 tokens per tool); tool use also adds a small system overhead.
- Each loop turn re-sends history, including tool results.
- Example: 2 model calls, ~700 + ~1000 input tokens and ~150 output tokens in total. Cost depends on the model price, so check the current pricing page.
- Optimise: prompt caching for tools + system prompt (cached reads are much cheaper), compact results, `max_tokens` limits, parallel calls to save turns, and cheap models for simple tool routing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tool use | Claude's name for function calling | Claude में function calling का नाम |
| input_schema | JSON Schema of tool inputs | Tool inputs का JSON Schema |
| tool_use block | Claude's request to call a tool | Tool बुलाने का Claude का अनुरोध |
| tool_result block | Your reply with the output | आपका output वाला जवाब |
| stop_reason | Why generation stopped | Generation क्यों रुका |
| tool_choice | Controls tool selection | Tool चुनने पर नियंत्रण |
| is_error | Marks a failed tool result | Failed result का निशान |

---

## ⚡ 3-Line Summary
English: Claude tool use returns a tool_use block with stop_reason "tool_use"; you run the function and answer with a tool_result block in a user message. Keep the assistant blocks in history and send all parallel results together. Validate inputs, cap steps, and keep results small.
Hindi: Claude tool use में stop_reason "tool_use" के साथ tool_use block आता है; आप function चलाकर user message में tool_result block से जवाब देते हैं। Assistant blocks को history में रखो और parallel results एक साथ भेजो। Inputs validate करो, steps सीमित रखो और results छोटे रखो।

---

## ➡️ Next Topic
**278. Next topic in 09-tool-use**: continue with the tool-use series (structured outputs via tools, or the next item in the roadmap).
