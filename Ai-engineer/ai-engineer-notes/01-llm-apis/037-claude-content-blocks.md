---

# 037. Claude — Content Blocks
# हिंदी में: Claude — Content Blocks

---

## 🔵 Simple Definition (English)
In Claude's API, message content is not just a string. It is a list of **content blocks**, each with a `type`: `text`, `image`, `tool_use`, `tool_result`, `thinking`, and more. A reply can contain several blocks (for example some text followed by a `tool_use` block). In requests you can send a plain string as shorthand for one text block.

## 🔵 सरल परिभाषा (Hindi)
Claude की API में message content सिर्फ़ string नहीं है। यह **content blocks** की list है, हर block का एक `type` होता है: `text`, `image`, `tool_use`, `tool_result`, `thinking` आदि। एक reply में कई blocks हो सकते हैं (जैसे थोड़ा text और उसके बाद `tool_use` block)। Request में आप एक text block की shorthand के रूप में सादी string भेज सकते हैं।

---

## 🔴 Problem it Solves
Modern LLM work is not only text. Models must return text AND ask to call a tool, accept images and documents, and sometimes show reasoning. A plain string cannot hold mixed content. Typed blocks make mixed, structured content explicit and machine-readable.

## 🔴 यह क्यों बना? (Hindi)
आज LLM का काम सिर्फ़ text नहीं है। Model को text लौटाना और साथ में tool call माँगना, images और documents लेना, और कभी reasoning दिखाना पड़ता है। साधारण string मिश्रित content नहीं रख सकती। Typed blocks मिश्रित content को साफ़ और machine-readable बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You send messages; content is a string OR a list of blocks
Step 2 → Block examples: {type:"text"}, {type:"image", source:{...}}, {type:"tool_result", ...}
Step 3 → Claude replies with message.content = [block, block, ...]
Step 4 → Loop over blocks and branch on block.type
Step 5 → type "text": show block.text to the user
Step 6 → type "tool_use": run your function using block.name and block.input, keep block.id
Step 7 → Send the next user message with a tool_result block: {tool_use_id: block.id, content: "..."}
Step 8 → stop_reason "end_turn" means done; "tool_use" means keep looping
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप messages भेजते हैं; content string या blocks की list होती है
Step 2 → Block उदाहरण: {type:"text"}, {type:"image", source:{...}}, {type:"tool_result", ...}
Step 3 → Claude message.content = [block, block, ...] के साथ जवाब देता है
Step 4 → Blocks पर loop चलाओ और block.type पर branch करो
Step 5 → type "text": block.text user को दिखाओ
Step 6 → type "tool_use": block.name और block.input से अपना function चलाओ, block.id रखो
Step 7 → अगला user message tool_result block के साथ भेजो: {tool_use_id: block.id, content: "..."}
Step 8 → stop_reason "end_turn" मतलब पूरा; "tool_use" मतलब loop जारी रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The user asks, "What is the duty on HS 8507.60 for imports from Japan?" Claude replies with two blocks: a `text` block ("I will check the duty table") and a `tool_use` block `get_duty(hs_code="8507.60", country="JP")`. Your code runs the lookup in the tariff database and sends back a `tool_result` block. Claude then writes the final text answer. A scanned invoice can also be sent as an `image` block for extracting the product description.

**Amazon-style AI**: A support bot gets a photo of a damaged parcel (image block) plus text, and calls an order-lookup tool.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: User पूछता है, "Japan से import पर HS 8507.60 की duty क्या है?" Claude दो blocks में जवाब देता है: एक `text` block ("मैं duty table देखता हूँ") और एक `tool_use` block `get_duty(hs_code="8507.60", country="JP")`। आपका code tariff database में lookup चलाकर `tool_result` block वापस भेजता है। फिर Claude अंतिम text जवाब लिखता है। Scanned invoice को भी `image` block के रूप में भेजकर product description निकाला जा सकता है।

**Amazon-style AI**: Support bot को टूटे parcel की photo (image block) और text मिलता है, और वह order-lookup tool call करता है।

---

## 💻 Code Example — Basic
```python
# Parse a Claude-style response with mixed blocks. Offline: we use plain dicts shaped like the real data.
from typing import Any, Dict, List                      # type hints

# A reply with text + a tool request (shape matches message.content as dicts)
content: List[Dict[str, Any]] = [
    {"type": "text", "text": "I will check the duty table."},
    {"type": "tool_use", "id": "toolu_01A", "name": "get_duty",
     "input": {"hs_code": "8507.60", "country": "JP"}},
]

def get_duty(hs_code: str, country: str) -> str:
    # Pretend database lookup
    return f"Duty for {hs_code} from {country}: 0%"

tool_results: List[Dict[str, Any]] = []                 # blocks we will send back
for block in content:                                   # walk through every block
    if block["type"] == "text":                         # plain text
        print("TEXT:", block["text"])
    elif block["type"] == "tool_use":                   # tool request
        result = get_duty(**block["input"])             # run our function
        tool_results.append({
            "type": "tool_result",                      # block type for the reply
            "tool_use_id": block["id"],                 # must match the tool_use id
            "content": result,                          # tool output as string
        })

# Next request: assistant turn (original content) + user turn (tool results)
next_messages = [
    {"role": "assistant", "content": content},
    {"role": "user", "content": tool_results},
]
print(next_messages[1])
```

