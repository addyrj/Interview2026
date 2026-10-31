---

# 194. Text Preprocessing
# हिंदी में: Text Preprocessing (टेक्स्ट प्रीप्रोसेसिंग)

---

## 🔵 Simple Definition (English)
Text preprocessing cleans raw extracted text before chunking and embedding: fix encoding, normalise Unicode and whitespace, remove headers/footers and boilerplate, repair hyphenated line breaks, deduplicate, and keep structure (headings, tables). For RAG, clean lightly: do not remove stop words or lowercase blindly.

## 🔵 सरल परिभाषा (Hindi)
Text preprocessing chunking और embedding से पहले raw text साफ़ करती है: encoding ठीक करना, Unicode और whitespace normalise करना, header/footer और boilerplate हटाना, hyphen से टूटी lines जोड़ना, duplicates हटाना, और structure (headings, tables) बचाना। RAG में हल्की सफ़ाई करो: stop words हटाना या बिना सोचे lowercase करना ज़रूरी नहीं।

---

## 🔴 Problem it Solves
Extracted PDFs contain "Page 12 of 300" on every page, ligatures ("ﬁ"), soft hyphens, broken words ("classifi-\ncation"), repeated disclaimers and mojibake ("â€™"). These add noise to embeddings, waste tokens, break keyword search and cause near-duplicate retrieval.

## 🔴 यह क्यों बना? (Hindi)
Extracted PDFs में हर page पर "Page 12 of 300", ligatures ("ﬁ"), soft hyphens, टूटे शब्द ("classifi-\ncation"), दोहराए disclaimers और mojibake ("â€™") होते हैं। ये embeddings में noise डालते हैं, tokens बर्बाद करते हैं, keyword search तोड़ते हैं और near-duplicate retrieval कराते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decode correctly (UTF-8) and fix mojibake
Step 2 → Unicode normalise (NFKC): ligatures, full-width chars, odd spaces
Step 3 → Remove control chars and soft hyphens
Step 4 → Join hyphenated line breaks ("classifi-\ncation" -> "classification")
Step 5 → Remove repeated headers/footers/page numbers (lines repeated on many pages)
Step 6 → Collapse whitespace but KEEP paragraph breaks and headings
Step 7 → Deduplicate identical/near-identical paragraphs (hash)
Step 8 → Log before/after size so you can see what was removed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सही decode (UTF-8) और mojibake ठीक करो
Step 2 → Unicode normalise (NFKC): ligatures, full-width chars, अजीब spaces
Step 3 → Control chars और soft hyphens हटाओ
Step 4 → Hyphen से टूटी lines जोड़ो
Step 5 → बार-बार आने वाले header/footer/page numbers हटाओ
Step 6 → Whitespace collapse करो पर paragraph breaks और headings रखो
Step 7 → Identical paragraphs को hash से dedupe करो
Step 8 → पहले/बाद का size log करो ताकि दिखे क्या हटा
```

---

## 🟡 Real World Example
**Tariff Classification System**: Every page of the tariff PDF ends with "Customs Tariff 2025 — Page 143". Without cleaning, 300 near-identical footer chunks pollute retrieval and a query on "customs tariff 2025" returns only footers. After cleaning, those lines are gone, "8518.30" stays intact (never strip digits or dots!), and "classifi-\ncation" becomes "classification" so BM25 finds it.
**Amazon AI**: Product descriptions contain HTML entities and emoji spam; they are normalised before embedding.

## 🟡 Real Example Hindi mein
**Tariff System**: Tariff PDF के हर page के अंत में "Customs Tariff 2025 — Page 143" है। सफ़ाई के बिना 300 लगभग-एक-जैसे footer chunks retrieval बिगाड़ते हैं और "customs tariff 2025" query सिर्फ footers लौटाती है। सफ़ाई के बाद वे lines हट जाती हैं, "8518.30" सुरक्षित रहता है (digits या dots कभी न हटाओ!), और "classifi-\ncation" "classification" बन जाता है ताकि BM25 उसे ढूँढ सके।
**Amazon AI**: Product descriptions में HTML entities और emoji spam होता है; embedding से पहले normalise किया जाता है।

---

## 💻 Code Example — Basic
```python
# Light, safe cleaning for RAG (standard library only, runs directly)
import re
import unicodedata
from collections import Counter
from typing import List

