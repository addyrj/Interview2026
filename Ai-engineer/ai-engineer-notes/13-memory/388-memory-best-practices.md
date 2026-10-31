---

# 388. Memory Best Practices
# हिंदी में: Memory की Best Practices

---

## 🔵 Simple Definition (English)
Memory best practices are simple rules for building chat memory that stays cheap, accurate and safe: store only useful facts, keep short-term and long-term memory separate, trim by tokens, summarise old turns, and test that memory really helps.

## 🔵 सरल परिभाषा (Hindi)
Memory best practices सरल नियम हैं ताकि chat memory सस्ती, सही और safe रहे: सिर्फ काम के facts store करो, short-term और long-term memory अलग रखो, tokens के हिसाब से trim करो, पुराने turns का summary बनाओ, और test करो कि memory सच में मदद करती है।

---

## 🔴 Problem it Solves
Teams often dump the whole conversation into every prompt. Results: cost grows each turn, the model gets distracted by old irrelevant text ("lost in the middle"), stale facts contradict new ones, and nobody can tell if memory improves answers. Best practices turn memory from a pile of text into a managed system.

## 🔴 यह क्यों बना? (Hindi)
Teams अक्सर पूरी conversation हर prompt में डाल देती हैं। नतीजा: हर turn के साथ cost बढ़ती है, model पुराने irrelevant text से confuse होता है ("lost in the middle"), पुराने facts नए facts से टकराते हैं, और कोई नहीं जानता कि memory से answers सुधरे या नहीं। Best practices memory को text के ढेर से एक managed system बनाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Separate layers: short-term (last turns) / summary (older turns) / long-term facts
Step 2 → Decide WHAT to save: stable preferences and confirmed facts, not chit-chat
Step 3 → Extract facts as small structured records {key, value, source, updated_at}
Step 4 → Build prompt under a fixed token budget: system + facts + summary + recent turns
Step 5 → When recent turns exceed budget, summarise the oldest part and drop it
Step 6 → Resolve conflicts: newer confirmed fact replaces older (keep history of change)
Step 7 → Evaluate: compare answers with and without memory on a test set; monitor tokens
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Layers अलग करो: short-term (last turns) / summary (पुराने turns) / long-term facts
Step 2 → तय करो क्या save करना है: stable preferences और confirmed facts, chit-chat नहीं
Step 3 → Facts को छोटे structured records में निकालो {key, value, source, updated_at}
Step 4 → Fixed token budget में prompt बनाओ: system + facts + summary + recent turns
Step 5 → Recent turns budget से ज़्यादा हों तो सबसे पुराना हिस्सा summarise करके हटाओ
Step 6 → Conflict सुलझाओ: नया confirmed fact पुराने को replace करे (बदलाव का history रखो)
Step 7 → Evaluate: memory के साथ और बिना answers की तुलना करो; tokens monitor करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Facts worth keeping: `{"preferred_country_of_origin": "VN", "default_incoterm": "FOB"}`. Not worth keeping: "thanks!", "ok". After 12 turns the system summarises turns 1-8 into: "User is classifying lithium battery packs, 5 kg, shipped from Vietnam." The next prompt carries the summary + last 4 turns instead of all 12.

**Zomato AI**: Long-term: "vegetarian, dislikes coriander". Short-term: "tonight I want something light". The long-term fact is stable; the short-term one expires after the session.

## 🟡 Real Example Hindi mein
**Tariff System**: रखने लायक facts: `{"preferred_country_of_origin": "VN", "default_incoterm": "FOB"}`। रखने लायक नहीं: "thanks!", "ok"। 12 turns के बाद system turns 1-8 का summary बनाता है: "User lithium battery packs, 5 kg, Vietnam से classify कर रहा है।" अगला prompt सारे 12 की जगह summary + last 4 turns ले जाता है।

**Zomato AI**: Long-term: "vegetarian, धनिया पसंद नहीं"। Short-term: "आज रात हल्का खाना चाहिए"। Long-term fact stable है; short-term session खत्म होते ही expire हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: sliding window + running summary + fact store (pure Python, runs offline)
from dataclasses import dataclass, field          # simple containers


@dataclass
class ChatMemory:
    """Three layers: facts, summary, recent turns."""
    facts: dict[str, str] = field(default_factory=dict)       # long-term key/value facts
    summary: str = ""                                          # compressed older turns
    recent: list[str] = field(default_factory=list)            # last turns, raw text
    max_recent: int = 4                                        # window size

    def add_turn(self, text: str) -> None:
        """Add a turn; if window is full, fold the oldest turn into the summary."""
        self.recent.append(text)                               # newest turn
        while len(self.recent) > self.max_recent:              # window overflow?
            oldest = self.recent.pop(0)                        # remove oldest
            # Real systems call an LLM here; we keep first 40 chars to stay offline
            self.summary = (self.summary + " | " + oldest[:40]).strip(" |")

    def remember(self, key: str, value: str) -> None:
        """Store or overwrite a stable fact (newest wins)."""
        self.facts[key] = value

    def build_context(self) -> str:
        """Create the memory block that goes into the prompt."""
        facts = "; ".join(f"{k}={v}" for k, v in self.facts.items())   # compact facts
        return f"FACTS: {facts}\nSUMMARY: {self.summary}\nRECENT: {self.recent}"


