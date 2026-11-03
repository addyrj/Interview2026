---

# Tokens + Cost Cheatsheet — Tokens, Caching, Cost, Deployment (Quick Revision)
# हिंदी में: Tokens, Caching, Cost और Deployment का Quick Revision

Condensed from token/cost topics in 01-llm-apis, all of 16-caching, Cost Impact sections across notes, and highlights from 19-system-design and 20-deployment. Core formula from the notes: `cost = in/1e6*p_in + out/1e6*p_out`; output tokens usually cost more than input.
> Prices, model names and IDs shown in the source notes are illustrative; always verify on the provider's official pricing/model pages.

---

## Tokens + model cost (01-llm-apis)

- **022 Tokens — Complete Guide** — Tokens are subword units (~4 chars each) — the currency of LLM APIs. Count with `tiktoken` before sending large documents to avoid silent truncation and unexpected costs.
  `enc = tiktoken.encoding_for_model('gpt-4o-mini')` · हिंदी: Tokens LLM API की currency हैं (~4 chars each)। Large documents भेजने से पहले `tiktoken` से count करो।
- **023 Context Window — What it Means** — The context window is the total token limit for input plus output in one request. Count tokens, reserve room for the answer, and trim or retrieve instead of stuffing everything. Bigger windows cost more and do not guarantee better answers.
  हिंदी: Context window एक request में input + output tokens की कुल limit है।
- **030 OpenAI API — Token Usage + Cost** — Read `response.usage` on every call and compute cost with current per-model prices. Log it by user and feature, set budgets and alerts, and cap `max_tokens`. Include streaming, retries, and non-chat endpoints so your numbers match the invoice.
  `PRICES = {'gpt-4o-mini': (0.15, 0.6), 'gpt-4o': (2.5, 10.0)}` · हिंदी: हर call में `response.usage` पढ़ो और मौजूदा model prices से cost निकालो।
- **044 Cost Optimization — Models** — Measure tokens and cost per feature first. Then trim prompts, cap outputs, cache, route and batch. Always re-check quality after every saving.
  `base = cost(3000, 400) * requests` · हिंदी: पहले हर feature का token और cost measure करो। फिर prompt छोटा करो, output cap करो, cache, routing और batching लगाओ।
- **045 Latency Optimization — Models** — Latency depends mostly on output tokens, model size and sequential steps. Stream, parallelise independent calls, use smaller models and cap output. Measure TTFT and p95, not only averages.
  हिंदी: Latency ज़्यादातर output tokens, model size और sequential steps से बनती है।
- **048 OpenAI Batch API** — Batch API runs large JSONL jobs asynchronously in up to 24 hours at about half price. Match results using `custom_id` and retry failed lines. Never use it for live user requests.
  `path = Path('batch_input.jsonl')` · हिंदी: Batch API बड़े JSONL jobs को 24 घंटे तक में लगभग आधी कीमत पर चलाता है। Results `custom_id` से match करो और failed lines retry करो।
- **049 Model Fallback Strategy** — Plan for failure: retry transient errors with backoff, then switch models or providers, then use cache or manual review. Use circuit breakers and log every fallback. Validate output formats on every model.
  हिंदी: Failure के लिए plan बनाओ: transient errors पर backoff के साथ retry, फिर model/provider बदलो, फिर cache या manual review।

**Key snippet — 022 Tokens — Complete Guide**
```python
enc = tiktoken.encoding_for_model('gpt-4o-mini')
text = 'Tariff classification for electronics'
tokens = enc.encode(text)
hindi_text = 'टैरिफ वर्गीकरण'
```

**Key snippet — 030 OpenAI API — Token Usage + Cost**
```python
@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
```

**Key snippet — 045 Latency Optimization — Models**
```python
async def fake_llm(task: str, seconds: float) -> str:
    await asyncio.sleep(seconds)
    return f'{task}: done'
```

---

## Caching (441-460)

