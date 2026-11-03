// Modal: portal, Escape to close, overlay click, focus trap, scroll lock, focus return
import { useState, useEffect, useRef, useId } from 'react';
import { createPortal } from 'react-dom';                // render outside the parent DOM tree

function Modal({ open, onClose, title, children }) {
  const dialogRef = useRef(null);                        // the dialog box element
  const lastFocused = useRef(null);                      // element to focus again on close
  const titleId = useId();                               // id for aria-labelledby
  const onCloseRef = useRef(onClose);                    // always the latest onClose
  onCloseRef.current = onClose;                          // so the effect need not depend on it

  useEffect(() => {
    if (!open) return;
    lastFocused.current = document.activeElement;        // remember who opened the modal
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';             // lock page scroll
    dialogRef.current?.focus();                          // move focus into the dialog

    const onKey = (e) => {
      if (e.key === 'Escape') { onCloseRef.current(); return; }     // Escape closes
      if (e.key !== 'Tab') return;
      const f = dialogRef.current.querySelectorAll(      // focusable elements inside
        'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (f.length === 0) { e.preventDefault(); return; }
      const first = f[0];
      const last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }  // wrap back
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); } // wrap forward
    };
    document.addEventListener('keydown', onKey);

    return () => {
      document.removeEventListener('keydown', onKey);    // cleanup listener
      document.body.style.overflow = prevOverflow;       // unlock scroll
      lastFocused.current?.focus?.();                    // return focus to the opener
    };
  }, [open]);                                            // re-run only when open changes

  if (!open) return null;                                // nothing rendered when closed

  return createPortal(
    <div
      onClick={onClose}                                  // click on the overlay closes
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.5)', display: 'grid', placeItems: 'center' }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}                                    // focusable by script
        onClick={(e) => e.stopPropagation()}             // clicks inside must not close
        style={{ background: '#fff', padding: 24, borderRadius: 8, minWidth: 280 }}
      >
        <h2 id={titleId}>{title}</h2>
        {children}
        <button onClick={onClose}>Close</button>
      </div>
    </div>,
    document.body                                        // mounted directly in body
  );
}

export default function App() {
  const [open, setOpen] = useState(false);               // modal visibility
  return (
    <div style={{ fontFamily: 'sans-serif' }}>
      <button onClick={() => setOpen(true)}>Delete account</button>
      <Modal open={open} onClose={() => setOpen(false)} title="Are you sure?">
        <p>This action cannot be undone.</p>
        <button onClick={() => setOpen(false)}>Confirm</button>
      </Modal>
    </div>
  );
}
