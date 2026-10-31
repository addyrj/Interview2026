---

# 212. Context Window Management
# हिंदी में: Context Window Management

---

## 🔵 Simple Definition (English)
Context window management means deciding what goes into the limited token space of an LLM call: system prompt, chat history, retrieved chunks, the question, and room for the answer. You count tokens, set a budget for each part, and trim what does not fit.

## 🔵 सरल परिभाषा (Hindi)
Context window management का मतलब है LLM call की सीमित token space में क्या जाएगा यह तय करना: system prompt, chat history, retrieved chunks, question और answer के लिए जगह। Tokens गिनो, हर हिस्से का budget बनाओ और जो fit न हो उसे काटो।

---

## 🔴 Problem it Solves
Even with 128K windows, stuffing everything is slow, expensive, and less accurate (see "lost in the middle"). Without a budget, long chats or many chunks overflow the limit and the API returns a context-length error, or older important messages get silently dropped.

## 🔴 यह क्यों बना? (Hindi)
128K window में भी सब कुछ भरना धीमा, महँगा और कम accurate होता है ("lost in the middle")। Budget के बिना लंबी chats या ज़्यादा chunks limit पार कर देते हैं और API context-length error देती है, या पुराने ज़रूरी messages चुपचाप गिर जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Know the model limit (e.g. 128,000 tokens) and your safe usable share
Step 2 → Reserve output tokens (e.g. 800) -> input budget = limit - output reserve
Step 3 → Allocate: system 300 | history 2,000 | question 200 | chunks the rest
Step 4 → Count tokens with the model's tokenizer (tiktoken)
Step 5 → Fill chunks in ranked order until the chunk budget is full
Step 6 → If still too big: drop low-rank chunks, summarise history, compress
Step 7 → Log tokens used vs budget for monitoring
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Model की limit (जैसे 128,000 tokens) और safe usable हिस्सा जानो
Step 2 → Output tokens reserve करो (जैसे 800) -> input budget = limit - reserve
Step 3 → बाँटो: system 300 | history 2,000 | question 200 | बाकी chunks
Step 4 → Model के tokenizer (tiktoken) से tokens गिनो
Step 5 → Chunks को rank order में भरो जब तक chunk budget खत्म न हो
Step 6 → फिर भी बड़ा हो तो low-rank chunks हटाओ, history summarise या compress करो
Step 7 → Budget बनाम used tokens log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A user uploads a 60-page customs notice and keeps chatting. Budget (8K target for cost): system 300, history 1,500, question 100, chunks 5,000, output 800. The pipeline reranks 30 chunks and packs the top ones until 5,000 tokens. **Zomato**: a long support chat is summarised after 10 turns. **Amazon**: product Q&A packs the top reviews until the budget is full.

## 🟡 Real Example Hindi mein
**Tariff System**: User 60-page customs notice upload करता है और chat करता रहता है। Budget (cost के लिए 8K target): system 300, history 1,500, question 100, chunks 5,000, output 800। Pipeline 30 chunks rerank करके top chunks को 5,000 tokens तक पैक करता है। **Zomato**: 10 turns के बाद लंबी support chat summarise होती है। **Amazon**: budget भरने तक top reviews पैक होते हैं।

---

## 💻 Code Example — Basic
```python
# Pure Python token budgeting. Uses a rough 4-chars-per-token counter so it runs offline.
from typing import List, Tuple  # type hints


def approx_tokens(text: str) -> int:
    """Rough count: 1 token is about 4 characters (use tiktoken in production)."""
    return max(1, len(text) // 4)  # at least 1


def pack_chunks(chunks: List[str], budget: int) -> Tuple[List[str], int]:
    """Add chunks in ranked order until the budget is used. Returns (kept, used_tokens)."""
    kept: List[str] = []  # chunks that fit
    used = 0  # tokens used so far
    for ch in chunks:  # best chunk first
        t = approx_tokens(ch)  # cost of this chunk
        if used + t > budget:  # would overflow
            continue  # skip it, a smaller later chunk might still fit
        kept.append(ch)  # keep chunk
        used += t  # update usage
    return kept, used  # result


if __name__ == "__main__":
    LIMIT, OUTPUT_RESERVE, SYSTEM, HISTORY, QUESTION = 2000, 300, 100, 400, 50  # toy numbers
    chunk_budget = LIMIT - OUTPUT_RESERVE - SYSTEM - HISTORY - QUESTION  # 1150 tokens for chunks
    chunks = ["a" * 2000, "b" * 1600, "c" * 800, "d" * 400]  # sizes 500,400,200,100 tokens
    kept, used = pack_chunks(chunks, chunk_budget)  # pack
    print("budget", chunk_budget, "used", used, "kept", len(kept))  # budget report
```

