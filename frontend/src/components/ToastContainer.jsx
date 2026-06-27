import React, { useState, useEffect } from 'react';
import Toast from './Toast';
import './styles.css';

// Simple toast manager – you can extend with context or external store
function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  // Example: expose a global function to push toasts (for demo purposes)
  useEffect(() => {
    window.showToast = (msg, type = 'info', duration = 3500) => {
      const id = Date.now();
      setToasts(prev => [...prev, { id, msg, type }]);
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, duration);
    };
    return () => {
      delete window.showToast;
    };
  }, []);

  return (
    <div className="toast-container">
      {toasts.map(t => (
        <Toast key={t.id} type={t.type}>
          {t.msg}
        </Toast>
      ))}
    </div>
  );
}

export default ToastContainer;
