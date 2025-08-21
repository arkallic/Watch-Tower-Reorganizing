// dashboard/frontend/src/spotlight-gate/components/CaptchaPage.jsx

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

{/* ==========================================
    CAPTCHA PAGE COMPONENT
   ========================================== */}

const CaptchaPage = ({ 
  nextStep, 
  prevStep, 
  config, 
  captchaResponse, 
  setCaptchaResponse,
  captchaFails,
  setCaptchaFails
}) => {
  const [captchaLoaded, setCaptchaLoaded] = useState(false);
  const [loading, setLoading] = useState(true);
  const captchaRef = useRef(null);

  // Load reCAPTCHA script
  useEffect(() => {
    if (!config?.recaptcha_site_key) {
      setLoading(false);
      return;
    }

    const loadRecaptcha = () => {
      if (window.grecaptcha) {
        setCaptchaLoaded(true);
        setLoading(false);
        renderCaptcha();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://www.google.com/recaptcha/api.js';
      script.async = true;
      script.defer = true;
      script.onload = () => {
        setCaptchaLoaded(true);
        setLoading(false);
        setTimeout(renderCaptcha, 100);
      };
      document.head.appendChild(script);
    };

    loadRecaptcha();
  }, [config]);

  const renderCaptcha = () => {
    if (window.grecaptcha && captchaRef.current && config?.recaptcha_site_key) {
      try {
        window.grecaptcha.render(captchaRef.current, {
          sitekey: config.recaptcha_site_key,
          callback: handleCaptchaSuccess,
          'expired-callback': handleCaptchaExpired,
          'error-callback': handleCaptchaError,
          theme: 'dark',
          size: 'normal'
        });
      } catch (error) {
        console.error('reCAPTCHA render error:', error);
      }
    }
  };

  const handleCaptchaSuccess = (response) => {
    setCaptchaResponse(response);
  };

  const handleCaptchaExpired = () => {
    setCaptchaResponse(null);
    setCaptchaFails(prev => prev + 1);
  };

  const handleCaptchaError = () => {
    setCaptchaResponse(null);
    setCaptchaFails(prev => prev + 1);
  };

  const resetCaptcha = () => {
    if (window.grecaptcha) {
      window.grecaptcha.reset();
      setCaptchaResponse(null);
    }
  };

  return (
    <div className="captcha-page">
      
      {/* Header */}
      <div className="page-header">
        <div className="header-icon">🛡️</div>
        <div>
          <h2>Security Check</h2>
          <p>Help us verify that you're a real person, not a bot!</p>
        </div>
      </div>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="captcha-content"
      >
        
        {/* Security Info */}
        <div className="security-info">
          <div className="info-card">
            <div className="info-icon">🤖</div>
            <div>
              <h3>Why do we need this?</h3>
              <p>
                This security check helps us prevent automated bots and spam accounts 
                from joining our community. It only takes a few seconds!
              </p>
            </div>
          </div>
        </div>

        {/* reCAPTCHA Container */}
        <div className="captcha-container">
          {loading && (
            <div className="captcha-loading">
              <div className="loading-spinner"></div>
              <p>Loading security check...</p>
            </div>
          )}
          
          {!loading && !config?.recaptcha_site_key && (
            <div className="captcha-disabled">
              <div className="disabled-icon">✅</div>
              <p>Security check is currently disabled</p>
              <small>You can proceed to the next step</small>
            </div>
          )}
          
          {!loading && config?.recaptcha_site_key && (
            <div className="captcha-widget">
              <div ref={captchaRef}></div>
              
              {captchaFails > 0 && (
                <div className="captcha-fails">
                  <p>⚠️ Previous attempts: {captchaFails}</p>
                  <button onClick={resetCaptcha} className="reset-button">
                    Try Again
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Help Text */}
        <div className="help-text">
          <details>
            <summary>Having trouble with the security check?</summary>
            <div className="help-content">
              <ul>
                <li>Make sure JavaScript is enabled in your browser</li>
                <li>Try refreshing the page if the check doesn't load</li>
                <li>Some ad blockers may interfere with the security check</li>
                <li>If you continue having issues, contact a moderator for help</li>
              </ul>
            </div>
          </details>
        </div>
      </motion.div>

      {/* Navigation */}
      <div className="page-navigation">
        <button 
          onClick={prevStep} 
          className="nav-button secondary"
        >
          ← Back
        </button>
        
        <button 
          onClick={nextStep} 
          className="nav-button primary"
          disabled={config?.recaptcha_site_key && !captchaResponse}
        >
          Continue →
        </button>
      </div>
    </div>
  );
};

export default CaptchaPage;