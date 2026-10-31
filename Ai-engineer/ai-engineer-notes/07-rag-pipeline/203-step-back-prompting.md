---

# 203. Step-Back Prompting
# हिंदी में: Step-Back Prompting (एक कदम पीछे हटकर पूछना)

---

## 🔵 Simple Definition (English)
Step-back prompting first turns a very specific question into a broader, more abstract one (the "step-back question"), retrieves background knowledge for that, and then answers the original question using both the specific and the background context. It helps when details alone do not reveal the governing rule.

## 🔵 सरल परिभाषा (Hindi)
Step-back prompting पहले बहुत specific सवाल को ज़्यादा व्यापक, abstract सवाल ("step-back question") में बदलती है, उसके लिए background knowledge retrieve करती है, और फिर specific और background दोनों context से original सवाल का जवाब देती है। यह तब मदद करती है जब सिर्फ details से नियम पता नहीं चलता।

---

## 🔴 Problem it Solves
Very specific questions retrieve very specific chunks, but the answer often depends on a general principle stored elsewhere. "Is a Bluetooth speaker with a built-in power bank classified as 8518 or 8507?" The answer depends on the general rule (principal function / General Interpretative Rule 3b) which no chunk about "speaker with power bank" contains. Step-back retrieves that rule.

## 🔴 यह क्यों बना? (Hindi)
बहुत specific सवाल बहुत specific chunks लाते हैं, पर जवाब अक्सर कहीं और रखे general सिद्धांत पर निर्भर करता है। "Power bank वाला Bluetooth speaker 8518 में आएगा या 8507 में?" का जवाब general rule (principal function / General Interpretative Rule 3b) पर निर्भर है जो "speaker with power bank" वाले किसी chunk में नहीं है। Step-back वही rule retrieve करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Receive the specific question
Step 2 → LLM (with a few examples) writes a step-back question: more general, about the underlying concept or rule
Step 3 → Retrieve for BOTH the original question and the step-back question
Step 4 → Merge contexts: background (rules/principles) + specifics (matching entries)
Step 5 → Generator answers the ORIGINAL question, reasoning from the principles to the specifics
Step 6 → Cite both kinds of chunks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Specific सवाल लो
Step 2 → LLM (कुछ examples के साथ) step-back सवाल लिखता है: ज़्यादा general, मूल concept या नियम के बारे में
Step 3 → ORIGINAL और step-back दोनों सवालों के लिए retrieve करो
Step 4 → Contexts merge करो: background (नियम/सिद्धांत) + specifics (matching entries)
Step 5 → Generator ORIGINAL सवाल का जवाब देता है, सिद्धांत से specifics तक reasoning करके
Step 6 → दोनों तरह के chunks cite करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Specific: "HS code for a Bluetooth speaker with a built-in power bank?" Step-back: "How are multi-function or composite goods classified under the HS General Interpretative Rules?" Retrieval returns GIR 3(b) text (background) plus chapter 85 notes and entries for 8518 and 8507 (specifics). The LLM applies "essential character" to decide.
**Amazon AI**: "Why does my Kindle 2019 battery drain overnight?" step-back: "What causes battery drain in e-readers?"

## 🟡 Real Example Hindi mein
**Tariff System**: Specific: "Built-in power bank वाले Bluetooth speaker का HS code?" Step-back: "HS General Interpretative Rules में multi-function या composite goods कैसे classify होते हैं?" Retrieval से GIR 3(b) का text (background) और chapter 85 notes व 8518, 8507 की entries (specifics) मिलती हैं। LLM "essential character" लगाकर तय करता है।
**Amazon AI**: "मेरे Kindle 2019 की battery रात भर में क्यों खत्म होती है?" step-back: "e-readers में battery drain के कारण क्या हैं?"

---

## 💻 Code Example — Basic
```python
# Step-back retrieval with a stub LLM and keyword retriever (pure Python, runs directly)
from typing import Dict, List

KB: Dict[str, str] = {
    "rule": "GIR 3(b): composite goods are classified by the component giving essential character.",
    "e8518": "HS 8518.22 loudspeakers and Bluetooth speakers.",
    "e8507": "HS 8507.60 lithium-ion accumulators and power banks.",
    "shoe": "HS 6403.99 leather footwear.",
}

def step_back(question: str) -> str:
    """Stand-in for an LLM call with few-shot examples of broadening a question."""
    return "How are composite or multi-function goods classified under the general interpretative rules?"

def retrieve(query: str, k: int = 2) -> List[str]:
    words = {w.strip("?.,").lower() for w in query.split()}  # query words
    scored = sorted(KB, key=lambda d: -len(words & {w.strip("?.,()").lower() for w in KB[d].split()}))  # overlap rank
    return scored[:k]

def answer_context(question: str) -> List[str]:
    """Combine specific hits and step-back hits, dedupe, keep order."""
    specific = retrieve(question)  # details
    background = retrieve(step_back(question))  # principles
    seen: List[str] = []
    for cid in background + specific:  # background first
        if cid not in seen:
            seen.append(cid)
    return [KB[c] for c in seen]

if __name__ == "__main__":
    q = "HS code for a Bluetooth speaker with a built-in power bank?"
    print("specific only:", [KB[c] for c in retrieve(q)])  # entries but no rule
    for line in answer_context(q):
        print("-", line)  # includes GIR rule + entries
```

