// Shopping cart: useReducer + context, add/remove/qty, derived totals, localStorage persistence
import { createContext, useContext, useReducer, useEffect, useMemo } from 'react'; // hooks
import { createRoot } from 'react-dom/client'; // root API

const PRODUCTS = [                                    // fake product catalog
  { id: 'p1', name: 'Wireless Mouse', price: 799 },
  { id: 'p2', name: 'USB-C Cable', price: 299 },
  { id: 'p3', name: 'Laptop Stand', price: 1499 },
];

// Pure reducer: all cart rules live here, easy to test
export function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD': {                                     // add item or bump quantity
      const found = state.items.find((i) => i.id === action.item.id);
      const items = found
        ? state.items.map((i) => (i.id === found.id ? { ...i, qty: i.qty + 1 } : i)) // new object
        : [...state.items, { ...action.item, qty: 1 }]; // new item with qty 1
      return { ...state, items };
    }
    case 'REMOVE':                                    // delete a line completely
      return { ...state, items: state.items.filter((i) => i.id !== action.id) };
    case 'SET_QTY': {                                 // change quantity, drop when 0 or less
      const qty = Math.max(0, Math.floor(action.qty)); // no negatives or decimals
      const items = state.items
        .map((i) => (i.id === action.id ? { ...i, qty } : i))
        .filter((i) => i.qty > 0);
      return { ...state, items };
    }
    case 'CLEAR':                                     // empty the cart
      return { ...state, items: [] };
    default:
      return state;                                   // unknown action: no change
  }
}

const CartContext = createContext(null);              // cart context

function loadInitial() {
  try {
    const raw = window.localStorage.getItem('cart');  // saved cart JSON
    return { items: raw ? JSON.parse(raw) : [] };
  } catch {
    return { items: [] };                             // bad JSON or no storage: start empty
  }
}

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, undefined, loadInitial); // lazy init
  useEffect(() => {
    window.localStorage.setItem('cart', JSON.stringify(state.items)); // persist each change
  }, [state.items]);

  const value = useMemo(() => {
    const count = state.items.reduce((n, i) => n + i.qty, 0);          // derived, not stored
    const total = state.items.reduce((n, i) => n + i.qty * i.price, 0); // derived, not stored
    return { items: state.items, count, total, dispatch };
  }, [state.items]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used inside <CartProvider>');
  return ctx;
}

const inr = (n) => `Rs ${n.toLocaleString('en-IN')}`; // simple price formatter

function ProductList() {
  const { dispatch } = useCart();
  return (
    <ul>
      {PRODUCTS.map((p) => (
        <li key={p.id}>
          {p.name} - {inr(p.price)}{' '}
          <button onClick={() => dispatch({ type: 'ADD', item: p })}>Add to cart</button>
        </li>
      ))}
    </ul>
  );
}

function Cart() {
  const { items, count, total, dispatch } = useCart();
  if (items.length === 0) return <p>Your cart is empty</p>; // empty state
  return (
    <section aria-label="Cart">
      <h2>Cart ({count})</h2>
      <ul>
        {items.map((i) => (
          <li key={i.id}>
            {i.name} x
            <input
              type="number" min="0" value={i.qty} aria-label={`Quantity of ${i.name}`}
              onChange={(e) => dispatch({ type: 'SET_QTY', id: i.id, qty: Number(e.target.value) || 0 })}
            />{' '}
            = {inr(i.qty * i.price)}{' '}
            <button onClick={() => dispatch({ type: 'REMOVE', id: i.id })}>Remove</button>
          </li>
        ))}
      </ul>
      <strong>Total: {inr(total)}</strong>{' '}
      <button onClick={() => dispatch({ type: 'CLEAR' })}>Clear</button>
    </section>
  );
}

export default function App() {
  return (
    <CartProvider>
      <h1>Amazon-style Shop</h1>
      <ProductList />
      <Cart />
    </CartProvider>
  );
}

const rootEl = typeof document !== 'undefined' && document.getElementById('root');
if (rootEl) createRoot(rootEl).render(<App />);
