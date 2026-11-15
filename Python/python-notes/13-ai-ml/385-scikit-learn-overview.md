---

# 385. Scikit-learn Overview
# हिंदी में: Scikit-learn का परिचय (classical Machine Learning toolkit)

---

## 🔵 Simple Definition (English)
Scikit-learn (`sklearn`) is the standard Python library for classical machine learning: classification, regression, clustering, preprocessing, and evaluation. Every model follows the same simple API: `fit(X, y)` to learn, `predict(X)` to use.

## 🔵 सरल परिभाषा (Hindi)
Scikit-learn (`sklearn`) classical machine learning की standard Python library है: classification, regression, clustering, preprocessing और evaluation। हर model एक ही सरल API follow करता है: सीखने के लिए `fit(X, y)`, इस्तेमाल के लिए `predict(X)`।

---

## 🔴 Problem it Solves
Before scikit-learn, every algorithm had its own interface, so swapping a model meant rewriting code. Data preparation (scaling, encoding, missing values) was done by hand and often leaked test data into training. Scikit-learn gives one uniform API, ready-made preprocessing, `Pipeline` to chain steps safely, and tools for splitting and scoring.

## 🔴 यह क्यों बना? (Hindi)
Scikit-learn से पहले हर algorithm का अपना interface था, इसलिए model बदलने का मतलब code दोबारा लिखना था। Data preparation (scaling, encoding, missing values) हाथ से होता था और अक्सर test data की जानकारी training में leak हो जाती थी। Scikit-learn एक जैसा API, तैयार preprocessing, steps को सुरक्षित जोड़ने के लिए `Pipeline`, और split व scoring के tools देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Prepare X (features, 2D: rows x columns) and y (target, 1D)
Step 2 → train_test_split: hold back a test set the model never sees while training
Step 3 → Estimator = model object: model = LogisticRegression()
Step 4 → model.fit(X_train, y_train)   -> learns parameters (ending with _, e.g. coef_)
Step 5 → model.predict(X_test)         -> predictions; predict_proba gives probabilities
Step 6 → Score with metrics (accuracy, F1, ...) or cross_val_score
Step 7 → Pipeline chains preprocessing + model so fit/predict apply everything in order

Transformers: fit() + transform()      Estimators/Predictors: fit() + predict()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → X (features, 2D: rows x columns) और y (target, 1D) तैयार करें
Step 2 → train_test_split: एक test set अलग रखें जिसे model training में नहीं देखता
Step 3 → Estimator = model object: model = LogisticRegression()
Step 4 → model.fit(X_train, y_train)   -> parameters सीखता है (नाम के अंत में _, जैसे coef_)
Step 5 → model.predict(X_test)         -> predictions; predict_proba probabilities देता है
Step 6 → Metrics (accuracy, F1, ...) या cross_val_score से score करें
Step 7 → Pipeline preprocessing + model को जोड़ता है ताकि fit/predict सब क्रम में चलें

Transformers: fit() + transform()      Estimators/Predictors: fit() + predict()
```

---

## 🟡 Real World Example
Razorpay-style fraud scoring: features are amount, hour, payment method, user age; target is fraud yes/no. A Pipeline imputes missing ages, scales numbers, one-hot encodes the method, and feeds a RandomForest. The model is saved with `joblib` and a FastAPI endpoint loads it at startup to score each payment in milliseconds. Other uses: house price regression, customer churn, product recommendation clustering.

## 🟡 Real Example Hindi mein
Razorpay जैसा fraud scoring: features हैं amount, घंटा, payment method, user की उम्र; target है fraud हां/नहीं। Pipeline गायब उम्र भरता है, numbers scale करता है, method को one-hot encode करता है और RandomForest को देता है। Model `joblib` से save होता है और FastAPI endpoint startup पर उसे load करके हर payment को milliseconds में score करता है। अन्य उपयोग: घर की कीमत (regression), customer churn, recommendation के लिए clustering।

---

## 💻 Code Example — Basic
```python
# Basic scikit-learn workflow (version 1.9)
import numpy as np                                    # arrays (sklearn works on numpy)
from sklearn.datasets import load_iris                # tiny built-in dataset (no download)
from sklearn.linear_model import LogisticRegression   # a classifier
from sklearn.model_selection import train_test_split  # split helper
from sklearn.metrics import accuracy_score            # simple metric

