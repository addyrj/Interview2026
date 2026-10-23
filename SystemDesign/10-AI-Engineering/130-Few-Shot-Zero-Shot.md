# 130. Few-Shot + Zero-Shot
# हिंदी में: Zero-Shot और Few-Shot Prompting — बिना उदाहरण सिर्फ़ निर्देश से काम करवाना (zero-shot) बनाम prompt में कुछ सही उदाहरण दिखाकर model को format और फ़ैसले का तरीका सिखाना (few-shot)

---

## 🔵 Simple Definition (English)
- **Zero-shot prompting**: give the model **only instructions** (and the input), with no examples. Example: "Classify this support message into one of: DELIVERY_DELAY, FOOD_QUALITY, REFUND, PAYMENT, OTHER." Modern instruction-tuned models handle many tasks well zero-shot.
- **Few-shot prompting**: include a **small number of input → output examples** (typically 2–10) in the prompt so the model infers the exact **format, style, labels and decision boundaries**. Called **in-context learning**, because the model "learns" from examples at inference time without weight updates.
- **Many-shot**: with long context windows, dozens to hundreds of examples can further improve consistency for some tasks, at higher token cost (mitigated by prompt caching).
- **Dynamic few-shot**: select the **most relevant examples per input** from a labelled bank (via embeddings similarity), instead of a fixed set.
Use few-shot when the task has **subtle judgement, a specific output style, domain jargon or a tricky format** that instructions alone don't pin down.

## 🔵 सरल परिभाषा (Hindi)
Zero-shot = सिर्फ़ निर्देश दो, कोई उदाहरण नहीं ("इस शिकायत को DELIVERY_DELAY, FOOD_QUALITY, REFUND… में से एक में बाँटो") — आजकल के models कई काम ऐसे ही कर लेते हैं।
Few-shot = prompt में 2–10 सही उदाहरण (input → output) दिखाओ ताकि model format, लहजा, labels और फ़ैसले की सीमा समझ ले (in-context learning — weights नहीं बदलते); many-shot = लंबे context में दर्जनों उदाहरण; dynamic few-shot = हर input के लिए सबसे मिलते-जुलते उदाहरण (embeddings से) चुनना। बारीक फ़ैसले, ख़ास style, domain शब्द या कठिन format हो तो few-shot।

---

## 🔴 Problem it Solves
Instructions alone are often ambiguous:
- "Classify urgency" — what counts as HIGH? Is "food cold" HIGH or MEDIUM? Is "rider rude" a delivery issue or a safety issue?
- "Write a product title" — how long? brand first? include size?
- Indian user messages mix languages ("khana thanda tha, refund chahiye"), slang and typos, and a zero-shot classifier may mislabel them.
- Output formats like specific JSON shapes, markers or tone drift without a concrete pattern.
A few well-chosen examples **demonstrate** the intended behaviour, often improving accuracy and consistency **without training a model**. It's quick to iterate, and examples are easy for domain experts (ops, support leads) to contribute.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ निर्देश अक्सर अस्पष्ट होते हैं: "urgency बताओ" — HIGH क्या है? "खाना ठंडा था" HIGH या MEDIUM? "rider बदतमीज़ था" delivery या safety? "product का title लिखो" — कितना लंबा, brand पहले? भारतीय यूज़र Hinglish, slang और typos लिखते हैं ("khana thanda tha, refund chahiye") — zero-shot ग़लत label दे सकता है।
कुछ अच्छे उदाहरण सही व्यवहार "दिखाते" हैं — model train किए बिना सटीकता और एकरूपता बढ़ती है, जल्दी सुधार होता है, और ops/support टीम भी उदाहरण दे सकती है।

---

## 🟢 How it Works — Step by Step

### Zero-shot vs few-shot vs fine-tuning

```
┌───────────────┬──────────────────────────────────┬────────────────────────┬──────────────────────┐
│ Approach      │ When                             │ Cost                   │ Iteration speed      │
├───────────────┼──────────────────────────────────┼────────────────────────┼──────────────────────┤
│ Zero-shot     │ Clear, common tasks; good evals  │ Lowest tokens          │ Instant              │
│ Few-shot      │ Subtle labels, format, style,    │ + example tokens per   │ Fast (edit examples) │
│ (2–10)        │ domain jargon, Hinglish          │ call (cacheable)       │                      │
│ Dynamic few-  │ Many categories / diverse inputs │ + retrieval step       │ Fast (grow the bank) │
│ shot          │                                  │                        │                      │
│ Many-shot     │ Long-context models, consistency │ High tokens (cache!)   │ Fast                 │
│ Fine-tuning   │ Thousands of examples, strict    │ Training + hosting;    │ Slow (retrain)       │
│ (Topic 150)   │ style, latency/cost at scale     │ shorter prompts later  │                      │
└───────────────┴──────────────────────────────────┴────────────────────────┴──────────────────────┘
Start zero-shot with good instructions → add few-shot if evals show format/judgement errors →
dynamic few-shot for breadth → fine-tune only when scale/consistency demands it
```

