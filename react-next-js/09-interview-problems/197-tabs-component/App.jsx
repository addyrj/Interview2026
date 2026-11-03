// Tabs: compound components + keyboard navigation (Arrow keys, Home, End), ARIA roles
import { createContext, useContext, useState, useId, useRef } from 'react';

const TabsContext = createContext(null);                 // shared state of one Tabs group

function Tabs({ defaultValue, children }) {
  const [active, setActive] = useState(defaultValue);    // selected tab value
  const baseId = useId();                                // id prefix for aria links
  return (
    <TabsContext.Provider value={{ active, setActive, baseId }}>
      {children}
    </TabsContext.Provider>
  );
}

function TabList({ children }) {
  const ref = useRef(null);
  const onKeyDown = (e) => {
    const tabs = [...ref.current.querySelectorAll('[role="tab"]')]; // all tab buttons
    const i = tabs.indexOf(document.activeElement);      // focused tab index
    if (i === -1) return;
    let next = null;
    if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];            // next, wrap
    if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length]; // previous, wrap
    if (e.key === 'Home') next = tabs[0];
    if (e.key === 'End') next = tabs[tabs.length - 1];
    if (next) { e.preventDefault(); next.focus(); next.click(); } // move focus and select
  };
  return <div role="tablist" ref={ref} onKeyDown={onKeyDown}>{children}</div>;
}

function Tab({ value, children }) {
  const { active, setActive, baseId } = useContext(TabsContext);
  const selected = active === value;
  return (
    <button
      role="tab"
      id={`${baseId}-tab-${value}`}
      aria-selected={selected}
      aria-controls={`${baseId}-panel-${value}`}
      tabIndex={selected ? 0 : -1}                       // roving tabindex: only active is tabbable
      onClick={() => setActive(value)}
      style={{ fontWeight: selected ? 'bold' : 'normal' }}
    >
      {children}
    </button>
  );
}

function TabPanel({ value, children }) {
  const { active, baseId } = useContext(TabsContext);
  if (active !== value) return null;                     // render only the active panel
  return (
    <div role="tabpanel" id={`${baseId}-panel-${value}`} aria-labelledby={`${baseId}-tab-${value}`}>
      {children}
    </div>
  );
}

Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

export default function App() {
  return (
    <Tabs defaultValue="menu">
      <Tabs.List>
        <Tabs.Tab value="menu">Menu</Tabs.Tab>
        <Tabs.Tab value="reviews">Reviews</Tabs.Tab>
        <Tabs.Tab value="info">Info</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel value="menu"><p>Biryani, Dosa, Paneer Tikka</p></Tabs.Panel>
      <Tabs.Panel value="reviews"><p>4.5 stars from 2,300 reviews</p></Tabs.Panel>
      <Tabs.Panel value="info"><p>Open 10am to 11pm</p></Tabs.Panel>
    </Tabs>
  );
}
