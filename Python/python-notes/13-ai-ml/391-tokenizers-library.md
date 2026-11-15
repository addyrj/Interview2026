---

# 391. tokenizers Library
# हिंदी में: tokenizers Library (Hugging Face की तेज़ tokenizer library)

---

## 🔵 Simple Definition (English)
`tokenizers` is Hugging Face's fast library (written in Rust) that turns text into token ids and back. It lets you train your own tokenizer (BPE, WordPiece, Unigram) or load a saved one, and handles padding, truncation and offsets.

## 🔵 सरल परिभाषा (Hindi)
`tokenizers` Hugging Face की तेज़ library है (Rust में लिखी) जो text को token ids में और वापस text में बदलती है। इससे आप अपना tokenizer train कर सकते हैं (BPE, WordPiece, Unigram) या saved tokenizer load कर सकते हैं, और padding, truncation व offsets भी मिलते हैं।

---

## 🔴 Problem it Solves
Models understand numbers, not text. Splitting by spaces fails for rare words ("Razorpayx"), typos and Hindi text. Subword tokenization splits unknown words into known pieces (`sw` + `##ig` + `##gy`) so the vocabulary stays small and nothing is "unknown". Python-only tokenizers were slow; this Rust library tokenizes a gigabyte of text in about a minute.

## 🔴 यह क्यों बना? (Hindi)
Models को numbers समझ आते हैं, text नहीं। सिर्फ space से बाँटना rare शब्दों ("Razorpayx"), typos और हिंदी text के लिए काम नहीं करता। Subword tokenization अनजान शब्द को जाने-पहचाने टुकड़ों में तोड़ देता है (`sw` + `##ig` + `##gy`), इसलिए vocabulary छोटी रहती है और कोई शब्द "unknown" नहीं होता। Python वाले tokenizers धीमे थे; यह Rust library एक GB text लगभग एक मिनट में tokenize कर देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalizer: clean text (lowercase, strip accents, NFD/NFKC)
Step 2 → Pre-tokenizer: split into rough words (whitespace, punctuation)
Step 3 → Model: split each word into subwords using the vocab (BPE / WordPiece / Unigram)
Step 4 → Post-processor: add special tokens ([CLS] ... [SEP])
Step 5 → Encoding object: tokens, ids, offsets, attention_mask, type_ids
Step 6 → Padding / truncation make a batch the same length
Step 7 → Decoder turns ids back into text
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Normalizer: text साफ करता है (lowercase, accents हटाना)
Step 2 → Pre-tokenizer: text को मोटे शब्दों में बाँटता है (space, punctuation)
Step 3 → Model: vocab से हर शब्द को subwords में तोड़ता है (BPE / WordPiece / Unigram)
Step 4 → Post-processor: special tokens जोड़ता है ([CLS] ... [SEP])
Step 5 → Encoding object: tokens, ids, offsets, attention_mask, type_ids
Step 6 → Padding / truncation से batch की लंबाई बराबर होती है
Step 7 → Decoder ids को वापस text बनाता है
```

---

## 🟡 Real World Example
A fintech company wants a model that understands its own text: "UPI", "NEFT", "razorpayx", merchant names. Public tokenizers split these into many meaningless pieces. They train a BPE tokenizer on their transaction notes so common domain words become single tokens, which saves tokens (and money) and improves accuracy. In an AI app you also use offsets to highlight which characters of a user's message produced a token.

## 🟡 Real Example Hindi mein
एक fintech company ऐसा model चाहती है जो उसका अपना text समझे: "UPI", "NEFT", "razorpayx", merchant names। Public tokenizers इन्हें कई बेमतलब टुकड़ों में तोड़ते हैं। वे अपने transaction notes पर BPE tokenizer train करते हैं ताकि domain के शब्द एक ही token बनें, जिससे tokens (और पैसे) बचते हैं और accuracy बढ़ती है। AI app में offsets से यह भी दिखा सकते हैं कि user के message के कौन से characters से कौन सा token बना।

---

## 💻 Code Example — Basic
```python
# Basic: train a tiny BPE tokenizer and encode text (pip install tokenizers)
from tokenizers import Tokenizer, models, trainers, pre_tokenizers  # core building blocks

corpus: list[str] = [  # tiny training data
    "razorpay payment success", "razorpay payment failed",
    "swiggy order delivered", "zomato order placed payment",
] * 5  # repeated so merges are learned

