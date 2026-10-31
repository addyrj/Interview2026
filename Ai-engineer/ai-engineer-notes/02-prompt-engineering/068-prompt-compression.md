---

# 068. Prompt Compression
# हिंदी में: Prompt Compression — कम tokens में वही मतलब

---

## 🔵 Simple Definition (English)
Prompt compression reduces the number of tokens in a prompt while keeping the information the model needs. You remove filler, shorten instructions, trim retrieved context, or summarise history. Fewer input tokens means lower cost and lower latency.

## 🔵 सरल परिभाषा (Hindi)
Prompt compression prompt के tokens घटाता है, पर model को चाहिए वाली जानकारी बनी रहती है। Filler हटाना, instructions छोटे करना, retrieved context trim करना, या history का summary बनाना इसमें आता है। कम input tokens = कम cost और कम latency।

---

## 🔴 Problem it Solves
Prompts grow: long system instructions, 10 retrieved chunks, 30 turns of chat history. You pay for every input token on every call, long prompts are slower, and they can hit the context limit. Extra text can also distract the model.

Compression keeps quality while cutting cost.

## 🔴 यह क्यों बना? (Hindi)
Prompts बढ़ते जाते हैं: लंबे system instructions, 10 retrieved chunks, 30 turns की history। हर call पर हर input token का पैसा लगता है, लंबे prompts धीमे होते हैं और context limit छू सकते हैं। फ़ालतू text model को भटका भी सकता है। Compression quality बनाए रखकर cost घटाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure: count tokens per part (system, history, context, question)
Step 2 → Find the biggest part
Step 3 → Apply a technique:
         a) Rewrite instructions shorter
         b) Drop low-value retrieved chunks (rerank, top-k smaller)
         c) Summarise old chat turns
         d) Remove duplicates, stopwords, boilerplate
         e) Use abbreviations / compact formats (tables, short keys)
Step 4 → Re-run the eval set
Step 5 → Accept only if quality stays within tolerance
Step 6 → Monitor token usage in production
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Measure: हर हिस्से के tokens गिनो (system, history, context, question)
Step 2 → सबसे बड़ा हिस्सा ढूँढो
Step 3 → Technique लगाओ:
         a) Instructions छोटे लिखो
         b) कम काम के chunks हटाओ (rerank, छोटा top-k)
         c) पुराने chat turns का summary
         d) Duplicates और boilerplate हटाओ
         e) Compact formats (छोटे keys, tables)
Step 4 → Eval set दोबारा चलाओ
Step 5 → Quality tolerance में रहे तभी accept करो
Step 6 → Production में token usage monitor करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The prompt has a 600-token system prompt, 8 retrieved tariff chunks (4,000 tokens) and a question. Compression: rewrite the system prompt to 250 tokens, rerank and keep the top 3 chunks (1,500 tokens), strip headers and page numbers. Input drops from about 4,700 to about 1,800 tokens (-60%), accuracy stays at 91%. At 200K requests/day this saves a large monthly bill.

**Amazon-style**: Long customer chat history is summarised into 150 tokens plus the last 3 turns.

## 🟡 Real Example Hindi mein
**Tariff System**: Prompt में 600-token system prompt, 8 retrieved chunks (4,000 tokens) और question है। Compression: system prompt 250 tokens में, rerank करके top 3 chunks (1,500 tokens), headers और page numbers हटाओ। Input लगभग 4,700 से 1,800 tokens (-60%), accuracy 91% ही रही। 2 लाख requests/day पर महीने का बड़ा बिल बचता है।

**Amazon-style**: लंबी chat history को 150 tokens के summary + आख़िरी 3 turns में बदला जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: measure and compress text with simple rules (pure Python, offline)
import re  # for cleaning text

