// dashboard/setup/pages/setup-pages/DomainConfigPage.jsx
import React from 'react';
import { motion } from 'framer-motion';

const DomainConfigPage = ({ data, updateData, nextStep, prevStep }) => {
  const handleDomainChange = (type) => {
    updateData('domain', type);
  };

  const handleCustomDomainChange = (domain) => {
    updateData('customDomain', domain);
  };

  const getExampleUrl = () => {
    if (data.domain === 'localhost') {
      return 'http://localhost:3000/dashboard';
    } else if (data.customDomain) {
      return `https://${data.customDomain}/dashboard`;
    } else {
      return 'https://your-domain.com/dashboard';
    }
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
        <h2>Domain Configuration</h2>
        <p className="section-description">
          Configure how you'll access the Watch Tower dashboard. This determines the URL 
          structure and accessibility of your moderation interface.
        </p>

        <div className="domain-options">
          <div 
            className={`domain-option ${data.domain === 'localhost' ? 'selected' : ''}`}
            onClick={() => handleDomainChange('localhost')}
          >
            <div className="option-header">
              <div className="option-icon">🏠</div>
              <h3>Localhost</h3>
              <div className="radio-indicator">
                <div className="radio-dot"></div>
              </div>
            </div>
            <p className="option-description">
              Access the dashboard locally on your server. Perfect for self-hosted setups 
              where you have direct access to the server.
            </p>
            <div className="option-details">
              <strong>Access URL:</strong> http://localhost:3000/dashboard<br/>
              <strong>Note:</strong> Others will need network access to your server
            </div>
          </div>

          <div 
            className={`domain-option ${data.domain === 'custom' ? 'selected' : ''}`}
            onClick={() => handleDomainChange('custom')}
          >
            <div className="option-header">
              <div className="option-icon">🌐</div>
              <h3>Custom Domain</h3>
              <div className="radio-indicator">
                <div className="radio-dot"></div>
              </div>
            </div>
            <p className="option-description">
              Use your own domain name for professional access. Requires proper DNS 
              configuration and SSL setup.
            </p>
            <div className="option-details">
              <strong>Example:</strong> https://bot.yourserver.com/dashboard<br/>
              <strong>Note:</strong> Requires domain setup and reverse proxy
            </div>
          </div>
        </div>

        {data.domain === 'custom' && (
          <motion.div
            className="custom-domain-input"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <label className="setting-label">Your Domain</label>
            <input
              type="text"
              value={data.customDomain}
              onChange={(e) => handleCustomDomainChange(e.target.value)}
              placeholder="bot.localdatahost.com"
              className="setting-input"
            />
            <div className="domain-preview">
              <strong>Dashboard URL:</strong> {getExampleUrl()}
            </div>
          </motion.div>
        )}

        <div className="domain-info">
          <h3>📋 Setup Requirements</h3>
          {data.domain === 'localhost' ? (
            <ul>
              <li>No additional setup required</li>
              <li>Dashboard accessible immediately</li>
              <li>Network access needed for remote users</li>
              <li>Consider VPN or SSH tunneling for remote access</li>
            </ul>
          ) : (
            <ul>
              <li>Domain name pointing to your server</li>
              <li>Reverse proxy (nginx/Apache) configuration</li>
              <li>SSL certificate for HTTPS</li>
              <li>Firewall rules allowing web traffic</li>
            </ul>
          )}
        </div>
      </motion.div>

      <div className="setup-navigation">
        <button onClick={prevStep} className="nav-button secondary">
          Back
        </button>
        <button 
          onClick={nextStep} 
          className="nav-button primary"
          disabled={data.domain === 'custom' && !data.customDomain}
        >
          Continue
        </button>
      </div>
    </div>
  );
};

export default DomainConfigPage;