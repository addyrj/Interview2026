// ThemeContext.jsx — global light/dark/system theme with persistence
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'; // React + hooks
import { useColorScheme } from 'react-native'; // reads the phone's system theme (re-renders on change)
import AsyncStorage from '@react-native-async-storage/async-storage'; // small key-value storage

// Colour palettes (one object per theme)
export const lightColors = { background: '#ffffff', card: '#f4f4f5', text: '#111111', subtext: '#666666', primary: '#fc8019' };
export const darkColors = { background: '#121212', card: '#1e1e1e', text: '#f5f5f5', subtext: '#a1a1aa', primary: '#fc8019' };

const STORAGE_KEY = 'theme-mode'; // key used in AsyncStorage
const ThemeContext = createContext(null); // context object (null = used outside provider)

export function ThemeProvider({ children }) {
  const systemScheme = useColorScheme(); // 'light' | 'dark' | null (null can happen on some devices)
  const [mode, setMode] = useState('system'); // user choice: 'system' | 'light' | 'dark'
  const [ready, setReady] = useState(false); // becomes true after we read storage

  // Load saved choice once, when the app starts
  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY)
      .then((saved) => {
        if (saved === 'light' || saved === 'dark' || saved === 'system') setMode(saved); // accept only valid values
      })
      .catch(() => {}) // storage failure should never crash the app
      .finally(() => setReady(true)); // allow UI to render
  }, []);

  // Change mode + save it
  const changeMode = (next) => {
    setMode(next); // update UI instantly
    AsyncStorage.setItem(STORAGE_KEY, next).catch(() => {}); // save in background
  };

  // Which theme is really active right now?
  const effective = mode === 'system' ? systemScheme ?? 'light' : mode; // fall back to light
  const isDark = effective === 'dark'; // boolean for convenience

  // useMemo: new object only when something really changed (prevents extra re-renders)
  const value = useMemo(
    () => ({ mode, isDark, colors: isDark ? darkColors : lightColors, setMode: changeMode }),
    [mode, isDark]
  );

  if (!ready) return null; // avoid a light-flash before saved dark mode is loaded
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

// Custom hook so screens write: const { colors } = useTheme();
export function useTheme() {
  const ctx = useContext(ThemeContext); // read context
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>'); // helpful error
  return ctx;
}
