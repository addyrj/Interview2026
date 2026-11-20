---

# 50. FileSearchTool
# हिंदी में: FileSearchTool (OpenAI vector store में खोज)
# Framework: OpenAI SDK
# Already Known: No

---

> Verified against openai-agents 0.24.0 (Python 3.13, fastapi 0.163.0, pydantic 2.14.3). NOT run against OpenAI: the search itself needs OPENAI_API_KEY, a real vector store and a Responses-API OpenAI model. What I did verify offline: the constructor fields, the `file_search` tool name, the request payload the SDK builds (`{'type': 'file_search', 'vector_store_ids': [...], 'max_num_results': 3}` plus `file_search_call.results` in `include`), and how the SDK records a file-search result item. The result items in the samples are SIMULATED, built from the openai types.

---

## 🔵 Simple Definition (2-3 lines)
`FileSearchTool` is a hosted tool: you give it one or more OpenAI vector store ids, and OpenAI performs semantic search over the files in those stores during the model call. Your process does not run retrieval code; the results come back inside the response.

## 🔵 सरल परिभाषा (Hindi)
`FileSearchTool` एक hosted tool है: आप इसे एक या अधिक OpenAI vector store ids देते हैं, और model call के दौरान OpenAI उन stores की files में semantic search करता है। आपका process retrieval code नहीं चलाता; results response के अंदर आते हैं।

---

## 🔴 Problem it Solves
Building RAG yourself means chunking, embedding, a vector DB, ranking and syncing files. For many internal-document questions that is heavy to build and operate. FileSearchTool offloads the retrieval pipeline to OpenAI so an agent can answer from your PDFs and docs with citations after you upload them to a vector store.

## 🔴 यह क्यों बना? (Hindi)
खुद RAG बनाने का मतलब है chunking, embeddings, vector DB, ranking और files की syncing। कई internal-document सवालों के लिए यह बनाना और चलाना भारी है। FileSearchTool retrieval pipeline OpenAI को सौंप देता है, ताकि files को vector store में अपलोड करने के बाद agent आपके PDFs और docs से citations के साथ जवाब दे सके।

---

## 🟢 How it Works

```
Step 1 -> (offline job) create a vector store, upload files,
          wait until indexing is complete  -> vector_store_id
Step 2 -> Agent(tools=[FileSearchTool(vector_store_ids=[id],
          max_num_results=5, include_search_results=True)])
Step 3 -> Model decides to search -> OpenAI runs the search
          server-side (nothing executes in your process)
Step 4 -> Response contains a file_search_call item
          (queries, and results if included)
Step 5 -> Model writes the answer using the retrieved chunks
          (often with file citations)
Step 6 -> You read result.new_items for citations
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> (offline job) vector store बनाओ, files upload करो,
          indexing पूरी होने तक रुको -> vector_store_id
Step 2 -> Agent(tools=[FileSearchTool(vector_store_ids=[id],
          max_num_results=5, include_search_results=True)])
Step 3 -> Model search करने का फ़ैसला करता है -> OpenAI server-side
          search चलाता है (आपके process में कुछ नहीं चलता)
Step 4 -> Response में file_search_call item आता है
          (queries, और results यदि include किए)
Step 5 -> Model retrieved chunks से जवाब लिखता है
          (अक्सर file citations के साथ)
Step 6 -> Citations के लिए result.new_items पढ़ो
```

**Constructor verified in 0.24.0:** `FileSearchTool(vector_store_ids, max_num_results=None, include_search_results=False, ranking_options=None, filters=None)`. `max_num_results` is documented as 1 to 50. The tool's `.name` is `file_search`.

**What the SDK sends (verified by converting the tool):** `{'type': 'file_search', 'vector_store_ids': ['vs_1'], 'max_num_results': 3}`, and with `include_search_results=True` it also asks for `file_search_call.results` in the response `include` list. (The converter is an SDK internal; I used it only to inspect the payload, do not depend on it.)

