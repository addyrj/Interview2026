---

# 119. Multimodal Embeddings — Complete Guide
# हिंदी में: Multimodal Embeddings — पूरी Guide

---

## 🔵 Simple Definition (English)
Multimodal embeddings put different kinds of data (text, images, sometimes PDFs/screenshots, audio) into one shared vector space. A text query like "blue cotton shirt" can then retrieve an image of one, and a screenshot of a table can be found with a text question. Examples: CLIP/SigLIP (open), Cohere Embed v4, Voyage multimodal.

## 🔵 सरल परिभाषा (Hindi)
Multimodal embeddings अलग-अलग तरह के data (text, images, कभी PDFs/screenshots, audio) को एक shared vector space में रखते हैं। तब "blue cotton shirt" जैसी text query उसकी image ढूँढ सकती है, और table के screenshot को text सवाल से पाया जा सकता है। उदाहरण: CLIP/SigLIP (open), Cohere Embed v4, Voyage multimodal।

---

## 🔴 Problem it Solves
Real documents mix text, charts, tables and photos. Text-only RAG loses chart/diagram content, and OCR breaks layout. Separate text and image indexes need complicated merging. One shared space makes cross-modal search (text to image, image to text, image to image) simple and lets you embed a PDF page as an image to keep layout.

## 🔴 यह क्यों बना? (Hindi)
Real documents में text, charts, tables और photos मिले होते हैं। Text-only RAG में chart/diagram की जानकारी खो जाती है, और OCR layout तोड़ देता है। अलग text और image indexes को merge करना जटिल है। एक shared space से cross-modal search (text से image, image से text, image से image) आसान होता है, और PDF page को image की तरह embed करके layout बचा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Model has a text encoder and an image encoder trained together
          (contrastive learning: matching pairs pulled close, others pushed away)
Step 2 → Index time: embed each image / page screenshot / text chunk
Step 3 → Store vectors with metadata: modality, source, page, URL
Step 4 → Query time: embed the text (or an image) with the same model
Step 5 → Nearest neighbours may be images, text, or both
Step 6 → Optionally re-rank, or pass retrieved images to a vision LLM
Step 7 → LLM answers using the retrieved text + images
Step 8 → Evaluate per modality: text-to-image, image-to-image, text-to-text
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Model में text encoder और image encoder साथ में trained होते हैं
          (contrastive learning: matching pairs पास, बाकी दूर)
Step 2 → Index time: हर image / page screenshot / text chunk embed करो
Step 3 → Vectors के साथ metadata: modality, source, page, URL
Step 4 → Query time: text (या image) को same model से embed करो
Step 5 → Nearest neighbours images, text या दोनों हो सकते हैं
Step 6 → चाहें तो re-rank, या retrieved images vision LLM को दो
Step 7 → LLM retrieved text + images से जवाब देता है
Step 8 → हर modality का अलग evaluation
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importers submit invoices (scanned PDFs with tables and logos), product photos, and text descriptions. Each page is rendered as an image and embedded with a multimodal model; product photos are embedded too. A text query "plastic injection moulded part" retrieves both similar past photos and matching invoice pages; a vision LLM then reads the top 3 pages and proposes the HS code.

**Amazon-style**: Search by photo plus a text tweak ("like this but in green").

## 🟡 Real Example Hindi mein
**Tariff System**: Importers invoices (tables और logos वाले scanned PDFs), product photos और text descriptions देते हैं। हर page को image बनाकर multimodal model से embed किया जाता है; product photos भी embed होते हैं। "plastic injection moulded part" जैसी text query पुरानी similar photos और matching invoice pages दोनों निकालती है; फिर vision LLM top 3 pages पढ़कर HS code सुझाता है।

**Amazon-style**: Photo + text बदलाव से search ("इसी जैसा पर green में")।

---

