// useLocalStorage: useState that persists, syncs across tabs, is SSR safe
import { useState, useEffect, useCallback } from 'react'; // React hooks

function read(key, initialValue) {
  if (typeof window === 'undefined') return initialValue;    // server: no localStorage
  try {
    const raw = window.localStorage.getItem(key);            // stored string or null
    return raw === null ? initialValue : JSON.parse(raw);    // parse JSON back to a value
  } catch {
    return initialValue;                                     // corrupt JSON / blocked storage
  }
}

export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => read(key, initialValue)); // lazy: read once

  const set = useCallback((next) => {
    setValue((prev) => {
      const resolved = typeof next === 'function' ? next(prev) : next; // support updater fn
      try {
        window.localStorage.setItem(key, JSON.stringify(resolved));    // persist
      } catch {
        /* quota exceeded or private mode: keep working in memory */
      }
      return resolved;
    });
  }, [key]);

  useEffect(() => {
    const onStorage = (e) => {                               // fires in OTHER tabs only
      if (e.key !== key) return;                             // some other key changed
      setValue(e.newValue === null ? initialValue : JSON.parse(e.newValue));
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage); // cleanup
    // initialValue intentionally omitted: it is only a fallback
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return [value, set];
}

export default useLocalStorage;

/* Usage:
const [lang, setLang] = useLocalStorage('lang', 'en');
setLang('hi');
setLang((l) => (l === 'en' ? 'hi' : 'en'));
*/