**Restrictions:** the docstring says it is supported only with OpenAI models via the Responses API. It will not work through a LiteLLM or chat-completions provider.

**Not covered here:** creating the vector store and uploading files (done with the OpenAI client; see current OpenAI docs, the API has changed names before). Keep that in an ingestion job, not in the request path.

**Hindi नोट:** यह tool तेज़ prototype के लिए बढ़िया है। जब आपको अपने chunking, hybrid search, reranker या data-residency पर नियंत्रण चाहिए, तब अपना RAG function tool बनाओ।

---

## 🟡 Real World Example
**Tariff Agent.** Customs circulars, tariff schedules and past rulings (PDFs) are uploaded to one vector store per tenant. The agent calls file search to find the clause about 6109.10 and answers with the file name as citation. An attribute filter (`year == 2025`) removes outdated circulars.

**Customer Support Agent:** search product manuals and policy PDFs.

## 🟡 Real Example Hindi mein
**Tariff Agent.** Customs circulars, tariff schedules और पुराने rulings (PDFs) हर tenant के लिए एक vector store में अपलोड हैं। Agent file search से 6109.10 वाली clause खोजता है और file name को citation बनाकर जवाब देता है। Attribute filter (`year == 2025`) पुराने circulars हटा देता है।

**Customer Support Agent:** product manuals और policy PDFs में खोज।

---

## 💻 Code Example — Basic
Runs offline with a SIMULATED hosted-tool result (a real run needs OpenAI). It shows how the SDK exposes the file-search call as a `tool_call_item` in `new_items`.

```python
# Basic: attach FileSearchTool (hosted) and see how the SDK handles its result items (offline, simulated)
import asyncio                                           # async runner
from agents import Agent, Runner, FileSearchTool         # SDK
from agents.testing import ScriptedModel, assistant_message  # fake LLM
from openai.types.responses import ResponseFileSearchToolCall  # the item a real OpenAI model would emit
from openai.types.responses.response_file_search_tool_call import Result  # one search hit

tool = FileSearchTool(                                   # hosted tool: OpenAI runs the search, not your process
    vector_store_ids=["vs_tariff_demo"],                 # id of a vector store you created with the OpenAI API (placeholder here)
    max_num_results=3,                                   # 1..50 per the SDK docstring
    include_search_results=True,                         # ask for result chunks in the output items
)

async def main() -> None:
    hit = ResponseFileSearchToolCall(                    # SIMULATED hosted-tool output (a real model/vector store produces this)
        id="fs_1", queries=["duty on 6109.10"], status="completed", type="file_search_call",
        results=[Result(file_id="f1", filename="tariff.pdf", score=0.9, text="6109.10: 20%", attributes={})])
    model = ScriptedModel([[hit, assistant_message("Duty is 20% (tariff.pdf).")]])
    agent = Agent(name="Tariff Agent", instructions="Answer from the tariff files.", model=model, tools=[tool])
    res = await Runner.run(agent, "Duty on 6109.10?")
    print(res.final_output)
    print([(i.type, type(i.raw_item).__name__) for i in res.new_items])  # hosted call shows up as a tool_call_item
    print("tool name:", tool.name)                       # file_search

asyncio.run(main())
# NOT run against a real vector store: needs OPENAI_API_KEY + a real vector_store_id + a Responses-API OpenAI model.
```

## 💻 Code Example — Advanced
Per-tenant `FileSearchTool` built per request with ranking threshold and attribute filter, citations extracted from the result items, FastAPI + error handling. Offline; the hosted result is simulated.

