---

# 307. Claude Agent
# हिंदी में: Claude Agent (Anthropic Tool Use वाला Agent)

---

## 🔵 Simple Definition (English)
A Claude agent is a loop around the Anthropic Messages API. You pass `tools`; Claude replies with `tool_use` content blocks and `stop_reason="tool_use"`. You run the tool and send back a `tool_result` block inside a user message. You repeat until `stop_reason="end_turn"`.

## 🔵 सरल परिभाषा (Hindi)
Claude agent Anthropic Messages API के आसपास बना loop है। आप `tools` देते हैं; Claude `tool_use` content block और `stop_reason="tool_use"` के साथ जवाब देता है। आप tool चलाकर user message में `tool_result` block वापस भेजते हैं। यह तब तक दोहराते हैं जब तक `stop_reason="end_turn"` न आ जाए।

---

## 🔴 Problem it Solves
Plain Claude can only generate text. It cannot look up live duty rates, query a database or send an email. Without a standard protocol every team invented its own text format and parser. Anthropic's tool use gives a typed, structured way for Claude to request actions and receive results.

## 🔴 यह क्यों बना? (Hindi)
अकेला Claude सिर्फ text लिख सकता है; live duty rate, database query या email नहीं कर सकता। हर team अपना text format बनाती थी। Anthropic का tool use एक typed, structured तरीका देता है जिससे Claude actions माँग सके और results पा सके।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define tools: name, description, input_schema (JSON schema)
Step 2 → client.messages.create(model, max_tokens, tools, messages)
Step 3 → Response content = [text block, tool_use block(id, name, input)]
Step 4 → If stop_reason == "tool_use": run each tool_use block
Step 5 → Append assistant content as-is to messages
Step 6 → Append user message: [tool_result(tool_use_id, content), ...]
Step 7 → Call again; loop until stop_reason == "end_turn"
Step 8 → Join text blocks as the final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tools define करो: name, description, input_schema
Step 2 → messages.create में tools और messages भेजो
Step 3 → Response में text और tool_use blocks आते हैं
Step 4 → stop_reason "tool_use" हो तो हर tool_use चलाओ
Step 5 → Assistant का content जैसा है वैसा messages में जोड़ो
Step 6 → User message में tool_result blocks (tool_use_id के साथ) जोड़ो
Step 7 → दोबारा call करो, जब तक "end_turn" न आए
Step 8 → Text blocks जोड़कर final answer दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer asks Claude "Classify: lithium power bank 10000mAh". Claude calls `lookup_hs_code`, gets candidates, then calls `check_restrictions` (lithium batteries have shipping rules) and writes a final answer with HS code plus a warning. Claude's long context also lets the agent read the full tariff notes.

**Amazon-style**: A support agent calls `get_order`, then `create_return_label`.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer पूछता है "Classify: lithium power bank 10000mAh"। Claude `lookup_hs_code` call करता है, फिर `check_restrictions` (lithium batteries के shipping नियम), और अंत में HS code के साथ warning देता है।
**Amazon**: Support agent `get_order` और फिर `create_return_label` call करता है।

---

## 💻 Code Example — Basic
```python
# Basic: Claude-style tool loop with a FAKE client (offline, pure Python).
from typing import Any                         # type hints

def lookup_hs_code(product: str) -> str:       # a simple tool
    return {"power bank": "8507.60"}.get(product.lower(), "UNKNOWN")  # fake DB

TOOLS = {"lookup_hs_code": lookup_hs_code}     # tool registry

class FakeClaude:                              # imitates response shape of the SDK
    def __init__(self) -> None:
        self.turn = 0                          # count calls

    def create(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        self.turn += 1                         # next turn
        if self.turn == 1:                     # first: request a tool
            return {"stop_reason": "tool_use", "content": [
                {"type": "text", "text": "Let me look that up."},
                {"type": "tool_use", "id": "tu_1", "name": "lookup_hs_code",
                 "input": {"product": "power bank"}}]}
        last = messages[-1]["content"][0]["content"]   # tool_result content
        return {"stop_reason": "end_turn",
                "content": [{"type": "text", "text": f"HS code is {last}"}]}

def run(question: str, max_steps: int = 5) -> str:
    client = FakeClaude()                      # fake client
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    for _ in range(max_steps):                 # bounded loop
        resp = client.create(messages)         # model call
        messages.append({"role": "assistant", "content": resp["content"]})  # keep as-is
        if resp["stop_reason"] != "tool_use":  # done?
            return "".join(b["text"] for b in resp["content"] if b["type"] == "text")
        results = []                           # collect tool_result blocks
        for block in resp["content"]:          # find tool_use blocks
            if block["type"] == "tool_use":
                out = TOOLS[block["name"]](**block["input"])   # run tool
                results.append({"type": "tool_result", "tool_use_id": block["id"], "content": out})
        messages.append({"role": "user", "content": results})  # results go in a USER message
    return "max_steps reached"

if __name__ == "__main__":
    print(run("Classify a power bank"))        # HS code is 8507.60
```

