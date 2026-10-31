---

# 373. Conversation History Management
# हिंदी में: Conversation History Management (बातचीत के इतिहास का प्रबंधन)

---

## 🔵 Simple Definition (English)
Conversation history management is the set of rules for storing, ordering, cleaning, trimming and sending the message list to the LLM: valid roles, alternating turns, tool-call pairing, token limits, and what to keep or drop.

## 🔵 सरल परिभाषा (Hindi)
Conversation history management उन नियमों का समूह है जो तय करते हैं कि message list को कैसे store, order, साफ़, trim और LLM को भेजा जाए: सही roles, बारी-बारी turns, tool-call pairing, token limits, और क्या रखना है या हटाना है।

---

## 🔴 Problem it Solves
- Raw history grows, gets expensive and eventually errors.
- Invalid structure breaks APIs (e.g. a `tool` message without its preceding assistant `tool_calls`; Anthropic requires first message from user).
- Huge tool outputs and duplicated content waste tokens.

## 🔴 यह क्यों बना? (Hindi)
- कच्ची history बढ़ती है, महँगी होती है और आखिर में error देती है।
- गलत structure API तोड़ देता है (जैसे `tool` message बिना उसके assistant `tool_calls` के)।
- बड़े tool outputs और दोहराव tokens बर्बाद करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Store every message with id, role, content, timestamp, token_count
Step 2 → Validate: roles allowed, tool results paired with tool calls, no empty content
Step 3 → Clean: truncate giant tool outputs, drop duplicates, strip PII if needed
Step 4 → Select: pinned messages (system, key facts) + recent window (+ summary of old)
Step 5 → Enforce token budget; never cut inside a tool-call pair
Step 6 → Send; store the reply and its usage
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर message id, role, content, time, token_count के साथ store करो
Step 2 → Validate: roles सही, tool results अपने tool calls के साथ, खाली content नहीं
Step 3 → साफ़ करो: बड़े tool outputs काटो, duplicates हटाओ, ज़रूरत हो तो PII हटाओ
Step 4 → चुनो: pinned messages (system, key facts) + हाल की window (+ पुराने का summary)
Step 5 → Token budget लगाओ; tool-call pair के बीच से कभी मत काटो
Step 6 → भेजो; reply और usage store करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The agent calls a `lookup_hs_code` tool that returns a 6,000-token table. Keeping it verbatim in history for the next 10 turns costs 60K tokens. Policy: keep the tool result for the current turn, then replace it in history with "[lookup_hs_code result: HS 6109, 3 candidates - truncated]".
**Zomato AI**: restaurant list tool outputs are trimmed after the user picks one.

## 🟡 Real Example Hindi mein
**Tariff System**: Agent `lookup_hs_code` tool call करता है जो 6,000-token की table लौटाता है। अगले 10 turns तक उसे वैसे ही रखना = 60K tokens। Policy: मौजूदा turn में रखो, फिर history में "[lookup_hs_code result: HS 6109, 3 candidates - truncated]" से बदल दो।
**Zomato AI**: user के चुनने के बाद restaurant list का tool output छोटा कर दिया जाता है।

---

## 💻 Code Example — Basic
```python
# Pure Python (offline): validate + clean + select a chat history
Message = dict[str, str]                                             # simple alias for a message

history: list[Message] = [                                           # sample raw history
    {"role": "system", "content": "Tariff assistant"},
    {"role": "user", "content": "Cotton shirt?"},
    {"role": "assistant", "content": "HS 6109"},
    {"role": "tool", "content": "X" * 5000},                         # giant tool output
    {"role": "user", "content": ""},                                 # empty message (invalid)
    {"role": "user", "content": "Duty in INR?"},
]

def clean(msgs: list[Message], max_tool_chars: int = 200) -> list[Message]:   # sanitise
    out: list[Message] = []                                          # cleaned list
    for m in msgs:                                                   # go through each
        content = m["content"].strip()                               # trim whitespace
        if not content:                                              # drop empty messages
            continue
        if m["role"] == "tool" and len(content) > max_tool_chars:    # shrink big tool output
            content = content[:max_tool_chars] + "...[truncated]"
        out.append({"role": m["role"], "content": content})          # keep cleaned copy
    return out

def select(msgs: list[Message], keep_last: int = 3) -> list[Message]:   # pinned + recent
    system = [m for m in msgs if m["role"] == "system"]              # always keep system
    rest = [m for m in msgs if m["role"] != "system"]                # everything else
    return system + rest[-keep_last:]                                # system + last N

final = select(clean(history))                                       # pipeline
for m in final:
    print(m["role"], len(m["content"]))                              # sizes after cleaning
```

