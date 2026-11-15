---

# 397. PyTorch Basics
# हिंदी में: PyTorch की बुनियादी बातें (tensors, autograd, training loop)

---

## 🔵 Simple Definition (English)
PyTorch is a deep learning library. It gives you tensors (like NumPy arrays that can run on a GPU), automatic differentiation (autograd) to compute gradients, and `torch.nn` to build and train neural networks in normal Python code.

## 🔵 सरल परिभाषा (Hindi)
PyTorch एक deep learning library है। इसमें tensors मिलते हैं (NumPy arrays जैसे, पर GPU पर चल सकते हैं), autograd से gradients अपने-आप निकलते हैं, और `torch.nn` से neural networks साधारण Python code में बनाकर train किए जाते हैं।

---

## 🔴 Problem it Solves
Training a neural network needs huge matrix math and the derivative of the loss for every weight. Writing those derivatives by hand is error-prone and NumPy cannot use a GPU. PyTorch records operations as you run them (a dynamic graph), computes gradients with one call (`loss.backward()`), and moves data to GPU with `.to("cuda")`. Because it is plain Python, you can debug with `print` and `pdb`.

## 🔴 यह क्यों बना? (Hindi)
Neural network train करने के लिए बहुत बड़ी matrix math और हर weight के लिए loss का derivative चाहिए। Derivatives हाथ से लिखना गलतियों वाला काम है और NumPy GPU इस्तेमाल नहीं कर सकता। PyTorch चलते समय operations record करता है (dynamic graph), एक call `loss.backward()` से gradients निकालता है और `.to("cuda")` से data GPU पर भेजता है। यह साधारण Python है, इसलिए `print` और `pdb` से debug हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Put data in tensors (torch.tensor / DataLoader batches)
Step 2 → Define a model: class with nn.Module, layers in __init__, math in forward()
Step 3 → Forward pass: predictions = model(x)
Step 4 → Loss: compare predictions with targets (MSELoss, CrossEntropyLoss)
Step 5 → optimizer.zero_grad() clears old gradients
Step 6 → loss.backward() computes gradients for every parameter (autograd)
Step 7 → optimizer.step() updates the weights
Step 8 → Repeat for many batches/epochs, then model.eval() + torch.no_grad() to predict
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data को tensors में रखें (torch.tensor / DataLoader batches)
Step 2 → nn.Module वाली class में model बनाएँ: layers __init__ में, math forward() में
Step 3 → Forward pass: predictions = model(x)
Step 4 → Loss: predictions की तुलना targets से (MSELoss, CrossEntropyLoss)
Step 5 → optimizer.zero_grad() पुराने gradients साफ करता है
Step 6 → loss.backward() हर parameter का gradient निकालता है (autograd)
Step 7 → optimizer.step() weights अपडेट करता है
Step 8 → कई batches/epochs दोहराएँ, फिर model.eval() + torch.no_grad() से predict करें
```

---

## 🟡 Real World Example
A food-delivery company predicts delivery time from distance, traffic and restaurant prep time with a small PyTorch regression model trained nightly. An AI team fine-tunes a text classifier that tags support tickets. A recommendation model embeds users and items as vectors. Hugging Face Transformers models are PyTorch `nn.Module` classes too.

## 🟡 Real Example Hindi mein
Food-delivery company दूरी, traffic और restaurant की तैयारी का समय देखकर delivery time का अनुमान एक छोटे PyTorch regression model से लगाती है जो रोज़ रात train होता है। AI team support tickets को tag करने वाला text classifier fine-tune करती है। Recommendation model users और items को vectors में embed करता है। Hugging Face Transformers के models भी PyTorch `nn.Module` ही हैं।

---

## 💻 Code Example — Basic
```python
# Basic tensors and autograd (pip install torch)
import torch  # the library

x: torch.Tensor = torch.tensor([[1.0, 2.0], [3.0, 4.0]])  # 2x2 tensor of floats
print(x.shape, x.dtype, x.device)  # shape, data type, where it lives
# Output: torch.Size([2, 2]) torch.float32 cpu

print(x @ x)  # matrix multiplication
# Output:
# tensor([[ 7., 10.],
#         [15., 22.]])

print(x.mean(), x.sum(dim=0))  # overall mean, sum down each column
# Output: tensor(2.5000) tensor([4., 6.])

print(x.view(4), x.reshape(1, 4).shape)  # change shape without copying data
# Output: tensor([1., 2., 3., 4.]) torch.Size([1, 4])

w: torch.Tensor = torch.tensor(3.0, requires_grad=True)  # track operations on this value
y: torch.Tensor = w ** 2 + 2 * w  # y = w^2 + 2w
y.backward()  # compute dy/dw automatically
print(w.grad)  # derivative 2w + 2 = 8 at w = 3
# Output: tensor(8.)

a: torch.Tensor = torch.ones(3)  # CPU tensor of ones
b = torch.from_numpy(a.numpy())  # NumPy view sharing the SAME memory
b += 1  # change through the NumPy array
print(a)  # the original tensor changed too
# Output: tensor([2., 2., 2.])

