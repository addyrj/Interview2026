---

# RAG Cheatsheet — Embeddings, Vector DBs, Chunking, RAG Pipeline (Quick Revision)
# हिंदी में: RAG का Quick Revision (Phases 04-07)

Condensed from topics 101-230: embeddings, vector databases, chunking, RAG pipeline. Each topic: gist, one key code line, Hindi hint.
> Prices, model names and IDs shown in the source notes are illustrative; always verify on the provider's official pricing/model pages.

---

## Phase 04 — Embeddings (101-125)

- **101 What are Embeddings** — Embeddings convert text meaning into dense vectors — similar meanings are close in vector space, enabling semantic search that finds "smartphone" when you have "mobile telephone" in your documents.
  `client = AsyncOpenAI()` · हिंदी: Embeddings text की meaning को vectors में convert करते हैं — similar meanings close होते हैं।
- **102 Why Embeddings Work** — Embeddings work because models learn that similar contexts mean similar meanings and encode this as closeness in vector space. Cosine similarity then finds related text even without shared words.
  `cooc: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))` · हिंदी: Embeddings इसलिए काम करते हैं क्योंकि models सीखते हैं कि समान context का मतलब समान अर्थ है और इसे vector space की नज़दीकी में encode करते…
- **103 Vector Space — Visual Explanation** — Every text becomes a point in high-dimensional space where distance and angle mean similarity. Normalise vectors, use cosine/dot product and ANN indexes for speed. 2D plots help intuition but do not replace real metrics.
  `query = (0.92, 0.08)` · हिंदी: हर text high-dimensional space का एक point बनता है जहाँ दूरी और angle का मतलब समानता है।
- **104 Cosine Similarity — Complete Guide** — Cosine similarity compares the direction of two embedding vectors and ignores their length. Scores are relative, not probabilities, so tune thresholds with real data. With normalised vectors it equals a dot product, which is faster.
  हिंदी: Cosine similarity दो embedding vectors की direction compare करती है, length नहीं।
- **105 Euclidean Distance — Complete Guide** — Euclidean distance is the straight-line distance between vectors; smaller means closer. It reacts to length, so for unit vectors it ranks the same as cosine. Use it for clustering and L2-based indexes.
  `v = [math.sqrt(0.5), math.sqrt(0.5)]` · हिंदी: Euclidean distance vectors के बीच की सीधी दूरी है; कम = ज़्यादा close।
- **106 Dot Product Similarity — Complete Guide** — Dot product multiplies and sums vector elements; bigger means more similar. With normalised vectors it is exactly cosine, but faster. Use it when vectors are normalised or when magnitude matters.
  हिंदी: Dot product vectors के elements को multiply करके जोड़ता है; बड़ा = ज़्यादा similar। Normalised vectors में यह cosine ही है, पर तेज़।
- **107 OpenAI Embeddings API — Complete Guide** — `client.embeddings.create` converts strings to vectors; batch many inputs per call. You pay per input token only, and queries must use the same model as documents. Add retries, caching, and store the model name.
  `vec: list[float] = embed_one('Wireless earbuds with charging case')` · हिंदी: `client.embeddings.create` strings को vectors में बदलता है; एक call में कई inputs भेजो।
- **108 text-embedding-3-small vs large — Complete Guide** — Small is cheap and good enough for most tasks; large is stronger but 6.5x costlier. Both can be shortened with `dimensions`. Decide with a measured eval, not by guessing.
  `SMALL = EmbModel('text-embedding-3-small', 1536, 0.02)` · हिंदी: Small सस्ता है और ज़्यादातर tasks के लिए काफी; large ज़्यादा strong पर 6.5x महँगा। दोनों को `dimensions` से छोटा कर सकते हैं।
- **109 Embedding Dimensions — Complete Guide** — Dimension is the vector length; it sets memory, storage, and search cost, not API price. Shorten only models that support it and re-normalise. Pick the knee of the recall-vs-size curve.
  `short = truncate_and_normalise(demo, 2)` · हिंदी: Dimension vector की length है; यह memory, storage और search cost तय करती है, API price नहीं।
- **110 Anthropic Embeddings — Complete Guide** — Anthropic has no embedding endpoint; use Voyage AI (recommended) or any other provider. Use `input_type` correctly and keep one model for queries and documents. Claude only sees the retrieved text, not the vectors.
  `docs = embed(['Headphones and earphones', 'Coffee, not roasted'], 'document')` · हिंदी: Anthropic का embedding endpoint नहीं है; Voyage AI (recommended) या कोई और provider use करो।
- **111 Cohere Embeddings — Complete Guide** — Cohere Embed handles many languages and needs `input_type`. Batch at most 96 texts and consider int8/binary vectors for storage. Add a reranker for precision.
  `vecs = embed(['Headphones', 'Static converters'], 'search_document')` · हिंदी: Cohere Embed कई भाषाओं को handle करता है और `input_type` माँगता है। एक call में अधिकतम 96 texts, और storage के लिए int8/binary सोचो।
- **112 Sentence Transformers (local embeddings) — Complete Guide** — sentence-transformers runs embedding models locally; no API cost and full privacy. Load the model once, normalise vectors, and keep blocking encode off the async event loop. Watch the max sequence length.
  `model = load_model()` · हिंदी: sentence-transformers embedding models को locally चलाता है; API cost नहीं, पूरी privacy।
- **113 Hugging Face Embeddings — Complete Guide** — Hugging Face gives access to many open embedding models usable via transformers, sentence-transformers, or TEI. Follow the model card for pooling and prefixes, and pick by your own eval. Self-hosting trades API fees for infra work.
  हिंदी: Hugging Face कई open embedding models देता है जिन्हें transformers, sentence-transformers या TEI से use कर सकते हैं।
- **114 Embedding Cost Optimization — Complete Guide** — Embedding cost falls with dedupe, caching, incremental updates, cheaper models, smaller vectors, and the Batch API. Measure tokens first and validate recall after each cut. The vector DB and LLM often cost more than embedding calls.
  हिंदी: Dedupe, caching, incremental updates, सस्ते models, छोटे vectors और Batch API से embedding cost घटती है।
- **115 Embedding Caching — Complete Guide** — Cache embeddings by hash(model+dims+text) so repeats cost nothing. Batch the misses and keep order. Always include the model in the key to avoid mixing vector spaces.
  `ce = CachedEmbedder(fake_embed, 'fake-v1')` · हिंदी: Embeddings को hash(model+dims+text) से cache करो ताकि repeats मुफ्त हों। Misses को batch करो और क्रम रखो।
- **116 Batch Embedding — Complete Guide** — Send many texts per request, cap concurrency, retry with backoff, and map results by index. Use the Batch API for 50% savings on offline loads. Checkpoint progress so jobs can resume.
  `T = TypeVar('T')` · हिंदी: एक request में कई texts भेजो, concurrency सीमित करो, backoff के साथ retry करो और index से results map करो।
