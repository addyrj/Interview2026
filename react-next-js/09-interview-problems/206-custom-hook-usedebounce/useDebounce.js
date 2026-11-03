// useDebounce: returns a value that updates only after the input stopped changing for `delay` ms
import { useState, useEffect } from 'react'; // React hooks

export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);         // the slow, settled copy

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay); // schedule the update
    return () => clearTimeout(id);                           // new value arrived: cancel old timer
  }, [value, delay]);                                        // restart on every change

  return debounced;
}

export default useDebounce;

/* Usage (Zomato search):
function Search() {
  const [q, setQ] = useState('');
  const debouncedQ = useDebounce(q, 400);
  useEffect(() => { if (debouncedQ) fetch(`/api/search?q=${debouncedQ}`); }, [debouncedQ]);
  return <input value={q} onChange={(e) => setQ(e.target.value)} />;
}
*/
