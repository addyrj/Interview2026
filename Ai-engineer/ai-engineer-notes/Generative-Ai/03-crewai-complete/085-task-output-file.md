---

# 85. Task output_file
# हिंदी में: Task का output_file (result को सीधे file में save करना)
# Framework: CrewAI
# Already Known: No

---

Verified against crewai 1.15.41 (installed in a venv, run offline with a fake LLM subclassing `crewai.llms.base_llm.BaseLLM`). Real model calls: not run - needs an LLM API key.

## 🔵 Simple Definition (2-3 lines)
`output_file` is a `Task` field. When the task finishes, CrewAI writes the task's final answer to that file path for you.
You can use `{placeholders}` from `kickoff(inputs=...)` in the path, and `create_directory=True` makes missing folders.

## 🔵 सरल परिभाषा (Hindi)
`output_file` `Task` का एक field है। Task खत्म होते ही CrewAI उसका final answer उस path की file में खुद लिख देता है।
Path में `kickoff(inputs=...)` वाले `{placeholders}` चल सकते हैं, और `create_directory=True` लगाने पर missing folders अपने आप बन जाते हैं।

---

## 🔴 Problem it Solves
Without it you must read `result.raw` after `kickoff()` and write the file yourself in every route. People forget, overwrite files, or write half-finished text when a later task fails. Report-type agents (tariff report, research summary) need a durable artifact, not just a Python string.

## 🔴 यह क्यों बना? (Hindi)
इसके बिना हर route में `kickoff()` के बाद `result.raw` पढ़कर file खुद लिखनी पड़ती है। लोग भूल जाते हैं, file overwrite हो जाती है, या बाद वाला task fail होने पर अधूरा text लिख जाता है। Tariff report या research summary जैसे agents को Python string नहीं, टिकने वाला artifact चाहिए।

---

## 🟢 How it Works

```
Step 1 -> Task(description, expected_output, output_file="reports/{item}.md")
Step 2 -> crew.kickoff(inputs={"item": "steel"})   # placeholders are filled
Step 3 -> Agent runs, produces TaskOutput.raw
Step 4 -> (if output_pydantic / output_json is set) the file gets JSON, else raw text
Step 5 -> CrewAI creates folders if create_directory=True, then writes the file
Step 6 -> You still get CrewOutput back in memory
```

Facts I confirmed by running the installed package:
- `{item}` inside `output_file` is interpolated from `inputs` (wrote `rep/steel.md`).
- A leading `/` is stripped, so `/abs/x.md` becomes `abs/x.md` under the current working directory. It does NOT write to the absolute location.
- `..` in the path raises a validation error: "Path traversal attempts are not allowed". This blocks agents or prompts from escaping the folder.
- With `output_pydantic=Tariff` the file contained the JSON of the model.
- `markdown=True` is another Task field that asks the agent to format the answer as Markdown.

## 🟢 कैसे काम करता है? (Hindi)
1. Task में `output_file="reports/{item}.md"` दें।
2. `kickoff(inputs={"item": "steel"})` पर `{item}` भर जाता है।
3. Agent answer बनाता है, और CrewAI उसे file में लिखता है।
4. अगर `output_pydantic` या `output_json` है तो file में JSON जाता है, वरना सादा text।
5. शुरुआती `/` हटा दिया जाता है (absolute path नहीं चलता) और `..` वाला path error देता है - यह सुरक्षा के लिए है।
6. Memory में आपको `CrewOutput` फिर भी मिलता है।

---

## 🟡 Real World Example
Tariff Agent: a customs analyst agent receives `{item}` and `{country}` and writes `reports/steel-IN.md` containing duty rate, legal basis and caveats. A downstream job (email sender, S3 uploader) just picks up files from `reports/`. Research Agent: a weekly research brief saved as `briefs/2026-w46.md`.

## 🟡 Real Example Hindi mein
Tariff Agent: customs analyst agent को `{item}` और `{country}` मिलते हैं, और वह `reports/steel-IN.md` में duty rate, कानूनी आधार और caveats लिखता है। आगे का job (email भेजना, S3 upload) बस `reports/` से files उठा लेता है। Research Agent: हर हफ्ते का brief `briefs/2026-w46.md` में।

---