- **117 Embedding for Different Data Types — Complete Guide** — Turn every data type into clean, meaningful text before embedding, and chunk it. Keep exact values and IDs as metadata filters. Evaluate each data type separately.
  हिंदी: Embed करने से पहले हर data type को साफ, अर्थपूर्ण text में बदलो और chunk करो। Exact values और IDs को metadata filters में रखो।
- **118 Image Embeddings Basics — Complete Guide** — Vision models convert pictures into vectors so similar images are close. CLIP also maps text into the same space. Use the same model for index and query, and use OCR for text in images.
  `red = [(250, 10, 10)] * 100` · हिंदी: Vision models तस्वीरों को vectors में बदलते हैं ताकि similar images पास रहें। CLIP text को भी उसी space में रखता है।
- **119 Multimodal Embeddings — Complete Guide** — Multimodal embeddings put text and images in one space for cross-modal search. Rank matters more than absolute score because of the modality gap. Combine with OCR for text-heavy pages and a vision LLM for final answers.
  हिंदी: Multimodal embeddings text और images को एक space में रखते हैं ताकि cross-modal search हो सके।
- **120 Embedding Evaluation — Complete Guide** — Evaluate embeddings with a labelled query set and metrics like recall@k, MRR, and nDCG. Compare models, dimensions and chunking by numbers, per segment. Freeze a golden set and run it on every change.
  हिंदी: Labelled query set और recall@k, MRR, nDCG जैसे metrics से embeddings evaluate करो।
- **121 Semantic Search — Complete Guide** — Semantic search embeds the query and finds the nearest document vectors, matching meaning rather than words. Use the same model both sides, add a score threshold, and rerank for precision. Combine with keyword search for exact identifiers.
  `index = [(d, embed(d)) for d in docs]` · हिंदी: Semantic search query को embed करके सबसे पास के document vectors ढूँढता है; शब्द नहीं, meaning match होता है।
- **122 Semantic vs Keyword Search — Complete Guide** — Keyword search matches exact words; semantic search matches meaning. Each fails where the other is strong, so hybrid search with rank fusion is the production default. Tune and evaluate by query type.
  `kw, sem = (ranking(bm25(q, DOCS)), ranking(semantic(q, DOCS)))` · हिंदी: Keyword search exact शब्द match करता है; semantic search meaning।
- **123 Embedding Drift — Complete Guide** — Drift is silent decay of retrieval quality from changing data, queries, or models. Store model metadata, monitor a golden set and score trends, and never mix versions in an index. Fix with incremental re-embedding or a blue/green migration.
  हिंदी: Drift बदलते data, queries या models से retrieval quality का चुपचाप गिरना है।
- **124 Fine-tuned Embeddings** — Fine-tuning adapts an embedding model to your domain with (query, positive) pairs. Always evaluate on held-out data and re-embed the whole corpus with the new model. Try hybrid search and better base models first.
  `q, d = ('mobile charger 20W', 'static converters 8504.40')` · हिंदी: Fine-tuning embedding model को आपके domain के हिसाब से ढालता है।
- **125 Embedding Best Practices** — Chunk small, normalise, batch, cache by content hash and store the model version with every vector. Never mix models in one index. Measure Recall@k on a golden set before and after every change.
  `chunks = chunk_words('static converters other than ... ' * 20, size=10, overlap=2)` · हिंदी: छोटे chunks बनाओ, normalise करो, batch और cache करो, और हर vector के साथ model version रखो। एक index में कभी अलग models मत मिलाओ।

**Key snippet — 101 What are Embeddings**
```python
client = AsyncOpenAI()
async def get_embedding(text: str, model: str='text-embedding-3-small') -> list[float]:
    """Get embedding vector for a single text."""
    text = text.replace('\n', ' ').strip()
    response = await client.embeddings.create(model=model, input=text)
    return response.data[0].embedding
```

**Key snippet — 108 text-embedding-3-small vs large — Complete Guide**
```python
@dataclass(frozen=True)
class EmbModel:
    name: str
    dims: int
    price_per_m: float
```

**Key snippet — 116 Batch Embedding — Complete Guide**
```python
T = TypeVar('T')
def batched(items: list[T], size: int) -> Iterator[list[T]]:
    """Yield consecutive slices of `size` items."""
    if size <= 0:
        raise ValueError('size must be positive')
    for i in range(0, len(items), size):
        yield items[i:i + size]
```

---

## Phase 05 — Vector Databases (126-155)

- **126 Vector Database — What + Why** — A vector database stores embeddings and finds the most similar ones fast using ANN indexes. It adds filtering, persistence and scale that brute force cannot. It is the retrieval engine of RAG.
  `db = TinyVectorDB()` · हिंदी: Vector database embeddings store करता है और ANN indexes से सबसे similar vectors तेज़ी से ढूँढता है।
- **127 How Vector Search Works** — Vector search embeds the query, scores it against stored vectors with cosine, dot or L2, and returns the top-k. Pre-filter by metadata and rerank for precision. Always use the same model and a consistent metric.
  हिंदी: Vector search query को embed करके stored vectors से cosine, dot या L2 से score करता है और top-k लौटाता है।
- **128 ANN — Approximate Nearest Neighbor** — ANN finds almost-the-closest vectors by checking only a small candidate set. You trade a little recall for massive speed and cost savings. Always measure recall against brute force and tune the knobs.
  `random.seed(7)` · हिंदी: ANN सिर्फ़ छोटे candidate set को check करके लगभग सबसे पास वाले vectors ढूँढता है। थोड़ा recall देकर बहुत speed और cost बचत मिलती है।
- **129 HNSW Algorithm** — HNSW is a layered proximity graph: coarse jumps at the top, fine search at the bottom. Tune M, efConstruction and ef_search for the recall/latency/memory balance. It is the default, high-recall ANN index but costs RAM.
  `random.seed(1)` · हिंदी: HNSW layers वाला proximity graph है: ऊपर बड़ी छलाँगें, नीचे बारीक search।
- **130 IVF Algorithm** — IVF clusters vectors with k-means and searches only the nprobe nearest clusters. It builds fast and, with PQ, uses very little memory. Tune nlist and nprobe, and retrain when data drifts.
  `random.seed(3)` · हिंदी: IVF vectors को k-means से clusters में बाँटता है और सिर्फ़ nprobe सबसे पास वाले clusters में search करता है।
- **131 Pinecone — Complete Guide** — Pinecone is a managed vector DB: create an index, upsert vectors with metadata, query top-k with filters. Namespaces isolate tenants; serverless removes capacity planning.
  `res = index.query(vector=[1.0, 0.0, 0.1, 0.0], top_k=1, include_metadata=True)` · हिंदी: Pinecone managed vector DB है: index बनाओ, metadata के साथ vectors upsert करो, filters के साथ top-k query करो।