```python
# Advanced: per-tenant FileSearchTool in FastAPI, with filters + ranking and a safe fallback (offline, simulated)
from fastapi import FastAPI, Header, HTTPException       # web
from fastapi.testclient import TestClient                # in-process client
from pydantic import BaseModel                           # schema
from openai.types.responses import ResponseFileSearchToolCall  # simulated hosted item
from openai.types.responses.response_file_search_tool_call import Result
from openai.types.responses.file_search_tool_param import RankingOptions  # typed dicts re-used by the SDK
from agents import Agent, Runner, FileSearchTool, AgentsException  # SDK
from agents.testing import ScriptedModel, assistant_message  # fake LLM

TENANT_STORES: dict[str, str] = {"acme": "vs_acme", "globex": "vs_globex"}  # one vector store per tenant (isolation)

def search_tool(tenant: str) -> FileSearchTool:          # build per request so a tenant never sees another's data
    store = TENANT_STORES.get(tenant)
    if store is None:
        raise KeyError(tenant)
    return FileSearchTool(
        vector_store_ids=[store],
        max_num_results=5,                               # keep context (and cost) small
        include_search_results=True,                     # lets us show citations in the UI
        ranking_options=RankingOptions(score_threshold=0.5),   # drop weak matches
        filters={"type": "eq", "key": "year", "value": 2025},  # attribute filter (Filters dict form from the openai types)
    )

app = FastAPI()

class Ask(BaseModel):
    question: str

@app.post("/ask")
async def ask(b: Ask, x_tenant: str = Header(...)) -> dict:
    try:
        tool = search_tool(x_tenant)
    except KeyError:
        raise HTTPException(status_code=404, detail="unknown tenant")
    sim = ResponseFileSearchToolCall(id="fs", queries=[b.question], status="completed", type="file_search_call",
          results=[Result(file_id="f1", filename="tariff.pdf", score=0.9, text="6109.10: 20%", attributes={"year": 2025})])
    model = ScriptedModel([[sim, assistant_message("20% per tariff.pdf")]])   # production: model="<an OpenAI Responses model>"
    agent = Agent(name="Tariff Agent", instructions="Cite the file name.", model=model, tools=[tool])
    try:
        res = await Runner.run(agent, b.question, max_turns=4)
    except AgentsException as exc:                       # base class of SDK errors
        raise HTTPException(status_code=502, detail=type(exc).__name__) from exc
    cites = [r.filename for i in res.new_items if i.type == "tool_call_item"
             for r in (getattr(i.raw_item, "results", None) or [])]
    return {"answer": res.final_output, "citations": cites}

if __name__ == "__main__":
    c = TestClient(app)
    print(c.post("/ask", json={"question": "duty 6109.10"}, headers={"x-tenant": "acme"}).json())
    print(c.post("/ask", json={"question": "x"}, headers={"x-tenant": "nobody"}).status_code)
# NOT run against OpenAI: needs OPENAI_API_KEY + real vector stores.
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Built-in file/vector search | No (bring your retriever/vector DB) | `RagTool`/knowledge sources (own store) | `FileSearchTool` (OpenAI vector stores, hosted) | No (use memory/retriever components) |
| Who runs retrieval | Your process | Your process | OpenAI servers | Your process |
| Control over chunking/rerank | Full | Medium | Limited (ranking_options, filters) | Full |
| Model/provider lock-in | None | None | OpenAI Responses API only | None |
| Setup effort | High | Medium | Low (upload files) | High |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Using one shared vector store for all tenants.
✅ Correct: One store per tenant (or strict attribute filters) and build the tool per request.

❌ Mistake 2: Uploading files and querying before indexing completes.
✅ Correct: Wait until the vector store files are processed; poll status in the ingestion job.

❌ Mistake 3: Using it with a non-OpenAI model through LiteLLM.
✅ Correct: Hosted tools need OpenAI Responses models; use a function-tool retriever otherwise.

❌ Mistake 4: Never reading citations from the result items.
✅ Correct: Enable `include_search_results` and surface file names so users can verify answers.

❌ Mistake 5: Putting ingestion inside the request handler.
✅ Correct: Ingest in a background job; the request path only searches.

---

## 🧠 Tricky Interview Question
Users complain the agent answers from an outdated 2022 circular even though a 2025 version is in the vector store. How do you debug and fix it?

**Answer:** First inspect what was retrieved: set `include_search_results=True` and log the returned file names, scores and `queries` from the file_search_call item. Likely causes: both versions are indexed and the old one scores higher; the query wording matches old text; or chunks lack dates. Fixes: add file attributes (year, status) at upload and use `filters` (for example year >= 2025); delete or archive superseded files so they are not in the store; raise `ranking_options.score_threshold` to drop weak matches; tell the model in instructions to prefer the latest effective date and to cite the file; and build a small eval set of known questions with expected source files so regressions are caught. Also remember that the model, not you, writes the search query, so check the logged queries.

---

## ⚫ Interview Questions + Answers

**Q1:** What does `FileSearchTool` do?

**A1:** It lets the model search OpenAI vector stores you reference by id; OpenAI runs retrieval server-side and returns chunks to the model.

**Q2:** Which models support it?

**A2:** Per the SDK docstring: OpenAI models using the Responses API only.

**Q3:** How do you get citations?

**A3:** Set `include_search_results=True` and read the file_search_call items (and message annotations) from `result.new_items`.

**Q4:** How do you restrict results to recent documents?

**A4:** Attach attributes at upload and pass `filters` (and optionally `ranking_options.score_threshold`).

**Q5:** Design a multi-tenant document Q&A service with it.

**A5:** Ingestion worker per tenant uploading to that tenant's vector store with attributes; API builds the tool per request from auth; per-tenant quotas; evals on gold questions; logs of queries and sources; fallback message when no result passes the threshold; delete flow for data-removal requests.

---

## 💰 Cost Impact
Cost has three parts: (1) vector store storage and file search tool-call fees charged by OpenAI (see the OpenAI pricing page; verify before budgeting), (2) retrieved chunks that are added to the model prompt, which count as input tokens, roughly chunks x chunk_size, and (3) the extra turn the model spends. Tips: lower `max_num_results`, use a score threshold, keep chunks focused, filter by attributes, and cache answers to frequent questions. I did not measure any numbers because the search was not run.

---

## 🔷 When to Use
✅ Use when:
- Q&A over a moderate set of documents quickly
- You are already on OpenAI Responses models
- You want managed ingestion/retrieval and citations
- Prototype before investing in custom RAG

❌ Avoid when:
- Need custom chunking, hybrid search or your own reranker
- Data must stay in your VPC/region
- Using non-OpenAI models

---

## 📊 Visual Diagram
```
  ingestion job (offline)                request path
  files --> vector store --> id          user question
              (OpenAI indexes)                 |
                    |                          v
                    |             Agent(tools=[FileSearchTool(ids)])
                    |                          |
                    |                          v
                    |                    OpenAI model call
                    |                          |  decides to search
                    +----------------> server-side semantic search
                                               |  top-k chunks (+scores)
                                               v
                                  answer + file citations
                                               |
                                  result.new_items -> citations in UI
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hosted tool | Runs on OpenAI servers | OpenAI servers पर चलता है |
| Vector store | OpenAI-managed index of your files | आपकी files का OpenAI-managed index |
| max_num_results | Max chunks returned (1 to 50) | लौटने वाले अधिकतम chunks (1 से 50) |
| Attribute filter | Restrict search by file metadata | file metadata से खोज सीमित करना |
| Citation | Pointer to the source file | source file का संदर्भ |

---

## ⚡ 3-Line Summary
English: `FileSearchTool` lets an OpenAI model search your vector stores with retrieval run by OpenAI.
Build it per tenant, filter and threshold results, and read citations from the result items.
It is great for fast RAG prototypes but ties you to OpenAI Responses models.

Hindi: `FileSearchTool` OpenAI model को आपके vector stores में खोजने देता है, retrieval OpenAI चलाता है।
इसे tenant के हिसाब से बनाएँ, results को filter और threshold करें, और citations result items से पढ़ें।
तेज़ RAG prototypes के लिए बढ़िया है, पर आपको OpenAI Responses models से बाँध देता है।

---

## ➡️ Next Topic
**#51 WebSearchTool** - the second hosted tool: live web search with location bias, domain filters and citations.

---