X, y = load_iris(return_X_y=True)                     # X: 150x4 features, y: 150 labels
X_train, X_test, y_train, y_test = train_test_split(  # split 80/20
    X, y, test_size=0.2, random_state=42, stratify=y) # fixed seed, keep class balance
print(X_train.shape, X_test.shape)                    # sizes of both parts
model: LogisticRegression = LogisticRegression(max_iter=200)   # create the model
model.fit(X_train, y_train)                           # learn from training data
pred: np.ndarray = model.predict(X_test)              # predict labels for unseen data
print(round(accuracy_score(y_test, pred), 3))         # fraction correct
print(pred[:5].tolist(), model.predict_proba(X_test[:1]).round(3).tolist())   # labels + probabilities
print(model.coef_.shape, hasattr(model, "classes_"))  # learned attributes end with "_"

# Output:
# (120, 4) (30, 4)
# 0.967
# [0, 2, 1, 1, 0] [[0.985, 0.015, 0.0]]
# (3, 4) True
```

## 💻 Code Example — Advanced
```python
# Production style: preprocessing Pipeline + cross-validation + save/load with joblib
from __future__ import annotations                    # modern hints
import random                                         # make synthetic data
import tempfile                                       # temp folder for the model file
from pathlib import Path                              # file paths
import joblib                                         # model persistence
import pandas as pd                                   # tabular data
from sklearn.compose import ColumnTransformer         # different steps per column
from sklearn.ensemble import RandomForestClassifier   # the model
from sklearn.impute import SimpleImputer              # fill missing values
from sklearn.model_selection import cross_val_score, train_test_split   # evaluation
from sklearn.pipeline import Pipeline                 # chain steps
from sklearn.preprocessing import OneHotEncoder, StandardScaler          # encode + scale


def make_data(n: int = 200) -> pd.DataFrame:
    """Synthetic payments: fraud if big night payment or very big COD."""
    random.seed(0)                                    # reproducible
    rows: list[dict[str, object]] = []                # collect rows
    for _ in range(n):                                # build n payments
        amount: float = random.uniform(50, 5000)      # payment value
        hour: int = random.randint(0, 23)             # hour of day
        method: str = random.choice(["upi", "card", "cod"])   # payment type
        age: int | None = random.choice([random.randint(18, 60), None])   # some ages missing
        fraud: int = int(amount > 3000 and hour < 6 or (method == "cod" and amount > 4000))   # label rule
        rows.append({"amount": amount, "hour": hour, "method": method, "age": age, "fraud": fraud})
    return pd.DataFrame(rows)                         # to DataFrame


def build_pipeline() -> Pipeline:
    """Preprocess numbers and categories, then classify."""
    num: Pipeline = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])   # fill, scale
    pre: ColumnTransformer = ColumnTransformer([      # route columns
        ("num", num, ["amount", "hour", "age"]),      # numeric columns
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["method"]),   # category column
    ])
    return Pipeline([("pre", pre), ("clf", RandomForestClassifier(n_estimators=50, random_state=0))])


df: pd.DataFrame = make_data()                        # build data
X: pd.DataFrame = df.drop(columns=["fraud"])          # features
y: pd.Series = df["fraud"]                            # target
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)   # split
pipe: Pipeline = build_pipeline()                     # create pipeline
scores = cross_val_score(pipe, Xtr, ytr, cv=5)        # 5-fold CV, preprocessing refit per fold (no leakage)
print("cv mean:", round(float(scores.mean()), 3))     # average accuracy
pipe.fit(Xtr, ytr)                                    # final fit on all training data
print("test acc:", round(float(pipe.score(Xte, yte)), 3))   # honest score on the test set
with tempfile.TemporaryDirectory() as d:              # temp folder cleaned automatically
    p: Path = Path(d) / "m.joblib"                    # model path
    joblib.dump(pipe, p)                              # save the WHOLE pipeline
    loaded = joblib.load(p)                           # load it back
    print("same preds:", (loaded.predict(Xte) == pipe.predict(Xte)).all())   # identical output
