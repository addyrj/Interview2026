---

# 182. RAG vs Fine-tuning
# हिंदी में: RAG बनाम Fine-tuning

---

## 🔵 Simple Definition (English)
RAG gives the model knowledge at question time by retrieving documents and putting them in the prompt. Fine-tuning changes the model's weights by training on examples, so it learns a style, a format or a skill. Simple rule: RAG is for knowledge (facts that change), fine-tuning is for behaviour (how to answer). They can be combined.

## 🔵 सरल परिभाषा (Hindi)
RAG सवाल के समय documents खोजकर prompt में डालकर model को knowledge देता है। Fine-tuning examples पर training करके model के weights बदलता है, ताकि वह style, format या skill सीखे। सरल नियम: RAG knowledge (बदलने वाले facts) के लिए, fine-tuning behaviour (जवाब कैसे दें) के लिए। दोनों साथ भी इस्तेमाल हो सकते हैं।

---

## 🔴 Problem it Solves
- Teams ask "should we fine-tune the model on our tariff documents?" - usually the wrong tool for facts: weights are a poor database, hard to update, cannot cite sources, and still hallucinate.
- Teams also over-use RAG for problems that need consistent output style or a narrow task skill, then pay for long prompts forever.
- Picking the right approach saves months and money.

## 🔴 यह क्यों बना? (Hindi)
- Teams पूछती हैं "क्या हम tariff documents पर model fine-tune करें?" - facts के लिए अक्सर गलत tool: weights खराब database हैं, update करना कठिन, source cite नहीं कर सकते, और hallucination फिर भी रहता है।
- कई teams उन समस्याओं पर भी RAG लगा देती हैं जिन्हें consistent style या narrow skill चाहिए, और लंबे prompts का पैसा हमेशा देती हैं।
- सही तरीका चुनने से महीनों और पैसे बचते हैं।

---

## 🟢 How it Works — Step by Step

```
RAG
Step 1 → Chunk and embed documents once; store in a vector DB
Step 2 → At query time: embed question, retrieve top-k chunks
Step 3 → Put chunks + question in the prompt; model answers from them
Step 4 → Update knowledge = update the index (minutes, no training)

FINE-TUNING
Step 1 → Collect hundreds to thousands of (input -> ideal output) examples
Step 2 → Train the model (provider API or LoRA on open models)
Step 3 → Get a new model id; call it like any model
Step 4 → Update behaviour = collect new data and train again (hours, cost, evaluation)

DECIDE
Step 5 → Knowledge changes often / needs citations / private docs   -> RAG
Step 6 → Need fixed format, tone, classification skill, shorter prompts -> fine-tune
Step 7 → Both (domain-specific behaviour + fresh facts)               -> fine-tuned model + RAG
```

## 🟢 कैसे काम करता है? (Hindi)
```
RAG
Step 1 → Documents को एक बार chunk + embed करके vector DB में रखो
Step 2 → Query पर: question embed करो, top-k chunks लाओ
Step 3 → Chunks + question prompt में डालो; model उन्हीं से जवाब देता है
Step 4 → Knowledge update = index update (मिनट, training नहीं)

FINE-TUNING
Step 1 → सैकड़ों से हज़ारों (input -> ideal output) examples इकट्ठा करो
Step 2 → Model train करो (provider API या open models पर LoRA)
Step 3 → नया model id मिलता है; सामान्य model की तरह call करो
Step 4 → Behaviour update = नया data + दोबारा training (घंटे, cost, evaluation)

फैसला
Step 5 → Knowledge बदलता है / citations चाहिए / private docs -> RAG
Step 6 → Fixed format, tone, classification skill, छोटे prompts -> fine-tune
Step 7 → दोनों -> fine-tuned model + RAG
```

---

## 🟡 Real World Example
**Tariff Classification System**:
- "What is the duty on 8517.13.00 from April 2025?" - a fact that changes every budget: RAG. Fine-tuning would freeze last year's rate in the weights.
- "Always answer in our JSON schema with hs_code, confidence, reasoning in 3 bullet points" - a behaviour: few-shot prompting first, fine-tune if the prompt becomes long or the model still breaks the format.
- "Classify 1M product descriptions into HS chapters cheaply" - a narrow skill at scale: fine-tune a small model on 10K labelled descriptions, then use RAG only for the ambiguous ones.

**Zomato style**: Menu and price facts - RAG. Brand voice for customer replies - fine-tune or prompt.