## 💻 Code Example — Advanced
```python
# Async history manager: token budget + tool-pair safety + pinned facts
import asyncio                                                       # async runtime
from dataclasses import dataclass, field                             # data classes
from typing import Literal                                           # role literal

Role = Literal["system", "user", "assistant", "tool"]                # allowed roles


def est_tokens(text: str) -> int:                                    # replace with tiktoken in prod
    return max(1, len(text) // 4)


@dataclass
class Msg:
    role: Role
    content: str
    tool_call_id: str | None = None                                  # links tool result to call
    pinned: bool = False                                             # never drop

    @property
    def tokens(self) -> int:
        return est_tokens(self.content) + 4                          # +4 role/format overhead


@dataclass
class HistoryManager:
    budget: int = 2000                                               # max history tokens
    msgs: list[Msg] = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)        # concurrent request safety

    async def add(self, m: Msg) -> None:
        if not m.content.strip():                                    # reject empty
            raise ValueError("empty message")
        async with self._lock:
            self.msgs.append(m)

    def _groups(self) -> list[list[Msg]]:                            # atomic units (tool pairs stay together)
        groups: list[list[Msg]] = []
        for m in self.msgs:
            if m.role == "tool" and groups:                          # attach tool result to previous group
                groups[-1].append(m)
            else:
                groups.append([m])
        return groups

    async def window(self) -> list[Msg]:
        async with self._lock:
            groups = self._groups()
        pinned = [g for g in groups if any(m.pinned for m in g)]     # always kept
        others = [g for g in groups if g not in pinned]
        used = sum(m.tokens for g in pinned for m in g)              # pinned cost first
        keep: list[list[Msg]] = []
        for g in reversed(others):                                   # newest first
            cost = sum(m.tokens for m in g)
            if used + cost > self.budget:                            # would overflow
                break
            keep.append(g)
            used += cost
        chosen = pinned + list(reversed(keep))                       # restore order approx.
        flat = [m for g in chosen for m in g]
        while flat and flat[0].role in ("assistant", "tool"):        # APIs prefer user-first history
            flat.pop(0)
        return flat


async def main() -> None:
    hm = HistoryManager(budget=60)
    await hm.add(Msg("system", "Tariff assistant", pinned=True))
    for i in range(6):
        await hm.add(Msg("user", f"question number {i} about shirts"))
        await hm.add(Msg("assistant", f"answer {i}"))
    kept = await hm.window()
    print(len(kept), "messages kept:", [m.content for m in kept][-3:])

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Keep one `HistoryManager` per session in Redis (serialise to JSON). Return `history_tokens` in the response so the front-end/ops can see growth. Reject over-long single messages with 413.

```python
# FastAPI: per-session history manager with size guard
from fastapi import FastAPI, HTTPException          # framework

app = FastAPI()                                     # app
managers: dict[str, HistoryManager] = {}            # use Redis in production

@app.post("/chat/{session_id}")
async def chat(session_id: str, text: str) -> dict[str, int | str]:
    if len(text) > 8000:                            # protect budget
        raise HTTPException(status_code=413, detail="message too long")
    hm = managers.setdefault(session_id, HistoryManager())
    await hm.add(Msg("user", text))
    window = await hm.window()                      # what we would send
    reply = f"ok ({len(window)} msgs)"              # LLM call goes here
    await hm.add(Msg("assistant", reply))
    return {"reply": reply, "history_tokens": sum(m.tokens for m in window)}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain core provides `trim_messages`, `filter_messages` and `RemoveMessage` (LangGraph) to manage history. `trim_messages` understands roles and can keep the system message and start on a human turn.