## 💻 Code Example — Advanced
```python
# Full tool loop with Claude: handles blocks, errors, loop limit; sync + async
import asyncio                                           # async runner
import json                                              # to stringify tool output
import logging                                           # logs
import os                                                # env
from typing import Any, Callable, Dict, List             # type hints

import anthropic                                         # SDK

logger = logging.getLogger(__name__)                     # logger
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")   # configurable model id
client = anthropic.AsyncAnthropic(max_retries=3, timeout=60.0)

TOOLS: List[Dict[str, Any]] = [{                         # tool schema (JSON Schema for input)
    "name": "get_duty",
    "description": "Look up import duty percent for an HS code and country.",
    "input_schema": {
        "type": "object",
        "properties": {"hs_code": {"type": "string"}, "country": {"type": "string"}},
        "required": ["hs_code", "country"],
    },
}]


def get_duty(hs_code: str, country: str) -> Dict[str, Any]:
    return {"hs_code": hs_code, "country": country, "duty_percent": 0.0}   # fake DB


REGISTRY: Dict[str, Callable[..., Any]] = {"get_duty": get_duty}   # name -> function


async def run_agent(question: str, max_steps: int = 5) -> str:
    messages: List[Dict[str, Any]] = [{"role": "user", "content": question}]
    for _ in range(max_steps):                           # hard cap prevents infinite loops
        try:
            resp = await client.messages.create(
                model=MODEL, max_tokens=500, tools=TOOLS, messages=messages)
        except anthropic.APIError as exc:
            logger.error("API error: %s", exc)
            return "Sorry, the AI service is unavailable."
        if resp.stop_reason != "tool_use":               # no tool requested: finished
            return "".join(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": resp.content})   # keep blocks as-is
        results: List[Dict[str, Any]] = []
        for block in resp.content:
            if block.type != "tool_use":                 # skip text blocks
                continue
            try:
                out = REGISTRY[block.name](**block.input)        # run tool
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": json.dumps(out)})
            except Exception as exc:                     # report tool errors to Claude
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": f"Error: {exc}", "is_error": True})
        messages.append({"role": "user", "content": results})   # all results in ONE user turn
    return "Stopped: too many tool steps."


if __name__ == "__main__":
    print(asyncio.run(run_agent("Duty for HS 8507.60 from Japan?")))
```

---

## 🟠 FastAPI Integration
Expose the agent loop as an endpoint, and return only the final text and a short tool trace for audit.

```python
from fastapi import FastAPI, HTTPException            # framework
from pydantic import BaseModel                        # models
# Reuse run_agent from the module above (for example: from agent import run_agent)

app = FastAPI()                                       # app


class Ask(BaseModel):
    question: str


@app.post("/agent")
async def agent(a: Ask) -> dict:
    answer = await run_agent(a.question, max_steps=4)
    if answer.startswith("Sorry"):                    # simple failure signal in this demo
        raise HTTPException(status_code=502, detail=answer)
    return {"answer": answer}

# Image input (vision) example block you could build for an uploaded invoice:
# {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `AIMessage.content` from `ChatAnthropic` can be a string or a list of blocks (when tools or thinking are used). `message.tool_calls` gives a normalised list of tool requests, and `ToolMessage` carries results. LangGraph's prebuilt `create_react_agent` runs this loop for you.

```python
from langchain_anthropic import ChatAnthropic            # Claude wrapper
from langchain_core.tools import tool                    # tool decorator

@tool
def get_duty(hs_code: str, country: str) -> str:
    """Look up import duty percent for an HS code and country."""
    return f"Duty for {hs_code} from {country}: 0%"      # fake DB

llm = ChatAnthropic(model="claude-sonnet-4-5", max_tokens=500).bind_tools([get_duty])
# ai = llm.invoke("Duty for HS 8507.60 from Japan?")
# print(ai.content)       # may be a list of blocks (text + tool_use)
# print(ai.tool_calls)    # [{'name': 'get_duty', 'args': {...}, 'id': 'toolu_...'}]

