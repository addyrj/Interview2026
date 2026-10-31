---

# 036. Claude — System Prompt Difference
# हिंदी में: Claude — System Prompt का फ़र्क

---

## 🔵 Simple Definition (English)
In Claude's Messages API, the system prompt is a separate top-level parameter called `system`, not a message with `role: "system"`. The `messages` list only contains `user` and `assistant` turns. The `system` value can be a plain string or a list of text blocks (which allows prompt caching with `cache_control`).

## 🔵 सरल परिभाषा (Hindi)
Claude की Messages API में system prompt एक अलग top-level parameter `system` है, `role: "system"` वाला message नहीं। `messages` list में सिर्फ़ `user` और `assistant` turns होते हैं। `system` की value साधारण string या text blocks की list हो सकती है (जिससे `cache_control` के साथ prompt caching संभव होती है)।

---

## 🔴 Problem it Solves
Mixing instructions and conversation in one list makes it easy for user text to impersonate instructions, and makes caching harder. A dedicated `system` field clearly separates "rules of the game" from "the conversation", keeps instructions stable across turns, and lets you cache a long static system prompt cheaply.

## 🔴 यह क्यों बना? (Hindi)
Instructions और conversation को एक list में मिलाने से user text के instructions की नकल करने का खतरा बढ़ता है और caching कठिन होती है। अलग `system` field "खेल के नियम" और "बातचीत" को साफ़ अलग रखता है, turns के बीच instructions स्थिर रखता है और लंबा static system prompt सस्ते में cache करने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write the rules, persona, format, and safety constraints as one system prompt
Step 2 → Pass it as system="..." (string) or system=[{type:"text", text:"...", cache_control:{...}}]
Step 3 → Pass only user/assistant turns in messages, starting with "user"
Step 4 → Claude reads system first, then the conversation
Step 5 → For multi-turn chat, re-send the same system with every request (API is stateless)
Step 6 → For long static prompts, mark a cache breakpoint with cache_control to reuse them cheaply
Step 7 → Keep dynamic data (user query, retrieved chunks) in messages, not in system
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Rules, persona, format और safety constraints एक system prompt में लिखो
Step 2 → उसे system="..." (string) या system=[{type:"text", text:"...", cache_control:{...}}] से दो
Step 3 → messages में सिर्फ़ user/assistant turns दो, "user" से शुरू करके
Step 4 → Claude पहले system पढ़ता है, फिर conversation
Step 5 → Multi-turn chat में हर request के साथ वही system दोबारा भेजो (API stateless है)
Step 6 → लंबे static prompts के लिए cache_control से cache breakpoint लगाओ ताकि सस्ते में reuse हो
Step 7 → Dynamic data (user query, retrieved chunks) messages में रखो, system में नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: The system prompt holds the 2,000-token rulebook: "You are a customs classification assistant. Use the General Rules of Interpretation. Output JSON with hs_code, confidence, and the note you relied on. Never invent codes." Each request only adds the product description. Marking the system prompt for caching means the 2,000 tokens are billed at the cheaper cached rate on repeat calls.

**Zomato AI**: System prompt defines persona and policy ("friendly, never promise refunds"), while each user message carries the actual question.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: System prompt में 2,000 tokens की rulebook है: "तुम customs classification assistant हो। General Rules of Interpretation use करो। hs_code, confidence और जिस note पर भरोसा किया वह JSON में दो। कभी codes गढ़ो मत।" हर request सिर्फ़ product description जोड़ती है। System prompt को caching के लिए mark करने पर दोहराई calls में उन 2,000 tokens का bill सस्ते cached rate पर बनता है।

**Zomato AI**: System prompt persona और policy तय करता है ("दोस्ताना, refund का वादा कभी नहीं"), जबकि हर user message में असली सवाल होता है।

---

## 💻 Code Example — Basic
```python
# Convert OpenAI-style messages to Claude format. Pure Python, runs offline.
from typing import Dict, List, Tuple                    # type hints

Msg = Dict[str, str]                                    # message type alias

def split_system(openai_messages: List[Msg]) -> Tuple[str, List[Msg]]:
    # Collect all system messages into one string
    system_parts = [m["content"] for m in openai_messages if m["role"] == "system"]
    # Keep only user and assistant turns for Claude's `messages`
    chat = [m for m in openai_messages if m["role"] in ("user", "assistant")]
    return "\n\n".join(system_parts), chat              # (system, messages)

openai_style = [
    {"role": "system", "content": "You are a tariff assistant."},   # rule 1
    {"role": "system", "content": "Answer in JSON."},               # rule 2
    {"role": "user", "content": "HS code for a power bank?"},       # question
]

system, messages = split_system(openai_style)           # split
print("system  :", system)                              # joined rules
print("messages:", messages)                            # only the user turn

# Real call:
# client.messages.create(model=MODEL, max_tokens=200, system=system, messages=messages)
```