- **441 LLM Caching — What + Why** — Caching reuses earlier LLM answers for repeated requests, saving tokens and latency. Build keys carefully, set TTLs and plan invalidation. Do not cache personalised or real-time answers.
  हिंदी: Caching दोहराई गई requests के लिए पुराने LLM answers reuse करता है, tokens और latency बचाता है।
- **442 Exact Match Caching** — Exact caching hashes the normalised request and returns the stored answer on identical repeats. It is safe and cheap but has a low hit rate for paraphrases. Include model, params and data version in the key.
  हिंदी: Exact caching normalised request का hash बनाकर identical repeats पर stored answer लौटाता है।
- **443 Semantic Caching** — Semantic caching reuses answers for queries with similar meaning using embeddings and a similarity threshold. It raises hit rate but risks wrong matches, so use strict thresholds and metadata filters. Layer it after exact caching.
  हिंदी: Semantic caching embeddings और similarity threshold से समान अर्थ वाले queries के answers reuse करता है।
- **444 Redis for LLM Caching** — Redis gives a shared, fast, expiring cache for LLM answers. Build a canonical hashed key, set a TTL, cache only successful deterministic calls and fail open. Every hit saves tokens and 1-3 seconds of latency.
  हिंदी: Redis LLM जवाबों के लिए shared, तेज़ और expire होने वाला cache देता है।
- **445 GPTCache Library** — GPTCache gives semantic caching with pluggable embedding, storage and vector modules. The key tuning knob is the similarity threshold, which trades hit rate against wrong answers. Use its generic get/put API with a modern async client.
  हिंदी: GPTCache में embedding, storage और vector modules जोड़कर semantic caching मिलती है।
- **446 LangChain Caching** — `set_llm_cache` adds caching to every LangChain/LangGraph model call with swappable backends. Use SQLite in dev, Redis in prod, and temperature 0. It does not isolate tenants, so be careful with private data.
  `set_llm_cache(InMemoryCache())` · हिंदी: `set_llm_cache` से हर LangChain/LangGraph model call में caching जुड़ जाती है और backend बदला जा सकता है।
- **447 Prompt Caching (Anthropic Native)** — Anthropic prompt caching reuses a static prompt prefix at about 10 percent of input price. Put stable content first, mark it with cache_control, and keep it byte-identical. Check cache_read_input_tokens to confirm savings.
  हिंदी: Anthropic prompt caching स्थिर prompt prefix को input price के लगभग 10 प्रतिशत पर दोबारा इस्तेमाल करता है।
- **448 Prompt Caching (OpenAI Native)** — OpenAI caches long prompt prefixes automatically (1,024 tokens or more) and discounts the cached input tokens. Put static content first and dynamic content last, and keep tools stable. Watch cached_tokens in usage to measure savings.
  हिंदी: OpenAI लंबे prompt prefix (1,024 tokens या ज़्यादा) अपने-आप cache करता है और cached input tokens पर discount देता है।
- **449 Cache Invalidation Strategy** — Invalidate by TTL, by versioned keys, and by targeted purges. Put prompt, model and data versions in the key so changes expire answers automatically. Avoid mass flushes that cause thundering herds.
  `PROMPT_V, DATA_V = ('p3', '2026-04')` · हिंदी: TTL, versioned keys और targeted purge से invalidate करो। Key में prompt, model और data version रखो ताकि बदलाव पर जवाब अपने-आप बेकार हो जाएँ।
- **450 Cache TTL for LLM** — Pick TTL by how fast the truth changes and how costly stale answers are. Add jitter and a max age for sliding TTLs. Never cache real-time facts as LLM answers.
  हिंदी: TTL इस हिसाब से चुनो कि सच्चाई कितनी जल्दी बदलती है और पुराने जवाब का नुकसान कितना है। Jitter लगाओ और sliding TTL में max age रखो।