new: pd.DataFrame = pd.DataFrame([{"amount": 4500.0, "hour": 2, "method": "cod", "age": None}])   # missing age is fine
print(pipe.predict(new).tolist())                     # raw data in, prediction out

# Output (numbers come from this synthetic data; yours match because of the fixed seed):
# cv mean: 0.973
# test acc: 1.0
# same preds: True
# [1]
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (scikit-learn) | JavaScript |
|---------|----------------------|-----------|
| Classical ML library | scikit-learn | ml5.js, brain.js, TensorFlow.js (mostly deep learning) |
| Train | `model.fit(X, y)` | library-specific (`await model.fit`) |
| Predict | `model.predict(X)` | `model.predict(tensor)` |
| Pipelines | `Pipeline` built in | write your own |
| Typical role | training + serving in Python | run pre-trained models in browser/Node |

```python
# Python way
from sklearn.linear_model import LinearRegression          # model
m = LinearRegression().fit([[1], [2], [3]], [2, 4, 6])     # learn y = 2x
print(m.predict([[10]]).round(1).tolist())                 # [20.0]
```
```javascript
// JavaScript way (e.g. ml-regression package)
import { SimpleLinearRegression } from "ml-regression";    // third party package
const m = new SimpleLinearRegression([1, 2, 3], [2, 4, 6]);// learn y = 2x
console.log(m.predict(10));                                // 20
```

Key difference: Python is the home of ML training with a unified API; JavaScript usually only runs models trained in Python (via ONNX or TensorFlow.js) and has no equivalent of the full sklearn toolbox.

---

## 🟠 FastAPI Connection
The classic ML deployment: train offline, save with `joblib`, load once at startup (not per request), and expose `/predict`. Use a Pydantic model for input validation. Verified with TestClient below using the Pipeline from the advanced example.

```python
# FastAPI example — fraud prediction endpoint (verified: returned 0.98 and 0.0 for two payments)
import pandas as pd                                        # build the input row
from fastapi import FastAPI                                # FastAPI
from pydantic import BaseModel                             # input validation

app: FastAPI = FastAPI()                                   # create app
MODEL = pipe                                               # in production: joblib.load("model.joblib") once at startup


class Txn(BaseModel):                                      # request body
    amount: float                                          # required
    hour: int                                              # required
    method: str                                            # required
    age: float | None = None                               # optional, imputer handles missing


@app.post("/predict")                                      # POST /predict
def predict(t: Txn) -> dict[str, float]:                   # sync def: CPU-bound
    X: pd.DataFrame = pd.DataFrame([t.model_dump()])       # same column names as training
    p: float = float(MODEL.predict_proba(X)[0][1])         # probability of class 1
    return {"fraud_probability": round(p, 3)}              # JSON result
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Data leakage: fitting the scaler on all data before splitting
✅ Correct: split first, fit on train only (or use a Pipeline)

```python
from sklearn.preprocessing import StandardScaler
# Wrong: StandardScaler().fit(X) then train_test_split   -> test info leaks into training
# Right: fit on X_train only, then transform both. A Pipeline does this for you:
# Pipeline([("sc", StandardScaler()), ("clf", model)])
```

❌ Mistake 2: Trusting accuracy on imbalanced data
✅ Correct: use precision, recall, F1, ROC-AUC

```python
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score
y = np.array([0] * 95 + [1] * 5)                      # only 5% fraud
d = DummyClassifier(strategy="most_frequent").fit(np.zeros((100, 1)), y)
print(accuracy_score(y, d.predict(np.zeros((100, 1)))))   # 0.95 — a model that catches NO fraud
```

❌ Mistake 3: Calling `transform` with a new scaler instead of the fitted one
✅ Correct: reuse the fitted object; refitting on test data changes the scale

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
X = np.array([[1.0], [2.0], [3.0], [100.0]])
sc = StandardScaler().fit(X[:3])                      # fitted on training rows only
print(sc.mean_.tolist(), sc.transform([[100.0]]).round(2).tolist())   # [2.0] [[120.02]]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score
y = np.array([0] * 95 + [1] * 5)
d = DummyClassifier(strategy="most_frequent").fit(np.zeros((100, 1)), y)
print(accuracy_score(y, d.predict(np.zeros((100, 1)))))
from sklearn.preprocessing import StandardScaler
print(hasattr(StandardScaler(), "scale_"))
```
Answer: `0.95`, then `False`. The dummy model always predicts the majority class, so it is right 95% of the time while never finding a single positive: this is why accuracy misleads on imbalanced data. Second line: learned attributes (ending with `_`, like `scale_`, `coef_`) exist only after `fit()`, so an unfitted `StandardScaler` does not have `scale_`.

