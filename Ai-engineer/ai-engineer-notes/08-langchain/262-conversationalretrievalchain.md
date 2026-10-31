---

# 262. ConversationalRetrievalChain
# हिंदी में: ConversationalRetrievalChain (बातचीत वाली Retrieval Chain)

---

## 🔵 Simple Definition (English)
`ConversationalRetrievalChain` is a legacy LangChain chain for RAG with **chat history**. It first rewrites the follow-up question into a standalone question (using the history), then retrieves documents and answers. Modern replacement: `create_history_aware_retriever` + `create_retrieval_chain`.

## 🔵 सरल परिभाषा (Hindi)
`ConversationalRetrievalChain` LangChain की legacy chain है जो **chat history** के साथ RAG करती है। ये पहले follow-up सवाल को history की मदद से standalone सवाल में बदलती है, फिर documents retrieve करके जवाब देती है। आधुनिक विकल्प: `create_history_aware_retriever` + `create_retrieval_chain`।

---

## 🔴 Problem it Solves
- `RetrievalQA` treats every question alone, so "And for tablets?" fails.
- You need both: history for understanding, and retrieval for facts.
- Doing the rewrite step by hand in every project was repeated work.

## 🔴 यह क्यों बना? (Hindi)
- `RetrievalQA` हर सवाल को अकेला देखती है, इसलिए "और tablets के लिए?" फ़ेल होता है।
- दोनों चाहिए: समझने के लिए history, और facts के लिए retrieval।
- हर project में rewrite step हाथ से लिखना दोहराव था।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input: {"question": "...", "chat_history": [(human, ai), ...]}
Step 2 → Condense-question LLM call: history + question → standalone question
Step 3 → Retriever fetches documents using the standalone question
Step 4 → QA LLM call: context + (standalone) question → answer
Step 5 → Output: {"answer": ..., "source_documents": ...} (+ "question", "chat_history")
Step 6 → YOU (or memory) append the new turn to chat_history
Step 7 → Two LLM calls per turn: one condense, one answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input: {"question": "...", "chat_history": [(human, ai), ...]}
Step 2 → Condense LLM call: history + question → standalone सवाल
Step 3 → Retriever standalone सवाल से documents लाता है
Step 4 → QA LLM call: context + (standalone) सवाल → जवाब
Step 5 → Output: {"answer": ..., "source_documents": ...} (+ "question", "chat_history")
Step 6 → नया turn chat_history में आप (या memory) जोड़ते हैं
Step 7 → हर turn में दो LLM calls: एक condense, एक answer
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Duty on lithium batteries?" then "What about for power banks?" The condense step makes the second "What is the import duty on power banks?" so the retriever finds the right chunk.
**Zomato AI**: "Show vegetarian restaurants" then "Which of them delivers fastest?"

## 🟡 Real Example Hindi mein
**Tariff System**: "Lithium batteries पर duty?" फिर "Power banks के लिए?" Condense step दूसरे सवाल को "Power banks पर import duty कितनी है?" बनाता है ताकि retriever सही chunk खोजे।
**Zomato AI**: "Vegetarian restaurants दिखाओ" फिर "इनमें सबसे तेज़ delivery किसकी है?"

---

## 💻 Code Example — Basic
```python
# Basic: the two-step flow (condense, then retrieve+answer) in pure Python, runnable
from typing import List, Tuple

FACTS = {
    "batteries": "Lithium batteries: HS 8507.60, duty 10%.",
    "power banks": "Power banks: HS 8507.60, duty 10%.",
    "speakers": "Speakers: HS 8518.22, duty 20%.",
}

def condense(question: str, history: List[Tuple[str, str]]) -> str:
    """Fake LLM: if question lacks a known topic, name the last topic from history."""
    q = question.lower()
    if any(topic in q for topic in FACTS):
        return question                                     # already standalone
    for human, _ai in reversed(history):                    # newest first
        for topic in FACTS:
            if topic in human.lower():
                return f"{question.rstrip('?')} for {topic}?"
    return question

def retrieve_and_answer(standalone: str) -> str:
    # Return facts for any topic in the standalone question
    hits = [fact for topic, fact in FACTS.items() if topic in standalone.lower()]
    return hits[0] if hits else "not found"

def conversational_rag(question: str, history: List[Tuple[str, str]]) -> str:
    standalone = condense(question, history)                # step 2
    answer = retrieve_and_answer(standalone)                # steps 3-4
    history.append((question, answer))                      # step 6: caller owns history
    print(f"{question!r} -> {standalone!r} -> {answer}")
    return answer

if __name__ == "__main__":
    hist: List[Tuple[str, str]] = []
    conversational_rag("Duty on batteries?", hist)
    conversational_rag("What about speakers?", hist)
    conversational_rag("And its HS code?", hist)            # resolves to speakers
```

