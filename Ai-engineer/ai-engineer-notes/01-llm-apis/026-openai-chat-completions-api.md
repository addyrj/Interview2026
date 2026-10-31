---

# 026. OpenAI Chat Completions API
# हिंदी में: OpenAI Chat Completions API

---

## 🔵 Simple Definition (English)
Chat Completions is the main OpenAI endpoint for conversation. You send a list of messages, each with a role (`system`, `user`, `assistant`, `tool`), and the model returns the next assistant message. The API is stateless: you re-send the history every time.

## 🔵 सरल परिभाषा (Hindi)
Chat Completions बातचीत के लिए OpenAI का मुख्य endpoint है। आप messages की list भेजते हैं, हर message का एक role होता है (`system`, `user`, `assistant`, `tool`), और model अगला assistant message लौटाता है। API stateless है: हर बार history दोबारा भेजनी पड़ती है।

---

## 🔴 Problem it Solves
Older completion APIs took one raw text prompt, so developers had to format dialogue by hand and mix instructions with user text (which also made prompt injection easier). Roles separate instructions from user input and make multi-turn chat, tool calling, and structured output clean.

## 🔴 यह क्यों बना? (Hindi)
पुराने completion APIs में एक raw text prompt जाता था, इसलिए developer को dialogue हाथ से format करना पड़ता था और instructions user text में मिल जाते थे (prompt injection भी आसान)। Roles से instructions और user input अलग रहते हैं, और multi-turn chat, tool calling और structured output साफ़ हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build messages: [system, user, assistant, user, ...]
Step 2 → Choose model and options (temperature, max_tokens, n, stop, seed)
Step 3 → POST to /v1/chat/completions via client.chat.completions.create()
Step 4 → Model reads all messages as one token sequence
Step 5 → Model generates assistant reply until stop or max_tokens
Step 6 → Response: choices[i].message, finish_reason, usage
Step 7 → You append the assistant reply to your history for the next turn
Step 8 → Check finish_reason: "stop" ok, "length" truncated, "tool_calls" run a tool
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → messages बनाओ: [system, user, assistant, user, ...]
Step 2 → model और options चुनो (temperature, max_tokens, n, stop, seed)
Step 3 → client.chat.completions.create() से /v1/chat/completions पर POST
Step 4 → Model सभी messages को एक token sequence की तरह पढ़ता है
Step 5 → Model stop या max_tokens तक assistant reply generate करता है
Step 6 → Response: choices[i].message, finish_reason, usage
Step 7 → Assistant reply को अगले turn के लिए history में जोड़ो
Step 8 → finish_reason देखो: "stop" ठीक, "length" कटा हुआ, "tool_calls" tool चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: 
- `system`: "You classify goods into HS codes. Use only the provided tariff excerpts."
- `user`: "Excerpts: ... Product: stainless steel water bottle."
- `assistant`: "7323.93 - Table, kitchen or other household articles of stainless steel."
- Follow-up `user`: "What if it has a plastic lid?" The history is re-sent so the model remembers the bottle.

**Amazon-style AI**: A "Rufus"-like shopping assistant keeps the last few turns and the product context inside messages.

## 🟡 Real Example Hindi mein
**Tariff Classification System**:
- `system`: "तुम सामान को HS codes में classify करते हो। सिर्फ़ दिए गए tariff excerpts use करो।"
- `user`: "Excerpts: ... Product: stainless steel water bottle."
- `assistant`: "7323.93 - stainless steel के घरेलू बर्तन।"
- Follow-up `user`: "अगर plastic lid हो तो?" History दोबारा भेजी जाती है ताकि model को bottle याद रहे।

**Amazon-style AI**: Shopping assistant आख़िरी कुछ turns और product context messages में रखता है।

---

## 💻 Code Example — Basic
```python
# Basic multi-turn chat with Chat Completions (needs OPENAI_API_KEY)
from openai import OpenAI                       # sync client

client = OpenAI()                               # key comes from environment

# History is just a Python list of dicts
messages = [
    {"role": "system", "content": "You classify goods into HS codes. Be brief."},  # rules
    {"role": "user", "content": "Stainless steel water bottle?"},                  # turn 1
]

# First call
r1 = client.chat.completions.create(
    model="gpt-4o-mini",                        # model name
    messages=messages,                          # full history
    temperature=0,                              # stable answers
    max_tokens=80,                              # cap output
)
answer1 = r1.choices[0].message.content         # assistant text
print("A1:", answer1)                           # show it
print("finish_reason:", r1.choices[0].finish_reason)   # "stop" or "length"

# Because the API is stateless, append the reply and the next question ourselves
messages.append({"role": "assistant", "content": answer1})          # remember reply
messages.append({"role": "user", "content": "And with a plastic lid?"})  # turn 2

r2 = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=80)
print("A2:", r2.choices[0].message.content)     # model uses earlier context
print("tokens:", r2.usage.prompt_tokens, r2.usage.completion_tokens)  # note growing input
```

