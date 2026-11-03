// Virtual list (windowing): render only the visible rows of a fixed-height list
import { useState, useMemo } from 'react'; // React hooks
import { createRoot } from 'react-dom/client'; // root API

// Pure math: which rows are visible? Easy to unit test.
export function getVisibleRange({ scrollTop, viewportHeight, itemHeight, total, overscan = 3 }) {
  const first = Math.floor(scrollTop / itemHeight);                     // first row touching the top
  const count = Math.ceil(viewportHeight / itemHeight);                 // rows that fit in the view
  const start = Math.max(0, first - overscan);                          // extra rows above
  const end = Math.min(total, first + count + overscan);                // extra rows below (exclusive)
  return { start, end };
}

export function VirtualList({ items, itemHeight = 40, height = 400, overscan = 3, renderItem }) {
  const [scrollTop, setScrollTop] = useState(0);                        // scroll position

  const { start, end } = useMemo(
    () => getVisibleRange({ scrollTop, viewportHeight: height, itemHeight, total: items.length, overscan }),
    [scrollTop, height, itemHeight, items.length, overscan]
  );

  const visible = [];                                                   // only these rows are in the DOM
  for (let i = start; i < end; i++) {
    visible.push(
      <div
        key={i}                                                         // index key is fine: fixed rows
        style={{ position: 'absolute', top: i * itemHeight, height: itemHeight, left: 0, right: 0 }}
      >
        {renderItem(items[i], i)}
      </div>
    );
  }

  return (
    <div
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}         // track scrolling
      style={{ height, overflowY: 'auto', position: 'relative' }}       // the viewport
      data-testid="viewport"
    >
      {/* Spacer gives the scrollbar the full height of all rows */}
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>{visible}</div>
    </div>
  );
}

const orders = Array.from({ length: 10000 }, (_, i) => `Order #${i + 1}`); // 10,000 fake rows

export default function App() {
  return (
    <VirtualList items={orders} renderItem={(text) => <span>{text}</span>} />
  );
}

const rootEl = typeof document !== 'undefined' && document.getElementById('root');
if (rootEl) createRoot(rootEl).render(<App />);
