# P06. Search Autocomplete / Typeahead (End-to-End Design)
# हिंदी में: Search Autocomplete — search box में हर अक्षर टाइप करते ही ~100 ms में सुझाव दिखाना (जैसे "bir" → biryani, biryani near me): client पर debounce, cache, keyboard/accessibility, और backend पर prefix index, ranking, personalization और data pipeline

---

## 🔵 Simple Definition (English)
**Autocomplete (typeahead)** suggests completions as the user types a query prefix, e.g. on Google, Amazon/Flipkart, Swiggy/Zomato ("bir" → "biryani", "Biryani Blues", "biryani near me").
End-to-end design has two halves:
- **Client** (web + mobile):
  - **debounce** keystrokes and **cancel stale requests** (avoid race conditions)
  - **cache** prefix results, show **recent searches**
  - highlight matched text
  - **keyboard navigation and accessibility** (ARIA combobox), mobile-friendly UI
  - analytics for suggestion clicks
- **Backend**:
  - a fast **prefix index** (trie with precomputed top-k per node, Elasticsearch completion suggester / edge n-grams, or Redis sorted sets)
  - **ranking** by popularity, recency, personalization and location
  - **typo tolerance and transliteration** (Hinglish: "paneer" ↔ "पनीर")
  - a **data pipeline** that aggregates query logs into the index (batch plus trending)
  - **caching** at edge and server so p99 stays **< 100 ms**

## 🔵 सरल परिभाषा (Hindi)
Autocomplete = यूज़र जैसे-जैसे टाइप करे, पूरे शब्द/सवाल के सुझाव दिखाना ("bir" → "biryani", "Biryani Blues")। दो हिस्से: Client — debounce (हर अक्षर पर request नहीं), पुरानी request रद्द (race से बचाव), prefix cache, recent searches, मिलते अक्षर highlight, keyboard और accessibility (ARIA combobox), click analytics; Backend — तेज़ prefix index (trie + हर node पर top-k, Elasticsearch, Redis), popularity/personalization/location से ranking, typo और Hinglish ("paneer" ↔ "पनीर"), query logs से index बनाने वाली pipeline, और cache ताकि 100 ms से कम।

---

## 🔴 Problem it Solves
Search is the highest-intent action in many apps (e-commerce, food, travel), and autocomplete:
- **Saves typing on mobile keyboards** and reduces spelling errors ("smasung", "biriyani").
- **Guides users to queries with results** (no "0 results"), and to popular or available items nearby.
- **Increases conversion** by jumping directly to entities (a restaurant, a product page).
The challenges: it fires on every keystroke (a **huge QPS multiplier**, about 5–10 requests per search), needs **< 100 ms** end-to-end to feel instant, must avoid **out-of-order results** on flaky networks, must handle **typos, transliteration and multiple languages**, must stay **fresh** for trending terms (a new movie, "IPL final") and must **filter offensive or unsafe suggestions**.

## 🔴 यह क्यों बना? (Hindi)
Search सबसे ज़्यादा इरादे वाला काम है और autocomplete: mobile keyboard पर टाइपिंग बचाता है, spelling ग़लतियाँ घटाता है ("smasung", "biriyani"), यूज़र को ऐसे सवालों पर ले जाता है जिनके नतीजे हैं, और सीधे restaurant/product पर पहुँचाकर conversion बढ़ाता है।
चुनौतियाँ: हर अक्षर पर request (एक search में 5–10 गुना QPS), 100 ms से कम चाहिए, धीमे नेटवर्क पर पुराने नतीजे बाद में आकर ग़लत न दिखें, typo/Hinglish/कई भाषाएँ, trending शब्द ("IPL final") जल्दी आएँ, और अपमानजनक सुझाव न दिखें।

---

## 🟢 How it Works — Step by Step

### 1. Requirements

```
Functional: top 5–10 suggestions per prefix; mixed types (queries, restaurants/products, categories);
            personalized (recent searches, location); typo-tolerant; Hindi/Hinglish/transliteration;
            trending updates within minutes–hours; blocklist for unsafe terms; web + mobile
Non-functional: p99 < 100 ms server, perceived < 150 ms; highly available; very high read QPS
Scale (assume): 50M searches/day × ~6 keystroke requests after debounce ≈ 300M requests/day
              ≈ 3.5k/s avg, 20k/s peak (dinner time / sale day)
```

### 2. Architecture

