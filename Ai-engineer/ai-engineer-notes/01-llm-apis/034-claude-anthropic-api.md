---

# 034. Claude (Anthropic) API
# हिंदी में: Claude (Anthropic) API

---

## 🔵 Simple Definition (English)
The Anthropic API gives access to Claude models through the **Messages API**. You send a list of `user`/`assistant` messages (the system prompt is a separate top-level field) and a required `max_tokens`, and you get back a message whose `content` is a list of blocks. The Python package is `anthropic`.

## 🔵 सरल परिभाषा (Hindi)
Anthropic API **Messages API** के ज़रिए Claude models तक पहुँच देती है। आप `user`/`assistant` messages की list भेजते हैं (system prompt एक अलग top-level field है) और ज़रूरी `max_tokens` देते हैं, और जवाब में ऐसा message मिलता है जिसका `content` blocks की list है। Python package `anthropic` है।

---

## 🔴 Problem it Solves
Relying on one provider is risky (outages, price changes, quality differences). Claude offers strong models for long documents, careful instruction following, coding, and tool use, plus a large context window and prompt caching. Knowing both OpenAI and Anthropic APIs lets you pick the best model per task and build fallbacks.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ एक provider पर निर्भर रहना जोखिम है (outages, price बदलाव, quality फ़र्क)। Claude लंबे documents, ध्यान से instructions follow करने, coding और tool use के लिए मज़बूत models देता है, साथ में बड़ी context window और prompt caching। OpenAI और Anthropic दोनों APIs जानने से आप task के हिसाब से best model चुन सकते हैं और fallbacks बना सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create an API key in the Anthropic Console; set ANTHROPIC_API_KEY
Step 2 → pip install anthropic ; client = anthropic.Anthropic()
Step 3 → Call client.messages.create(model=..., max_tokens=..., system=..., messages=[...])
Step 4 → Messages must alternate roles and start with "user" (consecutive same-role messages are merged)
Step 5 → Response: message.content = [ {type:"text", text:"..."} , ...]
Step 6 → Read message.content[0].text (check block type) and message.stop_reason
Step 7 → message.usage has input_tokens and output_tokens (billing)
Step 8 → Handle errors: anthropic.RateLimitError, APIStatusError, APIConnectionError
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Anthropic Console में API key बनाओ; ANTHROPIC_API_KEY set करो
Step 2 → pip install anthropic ; client = anthropic.Anthropic()
Step 3 → client.messages.create(model=..., max_tokens=..., system=..., messages=[...]) call करो
Step 4 → Messages में roles बारी-बारी से हों और "user" से शुरू हों
Step 5 → Response: message.content = [ {type:"text", text:"..."} , ...]
Step 6 → message.content[0].text पढ़ो (block type देखकर) और message.stop_reason
Step 7 → message.usage में input_tokens और output_tokens होते हैं (billing)
Step 8 → Errors संभालो: anthropic.RateLimitError, APIStatusError, APIConnectionError
```

---

## 🟡 Real World Example
**Tariff Classification System**: Long legal chapter notes and rulings (50K+ tokens) are fed to Claude for careful reading, with the system prompt "Cite the exact note supporting the code." Claude's long-context handling and instruction following suit the audit-style output. The same app keeps an OpenAI model as a fallback.

**Amazon-style AI**: Customer-support summarisation of long ticket threads, where reliable instruction following and tone matter.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: लंबे legal chapter notes और rulings (50K+ tokens) Claude को सावधानी से पढ़ने के लिए दिए जाते हैं, system prompt "code का समर्थन करने वाला exact note cite करो" के साथ। Claude की long-context handling और instruction following audit-style output के लिए ठीक बैठती है। वही app fallback के रूप में OpenAI model रखता है।

**Amazon-style AI**: लंबे ticket threads की customer-support summarisation, जहाँ भरोसेमंद instruction following और tone मायने रखते हैं।

---

## 💻 Code Example — Basic
```python
# Basic Claude call (needs: pip install anthropic, and ANTHROPIC_API_KEY)
import os                                        # env access
import anthropic                                 # official SDK

if not os.getenv("ANTHROPIC_API_KEY"):           # fail early with a clear message
    raise SystemExit("Set ANTHROPIC_API_KEY first")

client = anthropic.Anthropic()                   # reads the key from env

# Model ids change over time; read it from env so you can update without code changes.
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")   # check docs for current ids