- **451 Cache Key Design** — A cache key must include every field that changes the answer and no volatile fields. Normalise text, serialise canonically, and hash with SHA-256 (never Python hash). Add tenant and version parts for safety and invalidation.
  हिंदी: Cache key में वह हर field हो जो जवाब बदलता है और कोई volatile field नहीं।
- **452 Semantic Cache with Redis** — Redis vector search lets you cache LLM answers by meaning, not exact text. Store embedding plus answer, run KNN, and accept only within a tuned distance threshold and the right tenant. Watch false hits on numbers and personal data.
  हिंदी: Redis vector search से LLM जवाब अर्थ के आधार पर cache होते हैं, exact text से नहीं।
- **453 Semantic Cache with Qdrant** — A semantic cache embeds questions and reuses answers for similar ones via Qdrant search. Tune the threshold, filter by tenant and add expiry to avoid wrong or stale hits. It cuts both cost and latency for repeated intents.
  `cache.append((embed('hs code for iphone 15'), '8517.13'))` · हिंदी: Semantic cache questions को embed करके Qdrant से similar questions के answers दोबारा use करता है।
- **454 Cost Savings from Caching** — Savings come from hit rate times the cost of a call, minus cache overhead. Measure cost-weighted hit rate on real logs, not toy traffic. Combine response/semantic caching with provider prompt caching for the biggest effect.
  `per_call = llm_cost(1500, 250, p_in=0.15, p_out=0.6)` · हिंदी: बचत = hit rate x call की cost, minus cache का overhead। असली logs पर cost-weighted hit rate measure करो, नकली traffic पर नहीं।
- **455 Cache Hit Rate Optimization** — Raise hit rate by cleaning keys, ordering prompts static-first, tuning thresholds and TTLs, and warming the cache. Always track hit precision, not only hit rate. Start with cheap wins like normalisation.
  हिंदी: Keys साफ़ करके, prompt में static हिस्सा पहले रखकर, threshold और TTL tune करके और cache warm करके hit rate बढ़ाओ।
- **456 Streaming + Caching** — On a miss, stream and buffer, then cache only complete, clean answers. On a hit, replay the text as a stream so clients behave the same. Use coalescing to avoid duplicate concurrent calls.
  हिंदी: Miss पर stream करो और buffer करो, फिर सिर्फ़ पूरे और सही answers cache करो। Hit पर text को stream की तरह replay करो ताकि client वैसे ही चले।
- **457 Multi-tenant Caching** — Put tenant_id (from auth) in every cache key or filter so tenants never see each other's answers. Share a global namespace only for public content. Add quotas, TTLs and per-tenant deletion.
  `put('acme', 'our duty rate?', '5% (acme contract)')` · हिंदी: हर cache key या filter में tenant_id (auth से) रखो ताकि tenants एक-दूसरे के answers न देखें। Global namespace सिर्फ़ public content के लिए।
- **458 Cache Security** — Treat the cache as a trusted shortcut that must be protected: private network, auth, TLS, encryption, signing. Cache only validated, non-flagged, redacted answers, scoped per tenant. Keep a quick purge path and monitor anomalies.
  `entry = pack({'answer': '8517.13'})` · हिंदी: Cache को trusted shortcut मानकर बचाओ: private network, auth, TLS, encryption, signing।
- **459 Cache Monitoring** — Cache monitoring measures hit rate, latency, dollars saved and wrong-answer rate. Hit rate alone is misleading, so sample hits and audit quality. Use the numbers to tune threshold, TTL and keys.
  `stats = CacheStats()` · हिंदी: Cache monitoring hit rate, latency, बचे dollars और गलत-जवाब की दर मापती है।
- **460 Caching Best Practices** — Build keys from model, prompt version, normalized input and tenant. Use TTL with jitter, locks and event-based invalidation. Never cache errors, refusals or personal data, and always measure.
  `c = TTLCache()` · हिंदी: Keys model, prompt version, normalized input और tenant से बनाओ। TTL के साथ jitter, locks और event-based invalidation use करो।