```
Client (debounce 150–250 ms, cache, cancel) ──► CDN/edge (cache popular prefixes, short TTL, keyed by
                                                     prefix + city + lang)
                                                ──► Suggest service (stateless, in-memory index replicas)
                                                       ├─ prefix lookup → candidates (top-k precomputed)
                                                       ├─ merge: global + city-level + trending + entity
                                                       ├─ personalization rerank (recent searches,
                                                       │   affinities) — light, < 10 ms
                                                       └─ filter (blocklist, availability/serviceability)
Data pipeline:
  search logs (Kafka) → batch job (Spark, daily/hourly): normalize queries, count by city/lang/time,
  decay old counts, join entities (restaurants/products), build trie/FST with top-k per node →
  versioned index artifact (S3) → suggest servers load & swap atomically
  Streaming (Flink): trending terms (sudden spikes in last 15–60 min) → small "trending" index merged at query time
Alternative: Elasticsearch completion suggester / search_as_you_type fields (edge n-grams) for entity suggestions
```

### 3. Prefix index: trie with top-k per node

```
            (root)
           /      \
         b          p
         |          |
         i          a
         |          |
         r          n ── top-k: [paneer tikka, paneer butter masala, pani puri]
         |
   top-k at "bir": [biryani (98k), biryani near me (40k), biryani blues (12k), biriyani→biryani]
Query "bir" → walk 3 nodes → return stored top-k → O(len(prefix)) — no subtree scan at query time
Memory: compress (FST/radix tree), limit depth (e.g., 20 chars), per-city tries or city as a ranking feature
Updates: rebuild offline and swap (immutable index) rather than mutate live
```

### 4. Ranking signals

```
score = w1·log(popularity_city) + w2·recency_decay + w3·trending_boost + w4·personal_affinity
        + w5·conversion_rate (searches that led to orders) − penalties (no-results, low availability)
Entity suggestions (restaurant/product): open now, deliverable to user's location, rating
Personalization: user's recent searches & cuisines (client-side recent list + server signals)
Diversity: mix query completions + entities + categories (e.g., 4 queries, 3 restaurants, 1 cuisine)
```

### 5. Typos, transliteration, languages

```
Normalize: lowercase, trim, Unicode NFC, remove accents; map common variants (biriyani → biryani)
Fuzzy: edit distance ≤ 1–2 for prefixes ≥ 4 chars (Elasticsearch fuzzy, SymSpell), keyboard-adjacency
Transliteration: Hinglish ↔ Devanagari ("paneer" ↔ "पनीर", "chai" ↔ "चाय") via dictionary/ML model;
  index both scripts; detect script of input
Synonyms: "cold drink" ↔ "soft drinks", "mobile" ↔ "smartphone"
```

### 6. Client details (web & mobile)

```
- Debounce 150–250 ms (or trailing + leading for first char); min length 1–2 chars
- Cancel in-flight requests when the prefix changes (AbortController) → no out-of-order results
  (or tag responses with prefix and ignore stale ones)
- In-memory LRU cache of prefix → results (and prefix extension: filter cached "bir" locally for "biry"
  while waiting for server)
- Recent searches stored locally (MMKV/localStorage), shown on focus with empty input
- Highlight matched prefix (escape HTML! XSS — render as text spans)
- Keyboard: ↑/↓ to move, Enter to select, Esc to close; ARIA combobox/listbox (F18); announce count
- Mobile: large tap targets, keyboard "search" return key, dismiss on scroll, no layout jump
- Analytics: suggestion impressions & selected position → feeds ranking (CTR)
```

### 7. Caching

