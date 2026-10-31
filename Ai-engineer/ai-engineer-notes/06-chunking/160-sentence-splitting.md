---

# 160. Sentence Splitting
# हिंदी में: Sentence Splitting (वाक्यों में बाँटना)

---

## 🔵 Simple Definition (English)
Sentence splitting breaks text at sentence boundaries, then groups a few sentences per chunk (for example 3-5, with 1 sentence overlap). Chunks always start and end at complete sentences, so ideas are not cut in half.

## 🔵 सरल परिभाषा (Hindi)
Sentence splitting text को वाक्यों की सीमा पर तोड़ती है, फिर हर chunk में कुछ वाक्य (जैसे 3-5, 1 वाक्य overlap के साथ) रखती है। Chunks हमेशा पूरे वाक्य से शुरू और ख़त्म होते हैं, इसलिए विचार बीच में नहीं कटते।

---

## 🔴 Problem it Solves
Fixed windows cut inside sentences ("...classified under 85"), which damages both embedding quality and LLM reading. Sentence-level chunks give clean units, great for FAQs, support answers and precise citations. Naive `split(".")` however breaks on "Dr.", "8518.30", "e.g." and Hindi "।".

## 🔴 यह क्यों बना? (Hindi)
Fixed windows वाक्य के अंदर काटती हैं ("...classified under 85"), जिससे embedding quality और LLM का पढ़ना दोनों बिगड़ते हैं। Sentence-level chunks साफ़ इकाइयाँ देते हैं, जो FAQs, support answers और सटीक citations के लिए बढ़िया हैं। पर सीधा `split(".")` "Dr.", "8518.30", "e.g." और हिंदी "।" पर टूट जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise text (fix line-wrapped hyphenation, collapse whitespace)
Step 2 → Detect sentence ends: punctuation (. ! ? ।) followed by space + capital/digit/quote
Step 3 → Protect exceptions: abbreviations (Dr., No.), decimals/codes (8518.30), URLs
Step 4 → Group N sentences per chunk (also respect max characters)
Step 5 → Overlap: repeat the last 1 sentence in the next chunk
Step 6 → Embed chunks, keep sentence indexes as metadata
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Text normalise करो (line-wrap वाले hyphen ठीक करो, whitespace समेटो)
Step 2 → वाक्य का अंत पहचानो: punctuation (. ! ? ।) के बाद space + capital/digit/quote
Step 3 → अपवाद बचाओ: abbreviations (Dr., No.), decimals/codes (8518.30), URLs
Step 4 → हर chunk में N वाक्य रखो (max characters का भी ध्यान)
Step 5 → Overlap: आख़िरी 1 वाक्य अगले chunk में दोहराओ
Step 6 → Chunks embed करो, sentence indexes metadata में रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: the "Explanatory Notes" are written as short, self-contained statements: "Item X is excluded. Item Y is included." Grouping 4 sentences per chunk with 1-sentence overlap keeps each rule intact. The splitter must not break "8518.30" or "No. 5" into separate sentences.

**Zomato AI**: a support FAQ answer of 3 sentences becomes one chunk; the answer is returned whole, with the source sentence ids for citation.

## 🟡 Real Example Hindi mein
**Tariff System**: "Explanatory Notes" छोटे, स्वतंत्र कथनों में लिखे हैं: "Item X बाहर है। Item Y शामिल है।" हर chunk में 4 वाक्य और 1 वाक्य overlap हर नियम को पूरा रखता है। Splitter "8518.30" या "No. 5" को अलग वाक्य नहीं बनाना चाहिए।

**Zomato AI**: support FAQ का 3 वाक्यों वाला जवाब एक chunk बनता है; जवाब पूरा लौटता है, citation के लिए source sentence ids के साथ।

---

