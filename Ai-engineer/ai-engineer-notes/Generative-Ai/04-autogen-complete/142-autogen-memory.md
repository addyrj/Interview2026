---

# 142. AutoGen Memory
# हिंदी में: AutoGen Memory (agent की याददाश्त)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
AutoGen AgentChat has a `Memory` protocol in `autogen_core.memory`. You pass `memory=[...]` to an `AssistantAgent`; before each model call the agent asks every memory to `update_context`, which injects relevant facts into the model context as a system message. `ListMemory` is the simple built-in version.

## 🔵 सरल परिभाषा (Hindi)
AutoGen AgentChat में `autogen_core.memory` का `Memory` protocol है। `AssistantAgent` को `memory=[...]` देते हैं; हर model call से पहले agent हर memory से `update_context` करवाता है, जो ज़रूरी facts को system message बनाकर model context में डाल देता है। `ListMemory` सबसे सरल built-in रूप है।

---

## 🔴 Problem it Solves
An LLM call is stateless. Facts such as 'ACME imports leather shoes from Vietnam' must be repeated by the user or stuffed into every prompt. Chat history is not durable memory either: it is trimmed and it is per conversation.

## 🔴 यह क्यों बना? (Hindi)
LLM call stateless होता है। 'ACME वियतनाम से leather shoes import करता है' जैसे facts या तो user को दोहराने पड़ते हैं या हर prompt में ठूँसने पड़ते हैं। Chat history भी टिकाऊ memory नहीं है: वह कटती है और हर बातचीत की अलग होती है।

---

## 🟢 How it Works

```
Step 1 -> Create a memory object (ListMemory or your own Memory subclass)
Step 2 -> await memory.add(MemoryContent(...)) stores a fact
Step 3 -> Pass memory=[mem] to AssistantAgent
Step 4 -> Before each LLM call the agent calls mem.update_context(model_context)
Step 5 -> update_context adds a SystemMessage with the relevant memories
Step 6 -> Model answers using that context; query() can also be called directly
Step 7 -> clear() wipes the store; close() releases resources
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Memory object बनाओ (ListMemory या अपनी Memory subclass)
Step 2 -> await memory.add(MemoryContent(...)) से fact सहेजो
Step 3 -> AssistantAgent को memory=[mem] दो
Step 4 -> हर LLM call से पहले agent mem.update_context(model_context) बुलाता है
Step 5 -> update_context relevant memories वाला SystemMessage जोड़ता है
Step 6 -> Model उसी context से जवाब देता है; query() सीधे भी बुला सकते हैं
Step 7 -> clear() store खाली करता है; close() resources छोड़ता है
```

---

## 🟡 Real World Example
**Tariff Agent with importer profile.** Store 'ACME ships leather shoes from Vietnam' once. Every later question ('what is the duty for our shoes?') gets that fact injected automatically, so the agent already knows origin and product. Each importer gets its own memory object so facts never leak between customers.

## 🟡 Real Example Hindi mein
**Importer profile वाला Tariff Agent.** 'ACME वियतनाम से leather shoes भेजता है' एक बार सहेजें। बाद के हर सवाल ('हमारे shoes पर duty?') में यह fact अपने आप जुड़ जाता है, इसलिए agent को origin और product पहले से पता है। हर importer की अलग memory होती है ताकि customers के बीच facts leak न हों।

---

## 💻 Code Example — Basic
Basic: `ListMemory`. The code calls `update_context` by hand so you can see the SystemMessage it produces, then attaches the memory to an agent.

```python
# Basic: ListMemory feeding an AssistantAgent
import asyncio  # event loop
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType  # simple list memory
from autogen_core.model_context import BufferedChatCompletionContext  # chat context
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake model
from autogen_agentchat.agents import AssistantAgent  # agent

async def main() -> None:  # entry
    mem = ListMemory()  # empty memory
    await mem.add(MemoryContent(content="Importer ACME ships leather shoes from Vietnam", mime_type=MemoryMimeType.TEXT))  # store a fact
    ctx = BufferedChatCompletionContext(buffer_size=5)  # a context object to inject into
    update = await mem.update_context(ctx)  # what the agent does before each LLM call
    print(update.memories.results[0].content)  # the fact that was retrieved
    print(await ctx.get_messages())  # memory became a SystemMessage
    agent = AssistantAgent("tariff", ReplayChatCompletionClient(["ok"]), memory=[mem])  # attach memory to the agent
    res = await agent.run(task="hi")  # run
    print(res.messages[-1].content)  # fake answer

asyncio.run(main())  # go
```