### Choosing good examples

```
✓ REPRESENTATIVE of real inputs (actual user messages, incl. Hinglish, typos, short/long)
✓ DIVERSE: cover each label/edge case; don't let one pattern dominate (model copies superficial cues)
✓ BALANCED labels: avoid 5 REFUND examples and 1 PAYMENT → bias toward REFUND
✓ CORRECT & CONSISTENT outputs (same format every time; experts review)
✓ Include HARD/borderline cases with the right answer (where the rule is subtle)
✓ Order: shuffle or put most relevant last (recency effects); keep the actual input after examples
✓ Wrap in tags: <example><input>…</input><output>…</output></example> — clearly separate from the real input
✗ Don't include examples identical to test set (contaminated evals)
```

### Formats for examples

```
A) Inline in one user message (simple):
   <examples> <example> input … output … </example> … </examples>
   <input>{actual}</input>
B) Multi-turn "fake" conversation: user: example input → assistant: example output → … → user: actual
   (works well for chat models; keeps format very consistent)
```

### Dynamic few-shot selection

```
Labelled bank (1,000s of examples) → embed each input → store in vector DB (pgvector)
At request: embed new input → retrieve top-k similar examples (+ ensure label diversity) → build prompt
Benefits: relevant examples for each case, scales to many categories, easy to improve (add misclassified cases)
```

### Pitfalls

```
- Over-anchoring: model copies example wording/lengths too literally → vary examples
- Label leakage via superficial patterns (e.g., all REFUND examples contain "!!!")
- Token cost: 10 examples × 200 tokens = 2k extra tokens/call → use prompt caching for static examples
- Stale examples after policy changes → version the example bank with prompts
```

## 🟢 कैसे काम करता है? (Hindi)
1. शुरुआत zero-shot से (अच्छे निर्देश + evals); evals में format या फ़ैसले की ग़लतियाँ दिखें तो few-shot; बहुत सारी श्रेणियाँ हों तो dynamic few-shot; हज़ारों उदाहरण और बड़ा पैमाना हो तो fine-tuning।
2. अच्छे उदाहरण: असली inputs जैसे (Hinglish, typos, छोटे-बड़े), हर label और कठिन case शामिल, labels संतुलित (5 REFUND और 1 PAYMENT = झुकाव), जवाब सही और एक जैसे format में, tags में अलग।
3. दो तरीके: एक message में `<examples>` या नक़ली बातचीत (user उदाहरण → assistant जवाब → … → असली सवाल)।
4. Dynamic: labelled bank के हर उदाहरण का embedding pgvector में; नए input के सबसे मिलते-जुलते k उदाहरण (अलग-अलग labels के साथ) चुनकर prompt बनाओ; ग़लत हुए cases bank में जोड़ते जाओ।
5. सावधानी: model उदाहरणों के शब्द/लंबाई की नक़ल करे, सतही संकेतों से label (सब REFUND में "!!!"), tokens का ख़र्च (स्थिर उदाहरणों पर prompt caching), नीति बदले तो उदाहरण भी बदलो (version करो)।

---

## 🟡 Real World Example

**GPT-3 paper ("Language Models are Few-Shot Learners", 2020)** — showed that large models can perform new tasks from a few in-prompt examples without fine-tuning, which launched the era of in-context learning.

**Support ticket triage (Indian consumer apps)** — classifying chats and tickets into issue categories and urgency is a common first LLM use case. Teams typically start zero-shot, then add few-shot examples covering Hinglish and vernacular phrasing ("paise kat gaye par order nahi hua" → PAYMENT_DEBITED_NO_ORDER) to fix misclassifications.

**E-commerce catalog enrichment (Flipkart/Amazon/Meesho sellers)** — generating standardized product titles and attributes from messy seller inputs uses few-shot examples per category (mobiles vs sarees vs groceries) to enforce style guides.

**Many-shot research** — studies have shown that with long-context models, increasing the number of in-context examples (dozens to hundreds) can keep improving performance on some tasks, though at higher token cost.

