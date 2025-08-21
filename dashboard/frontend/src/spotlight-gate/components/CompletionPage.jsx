// dashboard/frontend/src/spotlight-gate/components/CompletionPage.jsx

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

{/* ==========================================
    COMPLETION PAGE COMPONENT
   ========================================== */}

const CompletionPage = ({ config, answers, submitting, userId, onSubmit }) => {
  const [result, setResult] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [displayResult, setDisplayResult] = useState(null);
  const [processingComplete, setProcessingComplete] = useState(false);

  // Check if this is test mode
  const isTestMode = config?.test_mode || false;

  {/* ==========================================
      CALCULATE RESULTS
     ========================================== */}
  
    useEffect(() => {
    if (!config || !answers || submitting) return;

    // Calculate verification results
    const questions = config.questions || [];
    const passingScore = config.passing_score || 3;
    
    let correctAnswers = 0;
    const failedQuestions = [];
    
    questions.forEach(question => {
      if (answers[question.id] === question.correct_answer) {
        correctAnswers++;
      } else if (answers[question.id]) {
        failedQuestions.push(question.text);
      }
    });

    const passed = correctAnswers >= passingScore;
    
    const calculatedResult = {
      passed,
      score: correctAnswers,
      total: questions.length,
      required: passingScore,
      failed_questions: failedQuestions,
      test_mode: isTestMode
    };

    setResult(calculatedResult);

    // Show confetti for successful verification
    if (passed) {
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);
    }

    // Simulate processing delay for dramatic effect
    if (!processingComplete) {
      setTimeout(() => {
        setProcessingComplete(true);
        setDisplayResult(calculatedResult);
      }, 2000);
    } else {
      setDisplayResult(calculatedResult);
    }
  }, [config, answers, submitting, processingComplete, isTestMode]);

  {/* ==========================================
      PROCESSING STATE
     ========================================== */}
  
  if (submitting || !processingComplete) {
    return (
      <div className="completion-page">
        <div className="processing-content">
          <div className="processing-animation">
            <div className="processing-spinner"></div>
            <div className="processing-circles">
              <div className="circle"></div>
              <div className="circle"></div>
              <div className="circle"></div>
            </div>
          </div>
          <h2>Processing Your Verification...</h2>
          <p>Please wait while we review your answers and run security checks.</p>
          <div className="processing-steps">
            <div className="step completed">✓ Checking your answers</div>
            <div className="step processing">⏳ Running security verification</div>
            <div className="step pending">⏱️ Finalizing verification</div>
          </div>
          {isTestMode && (
            <div className="test-mode-indicator">
              <p className="text-yellow-400 text-sm mt-4">
                🧪 Test Mode: Simulating verification process
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  {/* ==========================================
      LOADING FALLBACK
     ========================================== */}
  
  if (!displayResult) {
    return (
      <div className="completion-page">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading results...</p>
        </div>
      </div>
    );
  }

  {/* ==========================================
      MAIN COMPLETION CONTENT
     ========================================== */}
  
  return (
    <div className="completion-page">
      
      {/* Confetti Effect */}
      {showConfetti && (
        <div className="confetti-container">
          {[...Array(50)].map((_, i) => (
            <div 
              key={i} 
              className="confetti"
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                backgroundColor: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'][Math.floor(Math.random() * 5)]
              }}
            />
          ))}
        </div>
      )}

      <div className="completion-content">
        
        {/* ==========================================
            SUCCESS CASE
           ========================================== */}
        
        {displayResult.passed && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="success-content"
          >
            <div className="celebration-header">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="celebration-icon"
              >
                🎉
              </motion.div>
              <h1 className="success-title">
                {isTestMode ? 'Test Verification Complete!' : 'Verification Complete!'}
              </h1>
              <p className="success-subtitle">
                {isTestMode ? 'Preview: Welcome to the community!' : 'Welcome to the community!'}
              </p>
            </div>

            <div className="success-details">
              <div className="score-display">
                <div className="score-circle">
                  <span className="score-text">{displayResult.score}/{displayResult.total}</span>
                  <span className="score-label">Correct</span>
                </div>
              </div>

              <div className="success-message">
                <p>
                  🎊 <strong>Congratulations!</strong> You've successfully completed the verification process. 
                  You answered {displayResult.score} out of {displayResult.total} questions correctly, which {isTestMode ? 'would exceed' : 'exceeds'} 
                  our requirement of {displayResult.required} correct answers.
                </p>
                
                <div className="next-steps">
                  <h3>What happens next?</h3>
                  <ul>
                    <li>✅ {isTestMode ? 'You would receive' : 'You\'ll receive'} the verified member role automatically</li>
                    <li>🔓 You {isTestMode ? 'would have' : 'now have'} access to all server channels</li>
                    <li>💬 You can start chatting and participating in the community</li>
                    <li>📋 {isTestMode ? 'Your test session' : 'Your verification channel'} will be {isTestMode ? 'closed' : 'deleted'} shortly</li>
                  </ul>
                </div>

                <div className="welcome-note">
                  <p>
                    <strong>{isTestMode ? 'In a real scenario:' : 'Welcome aboard!'}</strong> {isTestMode ? 'The user would be' : 'We\'re'} excited to have {isTestMode ? 'them' : 'you'} as part of our community. 
                    {isTestMode ? 'They would be able to' : 'Feel free to'} introduce {isTestMode ? 'themselves' : 'yourself'} and start exploring!
                  </p>
                </div>

                {isTestMode && (
                  <div className="test-mode-notice">
                    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mt-4">
                      <h4 className="text-yellow-400 font-semibold mb-2">🧪 Test Mode Results</h4>
                      <p className="text-yellow-300 text-sm">
                        This is a preview of what users would see when they pass verification. 
                        No actual Discord roles or permissions have been modified.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => window.close()}
              className="close-button success"
            >
              {isTestMode ? 'Close Test Preview 🧪' : 'Close Window & Start Chatting! 🚀'}
            </motion.button>
          </motion.div>
        )}

        {/* ==========================================
            PENDING REVIEW CASE
           ========================================== */}
        
        {!displayResult.passed && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="pending-content"
          >
            <div className="pending-header">
              <div className="pending-icon">⏳</div>
              <h1 className="pending-title">
                {isTestMode ? 'Test Verification Submitted' : 'Verification Submitted'}
              </h1>
              <p className="pending-subtitle">
                {isTestMode ? 'Preview: Submission under review' : 'Your submission is under review'}
              </p>
            </div>

            <div className="pending-details">
              <div className="score-display pending">
                <div className="score-circle">
                  <span className="score-text">{displayResult.score}/{displayResult.total}</span>
                  <span className="score-label">Correct</span>
                </div>
                <div className="score-status">
                  <span className="required-text">Required: {displayResult.required}</span>
                </div>
              </div>

              <div className="pending-message">
                <p>
                  📋 {isTestMode ? 'In a real scenario, their' : 'Your'} verification {isTestMode ? 'would be' : 'has been'} submitted for manual review. 
                  {isTestMode ? 'They' : 'You'} answered {displayResult.score} out of {displayResult.total} questions correctly, 
                  which is below our automatic approval threshold of {displayResult.required} correct answers.
                </p>
                
                {displayResult.failed_questions && displayResult.failed_questions.length > 0 && (
                  <div className="failed-questions">
                    <h4>Questions that need review:</h4>
                    <ul>
                      {displayResult.failed_questions.slice(0, 3).map((question, index) => (
                        <li key={index} className="text-red-400 text-sm">• {question}</li>
                      ))}
                      {displayResult.failed_questions.length > 3 && (
                        <li className="text-red-400 text-sm">• And {displayResult.failed_questions.length - 3} more...</li>
                      )}
                    </ul>
                  </div>
                )}
                
                <div className="review-process">
                  <h3>What happens now?</h3>
                  <ul>
                    <li>🔍 A moderator will review {isTestMode ? 'the' : 'your'} submission</li>
                    <li>⏰ This typically takes a few hours (max 24 hours)</li>
                    <li>📧 {isTestMode ? 'The user would be' : 'You\'ll be'} notified of the decision via Discord</li>
                    <li>❓ {isTestMode ? 'They may be' : 'You may be'} contacted if clarification is needed</li>
                  </ul>
                </div>

                <div className="patience-note">
                  <p>
                    <strong>Thank you for your patience!</strong> While {isTestMode ? 'waiting' : 'you wait'}, feel free to explore 
                    any public channels that are available to new members.
                  </p>
                </div>

                {isTestMode && (
                  <div className="test-mode-notice">
                    <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4 mt-4">
                      <h4 className="text-orange-400 font-semibold mb-2">🧪 Test Mode Results</h4>
                      <p className="text-orange-300 text-sm">
                        This is a preview of what users would see when they need manual review. 
                        In reality, moderators would receive a notification to review this submission.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => window.close()}
              className="close-button pending"
            >
              {isTestMode ? 'Close Test Preview ⏳' : 'Close Window ⏳'}
            </motion.button>
          </motion.div>
        )}

        {/* ==========================================
            FOOTER
           ========================================== */}
        
        <div className="completion-footer">
          <p>
            {isTestMode 
              ? '🧪 This is a test preview - no actual verification was processed'
              : 'Having issues? Contact a moderator in the server for assistance.'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

{/* ==========================================
    EXPORT
   ========================================== */}

export default CompletionPage;