## 💻 Code Example — Basic
```python
# Cross-modal search with CLIP (sentence-transformers). Falls back to a printed note if not installed.
try:
    from PIL import Image                                   # pip install pillow
    from sentence_transformers import SentenceTransformer, util
    HAVE = True
except ImportError:
    HAVE = False


def demo() -> None:
    model = SentenceTransformer("clip-ViT-B-32")            # one model, both modalities
    # Create two tiny solid-colour images so the demo needs no files
    red = Image.new("RGB", (224, 224), (220, 20, 20))
    blue = Image.new("RGB", (224, 224), (20, 20, 220))
    img_vecs = model.encode([red, blue], normalize_embeddings=True)       # image vectors
    txt_vecs = model.encode(["a red square", "a blue square"], normalize_embeddings=True)
    sims = util.cos_sim(txt_vecs, img_vecs)                 # 2 x 2 text-vs-image scores
    print(sims)                                             # diagonal should be higher


if HAVE:
    demo()
else:
    print("pip install sentence-transformers pillow to run the CLIP demo")
```

## 💻 Code Example — Advanced
```python
# Hosted multimodal embeddings with Cohere Embed v4 (text + page images), async, error handling
import asyncio
import base64
import io
import numpy as np
import cohere
from PIL import Image

co = cohere.AsyncClientV2()                                 # reads CO_API_KEY


def to_data_url(img: Image.Image) -> str:
    """Cohere accepts base64 data URLs for images."""
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


async def embed_images(images: list[Image.Image]) -> np.ndarray:
    try:
        r = await co.embed(
            model="embed-v4.0",
            input_type="image",
            embedding_types=["float"],
            images=[to_data_url(i) for i in images],
        )
    except Exception as exc:
        raise RuntimeError(f"image embedding failed: {exc}") from exc
    v = np.asarray(r.embeddings.float_, dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


async def embed_queries(texts: list[str]) -> np.ndarray:
    try:
        r = await co.embed(model="embed-v4.0", input_type="search_query",
                           embedding_types=["float"], texts=texts)
    except Exception as exc:
        raise RuntimeError(f"text embedding failed: {exc}") from exc
    v = np.asarray(r.embeddings.float_, dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


async def main() -> None:
    pages = [Image.new("RGB", (300, 300), (255, 255, 255)), Image.new("RGB", (300, 300), (0, 0, 0))]
    index = await embed_images(pages)
    q = (await embed_queries(["invoice table with totals"]))[0]
    print(np.argsort(-(index @ q)))


if __name__ == "__main__":
    asyncio.run(main())                                     # needs CO_API_KEY
```
(The exact parameters for image input differ between Cohere SDK versions and between providers; check the current API reference before use. Voyage offers `voyage-multimodal-3` through `voyageai.Client().multimodal_embed(...)`.)

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PIL import Image, UnidentifiedImageError
import io
import asyncio
import numpy as np
from sentence_transformers import SentenceTransformer

app = FastAPI()
model = SentenceTransformer("clip-ViT-B-32")


@app.post("/embed/multimodal")
async def embed_multimodal(text: str | None = Form(None), image: UploadFile | None = File(None)
                           ) -> dict[str, list[float] | str]:
    if text is None and image is None:
        raise HTTPException(422, "provide text, image, or both")
    parts: list[np.ndarray] = []
    if text:
        parts.append((await asyncio.to_thread(model.encode, [text], normalize_embeddings=True))[0])
    if image:
        try:
            img = Image.open(io.BytesIO(await image.read())).convert("RGB")
        except (UnidentifiedImageError, OSError):
            raise HTTPException(422, "invalid image")
        parts.append((await asyncio.to_thread(model.encode, [img], normalize_embeddings=True))[0])
    vec = np.mean(parts, axis=0)                      # simple fusion of text and image vectors
    vec = vec / np.linalg.norm(vec)
    return {"vector": vec.tolist(), "modes": "+".join(m for m, p in (("text", text), ("image", image)) if p)}
```
The averaging fusion supports "this photo, but in green" style queries.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# Retrieval: use OpenCLIPEmbeddings / Cohere / Voyage multimodal with a vector store.
# Generation: pass retrieved images to a vision-capable chat model:
llm = ChatOpenAI(model="gpt-4o-mini")
msg = HumanMessage(content=[
    {"type": "text", "text": "Which HS code fits this product?"},
    {"type": "image_url", "image_url": {"url": "https://example.com/product.jpg"}},
])
# answer = llm.invoke([msg])
```
LangGraph pattern: node 1 embeds the query and retrieves text and image hits, node 2 builds a multimodal message, node 3 calls the vision LLM; a conditional edge asks for more evidence if confidence is low.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting text-to-image scores to be comparable with text-to-text scores
✅ Correct: Cross-modal scores sit in a lower range (modality gap). Normalise per modality or retrieve per modality and merge with ranks (RRF).

