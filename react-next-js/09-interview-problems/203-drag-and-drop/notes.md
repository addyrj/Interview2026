# 203. Build Drag and Drop
# हिंदी में: Drag and Drop बनाना

> Code: [App.jsx](./App.jsx) (complete Kanban board, tested with jsdom using simulated drag events)

---

## 🔵 Simple Definition (English)
**Drag and drop** lets a user pick up an item and drop it somewhere else, for example moving a task between columns. In React it is built with the browser's native HTML5 drag events (`draggable`, `onDragStart`, `onDragOver`, `onDrop`) and plain state updates.

## 🔵 सरल परिभाषा (Hindi)
**Drag and drop** में user किसी item को उठाकर दूसरी जगह छोड़ता है, जैसे task को एक column से दूसरे में ले जाना। React में इसे browser के native HTML5 drag events (`draggable`, `onDragStart`, `onDragOver`, `onDrop`) और साधारण state update से बनाते हैं।

---

## 🔴 Problem it Solves
Reordering and moving items with only buttons ("Move to Done") is slow and unnatural. Drag and drop is faster, but the native API is confusing: the drop never fires unless you cancel `dragover`, and data travels through a string-only `dataTransfer` object. Interviewers want to see that you understand the event order and keep the real data in React state.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ buttons ("Move to Done") से items हिलाना धीमा और अप्राकृतिक है। Drag and drop तेज़ है, पर native API उलझी है: `dragover` cancel किए बिना drop कभी fire नहीं होता, और data सिर्फ string वाले `dataTransfer` से जाता है। Interviewer देखना चाहते हैं कि आपको events का क्रम समझ आता है और असली data आप React state में रखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add draggable to the card; onDragStart stores the task id in dataTransfer
Step 2 → Columns listen to onDragOver and call e.preventDefault() (this allows dropping)
Step 3 → onDragOver also sets overCol to highlight the column under the pointer
Step 4 → onDrop reads the id from dataTransfer and updates the task's column in state
Step 5 → State update re-renders; the card appears in the new column; clear overCol
Step 6 → onDragLeave clears the highlight when the pointer leaves

Event order: dragstart → (dragenter → dragover repeating) → drop → dragend
Re-render: dragover fires every few hundred ms; set state only when the value really changes
(React skips a re-render when you set the same value, so setOverCol(col) is cheap).
Performance: hundreds of cards are fine; thousands need virtualization.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Card पर draggable लगाओ; onDragStart task id को dataTransfer में रखता है
Step 2 → Columns onDragOver सुनते हैं और e.preventDefault() बुलाते हैं (इसी से drop की अनुमति मिलती है)
Step 3 → onDragOver overCol भी सेट करता है ताकि pointer के नीचे वाला column highlight हो
Step 4 → onDrop dataTransfer से id पढ़ता है और state में task का column बदलता है
Step 5 → State update से re-render होता है; card नए column में दिखता है; overCol साफ़ होता है
Step 6 → Pointer बाहर जाने पर onDragLeave highlight हटाता है

Events का क्रम: dragstart → (dragenter → dragover बार-बार) → drop → dragend
Re-render: dragover बार-बार fire होता है; वही value सेट करने पर React re-render skip कर देता है,
इसलिए setOverCol(col) सस्ता है।
Performance: सैकड़ों cards ठीक हैं; हज़ारों के लिए virtualization चाहिए।
```

---

## 🟡 Real World Example
**Trello / Jira board style, or Swiggy's admin panel:** an operations manager drags an order card from "Preparing" to "Out for delivery". The column glows when the card is over it, and when dropped the order's status changes (and the app calls the API to save it).

## 🟡 Real Example Hindi mein
**Trello / Jira board या Swiggy का admin panel:** operations manager एक order card को "Preparing" से "Out for delivery" में drag करता है। Card ऊपर आते ही column चमकता है, और drop होने पर order का status बदलता है (और app API से उसे save करता है)।

---

## 💻 Code Example — Basic

```jsx
// Basic: drag a box into a drop zone
import { useState } from 'react';                          // state hook
import { createRoot } from 'react-dom/client';             // root API

