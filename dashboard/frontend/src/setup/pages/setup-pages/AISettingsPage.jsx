// dashboard/setup/pages/setup-pages/AISettingsPage.jsx
import React, { useState } from 'react';
import { motion } from 'framer-motion';

const AISettingsPage = ({ data, updateData, nextStep, prevStep }) => {
  const [channels, setChannels] = useState([]);
  const [showPromptExample, setShowPromptExample] = useState(false);

  const handleChange = (field, value) => {
    updateData('aiMonitoring', { [field]: value });
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
        <h2>AI Configuration</h2>
        <p className="section-description">
          Configure the AI analysis system that powers Watch Tower's intelligent moderation. 
          The AI model requires llama3.1 to be installed on your Ollama instance.
        </p>

        <div className="settings-grid">
          <div className="setting-item">
            <label className="setting-label">Ollama Endpoint</label>
            <input
              type="url"
              value={data.aiMonitoring.ollamaEndpoint}
              onChange={(e) => handleChange('ollamaEndpoint', e.target.value)}
              className="setting-input"
              placeholder="http://127.0.0.1:11434"
            />
            <p className="setting-description">
              The URL of your Ollama instance. Make sure llama3.1 model is installed 
              and accessible at this endpoint.
            </p>
          </div>

          <div className="setting-item">
            <label className="setting-label">Monitoring Scope</label>
            <select
              value={data.aiMonitoring.monitoringScope}
              onChange={(e) => handleChange('monitoringScope', e.target.value)}
              className="setting-select"
            >
              <option value="ALL">Monitor All Channels</option>
              <option value="SELECTED">Monitor Selected Channels Only</option>
              <option value="EXCLUDE">Monitor All Except Selected</option>
            </select>
            <p className="setting-description">
              Choose which channels the AI should monitor for problematic content.
            </p>
          </div>

          <div className="setting-item">
            <label className="setting-label">Flag Threshold (1-10)</label>
            <div className="threshold-container">
              <input
                type="range"
                min="1"
                max="10"
                value={data.aiMonitoring.flagThreshold}
                onChange={(e) => handleChange('flagThreshold', parseInt(e.target.value))}
                className="threshold-slider"
              />
              <span className="threshold-value">{data.aiMonitoring.flagThreshold}</span>
            </div>
            <p className="setting-description">
              Sensitivity for AI flagging. Higher values are more sensitive and may 
              produce more false positives.
            </p>
          </div>

          <div className="setting-item full-width">
            <label className="setting-label">
              Custom AI Prompt
              <button
                type="button"
                onClick={() => setShowPromptExample(!showPromptExample)}
                className="info-button"
              >
                {showPromptExample ? 'Hide' : 'Show'} Example
              </button>
            </label>
            <textarea
              value={data.aiMonitoring.customPrompt}
              onChange={(e) => handleChange('customPrompt', e.target.value)}
              className="setting-textarea"
              rows="8"
              placeholder="Enter your custom AI prompt..."
            />
            <p className="setting-description">
              This prompt tells the AI how to analyze messages. The example prompt was 
              designed for a psychosis support group but can be adapted for any community. 
              <strong>Important:</strong> The prompt must end with 'Message to analyze: "[Message here]"'
            </p>
            
            {showPromptExample && (
              <motion.div
                className="prompt-example"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <h4>Example Prompt:</h4>
                <pre className="example-prompt">
                  {data.aiMonitoring.customPrompt}
                </pre>
              </motion.div>
            )}
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

export default AISettingsPage;