## 💻 Code Example — Advanced
```python
# Production: exact tiktoken counts, per-part budget, history trimming, async-friendly.
import logging  # logs
from dataclasses import dataclass  # config

import tiktoken  # pip install tiktoken

logger = logging.getLogger("ctx_budget")  # logger


@dataclass(frozen=True)
class Budget:
    model_limit: int = 128_000  # model context size
    target: int = 8_000  # our own cheaper cap per request
    output_reserve: int = 800  # tokens kept for the answer
    system: int = 400  # max for system prompt
    history: int = 1_500  # max for chat history


class ContextManager:
    def __init__(self, budget: Budget = Budget(), model: str = "gpt-4o-mini") -> None:
        try:  # unknown model name falls back
            self.enc = tiktoken.encoding_for_model(model)  # exact tokenizer
        except KeyError:
            self.enc = tiktoken.get_encoding("o200k_base")  # fallback encoding
        self.b = budget  # store budget

    def count(self, text: str) -> int:
        return len(self.enc.encode(text))  # exact token count

    def trim_history(self, history: list[dict]) -> list[dict]:
        """Keep the most recent messages that fit the history budget."""
        kept: list[dict] = []  # result
        used = 0  # tokens used
        for msg in reversed(history):  # newest first
            t = self.count(msg["content"]) + 4  # +4 message overhead
            if used + t > self.b.history:  # over budget
                break  # stop, older ones dropped
            kept.append(msg)  # keep
            used += t  # add
        return list(reversed(kept))  # restore chronological order

    def pack(self, system: str, history: list[dict], question: str, chunks: list[str]) -> dict:
        """Return messages plus a usage report. Raises if system+question alone is too big."""
        sys_t, q_t = self.count(system), self.count(question)  # fixed parts
        if sys_t > self.b.system:  # system prompt too large
            raise ValueError(f"system prompt {sys_t} > {self.b.system} tokens")  # fail loudly
        hist = self.trim_history(history)  # trimmed history
        hist_t = sum(self.count(m["content"]) + 4 for m in hist)  # history tokens
        room = min(self.b.target, self.b.model_limit) - self.b.output_reserve - sys_t - hist_t - q_t  # chunk room
        kept: list[str] = []  # chunks that fit
        used = 0  # chunk tokens
        for ch in chunks:  # ranked order
            t = self.count(ch)  # cost
            if used + t <= room:  # fits
                kept.append(ch)  # keep
                used += t  # add
        logger.info("ctx used=%d room=%d kept=%d/%d", used, room, len(kept), len(chunks))  # monitoring
        return {"chunks": kept, "history": hist, "chunk_tokens": used, "room": room}  # result
```

---

## 🟠 FastAPI Integration
Apply the budget in the route before calling the LLM. Return token usage so the client and logs can track it. Return 413 if the user's own question is too large.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app
ctx = ContextManager()  # shared (tokenizer loaded once)


class Req(BaseModel):
    question: str  # question
    history: list[dict] = []  # prior turns


@app.post("/ask")  # route
async def ask(req: Req) -> dict:
    if ctx.count(req.question) > 2000:  # reject abuse early
        raise HTTPException(status_code=413, detail="Question too long")  # payload too large
    ranked_chunks = ["chunk 1 ...", "chunk 2 ..."]  # from retrieval + rerank
    packed = ctx.pack("You are a tariff assistant.", req.history, req.question, ranked_chunks)  # budget
    return {"kept_chunks": len(packed["chunks"]), "chunk_tokens": packed["chunk_tokens"]}  # info
```

---

## 🔗 LangChain / LangGraph Connection
`langchain_core.messages.trim_messages` trims chat history by token count. In LangGraph, put a `trim` step before the model node, and keep full history in the checkpointer.

```python
from langchain_core.messages import trim_messages  # history trimmer
from langchain_openai import ChatOpenAI  # model (also provides token counting)

