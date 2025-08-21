// dashboard/frontend/src/spotlight-gate/components/QuestionsPage.jsx

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

{/* ==========================================
    QUESTIONS PAGE COMPONENT
   ========================================== */}

const QuestionsPage = ({ 
  nextStep, 
  prevStep, 
  config, 
  answers, 
  setAnswers,
  onSubmit,
  submitting
}) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);

  const questions = config?.questions || [];
  const totalQuestions = questions.length;
  const passingScore = config?.passing_score || 3;

  // Load saved answer when question changes
  useEffect(() => {
    const question = questions[currentQuestion];
    if (question) {
      setSelectedAnswer(answers[question.id] || '');
    }
  }, [currentQuestion, questions, answers]);

  const handleAnswerSelect = (answer) => {
    setSelectedAnswer(answer);
    const question = questions[currentQuestion];
    if (question) {
      setAnswers(prev => ({
        ...prev,
        [question.id]: answer
      }));
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setShowFeedback(false);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
      setShowFeedback(false);
    }
  };

  const handleSubmit = async () => {
    const result = await onSubmit();
    setShowFeedback(true);
  };

  const getAnsweredCount = () => {
    return Object.keys(answers).length;
  };

  const canSubmit = () => {
    return getAnsweredCount() >= totalQuestions && !submitting;
  };

  if (!questions.length) {
    return (
      <div className="questions-page">
        <div className="no-questions">
          <h2>No Questions Available</h2>
          <p>The quiz has not been configured yet.</p>
          <button onClick={nextStep} className="nav-button primary">
            Continue
          </button>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <div className="questions-page">
      
      {/* Header */}
      <div className="page-header">
        <div className="header-icon">🧠</div>
        <div>
          <h2>Knowledge Check</h2>
          <p>Answer these questions to show you understand our rules</p>
        </div>
      </div>

      {/* Progress */}
      <div className="question-progress">
        <div className="progress-info">
          <span>Question {currentQuestion + 1} of {totalQuestions}</span>
          <span>{getAnsweredCount()}/{totalQuestions} answered</span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${((currentQuestion + 1) / totalQuestions) * 100}%` }}
          ></div>
        </div>
        <div className="passing-info">
          <small>You need {passingScore} correct answers to pass</small>
        </div>
      </div>

      {/* Question Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestion}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="question-content"
        >
          
          {/* Question */}
          <div className="question-card">
            <h3 className="question-text">{question.text}</h3>
            
            {/* Answer Options */}
            <div className="answer-options">
              {question.options.map((option, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleAnswerSelect(option)}
                  className={`answer-option ${selectedAnswer === option ? 'selected' : ''}`}
                >
                  <div className="option-letter">{String.fromCharCode(65 + index)}</div>
                  <div className="option-text">{option}</div>
                  {selectedAnswer === option && (
                    <div className="selection-indicator">✓</div>
                  )}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Question Navigation */}
          <div className="question-navigation">
            <button 
              onClick={prevQuestion}
              disabled={currentQuestion === 0}
              className="nav-button secondary small"
            >
              ← Previous
            </button>
            
            <div className="question-dots">
              {questions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentQuestion(index)}
                  className={`question-dot ${
                    index === currentQuestion ? 'active' : ''
                  } ${
                    answers[questions[index].id] ? 'answered' : ''
                  }`}
                  title={`Question ${index + 1}`}
                >
                  {index + 1}
                </button>
              ))}
            </div>
            
            <button 
              onClick={nextQuestion}
              disabled={currentQuestion === totalQuestions - 1}
              className="nav-button secondary small"
            >
              Next →
            </button>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Submit Section */}
      <div className="submit-section">
        <div className="submit-info">
          <p>
            {getAnsweredCount() < totalQuestions 
              ? `Please answer ${totalQuestions - getAnsweredCount()} more question${totalQuestions - getAnsweredCount() !== 1 ? 's' : ''}`
              : 'All questions answered! Ready to submit?'
            }
          </p>
        </div>
        
        <div className="submit-actions">
          <button 
            onClick={prevStep} 
            className="nav-button secondary"
            disabled={submitting}
          >
            ← Back
          </button>
          
          <button 
            onClick={handleSubmit}
            className="nav-button primary"
            disabled={!canSubmit()}
          >
            {submitting ? (
              <span className="submitting">
                <div className="loading-spinner small"></div>
                Submitting...
              </span>
            ) : (
              'Submit Answers ✅'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionsPage;