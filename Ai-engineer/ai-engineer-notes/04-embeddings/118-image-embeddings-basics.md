---

# 118. Image Embeddings Basics — Complete Guide
# हिंदी में: Image Embeddings की Basics — पूरी Guide

---

## 🔵 Simple Definition (English)
An image embedding is a vector that represents what a picture shows. A vision model (CNN, ViT, or CLIP) reads the pixels and outputs a fixed-length list of numbers. Similar-looking or similar-meaning images get nearby vectors, enabling image search, de-duplication, and classification.

## 🔵 सरल परिभाषा (Hindi)
Image embedding एक vector है जो बताता है कि तस्वीर में क्या है। Vision model (CNN, ViT या CLIP) pixels पढ़कर numbers की fixed-length list देता है। मिलती-जुलती images के vectors पास होते हैं, जिससे image search, de-duplication और classification संभव होती है।

---

## 🔴 Problem it Solves
Keyword search cannot find "red sneakers" if the image has no caption. Manual tagging of millions of images is slow and inconsistent. Image embeddings allow "find images like this one" (image-to-image) without any text, and with CLIP-style models also "find images matching this text".

## 🔴 यह क्यों बना? (Hindi)
अगर image का caption नहीं है तो keyword search "red sneakers" नहीं ढूँढ सकता। लाखों images की manual tagging धीमी और inconsistent है। Image embeddings से बिना text के "इस जैसी images ढूँढो" (image-to-image) संभव है, और CLIP जैसे models से "इस text से मेल खाती images" भी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load image, convert to RGB
Step 2 → Resize/crop to the model's input size (e.g. 224 x 224) and normalise pixels
Step 3 → Vision encoder (ViT / ResNet) turns patches into feature vectors
Step 4 → Pool/project to one vector (e.g. 512-d for CLIP ViT-B/32)
Step 5 → L2 normalise
Step 6 → Store in a vector DB with image id/path/metadata
Step 7 → Query: embed the query image (or text for CLIP) and run nearest-neighbour search
Step 8 → Rank by cosine; optionally filter by metadata
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image load करो, RGB में बदलो
Step 2 → Model के input size (जैसे 224 x 224) पर resize/crop और pixels normalise
Step 3 → Vision encoder (ViT / ResNet) patches को feature vectors में बदलता है
Step 4 → एक vector में pool/project (CLIP ViT-B/32 में 512-d)
Step 5 → L2 normalise
Step 6 → Image id/path/metadata के साथ vector DB में store
Step 7 → Query: query image (या CLIP में text) embed करके nearest-neighbour search
Step 8 → Cosine से rank; चाहें तो metadata filter
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importers upload product photos. The system embeds the photo with CLIP and retrieves the 10 most similar images from past classified shipments, whose HS codes become candidate answers. It also finds near-duplicate photos to detect repeated fraudulent declarations.

**Amazon / Zomato-style**: "Shop the look" (upload a photo, find similar products); Zomato finds visually similar dishes.

## 🟡 Real Example Hindi mein
**Tariff System**: Importers product photos upload करते हैं। System photo को CLIP से embed करके पुरानी classified shipments की 10 सबसे similar images निकालता है, जिनके HS codes candidate answers बनते हैं। Near-duplicate photos पकड़कर बार-बार की fraudulent declarations भी पता चलती हैं।

**Amazon / Zomato-style**: "Shop the look" (photo upload करो, similar products पाओ); Zomato visually similar dishes ढूँढता है।

---