- **132 Pinecone Index Setup** — Create indexes with the exact dimension and metric your embedding model needs; they cannot be changed later. Provision idempotently, wait for readiness and version index names. Use namespaces, not extra indexes, for tenants.
  `cfg = IndexConfig(name='tariff-hs-te3s-v1', model='text-embedding-3-small')` · हिंदी: Index को embedding model के सही dimension और metric के साथ बनाओ; ये बाद में नहीं बदलते।
- **133 Pinecone Upsert + Query** — Upsert vectors in batches of about 100 with stable ids; query with top_k, filters and include_metadata. Handle retries and stale chunks (delete old ids). Apply a score threshold before sending context to the LLM.
  हिंदी: Vectors को ~100 के batches में stable ids के साथ upsert करो; top_k, filters और include_metadata के साथ query करो।
- **134 Pinecone Metadata Filtering** — Attach flat metadata to vectors and pass a filter (`$eq`, `$in`, `$and`, ...) to the query so results obey business rules. Build filters with a typed model and always inject tenant scope on the server. Never post-filter after top_k.
  हिंदी: Vectors के साथ flat metadata जोड़ो और query में filter (`$eq`, `$in`, `$and`, ...) दो ताकि results business rules मानें।
- **135 Pinecone Namespaces** — Namespaces partition one index into isolated groups; every operation targets one namespace. They give safe multi-tenancy, cheaper scoped reads and one-call deletion.
  `s = NamespacedStore()` · हिंदी: Namespaces एक index को isolated groups में बाँटते हैं; हर operation एक namespace पर चलता है।
- **136 Pinecone Serverless vs Pod** — Serverless bills storage and usage and scales automatically; pods reserve hardware and bill hourly. Start with serverless, measure, and move to pods only if steady heavy traffic makes it cheaper or faster.
  हिंदी: Serverless storage और usage का bill देता है और अपने-आप scale होता है; pods hardware reserve करके घंटे के हिसाब से bill देते हैं।
- **137 Weaviate Basics** — Weaviate is an open-source, schema-based vector database with HNSW, BM25 and hybrid search plus filters. Create a collection, insert objects with vectors, query with near_vector, bm25 or hybrid, and always close the client.
  `client = weaviate.connect_to_local()` · हिंदी: Weaviate open-source, schema-based vector database है जिसमें HNSW, BM25, hybrid search और filters हैं।
- **138 Qdrant Basics** — Qdrant stores points (id, vector, payload) in collections and searches with HNSW plus fast payload filters. Use `:memory:` for tests, payload indexes for filtered fields and `query_points` for search. Quantisation and on-disk vectors control memory.
  `client = QdrantClient(':memory:')` · हिंदी: Qdrant collections में points (id, vector, payload) रखता है और HNSW व तेज़ payload filters से search करता है।
- **139 Chroma DB — Complete Guide** — Chroma is the easiest vector database: create a collection, add documents with metadata, query with filters. Use PersistentClient for disk storage and set cosine distance at creation. Great for prototypes; plan to migrate for heavy production use.
  `client = chromadb.Client()` · हिंदी: Chroma सबसे आसान vector database है: collection बनाओ, metadata के साथ documents add करो, filters के साथ query करो।
- **140 Chroma — Local + Cloud** — Chroma runs in memory, on local disk, as a server, or in the cloud, with the same collection API. Use server mode (HttpClient) when several workers share data, mount a volume, and choose the mode from configuration.
  हिंदी: Chroma memory, local disk, server या cloud में चलता है, collection API वही रहती है।
- **141 FAISS — Complete Guide** — FAISS is a fast library, not a database: you manage vectors, ids and metadata yourself. Use float32, normalise for cosine, choose Flat for exact or IVF/HNSW/PQ for scale, and save indexes with write_index.
  `faiss.normalize_L2(xb)` · हिंदी: FAISS तेज़ library है, database नहीं: vectors, ids और metadata आप खुद संभालते हैं।
- **142 FAISS — Local Vector Search** — Local FAISS search = embed, build an index suited to your size, save it with a side file of texts and metadata, load at startup. Filter with over-fetch plus post-filtering and swap rebuilt indexes atomically.
  `xb = np.stack([embed(d['text']) for d in docs])` · हिंदी: Local FAISS search = embed करो, size के हिसाब से index बनाओ, texts और metadata की side file के साथ save करो और startup पर load करो।
- **143 pgvector — PostgreSQL Extension** — pgvector adds vector columns, distance operators and HNSW/IVFFlat indexes to PostgreSQL, so semantic search becomes SQL with filters, joins and transactions. Match the index operator class to your query operator and tune ef_search or probes.
  `params = {'q': to_vector_literal([1.0, 0.0, 0.1, 0.0]), 'country': 'IN', 'k': 5}` · हिंदी: pgvector PostgreSQL में vector columns, distance operators और HNSW/IVFFlat indexes जोड़ता है, इसलिए semantic search filters, joins और trans…
- **144 pgvector Setup** — pgvector turns Postgres into a vector store with a `vector(n)` column and SQL distance operators. Match the dimension to the embedding model and the operator class to the query operator. Load data first, then build the HNSW index.
  हिंदी: pgvector Postgres को vector store बना देता है, `vector(n)` column और SQL operators के साथ।
- **145 pgvector Queries** — Use `ORDER BY embedding <=> q LIMIT k` with the operator that matches your index. Filters are applied after ANN candidates, so tune `ef_search` or use iterative scans. Convert distance to similarity only in SELECT.
  हिंदी: `ORDER BY embedding <=> q LIMIT k` index वाले operator के साथ use करो।
- **146 pgvector vs Pinecone** — pgvector is cheap and simple when you already use Postgres; Pinecone removes operations at huge scale. Decide with real vector counts, QPS and team size. Hide the backend behind an interface so you can switch.
  `store: VectorStore = InMemoryStore()` · हिंदी: Postgres पहले से है तो pgvector सस्ता और सरल है; बहुत बड़े scale पर Pinecone operations हटा देता है।
- **147 Redis as Vector DB** — Redis Stack can index float32 vectors with FLAT or HNSW and answer KNN queries in memory. It shines for semantic caching and low-latency retrieval. Mind RAM cost and tune thresholds carefully.
  `r = redis.Redis(host='localhost', port=6379)` · हिंदी: Redis Stack float32 vectors को FLAT या HNSW से index करके memory में KNN queries का जवाब देता है।
