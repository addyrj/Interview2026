---

# 157. Fixed Size Chunking
# हिंदी में: Fixed Size Chunking (बराबर आकार के टुकड़े)

---

## 🔵 Simple Definition (English)
Fixed size chunking cuts text every N characters (or N tokens), usually with an overlap of M so neighbouring chunks share some text. It is the simplest and fastest strategy and ignores sentence or paragraph boundaries.

## 🔵 सरल परिभाषा (Hindi)
Fixed size chunking text को हर N characters (या N tokens) पर काटती है, आमतौर पर M overlap के साथ ताकि पास-पास के chunks कुछ text साझा करें। यह सबसे सरल और तेज़ strategy है और sentence या paragraph की सीमाओं को नहीं देखती।

---

## 🔴 Problem it Solves
Embedding models and LLMs need bounded input. Fixed windows give predictable sizes, predictable cost, trivial code and a strong baseline. Overlap reduces the damage of cutting a sentence at the border.

## 🔴 यह क्यों बना? (Hindi)
Embedding models और LLMs को सीमित input चाहिए। Fixed windows से size, cost और code सब अनुमानित और सरल रहते हैं, और यह मज़बूत baseline देता है। Overlap border पर वाक्य कटने का नुकसान घटाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose chunk_size (for example 500 chars or 256 tokens) and overlap (for example 50)
Step 2 → step = chunk_size - overlap
Step 3 → start = 0; take text[start : start + chunk_size]
Step 4 → start += step; repeat until the end
Step 5 → Last chunk may be shorter (merge it into the previous one if tiny)
Step 6 → Embed every chunk; store with its start offset as metadata
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → chunk_size (जैसे 500 chars या 256 tokens) और overlap (जैसे 50) चुनो
Step 2 → step = chunk_size - overlap
Step 3 → start = 0; text[start : start + chunk_size] लो
Step 4 → start += step; अंत तक दोहराओ
Step 5 → आख़िरी chunk छोटा हो सकता है (बहुत छोटा हो तो पिछले में मिला दो)
Step 6 → हर chunk embed करो; start offset को metadata में रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: scanned tariff PDFs run through OCR produce messy text with no reliable paragraph breaks. Fixed-size token windows (300 tokens, 40 overlap) are a dependable first pass and keep embedding costs predictable. Later, structure-aware strategies replace it for the clean documents.

**Zomato AI**: customer reviews (short, unstructured) can use fixed 300-character windows safely since most reviews fit in one chunk.

## 🟡 Real Example Hindi mein
**Tariff System**: OCR से बने scanned tariff PDFs में भरोसेमंद paragraph breaks नहीं होते। Fixed token windows (300 tokens, 40 overlap) भरोसेमंद पहला कदम हैं और embedding cost अनुमानित रखते हैं। साफ़ documents के लिए बाद में structure-aware strategies लगाई जाती हैं।

**Zomato AI**: customer reviews (छोटे, unstructured) में fixed 300-character windows सुरक्षित हैं क्योंकि ज़्यादातर reviews एक chunk में आ जाते हैं।

---

## 💻 Code Example — Basic
```python
# Runs offline: fixed-size character chunking with overlap
def fixed_chunks(text: str, size: int = 100, overlap: int = 20) -> list[str]:
    """Split text into windows of `size` characters that overlap by `overlap` characters."""
    if size <= 0:
        raise ValueError("size must be positive")  # invalid configuration
    if not 0 <= overlap < size:
        raise ValueError("overlap must satisfy 0 <= overlap < size")  # else infinite loop
    step = size - overlap  # how far the window moves each time
    chunks: list[str] = []  # result list
    for start in range(0, len(text), step):  # slide the window
        piece = text[start:start + size]  # take one window
        if piece.strip():  # ignore whitespace-only windows
            chunks.append(piece)  # keep it
        if start + size >= len(text):  # reached the end
            break  # stop to avoid a tiny trailing duplicate
    return chunks


text = "Headphones and earphones are classified under 8518.30. " * 5  # sample text
for i, c in enumerate(fixed_chunks(text, size=100, overlap=20)):
    print(i, len(c), repr(c[:40]))  # preview each chunk
```