def normalise(text: str) -> str:
    """Unicode normalise, drop control chars and soft hyphens."""
    text = unicodedata.normalize("NFKC", text)  # ligatures -> letters, odd spaces -> spaces
    text = text.replace("­", "")  # remove soft hyphen
    return "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")  # drop control chars

def fix_hyphens(text: str) -> str:
    """Join words broken across lines: 'classifi-\\ncation' -> 'classification'."""
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)

def collapse_ws(text: str) -> str:
    """Collapse spaces/tabs but keep paragraph breaks."""
    text = re.sub(r"[ \t]+", " ", text)  # many spaces -> one
    return re.sub(r"\n{3,}", "\n\n", text).strip()  # at most one blank line

def drop_repeated_lines(pages: List[str], min_pages: int = 3) -> List[str]:
    """Remove lines (after stripping digits) that repeat on >= min_pages pages: headers/footers."""
    key = lambda ln: re.sub(r"\d+", "#", ln.strip())  # 'Page 12' and 'Page 13' share key 'Page #'
    counts = Counter(key(ln) for p in pages for ln in set(p.splitlines()) if ln.strip())  # pages per line
    return ["\n".join(ln for ln in p.splitlines() if counts[key(ln)] < min_pages) for p in pages]

def clean_pages(pages: List[str]) -> str:
    pages = drop_repeated_lines(pages)  # headers/footers first
    return collapse_ws(fix_hyphens(normalise("\n\n".join(pages))))  # then text-level fixes

if __name__ == "__main__":
    parts = [("ear", "phones"), ("speak", "ers"), ("micro", "phones"), ("head", "sets")]  # words split by a hyphen
    pages = [f"HS 8518.30 {a}-\n{b} classified\nCustoms Tariff 2025 - Page {i}"
             for i, (a, b) in enumerate(parts, start=1)]  # unique body, repeated footer
    out = clean_pages(pages)  # run cleaner
    print(out)  # footers gone, 'classification' joined, '8518.30' intact
    print(normalise("\ufb01ne text"))  # ligature fixed: 'fine text'
```

## 💻 Code Example — Advanced
```python
# Configurable async cleaning pipeline with metrics, per-step error isolation and dedupe
import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger("preprocess")  # logger
Step = Callable[[str], str]  # a cleaning step: str -> str

@dataclass
class CleanReport:
    chars_before: int = 0  # size before
    chars_after: int = 0  # size after
    duplicates_removed: int = 0  # paragraphs dropped
    failed_steps: list[str] = field(default_factory=list)  # steps that raised

    @property
    def saved_pct(self) -> float:
        return 0.0 if not self.chars_before else round(100 * (1 - self.chars_after / self.chars_before), 1)

def dedupe_paragraphs(text: str, report: CleanReport) -> str:
    """Drop exact duplicate paragraphs (case/space-insensitive hash)."""
    seen: set[str] = set(); out: list[str] = []  # state
    for para in text.split("\n\n"):
        h = hashlib.md5(re.sub(r"\s+", " ", para.lower()).strip().encode()).hexdigest()  # fingerprint
        if h in seen and para.strip():
            report.duplicates_removed += 1; continue  # duplicate
        seen.add(h); out.append(para)
    return "\n\n".join(out)