- **148 MongoDB Atlas Vector Search** — Atlas stores vectors inside documents and searches them with `$vectorSearch`. Declare filter fields in the index and set `numCandidates` well above `limit`. Indexing is asynchronous, so check index status.
  `client = MongoClient('mongodb+srv://USER:PASS@cluster0.example.mongodb.net')` · हिंदी: Atlas documents के अंदर vectors रखता है और `$vectorSearch` से search करता है।
- **149 Elasticsearch Vector Search** — Elasticsearch stores embeddings in `dense_vector` and runs HNSW kNN beside BM25. It is ideal for hybrid search with filters. Tune `num_candidates`, merge scores with RRF, and consider quantization.
  `es = Elasticsearch('http://localhost:9200')` · हिंदी: Elasticsearch `dense_vector` में embeddings रखकर BM25 के साथ HNSW kNN चलाता है। Filters के साथ hybrid search के लिए बढ़िया है।
- **150 Choosing Right Vector DB** — Pick the simplest vector DB that meets scale, latency, filter and budget needs. Start with what you already run and benchmark on your own data. Hide the choice behind an interface.
  हिंदी: वह सबसे सरल vector DB चुनो जो scale, latency, filter और budget की ज़रूरतें पूरी करे।
- **151 Vector DB Indexing Strategy** — FLAT is exact, IVF scans selected clusters, HNSW walks a graph; each trades recall, speed and memory. Use FLAT for small data and HNSW for most production search. Always measure recall against exact search.
  `random.seed(7)` · हिंदी: FLAT exact है, IVF चुने हुए clusters scan करता है, HNSW graph पर चलता है; हर एक recall, speed और memory में trade-off करता है।
- **152 Hybrid Search Setup** — Hybrid search merges keyword and vector rankings, typically with RRF. It fixes the weaknesses of each method alone. Index the same text in both and evaluate with labelled queries.
  हिंदी: Hybrid search keyword और vector rankings को आमतौर पर RRF से मिलाता है। यह दोनों तरीकों की अलग-अलग कमज़ोरियाँ दूर करता है।
- **153 Vector DB Performance** — Measure p95/p99 latency, QPS and recall@k against exact search before tuning. Find the real bottleneck across embedding, network, index and LLM. Tune one knob at a time and re-measure.
  `random.seed(1)` · हिंदी: Tuning से पहले p95/p99 latency, QPS और recall@k को exact search के मुक़ाबले नापो।
- **154 Vector DB Cost Optimization** — Vector cost = storage/RAM + compute + embedding tokens + LLM tokens. Reduce dimensions, quantize with rescoring, dedupe, embed incrementally and cache. Always monitor recall and cost together.
  `base = storage_gb(N, 3072, 4)` · हिंदी: Vector cost = storage/RAM + compute + embedding tokens + LLM tokens।
- **155 Vector DB Best Practices** — Use deterministic ids, store model and version metadata, and never mix embedding models. Enforce tenant filters server-side, handle updates and deletes, and keep an evaluation set in CI. Monitor recall, latency and cost together.
  `rec = ChunkRecord('tariff_2026.pdf', 12, 'Headphones fall under 8518.30', tenant_id='acme')` · हिंदी: Deterministic ids use करो, model और version metadata रखो, और embedding models कभी मत मिलाओ।

**Key snippet — 126 Vector Database — What + Why**
```python
@dataclass
class Record:
    id: str
    vector: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Key snippet — 136 Pinecone Serverless vs Pod**
```python
@dataclass(frozen=True)
class Prices:
    pod_hour: float = 0.1
    storage_gb_month: float = 0.33
    read_per_million: float = 16.0
    write_per_million: float = 4.0
```

**Key snippet — 146 pgvector vs Pinecone**
```python
class VectorStore(Protocol):
    """What the app needs; backends hide the details."""

    def upsert(self, id: str, vec: list[float], meta: dict) -> None:
        ...

    def query(self, vec: list[float], k: int) -> list[tuple[str, float]]:
        ...
