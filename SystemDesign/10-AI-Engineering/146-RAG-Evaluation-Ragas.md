# 146. RAG Evaluation (Ragas)
# हिंदी में: RAG Evaluation — यह नापना कि आपका RAG system सही documents ढूँढ रहा है (retrieval) और उन्हीं पर आधारित सही जवाब दे रहा है (generation): context precision/recall, faithfulness, answer relevancy/correctness, eval datasets, LLM-as-judge, Ragas library और CI में evals

---

## 🔵 Simple Definition (English)
**RAG evaluation** measures the two halves of a RAG system separately and end to end:
- **Retrieval quality**: did we fetch the right context?
  - **Context recall**: does the retrieved context contain the information needed for the reference answer?
  - **Context precision**: are the retrieved chunks relevant, and ranked near the top?
  - Classic IR metrics: **hit rate / recall@k, MRR, nDCG**.
- **Generation quality**: did the answer use the context well?
  - **Faithfulness / groundedness**: are the answer's claims supported by the retrieved context (no hallucination)?
  - **Answer relevancy**: does it address the question?
  - **Answer correctness**: does it match a reference (ground-truth) answer?
  - Plus format, citation validity, tone and language.
- **System metrics**: latency, cost per answer, refusal or "I don't know" rate, escalation rate, user feedback.
**Ragas** is a popular open-source library implementing LLM-assisted RAG metrics (faithfulness, response relevancy, context precision and recall, and more) and synthetic test-set generation. Teams combine **offline evals** (a curated dataset, run in CI on every change) with **online evals** (production sampling, user feedback, LLM judges on live traces).

## 🔵 सरल परिभाषा (Hindi)
RAG evaluation दोनों हिस्से अलग-अलग और साथ में नापता है: Retrieval — सही context आया? (context recall: जवाब के लिए ज़रूरी जानकारी मिली?; context precision: आए हुए chunks प्रासंगिक और ऊपर?; recall@k, MRR, nDCG); Generation — जवाब ने context का सही इस्तेमाल किया? (faithfulness: हर दावा context से समर्थित, गढ़ा नहीं; answer relevancy: सवाल का जवाब है?; correctness: सही जवाब से मेल; format, citations, भाषा); System — latency, ख़र्च, "पता नहीं" दर, escalation, यूज़र feedback।
Ragas open-source library ये LLM-आधारित metrics और synthetic test data देती है; offline evals (हर बदलाव पर CI में) + online evals (production sampling, feedback)।

---

## 🔴 Problem it Solves
RAG systems have many knobs (chunk size, embedding model, hybrid weights, rerankers, prompts, LLM choice), and **"it looked good on five questions"** isn't evidence:
- A chunking change can **silently drop recall** for Hindi queries.
- A new prompt can **increase hallucinations** while sounding more confident.
- Switching to a cheaper model may lower **faithfulness** in subtle cases (fee calculations, eligibility rules).
- Without separate retrieval metrics, you can't tell whether a wrong answer came from **bad retrieval or bad generation**, so you fix the wrong thing.
- Stakeholders (support heads, compliance) need **quantitative evidence** before launching to millions of users.
Systematic evaluation turns RAG development into **measurable engineering**: compare variants, prevent regressions in CI, and monitor quality in production.

## 🔴 यह क्यों बना? (Hindi)
RAG में बहुत knobs (chunk आकार, embedding model, hybrid वज़न, reranker, prompt, LLM) और "5 सवालों पर अच्छा लगा" कोई सबूत नहीं: chunking बदलने से हिंदी सवालों का recall चुपचाप गिर सकता है; नया prompt ज़्यादा आत्मविश्वास से ज़्यादा गढ़ सकता है; सस्ता model fees या पात्रता नियमों में faithfulness घटा सकता है; retrieval अलग से न नापो तो पता नहीं ग़लती खोज में थी या जवाब में — ग़लत चीज़ ठीक करोगे; support/compliance प्रमुखों को launch से पहले आँकड़े चाहिए।
व्यवस्थित evaluation RAG को नापने लायक engineering बनाता है — variants की तुलना, CI में regressions रोकना, production में निगरानी।

