# 152. Hallucination Handling
# हिंदी में: Hallucination Handling — LLM का आत्मविश्वास से ग़लत या गढ़ी हुई बात कहना (नक़ली नीति, ग़लत राशि, न मौजूद citations) — क्यों होता है, और इसे रोकने, पकड़ने और नुक़सान सीमित करने की परतें: grounding, "पता नहीं" कहने की अनुमति, tools, verification, UX और निगरानी

---

## 🔵 Simple Definition (English)
A **hallucination** is model output that is **fluent and confident but not true or not supported** by the provided sources:
- **Factual errors**: a wrong refund timeline or fee, a non-existent feature.
- **Unsupported claims** in RAG: statements not found in the retrieved context (extrinsic), or ones that contradict it (intrinsic).
- **Fabricated references**: fake citations, URLs, case laws, API methods, order IDs.
- **Reasoning and arithmetic errors**: a wrong total, or a misapplied rule.
- **Fake actions**: claiming "I've processed your refund" when no tool succeeded.
Hallucinations come from how LLMs work: they predict likely text rather than verify truth, they're trained to be helpful (always answer), and they're affected by knowledge gaps, the knowledge cutoff, poor retrieval, long or conflicting context and sampling randomness.
**Handling** means **defence in depth**:
- **Prevention**: grounding, abstention, tools, constraints, good prompts.
- **Detection**: verification, claim checking, citation validation, validators.
- **Containment**: UX disclosure, human review, guardrails on commitments.
- **Measurement**: eval suites, online monitoring.

## 🔵 सरल परिभाषा (Hindi)
Hallucination = model का ऐसा जवाब जो धाराप्रवाह और आत्मविश्वासी हो पर सच नहीं या स्रोतों से समर्थित नहीं: ग़लत तथ्य (ग़लत refund समय/fee, न मौजूद feature), RAG में ऐसे दावे जो context में नहीं या उसके उलट, नक़ली citations/URLs/कानूनी cases/API methods, गणना/तर्क की ग़लती, और "मैंने refund कर दिया" जबकि कोई tool सफल नहीं हुआ।
कारण: LLM सच जाँचता नहीं, संभावित text बनाता है; हमेशा जवाब देने की training; ज्ञान की कमी/cutoff; ख़राब retrieval; लंबा/उलटा context; randomness। संभालना = कई परतें: रोकना (grounding, "पता नहीं", tools, सीमाएँ), पकड़ना (verification, citations जाँच, validators), नुक़सान सीमित करना (UX, इंसानी जाँच, वादों पर guardrails), और नापना।

---

## 🔴 Problem it Solves
Hallucinations are the **number one trust and liability risk** for LLM products:
- **Legal and financial liability**: a tribunal held Air Canada (2024) to refund terms its chatbot invented. Lawyers were sanctioned (Mata v. Avianca, 2023) for submitting ChatGPT-fabricated case citations.
- **Brand and market impact**: Google's Bard launch demo (Feb 2023) contained a factual error about the James Webb Space Telescope, and Alphabet's market value fell by around $100 billion that day.
- **Operational cost**: wrong answers lead to repeat contacts, refunds, escalations and angry social posts. At 1 lakh conversations a day, a 2% hallucination rate means 2,000 wrong answers daily.
- **Regulated domains**: finance (RBI, SEBI), health and legal require accuracy and accountability.
You can't eliminate hallucinations, but you can **drive the rate down, catch most of what remains, and ensure the rest can't cause serious harm**.

## 🔴 यह क्यों बना? (Hindi)
Hallucination LLM products का सबसे बड़ा भरोसे और ज़िम्मेदारी का जोखिम है: Air Canada (2024) को chatbot के गढ़े refund नियम मानने पड़े; Mata v. Avianca (2023) में वकीलों पर ChatGPT के नक़ली cases देने के लिए जुर्माना; Google Bard के launch demo (फ़रवरी 2023) में James Webb telescope वाली ग़लती के दिन Alphabet की क़ीमत ~$100 अरब गिरी; रोज़ 1 लाख बातचीत पर 2% = रोज़ 2,000 ग़लत जवाब — दोबारा संपर्क, refunds, नाराज़ posts; finance/health/legal में सटीकता ज़रूरी।
इसे शून्य नहीं कर सकते, पर दर घटा सकते हैं, बाक़ी में से ज़्यादातर पकड़ सकते हैं, और बचा हुआ गंभीर नुक़सान न कर पाए — ऐसा बना सकते हैं।

---

## 🟢 How it Works — Step by Step

### Why it happens (map causes → fixes)

