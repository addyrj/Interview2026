// Drag and drop kanban board using the native HTML5 drag events (no library)
import { useState } from 'react'; // state hook
import { createRoot } from 'react-dom/client'; // root API

const COLUMNS = ['todo', 'doing', 'done'];              // column ids in display order
const TITLES = { todo: 'To Do', doing: 'In Progress', done: 'Done' };

// Pure helper: move a task to another column (immutable)
export function moveTask(tasks, id, column) {
  return tasks.map((t) => (t.id === id ? { ...t, column } : t));
}

const initial = [
  { id: 1, text: 'Design cart page', column: 'todo' },
  { id: 2, text: 'Fix checkout bug', column: 'doing' },
  { id: 3, text: 'Ship dark mode', column: 'done' },
];

export default function App() {
  const [tasks, setTasks] = useState(initial);          // all tasks
  const [overCol, setOverCol] = useState(null);         // column highlighted while dragging

  const onDragStart = (e, id) => {
    e.dataTransfer.setData('text/plain', String(id));   // carry the task id
    e.dataTransfer.effectAllowed = 'move';              // show a "move" cursor
  };

  const onDragOver = (e, col) => {
    e.preventDefault();                                 // REQUIRED: without it, drop never fires
    setOverCol(col);                                    // highlight the target column
  };

  const onDrop = (e, col) => {
    e.preventDefault();
    const id = Number(e.dataTransfer.getData('text/plain')); // read the carried id
    setTasks((prev) => moveTask(prev, id, col));        // update column
    setOverCol(null);                                   // remove highlight
  };

  return (
    <div style={{ display: 'flex', gap: 16 }}>
      {COLUMNS.map((col) => (
        <div
          key={col}
          data-testid={`col-${col}`}
          onDragOver={(e) => onDragOver(e, col)}
          onDragLeave={() => setOverCol(null)}
          onDrop={(e) => onDrop(e, col)}
          style={{
            flex: 1, minHeight: 200, padding: 8, borderRadius: 8,
            background: overCol === col ? '#e8f0fe' : '#f4f4f4', // highlight target
          }}
        >
          <h3>{TITLES[col]}</h3>
          {tasks.filter((t) => t.column === col).map((t) => (
            <div
              key={t.id}
              draggable                                  // makes the element draggable
              onDragStart={(e) => onDragStart(e, t.id)}
              style={{ background: '#fff', margin: '6px 0', padding: 8, cursor: 'grab' }}
            >
              {t.text}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

const rootEl = typeof document !== 'undefined' && document.getElementById('root');
if (rootEl) createRoot(rootEl).render(<App />);