## 💻 Code Example — Advanced
```python
# Production: real anthropic SDK, async, error handling, type hints.
import asyncio                                 # async runtime
import json                                    # for serialising dict results
import logging                                 # logs
from typing import Any
import anthropic                               # pip install anthropic
from anthropic import AsyncAnthropic

log = logging.getLogger("claude_agent")        # logger
client = AsyncAnthropic()                      # reads ANTHROPIC_API_KEY
MODEL = "claude-sonnet-4-5"                    # use a current model id from your account

TOOLS: list[dict[str, Any]] = [{               # Anthropic uses "input_schema"
    "name": "lookup_hs_code",
    "description": "Return candidate HS codes for a product description.",
    "input_schema": {"type": "object",
                     "properties": {"product": {"type": "string"}},
                     "required": ["product"]}}]

async def lookup_hs_code(product: str) -> dict[str, Any]:   # async tool
    await asyncio.sleep(0)                     # pretend I/O
    return {"candidates": [{"code": "8507.60", "score": 0.93}]}

REGISTRY = {"lookup_hs_code": lookup_hs_code}  # name -> function

async def exec_tool(block: Any) -> dict[str, Any]:
    try:
        result = await REGISTRY[block.name](**block.input)  # run tool
        return {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
    except Exception as exc:                   # tell Claude about the failure
        return {"type": "tool_result", "tool_use_id": block.id,
                "content": f"Error: {exc}", "is_error": True}   # is_error flag is supported

async def run_agent(question: str, max_steps: int = 6) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    tokens_in = tokens_out = 0                 # usage counters
    for step in range(max_steps):
        try:
            resp = await client.messages.create(
                model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages,
                system="You are a customs tariff assistant. Use tools for facts.")
        except anthropic.RateLimitError:       # 429 -> back off
            await asyncio.sleep(2 ** step)
            continue
        except anthropic.APIStatusError as exc:  # other HTTP errors
            log.error("API status %s", exc.status_code)
            raise
        tokens_in += resp.usage.input_tokens   # input tokens
        tokens_out += resp.usage.output_tokens # output tokens
        messages.append({"role": "assistant", "content": resp.content})  # keep blocks
        if resp.stop_reason != "tool_use":     # finished
            text = "".join(b.text for b in resp.content if b.type == "text")
            return {"answer": text, "tokens_in": tokens_in, "tokens_out": tokens_out}
        calls = [b for b in resp.content if b.type == "tool_use"]
        results = await asyncio.gather(*[exec_tool(b) for b in calls])  # parallel
        messages.append({"role": "user", "content": list(results)})     # one user msg
    return {"answer": "max_steps reached", "tokens_in": tokens_in, "tokens_out": tokens_out}

if __name__ == "__main__":
    print(asyncio.run(run_agent("Classify a 10000mAh power bank")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException   # framework
from pydantic import BaseModel, Field        # validation

app = FastAPI()                              # app

class Req(BaseModel):                        # input
    question: str = Field(min_length=3)

@app.post("/claude-agent")                   # route
async def claude_agent(req: Req) -> dict:
    try:
        return await run_agent(req.question) # Advanced example above
    except Exception as exc:                 # map to HTTP error
        raise HTTPException(status_code=502, detail=str(exc))
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_anthropic import ChatAnthropic        # Claude wrapper
from langchain_core.tools import tool                # tool decorator
from langgraph.prebuilt import create_react_agent    # agent loop

@tool                                                # schema from type hints
def lookup_hs_code(product: str) -> str:
    """Return the HS code for a product."""
    return "8507.60"

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)   # same API under the hood
agent = create_react_agent(llm, [lookup_hs_code])    # loop handled for you
print(agent.invoke({"messages": [("user", "HS code for power bank?")]})["messages"][-1].content)
```
The same tool code works with OpenAI or Claude, because LangChain converts the schema for each provider.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending `tool_result` in an assistant or `tool` role message.
✅ Correct: Anthropic needs it inside a **user** message as a content block.

