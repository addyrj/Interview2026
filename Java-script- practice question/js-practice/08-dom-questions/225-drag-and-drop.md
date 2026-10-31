---

# Q225. Drag and Drop
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Make `.item` elements draggable and allow dropping them into `#dropzone` using the HTML5 Drag and Drop API.

---

## 💡 Quick Concept (2 lines only)
Set `draggable="true"`, store the id in `dragstart`, and in the drop zone call `preventDefault()` on `dragover` so `drop` fires.
हिंदी: `dragover` पर `preventDefault()` ज़रूरी है, वरना `drop` event कभी fire नहीं होगा।

---

## ✅ Answer / Solution

```html
<div class="item" id="a" draggable="true">Item A</div>
<div class="item" id="b" draggable="true">Item B</div>
<div id="dropzone" style="min-height:80px;border:2px dashed gray">Drop here</div>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: On dragstart save dragged element id in dataTransfer
// Step 2: On dragover of zone call preventDefault (allow drop)
// Step 3: On drop read id and append the element

const zone = document.getElementById('dropzone');        // drop target

document.querySelectorAll('.item').forEach((item) => {   // each draggable
  item.addEventListener('dragstart', (e) => {            // drag begins
    e.dataTransfer.setData('text/plain', item.id);       // save which element
    e.dataTransfer.effectAllowed = 'move';               // we will move it
  });
});

zone.addEventListener('dragover', (e) => {               // while hovering the zone
  e.preventDefault();                                    // REQUIRED to allow dropping
  zone.classList.add('hover');                           // visual feedback
});

zone.addEventListener('dragleave', () => {              // pointer left the zone
  zone.classList.remove('hover');                        // remove feedback
});

zone.addEventListener('drop', (e) => {                   // item dropped
  e.preventDefault();                                    // stop browser opening/navigating
  const id = e.dataTransfer.getData('text/plain');       // read saved id
  const el = document.getElementById(id);                // find element
  if (el) zone.appendChild(el);                          // move into zone
  zone.classList.remove('hover');                        // clear feedback
  console.log('Dropped:', id);                           // log result
});

// ============================================
// TEST CASES
// ============================================

// Test 1: drag Item A into zone -> Expected: Dropped: a ; zone.children.length === 1
// Test 2: drag Item B into zone -> Expected: Dropped: b ; zone.children.length === 2
// Test 3: remove e.preventDefault() in dragover -> Expected: drop never fires
```

---

## 🔍 Why This Works (3 lines max)
`dataTransfer` carries data between `dragstart` and `drop`. Elements are not drop targets by default; cancelling `dragover` marks the zone as valid. Appending the same node moves it.
हिंदी: `dataTransfer` data ले जाता है, और `dragover` cancel करने से zone valid drop target बनता है।

---

## ⚡ Alternative Solution
```javascript
// Pointer events approach (works on touch too, full control)
let dragged = null;                                      // currently dragged node
document.addEventListener('pointerdown', (e) => {        // start
  dragged = e.target.closest('.item');                   // pick item
});
document.addEventListener('pointerup', (e) => {          // end
  const under = document.elementFromPoint(e.clientX, e.clientY); // what is below pointer
  if (dragged && under === zone) zone.appendChild(dragged);       // drop if over zone
  dragged = null;                                        // reset
});
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no preventDefault in dragover -> drop never fires
zone.addEventListener('dragover', () => {});

// ✅ Correct
zone.addEventListener('dragover', (e) => e.preventDefault());
```

---

## 🎯 Interview Tip (1 line)
Say: "HTML5 DnD doesn't work on touch; for production use pointer events or a library like dnd-kit, and always preventDefault on dragover and drop."

---

## 🔗 Related Questions
→ Q235 (file drag + drop upload) | Q221 (event delegation) | Q200 (undo/redo)