## 💻 Code Example — Basic
```python
# Runs offline: regex sentence splitter that protects codes/abbreviations + grouping with overlap
import re

ABBREV = ("Dr", "Mr", "Mrs", "No", "Art", "Sec", "e.g", "i.e", "vs", "approx")  # words ending with a dot


def split_sentences(text: str) -> list[str]:
    t = re.sub(r"\s+", " ", text).strip()  # collapse whitespace/newlines
    for a in ABBREV:
        t = t.replace(f"{a}. ", f"{a}<DOT> ")  # protect abbreviation dots
    t = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", t)  # protect decimals and codes like 8518.30
    parts = re.split(r"(?<=[.!?।])\s+(?=[A-Zऀ-ॿ0-9\"'(])", t)  # boundary: end mark + space + start char
    return [p.replace("<DOT>", ".").strip() for p in parts if p.strip()]  # restore dots


def group(sentences: list[str], per_chunk: int = 3, overlap: int = 1) -> list[str]:
    if overlap >= per_chunk:
        raise ValueError("overlap must be smaller than per_chunk")
    step = per_chunk - overlap  # sentences to advance
    chunks = []
    for i in range(0, len(sentences), step):
        chunks.append(" ".join(sentences[i:i + per_chunk]))  # join sentences into one chunk
        if i + per_chunk >= len(sentences):  # last window reached
            break
    return chunks


text = ("Dr. Rao reviewed code 8518.30 for headphones. It applies to wired and wireless types. "
        "Microphone models go to 8518.40. See No. 5 of the notes. यह नियम 2026 से लागू है। नया कोड देखें।")
sents = split_sentences(text)
print(len(sents), sents)  # expect 6 sentences
print(group(sents, 3, 1))
```

## 💻 Code Example — Advanced
```python
# Production: pluggable splitter (pysbd if installed, regex fallback), size-aware grouping, async, errors
import asyncio
import logging
import re
from dataclasses import dataclass

log = logging.getLogger("sentence_chunker")

try:
    import pysbd  # pip install pysbd  (rule-based, handles many abbreviations)
    _seg = pysbd.Segmenter(language="en", clean=False)
    def split(text: str) -> list[str]:
        return [s.strip() for s in _seg.segment(text) if s.strip()]
except ImportError:
    log.warning("pysbd missing; using regex fallback")
    def split(text: str) -> list[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?।])\s+", text) if s.strip()]


@dataclass(frozen=True)
class SentenceChunk:
    text: str
    first_sentence: int
    last_sentence: int


def chunk_sentences(text: str, max_chars: int = 600, overlap_sentences: int = 1) -> list[SentenceChunk]:
    sents = split(text)
    out: list[SentenceChunk] = []
    i = 0
    while i < len(sents):
        j, size = i, 0
        while j < len(sents) and (size + len(sents[j]) <= max_chars or j == i):  # always take at least one
            size += len(sents[j]) + 1
            j += 1
        out.append(SentenceChunk(" ".join(sents[i:j]), i, j - 1))
        if j >= len(sents):
            break
        i = max(j - overlap_sentences, i + 1)  # step back for overlap, but always move forward
    return out


async def achunk(text: str, **kw) -> list[SentenceChunk]:
    return await asyncio.to_thread(chunk_sentences, text, **kw)


if __name__ == "__main__":
    demo = "Headphones are 8518.30. " * 40
    r = asyncio.run(achunk(demo, max_chars=200))
    print(len(r), r[0].first_sentence, r[0].last_sentence)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class Req(BaseModel):
    text: str = Field(min_length=1)
    max_chars: int = Field(600, ge=100, le=3000)


@app.post("/chunk/sentences")
async def sentences(req: Req) -> dict:
    try:
        chunks = await achunk(req.text, max_chars=req.max_chars)  # from Advanced example
    except Exception as exc:  # defensive: segmenters can fail on odd input
        raise HTTPException(status_code=422, detail=f"could not split: {exc}")
    return {"count": len(chunks), "chunks": [c.__dict__ for c in chunks[:20]]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-text-splitters nltk   (then: nltk.download("punkt_tab"))
from langchain_text_splitters import NLTKTextSplitter, SentenceTransformersTokenTextSplitter

nltk_splitter = NLTKTextSplitter(chunk_size=600, chunk_overlap=0)        # sentence-aware via NLTK
docs = nltk_splitter.create_documents(["Headphones are 8518.30. Microphone models are 8518.40."])

# Or a regex-driven recursive splitter that prefers sentence ends:
from langchain_text_splitters import RecursiveCharacterTextSplitter
sent_first = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", "। ", ". ", " "], chunk_size=600, chunk_overlap=80)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `text.split(".")`
```python
# Wrong: breaks "8518.30" into "8518" and "30", and "Dr." into a sentence
sents = text.split(".")
# Right: boundary regex with protections, or pysbd/nltk/spaCy
sents = split_sentences(text)
```

❌ Mistake 2: One sentence per chunk with no context
```python
# Wrong: "It applies to wired types." -> what is "It"?
# Right: group 3-5 sentences, overlap 1, and/or prepend the section title to every chunk
```

---

## 🧠 Tricky Interview Question

**Q**: "Your sentence chunker splits the sentence 'The duty is 12.5% ad valorem.' into two sentences. Why, and how to fix it generically?"

**Answer**: A naive regex treats "." as a terminator whenever it is followed by a digit or word. "12.5" has a dot between digits, and "% ad" may follow a dot in some patterns. Fix by requiring the boundary to be punctuation followed by whitespace and then an uppercase letter or opening quote, protecting digit-dot-digit patterns, and using a maintained segmenter (pysbd, spaCy, NLTK Punkt) for abbreviations. Then unit-test with a list of tricky cases from your own corpus (codes, currency, abbreviations, Hindi danda).

---

## ⚫ Interview Questions + Answers

Q1: Why not just split on periods?
A1: Periods also appear in abbreviations, decimals, codes and URLs, so you get broken fragments.

Q2: What marks a sentence end in Hindi?
A2: The danda "।" (and "?" or "!"). Splitters must include it.

Q3: Why group several sentences per chunk?
A3: Single sentences lack context and give too many tiny vectors; groups of 3-5 balance precision and context.

Q4: Name tools for sentence segmentation.
A4: NLTK Punkt, spaCy, pysbd, and regex rules for simple cases.

Q5: How would you evaluate a sentence splitter?
A5: Create a gold set of 100-200 tricky passages with manually marked boundaries, compute precision/recall of boundaries, and also run end-to-end retrieval recall@k, because perfect boundaries are only useful if retrieval improves.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Clean prose, FAQs, support articles, precise citation needed

❌ Avoid when:
- Tables, code, lists with few full sentences
- Text with no punctuation (transcripts: use time/speaker windows)

---

## 📊 Visual Diagram
```
 text ─► [S1][S2][S3][S4][S5][S6][S7]
 group 3, overlap 1:
   chunk A: S1 S2 S3
   chunk B:       S3 S4 S5
   chunk C:             S5 S6 S7
 (each chunk begins and ends on a full sentence)
