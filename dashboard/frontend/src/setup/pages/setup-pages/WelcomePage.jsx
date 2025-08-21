// dashboard/setup/pages/setup-pages/WelcomePage.jsx
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const WelcomePage = ({ nextStep }) => {
  const [logoAnimated, setLogoAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLogoAnimated(true);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="welcome-page">
      <motion.div
        className="logo-container"
        initial={{ scale: 1.2, x: 0 }}
        animate={{ 
          scale: logoAnimated ? 0.7 : 1.2, 
          x: logoAnimated ? -400 : 0 
        }}
        transition={{ duration: 1, ease: "easeInOut" }}
      >
        <img 
          src="/dashboard/images/logo.png" 
          alt="Watch Tower Logo" 
          className="setup-logo"
        />
      </motion.div>

      <motion.div
        className="welcome-content"
        initial={{ opacity: 0, x: 100 }}
        animate={{ opacity: logoAnimated ? 1 : 0, x: logoAnimated ? 0 : 100 }}
        transition={{ duration: 0.8, delay: logoAnimated ? 0.5 : 0 }}
      >
        <div className="welcome-header">
          <h1 className="glowing-title">Welcome to Watch Tower</h1>
          <h2 className="subtitle">Vibe coded. Vibe Moddin'</h2>
        </div>

        <motion.div
          className="introduction"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: logoAnimated ? 1 : 0, y: logoAnimated ? 0 : 30 }}
          transition={{ duration: 0.6, delay: logoAnimated ? 1 : 0 }}
        >
          <p>
            Watch Tower is a comprehensive suite of Discord Moderation tools powered by AI analysis, 
            an extensive dashboard and its own Moderation Syntax ("ModStrings"). Your community is 
            one step closer to greatness and ready to conquer the world!
          </p>
          <p>
            As this appears to be your first time installing the bot, it's time to go through some 
            baller setup. You ready?
          </p>
        </motion.div>

        <motion.button
          className="hell-ya-button"
          onClick={nextStep}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ 
            opacity: logoAnimated ? 1 : 0, 
            scale: logoAnimated ? 1 : 0.8 
          }}
          transition={{ duration: 0.4, delay: logoAnimated ? 1.5 : 0 }}
          whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(59, 130, 246, 0.6)" }}
          whileTap={{ scale: 0.95 }}
        >
          Hell ya!
        </motion.button>
      </motion.div>
    </div>
  );
};

export default WelcomePage;