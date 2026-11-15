---

# 398. TensorFlow Basics
# हिंदी में: TensorFlow Basics (Google की deep learning library)

---

## 🔵 Simple Definition (English)
TensorFlow is Google's library for numerical computing and deep learning. It works with tensors (n-dimensional arrays), computes gradients automatically (`tf.GradientTape`), and ships with Keras (`tf.keras`), a high-level API to build, train and save neural networks. Install: `pip install tensorflow`.

## 🔵 सरल परिभाषा (Hindi)
TensorFlow Google की numerical computing और deep learning library है। यह tensors (n-dimensional arrays) पर काम करती है, gradients अपने आप निकालती है (`tf.GradientTape`) और Keras (`tf.keras`) देती है, जिससे neural networks बनाना, train करना और save करना आसान है।

---

## 🔴 Problem it Solves
Training a neural network by hand means writing matrix math, derivatives (backpropagation) and GPU code. TensorFlow does automatic differentiation, runs on CPU/GPU/TPU, compiles Python functions into fast graphs (`tf.function`), builds efficient input pipelines (`tf.data`) and exports models for servers, mobile and browsers.

## 🔴 यह क्यों बना? (Hindi)
Neural network हाथ से train करने के लिए matrix math, derivatives (backpropagation) और GPU code लिखना पड़ता है। TensorFlow automatic differentiation करता है, CPU/GPU/TPU पर चलता है, Python functions को तेज़ graphs में compile करता है (`tf.function`), `tf.data` से input pipeline बनाता है और models को server, mobile, browser के लिए export करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Data -> tensors (tf.constant / numpy arrays / tf.data.Dataset)
Step 2 → Define model: Sequential([Input, Dense, Dense...])
Step 3 → model.compile(optimizer, loss)
Step 4 → model.fit(X, y, epochs, batch_size): forward pass -> loss -> gradients -> update weights
Step 5 → model.predict(X) for inference, model.evaluate for metrics
Step 6 → model.save("m.keras") / tf.keras.models.load_model("m.keras")
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data को tensors में बदलना (tf.constant / numpy / tf.data.Dataset)
Step 2 → Model बनाना: Sequential([Input, Dense, Dense...])
Step 3 → model.compile(optimizer, loss)
Step 4 → model.fit(...): forward pass -> loss -> gradients -> weights update
Step 5 → model.predict(X) से predictions
Step 6 → model.save("m.keras") और load_model("m.keras") से सेव/लोड
```

---

## 🟡 Real World Example
A Dream11-style app predicts a player's fantasy points from recent form numbers using a small Keras regression model. An e-commerce site trains an image classifier on product photos. The model is saved as `.keras` and served behind FastAPI or exported to TF Lite for the mobile app.

## 🟡 Real Example Hindi mein
Dream11 जैसा app खिलाड़ी के हाल के प्रदर्शन के numbers से fantasy points predict करने के लिए छोटा Keras regression model इस्तेमाल करता है। E-commerce साइट product photos पर image classifier train करती है। Model `.keras` में सेव होकर FastAPI के पीछे चलता है या मोबाइल app के लिए TF Lite में export होता है।

---

## 💻 Code Example — Basic
```python
# VERIFIED: ran with tensorflow 2.21.0 (Keras 3.15), numpy 2.5.4, Python 3.13, CPU.
# Install: pip install tensorflow numpy
import os  # to quiet TensorFlow logs

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # hide info/warning logs (set BEFORE importing tensorflow)

import tensorflow as tf  # the library

print(tf.__version__)  # Output: 2.21.0 (your version may differ)

a = tf.constant([[1.0, 2.0], [3.0, 4.0]])  # immutable 2x2 tensor
print(a.shape, a.dtype)  # Output: (2, 2) <dtype: 'float32'>
print((a @ a).numpy().tolist())  # matrix multiply, then to python lists
# Output: [[7.0, 10.0], [15.0, 22.0]]

x = tf.Variable(3.0)  # a Variable is a trainable/mutable value
with tf.GradientTape() as tape:  # record operations for differentiation
    y = x ** 2 + 2 * x  # y = x^2 + 2x
grad = tape.gradient(y, x)  # dy/dx = 2x + 2 = 8 at x = 3
print(grad.numpy())  # Output: 8.0

@tf.function  # compile this Python function into a TF graph
def double(v: tf.Tensor) -> tf.Tensor:  # type hints for clarity
    return v * 2  # runs as a graph after the first call

print(double(tf.constant(3)).numpy())  # Output: 6
```

## 💻 Code Example — Advanced
```python
# VERIFIED: trained and saved/loaded on CPU with tensorflow 2.21.0 / Keras 3.
# Production style: seeds, tf.data pipeline, Keras model, early stopping, save/load, shape checks.
import os  # env var for logs

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # quiet logs
from typing import Tuple  # type hints