```python
# Wrong: one global threshold 0.8 for all modalities
# Right: per-modality thresholds or rank fusion
```

❌ Mistake 2: Mixing two different multimodal models in one index
✅ Correct: One model for all modalities in an index.

❌ Mistake 3: Trusting the embedding for text inside images
✅ Correct: Use a document-aware model, or OCR + text embedding, for dense text pages.

---

## 🧠 Tricky Interview Question

**Q**: "CLIP retrieves a photo of a dog for the query 'cat', because the top image-to-text scores are all around 0.25. What is happening?"

**Answer**: The "modality gap": image and text embeddings occupy different regions of the shared space, so cross-modal cosine scores are small (about 0.2 to 0.35 for CLIP) and differences between good and bad matches are narrow. Rank is meaningful, absolute value is not. Use relative ranking, calibrate thresholds on labelled data, re-rank with a vision LLM, or use a newer model (SigLIP, Cohere v4) with better alignment.

---

## ⚫ Interview Questions + Answers

Q1: What is a multimodal embedding?
A1: A vector in a shared space for multiple data types, so text and images can be compared.

Q2: How are CLIP-like models trained?
A2: Contrastively on image-caption pairs: pull matching pairs together, push mismatched ones apart.

Q3: Why embed PDF pages as images?
A3: It keeps layout, tables and charts that text extraction and OCR lose (the ColPali-style approach).

Q4: What is the modality gap?
A4: Text and image vectors cluster in separate zones, so cross-modal similarities are lower than within-modality ones.

Q5: Design multimodal RAG for invoices and photos.
A5: Render pages to images, embed pages and photos with a multimodal model, also OCR the text and embed it for exact terms, store modality/source/page metadata, do hybrid retrieval and rank fusion, send the top pages and images to a vision LLM with citations, evaluate recall by modality, and cache embeddings by file hash.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Visual content carries meaning (charts, products, diagrams)
- Search across text and images is needed

❌ Avoid when:
- Everything is plain text (a text model is cheaper and stronger)
- You need exact text lookup in images (use OCR)

---

## 📊 Visual Diagram
```
  text "red shirt" ──┐                    ┌── image of red shirt
                     ├──► shared vector space ◄──┤
  PDF page image ────┘     (nearby = similar)    └── another shirt photo

  query vector ──► nearest neighbours (any modality) ──► vision LLM ──► answer
```

---

## 💰 Cost Impact
Multimodal APIs bill images by pixels or token equivalents (for example, an image can count as hundreds to over a thousand tokens; check each provider's pricing). Embedding every PDF page as an image is far more expensive than text chunks. Optimise: downscale images, embed only pages that contain figures/tables, cache by file hash, use open CLIP/SigLIP locally for photos, and keep vision LLM calls to the top few results (image input tokens are expensive).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multimodal | More than one data type | एक से ज़्यादा data type |
| Shared space | One vector space for all types | सबके लिए एक vector space |
| Contrastive learning | Pull matches, push non-matches | Matches पास, बाकी दूर |
| Modality gap | Text/image cluster apart | Text/image का अलग cluster |
| RRF | Reciprocal rank fusion | Ranks को मिलाने की विधि |
| Vision LLM | LLM that reads images | Images पढ़ने वाला LLM |

---

## ⚡ 3-Line Summary
English: Multimodal embeddings put text and images in one space for cross-modal search. Rank matters more than absolute score because of the modality gap. Combine with OCR for text-heavy pages and a vision LLM for final answers.
Hindi: Multimodal embeddings text और images को एक space में रखते हैं ताकि cross-modal search हो सके। Modality gap के कारण absolute score से ज़्यादा rank मायने रखता है। Text-heavy pages के लिए OCR और final answers के लिए vision LLM जोड़ो।

---

## ➡️ Next Topic
**120. Embedding Evaluation** - how to measure whether your embeddings actually retrieve the right things (recall@k, MRR, nDCG).