```

---

## Phase 06 — Chunking (156-180)

- **156 Why Chunking Matters** — Chunking splits documents into retrievable pieces so RAG sends only relevant text to the LLM. Chunk size, overlap and boundaries strongly affect accuracy and cost. Test strategies with labelled questions.
  `chunks = split_sentences(DOC)` · हिंदी: Chunking documents को retrieve होने लायक टुकड़ों में बाँटती है ताकि RAG LLM को सिर्फ़ relevant text भेजे।
- **157 Fixed Size Chunking** — Fixed size chunking slices text into equal windows with overlap. It is simple, fast and predictable, but ignores meaning. Use it for messy text or as a baseline, preferably sized in tokens.
  हिंदी: Fixed size chunking text को overlap के साथ बराबर windows में काटती है। यह सरल, तेज़ और अनुमानित है, पर अर्थ को नहीं देखती।
- **158 Recursive Character Splitting** — Recursive splitting tries paragraph, line, sentence, word, character in order until chunks fit. It is the best general default because it respects structure and enforces a size cap. Tune size and overlap with evaluation.
  हिंदी: Recursive splitting paragraph, line, sentence, word, character क्रम से आज़माती है जब तक chunks फिट न हों।
- **159 Semantic Chunking** — Semantic chunking embeds sentences and cuts where neighbouring similarity drops. It gives topic-coherent chunks at the price of extra embedding work. Always apply min/max sizes and compare against simpler splitters.
  हिंदी: Semantic chunking sentences को embed करके वहाँ काटती है जहाँ पड़ोसी similarity गिरती है।
- **160 Sentence Splitting** — Sentence splitting keeps ideas whole by cutting at sentence ends and grouping a few sentences per chunk. Protect codes, decimals and abbreviations, and include the Hindi danda. Use a tested segmenter.
  `ABBREV = ('Dr', 'Mr', 'Mrs', 'No', 'Art', 'Sec', 'e.g', 'i.e', 'vs', 'approx')` · हिंदी: Sentence splitting वाक्य के अंत पर काटकर विचार पूरे रखती है और हर chunk में कुछ वाक्य समूहित करती है।
- **161 Paragraph Splitting** — Paragraph splitting uses authors' own blank lines as boundaries, giving coherent chunks. Merge tiny paragraphs, split huge ones, and verify the extracted text really has paragraph breaks. Keep paragraph ids for citations.
  हिंदी: Paragraph splitting लेखक की खाली lines को सीमा बनाकर coherent chunks देती है।
- **162 Markdown Splitting** — Markdown splitting follows headings so each chunk is a section with its heading path attached. Sub-split long sections and merge tiny ones. Prefix chunks with their path and use it for filters and citations.
  हिंदी: Markdown splitting headings का पालन करती है, इसलिए हर chunk अपनी heading path के साथ एक section होता है।
- **163 Code Splitting** — Code splitting cuts at functions and classes using parsers or language-aware separators. Each chunk carries file path, symbol name and imports as context. Split large units internally and keep the header on every part.
  हिंदी: Code splitting parsers या language-aware separators से functions और classes पर काटती है।
- **164 HTML Splitting** — HTML splitting cuts pages by heading tags, not by character count. It keeps tables whole and stores the heading path as metadata. Remove boilerplate first and sub-split only oversize sections.
  `parser = SectionSplitter()` · हिंदी: HTML splitting page को heading tags से काटती है, character count से नहीं। Tables पूरी रहती हैं और heading path metadata में जाता है।
- **165 PDF Chunking** — PDF chunking = extract, clean, split, and tag with page numbers. Extraction quality (reading order, OCR, tables) matters more than chunk size. Always strip repeated headers and cite pages.
  हिंदी: PDF chunking = extract, clean, split और page number लगाना।
- **166 chunk_size — How to Choose** — chunk_size trades precision (small) against context (large); start near 300-500 tokens. Measure in tokens and tune with an eval set, not with blog advice. Different document types need different sizes.
  हिंदी: chunk_size में precision (छोटा) और context (बड़ा) का trade-off है; 300-500 tokens से शुरू करो। Tokens में नापो और eval set से tune करो।
- **167 chunk_overlap — How to Choose** — Overlap repeats border text so ideas are not cut between chunks. Use 10-15% of chunk_size and never more than about 20-25%. Too much overlap creates duplicates and extra cost.
  `sents = sentences(text)` · हिंदी: Overlap border text दोहराता है ताकि idea chunks के बीच न कटे। chunk_size का 10-15% रखो, 20-25% से ज़्यादा नहीं।
- **168 Chunking for Different Doc Types** — Different documents have different natural units, so pick the splitter by doc type. Use code boundaries, headings, rows, turns or records, and fall back to recursive splitting for unknown types. Always store doc_type in metadata.
  हिंदी: अलग documents की natural units अलग हैं, इसलिए doc type से splitter चुनो।
- **169 Chunking for Tariff Documents** — Tariff documents are trees, so chunk one tariff line per chunk with its full breadcrumb. Chunk Chapter Notes separately and link them by chapter. Use metadata and hybrid search for exact HS codes and effective dates.
  हिंदी: Tariff documents tree होते हैं, इसलिए हर tariff line का एक chunk, पूरे breadcrumb के साथ। Chapter Notes अलग chunks, chapter से linked।
- **170 Parent-Child Chunking** — Search with small child chunks and answer with their bigger parent chunks. Embed only children; keep parents in a docstore linked by parent_id. Control cost by expanding only the top 1-2 parents.
  `parents = [p.strip() for p in re.split('(?m)^# ', doc) if p.strip()]` · हिंदी: छोटे child chunks से search करो और उनके बड़े parent chunks से जवाब दो।
- **171 Hierarchical Chunking** — Hierarchical chunking builds a multi-level tree with summaries at internal nodes. Retrieval narrows from chapter to section to paragraph, which is faster and more precise. Keep top-k above 1 at upper levels to avoid routing errors.
  हिंदी: Hierarchical chunking में कई levels का tree बनता है और ऊपरी nodes में summary रहती है।
- **172 Late Chunking** — Late chunking embeds the entire document first and then pools token vectors into chunk vectors. Each chunk vector carries document-wide context at no extra LLM cost. It needs a long-context embedding model and documents that fit the window.
  `chunk_a, chunk_b = ((0, 2), (2, 5))` · हिंदी: Late chunking पहले पूरे document को embed करती है और फिर token vectors को pool करके chunk vectors बनाती है।
- **173 Contextual Chunking (Anthropic method)** — Contextual chunking asks an LLM to write a short situating sentence for each chunk, then embeds and BM25-indexes context plus chunk. It fixes lost context and improves both vector and keyword retrieval.
  हिंदी: Contextual chunking में LLM हर chunk के लिए छोटा संदर्भ वाक्य लिखता है, फिर context + chunk को embed और BM25 index किया जाता है।
- **174 Agentic Chunking** — Agentic chunking lets an LLM turn text into standalone statements and group them into chunks by meaning. It works well on messy, interleaved text but costs more and is non-deterministic.
  हिंदी: Agentic chunking में LLM text को standalone statements में बदलकर उन्हें अर्थ के आधार पर chunks में group करता है।
- **175 Chunking Evaluation** — Evaluate chunking with a labelled question set and metrics like recall@k, MRR, precision, answer correctness and token cost. Change one variable at a time and keep the eval in CI. Retrieval metrics diagnose; end-to-end accuracy decides.
  हिंदी: Labelled question set और recall@k, MRR, precision, answer correctness व token cost जैसे metrics से chunking जाँचो।
- **176 Chunk Size Impact on RAG** — Chunk size trades vector sharpness and cost against answer completeness. Small chunks are precise but fragmented; large chunks are complete but noisy and expensive.
  `words = ' '.join(facts).split()` · हिंदी: Chunk size में vector की तेज़ी और cost बनाम जवाब की पूर्णता का trade-off है।
- **177 Chunk Overlap Impact** — Overlap raises border recall but adds storage, embedding cost and near-duplicate results. Gains plateau around 10-20%, so more is rarely better. Use MMR or merge adjacent chunks to remove duplicates.
  `FACT = (6, 13)` · हिंदी: Overlap border recall बढ़ाता है पर storage, embedding cost और लगभग-duplicate नतीजे भी बढ़ाता है।
- **178 Multi-level Chunking** — Multi-level chunking indexes the same text at several sizes and fuses the results. Small levels answer precise questions; large levels answer broad ones. Remove nested duplicates and keep the number of levels small.
  `LEVELS = make_levels(text)` · हिंदी: Multi-level chunking एक ही text को कई sizes पर index करके नतीजे fuse करती है।
- **179 Chunking + Metadata** — Metadata turns chunks from loose text into filterable, citable, updatable records. Attach source, position, dates and access fields at chunk time and pre-filter before similarity. Use stable ids and enforce tenant rules in the database query.
  हिंदी: Metadata chunks को ढीले text से filter, cite और update हो सकने वाले records बनाता है।
- **180 Chunking Best Practices** — Good chunking respects structure, stays self-contained, uses sensible size and small overlap, and carries metadata. Lint chunks before indexing and evaluate with real questions. Look at the data first and tune last.
  हिंदी: अच्छी chunking structure का सम्मान करती है, self-contained रहती है, सही size और छोटा overlap रखती है और metadata साथ रखती है।

**Key snippet — 156 Why Chunking Matters**
```python
DOC = 'Chapter 85 covers electrical machinery. Headphones and earphones are classified under 8518.30, except those with microphones, which are classified under 8518.40. Chapter 61 covers knitted apparel. Cotton T-shirts are classified under 6109.10. Chapter 94 covers furniture. Wooden chairs are classified under 9401.61.'
def tokens(text: str) -> set[str]:
    return set(re.findall('[a-z0-9.]+', text.lower()))
