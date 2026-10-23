# 136. Chunking Strategies
# हिंदी में: Chunking Strategies — लंबे documents (PDF, help articles, नीतियाँ, manuals) को embed करने से पहले सही आकार के टुकड़ों (chunks) में बाँटना, ताकि search में सही और पूरा संदर्भ मिले — fixed, recursive, structure-aware, semantic chunking, overlap और metadata

---

## 🔵 Simple Definition (English)
**Chunking** splits documents into smaller pieces (chunks) that are embedded and indexed individually for retrieval. Chunk design strongly affects RAG quality:
- **Too large**: embeddings become "blurry" (many topics in one vector), retrieval is less precise, you waste context tokens and hit model input limits.
- **Too small**: chunks lose context ("it applies within 7 days": what does "it" refer to?), answers lack necessary detail, and you need more chunks per query.
Strategies:
- **Fixed-size** (by tokens or characters) with **overlap**.
- **Recursive** splitting by separators (sections → paragraphs → sentences).
- **Structure-aware**: by headings, Markdown/HTML sections, PDF layout, tables, code functions, FAQ question-answer pairs.
- **Semantic chunking**: split where embedding similarity between sentences drops, i.e. at topic shifts.
- **Hierarchical / parent-child**: retrieve small chunks, return the larger parent section.
- **Contextual chunk enrichment**: prepend the document title or section path, or an LLM-generated context summary, to each chunk.
Every chunk carries **metadata** (doc id, title, section, URL, page, language, updated_at, ACL) for filtering and citations.

## 🔵 सरल परिभाषा (Hindi)
Chunking = लंबे documents को छोटे टुकड़ों में बाँटना जिन्हें अलग-अलग embed और index किया जाता है — RAG की गुणवत्ता इसी पर बहुत टिकी है: बहुत बड़े chunks = धुंधला embedding (कई विषय एक vector में), कम सटीक खोज, tokens की बर्बादी; बहुत छोटे = संदर्भ खो जाता है ("यह 7 दिन में लागू होता है" — "यह" क्या?)।
तरीके: तय आकार (tokens) + overlap; recursive (section → paragraph → वाक्य); ढाँचे के हिसाब से (headings, tables, FAQ के सवाल-जवाब, code functions); semantic (जहाँ विषय बदले); parent-child (छोटा chunk ढूँढो, बड़ा हिस्सा लौटाओ); हर chunk में शीर्षक/section path या छोटा सारांश जोड़ना। हर chunk के साथ metadata (doc, section, URL, page, भाषा, ACL)।

---

## 🔴 Problem it Solves
Real enterprise documents are messy: 80-page policy PDFs, help centres with hundreds of articles, contracts, product manuals, tables of fees, FAQ pages, scanned forms, code repositories. Naive chunking (every 1,000 characters) causes:
- **Split facts**: "Refunds are processed within" in chunk 12 and "5–7 working days for UPI" in chunk 13, so retrieval gets half the answer.
- **Lost headers**: a chunk of a fee table without its column headers is meaningless.
- **Wrong context**: a chunk about "Gold members" retrieved for a regular user's question because the heading wasn't included.
- **Cross-document noise**: boilerplate (headers, footers, disclaimers) repeated in every chunk dominates similarity.
Good chunking gives **coherent, self-contained, well-labelled units of meaning**, which directly improves retrieval recall and precision, answer faithfulness and citation quality.

## 🔴 यह क्यों बना? (Hindi)
असली documents गड़बड़ होते हैं: 80 पन्नों की नीति PDF, सैकड़ों help लेख, contracts, manuals, fees की tables, FAQ, scanned forms, code। लापरवाह chunking (हर 1,000 अक्षर) से: तथ्य बँट जाता है ("Refund होता है" एक chunk में, "UPI के लिए 5–7 दिन में" अगले में) — आधा जवाब; table का टुकड़ा बिना column headers के बेकार; heading नहीं तो "Gold members" वाला हिस्सा आम यूज़र के सवाल पर; हर chunk में दोहराए header/footer similarity बिगाड़ें।
अच्छी chunking = पूरे, आत्मनिर्भर, अच्छे label वाले अर्थ के टुकड़े — बेहतर retrieval, सच्चे जवाब और बेहतर citations।

