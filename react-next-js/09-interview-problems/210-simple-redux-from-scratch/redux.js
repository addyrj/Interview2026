// Mini Redux from scratch: createStore, combineReducers, applyMiddleware, thunk, and a React hook
import { useSyncExternalStore } from 'react'; // React 18+ API for subscribing to external stores

export function createStore(reducer, preloadedState, enhancer) {
  if (typeof preloadedState === 'function' && enhancer === undefined) {
    enhancer = preloadedState;                               // createStore(reducer, enhancer)
    preloadedState = undefined;
  }
  if (enhancer) return enhancer(createStore)(reducer, preloadedState); // e.g. applyMiddleware

  let state = preloadedState;                                // the single state tree
  let listeners = [];                                        // subscribed callbacks

  const getState = () => state;                              // read current state

  const dispatch = (action) => {
    if (!action || typeof action.type === 'undefined') throw new Error('Action must have a type');
    state = reducer(state, action);                          // reducer returns the NEXT state
    listeners.slice().forEach((l) => l());                   // notify (copy: safe if one unsubscribes)
    return action;
  };

  const subscribe = (listener) => {
    listeners.push(listener);
    return () => { listeners = listeners.filter((l) => l !== listener); }; // unsubscribe fn
  };

  dispatch({ type: '@@INIT' });                              // fill initial state from reducers
  return { getState, dispatch, subscribe };
}

export function combineReducers(reducers) {
  const keys = Object.keys(reducers);
  return (state = {}, action) => {
    let changed = false;
    const next = {};
    for (const key of keys) {
      next[key] = reducers[key](state[key], action);         // each slice handles its own part
      if (next[key] !== state[key]) changed = true;
    }
    return changed ? next : state;                           // keep identity when nothing changed
  };
}

export function applyMiddleware(...middlewares) {
  return (createStoreFn) => (reducer, preloadedState) => {
    const store = createStoreFn(reducer, preloadedState);
    let dispatch = () => { throw new Error('Dispatching while constructing middleware'); };
    const api = { getState: store.getState, dispatch: (a) => dispatch(a) };
    const chain = middlewares.map((m) => m(api));            // give each middleware the api
    dispatch = chain.reduceRight((next, mw) => mw(next), store.dispatch); // compose right to left
    return { ...store, dispatch };
  };
}

// Thunk middleware: dispatch(fn) runs fn(dispatch, getState) for async logic
export const thunk = ({ dispatch, getState }) => (next) => (action) =>
  typeof action === 'function' ? action(dispatch, getState) : next(action);

// React binding: re-render only when the selected value changes
export function createHooks(store) {
  return {
    useSelector: (selector) =>
      useSyncExternalStore(store.subscribe, () => selector(store.getState())),
    useDispatch: () => store.dispatch,
  };
}
