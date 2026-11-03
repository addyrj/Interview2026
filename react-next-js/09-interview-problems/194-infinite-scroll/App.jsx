// Infinite Scroll: load the next page when a sentinel element becomes visible
import { useState, useEffect, useRef, useCallback } from 'react';

const PAGE_SIZE = 10;                                    // items per page
const TOTAL = 45;                                        // pretend server has 45 items

// Fake paginated API: returns { items, hasMore }
function fetchPage(page) {
  return new Promise((resolve) => {
    setTimeout(() => {                                   // pretend network delay
      const start = page * PAGE_SIZE;
      const items = Array.from(
        { length: Math.max(0, Math.min(PAGE_SIZE, TOTAL - start)) },
        (_, i) => ({ id: start + i + 1, title: `Restaurant #${start + i + 1}` })
      );
      resolve({ items, hasMore: start + PAGE_SIZE < TOTAL });
    }, 400);
  });
}

export default function App() {
  const [items, setItems] = useState([]);                // all loaded items
  const [page, setPage] = useState(0);                   // next page to load
  const [loading, setLoading] = useState(false);         // request in progress
  const [hasMore, setHasMore] = useState(true);          // is there more data?
  const loadingRef = useRef(false);                      // sync guard against double loads
  const observerRef = useRef(null);                      // current IntersectionObserver

  const loadMore = useCallback(async () => {
    if (loadingRef.current) return;                      // already loading: ignore
    loadingRef.current = true;
    setLoading(true);
    try {
      const res = await fetchPage(page);                 // get the next page
      setItems((prev) => [...prev, ...res.items]);       // append, never replace
      setHasMore(res.hasMore);
      setPage((p) => p + 1);
    } catch (err) {
      console.error('load failed', err);                 // real app: show an error + retry button
    } finally {
      loadingRef.current = false;                        // always release the guard
      setLoading(false);
    }
  }, [page]);

  // Callback ref for the sentinel: connects the observer whenever the element mounts
  const sentinelRef = useCallback(
    (node) => {
      if (observerRef.current) observerRef.current.disconnect(); // remove the old observer
      if (!node || !hasMore) return;                     // nothing to watch
      observerRef.current = new IntersectionObserver(
        (entries) => { if (entries[0].isIntersecting) loadMore(); }, // sentinel visible: load
        { rootMargin: '200px' }                          // start loading a bit early
      );
      observerRef.current.observe(node);
    },
    [hasMore, loadMore]
  );

  useEffect(() => () => observerRef.current?.disconnect(), []); // cleanup on unmount

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 360 }}>
      <ul>{items.map((i) => <li key={i.id} style={{ padding: 24 }}>{i.title}</li>)}</ul>
      {hasMore && <div ref={sentinelRef} style={{ height: 1 }} />}  {/* sentinel at the bottom */}
      {loading && <p>Loading...</p>}
      {!hasMore && <p>You have seen everything.</p>}
    </div>
  );
}
