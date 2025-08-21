// dashboard/setup/pages/setup-pages/DisclaimerPage.jsx
import React from 'react';
import { motion } from 'framer-motion';

const DisclaimerPage = ({ nextStep, prevStep }) => {
  return (
    <div className="setup-page-content">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <img src="/dashboard/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </motion.div>

      <motion.div
        className="setup-content-area disclaimer-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="disclaimer-header">
          <div className="warning-icon">⚠️</div>
          <h2>Important Notice</h2>
        </div>

        <div className="disclaimer-text">
          <div className="disclaimer-card">
            <h3>🚧 Beta Software</h3>
            <p>
              Watch Tower is currently in beta and is <strong>vibe coded</strong>. While we've put 
              extensive effort into making it robust, you may encounter bugs or unexpected behavior. 
              Please report any issues you find!
            </p>
          </div>

          <div className="disclaimer-card">
            <h3>📊 Data & Privacy</h3>
            <p>
              Watch Tower processes Discord messages for moderation purposes. All data is stored 
              locally on your server and is never sent to external services except for AI analysis 
              through your configured Ollama instance.
            </p>
          </div>

          <div className="disclaimer-card">
            <h3>🛠️ Open Source</h3>
            <p>
              This project is hosted on GitHub and is completely open source. You can find the 
              repository link in the "About Bot" section of the dashboard. Contributions, bug 
              reports, and feature requests are welcome!
            </p>
          </div>

          <div className="disclaimer-card">
            <h3>💡 Getting Help</h3>
            <p>
              If you encounter issues or need help, check the GitHub repository for documentation, 
              known issues, and troubleshooting guides. The community is there to help!
            </p>
          </div>
        </div>

        <div className="disclaimer-footer">
          <p>
            By continuing, you acknowledge that you understand this software is in beta and 
            may have bugs or incomplete features.
          </p>
        </div>
      </motion.div>

      <div className="setup-navigation">
        <button onClick={prevStep} className="nav-button secondary">
          Back
        </button>
        <button onClick={nextStep} className="nav-button primary">
          I Understand, Continue
        </button>
      </div>
    </div>
  );
};

export default DisclaimerPage;