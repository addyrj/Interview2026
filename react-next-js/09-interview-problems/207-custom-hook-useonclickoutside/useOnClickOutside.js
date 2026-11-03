// useOnClickOutside: call handler when the user presses/touches outside the referenced element
import { useEffect, useRef } from 'react'; // React hooks

export function useOnClickOutside(ref, handler) {
  const handlerRef = useRef(handler);                        // always hold the latest handler
  useEffect(() => {
    handlerRef.current = handler;                            // update without re-subscribing
  });

  useEffect(() => {
    const listener = (event) => {
      const el = ref.current;                                // the element to protect
      if (!el || el.contains(event.target)) return;          // click inside (or not mounted): ignore
      handlerRef.current(event);                             // click outside: notify
    };
    document.addEventListener('mousedown', listener);        // mouse
    document.addEventListener('touchstart', listener);       // touch devices
    return () => {
      document.removeEventListener('mousedown', listener);   // cleanup
      document.removeEventListener('touchstart', listener);
    };
  }, [ref]);                                                 // ref object is stable
}

export default useOnClickOutside;

/* Usage (Flipkart dropdown):
function Menu() {
  const ref = useRef(null);
  const [open, setOpen] = useState(false);
  useOnClickOutside(ref, () => setOpen(false));
  return <div ref={ref}><button onClick={() => setOpen(o => !o)}>Menu</button>{open && <ul>...</ul>}</div>;
}
*/
