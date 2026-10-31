---

# 381. Context Window Management
# हिंदी में: Context Window Management

---

## 🔵 Simple Definition (English)
Context window management is deciding what goes into the model's limited input space on each call: system prompt, history, memories, documents, and room for the answer. When things do not fit, you trim, summarise or retrieve instead.

## 🔵 सरल परिभाषा (Hindi)
Context window management का मतलब है हर call में model की सीमित input जगह में क्या जाएगा ये तय करना: system prompt, history, memories, documents और जवाब के लिए जगह। जब सब fit न हो, तो trim, summarise या retrieve करते हैं।

---

## 🔴 Problem it Solves
Chats and documents grow, but windows are finite and cost grows per token. Overflow causes API errors or silent loss of content; stuffing the window hurts accuracy ("lost in the middle") and bill.

## 🔴 यह क्यों बना? (Hindi)
Chats और documents बढ़ते हैं पर window सीमित है और cost per token बढ़ती है। Overflow से API error या चुपचाप content खोना होता है; window भरने से accuracy ("lost in the middle") और bill दोनों बिगड़ते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Know the model limit (e.g. 128K) and reserve output space
Step 2 → Count tokens of each part (tiktoken)
Step 3 → Pin must-haves: system prompt, latest user message
Step 4 → Add retrieved docs/memories by relevance
Step 5 → Fill remaining space with recent history (newest first)
Step 6 → If still too big: summarise old turns / drop low-ranked chunks
Step 7 → Put key info at the start and end (not the middle)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Model की limit जानो (जैसे 128K) और output के लिए जगह रखो
Step 2 → हर हिस्से के tokens गिनो (tiktoken)
Step 3 → ज़रूरी चीज़ें pin करो: system prompt, latest user message
Step 4 → Relevance के हिसाब से docs/memories जोड़ो
Step 5 → बची जगह में recent history भरो (नई पहले)
Step 6 → फिर भी ज़्यादा हो: पुराने turns summarise / कम-ranked chunks हटाओ
Step 7 → ज़रूरी info शुरू और अंत में रखो (बीच में नहीं)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A 90-turn session plus 12 retrieved tariff chunks exceeds the window you chose (say 16K for cost). Manager pins system prompt (300), question (50), keeps top 4 chunks (2000), last 6 turns (1200), and a 200-token summary of the rest. **Zomato-style**: a support bot keeps the current order and last 5 messages, not the whole month.

## 🟡 Real Example Hindi mein
**Tariff System**: 90 turns की session और 12 retrieved tariff chunks आपकी चुनी window (मान लो cost के लिए 16K) से बड़े हैं। Manager system prompt (300), सवाल (50), top 4 chunks (2000), आखिरी 6 turns (1200) और बाकी का 200-token summary रखता है। **Zomato-style**: support bot मौजूदा order और आखिरी 5 messages रखता है, पूरा महीना नहीं।

---

## 💻 Code Example — Basic
```python
# Pure Python: fit messages into a window, newest first. Word count stands in for tokens.
def count(text: str) -> int:
    return len(text.split())                                 # crude token estimate

def fit_history(system: str, history: list[str], question: str, limit: int) -> list[str]:
    used = count(system) + count(question)                   # pinned parts always included
    kept: list[str] = []                                     # chosen history
    for msg in reversed(history):                            # walk newest -> oldest
        n = count(msg)                                       # size of this message
        if used + n > limit:                                 # does not fit
            break                                            # stop adding older ones
        kept.append(msg); used += n                          # keep it
    kept.reverse()                                           # back to chronological order
    return [system, *kept, question]                         # final prompt parts

history = [f"turn {i}: " + "word " * 10 for i in range(20)]  # 20 fake turns of 12 words
out = fit_history("You are a tariff bot.", history, "duty on batteries?", limit=60)
print(len(out) - 2, "history turns kept")                    # how many survived
```

## 💻 Code Example — Advanced
```python
# Production: token-exact manager with reserved output, pinned parts, summary fallback.
import logging                                               # logs
from dataclasses import dataclass, field                     # simple data holder
import tiktoken                                              # exact tokens

log = logging.getLogger("ctx")                               # logger
enc = tiktoken.get_encoding("o200k_base")                    # gpt-4o encoding

def tok(text: str) -> int:
    return len(enc.encode(text))                             # exact token count

@dataclass
class ContextManager:
    window: int = 16_000                                     # our chosen window (<= model max)
    reserve_output: int = 1_000                              # room for the answer
    overhead_per_msg: int = 4                                # chat format overhead
    summary: str = ""                                        # rolling summary of dropped turns
    dropped: list[str] = field(default_factory=list)         # turns we removed

    def build(self, system: str, docs: list[str], history: list[dict[str, str]], question: str) -> list[dict[str, str]]:
        budget = self.window - self.reserve_output           # usable input tokens
        pinned = tok(system) + tok(question) + 2 * self.overhead_per_msg   # must-haves
        if pinned > budget:                                  # impossible case
            raise ValueError("system+question exceed window")
        budget -= pinned                                     # what is left
        kept_docs: list[str] = []                            # chosen documents
        for d in docs[:6]:                                   # docs are already ranked
            n = tok(d)
            if n > budget * 0.5:                             # docs may use at most half the rest
                break
            kept_docs.append(d); budget -= n
        kept_hist: list[dict[str, str]] = []                 # chosen history
        for m in reversed(history):                          # newest first
            n = tok(m["content"]) + self.overhead_per_msg
            if n > budget:
                self.dropped.append(m["content"])            # remember what we lost
                continue
            kept_hist.append(m); budget -= n
        kept_hist.reverse()                                  # chronological
        sys_full = system + ("\n\nSummary of earlier chat: " + self.summary if self.summary else "")
        ctx = "\n\n".join(kept_docs)                         # documents block
        return [{"role": "system", "content": sys_full},
                *kept_hist,
                {"role": "user", "content": (f"Docs:\n{ctx}\n\n" if ctx else "") + question}]

if __name__ == "__main__":
    cm = ContextManager(window=500, reserve_output=100)      # tiny window for demo
    hist = [{"role": "user", "content": "battery question " * 20} for _ in range(10)]
    msgs = cm.build("You are a tariff bot.", ["HS 8507.60 duty 20 percent"], hist, "duty?")
    print(len(msgs), "messages;", len(cm.dropped), "dropped")
```
Async note: building context is CPU-only; call it inside your `async def` handler directly, and only the LLM call (`await client.chat.completions.create(...)`) is awaited.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException                   # app + errors
from pydantic import BaseModel                               # models

