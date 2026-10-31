---

# 124. Fine-tuned Embeddings
# हिंदी में: Fine-tuned Embeddings (अपने domain के लिए embedding model को train करना)

---

## 🔵 Simple Definition (English)
Fine-tuning an embedding model means taking a pre-trained model (like `all-MiniLM-L6-v2` or `bge-base`) and training it a little more on YOUR domain pairs (query, relevant document). After training, texts that mean the same thing in your domain land closer together in vector space. It is used when generic embeddings fail on specialised jargon.

## 🔵 सरल परिभाषा (Hindi)
Embedding model को fine-tune करने का मतलब है एक pre-trained model (जैसे `bge-base`) को अपने domain के (query, relevant document) pairs पर थोड़ा और train करना। इसके बाद आपके domain में जिन texts का मतलब एक जैसा है वो vector space में पास आ जाते हैं। जब generic embeddings specialised jargon पर fail होते हैं, तब यह use होता है।

---

## 🔴 Problem it Solves
Generic embedding models are trained on web text. They do not know that "HS 8517.13" means "smartphones", or that "CIF" and "Cost Insurance Freight" are the same. Retrieval returns wrong chunks, and the RAG answer is wrong even though the LLM is fine. Prompt tricks cannot fix a bad retriever. Fine-tuning teaches the embedding space your vocabulary and what "relevant" means for your users.

## 🔴 यह क्यों बना? (Hindi)
Generic models web text पर train होते हैं। उन्हें नहीं पता कि "HS 8517.13" का मतलब smartphones है। Retrieval गलत chunks लाता है और RAG का answer गलत हो जाता है, चाहे LLM अच्छा हो। Prompt से bad retriever ठीक नहीं होता। Fine-tuning embedding space को आपकी vocabulary सिखाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect (query, positive_passage) pairs from logs / experts / LLM-generated synthetic queries
Step 2 → Mine hard negatives (passages that look similar but are WRONG) with the base model
Step 3 → Split train / validation (keep a held-out retrieval eval set, e.g. 20%)
Step 4 → Pick a loss: MultipleNegativesRankingLoss (in-batch negatives) is the common default
Step 5 → Train 1-3 epochs with a small learning rate (e.g. 2e-5) so the model does not forget
Step 6 → Evaluate Recall@k / MRR / nDCG on held-out set vs the base model
Step 7 → Re-embed the ENTIRE corpus with the new model (old vectors are incompatible!)
Step 8 → Deploy new model + new index together, version both
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → (query, सही passage) pairs इकट्ठा करो - logs, experts या LLM से synthetic queries
Step 2 → Hard negatives निकालो (दिखने में similar पर गलत passages)
Step 3 → Train / validation split करो (20% held-out eval set)
Step 4 → Loss चुनो: MultipleNegativesRankingLoss (सबसे common default)
Step 5 → 1-3 epochs, छोटा learning rate (2e-5) ताकि model पुराना knowledge न भूले
Step 6 → Base model से Recall@k / MRR / nDCG compare करो
Step 7 → पूरे corpus को नए model से दोबारा embed करो (पुराने vectors compatible नहीं हैं)
Step 8 → नया model + नया index साथ में deploy करो, दोनों को version करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Users type "mobile charger 20W USB-C" but the tariff schedule says "Static converters, other, 8504.40". The generic model scores this pair low. We build 5,000 pairs from past classifications (product description -> correct HS heading chapter text) and fine-tune. Recall@5 on the held-out set goes from 0.62 to 0.84, so the classifier sees the right heading in its context far more often.

**Zomato AI**: "something light, not oily" must match dishes tagged "steamed, grilled, low-calorie". Click logs (search query -> dish ordered) give free training pairs.

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "mobile charger 20W USB-C" पर tariff schedule में "Static converters, 8504.40" लिखा है। Generic model इन्हें दूर रखता है। हमने पुराने classifications से 5,000 pairs बनाए और fine-tune किया। Held-out Recall@5 0.62 से 0.84 हुआ। **Zomato**: "हल्का, तेल कम" query को steamed/grilled dishes से match करना है, click logs से free training pairs मिलते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: pure-Python demo of WHY fine-tuning helps (no libraries needed, runs offline)
import math                                    # math for sqrt in cosine similarity
from typing import Dict, List                  # type hints for clarity

