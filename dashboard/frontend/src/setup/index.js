// dashboard/setup/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import FirstTimeSetup from './pages/FirstTimeSetup';
import './pages/FirstTimeSetup.css';

// Check if this is first time setup
const checkFirstTimeSetup = async () => {
  try {
    const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const response = await fetch(isDevelopment ? 'http://localhost:8001/setup/check' : '/bot-api/setup/check');
    const data = await response.json();
    return data.isFirstTime;
  } catch (error) {
    console.error('Failed to check setup status:', error);
    return false;
  }
};

// Initialize setup if needed
const initializeSetup = async () => {
 const isFirstTime = await checkFirstTimeSetup();
 
 if (isFirstTime) {
   // Show first time setup
   const root = ReactDOM.createRoot(document.getElementById('root'));
   root.render(<FirstTimeSetup />);
 } else {
   // Redirect to normal dashboard
   window.location.href = '/dashboard';
 }
};

// Start the setup check
initializeSetup();