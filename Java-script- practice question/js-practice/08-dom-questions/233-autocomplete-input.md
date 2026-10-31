---

# Q233. Autocomplete Input
# Category: DOM Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build an autocomplete: show matching suggestions below an input, support Arrow Up/Down + Enter keyboard selection, click selection, and Escape to close.

---

## 💡 Quick Concept (2 lines only)
Filter a list on input, render suggestions, track an `activeIndex` for keyboard navigation, and use delegation for clicks.
हिंदी: Input पर list filter करो, `activeIndex` से keyboard चलाओ, और click के लिए delegation use करो।

---

## ✅ Answer / Solution

```html
<div style="position:relative;width:240px">
  <input id="ac" autocomplete="off" placeholder="Fruit...">
  <ul id="sug" style="position:absolute;margin:0;padding:0;list-style:none"></ul>
</div>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Data + state
// Step 2: render() builds the list and marks active item
// Step 3: Handle input, keydown, click

const DATA = ['Apple', 'Apricot', 'Banana', 'Blueberry', 'Cherry', 'Grape']; // sample data
const input = document.getElementById('ac');             // text input
const list = document.getElementById('sug');             // suggestion list
let matches = [];                                        // current matches
let active = -1;                                         // highlighted index

function render() {
  list.replaceChildren();                                // clear list
  matches.forEach((text, i) => {                         // build each suggestion
    const li = document.createElement('li');             // item
    li.textContent = text;                               // safe text
    li.dataset.index = i;                                // store index
    li.style.background = i === active ? '#cde' : '';    // highlight active
    list.appendChild(li);                                // add
  });
}

function choose(i) {
  if (i < 0 || i >= matches.length) return;              // invalid index
  input.value = matches[i];                              // fill input
  matches = []; active = -1; render();                   // close list
  console.log('chosen:', input.value);                   // log
}

input.addEventListener('input', () => {                  // typing
  const q = input.value.trim().toLowerCase();            // normalized query
  matches = q ? DATA.filter((d) => d.toLowerCase().startsWith(q)) : []; // filter
  active = -1;                                           // reset highlight
  render();                                              // update UI
});

input.addEventListener('keydown', (e) => {               // keyboard control
  if (e.key === 'ArrowDown') { active = (active + 1) % matches.length; e.preventDefault(); } // next
  else if (e.key === 'ArrowUp') { active = (active - 1 + matches.length) % matches.length; e.preventDefault(); } // prev
  else if (e.key === 'Enter') { choose(active); }        // select
  else if (e.key === 'Escape') { matches = []; active = -1; } // close
  render();                                              // redraw
});

list.addEventListener('click', (e) => {                  // delegated click
  const li = e.target.closest('li');                     // clicked item
  if (li) choose(Number(li.dataset.index));              // select it
});

// ============================================
// TEST CASES
// ============================================

// Test 1: type "ap"          -> Expected: list shows Apple, Apricot
// Test 2: ArrowDown, Enter   -> Expected: input.value === "Apple"; log "chosen: Apple"
// Test 3: type "zzz"         -> Expected: empty list
// Test 4: type "b", Escape   -> Expected: list closes
```

---

## 🔍 Why This Works (3 lines max)
A single `matches` array and `active` index are the state; `render()` always redraws from state. Modulo math wraps navigation. Delegated click handles dynamic items.
हिंदी: State (`matches`, `active`) से UI बनता है, और modulo से up/down wrap हो जाता है।

---

## ⚡ Alternative Solution
```html
<!-- Native, zero JS: datalist -->
<input list="fruits"><datalist id="fruits"><option value="Apple"><option value="Banana"></datalist>
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: innerHTML with user data -> XSS
list.innerHTML = matches.map((m) => `<li>${m}</li>`).join('');

// ✅ Correct: textContent / createElement (see above). Also debounce server calls.
```

---

## 🎯 Interview Tip (1 line)
Say: "State-driven render, keyboard accessibility (aria-activedescendant/role=listbox), debounce + abort stale requests, and escape user text."

---

## 🔗 Related Questions
→ Q232 (debounce search) | Q221 (event delegation) | Q181 (search with debounce)
