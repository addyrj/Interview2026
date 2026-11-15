// useNetInfo.js — our own hook on top of @react-native-community/netinfo
import { useEffect, useState } from 'react'; // hooks
import NetInfo from '@react-native-community/netinfo'; // network library

export default function useNetInfo() {
  // Assume online until we learn otherwise (avoids a flash of "offline" banner)
  const [state, setState] = useState({ isConnected: true, isInternetReachable: true, type: 'unknown' });

  useEffect(() => {
    // addEventListener returns an unsubscribe function
    const unsubscribe = NetInfo.addEventListener((s) => {
      setState({
        isConnected: s.isConnected ?? false, // connected to wifi/cell?
        isInternetReachable: s.isInternetReachable ?? s.isConnected ?? false, // can really reach internet? (null = unknown)
        type: s.type, // 'wifi' | 'cellular' | 'none' | ...
      });
    });
    return unsubscribe; // cleanup on unmount
  }, []);

  // "Offline" only when we are sure
  const isOffline = state.isConnected === false || state.isInternetReachable === false;
  return { ...state, isOffline };
}