---

## 🟢 How it Works — Step by Step

### The ingestion pipeline

```
Source (PDF, HTML, DOCX, Markdown, Notion/Confluence, tickets, code)
 → PARSE: extract text + structure (headings, lists, tables, page numbers); OCR for scans; remove
          boilerplate (nav, footers, repeated disclaimers); normalize whitespace/Unicode (Devanagari NFC)
 → SEGMENT by structure (sections/FAQ pairs/table rows) → CHUNK within segments to target size
 → ENRICH each chunk: title, section path ("Refund Policy > UPI Payments"), doc summary/context,
          language, product, effective_date, ACL/tenant, source URL + page
 → EMBED (Topic 133) → INDEX (Topic 134) + keyword index (Topic 138)
```

### Strategy comparison

```
┌────────────────────┬──────────────────────────────────────────────┬────────────────────────────────┐
│ Strategy           │ How                                          │ Good for                       │
├────────────────────┼──────────────────────────────────────────────┼────────────────────────────────┤
│ Fixed-size + overlap│ e.g., 400–800 tokens, 10–20% overlap         │ Baseline, unstructured text    │
│ Recursive          │ split on \n\n → \n → sentence → word until    │ General docs (default in       │
│                    │ under size limit                              │ LangChain splitters)           │
│ Structure-aware    │ headings/sections, Markdown/HTML tags, PDF    │ Help centres, policies,        │
│                    │ layout, table-aware, code AST                 │ manuals, code                  │
│ FAQ / Q&A pairs    │ one chunk per question + answer               │ Support knowledge bases        │
│ Semantic           │ embed sentences, split at similarity drops    │ Long narrative docs, transcripts│
│ Parent-child       │ index small child chunks; return parent       │ Precise matching + full context│
│ (small-to-big)     │ section to the LLM                            │                                │
│ Contextual chunks  │ prepend LLM-written 1–2 line context of where │ Docs where chunks are          │
│                    │ chunk sits in the doc                         │ ambiguous out of context       │
└────────────────────┴──────────────────────────────────────────────┴────────────────────────────────┘
```

### Choosing chunk size & overlap

```
Start: ~300–800 tokens for prose, overlap 10–20% (keeps sentences that span boundaries)
Smaller (100–300) → precise facts, FAQ-like content; Larger (800–1500) → reasoning over long passages
Match embedding model max input; keep top_k × chunk_size within your context budget
Tune with a retrieval eval (recall@k, answer faithfulness) — there's no universal best size
```

### Tables, code & special content

```
Tables: keep header row with every row-group chunk; or convert each row to a sentence
        ("Plan: Gold | Delivery fee: ₹0 | Min order: ₹199"); store full table as parent
Code: split by function/class (AST), include file path & signature in metadata
Transcripts/chats: chunk by turn windows with speaker labels & timestamps
Multilingual: don't split inside Devanagari conjuncts; sentence boundaries "।" for Hindi; keep language tag
Images/diagrams: captions or vision-model descriptions as text chunks linked to the image
```

### Contextual retrieval idea