message = client.messages.create(
    model=MODEL,                                 # which Claude model
    max_tokens=200,                              # REQUIRED in the Messages API
    system="You are a customs tariff assistant. Be concise.",   # top-level system field
    messages=[{"role": "user", "content": "HS heading for a smartphone?"}],   # chat turns
)

print(message.content[0].text)                   # first content block (type "text")
print("stop_reason:", message.stop_reason)       # end_turn, max_tokens, tool_use ...
print("tokens in/out:", message.usage.input_tokens, message.usage.output_tokens)
```

## 💻 Code Example — Advanced
```python
# Production wrapper: typed result, errors, retries via SDK, sync + async
import asyncio                                           # async runner
import logging                                           # logs
import os                                                # env
from dataclasses import dataclass                        # result container
from typing import Optional                              # type hints

import anthropic                                         # SDK

logger = logging.getLogger(__name__)                     # logger
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")   # configurable model id

sync_client = anthropic.Anthropic(max_retries=3, timeout=60.0)      # built-in retries
async_client = anthropic.AsyncAnthropic(max_retries=3, timeout=60.0)


@dataclass
class ClaudeResult:
    text: str                                            # joined text blocks
    input_tokens: int                                    # billed input
    output_tokens: int                                   # billed output
    stop_reason: Optional[str]                           # why it stopped


def _to_result(msg: anthropic.types.Message) -> ClaudeResult:
    # content is a list of blocks; keep only text blocks
    text = "".join(b.text for b in msg.content if b.type == "text")
    return ClaudeResult(text, msg.usage.input_tokens, msg.usage.output_tokens, msg.stop_reason)


def ask(prompt: str, system: str = "Be concise.") -> Optional[ClaudeResult]:
    try:
        msg = sync_client.messages.create(
            model=MODEL, max_tokens=300, system=system,
            messages=[{"role": "user", "content": prompt}])
        return _to_result(msg)
    except anthropic.RateLimitError:                     # 429
        logger.warning("rate limited")
    except anthropic.APIConnectionError as exc:          # network
        logger.error("connection: %s", exc)
    except anthropic.APIStatusError as exc:              # other HTTP errors
        logger.error("status %s: %s", exc.status_code, exc.message)
    return None


async def aask(prompt: str, system: str = "Be concise.") -> Optional[ClaudeResult]:
    try:
        msg = await async_client.messages.create(
            model=MODEL, max_tokens=300, system=system,
            messages=[{"role": "user", "content": prompt}])
        return _to_result(msg)
    except anthropic.APIError as exc:                    # base class for all SDK errors
        logger.error("async call failed: %s", exc)
        return None


if __name__ == "__main__":
    print(asyncio.run(aask("HS heading for a laptop?")))
```

---

## 🟠 FastAPI Integration

```python
import os                                          # env
import anthropic                                   # SDK
from fastapi import FastAPI, HTTPException         # framework
from pydantic import BaseModel                     # models

app = FastAPI()                                    # app
client = anthropic.AsyncAnthropic(max_retries=2, timeout=60.0)   # shared async client
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")


class Q(BaseModel):
    product: str


@app.post("/classify")
async def classify(q: Q) -> dict:
    try:
        msg = await client.messages.create(
            model=MODEL,
            max_tokens=100,
            system="Return only the 6-digit HS code.",
            messages=[{"role": "user", "content": q.product}],
            temperature=0,
        )
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Busy, retry shortly")
    except anthropic.APIError:
        raise HTTPException(status_code=502, detail="AI service unavailable")
    text = "".join(b.text for b in msg.content if b.type == "text")
    return {"hs_code": text.strip(),
            "usage": {"in": msg.usage.input_tokens, "out": msg.usage.output_tokens}}
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-anthropic` provides `ChatAnthropic`. It converts LangChain messages (a `SystemMessage` becomes the top-level `system`) and supports tool calling, streaming, and `usage_metadata`.

```python
from langchain_anthropic import ChatAnthropic            # pip install langchain-anthropic
from langchain_core.prompts import ChatPromptTemplate    # prompts
from langchain_core.output_parsers import StrOutputParser

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0, max_tokens=200)
chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Return only the 6-digit HS code."),
        ("human", "{product}"),
    ])
    | llm
    | StrOutputParser()
)
# print(chain.invoke({"product": "power bank"}))   # needs ANTHROPIC_API_KEY
# LangGraph: use `llm` inside any node exactly like ChatOpenAI.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `max_tokens`
✅ Correct: It is required.