def overlap(query: str, text: str) -> int:
    return len(tokens(query) & tokens(text))
```

**Key snippet — 165 PDF Chunking**
```python
pages = ['Customs Tariff 2025\nChapter 85 Electrical machinery.\nSmartphones: 10 percent duty.\nPage 1', 'Customs Tariff 2025\nMicrophones: 7.5 percent duty.\nBatteries: 20 percent duty.\nPage 2']
def clean(page: str) -> str:
    lines = page.splitlines()
    keep = [ln for ln in lines if not ln.startswith('Customs Tariff') and (not re.fullmatch('Page \\d+', ln.strip()))]
    return '\n'.join(keep)
```

**Key snippet — 173 Contextual Chunking (Anthropic method)**
```python
document = 'Customs Ruling 2025-114: imported 5G foldable smartphones. The goods have a modem and a display. The goods are classified under 8517.13.00 because the modem function is principal.'
chunks = ['The goods have a modem and a display.', 'The goods are classified under 8517.13.00 because the modem function is principal.']
def fake_llm_context(doc: str, chunk: str) -> str:
    title = doc.split('.')[0]
    return f'From {title}.'
```

---

## Phase 07 — RAG Pipeline (181-230)

- **181 RAG — What + Why — Complete Guide** — RAG = retrieve relevant document chunks first → inject as context → LLM generates grounded answer. Solves LLM knowledge cutoff, private data access, and hallucination. Production RAG adds hybrid search, reranking, caching, and Ragas evaluation.
  `client = AsyncOpenAI()` · हिंदी: RAG = पहले relevant chunks retrieve → context में inject → LLM grounded answer।
- **182 RAG vs Fine-tuning** — RAG is for knowledge that changes and needs citations; fine-tuning is for behaviour, format and narrow skills. Try prompting, then RAG, then fine-tuning, and combine them when both needs exist. Do not fine-tune to store facts.
  हिंदी: RAG बदलने वाले और citation वाले knowledge के लिए है; fine-tuning behaviour, format और narrow skills के लिए।
- **183 RAG Architecture Overview** — RAG has an offline ingestion pipeline and an online query pipeline: retrieve, rerank, prompt, generate, validate. Debug stage by stage with logs and a golden set. Add refusal, caching and monitoring for production.
  `INDEX: list[tuple[str, str]] = [(src, c) for src, t in DOCS.items() for c in chunk(t)]` · हिंदी: RAG में offline ingestion pipeline और online query pipeline होती हैं: retrieve, rerank, prompt, generate, validate।
- **184 Naive RAG** — Naive RAG = fixed chunks, embeddings, top-k retrieval, stuff into prompt, generate. It is the right baseline but fails on exact identifiers, split answers and out-of-scope questions.
  `CHUNKS = fixed_chunks(DOC)` · हिंदी: Naive RAG = fixed chunks, embeddings, top-k retrieval, prompt में डालो, generate करो।
- **185 Advanced RAG** — Advanced RAG adds stages before, during and after retrieval to fix naive RAG failures.
  हिंदी: Advanced RAG, retrieval से पहले, दौरान और बाद में stages जोड़कर naive RAG की कमियाँ ठीक करता है।
- **186 Modular RAG** — Modular RAG splits the pipeline into swappable modules and a routing flow.
  हिंदी: Modular RAG pipeline को swappable modules और routing flow में बाँटता है।
- **187 RAG Pipeline Components** — RAG = offline indexing (load, clean, split, embed, store) + online querying (retrieve, rerank, prompt, generate).
  हिंदी: RAG = offline indexing (load, clean, split, embed, store) + online querying (retrieve, rerank, prompt, generate)।
- **188 Indexing Pipeline** — Indexing turns documents into a searchable store through load, chunk, embed, upsert.
  हिंदी: Indexing documents को load, chunk, embed, upsert से searchable store में बदलती है।
- **189 Retrieval Pipeline** — Retrieval finds the best chunks per query using filters, dense plus sparse search, fusion and reranking.
  हिंदी: Retrieval filters, dense + sparse search, fusion और reranking से हर query के best chunks ढूँढता है।
- **190 Generation Pipeline** — Generation turns retrieved chunks into a grounded, cited, schema-valid answer.
  हिंदी: Generation retrieved chunks को grounded, cited, schema-valid जवाब में बदलती है।
- **191 Document Loaders (PDF, CSV, Web, DB)** — Loaders turn PDF, CSV, web and DB data into uniform Documents with metadata.
  हिंदी: Loaders PDF, CSV, web और DB data को metadata वाले uniform Documents में बदलते हैं।
- **192 LangChain Document Loaders** — LangChain loaders convert many source types into one `Document` type with metadata.
  हिंदी: LangChain loaders कई source types को metadata वाले एक `Document` type में बदलते हैं।
- **193 LlamaIndex Loaders** — LlamaIndex readers load files and SaaS data into Documents, which are split into Nodes.
  हिंदी: LlamaIndex readers files और SaaS data को Documents में लाते हैं, जो Nodes में बँटते हैं।
- **194 Text Preprocessing** — Clean extracted text lightly: normalise Unicode, fix hyphens, remove headers/footers, dedupe.
  हिंदी: Extracted text हल्का साफ़ करो: Unicode normalise, hyphens ठीक, header/footer हटाओ, dedupe।
- **195 Metadata Extraction** — Metadata extraction adds filterable, citable facts to every chunk.
  `HS_RE = re.compile('\\b(\\d{4})\\.(\\d{2})\\b')` · हिंदी: Metadata extraction हर chunk में filter और cite करने लायक facts जोड़ती है।
- **196 Metadata Filtering in RAG** — Metadata filters limit vector search to allowed chunks for precision and security.
  हिंदी: Metadata filters precision और security के लिए vector search को allowed chunks तक सीमित करते हैं।
- **197 BM25 — Keyword Search** — BM25 ranks documents by rare matching query terms with saturation and length normalisation.
  हिंदी: BM25 documents को query के दुर्लभ matching शब्दों, saturation और length normalisation से rank करता है।
- **198 Dense Retrieval** — Dense retrieval embeds queries and chunks and finds nearest vectors, matching by meaning.
  हिंदी: Dense retrieval queries और chunks को embed करके nearest vectors ढूँढता है, यानी अर्थ से match।
- **199 Hybrid Search (BM25 + Dense)** — Hybrid search merges BM25 (exact terms) and dense (meaning) results.
  हिंदी: Hybrid search BM25 (exact शब्द) और dense (अर्थ) के results मिलाता है।
- **200 Reciprocal Rank Fusion (RRF)** — RRF scores each item as the sum of 1/(k+rank) across ranked lists, with k = 60.
  हिंदी: RRF हर item का score ranked lists में 1/(k+rank) का जोड़ लेता है, k = 60।
- **201 Multi-Query Retrieval** — Multi-query retrieval rewrites a question into several variants, retrieves for each and fuses the results.
  हिंदी: Multi-query retrieval सवाल को कई variants में rewrite करता है, हर एक पर retrieve करके results fuse करता है।
- **202 HyDE — Hypothetical Document Embeddings** — HyDE embeds an LLM-written hypothetical answer instead of the question to find real chunks.
  हिंदी: HyDE सवाल की जगह LLM के लिखे काल्पनिक जवाब को embed करके असली chunks ढूँढता है।
- **203 Step-Back Prompting** — Step-back prompting asks a broader question to retrieve governing principles, then answers the original question with both contexts.
  हिंदी: Step-back prompting व्यापक सवाल पूछकर नियम/सिद्धांत retrieve करती है, फिर दोनों contexts से original सवाल का जवाब देती है।
- **204 Query Expansion** — Query expansion adds synonyms, abbreviations and related terms so searches match documents with different wording.
  हिंदी: Query expansion synonyms, abbreviations और related शब्द जोड़ती है ताकि अलग शब्दों वाले documents भी match हों।
- **205 Query Decomposition** — Query decomposition splits a complex question into simple sub-questions. Each is retrieved in parallel and the results are merged for one answer. Gate it, cap it, and use a cheap model to keep cost and latency low.
  हिंदी: Query decomposition complex सवाल को simple sub-questions में तोड़ता है। हर एक का retrieval parallel होता है और results merge होते हैं।
- **206 Reranking — What + Why** — Reranking re-scores a wide candidate set with a precise model and keeps the best few. It improves answer quality and cuts prompt tokens, at the price of added latency. Always keep a fallback to retrieval order.
  हिंदी: Reranking चौड़े candidate set को precise model से दोबारा score करता है और best कुछ रखता है।
- **207 Cross-Encoder Reranking** — A cross-encoder reads the query and chunk together and outputs one score, giving high precision. It is too slow for the whole corpus, so use it only on the top 20-100 candidates. Load once, batch, and watch the token limit.
  हिंदी: Cross-encoder query और chunk को साथ पढ़कर एक score देता है, जिससे precision ज़्यादा मिलती है।
- **208 Cohere Reranker** — Cohere Rerank is a hosted API that reorders retrieved chunks with a relevance score. It is easy to add, multilingual, and saves LLM tokens. Add timeouts, retries and a fallback for production.
  हिंदी: Cohere Rerank एक hosted API है जो retrieved chunks को relevance score से दोबारा order करता है।
- **209 ColBERT Reranking** — ColBERT stores a vector per token and scores with MaxSim late interaction. It is more precise than a bi-encoder and cheaper than a cross-encoder. The cost is a larger index.
  हिंदी: ColBERT हर token का vector रखता है और MaxSim late interaction से score करता है।
- **210 LLM Reranking** — LLM reranking lets a chat model sort chunks using custom rules and reasoning. It is flexible but slow, costly and a bit random. Use structured output, small N, and a fallback.
  हिंदी: LLM reranking में chat model custom rules और reasoning से chunks sort करता है। यह flexible है पर धीमा, महँगा और थोड़ा random है।
- **211 RAG Prompt Template** — A RAG prompt template combines rules, labelled context, and the question. It forces grounded answers, citations, and safe refusals. Treat context as untrusted data and validate the output.
  हिंदी: RAG prompt template में rules, labelled context और question होते हैं। यह grounded answers, citations और safe refusal देता है।
- **212 Context Window Management** — Treat the context window as a budget: system, history, question, chunks, and output reserve. Count tokens exactly and trim history and low-rank chunks. A smaller, deliberate context is cheaper, faster and often more accurate.
  हिंदी: Context window को budget की तरह देखो: system, history, question, chunks और output reserve।
- **213 Context Compression** — Context compression keeps only the relevant parts of retrieved chunks. It cuts noise and tokens, but LLM-based compression has its own cost. Prefer verbatim extraction for exact data like duties and codes.
  हिंदी: Context compression retrieved chunks के सिर्फ़ relevant हिस्से रखता है।
- **214 Lost in Middle — Fix** — LLMs remember the start and end of a prompt best, so key chunks should not sit in the middle. Rerank, cut to a few chunks, then reorder so the best ones are at the edges. Verify with a needle-position test.
  `T = TypeVar('T')` · हिंदी: LLM prompt की शुरुआत और अंत सबसे अच्छा याद रखते हैं, इसलिए key chunks बीच में नहीं होने चाहिए।
- **215 RAG Response Generation** — Generation turns the prepared context into the final answer. Use low temperature, structured output, token caps and a grounding check. Return sources and usage with every answer.
  हिंदी: Generation तैयार context को final answer में बदलता है। कम temperature, structured output, token cap और grounding check use करो।
- **216 Source Citation in RAG** — Citations tie each claim to a source chunk so users can verify. Label chunks with short ids, parse and validate the ids, and map them to metadata in code. Verify support, not just existence.
  हिंदी: Citations हर claim को source chunk से जोड़ते हैं ताकि users verify कर सकें।
- **217 RAG with Streaming** — In RAG, retrieve first, then stream the generation to cut time to first token. Use SSE with sources first, deltas next, and a done event with usage. Handle disconnects and mid-stream errors.
  हिंदी: RAG में पहले retrieve करो, फिर generation stream करो ताकि पहला token जल्दी दिखे।
- **218 RAG with FastAPI** — Wrap the RAG pipeline in FastAPI with lifespan-managed clients, validated models, timeouts and clear HTTP error codes. Return answer, sources and token usage. Keep everything async and observable.
  `app = FastAPI(title='Tariff RAG (basic)')` · हिंदी: RAG pipeline को FastAPI में लपेटो: lifespan से बने clients, validated models, timeouts और साफ़ HTTP error codes के साथ।
- **219 RAG with LangChain** — LangChain wires loaders, splitters, vector stores, retrievers, prompts and models with LCEL. Build the chain once, use async, and retrieve only once per request. Move to LangGraph when you need loops and state.
  `store = InMemoryVectorStore.from_documents(docs, DeterministicFakeEmbedding(size=64))` · हिंदी: LangChain loaders, splitters, vector stores, retrievers, prompts और models को LCEL से जोड़ता है।
- **220 RAG with LlamaIndex** — LlamaIndex turns documents into Nodes, indexes them, and gives a query engine that returns answers with source nodes. Persist indexes, set models explicitly, and pick the response mode wisely. Use it when data handling is the hard part.
  `Settings.llm = MockLLM(max_tokens=50)` · हिंदी: LlamaIndex documents को Nodes में बदलता है, index करता है और source nodes के साथ answer देने वाला query engine देता है।
- **221 Conversational RAG** — Conversational RAG rewrites follow-up messages into standalone questions using chat history, then retrieves normally. Store history per session and keep it bounded. Log both raw and rewritten questions to catch errors.
  हिंदी: Conversational RAG follow-up messages को chat history से standalone सवालों में बदलता है, फिर normal retrieval करता है।
- **222 Multi-turn RAG** — Multi-turn RAG rewrites each follow-up into a standalone question using chat history before retrieval. It trims or summarizes history so cost and context stay under control. Store sessions outside process memory for production.
  हिंदी: Multi-turn RAG हर follow-up को history की मदद से standalone सवाल बनाकर retrieve करता है।
- **223 RAG Memory** — RAG memory = short-term window plus long-term fact store retrieved like documents. Save extracted facts per user, dedupe and expire them. Keep it private, small, and cheap.
  हिंदी: RAG memory = short-term window + long-term fact store, जिसे documents की तरह retrieve किया जाता है।
- **224 Agentic RAG** — Agentic RAG lets an LLM agent decide when, where and how to retrieve, looping until it has enough evidence. It beats fixed pipelines on complex questions but costs more and is less predictable.
  हिंदी: Agentic RAG में LLM agent तय करता है कि कब, कहाँ और कैसे retrieve करना है, और काफ़ी सबूत मिलने तक loop चलता है।
- **225 Self-RAG** — Self-RAG lets the LLM decide when to retrieve and critique chunks and answers. It reduces hallucination by dropping bad context and rejecting ungrounded answers. It costs extra LLM calls, so cap loops and use small graders.
  हिंदी: Self-RAG में LLM तय करता है कब retrieve करना है और chunks/answers को critique करता है।
- **226 Corrective RAG (CRAG)** — CRAG grades retrieved chunks and decides Correct, Incorrect or Ambiguous. Bad retrieval triggers a fallback such as web search. This avoids hallucinating from irrelevant context.
  हिंदी: CRAG retrieved chunks को grade करके Correct, Incorrect या Ambiguous तय करता है। खराब retrieval पर web search जैसा fallback चलता है।
- **227 RAG Fusion** — RAG Fusion creates multiple query variants and retrieves for each. RRF merges the ranked lists so consistently high chunks win. It boosts recall for vague queries at small extra cost.
  हिंदी: RAG Fusion कई query variants बनाकर हर एक के लिए retrieve करता है। RRF ranked lists मिलाता है ताकि बार-बार ऊपर आने वाले chunks जीतें।
- **228 Multi-Modal RAG** — Multi-Modal RAG handles tables, images and scans, not just text. Index summaries or image embeddings, but answer from the raw object with a vision LLM. Control cost with low image detail and batch ingestion.
  हिंदी: Multi-Modal RAG tables, images और scans संभालता है, सिर्फ text नहीं।
- **229 RAG for Tariff System** — The tariff RAG uses hierarchical chunks, hybrid search, reranking and structured output. A validator and review queue protect against wrong codes. Freshness metadata keeps answers current.
  हिंदी: Tariff RAG में hierarchical chunks, hybrid search, reranking और structured output होते हैं।
- **230 RAG Production Checklist** — A RAG is production-ready only when data, retrieval, generation, safety, performance, cost and monitoring are all covered. Gate releases with a golden-set evaluation. Watch quality, latency and token cost continuously.
  हिंदी: RAG तभी production-ready है जब data, retrieval, generation, safety, performance, cost और monitoring सब कवर हों।

**Key snippet — 181 RAG — What + Why — Complete Guide**
```python
client = AsyncOpenAI()
async def build_index(documents: list[str]) -> tuple[list[list[float]], list[str]]:
    """Embed all documents. Returns (vectors, texts)."""
    response = await client.embeddings.create(model='text-embedding-3-small', input=documents)
    vectors = [item.embedding for item in response.data]
    return (vectors, documents)