def rough_tokens(text: str) -> int:
    # Rough rule: 1 token ~ 4 characters (use tiktoken for exact counts)
    return max(1, len(text) // 4)

def compress(text: str) -> str:
    text = re.sub(r"\s+", " ", text)                         # collapse spaces/newlines
    text = re.sub(r"(?i)\bpage \d+ of \d+\b", "", text)       # remove page numbers
    text = re.sub(r"(?i)\b(please|kindly|very|really|basically)\b ", "", text)   # filler words
    return text.strip()                                       # trim ends

verbose = """
Please kindly make sure that you are very careful and you really should
classify the product below into the correct HS code.   Page 3 of 40
"""

short = compress(verbose)                                     # compressed version
print(short)                                                  # cleaner text
print(rough_tokens(verbose), "->", rough_tokens(short))       # token estimate before -> after
```

## 💻 Code Example — Advanced
```python
# Production: token-budgeted context builder + history summarisation (async)
from __future__ import annotations

import asyncio                                    # async runner
from dataclasses import dataclass                 # chunk container
from typing import Awaitable, Callable            # type hints

import tiktoken                                   # exact token counts (pip install tiktoken)

LLM = Callable[[str], Awaitable[str]]             # prompt -> reply
ENC = tiktoken.get_encoding("o200k_base")         # encoding used by gpt-4o family

def count(text: str) -> int:
    return len(ENC.encode(text))                  # exact tokens

@dataclass(frozen=True)
class Chunk:
    text: str                                     # chunk text
    score: float                                  # relevance score from retriever/reranker

def pack_context(chunks: list[Chunk], budget: int) -> list[Chunk]:
    """Keep the highest-scoring chunks that fit inside the token budget."""
    chosen: list[Chunk] = []                      # selected chunks
    used = 0                                      # tokens used so far
    seen: set[str] = set()                        # for duplicate removal
    for ch in sorted(chunks, key=lambda c: c.score, reverse=True):   # best first
        key = ch.text.strip().lower()             # normalised text for dedupe
        if key in seen:                           # skip duplicates
            continue
        n = count(ch.text)                        # chunk size
        if used + n > budget:                     # would exceed budget
            continue
        chosen.append(ch)                         # keep it
        seen.add(key)                             # remember
        used += n                                 # update usage
    return chosen

async def compress_history(llm: LLM, turns: list[str], keep_last: int = 3) -> str:
    """Summarise old turns, keep the last few verbatim."""
    old, recent = turns[:-keep_last], turns[-keep_last:]        # split history
    if not old:                                                  # nothing to summarise
        return "\n".join(recent)
    try:
        summary = await llm("Summarise in max 80 words, keep names/codes:\n" + "\n".join(old))
    except Exception:                                            # on failure keep raw text, trimmed
        summary = "\n".join(old)[-400:]
    return f"Summary: {summary}\n" + "\n".join(recent)           # compact history

async def _demo() -> None:
    chunks = [Chunk("Heading 8518: headphones", 0.9), Chunk("Heading 8518: headphones", 0.8),
              Chunk("Chapter 85 notes " * 50, 0.4), Chunk("Heading 8517: phones", 0.7)]
    print([c.text[:20] for c in pack_context(chunks, budget=60)])
    async def fake(p: str) -> str:
        return "User asked about earbuds and charger codes."
    print(await compress_history(fake, [f"turn {i}" for i in range(8)]))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: use exact counts (`tiktoken`) for budgeting. Compression itself can cost tokens if you call an LLM to summarise, so do it only when the saving is larger than the summary cost.

---

## 🟠 FastAPI Integration
Add a context-packing step before the LLM call and return token stats in the response so you can watch savings.

```python
from fastapi import FastAPI                       # framework
from pydantic import BaseModel                    # models
from openai import AsyncOpenAI                    # openai>=1

app = FastAPI()                                   # app
client = AsyncOpenAI()                            # client

class Ask(BaseModel):
    question: str                                 # user question

async def retrieve(question: str) -> list[Chunk]: # placeholder retriever
    return [Chunk("Heading 8518: headphones", 0.9), Chunk("Heading 8517: phones", 0.6)]

@app.post("/ask")
async def ask(body: Ask) -> dict:
    chunks = pack_context(await retrieve(body.question), budget=1500)   # compress context
    context = "\n".join(c.text for c in chunks)                         # join chunks
    resp = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=200,
        messages=[{"role": "system", "content": "Answer from CONTEXT only."},
                  {"role": "user", "content": f"CONTEXT:\n{context}\n\nQ: {body.question}"}])
    u = resp.usage                                                      # real token usage
    return {"answer": resp.choices[0].message.content,
            "prompt_tokens": u.prompt_tokens if u else None}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain offers `ContextualCompressionRetriever` (with an LLM or embedding filter) to compress retrieved documents, and `trim_messages` in `langchain_core.messages` to fit chat history in a token budget. In LangGraph, put a "trim" step before the model node.

```python
from langchain_core.messages import trim_messages, HumanMessage, AIMessage   # message utils
from langchain_openai import ChatOpenAI                                      # model

llm = ChatOpenAI(model="gpt-4o-mini")                          # also serves as token counter
history = [HumanMessage("hi"), AIMessage("hello"), HumanMessage("code for earbuds?")]
trimmed = trim_messages(
    history, max_tokens=500, strategy="last",                  # keep the latest messages
    token_counter=llm, include_system=True, start_on="human",  # valid start of conversation
)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Compressing without measuring quality
✅ Correct: Compare eval scores before and after.
```python
# Wrong
prompt = prompt[:2000]          # blind truncation may cut the key fact

# Right
if eval_score(compressed) >= eval_score(original) - 0.01:
    use(compressed)
```

❌ Mistake 2: Cutting the end of the context blindly (the question or rules get lost)
✅ Correct: Trim the lowest-value middle items; keep system rules and the question.
```python
# Wrong
text = system + context + question
text = text[:4000]

# Right
context = pack_context(chunks, budget=1500)     # trim only the context
```

❌ Mistake 3: Removing legal or numeric details (codes, dates, amounts) during summarising. Tell the summariser to keep them.

---

## 🧠 Tricky Interview Question
**Q**: "You cut the prompt by 50% and cost dropped, but support tickets about wrong answers rose. What happened?"

**Answer**: Compression removed information that mattered for rare cases. Average eval accuracy hid it because the eval set lacked those cases. Fix: add slices to the eval (rare products, long documents), compress by relevance rather than position, keep critical rules uncompressed, A/B test with a canary, and track quality metrics (not only cost) per compression release.

---

## ⚫ Interview Questions + Answers

Q1: Why compress prompts?
A1: To reduce cost and latency, avoid context limits and reduce distraction.

Q2: Name three compression techniques.
A2: Shorter instructions, top-k and reranking for retrieved chunks, and summarising old chat history (also dedupe, compact formats).

Q3: How do you count tokens accurately?
A3: Use the model's tokenizer, e.g. `tiktoken` for OpenAI models, or the provider's token-count API. Character count is only an estimate.

Q4: What is the risk of summarising chat history?
A4: Loss of details (IDs, numbers, constraints) and summary drift over many rounds. Keep key facts in structured memory and re-summarise from the original when possible.

Q5 (Hard): Design a token-budget manager for a RAG chat with a 8K budget.
A5: Reserve output tokens (e.g. 1K) and the system prompt (fixed). Split the rest by priority: current question (always), last N turns, retrieved chunks by rerank score, then summarised older history. Pack greedily by priority with exact counts, dedupe chunks, and degrade gracefully (fewer chunks first). Log tokens per part and evaluate quality per budget level.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prompts are long and traffic is high
- You approach the context limit
- Latency matters

❌ Avoid when:
- Prompts are short already (little gain)
- Exact wording matters (legal text, code)
- You cannot measure quality impact

---

## 📊 Visual Diagram
```
BEFORE (4,700 tokens)
+-------------+----------------------------+---------+------+
| system 600  | 8 chunks 4,000             | hist 0  | Q 100|
+-------------+----------------------------+---------+------+

AFTER (1,800 tokens)
+---------+------------------+--------+------+
| sys 250 | top-3 chunks 1,500| hist 0 | Q 50 |
+---------+------------------+--------+------+

 techniques: rewrite - rerank - dedupe - summarise - trim
```

---

## 💰 Cost Impact
Input cost = input_tokens x price. With gpt-4o-mini input at $0.15 per 1M tokens (check current pricing), cutting 2,900 tokens per request at 200K requests/day saves about 580M tokens/day, roughly $87/day. With a more expensive model the saving is multiples higher. Latency also drops because the model processes fewer tokens.

Optimisation: measure first, compress the biggest block, prefer rerank over LLM summarising (cheaper), cache static prefixes, and verify quality on every change.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compression | Fewer tokens, same meaning | कम tokens, वही मतलब |
| Token budget | Max tokens allowed for a part | किसी हिस्से के लिए tokens की सीमा |
| Reranking | Re-order chunks by relevance | Relevance से chunks का क्रम बदलना |
| Dedupe | Remove duplicate content | दोहराव हटाना |
| Summarisation | Short version of long text | लंबे text का सार |
| Truncation | Cutting text by length | लंबाई से text काटना |

---

## ⚡ 3-Line Summary
English: Prompt compression cuts input tokens with shorter instructions, fewer but better chunks and summarised history. Measure tokens per part first and re-run evals after every change. Savings in cost and latency are real only if quality holds.
Hindi: Prompt compression छोटे instructions, कम पर बेहतर chunks और summarised history से input tokens घटाता है। पहले हर हिस्से के tokens मापो और हर बदलाव के बाद eval चलाओ। Cost और latency की बचत तभी असली है जब quality बनी रहे।

---

## ➡️ Next Topic
**069. Prompt Caching (Anthropic + OpenAI)** — instead of shrinking the prompt, pay less for the repeated prefix.