# trimmer = trim_messages(
#     max_tokens=1500,               # history budget
#     strategy="last",               # keep the most recent
#     token_counter=ChatOpenAI(model="gpt-4o-mini"),  # counts tokens
#     include_system=True,           # always keep system message
#     start_on="human",              # valid conversation start
# )
# trimmed = trimmer.invoke(messages)  # use before the LLM call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to reserve output tokens
✅ Correct: input + max_tokens must be within the window.

```python
# Wrong: input fills 100% of the window, the answer gets cut or the call errors
messages = pack_everything(limit=128_000)

# Right: reserve output
input_budget = 128_000 - 800
```

❌ Mistake 2: Dropping the oldest messages including the system prompt
✅ Correct: Always keep the system prompt; trim only history.

```python
# Wrong: truncating the list from the start removes the rules
messages = messages[-10:]

# Right: system + last N turns
messages = [messages[0]] + messages[-10:]
```

---

## 🧠 Tricky Interview Question
**Q**: "The model supports 1M tokens. Why not drop retrieval and put all documents in the prompt?"

**Answer**: Cost (you pay for every input token on every request), latency (long prefill), accuracy (lost in the middle, distracting content), no fine-grained access control or citations, and knowledge bases usually exceed even 1M tokens and change daily. Long context helps for single big documents or when caching a stable prefix; RAG stays better for large, changing, permissioned corpora. Often combine both: retrieve generously, then pack within a deliberate budget.

---

## ⚫ Interview Questions + Answers

Q1: What is a context window?
A1: The maximum number of tokens (input + output) a model can handle in one call.

Q2: Why reserve tokens for output?
A2: The output counts toward the window. Without a reserve the answer may be truncated or the request rejected.

Q3: How do you count tokens accurately?
A3: Use the model's tokenizer (tiktoken for OpenAI) and add per-message overhead. Anthropic and others provide token-counting endpoints.

Q4: How to handle long chat history?
A4: Sliding window of recent turns, plus a running summary of older turns, plus selective memory retrieval for specific facts.

Q5: Design token management for a multi-tenant RAG API.
A5: Per-tenant limits and quotas, a global token budget per request, exact counting with cached tokenizers, tiered models by plan, history summarisation, hard caps on question size, usage logging per tenant for billing, alerts on budget overruns, and graceful degradation (fewer chunks) instead of errors.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chats are multi-turn and growing
- Many chunks or long documents are involved
- Cost and latency are monitored

❌ Avoid over-engineering when:
- Single short prompts with tiny context
- Prototypes (but still reserve output tokens)

---

## 📊 Visual Diagram
```
|<──────────── target context 8,000 tokens ────────────>|
┌────────┬──────────┬────────┬─────────────────┬────────┐
│ system │ history  │ quest. │ chunks (ranked) │ output │
│  300   │  1,500   │  100   │     5,300       │  800   │
└────────┴──────────┴────────┴─────────────────┴────────┘
          trim old    fixed     fill until full   reserved
```

---

## 💰 Cost Impact
- Cost scales with input tokens on every call. An 8K target vs 32K stuffing is 4x cheaper on input.
- Example on gpt-4o-mini ($0.15 per 1M input, as used in this repo's notes): 8,000 tokens = $0.0012 per query; 32,000 tokens = $0.0048. At 100K queries per day the difference is about $360 per day.
- Optimise: set a target well below the model limit, trim history, summarise, compress chunks, use prompt caching for the stable prefix.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context window | Max tokens per call | एक call में max tokens |
| Token budget | Planned token split | Tokens का बँटवारा |
| Output reserve | Tokens kept for answer | Answer के लिए रखे tokens |
| Sliding window | Keep only recent turns | सिर्फ़ हाल की turns रखना |
| tiktoken | Exact token counter | सटीक token counter |

---

## ⚡ 3-Line Summary
English: Treat the context window as a budget: system, history, question, chunks, and output reserve. Count tokens exactly and trim history and low-rank chunks. A smaller, deliberate context is cheaper, faster and often more accurate.
Hindi: Context window को budget की तरह देखो: system, history, question, chunks और output reserve। Tokens सटीक गिनो और history व low-rank chunks काटो। छोटा, सोचा-समझा context सस्ता, तेज़ और अक्सर ज़्यादा accurate होता है।

---

## ➡️ Next Topic
**213. Context Compression** — shrinking the chunks themselves so more useful information fits in the budget.