**Key snippet — 441 LLM Caching — What + Why**
```python
CACHE: dict[str, str] = {}
STATS = {'hits': 0, 'misses': 0}
def make_key(model: str, prompt: str) -> str:
    """Normalise the prompt and hash it with the model name."""
    normalised = ' '.join(prompt.lower().split())
    return hashlib.sha256(f'{model}|{normalised}'.encode()).hexdigest()
```

**Key snippet — 447 Prompt Caching (Anthropic Native)**
```python
LONG_MANUAL = 'TARIFF MANUAL SECTION ... ' * 400
def build_request(question: str) -> dict:
    return {'model': 'claude-sonnet-4-5', 'max_tokens': 300, 'system': [{'type': 'text', 'text': 'You classify goods into HS codes.'}, {'type': 'text', 'text': LONG_MANUAL, 'cache_control': {'type': 'ephemeral'}}], 'messages': [{'role': 'user', 'content': question}]}
def cost(usage: dict, price_in: float=3.0) -> float:
    return (usage['input_tokens'] * price_in + usage['cache_creation_input_tokens'] * price_in * 1.25 + usage['cache_read_input_tokens'] * price_in * 0.1) / 1000000
```

**Key snippet — 453 Semantic Cache with Qdrant**
```python
def embed(text: str) -> Counter[str]:
    return Counter(text.lower().split())
def cosine(a: Counter[str], b: Counter[str]) -> float:
    dot = sum((a[w] * b[w] for w in a))
    na = math.sqrt(sum((v * v for v in a.values())))
    nb = math.sqrt(sum((v * v for v in b.values())))
    return dot / (na * nb) if na and nb else 0.0
```

---

## System design highlights (19)

- **506 AI System Design — Framework** — Follow a fixed order: requirements, estimates, baseline, design, quality, operations, trade-offs.
  `r = estimate(qps=50, in_tokens=1500, out_tokens=150, in_price_per_m=0.5, out_price_per_m=1.5)` · हिंदी: क्रम रखो: requirements, estimates, baseline, design, quality, operations, trade-offs।
- **509 LLM Selection for Production** — Choose models by your own evals, not hype: quality, latency, cost and constraints.
  `bar, max_latency = (0.92, 2000)` · हिंदी: Hype नहीं, अपने evals से model चुनो: quality, latency, cost, constraints।
- **515 Caching Strategy** — Cache at several layers: exact, semantic, embeddings, retrieval, and provider prompt cache.
  `cache = TTLCache(ttl_seconds=60)` · हिंदी: कई layers पर cache करो: exact, semantic, embeddings, retrieval, provider prompt cache।
- **516 Scalability in AI Systems** — AI systems usually bottleneck on model rate limits and slow calls, not CPU.
  हिंदी: AI systems में bottleneck अक्सर model rate limits और धीमी calls होते हैं, CPU नहीं।
- **520 Cost Architecture for AI** — Design cost in from day one: meter every call, set budgets, cache, route to small models first, and cap tokens. Judge success by cost per successful task, not cost per call. Add alerts and a kill switch so bugs cannot drain the budget.
  `b = Budget(limit_usd=0.01)` · हिंदी: Cost को शुरू से design करो: हर call meter करो, budget लगाओ, cache करो, पहले छोटा model और tokens cap।
- **521 Latency Budget Design** — A latency budget splits the total time target into per-step slices with timeouts and one shared deadline. Use p95, parallelise, stream, and degrade gracefully instead of failing. Output tokens and the LLM step usually dominate, so cut them first.
  हिंदी: Latency budget कुल target को per-step slices, timeouts और एक shared deadline में बाँटता है।
- **523 Fallback Strategies** — A fallback ladder (backup model, cache, rules, human) lets the system answer when the primary path fails. Mark degraded answers and never auto-act on low-trust ones. Test and monitor fallbacks, because untested plan B fails when needed.
  हिंदी: Fallback ladder (backup model, cache, rules, human) से primary fail होने पर भी system जवाब देता है।