## 💻 Code Example — Basic
```python
# Image embeddings with CLIP via sentence-transformers (falls back to a tiny hand-made embedder offline)
from pathlib import Path
from typing import Any

try:
    from PIL import Image                               # pip install pillow
    from sentence_transformers import SentenceTransformer   # pip install sentence-transformers
    HAVE = True
except ImportError:
    HAVE = False


def color_histogram_embed(pixels: list[tuple[int, int, int]]) -> list[float]:
    """Toy 'embedding': average R,G,B (shows the idea of images -> numbers; not semantic)."""
    n = max(1, len(pixels))
    return [sum(p[i] for p in pixels) / n / 255 for i in range(3)]


def clip_embed(paths: list[str]) -> Any:
    model = SentenceTransformer("clip-ViT-B-32")        # 512-d image+text model
    images = [Image.open(p).convert("RGB") for p in paths]   # load as RGB
    return model.encode(images, normalize_embeddings=True)   # (n, 512)


red = [(250, 10, 10)] * 100
dark_red = [(200, 20, 20)] * 100
blue = [(10, 10, 250)] * 100
print("red      :", [round(x, 2) for x in color_histogram_embed(red)])
print("dark red :", [round(x, 2) for x in color_histogram_embed(dark_red)])
print("blue     :", [round(x, 2) for x in color_histogram_embed(blue)])
if HAVE:
    print("CLIP available: call clip_embed(['a.jpg', 'b.jpg'])")
```

## 💻 Code Example — Advanced
```python
# Image similarity search service logic: embed folder, search by image or text, async-friendly
import asyncio
from pathlib import Path
import numpy as np
from numpy.typing import NDArray
from PIL import Image
from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:                                    # lazy singleton
        _model = SentenceTransformer("clip-ViT-B-32")
    return _model


def embed_images_sync(paths: list[Path]) -> NDArray[np.float32]:
    """Blocking embedding of images; skips unreadable files with a clear error."""
    imgs: list[Image.Image] = []
    for p in paths:
        try:
            imgs.append(Image.open(p).convert("RGB"))
        except (OSError, ValueError) as exc:
            raise ValueError(f"cannot read image {p}: {exc}") from exc
    return get_model().encode(imgs, batch_size=16, normalize_embeddings=True).astype(np.float32)


async def embed_images(paths: list[Path]) -> NDArray[np.float32]:
    return await asyncio.to_thread(embed_images_sync, paths)   # keep event loop free


async def embed_text(texts: list[str]) -> NDArray[np.float32]:
    return await asyncio.to_thread(
        lambda: get_model().encode(texts, normalize_embeddings=True).astype(np.float32))


def top_k(query: NDArray[np.float32], index: NDArray[np.float32], k: int = 5) -> list[tuple[int, float]]:
    scores = index @ query                                 # unit vectors -> cosine
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order]


async def main() -> None:
    files = sorted(Path("images").glob("*.jpg"))           # your folder
    index = await embed_images(files)
    q = (await embed_text(["a pair of wireless earbuds"]))[0]   # text -> image search (CLIP)
    for i, s in top_k(q, index):
        print(files[i].name, round(s, 3))


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError
import io
import asyncio
import numpy as np
from sentence_transformers import SentenceTransformer

app = FastAPI()
model = SentenceTransformer("clip-ViT-B-32")        # loaded once at startup
INDEX: np.ndarray = np.zeros((0, 512), dtype=np.float32)   # fill from your DB
IDS: list[str] = []


@app.post("/search/image")
async def search_image(file: UploadFile = File(...), k: int = 5) -> list[dict[str, float | str]]:
    data = await file.read()
    if len(data) > 5_000_000:                        # basic size guard (5 MB)
        raise HTTPException(413, "image too large")
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(422, "not a valid image")
    vec = await asyncio.to_thread(model.encode, [img], normalize_embeddings=True)
    if len(IDS) == 0:
        return []
    scores = INDEX @ vec[0]
    return [{"id": IDS[i], "score": float(scores[i])} for i in np.argsort(-scores)[:k]]
```
(Needs `python-multipart` installed for uploads.)

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_experimental.open_clip import OpenCLIPEmbeddings   # pip install langchain-experimental open_clip_torch