# LangGraph: from langgraph.prebuilt import create_react_agent
# agent = create_react_agent(ChatAnthropic(model="claude-sonnet-4-5"), [get_duty])
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating `message.content` as a string
✅ Correct: Filter blocks by type.

```python
# Wrong — TypeError or prints a list repr
print(msg.content + "!")
# Right
text = "".join(b.text for b in msg.content if b.type == "text")
```

❌ Mistake 2: Dropping the assistant's `tool_use` blocks when sending the result back
✅ Correct: Append the full assistant content (with its `tool_use` blocks), then a user message with matching `tool_result` blocks.

❌ Mistake 3: Wrong `tool_use_id` or splitting parallel results into separate user messages
✅ Correct: Every `tool_use` id needs a `tool_result` with the same id, all returned together in one user message.

❌ Mistake 4: No loop limit
✅ Correct: Cap steps (`max_steps`) so a confused model cannot loop forever and burn tokens.

---

## 🧠 Tricky Interview Question

**Q**: "Claude returns `stop_reason: 'max_tokens'` while the last block is a half-written `tool_use`. What do you do?"

**Answer**: Never execute a truncated tool call: its JSON input may be incomplete or invalid. Treat `max_tokens` as a failure for that step: raise `max_tokens`, shorten the context, or simplify the tool schema, then retry the request. Also add validation of `block.input` against the schema (pydantic) before running any tool, and alert on truncation rates. This protects against running a tool with partial arguments.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is a content block?
A1: A typed piece of message content such as `text`, `image`, `tool_use`, or `tool_result`.

Q2: [Easy] How do you read text from a Claude reply?
A2: Join `block.text` for blocks where `block.type == "text"`.

Q3: [Medium] What is `tool_use` and how do you respond to it?
A3: Claude's request to call your function (with `id`, `name`, `input`). Run it, then send a user message with a `tool_result` block carrying the same `tool_use_id`.

Q4: [Medium] Can a message have multiple blocks?
A4: Yes, both in requests (text plus images) and in replies (text plus several tool_use blocks, enabling parallel tool calls).

Q5: [Hard] How do you make tool use safe in production?
A5: Validate inputs with schemas, restrict tools to least privilege, enforce authorisation in code (not in prompts), cap loop steps and token budgets, return tool errors with `is_error`, log every call for audit, and add timeouts and idempotency for side-effecting tools.

---

## 🔷 When to Use + When Not to Use
✅ Use blocks when:
- Tool calling, vision/documents, extended thinking, multi-part replies

❌ Avoid complexity when:
- A one-shot text answer is enough (just join text blocks)

---

## 📊 Visual Diagram
```
assistant message.content
 +-----------------------------------------------+
 | [0] {type:"text",     text:"Checking duty..."} |
 | [1] {type:"tool_use", id:"toolu_01A",          |
 |      name:"get_duty", input:{hs_code:...}}     |
 +-----------------------------------------------+
          | your code runs get_duty()
          v
user message.content
 +-----------------------------------------------+
 | [0] {type:"tool_result", tool_use_id:"toolu_01A",|
 |      content:"0%"}                              |
 +-----------------------------------------------+
          v
assistant: [{type:"text", text:"Duty is 0%."}]  stop_reason="end_turn"
```

---

## 💰 Cost Impact
- Tool definitions, tool_use blocks, and tool_result blocks are all tokens; each loop step re-sends the growing history, so long agent loops multiply input cost.
- Images are billed as input tokens based on their size; resize large images before sending.
- Optimise: cap steps, keep tool outputs short (return only needed fields), cache static tool definitions and system prompt, and summarise old tool results.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Content block | Typed piece of content | Typed content का हिस्सा |
| text block | Plain text piece | सादा text का टुकड़ा |
| tool_use | Claude asks to call a tool | Claude का tool call माँगना |
| tool_result | Your tool's output sent back | आपके tool का output वापस भेजना |
| tool_use_id | Links result to request | Result को request से जोड़ने वाली ID |
| stop_reason | Why generation ended | Generation क्यों रुका |

---

## ⚡ 3-Line Summary
English: Claude messages hold lists of typed content blocks (text, image, tool_use, tool_result). Loop over `message.content`, branch on `type`, and answer each `tool_use` with a matching `tool_result`. Validate tool inputs, cap loop steps, and never run truncated tool calls.
Hindi: Claude के messages में typed content blocks की list होती है (text, image, tool_use, tool_result)। `message.content` पर loop चलाओ, `type` पर branch करो और हर `tool_use` का जवाब matching `tool_result` से दो। Tool inputs validate करो, loop steps सीमित रखो और अधूरी tool calls कभी मत चलाओ।

---

## ➡️ Next Topic
**038. Claude — Streaming** — receive Claude replies token by token with the streaming helpers.