import numpy as np  # data
import tensorflow as tf  # framework

tf.random.set_seed(0)  # reproducible weights init / shuffling
np.random.seed(0)  # reproducible data


def make_data(n: int = 256) -> Tuple[np.ndarray, np.ndarray]:
    """Fake regression data: y = 2*x0 - x1 + 0.5*x2 + 1."""
    X: np.ndarray = np.random.rand(n, 3).astype("float32")  # features in [0, 1)
    w: np.ndarray = np.array([2.0, -1.0, 0.5], dtype="float32")  # true weights
    y: np.ndarray = X @ w + 1.0  # targets (no noise)
    return X, y


def build_model() -> tf.keras.Model:
    """Small MLP with an explicit Input layer (Keras 3 style)."""
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(3,)),  # 3 input features
        tf.keras.layers.Dense(8, activation="relu"),  # hidden layer
        tf.keras.layers.Dense(1),  # one output (regression)
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(0.05), loss="mse")  # how to learn
    return model


X, y = make_data()  # create data
model = build_model()  # create model
stop = tf.keras.callbacks.EarlyStopping(monitor="loss", patience=5, restore_best_weights=True)  # avoid waste
history = model.fit(X, y, epochs=30, batch_size=32, verbose=0, callbacks=[stop])  # train silently

first, last = history.history["loss"][0], history.history["loss"][-1]  # first vs final loss
print(first > last, last < 0.05)  # Output: True True   (loss decreased and is small)
print(model.predict(X[:2], verbose=0).shape)  # Output: (2, 1)

model.save("m.keras")  # native Keras format (architecture + weights + optimizer)
loaded = tf.keras.models.load_model("m.keras")  # restore
same: bool = np.allclose(loaded.predict(X[:2], verbose=0), model.predict(X[:2], verbose=0))
print(same)  # Output: True

ds = tf.data.Dataset.from_tensor_slices((X, y)).shuffle(256).batch(64).prefetch(1)  # input pipeline
xb, yb = next(iter(ds))  # first batch
print(xb.shape)  # Output: (64, 3)

try:  # wrong input shape raises a clear error
    model.predict(np.zeros((2, 5), dtype="float32"), verbose=0)
except ValueError as exc:
    print("ValueError:", str(exc)[:40])  # message text depends on the Keras version
```

---

## 🟠 JavaScript vs Python Comparison
TensorFlow.js (`@tensorflow/tfjs`) mirrors the API in JavaScript, and you can convert Keras models to run in the browser.

```python
# Python: Keras
import tensorflow as tf
model = tf.keras.Sequential([tf.keras.Input(shape=(3,)), tf.keras.layers.Dense(1)])
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=5)
```
```javascript
// JavaScript: TensorFlow.js
import * as tf from "@tensorflow/tfjs";
const model = tf.sequential();
model.add(tf.layers.dense({ units: 1, inputShape: [3] }));
model.compile({ optimizer: "adam", loss: "meanSquaredError" });
await model.fit(xs, ys, { epochs: 5 });
```

Key differences: JS code is async (`await model.fit`) and uses camelCase options and `inputShape`. Python training is much faster and has the full tooling (`tf.data`, TPU, TF Serving). Typical flow: train in Python, convert, run inference in the browser with tfjs.

---

## 🟠 FastAPI Connection
Load the saved model once at startup and call `predict` in a `def` endpoint (inference is CPU/GPU-bound and blocking).

```python
# FastAPI + Keras model (structure shown; loads m.keras produced above)
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # quiet logs before importing tensorflow
from contextlib import asynccontextmanager  # lifespan
from typing import Any, AsyncIterator, Dict, List
import numpy as np  # arrays
import tensorflow as tf  # model
from fastapi import FastAPI  # web
from pydantic import BaseModel, Field  # validation

store: Dict[str, Any] = {}  # loaded model lives here


class Features(BaseModel):  # request body
    values: List[float] = Field(min_length=3, max_length=3)  # exactly 3 features


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    store["model"] = tf.keras.models.load_model("m.keras")  # load once
    yield
    store.clear()


app = FastAPI(lifespan=lifespan)


@app.post("/predict")
def predict(body: Features) -> Dict[str, float]:  # def -> thread pool
    x = np.array([body.values], dtype="float32")  # shape (1, 3)
    pred = store["model"].predict(x, verbose=0)  # shape (1, 1)
    return {"prediction": float(pred[0][0])}  # JSON number
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the wrong Keras import / old APIs
```python
# Wrong (TF 1.x style, removed): tf.Session(), tf.placeholder(), model.save("m.h5") as the default
# Right (TF 2.x / Keras 3): eager execution by default, model.save("m.keras")
```

