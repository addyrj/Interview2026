# 122. Search System (Web Search like Google)
# हिंदी में: Search System — इंटरनेट के अरबों पन्ने crawl करना (पढ़ना), उनका index बनाना, और यूज़र की query पर milliseconds में सबसे सही नतीजे क्रम (ranking) में दिखाना

---

## 🔵 Simple Definition (English)
Design a **web search engine**: a **crawler** discovers and downloads billions of web pages; a **processing/indexing pipeline** parses content, extracts links and text, and builds a massive distributed **inverted index**; a **ranking system** combines **relevance** (BM25/learned models), **authority** (PageRank-style link analysis), **freshness** and **user signals**; a **query serving** system answers queries in **< 200 ms** by fanning out to index shards and merging results; plus **autocomplete**, **spell correction** and **snippets**.
(The same principles apply to product search, site search and log search at smaller scale; see Topic 53a.)

## 🔵 सरल परिभाषा (Hindi)
Search engine के हिस्से: crawler अरबों web pages ढूँढकर download करता है; indexing pipeline उनसे शब्द और links निकालकर inverted index बनाती है; ranking सबसे relevant और भरोसेमंद pages ऊपर रखती है (PageRank, BM25, ML); और query serving सैकड़ों index टुकड़ों से 200 ms में नतीजे जोड़कर दिखाती है। साथ में autocomplete और spelling सुधार।

---

## 🔴 Problem it Solves
- The web has **hundreds of billions of pages**, constantly changing; no one can browse it manually.
- Users type 2–3 words and expect the **best answer first**, in a fraction of a second.
- Scanning documents per query is impossible, so you need **precomputed indexes**.
- Spam/SEO manipulation, duplicates, freshness (news within minutes) and many languages (Hindi, Hinglish!).

## 🔴 यह क्यों बना? (Hindi)
इंटरनेट पर सैकड़ों अरब पन्ने हैं जो बदलते रहते हैं; यूज़र 2-3 शब्द लिखकर सेकंड के छोटे हिस्से में सबसे अच्छा जवाब पहले चाहता है। हर query पर सारे पन्ने पढ़ना नामुमकिन — इसलिए पहले से बना index चाहिए; साथ में spam, duplicate pages, ताज़ा ख़बरें और कई भाषाएँ।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional: crawl web, index text/links/metadata, keyword search with ranked results + snippets,
            autocomplete, spell correction, (images/news/local verticals out of scope)
Non-functional: query latency p99 < 200–300 ms, very high QPS (100k+), fresh index for news (minutes)
                and broad index (days), highly available, relevant & spam-resistant
```

### 2. Estimation

```
Index 50B pages × 100 KB raw HTML = 5 PB raw; compressed text + index ~ 1 PB+ (sharded)
Crawl: refresh 5B pages/day ≈ 58k pages/s fetched (politeness-limited per host)
Queries: 100k QPS peak; each query touches all index shards (fan-out) → thousands of machines
```

### 3. High-level architecture

```
 ┌──────────────── OFFLINE / NEAR-LINE ────────────────┐      ┌──────────── ONLINE ─────────────┐
 Seed URLs → URL Frontier (priority + politeness queues) │      │ User query                       │
     │          ▲ new links                             │      │   ▼                              │
     ▼          │                                       │      │ Query frontend (spell, parse,    │
 Fetchers (distributed, robots.txt, rate per host)      │      │   synonyms, intent)              │
     ▼                                                  │      │   ▼                              │
 Raw page store (object storage / Bigtable)             │      │ Root/aggregator ── fan-out ──►   │
     ▼                                                  │      │   index shard servers (×1000s)   │
 Parse → dedupe (simhash) → extract text, links, lang   │      │   each: top-K from local index   │
     ▼                     │                            │      │   ◄── merge, re-rank (ML),       │
 Link graph → PageRank batch                            │      │       snippets from doc store    │
     ▼                     ▼                            │      │   ▼                              │
 Indexer: build inverted index segments (sharded) ──────┼─────►│ Results (+ caching of popular    │
                                                        │      │   queries)                       │
 └──────────────────────────────────────────────────────┘      └──────────────────────────────────┘