## 💻 Code Example — Advanced
```python
# Legacy ConversationalRetrievalChain and the modern history-aware version (async, typed)
import asyncio
import warnings
from typing import Any

from langchain.chains import ConversationalRetrievalChain                   # legacy
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

warnings.filterwarnings("ignore", category=DeprecationWarning)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=300)

def build_legacy(retriever: Any) -> Any:
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,        # also return the docs used
    )

def build_modern(retriever: Any) -> Any:
    condense_prompt = ChatPromptTemplate.from_messages([
        ("system", "Rewrite the last user question as a standalone question. Do NOT answer it."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware = create_history_aware_retriever(llm, retriever, condense_prompt)
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer only from the context. If missing, say 'not found'.\n\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    return create_retrieval_chain(history_aware, create_stuff_documents_chain(llm, qa_prompt))

async def chat_turn(chain: Any, question: str, history: list[BaseMessage]) -> str:
    try:
        out = await chain.ainvoke({"input": question, "chat_history": history})
    except Exception as exc:                                  # API / retriever failure
        return f"Error: {type(exc).__name__}"
    history += [HumanMessage(question), AIMessage(out["answer"])]   # we manage the history
    return str(out["answer"])

# legacy usage (history is a list of (human, ai) tuples):
#   build_legacy(retriever).invoke({"question": "...", "chat_history": [("hi", "hello")]})["answer"]
# modern usage:
#   chain = build_modern(retriever); hist: list[BaseMessage] = []
#   print(asyncio.run(chat_turn(chain, "Duty on lithium batteries?", hist)))   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
The client sends `session_id`; the server loads history from a store, runs the chain, and saves the turn.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
histories: dict[str, list[BaseMessage]] = {}   # use Redis in production
chain: Any = None                              # build_modern(retriever) at startup

class In(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    question: str = Field(min_length=2, max_length=1000)

@app.post("/chat")
async def chat(body: In) -> dict[str, str]:
    hist = histories.setdefault(body.session_id, [])
    answer = await chat_turn(chain, body.question, hist[-10:])  # trimmed copy for the prompt
    hist += [HumanMessage(body.question), AIMessage(answer)]     # persist full history
    return {"answer": answer}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain docs deprecate this chain in favour of `create_history_aware_retriever` + `create_retrieval_chain`, wrapped with `RunnableWithMessageHistory` for automatic history. In LangGraph: `messages` in the state, a `condense` node, a `retrieve` node and a `generate` node, with a checkpointer for memory. It also lets you add grading and retries.

```python
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

store: dict[str, InMemoryChatMessageHistory] = {}
def get_hist(sid: str) -> InMemoryChatMessageHistory:
    return store.setdefault(sid, InMemoryChatMessageHistory())

conv = RunnableWithMessageHistory(
    build_modern(retriever), get_hist,
    input_messages_key="input", history_messages_key="chat_history",
    output_messages_key="answer",
)
# conv.invoke({"input": "Duty on batteries?"}, config={"configurable": {"session_id": "s1"}})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting that the chain does NOT save history by itself.
✅ Correct: Append each turn yourself, or attach memory or `RunnableWithMessageHistory`.

