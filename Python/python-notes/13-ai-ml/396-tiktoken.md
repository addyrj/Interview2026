---

# 396. tiktoken
# हिंदी में: tiktoken (OpenAI Tokenizer)

---

## 🔵 Simple Definition (English)
`tiktoken` is OpenAI's fast tokenizer library. It turns text into a list of integer token ids (and back). LLMs read, limit and bill by tokens, not by characters or words, so `tiktoken` tells you exactly how many tokens your text uses.

## 🔵 सरल परिभाषा (Hindi)
`tiktoken` OpenAI की तेज tokenizer library है। यह text को integer token ids की list में बदलती है (और वापस text में भी)। LLMs tokens के हिसाब से पढ़ते, limit लगाते और bill करते हैं, characters या words के हिसाब से नहीं, इसलिए `tiktoken` बताती है कि आपका text कितने tokens लेगा।

---

## 🔴 Problem it Solves
Every model has a context window (for example 128k tokens) and every API call is priced per token. Guessing with `len(text) / 4` is inaccurate, especially for code, emojis and Hindi. Without exact counts you hit "maximum context length exceeded" errors, cut documents in the wrong place and get surprise bills.

## 🔴 यह क्यों बना? (Hindi)
हर model की एक context window होती है (जैसे 128k tokens) और हर API call tokens के हिसाब से महंगी होती है। `len(text) / 4` से अंदाजा लगाना गलत होता है, खासकर code, emojis और हिंदी में। सही गिनती के बिना "maximum context length exceeded" error आता है, documents गलत जगह कटते हैं और bill चौंकाने वाला आता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose an encoding: tiktoken.get_encoding("cl100k_base") or encoding_for_model("gpt-4o")
Step 2 → enc.encode(text) splits text into sub-word pieces using Byte-Pair Encoding (BPE)
Step 3 → Each piece is looked up in the vocabulary and becomes an int id
Step 4 → len(ids) = token count. This is what the API counts and bills
Step 5 → enc.decode(ids) gives the text back exactly (lossless round trip)
Step 6 → Use the count to truncate, chunk, or estimate cost before calling the API
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Encoding चुनो: tiktoken.get_encoding("cl100k_base") या encoding_for_model("gpt-4o")
Step 2 → enc.encode(text) Byte-Pair Encoding (BPE) से text को sub-word टुकड़ों में बांटता है
Step 3 → हर टुकड़ा vocabulary में खोजा जाता है और एक int id बन जाता है
Step 4 → len(ids) = token count। API इसी को गिनती और bill करती है
Step 5 → enc.decode(ids) वही text वापस देता है (lossless round trip)
Step 6 → API call से पहले count से truncate, chunk या cost का अंदाजा लगाओ
```

---

## 🟡 Real World Example
A document-chat app (PDF Q&A) splits a 200-page PDF into chunks of 500 tokens with 50 tokens overlap before creating embeddings. It also counts the tokens of the system prompt + history + retrieved chunks and trims old chat history so the request never exceeds the model's context window. A billing dashboard multiplies counted tokens by the price per million to show each customer's cost.

## 🟡 Real Example Hindi mein
Document-chat app (PDF Q&A) 200 पन्नों के PDF को embeddings बनाने से पहले 500 tokens के chunks में, 50 tokens overlap के साथ, बांटता है। यह system prompt + history + मिले chunks के tokens भी गिनता है और पुरानी chat history काटता है ताकि request model की context window से बाहर न जाए। Billing dashboard गिने हुए tokens को प्रति million की कीमत से गुणा करके हर customer का cost दिखाता है।

---

## 💻 Code Example — Basic
```python
# Basic tiktoken examples   (pip install tiktoken; tested with 0.14.0)
# Note: the first call downloads the vocabulary file from the internet, then caches it.
import tiktoken                                    # OpenAI's tokenizer library

enc = tiktoken.get_encoding("cl100k_base")         # encoding used by GPT-4 / GPT-3.5 era models
tokens: list[int] = enc.encode("hello world")      # text -> token ids
print(tokens)                                      # list of ints
print(len(tokens))                                 # token count (this is what you pay for)
print(enc.decode(tokens))                          # token ids -> text (round trip)
print([enc.decode([t]) for t in tokens])           # see the text piece for each token

print(len(enc.encode("नमस्ते दुनिया")))             # Hindi text: roughly 1 token per character
print(len("नमस्ते दुनिया"))                         # number of characters, for comparison
print(len(enc.encode("a" * 100)))                  # repeated chars compress well

m = tiktoken.encoding_for_model("gpt-4o")          # pick encoding by model name
print(m.name)                                      # o200k_base for gpt-4o
print(len(m.encode("hello world")))                # different vocab, maybe different count

# Output (really executed):
# [15339, 1917]
# 2
# hello world
# ['hello', ' world']
# 13
# 13
# 13
# o200k_base
# 2
```
Note: Hindi in `cl100k_base` came out at about 1 token per character, while English is about 4 characters per token. So the same sentence in Hindi costs several times more tokens. Exact numbers depend on the encoding.

## 💻 Code Example — Advanced
```python
# Production style: token budget, chat message counting, safe truncation, chunking
import tiktoken                                    # tokenizer