```

### 4. Crawler deep dive

```
URL frontier: priority by importance (PageRank, change frequency) + per-host queues for politeness
Politeness: obey robots.txt, crawl-delay; limit concurrent requests per domain
Dedup URLs: normalize (lowercase host, strip fragments/tracking params), Bloom filter of seen URLs
Dedup content: simhash/minhash for near-duplicate pages (mirrors, printer versions)
Freshness: recrawl frequency per page (news sites minutes, static pages weeks), sitemaps, ping APIs
Traps: infinite calendars/URL params → limits per host/path depth
Rendering: some pages need JS rendering (headless browser) — expensive, prioritized
```

### 5. Index deep dive (Topic 53a at web scale)

```
Inverted index: term → posting list [(docId, term frequency, positions, field flags)...]
  sorted by docId → compressed (delta + varint/PForDelta) → intersect fast (skip lists)
Sharding:
  Document-partitioned ⭐ (each shard has full index for a subset of docs)
     → query goes to ALL shards; each returns local top-K; merge   (Google, Elasticsearch)
  Term-partitioned (each shard owns some terms) → fewer shards per query but hot terms & multi-term joins hard
Replicas per shard for QPS + availability; tiered index (high-quality docs in fast tier first)
Index updates: big batch rebuilds + incremental/real-time index for fresh content (news), merged at query time
```

### 6. Ranking

```
Stage 1 (cheap, on each shard): retrieve candidates with BM25 + static quality score (PageRank,
         spam score, freshness) → top 1,000
Stage 2 (expensive, at aggregator): learning-to-rank / neural models with hundreds of features:
         query-doc relevance, term proximity, title/anchor text matches, user engagement (CTR, dwell),
         freshness for time-sensitive queries, location/language, page speed/mobile-friendliness
PageRank: page importance from link graph (iterative: PR(A) = (1−d) + d × Σ PR(T)/C(T))
Anti-spam: link farm detection, content quality classifiers
```

### 7. Query serving & latency

```
Query processing: tokenize, normalize, spell-correct ("biryni" → "biryani"), synonyms, transliteration
  (Hinglish), intent detection (navigational/informational/local)
Fan-out to all shards in parallel with tight deadlines; tail tolerance: hedged requests (send to 2 replicas,
  use first), partial results if a shard is slow (graceful degradation)
Caching: result cache for popular queries (head queries repeat a lot); posting-list cache in RAM
Snippets: fetch doc text from doc store, highlight query terms
```

### 8. Autocomplete
```
Prefix → top suggestions from query logs (popularity, freshness, personalization), filtered for safety
Data structure: trie / FST with top-K per node, or Elasticsearch completion suggester; served from memory
Update suggestions periodically (trending queries) — see P06 Typeahead for full design
```

## 🟢 कैसे काम करता है? (Hindi)
1. Crawler: URL frontier (महत्व के हिसाब से क्रम + हर साइट पर धीमे-धीमे), robots.txt का पालन, duplicate URLs/pages हटाना (Bloom filter, simhash), ज़रूरी pages बार-बार crawl।
2. Indexing: pages से शब्द और links निकालकर inverted index (शब्द → documents की सूची), दस्तावेज़ों के हिसाब से हज़ारों shards में।
3. Ranking दो चरण: हर shard BM25 + PageRank से 1000 अच्छे candidates; फिर aggregator ML model (CTR, ताज़गी, भाषा, mobile) से अंतिम क्रम।
4. Query: spelling सुधार, Hinglish समझना, सारे shards पर एक साथ, धीमे shard का इंतज़ार नहीं (hedged requests), popular queries का cache।
5. Autocomplete: पुरानी queries से prefix के top सुझाव, memory में trie से।

---

## 🟡 Real World Example

**Google** — the original PageRank paper (1998) and the BigTable/MapReduce/GFS papers describe the crawl and index infrastructure. Today Google serves billions of queries per day with ML ranking (RankBrain, BERT) and a real-time index ("Caffeine", 2010) for fresh content.

**Bing, Yandex, Baidu** — similar architectures, with document-partitioned indexes and multi-stage ranking.

**Common Crawl** — an open dataset of billions of crawled pages, often used to train language models and to study crawling.

**Product search at Flipkart/Amazon** — the same inverted index plus learning-to-rank ideas, with commerce signals (sales, conversion, price, availability) and query understanding for Indian languages and transliterations.

## 🟡 Real Example Hindi में
Google का PageRank paper (1998) और BigTable/MapReduce papers crawl-index ढाँचा बताते हैं; आज ML ranking (BERT) और ताज़ा content के लिए real-time index (Caffeine)।
Flipkart/Amazon की product search भी यही inverted index + ML ranking है — बिक्री, conversion, कीमत, stock और Hindi/Hinglish query समझने के साथ।

---

## 🟠 My Stack Example

### Tiny polite crawler (Node) — frontier, robots, dedup
```js
import robotsParser from 'robots-parser';
const seen = new BloomFilter(10_000_000, 0.001);          // Topic 53
const perHostNextAllowed = new Map();

