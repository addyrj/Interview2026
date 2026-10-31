---

# 228. Multi-Modal RAG
# हिंदी में: Multi-Modal RAG (text + image + table)

---

## 🔵 Simple Definition (English)
Multi-Modal RAG retrieves and answers over more than text: images, tables, charts and scanned pages. Content is either summarised into text for retrieval, or embedded with a multi-modal model, then passed to a vision-capable LLM.

## 🔵 सरल परिभाषा (Hindi)
Multi-Modal RAG सिर्फ text नहीं, images, tables, charts और scanned pages पर भी retrieve और answer करता है। Content को या तो text summary बनाकर index करते हैं, या multi-modal model से embed करते हैं, फिर vision-capable LLM को देते हैं।

---

## 🔴 Problem it Solves
Real documents are not plain text. Tariff PDFs hold duty tables, invoices are scans, product pages have photos. Text-only RAG loses tables (flattened into garbage) and ignores images entirely, so answers are incomplete or wrong.

## 🔴 यह क्यों बना? (Hindi)
असली documents सिर्फ text नहीं होते। Tariff PDFs में duty tables, invoices scans, product pages में photos। Text-only RAG tables बिगाड़ देता है और images को ignore करता है, इसलिए answers अधूरे या गलत होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parse the document: split into text, tables, images
Step 2 → Choose a strategy:
           A) Summarise tables/images to text, embed the summaries
           B) Embed images directly (CLIP / multi-modal embeddings)
           C) Page-as-image retrieval (ColPali-style)
Step 3 → Store vectors + keep a pointer to the raw table/image
Step 4 → Query: embed question, retrieve top-k (text + image refs)
Step 5 → Load raw content for hits
Step 6 → Send text + images to a vision LLM (e.g., gpt-4o)
Step 7 → Answer with citation to page/figure
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Document parse करो: text, tables, images अलग
Step 2 → Strategy चुनो: A) tables/images की text summary embed
          B) images सीधे embed (CLIP) C) पूरा page image की तरह
Step 3 → Vectors store करो + raw table/image का pointer रखो
Step 4 → Query embed करके top-k लाओ
Step 5 → Hits का raw content load करो
Step 6 → Text + images vision LLM को भेजो
Step 7 → Page/figure के citation के साथ answer दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs circular has a duty table as an image and a product photo of a "solar inverter". Strategy A: a vision LLM writes "Table: HS 8504.40, BCD 7.5 percent, IGST 12 percent", embeds it, and stores the PNG pointer. At query time the table image itself goes to gpt-4o for an exact read. **Amazon**: "does this charger match the one in my photo?" uses image embeddings + catalog text.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs circular में duty table image के रूप में है और "solar inverter" की product photo। Strategy A: vision LLM "Table: HS 8504.40, BCD 7.5%, IGST 12%" जैसी summary लिखता है, उसे embed करता है, PNG का pointer रखता है। Query पर table image खुद gpt-4o को जाती है ताकि exact पढ़ा जा सके।

---

## 💻 Code Example — Basic
```python
# Multi-vector pattern offline: index summaries, return raw objects (mock summarizer)
from dataclasses import dataclass

@dataclass
class Item:
    kind: str  # "text" | "table" | "image"
    raw: str  # raw content or file path
    summary: str  # text used for retrieval

ITEMS: list[Item] = [
    Item("text", "Chapter 85 notes ...", "chapter 85 notes electrical goods"),
    Item("table", "| 8504.40 | 7.5% | 12% |", "duty table inverter 8504.40 bcd 7.5 igst 12"),
    Item("image", "figs/inverter.png", "photo of solar inverter device"),
]

def search(query: str, k: int = 2) -> list[Item]:
    q = set(query.lower().split())  # query words
    ranked = sorted(ITEMS, key=lambda i: -len(q & set(i.summary.split())))  # overlap score
    return ranked[:k]  # top-k items

for hit in search("duty on solar inverter"):
    print(hit.kind, "->", hit.raw)  # the RAW object is what the LLM finally sees
```