tok: Tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))  # BPE model with an unknown token
tok.pre_tokenizer = pre_tokenizers.Whitespace()  # split on spaces and punctuation first
trainer = trainers.BpeTrainer(vocab_size=60, special_tokens=["[UNK]", "[PAD]"])  # target vocab size
tok.train_from_iterator(corpus, trainer)  # learn merges from text
print(tok.get_vocab_size())  # final vocabulary size
# Output: 60

enc = tok.encode("razorpay payment failed")  # text -> Encoding object
print(enc.tokens)  # the subword strings
# Output: ['razorpay', 'payment', 'failed']
print(enc.ids)  # numeric ids the model would receive (can differ per training run/version)
# Output: [35, 30, 59]
print(enc.offsets)  # (start, end) character position of each token in the original text
# Output: [(0, 8), (9, 16), (17, 23)]

enc2 = tok.encode("zomato xyz!")  # contains unseen characters
print(enc2.tokens)  # unseen characters become [UNK]
# Output: ['zomat', 'o', '[UNK]', 'y', 'z', '[UNK]']

tok.enable_padding(pad_id=1, pad_token="[PAD]")  # pad batch to the longest item
tok.enable_truncation(max_length=4)  # cut anything longer than 4 tokens
batch = tok.encode_batch(["razorpay payment failed now", "swiggy"])  # encode many at once
print([b.tokens for b in batch])  # padded and truncated
# Output: [['razorpay', 'payment', 'failed', 'n'], ['sw', 'igg', 'y', '[PAD]']]
print([b.attention_mask for b in batch])  # 1 = real token, 0 = padding
# Output: [[1, 1, 1, 1], [1, 1, 1, 0]]
```

## 💻 Code Example — Advanced
```python
# Production style: WordPiece tokenizer with normalizer, [CLS]/[SEP] template, pair input, save/load
import os  # path joining
import tempfile  # temporary folder for the demo
from typing import List  # type hints
from tokenizers import Tokenizer, decoders, models, normalizers, pre_tokenizers, processors, trainers  # parts

CORPUS: List[str] = [  # training sentences
    "Razorpay payment success", "razorpay PAYMENT failed",
    "Swiggy order delivered", "Zomato order placed",
] * 10  # repeat for stable statistics
SPECIAL: List[str] = ["[UNK]", "[PAD]", "[CLS]", "[SEP]"]  # reserved tokens (ids 0 to 3)


def build() -> Tokenizer:  # assemble the whole pipeline
    tok: Tokenizer = Tokenizer(models.WordPiece(unk_token="[UNK]"))  # BERT-style model
    tok.normalizer = normalizers.Sequence(  # normalization steps in order
        [normalizers.NFD(), normalizers.Lowercase(), normalizers.StripAccents()]  # decompose, lower, strip accents
    )
    tok.pre_tokenizer = pre_tokenizers.Whitespace()  # rough word split
    trainer = trainers.WordPieceTrainer(vocab_size=80, special_tokens=SPECIAL)  # trainer config
    tok.train_from_iterator(CORPUS, trainer)  # train
    cls_id: int = tok.token_to_id("[CLS]")  # id of [CLS]
    sep_id: int = tok.token_to_id("[SEP]")  # id of [SEP]
    tok.post_processor = processors.TemplateProcessing(  # add special tokens automatically
        single="[CLS] $A [SEP]",  # one sentence
        pair="[CLS] $A [SEP] $B:1 [SEP]:1",  # two sentences, second gets type_id 1
        special_tokens=[("[CLS]", cls_id), ("[SEP]", sep_id)],  # token -> id map
    )
    tok.decoder = decoders.WordPiece()  # glue ## pieces back together
    tok.enable_padding(pad_id=tok.token_to_id("[PAD]"), pad_token="[PAD]")  # pad to longest
    tok.enable_truncation(max_length=10)  # model limit
    return tok  # ready


tok: Tokenizer = build()  # create
print(tok.get_vocab_size())  # vocab size
# Output: 80
e = tok.encode("RAZORPAY Payment")  # uppercase is normalized
print(e.tokens, e.type_ids)  # [CLS]/[SEP] added automatically
# Output: ['[CLS]', 'razorpay', 'payment', '[SEP]'] [0, 0, 0, 0]