---

## ⚫ Interview Questions + Answers

Q1: What is the sklearn estimator API?
A1: Estimators have `fit(X, y)`. Predictors add `predict(X)` (and `predict_proba`, `score`). Transformers add `transform(X)` (and `fit_transform`). Hyperparameters go in `__init__`; learned values end with `_`.

Q2: What is data leakage and how does a Pipeline help?
A2: Leakage is when information from the test set influences training (for example scaling with the full-data mean). A Pipeline refits every step only on the training part inside each CV fold.

Q3: Why `random_state` and `stratify`?
A3: `random_state` makes splits reproducible. `stratify=y` keeps the class proportions the same in train and test, important for imbalanced labels.

Q4: Which metric for imbalanced classification?
A4: Precision, recall, F1, PR-AUC or ROC-AUC, chosen by business cost (missed fraud vs false alarms). Not plain accuracy.

Q5: How do you deploy a sklearn model?
A5: `joblib.dump(pipeline, "model.joblib")`, load once at app startup, validate input with Pydantic, and call `predict` in a sync endpoint. Pin the sklearn version: a model pickled with one version may not load in another. Never load pickles from untrusted sources.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tabular data: classification, regression, clustering
- You need quick baselines (logistic regression, random forest)
- You want a clean preprocessing + model pipeline

❌ Avoid when:
- Images, audio, long text: use deep learning (PyTorch, transformers)
- Data is far bigger than memory: use out-of-core tools, XGBoost/LightGBM, Spark
- You need GPU training: sklearn is mostly CPU

---

## 📊 Visual Diagram
```
raw DataFrame
     │
     ▼
┌─────────────────────── Pipeline ───────────────────────┐
│ ColumnTransformer                                       │
│   numeric: impute(median) -> scale                      │
│   category: one-hot                                     │
│ RandomForestClassifier                                  │
└────────────┬────────────────────────────────────────────┘
   fit(X_train, y_train)         predict(X_new) -> labels
             │
        joblib.dump -> model.joblib -> FastAPI /predict
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Estimator | Object with `fit` | `fit` वाला object |
| Transformer | Changes data (`transform`) | Data बदलने वाला |
| Pipeline | Chain of steps | Steps की श्रृंखला |
| Data leakage | Test info leaks into training | Test की जानकारी training में आना |
| Cross-validation | Repeated train/validate splits | बार-बार train/validate split |
| Overfitting | Memorizes training data | Training data रट लेना |

---

## ⚡ 3-Line Summary
English: scikit-learn gives every model the same `fit` / `predict` API plus preprocessing, pipelines, metrics and cross-validation. Always split first, use a Pipeline to avoid leakage, and pick metrics that fit your data. Save with `joblib` and serve from FastAPI.
Hindi: scikit-learn हर model को एक जैसा `fit` / `predict` API, साथ में preprocessing, pipelines, metrics और cross-validation देती है। हमेशा पहले split करें, leakage से बचने के लिए Pipeline लें, और data के हिसाब से metric चुनें। `joblib` से save करें और FastAPI से serve करें।

---

## ➡️ Next Topic
**387. Anthropic Python SDK** — call Claude from Python: messages, streaming, tool use and error handling.
