# 192. Build Todo App (CRUD)
# हिंदी में: Todo App बनाना (Create, Read, Update, Delete)

Code: [`App.jsx`](./App.jsx) in this folder (complete: add, edit by double click, toggle, delete, filter, localStorage persistence).

---

## 🔵 Simple Definition (English)
The Todo App is the standard CRUD interview problem. The user can **C**reate items, **R**ead (see) them, **U**pdate (edit or mark done) them and **D**elete them. It tests list state, immutable updates, keys, controlled inputs and derived data.

## 🔵 सरल परिभाषा (Hindi)
Todo App CRUD वाला standard interview problem है। User items **C**reate कर सकता है, **R**ead (देख) सकता है, **U**pdate (edit या done mark) कर सकता है और **D**elete कर सकता है। इसमें list state, immutable updates, keys, controlled inputs और derived data की परीक्षा होती है।

---

## 🔴 Problem it Solves

Real apps manage lists: cart items, notifications, tasks. Beginners mutate arrays with `push` or `splice`, use the array index as `key`, or store filtered lists in extra state that gets out of sync. This problem checks that you update arrays immutably, use stable ids, and compute filtered data during render.

```jsx
// PROBLEM: mutation does not trigger a proper re-render
const addTodo = () => {
  todos.push({ id: 1, text });        // ❌ mutates the same array
  setTodos(todos);                    // same reference → React may skip the update
};
```

## 🔴 यह क्यों बना? (Hindi)
असली apps lists संभालते हैं: cart items, notifications, tasks। नए developers arrays को `push` या `splice` से mutate करते हैं, array index को `key` बना देते हैं, या filtered list को अलग state में रखते हैं जो sync से बाहर हो जाती है। यह problem जाँचता है कि आप arrays को immutably update करते हैं, stable ids इस्तेमाल करते हैं और filtered data render के दौरान निकालते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State: todos = [{ id, text, done }], text (new input), filter ('all'|'active'|'done')
Step 2 → CREATE: form submit → trim text → setTodos(prev => [...prev, newTodo]) → clear input
Step 3 → READ: filter todos during render → map to <TodoItem key={todo.id} />
Step 4 → UPDATE: toggle/edit → setTodos(prev => prev.map(t => t.id === id ? {...t, ...} : t))
Step 5 → DELETE: setTodos(prev => prev.filter(t => t.id !== id))
Step 6 → PERSIST: useEffect([todos]) saves JSON to localStorage; lazy useState reads it once
Step 7 → DERIVE: "items left" and the visible list are computed, never stored

Interview approach: "Single source of truth (todos), immutable updates with map/filter/spread,
stable ids as keys, derived values, small child component for row-local edit state."
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State: todos = [{ id, text, done }], text (नया input), filter ('all'|'active'|'done')
Step 2 → CREATE: form submit → text trim → setTodos(prev => [...prev, newTodo]) → input खाली
Step 3 → READ: render के दौरान todos filter करो → <TodoItem key={todo.id} /> में map करो
Step 4 → UPDATE: toggle/edit → setTodos(prev => prev.map(t => t.id === id ? {...t, ...} : t))
Step 5 → DELETE: setTodos(prev => prev.filter(t => t.id !== id))
Step 6 → PERSIST: useEffect([todos]) JSON को localStorage में सेव करता है; lazy useState उसे एक बार पढ़ता है
Step 7 → DERIVE: "items left" और visible list की गणना होती है, उन्हें store नहीं करते

Interview approach: "एक source of truth (todos), map/filter/spread से immutable updates,
keys के लिए stable ids, derived values, row की edit state के लिए छोटा child component।"
```

---

## 🟡 Real World Example
**Swiggy cart / Zomato "saved addresses":** each row can be edited, selected and deleted. **Google Keep / Notion tasks** are literally todo lists. In all of them, the list of items is one array in state (or on a server), and each action is a pure "old list → new list" transformation.

## 🟡 Real Example Hindi mein
**Swiggy cart / Zomato "saved addresses":** हर row को edit, select और delete किया जा सकता है। **Google Keep / Notion tasks** सीधे todo lists हैं। सबमें items की list एक array में state (या server) में होती है, और हर action "पुरानी list → नई list" का शुद्ध transformation है।

---

## 💻 Code Example — Basic

```jsx
// Minimal todo: add, toggle, delete (no persistence, no edit)
import { useState } from 'react';