---

## 🟢 How it Works — Step by Step

### What to measure, where failures come from

```
Question ──► RETRIEVAL ──► contexts ──► GENERATION ──► answer
              │                           │
              ├─ context_recall            ├─ faithfulness (claims ⊆ contexts)
              ├─ context_precision         ├─ answer_relevancy (addresses question)
              ├─ recall@k / MRR / nDCG     ├─ answer_correctness (vs reference)
              └─ (needs labelled relevant  └─ citation validity, format, language, tone
                  docs or reference answer)
Diagnosis grid:
  low recall + low faithfulness?  → fix retrieval first (chunking, hybrid, rerank, query rewrite)
  high recall + low faithfulness? → fix generation (prompt grounding, model, temperature, context order)
  high both + low correctness?    → reference/policy mismatch, outdated docs, ambiguous questions
```

### How LLM-assisted metrics work (intuition)

```
Faithfulness: LLM breaks the answer into atomic claims → checks each claim against retrieved context →
              score = supported_claims / total_claims
Answer relevancy: generate likely questions from the answer → embedding similarity to the original question
Context precision: for each retrieved chunk, judge if it's relevant/useful → reward relevant chunks ranked high
Context recall: split the REFERENCE answer into statements → check how many are attributable to contexts
Caveats: judges have bias & variance → use strong judge model, fixed prompts, temperature 0, calibrate
         against human labels on a sample, track judge agreement
```

### Building the evaluation dataset

```
Sources:
  1. Expert-written "golden" Q&A (support leads write 100–300 real questions + reference answers + source docs)
  2. Production logs: sample real user questions (anonymized), label a subset
  3. Synthetic generation from documents (Ragas test-set generators / LLM prompts) → human review
Coverage: languages (English, Hindi, Hinglish), product lines, easy vs multi-hop, unanswerable questions
  (to test "I don't know"), adversarial (prompt injection in docs), outdated-policy traps, numeric questions
Versioning: dataset v1, v2…; never tune on the test split (keep a held-out set)
```

### Evaluation workflow

```
OFFLINE (every PR / nightly):
  run pipeline variant on eval set → compute retrieval + generation metrics → compare to baseline →
  fail CI if faithfulness or recall drops beyond threshold → store results per version (prompt, model,
  chunking config, index snapshot)
ONLINE (production):
  sample N% traces → LLM judges (faithfulness, relevancy) asynchronously → dashboards by segment
  user signals: 👍/👎, "talk to agent" clicks, repeat questions, CSAT
  alert on drift (sudden drop after doc update or model change); route low-scoring traces to human review
```

### Thresholds & reporting

```
Example launch bar (support bot): faithfulness ≥ 0.9, context recall ≥ 0.85 on golden set,
correct "I don't know" ≥ 90% on unanswerable set, p95 latency ≤ 4 s, cost ≤ ₹0.50/answer
Report per segment (language, product, question type) — averages hide failures in Hindi or rare products
```