## 💻 Code Example — Advanced
```python
# Claude call with a cached system prompt, sync + async, error handling
import asyncio                                           # async runner
import logging                                           # logs
import os                                                # env
from typing import Any, Dict, List, Optional             # type hints

import anthropic                                         # SDK

logger = logging.getLogger(__name__)                     # logger
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")   # configurable model id

RULEBOOK = (                                             # long static instructions
    "You are a customs classification assistant.\n"
    "Apply the General Rules of Interpretation in order.\n"
    'Return JSON: {"hs_code": str, "confidence": float, "note": str}.\n'
    "Never invent codes. If unsure, set confidence below 0.5."
)

# System as a list of blocks allows cache_control on the static part.
# Caching only takes effect when the prefix is long enough (see the docs for minimum size).
SYSTEM_BLOCKS: List[Dict[str, Any]] = [
    {"type": "text", "text": RULEBOOK, "cache_control": {"type": "ephemeral"}},
]

sync_client = anthropic.Anthropic(max_retries=3, timeout=60.0)
async_client = anthropic.AsyncAnthropic(max_retries=3, timeout=60.0)


def classify(product: str) -> Optional[str]:
    try:
        msg = sync_client.messages.create(
            model=MODEL, max_tokens=300, temperature=0,
            system=SYSTEM_BLOCKS,                        # top-level system (blocks form)
            messages=[{"role": "user", "content": f"Product: {product}"}],
        )
    except anthropic.BadRequestError as exc:             # e.g. invalid structure
        logger.error("bad request: %s", exc.message)
        return None
    except anthropic.APIError as exc:                    # any other API error
        logger.error("api error: %s", exc)
        return None
    # Cache metrics (present on usage when caching is used)
    logger.info("cache read=%s write=%s",
                getattr(msg.usage, "cache_read_input_tokens", None),
                getattr(msg.usage, "cache_creation_input_tokens", None))
    return "".join(b.text for b in msg.content if b.type == "text")


async def aclassify(product: str) -> Optional[str]:
    try:
        msg = await async_client.messages.create(
            model=MODEL, max_tokens=300, temperature=0, system=SYSTEM_BLOCKS,
            messages=[{"role": "user", "content": f"Product: {product}"}])
    except anthropic.APIError as exc:
        logger.error("async api error: %s", exc)
        return None
    return "".join(b.text for b in msg.content if b.type == "text")


if __name__ == "__main__":
    print(asyncio.run(aclassify("lithium power bank 10000mAh")))
```

---

## 🟠 FastAPI Integration
Keep the system prompt in one module-level constant (or load it from a versioned file), and never let users edit it directly.

```python
import os                                         # env
import anthropic                                  # SDK
from fastapi import FastAPI, HTTPException        # framework
from pydantic import BaseModel, Field             # pydantic v2

app = FastAPI()                                   # app
client = anthropic.AsyncAnthropic(max_retries=2, timeout=60.0)
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
SYSTEM_PROMPT = "You are a customs classification assistant. Return only the 6-digit HS code."


class Body(BaseModel):
    product: str = Field(min_length=2, max_length=500)    # limits abuse and cost


@app.post("/classify")
async def classify(b: Body) -> dict:
    try:
        msg = await client.messages.create(
            model=MODEL, max_tokens=30, temperature=0,
            system=SYSTEM_PROMPT,                          # server-controlled
            messages=[{"role": "user", "content": b.product}])   # user-controlled
    except anthropic.APIError:
        raise HTTPException(status_code=502, detail="AI service unavailable")
    return {"hs_code": "".join(x.text for x in msg.content if x.type == "text").strip()}
```

---

## 🔗 LangChain / LangGraph Connection
`ChatAnthropic` converts a LangChain `SystemMessage` into the top-level `system` automatically. Prompt templates with `("system", ...)` work the same for OpenAI and Claude, so your chain stays portable.

