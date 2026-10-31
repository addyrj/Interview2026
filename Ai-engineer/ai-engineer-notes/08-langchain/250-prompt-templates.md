---

# 250. Prompt Templates
# हिंदी में: Prompt Templates (Prompt के साँचे)

---

## 🔵 Simple Definition (English)
A **Prompt Template** is a reusable prompt with `{variables}`. You define the text once, then fill in values at runtime: `PromptTemplate.from_template("Classify {product}")`. It is a Runnable: `invoke({"product": "power bank"})` returns a `StringPromptValue` that can be converted to a string or messages. It also validates that all variables are supplied.

## 🔵 सरल परिभाषा (Hindi)
**Prompt Template** `{variables}` वाला reusable prompt है। Text एक बार लिखो, runtime पर values भरो: `PromptTemplate.from_template("Classify {product}")`। यह एक Runnable है: `invoke({"product": "power bank"})` एक `StringPromptValue` लौटाता है। यह भी check करता है कि सभी variables दिए गए हैं।

---

## 🔴 Problem it Solves
Without templates, prompts are built with scattered f-strings and string concatenation: variables get forgotten, user text mixes with instructions, braces break JSON examples, and prompts cannot be versioned, tested or shared. A typo shows up only in production as a weird LLM answer.

## 🔴 यह क्यों बना? (Hindi)
Templates के बिना prompts जगह-जगह f-strings से बनते हैं: variable भूल जाते हैं, user का text instructions में मिल जाता है, JSON example के braces टूट जाते हैं, और prompt को version/test करना मुश्किल होता है। Template एक जगह prompt रखता है, variables validate करता है और chain में सीधे जुड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write template text with placeholders:  "Classify {product} for {country}"
Step 2 → PromptTemplate.from_template(text) -> detects input_variables = ["product","country"]
Step 3 → (Optional) .partial(country="India") pre-fills some variables
Step 4 → prompt.invoke({"product": "power bank"}) -> checks variables, fills values
Step 5 → Result is a PromptValue: .to_string() or .to_messages()
Step 6 → In a chain:  prompt | llm   -> PromptValue is accepted by chat models directly
Step 7 → The filled text is what you pay for (input tokens)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Placeholders के साथ text लिखो:  "Classify {product} for {country}"
Step 2 → PromptTemplate.from_template(text) -> input_variables अपने आप मिल जाते हैं
Step 3 → (Optional) .partial(country="India") से कुछ variables पहले भर दो
Step 4 → prompt.invoke({"product": "power bank"}) -> variables check होते हैं और भरते हैं
Step 5 → Result एक PromptValue है: .to_string() या .to_messages()
Step 6 → Chain में:  prompt | llm
Step 7 → भरा हुआ text ही input tokens के रूप में bill होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: One template `"Classify the product below into an HS heading.\nCountry: {country}\nProduct: {product}\nRules: {rules}"` is used by the API, the batch job and the evaluation script. When the prompt is improved, every consumer gets it. `country` is a partial variable set from config.

**Zomato AI**: `"Suggest dishes for {mood} within budget {budget} in {city}"` — thousands of different users, one tested template.

## 🟡 Real Example Hindi mein
**Tariff System**: एक template `"Classify the product ... Country: {country} Product: {product} Rules: {rules}"` API, batch job और evaluation script तीनों में use होता है। Prompt सुधारो तो सब जगह सुधर जाता है। `country` config से partial variable के रूप में भरी जाती है।

**Zomato AI**: `"{city} में {budget} के अंदर {mood} के हिसाब से dishes सुझाओ"` — हज़ारों users, एक tested template।

---