```
Chunk alone: "The limit is ₹10,000 per day."  ← limit of what?
Enriched:    "[Doc: UPI Lite FAQ > Limits] This chunk describes UPI Lite wallet limits. The limit is ₹10,000 per day."
→ embed & index the enriched text (both vector and BM25) → big retrieval gains for ambiguous chunks
(cost: one cheap LLM call per chunk at ingestion; cache the document in the prompt to save tokens)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Pipeline: source (PDF, HTML, DOCX, Notion, tickets, code) → parse (text + headings, tables, page; scans के लिए OCR; header/footer जैसा दोहराया हिस्सा हटाओ; देवनागरी Unicode normalize) → ढाँचे से हिस्से → तय आकार के chunks → enrich (शीर्षक, section path, भाषा, तारीख़, ACL, URL/page) → embed → vector + keyword index।
2. तरीके: तय आकार + overlap (शुरुआत), recursive (paragraph → वाक्य), ढाँचे वाला (headings, tables, code), FAQ में हर सवाल-जवाब एक chunk, semantic (विषय बदलने पर), parent-child (छोटा ढूँढो, बड़ा section दो), contextual (हर chunk में 1–2 line का संदर्भ)।
3. आकार: गद्य के लिए ~300–800 tokens, 10–20% overlap; छोटे chunks = सटीक तथ्य, बड़े = लंबी सोच; embedding model की सीमा और context budget का ध्यान; सही आकार retrieval eval से तय करो।
4. Tables में हर हिस्से के साथ header row (या हर row को वाक्य बनाओ); code function/class से; chats में बोलने वाले के label के साथ; हिंदी में "।" से वाक्य, संयुक्ताक्षर के बीच न काटो; images का caption/description।
5. Contextual retrieval: "सीमा ₹10,000 प्रति दिन है" अकेले में अस्पष्ट — आगे "[UPI Lite FAQ > Limits] यह हिस्सा UPI Lite की सीमा बताता है" जोड़कर embed/index करो — ingestion पर एक सस्ती LLM call प्रति chunk।

---

## 🟡 Real World Example

**Anthropic "Contextual Retrieval" (2024)** — Anthropic described prepending short, LLM-generated chunk-specific context before embedding and BM25 indexing ("Contextual Embeddings" + "Contextual BM25"). They reported that failed retrievals dropped substantially (about 49%), and by about 67% when combined with reranking, in their experiments.

**LangChain / LlamaIndex splitters** — recursive character and token splitters, Markdown/HTML header splitters, semantic splitters and parent-document retrievers became standard tools, reflecting that structure-aware chunking beats naive fixed windows for most corpora.

**Support knowledge bases (Swiggy/Zomato/banks/telecom)** — help centres are usually chunked per FAQ entry or article section with titles, product (Instamart vs Food), language and effective dates. Policy updates must replace old chunks, or bots quote outdated rules.

**Government schemes chatbots (e.g., Jugalbandi, 2023)** — AI4Bharat and Microsoft's Jugalbandi answered questions about government schemes in Indian languages over WhatsApp. That requires chunking long scheme documents into eligibility, benefits and how-to-apply sections across translated content.

## 🟡 Real Example Hindi में
Anthropic ने 2024 में "Contextual Retrieval" बताया — embed और BM25 index से पहले हर chunk में LLM से बना छोटा संदर्भ जोड़ना; उनके प्रयोगों में असफल retrievals ~49% घटे, reranking के साथ ~67%।
LangChain/LlamaIndex के recursive, Markdown header, semantic splitters और parent-document retrievers मानक बन गए; बैंक/telecom/Swiggy के help centres हर FAQ या section को chunk करते हैं (शीर्षक, product, भाषा, लागू तारीख़ के साथ) — नीति बदले तो पुराने chunks हटाने ज़रूरी; Jugalbandi (2023) ने सरकारी योजनाओं के लंबे documents को पात्रता/लाभ/आवेदन जैसे हिस्सों में बाँटकर भारतीय भाषाओं में WhatsApp पर जवाब दिए।

---

## 🟠 My Stack Example

### Structure-aware Markdown/HTML chunking with section path + token budget (Python)
```python
import re, tiktoken
enc = tiktoken.get_encoding("cl100k_base")                    # rough token counting for sizing (model-agnostic estimate)
def ntok(s): return len(enc.encode(s))

def split_markdown_sections(md: str):
    """Yield (section_path, text) using headings as boundaries."""
    path, buf = [], []
    for line in md.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            if buf: yield " > ".join(path), "\n".join(buf).strip(); buf = []
            level = len(m.group(1)); path = path[:level - 1] + [m.group(2).strip()]
        else:
            buf.append(line)
    if buf: yield " > ".join(path), "\n".join(buf).strip()