## 🟡 Real Example Hindi में
2020 के GPT-3 paper ("Language Models are Few-Shot Learners") ने दिखाया कि बड़े models prompt के कुछ उदाहरणों से ही नए काम कर सकते हैं — in-context learning की शुरुआत।
भारतीय ऐप्स में support tickets को श्रेणी और urgency में बाँटना आम पहला LLM काम है — zero-shot से शुरू, फिर Hinglish उदाहरण ("paise kat gaye par order nahi hua" → PAYMENT_DEBITED_NO_ORDER); Flipkart/Meesho sellers के गड़बड़ inputs से साफ़ product titles बनाने में हर category के few-shot उदाहरण।

---

## 🟠 My Stack Example

### Zero-shot classifier (baseline)
```python
LABELS = ["DELIVERY_DELAY", "FOOD_QUALITY", "MISSING_ITEM", "PAYMENT_DEBITED_NO_ORDER", "REFUND_STATUS", "RIDER_BEHAVIOUR", "OTHER"]

def classify_zero_shot(text: str) -> str:
    r = client.messages.create(model="claude-haiku-5-5", max_tokens=10, temperature=0,
        system=f"Classify the customer's message into exactly one label from: {', '.join(LABELS)}. Reply with the label only.",
        messages=[{"role": "user", "content": f"<message>{text}</message>"}])
    label = r.content[0].text.strip()
    return label if label in LABELS else "OTHER"
```

### Few-shot as multi-turn examples (static, cache-friendly)
```python
FEW_SHOT = [
    ("khana thanda tha aur packet bhi khula hua tha", "FOOD_QUALITY"),
    ("Paise kat gaye par order place nahi hua", "PAYMENT_DEBITED_NO_ORDER"),
    ("Order 45 min late hai, rider ka location move hi nahi ho raha", "DELIVERY_DELAY"),
    ("Raita nahi aaya, bill mein tha", "MISSING_ITEM"),
    ("Refund kab tak aayega? 5 din ho gaye", "REFUND_STATUS"),
    ("Delivery boy ne gaali di", "RIDER_BEHAVIOUR"),
]

def classify_few_shot(text: str) -> str:
    msgs = []
    for inp, out in FEW_SHOT:
        msgs += [{"role": "user", "content": f"<message>{inp}</message>"}, {"role": "assistant", "content": out}]
    msgs.append({"role": "user", "content": f"<message>{text}</message>"})
    r = client.messages.create(model="claude-haiku-5-5", max_tokens=10, temperature=0,
        system=[{"type": "text", "text": f"Classify into one label: {', '.join(LABELS)}. Reply with the label only.",
                 "cache_control": {"type": "ephemeral"}}],          # cache static system part
        messages=msgs)
    label = r.content[0].text.strip()
    return label if label in LABELS else "OTHER"
```

### Dynamic few-shot with pgvector (pick similar labelled examples)
```sql
CREATE TABLE labelled_examples (id BIGSERIAL PRIMARY KEY, text TEXT, label TEXT, embedding vector(1024), created_at TIMESTAMPTZ DEFAULT now());
CREATE INDEX ON labelled_examples USING hnsw (embedding vector_cosine_ops);
```
```python
def dynamic_examples(text: str, k: int = 6):
    q = embed(text)                                               # Topic 133 (e.g., Voyage/OpenAI embeddings)
    rows = db.fetch("SELECT text, label FROM labelled_examples ORDER BY embedding <=> $1 LIMIT 30", q)
    picked, seen = [], {}
    for r in rows:                                                # keep label diversity (max 2 per label)
        if seen.get(r["label"], 0) < 2: picked.append(r); seen[r["label"]] = seen.get(r["label"], 0) + 1
        if len(picked) == k: break
    return picked[::-1]                                           # most similar last (closest to the input)
```

### Measure: zero-shot vs few-shot on the same eval set
```python
evalset = load_jsonl("evals/ticket_labels.jsonl")               # 300 real tickets with expert labels
for name, fn in [("zero", classify_zero_shot), ("few", classify_few_shot)]:
    preds = [fn(e["text"]) for e in evalset]
    acc = sum(p == e["label"] for p, e in zip(preds, evalset)) / len(evalset)
    print(name, f"accuracy={acc:.2%}", per_label_f1(preds, evalset))   # also check per-label recall
```

