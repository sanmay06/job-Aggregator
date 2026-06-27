import React from 'react';
import './styles.css';

function FormInput({ type='text', value, onChange, placeholder, required }) {
  return (
    <input
      className="form-control"
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
    />
  );
}

export default FormInput;