```

**Key snippet — 198 Dense Retrieval**
```python
FAKE_EMBED: Dict[str, List[float]] = {'earphones': [0.95, 0.05, 0.0], 'headset': [0.9, 0.1, 0.0], 'smartphone': [0.05, 0.95, 0.0], 'leather shoes': [0.0, 0.0, 1.0]}
def embed(text: str) -> List[float]:
    """Average the vectors of known words (toy model)."""
    vecs = [v for w, v in FAKE_EMBED.items() if w in text.lower()]
    if not vecs:
        return [0.0, 0.0, 0.0]
    return [sum(col) / len(vecs) for col in zip(*vecs)]
```

**Key snippet — 216 Source Citation in RAG**
```python
CHUNKS: List[Dict[str, str]] = [{'text': 'Smartphones HS 8517.13 duty 20 percent.', 'title': 'Customs Tariff 2024', 'page': '412'}, {'text': 'Refurbished phones need an import licence.', 'title': 'DGFT Notification 12/2023', 'page': '3'}]
ANSWER: str = 'Smartphones are HS 8517.13 [S1] with 20 percent duty [S1]. Refurbished ones need a licence [S2] [S9].'
```

---

## Top 10 interview questions

**1. Cosine Similarity: What range does cosine similarity have?** (104)
-1 to 1. For most text embedding models real scores fall between about 0 and 1.

**2. HNSW Algorithm: What does HNSW stand for?** (129)
Hierarchical Navigable Small World, a multi-layer proximity graph for approximate nearest neighbour search.

**3. Hybrid Search Setup: What is hybrid search?** (152)
Combining keyword and vector retrieval and merging their results.

**4. Recursive Character Splitting: What is the default separator order?** (158)
Paragraph break `"\n\n"`, line break `"\n"`, space `" "`, then empty string (characters).

**5. chunk_overlap: What is chunk_overlap?** (167)
The amount of text shared between consecutive chunks, so information at the border is not lost.

**6. RAG vs Fine-tuning: One-line difference between RAG and fine-tuning?** (182)
RAG adds knowledge at query time via retrieval; fine-tuning changes the model's behaviour via training.

**7. Advanced RAG: What is the difference between Naive and Advanced RAG?** (185)
Naive RAG is index, retrieve top-k, generate. Advanced RAG adds pre-retrieval (query rewriting), retrieval (hybrid, filters) and post-retrieval (rerank, compress) stages.

**8. Reciprocal Rank Fusion (RRF): What does RRF stand for and what is the formula?** (200)
Reciprocal Rank Fusion; score(d) = sum over rankers of 1 / (k + rank_r(d)), commonly k = 60.

**9. HyDE: What does HyDE stand for?** (202)
Hypothetical Document Embeddings (Gao et al., 2022).

**10. Cross-Encoder Reranking: What does a cross-encoder output?** (207)
One relevance score (logit) for a (query, document) pair.

