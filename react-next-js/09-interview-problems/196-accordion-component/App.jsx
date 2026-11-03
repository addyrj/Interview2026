// Accordion: single or multiple open panels, accessible buttons, controlled by one state
import { useState, useId } from 'react';

function Accordion({ items, multiple = false }) {
  const [openIds, setOpenIds] = useState(new Set());     // ids of open panels
  const baseId = useId();                                // unique id prefix

  const toggle = (id) =>
    setOpenIds((prev) => {
      const next = new Set(multiple ? prev : []);        // single mode: start empty
      if (prev.has(id)) next.delete(id);                 // open -> close
      else next.add(id);                                 // closed -> open
      return next;                                       // new Set so React re-renders
    });

  return (
    <div>
      {items.map((item) => {
        const isOpen = openIds.has(item.id);
        return (
          <div key={item.id}>
            <h3>
              <button
                id={`${baseId}-btn-${item.id}`}
                aria-expanded={isOpen}                   // screen readers announce state
                aria-controls={`${baseId}-panel-${item.id}`}
                onClick={() => toggle(item.id)}
              >
                {item.title} {isOpen ? '-' : '+'}
              </button>
            </h3>
            <div
              id={`${baseId}-panel-${item.id}`}
              role="region"
              aria-labelledby={`${baseId}-btn-${item.id}`}
              hidden={!isOpen}                           // hidden keeps state of children
            >
              <p>{item.content}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

const FAQ = [
  { id: 'a', title: 'How do I track my order?', content: 'Open Orders and tap Track.' },
  { id: 'b', title: 'Can I cancel an order?', content: 'Yes, before the restaurant accepts it.' },
  { id: 'c', title: 'How do refunds work?', content: 'Refunds reach you in 5-7 days.' },
];

export default function App() {
  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 400 }}>
      <h1>FAQ</h1>
      <Accordion items={FAQ} />                          {/* only one open at a time */}
    </div>
  );
}

export { Accordion };                                    // reuse with multiple={true}