def chunk_section(text: str, max_tokens=500, overlap_tokens=60):
    paras, chunks, cur = [p for p in text.split("\n\n") if p.strip()], [], []
    for p in paras:                                            # recursive-ish: paragraphs first
        if ntok("\n\n".join(cur + [p])) <= max_tokens: cur.append(p); continue
        if cur: chunks.append("\n\n".join(cur))
        tail = enc.decode(enc.encode(chunks[-1])[-overlap_tokens:]) if chunks else ""
        cur = [tail, p] if tail else [p]
        while ntok("\n\n".join(cur)) > max_tokens:            # very long paragraph → split by sentences (incl. Hindi "।")
            sents = re.split(r"(?<=[.!?।])\s+", "\n\n".join(cur)); half = len(sents) // 2 or 1
            chunks.append(" ".join(sents[:half])); cur = [" ".join(sents[half:])]
    if cur: chunks.append("\n\n".join(cur))
    return chunks

def chunk_document(doc):                                       # doc: {id, title, url, lang, markdown, tenant_id, updated_at}
    out = []
    for section_path, text in split_markdown_sections(doc["markdown"]):
        for i, c in enumerate(chunk_section(text)):
            header = f"[{doc['title']}{' > ' + section_path if section_path else ''}]"
            out.append({"id": f"{doc['id']}#{len(out)}", "text_for_embedding": f"{header}\n{c}", "display_text": c,
                        "metadata": {"doc_id": doc["id"], "section": section_path, "url": doc["url"], "lang": doc["lang"],
                                     "tenant_id": doc["tenant_id"], "updated_at": doc["updated_at"]}})
    return out
```

### FAQ pages: one chunk per Q&A pair
```python
def chunk_faq(faqs, doc):     # faqs: [{"q": "UPI refund kab aayega?", "a": "UPI refunds reach in 5–7 working days..."}]
    return [{"id": f"{doc['id']}#faq{i}", "text_for_embedding": f"Q: {f['q']}\nA: {f['a']}", "display_text": f["a"],
             "metadata": {"doc_id": doc["id"], "question": f["q"], "lang": doc["lang"]}} for i, f in enumerate(faqs)]
```

### Tables: keep headers with each row-group
```python
def chunk_table(headers, rows, caption, rows_per_chunk=10):
    for i in range(0, len(rows), rows_per_chunk):
        lines = [" | ".join(headers)] + [" | ".join(map(str, r)) for r in rows[i:i + rows_per_chunk]]
        yield f"{caption}\n" + "\n".join(lines)               # "Delivery fee by plan\nPlan | Fee | Min order\nGold | ₹0 | ₹199 ..."
```

### Contextual chunk enrichment with a cheap model + prompt caching
```python
def contextualize(doc_text: str, chunk: str) -> str:
    r = client.messages.create(model="claude-haiku-5-5", max_tokens=80, temperature=0,
        system=[{"type": "text", "text": f"<document>\n{doc_text}\n</document>", "cache_control": {"type": "ephemeral"}}],  # cached per doc
        messages=[{"role": "user", "content": f"<chunk>{chunk}</chunk>\nWrite 1–2 sentences situating this chunk within the document "
                                              "to improve search retrieval. Output only the context."}])
    return r.content[0].text.strip() + "\n" + chunk          # embed & BM25-index this enriched text
```

### Parent-child retrieval (small-to-big)
```sql
-- children: small chunks for matching; parents: full sections returned to the LLM
CREATE TABLE kb_parents (id TEXT PRIMARY KEY, doc_id TEXT, section TEXT, text TEXT);
CREATE TABLE kb_children (id TEXT PRIMARY KEY, parent_id TEXT REFERENCES kb_parents(id), embedding vector(1024), text TEXT);
-- query: find top children, then fetch DISTINCT parents
SELECT DISTINCT p.* FROM (SELECT parent_id FROM kb_children ORDER BY embedding <=> $1 LIMIT 12) c JOIN kb_parents p ON p.id = c.parent_id LIMIT 4;
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you choose a chunking strategy for RAG?**
A1: Start from the document structure. Help centres and FAQs chunk per question or section, policies and manuals by headings, code by functions, tables with headers kept, and transcripts by speaker windows. Within segments, apply token-based recursive splitting to a target size (often 300–800 tokens with 10–20% overlap). Enrich chunks with titles and section paths (or LLM-generated context) and rich metadata. Then tune size, overlap and strategy using a retrieval evaluation set (recall@k, MRR, answer faithfulness) on real queries.