Vector = List[float]                           # a vector is a list of floats

def cosine(a: Vector, b: Vector) -> float:
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))     # dot product
    na = math.sqrt(sum(x * x for x in a))      # length of a
    nb = math.sqrt(sum(y * y for y in b))      # length of b
    if na == 0 or nb == 0:                     # guard against division by zero
        return 0.0                             # zero vector has no direction
    return dot / (na * nb)                     # standard cosine formula

# Toy 3-D "base model" space: dims = [electronics, food, legal]
base: Dict[str, Vector] = {
    "mobile charger 20W": [0.50, 0.40, 0.10],  # generic model is confused (food-ish?)
    "static converters 8504.40": [0.10, 0.10, 0.90],  # jargon looks like "legal"
}
# Same texts after fine-tuning on tariff pairs: both moved into electronics
tuned: Dict[str, Vector] = {
    "mobile charger 20W": [0.90, 0.05, 0.05],  # now clearly electronics
    "static converters 8504.40": [0.85, 0.02, 0.13],  # jargon pulled close
}

q, d = "mobile charger 20W", "static converters 8504.40"   # query and relevant doc
print("base :", round(cosine(base[q], base[d]), 3))         # low similarity
print("tuned:", round(cosine(tuned[q], tuned[d]), 3))       # high similarity
```

## 💻 Code Example — Advanced
```python
# Advanced: fine-tune with sentence-transformers (pip install sentence-transformers datasets)
# Uses the classic model.fit API, which works on sentence-transformers v2 and v3.
import asyncio                                         # async wrapper for FastAPI use
import logging                                         # log failures instead of print
from typing import List, Tuple                         # type hints

from sentence_transformers import InputExample, SentenceTransformer, losses  # core classes
from sentence_transformers.evaluation import InformationRetrievalEvaluator   # retrieval metric
from torch.utils.data import DataLoader                # batches the training pairs

logger = logging.getLogger("embed_ft")                 # module logger

def build_examples(pairs: List[Tuple[str, str]]) -> List[InputExample]:
    """Turn (query, positive) tuples into InputExample objects."""
    return [InputExample(texts=[q, p]) for q, p in pairs]   # MNRL needs [anchor, positive]

def finetune(
    pairs: List[Tuple[str, str]],                      # training pairs
    base_model: str = "BAAI/bge-small-en-v1.5",        # small + good base model
    out_dir: str = "tariff-embed-v1",                  # where to save the result
    epochs: int = 2,                                   # few epochs avoid forgetting
    batch_size: int = 32,                              # bigger batch = more in-batch negatives
) -> str:
    """Fine-tune and save. Returns the output directory."""
    if len(pairs) < 100:                               # too little data hurts quality
        raise ValueError("Need at least ~100 pairs; use synthetic data generation")
    try:
        model = SentenceTransformer(base_model)        # load the pre-trained model
        loader = DataLoader(build_examples(pairs), shuffle=True, batch_size=batch_size)  # batching
        loss = losses.MultipleNegativesRankingLoss(model)  # other batch items act as negatives
        model.fit(                                     # run training
            train_objectives=[(loader, loss)],         # data + loss
            epochs=epochs,                             # number of passes
            warmup_steps=int(0.1 * len(loader)),       # gentle LR warmup
            optimizer_params={"lr": 2e-5},             # small LR
            show_progress_bar=False,                   # quiet logs
        )
        model.save(out_dir)                            # persist the tuned model
        return out_dir                                 # caller loads it later
    except Exception as exc:                           # catch OOM, bad data, etc.
        logger.exception("fine-tune failed: %s", exc)  # log full traceback
        raise                                          # let the caller decide

def evaluate(model_dir: str, queries: dict, corpus: dict, relevant: dict) -> float:
    """Return the evaluator score (MAP/nDCG family) for a model on held-out data."""
    model = SentenceTransformer(model_dir)             # load model to test
    ev = InformationRetrievalEvaluator(queries, corpus, relevant)  # id->text, id->text, id->set(ids)
    return float(ev(model))                            # score (higher is better)