async function crawlOne(url) {
  const u = normalize(url);                               // lowercase host, strip #, utm_*
  if (seen.mightContain(u)) return; seen.add(u);
  const host = new URL(u).host;
  const robots = await robotsFor(host);                   // cached robots.txt
  if (!robots.isAllowed(u, 'MyBot')) return;
  const wait = (perHostNextAllowed.get(host) ?? 0) - Date.now();
  if (wait > 0) return frontier.requeue(u, wait);         // politeness
  perHostNextAllowed.set(host, Date.now() + (robots.getCrawlDelay('MyBot') ?? 1) * 1000);

  const res = await fetch(u, { headers: { 'User-Agent': 'MyBot/1.0 (+https://myapp.com/bot)' }, signal: AbortSignal.timeout(10_000) });
  if (!res.ok || !res.headers.get('content-type')?.includes('text/html')) return;
  const html = await res.text();
  await rawStore.put(sha256(u), html);                    // S3
  const { text, links, title } = parseHtml(html, u);
  await indexQueue.add('index', { url: u, title, text, simhash: simhash(text) });
  for (const l of links) frontier.add(l, priorityOf(l));
}
```

### Indexing & querying with Elasticsearch / OpenSearch (site-scale search engine)
```js
await es.indices.create({ index: 'pages_v1', mappings: { properties: {
  url: { type: 'keyword' }, title: { type: 'text', analyzer: 'english' }, body: { type: 'text', analyzer: 'english' },
  pagerank: { type: 'rank_feature' }, updated_at: { type: 'date' }, lang: { type: 'keyword' } } } });

const r = await es.search({ index: 'pages', size: 10, query: { bool: {
  must: { multi_match: { query: q, fields: ['title^3', 'body'], fuzziness: 'AUTO' } },
  should: [{ rank_feature: { field: 'pagerank', boost: 2 } },
           { distance_feature: { field: 'updated_at', pivot: '30d', origin: 'now' } }] } },
  highlight: { fields: { body: { fragment_size: 160, number_of_fragments: 1 } } } });     // snippets
```

### PageRank (Python, small graph, power iteration)
```python
def pagerank(links: dict[str, list[str]], d=0.85, iters=30):
    nodes = set(links) | {v for vs in links.values() for v in vs}
    pr = {n: 1 / len(nodes) for n in nodes}
    for _ in range(iters):
        new = {n: (1 - d) / len(nodes) for n in nodes}
        for src, outs in links.items():
            for dst in outs:
                new[dst] += d * pr[src] / len(outs)
        pr = new
    return pr
# At web scale: Spark/MapReduce over the link graph, recomputed periodically
```

### Query service: cache head queries + timeouts (FastAPI)
```python
@app.get("/search")
async def search(q: str, page: int = 1):
    key = f"serp:{normalize(q)}:{page}"
    if (hit := await r.get(key)):
        return json.loads(hit)
    corrected = spell.correct(q)                            # "biryni" → "biryani"
    results = await asyncio.wait_for(search_backend(corrected, page), timeout=0.25)
    payload = {"query": q, "corrected": corrected if corrected != q else None, "results": results}
    await r.set(key, json.dumps(payload), ex=300)
    return payload