```
Cause                                         Fix
────────────────────────────────────────────  ──────────────────────────────────────────────────────
Model doesn't know (private/recent data)      RAG / tools for facts; knowledge cutoff awareness
Retrieval missed the right chunk              better chunking, hybrid + rerank, query rewrite (Topics 136–139)
Prompt pressures it to answer                 explicit permission to say "I don't know" + escalation path
Context ambiguous/conflicting/outdated        effective-date filters, dedupe, "prefer latest policy", cite sources
Exact numbers/math                            tools/code compute; LLM only explains
Long context, details lost                    fewer, better chunks; key info at start/end
High temperature / creative decoding          temperature 0–0.3 for factual tasks
Free-form outputs                             structured outputs with enums, nullable unknowns (Topic 132)
Claimed actions without execution             only report actions from successful tool results (code-enforced)
```

### Prevention layer

```
1. Ground: "Answer ONLY using <sources>; cite [S#] for every factual sentence"
2. Abstain: "If the sources don't contain the answer, say you don't know and offer an agent" +
   retrieval-score threshold → skip generation & abstain when top score is low
3. Quote-first: ask the model to extract relevant quotes, then answer only from those quotes
4. Tools for facts: order status, prices, fees, refund amounts come from APIs, not model memory
5. Constrain: schemas, enums, allowed values (no invented plan names, coupon codes)
6. Low temperature; concise answers (fewer claims → fewer errors)
```

### Detection layer

```
Citation validation: every [S#] exists among provided sources; cited text actually contains the claim
Claim-level verification: split answer into atomic claims → check each against sources (NLI model or LLM
  judge) → unsupported claims → regenerate, remove, or abstain
Numeric/entity validators: amounts, dates, order IDs, coupon codes match tool/DB data
Self-consistency / multiple samples for high-stakes answers (disagreement → review)
Chain-of-Verification: draft → generate verification questions → answer them independently → revise
Action honesty check: if answer says "refund processed", a successful refund tool call must exist in trace
```

### Containment & UX

```
Show sources and "last updated" dates; allow users to open the policy
Calibrated language: "According to our refund policy [S1]…" rather than absolute claims
Easy escalation ("Talk to an agent"), feedback buttons, correction flows
High-stakes (money, health, legal): human review or approval; deterministic rules decide, LLM explains
Disclaimers where appropriate (not as a substitute for controls)
```

### Measurement

```
Offline: faithfulness / groundedness on eval sets (Topic 146), unanswerable-question abstention rate,
  numeric accuracy, citation validity
Online: sampled judge groundedness, user 👎 with "wrong info" reason, recontact within 24 h,
  escalations due to wrong info, policy-violation audits
Track by segment (language, product, intent) and after every model/prompt/index change
```

## 🟢 कैसे काम करता है? (Hindi)
1. कारण → इलाज: model नहीं जानता → RAG/tools; retrieval चूका → chunking, hybrid + rerank; prompt जवाब पर मजबूर करता → "पता नहीं" की अनुमति; उलटा/पुराना context → तारीख़ filter, नई नीति को प्राथमिकता; गणना → tools; ज़्यादा temperature → 0–0.3; खुला output → schema/enums; बिना काम किए "कर दिया" → सिर्फ़ सफल tool नतीजे पर ही बताना (code से लागू)।
2. रोकना: "सिर्फ़ sources से, हर तथ्य पर [S#]"; retrieval score कम हो तो generation छोड़कर "पता नहीं"; पहले quotes निकालो फिर उन्हीं से जवाब; राशि/status/fees APIs से; enums (गढ़े plan/coupon नहीं); छोटा जवाब = कम दावे = कम ग़लती।
3. पकड़ना: citations जाँचो (मौजूद हैं और दावा उनमें है), जवाब को छोटे दावों में तोड़कर हर दावा sources से (NLI या LLM judge) — असमर्थित हटाओ/दोबारा लिखो/"पता नहीं"; राशि, तारीख़, order ID, coupon को tool/DB डेटा से मिलाओ; बड़े फ़ैसलों पर कई samples; Chain-of-Verification; "refund हो गया" बोले तो trace में सफल refund tool ज़रूरी।
4. नुक़सान सीमित: sources और "अपडेट तारीख़" दिखाओ, "हमारी नीति के अनुसार [S1]…" जैसी भाषा, "agent से बात" आसान, पैसे/स्वास्थ्य/कानून में इंसान या पक्के नियम फ़ैसला करें और LLM सिर्फ़ समझाए।
5. नापना: offline faithfulness, बिना-जवाब सवालों पर "पता नहीं" दर, संख्याओं की सटीकता, citations; online judges, "ग़लत जानकारी" वाले 👎, 24 घंटे में दोबारा संपर्क — हर segment और हर बदलाव के बाद।

---

## 🟡 Real World Example

**Mata v. Avianca (US, 2023)** — lawyers submitted a brief citing six non-existent court cases generated by ChatGPT and were sanctioned. It's the textbook example of fabricated references and why outputs must be verified against authoritative sources.

