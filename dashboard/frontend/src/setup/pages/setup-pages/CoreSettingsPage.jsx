// dashboard/setup/pages/setup-pages/CoreSettingsPage.jsx
import React from 'react';
import { motion } from 'framer-motion';

const CoreSettingsPage = ({ data, updateData, nextStep, prevStep }) => {
  const handleChange = (field, value) => {
    updateData('coreSettings', { [field]: value });
  };

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
        className="setup-content-area"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <h2>First some basic settings. Let's vibe it up, homie</h2>
        <p className="section-description">
          Core settings control the fundamental behavior of Watch Tower. These settings determine 
          how the bot processes messages, creates cases, and manages moderation data.
        </p>

        <div className="settings-grid">
          <div className="setting-item">
            <label className="setting-label">
              <input
                type="checkbox"
                checked={data.coreSettings.enableBot}
                onChange={(e) => handleChange('enableBot', e.target.checked)}
                className="setting-checkbox"
              />
              <span className="checkmark"></span>
              Enable Bot After Setup
            </label>
            <p className="setting-description">
              If enabled, the bot will start monitoring immediately after setup. 
              If disabled, you can enable it later in the dashboard settings.
            </p>
          </div>

          <div className="setting-item">
            <label className="setting-label">Time Window (Hours)</label>
            <input
              type="number"
              min="1"
              max="168"
              value={data.coreSettings.timeWindow}
              onChange={(e) => handleChange('timeWindow', parseInt(e.target.value))}
              className="setting-input"
            />
            <p className="setting-description">
              How many hours of message history to analyze for patterns and context. 
              Longer windows provide better context but use more resources.
            </p>
          </div>

          <div className="setting-item">
            <label className="setting-label">Messages Per Case</label>
            <input
              type="number"
              min="5"
              max="50"
              value={data.coreSettings.messagesPerCase}
              onChange={(e) => handleChange('messagesPerCase', parseInt(e.target.value))}
              className="setting-input"
            />
            <p className="setting-description">
              Number of recent messages to preserve with each moderation case. 
              These provide context for moderators when reviewing incidents.
            </p>
          </div>
        </div>
      </motion.div>

      <div className="setup-navigation">
        <button onClick={prevStep} className="nav-button secondary">
          Back
        </button>
        <button onClick={nextStep} className="nav-button primary">
          Continue
        </button>
      </div>
    </div>
  );
};

export default CoreSettingsPage;