---

# 022. Tokens — Complete Guide
# हिंदी में: Tokens — पूरी Guide

---

## 🔵 Simple Definition (English)
A token is the basic unit that LLMs process — not a word, not a character, but a subword piece (usually 2–6 characters). "tokenization" splits to ["token", "ization"]. LLMs have a **context window** measured in tokens (how much they can read at once). API cost is charged per token. Understanding tokens is critical for cost optimization and avoiding context limit errors.

## 🔵 सरल परिभाषा (Hindi)
Token LLM की basic processing unit है — word नहीं, character नहीं, बल्कि subword piece (usually 2-6 characters)। "tokenization" → ["token", "ization"]। LLM का context window tokens में measure होता है। API cost per token charge होती है। Tokens समझना = cost optimize करना।

---

## 🔴 Problem it Solves
If LLMs processed character by character: "elephant" = 8 steps, too many. Word by word: "tokenization" is one word but may never appear in training. Tokens are the sweet spot — common patterns get single tokens ("the" = 1 token), rare/long words get split into subtokens. Vocabulary is fixed and finite (50k–100k tokens).

## 🔴 यह क्यों बना? (Hindi)
Character by character: बहुत ज़्यादा steps। Word by word: rare words handle करना मुश्किल। Tokens: common patterns = 1 token, rare words = multiple subtokens। Fixed, finite vocabulary।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Text → Tokenizer (Byte Pair Encoding / BPE algorithm)
Step 2 → Tokenizer splits text into subwords based on frequency in training data
Step 3 → Each subword maps to a unique integer ID (vocabulary index)
Step 4 → [token_ids] fed into LLM as input
Step 5 → LLM outputs probabilities over the full vocabulary for next token
Step 6 → Chosen token_id → decoded back to text
Step 7 → Cost = (input_tokens + output_tokens) × price_per_token
```

---

## 🟡 Real World Example
**Tariff Classification System**: A user uploads a 50-page PDF tariff document. Before processing: count tokens with `tiktoken` — if it's 80,000 tokens, it won't fit in a 32K context window. Solution: chunk the document, embed each chunk, retrieve only relevant chunks (RAG). Token counting prevents silent context truncation that would give wrong answers.

## 🟡 Real Example Hindi mein
**Tariff System**: User 50-page PDF upload करता है। Process करने से पहले: `tiktoken` से tokens count करो। 80,000 tokens है तो 32K context window में fit नहीं होगा। Solution: document chunk करो → RAG।

---

## 💻 Code Example — Basic
```python
# tiktoken — OpenAI's tokenizer library
# pip install tiktoken
import tiktoken

# Get the tokenizer for a specific model:
enc = tiktoken.encoding_for_model("gpt-4o-mini")   # same tokenizer as gpt-4o

text = "Tariff classification for electronics"

# Count tokens:
tokens = enc.encode(text)
print(f"Text: {text!r}")
print(f"Token count: {len(tokens)}")     # 5
print(f"Token IDs: {tokens}")            # [51, 10695, 23110, 369, 41640]
print(f"Tokens:    {[enc.decode([t]) for t in tokens]}")
# ['T', 'ariff', ' classification', ' for', ' electronics']

# Rule of thumb: 1 token ≈ 4 characters ≈ 0.75 words
print(f"\nCharacter count: {len(text)}")              # 38 chars / 5 tokens = 7.6 chars/token
print(f"Word count: {len(text.split())}")             # 4 words / 5 tokens = 0.8 tokens/word

# Different languages tokenize differently!
hindi_text = "टैरिफ वर्गीकरण"
hindi_tokens = enc.encode(hindi_text)
print(f"\nHindi token count: {len(hindi_tokens)}")    # much more than English!
# Hindi, Chinese etc. are often 2-4x more tokens than English
```

## 💻 Code Example — Advanced
```python
# Production: token counting for cost estimation + context management
import tiktoken
from typing import Any