app = FastAPI()                                              # app
managers: dict[str, ContextManager] = {}                     # session -> manager

class Turn(BaseModel):
    session_id: str                                          # session key
    question: str                                            # user text

@app.post("/chat")
async def chat(t: Turn) -> dict[str, int]:
    cm = managers.setdefault(t.session_id, ContextManager()) # per-session state
    try:
        msgs = cm.build("You are a tariff bot.", [], [], t.question)   # plug real history/docs here
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc))          # payload too large
    return {"prompt_tokens": sum(tok(m["content"]) for m in msgs)}     # report size
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.messages import trim_messages, HumanMessage, AIMessage, SystemMessage   # built-in trimmer
from langchain_openai import ChatOpenAI                      # model

llm = ChatOpenAI(model="gpt-4o-mini")                        # chat model
trimmer = trim_messages(
    max_tokens=2000,                                         # budget for history
    strategy="last",                                         # keep the newest messages
    token_counter=llm,                                       # model counts tokens
    include_system=True,                                     # keep the system message
    start_on="human",                                        # valid start of conversation
)
msgs = [SystemMessage("tariff bot"), HumanMessage("hi"), AIMessage("hello"), HumanMessage("duty?")]
trimmed = trimmer.invoke(msgs)                               # use in LCEL: trimmer | llm
# LangGraph: run trim_messages (or summarisation) inside the node before calling the LLM.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Filling the whole window with input (no room for the answer)
✅ Correct: reserve output tokens.

```python
# Wrong
budget = MODEL_MAX
# Right
budget = MODEL_MAX - max_output_tokens
```

❌ Mistake 2: Truncating from the start and losing the system prompt
✅ Correct: pin system prompt, trim the middle/oldest history.

```python
# Wrong
messages = messages[-20:]
# Right
messages = [system, *messages[-20:]]
```

---

## 🧠 Tricky Interview Question
**Q**: "You moved from a 32K to a 1M-token model. Is context management still needed?"

**Answer**: Yes. Cost and latency scale with tokens, accuracy drops on long, noisy context (lost in the middle), and rate limits count tokens. A big window raises the ceiling, but relevant, compact context is still cheaper, faster and more accurate.

---

## ⚫ Interview Questions + Answers

Q1: What is a context window? (Easy)
A1: Maximum tokens (input plus output) the model handles in one call.

Q2: Why reserve output tokens? (Easy)
A2: Input and output share the window; otherwise the answer is cut off or the call errors.

Q3: Name three strategies when history is too long. (Medium)
A3: Sliding window, summarisation of old turns, retrieval of relevant past turns (vector memory).

Q4: What is "lost in the middle"? (Medium)
A4: Models use information at the start and end of long contexts better than the middle; order matters.

Q5: Design a policy for a chatbot with docs, memory and history. (Hard)
A5: Fixed token shares per section, pin system+question, rank docs and cut, newest-first history with rolling summary, put key facts at edges, log token usage per section, alert on overflows, and test with adversarially long inputs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chats longer than a few turns
- RAG with many chunks
- Cost-sensitive production

❌ Avoid over-engineering when:
- One-shot short prompts
- Prototype stage

---

## 📊 Visual Diagram
```
 |<----------------- window (16K) ----------------->|
 [system][summary][docs ......][history ...][question][output reserve]
  pinned  rolling   ranked,cut   newest-first  pinned   never used for input
```

---

## 💰 Cost Impact
Input tokens are billed on every call, so a 10K-token history resent on 100 turns costs 1M input tokens (about $0.15 on gpt-4o-mini, $2.50 on gpt-4o-class). Trimming to 2K cuts that 5x. Also use prompt caching for the stable prefix (system + pinned docs).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context window | Max tokens per call | एक call की max token सीमा |
| Pinned | Always included | हमेशा शामिल |
| Sliding window | Keep newest turns | नए turns रखना |
| Rolling summary | Summary updated over time | बढ़ता हुआ summary |
| Lost in the middle | Weak recall of middle text | बीच के text की कमज़ोर याद |

---

## ⚡ 3-Line Summary
English: Decide per call what enters the window and reserve room for the answer. Pin essentials, rank extras, trim oldest, summarise the rest. Bigger windows do not remove the need.
Hindi: हर call में तय करो window में क्या जाएगा और जवाब के लिए जगह रखो। ज़रूरी चीज़ें pin करो, extras rank करो, पुराना trim करो, बाकी summarise करो। बड़ी window से ये ज़रूरत खत्म नहीं होती।

---

## ➡️ Next Topic
**382. Token Budget Management** - turning these limits into explicit per-section and per-user budgets.