## 💻 Code Example — Advanced
```python
# Async step-back pipeline: few-shot prompt, parallel retrieval, labelled context, fallback on failure
import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable

logger = logging.getLogger("stepback")  # logger
LLM = Callable[[str], Awaitable[str]]  # prompt -> text
Retriever = Callable[[str, int], Awaitable[list[str]]]  # query, k -> chunk texts

FEW_SHOT = """You rewrite specific questions into broader step-back questions about the underlying rule or concept.
Q: What HS code applies to a left-handed leather glove with a heating element?
Step-back: How are composite articles and electrical heating goods classified under HS rules?
Q: Why was my shipment of 500 Samsung S24 phones taxed at 18 percent in Chennai?
Step-back: How is import duty and IGST determined for smartphones in India?
Q: {q}
Step-back:"""  # two examples teach the pattern (~150 prompt tokens)

@dataclass
class StepBackContext:
    step_back_question: str  # generated broader question
    background: list[str]  # general principles
    specifics: list[str]  # matches for the original question

class StepBackRAG:
    def __init__(self, llm: LLM, retriever: Retriever, k: int = 3) -> None:
        self.llm, self.retriever, self.k = llm, retriever, k  # deps

    async def build_context(self, question: str) -> StepBackContext:
        try:
            sb = (await asyncio.wait_for(self.llm(FEW_SHOT.format(q=question)), 6)).strip()  # generate step-back
        except Exception as exc:
            logger.warning("step-back generation failed: %r", exc)
            sb = ""  # degrade to normal retrieval
        tasks = [self.retriever(question, self.k)]  # always retrieve specifics
        if sb:
            tasks.append(self.retriever(sb, self.k))  # plus background
        results = await asyncio.gather(*tasks, return_exceptions=True)  # parallel
        specifics = results[0] if isinstance(results[0], list) else []
        background = results[1] if len(results) > 1 and isinstance(results[1], list) else []
        return StepBackContext(sb, background, specifics)

    @staticmethod
    def to_prompt(question: str, ctx: StepBackContext) -> str:
        bg = "\n".join(f"- {c}" for c in ctx.background) or "(none)"  # labelled sections help the LLM
        sp = "\n".join(f"- {c}" for c in ctx.specifics) or "(none)"
        return (f"Background principles:\n{bg}\n\nSpecific entries:\n{sp}\n\n"
                f"Using the principles, answer the question. Cite sources.\nQuestion: {question}")

async def llm_stub(p: str) -> str: return "How are composite goods classified under the HS general rules?"
async def ret_stub(q: str, k: int) -> list[str]:
    return ["GIR 3(b): essential character decides"] if "composite" in q else ["HS 8518.22 Bluetooth speakers"]

if __name__ == "__main__":
    rag = StepBackRAG(llm_stub, ret_stub)
    ctx = asyncio.run(rag.build_context("HS code for a speaker with a power bank?"))
    print(rag.to_prompt("HS code for a speaker with a power bank?", ctx))
```

---

## 🟠 FastAPI Integration
Use step-back for "reasoning-heavy" questions only. A cheap classifier (length, presence of "why/how/classify") decides. Return both the original and step-back queries when debugging.

```python
# FastAPI route: step-back used when the question looks specific and reasoning-heavy
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()  # app
rag = StepBackRAG(real_llm, real_retriever)  # build once with real clients

class Q(BaseModel):
    question: str

@app.post("/ask")
async def ask(q: Q) -> dict:
    ctx = await rag.build_context(q.question)  # parallel retrievals
    prompt = rag.to_prompt(q.question, ctx)  # labelled context
    answer = await real_llm(prompt)  # final generation
    return {"answer": answer, "step_back_question": ctx.step_back_question,
            "n_background": len(ctx.background), "n_specific": len(ctx.specifics)}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's "RAG from scratch" shows step-back with `FewShotChatMessagePromptTemplate` to generate the broader question, then runs two retrievers in a `RunnableParallel` (`normal_context`, `step_back_context`) feeding one answer prompt. In LangGraph: nodes `step_back` -> `retrieve_both` -> `generate`.

```python
# LCEL step-back (needs langchain-core, langchain-openai, OPENAI_API_KEY)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # deterministic rewrites
step_back_chain = (ChatPromptTemplate.from_template(
    "Rewrite as a broader question about the underlying rule or concept: {question}") | llm | StrOutputParser())
retriever = RunnableLambda(lambda q: [f"chunk for: {q}"])  # stand-in for vectorstore.as_retriever()