## 🟢 कैसे काम करता है? (Hindi)
1. Retrieval के नाप (context recall, precision, recall@k, MRR) और generation के नाप (faithfulness, relevancy, correctness, citations) अलग-अलग; recall कम = पहले retrieval सुधारो (chunking, hybrid, rerank), recall अच्छा पर faithfulness कम = generation (prompt, model, temperature), दोनों अच्छे पर जवाब ग़लत = पुराने docs या नीति का बेमेल।
2. LLM-आधारित नाप: faithfulness — जवाब को छोटे दावों में तोड़कर हर दावा context से जाँचो; relevancy — जवाब से संभावित सवाल बनाकर असली सवाल से मिलाओ; context recall — सही जवाब के कथन context में मिले?; judge का झुकाव कम करने के लिए मज़बूत judge model, temperature 0, इंसानी labels से मिलान।
3. Dataset: विशेषज्ञों के 100–300 सवाल + सही जवाब + स्रोत, production के असली (anonymized) सवाल, documents से synthetic सवाल (इंसान जाँचे); हिंदी/Hinglish, कई कदम वाले, जवाब-न-होने वाले, injection और पुरानी नीति वाले सवाल; versions रखो, test हिस्से पर tune मत करो।
4. Offline: हर PR/रात — variant चलाओ, metrics, baseline से तुलना, faithfulness/recall गिरे तो CI fail; Online: कुछ % traces पर async judges, 👍/👎, "agent से बात" clicks, drift पर alert, कम score वाले traces इंसान को।
5. Launch की शर्त तय करो (faithfulness ≥ 0.9, recall ≥ 0.85, "पता नहीं" सही ≥ 90%, p95 ≤ 4 s, ₹0.50/जवाब) और हर segment (भाषा, product) के हिसाब से report — औसत हिंदी की कमियाँ छुपा देता है।

---

## 🟡 Real World Example

**Ragas (2023)** — introduced reference-free RAG metrics (faithfulness, answer relevancy, context precision and recall) and became widely used in the open-source community and in evaluation platforms (LangSmith, Langfuse and others integrate RAG evaluators).

**Anthropic's Contextual Retrieval study (2024)** — evaluated retrieval changes with a top-20 retrieval-failure-rate metric across codebases, fiction, papers and other domains, and reported percentage improvements. It's a good example of measuring retrieval separately from generation.

**Air Canada chatbot case (2024)** — a tribunal held the airline liable after its chatbot gave incorrect refund information. It shows why faithfulness evaluation, outdated-policy tests and human review matter before deploying customer-facing answers.

**Indian support deployments (illustrative)** — teams launching bilingual help bots typically report metrics per language and product line, discovering that Hinglish queries or regional terms need targeted retrieval fixes (transliteration, synonyms) that overall averages hide.

## 🟡 Real Example Hindi में
Ragas (2023) ने बिना reference वाले RAG metrics (faithfulness, answer relevancy, context precision/recall) दिए और बहुत लोकप्रिय हुआ; LangSmith, Langfuse जैसे platforms में भी RAG evaluators; Anthropic के Contextual Retrieval अध्ययन (2024) ने retrieval को अलग से "top-20 failure rate" से नापा।
2024 में Air Canada के chatbot ने ग़लत refund जानकारी दी और tribunal ने airline को ज़िम्मेदार ठहराया — इसलिए faithfulness evals, पुरानी नीति वाले tests और इंसानी जाँच ज़रूरी; भारत में दो-भाषी help bots की टीमें भाषा/product के हिसाब से metrics देखकर Hinglish के लिए अलग सुधार (transliteration, synonyms) करती हैं।

---

## 🟠 My Stack Example

### Eval dataset format (JSONL)
```json
{"id": "q017", "question": "UPI refund kitne din mein aata hai?", "lang": "hinglish", "segment": "refunds",
 "reference": "UPI refunds are credited to the original account within 5–7 working days after cancellation.",
 "relevant_doc_ids": ["refund-policy#3"], "answerable": true}
{"id": "q101", "question": "Can I get a refund for an order from 2019?", "segment": "refunds",
 "reference": "I don't know / not covered", "relevant_doc_ids": [], "answerable": false}
```