## 💻 Code Example — Advanced
Advanced: a custom `Memory` subclass implementing all five abstract methods (`add`, `query`, `update_context`, `clear`, `close`) with naive keyword search, one memory per importer, behind FastAPI.

```python
# Advanced: custom Memory (keyword search, per-importer) behind FastAPI
import asyncio  # async
from typing import Any  # typing
from fastapi import FastAPI  # web
from fastapi.testclient import TestClient  # test
from pydantic import BaseModel  # body model
from autogen_core import CancellationToken  # cancel token type
from autogen_core.memory import Memory, MemoryContent, MemoryQueryResult, UpdateContextResult  # memory protocol
from autogen_core.model_context import ChatCompletionContext  # context type
from autogen_core.models import SystemMessage  # message type
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake model
from autogen_agentchat.agents import AssistantAgent  # agent

class KeywordMemory(Memory):  # implement the 5 abstract methods
    def __init__(self) -> None:  # init
        self.items: list[MemoryContent] = []  # store

    async def add(self, content: MemoryContent, cancellation_token: CancellationToken | None = None) -> None:  # write
        self.items.append(content)  # append fact

    async def query(self, query: str | MemoryContent, cancellation_token: CancellationToken | None = None, **kwargs: Any) -> MemoryQueryResult:  # read
        q = (query if isinstance(query, str) else str(query.content)).lower()  # normalise
        hits = [m for m in self.items if any(w in str(m.content).lower() for w in q.split())]  # naive keyword match
        return MemoryQueryResult(results=hits)  # wrap

    async def update_context(self, model_context: ChatCompletionContext) -> UpdateContextResult:  # called before each LLM call
        msgs = await model_context.get_messages()  # current chat
        last = str(getattr(msgs[-1], "content", "")) if msgs else ""  # latest user text
        res = await self.query(last)  # retrieve relevant facts
        if res.results:  # only inject when something matched
            await model_context.add_message(SystemMessage(content="Known facts: " + "; ".join(str(r.content) for r in res.results)))  # inject
        return UpdateContextResult(memories=res)  # report what was used

    async def clear(self) -> None:  # wipe
        self.items.clear()  # empty

    async def close(self) -> None:  # cleanup hook
        return None  # nothing to close

STORE: dict[str, KeywordMemory] = {}  # one memory per importer id
app = FastAPI()  # app

class Fact(BaseModel):  # body
    text: str  # fact text

@app.post("/memory/{importer}")  # add fact
async def add(importer: str, f: Fact) -> dict[str, int]:  # handler
    mem = STORE.setdefault(importer, KeywordMemory())  # get or create
    await mem.add(MemoryContent(content=f.text, mime_type="text/plain"))  # store
    return {"count": len(mem.items)}  # size

@app.post("/ask/{importer}")  # ask
async def ask(importer: str, f: Fact) -> dict[str, str]:  # handler
    mem = STORE.setdefault(importer, KeywordMemory())  # memory for this importer only
    agent = AssistantAgent("a", ReplayChatCompletionClient(["noted"]), memory=[mem])  # fake LLM
    res = await agent.run(task=f.text)  # run
    return {"answer": str(res.messages[-1].content)}  # answer

c = TestClient(app)  # client
print(c.post("/memory/acme", json={"text": "acme ships shoes from vietnam"}).json())  # add
print(c.post("/ask/acme", json={"text": "duty for shoes"}).json())  # ask
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing. The packages `autogen_ext.memory` contains submodules `canvas`, `chromadb`, `mem0`, `redis` (names confirmed by listing the installed package); those vector/cloud backends were NOT run (they need extra dependencies, a server or an API key).

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---|---|---|---|---|
| Short-term memory | State messages / checkpointer | Short-term memory (task context) | Session objects | Model context (chat history) per agent |
| Long-term store | Store API (cross-thread) | Long-term / entity memory | Not built in; use tools or your DB | Memory protocol: ListMemory, chromadb, redis, mem0 extensions |
| Injection point | You read state in nodes | Automatic into prompts | Instructions / session | update_context adds SystemMessage before each LLM call |
| Custom backend | Implement a store | Custom storage class | Custom Session | Subclass Memory (5 methods) |
| Per-user isolation | thread_id / namespace | Per crew/agent config | Per session id | One Memory object per user |
| Persist across restarts | Checkpointer DB | Configured storage | Session backend | Depends on backend (ListMemory is in-process only) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using one global ListMemory for all users.
✅ Correct: Create one memory per user/tenant (see the `STORE` dict keyed by importer) so facts never cross customers.

❌ Mistake: Expecting ListMemory to survive a restart.
✅ Correct: ListMemory lives in process memory. Use a persistent backend or save facts to your DB and reload them.

❌ Mistake: Injecting every fact on every call.
✅ Correct: Implement `update_context` to query only relevant facts; otherwise token cost grows with the store.

❌ Mistake: Treating memory as truth.
✅ Correct: Facts can be stale or wrong. Add timestamps/sources in `MemoryContent.metadata` and let users correct them.

---

## 🧠 Tricky Interview Question
After 3 months the tariff agent confidently uses an importer's old origin country. How do you design memory to prevent this?

Answer: Memory without freshness is a liability. Store facts with metadata (source, created_at, confidence), make `update_context` rank by relevance and recency, include the date in the injected text ('as of 2026-01') so the model can hedge, let users view/edit/delete facts (a `clear` or delete endpoint), and for high-stakes fields (origin, product) always re-confirm through a tool or the user instead of trusting memory. Keep a TTL for facts that expire.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you attach memory to an AssistantAgent?
A1: `AssistantAgent(name, model_client, memory=[my_memory])`.

Q2: [Medium] What does `update_context` do?
A2: It is called before each model call, reads the model context, finds relevant memories and appends them (as a SystemMessage in ListMemory) so the model sees them.

Q3: [Hard] Which methods must a custom Memory implement?
A3: `add`, `query`, `update_context`, `clear`, `close` (all abstract in `autogen_core.memory.Memory`).

Q4: [Hard] Memory vs chat history: difference?
A4: History is the running conversation in the model context and is trimmed or reset; memory is a separate store of facts that outlives one conversation and is injected on demand.

Q5: [System Design] Design long-term memory for 10,000 importers.
A5: Per-importer namespaced store (vector DB such as the chromadb/redis extensions or your own table), embedding + keyword hybrid retrieval, top-k limit, TTL and edit/delete APIs, encryption and tenant isolation, evaluation of retrieval quality, and a token budget for the injected block.

---

## 💰 Cost Impact
Injected memory is paid for as input tokens on every model call. Formula: `extra_cost = calls * injected_tokens * in_price`. A 10-fact block of roughly 200 tokens (estimate) over 1,000 calls adds about 200,000 input tokens. Tips: retrieve top-k only, summarise old facts, avoid injecting on turns that do not need them. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Users expect the agent to remember profile facts and preferences.
- Facts are reused across many conversations.
- You need per-user personalisation.

❌ Avoid when:
- Data is sensitive and you have no deletion or isolation story.
- Facts change every minute (use a live tool instead).
- A short single-turn task where history is enough.

---

## 📊 Visual Diagram
```
 add(fact) --> [ Memory store ]
                         |
 user question --> AssistantAgent
                         |  before each LLM call
                         v
                 memory.update_context(ctx)
                         |  query(relevant facts)
                         v
          ctx += SystemMessage("Relevant memory content: ...")
                         |
                         v
                  Model client --> answer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|---|---|---|
| Memory | Protocol for storing and retrieving facts | तथ्य सहेजने और खोजने का protocol |
| ListMemory | Simple in-process list memory | सरल in-process list memory |
| MemoryContent | One stored item (content + mime type + metadata) | एक सहेजा गया item |
| update_context | Hook that injects memories into the model context | memories को model context में डालने वाला hook |
| query | Search memory for relevant items | relevant items खोजना |
| model context | Messages sent to the model | model को भेजे जाने वाले messages |
| tenant isolation | Separate memory per customer | हर customer की अलग memory |

---

## ⚡ 3-Line Summary
English: Memory is a protocol: add, query, update_context, clear, close.
The agent injects relevant facts as a system message before each model call.
Use one memory per user and keep injected text small.
Hindi: Memory एक protocol है: add, query, update_context, clear, close।
Agent हर model call से पहले relevant facts को system message बनाकर जोड़ता है।
हर user की अलग memory रखें और injected text छोटा रखें।

---

## ➡️ Next Topic
143. AutoGen Code Execution -- letting agents write and run code safely with CodeExecutorAgent and executors.

---