```python
# langchain_core trim_messages: keep system + last tokens, start on human, end on human
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages

msgs = [SystemMessage("Tariff assistant"), HumanMessage("Cotton shirt?"), AIMessage("HS 6109"),
        HumanMessage("Duty in INR?")]
trimmed = trim_messages(
    msgs,
    max_tokens=3,                 # with token_counter=len, counts MESSAGES (simple demo)
    token_counter=len,            # swap for a model or tiktoken-based counter for real tokens
    strategy="last",              # keep most recent
    include_system=True,          # keep the system message
    start_on="human",             # valid conversation start
)
print([type(m).__name__ for m in trimmed])
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Cutting between a tool call and its result
✅ Correct: treat them as one unit.

```python
# Wrong: msgs[-3:]    # may start with a tool message -> API 400 error
# Right: group (assistant tool_calls + tool results) and trim by group
```

❌ Mistake 2: Mutating the stored history for display needs
✅ Correct: keep the full log in the DB; build a separate *view* to send.

```python
# Wrong: history = history[-5:]       # permanently destroys data
# Right: view = select(history)       # DB keeps everything, view is what the LLM sees
```

---

## 🧠 Tricky Interview Question
**Q**: "You trim history to the last 5 messages and the user's original instruction ('answer only in Hindi') is lost after 3 turns. What do you do?"

**Answer**: Instructions that must persist should not live in the sliding part. Pin them: put them in the system prompt or a pinned facts/preferences block that is always included, and extract them on arrival (preference detection). Combine: pinned block + running summary + recent window.

---

## ⚫ Interview Questions + Answers

Q1: Why validate history before each call?
A1: Providers reject malformed sequences (orphan tool messages, wrong first role), and bad structure wastes retries.

Q2: What should always be kept?
A2: System prompt, pinned user preferences/facts, the latest user message, tool call/result pairs of the current turn.

Q3: How do you handle huge tool outputs?
A3: Truncate or summarise after use, store the full result outside the prompt and reference by id, fetch again if needed.

Q4: Store full history or trimmed?
A4: Store full (audit, analytics, re-summarise), send a trimmed *view*.

Q5: How do you design this for streaming, concurrent requests per user?
A5: Per-session lock or optimistic version, append-only log with message ids, build the window from a consistent snapshot, idempotent writes so retries do not duplicate messages.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any multi-turn chat or agent loop
- Tool-heavy agents with large outputs

❌ Avoid heavy machinery when:
- One-shot prompts (no history)
- Short fixed-length flows (3 turns max)

---

## 📊 Visual Diagram
```
 DB (full log) ─▶ validate ─▶ clean (truncate tools) ─▶ select
                                                        │ pinned + recent + summary
                                                        ▼
                                         token budget check ─▶ LLM
```

---

## 💰 Cost Impact
- Cleaning a 6,000-token tool result to 100 tokens across 10 turns saves ~59K input tokens per conversation (about $0.009 on gpt-4o-mini, far more on larger models at scale).
- Always log `prompt_tokens` per call; alert when it exceeds the budget.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pinned message | Never dropped | कभी न हटने वाला message |
| Trim | Cut old messages | पुराने messages काटना |
| Tool pair | Call + its result | Tool call और उसका result |
| View | What is sent to LLM | LLM को जो भेजा जाए |
| Token budget | Max tokens allowed | अनुमत max tokens |

---

## ⚡ 3-Line Summary
English: Manage history by validating, cleaning and selecting a view for the LLM while keeping the full log elsewhere. Pin what must persist and keep tool pairs intact. Track tokens every call.
Hindi: History को validate, साफ़ और select करके LLM के लिए एक view बनाओ, पूरा log अलग रखो। जो ज़रूरी है उसे pin करो और tool pairs को साथ रखो। हर call में tokens track करो।

---

## ➡️ Next Topic
**374. Sliding Window Memory** — the simplest selection strategy: keep only the last N turns.