mem = ChatMemory()                                             # new memory
mem.remember("origin", "VN")                                   # confirmed fact
mem.remember("origin", "CN")                                   # user corrected -> overwrite
for i in range(1, 8):                                          # simulate 7 turns
    mem.add_turn(f"turn {i}: question about lithium battery pack number {i}")
print(mem.build_context())                                     # facts + summary + 4 recent
```

## 💻 Code Example — Advanced
```python
# Advanced: token-budgeted prompt builder with async summariser and fallback
import asyncio                                        # async runtime
from typing import Awaitable, Callable               # callable type hints

Summariser = Callable[[str], Awaitable[str]]          # async fn: text -> summary


def est_tokens(text: str) -> int:
    """Rough estimate (~4 chars per token). Use tiktoken in production."""
    return max(1, len(text) // 4)


async def fake_llm_summary(text: str) -> str:
    """Offline stand-in for an LLM summarisation call."""
    await asyncio.sleep(0)                            # yield control like real I/O
    return "Summary: " + text[:60].replace("\n", " ")  # short deterministic summary


class BudgetedMemory:
    """Keeps total memory under `budget` tokens by summarising old turns."""

    def __init__(self, summarise: Summariser, budget: int = 120) -> None:
        self.summarise = summarise                    # injected, easy to mock in tests
        self.budget = budget                          # max tokens for memory block
        self.turns: list[str] = []                    # raw recent turns
        self.summary: str = ""                        # rolling summary

    def _size(self) -> int:
        """Current memory size in tokens."""
        return est_tokens(self.summary) + sum(est_tokens(t) for t in self.turns)

    async def add(self, turn: str) -> None:
        """Add a turn and compact if over budget."""
        self.turns.append(turn)
        while self._size() > self.budget and len(self.turns) > 1:   # keep >= 1 turn
            old = self.turns.pop(0)                    # oldest turn leaves the window
            try:
                self.summary = await self.summarise(f"{self.summary}\n{old}")
            except Exception:                          # LLM down -> degrade, do not crash
                self.summary = (self.summary + " " + old)[-200:]   # crude truncation

    def render(self) -> str:
        """Final text to inject in the prompt."""
        return f"[summary] {self.summary}\n[recent] " + " || ".join(self.turns)


async def main() -> None:
    mem = BudgetedMemory(fake_llm_summary, budget=60)
    for i in range(8):
        await mem.add(f"User asked about HS code variant {i} for battery pack with details")
    print(mem.render())
    print("tokens:", mem._size(), "<= budget 60 (approximately)")


asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
# FastAPI: expose memory with explicit read/write endpoints and a debug view
from fastapi import FastAPI, HTTPException            # framework
from pydantic import BaseModel                         # validation

app = FastAPI()
sessions: dict[str, BudgetedMemory] = {}               # session_id -> memory (use Redis in prod)


class Turn(BaseModel):
    session_id: str                                    # which conversation
    text: str                                          # user message


@app.post("/chat")
async def chat(turn: Turn) -> dict:
    mem = sessions.setdefault(turn.session_id, BudgetedMemory(fake_llm_summary))
    context = mem.render()                              # memory BEFORE adding this turn
    reply = f"(answer using {len(context)} chars of memory)"   # call LLM here
    await mem.add(f"user: {turn.text}")                 # store user turn
    await mem.add(f"bot: {reply}")                      # store bot turn
    return {"reply": reply, "memory_tokens": mem._size()}   # expose token usage


@app.get("/chat/{session_id}/memory")
async def inspect(session_id: str) -> dict:
    if session_id not in sessions:
        raise HTTPException(404, "unknown session")
    return {"memory": sessions[session_id].render()}    # debug (protect with auth!)
```

---

## 🔗 LangChain / LangGraph Connection
Modern LangChain uses `langchain-core` message utilities. `trim_messages` keeps history under a token budget without any deprecated memory classes.

```python
# LangChain core: trim history by token count (here counted per message for offline use)
from langchain_core.messages import HumanMessage, AIMessage, trim_messages

history = [HumanMessage(content=f"question {i}") if i % 2 == 0
           else AIMessage(content=f"answer {i}") for i in range(10)]

trimmed = trim_messages(
    history,
    max_tokens=4,              # with token_counter=len this means "4 messages"
    token_counter=len,         # count each message as 1 (swap for a real model counter)
    strategy="last",           # keep the newest messages
    start_on="human",          # history must start with a human message
    include_system=False,
)
print([m.content for m in trimmed])
# In LangGraph: put trimming in a node before the LLM node, and use a checkpointer
# (PostgresSaver) for persistence plus the Store API for long-term user facts.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending the entire history every time
✅ Correct: Fixed budget with summary and recent window.

```python
# Wrong
prompt = "\n".join(all_turns)
# Right
prompt = mem.build_context()   # facts + summary + last N turns
```

❌ Mistake 2: Storing guesses as facts
✅ Correct: Store only user-confirmed facts, with source and timestamp.

```python
# Wrong - model's guess becomes permanent truth
mem.remember("origin", llm_guess)
# Right - save only when the user confirmed
if user_confirmed:
    mem.remember("origin", value)
```

❌ Mistake 3: Never testing memory
✅ Correct: Run a fixed set of multi-turn test chats and compare answer quality with and without memory.

---

## 🧠 Tricky Interview Question

**Q**: "After adding summarisation, answers got cheaper but users report the bot 'forgets' exact numbers such as an invoice amount or HS code. Why, and how do you fix it?"

**Answer**: Summaries are lossy; LLM summarisers drop precise values like codes, amounts and dates. Fix: extract exact entities into structured facts (HS code, amount, country) before summarising, and keep them outside the summary in the facts layer. Summarise only narrative text. Also instruct the summariser: "preserve all numbers, codes and names verbatim", and add a regression test that checks those values survive.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between short-term and long-term memory in chatbots?
A1: Short-term is the recent conversation inside the current context (sliding window). Long-term persists across sessions (user preferences, facts) in a database or vector store.

Q2: Why is sending full history a problem?
A2: Cost and quality. Every turn resends all tokens, so cost grows with conversation length, and models do worse when relevant info is buried in a long context. It can also hit the context limit.

Q3: When do you summarise versus truncate?
A3: Truncate when old turns are unimportant (casual chat). Summarise when older context matters but is too long. Use structured fact extraction when exact values matter.

Q4: How do you handle contradicting memories ("origin is VN" then "origin is CN")?
A4: Newer confirmed information wins; keep a timestamp and previous value for audit. Optionally ask the user to confirm when the conflict is important.

Q5 (Hard): How would you evaluate whether a memory system is good?
A5: Build a multi-turn test set with questions that need earlier context ("and for the 5 kg pack?"). Metrics: answer correctness with memory vs without, recall of seeded facts after N turns and after summarisation, token usage per turn, latency, and leakage tests across users. Run in CI on every change to the summariser or trimming rules, and use LLM-as-judge for open-ended answers. Track average prompt tokens per turn in production as an operational metric.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Conversations are multi-turn and later questions depend on earlier ones
- Users return across sessions and expect personalisation
- Prompt cost or context limits are a concern

❌ Avoid when:
- Requests are single-shot and independent
- The data is regulated and you cannot justify retention

---

## 📊 Visual Diagram
```
 ┌───────────── Prompt (token budget e.g. 1500) ─────────────┐
 │ System prompt        (cached, stable)                     │
 │ LONG-TERM FACTS      {origin: CN, incoterm: FOB}          │
 │ SUMMARY              "classifying lithium battery packs"  │
 │ RECENT TURNS (4)     user/bot/user/bot                    │
 │ NEW QUESTION                                              │
 └───────────────────────────────────────────────────────────┘
   old turns ──► summarise ──► summary      chit-chat ──► dropped
```

---

## 💰 Cost Impact
- Without management, a 30-turn chat at ~100 tokens per message resends up to ~3000 tokens per call and grows linearly; total tokens over the chat grow roughly quadratically.
- With a 1500-token budget, input per call stays flat. At 100K calls/day on gpt-4o-mini ($0.15 per 1M input), saving 1500 tokens per call saves about $22/day.
- The summarisation call itself costs tokens, so run it only when the window overflows and use a cheap model.
- Put the stable system prompt first so provider prompt caching can discount it.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sliding window | Keep only last N turns | सिर्फ आखिरी N turns रखना |
| Summary memory | Compressed older conversation | पुरानी बातचीत का सार |
| Fact store | Structured long-term facts | Structured long-term facts |
| Token budget | Max tokens for memory | Memory के लिए token सीमा |
| Lossy | Some detail is lost | कुछ detail खो जाती है |
| Regression test | Test to catch new breakage | नई गड़बड़ पकड़ने वाला test |

---

## ⚡ 3-Line Summary
English: Split memory into facts, summary and recent turns, and keep the whole block under a token budget. Store only confirmed, useful facts and let newer facts replace older ones. Test memory and track tokens, because summaries lose exact details.
Hindi: Memory को facts, summary और recent turns में बाँटो और पूरा block token budget में रखो। सिर्फ confirmed और काम के facts store करो, नया fact पुराने को replace करे। Memory को test करो और tokens track करो, क्योंकि summary में exact details खो जाती हैं।

---

## ➡️ Next Topic
**389. Why Evaluation Matters** — memory is built; now learn how to measure whether the whole AI system actually gives correct answers.
