// useCamera.js — hook around expo-camera (CameraView API, SDK 51+)
import { useCallback, useRef, useState } from 'react'; // hooks
import { useCameraPermissions } from 'expo-camera'; // permission hook from expo-camera

export default function useCamera() {
  const cameraRef = useRef(null); // attach to <CameraView ref={cameraRef} />
  const [permission, requestPermission] = useCameraPermissions(); // null until loaded
  const [facing, setFacing] = useState('back'); // 'back' | 'front'
  const [flash, setFlash] = useState('off'); // 'off' | 'on' | 'auto'
  const [photo, setPhoto] = useState(null); // { uri, width, height }
  const [busy, setBusy] = useState(false); // block double taps
  const [error, setError] = useState(null); // error text

  const toggleFacing = useCallback(() => setFacing((f) => (f === 'back' ? 'front' : 'back')), []); // flip camera
  const toggleFlash = useCallback(() => setFlash((f) => (f === 'off' ? 'on' : 'off')), []); // flash on/off

  const takePhoto = useCallback(async () => {
    if (!cameraRef.current || busy) return null; // not ready or already capturing
    setBusy(true); setError(null);
    try {
      const result = await cameraRef.current.takePictureAsync({ quality: 0.7 }); // compress a bit
      setPhoto(result); // keep for preview
      return result;
    } catch (e) {
      setError(e.message ?? 'Capture failed');
      return null;
    } finally {
      setBusy(false);
    }
  }, [busy]);

  const reset = useCallback(() => setPhoto(null), []); // "Retake"

  return {
    cameraRef, facing, flash, photo, busy, error,
    permission, requestPermission, // permission?.granted is the key flag
    toggleFacing, toggleFlash, takePhoto, reset,
  };
}