async def finetune_async(pairs: List[Tuple[str, str]]) -> str:
    """Training is CPU/GPU blocking, so run it in a worker thread."""
    return await asyncio.to_thread(finetune, pairs)    # keeps the event loop free

# Token usage: local fine-tuning uses 0 API tokens. Synthetic query generation with an LLM
# costs ~150 input + 30 output tokens per chunk (see Cost Impact).
```

---

## 🟠 FastAPI Integration
Serve the fine-tuned model behind an `/embed` route and start training as a background job (never inside a request).

```python
from fastapi import BackgroundTasks, FastAPI, HTTPException   # FastAPI core
from pydantic import BaseModel                                 # request validation (pydantic v2)
from sentence_transformers import SentenceTransformer          # load the tuned model

app = FastAPI()                                                # the app
MODEL_DIR = "tariff-embed-v1"                                  # versioned model folder
model: SentenceTransformer | None = None                       # loaded lazily

class EmbedRequest(BaseModel):                                 # input schema
    texts: list[str]                                           # texts to embed

@app.on_event("startup")                                       # load once at start
def load_model() -> None:
    global model                                               # assign module-level variable
    model = SentenceTransformer(MODEL_DIR)                     # heavy, so do it once

@app.post("/embed")                                            # embedding endpoint
async def embed(req: EmbedRequest) -> dict:
    if model is None:                                          # model failed to load
        raise HTTPException(503, "model not ready")            # service unavailable
    vecs = model.encode(req.texts, normalize_embeddings=True)  # unit vectors for cosine
    return {"model": MODEL_DIR, "vectors": vecs.tolist()}      # return version with vectors

@app.post("/train")                                            # trigger training job
async def train(bg: BackgroundTasks) -> dict:
    bg.add_task(print, "training would start here")            # replace with finetune()
    return {"status": "started"}                               # return immediately
```

---

## 🔗 LangChain / LangGraph Connection
A fine-tuned model plugs into LangChain through `HuggingFaceEmbeddings` (package `langchain-huggingface`). Everything downstream (vector stores, retrievers, LangGraph retrieval nodes) works unchanged.

```python
from langchain_huggingface import HuggingFaceEmbeddings        # wrapper for sentence-transformers

emb = HuggingFaceEmbeddings(                                   # build embedding object
    model_name="tariff-embed-v1",                              # local fine-tuned folder
    encode_kwargs={"normalize_embeddings": True},              # unit vectors
)
vec = emb.embed_query("mobile charger 20W")                    # one query vector
docs = emb.embed_documents(["Static converters 8504.40"])      # list of document vectors
# In LangGraph: a "retrieve" node calls vectorstore.as_retriever() built with `emb`.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fine-tuning, then querying an OLD index with the NEW model
✅ Correct: re-embed the whole corpus and rebuild the index.

```python
# Wrong: new model for queries, old vectors in the index -> garbage similarity
q = new_model.encode("charger")
index.query(vector=q.tolist(), top_k=5)    # index holds base-model vectors!

# Right: re-embed everything with the same model, store model version in metadata
docs_vecs = new_model.encode(all_docs, normalize_embeddings=True)
index_v2.upsert([(str(i), v.tolist(), {"model": "tariff-embed-v1"}) for i, v in enumerate(docs_vecs)])
```

❌ Mistake 2: No held-out evaluation (you cannot tell if it improved)
✅ Correct: always compare Recall@k of base vs tuned on unseen queries.

```python
# Wrong: "loss went down, so it must be better"
# Right:
base_score = evaluate("BAAI/bge-small-en-v1.5", queries, corpus, relevant)
tuned_score = evaluate("tariff-embed-v1", queries, corpus, relevant)
assert tuned_score > base_score, "fine-tune did not help; keep the base model"
```

---

## 🧠 Tricky Interview Question

**Q**: "You fine-tuned your embedding model. Offline Recall@5 improved from 0.62 to 0.84, but after deployment overall answer quality dropped for general queries. Why?"

**Answer**: Catastrophic forgetting / narrow overfitting. The model got better at tariff jargon and worse at general language, and the held-out set only had tariff queries. Also check for deployment bugs (old index, mixed model versions). Fixes: use a lower LR and fewer epochs, mix in general data, evaluate on both domain and general sets, or combine fine-tuned dense search with BM25 hybrid search as a safety net.

