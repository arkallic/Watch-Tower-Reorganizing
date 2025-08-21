// dashboard/frontend/src/spotlight-gate/components/RulesPage.jsx

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

const RulesPage = ({ nextStep, prevStep, config }) => {
  const [hasScrolled, setHasScrolled] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const scrollAreaRef = useRef(null);

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
    
    // Enable checkbox when user scrolls to 90% or if content is short enough
    if (scrollPercentage >= 90 || scrollHeight <= clientHeight + 10) {
      setHasScrolled(true);
    }
  };

  // Check if content is short enough on mount
  useEffect(() => {
    if (scrollAreaRef.current) {
      const { scrollHeight, clientHeight } = scrollAreaRef.current;
      if (scrollHeight <= clientHeight + 10) {
        setHasScrolled(true);
      }
    }
  }, [config]);

  return (
    <div className="rules-page">
      {/* Header */}
      <div className="page-header">
        <div className="header-icon">📋</div>
        <div>
          <h2>Community Rules & Guidelines</h2>
          <p>Please read our rules carefully - you'll be quizzed on them!</p>
        </div>
      </div>

      {/* Rules Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="rules-content"
      >
        <div 
          ref={scrollAreaRef}
          className="rules-scroll-area"
          onScroll={handleScroll}
        >
          {config?.rules ? (
            <ReactMarkdown className="markdown-content">
              {config.rules}
            </ReactMarkdown>
          ) : (
            <div className="default-rules">
              <h3>📋 Community Guidelines</h3>
              <p>Welcome to our community! Please follow these simple rules:</p>
              
              <div className="rule-section">
                <h4>🤝 Be Respectful</h4>
                <p>Treat all members with kindness and respect. We're all here to have a good time!</p>
              </div>
              
              <div className="rule-section">
                <h4>🚫 No Spam or Self-Promotion</h4>
                <p>Keep discussions relevant and avoid excessive self-promotion.</p>
              </div>
              
              <div className="rule-section">
                <h4>🔞 Keep It Family-Friendly</h4>
                <p>No NSFW content - keep all content appropriate for all ages.</p>
              </div>
              
              <div className="rule-section">
                <h4>📍 Use Appropriate Channels</h4>
                <p>Post content in the right places to keep things organized.</p>
              </div>
              
              <div className="rule-section">
                <h4>⚖️ Follow Discord ToS</h4>
                <p>All Discord Terms of Service apply here as well.</p>
              </div>

              {/* Add more content to make it scrollable */}
              <div className="rule-section">
                <h4>💬 Communication Guidelines</h4>
                <p>Use clear, respectful language. Avoid excessive caps lock or spam.</p>
              </div>

              <div className="rule-section">
                <h4>🎮 Gaming Etiquette</h4>
                <p>Be a good sport whether winning or losing. Help newcomers learn.</p>
              </div>

              <div className="rule-section">
                <h4>🔗 Link Sharing</h4>
                <p>Only share links that are relevant and safe. No suspicious downloads.</p>
              </div>

              <div className="rule-section">
                <h4>⚠️ Reporting Issues</h4>
                <p>If you see rule violations, report them to moderators instead of engaging.</p>
              </div>

              <div className="rule-section">
                <h4>✅ Final Notes</h4>
                <p>Thank you for taking the time to read these rules. Following them helps keep our community welcoming and fun for everyone!</p>
              </div>
            </div>
          )}
        </div>
        
        {!hasScrolled && (
          <div className="scroll-indicator">
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="scroll-arrow"
            >
              ↓ Scroll to read all rules ↓
            </motion.div>
          </div>
        )}
      </motion.div>

      {/* Agreement Checkbox */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: hasScrolled ? 1 : 0.3 }}
        className="agreement-section"
      >
        <label className="agreement-checkbox">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            disabled={!hasScrolled}
          />
          <span className="checkmark"></span>
          <span className="agreement-text">
            I have read and agree to follow these community rules and guidelines
          </span>
        </label>
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
          disabled={!hasScrolled || !agreed}
        >
          I Understand → 
        </button>
      </div>
    </div>
  );
};

export default RulesPage;