clip = OpenCLIPEmbeddings(model_name="ViT-B-32", checkpoint="laion2b_s34b_b79k")
img_vecs = clip.embed_image(["images/a.jpg", "images/b.jpg"])     # image paths
txt_vec = clip.embed_query("wireless earbuds")
```
These work with Chroma (`add_images`) for multimodal retrieval. In LangGraph, an "image analysis" node can embed the uploaded photo, retrieve similar items, and pass their HS codes to an LLM node for the final answer. (The experimental class API may change; check the current docs.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Comparing image vectors from different models
✅ Correct: One model for all images and queries.

```python
# Wrong: index built with ResNet, query embedded with CLIP
# Right: same model both sides
```

❌ Mistake 2: Skipping resize/normalisation
✅ Correct: Use the model's own preprocessing (processor/transform); libraries do this for you.

❌ Mistake 3: Using image vectors for exact matching or OCR-style tasks
✅ Correct: Images that differ only by small text (e.g. a serial number) look the same to CLIP. Use OCR + metadata.

---

## 🧠 Tricky Interview Question

**Q**: "Two photos of different electronics (a charger and a power bank) from the same angle on a white background score 0.95, while two photos of the same charger from different angles score 0.80. Why and what do you do?"

**Answer**: General vision models weigh composition, colour, and background heavily, so look-alike scenes cluster together. Remedies: crop/segment the product (remove background), embed multiple views and aggregate, use a domain fine-tuned model, combine with text embeddings of titles, add metadata filters (category), and re-rank with a classifier or an LLM with vision.

---

## ⚫ Interview Questions + Answers

Q1: What is an image embedding?
A1: A numeric vector produced by a vision model that represents the image content.

Q2: Which model is popular for image and text in one space?
A2: CLIP (OpenAI), plus open versions like OpenCLIP and SigLIP.

Q3: What similarity metric do you use?
A3: Cosine similarity (or dot product on normalised vectors).

Q4: Why store the image file separately from the vector?
A4: Vector DBs store vectors and small metadata; images belong in object storage (S3), with the URL as metadata.

Q5: How do you scale image search to 100M images?
A5: Batch embed on GPUs, store 512-d vectors (quantised) in an ANN index (HNSW/IVF-PQ), shard, store images in S3/CDN, precompute thumbnails, filter by metadata, re-rank top results with a heavier model, and monitor recall using a labelled set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Visual similarity search, de-duplication, recommendations
- Captions or tags are missing

❌ Avoid when:
- Text in the image matters (use OCR)
- Fine-grained differences (counts, small labels) decide the answer

---

## 📊 Visual Diagram
```
 photo.jpg ─► resize 224x224 ─► vision encoder (ViT) ─► [0.12, -0.4, ... 512 numbers]
                                                            │ normalise
                                                            ▼
                                             vector DB ◄─ nearest neighbours
 text "earbuds" ─► CLIP text encoder ─► same 512-d space (CLIP only)
```

---

## 💰 Cost Impact
Local CLIP is free per call but needs a GPU (a GPU can embed hundreds of images per second). Hosted multimodal APIs (Cohere embed v4, Voyage multimodal) charge per image/pixel or token; check the current pricing. Storage: 512 floats x 4 B = 2 KB per image; 10M images = 20 GB. Optimise by embedding thumbnails (smaller), caching by file hash, and de-duplicating before embedding. No LLM tokens are used unless you add a vision LLM step (which is billed per image tokens).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Image embedding | Vector of an image | Image का vector |
| CLIP | Joint image-text model | Image और text का joint model |
| ViT | Vision Transformer | Vision Transformer |
| Near-duplicate | Almost same image | लगभग वही image |
| Thumbnail | Small preview | छोटी preview image |
| Re-rank | Re-order results | Results का दोबारा क्रम |

---

## ⚡ 3-Line Summary
English: Vision models convert pictures into vectors so similar images are close. CLIP also maps text into the same space. Use the same model for index and query, and use OCR for text in images.
Hindi: Vision models तस्वीरों को vectors में बदलते हैं ताकि similar images पास रहें। CLIP text को भी उसी space में रखता है। Index और query में same model रखो, और images में text के लिए OCR use करो।

---

## ➡️ Next Topic
**119. Multimodal Embeddings** - one space for text, images (and more) with hosted and open models.
