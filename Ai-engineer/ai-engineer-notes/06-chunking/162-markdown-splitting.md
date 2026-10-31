---

# 162. Markdown Splitting
# हिंदी में: Markdown Splitting (Headings के आधार पर)

---

## 🔵 Simple Definition (English)
Markdown splitting cuts a document at its headings (`#`, `##`, `###`) and stores the heading path (for example "Chapter 85 > Headphones > Exceptions") as metadata or as a prefix on each chunk. Each chunk is one section, with its context attached.

## 🔵 सरल परिभाषा (Hindi)
Markdown splitting document को उसकी headings (`#`, `##`, `###`) पर काटती है और heading path (जैसे "Chapter 85 > Headphones > Exceptions") को metadata या हर chunk के prefix में रखती है। हर chunk एक section होता है, अपने संदर्भ के साथ।

---

## 🔴 Problem it Solves
A paragraph like "This does not apply to items under 5 USD." is meaningless without knowing which section it belongs to. Heading-based splitting keeps sections whole and gives each chunk its context, improving both retrieval and citations. It is ideal for docs, READMEs, wikis, and converted HTML/PDF.

## 🔴 यह क्यों बना? (Hindi)
"यह 5 USD से कम items पर लागू नहीं होता।" जैसे paragraph का मतलब तब तक नहीं जब तक पता न हो कि वह किस section का है। Heading-based splitting sections को पूरा रखती है और हर chunk को उसका संदर्भ देती है, जिससे retrieval और citations दोनों सुधरते हैं। Docs, READMEs, wikis और converted HTML/PDF के लिए आदर्श।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parse lines; detect headings with ^#{1,6}\s
Step 2 → Maintain a stack of current headings: {h1: ..., h2: ..., h3: ...}
Step 3 → Collect body text under the current heading until the next heading
Step 4 → Emit a chunk = body text + metadata {h1, h2, h3}
Step 5 → If a section is too long, sub-split it (recursive splitter), keeping the same metadata
Step 6 → (Optional) prefix the chunk text with its heading path before embedding
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Lines parse करो; headings ^#{1,6}\s से पहचानो
Step 2 → मौजूदा headings का stack रखो: {h1: ..., h2: ..., h3: ...}
Step 3 → अगली heading आने तक मौजूदा heading के नीचे का body text जमा करो
Step 4 → Chunk बनाओ = body text + metadata {h1, h2, h3}
Step 5 → Section बहुत लंबा हो तो recursive splitter से तोड़ो, वही metadata रखकर
Step 6 → (Optional) embed से पहले chunk text के आगे heading path जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: the internal HS guide is Markdown: `# Chapter 85`, `## 8518 Headphones`, `### Exceptions`. A question "are microphone headsets excluded?" retrieves the "Exceptions" section whose metadata reads `Chapter 85 > 8518 Headphones > Exceptions`, so the LLM answers with the right scope and cites the section.

**Zomato AI**: restaurant onboarding docs in Markdown: sections for Menu, Pricing, Refunds; "Refunds" chunks are retrieved for refund questions without Menu noise.

## 🟡 Real Example Hindi mein
**Tariff System**: internal HS guide Markdown में है: `# Chapter 85`, `## 8518 Headphones`, `### Exceptions`। "क्या microphone headsets बाहर हैं?" पर "Exceptions" section मिलता है जिसका metadata `Chapter 85 > 8518 Headphones > Exceptions` है, इसलिए LLM सही दायरे में जवाब देता है और section cite करता है।

**Zomato AI**: Markdown में restaurant onboarding docs: Menu, Pricing, Refunds sections; refund सवालों पर "Refunds" chunks मिलते हैं, Menu का शोर नहीं।

---

## 💻 Code Example — Basic
```python
# Runs offline: heading-aware Markdown splitter that keeps the heading path as metadata
import re

FENCE = "`" * 3  # the three-backtick fence marker, built this way so it is easy to read here


def markdown_sections(md: str) -> list[dict]:
    """Return [{'path': 'A > B', 'text': '...'}] for each section that has body text."""
    stack: list[tuple[int, str]] = []  # (level, title) of currently open headings
    sections: list[dict] = []
    body: list[str] = []  # lines of the current section
    in_code = False  # do not treat '#' inside fenced code as headings

    def flush() -> None:
        text = "\n".join(body).strip()
        if text:
            sections.append({"path": " > ".join(t for _, t in stack), "text": text})
        body.clear()

    for line in md.splitlines():
        if line.strip().startswith(FENCE):
            in_code = not in_code  # toggle fenced code state
        m = None if in_code else re.match(r"^(#{1,6})\s+(.*)$", line)  # heading detection
        if m:
            flush()  # close the previous section
            level, title = len(m.group(1)), m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()  # leave deeper/equal headings
            stack.append((level, title))  # open the new heading
        else:
            body.append(line)
    flush()
    return sections


md = """# Chapter 85
Electrical machinery.
## 8518 Headphones
Headphones are classified under 8518.30.
### Exceptions
Models with microphones go to 8518.40.
"""
for s in markdown_sections(md):
    print(s["path"], "->", s["text"])
```

## 💻 Code Example — Advanced
```python
# Production: LangChain header splitter + size control + heading prefix, async, error handling
import asyncio
import logging

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

log = logging.getLogger("markdown_chunker")

HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]  # markdown marker -> metadata key


def split_markdown(md: str, source: str, max_chars: int = 1000, overlap: int = 100) -> list[Document]:
    if not md.strip():
        return []
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS, strip_headers=True)  # one Document per section
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=overlap)  # for long sections
    try:
        sections = header_splitter.split_text(md)
        chunks = size_splitter.split_documents(sections)  # metadata (h1/h2/h3) is copied to sub-chunks
    except Exception:
        log.exception("markdown split failed for %s", source)
        raise
    for c in chunks:
        path = " > ".join(c.metadata[k] for _, k in HEADERS if k in c.metadata)  # heading path
        c.metadata.update({"source": source, "section_path": path})
        c.page_content = f"[{path}]\n{c.page_content}" if path else c.page_content  # prefix improves embeddings
    return chunks