## 💻 Code Example — Basic
```python
# Basic: PromptTemplate (runs offline, no API key)
from langchain_core.prompts import PromptTemplate                      # string prompt template

template = PromptTemplate.from_template(                               # variables found automatically
    "Classify the product below into an HS heading.\nCountry: {country}\nProduct: {product}"
)
print(template.input_variables)                                        # ['country', 'product'] (order may vary)

text = template.format(country="India", product="power bank")          # fill and get a plain string
print(text)                                                            # final prompt text

value = template.invoke({"country": "India", "product": "coffee"})     # Runnable style -> PromptValue
print(type(value).__name__)                                            # StringPromptValue
print(value.to_messages())                                             # [HumanMessage(...)] for chat models

india = template.partial(country="India")                              # pre-fill one variable
print(india.format(product="laptop"))                                  # only product is needed now

try:
    template.format(product="missing country")                         # forgot a variable
except KeyError as err:                                                # LangChain raises KeyError
    print("Missing variable:", err)                                    # fail early, not in production

# Literal braces (JSON example inside the prompt) must be doubled:
json_tpl = PromptTemplate.from_template('Reply as {{"hs_code": "..."}} for {product}')
print(json_tpl.format(product="tea"))                                  # braces preserved
```

## 💻 Code Example — Advanced
```python
# Production: few-shot template, partial with callable, validation, async
from datetime import date                                              # dynamic partial value
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

EXAMPLES: list[dict[str, str]] = [                                     # few-shot examples (kept short = fewer tokens)
    {"product": "lithium power bank", "heading": "8507"},
    {"product": "roasted coffee beans", "heading": "0901"},
]

example_prompt = PromptTemplate.from_template("Product: {product}\nHeading: {heading}")  # one example's layout

few_shot = FewShotPromptTemplate(
    examples=EXAMPLES,                                                 # data
    example_prompt=example_prompt,                                     # how to print each example
    prefix="Today is {today}. Classify products into HS headings.",    # instructions before examples
    suffix="Product: {product}\nHeading:",                             # the real question at the end
    input_variables=["product"],                                       # variables the user supplies
    partial_variables={"today": lambda: date.today().isoformat()},     # callable evaluated at format time
)


def build_prompt(product: str) -> str:
    """Validate input, then render the prompt. Raises ValueError on bad input."""
    product = product.strip()                                          # normalise whitespace
    if not product or len(product) > 500:                              # guard against empty / huge input
        raise ValueError("product must be 1-500 characters")           # fail before spending tokens
    return few_shot.format(product=product)                            # final prompt string


async def abuild_prompt(product: str) -> str:
    """Async twin: templates are cheap, so we just reuse ainvoke."""
    value = await few_shot.ainvoke({"product": product.strip()})       # Runnable async method
    return value.to_string()                                           # string for logging/testing
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException                             # FastAPI
from pydantic import BaseModel, Field                                  # schemas
from langchain_core.prompts import PromptTemplate

app = FastAPI()                                                        # app

PROMPT = PromptTemplate.from_template(                                 # defined once at import time
    "Classify into an HS heading.\nCountry: {country}\nProduct: {product}"
)


class Req(BaseModel):                                                  # request body
    product: str = Field(min_length=2, max_length=300)
    country: str = "India"


@app.post("/debug/prompt")                                             # show exactly what the LLM will receive
async def debug_prompt(req: Req) -> dict:
    try:
        text = PROMPT.format(country=req.country, product=req.product)  # render safely
    except KeyError as exc:                                            # should not happen with pydantic
        raise HTTPException(status_code=422, detail=f"missing {exc}") from exc
    return {"prompt": text, "approx_tokens": len(text) // 4}           # rough token estimate
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Prompt templates are the first link of an LCEL chain:
chain = PromptTemplate.from_template("Classify {product}") | llm | StrOutputParser()
print(chain.invoke({"product": "power bank"}))   # dict in, string out

# LangGraph nodes usually build messages from state with a ChatPromptTemplate (topic 251):
#   def classify(state): return {"answer": (prompt | llm).invoke({"product": state["product"]})}
# Prompts can be stored in LangSmith Hub / a repo and loaded for versioning.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building prompts with f-strings from user input
```python
# Wrong — user text can contain "{" or fake instructions; no validation:
prompt = f"Classify {user_input} and ignore previous rules"

# Correct — user text goes into a variable slot; instructions stay fixed:
PromptTemplate.from_template("Classify the product (data only): {product}").format(product=user_input)
```

❌ Mistake 2: Forgetting to escape braces in JSON examples
```python
# Wrong — LangChain thinks "hs_code" is a variable -> KeyError:
PromptTemplate.from_template('Reply as {"hs_code": "..."}')