- **524 Multi-model Strategy** — Use different models for different tasks: cheap for easy, strong for hard, vision and embeddings where needed, plus a backup vendor. Pick by your own evals and route through a gateway with confidence-based escalation.
  हिंदी: अलग tasks के लिए अलग models: आसान के लिए सस्ता, कठिन के लिए मज़बूत, ज़रूरत पर vision/embedding और एक backup vendor।
- **531 Design: RAG for 1M Documents** — At 1M documents use async batched ingestion, a vector DB with metadata filters, hybrid search, and a reranker. Dedupe and index incrementally, cache aggressively, and measure recall as the corpus grows. Design the latency and cost budget per stage.
  हिंदी: 10 लाख documents पर async batched ingestion, metadata filters वाला vector DB, hybrid search और reranker use करो।
- **536 Design: Tariff Classification System** — Retrieve candidate headings, let the LLM choose only among them, then validate. Route low confidence to humans and log everything. Evaluate by chapter and cost-weighted error.
  `code, conf = classify('wireless earbuds with case')` · हिंदी: Candidate headings retrieve करो, LLM को सिर्फ उन्हीं में से चुनने दो, फिर validate करो। कम confidence इंसान को भेजो और सब कुछ log करो।

**Key snippet — 506 AI System Design — Framework**
```python
def estimate(qps: float, in_tokens: int, out_tokens: int, in_price_per_m: float, out_price_per_m: float) -> dict[str, float]:
    per_req = in_tokens * in_price_per_m / 1000000.0 + out_tokens * out_price_per_m / 1000000.0
    per_day = per_req * qps * 86400
    return {'cost_per_request': per_req, 'cost_per_day': per_day, 'tokens_per_sec': qps * (in_tokens + out_tokens)}
```

**Key snippet — 515 Caching Strategy**
```python
cache = TTLCache(ttl_seconds=60)
key = 'IN|2025|iphone 15'
cache.set(key, '8517.13')
```

**Key snippet — 520 Cost Architecture for AI**
```python
PRICES: dict[str, dict[str, float]] = {'small': {'input': 0.15, 'output': 0.6}, 'large': {'input': 3.0, 'output': 15.0}}
def cost_usd(model: str, in_tok: int, out_tok: int) -> float:
    """Return the dollar cost of one call."""
    p = PRICES[model]
    return in_tok * p['input'] / 1000000.0 + out_tok * p['output'] / 1000000.0
```

---

## Deployment highlights (20)

- **541 Dockerizing AI Apps** — Docker packages the app and its dependencies for identical runs everywhere. Copy requirements first, keep secrets out of images, and add health checks. Containers are disposable, so keep state outside.
  `app = FastAPI()` · हिंदी: Docker app और dependencies को पैक करता है ताकि हर जगह एक जैसा चले।
- **545 Environment Variables for AI** — Keep model names, URLs, limits and flags in environment variables, loaded into one typed, validated settings class. Fail fast on missing values and never commit `.env`. Use a secret manager for real credentials in production.
  हिंदी: Model names, URLs, limits और flags को environment variables में रखो और एक typed, validated settings class में load करो।
- **546 Secrets in AI Deployment** — Store secrets in a secret manager, inject them at runtime, give each service only what it needs, and use separate keys per environment. Never put them in code, images, prompts or logs. Rotate regularly and revoke at once after any leak.
  हिंदी: Secrets को secret manager में रखो, runtime पर inject करो, हर service को सिर्फ ज़रूरी secrets दो और हर environment की अलग keys रखो।
- **556 Auto Scaling for AI** — Autoscaling adds and removes instances using a metric and target. For I/O-bound AI apps scale on requests per target, concurrency or queue depth, not CPU. Cap the maximum to respect provider rate limits and budget.
  हिंदी: Autoscaling metric और target के आधार पर instances जोड़ता-घटाता है।