ENC = tiktoken.get_encoding("cl100k_base")         # load once (it is cached after first use)


def count_tokens(text: str) -> int:
    """Number of tokens in text."""
    return len(ENC.encode(text))                   # encode and count


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Cut text so it fits max_tokens, never splitting mid-token."""
    if max_tokens < 0:                             # guard bad input
        raise ValueError("max_tokens must be >= 0")
    ids: list[int] = ENC.encode(text)              # tokenize
    return ENC.decode(ids[:max_tokens])            # keep first N tokens


def chunk_by_tokens(text: str, size: int, overlap: int = 0) -> list[str]:
    """Split text into chunks of `size` tokens with optional overlap (RAG chunking)."""
    if overlap >= size:                            # would loop forever
        raise ValueError("overlap must be smaller than size")
    ids: list[int] = ENC.encode(text)              # tokenize once
    step: int = size - overlap                     # how far to move each time
    return [ENC.decode(ids[i:i + size]) for i in range(0, len(ids), step)]


def count_chat_tokens(messages: list[dict[str, str]]) -> int:
    """Rough chat prompt size: ~3 tokens overhead per message + 3 for reply priming.
    This is an approximation; exact overhead differs by model."""
    total: int = 3                                 # reply priming
    for m in messages:                             # each message
        total += 3                                 # role/format overhead (approx)
        total += count_tokens(m["role"]) + count_tokens(m["content"])
    return total


def estimate_cost(tokens: int, usd_per_million: float) -> float:
    """Cost in USD for a token count at a given price per 1M tokens."""
    return tokens / 1_000_000 * usd_per_million


text: str = "Tokens are the unit LLMs read and bill by. " * 5
print(count_tokens(text))
print(repr(truncate_to_tokens(text, 8)))
chunks = chunk_by_tokens(text, 20, overlap=5)
print(len(chunks), [count_tokens(c) for c in chunks])
msgs = [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "Hi!"}]
print(count_chat_tokens(msgs))
print(f"${estimate_cost(1500, 2.5):.6f}")
try:
    chunk_by_tokens("x", 5, overlap=5)
except ValueError as e:
    print("Error:", e)
print(ENC.decode(ENC.encode("emoji 😀")) == "emoji 😀")  # round trip works for unicode
print(len(ENC.encode("😀")))                               # one emoji can be several tokens

# Output (really executed):
# 61
# 'Tokens are the unit LLMs read'
# 5 [20, 20, 20, 16, 1]
# 17
# $0.003750
# Error: overlap must be smaller than size
# True
# 2
```
Note: the price (`2.5` USD per million) is only an example, use your provider's current price. The last chunk `[... , 1]` has only 1 token because of the overlap: in production drop tiny tail chunks.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Library | `tiktoken` (OpenAI, Rust core) | `js-tiktoken` or `gpt-tokenizer` (npm) |
| Get encoding | `get_encoding("cl100k_base")` | `getEncoding("cl100k_base")` |
| Encode | `enc.encode(text)` | `enc.encode(text)` |
| Free memory | automatic | `enc.free()` is needed for the WASM `tiktoken` package |
| Speed | very fast (Rust) | fast, but pure-JS variants are slower |

```python
# Python way
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
print(len(enc.encode("hello world")))              # 2
```
```javascript
// JavaScript way (npm i js-tiktoken)
import { getEncoding } from "js-tiktoken";
const enc = getEncoding("cl100k_base");
console.log(enc.encode("hello world").length);     // 2
```

Key difference: the token ids are the same in both languages (same vocabulary), so you can count tokens in a React/Node frontend and in your Python backend and get matching results.

---

## 🟠 FastAPI Connection
Use `tiktoken` in a FastAPI AI service to reject over-long prompts early (HTTP 413 or 422) before paying for an LLM call, and to return usage data. Load the encoding once at module level: creating it per request is slow.

```python
# FastAPI example — prompt budget guard (run with TestClient)
import tiktoken
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

app: FastAPI = FastAPI()
ENC = tiktoken.get_encoding("cl100k_base")         # loaded once at import time
MAX_PROMPT_TOKENS: int = 20                        # tiny limit so the demo is short


class Prompt(BaseModel):
    text: str


@app.post("/count")
def count(p: Prompt) -> dict[str, int]:
    n: int = len(ENC.encode(p.text))               # exact token count
    if n > MAX_PROMPT_TOKENS:                      # reject before calling the LLM
        raise HTTPException(status_code=413, detail=f"prompt has {n} tokens, max {MAX_PROMPT_TOKENS}")
    return {"tokens": n}


c = TestClient(app)
print(c.post("/count", json={"text": "hello world"}).json())
print(c.post("/count", json={"text": "word " * 50}).status_code)
```
Output (really executed): `{'tokens': 2}` then `413`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Estimating tokens with `len(text.split())` or `len(text) / 4`
✅ Correct: use the real tokenizer of the model you call

```python
# Wrong: "tokenization" is 1 word, 12 characters
len("tokenization".split())                         # 1
# Right: really 2 tokens in cl100k_base
len(enc.encode("tokenization"))                    # 2
```

❌ Mistake 2: Using the wrong encoding for the model
✅ Correct: `tiktoken.encoding_for_model("gpt-4o")` (o200k_base) instead of hard-coding `cl100k_base`

```python
# Wrong: counts for an old model, drifts for newer ones
enc = tiktoken.get_encoding("cl100k_base")
# Right
enc = tiktoken.encoding_for_model("gpt-4o")
```
Also: tiktoken only matches OpenAI models. Claude, Gemini and Llama use different tokenizers, so treat tiktoken counts for them as an estimate only.

❌ Mistake 3: Encoding text that contains special tokens like `<|endoftext|>` without handling them
✅ Correct: pass `allowed_special` or `disallowed_special=()` on purpose (user text could otherwise inject special tokens)

```python
# Wrong: raises ValueError (special token found in text)
enc.encode("<|endoftext|>")
# Right: treat it as plain text
enc.encode("<|endoftext|>", disallowed_special=())     # [27, 91, 8862, 728, 428, 91, 29]
# or treat it as the real special token
enc.encode("<|endoftext|>", allowed_special={"<|endoftext|>"})   # [100257]
```

---

## 🧠 Tricky Interview Question

```python
import tiktoken
e = tiktoken.get_encoding("cl100k_base")
print(e.encode("hello"), e.encode(" hello"), e.encode("Hello"))
print(e.encode("hello") == e.encode(" hello"))
print(len("tokenization"), len(e.encode("tokenization")))
```
Answer (really executed):
```
[15339] [24748] [9906]
False
12 2
```
Tokens are case sensitive and whitespace sensitive: `"hello"`, `" hello"` (with a leading space) and `"Hello"` are three different tokens with three different ids. That is why prompts with odd spacing can cost more, and why you must never compare token ids across different encodings. A 12-character word can be just 2 tokens.

---

## ⚫ Interview Questions + Answers

Q1: What is a token?
A1: A sub-word unit from the model's vocabulary. Common words are 1 token, rare words split into several pieces. In English, about 4 characters or 0.75 words per token on average.

Q2: What is BPE (Byte-Pair Encoding)?
A2: A method that starts from bytes and repeatedly merges the most frequent pairs into new vocabulary entries. This keeps the vocabulary small yet lets the model represent any text, including emoji and rare words.

Q3: Why do Hindi or other non-English texts cost more?
A3: The vocabulary was built mostly from English-heavy data, so Devanagari text splits into many small pieces (about 1 token per character in our test). Newer encodings like `o200k_base` improve this, but the gap remains.

Q4: How do you stay within a context window?
A4: Count tokens of system prompt + history + retrieved context + expected output (`max_tokens`). Trim the oldest history or the lowest-ranked chunks until the total fits.

Q5: Does `tiktoken` work offline?
A5: Only after the vocabulary file is cached. The first `get_encoding` downloads it. For air-gapped servers, set the `TIKTOKEN_CACHE_DIR` environment variable to a pre-populated folder.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Counting or limiting tokens for OpenAI models
- Chunking documents for embeddings and RAG
- Estimating cost before running large batch jobs

❌ Avoid when:
- You call Claude, Gemini or Llama: use their own token-counting APIs or tokenizers for exact numbers
- You only need a rough size and speed does not matter (still better than guessing, but not essential)
- You need word-level analysis (use a normal NLP tokenizer such as spaCy)

---

## 📊 Visual Diagram
```
 "hello world"
      │ enc.encode()
      ▼
 ["hello", " world"]      <- sub-word pieces (BPE)
      │
      ▼
 [15339, 1917]            <- token ids   len() = 2 tokens = what you pay for
      │ enc.decode()
      ▼
 "hello world"            <- lossless round trip

 Budget:  system(17) + history(300) + context(1500) + answer(500)  <= window (128000)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token | Sub-word unit the model reads | Model जो sub-word इकाई पढ़ता है |
| BPE | Merge frequent byte pairs into tokens | बार-बार आने वाले pairs को जोड़ना |
| Encoding | A named vocabulary (cl100k_base, o200k_base) | नाम वाली vocabulary |
| Context window | Max tokens the model can see | Model एक बार में कितने tokens देख सकता है |
| Overlap | Tokens repeated between neighbouring chunks | पास के chunks में दोहराए tokens |
| Special token | Reserved token like end-of-text | आरक्षित token |

---

## ⚡ 3-Line Summary
English: `tiktoken` converts text to token ids and back, so you can count tokens exactly for OpenAI models. Use it to enforce context limits, chunk documents for RAG and estimate cost. Pick the encoding that matches your model and handle special tokens on purpose.
Hindi: `tiktoken` text को token ids में और वापस बदलती है, जिससे OpenAI models के लिए tokens की सही गिनती होती है। इसे context limits लागू करने, RAG के लिए documents chunk करने और cost का अंदाजा लगाने में इस्तेमाल करें। अपने model के अनुसार encoding चुनें और special tokens को सोच-समझकर संभालें।

---

## ➡️ Next Topic
**397. PyTorch Basics** — tensors, autograd and a training loop: the framework behind most modern deep learning research.
