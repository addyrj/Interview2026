// Signup form with validation: controlled inputs, validate on blur, errors after submit, a11y
import { useState } from 'react';

// Pure validator: returns an object of error messages (empty object = valid)
export function validate(v) {
  const e = {};
  if (!v.name.trim()) e.name = 'Name is required';
  if (!v.email.trim()) e.email = 'Email is required';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.email)) e.email = 'Enter a valid email';
  if (v.password.length < 8) e.password = 'Password must be at least 8 characters';
  else if (!/\d/.test(v.password)) e.password = 'Password needs at least one number';
  if (v.confirm !== v.password) e.confirm = 'Passwords do not match';
  return e;
}

export default function App() {
  const [values, setValues] = useState({ name: '', email: '', password: '', confirm: '' });
  const [touched, setTouched] = useState({});             // fields the user has left
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const errors = validate(values);                        // derived on every render, cheap
  const isValid = Object.keys(errors).length === 0;

  const onChange = (e) => setValues((v) => ({ ...v, [e.target.name]: e.target.value }));
  const onBlur = (e) => setTouched((t) => ({ ...t, [e.target.name]: true })); // show error after blur

  const onSubmit = async (e) => {
    e.preventDefault();
    setTouched({ name: true, email: true, password: true, confirm: true }); // reveal all errors
    if (!isValid) return;                                 // block invalid submit
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 500));         // pretend API call
    setSubmitting(false);
    setDone(true);
  };

  if (done) return <p role="status">Welcome, {values.name}!</p>;

  const field = (name, label, type = 'text') => (
    <p>
      <label>
        {label}{' '}
        <input
          name={name}
          type={type}
          value={values[name]}
          onChange={onChange}
          onBlur={onBlur}
          aria-invalid={Boolean(touched[name] && errors[name])}
          aria-describedby={`${name}-err`}
        />
      </label>
      <span id={`${name}-err`} role="alert" style={{ color: 'crimson', marginLeft: 8 }}>
        {touched[name] && errors[name]}
      </span>
    </p>
  );

  return (
    <form onSubmit={onSubmit} noValidate style={{ fontFamily: 'sans-serif' }}>
      <h1>Sign up</h1>
      {field('name', 'Name')}
      {field('email', 'Email', 'email')}
      {field('password', 'Password', 'password')}
      {field('confirm', 'Confirm password', 'password')}
      <button type="submit" disabled={submitting}>{submitting ? 'Saving...' : 'Create account'}</button>
    </form>
  );
}