**Q2: What problems do too-large and too-small chunks cause?**
A2: Large chunks mix multiple topics, so their embeddings are less specific, retrieval precision drops, irrelevant text consumes context tokens and you may exceed embedding input limits. Small chunks lose surrounding context (pronouns, conditions, headings), retrieve fragments that don't answer the question, and require more chunks per query, increasing noise. Parent-child retrieval combines small chunks for matching with larger parents for context.

**Q3: How do you handle tables and PDFs?**
A3: Use layout-aware parsers or vision models to extract text with structure (headings, reading order, tables, page numbers), and remove repeated headers and footers. For tables, keep the header row with each chunk of rows or convert rows into self-describing sentences, and store the full table as a parent for context. Keep page numbers in metadata for citations. For scanned PDFs, use OCR with quality checks. Validate extraction on samples, because parsing errors silently poison retrieval.

**Q4: What is contextual retrieval?**
A4: Before embedding and keyword-indexing each chunk, you prepend a short description of where the chunk fits in its document (generated by an LLM given the whole document), plus the title and section path. This disambiguates chunks like "The limit is ₹10,000 per day" by adding what limit and which product. Anthropic reported large reductions in retrieval failures, especially combined with BM25 and reranking. The cost is an ingestion-time LLM call per chunk, reduced with prompt caching of the document.

**Q5: How do you keep chunks up to date when documents change?**
A5: Give chunks stable IDs derived from the document ID and position, store source version and `updated_at` in metadata, and on each document change re-parse, re-chunk and re-embed it, atomically replacing all its chunks (delete and insert or versioned upsert). Drive this from CMS webhooks or CDC with idempotent workers. Filter out expired or superseded content using effective dates, and reconcile periodically, so the assistant never cites outdated policies.

---

## 🔷 Trade-offs
✅ Small chunks: precise matches — ❌ missing context (use parent-child).
✅ Large chunks: full context — ❌ blurry embeddings, token waste.
✅ Structure-aware parsing: big quality gains — ❌ parser complexity per format.
✅ Contextual enrichment: fewer retrieval failures — ❌ ingestion LLM cost & time.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunk | Indexed piece of a document | document का टुकड़ा |
| Chunk size | Tokens per chunk | टुकड़े का आकार |
| Overlap | Shared tokens between chunks | टुकड़ों में साझा हिस्सा |
| Recursive splitting | Split by separators hierarchy | क्रम से बाँटना |
| Structure-aware | Use headings/tables/layout | ढाँचे के हिसाब से |
| Semantic chunking | Split at topic shifts | विषय बदलने पर बाँटना |
| Parent-child | Small match, big context | छोटा ढूँढो, बड़ा दो |
| Contextual retrieval | Add doc context to chunk | chunk में संदर्भ जोड़ना |
| Metadata | Chunk attributes | chunk की जानकारी |
| Boilerplate | Repeated non-content text | दोहराया बेकार text |

---

## ⚡ 3-Line Summary
**English:**
1. Chunking quality drives RAG quality: parse structure, remove boilerplate, chunk by sections/FAQ/tables/code, then size (≈300–800 tokens, 10–20% overlap) and tune with evals.
2. Enrich chunks with titles, section paths or LLM-generated context; use parent-child to match small and return big.
3. Carry metadata (doc, section, URL/page, lang, ACL, dates) for filters/citations, and atomically re-chunk on document changes.

**Hindi:**
1. RAG की गुणवत्ता chunking पर: ढाँचा पढ़ो, बेकार हटाओ, section/FAQ/table/code से बाँटो, ~300–800 tokens + overlap, evals से tune।
2. Chunks में शीर्षक/section path/संदर्भ जोड़ो; parent-child से छोटा ढूँढो, बड़ा दो।
3. Metadata साथ रखो (filters, citations), document बदले तो chunks एक साथ बदलो।

---

## ➡️ Next Topic Suggestion
**137. RAG — Full Pipeline** — Now put it all together: ingestion, retrieval, reranking, prompt assembly, generation with citations, and evaluation, for a production-grade "chat with your documents" system.