## 💻 Code Example — Basic
```python
# basic_output_file.py  (verified: crewai 1.15.41, offline with a fake LLM)
from crewai import Agent, Task, Crew, Process  # core CrewAI classes

LLM_NAME = "gpt-4o-mini"  # model string; needs OPENAI_API_KEY when really run

analyst = Agent(  # one agent that writes the tariff report
    role="Customs Tariff Analyst",  # job title shown in the prompt
    goal="Give the import duty for the requested item",  # what it optimises for
    backstory="You know HS codes and duty schedules well.",  # persona context
    llm=LLM_NAME,  # which LLM to call
    allow_delegation=False,  # single agent, so no delegation
)

report_task = Task(  # the unit of work
    description="Find the import duty for {item} into {country}.",  # {} filled from inputs
    expected_output="A short Markdown report with duty rate and legal basis.",  # shape of answer
    agent=analyst,  # who does it
    output_file="reports/{item}-{country}.md",  # RELATIVE path, placeholders allowed
    create_directory=True,  # make reports/ if it is missing
    markdown=True,  # ask for Markdown formatting
)

crew = Crew(  # wrap agent + task
    agents=[analyst],  # list of agents
    tasks=[report_task],  # list of tasks
    process=Process.sequential,  # run tasks in order
)

if __name__ == "__main__":  # run only as a script
    result = crew.kickoff(inputs={"item": "steel", "country": "IN"})  # blocks until done
    print(result.raw)  # final text (also saved in reports/steel-IN.md)
    print(result.token_usage)  # UsageMetrics: total/prompt/completion tokens
```

## 💻 Code Example — Advanced
```python
# advanced_output_file.py  (FastAPI + async + error handling + type hints)
from __future__ import annotations  # allow modern type hints everywhere

import re  # to sanitise user input before it becomes a file name
import uuid  # unique id per request so files never collide
from pathlib import Path  # safe path handling

from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel, Field  # request validation
from crewai import Agent, Task, Crew, Process  # CrewAI core

LLM_NAME = "gpt-4o-mini"  # replace with your model string
REPORT_DIR = Path("reports")  # all outputs live here (relative on purpose)

app = FastAPI(title="Tariff Report API")  # ASGI app


class ReportRequest(BaseModel):  # request body schema
    item: str = Field(..., min_length=2, max_length=60)  # product name
    country: str = Field("IN", pattern=r"^[A-Z]{2}$")  # ISO-2 country code


class ReportResponse(BaseModel):  # response body schema
    report_path: str  # where the file was written
    text: str  # the report text
    total_tokens: int  # token usage for cost tracking


def build_crew(file_stem: str) -> Crew:  # new crew per request => no shared state
    analyst: Agent = Agent(  # the report writer
        role="Customs Tariff Analyst",  # role
        goal="Write an accurate duty report",  # goal
        backstory="Ten years of customs classification experience.",  # backstory
        llm=LLM_NAME,  # model
        allow_delegation=False,  # keep it simple
        max_iter=5,  # cap reasoning loops to cap cost
    )
    task: Task = Task(  # the task with a per-request file
        description="Find import duty for {item} into {country}.",  # prompt text
        expected_output="Markdown report: rate, legal basis, caveats.",  # contract
        agent=analyst,  # owner
        output_file=f"{REPORT_DIR}/{file_stem}.md",  # unique file per request
        create_directory=True,  # create folder on first use
    )
    return Crew(agents=[analyst], tasks=[task], process=Process.sequential)  # assemble


@app.post("/report", response_model=ReportResponse)  # POST /report
async def make_report(req: ReportRequest) -> ReportResponse:  # async route
    safe_item: str = re.sub(r"[^a-z0-9]+", "-", req.item.lower()).strip("-")  # slug
    stem: str = f"{safe_item}-{req.country}-{uuid.uuid4().hex[:8]}"  # unique name
    crew: Crew = build_crew(stem)  # fresh crew
    try:
        out = await crew.akickoff(inputs={"item": req.item, "country": req.country})  # async run
    except Exception as exc:  # LLM/network/validation errors
        raise HTTPException(status_code=502, detail=f"crew failed: {exc}") from exc  # map to 502
    path: Path = REPORT_DIR / f"{stem}.md"  # expected output location
    if not path.exists():  # file missing means writer failed silently
        raise HTTPException(status_code=500, detail="report file was not written")  # fail loudly
    return ReportResponse(  # build the reply
        report_path=str(path),  # path string
        text=out.raw,  # in-memory copy
        total_tokens=out.token_usage.total_tokens,  # cost metric
    )
```
Not run with a real model - needs an API key. The same code was run via FastAPI `TestClient` with a fake LLM and the file was created (see Verification below).

**Verification:** `Crew.akickoff` and `Crew.kickoff_async` both exist in 1.15.41 and returned `CrewOutput` with a fake LLM that implements `call` and `acall`. In that fake run `token_usage` was all zeros because the fake makes no real usage report - a real provider fills it.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Save result to file | You write a node that writes the file | Built in: `Task(output_file=...)` | You write the file after `Runner.run` | You write the file after `run()` |
| Placeholders in path | Python f-string | `{key}` from `kickoff(inputs)` | Python f-string | Python f-string |
| Auto-create folders | Manual `mkdir` | `create_directory=True` | Manual | Manual |
| Path traversal guard | None (your code) | Rejects `..` | None | None |
| Structured file content | State schema, you dump | `output_pydantic` -> JSON in file | `output_type` then you dump | Structured message, you dump |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Using an absolute path like `/var/data/report.md` and expecting it there.
✅ Correct: Use a relative path under your working directory (the leading `/` is stripped). Move or sync the file afterwards if it must live elsewhere.