### Run the pipeline and score with Ragas (Python; API names per Ragas 0.2+ — check your version)
```python
from ragas import EvaluationDataset, evaluate
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithReference, LLMContextRecall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_anthropic import ChatAnthropic
from langchain_voyageai import VoyageAIEmbeddings

cases = load_jsonl("evals/help_rag_v3.jsonl")
rows = []
for c in cases:
    out = run_rag(c["question"])                      # returns {"answer", "contexts": [chunk texts], "doc_ids"}
    rows.append({"user_input": c["question"], "retrieved_contexts": out["contexts"],
                 "response": out["answer"], "reference": c["reference"]})

judge = LangchainLLMWrapper(ChatAnthropic(model="claude-sonnet-5-5", temperature=0))
emb = LangchainEmbeddingsWrapper(VoyageAIEmbeddings(model="voyage-3.5"))
result = evaluate(dataset=EvaluationDataset.from_list(rows),
                  metrics=[Faithfulness(), ResponseRelevancy(), LLMContextPrecisionWithReference(), LLMContextRecall()],
                  llm=judge, embeddings=emb)
df = result.to_pandas()
print(df.groupby([c["segment"] for c in cases])[["faithfulness", "context_recall"]].mean())   # per-segment view
```

### Classic retrieval metrics without an LLM judge (fast, cheap)
```python
def retrieval_metrics(cases, k=5):
    hits, rr = 0, 0.0
    for c in cases:
        if not c["relevant_doc_ids"]: continue
        ranked = [d.doc_chunk_id for d in retrieve(c["question"], k=k)]
        positions = [i for i, d in enumerate(ranked) if d in c["relevant_doc_ids"]]
        hits += bool(positions); rr += 1 / (positions[0] + 1) if positions else 0
    n = sum(1 for c in cases if c["relevant_doc_ids"])
    return {"recall@k": hits / n, "mrr": rr / n}
```

### Custom LLM-as-judge for "correct I-don't-know" and citation validity
```python
JUDGE_SYSTEM = ("You grade a support answer. Given the question, sources and answer, return JSON: "
                '{"grounded": true|false, "says_dont_know": true|false, "citations_valid": true|false, "reason": "..."}. '
                "grounded=false if any factual claim is not supported by the sources.")
def judge(case, out):
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=200, temperature=0, system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": json.dumps({"question": case["question"], "sources": out["contexts"], "answer": out["answer"]}, ensure_ascii=False)}])
    return json.loads(r.content[0].text)
# For unanswerable cases expect says_dont_know=True; calibrate judge vs 50 human-labelled samples
```

### CI gate (GitHub Actions step)
```yaml
- name: RAG evals
  run: python evals/run.py --dataset evals/help_rag_v3.jsonl --baseline results/main.json --out results/pr.json
- name: Enforce thresholds
  run: python evals/gate.py results/pr.json --min faithfulness=0.90 --min context_recall=0.85 --max-drop 0.02
```