```python
# Wrong: history stays empty, so follow-ups fail
chain.invoke({"question": q, "chat_history": []})
# Right
result = chain.invoke({"question": q, "chat_history": history})
history.append((q, result["answer"]))
```

❌ Mistake 2: Using the original question (not the standalone one) for retrieval.
✅ Correct: Retrieve with the condensed question.

❌ Mistake 3: Passing full history forever.
✅ Correct: Trim or summarise history.

---

## 🧠 Tricky Interview Question
**Q**: "Your conversational RAG answers a follow-up wrongly: the user said 'What about Germany?' after a question on India duties, and it returned India data. The retrieval logs show a condensed question 'What about India duties for Germany?'. What is wrong?"

**Answer**: The condense prompt is mixing old context into the new one. Fix the condense prompt: "If the new question changes an entity, replace the old entity; do not keep both." Add few-shot examples of topic switches, log the standalone question, test with a conversation eval set containing entity changes, and consider metadata filters (country=Germany) extracted explicitly rather than relying on free-text rewrite.

---

## ⚫ Interview Questions + Answers

Q1: What are the inputs of ConversationalRetrievalChain?
A1: `question` and `chat_history` (list of tuples or messages), or a memory object that provides history.

Q2: Why two LLM calls per turn?
A2: One to condense history + question into a standalone question for retrieval, another to answer using retrieved context.

Q3: How do you return sources?
A3: `return_source_documents=True`, then read `source_documents` in the output.

Q4: How can you reduce its cost?
A4: Use a cheaper model for condensing (`condense_question_llm`), skip condensing when history is empty, trim history, lower `k`.

Q5: Compare ConversationalRetrievalChain with the modern approach for a production bot.
A5: The modern approach exposes each step: you control the condense prompt, retriever, answer prompt, history storage, streaming and tracing, and it runs in LangGraph when you need grading or tools. The legacy chain bundles these behind one class with limited hooks, and is deprecated, so new bots should use create_history_aware_retriever + create_retrieval_chain (or a LangGraph graph).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Maintaining legacy code
- Studying how conversational RAG is structured

❌ Avoid when:
- Starting new projects
- You need tool use, routing, grading
- You need exact control of streaming and tracing

---

## 📊 Visual Diagram
```
 question + chat_history
        │
        ▼
 ┌───────────────┐  standalone question
 │ Condense LLM  │───────────────┐
 └───────────────┘               ▼
                          ┌─────────────┐   top-k docs
                          │  Retriever  │──────────────┐
                          └─────────────┘              ▼
                                               ┌───────────────┐
                                               │   QA LLM      │──► answer + sources
                                               └───────────────┘
```

---

## 💰 Cost Impact
- Condense call: ~history (up to few hundred tokens) + question; small output (~30 tokens).
- Answer call: context chunks (e.g. 4 x 300 tokens) + history.
- Typical turn: ~1800 input + ~200 output tokens, about $0.0004 on gpt-4o-mini; double that if history is untrimmed.
- Optimise: cheap condense model, skip condense on first turn, trim history, cache standalone-question results.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| chat_history | Earlier turns passed in | पिछली बातचीत |
| Condense question | Rewrite follow-up to standalone | Follow-up को पूरा सवाल बनाना |
| History-aware retriever | Retriever that uses chat history | History समझने वाला retriever |
| source_documents | Docs behind the answer | जवाब के पीछे के docs |
| Deprecated | Replaced by newer API | नए API से बदला गया |

---

## ⚡ 3-Line Summary
English: ConversationalRetrievalChain condenses the follow-up using chat history, retrieves, then answers. It does not store history itself and is deprecated. Use create_history_aware_retriever with create_retrieval_chain, or LangGraph, for new work.
Hindi: ConversationalRetrievalChain follow-up को history से condense करती है, फिर retrieve और answer करती है। ये history खुद save नहीं करती और deprecated है। नए काम के लिए create_history_aware_retriever + create_retrieval_chain या LangGraph इस्तेमाल करो।

---

## ➡️ Next Topic
**263. LCEL RAG Chain**: build the same RAG pipeline with pipes, streaming and sources.
