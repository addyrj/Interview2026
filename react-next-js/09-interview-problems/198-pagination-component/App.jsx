// Pagination: reusable component with page window + ellipsis, and client-side paging demo
import { useState, useMemo } from 'react';

// Pure helper: pages to show, e.g. [1, '...', 4, 5, 6, '...', 20]
export function getPageRange(current, total, siblings = 1) {
  const first = 1;
  const last = total;
  const start = Math.max(first + 1, current - siblings);  // window start
  const end = Math.min(last - 1, current + siblings);     // window end
  const pages = [first];
  if (start > first + 1) pages.push('...');               // gap after first page
  for (let p = start; p <= end; p++) pages.push(p);       // middle window
  if (end < last - 1) pages.push('...');                  // gap before last page
  if (last > first) pages.push(last);
  return pages;
}

export function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null;                       // nothing to paginate
  const range = getPageRange(page, totalPages);
  return (
    <nav aria-label="Pagination">
      <button onClick={() => onChange(page - 1)} disabled={page === 1}>Prev</button>
      {range.map((p, i) =>
        p === '...' ? (
          <span key={`gap-${i}`}> ... </span>
        ) : (
          <button
            key={p}
            onClick={() => onChange(p)}
            aria-current={p === page ? 'page' : undefined}  // marks the current page
            disabled={p === page}
          >
            {p}
          </button>
        )
      )}
      <button onClick={() => onChange(page + 1)} disabled={page === totalPages}>Next</button>
    </nav>
  );
}

const ALL = Array.from({ length: 95 }, (_, i) => `Order #${i + 1}`); // 95 fake items
const PAGE_SIZE = 10;

export default function App() {
  const [page, setPage] = useState(1);                    // current page, 1-based
  const totalPages = Math.ceil(ALL.length / PAGE_SIZE);   // 10 pages
  const slice = useMemo(                                  // items of current page only
    () => ALL.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    [page]
  );
  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 420 }}>
      <ul>{slice.map((o) => <li key={o}>{o}</li>)}</ul>
      <Pagination page={page} totalPages={totalPages} onChange={setPage} />
    </div>
  );
}