**Air Canada chatbot (2024)** — the chatbot told a customer he could claim a bereavement fare refund retroactively, contradicting actual policy, and the tribunal held the airline responsible. It shows how grounded policy answers and commitment guardrails protect businesses.

**Google Bard demo (Feb 2023)** — a promotional answer wrongly claimed the James Webb Space Telescope took the first pictures of an exoplanet. Alphabet's shares fell sharply that day (around $100B in market value), illustrating reputational stakes.

**Chain-of-Verification (Meta AI, 2023)** — research showing that drafting, then planning and answering verification questions independently, reduces hallucinations in list and long-form generation. It's one of several verification techniques used in production pipelines.

## 🟡 Real Example Hindi में
Mata v. Avianca (2023) में वकीलों ने ChatGPT के बनाए 6 नक़ली court cases दिए और सज़ा मिली — नक़ली references का क्लासिक उदाहरण; Air Canada (2024) के chatbot ने नीति के उलट refund बताया और tribunal ने airline को ज़िम्मेदार ठहराया।
Google Bard के demo (फ़रवरी 2023) में James Webb telescope पर ग़लत दावे के दिन Alphabet के शेयर तेज़ी से गिरे (~$100 अरब); Meta के Chain-of-Verification (2023) ने दिखाया कि पहले draft, फिर अलग से जाँच वाले सवाल और जवाब से hallucinations घटते हैं।

---

## 🟠 My Stack Example

### Abstain when retrieval is weak (don't let the model guess)
```python
async def answer_or_abstain(question, user):
    top = (await rerank(question, await hybrid_search(question, user.tenant_id, user.groups, k=40)))[:5]
    if not top or top[0].score < 0.25:                        # threshold tuned on eval set (answerable vs unanswerable)
        return {"answer": "I couldn't find this in our help articles. Shall I connect you to an agent?", "abstained": True}
    return await grounded_answer(question, top)
```

### Quote-first grounded prompt
```python
GROUNDED_SYSTEM = """Answer customer questions using ONLY the provided sources.
Step 1: In <quotes>, copy the exact sentences from the sources that answer the question (with [S#]).
Step 2: In <answer>, answer concisely using only those quotes, citing [S#] after each claim.
If no quote answers the question, write <answer>NOT_FOUND</answer>."""
```

### Claim-level verification with an LLM judge (post-generation)
```python
class ClaimCheck(BaseModel):
    claims: list[dict]          # [{"claim": "...", "supported": true|false, "source": "S2"|null}]

async def verify_answer(answer: str, sources: list[Chunk]) -> ClaimCheck:
    src = "\n".join(f"[S{i+1}] {c.text}" for i, c in enumerate(sources))
    return await structured_call("claude-sonnet-5-5",
        "Split the answer into atomic factual claims. For each, say whether it is directly supported by the sources. "
        "Be strict: paraphrases are fine, additions are not.", f"<sources>{src}</sources>\n<answer>{answer}</answer>", ClaimCheck)

async def safe_answer(question, sources):
    draft = await generate_answer(question, sources)
    check = await verify_answer(draft, sources)
    unsupported = [c for c in check.claims if not c["supported"]]
    if not unsupported: return draft
    if len(unsupported) <= 1:                                  # repair once
        return await generate_answer(question, sources, extra=f"Remove or fix these unsupported claims: {unsupported}")
    return "I'm not fully sure about this. Let me connect you with an agent."   # contain
```

### Numeric & action validators against system-of-record data
```python
def validate_against_tools(answer: str, trace) -> list[str]:
    issues = []
    amounts = {int(a.replace(",", "")) for a in re.findall(r"₹\s?([\d,]+)", answer)}
    allowed = {r["amount_paise"] // 100 for r in trace.tool_results("get_refund_status", "create_refund_request")}
    if amounts - allowed - {0}: issues.append(f"Amounts not backed by tools: {amounts - allowed}")
    if re.search(r"\b(refund (has been|is) (processed|initiated)|I'?ve (raised|processed))\b", answer, re.I) \
       and not trace.succeeded("create_refund_request"):
        issues.append("Claims a refund action that did not succeed")
    return issues          # non-empty → block/repair before sending
```

### Track hallucination signals online
```sql
SELECT date_trunc('day', ts) d, lang,
       avg(CASE WHEN judge_grounded THEN 1 ELSE 0 END) AS groundedness,
       sum(CASE WHEN feedback_reason = 'wrong_info' THEN 1 ELSE 0 END) AS wrong_info_reports
FROM ai_answers WHERE ts > now() - interval '14 days' GROUP BY 1, 2 ORDER BY 1 DESC;
```

---

## ⚫ Interview Questions + Answers