print(torch.zeros(2, 3).shape, torch.arange(5), torch.randn(2).shape)  # common constructors
# Output: torch.Size([2, 3]) tensor([0, 1, 2, 3, 4]) torch.Size([2])

with torch.no_grad():  # do not track gradients (inference mode)
    z: torch.Tensor = w * 2  # computed without a graph
print(z.requires_grad)  # no tracking inside no_grad
# Output: False
```

## 💻 Code Example — Advanced
```python
# Production style: Dataset/DataLoader, nn.Module, training loop, eval, save/load
import os  # file paths
import tempfile  # demo folder
import torch  # tensors
from torch import nn  # layers and losses
from torch.utils.data import DataLoader, TensorDataset  # batching tools

torch.manual_seed(0)  # reproducible random numbers
X: torch.Tensor = torch.rand(256, 2)  # 256 samples, 2 features
y: torch.Tensor = (3 * X[:, 0] + 2 * X[:, 1] + 1).unsqueeze(1)  # true rule: 3a + 2b + 1
loader: DataLoader = DataLoader(TensorDataset(X, y), batch_size=32, shuffle=True)  # mini-batches


class LinearNet(nn.Module):  # every model subclasses nn.Module
    def __init__(self, n_in: int) -> None:  # build layers here
        super().__init__()  # required parent init
        self.net = nn.Sequential(nn.Linear(n_in, 8), nn.ReLU(), nn.Linear(8, 1))  # 2 -> 8 -> 1

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # define the computation
        return self.net(x)  # call model(x), not model.forward(x)


device: str = "cpu"  # use "cuda" or "mps" if available (torch.cuda.is_available())
model: LinearNet = LinearNet(2).to(device)  # move parameters to device
opt: torch.optim.Optimizer = torch.optim.Adam(model.parameters(), lr=0.05)  # optimizer
loss_fn: nn.Module = nn.MSELoss()  # regression loss

for epoch in range(60):  # training epochs
    total: float = 0.0  # running loss
    model.train()  # training mode (dropout/batchnorm active)
    for xb, yb in loader:  # each mini-batch
        xb, yb = xb.to(device), yb.to(device)  # data must be on the same device as the model
        opt.zero_grad()  # clear gradients from the previous step
        loss: torch.Tensor = loss_fn(model(xb), yb)  # forward pass + loss
        loss.backward()  # backpropagation
        opt.step()  # update weights
        total += loss.item() * len(xb)  # .item() converts a 1-value tensor to float
    if epoch % 20 == 0 or epoch == 59:  # print a few lines
        print(epoch, round(total / len(X), 4))  # average loss
# Output (values may differ slightly across PyTorch versions/platforms):
# 0 9.8985
# 20 0.0048
# 40 0.0
# 59 0.0

model.eval()  # evaluation mode
with torch.no_grad():  # no gradients needed to predict
    pred: float = model(torch.tensor([[1.0, 1.0]])).item()  # true answer is 3 + 2 + 1 = 6
print(round(pred, 1))  # learned it
# Output: 6.0

path: str = os.path.join(tempfile.mkdtemp(), "model.pt")  # where to save
torch.save(model.state_dict(), path)  # save only the weights (recommended)
m2: LinearNet = LinearNet(2)  # new model with the same architecture
m2.load_state_dict(torch.load(path, weights_only=True))  # load weights safely
m2.eval()  # inference mode
print(torch.allclose(m2(X[:3]), model(X[:3])))  # same predictions
# Output: True
print(sum(p.numel() for p in model.parameters()))  # count parameters: (2*8+8) + (8*1+1)
# Output: 33
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has TensorFlow.js and ONNX Runtime Web for running models in the browser or Node. Training big models is done in Python with PyTorch, then exported (ONNX/TorchScript) for JS if needed.

```python
# Python (PyTorch)
import torch  # import
t = torch.tensor([1.0, 2.0, 3.0])  # tensor
print((t * 2).sum().item())  # 12.0
```
```javascript
// JavaScript (TensorFlow.js)
import * as tf from "@tensorflow/tfjs";
const t = tf.tensor1d([1, 2, 3]);
t.mul(2).sum().array().then(console.log); // 12
```

Key differences: PyTorch tensors are mutable and tracked by autograd; TF.js tensors are immutable and must be freed (`tf.tidy`). Python training loops are written by hand; JS libraries usually only run inference.

---

## 🟠 FastAPI Connection
Load the trained model once at startup, call `model.eval()`, wrap prediction in `torch.no_grad()` and expose it with a Pydantic request. Use a plain `def` endpoint because inference is CPU/GPU-bound and would block an `async def` event loop.

