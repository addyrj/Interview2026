---

# D153. Online Stock Span
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #901 | Asked: Amazon, Google, Microsoft, Goldman Sachs

---

## ❓ Problem
Design `StockSpanner` with `next(price)` that returns the span: the number of consecutive days (including today, going backwards) with price <= today's price.

```
next(100) → 1
next(80)  → 1
next(60)  → 1
next(70)  → 2
next(60)  → 1
next(75)  → 4
next(85)  → 6
```

---

## 💡 Quick Concept (2 lines only)
Stack of `[price, span]` with strictly decreasing prices. For a new price, pop all entries with price <= it and add their spans to today's span, then push.
हिंदी: छोटे या बराबर prices pop करो और उनके span जोड़ते जाओ, फिर आज का [price, span] push करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — store all prices, scan back. O(n) per call
// ============================================

class StockSpannerBrute {
  constructor() { this.prices = []; }                // all prices so far
  next(price) {
    this.prices.push(price);                         // add today
    let span = 0;
    for (let i = this.prices.length - 1; i >= 0; i--) {
      if (this.prices[i] <= price) span++;           // count backwards
      else break;                                    // stop at first greater
    }
    return span;
  }
}

// ============================================
// APPROACH 2: Monotonic stack — amortized O(1) per call ✅ PREFERRED
// ============================================

class StockSpanner {
  constructor() {
    this.stack = [];                                 // [price, span], prices decreasing
  }

  next(price) {
    let span = 1;                                    // today counts as 1
    // absorb all previous days that were <= today
    while (this.stack.length && this.stack[this.stack.length - 1][0] <= price) {
      span += this.stack.pop()[1];                   // add their whole span
    }
    this.stack.push([price, span]);                  // remember today
    return span;
  }
}

// ============================================
// TEST CASES
// ============================================

const s = new StockSpanner();
const prices = [100, 80, 60, 70, 60, 75, 85];
console.log(prices.map(p => s.next(p)));             // [1,1,1,2,1,4,6]

const s2 = new StockSpanner();
console.log([10, 10, 10].map(p => s2.next(p)));      // [1,2,3]

const s3 = new StockSpanner();
console.log([5, 4, 3, 2].map(p => s3.next(p)));      // [1,1,1,1]

const b = new StockSpannerBrute();
console.log(prices.map(p => b.next(p)));             // [1,1,1,2,1,4,6]
```

---

## 🔍 Why It Works
```
100 -> stack [[100,1]]                 span 1
80  -> [[100,1],[80,1]]                span 1
60  -> [[100,1],[80,1],[60,1]]         span 1
70  -> pop 60 -> span 2 -> [[100,1],[80,1],[70,2]]
60  -> [..,[70,2],[60,1]]              span 1
75  -> pop 60,70 -> 1+1+2=4 -> [[100,1],[80,1],[75,4]]
85  -> pop 75,80 -> 1+4+1=6 -> [[100,1],[85,6]]
```
हिंदी: पुराने छोटे prices का span पहले से जमा है, इसलिए उन्हें दोबारा गिनना नहीं पड़ता।

---

## 📊 Complexity
```
Brute force: next() O(n) | Space O(n)
Stack:       next() amortized O(1) | Space O(n)
```

---

## ⚡ Variations
```
- Previous Smaller/Greater Element via the same stack
- Span with "<" instead of "<="
- Daily Temperatures (D143) — forward-looking version
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: storing only prices -> must also store spans, else you recount
// ❌ Wrong: popping with < instead of <=  -> equal prices would not merge
```

---

## 🎯 Interview Tip
Say: "Each price is pushed and popped once so it is amortized O(1). Storing the span lets me skip over whole groups." Link it to Daily Temperatures.

---

## 🔗 Related Problems
→ D143 (Daily Temperatures) | D144 (Next Greater Element) | D146 (Largest Rectangle in Histogram)