## 💻 Code Example — Advanced
```python
# Production: token-based windows with tiktoken (fallback to words), async, typed, error handling
import asyncio
import logging
from dataclasses import dataclass
from typing import Callable

log = logging.getLogger("fixed_chunker")

try:
    import tiktoken  # pip install tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")  # tokenizer used by many OpenAI models
    encode: Callable[[str], list] = _enc.encode
    decode: Callable[[list], str] = _enc.decode
except Exception:  # library or vocab download unavailable -> degrade gracefully
    log.warning("tiktoken unavailable, falling back to whitespace words")
    encode = lambda s: s.split(" ")  # noqa: E731
    decode = lambda toks: " ".join(toks)  # noqa: E731


@dataclass(frozen=True)
class TokenChunk:
    text: str
    start_token: int  # position in the token stream (useful for citations)
    n_tokens: int


def token_chunks(text: str, max_tokens: int = 300, overlap_tokens: int = 40) -> list[TokenChunk]:
    if max_tokens <= overlap_tokens:
        raise ValueError("max_tokens must be greater than overlap_tokens")
    toks = encode(text)  # tokenise once
    step = max_tokens - overlap_tokens
    out: list[TokenChunk] = []
    for start in range(0, len(toks), step):
        window = toks[start:start + max_tokens]
        out.append(TokenChunk(decode(window), start, len(window)))
        if start + max_tokens >= len(toks):
            break
    return out


async def atoken_chunks(text: str, **kw) -> list[TokenChunk]:
    return await asyncio.to_thread(token_chunks, text, **kw)  # CPU-bound work off the event loop


if __name__ == "__main__":
    res = asyncio.run(atoken_chunks("Tariff headings explain goods. " * 300, max_tokens=120, overlap_tokens=20))
    print(len(res), res[0].n_tokens)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class ChunkRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2_000_000)  # protect the server
    max_tokens: int = Field(300, ge=50, le=2000)
    overlap_tokens: int = Field(40, ge=0, le=500)


@app.post("/chunk/fixed")
async def chunk_fixed(req: ChunkRequest) -> dict:
    chunks = await atoken_chunks(req.text, max_tokens=req.max_tokens, overlap_tokens=req.overlap_tokens)
    return {"count": len(chunks), "chunks": [c.__dict__ for c in chunks[:50]]}  # cap the response size
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-text-splitters tiktoken
from langchain_text_splitters import CharacterTextSplitter

# separator="" makes it a pure fixed-size splitter; from_tiktoken_encoder measures size in tokens
splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base", chunk_size=300, chunk_overlap=40, separator="",
)
docs = splitter.create_documents(["Headphones are classified under 8518.30. " * 200])
# Feed `docs` to vector_store.add_documents(docs); use inside a LangGraph "ingest" step if needed.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Overlap greater than or equal to size
```python
# Wrong: step = 0 or negative -> infinite loop / error
fixed_chunks(text, size=100, overlap=100)
# Right
fixed_chunks(text, size=100, overlap=20)
```

❌ Mistake 2: Mixing characters and tokens
```python
# Wrong: "chunk_size=1000" thinking tokens, but the splitter counts characters (about 250 tokens)
# Right: be explicit; use a token-based splitter when you care about model limits
splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=300, chunk_overlap=40, separator="")
```

---

## 🧠 Tricky Interview Question

**Q**: "You use fixed 500-character chunks with 50 overlap. A user asks about an exception clause and retrieval keeps returning the main rule only. Why, and how do you fix it without changing models?"

**Answer**: The window boundary separated the rule from its exception, and the overlap (50 chars, under 10 words) was too small to carry the full clause. Solutions: increase overlap (15-20 percent), switch to boundary-aware splitting (sentence, paragraph or heading), add neighbouring-chunk expansion at retrieval time (return chunk i-1, i, i+1), or index small chunks but pass their parent section to the LLM. Evaluate each change on exception-type questions.

---

## ⚫ Interview Questions + Answers

Q1: What is fixed-size chunking?
A1: Cutting text into equal-length pieces by characters or tokens, optionally with overlap.

Q2: Why add overlap?
A2: So content near a boundary appears fully in at least one chunk; it reduces lost context.

Q3: Characters vs tokens for size?
A3: Tokens match model limits and cost exactly; characters are simpler. English averages about 4 characters per token, but Hindi or code differ a lot.

Q4: Main weakness?
A4: It ignores meaning: sentences, tables and lists are cut randomly, which hurts retrieval quality.

Q5: When would you still choose fixed-size in production?
A5: For noisy text without structure (OCR, transcripts), as a baseline or fallback, when predictable cost matters most, or for very large corpora where speed is key. Combine with metadata and neighbour expansion to offset the weaknesses.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Unstructured or messy text, baselines, very large volumes

❌ Avoid when:
- Documents have clear structure (headings, paragraphs, code) that you can exploit
- Exact clauses and tables matter

---

## 📊 Visual Diagram
```
 text: ABCDEFGHIJKLMNOPQRSTUVWXYZ...   size=10  overlap=3  step=7

 chunk0: [ABCDEFGHIJ]
 chunk1:        [HIJKLMNOPQ]          <- HIJ repeated (overlap)
 chunk2:               [OPQRSTUVWX]
 chunk3:                      [VWXYZ...]
```

---

## 💰 Cost Impact
- Embedding tokens = chunk tokens x number of chunks. Overlap of 20 percent adds about 25 percent more tokens to embed. For 100K tokens of source text: no overlap embeds 100K; with 20 percent overlap it embeds about 125K.
- Prompt tokens = k x chunk size. With 300-token chunks and k=4 that is about 1,200 tokens; with 1,000-token chunks it is 4,000. Smaller fixed chunks lower LLM cost but risk losing context.
- Optimise: smallest size that keeps recall, overlap of 10-15 percent, drop empty/duplicate chunks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Window | Slice of text | Text का हिस्सा |
| Step / stride | Window movement distance | Window के बढ़ने की दूरी |
| Overlap | Repeated boundary text | दोहराया गया border text |
| Token-based | Sizes measured in tokens | Tokens में माप |
| Baseline | Simple starting method | सरल शुरुआती तरीका |

---

## ⚡ 3-Line Summary
English: Fixed size chunking slices text into equal windows with overlap. It is simple, fast and predictable, but ignores meaning. Use it for messy text or as a baseline, preferably sized in tokens.
Hindi: Fixed size chunking text को overlap के साथ बराबर windows में काटती है। यह सरल, तेज़ और अनुमानित है, पर अर्थ को नहीं देखती। गंदे text या baseline के लिए use करो, बेहतर है tokens में size रखो।

---

## ➡️ Next Topic
**158. Recursive Character Splitting** — split by the biggest natural separator first, so chunks respect paragraphs and sentences.