```python
# Wrong — raises an error
client.messages.create(model=MODEL, messages=msgs)
# Right
client.messages.create(model=MODEL, max_tokens=300, messages=msgs)
```

❌ Mistake 2: Putting the system prompt inside `messages` with role "system"
✅ Correct: Use the top-level `system=` argument (see topic 036).

❌ Mistake 3: Assuming `content` is a string
✅ Correct: It is a list of blocks; read `.text` from blocks with `type == "text"` (see topic 037).

❌ Mistake 4: Hard-coding model ids forever
✅ Correct: Keep model ids in config; they are retired and renewed. Check the official models page.

---

## 🧠 Tricky Interview Question

**Q**: "You port an OpenAI-based classifier to Claude by changing only the model name and client. It fails with validation errors. What differences did you miss?"

**Answer**: (1) `max_tokens` is required in Claude. (2) System prompt is a top-level `system` parameter, not a message role. (3) Response text is `message.content[0].text` (a list of blocks), not `choices[0].message.content`. (4) Usage fields are `input_tokens`/`output_tokens`. (5) Message roles must alternate and start with `user`. (6) Parameters such as `response_format`, `n`, `logprobs`, and `seed` do not exist the same way; structured output is done through tools or prompting. (7) Error class names differ. An adapter layer (or LiteLLM) hides these differences.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which endpoint do you use for chat with Claude?
A1: The Messages API: `client.messages.create(...)`.

Q2: [Easy] Where does the system prompt go?
A2: In the top-level `system` parameter.

Q3: [Medium] What does `stop_reason` mean?
A3: Why generation ended: `end_turn` (natural), `max_tokens` (cut off), `stop_sequence`, `tool_use` (Claude wants a tool), and others.

Q4: [Medium] How do you count or reduce Claude costs?
A4: Read `usage.input_tokens/output_tokens`; use prompt caching (`cache_control`) for repeated long prefixes; choose a smaller Claude model for simple tasks; cap `max_tokens`; use the Message Batches API for offline work.

Q5: [Hard] When would you choose Claude over GPT, or the reverse?
A5: Decide by evals on your data, not brand. Consider quality on your task, context length, latency, price, tool-use reliability, safety behaviour, data-residency/compliance, and rate limits. Many teams use both with routing and fallbacks to avoid single-provider risk.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long documents, careful instruction following, coding, agents with tools
- You want provider redundancy

❌ Avoid when:
- You need OpenAI-only features (for example certain embeddings or image generation)
- Your evals show another model is cheaper at equal quality

---

## 📊 Visual Diagram
```
Your app
   |  client.messages.create(model, max_tokens, system, messages)
   v
+--------------------- Anthropic Messages API ----------------------+
| Message { id, role:"assistant", content:[ {type:"text",text:...} ],|
|           stop_reason, usage:{input_tokens, output_tokens} }       |
+--------------------------------------------------------------------+
   |
   v  text = "".join(b.text for b in msg.content if b.type == "text")
```

---

## 💰 Cost Impact
- Billed per input and output token (prices differ per Claude model; check the pricing page).
- Prompt caching can sharply cut cost for long, repeated prefixes (cached reads are billed at a fraction of normal input price; cache writes cost slightly more).
- Optimise: smallest sufficient model, `max_tokens`, shorter prompts, caching static context (tariff notes), and Message Batches for non-urgent jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Messages API | Claude's chat endpoint | Claude का chat endpoint |
| max_tokens | Required output cap | ज़रूरी output सीमा |
| system | Top-level instructions field | Top-level निर्देश field |
| Content block | Piece of the reply (text, tool_use) | जवाब का हिस्सा |
| stop_reason | Why generation ended | Generation क्यों रुका |
| Prompt caching | Reuse long prefixes cheaply | लंबे prefix सस्ते में दोबारा use |

---

## ⚡ 3-Line Summary
English: Claude is called through the Messages API with a required `max_tokens` and a top-level `system` field. The reply is a list of content blocks, and usage is `input_tokens`/`output_tokens`. Keep model ids in config and use an adapter layer for multi-provider apps.
Hindi: Claude को Messages API से call करते हैं, जिसमें `max_tokens` ज़रूरी है और `system` top-level field है। Reply content blocks की list है और usage `input_tokens`/`output_tokens` है। Model ids config में रखो और multi-provider apps के लिए adapter layer बनाओ।

---

## ➡️ Next Topic
**035. Claude API vs OpenAI API** — a side-by-side comparison of the two APIs.