## 💻 Code Example — Advanced
```python
# Production chat session: history, truncation check, JSON mode, errors, async
import asyncio                                           # async runner
import json                                              # parse JSON answers
import logging                                           # logs
from typing import Any, Dict, List                       # type hints

from openai import APIStatusError, AsyncOpenAI           # async client + error

logger = logging.getLogger(__name__)                     # logger
Msg = Dict[str, Any]                                     # message alias


class ChatSession:
    def __init__(self, system: str, model: str = "gpt-4o-mini", max_turns: int = 6) -> None:
        self.client = AsyncOpenAI(timeout=30.0, max_retries=2)   # reusable client
        self.model = model                                       # model name
        self.system: Msg = {"role": "system", "content": system} # fixed instructions
        self.turns: List[Msg] = []                               # user/assistant history
        self.max_turns = max_turns                               # keep memory small

    def _messages(self) -> List[Msg]:
        recent = self.turns[-self.max_turns * 2:]                # last N exchanges
        return [self.system, *recent]                            # system always first

    async def say(self, text: str) -> Dict[str, Any]:
        self.turns.append({"role": "user", "content": text})     # add user turn
        try:
            r = await self.client.chat.completions.create(
                model=self.model,
                messages=self._messages(),
                temperature=0,
                max_tokens=200,
                response_format={"type": "json_object"},         # force valid JSON
            )
        except APIStatusError as exc:                            # 4xx / 5xx
            self.turns.pop()                                     # undo failed turn
            logger.error("API error %s", exc.status_code)
            raise
        choice = r.choices[0]                                    # first (only) choice
        if choice.finish_reason == "length":                     # output was cut
            logger.warning("answer truncated, raise max_tokens")
        content = choice.message.content or "{}"                 # may be None
        self.turns.append({"role": "assistant", "content": content})  # save reply
        try:
            data = json.loads(content)                           # parse JSON
        except json.JSONDecodeError:
            data = {"raw": content}                              # fallback
        return {"data": data, "usage": r.usage.model_dump()}     # answer + token usage


async def main() -> None:
    s = ChatSession('Reply as JSON: {"hs_code": str, "reason": str}')  # JSON mode needs the word JSON
    print(await s.say("Stainless steel water bottle"))
    print(await s.say("With a plastic lid"))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Keep per-user history in a store (Redis or a database). The API itself is stateless.

```python
from collections import defaultdict               # simple in-memory store (demo only)
from typing import Dict, List
from fastapi import FastAPI, HTTPException        # framework
from pydantic import BaseModel                    # models
from openai import APIStatusError, AsyncOpenAI    # client + error

app = FastAPI()                                   # app
client = AsyncOpenAI()                            # shared client
HISTORY: Dict[str, List[dict]] = defaultdict(list)   # use Redis in production


class ChatIn(BaseModel):
    session_id: str                               # which conversation
    message: str                                  # new user text