❌ Mistake 2: One fixed file name (`report.md`) in a web API. Two concurrent users overwrite each other.
✅ Correct: Put a unique id in the path (`reports/{item}-{uuid}.md`) and build the crew per request.

❌ Mistake 3: Forgetting `create_directory=True`, then the first run fails or writes nothing.
✅ Correct: Set it, or create the directory at app start.

---

## 🧠 Tricky Interview Question
Your tariff API writes `report.md` using `output_file`. Under load users complain that they receive another customer's report. Why, and how do you fix it?

Answer: A fixed `output_file` is shared global state. Two concurrent `kickoff` calls write the same path, and a reader may read the file after the other request overwrote it. Fix: unique path per request (UUID in file name), return `result.raw` from memory instead of re-reading the file, and treat the file as an audit artifact only. Also build the Crew per request. Do not rely on a lock, it hides the problem and kills throughput. For multi-tenant data add a tenant folder and access control, because `output_file` has no authorisation.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does `output_file` do?
A1: It writes the task's output to a file when the task completes.

Q2: [Medium] Can the path use input variables?
A2: Yes. `{item}` in `output_file` is filled from `kickoff(inputs=...)` (confirmed by running 1.15.41).

Q3: [Hard] What happens with an absolute path or `..`?
A3: In 1.15.41 a leading slash is stripped so it becomes relative to the working directory, and `..` raises "Path traversal attempts are not allowed". Re-check on upgrade.

Q4: [Hard] If the task has `output_pydantic`, what is in the file?
A4: The JSON of the model (my run showed `{"item":"steel","rate":10.0}`), not free text.

Q5: [System Design] Design report generation for 1000 concurrent users.
A5: FastAPI accepts the request, returns a job id, and pushes to a queue. Workers run `akickoff` with a per-job crew and unique `output_file` on shared storage or local disk then upload to object storage. Return `result.raw` and a signed URL. Add timeouts, `max_iter`, retries with backoff, and a cleanup job for old files.

---

## 💰 Cost Impact
Writing a file adds no LLM tokens. Cost comes from the task itself: roughly (prompt tokens x input price) + (completion tokens x output price). Token count per run is not fixed - read `result.token_usage` and log it. Tips: keep `expected_output` short, set `max_iter`, use a small model for formatting-only tasks, and do not ask for "Markdown with long explanation" if the consumer only needs a rate. Prices change - verify on the provider page.

## 🔷 When to Use
✅ Use when:
- The result must survive the request (reports, audit trails).
- Another system consumes files (email, upload, BI).
- You want a quick artifact during development.

❌ Avoid when:
- The API should return data only (use `result.raw` or `output_pydantic`).
- Multi-tenant data without an isolation plan.
- Files cannot be written (read-only containers) - use object storage.

---

## 📊 Visual Diagram
```
 POST /report {item, country}
        |
        v
 +-----------------+    inputs    +----------------------+
 | FastAPI route   | -----------> | Crew.akickoff()      |
 +-----------------+              |  Task(output_file=   |
        ^                         |   "reports/{..}.md") |
        |                         +----------+-----------+
        |                                    | LLM calls (tokens)
        |                                    v
        |                         +----------------------+
        |   CrewOutput.raw        | TaskOutput.raw       |
        +-------------------------|  -> write file       |
                                  +----------+-----------+
                                             v
                                     reports/steel-IN-ab12.md
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| output_file | Path where the task result is saved | task का result जिस file में save हो |
| create_directory | Make missing folders | missing folders बनाना |
| placeholder | `{name}` replaced by input | `{name}` जिसकी जगह input आता है |
| path traversal | `..` trick to leave the folder | `..` से folder के बाहर जाने की चाल |
| artifact | Durable output file | टिकने वाली output file |
| token_usage | Token counts of the run | run के tokens की गिनती |

---

## ⚡ 3-Line Summary
English: `output_file` saves a task result to disk automatically.
Use relative paths with `{placeholders}`, `create_directory=True`, and a unique name per request.
Leading `/` is stripped and `..` is rejected.

Hindi: `output_file` task का result अपने आप disk पर save करता है।
Relative path, `{placeholders}`, `create_directory=True` और हर request के लिए unique नाम रखें।
शुरुआती `/` हट जाता है और `..` reject होता है।

---

## ➡️ Next Topic
**#86 Task callback** - after the file is written you often want to trigger something (notify, log, upload). The task callback runs right when a task finishes.

---