```

---

## ⚫ Interview Questions + Answers

**Q1: Describe the main components of a web search engine.**
A1: A crawler (URL frontier with prioritization and per-host politeness, distributed fetchers, robots.txt compliance, URL and content dedup) feeds a processing pipeline (parsing, language detection, near-duplicate detection, link extraction), which builds a sharded inverted index and computes link-based authority (PageRank). A multi-stage ranking system and a query-serving layer (query understanding, fan-out to index shards with deadlines, merging, re-ranking, snippets, caching) answer queries, with autocomplete and spell correction on the side.

**Q2: How is the index partitioned and queried at scale?**
A2: Usually by document: each shard holds the full inverted index for a subset of documents, replicated for throughput. A query is sent to every shard in parallel. Each computes a local top-K using cheap scoring, and an aggregator merges results and applies expensive ML re-ranking to the top candidates. Term partitioning reduces per-query fan-out but suffers from hot terms and expensive multi-term intersections across machines. Tail latency is handled with replicas, hedged requests and partial results.

**Q3: How does PageRank work, and is it enough for ranking?**
A3: PageRank models a random surfer: a page's importance is the probability of landing on it, computed iteratively from inbound links weighted by the linking pages' rank divided by their out-degree, with a damping factor. It measures query-independent authority. Alone it's insufficient. Modern ranking combines query relevance (BM25, term proximity, field matches, semantic and neural matching), freshness, user engagement signals, page quality and spam signals, and personalization, learned with ranking models.

**Q4: How would you make the crawler polite and efficient?**
A4: Respect robots.txt and crawl-delay, and identify the bot with a user agent and contact URL. Use per-host queues so each domain gets limited concurrency and a minimum delay between fetches. Prioritize URLs by importance and change frequency, normalize and dedupe URLs (with Bloom filters), and detect near-duplicate content (simhash). Avoid crawler traps with path-depth and per-host limits, use conditional GETs (ETag, If-Modified-Since) to skip unchanged pages, and use sitemaps for discovery.

**Q5: How do you keep search results fresh for news?**
A5: Maintain a separate real-time or incremental index for recently crawled content, fed by high-frequency crawling of news sources, feeds, sitemaps and pings. The query layer merges results from the fresh index and the main (batch-built) index, and the ranking model boosts freshness for time-sensitive queries (detected by query intent and spikes). The main index is rebuilt or merged in batches over time.

---

## 🔷 Trade-offs
✅ Document partitioning: simple, balanced — ❌ every query hits all shards (tail latency).
✅ Multi-stage ranking: quality at acceptable cost — ❌ complex ML infrastructure.
✅ Frequent recrawl: freshness — ❌ bandwidth/politeness costs; prioritize smartly.
✅ Result caching: cheap head queries — ❌ staleness, personalization limits caching.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Crawler | Program fetching web pages | web pages लाने वाला प्रोग्राम |
| URL frontier | Queue of URLs to crawl | crawl होने वाले URLs की कतार |
| Politeness | Limiting load on each site | हर साइट पर कम बोझ |
| robots.txt | Site's crawl rules | साइट के crawl नियम |
| Inverted index | Term → documents | शब्द → documents |
| Posting list | Docs containing a term | किसी शब्द वाले documents |
| PageRank | Link-based importance score | links से महत्व |
| BM25 | Text relevance scoring | टेक्स्ट relevance score |
| Learning to rank | ML-based ranking | ML से क्रम |
| Simhash | Near-duplicate detection hash | लगभग एक जैसे pages पहचानना |

---

## ⚡ 3-Line Summary
**English:**
1. Crawler (prioritized, polite frontier, dedup) → parsing & link graph → sharded inverted index + PageRank.
2. Queries: understand (spell, synonyms) → fan out to document-partitioned shards → local top-K → ML re-rank → snippets; cache head queries.
3. Freshness via real-time index merged at query time; handle spam, duplicates and tail latency (hedging, partial results).

**Hindi:**
1. Crawler (प्राथमिकता, धीमे-धीमे, dedup) → parsing और link graph → shards वाला inverted index + PageRank।
2. Query: समझो → सारे shards → local top-K → ML ranking → snippets; popular queries cache।
3. ताज़गी के लिए real-time index; spam, duplicates और धीमे shards संभालो।

---

## ➡️ Next Topic Suggestion
**123. Real-Time IoT Platform** — From web pages to devices: next, an IoT platform ingesting telemetry from millions of devices (MQTT, time-series storage, rules engine, device commands and OTA updates).