**Q1: Why do LLMs hallucinate?**
A1: LLMs generate the most plausible continuation of text rather than retrieving verified facts, so when they lack knowledge (private, niche or post-cutoff information), receive poor or conflicting context, or are pressured to answer, they can produce fluent fabrications. Training that rewards helpful-sounding answers, sampling randomness, long contexts where details get lost, and tasks needing exact computation all contribute. In RAG, many hallucinations actually stem from retrieval failures that leave the model without the right evidence.

**Q2: How do you reduce hallucinations in a RAG chatbot?**
A2: Improve retrieval (chunking, hybrid search, reranking, metadata filters, query rewriting) so the right evidence is present. Instruct the model to answer only from sources with citations, and allow "I don't know", abstaining when retrieval confidence is low. Use quote-first prompting, low temperature and concise answers, and get facts like amounts and statuses from tools rather than generation. Then add post-generation checks: citation validation, claim-level verification against sources, and validators for numbers and entities. Measure faithfulness offline and online.

**Q3: How can you detect a hallucination automatically?**
A3: Decompose the answer into atomic claims and check each one's entailment against the provided sources, using an NLI model or an LLM judge with a strict rubric. Validate that cited source IDs exist and contain the cited claim. Cross-check numbers, dates, IDs and codes against tool results or databases. For high-stakes cases, sample multiple answers and flag disagreement (self-consistency), or use chain-of-verification. Verify claimed actions against the execution trace. Unsupported content triggers repair, removal, abstention or human review.

**Q4: What do you do when hallucinations can't be fully eliminated?**
A4: Contain the impact. Put deterministic systems in charge of decisions and commitments (refunds, prices, eligibility), with the LLM only explaining them. Require human review for high-stakes outputs. Show sources and dates so users can verify, use calibrated language, offer easy escalation and feedback, and monitor hallucination signals continuously, feeding failures into eval datasets and fixes. Set an acceptable risk level per use case and don't deploy in contexts where the residual risk is unacceptable.

**Q5: How is hallucination different in agents vs chat?**
A5: In agents, hallucinations can become actions: invented tool arguments (a wrong order ID), misreading tool results, claiming success after a failed call, or fabricated intermediate facts that drive later steps. Mitigations include strict tool schemas and validation, authz and policy checks in code, reporting only outcomes confirmed by tool results, verification steps before irreversible actions, human approval for high-impact actions, step limits, and traces that let you audit what actually happened versus what the model said.

---

## 🔷 Trade-offs
✅ Strict grounding & abstention: fewer hallucinations — ❌ more "I don't know", needs good retrieval.
✅ Claim-level verification: catches unsupported content — ❌ extra latency & cost (use for high-stakes or sampled).
✅ Deterministic decisions + LLM explanation: safe commitments — ❌ less flexibility.
✅ Showing sources: user trust & verification — ❌ UI complexity, exposes stale docs (keep KB fresh).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hallucination | Fluent but false/unsupported output | गढ़ा हुआ ग़लत जवाब |
| Grounding | Answers tied to sources | स्रोतों पर आधारित |
| Abstention | Saying "I don't know" | "पता नहीं" कहना |
| Faithfulness | Claims supported by context | context से समर्थित |
| Intrinsic / extrinsic | Contradicts / unsupported by source | उलटा / असमर्थित |
| Claim decomposition | Split answer into atomic claims | जवाब को दावों में तोड़ना |
| NLI / entailment | Does source imply claim? | स्रोत से दावा निकलता है? |
| Chain-of-Verification | Draft → verify → revise | बनाओ → जाँचो → सुधारो |
| Fabricated citation | Fake reference | नक़ली हवाला |
| Commitment guardrail | Block unbacked promises | बिना आधार वादे रोकना |

---

## ⚡ 3-Line Summary
**English:**
1. Hallucinations come from next-token prediction + missing/poor context + pressure to answer; many RAG hallucinations are retrieval failures.
2. Prevent (grounding, abstention thresholds, quote-first, tools for facts, schemas, low temperature) and detect (citation/claim verification, numeric & action validators, self-consistency).
3. Contain (deterministic decisions, human review, sources & escalation UX) and measure faithfulness offline/online by segment.

**Hindi:**
1. Hallucination = अगले token का अनुमान + कमज़ोर context + जवाब देने का दबाव; RAG में अक्सर retrieval की चूक।
2. रोको (grounding, "पता नहीं", quotes पहले, तथ्यों के लिए tools, schema) और पकड़ो (citations/दावों की जाँच, संख्या और action validators)।
3. नुक़सान सीमित करो (पक्के नियम फ़ैसला करें, इंसानी जाँच, sources और escalation) और faithfulness नापो।

---

## ➡️ Next Topic Suggestion
**153. Cost Optimization (Tokens)** — Quality and safety layers cost tokens. Next: the full toolkit for cutting LLM costs (routing, caching, prompt and context trimming, output control, batching, distillation) without hurting quality.