batch = tok.encode_batch(["razorpay payment failed", "razorpay"])  # two lengths
print([b.tokens for b in batch])  # second is padded
# Output: [['[CLS]', 'razorpay', 'payment', 'failed', '[SEP]'], ['[CLS]', 'razorpay', '[SEP]', '[PAD]', '[PAD]']]
# (training order is not deterministic: 'failed' may also appear as 'fail', '##ed' on another run)
print([b.attention_mask for b in batch])  # mask hides the padding
# Output: [[1, 1, 1, 1, 1], [1, 1, 1, 0, 0]]

p = tok.encode("swiggy order", "zomato order")  # sentence pair, truncated to 10
print(p.tokens)  # the longest sequence is shortened first
# Output: ['[CLS]', 'sw', '##ig', '##gy', '[SEP]', 'zo', '##mat', '##o', 'order', '[SEP]']
print(p.type_ids)  # 0 = first sentence, 1 = second
# Output: [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
print(tok.decode(tok.encode("swiggy order").ids))  # ids -> text (special tokens skipped by default)
# Output: swiggy order

path: str = os.path.join(tempfile.mkdtemp(), "tokenizer.json")  # where to save
tok.save(path)  # one JSON file holds the whole pipeline
t2: Tokenizer = Tokenizer.from_file(path)  # load it back
print(t2.encode("swiggy order").ids == tok.encode("swiggy order").ids)  # identical behaviour
# Output: True
```

Note: exact ids and splits depend on training data, vocab size and library version. The structure of the output is what matters.

---

## 🟠 JavaScript vs Python Comparison
In JavaScript you usually only load a ready tokenizer (for example `@huggingface/transformers` or `gpt-tokenizer`) to count tokens in the browser. Training happens in Python.

```python
# Python: load and use a saved tokenizer
from tokenizers import Tokenizer  # import
tok = Tokenizer.from_file("tokenizer.json")  # load JSON
enc = tok.encode("hello world")  # encode
print(enc.ids)  # list of ints
```
```javascript
// JavaScript: load a pre-trained tokenizer from the Hub
import { AutoTokenizer } from "@huggingface/transformers";
const tok = await AutoTokenizer.from_pretrained("Xenova/bert-base-uncased");
const out = await tok("hello world");  // out.input_ids
```

Key differences: Python can train and customize every stage; JS packages mainly run inference. The same `tokenizer.json` format can be used on both sides.

---

## 🟠 FastAPI Connection
A FastAPI service can use a tokenizer to count tokens and reject prompts that are too long before calling a model. Load the tokenizer once at startup (it is thread-safe for encoding) and reuse it.

```python
# FastAPI: token-count guard (pip install fastapi httpx tokenizers)
from typing import Dict  # type hints
from fastapi import FastAPI, HTTPException  # app and errors
from fastapi.testclient import TestClient  # test client
from pydantic import BaseModel  # request body
from tokenizers import Tokenizer, models, pre_tokenizers, trainers  # build a tiny tokenizer

tok: Tokenizer = Tokenizer(models.WordLevel(unk_token="[UNK]"))  # simple word-level model
tok.pre_tokenizer = pre_tokenizers.Whitespace()  # split on whitespace
tok.train_from_iterator(["hello world how are you"], trainers.WordLevelTrainer(special_tokens=["[UNK]"]))  # tiny vocab
MAX_TOKENS: int = 4  # prompt limit for the demo

app: FastAPI = FastAPI()  # create app


class Prompt(BaseModel):  # request body
    text: str  # user text


@app.post("/count")  # endpoint
def count(p: Prompt) -> Dict[str, int]:  # sync def: tokenizing is CPU work
    n: int = len(tok.encode(p.text).ids)  # number of tokens
    if n > MAX_TOKENS:  # too long
        raise HTTPException(status_code=413, detail=f"{n} tokens, max {MAX_TOKENS}")  # payload too large
    return {"tokens": n}  # ok


c: TestClient = TestClient(app)  # in-process client
print(c.post("/count", json={"text": "hello world"}).json())  # short prompt
# Output: {'tokens': 2}
print(c.post("/count", json={"text": "hello world how are you"}).status_code)  # five tokens
# Output: 413
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a different tokenizer than the model was trained with
✅ Correct: load the tokenizer that ships with the model (`Tokenizer.from_pretrained("bert-base-uncased")`)

