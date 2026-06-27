import React from 'react';
import './styles.css';

function Toast({ type = 'info', children }) {
  return (
    <div className={`toast toast--${type}`} role="alert" aria-live="assertive">
      {children}
    </div>
  );
}

export default Toast;
