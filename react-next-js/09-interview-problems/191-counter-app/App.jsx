// Counter App: increment, decrement, reset, custom step, min/max limits
import { useState } from 'react';                       // useState holds the count

const MIN = -10;                                         // lower limit of the counter
const MAX = 10;                                          // upper limit of the counter

export default function App() {
  const [count, setCount] = useState(0);                 // current count, starts at 0
  const [step, setStep] = useState(1);                   // how much one click changes

  // Functional updates: always based on the latest state, safe for batched updates
  const increment = () => setCount((c) => Math.min(MAX, c + step)); // never go above MAX
  const decrement = () => setCount((c) => Math.max(MIN, c - step)); // never go below MIN
  const reset = () => setCount(0);                       // back to the start

  return (
    <div style={{ fontFamily: 'sans-serif', textAlign: 'center' }}>
      <h1 data-testid="count">{count}</h1>               {/* current value */}
      <button onClick={decrement} disabled={count <= MIN}>-</button> {/* disabled at MIN */}
      <button onClick={reset}>Reset</button>             {/* reset to 0 */}
      <button onClick={increment} disabled={count >= MAX}>+</button> {/* disabled at MAX */}
      <p>
        <label>
          Step:{' '}
          <input
            type="number"
            min="1"
            value={step}                                 // controlled input
            onChange={(e) => setStep(Math.max(1, Number(e.target.value) || 1))} // keep step >= 1
          />
        </label>
      </p>
    </div>
  );
}