## 🟡 Real Example Hindi mein
**Tariff System**:
- "April 2025 से 8517.13.00 की duty?" - हर budget में बदलने वाला fact: RAG। Fine-tuning पिछले साल की rate weights में जमा कर देगा।
- "हमेशा हमारे JSON schema में जवाब दो" - यह behaviour है: पहले few-shot prompt, prompt लंबा हो जाए या format टूटे तो fine-tune।
- "10 लाख product descriptions को सस्ते में HS chapters में बाँटो" - scale पर narrow skill: 10K labelled descriptions पर छोटा model fine-tune करो, अस्पष्ट मामलों के लिए RAG।

**Zomato**: Menu और price facts - RAG। Customer replies की brand voice - fine-tune या prompt।

---

## 💻 Code Example — Basic
```python
# Basic decision helper: score a use case and recommend RAG, fine-tuning, both, or prompting only.
def recommend(knowledge_changes_often: bool, needs_citations: bool, private_docs: bool,
              needs_fixed_style: bool, narrow_task_at_scale: bool, labelled_examples: int) -> str:
    rag_score = sum([knowledge_changes_often, needs_citations, private_docs])  # reasons for RAG (0-3)
    ft_score = sum([needs_fixed_style, narrow_task_at_scale])  # reasons for fine-tuning (0-2)
    if ft_score and labelled_examples < 200:  # not enough data to fine-tune well
        ft_score = 0  # fall back to prompting / few-shot
    if rag_score and ft_score:  # both needed
        return "fine-tune for behaviour + RAG for knowledge"  # combined
    if rag_score:  # knowledge problem
        return "RAG"  # retrieval
    if ft_score:  # behaviour problem
        return "fine-tuning"  # training
    return "prompting only (few-shot examples)"  # simplest option

print(recommend(True, True, True, False, False, 0))  # RAG
print(recommend(False, False, False, True, True, 5000))  # fine-tuning
print(recommend(True, True, True, True, False, 1000))  # both
print(recommend(False, False, False, True, False, 20))  # prompting only
```

## 💻 Code Example — Advanced
```python
# Production-style cost model: compare monthly cost of RAG, fine-tuning and both.
# All prices are PARAMETERS - fill them from the provider's current pricing page.
from __future__ import annotations  # modern hints

import asyncio  # async version
from dataclasses import dataclass  # container


@dataclass(frozen=True)
class Workload:  # usage assumptions
    queries_per_month: int  # traffic
    question_tokens: int  # user question + system prompt
    answer_tokens: int  # model output
    rag_context_tokens: int  # retrieved chunks per query (top_k x chunk size)
    fewshot_tokens: int  # extra instruction/few-shot tokens a base model needs but a tuned model does not


@dataclass(frozen=True)
class Prices:  # USD per 1M tokens (parameters)
    base_in: float  # base model input
    base_out: float  # base model output
    tuned_in: float  # fine-tuned model input (usually higher)
    tuned_out: float  # fine-tuned model output
    embed: float  # embedding price
    train: float  # training price per 1M training tokens


def monthly_cost(w: Workload, p: Prices, corpus_tokens: int = 0, train_tokens: int = 0, mode: str = "rag") -> float:
    """Return estimated monthly USD for 'rag', 'finetune' or 'both'."""
    if w.queries_per_month <= 0:  # validate
        raise ValueError("queries_per_month must be positive")  # error
    q = w.queries_per_month  # shortcut
    if mode == "rag":  # base model + retrieved context
        tin = q * (w.question_tokens + w.fewshot_tokens + w.rag_context_tokens)  # input tokens
        return tin * p.base_in / 1e6 + q * w.answer_tokens * p.base_out / 1e6 + corpus_tokens * p.embed / 1e6  # total
    if mode == "finetune":  # tuned model, no context, no few-shot (facts frozen in weights)
        tin = q * w.question_tokens  # input tokens
        return tin * p.tuned_in / 1e6 + q * w.answer_tokens * p.tuned_out / 1e6 + train_tokens * p.train / 1e6  # total
    if mode == "both":  # tuned model + retrieved context
        tin = q * (w.question_tokens + w.rag_context_tokens)  # input tokens
        return (tin * p.tuned_in / 1e6 + q * w.answer_tokens * p.tuned_out / 1e6
                + corpus_tokens * p.embed / 1e6 + train_tokens * p.train / 1e6)  # total
    raise ValueError(f"unknown mode {mode!r}")  # bad mode


async def compare(w: Workload, p: Prices, corpus_tokens: int, train_tokens: int) -> dict[str, float]:
    try:  # compute all modes concurrently (cheap, but shows the async pattern)
        r, f, b = await asyncio.gather(*(asyncio.to_thread(monthly_cost, w, p, corpus_tokens, train_tokens, m)
                                         for m in ("rag", "finetune", "both")))  # three estimates
    except ValueError as exc:  # invalid inputs
        raise RuntimeError(f"cost model failed: {exc}") from exc  # wrap
    return {"rag": round(r, 2), "finetune": round(f, 2), "both": round(b, 2)}  # dollars per month


if __name__ == "__main__":  # demo with ILLUSTRATIVE numbers only
    w = Workload(3_000_000, 150, 200, 1500, 400)  # 3M queries/month
    p = Prices(base_in=0.15, base_out=0.60, tuned_in=0.30, tuned_out=1.20, embed=0.02, train=3.0)  # example prices
    print(asyncio.run(compare(w, p, corpus_tokens=50_000_000, train_tokens=20_000_000)))  # compare
```