chain = (
    RunnableParallel(question=RunnablePassthrough(),
                     step_back=step_back_chain)  # make both questions
    | RunnablePassthrough.assign(normal_ctx=lambda x: retriever.invoke(x["question"]),
                                 background_ctx=lambda x: retriever.invoke(x["step_back"]))  # two retrievals
    | ChatPromptTemplate.from_template(
        "Background:\n{background_ctx}\n\nDetails:\n{normal_ctx}\n\nQuestion: {question}\nAnswer:")
    | llm | StrOutputParser()
)
# print(chain.invoke("HS code for a speaker with a power bank?"))   # needs OPENAI_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Replacing the original question with the step-back one.
✅ Correct: Retrieve with both and answer the original question.

```python
# Wrong
docs = retrieve(step_back_question); answer(step_back_question, docs)
# Right
docs = retrieve(question) + retrieve(step_back_question); answer(question, docs)
```

❌ Mistake 2: A vague step-back prompt with no examples, producing generic questions ("What is customs?").
✅ Correct: Give 2-3 domain examples that show the right level of abstraction.

```python
# Wrong
prompt = "Make this question more general: {q}"
# Right
prompt = FEW_SHOT_WITH_DOMAIN_EXAMPLES.format(q=question)
```

---

## 🧠 Tricky Interview Question
**Q**: "How is step-back different from multi-query, and when does each win?"

**Answer**: Multi-query makes *paraphrases at the same level* to improve recall of the same target chunks (vocabulary coverage). Step-back changes the *level of abstraction* to fetch *different* chunks: principles, definitions, rules that the specific question implicitly depends on. Multi-query wins for vocabulary mismatch ("earbuds" vs "headsets"). Step-back wins for reasoning questions needing a governing rule (classification rules, policy exceptions, "why" questions). They can be combined: step-back question + paraphrases of each.

---

## ⚫ Interview Questions + Answers

Q1: What is a step-back question?
A1: A more general, abstract question about the concept behind the specific one (e.g., "How are composite goods classified?").

Q2: Which paper introduced it?
A2: "Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models" (Zheng et al., Google DeepMind, 2023).

Q3: What extra cost does it add?
A3: One short LLM call (about 150-200 prompt tokens with few-shot, ~40 output) and one extra retrieval; context grows with the background chunks.

Q4: What kinds of questions benefit most?
A4: Rule-based or reasoning questions where the answer depends on general principles (classification, policy, physics/chemistry-style questions, "why" questions).

Q5: How do you keep the context small while using both retrievals?
A5: Retrieve k=2-3 for each, dedupe, rerank against the original question, label sections ("Principles" vs "Entries"), and cap total tokens; apply step-back only through a router for reasoning-heavy queries.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Answers depend on rules, definitions, principles
- Questions are very specific or contain many details
- Domain has hierarchical knowledge (law, tariff, medicine)

❌ Avoid when:
- Simple fact lookup ("duty on 8518.30")
- Queries already general
- Latency/cost budgets are strict

---

## 📊 Visual Diagram
```
 Specific Q: "HS code for speaker with power bank?"
        │                      │ LLM (few-shot)
        │                      ▼
        │         Step-back Q: "How are composite goods classified?"
        ▼                      ▼
   retrieve (entries)    retrieve (principles / GIR rules)
        └──────────┬───────────┘
                   ▼
   Context: [Principles] + [Entries]  ──► LLM answers ORIGINAL question
```

---

## 💰 Cost Impact
Extra call: ~200 prompt + ~40 output tokens on gpt-4o-mini = about 0.00005 USD. Extra retrieval is cheap. The larger prompt (2x chunks) can add ~800 tokens, about 0.00012 USD more. Total overhead roughly 0.0002 USD per query, justified only if it improves correctness on reasoning questions.
Optimize: route by question type, k=2 per retrieval, rerank and truncate, cache step-back questions for repeated queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Step-back question | Broader question about the principle | सिद्धांत के बारे में व्यापक सवाल |
| Abstraction | Moving to a general level | सामान्य स्तर पर जाना |
| Few-shot prompt | Prompt with examples | Examples वाला prompt |
| Background context | Principles/rules chunks | नियमों/सिद्धांतों वाले chunks |
| GIR | General Interpretative Rules (HS) | HS के सामान्य व्याख्या नियम |
| Router | Decides whether to use the technique | तय करता है कि technique लगानी है या नहीं |

---

## ⚡ 3-Line Summary
English: Step-back prompting asks a broader question to retrieve governing principles, then answers the original question with both contexts.
It beats paraphrasing for reasoning and rule-based questions.
Keep the original query, use few-shot examples, and route to avoid needless cost.
Hindi: Step-back prompting व्यापक सवाल पूछकर नियम/सिद्धांत retrieve करती है, फिर दोनों contexts से original सवाल का जवाब देती है।
Reasoning और rule-based सवालों में यह paraphrasing से बेहतर है।
Original query रखो, few-shot examples दो, और अनावश्यक cost से बचने के लिए routing करो।

---

## ➡️ Next Topic
**204. Query Expansion**: add synonyms, related terms and LLM-generated keywords to one query to improve recall.