function App() {
  const [dropped, setDropped] = useState(false);           // has the box been dropped?

  return (
    <div>
      {!dropped && (
        <div
          draggable                                        // enables native dragging
          onDragStart={(e) => e.dataTransfer.setData('text/plain', 'box')} // required in Firefox
        >
          Drag me
        </div>
      )}
      <div
        style={{ height: 100, border: '2px dashed gray' }}
        onDragOver={(e) => e.preventDefault()}             // WITHOUT this, drop never fires
        onDrop={() => setDropped(true)}                    // box was dropped here
      >
        {dropped ? 'Dropped!' : 'Drop zone'}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Kanban logic from App.jsx: pure helper + three handlers
const COLUMNS = ['todo', 'doing', 'done'];

// Pure function: immutable move, easy to unit test
export function moveTask(tasks, id, column) {
  return tasks.map((t) => (t.id === id ? { ...t, column } : t));
}

function Board() {
  const [tasks, setTasks] = useState(initial);
  const [overCol, setOverCol] = useState(null);            // highlighted column

  const onDragStart = (e, id) => {
    e.dataTransfer.setData('text/plain', String(id));      // dataTransfer only stores strings
    e.dataTransfer.effectAllowed = 'move';                 // cursor shows "move"
  };
  const onDragOver = (e, col) => { e.preventDefault(); setOverCol(col); };
  const onDrop = (e, col) => {
    e.preventDefault();
    const id = Number(e.dataTransfer.getData('text/plain')); // string back to number
    setTasks((prev) => moveTask(prev, id, col));           // state is the source of truth
    setOverCol(null);
  };
  // render: COLUMNS.map(col => <div onDragOver onDragLeave onDrop> + tasks.filter(...) cards)
}
```

For reordering inside a column or touch screens, use a library such as `@dnd-kit/core`
(native HTML5 drag does not work on most touch devices). The native version is enough for interviews.

---

## 🟠 Next.js Connection
Drag and drop is purely interactive, so the board must be a Client Component (`'use client'`). The page can fetch the initial tasks on the server and pass them as props. After a drop, update the UI at once (optimistic) and send the change with a Server Action.

```jsx
// app/board/page.jsx (Server Component): fetch data on the server
import Board from './Board';                              // Client Component
import { getTasks } from '@/lib/tasks';                   // hypothetical DB helper

export default async function Page() {
  const tasks = await getTasks();                         // no client waterfall
  return <Board initialTasks={tasks} />;                  // serialisable props only
}

// app/board/Board.jsx
'use client';                                             // drag events need the browser
import { moveTaskAction } from './actions';               // 'use server' function
// inside onDrop: setTasks(...optimistic); moveTaskAction(id, col);  // persist
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `e.preventDefault()` in `onDragOver`
✅ **Correct:** Always cancel `dragover` on the drop target

```jsx
// Wrong: onDrop never fires
<div onDrop={handleDrop}>zone</div>
// Right
<div onDragOver={(e) => e.preventDefault()} onDrop={handleDrop}>zone</div>
```

❌ **Mistake 2:** Moving DOM nodes yourself (`appendChild`) inside React
✅ **Correct:** Change state and let React render the new position

```jsx
// Wrong: React's virtual DOM no longer matches the real DOM
e.target.appendChild(dragged);
// Right
setTasks((prev) => moveTask(prev, id, col));
```

❌ **Mistake 3:** Reading drag data in `onDragOver`
✅ **Correct:** Read it in `onDrop` (browsers hide `getData` during dragover for security)

```jsx
// Wrong: returns '' during dragover in most browsers
onDragOver={(e) => console.log(e.dataTransfer.getData('text/plain'))}
// Right: store the dragged id in state/ref in dragstart if you need it earlier
```

---

## 🧠 Tricky Interview Question

```jsx
<div onDrop={() => alert('dropped')}>Drop here</div>
```
**Answer:** The alert never appears. By default the browser treats most elements as **not** valid drop targets. The target must call `preventDefault()` on `dragover` (and `dragenter` for some cases) to signal that dropping is allowed. Without it the `drop` event is never dispatched. Fix: add `onDragOver={(e) => e.preventDefault()}`.

---

## ⚫ Interview Questions + Answers

Q1: Which events does native drag and drop use?
A1: On the dragged element: `dragstart`, `drag`, `dragend`. On the target: `dragenter`, `dragover`, `dragleave`, `drop`. You must cancel `dragover` for `drop` to fire.

Q2: Where should the data live, `dataTransfer` or state?
A2: The real data lives in React state. `dataTransfer` only carries a small string (an id) between the events, and it can only be read fully in `drop`.

Q3: Why does native drag and drop not work well on mobile?
A3: HTML5 drag events are not fired by most touch browsers. Use pointer events or a library such as `@dnd-kit`, which supports touch and keyboard.

Q4: How do you make drag and drop accessible?
A4: Provide a keyboard alternative (for example a "Move to..." menu, or dnd-kit's keyboard sensor), announce changes with `aria-live`, and keep focus on the moved item.

Q5: How would you save the new position to a server?
A5: Update state optimistically, call the API (or Server Action), and roll the state back if the request fails. Debounce if the user can drop many times quickly.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Moving items between lists (boards, playlists, menus)
- Reordering a short list by hand

❌ **Avoid when:**
- Touch support is essential and you have no library (native events are unreliable)
- The list has thousands of items (use virtualization plus a dedicated library)
- A simple "move" button is clearer and more accessible

---

## 📊 Visual Diagram

```
   [Card #2 draggable]
        │ dragstart → dataTransfer.setData("2")
        ▼
   ┌─ To Do ──┐   ┌─ Doing ──┐   ┌─ Done ───┐
   │          │   │          │   │ dragover │ ← preventDefault() + highlight
   └──────────┘   └──────────┘   │ drop     │ ← getData("2") → setTasks(moveTask)
                                  └──────────┘
        state: tasks[2].column = "done"  → React re-renders the card in the new column
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| draggable | HTML attribute that allows dragging | Drag करने की अनुमति देने वाला attribute |
| dataTransfer | Object carrying data during a drag | Drag के दौरान data ले जाने वाला object |
| Drop target | Element that accepts a drop | जो element drop स्वीकार करे |
| preventDefault | Cancels the browser default action | Browser की default क्रिया रोकना |
| Optimistic update | Update UI before the server replies | Server के जवाब से पहले UI बदलना |
| Sensor | dnd-kit input source (mouse, touch, keyboard) | Input का स्रोत |

---

## ⚡ 3-Line Summary
**English:**
1. Use `draggable`, `onDragStart` (store id), `onDragOver` (preventDefault) and `onDrop` (update state).
2. Keep real data in React state, and use `dataTransfer` only to pass a small id string.
3. In Next.js make the board a Client Component and persist moves with Server Actions.

**Hindi:**
1. `draggable`, `onDragStart` (id रखो), `onDragOver` (preventDefault) और `onDrop` (state बदलो) इस्तेमाल करो।
2. असली data React state में रखो, और `dataTransfer` सिर्फ छोटी id string भेजने के लिए इस्तेमाल करो।
3. Next.js में board को Client Component बनाओ और moves को Server Actions से save करो।

---

## ➡️ Next Topic
**204. Build Custom Hook — useFetch** — अब reusable logic की practice: loading, error, cancel और race conditions संभालने वाला data-fetching hook।