### Online sampling of production traces
```python
async def online_eval_worker():
    async for trace in traces.sample(rate=0.05, since="5m"):              # 5% of live answers
        scores = judge({"question": trace.question}, {"contexts": trace.contexts, "answer": trace.answer})
        await metrics.record("rag_grounded", scores["grounded"], tags={"lang": trace.lang, "product": trace.product})
        if not scores["grounded"]: await review_queue.add(trace.id, reason=scores["reason"])
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you evaluate a RAG system?**
A1: Evaluate retrieval and generation separately and end to end. For retrieval, measure context recall, precision and ranking (recall@k, MRR, nDCG) against labelled relevant documents or reference answers. For generation, measure faithfulness (claims supported by context), answer relevancy, correctness versus references, citation validity, format and language. Add system metrics (latency, cost, "I don't know" rate). Use a versioned, representative eval dataset (expert golden Q&A, sampled production questions, reviewed synthetic data, plus unanswerable and adversarial cases), run it in CI against a baseline, and monitor production with sampled LLM judges and user feedback.

**Q2: What is faithfulness and how is it measured?**
A2: Faithfulness, or groundedness, measures whether every factual claim in the answer is supported by the retrieved context, i.e. the absence of hallucination relative to sources. LLM-assisted evaluation decomposes the answer into atomic claims and asks a judge model whether each is entailed by the context. The score is the fraction of supported claims. NLI models can also be used. It's critical for support, legal and finance, where answers must reflect official documents exactly.

**Q3: How do you build an evaluation dataset when you have no labels?**
A3: Start small but real. Have domain experts write 100–200 representative questions with reference answers and source documents. Sample anonymized production queries and label a subset. Generate synthetic questions from documents with an LLM (Ragas test-set generation), covering single-hop, multi-hop and reasoning types, then have humans review. Include unanswerable, ambiguous, multilingual (Hindi, Hinglish) and adversarial cases. Version the dataset, keep a held-out test split, and grow it continuously from production failures.

**Q4: Can you trust LLM-as-judge metrics?**
A4: Partially. They scale well and correlate reasonably with human judgement when well designed, but they have biases (verbosity, position, self-preference) and variance. Mitigate with a strong judge model at temperature 0, fixed rubric prompts, decomposed checks (claim-level rather than overall), calibration against a human-labelled sample (track agreement), deterministic metrics where possible (exact-match fields, citation ID validity, retrieval recall), and spot human review, especially for launch decisions.

**Q5: How do you prevent regressions when changing prompts, models or chunking?**
A5: Treat every component as versioned configuration: prompt version, model, embedding model, chunking parameters, index snapshot. Run the offline eval suite on every PR or nightly, compare against the main baseline with per-segment metrics, and block merges when key metrics (faithfulness, context recall, correct refusals) drop beyond thresholds. Roll out behind flags with online sampling and alerting, keep the previous configuration for instant rollback, and add each production failure to the dataset.

---

## 🔷 Trade-offs
✅ LLM-assisted metrics: scalable, reference-free options — ❌ judge cost, bias, variance.
✅ Deterministic IR metrics: cheap, stable — ❌ need labelled relevant docs.
✅ Large eval sets: confidence — ❌ cost & time per run (use tiers: smoke on PR, full nightly).
✅ Online evals: real-world signal — ❌ privacy handling, delayed labels.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context recall | Needed info present in context | ज़रूरी जानकारी मिली |
| Context precision | Retrieved chunks relevant & ranked high | आए chunks प्रासंगिक |
| Faithfulness | Answer supported by context | जवाब स्रोत पर आधारित |
| Answer relevancy | Addresses the question | सवाल का जवाब |
| Answer correctness | Matches reference | सही जवाब से मेल |
| Golden dataset | Expert-labelled eval set | विशेषज्ञों का eval डेटा |
| LLM-as-judge | Model grading outputs | model से जाँच |
| Ragas | RAG evaluation library | RAG जाँच library |
| Regression gate | CI threshold check | CI में गुणवत्ता की शर्त |
| Online evaluation | Scoring live traffic | live traffic की जाँच |

---

## ⚡ 3-Line Summary
**English:**
1. Measure retrieval (context recall/precision, recall@k, MRR) separately from generation (faithfulness, relevancy, correctness, citations) to locate failures.
2. Build a versioned dataset (golden + production + reviewed synthetic, incl. unanswerable, Hindi/Hinglish, adversarial); use Ragas/LLM judges calibrated with humans.
3. Gate changes in CI against baselines per segment, and monitor production with sampled judges, user feedback and drift alerts.

**Hindi:**
1. Retrieval (recall, precision) और generation (faithfulness, relevancy, correctness) अलग नापो — ग़लती कहाँ है पता चले।
2. Versioned dataset (विशेषज्ञ + production + जाँचा synthetic, हिंदी/Hinglish, बिना-जवाब वाले); Ragas/LLM judges इंसानी labels से मिलाकर।
3. CI में baseline से तुलना करके रोक, production में sampling, feedback और drift alerts।

---

## ➡️ Next Topic Suggestion
**147. LangSmith Observability** — Evals tell you quality on a dataset. Observability tells you what's happening on every live request. Next: tracing LLM apps, metrics, feedback, prompt versioning, and tools like LangSmith and Langfuse.
