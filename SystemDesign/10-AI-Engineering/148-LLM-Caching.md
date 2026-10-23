# 148. LLM Caching
# हिंदी में: LLM Caching — LLM के महँगे और धीमे काम को दोबारा न करना: बिल्कुल वही सवाल (exact cache), मिलता-जुलता सवाल (semantic cache), prompt का स्थिर हिस्सा (provider prompt caching), embeddings/retrieval/tool नतीजों का cache — ख़र्च और latency दोनों घटाने के लिए, पर ग़लत या पुराना जवाब दिए बिना

---

## 🔵 Simple Definition (English)
**LLM caching** reuses previous computation to cut **cost and latency**. There are several layers:
1. **Exact-match response cache**: same normalized input, model, parameters, prompt version and context gives the same stored answer (e.g., Redis with a TTL). Best for deterministic tasks (temperature 0 classification, FAQ answers, translations of fixed strings).
2. **Semantic cache**: embed the user query, and if a previous query is **very similar** (cosine ≥ a high threshold), return its answer. This catches paraphrases ("refund kab aayega" ≈ "when will I get my refund"), but risks **false hits**.
3. **Provider prompt caching**: the provider caches the **processed prefix** of long prompts (system prompt, tool definitions, big documents, few-shot examples). Subsequent requests sharing that prefix are **cheaper and faster**. Anthropic uses explicit `cache_control` breakpoints, and OpenAI caches long prefixes automatically.
4. **KV/prefix caching in self-hosted inference** (vLLM, TensorRT-LLM): reuse attention key/value states for shared prefixes.
5. **Component caches**: embeddings (by content hash), query embeddings, retrieval results, reranker scores, tool results (order status for 15 s).
Correctness rules: **include every input that affects the answer in the cache key** (prompt version, tenant, language, user scope, document versions), **never share personalized answers across users**, and **invalidate** when data changes.

## 🔵 सरल परिभाषा (Hindi)
LLM caching = पहले किया काम दोबारा इस्तेमाल करके ख़र्च और देर घटाना, कई परतों में: (1) Exact cache — बिल्कुल वही input + model + prompt version + context = वही जवाब (Redis + TTL; classification, FAQ के लिए बढ़िया); (2) Semantic cache — सवाल का embedding, पहले का बहुत मिलता-जुलता सवाल मिले तो उसका जवाब ("refund kab aayega" ≈ "when will I get my refund") — पर ग़लत मेल का ख़तरा; (3) Provider prompt caching — लंबे prompt का स्थिर शुरुआती हिस्सा (system, tools, documents, उदाहरण) provider cache करता है — अगली requests सस्ती/तेज़; (4) self-hosted में KV/prefix cache; (5) embeddings, retrieval, reranker, tool नतीजों का cache।
नियम: जवाब पर असर डालने वाली हर चीज़ key में (prompt version, tenant, भाषा, यूज़र, document version), एक यूज़र का निजी जवाब दूसरे को कभी नहीं, डेटा बदले तो invalidate।

---

