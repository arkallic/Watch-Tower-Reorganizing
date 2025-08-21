// dashboard/frontend/src/spotlight-gate/SpotlightGate.jsx

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './SpotlightGate.css';
import WelcomePage from './components/WelcomePage';
import RulesPage from './components/RulesPage';
import CaptchaPage from './components/CaptchaPage';
import QuestionsPage from './components/QuestionsPage';
import CompletionPage from './components/CompletionPage';
import { useSpotlightGate } from './hooks/useSpotlightGate';

const SpotlightGate = () => {
  const { userId, key } = useParams();
  const navigate = useNavigate();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [startTime] = useState(Date.now());
  const [answers, setAnswers] = useState({});
  const [captchaResponse, setCaptchaResponse] = useState(null);
  const [captchaFails, setCaptchaFails] = useState(0);
  
  const {
    config,
    loading,
    error,
    submitVerification,
    submitting
  } = useSpotlightGate(userId, key);

  const steps = [
    { id: 'welcome', title: 'Welcome', component: WelcomePage },
    { id: 'rules', title: 'Rules', component: RulesPage },
    ...(config?.captcha_enabled ? [{ id: 'captcha', title: 'Security', component: CaptchaPage }] : []),
    { id: 'questions', title: 'Quiz', component: QuestionsPage },
    { id: 'completion', title: 'Complete', component: CompletionPage }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (stepIndex) => {
    if (stepIndex >= 0 && stepIndex < steps.length) {
      setCurrentStep(stepIndex);
    }
  };

  const handleSubmitVerification = async () => {
    const completionTime = (Date.now() - startTime) / 1000;
    
    const submissionData = {
      userId,
      key,
      answers,
      recaptchaResponse: captchaResponse,
      timeToComplete: completionTime,
      captchaFails
    };

    const result = await submitVerification(submissionData);
    goToStep(steps.length - 1);
    return result;
  };

  useEffect(() => {
    if (error) {
      console.error('SpotlightGate error:', error);
    }
  }, [error]);

  const renderCurrentStep = () => {
    if (loading) {
      return (
        <div className="spotlight-loading">
          <div className="loading-spinner"></div>
          <h2>Loading verification...</h2>
          <p>Please wait while we prepare your verification process.</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="spotlight-error">
          <div className="error-icon">⚠️</div>
          <h2>Verification Unavailable</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button 
              onClick={() => window.location.reload()} 
              className="retry-button"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    const CurrentStepComponent = steps[currentStep]?.component;
    
    if (!CurrentStepComponent) {
      return (
        <div className="spotlight-error">
          <h2>Invalid Step</h2>
          <p>Something went wrong with the verification process.</p>
        </div>
      );
    }

    return (
      <CurrentStepComponent
        config={config}
        answers={answers}
        setAnswers={setAnswers}
        captchaResponse={captchaResponse}
        setCaptchaResponse={setCaptchaResponse}
        captchaFails={captchaFails}
        setCaptchaFails={setCaptchaFails}
        nextStep={nextStep}
        prevStep={prevStep}
        goToStep={goToStep}
        currentStep={currentStep}
        totalSteps={steps.length}
        onSubmit={handleSubmitVerification}
        submitting={submitting}
        userId={userId}
        isLastStep={currentStep === steps.length - 1}
      />
    );
  };

  return (
    <div className="spotlight-gate">
      {/* Animated Background */}
      <div className="spotlight-background">
        <div className="bg-gradient"></div>
        <div className="bg-grid"></div>
        <div className="bg-particles"></div>
      </div>

      {/* Floating Emojis */}
      <div className="floating-emojis">
        {[...Array(15)].map((_, i) => (
          <div 
            key={i}
            className="floating-emoji"
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 20}s`,
              animationDuration: `${15 + Math.random() * 10}s`,
            }}
          >
            {['🎉', '🚀', '⭐', '🌟', '✨', '💫', '🎊', '🔒', '🛡️', '👋', '🎯', '🎭', '🎪', '🎨', '🎵'][Math.floor(Math.random() * 15)]}
          </div>
        ))}
      </div>

      {/* Progress Indicator */}
      <div className="progress-indicator">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          ></div>
        </div>
        <p className="progress-text">Step {currentStep + 1} of {steps.length}</p>
      </div>

      {/* Content Container */}
      <div className="spotlight-container">
        {/* Main Content */}
        <div className="spotlight-content">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
              className="step-content"
            >
              {renderCurrentStep()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Step Navigation Dots */}
      <div className="step-navigation">
        <div className="step-dots">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`step-dot ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
              title={step.title}
            >
              {index + 1}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="spotlight-footer">
        <p>🔒 Protected with <strong>Watch Gate</strong> - A private moderation bot</p>
      </div>
    </div>
  );
};

export default SpotlightGate;