class Preprocessor:
    def __init__(self, steps: list[tuple[str, Step]]) -> None:
        self.steps = steps  # ordered (name, function)

    def run(self, text: str) -> tuple[str, CleanReport]:
        rep = CleanReport(chars_before=len(text))  # start report
        for name, fn in self.steps:
            try:
                new = fn(text)
                if not new.strip():  # safety: a step must not wipe the document
                    raise ValueError("step produced empty text")
                text = new
            except Exception as exc:  # skip broken step, keep going
                logger.warning("step %s skipped: %r", name, exc); rep.failed_steps.append(name)
        text = dedupe_paragraphs(text, rep)  # final dedupe
        rep.chars_after = len(text)
        return text, rep

    async def arun_many(self, texts: list[str]) -> list[tuple[str, CleanReport]]:
        return await asyncio.gather(*(asyncio.to_thread(self.run, t) for t in texts))  # parallel CPU work in threads

if __name__ == "__main__":
    pre = Preprocessor([("ws", lambda t: re.sub(r"[ \t]+", " ", t)),
                        ("hyph", lambda t: re.sub(r"(\w)-\n(\w)", r"\1\2", t))])
    docs = ["HS 8518.30  earphones\n\nHS 8518.30 earphones\n\nclassifi-\ncation"]
    for text, rep in asyncio.run(pre.arun_many(docs)):
        print(repr(text), rep)  # duplicates_removed=1
```

---

## 🟠 FastAPI Integration
Run preprocessing inside the ingestion path (not per query). Offer a `/preprocess/preview` endpoint so content owners can see what will be removed. Use `asyncio.to_thread` for large texts.

```python
# FastAPI: preview what cleaning will do
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()  # app

class PreviewReq(BaseModel):
    text: str = Field(max_length=200_000)  # cap size

@app.post("/preprocess/preview")
async def preview(req: PreviewReq) -> dict:
    cleaned, rep = await asyncio.to_thread(pre.run, req.text)  # Preprocessor from Advanced example
    return {"cleaned_preview": cleaned[:1000], "saved_pct": rep.saved_pct,
            "duplicates_removed": rep.duplicates_removed, "failed_steps": rep.failed_steps}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `Html2TextTransformer`, `BeautifulSoupTransformer` (document transformers) and `RecursiveCharacterTextSplitter` (which already prefers paragraph/sentence boundaries). Custom cleaning is typically a `RunnableLambda` before the splitter, or a `BaseDocumentTransformer`.