```
Client cache (session) → CDN edge cache for top prefixes (1–2 char prefixes are hottest) with TTL 5–15 min,
key = prefix + city + language (not user-specific); personalization applied client-side or by a thin
personal layer → server in-memory index (no DB on the hot path)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Client: 150–250 ms debounce, prefix बदलते ही पुरानी request cancel (AbortController), prefix का LRU cache ("bir" के नतीजे "biry" के लिए local filter), focus पर recent searches, मिलते अक्षर highlight (HTML नहीं, text — XSS), ↑/↓/Enter/Esc और ARIA combobox।
2. Backend का hot path DB नहीं — memory में trie जिसमें हर node पर top-k पहले से गिने हुए: "bir" के 3 nodes चलो और सीधे top-k लौटाओ; CDN पर 1–2 अक्षर वाले लोकप्रिय prefixes 5–15 मिनट cache (prefix + शहर + भाषा)।
3. Pipeline: search logs (Kafka) → Spark (रोज़/घंटे) — normalize, शहर/भाषा के हिसाब से गिनती, पुराने को कम वज़न, restaurants/products जोड़ो → trie/FST बनाकर S3 → servers पर atomic swap; Flink से पिछले 15–60 मिनट के trending शब्द अलग छोटे index में।
4. Ranking: शहर में लोकप्रियता, ताज़गी, trending, यूज़र की पसंद, order तक पहुँचने की दर; entities के लिए "अभी खुला है", "आपके पते तक delivery", rating; queries + restaurants + cuisine का मिश्रण।
5. Typo (edit distance 1–2, "biriyani" → biryani), Hinglish ↔ देवनागरी ("paneer" ↔ "पनीर"), synonyms ("cold drink" ↔ soft drinks); अपमानजनक शब्दों की blocklist।

---

## 🟡 Real World Example

**Google Autocomplete** — suggestions are predicted from aggregated search activity, freshness/trending and location and language. Google applies policies to remove violent, hateful or harmful predictions, a reminder that moderation is part of the design.

**Amazon & Flipkart** — e-commerce autocomplete mixes query completions with category scoping ("iphone 16 in Mobiles"). Flipkart has invested in vernacular and Hinglish search and spelling correction for Indian users typing in transliterated or misspelled forms.

**Swiggy / Zomato** — search suggests dishes, cuisines and restaurants that are **open and deliverable to your location right now**, so ranking depends on real-time serviceability, not just global popularity.

**LinkedIn (Cleo) / Twitter typeahead** — both published typeahead architectures with in-memory indexes, prefix-based retrieval and personalized ranking (connections, followed accounts) under tight latency budgets.

## 🟡 Real Example Hindi में
Google Autocomplete करोड़ों searches, ताज़गी, जगह और भाषा से सुझाव देता है और हिंसक/नफ़रती सुझाव हटाने की नीति रखता है — moderation भी design का हिस्सा।
Flipkart ने Hinglish और भारतीय भाषाओं में search और spelling सुधार पर काम किया; Swiggy/Zomato सिर्फ़ वही dishes/restaurants सुझाते हैं जो अभी खुले हैं और आपके पते तक पहुँच सकते हैं; LinkedIn और Twitter ने memory वाले index + personalized ranking वाले typeahead के बारे में लिखा है।

---

## 🟠 My Stack Example

### React (web) / RN: debounced, cancellable, cached autocomplete hook
```ts
// shared/useAutocomplete.ts — works in Next.js and React Native
const cache = new Map<string, Suggestion[]>();                     // simple LRU could replace this
export function useAutocomplete(query: string, ctx: { city: string; lang: string }) {
  const [items, setItems] = useState<Suggestion[]>([]);
  const q = query.trim().toLowerCase();
  const debounced = useDebouncedValue(q, 180);

  useEffect(() => {                                                 // instant local refinement while typing
    for (let i = q.length - 1; i > 0; i--) {
      const parent = cache.get(`${ctx.city}:${ctx.lang}:${q.slice(0, i)}`);
      if (parent) { setItems(parent.filter((s) => s.text.toLowerCase().startsWith(q))); break; }
    }
  }, [q]);

  useEffect(() => {
    if (debounced.length < 1) return setItems(recentSearches());
    const key = `${ctx.city}:${ctx.lang}:${debounced}`;
    if (cache.has(key)) return setItems(cache.get(key)!);
    const ctrl = new AbortController();
    http.get<Suggestion[]>('/suggest', { params: { q: debounced, city: ctx.city, lang: ctx.lang }, signal: ctrl.signal })
      .then((r) => { cache.set(key, r.data); setItems(r.data); })
      .catch(() => {});                                             // aborted or failed → keep local items
    return () => ctrl.abort();                                      // cancel stale request → no out-of-order
  }, [debounced, ctx.city, ctx.lang]);
  return items;
}
```

### Accessible combobox UI (web)
```tsx
export function SearchBox() {
  const [value, setValue] = useState(''); const [active, setActive] = useState(-1);
  const items = useAutocomplete(value, { city: 'BLR', lang: 'en' });
  const listId = 'search-suggestions';
  return (
    <div>
      <input role="combobox" aria-expanded={items.length > 0} aria-controls={listId} aria-autocomplete="list"
        aria-activedescendant={active >= 0 ? `sugg-${active}` : undefined} value={value} placeholder="Search for dishes & restaurants"
        onChange={(e) => { setValue(e.target.value); setActive(-1); }}
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') setActive((a) => Math.min(a + 1, items.length - 1));
          if (e.key === 'ArrowUp') setActive((a) => Math.max(a - 1, 0));
          if (e.key === 'Enter' && active >= 0) select(items[active], active);
          if (e.key === 'Escape') setValue('');
        }} />
      <ul id={listId} role="listbox">
        {items.map((s, i) => (
          <li key={s.id} id={`sugg-${i}`} role="option" aria-selected={i === active} onMouseDown={() => select(s, i)}>
            <Highlight text={s.text} prefix={value} />{s.type === 'restaurant' && <small> · Restaurant · {s.etaMin} min</small>}
          </li>
        ))}
      </ul>
      <span className="sr-only" aria-live="polite">{items.length} suggestions</span>
    </div>
  );
}
const Highlight = ({ text, prefix }: { text: string; prefix: string }) => {
  const n = text.toLowerCase().startsWith(prefix.toLowerCase()) ? prefix.length : 0;
  return <span><strong>{text.slice(0, n)}</strong>{text.slice(n)}</span>;        // text nodes only → XSS-safe
};
```

### Suggest service: in-memory trie with top-k (TypeScript, built offline, loaded at startup)
```ts
class Node { children = new Map<string, Node>(); top: Entry[] = []; }
type Entry = { text: string; score: number; type: 'query' | 'restaurant' | 'cuisine'; id: string };

