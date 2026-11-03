// Dark mode toggle: context + localStorage + system preference + data-theme attribute
import { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react'; // React hooks
import { createRoot } from 'react-dom/client'; // React 18/19 root API

const STORAGE_KEY = 'theme';                  // localStorage key
const ThemeContext = createContext(null);     // shared theme state

// Read the first theme: saved choice wins, otherwise the OS preference
function getInitialTheme() {
  if (typeof window === 'undefined') return 'light';          // server/no DOM: safe default
  const saved = window.localStorage.getItem(STORAGE_KEY);     // user's earlier choice
  if (saved === 'light' || saved === 'dark') return saved;    // trust only valid values
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; // OS setting
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getInitialTheme);        // lazy init: runs once

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme); // CSS reads [data-theme="dark"]
    window.localStorage.setItem(STORAGE_KEY, theme);            // remember the choice
  }, [theme]);                                                  // runs only when theme changes

  const toggle = useCallback(() => setTheme((t) => (t === 'dark' ? 'light' : 'dark')), []); // stable fn
  const value = useMemo(() => ({ theme, toggle }), [theme, toggle]); // stable context value

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);                          // read nearest provider
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>'); // misuse guard
  return ctx;
}

export function ThemeToggle() {
  const { theme, toggle } = useTheme();                          // read + update theme
  return (
    <button onClick={toggle} aria-pressed={theme === 'dark'} aria-label="Toggle dark mode">
      {theme === 'dark' ? 'Switch to light' : 'Switch to dark'}
    </button>
  );
}

const css = `
  :root { --bg: #ffffff; --fg: #111111; }                        /* light tokens */
  [data-theme="dark"] { --bg: #121212; --fg: #f5f5f5; }          /* dark tokens */
  body { background: var(--bg); color: var(--fg); transition: background .2s; }
`;

export default function App() {
  return (
    <ThemeProvider>
      <style>{css}</style>
      <h1>Swiggy Settings</h1>
      <ThemeToggle />
    </ThemeProvider>
  );
}

// Mount only when a #root element exists (keeps the file importable in tests)
const rootEl = typeof document !== 'undefined' && document.getElementById('root');
if (rootEl) createRoot(rootEl).render(<App />);