```python
from langchain_anthropic import ChatAnthropic              # Claude wrapper
from langchain_core.prompts import ChatPromptTemplate      # templates

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0, max_tokens=100)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a customs classification assistant. Return only the HS code."),
    ("human", "{product}"),
])
chain = prompt | llm      # the ("system", ...) tuple becomes Claude's top-level `system`
# print(chain.invoke({"product": "power bank"}).content)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A `{"role": "system"}` entry inside `messages`
✅ Correct: Use the `system=` argument.

```python
# Wrong — API returns a validation error (invalid role)
messages=[{"role": "system", "content": "rules"}, {"role": "user", "content": "hi"}]
# Right
system="rules", messages=[{"role": "user", "content": "hi"}]
```

❌ Mistake 2: Putting changing data (dates, user name) at the start of a cached system prompt
✅ Correct: Any change in the cached prefix invalidates the cache; put dynamic bits after the cache breakpoint or in `messages`.

❌ Mistake 3: Forgetting to re-send the system prompt each turn
✅ Correct: The API is stateless; send `system` on every call.

❌ Mistake 4: Trusting the system prompt as a security boundary
✅ Correct: Prompts can be bypassed by injection; enforce permissions and validation in code.

---

## 🧠 Tricky Interview Question

**Q**: "You enabled prompt caching on a 3,000-token system prompt, but your bill did not drop and `cache_read_input_tokens` is always 0. Why?"

**Answer**: Common causes: (1) the prefix changes on each call (a timestamp or user id inside the cached part), so there is no exact-match prefix; (2) the cached prefix is below the model's minimum cacheable length; (3) calls are spaced beyond the cache lifetime (short default TTL), so entries expire; (4) `cache_control` is placed on the wrong block, or tools/system ordering differs between calls; (5) requests are sent to different models. Fix: keep the cached prefix byte-identical, put dynamic content after it, verify size, and send traffic frequently enough, then check `usage.cache_creation_input_tokens` and `cache_read_input_tokens`.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you give Claude a system prompt?
A1: Pass the `system` parameter to `messages.create`, not a message with role `system`.

Q2: [Easy] What roles are allowed in Claude `messages`?
A2: `user` and `assistant`, alternating, starting with `user`.

Q3: [Medium] Can `system` be something other than a string?
A3: Yes, a list of text blocks, which lets you attach `cache_control` to cache long static instructions.

Q4: [Medium] Where should retrieved RAG chunks go?
A4: Into the `user` message (clearly delimited, e.g. in tags), because they change per request; keep the system prompt static and cacheable.

Q5: [Hard] How do you handle prompt injection given the system prompt design?
A5: Treat system text as guidance, not security. Wrap untrusted content in delimiters and tell the model it is data; validate outputs with schemas; restrict tools with least privilege and server-side checks; never put secrets in the prompt; log and test with adversarial inputs.

---

## 🔷 When to Use + When Not to Use
✅ Use the `system` field for:
- Persona, rules, output format, safety policy
- Long, stable instructions you want cached

❌ Avoid putting in `system`:
- Per-request data (user query, retrieved chunks)
- Secrets or credentials

---

## 📊 Visual Diagram
```
OpenAI:   messages = [ {system}, {user}, {assistant}, {user} ]

Claude:   system   = "rules ..."        <-- top-level (can be blocks + cache_control)
          messages = [ {user}, {assistant}, {user} ]

            +-- system (static, cacheable) --+
request ==> | rulebook 2,000 tokens          | ==> cached after first call
            +-- messages (dynamic) ----------+
            | "Product: power bank"          |
            +--------------------------------+
```

---

## 💰 Cost Impact
- System tokens count as input tokens on every call. A 2,000-token system prompt at 100K calls per day is 200M input tokens per day if not cached.
- Prompt caching: cached reads are billed at a fraction of normal input price (cache writes cost a bit more than normal input), so repeated long system prompts become much cheaper. Check the current pricing page for exact multipliers.
- Optimise: keep the system prompt tight, move rarely-needed rules into retrieval, put static content first, and monitor `cache_read_input_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| System prompt | Rules and persona for the model | Model के नियम और persona |
| Top-level parameter | Argument outside `messages` | `messages` के बाहर का argument |
| cache_control | Marks a cacheable prefix | Cache होने वाला prefix चिह्नित करना |
| Prompt caching | Reuse prefix cheaply | Prefix को सस्ते में reuse |
| Stateless | No memory between calls | Calls के बीच कोई memory नहीं |
| Prompt injection | Malicious text overriding rules | नियम बदलने वाला दुर्भावनापूर्ण text |

---

## ⚡ 3-Line Summary
English: Claude takes the system prompt in a top-level `system` field; `messages` hold only user and assistant turns. Keep `system` static so it can be cached, and put per-request data in `messages`. Do not rely on the system prompt for security.
Hindi: Claude में system prompt top-level `system` field में जाता है; `messages` में सिर्फ़ user और assistant turns होते हैं। `system` को static रखो ताकि cache हो सके, और per-request data `messages` में रखो। Security के लिए system prompt पर भरोसा मत करो।

---

## ➡️ Next Topic
**037. Claude — Content Blocks** — text, tool_use, tool_result, and image blocks inside messages.
