---

# 383. Memory Compression
# हिंदी में: Memory Compression

---

## 🔵 Simple Definition (English)
Memory compression makes stored memory smaller while keeping what matters: summarising old turns, merging duplicate facts, dropping filler, and storing short structured facts instead of raw text.

## 🔵 सरल परिभाषा (Hindi)
Memory compression stored memory को छोटा करती है, ज़रूरी बातें रखते हुए: पुराने turns का summary, duplicate facts merge, filler हटाना, और raw text की जगह छोटे structured facts store करना।

---

## 🔴 Problem it Solves
Memory grows every turn. Raw logs cost tokens when injected and noise hurts retrieval. Compression keeps memory cheap to store, cheap to send, and easy to search.

## 🔴 यह क्यों बना? (Hindi)
Memory हर turn बढ़ती है। Raw logs inject करने पर tokens खर्च होते हैं और noise retrieval बिगाड़ता है। Compression memory को store करने, भेजने और खोजने में सस्ता रखती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Trigger: memory exceeds N tokens or every K turns
Step 2 → Pick the oldest chunk (keep the newest turns raw)
Step 3 → Extract facts (entities, decisions, numbers) first
Step 4 → Summarise the remaining narrative with a cheap LLM
Step 5 → Merge with the existing summary (rolling summary)
Step 6 → Dedupe facts; keep newest on conflict
Step 7 → Store compressed version; archive raw text cold (optional)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Trigger: memory N tokens से बड़ी हो या हर K turns पर
Step 2 → सबसे पुराना chunk लो (नए turns raw रखो)
Step 3 → पहले facts निकालो (entities, decisions, numbers)
Step 4 → बाकी narrative को सस्ते LLM से summarise करो
Step 5 → मौजूदा summary से merge करो (rolling summary)
Step 6 → Facts dedupe करो; conflict में नया रखो
Step 7 → Compressed version store करो; raw text cold archive (optional)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A 60-turn classification session (4,500 tokens) compresses into: facts "product=48V Li-ion pack; origin=Vietnam; HS=8507.60; ruling=duty 20 percent" plus a 60-token summary. The next session starts with about 100 tokens of context. **Amazon-style**: years of orders compress into "prefers Nike, size 42, buys monthly".

## 🟡 Real Example Hindi mein
**Tariff System**: 60-turn classification session (4,500 tokens) compress होकर बनती है: facts "product=48V Li-ion pack; origin=Vietnam; HS=8507.60; ruling=duty 20 percent" और 60-token summary। अगला session लगभग 100 tokens के context से शुरू होता है। **Amazon-style**: सालों के orders compress होकर "Nike पसंद, size 42, हर महीने खरीदता है"।

---

## 💻 Code Example — Basic
```python
# Pure Python compression: dedupe + drop filler + keep newest on conflict. Runs offline.
FILLER = {"ok", "thanks", "hello", "hi", "sure"}              # low-value messages

def compress(facts: list[str]) -> list[str]:
    latest: dict[str, str] = {}                               # key -> newest value
    for line in facts:
        if line.lower().strip(" .!") in FILLER:               # skip filler
            continue
        if ":" in line:                                       # structured fact "key: value"
            key, value = line.split(":", 1)
            latest[key.strip().lower()] = value.strip()       # newer overwrites older
        else:
            latest[line.lower()] = ""                         # free text kept once (dedupe by dict key)
    return [f"{k}: {v}" if v else k for k, v in latest.items()]   # back to strings

raw = ["hello", "origin: China", "product: battery", "ok", "origin: Vietnam", "product: battery"]
print(compress(raw))                                          # ['origin: Vietnam', 'product: battery']
```