```python
# Wrong (OpenAI style)
messages.append({"role": "tool", "tool_call_id": id, "content": out})
# Right (Anthropic style)
messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": id, "content": out}]})
```

❌ Mistake 2: Dropping the assistant `tool_use` blocks from history.
✅ Correct: append `resp.content` unchanged, or the `tool_use_id` has nothing to match.

❌ Mistake 3: Putting the system prompt in `messages`.
✅ Correct: use the top-level `system=` parameter.

---

## 🧠 Tricky Interview Question
**Q**: "Claude returns text AND a tool_use block in the same turn. You ignore the text and only run the tool. What goes wrong?"

**Answer**: Nothing breaks in the API, but you lose the model's reasoning or user-facing text, and if you rebuild the assistant message from only the tool block, history differs from what Claude produced. Always store the full `content` list. If you want to show progress to users, display the text blocks while tools run. For extended thinking models, thinking blocks must also be passed back unchanged during tool use.

---

## ⚫ Interview Questions + Answers

Q1: What is `stop_reason` and which values matter for agents?
A1: It says why generation stopped: `tool_use` (run tools and continue), `end_turn` (done), `max_tokens` (cut off, increase limit), `stop_sequence`.

Q2: How does Claude's tool schema differ from OpenAI's?
A2: Claude uses `input_schema` at top level of each tool; OpenAI wraps `{"type":"function","function":{"parameters":...}}`. Arguments arrive as a parsed dict (`block.input`) in Claude, but as a JSON string in OpenAI.

Q3: Can Claude call tools in parallel?
A3: Yes, one response can contain several `tool_use` blocks. Run them concurrently and return all `tool_result` blocks in one user message.

Q4: Why is `max_tokens` required?
A4: Anthropic's API makes it mandatory. If it is too low, a `tool_use` block can be cut off (`stop_reason="max_tokens"`), giving broken input.

Q5: (Hard) How would you cut cost for an agent with a 4K-token system prompt and 12 tools?
A5: Use prompt caching: mark the system prompt and tools with `cache_control`, so repeated loop steps read them from cache at a much lower price. Also route simple questions to a smaller model, trim tool outputs, and cap steps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need long-context reading with tools (large tariff documents)
- You want careful instruction following in multi-step tasks
- You want tool use plus prompt caching

❌ Avoid when:
- A single prompt without tools is enough
- You need strict fixed order (use LangGraph)
- Very low latency is needed with a large model

---

## 📊 Visual Diagram
```
messages + tools ──► Claude
                       │
        stop_reason?   │
   ┌──── tool_use ◄────┤
   │                   └──── end_turn ──► final text
   ▼
run tools
   │
   ▼
user: [tool_result, ...] ──► back to Claude
```

---

## 💰 Cost Impact
Each loop sends the whole conversation again, so tokens grow per step. Tool definitions also count as input tokens.

Optimise: prompt caching (cache reads are billed far lower than normal input), smaller model for easy steps, short tool outputs (summarise before returning), `max_tokens` set sensibly, and step limits. Log `usage.input_tokens` and `usage.output_tokens` on every call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tool_use | Claude's request to run a tool | Tool चलाने की माँग |
| tool_result | Your reply with the output | Tool का output |
| stop_reason | Why Claude stopped | रुकने का कारण |
| input_schema | JSON schema of tool inputs | Tool inputs का schema |
| Content block | Typed piece of a message | Message का typed हिस्सा |
| Prompt caching | Reuse repeated prompt prefix cheaply | दोहराए prompt को सस्ते में reuse |

---

## ⚡ 3-Line Summary
English: A Claude agent loops on `stop_reason="tool_use"`, running tools and returning `tool_result` blocks inside a user message. Keep assistant content unchanged and handle errors with `is_error`. Use prompt caching to reduce the growing token cost.
Hindi: Claude agent `stop_reason="tool_use"` पर loop करता है, tools चलाता है और `tool_result` को user message में भेजता है। Assistant content जैसा है वैसा रखो और errors `is_error` से बताओ। बढ़ते token cost के लिए prompt caching इस्तेमाल करो।

---

## ➡️ Next Topic
**308. Agent Memory** — how agents remember earlier turns and facts across sessions.
