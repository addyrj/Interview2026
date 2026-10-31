---

# 163. Code Splitting
# हिंदी में: Code Splitting (Functions और Classes के आधार पर)

---

## 🔵 Simple Definition (English)
Code splitting chunks source code along its syntax: one function, one class or one logical block per chunk, with imports and a signature or docstring as context. It avoids cutting a function in half the way a plain character splitter would.

## 🔵 सरल परिभाषा (Hindi)
Code splitting source code को उसके syntax के हिसाब से chunk करती है: हर chunk में एक function, एक class या एक logical block, साथ में imports और signature या docstring संदर्भ के रूप में। यह function को बीच से नहीं काटती, जैसा सामान्य character splitter करता है।

---

## 🔴 Problem it Solves
Code has strict structure: half a function is useless or misleading. Generic text splitters break on blank lines inside functions and separate a `def` line from its body. Code RAG (assistants that answer "where is duty calculated?") needs chunks that are complete, searchable units with file and symbol names.

## 🔴 यह क्यों बना? (Hindi)
Code का structure सख़्त होता है: आधा function बेकार या भ्रामक है। सामान्य text splitters functions के अंदर की खाली lines पर टूटते हैं और `def` line को उसके body से अलग कर देते हैं। Code RAG (जो "duty कहाँ calculate होती है?" का जवाब दे) को पूरे, खोजने योग्य units चाहिए जिनमें file और symbol नाम हों।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Detect language (file extension)
Step 2 → Parse: Python ast / tree-sitter for many languages (or language-specific separators)
Step 3 → Extract top-level units: functions, classes (methods as sub-chunks if the class is big)
Step 4 → Chunk text = signature + docstring + body, prefixed with "# file: path | symbol: name"
Step 5 → Too long? Split inside the unit at statement/blank-line boundaries; keep the header on every part
Step 6 → Metadata: file path, symbol, language, line range; embed; optionally also embed a summary
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Language पहचानो (file extension से)
Step 2 → Parse करो: Python ast / कई languages के लिए tree-sitter (या language-specific separators)
Step 3 → Top-level units निकालो: functions, classes (बड़ी class हो तो methods अलग chunks)
Step 4 → Chunk text = signature + docstring + body, आगे "# file: path | symbol: name"
Step 5 → बहुत लंबा? Unit के अंदर statement/blank-line सीमा पर तोड़ो; हर हिस्से में header रखो
Step 6 → Metadata: file path, symbol, language, line range; embed करो; चाहें तो summary भी embed करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: the team asks an internal assistant "how do we compute anti-dumping duty and where is it applied?" The repository is chunked per function (`calculate_duty`, `apply_exemptions`, ...) with file path and symbol name. Retrieval returns the complete `calculate_duty` function and its caller, not fragments.

**Amazon-style dev tools**: internal code search chunked per function with call-graph metadata so "who calls `compute_tax`?" can be answered.

## 🟡 Real Example Hindi mein
**Tariff System**: team internal assistant से पूछती है "anti-dumping duty कैसे calculate होती है और कहाँ लागू होती है?" Repository को हर function (`calculate_duty`, `apply_exemptions`, ...) के हिसाब से file path और symbol नाम के साथ chunk किया गया है। Retrieval टुकड़े नहीं, पूरा `calculate_duty` function और उसका caller लौटाता है।

**Amazon-style dev tools**: internal code search हर function के हिसाब से call-graph metadata के साथ chunked है, ताकि "`compute_tax` को कौन call करता है?" का जवाब मिल सके।

---

## 💻 Code Example — Basic
```python
# Runs offline: split Python source into function/class chunks using the standard library ast module
import ast


def python_chunks(source: str, path: str = "module.py") -> list[dict]:
    """Return one chunk per top-level function/class, with a header that names file and symbol."""
    tree = ast.parse(source)  # raises SyntaxError for invalid code
    lines = source.splitlines()  # to slice original text by line numbers
    chunks: list[dict] = []
    imports = [lines[n.lineno - 1] for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]  # shared context
    for node in tree.body:  # only top-level statements
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = (node.decorator_list[0].lineno if node.decorator_list else node.lineno) - 1  # include decorators
            end = node.end_lineno  # last line of the node (Python 3.8+)
            body = "\n".join(lines[start:end])  # exact source text
            header = f"# file: {path} | symbol: {node.name} | lines {start + 1}-{end}"  # context header
            chunks.append({
                "text": f"{header}\n" + ("\n".join(imports) + "\n\n" if imports else "") + body,
                "symbol": node.name, "kind": type(node).__name__, "start": start + 1, "end": end,
            })
    return chunks


code = '''
import math

def duty(value: float, rate: float) -> float:
    """Return duty amount."""
    return value * rate

class Classifier:
    def code_for(self, text: str) -> str:
        return "8518.30"
'''
for c in python_chunks(code):
    print(c["kind"], c["symbol"], c["start"], c["end"])
```