```python
# Wrong: ids from tokenizer A fed to model B -> garbage output, no error
# Right: same tokenizer file/name as the model
```

❌ Mistake 2: Forgetting padding and the attention mask in batches
✅ Correct: enable padding and pass `attention_mask` to the model

```python
# Wrong: ragged lists of ids cannot become a tensor
# Right: tok.enable_padding(...); use enc.ids and enc.attention_mask for every item
```

❌ Mistake 3: Counting words instead of tokens for cost/limits
✅ Correct: count with the real tokenizer (`len(enc.ids)`)

```python
# Wrong: len(text.split()) -> underestimates; Hindi and code use many more tokens per word
# Right: len(tok.encode(text).ids)
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print for the vocabulary `{"[UNK]": 0, "play": 1, "##ing": 2}` with a WordPiece model?

```python
from tokenizers import Tokenizer, models, pre_tokenizers
tok = Tokenizer(models.WordPiece({"[UNK]": 0, "play": 1, "##ing": 2}, unk_token="[UNK]"))
tok.pre_tokenizer = pre_tokenizers.Whitespace()
print(tok.encode("playing").tokens, tok.encode("played").tokens)
```

**Answer**:
```
['play', '##ing'] ['[UNK]']
```
WordPiece matches the longest known prefix, then continues with `##` pieces. "played" would need `##ed` which is missing, so the WHOLE word becomes `[UNK]` (not `play` + `[UNK]`). This is a known WordPiece behaviour, and is one reason byte-level BPE (GPT style) never produces unknowns.

---

## ⚫ Interview Questions + Answers

Q1: BPE vs WordPiece vs Unigram?
A1: BPE merges the most frequent pair of symbols repeatedly. WordPiece merges the pair that maximizes training-data likelihood (BERT). Unigram starts large and prunes tokens by loss (SentencePiece, T5).

Q2: Why subwords and not words or characters?
A2: Words give a huge vocabulary and unknown tokens. Characters give very long sequences. Subwords balance both.

Q3: What are offsets used for?
A3: They map each token back to character positions in the original text: highlighting, NER, question answering spans.

Q4: What is the attention mask?
A4: A list of 1/0 telling the model which positions are real tokens and which are padding.

Q5: Why is `tokenizers` fast?
A5: It is written in Rust, uses parallelism in `encode_batch`, and avoids Python overhead. Set `TOKENIZERS_PARALLELISM=false` if you fork processes (avoids a warning/deadlock).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Training a custom tokenizer for a domain or language
- You need offsets, fast batch encoding or exact model-compatible ids
- Counting tokens for limits and cost

❌ Avoid when:
- You use OpenAI models only (use `tiktoken`, their exact tokenizer)
- You just load a model with `transformers` (its `AutoTokenizer` already wraps this library)

---

## 📊 Visual Diagram

```
"Razorpay Payment"
   │ Normalizer       -> "razorpay payment"
   │ Pre-tokenizer    -> ["razorpay", "payment"]
   │ Model (WordPiece)-> [razorpay] [payment]
   │ Post-processor   -> [CLS] razorpay payment [SEP]
   ▼
 ids: [2, 40, 37, 3]  + attention_mask [1,1,1,1]  (numbers vary)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token | Smallest unit a model reads | Model की सबसे छोटी इकाई |
| Subword | Piece of a word | शब्द का टुकड़ा |
| Vocab | List of all known tokens | सभी known tokens की सूची |
| Offsets | Character positions of tokens | Tokens की character position |
| Attention mask | Marks real vs padding tokens | असली और padding tokens की पहचान |
| Special tokens | [CLS], [SEP], [PAD], [UNK] | विशेष tokens |

---

## ⚡ 3-Line Summary
English: `tokenizers` converts text to ids through normalizer, pre-tokenizer, model and post-processor. It trains BPE, WordPiece or Unigram, adds padding and truncation, and saves everything in one JSON file. Always use the tokenizer that matches your model.
Hindi: `tokenizers` text को normalizer, pre-tokenizer, model और post-processor से गुज़ारकर ids बनाती है। यह BPE, WordPiece या Unigram train करती है, padding व truncation देती है और सब कुछ एक JSON file में save करती है। हमेशा model से मेल खाता tokenizer इस्तेमाल करें।

---

## ➡️ Next Topic
**392. sentence-transformers** — turn sentences into embedding vectors for semantic search.
