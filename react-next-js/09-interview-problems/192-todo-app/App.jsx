// Todo App: create, read, update (edit + toggle), delete, filter, persisted in localStorage
import { useState, useEffect } from 'react';             // state + side effect for saving

const KEY = 'todos-v1';                                  // localStorage key

function loadTodos() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || [];  // read saved todos
  } catch {
    return [];                                           // bad JSON or no localStorage
  }
}

function TodoItem({ todo, onToggle, onDelete, onEdit }) {
  const [editing, setEditing] = useState(false);         // is this row in edit mode?
  const [draft, setDraft] = useState(todo.text);         // text being edited

  const save = () => {
    const text = draft.trim();                           // remove extra spaces
    if (text) onEdit(todo.id, text);                     // save only non-empty text
    else setDraft(todo.text);                            // empty: restore old text
    setEditing(false);                                   // leave edit mode
  };

  return (
    <li>
      <input type="checkbox" checked={todo.done} onChange={() => onToggle(todo.id)} /> {/* toggle */}
      {editing ? (
        <input
          autoFocus
          value={draft}
          onChange={(e) => setDraft(e.target.value)}     // controlled edit input
          onBlur={save}                                  // save when focus leaves
          onKeyDown={(e) => e.key === 'Enter' && save()} // Enter saves
        />
      ) : (
        <span
          onDoubleClick={() => setEditing(true)}         // double click to edit
          style={{ textDecoration: todo.done ? 'line-through' : 'none' }}
        >
          {todo.text}
        </span>
      )}
      <button onClick={() => onDelete(todo.id)} aria-label={`Delete ${todo.text}`}>x</button>
    </li>
  );
}

export default function App() {
  const [todos, setTodos] = useState(loadTodos);          // lazy init: read storage once
  const [text, setText] = useState('');                   // new todo input
  const [filter, setFilter] = useState('all');            // all | active | done

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(todos));     // save on every change
  }, [todos]);

  const add = (e) => {
    e.preventDefault();                                   // stop page reload
    const t = text.trim();                                // clean input
    if (!t) return;                                       // ignore empty todo
    setTodos((prev) => [...prev, { id: crypto.randomUUID(), text: t, done: false }]); // CREATE
    setText('');                                          // clear the input
  };
  const toggle = (id) =>
    setTodos((prev) => prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t))); // UPDATE
  const edit = (id, newText) =>
    setTodos((prev) => prev.map((t) => (t.id === id ? { ...t, text: newText } : t))); // UPDATE
  const remove = (id) => setTodos((prev) => prev.filter((t) => t.id !== id));          // DELETE

  const visible = todos.filter((t) =>                     // derived data, not stored in state
    filter === 'all' ? true : filter === 'done' ? t.done : !t.done
  );
  const left = todos.filter((t) => !t.done).length;       // items still to do

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 400 }}>
      <h1>Todos</h1>
      <form onSubmit={add}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="What needs to be done?" />
        <button type="submit">Add</button>
      </form>
      <ul>
        {visible.map((t) => (
          <TodoItem key={t.id} todo={t} onToggle={toggle} onDelete={remove} onEdit={edit} /> // stable key
        ))}
      </ul>
      <p>{left} item(s) left</p>
      {['all', 'active', 'done'].map((f) => (
        <button key={f} onClick={() => setFilter(f)} disabled={filter === f}>{f}</button>
      ))}
    </div>
  );
}
