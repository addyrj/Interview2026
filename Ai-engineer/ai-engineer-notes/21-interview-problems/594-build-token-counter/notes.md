---

# 594. Build Token Counter
# हिंदी में: Token Counter बनाना

---

## 🔵 Simple Definition (English)
A token counter tells you how many tokens a text or a chat message list will use, before you send it. It lets you check the context window, estimate cost, and truncate safely.

## 🔵 सरल परिभाषा (Hindi)
Token counter बताता है कि कोई text या chat messages कितने tokens लेंगे, भेजने से पहले। इससे context window check, cost estimate और safe truncation होता है।

---

## 🔴 Problem it Solves
Counting characters or words is wrong: tokens differ by model and by language (Hindi uses far more tokens per character than English). Sending too much causes API errors or truncated context; sending too little wastes capacity.

## 🔴 यह क्यों बना? (Hindi)
Characters या words गिनना गलत है: tokens model और language के हिसाब से बदलते हैं (Hindi में English से ज़्यादा tokens लगते हैं)। ज़्यादा भेजने पर error या truncation होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load the tokenizer for the target model (tiktoken encoding)
Step 2 → If unavailable, use a heuristic (~4 chars/token, Devanagari heavier)
Step 3 → count_text: len(encode(text))
Step 4 → count_messages: sum text tokens + per-message overhead + reply priming
Step 5 → fits_context: count + reserved output <= window
Step 6 → truncate_to_tokens: encode, slice, decode
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Model का tokenizer load करो (tiktoken)
Step 2 → न मिले तो heuristic (~4 chars/token, Devanagari ज़्यादा भारी)
Step 3 → count_text: len(encode(text))
Step 4 → count_messages: text tokens + हर message का overhead + reply priming
Step 5 → fits_context: count + output reserve <= window
Step 6 → truncate: encode, slice, decode
```

---

## 🟡 Real World Example
**Tariff Classification System**: A broker uploads a 60-page tariff note. The counter says 90,000 tokens, which exceeds the chosen budget of 8,000 for context, so the system chunks it and retrieves only relevant parts. Hindi-language invoices are counted with the heavier ratio so cost estimates stay honest.

**Amazon-style**: a product-review summariser trims reviews to a token budget before the call.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker 60-page tariff note upload करता है। Counter बताता है 90,000 tokens, जो 8,000 के budget से ज़्यादा है, इसलिए chunking + retrieval होती है। Hindi invoices के लिए heavier ratio से cost estimate सही रहता है।

**Amazon**: Review summariser calls से पहले reviews को token budget में काटता है।

---

## 💻 Code Example — Basic
```python
# Heuristic counter (no libraries needed); an ESTIMATE only
def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token for English."""
    if not text:                              # empty text has zero tokens
        return 0
    return max(1, round(len(text) / 4))       # at least 1 token for any text


print(estimate_tokens("Tariff classification for electronics"))  # 38 chars -> 10
```

## 💻 Code Example — Advanced
Full file: `main.py`. It tries `tiktoken` (exact) and falls back to a heuristic. Observed run here (tiktoken not available, so heuristic):
```
engine: heuristic
messages: 25
hindi vs english: 9 5
fits 128k: True
truncated: 'word word word word'
async: 3
```
```python
# Excerpt from main.py
def count_messages(messages: list[dict[str, str]]) -> int:
    total = 3                                    # reply priming (approximate)
    for m in messages:                           # every chat message
        if "content" not in m or "role" not in m:
            raise ValueError("message needs role and content")   # validate input
        total += 4 + count_text(m["role"]) + count_text(m["content"])  # overhead+text
    return total                                 # overhead values vary by model


async def acount(text: str) -> int:
    return await asyncio.to_thread(count_text, text)   # keep CPU work off the loop
```
Exact overhead per message differs by model; treat message counts as approximate and prefer the provider's reported `usage` or a token-counting endpoint where available.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import acount, truncate_to_tokens             # our module

app = FastAPI()


class Doc(BaseModel):
    text: str
    max_tokens: int = 8000


@app.post("/tokens")
async def tokens(doc: Doc) -> dict:
    n = await acount(doc.text)                          # count off the event loop
    if doc.max_tokens < 0:                              # input validation
        raise HTTPException(status_code=422, detail="max_tokens must be >= 0")
    return {"tokens": n, "fits": n <= doc.max_tokens,
            "preview": truncate_to_tokens(doc.text, min(doc.max_tokens, 50))}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain chat models have `get_num_tokens(text)`; `trim_messages` keeps a conversation inside a token budget.

```python
from langchain_core.messages import trim_messages, HumanMessage, AIMessage


def count_tokens_approx(messages) -> int:
    return sum(len(str(m.content)) // 4 for m in messages)   # swap in real counter


history = [HumanMessage("hi " * 50), AIMessage("hello " * 50), HumanMessage("HS for laptop?")]
trimmed = trim_messages(history, max_tokens=60, token_counter=count_tokens_approx,
                        strategy="last")                      # keep newest messages
```
In LangGraph, run trimming inside a node before the LLM node so state never overflows the window.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `len(text.split())` as the token count.
✅ Correct: use the model's tokenizer.
```python
# Wrong
n = len(text.split())
# Right
n = count_text(text)
```

❌ Mistake 2: Forgetting to reserve room for the output.
✅ Correct: `input_tokens + max_output <= window`.

❌ Mistake 3: Truncating by characters mid-token, or cutting JSON in half. Truncate by tokens, preferably at chunk boundaries.

---

## 🧠 Tricky Interview Question
**Q**: "Your counter says the prompt is 7,900 tokens for an 8,192 window, but the API rejects it. Why?"

**Answer**: Message overhead and special tokens, tool/function schemas, and the reserved `max_tokens` for output all count toward the window, and a different tokenizer (another model family) gives a different count. Fix: reserve a safety margin, count with the exact model's tokenizer or provider count endpoint, and include tool definitions in the count.

---

## ⚫ Interview Questions + Answers

Q1: What is a token?
A1: A subword unit of text that the model reads; prices and limits are in tokens.

Q2: Why does Hindi cost more than English?
A2: Tokenizer vocabularies are mostly learned from English, so Devanagari splits into more, smaller pieces.

Q3: Why wrap counting in `asyncio.to_thread`?
A3: Tokenizing a large document is CPU-bound and would block the event loop for other requests.

Q4: How do you count tokens for chat messages?
A4: Sum content tokens plus the per-message and reply overhead specific to the model; verify with the provider's `usage`.

Q5 (Hard): How do you keep a long chat inside the window without losing key facts?
A5: Keep the system prompt, keep the last N turns by token budget, and summarise older turns into a rolling summary (or store them in memory/RAG); re-count after each step.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Documents of unknown size, RAG chunking, chat history trimming
- Pre-call cost estimates and quotas

❌ Avoid when:
- Tiny fixed prompts far from the limit (a heuristic is enough)

---

## 📊 Visual Diagram
```
 text ─► tokenizer ─► [ids] ─► count
   │          │ missing?
   │          ▼
   │     heuristic (chars/4, Hindi x1.5)
   ▼
 messages: 3 + Σ(4 + role + content)  ─►  + reserve_output <= window ?
                                              │yes        │no
                                              ▼           ▼
                                            send     truncate / RAG
```

---

## 💰 Cost Impact
Counting locally with a tokenizer is free (no API call). It saves money by catching oversized prompts before they are billed and by enabling trimming. Optimise: cache counts for static prompts, count once per chunk at ingest time, and store the count with the chunk.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tokenizer | Splits text into tokens | Text को tokens में बाँटने वाला |
| Context window | Max tokens per request | एक request की token सीमा |
| Heuristic | Rough estimate rule | अनुमान का नियम |
| Truncate | Cut to fit | काटकर छोटा करना |
| Reserve output | Room left for the answer | Answer के लिए जगह |

---

## ⚡ 3-Line Summary
English: Count with the model's tokenizer, fall back to a heuristic only as an estimate. Include message overhead and output reserve. Truncate by tokens.
Hindi: Model के tokenizer से count करो, heuristic सिर्फ अनुमान है। Message overhead और output reserve जोड़ो। Truncation tokens के हिसाब से करो।

---

## ➡️ Next Topic
**595. Build Prompt Manager** — once sizes are under control, manage prompt versions safely.