```python
# FastAPI serving a PyTorch model (pip install fastapi httpx torch)
from typing import List  # type hints
import torch  # tensors
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # test client
from pydantic import BaseModel, Field  # validation
from torch import nn  # layers

torch.manual_seed(0)  # same weights each run
model: nn.Module = nn.Linear(2, 1)  # in production: load_state_dict from a file
model.eval()  # inference mode

app: FastAPI = FastAPI()  # app


class Features(BaseModel):  # request body
    values: List[float] = Field(min_length=2, max_length=2)  # exactly two numbers


@app.post("/predict")  # endpoint
def predict(f: Features) -> dict[str, float]:  # sync def: runs in a thread pool
    with torch.no_grad():  # no gradient tracking
        out: float = model(torch.tensor([f.values])).item()  # batch of one row
    return {"prediction": round(out, 4)}  # JSON-safe float


c: TestClient = TestClient(app)  # client
r = c.post("/predict", json={"values": [1.0, 2.0]})  # call
print(r.status_code, list(r.json()))  # prediction value depends on the random init, so show keys
# Output: 200 ['prediction']
print(c.post("/predict", json={"values": [1.0]}).status_code)  # wrong length
# Output: 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `optimizer.zero_grad()`
✅ Correct: clear gradients every step (PyTorch accumulates them)

```python
# Wrong: loss.backward(); opt.step()   # gradients keep adding up across batches
# Right: opt.zero_grad(); loss.backward(); opt.step()
```

❌ Mistake 2: Predicting without `model.eval()` and `torch.no_grad()`
✅ Correct: use both in inference

```python
# Wrong: model(x) in the API -> dropout still active, memory grows from the graph
# Right:
# model.eval()
# with torch.no_grad(): out = model(x)
```

❌ Mistake 3: Model and data on different devices
✅ Correct: `.to(device)` for both

```python
# Wrong: model on cuda, x on cpu -> RuntimeError: Expected all tensors on the same device
# Right: model.to(device); x = x.to(device)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import torch
a = torch.ones(3)
b = a.numpy()
b[0] = 5
c = a.clone()
c[1] = 9
x = torch.tensor(2.0, requires_grad=True)
y = x * x
y.backward()
y2 = x * x
y2.backward()
print(a, c, x.grad)
```

**Answer**:
```
tensor([5., 1., 1.]) tensor([5., 9., 1.]) tensor(8.)
```
`a.numpy()` shares memory, so changing `b` changed `a`. `clone()` copies, so changing `c[1]` does not touch `a` (but `c` was cloned after `b[0] = 5`, so it has 5 too). Gradients accumulate: the first backward adds 4, the second adds 4 more, so `x.grad` is 8, not 4. This is exactly why `zero_grad()` exists.

---

## ⚫ Interview Questions + Answers

Q1: What is autograd?
A1: PyTorch records each tensor operation in a graph. `backward()` walks the graph in reverse applying the chain rule to fill `.grad` for every tensor with `requires_grad=True`.

Q2: `view` vs `reshape`?
A2: `view` needs contiguous memory and never copies. `reshape` returns a view when possible and copies otherwise.

Q3: `model.train()` vs `model.eval()`?
A3: They switch layers like Dropout and BatchNorm between training and inference behaviour. `eval()` does not turn off gradients; `torch.no_grad()` does.

Q4: Why save `state_dict` instead of the whole model?
A4: A state_dict holds only weights, so loading does not depend on pickled class paths. Use `weights_only=True` when loading to avoid executing untrusted pickles.

Q5: PyTorch vs TensorFlow?
A5: PyTorch is dynamic and Pythonic, dominant in research and LLM work. TensorFlow/Keras has strong deployment tooling (TF Serving, TFLite). Both are widely used.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Training or fine-tuning neural networks, working with Hugging Face models
- You need GPU acceleration and custom architectures

❌ Avoid when:
- Tabular data with small size (scikit-learn or XGBoost is faster to ship)
- You only call a hosted LLM API (no local model needed)

---

## 📊 Visual Diagram

```
 batch x ──► model(x) ──► predictions ──► loss(pred, y)
                ▲                              │
                │ optimizer.step()             │ loss.backward()
                └────── gradients (.grad) ◄────┘
 (zero_grad() clears gradients before every backward)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tensor | N-dimensional array | N-आयामी array |
| Autograd | Automatic gradient computation | अपने-आप gradient निकालना |
| nn.Module | Base class of every model | हर model की base class |
| Optimizer | Updates weights (SGD, Adam) | Weights अपडेट करने वाला |
| Epoch | One full pass over the data | पूरे data का एक चक्कर |
| state_dict | Dictionary of model weights | Model के weights का dictionary |

---

## ⚡ 3-Line Summary
English: PyTorch gives tensors, autograd and nn.Module. A training loop is: zero_grad, forward, loss, backward, step. For inference use eval() and no_grad() and load the model once at startup.
Hindi: PyTorch tensors, autograd और nn.Module देता है। Training loop है: zero_grad, forward, loss, backward, step। Inference में eval() और no_grad() इस्तेमाल करें और model startup पर एक बार load करें।

---

## ➡️ Next Topic
**398. TensorFlow Basics** — Keras models and tf.function.