- **559 CI/CD for AI Apps** — CI/CD automates testing and deployment on every change. For AI apps add eval gates and cost checks, mock LLMs in unit tests, and tag images by SHA. Roll out gradually and roll back automatically.
  हिंदी: CI/CD हर change पर testing और deployment automate करता है।
- **566 Cost Monitoring in Production** — Compute cost from real token usage, tag it by tenant and feature, and store it in fast counters. Enforce soft and hard budgets with graceful degradation before blocking. Watch hidden multipliers: retries, agent loops, long histories.
  `t = CostTracker(daily_budget_usd=0.01)` · हिंदी: असली token usage से cost निकालो, tenant और feature से tag करो और तेज़ counters में रखो।
- **567 Rate Limiting AI API** — Limit both requests and tokens per caller using shared Redis counters, and return 429 with Retry-After. Also throttle outbound calls and retry provider 429s with exponential backoff and jitter.
  `bucket = TokenBucket(capacity=5, refill_per_sec=1)` · हिंदी: Shared Redis counters से हर caller के requests और tokens दोनों limit करो और Retry-After के साथ 429 दो।
- **570 AI Production Checklist** — Before launch, verify quality evals, reliability (timeouts, fallbacks), security, privacy, cost caps, monitoring, and a tested rollback. Automate the checks in CI and readiness probes. After launch, feed production failures back into the eval set.
  हिंदी: Launch से पहले quality evals, reliability (timeouts, fallbacks), security, privacy, cost caps, monitoring और tested rollback जाँचो।

**Key snippet — 541 Dockerizing AI Apps**
```python
app = FastAPI()
@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
```

**Key snippet — 556 Auto Scaling for AI**
```python
def desired_instances(current_load: float, target_per_instance: float, min_n: int=2, max_n: int=12) -> int:
    """Return how many instances are needed to keep each near the target."""
    if target_per_instance <= 0:
        raise ValueError('target_per_instance must be positive')
    needed = math.ceil(current_load / target_per_instance)
    return max(min_n, min(max_n, needed))
```

**Key snippet — 566 Cost Monitoring in Production**
```python
PRICES: dict[str, tuple[float, float]] = {'small-model': (0.15, 0.6), 'large-model': (3.0, 15.0)}
def call_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    if model not in PRICES:
        raise KeyError(f'no price for {model}')
    p_in, p_out = PRICES[model]
    return tokens_in * p_in / 1000000 + tokens_out * p_out / 1000000
```

---

## Cost Impact digest (from the notes' Cost Impact sections)