❌ Mistake 2: Mismatched dtype (float64 numpy into a float32 model)
```python
# Wrong: np.random.rand gives float64 -> slower / dtype warnings / errors in some ops
X = np.random.rand(100, 3)

# Right
X = np.random.rand(100, 3).astype("float32")
```

❌ Mistake 3: Wrong input shape or missing batch dimension
```python
# Wrong: shape (3,) is not a batch
model.predict(np.array([1.0, 2.0, 3.0], dtype="float32"))

# Right: shape (1, 3)
model.predict(np.array([[1.0, 2.0, 3.0]], dtype="float32"))
```

❌ Mistake 4: Loading the model on every request
```python
# Wrong: load_model inside the endpoint (slow, memory spikes)
# Right: load once in lifespan and reuse
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print, and why is `grad` possibly `None` in the second case?

```python
x = tf.Variable(3.0)
with tf.GradientTape() as t:
    y = x ** 2
print(t.gradient(y, x))          # (1)

c = tf.constant(3.0)
with tf.GradientTape() as t:
    y = c ** 2
print(t.gradient(y, c))          # (2)
```

**Answer**: (1) prints `tf.Tensor(6.0, shape=(), dtype=float32)` because `Variable`s are watched automatically. (2) prints `None` because a plain `tf.constant` is not tracked; you must call `t.watch(c)` inside the tape first. Also note that a `GradientTape` is released after one `.gradient()` call unless you create it with `persistent=True`.

---

## ⚫ Interview Questions + Answers

Q1: What is a tensor?
A1: An n-dimensional array with a dtype and shape (scalar, vector, matrix, ...). `tf.constant` is immutable, `tf.Variable` is mutable and trainable.

Q2: Eager execution vs `tf.function`?
A2: TF 2.x runs eagerly (line by line, easy to debug). `@tf.function` traces the function into a graph for speed and deployment. Python side effects like `print` run only during tracing; use `tf.print` for runtime logging.

Q3: TensorFlow vs PyTorch?
A3: PyTorch is more popular for research and has a Pythonic feel; TensorFlow has stronger deployment tooling (TF Serving, TF Lite, TF.js). Keras 3 can now run on multiple backends (TensorFlow, JAX, PyTorch).

Q4: What do `compile` and `fit` do?
A4: `compile` sets optimizer, loss and metrics. `fit` runs the training loop: batches, forward pass, loss, gradients and weight updates for each epoch.

Q5: How to prevent overfitting?
A5: More data, regularization/dropout, early stopping (`EarlyStopping` callback), validation split, simpler model, data augmentation.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need to train and deploy neural networks, especially to mobile/browser (TF Lite, TF.js)
- Your team already has TF/TFX pipelines or uses TPUs
- You want Keras's simple high-level API

❌ Avoid when:
- Classical ML on tabular data is enough (use scikit-learn / XGBoost)
- You only call hosted LLM APIs (no local training needed)
- You are doing cutting-edge research where the PyTorch ecosystem dominates

---

## 📊 Visual Diagram

```
 X (batch, 3) ──► Dense(8, relu) ──► Dense(1) ──► y_pred
                                                   │
 y_true ───────────────────────────────────────────┤ loss = mse(y_true, y_pred)
                                                   ▼
                        GradientTape -> gradients -> Adam updates weights
                        (repeat for every batch, every epoch)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tensor | n-dimensional array | n-आयामी array |
| Gradient | Direction to reduce loss | loss घटाने की दिशा |
| Epoch | One pass over all data | पूरे data पर एक चक्कर |
| Batch | Small group of samples | samples का छोटा समूह |
| Optimizer | Updates weights (Adam) | weights बदलने वाला |
| Loss | Error to minimise | कम करने वाली गलती |

---

## ⚡ 3-Line Summary
English: TensorFlow computes on tensors, differentiates automatically with `GradientTape`, and Keras gives `Sequential`, `compile`, `fit`, `predict`, and `.keras` save/load. Use float32, batch dimensions, `tf.data`, and load models once in FastAPI.
Hindi: TensorFlow tensors पर काम करता है, `GradientTape` से gradients निकालता है और Keras में `Sequential`, `compile`, `fit`, `predict` और `.keras` save/load मिलता है। float32, batch dimension, `tf.data` इस्तेमाल करें और FastAPI में model एक बार load करें।

---

## ➡️ Next Topic
**399. Pydantic for AI Apps** (already written), then **401. Python Performance Issues**.