---

## 🟠 FastAPI Integration
A single API can route per request: knowledge questions go through RAG; formatting/classification tasks go straight to a (possibly fine-tuned) model. The router below is rule-based; production systems may use a small classifier.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app


class Ask(BaseModel):  # request
    question: str  # user question
    task: str = "qa"  # "qa" (needs knowledge) or "classify" (narrow skill)


async def rag_answer(q: str) -> str:  # placeholder RAG path
    return f"[RAG] retrieved docs + answer for: {q}"  # replace with retrieval + LLM call


async def tuned_classify(q: str) -> str:  # placeholder fine-tuned path
    return f"[fine-tuned model] label for: {q}"  # replace with the tuned model id call


@app.post("/ask")  # route
async def ask(req: Ask) -> dict:  # handler
    if req.task == "classify":  # narrow skill -> fine-tuned/small model
        return {"path": "finetuned", "answer": await tuned_classify(req.question)}  # no retrieval cost
    return {"path": "rag", "answer": await rag_answer(req.question)}  # knowledge -> RAG
```

---

## 🔗 LangChain / LangGraph Connection
In LangChain, RAG is a retriever plus prompt plus model chain (LCEL). A fine-tuned model is just another `model` argument, such as `ChatOpenAI(model="ft:...")`. LangGraph can route between paths with a conditional edge and can combine them (tuned model + retriever).

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_core.output_parsers import StrOutputParser  # parser
# from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("Answer using only the context.\nContext:\n{context}\n\nQuestion: {question}")  # RAG prompt
# llm = ChatOpenAI(model="gpt-4o-mini")            # base model for RAG
# tuned = ChatOpenAI(model="ft:gpt-4o-mini:org::id") # fine-tuned model id (provider specific)
# rag_chain = {"context": retriever, "question": lambda x: x} | prompt | llm | StrOutputParser()
# combined = {"context": retriever, "question": lambda x: x} | prompt | tuned | StrOutputParser()  # both
# LangGraph: add_conditional_edges("router", pick_path, {"rag": "retrieve", "classify": "tuned_llm"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fine-tuning to "teach" the model facts
✅ Correct: Put facts in a retrieval index; fine-tune only behaviour.

```python
# Wrong - bake current duty rates into weights; they are stale after the next budget
train_data = [{"q": "duty on 8517.13.00?", "a": "10%"}]  # facts in training data