```

---

## 💰 Cost Impact
- Overlap of 1 sentence in groups of 3 repeats about a third of the text: embeddings cost about 1.5x of the no-overlap baseline. Use groups of 4-5 with 1 overlap to cut it to 20-25 percent.
- Clean sentence boundaries help the LLM read faster, and precise chunks let you use a smaller k, saving prompt tokens (for example k=3 instead of 6 saves about 900 tokens per request at 300 tokens per chunk).
- Segmentation itself is cheap CPU, with no API cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sentence boundary | Where a sentence ends | वाक्य की सीमा |
| Segmenter | Tool that finds boundaries | सीमा खोजने वाला tool |
| Danda (।) | Hindi full stop | हिंदी का पूर्ण विराम |
| Abbreviation | Shortened word with a dot | संक्षिप्त शब्द |
| Sentence window | N sentences per chunk | प्रति chunk N वाक्य |

---

## ⚡ 3-Line Summary
English: Sentence splitting keeps ideas whole by cutting at sentence ends and grouping a few sentences per chunk. Protect codes, decimals and abbreviations, and include the Hindi danda. Use a tested segmenter.
Hindi: Sentence splitting वाक्य के अंत पर काटकर विचार पूरे रखती है और हर chunk में कुछ वाक्य समूहित करती है। Codes, decimals, abbreviations बचाओ और हिंदी "।" शामिल करो। परखा हुआ segmenter use करो।

---

## ➡️ Next Topic
**161. Paragraph Splitting** — use the author's own paragraph breaks as natural chunk boundaries.