## 💻 Code Example — Advanced
```python
# Production: big-unit handling, multi-language fallback with LangChain, async, error handling
import ast
import asyncio
import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

log = logging.getLogger("code_chunker")
EXT_TO_LANG = {".py": Language.PYTHON, ".js": Language.JS, ".ts": Language.TS, ".java": Language.JAVA, ".go": Language.GO}


def split_python_file(path: Path, max_chars: int = 1500) -> list[Document]:
    source = path.read_text(encoding="utf-8")
    docs: list[Document] = []
    try:
        chunks = python_chunks(source, str(path))  # from the Basic example
    except SyntaxError:
        log.warning("syntax error in %s; falling back to text splitting", path)
        return split_generic(path, source, max_chars)
    inner = RecursiveCharacterTextSplitter.from_language(Language.PYTHON, chunk_size=max_chars, chunk_overlap=100)
    for c in chunks:
        meta = {"source": str(path), "symbol": c["symbol"], "kind": c["kind"], "start_line": c["start"]}
        if len(c["text"]) <= max_chars:
            docs.append(Document(page_content=c["text"], metadata=meta))
        else:  # long class/function: split inside, keep header on every part
            header = c["text"].split("\n", 1)[0]
            for part in inner.split_text(c["text"]):
                docs.append(Document(page_content=part if part.startswith("# file:") else f"{header}\n{part}", metadata=meta))
    return docs


def split_generic(path: Path, source: str, max_chars: int) -> list[Document]:
    lang = EXT_TO_LANG.get(path.suffix)
    splitter = (RecursiveCharacterTextSplitter.from_language(lang, chunk_size=max_chars, chunk_overlap=100)
                if lang else RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=100))
    return splitter.create_documents([source], metadatas=[{"source": str(path)}])


async def split_repo(root: str, max_chars: int = 1500) -> list[Document]:
    out: list[Document] = []
    for p in Path(root).rglob("*"):
        if p.suffix not in EXT_TO_LANG or ".git" in p.parts or "node_modules" in p.parts:
            continue  # skip vendor and VCS folders
        try:
            if p.suffix == ".py":
                out += await asyncio.to_thread(split_python_file, p, max_chars)
            else:
                out += await asyncio.to_thread(split_generic, p, p.read_text(encoding="utf-8"), max_chars)
        except (OSError, UnicodeDecodeError):
            log.exception("skipping unreadable file %s", p)
    return out
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class CodeReq(BaseModel):
    source: str
    path: str = "snippet.py"


@app.post("/chunk/code")
async def chunk_code(req: CodeReq) -> dict:
    try:
        chunks = python_chunks(req.source, req.path)  # from Basic example
    except SyntaxError as exc:
        raise HTTPException(status_code=422, detail=f"invalid Python: {exc.msg} (line {exc.lineno})")
    return {"count": len(chunks), "symbols": [c["symbol"] for c in chunks]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

py_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=600, chunk_overlap=60)
docs = py_splitter.create_documents(["def duty(v, r):\n    return v * r\n\n\nclass A:\n    pass\n"])
print(RecursiveCharacterTextSplitter.get_separators_for_language(Language.PYTHON))
# e.g. ['\nclass ', '\ndef ', '\n\tdef ', '\n\n', '\n', ' ', '']  -> splits at class/def boundaries first
# LangChain also has LanguageParser (document loader) that parses functions/classes via tree-sitter.
# In LangGraph: a "code_search" node can retrieve these chunks and a second node can ask the LLM to explain them.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Splitting code with a prose splitter
```python
# Wrong: RecursiveCharacterTextSplitter(chunk_size=300) -> a def line ends up in one chunk, its body in the next
# Right: language-aware splitting (ast, tree-sitter, or from_language(Language.PYTHON, ...))
```

❌ Mistake 2: No file or symbol context in the chunk
```python
# Wrong: chunk = "return value * rate"  (what function? what file?)
# Right: chunk text starts with "# file: pricing/duty.py | symbol: calculate_duty" and metadata stores the same
```

---

## 🧠 Tricky Interview Question

**Q**: "A developer asks the code assistant 'where is the VAT rate applied?'. Retrieval returns the function that defines `VAT_RATE = 0.18` but not the function that uses it. How do you improve it?"

**Answer**: Pure similarity finds the constant definition because the query words match it. Improve by (1) indexing both code and natural-language summaries per function (LLM-generated docstrings), (2) adding call-graph or import metadata so you can expand from a retrieved symbol to its callers and callees, (3) hybrid search with identifier matching (BM25 on symbol names), (4) retrieving small chunks but expanding to the enclosing function/class, and (5) evaluating with real developer questions rather than generic text queries.

---

## ⚫ Interview Questions + Answers

Q1: Why not use a normal text splitter for code?
A1: It ignores syntax and can separate a function signature from its body, producing meaningless chunks.

Q2: What are two ways to split code by structure?
A2: Parse with ast or tree-sitter to extract functions/classes, or use language-specific separators (for example `\nclass `, `\ndef `) in a recursive splitter.

Q3: What context should each code chunk carry?
A3: File path, symbol name, language, line range, and relevant imports or the class name for methods.

Q4: How do you handle very large functions?
A4: Split inside at logical boundaries (blank lines, statements) and repeat the header with the signature in each part.

Q5: How would you build a code-RAG system for a 2M-line monorepo?
A5: Parse with tree-sitter for all languages, chunk by symbol, store metadata (path, symbol, imports, git commit), embed code plus LLM summaries with a code-capable embedding model, use hybrid search, update incrementally by git diff and file hash, and respect permissions per repository. Evaluate using real developer questions with known answer locations.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code search assistants, repo Q&A, documentation generation

❌ Avoid when:
- You only index README/docs (use Markdown splitting)
- Generated, minified or vendored code (exclude it)

---

## 📊 Visual Diagram
```
 duty.py
 ┌───────────────────────────────┐
 │ import math                   │
 │ def calculate_duty(...): ...  │ ──► chunk 1  [# file: duty.py | symbol: calculate_duty]
 │ def apply_exemptions(...):... │ ──► chunk 2  [# file: duty.py | symbol: apply_exemptions]
 │ class Classifier:             │ ──► chunk 3  [class header + methods; long -> sub-chunks]
 └───────────────────────────────┘
 each chunk: header + (imports) + complete unit + metadata {path, symbol, lines}
```

---

## 💰 Cost Impact
- Code tokenizes less efficiently than prose (symbols, indentation), so 1,000 characters of code can be 300-400 tokens. Budget embedding and prompt sizes in tokens, not characters.
- Headers add tokens per chunk (about 15-25), a small cost with a large retrieval benefit.
- LLM-generated summaries per function add an LLM call per chunk at ingestion: use a small model, do it once, cache by file hash, and re-run only on changed files.
- At query time return only the top 3-5 symbols to keep prompts small.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AST | Tree form of source code | Code का tree रूप |
| tree-sitter | Multi-language parser | कई languages का parser |
| Symbol | Named function/class/variable | नामित function/class |
| Call graph | Who calls whom | कौन किसे call करता है |
| Language-aware splitter | Splitter using code separators | Code separators वाला splitter |

---

## ⚡ 3-Line Summary
English: Code splitting cuts at functions and classes using parsers or language-aware separators. Each chunk carries file path, symbol name and imports as context. Split large units internally and keep the header on every part.
Hindi: Code splitting parsers या language-aware separators से functions और classes पर काटती है। हर chunk में संदर्भ के रूप में file path, symbol नाम और imports रहते हैं। बड़े units को अंदर से तोड़ो और हर हिस्से में header रखो।

---

## ➡️ Next Topic
**164. HTML Splitting** — splitting web pages by tags and headings while dropping navigation noise.
