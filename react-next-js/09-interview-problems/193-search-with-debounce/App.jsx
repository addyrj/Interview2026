// Search with debounce: call the API only after the user stops typing for 400ms
import { useState, useEffect } from 'react';             // state + effects

// Small reusable hook: returns `value` only after `delay` ms of no change
function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);     // delayed copy of the value
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay); // start the timer
    return () => clearTimeout(id);                       // new keystroke cancels the old timer
  }, [value, delay]);
  return debounced;
}

// Fake API so the file runs anywhere; replace with fetch(url, { signal })
const DATA = ['Biryani', 'Burger', 'Butter Chicken', 'Dosa', 'Idli', 'Paneer Tikka', 'Pizza', 'Samosa'];
function fakeSearch(q, signal) {
  return new Promise((resolve, reject) => {
    const id = setTimeout(
      () => resolve(DATA.filter((d) => d.toLowerCase().includes(q.toLowerCase()))),
      300                                                // pretend network delay
    );
    signal.addEventListener('abort', () => {             // cancel support, like fetch
      clearTimeout(id);
      reject(new DOMException('Aborted', 'AbortError'));
    });
  });
}

export default function App() {
  const [query, setQuery] = useState('');                // what the user typed (instant)
  const debounced = useDebounce(query, 400);             // what we search for (delayed)
  const [results, setResults] = useState([]);            // results from the API
  const [loading, setLoading] = useState(false);         // loading flag
  const [error, setError] = useState(null);              // error message

  useEffect(() => {
    const q = debounced.trim();                          // ignore spaces
    if (!q) { setResults([]); return; }                  // empty query: clear results
    const controller = new AbortController();            // lets us cancel stale requests
    setLoading(true);
    setError(null);
    fakeSearch(q, controller.signal)
      .then(setResults)                                  // save results
      .catch((err) => { if (err.name !== 'AbortError') setError('Search failed'); }) // ignore cancels
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();                     // cleanup: cancel on change/unmount
  }, [debounced]);                                       // runs only when debounced value changes

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 360 }}>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}       // updates on every keystroke
        placeholder="Search food..."
        aria-label="Search food"
      />
      {loading && <p>Searching...</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && debounced && results.length === 0 && !error && <p>No results</p>}
      <ul>{results.map((r) => <li key={r}>{r}</li>)}</ul>
    </div>
  );
}