- **114 Embedding Cost Optimization — Complete Guide** — Example: 400k notes x 300 tokens = 120M tokens. Full nightly re-embed with small: $2.40/night (about $72/month). Incremental (0.5% change): $0.012/night. With large: $15.60 vs $0.08. Batch API halves both.
- **116 Batch Embedding — Complete Guide** — Batching itself does not change per-token price, but the Batch API gives 50% off: for 400M tokens with small, $8 becomes $4 (large: $52 becomes $26). Savings also come from fewer failed/retried calls.
- **154 Vector DB Cost Optimization** — Embedding tokens: one-time per chunk plus tiny per query. Hash-based incremental ingestion avoids paying again for unchanged text. Check current embedding prices; they are low per 1M tokens but add up for large corpora.
- **166 chunk_size — How to Choose** — Input tokens per query = top_k x chunk_size + prompt. Example: top_k=5 x 512 = 2560 tokens vs 5 x 256 = 1280 tokens. At $0.15 per 1M input tokens: 100K queries x 2560 = $38.40 vs $19.20.
- **182 RAG vs Fine-tuning** — RAG: embedding corpus once (cheap), plus extra input tokens per query (top_k x chunk size, for example 1,500 tokens). 3M queries/month x 1,500 tokens x $0.15/1M = about $675 extra input cost.
- **206 Reranking — What + Why** — Reranking itself costs: Cohere per 1,000 searches (check current pricing), or GPU time for open-source cross-encoders; LLM-based rerank costs tokens.
- **268 LangChain Caching** — Cache hit = **0 tokens, ~0 cost, ~5 ms**. Cost saved = hit_rate x cost_per_call x volume. Example: 100K queries/day, 500 in + 200 out on gpt-4o-mini = $0.000195/query = $19.50/day.
- **304 Agent Max Iterations** — A stuck agent at cap 15 with 600 tokens/step history growth pays about 15 x base + 600 x 120 = large; at cap 6 it pays under a third.
- **374 Sliding Window Memory** — Without a window, turn n sends about n x 150 tokens; at 40 turns that is 6,000 tokens per call. With k=6, it stays near 900 tokens per call: about 85 percent cheaper at turn 40.
- **382 Token Budget Management** — Budgets bound worst-case spend: 1000 users x 20K tokens/day x 30 days = 600M tokens/month, about $90 input on gpt-4o-mini at $0.15/M (more with output).
- **434 Cost Tracking per Request** — Tracking adds no tokens; the ledger is a few bytes per call.
- **437 Token Usage Monitoring** — Input tokens are usually the bulk of RAG spend. Going from 480 to 2,110 input tokens at 1M requests/month on gpt-4o-mini adds about 1.63B tokens, roughly $245/month (at $0.15 per 1M).
- **494 Fine Tuning Cost Estimation** — This whole topic is cost. Key levers: shorter prompts, fewer epochs, smaller model, cleaner data. Illustrative example: 7.2M training tokens at $3 per 1M is $21.6.
- **520 Cost Architecture for AI** — Illustrative example (prices are examples, check current pricing): 1M requests/month, 700 input + 100 output tokens each. All large ($3 / $15 per 1M): 700M x $3 + 100M x $15 = $2,100 + $1,500 = $3,600.
- **566 Cost Monitoring in Production** — Monitoring prevents runaway spend. Illustrative: an agent loop of 50 calls x 4,000 tokens on a large model could cost far more than a single call; a budget cap stops it.

---

## Top 10 interview questions

**1. OpenAI API: Where do you find token counts for a call?** (030)
In `response.usage`: `prompt_tokens`, `completion_tokens`, `total_tokens`.

**2. Tokens: What is BPE (Byte Pair Encoding)?** (022)
BPE is the tokenization algorithm used by GPT models. It starts with individual bytes, then iteratively merges the most frequent adjacent pairs.

**3. LLM Caching: What is LLM caching?** (441)
Reusing stored model responses for repeated requests to save cost and latency.

**4. Exact Match Caching: What is exact match caching?** (442)
Caching where a stored response is reused only when the normalised request is identical.

**5. Semantic Caching: What is semantic caching?** (443)
Reusing cached answers when a new query is semantically similar, found through embedding similarity.

**6. Prompt Caching (Anthropic Native): What is prompt caching?** (447)
The provider stores the processed prefix of your prompt and reuses it for later calls, charging much less for those tokens and reducing latency.

**7. Cost Savings from Caching: What are the main caching layers for LLM apps?** (454)
Exact response cache (Redis), semantic cache (vector DB), and provider prompt caching (discounted repeated prefix tokens).

**8. Cache Hit Rate Optimization: What lowers cache hit rate the most?** (455)
Noisy keys (timestamps, IDs), short TTLs, strict thresholds, and cold caches after deploys.

**9. Cost Architecture for AI: What are the main cost drivers of an LLM app?** (520)
Input tokens, output tokens (usually pricier), number of calls per task (agents, retries), model choice, and embeddings/vector storage. Output tokens often cost several times input tokens.

**10. Cost Monitoring in Production: How is LLM API cost calculated?** (566)
input_tokens x input price + output_tokens x output price, usually per 1M tokens. Some providers discount cached input tokens.