## 💻 Code Example — Advanced
```python
# Production: rolling summary compressor, async, with token trigger and safe fallback.
import logging                                                # logs
import tiktoken                                               # counting
from openai import AsyncOpenAI, OpenAIError                   # LLM

log = logging.getLogger("compress")                           # logger
enc = tiktoken.get_encoding("o200k_base")                     # encoding

class RollingMemory:
    def __init__(self, max_raw_tokens: int = 1500, keep_last: int = 4) -> None:
        self.client = AsyncOpenAI()                           # needs OPENAI_API_KEY
        self.summary = ""                                     # compressed past
        self.raw: list[str] = []                              # recent turns, uncompressed
        self.max_raw_tokens = max_raw_tokens                  # trigger size
        self.keep_last = keep_last                            # turns never compressed

    def _raw_tokens(self) -> int:
        return sum(len(enc.encode(t)) for t in self.raw)      # tokens in raw buffer

    async def add(self, turn: str) -> None:
        self.raw.append(turn)                                 # always append
        if self._raw_tokens() > self.max_raw_tokens and len(self.raw) > self.keep_last:
            await self._compress()                            # compress when over budget

    async def _compress(self) -> None:
        old, self.raw = self.raw[:-self.keep_last], self.raw[-self.keep_last:]   # split old/new
        prompt = (f"Existing summary:\n{self.summary}\n\nNew turns:\n" + "\n".join(old)
                  + "\n\nUpdate the summary in under 120 words. Keep names, numbers, codes, decisions.")
        try:
            r = await self.client.chat.completions.create(
                model="gpt-4o-mini", max_tokens=200, temperature=0,
                messages=[{"role": "user", "content": prompt}])
            self.summary = r.choices[0].message.content or self.summary   # new summary
        except OpenAIError as exc:
            log.warning("compress failed, restoring raw: %s", exc)
            self.raw = old + self.raw                         # do not lose data on failure

    def context(self) -> str:
        return f"Summary: {self.summary}\nRecent:\n" + "\n".join(self.raw)   # prompt text
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks                  # app + bg
from pydantic import BaseModel                                # model

app = FastAPI()                                               # app
mems: dict[str, RollingMemory] = {}                           # session -> memory

class Msg(BaseModel):
    session_id: str                                           # session
    text: str                                                 # message

@app.post("/turn")
async def turn(m: Msg, bg: BackgroundTasks) -> dict[str, str]:
    mem = mems.setdefault(m.session_id, RollingMemory())      # get/create
    ctx = mem.context()                                       # use for the LLM prompt
    bg.add_task(mem.add, m.text)                              # compress off the request path
    return {"context_preview": ctx[:200]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.messages import RemoveMessage, HumanMessage, SystemMessage   # message ops
from langchain_openai import ChatOpenAI                       # model

llm = ChatOpenAI(model="gpt-4o-mini")                         # cheap summariser

def summarize_node(state: dict) -> dict:
    msgs = state["messages"]                                  # LangGraph messages list
    if len(msgs) <= 6:                                        # nothing to do
        return {}
    old = msgs[:-4]                                           # compress all but last 4
    text = "\n".join(str(m.content) for m in old)             # flatten
    summary = llm.invoke(f"Summarise briefly, keep codes and numbers:\n{text}").content
    deletes = [RemoveMessage(id=m.id) for m in old]           # remove old (needs add_messages reducer)
    return {"messages": deletes + [SystemMessage(f"Summary: {summary}")], "summary": summary}
# Pattern from LangGraph docs: summarise node + trim by RemoveMessage.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Summarising away exact numbers and codes
✅ Correct: extract hard facts first, summarise only the narrative.

```python
# Wrong
"Summarise this chat"
# Right
"Keep every HS code, number, name and decision verbatim; summarise the rest"
```

❌ Mistake 2: Compressing on the request path (user waits)
✅ Correct: background task or queue.

```python
# Wrong
await mem._compress(); return answer
# Right
bg.add_task(mem.add, text)
```

---

## 🧠 Tricky Interview Question
**Q**: "After many compressions the bot forgets an early detail. Why?"

**Answer**: Repeated lossy summarisation of a summary ("telephone game") drifts and drops rare details. Mitigate: keep a structured fact store separate from prose, keep raw archive for re-summarisation, compress from raw not from summaries when possible, and test recall of seeded facts.

---

## ⚫ Interview Questions + Answers

Q1: What is memory compression? (Easy)
A1: Reducing memory size while preserving key information, via summary, dedupe and facts.

Q2: When to trigger it? (Easy)
A2: When memory crosses a token threshold or after K turns.

Q3: Lossy vs lossless? (Medium)
A3: Dedupe and structuring are near-lossless; summarisation is lossy. Use lossless first.

Q4: How do you measure compression quality? (Medium)
A4: Compression ratio plus downstream tests: seed facts, ask questions after compression, measure answer correctness.

Q5: Design compression for 1M users cheaply. (Hard)
A5: Event-driven workers per user, cheap model, batch several users' jobs, only compress when threshold passes, store facts structured, archive raw to object storage, rate-limit, and monitor cost per compression.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long-lived memory
- Token costs matter

❌ Avoid when:
- Legal/audit text must be verbatim (archive instead)
- Sessions are short

---

## 📊 Visual Diagram
```
 raw turns: t1 t2 t3 t4 t5 t6 t7 t8 t9 t10
            └──── old ────┘ └── keep raw ──┘
                  │ facts + summary
                  ▼
 [facts: HS=8507.60, origin=VN] [summary 80 tokens] + t7..t10
```

---

## 💰 Cost Impact
Compression costs one cheap call (about 700 tokens, roughly $0.0002 on gpt-4o-mini) but saves thousands of input tokens on every later call. Break-even is usually within 2-3 subsequent turns. Optimise by compressing in batches and in the background.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compression | Make smaller, keep meaning | छोटा करना, अर्थ रखना |
| Rolling summary | Updated summary | लगातार update होता summary |
| Lossy | Some info lost | कुछ info खोना |
| Dedupe | Remove duplicates | duplicates हटाना |
| Cold storage | Cheap archive | सस्ता archive |

---

## ⚡ 3-Line Summary
English: Compress memory by facts, dedupe and rolling summaries. Do it in the background when a threshold is crossed. Keep exact facts separate to avoid drift.
Hindi: Facts, dedupe और rolling summary से memory compress करो। Threshold पार होने पर background में करो। Drift से बचने के लिए exact facts अलग रखो।

---

## ➡️ Next Topic
**384. Memory Retrieval** - how to fetch the right memories fast and accurately.