export class PrefixIndex {
  root = new Node();
  static build(entries: Entry[], k = 10, maxDepth = 20) {
    const idx = new PrefixIndex();
    for (const e of entries) {
      let n = idx.root;
      for (const ch of normalize(e.text).slice(0, maxDepth)) {
        n = n.children.get(ch) ?? (n.children.set(ch, new Node()), n.children.get(ch)!);
        n.top.push(e);
        if (n.top.length > k * 2) n.top = n.top.sort((a, b) => b.score - a.score).slice(0, k);  // keep top-k
      }
    }
    return idx;
  }
  lookup(prefix: string): Entry[] {
    let n: Node | undefined = this.root;
    for (const ch of normalize(prefix)) { n = n.children.get(ch); if (!n) return []; }
    return n.top.sort((a, b) => b.score - a.score);
  }
}

// HTTP handler: lookup → merge trending → filter → personalize lightly → cache headers
app.get('/suggest', async (req, res) => {
  const { q = '', city = 'BLR', lang = 'en' } = req.query as Record<string, string>;
  const base = indexes.get(`${city}:${lang}`)?.lookup(q) ?? [];
  const trending = trendingIndex.lookup(q).map((e) => ({ ...e, score: e.score * 1.5 }));
  const merged = dedupe([...trending, ...base]).filter((e) => !blocklist.has(e.text)).filter((e) => e.type !== 'restaurant' || isServiceable(e.id, req));
  res.set('Cache-Control', q.length <= 2 ? 'public, max-age=300' : 'public, max-age=60');   // CDN-friendly (no user data)
  res.json(merged.slice(0, 8).map(({ text, type, id }) => ({ text, type, id })));
});
```

### Offline pipeline: query counts → index artifact (PySpark sketch)
```python
logs = spark.read.json("s3://logs/search/date=2026-10-17/*")
counts = (logs.filter("query IS NOT NULL")
  .withColumn("q", normalize_udf("query"))
  .groupBy("city", "lang", "q").agg(F.count("*").alias("n"), F.sum("led_to_order").alias("orders"))
  .withColumn("score", F.log1p("n") * 0.7 + F.log1p("orders") * 0.3))
prev = spark.read.parquet("s3://suggest/scores/latest")            # exponential decay of history
final = blend_with_decay(prev, counts, half_life_days=14).filter("n >= 5")   # privacy: drop rare queries
final.write.parquet("s3://suggest/scores/2026-10-18")
# Builder job converts scores → per-city/lang trie artifacts → servers hot-swap
```

### Elasticsearch alternative for entity suggestions
```json
PUT restaurants
{ "mappings": { "properties": {
  "name": { "type": "search_as_you_type" },
  "name_hi": { "type": "search_as_you_type", "analyzer": "standard" },
  "location": { "type": "geo_point" }, "is_open": { "type": "boolean" }, "rating": { "type": "float" } } } }
// query: multi_match bool_prefix on name, name._2gram, name._3gram + filter is_open + geo_distance + function_score(rating)
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you keep autocomplete under 100 ms at high QPS?**
A1: Keep the hot path entirely in memory: a prebuilt prefix structure (trie, radix tree or FST) storing the top-k suggestions per node, so a lookup is O(prefix length) with no subtree scan or database call. Replicate stateless suggest servers per region, cache popular short prefixes at the CDN and edge (keyed by prefix, city and language, without user data), apply only lightweight personalization at request time, and debounce, cache and cancel on the client to cut request volume. Build indexes offline and hot-swap them.

