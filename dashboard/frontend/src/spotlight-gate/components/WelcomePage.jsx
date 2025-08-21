// dashboard/frontend/src/spotlight-gate/components/WelcomePage.jsx

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

{/* ==========================================
    WELCOME PAGE COMPONENT
   ========================================== */}

const WelcomePage = ({ nextStep, config }) => {
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowContent(true), 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="welcome-page">
      
      {/* Header */}
      <div className="page-header">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="logo-container"
        >
          <img 
            src="/images/logo.png" 
            alt="Server Logo" 
            className="welcome-logo"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        </motion.div>
        
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="welcome-header"
        >
          <h1 className="glowing-title">Welcome!</h1>
          <p className="subtitle">Let's get you verified and ready to join our community</p>
        </motion.div>
      </div>

      {/* Content */}
      <motion.div
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className={`welcome-content ${showContent ? 'show' : ''}`}
      >
        <div className="introduction">
          <p>
            🎉 <strong>Congratulations!</strong> You've been invited to join our awesome community. 
            Before you can start chatting and having fun, we need to make sure you're a real person 
            and that you understand our community guidelines.
          </p>
          
          <p>
            This quick verification process will take just a few minutes and includes:
          </p>
          
          <ul className="verification-steps">
            <li>📋 Reading our community rules</li>
            {config?.captcha_enabled && <li>🤖 Completing a security check</li>}
            <li>❓ Answering a few simple questions</li>
            <li>✅ Getting your verified role!</li>
          </ul>
          
          <p>
            <em>Don't worry - it's designed to be quick and easy for real humans!</em> 🚀
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={nextStep}
          className="hell-ya-button"
        >
          Hell Yeah, Let's Do This! 🔥
        </motion.button>
      </motion.div>

      {/* Floating Elements */}
      <div className="floating-elements">
        <motion.div
          animate={{ y: [-10, 10, -10] }}
          transition={{ duration: 3, repeat: Infinity }}
          className="floating-emoji"
          style={{ top: '20%', left: '10%' }}
        >
          🎊
        </motion.div>
        <motion.div
          animate={{ y: [10, -10, 10] }}
          transition={{ duration: 4, repeat: Infinity }}
          className="floating-emoji"
          style={{ top: '60%', right: '15%' }}
        >
          🚀
        </motion.div>
        <motion.div
          animate={{ y: [-15, 15, -15] }}
          transition={{ duration: 5, repeat: Infinity }}
          className="floating-emoji"
          style={{ bottom: '30%', left: '15%' }}
        >
          ⭐
        </motion.div>
      </div>
    </div>
  );
};

export default WelcomePage;