---

# Q221. Event Delegation Example
# Category: DOM Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
You have a `<ul>` with many `<li>` items (some added later dynamically).
Attach ONE click listener so that clicking any `<li>` logs its text, without adding a listener on every item.

---

## 💡 Quick Concept (2 lines only)
Events bubble up, so one listener on the parent can handle clicks of all children using `event.target`.
हिंदी: Event ऊपर bubble होता है, इसलिए parent पर एक ही listener सारे children के click संभाल लेता है।

---

## ✅ Answer / Solution

```html
<ul id="list">
  <li data-id="1">Apple</li>
  <li data-id="2">Banana</li>
</ul>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Get the parent element once
// Step 2: Attach a single click listener on the parent
// Step 3: Use event.target.closest() to find the clicked <li>

const list = document.getElementById('list'); // parent container

list.addEventListener('click', (event) => {   // one listener for all children
  const li = event.target.closest('li');      // find nearest li (handles nested tags)
  if (!li || !list.contains(li)) return;      // ignore clicks outside any li
  console.log('Clicked:', li.textContent, 'id =', li.dataset.id); // use the item
});

// Dynamically added items work automatically
const newLi = document.createElement('li');   // create new item
newLi.textContent = 'Cherry';                 // set its text
newLi.dataset.id = '3';                       // set data-id
list.appendChild(newLi);                      // add to DOM (no new listener needed)

// ============================================
// TEST CASES
// ============================================

// Test 1: click "Apple"   -> Expected: Clicked: Apple id = 1
// Test 2: click "Cherry"  -> Expected: Clicked: Cherry id = 3 (works for dynamic item)
// Test 3: click the gap in <ul> outside li -> Expected: nothing logged
// Console check: list.querySelectorAll('li').length // Expected: 3
```

---

## 🔍 Why This Works (3 lines max)
Click on `<li>` bubbles to `<ul>`, where our handler runs. `event.target` tells which child was clicked, and `closest()` handles clicks on inner tags like `<span>`. One listener means less memory and dynamic items work for free.
हिंदी: Bubbling की वजह से parent को child का click मिलता है, और `target` से पता चलता है कि कौन सा child था।

---

## ⚡ Alternative Solution
```javascript
// Using matches() — works only if the li has no nested children
list.addEventListener('click', (e) => {       // listener on parent
  if (e.target.matches('li')) {               // check selector match
    console.log(e.target.textContent);        // log text
  }
});
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: listener on every li — new items get nothing, memory heavy
document.querySelectorAll('li').forEach((li) => {
  li.addEventListener('click', () => console.log(li.textContent));
});

// ✅ Correct: single delegated listener on the parent (see above)
```

---

## 🎯 Interview Tip (1 line)
Say: "Delegation uses bubbling + event.target; it saves memory and handles dynamic elements — but events like focus/blur don't bubble (use focusin/focusout)."

---

## 🔗 Related Questions
→ Q222 (custom event) | Q310 (bubbling vs capturing) | Q286 (efficient event listeners)
