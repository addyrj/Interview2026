// useFetch: loading / error / data with AbortController, race-condition safe, manual refetch
import { useState, useEffect, useCallback } from 'react'; // React hooks

export function useFetch(url, options) {
  const [state, setState] = useState({ data: null, error: null, loading: Boolean(url) }); // one object
  const [tick, setTick] = useState(0);                       // bump to force a refetch

  // options is usually a new object each render, so serialise it for a stable dependency
  const optionsKey = JSON.stringify(options ?? null);

  useEffect(() => {
    if (!url) return undefined;                              // nothing to fetch yet
    const controller = new AbortController();                // lets us cancel the request
    setState((s) => ({ ...s, loading: true, error: null })); // keep old data while reloading

    fetch(url, { ...JSON.parse(optionsKey), signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);  // fetch does NOT reject on 404/500
        return res.json();
      })
      .then((data) => setState({ data, error: null, loading: false })) // success
      .catch((error) => {
        if (error.name === 'AbortError') return;             // cancelled on purpose: ignore
        setState((s) => ({ ...s, error, loading: false }));  // real failure
      });

    return () => controller.abort();                         // cleanup: url changed or unmounted
  }, [url, optionsKey, tick]);

  const refetch = useCallback(() => setTick((t) => t + 1), []); // stable function
  return { ...state, refetch };
}

export default useFetch;

/* Usage:
function Restaurants({ city }) {
  const { data, loading, error, refetch } = useFetch(`/api/restaurants?city=${city}`);
  if (loading) return <p>Loading...</p>;
  if (error) return <button onClick={refetch}>Retry</button>;
  return <ul>{data.map((r) => <li key={r.id}>{r.name}</li>)}</ul>;
}
*/
