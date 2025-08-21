// dashboard/frontend/src/spotlight-gate/hooks/useSpotlightGate.js

import { useState, useEffect } from 'react';

export const useSpotlightGate = (userId, key) => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Check if this is a test mode
  const isTestMode = key && key.startsWith('test-');

  // Load configuration
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const apiBase = isDevelopment ? 'http://localhost:8000' : '';
        
        if (isTestMode) {
          // For test mode, get current settings from the dashboard
          const response = await fetch(`${apiBase}/api/settings/spotlight`);
          
          if (!response.ok) {
            throw new Error('Failed to load Spotlight settings for testing');
          }
          
          const settingsData = await response.json();
          
          // Transform settings into config format
          const testConfig = {
            success: true,
            rules: settingsData.spotlight_rules || generateDefaultRules(),
            questions: settingsData.spotlight_questions || generateDefaultQuestions(),
            recaptcha_site_key: settingsData.spotlight_recaptcha_site_key || "",
            captcha_enabled: settingsData.spotlight_captcha_enabled || false,
            passing_score: settingsData.spotlight_passing_score || 3,
            server_name: settingsData.server_name || "Test Server",
            test_mode: true
          };
          
          setConfig(testConfig);
        } else {
          // Real verification mode
          const response = await fetch(`${apiBase}/api/gate/config/${userId}/${key}`);
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to load verification');
          }
          
          const data = await response.json();
          
          if (!data.success) {
            throw new Error(data.error || 'Invalid verification link');
          }
          
          setConfig(data);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (userId && key) {
      fetchConfig();
    } else {
      setError('Invalid verification link');
      setLoading(false);
    }
  }, [userId, key, isTestMode]);

  // Submit verification
  const submitVerification = async (submissionData) => {
    try {
      setSubmitting(true);
      
      if (isTestMode) {
        // Mock submission for test mode
        await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay
        
        // Calculate mock score
        const questions = config?.questions || [];
        let correctAnswers = 0;
        
        questions.forEach(question => {
          if (submissionData.answers[question.id] === question.correct_answer) {
            correctAnswers++;
          }
        });
        
        const passed = correctAnswers >= (config?.passing_score || 3);
        
        return {
          success: true,
          passed,
          score: correctAnswers,
          total: questions.length,
          required: config?.passing_score || 3,
          test_mode: true
        };
      } else {
        // Real submission
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const apiBase = isDevelopment ? 'http://localhost:8000' : '';

        const verifyResponse = await fetch(`${apiBase}/api/gate/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(submissionData)
        });

        const verifyResult = await verifyResponse.json();

        // Log attempt
        const logData = {
          userId: submissionData.userId,
          username: 'Unknown',
          display_name: 'Unknown',
          avatar: '',
          status: verifyResult.passed ? 'Passed' : 'Pending',
          date: new Date().toISOString(),
          time_to_complete: submissionData.timeToComplete,
          captcha_fails: submissionData.captchaFails,
          failed_questions: verifyResult.failed_questions || [],
          red_flags: [],
          score: verifyResult.score || 0,
          total_questions: verifyResult.total || 0,
          passed: verifyResult.passed || false
        };

        await fetch(`${apiBase}/api/gate/log`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(logData)
        });

        return verifyResult;
      }
    } catch (err) {
      console.error('Verification submission error:', err);
      return { success: false, error: err.message };
    } finally {
      setSubmitting(false);
    }
  };

  return {
    config,
    loading,
    error,
    submitVerification,
    submitting
  };
};

// Helper functions for test mode
const generateDefaultRules = () => `# Welcome to our Community!

## 📋 Community Guidelines

Please read and follow these rules to maintain a positive environment:

### 🤝 Be Respectful
- Treat all members with kindness and respect
- No harassment, bullying, or discrimination
- Keep discussions civil and constructive

### 🚫 No Spam or Self-Promotion
- Avoid excessive self-promotion or advertising
- Don't flood channels with repetitive messages
- Use appropriate channels for specific content

### 🔞 Keep It Appropriate
- No NSFW content or inappropriate material
- Keep language family-friendly
- Respect all age groups in our community

### 📍 Use Appropriate Channels
- Post content in the right channels
- Read channel descriptions before posting
- Ask moderators if you're unsure where to post

### ⚖️ Follow Discord Terms of Service
- All Discord ToS rules apply here
- No illegal content or activities
- Report violations to moderators`;

const generateDefaultQuestions = () => [
  {
    id: "q1",
    text: "What should you do if you want to promote your own content?",
    options: [
      "Post it in any channel immediately",
      "Ask a moderator first or use designated channels",
      "Spam it in multiple channels",
      "Promote it constantly"
    ],
    correct_answer: "Ask a moderator first or use designated channels"
  },
  {
    id: "q2", 
    text: "How should you treat other community members?",
    options: [
      "However I want",
      "With respect and kindness",
      "Ignore them completely",
      "Only talk to certain people"
    ],
    correct_answer: "With respect and kindness"
  },
  {
    id: "q3",
    text: "What type of content should you avoid posting?",
    options: [
      "Helpful questions and discussions",
      "NSFW or inappropriate material", 
      "On-topic conversations",
      "Friendly introductions"
    ],
    correct_answer: "NSFW or inappropriate material"
  },
  {
    id: "q4",
    text: "If you're unsure where to post something, what should you do?",
    options: [
      "Post it anywhere and hope for the best",
      "Don't post it at all",
      "Ask a moderator for guidance",
      "Post it in every channel"
    ],
    correct_answer: "Ask a moderator for guidance"
  }
];