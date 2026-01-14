/**
 * Main Entry Point
 * Renders the React application
 * 
 * @author Indian Law RAG Chatbot Project
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// Global styles
import './index.css';

// Render application
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
