// CartContext.jsx — cart state with a reducer (add / remove / clear)
import React, { createContext, useContext, useMemo, useReducer } from 'react'; // React + hooks

// Pure function: easy to unit test
export function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD': { // add one item
      const found = state[action.item.id]; // existing line?
      return { ...state, [action.item.id]: { item: action.item, qty: (found?.qty ?? 0) + 1 } };
    }
    case 'REMOVE': { // remove one item
      const found = state[action.id];
      if (!found) return state; // nothing to remove
      if (found.qty <= 1) { const { [action.id]: _gone, ...rest } = state; return rest; } // delete line at 0
      return { ...state, [action.id]: { ...found, qty: found.qty - 1 } };
    }
    case 'CLEAR': return {}; // empty cart
    default: return state;
  }
}

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [lines, dispatch] = useReducer(cartReducer, {}); // { id: {item, qty} }
  const value = useMemo(() => {
    const list = Object.values(lines); // array form for FlatList
    return {
      lines: list,
      count: list.reduce((n, l) => n + l.qty, 0), // total items
      total: list.reduce((s, l) => s + l.qty * l.item.price, 0), // total price
      qtyOf: (id) => lines[id]?.qty ?? 0,
      add: (item) => dispatch({ type: 'ADD', item }),
      remove: (id) => dispatch({ type: 'REMOVE', id }),
      clear: () => dispatch({ type: 'CLEAR' }),
    };
  }, [lines]);
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be inside <CartProvider>');
  return ctx;
};