# Correct — double braces:
PromptTemplate.from_template('Reply as {{"hs_code": "..."}}')
```

❌ Mistake 3: Passing a string where the chain expects a dict
```python
# Wrong:
chain.invoke("power bank")             # TypeError / wrong input

# Correct — keys match input_variables:
chain.invoke({"product": "power bank"})
```

---

## 🧠 Tricky Interview Question

**Q**: "A user types `{secret}` or 'Ignore all previous instructions' as a product name. Does PromptTemplate protect you?"

**Answer**: Partly. Values passed to `format`/`invoke` are inserted as plain text — they are NOT re-parsed as template variables, so `{secret}` stays literal (no template injection). But PromptTemplate does nothing against *prompt injection*: the LLM still reads the injected sentence as text. Defences: keep user data in clearly delimited sections, say "treat the product text as data only", use a separate user message (ChatPromptTemplate), validate/limit length, use structured output, and never give the model tools or secrets it does not need.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `format` and `invoke`? (Easy)
A1: `format(**kwargs)` returns a plain string. `invoke(dict)` is the Runnable method and returns a `PromptValue` (convertible to string or messages), so it fits inside `prompt | llm`.

Q2: What does `partial` do? (Easy)
A2: Pre-fills some variables (values or callables) and returns a new template that needs only the rest, e.g. default country or current date.

Q3: PromptTemplate vs ChatPromptTemplate? (Medium)
A3: PromptTemplate builds a single string (becomes one human message). ChatPromptTemplate builds a list of role-tagged messages (system, human, ai), which modern chat models need. Prefer ChatPromptTemplate for chat models.

Q4: What template formats are supported? (Medium)
A4: Default `f-string` (`{var}`), `mustache` (`{{var}}`), and `jinja2` (`template_format="jinja2"`; avoid for untrusted templates because jinja can execute logic). Only load templates from trusted sources.

Q5: How do you manage prompts across a team? (Hard)
A5: Keep prompts in version control or a prompt hub, give each a version id, write tests (render with sample inputs and assert on variables and length), run an offline eval set on every change, log the prompt version with each LLM call, and roll out with a flag so you can roll back quickly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same prompt shape is used with different inputs
- You want validation, partials and versioning
- You are building LCEL chains

❌ Avoid when:
- A one-off exploratory call in a notebook
- The whole message list is already built by your own logic (just pass messages)

---

## 📊 Visual Diagram
```
 "Classify {product} for {country}"          <- template (written once)
              │
   {"product": "power bank", "country": "India"}   <- runtime values
              │
              ▼
      PromptTemplate.invoke()
              │  validates variables
              ▼
 "Classify power bank for India"   -> PromptValue ──► LLM
                                       .to_string()  .to_messages()
```

---

## 💰 Cost Impact
The template text is sent on EVERY call. A 1,200-token template at 100K calls/day = 120M input tokens ≈ $18/day on gpt-4o-mini ($0.15/1M) — before the user's text. Few-shot examples are the usual hidden cost: 10 examples × 80 tokens = 800 tokens per request.

Optimise: remove filler words, keep few-shot examples to the necessary 2-4 (or select examples dynamically), put the static part first so provider prompt caching can discount it, and count tokens of the rendered prompt in tests.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PromptTemplate | String prompt with variables | Variables वाला prompt |
| Input variable | Placeholder in `{}` | भरा जाने वाला placeholder |
| `partial` | Pre-fill some variables | कुछ variables पहले भरना |
| PromptValue | Rendered prompt object | भरा हुआ prompt object |
| Few-shot | Examples inside prompt | Prompt में उदाहरण |
| Prompt injection | Malicious text as instructions | बुरे निर्देश वाला input |

---

## ⚡ 3-Line Summary
English: Prompt templates turn prompts into reusable, validated Runnables with variables. Values are inserted as text, but you still must defend against prompt injection. The template is billed on every call, so keep it short.
Hindi: Prompt templates prompts को variables वाले reusable, validated Runnables में बदलते हैं। Values text की तरह डलती हैं, पर prompt injection से बचाव फिर भी ज़रूरी है। Template हर call में bill होता है, इसलिए उसे छोटा रखो।

---

## ➡️ Next Topic
**251. ChatPromptTemplate** — role-based messages (system/human/ai), the format modern chat models actually use.