**Q2: How do you prevent out-of-order suggestions on the client?**
A2: Cancel the previous in-flight request whenever the input changes (AbortController), and/or tag each response with the prefix it was for and ignore responses that don't match the current input. Debouncing reduces the number of requests, and a local cache gives immediate results for previously seen prefixes. Libraries like React Query handle this when the prefix is part of the query key. Never render results for an older prefix after a newer one.

**Q3: How do you update suggestions with trending queries?**
A3: Run two layers. A batch pipeline (hourly or daily) aggregates normalized query logs with decay into popularity scores and rebuilds the main index. A streaming job (Flink or Kafka Streams) detects sudden spikes over short windows (15–60 minutes) per region and maintains a small trending index merged at query time with a boost. Moderation filters both layers. Swap indexes atomically, and keep previous versions for quick rollback.

**Q4: How would you handle Indian languages and Hinglish?**
A4: Normalize input (Unicode NFC, lowercase, common spelling variants), detect the script, and index suggestions in both Latin transliteration and native scripts with transliteration mappings (dictionary plus ML), so "paneer" matches "पनीर". Add fuzzy matching tuned for common misspellings, synonyms and colloquial terms, and per-language ranking data. Show results in the user's preferred language. Build training data from query reformulations (users correcting themselves) to improve spelling correction.

**Q5: Trie vs Elasticsearch for autocomplete?**
A5: A custom in-memory trie or FST with precomputed top-k per node gives the lowest, most predictable latency for query completions at huge QPS, but requires an offline build pipeline and custom ranking logic. Elasticsearch (completion suggester, `search_as_you_type`, edge n-grams) is quicker to build and great for entity suggestions with filters (geo, open now), fuzzy matching and frequent updates, but adds cluster latency and cost under very high QPS. Many systems combine both: an in-memory index for popular queries and Elasticsearch for entity lookups.

---

## 🔷 Trade-offs
✅ Precomputed top-k trie: ultra-fast — ❌ memory heavy, offline rebuilds, less flexible filtering.
✅ Elasticsearch: flexible, fuzzy, geo filters — ❌ higher latency/cost at extreme QPS.
✅ Aggressive personalization: relevance — ❌ cacheability drops; privacy considerations.
✅ Short debounce: responsive — ❌ more requests; long debounce: fewer requests — ❌ feels laggy.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Typeahead | Suggestions while typing | टाइप करते समय सुझाव |
| Prefix | Beginning of a query | शब्द की शुरुआत |
| Trie | Prefix tree data structure | prefix पेड़ |
| Top-k per node | Precomputed best suggestions | पहले से गिने सबसे अच्छे |
| FST | Compact finite state transducer | छोटा compressed index |
| Debounce | Wait for typing pause | टाइपिंग रुकने का इंतज़ार |
| Edge n-gram | Indexed prefixes of words | शब्दों के prefix index |
| Transliteration | Script conversion (paneer↔पनीर) | लिपि बदलना |
| Trending | Sudden popularity spike | अचानक लोकप्रिय |
| Combobox | Accessible input + listbox | सुलभ सुझाव box |

---

## ⚡ 3-Line Summary
**English:**
1. Client: debounce, cancel stale requests, prefix cache + local refinement, recent searches, XSS-safe highlighting, accessible combobox.
2. Backend: in-memory trie/FST with top-k per node (or Elasticsearch for entities), merged with trending, filtered (blocklist, serviceability), lightly personalized, CDN-cached.
3. Pipeline: logs → normalized, decayed, per-city/lang scores → index artifacts hot-swapped; handle typos, synonyms and Hinglish transliteration.

**Hindi:**
1. Client: debounce, पुरानी request cancel, prefix cache, recent searches, सुरक्षित highlight, accessible combobox।
2. Backend: memory में trie (हर node पर top-k) या entities के लिए Elasticsearch, trending + filters + थोड़ा personalization, CDN cache।
3. Pipeline: logs → शहर/भाषा के scores → index बनाकर swap; typo, synonyms और Hinglish का ध्यान।

---

## ➡️ Next Topic Suggestion
**P07. YouTube — Video Player + Upload** — From text queries to heavy media: the end-to-end path of a video from a creator's phone to millions of viewers, including upload, transcoding, adaptive streaming players and analytics.