## 🔴 Problem it Solves
LLM calls are among the **most expensive and slowest** operations in modern apps:
- A 6,000-token system prompt plus tools plus policy documents is sent **on every request**, so you pay to process the same prefix millions of times.
- During a Big Billion Days sale or IPL night, **thousands of users ask the same questions** ("refund kab aayega", "order cancel kaise karein"). Generating each answer fresh wastes money and adds seconds of latency.
- Agents re-call the same tools and re-embed the same texts.
- Users feel every second: caching turns a 3 s generation into a 50 ms lookup.
Without discipline, caches cause **stale answers** (an old refund policy), **wrong answers** (a semantic false hit: a card-refund answer for a UPI question) or **data leaks** (one user's order details served to another). Good caching design is a balance of **hit rate, freshness, correctness and isolation**.

## 🔴 यह क्यों बना? (Hindi)
LLM calls आज के ऐप्स के सबसे महँगे और धीमे काम हैं: 6,000 tokens का system prompt + tools + नीति documents हर request पर — वही हिस्सा लाखों बार पढ़वाने का पैसा; Big Billion Days या IPL रात में हज़ारों लोग एक ही सवाल पूछते हैं ("refund kab aayega") — हर बार नया जवाब बनाना पैसे और सेकंडों की बर्बादी; agents वही tools और embeddings दोबारा; caching से 3 सेकंड का जवाब 50 ms में।
अनुशासन के बिना cache से पुराने जवाब (पुरानी नीति), ग़लत जवाब (UPI सवाल पर card refund वाला) या डेटा leak (एक यूज़र का order दूसरे को); अच्छा design = hit rate, ताज़गी, सही होना और अलगाव का संतुलन।

---

## 🟢 How it Works — Step by Step

### Where caches sit in a RAG/agent request

```
User query
  │ ① Exact response cache (Redis)  key = H(tenant, lang, prompt_ver, model, normalized_query, kb_version)
  │      hit → return (≈ 5–50 ms)
  │ ② Semantic cache (vector index of past Q→A, scoped by tenant/lang/kb_version)
  │      sim ≥ 0.95 + same intent → return cached answer (optionally lightly re-validated)
  ▼
  ③ Query-embedding cache (hash → vector) → retrieval-results cache (query hash + filters → doc ids, TTL)
  ▼
  ④ LLM call with PROVIDER PROMPT CACHE: [system + tools + few-shot + static docs] cached prefix
     + [retrieved chunks + user question] dynamic suffix
  ▼
  ⑤ Tool-result cache (read-only tools, short TTL: order status 15 s, menu 60 s)
  ▼
Store answer in ①/② if cacheable (non-personalized, grounded, passed guardrails)
```

### Provider prompt caching (how to structure prompts)

```
Order matters: put STABLE content first, VARIABLE content last
  [tools] → [system instructions] → [few-shot examples] → [large static docs/policies]  ← cache breakpoint
  → [per-request retrieved chunks] → [conversation] → [user question]
Anthropic: mark breakpoints with cache_control {"type": "ephemeral"} on blocks (up to a few breakpoints);
  cached prefix must match exactly; cache expires after a short TTL of inactivity (longer TTL options exist);
  cache writes cost a bit more, cache reads cost a small fraction of normal input tokens → big savings for
  long, repeated prefixes; response usage shows cache_creation_input_tokens / cache_read_input_tokens
OpenAI: automatic caching for long prompt prefixes; cached tokens billed at a discount
Tip: don't put timestamps/user names at the START of the system prompt — it breaks the shared prefix
```

### Semantic cache design

```
Candidates: FAQ-like, non-personalized questions (policies, how-to, general info)
NOT for: "where is MY order", account-specific, time-sensitive (live scores, prices), legal/medical advice
Key safety checks:
  - high similarity threshold (tune on labelled pairs: e.g., 0.95+) + same detected intent/entities
    (UPI vs card, Instamart vs Food) → avoid false hits
  - scope by tenant, language, kb_version (invalidate when docs change)
  - store answer + sources; optionally re-run cheap verification (do sources still exist?)
  - TTL & max entries; track hit precision with sampled audits
```

### Invalidation strategies

```
Versioned keys: include prompt_version, model, kb_version (bump on document re-index) → old entries die naturally
Event-driven: on policy/article update → delete related cache entries (tag by doc_id)
TTL: short for volatile (order status), longer for stable FAQs (hours/days)
Stampede protection: single-flight locks so 1,000 identical concurrent misses trigger one LLM call
```

### Measuring value

```
Hit rate per layer, ₹ saved (tokens avoided × price), latency p50/p95 hit vs miss, false-hit rate (audits),
staleness incidents; provider usage fields for prompt cache read/write tokens
```

## 🟢 कैसे काम करता है? (Hindi)
1. Request के रास्ते में caches: ① exact (tenant, भाषा, prompt version, model, साफ़ किया सवाल, KB version की key) → ② semantic (पुराने सवाल-जवाब का vector index, similarity ≥ 0.95 + वही इरादा) → ③ query embedding और retrieval नतीजों का cache → ④ LLM call में provider prompt cache → ⑤ read-only tool नतीजे (order status 15 सेकंड) → cache लायक हो तो जवाब save।
2. Prompt caching के लिए क्रम: पहले स्थिर (tools, system, उदाहरण, बड़ी नीतियाँ) — वहाँ breakpoint (`cache_control`), फिर बदलने वाला (retrieved chunks, बातचीत, सवाल); system prompt की शुरुआत में समय/नाम मत डालो — साझा prefix टूटता है; usage में cache read/write tokens दिखते हैं।
3. Semantic cache सिर्फ़ FAQ जैसे, सबके लिए एक जैसे सवालों पर — "मेरा order", खाते वाले, live कीमत/score, कानूनी/चिकित्सा पर नहीं; ऊँचा threshold, वही entities (UPI बनाम card), tenant/भाषा/KB version से scoped, TTL, audits से ग़लत मेल नापो।
4. Invalidation: key में versions (prompt, model, KB) — बदलते ही पुराने अपने-आप बेकार; document बदले तो उससे जुड़े entries हटाओ; अस्थिर डेटा का छोटा TTL; 1,000 एक जैसे miss पर एक ही LLM call (single-flight)।
5. फ़ायदा नापो: हर परत का hit rate, ₹ बचत, hit बनाम miss latency, ग़लत-hit दर, पुराने जवाब की घटनाएँ।

---

## 🟡 Real World Example

**Anthropic prompt caching (2024)** — Anthropic launched prompt caching stating it can reduce costs by up to 90% and latency by up to 85% for long prompts. Typical uses are long system prompts, many-shot examples, large documents ("chat with this 200-page PDF") and agent tool definitions reused across turns.

**OpenAI automatic prompt caching (2024)** — applies discounts on cached prompt prefixes automatically for long prompts, rewarding apps that keep stable content at the beginning.

**Semantic caching for FAQs** — support platforms use semantic caches (e.g., Redis vector search with RedisVL, GPTCache) to answer high-volume repeated questions instantly. Indian e-commerce and food apps during sales see massive repetition of "refund/cancel/delivery time" questions, ideal for scoped semantic caching with careful thresholds.

**vLLM prefix caching** — open-source inference servers reuse KV cache for shared prefixes, cutting GPU compute for self-hosted models with common system prompts, important for teams running Llama or Indic models on their own GPUs.

## 🟡 Real Example Hindi में
Anthropic ने 2024 में prompt caching लॉन्च करते हुए लंबे prompts पर ख़र्च 90% तक और latency 85% तक कम होने की बात कही — लंबे system prompts, ढेर सारे उदाहरण, 200 पन्नों की PDF, agent tool definitions; OpenAI लंबे prefixes पर अपने-आप छूट देता है।
Support platforms Redis vector search (RedisVL)/GPTCache से FAQ जैसे बार-बार आने वाले सवाल तुरंत देते हैं — भारतीय sales में "refund/cancel/delivery time" सवाल लाखों बार; self-hosted Llama/Indic models के लिए vLLM prefix caching GPU बचाता है।

---

## 🟠 My Stack Example

### Provider prompt caching with Anthropic (stable prefix cached)
```python
POLICY_DOCS = load_text("kb/refund_policy_v12.md")              # large, stable (~8k tokens)

resp = client.messages.create(
    model="claude-sonnet-5-5", max_tokens=400,
    tools=SUPPORT_TOOLS,                                         # tools are part of the cacheable prefix
    system=[
        {"type": "text", "text": SUPPORT_SYSTEM_V7},
        {"type": "text", "text": f"<policy>\n{POLICY_DOCS}\n</policy>", "cache_control": {"type": "ephemeral"}},   # breakpoint
    ],
    messages=[{"role": "user", "content": f"<sources>{retrieved}</sources>\n<question>{question}</question>"}],   # dynamic
)
u = resp.usage
log.info("cache write=%s read=%s input=%s", u.cache_creation_input_tokens, u.cache_read_input_tokens, u.input_tokens)
```

### Exact-match response cache with versioned keys + single-flight (Node + Redis)
```js
import crypto from 'node:crypto';
const norm = (s) => s.toLowerCase().normalize('NFC').replace(/\s+/g, ' ').trim();

export async function cachedAnswer({ tenantId, lang, question, kbVersion }, compute) {
  const key = 'ans:' + crypto.createHash('sha256')
    .update(JSON.stringify({ tenantId, lang, q: norm(question), kbVersion, prompt: 'support_v7', model: 'claude-sonnet-5-5' }))
    .digest('hex');
  const hit = await redis.get(key);
  if (hit) { metrics.inc('llm_cache_hit', { layer: 'exact' }); return JSON.parse(hit); }

  const lock = await redis.set(`${key}:lock`, '1', 'NX', 'EX', 30);              // single-flight
  if (!lock) { await sleep(300); const again = await redis.get(key); if (again) return JSON.parse(again); }
  const result = await compute();                                               // RAG pipeline
  if (result.cacheable) await redis.set(key, JSON.stringify(result), 'EX', 6 * 3600);
  await redis.del(`${key}:lock`);
  return result;
}
// kbVersion bumps when articles are re-indexed → old entries naturally stop being used
```

### Semantic cache with pgvector (scoped, thresholded, intent-checked)
```sql
CREATE TABLE semantic_cache (id BIGSERIAL PRIMARY KEY, tenant_id BIGINT, lang TEXT, kb_version INT, intent TEXT,
  question TEXT, answer JSONB, embedding vector(1024), created_at TIMESTAMPTZ DEFAULT now(), hits INT DEFAULT 0);
CREATE INDEX ON semantic_cache USING hnsw (embedding vector_cosine_ops);
```
```python
async def semantic_lookup(tenant_id, lang, kb_version, question):
    intent = await classify_intent(question)                        # e.g., REFUND_TIMELINE_UPI
    if intent in PERSONALIZED_INTENTS: return None                  # never cache "where is MY order"
    row = await db.fetchrow("""
        SELECT id, answer, 1 - (embedding <=> $1) AS sim FROM semantic_cache
        WHERE tenant_id=$2 AND lang=$3 AND kb_version=$4 AND intent=$5
          AND created_at > now() - interval '7 days'
        ORDER BY embedding <=> $1 LIMIT 1""", embed_query(question), tenant_id, lang, kb_version, intent)
    if row and row["sim"] >= 0.95:
        await db.execute("UPDATE semantic_cache SET hits = hits + 1 WHERE id=$1", row["id"])
        return row["answer"]
    return None
```

### Embedding cache by content hash (ingestion) & tool-result TTL cache
```python
# Embeddings: see Topic 133 (content_hash, model) → vector table
@cached(ttl_seconds=15, key=lambda user, order_id: f"order_status:{user.id}:{order_id}")   # per-user scope!
async def get_order_status_cached(user, order_id): return await orders.status(user, order_id)
```

### Cost dashboard query (savings estimate)
```sql
SELECT date_trunc('day', ts) AS day,
       sum(cache_read_tokens) * 0.9 * price_per_input_token AS est_savings_inr,       -- ~90% discount on cached reads
       avg(CASE WHEN cache_layer IS NOT NULL THEN 1 ELSE 0 END) AS any_cache_hit_rate
FROM llm_calls GROUP BY 1 ORDER BY 1 DESC;
```

---

## ⚫ Interview Questions + Answers

**Q1: What kinds of caching apply to LLM applications?**
A1: An exact-match response cache for repeated identical inputs (deterministic tasks), a semantic cache for paraphrased, non-personalized questions, provider-side prompt caching for long shared prompt prefixes (system prompts, tools, documents, examples), KV and prefix caching in self-hosted inference servers, and component caches for embeddings (by content hash), retrieval results, reranker scores and read-only tool results. Each has different hit rates and risks. Combine them with versioned keys, scoping and TTLs.

**Q2: How does provider prompt caching work and how do you maximize it?**
A2: The provider stores the processed state of a prompt prefix, so later requests with the identical prefix skip reprocessing those tokens, which are billed at a discount and with lower latency. Maximize hits by placing stable content first (tools, system instructions, few-shot examples, large reference documents) and variable content last (retrieved chunks, conversation, the question), marking cache breakpoints where required (Anthropic `cache_control`), avoiding per-request values (timestamps, names) in the prefix, and keeping traffic frequent enough relative to the cache TTL. Verify savings with the usage fields.

**Q3: What are the risks of semantic caching and how do you mitigate them?**
A3: False hits, where a semantically similar but materially different question gets a wrong answer (UPI vs card refunds, different products or cities), plus stale answers after policy changes and cross-user leakage of personalized content. Mitigate by caching only non-personalized intents, using a high, tuned similarity threshold plus an intent or entity match, scoping by tenant, language and knowledge-base version, applying TTLs and event-driven invalidation, storing sources with answers, and auditing hit precision regularly.

**Q4: How do you keep cached answers fresh?**
A4: Include versions in the cache key (prompt version, model, knowledge-base or index version) so changes automatically bypass old entries. Do event-driven invalidation when documents or policies update (delete entries tagged with the affected doc IDs). Use TTLs proportional to volatility (seconds for live statuses, hours for FAQs), and never cache time-sensitive or personalized responses globally. Monitor staleness incidents.

**Q5: Where does caching NOT make sense?**
A5: For personalized or account-specific responses (unless scoped per user with short TTLs), real-time data (live order status, prices, scores beyond seconds), creative tasks where variety is desired, safety-critical or regulated advice where every answer must reflect current context and checks, and low-repetition workloads where hit rates won't justify the complexity. In those cases, focus instead on prompt caching for the static prefix and on cost controls.

---

## 🔷 Trade-offs
✅ Exact cache: zero risk of semantic mismatch, huge savings on repeats — ❌ low hit rate for free-form text.
✅ Semantic cache: higher hit rate — ❌ false-hit risk; needs thresholds, scoping, audits.
✅ Prompt caching: big savings on long prefixes, no correctness risk — ❌ requires stable prompt structure; TTL limits.
✅ Long TTLs: more savings — ❌ staleness.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exact cache | Identical input → stored output | बिल्कुल वही सवाल → वही जवाब |
| Semantic cache | Similar query → cached answer | मिलता सवाल → पुराना जवाब |
| Prompt caching | Provider caches prompt prefix | prompt के शुरुआती हिस्से का cache |
| Cache breakpoint | Marks end of cacheable prefix | cache वाले हिस्से की सीमा |
| KV / prefix cache | Reused attention states | attention की दोबारा इस्तेमाल स्थिति |
| Cache key | Inputs identifying an entry | cache की पहचान |
| Versioned key | Key includes data/prompt versions | version वाली key |
| TTL | Expiry time | कितनी देर रहे |
| False hit | Wrong cached answer returned | ग़लत मेल |
| Single-flight | One computation for concurrent misses | एक साथ के miss पर एक काम |

---

## ⚡ 3-Line Summary
**English:**
1. Layers: exact response cache, semantic cache, provider prompt caching (stable prefix first), self-hosted KV cache, and component caches (embeddings, retrieval, tools).
2. Correctness: put every answer-affecting input in keys (prompt/model/KB versions, tenant, lang), never share personalized answers, invalidate on change, tune semantic thresholds.
3. Measure hit rates, ₹ saved, latency and false hits; prompt caching is the safest big win for long prompts.

**Hindi:**
1. परतें: exact, semantic, provider prompt caching (स्थिर हिस्सा पहले), KV cache, embeddings/retrieval/tools cache।
2. सही होना: key में सब versions, tenant, भाषा; निजी जवाब साझा नहीं; बदलाव पर invalidate; semantic threshold tune।
3. Hit rate, ₹ बचत, latency और ग़लत hits नापो; लंबे prompts के लिए prompt caching सबसे सुरक्षित बड़ा फ़ायदा।

---

## ➡️ Next Topic Suggestion
**149. Guardrails + Safety** — Faster and cheaper isn't enough: AI systems must be safe and trustworthy. Next: prompt injection, jailbreaks, PII leakage, harmful output, excessive agency, and layered guardrails.
