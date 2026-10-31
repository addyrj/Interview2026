---

# Q010. setTimeout + let Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), (3 - i) * 10);
}
```

---

## 💡 Quick Concept (2 lines only)
`let` gives each iteration its own `i`, and timers fire by delay, not by creation order.
हिंदी: let हर iteration को अपना i देता है, और timers delay के हिसाब से चलते हैं, बनने के order से नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: i=0 -> delay 30ms, i=1 -> delay 20ms, i=2 -> delay 10ms
// Step 2: each callback keeps its own i
// Step 3: shortest delay fires first -> 2, 1, 0

for (let i = 0; i < 3; i++) {                     // new i per iteration
  setTimeout(() => console.log(i), (3 - i) * 10); // delay shrinks as i grows
}

// ============================================
// TEST CASES
// ============================================

for (let j = 0; j < 3; j++) {                     // same delay for all
  setTimeout(() => console.log('same', j), 100);  // same delay -> creation order
}

// Overall output:
// 2
// 1
// 0
// same 0
// same 1
// same 2
```

---

## 🔍 Why This Works (3 lines max)
Each closure holds its own `i`, so values are correct (0, 1, 2). Order depends only on delay; equal delays run in the order they were scheduled.
हिंदी: Values सही रहती हैं, order सिर्फ delay से तय होता है; same delay हो तो scheduling order चलता है।

---

## ⚡ Alternative Solution
```javascript
// Using forEach gives the same per-item scope
[0, 1, 2].forEach((n) => setTimeout(() => console.log('fe', n), 200 + n)); // fe 0, fe 1, fe 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Assuming timers always print in creation order
// ✅ Shorter delay fires first, regardless of when it was created
```

---

## 🎯 Interview Tip (1 line)
Say: "let fixes the capture problem; timer order is decided by delay, then insertion order."

---

## 🔗 Related Questions
→ Q007 (closure loop let) | Q009 (setTimeout + var) | Q013 (Promise + setTimeout) | Q017 (event loop mixed)
