// useLocation.js — custom hook around expo-location (foreground only)
import { useCallback, useEffect, useRef, useState } from 'react'; // hooks
import * as Location from 'expo-location'; // Expo location API

export default function useLocation({ watch = false } = {}) {
  const [coords, setCoords] = useState(null); // { latitude, longitude, accuracy }
  const [error, setError] = useState(null); // string message or null
  const [loading, setLoading] = useState(false); // true while fetching
  const [permission, setPermission] = useState('undetermined'); // 'granted' | 'denied' | 'undetermined'
  const subRef = useRef(null); // holds watch subscription so we can remove it
  const mounted = useRef(true); // avoid setState after unmount

  // Ask permission, return true/false
  const requestPermission = useCallback(async () => {
    const { status } = await Location.requestForegroundPermissionsAsync(); // shows OS dialog
    if (mounted.current) setPermission(status); // store result
    return status === 'granted';
  }, []);

  // One-time position fetch
  const refresh = useCallback(async () => {
    setLoading(true); setError(null); // reset state
    try {
      const ok = await requestPermission(); // permission first
      if (!ok) { if (mounted.current) setError('Location permission denied'); return; }
      const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced }); // GPS/network
      if (mounted.current) setCoords(pos.coords); // save
    } catch (e) {
      if (mounted.current) setError(e.message ?? 'Could not get location'); // e.g. GPS off
    } finally {
      if (mounted.current) setLoading(false); // always stop spinner
    }
  }, [requestPermission]);

  useEffect(() => {
    mounted.current = true;
    if (!watch) { refresh(); return () => { mounted.current = false; }; } // simple mode: fetch once
    (async () => { // live tracking mode (Swiggy delivery partner)
      const ok = await requestPermission();
      if (!ok) { setError('Location permission denied'); return; }
      subRef.current = await Location.watchPositionAsync(
        { accuracy: Location.Accuracy.High, timeInterval: 5000, distanceInterval: 10 }, // every 5s or 10m
        (pos) => mounted.current && setCoords(pos.coords) // update on each move
      );
      if (!mounted.current) subRef.current.remove(); // unmounted while awaiting
    })();
    return () => { mounted.current = false; subRef.current?.remove(); }; // cleanup: stop GPS updates
  }, [watch, refresh, requestPermission]);

  return { coords, error, loading, permission, refresh };
}