@app.post("/chat")
async def chat(body: ChatIn) -> dict:
    hist = HISTORY[body.session_id]               # get this user's history
    hist.append({"role": "user", "content": body.message})
    msgs = [{"role": "system", "content": "You are a tariff assistant."}, *hist[-10:]]
    try:
        r = await client.chat.completions.create(
            model="gpt-4o-mini", messages=msgs, max_tokens=250)
    except APIStatusError as exc:
        hist.pop()                                # rollback failed turn
        raise HTTPException(status_code=502, detail=f"upstream {exc.status_code}")
    reply = r.choices[0].message.content or ""
    hist.append({"role": "assistant", "content": reply})
    return {"reply": reply, "total_tokens": r.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain converts its message classes into this same `messages` list. `ChatOpenAI.invoke` calls Chat Completions under the hood. LangGraph stores messages in state with the `add_messages` reducer.

```python
from langchain_openai import ChatOpenAI                       # wrapper over Chat Completions
from langchain_core.messages import HumanMessage, SystemMessage  # role classes

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)          # model object
msgs = [
    SystemMessage("You classify goods into HS codes. Be brief."),   # becomes role=system
    HumanMessage("Stainless steel water bottle?"),                  # becomes role=user
]
# reply = llm.invoke(msgs)            # AIMessage with .content and .usage_metadata
# print(reply.content, reply.usage_metadata)

# LangGraph: MessagesState keeps this list in graph state automatically:
# from langgraph.graph import MessagesState, StateGraph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting the API to remember previous calls
✅ Correct: Re-send the history yourself.

```python
# Wrong — model has no idea what "it" means
client.chat.completions.create(model="gpt-4o-mini",
    messages=[{"role": "user", "content": "And with a lid?"}])
# Right — include earlier turns
client.chat.completions.create(model="gpt-4o-mini", messages=history + [new_user_msg])
```

❌ Mistake 2: Ignoring `finish_reason`
✅ Correct: `"length"` means the answer was cut. Raise `max_tokens` or shorten the request.

❌ Mistake 3: Using `response_format={"type": "json_object"}` without mentioning JSON in the prompt
✅ Correct: The prompt must tell the model to output JSON, or the API returns an error. Prefer structured outputs with a JSON schema when available.

---

## 🧠 Tricky Interview Question

**Q**: "A user chats for 30 turns. Cost per message keeps rising and answers get worse. Why?"

**Answer**: The API is stateless, so every call re-sends all earlier messages. Input tokens grow with each turn, so cost rises, latency rises, and long context dilutes attention. Fix: keep a sliding window of recent turns, summarise older ones, store durable facts separately, and use prompt caching for the static system prompt. Also track `usage.prompt_tokens` per turn to spot growth early.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What roles exist in Chat Completions?
A1: `system` (or `developer` on newer models) for instructions, `user`, `assistant`, and `tool` for tool results.

Q2: [Easy] Is the API stateful?
A2: No. You send the whole conversation each time.

Q3: [Medium] What does `finish_reason` tell you?
A3: Why generation stopped: `stop` (natural end), `length` (hit max tokens), `tool_calls` (model wants a tool), `content_filter` (blocked).

Q4: [Medium] What is `n` and when would you use it?
A4: Number of alternative completions. You pay for all of them. Useful for self-consistency voting, rarely for normal apps.

Q5: [Hard] Chat Completions vs the newer Responses API?
A5: Chat Completions is the long-standing stateless message API and remains widely supported, including by many compatible providers (Groq, Ollama, LiteLLM). The Responses API is OpenAI's newer interface that adds built-in tools and optional server-side conversation state. For portability across providers, Chat Completions is still the common denominator; check the docs for features available only in Responses.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building chatbots, classifiers, extractors, agents with tool calling
- You want portability to OpenAI-compatible providers

❌ Avoid when:
- You only need vectors (use embeddings)
- You need huge offline workloads (use Batch API for 50 percent lower cost)

---

## 📊 Visual Diagram
```
messages = [ system | user | assistant | user ]
                         |
                         v
            POST /v1/chat/completions
                         |
                         v
   +---------------------------------------------+
   | choices[0].message  = {role: assistant, ...} |
   | choices[0].finish_reason = stop | length     |
   | usage = {prompt, completion, total tokens}   |
   +---------------------------------------------+
                         |
     append reply to history ---> next turn (stateless!)
```

---

## 💰 Cost Impact
- Every request is billed for ALL messages sent (input) plus the reply (output).
- A 10-turn chat with 300 tokens per turn re-sends up to about 3,000 tokens on turn 10; total input across the chat is roughly 16,500 tokens, not 3,000.
- Optimise: sliding window or summary, short system prompt, `max_tokens`, prompt caching for repeated prefixes, `n=1`, cheaper model for easy turns, and Batch API for offline work.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Role | Who wrote the message | Message किसने लिखा |
| System message | Instructions for behaviour | Behaviour के निर्देश |
| Stateless | Server keeps no memory | Server को कुछ याद नहीं रहता |
| finish_reason | Why generation stopped | Generation क्यों रुका |
| response_format | Force JSON output | JSON output मजबूर करना |
| n | Number of completions | Completions की संख्या |

---

## ⚡ 3-Line Summary
English: Chat Completions takes a list of role-tagged messages and returns the next assistant message. It is stateless, so you must re-send history and manage its size. Check `finish_reason` and `usage` on every call.
Hindi: Chat Completions role वाले messages की list लेकर अगला assistant message देता है। यह stateless है, इसलिए history खुद भेजो और उसका size संभालो। हर call में `finish_reason` और `usage` देखो।

---

## ➡️ Next Topic
**027. OpenAI Models Overview** — which model to choose (gpt-4o, gpt-4o-mini, reasoning models) for which task.