async def asplit_markdown(md: str, source: str, **kw) -> list[Document]:
    return await asyncio.to_thread(split_markdown, md, source, **kw)


if __name__ == "__main__":
    text = "# Ch 85\n## 8518\nHeadphones are 8518.30.\n### Exceptions\nMicrophone models are 8518.40.\n"
    for d in asyncio.run(asplit_markdown(text, "guide.md")):
        print(d.metadata, repr(d.page_content))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class MdReq(BaseModel):
    markdown: str
    source: str = "doc.md"


@app.post("/chunk/markdown")
async def chunk_markdown(req: MdReq) -> dict:
    docs = await asplit_markdown(req.markdown, req.source)  # from Advanced example
    return {"count": len(docs), "sections": sorted({d.metadata.get("section_path", "") for d in docs})}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Typical docs pipeline: load .md files -> header split -> store with metadata -> filter by section later
from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader("docs/", glob="**/*.md", loader_cls=TextLoader)
chunks = [c for d in loader.load() for c in split_markdown(d.page_content, d.metadata["source"])]
# vector_store.add_documents(chunks)
# retriever = vector_store.as_retriever(search_kwargs={"k": 4, "filter": {"h1": "Chapter 85"}})
# In LangGraph the metadata lets a router node restrict retrieval to a chapter.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating `#` inside code blocks as headings
```python
# Wrong: "# install deps" in a bash snippet starts a new section
# Right: track fenced-code state (three backticks) while scanning; MarkdownHeaderTextSplitter handles code fences by default
```

❌ Mistake 2: Dropping heading text from the chunk and from metadata
```python
# Wrong: strip_headers=True and no metadata kept -> chunk "Models with microphones go to 8518.40" has no subject
# Right: keep headings in metadata AND prefix the chunk with its path before embedding
```

---

## 🧠 Tricky Interview Question

**Q**: "Your Markdown docs have very long sections (5,000 words under one `##`) and very short ones (one line). Heading-based chunks give poor retrieval. What do you do?"

**Answer**: Use two-level logic. First split by headings (to get context and metadata), then apply a size-based splitter inside long sections (keeping the same heading metadata) and merge tiny sections into their parent or next sibling until a minimum size. Prefix each chunk with its heading path so even small chunks stay interpretable. Optionally keep the whole section as a "parent" document and retrieve small children but pass the parent to the LLM.

---

## ⚫ Interview Questions + Answers

Q1: What does MarkdownHeaderTextSplitter do?
A1: Splits Markdown at the headings you specify and stores the headings in each Document's metadata.

Q2: Why is the heading path useful?
A2: It provides context for ambiguous text, enables metadata filters and gives precise citations.

Q3: What if a section is too long?
A3: Sub-split with a recursive splitter, keeping the section's metadata.

Q4: Does it work for HTML or PDF?
A4: Convert them to Markdown first (or use HTMLHeaderTextSplitter for HTML). Layout-aware PDF converters can produce Markdown with headings.

Q5: How would you design retrieval so answers contain full context while searching small chunks?
A5: Index small child chunks (200-400 tokens) with a `parent_id` and heading path, retrieve top-k children, dedupe by parent, then fetch parent sections (capped at a token budget) for the LLM. LangChain's ParentDocumentRetriever implements the pattern.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Documentation, wikis, READMEs, guides, reports with consistent headings

❌ Avoid when:
- Text with no headings (transcripts, emails)
- Headings are inconsistent or purely decorative

---

## 📊 Visual Diagram
```
 # Chapter 85
 ## 8518 Headphones
 Headphones are 8518.30.             ──► chunk A  meta: {h1:"Chapter 85", h2:"8518 Headphones"}
 ### Exceptions
 Microphone models go to 8518.40.    ──► chunk B  meta: {h1:"Chapter 85", h2:"8518 Headphones", h3:"Exceptions"}
 ## 8517 Phones
 Smartphones are 8517.13.            ──► chunk C  meta: {h1:"Chapter 85", h2:"8517 Phones"}
```

---

## 💰 Cost Impact
- A heading prefix adds a few tokens to every chunk (for example 10-15 tokens); for 10,000 chunks that is about 100K-150K extra embedding tokens, a small one-time cost that usually improves retrieval.
- Metadata filters (by chapter) shrink the search space and lower the number of irrelevant chunks in prompts.
- Parent-child retrieval raises prompt tokens (parent sections are bigger), so cap the parent size (for example 1,000 tokens).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Heading path | Chain of headings above text | ऊपर की headings की श्रृंखला |
| Section | Text under one heading | एक heading के नीचे का text |
| Fenced code | Code between ``` marks | ``` के बीच का code |
| Parent document | Larger section for a chunk | Chunk का बड़ा section |
| strip_headers | Remove heading lines from text | Heading lines हटाना |

---

## ⚡ 3-Line Summary
English: Markdown splitting follows headings so each chunk is a section with its heading path attached. Sub-split long sections and merge tiny ones. Prefix chunks with their path and use it for filters and citations.
Hindi: Markdown splitting headings का पालन करती है, इसलिए हर chunk अपनी heading path के साथ एक section होता है। लंबे sections को तोड़ो और छोटे मिलाओ। Chunks के आगे path जोड़ो और उसे filters और citations में use करो।

---

## ➡️ Next Topic
**163. Code Splitting** — splitting source code by functions and classes, not by characters.