export default function Todo() {
  const [todos, setTodos] = useState([]);                    // list of { id, text, done }
  const [text, setText] = useState('');                      // controlled input value

  const add = (e) => {
    e.preventDefault();                                      // no page reload
    if (!text.trim()) return;                                // ignore empty
    setTodos((prev) => [...prev, { id: crypto.randomUUID(), text: text.trim(), done: false }]); // new array
    setText('');                                             // clear input
  };

  return (
    <div>
      <form onSubmit={add}>
        <input value={text} onChange={(e) => setText(e.target.value)} />
        <button>Add</button>
      </form>
      <ul>
        {todos.map((t) => (
          <li key={t.id}>                                    {/* stable key, never the index */}
            <input
              type="checkbox" checked={t.done}
              onChange={() => setTodos((p) => p.map((x) => (x.id === t.id ? { ...x, done: !x.done } : x)))}
            />
            {t.text}
            <button onClick={() => setTodos((p) => p.filter((x) => x.id !== t.id))}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 💻 Code Example — Advanced

The full version in [`App.jsx`](./App.jsx) adds edit mode, filters, lazy `localStorage` init and a `TodoItem` child. Key excerpts:

```jsx
// 1. Lazy initial state: the loader runs once, not on every render
const [todos, setTodos] = useState(loadTodos);               // pass the function, do not call it

// 2. Persist on change
useEffect(() => {
  localStorage.setItem(KEY, JSON.stringify(todos));          // runs after todos changes
}, [todos]);

// 3. Derived data: never store the filtered list in state
const visible = todos.filter((t) =>
  filter === 'all' ? true : filter === 'done' ? t.done : !t.done
);
const left = todos.filter((t) => !t.done).length;            // "items left"

// 4. Row-local state lives in the row: editing + draft only affect ONE item
function TodoItem({ todo, onToggle, onDelete, onEdit }) {
  const [editing, setEditing] = useState(false);             // edit mode for this row
  const [draft, setDraft] = useState(todo.text);             // text being edited
  // Enter or blur saves; empty text restores the old text
}
```

Verified with a jsdom test: add, toggle (strike-through), localStorage content, "active" filter, delete all behave correctly.

---

## 🟠 Next.js Connection

In Next.js you usually keep the data on the server and mutate it with **Server Actions**, while the interactive row stays a Client Component.

```jsx
// app/todos/actions.js
'use server';                                            // Server Actions file
import { revalidatePath } from 'next/cache';
import { db } from '@/lib/db';                           // hypothetical database client

export async function addTodo(formData) {
  const text = String(formData.get('text') ?? '').trim();// validate on the server, never trust the client
  if (!text) return;
  await db.todo.create({ data: { text } });              // CREATE
  revalidatePath('/todos');                              // refresh the list shown by the page
}
export async function deleteTodo(id) {
  await db.todo.delete({ where: { id } });               // DELETE
  revalidatePath('/todos');
}
```

```jsx
// app/todos/page.jsx (Server Component): READ happens on the server
import { db } from '@/lib/db';
import { addTodo, deleteTodo } from './actions';

export default async function Page() {
  const todos = await db.todo.findMany();                // no useEffect, no loading state
  return (
    <>
      <form action={addTodo}><input name="text" /><button>Add</button></form>
      <ul>
        {todos.map((t) => (
          <li key={t.id}>
            {t.text}
            <form action={deleteTodo.bind(null, t.id)}><button>x</button></form>
          </li>
        ))}
      </ul>
    </>
  );
}
```
Also note: `localStorage` does not exist during SSR, so only touch it inside effects or event handlers in a Client Component. For instant UI use `useOptimistic` (React 19).

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating the array or object in state
✅ **Correct:** Return new arrays/objects with spread, `map`, `filter`.

```jsx
// Wrong
todos[i].done = !todos[i].done;                          // ❌ mutation
setTodos(todos);                                         // same reference

// Right
setTodos((prev) => prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t))); // ✅
```

❌ **Mistake 2:** Using the index as `key`
✅ **Correct:** Use a stable unique id. With index keys, deleting or filtering shifts state (edit drafts, checkboxes) to the wrong row.

```jsx
// Wrong: delete the first item and the second row inherits its editing state
{todos.map((t, i) => <TodoItem key={i} todo={t} />)}     // ❌

// Right
{todos.map((t) => <TodoItem key={t.id} todo={t} />)}     // ✅
```

❌ **Mistake 3:** Storing derived data (filtered list, count) in state
✅ **Correct:** Compute it during render. Duplicated state goes out of sync.

```jsx
// Wrong: two sources of truth
const [visible, setVisible] = useState([]);              // ❌ must be updated everywhere
// Right
const visible = todos.filter(/* by filter */);           // ✅ always correct
```

---

## 🧠 Tricky Interview Question

```jsx
function List() {
  const [items, setItems] = useState(['a', 'b', 'c']);
  return (
    <>
      {items.map((x, i) => (
        <input key={i} defaultValue={x} />      // index as key, uncontrolled input
      ))}
      <button onClick={() => setItems((p) => p.slice(1))}>Remove first</button>
    </>
  );
}
// The user types "ZZZ" into the FIRST input, then clicks "Remove first".
// What do the inputs show now?
```
**Answer:** The two remaining inputs show `ZZZ` and `b`, which is not what you expect. After removal `items = ['b','c']`. With keys `0` and `1`, React matches the old input 0 with the new input 0 (it keeps the DOM node and its typed value `ZZZ`), and `defaultValue` only matters on mount, so it does not update. Input with key 2 is removed. With stable keys (`key={x}`), React would remove the DOM node of `a` (with the `ZZZ` text), and the inputs would show `b` and `c`. Lesson: index keys are only safe for static lists that never reorder, insert or delete.

---

## ⚫ Interview Questions + Answers

Q1: How do you add, update and delete items in an array state without mutation?
A1: Add: `[...prev, item]`. Update: `prev.map(t => t.id === id ? { ...t, ...changes } : t)`. Delete: `prev.filter(t => t.id !== id)`. Each returns a new array, so React sees a changed reference and re-renders.

Q2: Why do you need unique, stable keys?
A2: Keys let React match old and new elements across renders. Stable ids keep component state (edit mode, input drafts) attached to the right row when the list changes. Index keys break this on insert, delete or reorder.

Q3: Why is `loadTodos` passed to `useState` instead of `loadTodos()`?
A3: Passing the function is lazy initialisation: React calls it once on the first render. Calling it every render would read and parse `localStorage` each time (wasted work), even though the result is ignored after the first render.

Q4: How would you optimise a list of 10,000 todos?
A4: Wrap `TodoItem` in `React.memo` and pass stable callbacks (`useCallback`, which works well because the handlers use functional updates and need no changing dependencies), paginate or virtualise the list (topic 209), and avoid recalculating the filter with `useMemo` if profiling shows a cost.

Q5: Where would the edit state live, and why?
A5: In `TodoItem`, because only that row needs `editing` and `draft`. Putting it in `App` would re-render the whole list on every keystroke. Only the saved result is sent up with `onEdit(id, text)`.

---

## 🔷 When to Use + When Not to Use
✅ **Use local state for a todo list when:**
- It is a small, single-user list in one page or component
- You do not need server sync or sharing

❌ **Avoid when:**
- The list is shared between users or devices (server state: TanStack Query, Server Actions)
- Updates have complex rules or undo/redo (use `useReducer`)

---

## 📊 Visual Diagram

```
   state: todos[] (single source of truth)
        │
        ├── CREATE  [...prev, new]
        ├── UPDATE  prev.map(...)
        └── DELETE  prev.filter(...)
        │
        ▼
   render: visible = todos.filter(byFilter)   (derived)
        │
        ▼
   <ul> <TodoItem key=id /> ... </ul>        TodoItem keeps its own editing/draft state
        │
        └─ useEffect([todos]) → localStorage

   Re-render: any change to todos re-renders App and its rows.
   Optimisation: React.memo(TodoItem) + stable callbacks for big lists.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CRUD | Create, Read, Update, Delete | बनाओ, पढ़ो, बदलो, हटाओ |
| Immutable update | Make a new copy instead of changing | बदलने की जगह नई copy बनाना |
| key | Stable id used by React to match items | React को items पहचानने वाली stable id |
| Lazy init | Passing a function to useState | useState को function देना |
| Derived data | Computed from state at render | State से render में निकाला data |
| Controlled input | Value controlled by React state | React state से चलने वाला input |
| Single source of truth | One place owns the data | डेटा का एक ही मालिक |
| Server Action | Server function called from forms | Forms से call होने वाला server function |

---

## ⚡ 3-Line Summary
**English:**
1. Keep one `todos` array in state and change it only with new arrays (`spread`, `map`, `filter`).
2. Use stable ids as keys, compute filtered lists and counts during render, and keep row-only state in the row.
3. Persist with a lazy `useState` plus `useEffect`, or in Next.js use Server Actions with `revalidatePath`.

**Hindi:**
1. एक `todos` array state में रखो और उसे सिर्फ नए arrays (`spread`, `map`, `filter`) से बदलो।
2. Keys के लिए stable ids लो, filtered lists और counts render में निकालो, और row की अपनी state row में रखो।
3. Lazy `useState` और `useEffect` से persist करो, या Next.js में Server Actions के साथ `revalidatePath` इस्तेमाल करो।

---

## ➡️ Next Topic
**193. Build Search with Debounce** — user हर keystroke पर API न बुलाए, इसके लिए debounce, request cancel (AbortController) और loading/error states।
