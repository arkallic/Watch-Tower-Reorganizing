import React, { useState } from 'react';
import { motion } from 'framer-motion';

const FinalPage = ({ data, onComplete }) => {
  const [isCompleting, setIsCompleting] = useState(false);

  const completeSetup = async () => {
    setIsCompleting(true);
    
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      const response = await fetch(`${apiBase}/api/pagedata/setup-complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        if (onComplete) {
            onComplete();
        }
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);
      } else {
        throw new Error('Setup completion failed on the backend.');
      }
    } catch (error) {
      console.error('Setup completion error:', error);
      alert(`An error occurred while finalizing setup: ${error.message}`);
      setIsCompleting(false);
    }
  };

  const getDashboardUrl = () => {
    if (data.domain === 'localhost') {
      return 'http://localhost:3000/dashboard';
    } else {
      return `https://${data.customDomain}/dashboard`;
    }
  };

  return (
    <div className="setup-page-content final-page">
      <motion.div
        className="congratulations-header"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8 }}
      >
        <div className="celebration-icon">🎉</div>
        <h1 className="congrats-title">Congratulations!</h1>
        <h2 className="congrats-subtitle">Watch Tower Setup Complete</h2>
      </motion.div>

      <motion.div
        className="setup-summary"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="summary-grid">
          <div className="summary-card">
            <h3>🔧 Core Settings</h3>
            <ul>
              <li>Bot Enabled: {data.coreSettings.enableBot ? 'Yes' : 'No'}</li>
              <li>Time Window: {data.coreSettings.timeWindow} hours</li>
              <li>Messages Per Case: {data.coreSettings.messagesPerCase}</li>
            </ul>
          </div>

          <div className="summary-card">
            <h3>📢 Channels</h3>
            <ul>
              <li>Report Channel: {data.channels.reportChannel ? '✓' : '✗'}</li>
              <li>Mod Actions: {data.channels.modActionReportChannel ? '✓' : '✗'}</li>
              <li>Mod Chat: {data.channels.modChatChannel ? '✓' : '✗'}</li>
            </ul>
          </div>

          <div className="summary-card">
            <h3>🤖 AI Monitoring</h3>
            <ul>
              <li>AI Enabled: {data.aiMonitoring.enabled ? 'Yes' : 'No'}</li>
              <li>Flag Threshold: {data.aiMonitoring.flagThreshold}/10</li>
              <li>Custom Prompt: {data.aiMonitoring.customPrompt ? 'Yes' : 'Default'}</li>
            </ul>
          </div>

          <div className="summary-card">
            <h3>⚡ ModStrings</h3>
            <ul>
              <li>Enabled: {data.modStrings.enabled ? 'Yes' : 'No'}</li>
              <li>Scope: {data.modStrings.scopeConfig}</li>
            </ul>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="tips-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <h3>💡 Pro Tips for Getting Started</h3>
        <div className="tips-grid">
          <div className="tip-card">
            <div className="tip-icon">📊</div>
            <h4>Dashboard</h4>
            <p>Monitor your server's health and moderation statistics at: 
              <a href={getDashboardUrl()} target="_blank" rel="noopener noreferrer">
                {getDashboardUrl()}
              </a>
            </p>
          </div>

          <div className="tip-card">
            <div className="tip-icon">⚙️</div>
            <h4>Settings</h4>
            <p>Fine-tune your configuration anytime in the dashboard settings. 
            All changes {data.approvalUser ? 'require approval' : 'take effect immediately'}.</p>
          </div>

          <div className="tip-card">
            <div className="tip-icon">📚</div>
            <h4>ModStrings</h4>
            <p>Create powerful automation rules using our custom ModString syntax. 
            Check the documentation for advanced patterns and examples.</p>
          </div>

          <div className="tip-card">
            <div className="tip-icon">🚀</div>
            <h4>GitHub</h4>
            <p>This project is open source! Find updates, report issues, and contribute at the 
            GitHub repository linked in the "About Bot" section.</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        className="completion-actions"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.9 }}
      >
        <button
          onClick={completeSetup}
          disabled={isCompleting}
          className="complete-button"
        >
          {isCompleting ? (
            <>
              <div className="spinner"></div>
              Finalizing Setup...
            </>
          ) : (
            'Go to Dashboard'
          )}
        </button>
        
        <p className="completion-note">
          Your Watch Tower bot is now ready to protect your community! 
          {data.coreSettings.enableBot && ' It will start monitoring immediately.'}
        </p>
      </motion.div>
    </div>
  );
};

export default FinalPage;