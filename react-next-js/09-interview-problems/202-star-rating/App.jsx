// Star rating: hover preview, click to set, keyboard support, readOnly mode
import { useState } from 'react'; // state hook
import { createRoot } from 'react-dom/client'; // root API

export function StarRating({ value = 0, onChange, max = 5, readOnly = false }) {
  const [hover, setHover] = useState(0);                 // star under the mouse (0 = none)
  const shown = hover || value;                          // hover preview wins over the saved value

  return (
    <div
      role="radiogroup"                                  // screen readers: choose one option
      aria-label="Rating"
      onMouseLeave={() => setHover(0)}                   // leaving the group clears preview
    >
      {Array.from({ length: max }, (_, i) => i + 1).map((star) => (
        <button
          key={star}
          type="button"                                  // never submit a surrounding form
          role="radio"
          aria-checked={value === star}                  // state for assistive tech
          aria-label={`${star} star${star > 1 ? 's' : ''}`}
          disabled={readOnly}
          onMouseEnter={() => !readOnly && setHover(star)} // preview on hover
          onClick={() => onChange?.(star === value ? 0 : star)} // click same star again = clear
          style={{
            background: 'none', border: 'none', fontSize: 28, cursor: readOnly ? 'default' : 'pointer',
            color: star <= shown ? '#f5a623' : '#ccc',   // filled vs empty colour
          }}
        >
          {star <= shown ? '★' : '☆'}
        </button>
      ))}
    </div>
  );
}

export default function App() {
  const [rating, setRating] = useState(0);               // parent owns the value (controlled)
  return (
    <div>
      <h2>Rate your Zomato order</h2>
      <StarRating value={rating} onChange={setRating} />
      <p>{rating ? `You rated ${rating}/5` : 'No rating yet'}</p>
      <StarRating value={4} readOnly />                  {/* display-only average rating */}
    </div>
  );
}

const rootEl = typeof document !== 'undefined' && document.getElementById('root');
if (rootEl) createRoot(rootEl).render(<App />);