class TokenCounter:
    """Tracks token usage and estimates cost for gpt-4o-mini."""

    # Prices per 1M tokens (as of 2024):
    PRICES = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o":      {"input": 5.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    }

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.encoding = tiktoken.encoding_for_model(
            "gpt-4o"   # tiktoken uses same encoding for gpt-4o and gpt-4o-mini
        )
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def count(self, text: str) -> int:
        """Count tokens in a string."""
        return len(self.encoding.encode(text))

    def count_messages(self, messages: list[dict[str, str]]) -> int:
        """Count tokens in a messages list (matches OpenAI's actual counting)."""
        total = 0
        for message in messages:
            total += 4   # each message has ~4 overhead tokens
            for key, value in message.items():
                total += self.count(value)
        total += 2   # reply priming
        return total

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD."""
        prices = self.PRICES.get(self.model, self.PRICES["gpt-4o-mini"])
        return (
            input_tokens  * prices["input"]  / 1_000_000 +
            output_tokens * prices["output"] / 1_000_000
        )

    def will_fit(self, messages: list[dict], max_context: int = 128_000) -> bool:
        """Check if messages fit in context window (with buffer for response)."""
        used = self.count_messages(messages)
        return used < (max_context - 2000)   # 2000 buffer for response

    def truncate_to_fit(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)

# Usage:
counter = TokenCounter("gpt-4o-mini")

messages = [
    {"role": "system", "content": "You are a tariff classification assistant."},
    {"role": "user",   "content": "What HS code for iPhone 15?"},
]

token_count = counter.count_messages(messages)
print(f"Message tokens: {token_count}")     # ~25 tokens

doc = "This is a very long tariff document..." * 1000
if not counter.will_fit([{"role": "user", "content": doc}]):
    # Truncate or use RAG
    doc = counter.truncate_to_fit(doc, max_tokens=10_000)

cost = counter.estimate_cost(input_tokens=500, output_tokens=200)
print(f"Estimated cost: ${cost:.6f}")   # ~$0.000195
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel
import tiktoken
from openai import AsyncOpenAI

app = FastAPI()
client = AsyncOpenAI()
enc = tiktoken.encoding_for_model("gpt-4o")   # module-level (shared)

class TokenCheckRequest(BaseModel):
    text: str
    model: str = "gpt-4o-mini"

class QueryRequest(BaseModel):
    query: str

@app.post("/token-count")
async def count_tokens(request: TokenCheckRequest):
    """Returns token count for a given text + cost estimate."""
    count = len(enc.encode(request.text))
    prices = {"gpt-4o-mini": 0.15, "gpt-4o": 5.00}
    cost = count * prices.get(request.model, 0.15) / 1_000_000
    return {
        "token_count": count,
        "estimated_cost_usd": round(cost, 8),
        "fits_in_128k": count < 128_000,
        "fits_in_32k": count < 32_000,
    }

@app.post("/ask-tariff")
async def ask_tariff(request: QueryRequest):
    """Ask tariff question with token tracking in response."""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer tariff questions concisely."},
            {"role": "user",   "content": request.query},
        ],
        max_tokens=300,
    )
    return {
        "answer": response.choices[0].message.content,
        "tokens": {
            "input":  response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
            "total":  response.usage.total_tokens,
        },
        "cost_usd": round(
            response.usage.prompt_tokens    * 0.15 / 1_000_000 +
            response.usage.completion_tokens * 0.60 / 1_000_000,
            8
        ),
    }
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain tracks tokens automatically through callbacks:
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback

llm = ChatOpenAI(model="gpt-4o-mini")

# get_openai_callback captures token usage:
with get_openai_callback() as cb:
    response = await llm.ainvoke("What HS code for smartphones?")
    print(f"Tokens: {cb.total_tokens}")
    print(f"Cost: ${cb.total_cost:.6f}")

# LangGraph: tokens accumulate across all LLM nodes in a workflow:
# Total cost of a LangGraph workflow = sum of tokens in all LLM node calls
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not counting tokens before sending large documents
```python
# Wrong — silent truncation at context limit:
with open("tariff_document.pdf") as f:
    text = f.read()   # might be 500K characters!
response = llm.invoke(text)   # GPT silently truncates to context limit — wrong answer!

# Correct — count first, chunk if needed:
token_count = len(enc.encode(text))
if token_count > 100_000:  # leave buffer
    print(f"Too large ({token_count} tokens) — use RAG")
    chunks = chunk_document(text)
    # embed chunks, retrieve relevant ones
```

❌ Mistake 2: Estimating cost with character count instead of tokens
```python
# Wrong — inaccurate cost estimate:
char_count = len(text)
estimated_tokens = char_count / 4   # rough but unreliable for code, Hindi etc.

# Correct — use tiktoken for accurate count:
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")
actual_tokens = len(enc.encode(text))
```

---

## 🧠 Tricky Interview Question

**Q**: "Your RAG system works perfectly in testing (English docs) but costs 4x more than expected when deployed with Hindi documents. Why?"

**Answer**: Hindi (and most non-Latin scripts) tokenize much less efficiently than English. English averages ~1 token per 4 characters; Hindi, Chinese, Japanese average ~1 token per 1-2 characters. A Hindi document that's the same "size" as an English document may use 3-4x more tokens. Solutions: (1) translate documents to English before embedding (adds latency/cost), (2) use a multilingual embedding model that's token-efficient, (3) adjust chunk sizes for Hindi documents (smaller chunks in character count = similar token count to English chunks).

---

## ⚫ Interview Questions + Answers

Q1: What is BPE (Byte Pair Encoding)?
A1: BPE is the tokenization algorithm used by GPT models. It starts with individual bytes, then iteratively merges the most frequent adjacent pairs. Common subwords ("the", "ing", "tion") get single tokens; rare sequences get split into subtokens. Result: ~50k token vocabulary that covers all text efficiently. LLaMA uses SentencePiece (similar concept).

Q2: What is `tiktoken` and when should you use it?
A2: `tiktoken` is OpenAI's open-source tokenizer — gives the exact same token counts as the API. Use it: (1) before API calls to check if content fits in context window, (2) for cost estimation, (3) to split text at clean token boundaries, (4) in preprocessing pipelines. `tiktoken.encoding_for_model("gpt-4o")` returns the right encoder.

Q3: Why does the same text have different token counts in different models?
A3: Different models use different tokenizers with different vocabularies. GPT-4 uses `cl100k_base` (~100k vocabulary). GPT-3.5 uses `p50k_base` (~50k). LLaMA uses SentencePiece. Claude uses its own tokenizer. A sentence that's 15 tokens in GPT-4 might be 17 tokens in LLaMA. Always use the model's own tokenizer for accurate counts.

Q4: What is the context window and why does it matter for RAG?
A4: Context window = maximum tokens an LLM can process at once (input + output combined). GPT-4o: 128K tokens. Claude 3.5 Sonnet: 200K tokens. For RAG: your retrieved chunks + question + system prompt must fit within the context window. "Lost in the middle" problem: LLMs perform worse on information in the middle of a long context. RAG solves this by retrieving only the most relevant chunks.

Q5: How do you optimize costs for a high-volume tariff query system?
A5: (1) Use gpt-4o-mini (33x cheaper than gpt-4o) for simple queries — route complex ones to gpt-4o. (2) Implement semantic caching: if "iPhone 15 HS code" was asked before, return cached answer. (3) Compress prompts — remove verbose instructions, use abbreviations in system prompt. (4) Limit output tokens with `max_tokens`. (5) Batch similar requests with OpenAI Batch API (50% cheaper). (6) Use Anthropic's prompt caching for repeated system prompts (90% cheaper on cache hits).

---

## 🔷 When to Use + When Not to Use

✅ Token counting is essential when:
- Processing user-uploaded documents (unknown size)
- Building RAG systems (need to fit chunks in context)
- Cost budgeting and monitoring
- Ensuring prompts stay within context limits

❌ Don't overthink tokens when:
- Simple API calls with short prompts (< 1K tokens) — cost negligible
- Prototyping / development (optimize in production)

---

## 📊 Visual Diagram
```
Text:     "Tariff classification for electronics"
           │
           ▼ BPE Tokenizer
Tokens:   ["T","ariff"," classification"," for"," electronics"]
IDs:      [  51,10695,        23110,      369,       41640    ]
Count:     5 tokens

Cost calculation:
┌─────────────────────────────────────────────┐
│ Input:  500 tokens × $0.15/1M = $0.000075  │
│ Output: 200 tokens × $0.60/1M = $0.000120  │
│ Total:                          $0.000195  │
│                                             │
│ 100K queries/day = $19.50/day              │
│ 3M queries/month = $585/month              │
└─────────────────────────────────────────────┘
```

---

## 💰 Cost Impact
| Model | Input/1M | Output/1M | 1K queries (500in+200out) |
|-------|----------|-----------|--------------------------|
| gpt-4o-mini | $0.15 | $0.60 | $0.195 |
| gpt-4o | $5.00 | $15.00 | $8.00 |
| claude-3-haiku | $0.25 | $1.25 | $0.50 |
| claude-3-5-sonnet | $3.00 | $15.00 | $4.50 |

Key optimization: **gpt-4o-mini** handles ~95% of tasks at 40x less cost than gpt-4o.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token | Subword unit of text (~4 chars) | Text की subword unit |
| Tokenizer | Converts text to token IDs | Text → token IDs converter |
| BPE | Byte Pair Encoding tokenization | Token बनाने का algorithm |
| Context window | Max tokens LLM reads at once | LLM एक बार में कितना पढ़े |
| tiktoken | OpenAI's tokenizer library | Token counting library |
| Prompt tokens | Input tokens | Input tokens |
| Completion tokens | Output tokens | Output tokens |

---

## ⚡ 3-Line Summary
English: Tokens are subword units (~4 chars each) — the currency of LLM APIs. Count with `tiktoken` before sending large documents to avoid silent truncation and unexpected costs. Hindi/non-Latin text uses 3-4x more tokens than English — critical for cost estimation in multilingual apps.
Hindi: Tokens LLM API की currency हैं (~4 chars each)। Large documents भेजने से पहले `tiktoken` से count करो। Hindi text 3-4x ज़्यादा tokens use करती है — multilingual apps में cost estimate जरूरी।

---

## ➡️ Next Topic
**023. Context Window** — what it means in practice, 128K vs 200K windows, "lost in the middle" problem, how RAG solves it.
