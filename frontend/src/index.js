import React from 'react';
import ReactDom from 'react-dom/client'
import App from './App.jsx';
import { AuthProvider } from "./Authorize";

const root = ReactDom.createRoot(document.getElementById("root"));

root.render(
    <React.StrictMode>
        <AuthProvider>
            <App />
        </AuthProvider>
    </React.StrictMode>
)