---

## ⚫ Interview Questions + Answers

Q1: What is fine-tuning an embedding model?
A1: Continuing training of a pre-trained embedding model on domain (query, positive) pairs so relevant texts get higher cosine similarity.

Q2: Why must you re-embed all documents after fine-tuning?
A2: Vectors from different models live in different spaces. Mixing them makes similarity scores meaningless, so the whole index must be rebuilt with the new model.

Q3: What is MultipleNegativesRankingLoss and why is it popular?
A3: For each (query, positive) in a batch, all other positives in the batch are treated as negatives. You only need positive pairs, no labelled negatives, and larger batches give better training signal.

Q4: How do you get training data if you have no labels?
A4: Use click or accept logs, expert-labelled classifications, or generate synthetic queries with an LLM for each chunk ("write 3 questions this chunk answers"), then filter low-quality ones.

Q5: When is fine-tuning NOT worth it compared with hybrid search or a better base model?
A5: If a stronger base model or BM25 hybrid search already reaches the target recall, skip it. Fine-tuning adds a retraining pipeline, versioning, re-indexing and drift monitoring. It pays off when jargon is heavy, you have 1k+ good pairs, and the recall gap is measurable. Always try cheap fixes first (better chunking, query rewriting, hybrid search, a bigger model).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Domain jargon, codes or abbreviations that generic models miss
- You have at least ~1,000 quality (query, passage) pairs
- Measured retrieval recall is the bottleneck of RAG quality

❌ Avoid when:
- Data is tiny or noisy
- Hybrid search or a stronger off-the-shelf model already works
- Corpus changes every day and you cannot afford constant re-embedding

---

## 📊 Visual Diagram
```
 (query, positive) pairs + hard negatives
              │
              ▼
   ┌──────────────────────┐   train 1-3 epochs, lr 2e-5
   │ Base embedding model │ ─────────────────────────────┐
   └──────────────────────┘                              ▼
                                              ┌────────────────────┐
   Eval: Recall@5 base 0.62  ◄──compare──►    │ Fine-tuned model   │ Recall@5 0.84
                                              └─────────┬──────────┘
                                                        ▼
                                   Re-embed ALL docs -> new index (versioned)
```

---

## 💰 Cost Impact
- Training itself: local GPU, no per-token API cost (a small model on 5k pairs takes minutes on one GPU).
- Synthetic data via LLM: 10,000 chunks x (~300 input + ~100 output tokens) = 3M input + 1M output tokens. On gpt-4o-mini ($0.15 / $0.60 per 1M) that is about $0.45 + $0.60 = ~$1.05.
- Re-embedding: 1M chunks x 300 tokens = 300M tokens. At $0.02 per 1M (text-embedding-3-small) = $6. With a self-hosted tuned model, API cost is $0 (you pay GPU time).
- Optimisation: use a small base model (384-768 dims) to cut vector storage and query latency; cache embeddings; re-embed only changed documents.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fine-tuning | Extra training on domain data | Domain data पर अतिरिक्त training |
| Hard negative | Similar-looking but wrong passage | देखने में सही पर गलत passage |
| In-batch negatives | Other items in the batch used as negatives | Batch के बाकी items को negative मानना |
| MNRL | MultipleNegativesRankingLoss | Contrastive loss function |
| Recall@k | Share of queries whose answer is in top k | Top k में सही answer मिलने की दर |
| Catastrophic forgetting | Model loses general ability | General knowledge भूल जाना |
| Re-embedding | Recompute all vectors with the new model | सभी vectors दोबारा बनाना |

---

## ⚡ 3-Line Summary
English: Fine-tuning adapts an embedding model to your domain with (query, positive) pairs. Always evaluate on held-out data and re-embed the whole corpus with the new model. Try hybrid search and better base models first.
Hindi: Fine-tuning embedding model को आपके domain के हिसाब से ढालता है। Held-out data पर evaluate करो और पूरे corpus को नए model से दोबारा embed करो। पहले hybrid search और बेहतर base model आज़माओ।

---

## ➡️ Next Topic
**125. Embedding Best Practices** — chunking, normalisation, model/version management and the checklist that avoids most retrieval bugs.