# Right - keep facts in the index, teach the format
train_data = [{"q": "Context: ... 8517.13.00 duty 10% ...\nQuestion: duty?", "a": '{"hs_code":"8517.13.00","duty":"10%"}'}]
```

❌ Mistake 2: Choosing before trying the cheap options
✅ Correct: Order: better prompt -> few-shot -> RAG -> fine-tuning -> both. Measure at each step.

❌ Mistake 3: Believing RAG removes hallucination.
✅ Correct: RAG reduces it; you still need citations, "I don't know" handling and evaluation.

---

## 🧠 Tricky Interview Question
**Q**: "Your CEO says: 'Fine-tune GPT on all our 10,000 tariff PDFs so it knows everything and we can drop the vector DB.' What do you answer?"

**Answer**: Fine-tuning is poor at storing facts: it learns patterns, not a reliable lookup table, so the model may blend or invent rates; it cannot cite page numbers; it becomes stale when rules change (retraining needed for every update); permissions cannot be enforced per user; and it is costly. Use RAG for the tariff knowledge, with citations and date filters. Consider fine-tuning only for behaviour: output schema, tone, domain-specific classification skill, or to shorten prompts at high volume. If both matter, combine: fine-tuned model for behaviour + RAG for facts. Prove the choice with an eval set comparing the options on accuracy, cost and update time.

---

## ⚫ Interview Questions + Answers

Q1: One-line difference between RAG and fine-tuning?
A1: RAG adds knowledge at query time via retrieval; fine-tuning changes the model's behaviour via training.

Q2: Which handles frequently changing data better?
A2: RAG - update the index; no retraining.

Q3: Can RAG and fine-tuning be combined?
A3: Yes. Fine-tune for style/format/skill and use RAG to supply fresh facts in the prompt.

Q4: Which gives citations?
A4: RAG, because retrieved chunks carry sources. A fine-tuned model cannot reliably point to where a fact came from.

Q5: (Hard) When would fine-tuning beat RAG outright?
A5: When the task is a narrow, stable skill with lots of labelled data (classification, extraction in a fixed schema, tone), when latency and cost per call matter at huge volume (short prompts, smaller model), or when the model must follow a complex format reliably. Not for facts that change.

---

## 🔷 When to Use + When Not to Use
✅ Use RAG when:
- Knowledge is private, large or changing
- You need citations and access control
✅ Use fine-tuning when:
- You need consistent behaviour, format or a narrow skill, with hundreds+ labelled examples

❌ Avoid RAG when:
- The whole knowledge fits in the prompt (just include it) or no external knowledge is needed
❌ Avoid fine-tuning when:
- Goal is "teach it our documents", data is small, or knowledge changes weekly

---

## 📊 Visual Diagram
```
                 knowledge (facts)                       behaviour (how)
 changes often ───────► RAG                  fixed style/format/skill ───► FINE-TUNE
                                                     
 question ─► [retrieve docs] ─► prompt(+docs) ─► base LLM ─► answer + citations     (RAG)
 question ───────────────────────────────────► tuned LLM ─► answer in house style   (FT)
 question ─► [retrieve docs] ─► prompt(+docs) ─► tuned LLM ─► cited, on-format answer (BOTH)

 effort / speed to update:   RAG: minutes (re-index)     FT: hours-days (data + train + eval)
```

---

## 💰 Cost Impact
- RAG: embedding corpus once (cheap), plus extra input tokens per query (top_k x chunk size, for example 1,500 tokens). 3M queries/month x 1,500 tokens x $0.15/1M = about $675 extra input cost.
- Fine-tuning: one-off training cost (training tokens x price, plus experiments), tuned models are usually priced higher per token than base models, and every knowledge change means retraining. Benefit: no retrieved context and fewer few-shot tokens, so shorter prompts.
- Break-even depends on volume: high volume with a stable narrow task favours fine-tuning; changing knowledge favours RAG.
- Optimise: start with RAG + good prompts; use a small model; cache; consider fine-tuning a small model later to replace long prompts. Always recompute with current prices.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieve docs then generate | पहले खोजो, फिर जवाब बनाओ |
| Fine-tuning | Train model on examples | Examples पर model को train करना |
| LoRA | Low-cost adapter fine-tuning | कम खर्च वाली fine-tuning विधि |
| Few-shot | Examples inside the prompt | Prompt में उदाहरण |
| Grounding | Answer tied to sources | जवाब का source से जुड़ा होना |
| Knowledge cutoff | Training data end date | Training data की अंतिम तारीख |

---

## ⚡ 3-Line Summary
English: RAG is for knowledge that changes and needs citations; fine-tuning is for behaviour, format and narrow skills. Try prompting, then RAG, then fine-tuning, and combine them when both needs exist. Do not fine-tune to store facts.
Hindi: RAG बदलने वाले और citation वाले knowledge के लिए है; fine-tuning behaviour, format और narrow skills के लिए। पहले prompting, फिर RAG, फिर fine-tuning आज़माओ, और दोनों ज़रूरतें हों तो मिलाओ। Facts store करने के लिए fine-tune मत करो।

---

## ➡️ Next Topic
**183. RAG Architecture Overview** - the full picture: ingestion, retrieval, generation and evaluation components.