## 💻 Code Example — Advanced
```python
# Async multi-modal answer: retrieved text + base64 images -> vision LLM
import asyncio
import base64
from pathlib import Path
from openai import AsyncOpenAI, APIError

client = AsyncOpenAI()

def encode_image(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("utf-8")  # file -> base64

async def summarize_image(path: str) -> str:
    """Ingestion: vision model describes a table/figure for indexing."""
    b64 = encode_image(path)
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=300,  # cap output cost
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this tariff table/figure as searchable text."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "low"}},
            ],
        }],
    )
    return resp.choices[0].message.content or ""

async def answer(question: str, texts: list[str], image_paths: list[str]) -> str:
    content: list[dict] = [{"type": "text", "text": f"Context:\n{chr(10).join(texts)}\n\nQ: {question}"}]
    for p in image_paths:  # attach retrieved images
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(p)}"}})
    try:
        r = await client.chat.completions.create(
            model="gpt-4o", max_tokens=400, messages=[{"role": "user", "content": content}]
        )
        return r.choices[0].message.content or ""
    except APIError as exc:  # network / rate limit / bad image
        return f"Vision call failed: {exc}"
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/tariff/ingest-image")
async def ingest(file: UploadFile = File(...)) -> dict:
    path = f"/tmp/{file.filename}"  # use a safe temp dir in prod
    with open(path, "wb") as f:
        f.write(await file.read())  # save upload
    summary = await summarize_image(path)  # describe it
    # vectorstore.add_texts([summary], metadatas=[{"image_path": path}])  # index summary + pointer
    return {"summary": summary, "path": path}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's **MultiVectorRetriever** stores summaries in the vector store and raw docs in a docstore (`InMemoryStore`), linked by `doc_id`. Retrieval returns the raw item. `unstructured` / `UnstructuredPDFLoader` can extract tables and images.

```python
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
# retriever = MultiVectorRetriever(vectorstore=vs, docstore=InMemoryStore(), id_key="doc_id")
# retriever.vectorstore.add_documents(summary_docs)   # summaries with metadata doc_id
# retriever.docstore.mset(list(zip(ids, raw_items)))  # raw tables/images
# In LangGraph: parse -> summarize -> index nodes for ingestion; retrieve -> vision_answer for query.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Flattening tables with plain text extraction
```python
# Wrong: page.extract_text()  -> columns merge into nonsense
# Right: extract tables as markdown/HTML or summarise table image with a vision model
```

❌ Mistake 2: Sending full-resolution images always
```python
# Wrong: "detail": "high" for every image
# Right: "detail": "low" unless fine print matters; resize before sending
```

---

## 🧠 Tricky Interview Question
**Q**: "Retrieval finds the right table summary but the answer shows wrong numbers. Why?"

**Answer**: The summary was used for retrieval but the LLM answered from the summary, not the original. Summaries lose digits. Use the multi-vector pattern: retrieve by summary, answer from the raw table (markdown or image). Also add a verification step that quotes cell values.

---

## ⚫ Interview Questions + Answers

Q1: Why not just OCR everything? (Easy)
A1: OCR loses layout (tables, charts) and visual meaning. Fine for plain scans, weak for tables/figures.

Q2: What is a multi-vector retriever? (Easy)
A2: Index one representation (summary) but return another (raw doc), linked by an ID.

Q3: CLIP embeddings vs summaries? (Medium)
A3: CLIP embeds images and text in one space, enabling text-to-image search, but captures coarse semantics. Summaries via a vision LLM capture detail (numbers, labels) but cost tokens at ingest.

Q4: What is page-image retrieval (ColPali)? (Medium)
A4: Embed whole page screenshots with a vision-language retriever, skipping parsing. Good for layout-heavy docs, heavier storage.

Q5: Design multi-modal RAG for 100k scanned customs forms. (Hard)
A5: Batch ingest: layout parser, tables to markdown, figures to low-detail vision summaries (batch API for 50 percent off), multi-vector store, hybrid search, rerank, answer with raw table plus page image, cite page numbers, monitor per-modality recall.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers live in tables, charts, scans, photos
- Visual product/document search

❌ Avoid when:
- Corpus is clean text (extra cost, no gain)
- Vision cost exceeds value of the images

---

## 📊 Visual Diagram
```
 PDF ─► Parser ─┬─► text chunks ───────────┐
                ├─► tables ─► summary ─────┤► Vector store (summaries)
                └─► images ─► summary ─────┘          │
                       │raw                            │ top-k ids
                       ▼                               ▼
                  Docstore  ◄────────── fetch raw ─────┘
                       ▼
               Vision LLM (text + images) ─► Answer + citation
```

---

## 💰 Cost Impact
Images cost tokens: gpt-4o low detail is a fixed small cost (about 85 tokens); high detail tiles can reach 1,000+ tokens per image. Ingestion summaries are one-time; query-time image inputs recur. Optimise: low detail by default, downscale, send only top-1/2 images, summarise at ingest (batch API), cache answers.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Modality | Type of data (text/image) | डेटा का प्रकार |
| CLIP | Joint image-text embedding | Image-text embedding |
| Multi-vector | Index summary, return raw | Summary से ढूँढो, raw दो |
| Vision LLM | LLM that reads images | Image पढ़ने वाला LLM |
| Docstore | Stores raw objects | Raw objects का store |

---

## ⚡ 3-Line Summary
English: Multi-Modal RAG handles tables, images and scans, not just text. Index summaries or image embeddings, but answer from the raw object with a vision LLM. Control cost with low image detail and batch ingestion.
Hindi: Multi-Modal RAG tables, images और scans संभालता है, सिर्फ text नहीं। Summaries/image embeddings index करो, पर answer raw object से vision LLM के जरिए दो। Low image detail और batch ingestion से cost काबू में रखो।

---

## ➡️ Next Topic
**229. RAG for Tariff System** — putting all RAG pieces together for our main project.