### Node: few-shot product title normalizer
```js
const examples = [
  { in: 'samsung galaxy m14 5g 6gb 128gb blue new box pack', out: 'Samsung Galaxy M14 5G (Blue, 6GB RAM, 128GB Storage)' },
  { in: 'redmi note13 pro 8/256 black', out: 'Redmi Note 13 Pro (Black, 8GB RAM, 256GB Storage)' },
];
const content = `<examples>${examples.map((e) => `<example><input>${e.in}</input><output>${e.out}</output></example>`).join('')}</examples>
<input>${sellerTitle}</input>`;
const r = await anthropic.messages.create({ model: 'claude-haiku-5-5', max_tokens: 60, temperature: 0,
  system: 'Rewrite the seller product title into the marketplace format shown in examples. Output only the title.',
  messages: [{ role: 'user', content }] });
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between zero-shot and few-shot prompting?**
A1: Zero-shot gives only instructions and the input, relying on the model's instruction-following ability. It's cheapest and fine for clear, common tasks. Few-shot adds a handful of input-output examples in the prompt so the model infers the exact format, labels, style and decision boundaries through in-context learning, which typically improves consistency for subtle or domain-specific tasks at the cost of extra tokens. Neither updates model weights.

**Q2: How do you pick few-shot examples?**
A2: Use real, representative inputs (including messy, multilingual and edge cases), cover every label or behaviour with balanced counts, and make outputs correct and consistently formatted, reviewed by domain experts. Include borderline cases that demonstrate the rule, vary superficial features so the model doesn't latch onto them, and order examples thoughtfully (the most relevant near the input). Keep them separate from evaluation data. Measure on an eval set whether each example set helps.

**Q3: What is dynamic few-shot and when would you use it?**
A3: Instead of a fixed example set, you keep a labelled example bank, embed inputs, and for each new request retrieve the most similar examples (with constraints like label diversity) to include in the prompt. It's useful with many categories or diverse inputs, where a fixed small set can't cover everything. It improves relevance and lets teams fix errors by adding misclassified cases to the bank, at the cost of an extra retrieval step and less cacheable prompts.

**Q4: When should you move from few-shot to fine-tuning?**
A4: When you have thousands of high-quality labelled examples, need very consistent output style or behaviour that prompts can't reliably achieve, prompts with many examples become too costly or slow at your volume, or you want to use a smaller, cheaper model with comparable quality. Fine-tuning has costs: data preparation, training, evaluation, hosting, and retraining when requirements change. Evaluate first whether better prompts, dynamic examples or RAG solve the issue.

**Q5: What are the risks of few-shot prompting?**
A5: The model may overfit to surface features of examples (copying lengths, wording or punctuation), become biased toward over-represented labels, or misapply examples to dissimilar inputs. Examples add tokens to every call (higher cost and latency, partly mitigated by caching), can become stale when policies change, and may leak sensitive data if real user messages aren't anonymized. Mitigate with diverse, balanced, anonymized, versioned examples and continuous evaluation.

---

## 🔷 Trade-offs
✅ Zero-shot: cheapest, simplest — ❌ less control over format/judgement.
✅ Few-shot: big accuracy/consistency gains quickly — ❌ token cost, bias risk.
✅ Dynamic few-shot: relevant examples at scale — ❌ retrieval infra, less caching.
✅ Many-shot: strong consistency — ❌ high tokens (cache), latency.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Zero-shot | Instructions only, no examples | बिना उदाहरण |
| Few-shot | A few examples in prompt | कुछ उदाहरणों के साथ |
| In-context learning | Learning from prompt examples | prompt से सीखना |
| Many-shot | Dozens/hundreds of examples | बहुत सारे उदाहरण |
| Dynamic few-shot | Retrieve examples per input | हर input के हिसाब से उदाहरण |
| Example bank | Labelled examples store | उदाहरणों का भंडार |
| Label balance | Even coverage of classes | श्रेणियों का संतुलन |
| Over-anchoring | Copying example surface cues | उदाहरण की नक़ल |
| Eval set | Held-out test cases | जाँच के अलग उदाहरण |
| Prompt caching | Reuse static prompt prefix | स्थिर हिस्सा दोबारा इस्तेमाल |

---

## ⚡ 3-Line Summary
**English:**
1. Zero-shot = instructions only; few-shot = add 2–10 examples so the model infers format, labels and judgement (in-context learning).
2. Good examples are real, diverse, balanced, correct, tagged and include borderline cases; dynamic few-shot retrieves similar examples from a labelled bank.
3. Measure on eval sets, cache static examples, version example banks, and consider fine-tuning only at scale with lots of data.

**Hindi:**
1. Zero-shot = सिर्फ़ निर्देश; few-shot = 2–10 उदाहरण ताकि model format, labels और फ़ैसला समझे।
2. अच्छे उदाहरण असली, विविध, संतुलित, सही; dynamic few-shot से हर input के मिलते-जुलते उदाहरण।
3. Evals से नापो, स्थिर उदाहरण cache करो, versions रखो; fine-tuning सिर्फ़ बड़े पैमाने पर।

---

## ➡️ Next Topic Suggestion
**131. Chain of Thought** — Some tasks need the model to reason before answering. Next: chain-of-thought prompting, separating reasoning from answers, self-consistency, reasoning models and when step-by-step thinking is worth the extra tokens.
