// useWindowSize: current window width/height, SSR safe, listener cleaned up, optional throttle
import { useState, useEffect } from 'react'; // React hooks

export function useWindowSize(throttleMs = 100) {
  // Start with undefined on server AND first client render so hydration matches
  const [size, setSize] = useState({ width: undefined, height: undefined });

  useEffect(() => {
    let timer = null;                                        // pending throttled update
    const update = () => {
      timer = null;
      setSize({ width: window.innerWidth, height: window.innerHeight }); // read real size
    };
    const onResize = () => {
      if (timer === null) timer = setTimeout(update, throttleMs); // at most once per window
    };

    update();                                                // set the initial size after mount
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);        // cleanup listener
      if (timer !== null) clearTimeout(timer);               // cleanup pending timer
    };
  }, [throttleMs]);

  return size;
}

export default useWindowSize;

/* Usage:
const { width } = useWindowSize();
const isMobile = width !== undefined && width < 768;
*/