```python
# Cleaning as a document transformer (needs langchain-core)
from typing import Any, Sequence
from langchain_core.documents import BaseDocumentTransformer, Document

class CleanTransformer(BaseDocumentTransformer):
    """Applies clean_pages-style logic to each Document."""
    def transform_documents(self, documents: Sequence[Document], **kwargs: Any) -> Sequence[Document]:
        return [Document(page_content=" ".join(d.page_content.split()), metadata=d.metadata) for d in documents]

docs = [Document(page_content="HS   8518.30\n\n earphones", metadata={"page": 1})]
print(CleanTransformer().transform_documents(docs)[0].page_content)  # 'HS 8518.30 earphones'
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Classic NLP cleaning (lowercase, strip punctuation, remove stop words) before embedding.
✅ Correct: Modern embedding models understand natural text; stripping punctuation destroys codes like "8518.30" and "not" removal flips meaning.

```python
# Wrong
text = re.sub(r"[^a-z ]", "", text.lower())     # "8518.30" -> "", "no duty" -> "duty" without stop-word list
# Right
text = " ".join(text.split())                    # whitespace only
```

❌ Mistake 2: Cleaning only the documents, not the queries (or vice versa).
✅ Correct: Apply the same normalisation (Unicode, whitespace) to queries so BM25/embedding behave consistently.

```python
# Wrong
index(normalise(doc)); search(raw_query)
# Right
index(normalise(doc)); search(normalise(raw_query))
```

---

## 🧠 Tricky Interview Question
**Q**: "After a cleaning step was added, retrieval recall dropped from 85 to 70 percent. What could have gone wrong?"

**Answer**: Likely over-cleaning removed meaningful text: e.g., regex that strips lines with numbers deleted table rows or HS codes; header removal also removed real section titles; dedupe merged legitimately repeated paragraphs from different chapters; lowercasing or punctuation removal changed codes. Debug by diffing before/after on a sample, checking removed lines list, and re-running the eval per step (ablation). Make each step reversible/loggable and gate changes by eval results.

---

## ⚫ Interview Questions + Answers

Q1: Why is Unicode normalisation useful?
A1: The same visible text can have different code points (ligatures, full-width, combining accents). NFKC makes them consistent so exact and keyword matching work.

Q2: Should you remove stop words for RAG?
A2: Generally no. Dense models use full sentences, and stop words (like "not") can carry meaning. For BM25, the scoring (IDF) already down-weights common words.

Q3: How do you detect headers and footers?
A3: Lines that repeat (after masking digits) on many pages or appear at consistent positions; remove those above a frequency threshold.

Q4: What is near-duplicate detection and why use it?
A4: Finding almost-identical text (MinHash/SimHash/embedding similarity) to avoid redundant chunks that waste tokens and bias retrieval.

Q5: How do you handle multilingual or mixed Hindi-English text?
A5: Keep Unicode intact (NFC/NFKC), do not ASCII-fold, use a multilingual embedding model, preserve script-specific punctuation (the danda), and chunk by characters/tokens measured with the model's own tokenizer since Devanagari uses more tokens.

---

## 🔷 When to Use + When Not to Use
✅ Use preprocessing when:
- Sources are PDFs, scraped web pages, OCR output
- You see repeated boilerplate in retrieved chunks
- You use keyword (BM25) search

❌ Avoid heavy cleaning when:
- Text is already clean (database fields)
- Exact wording matters (legal clauses): keep original text and store cleaned text only for the search index

---

## 📊 Visual Diagram
```
 raw text
   │ decode + NFKC
   ▼
 remove control chars / soft hyphens
   ▼
 join "classifi-\ncation"
   ▼
 drop repeated headers/footers ("Page #")
   ▼
 collapse whitespace (keep paragraphs)
   ▼
 dedupe paragraphs (hash)
   ▼
 clean text ──► Splitter     (keep original text in metadata if exact quoting is needed)
```

---

## 💰 Cost Impact
Cleaning is CPU-only (free in tokens) but cuts spend: removing 10 percent boilerplate from 50M tokens saves 5M embedding tokens (0.10 USD) once, and 10 percent of context tokens per query for the life of the system. For 100k queries/day at ~1600 context tokens, that is 16M tokens/day, about 2.40 USD/day on gpt-4o-mini input.
Optimize: do it once at ingestion, cache by file hash, measure saved percent in a report.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Normalisation | Make text forms consistent | Text को एक जैसा बनाना |
| NFKC | Unicode compatibility normal form | Unicode normalisation का रूप |
| Boilerplate | Repeated filler text | बार-बार आने वाला भराव text |
| Deduplication | Remove repeated content | Duplicates हटाना |
| Mojibake | Wrongly decoded characters | गलत decode हुए अक्षर |
| Stop words | Very common words (the, is) | बहुत आम शब्द |

---

## ⚡ 3-Line Summary
English: Clean extracted text lightly: normalise Unicode, fix hyphens, remove headers/footers, dedupe.
Never strip digits or punctuation that carry meaning, like HS codes.
Log before/after and test with an eval so cleaning never hurts recall.
Hindi: Extracted text हल्का साफ़ करो: Unicode normalise, hyphens ठीक, header/footer हटाओ, dedupe।
HS codes जैसे digits या punctuation कभी मत हटाओ।
Before/after log करो और eval से जाँचो कि सफ़ाई recall नहीं घटा रही।

---

## ➡️ Next Topic
**195. Metadata Extraction**: adding structure (chapter, country, date, HS code) to each chunk automatically.
