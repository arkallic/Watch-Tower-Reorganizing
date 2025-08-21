import React, { useState, useEffect } from 'react';
import './FirstTimeSetup.css';

const FirstTimeSetup = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [guildData, setGuildData] = useState({ channels: [], roles: [], members: [] });
  const [setupData, setSetupData] = useState({
    domain: 'localhost',
    customDomain: '',
    approvalUser: null,
    coreSettings: {
      enableBot: true,
      timeWindow: 24,
      messagesPerCase: 10
    },
    channels: {
      reportChannel: null,
      modActionReportChannel: null,
      modChatChannel: null,
      watchedChannels: []
    },
    modStrings: {
      enabled: false,
      scopeConfig: 'PERM'
    },
    aiMonitoring: {
      enabled: true,
      ollamaEndpoint: 'http://127.0.0.1:11434',
      model: 'llama3.1',
      monitoringScope: 'ALL',
      watchedChannels: [],
      flagThreshold: 7,
      customPrompt: ''
    },
    permissions: {
      moderatorRoles: []
    },
    advanced: {
      maxCaseDays: 30,
      saveDeletedAttachments: true,
      deletedMessageRetention: 7,
      maxAttachmentSize: null
    },
    cases: {
      autoResolveAfter: 30,
      requireModeratorApproval: false
    }
  });

  useEffect(() => {
    fetchDiscordData();
  }, []);

  const fetchDiscordData = async () => {
    const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const apiBase = isDevelopment ? 'http://localhost:8000' : '';
    
    try {
      const response = await fetch(`${apiBase}/api/pagedata/settings`);
      const data = await response.json();
      if (data.guildInfo && !data.guildInfo.error) {
        setGuildData({
          channels: data.guildInfo.channels?.text_channels || [],
          roles: data.guildInfo.roles || [],
          members: []
        });
      }
    } catch (error) {
      console.error('Failed to fetch Discord guild data:', error);
    }

    try {
      const membersResponse = await fetch(`${apiBase}/api/pagedata/members`);
      const membersData = await membersResponse.json();
      if (membersData.members) {
        setGuildData(prev => ({
          ...prev,
          members: membersData.members.filter(member => !member.bot)
        }));
      }
    } catch (error) {
      console.error('Failed to fetch members:', error);
    }
  };

  const steps = [
    { component: WelcomePage, title: "Welcome" },
    { component: DisclaimerPage, title: "Important Notice" },
    { component: DomainConfigPage, title: "Domain Configuration" },
    { component: ApprovalUserPage, title: "Approval User" },
    { component: CoreSettingsPage, title: "Core Settings" },
    { component: ChannelConfigPage, title: "Channel Configuration" },
    { component: ModStringsPage, title: "ModStrings Setup" },
    { component: AIMonitoringPage, title: "AI Monitoring" },
    { component: AIConfigPage, title: "AI Configuration" },
    { component: PermissionsPage, title: "Permissions & Roles" },
    { component: CasesConfigPage, title: "Cases Configuration" },
    { component: AdvancedSettingsPage, title: "Advanced Settings" },
    { component: FinalPage, title: "Setup Complete" }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setIsTransitioning(true);
      setDirection(1);
      setTimeout(() => {
        setCurrentStep(currentStep + 1);
        setIsTransitioning(false);
      }, 150);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setIsTransitioning(true);
      setDirection(-1);
      setTimeout(() => {
        setCurrentStep(currentStep - 1);
        setIsTransitioning(false);
      }, 150);
    }
  };

  const updateSetupData = (section, data) => {
    if (typeof section === 'string' && typeof data !== 'object') {
      setSetupData(prev => ({ ...prev, [section]: data }));
    } else {
      setSetupData(prev => ({
        ...prev,
        [section]: { ...prev[section], ...data }
      }));
    }
  };

  const CurrentComponent = steps[currentStep].component;

  return (
    <div className="setup-container">
      <div className="setup-background">
        <div className="animated-bg"></div>
        <div className="particles"></div>
      </div>
      
      <div className="setup-content">
        <div 
          className={`setup-page ${isTransitioning ? 'transitioning' : ''} ${direction > 0 ? 'slide-left' : 'slide-right'}`}
          key={currentStep}
        >
          <CurrentComponent
            data={setupData}
            updateData={updateSetupData}
            guildData={guildData}
            nextStep={nextStep}
            prevStep={prevStep}
            currentStep={currentStep}
            totalSteps={steps.length}
            isFirstStep={currentStep === 0}
            isLastStep={currentStep === steps.length - 1}
            onComplete={onComplete}
          />
        </div>
      </div>

      {currentStep > 0 && currentStep < steps.length - 1 && (
        <div className="progress-indicator">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />
          </div>
          <div className="progress-text">
            Step {currentStep} of {steps.length - 1}: {steps[currentStep].title}
          </div>
        </div>
      )}
    </div>
  );
};

const WelcomePage = ({ nextStep }) => {
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowContent(true), 300);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="welcome-page">
      <div className="welcome-header">
        <h1 className="glowing-title">Welcome to Watch Tower</h1>
        <h2 className="subtitle">Vibe coded. Vibe Moddin'</h2>
      </div>

      <div className="logo-container">
        <img 
          src="/images/logo.png" 
          alt="Watch Tower Logo" 
          className="setup-logo"
        />
      </div>

      <div className={`welcome-content ${showContent ? 'show' : ''}`}>
        <div className="introduction">
          <p>
            Watch Tower is a comprehensive suite of Discord Moderation tools powered by AI analysis, 
            an extensive dashboard and its own Moderation Syntax ("ModStrings"). Your community is 
            one step closer to greatness and ready to conquer the world!
          </p>
          <p>
            As this appears to be your first time installing the bot, it's time to go through some 
            baller setup. You ready?
          </p>
        </div>

        <button
          className="hell-ya-button"
          onClick={nextStep}
        >
          Hell ya!
        </button>
      </div>
    </div>
  );
};

const DisclaimerPage = ({ nextStep, prevStep }) => {
  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area disclaimer-content">
        <div className="disclaimer-header">
          <div className="warning-icon">⚠️</div>
          <h2>Important Notice</h2>
        </div>

        <div className="disclaimer-text">
          <div className="disclaimer-card">
            <h3>🚧 Beta Software</h3>
            <p>
              Watch Tower is currently in beta and is <strong>vibe coded</strong>. While we've put 
              extensive effort into making it robust, you may encounter bugs or unexpected behavior. 
              Please report any issues you find!
            </p>
          </div>

          <div className="disclaimer-card">
            <h3>🛠️ Open Source</h3>
            <p>
              This project is hosted on GitHub and is completely open source. You can find the 
              repository link in the "About Bot" section of the dashboard. Contributions, bug 
              reports, and feature requests are welcome!
            </p>
          </div>

          <div className="disclaimer-card">
            <h3>💡 Getting Help</h3>
            <p>
              If you encounter issues or need help, check the GitHub repository for documentation, 
              known issues, and troubleshooting guides. The community is there to help!
            </p>
          </div>
        </div>
      </div>

      <div className="setup-navigation">
        <button onClick={prevStep} className="nav-button secondary">
          Back
        </button>
        <button onClick={nextStep} className="nav-button primary">
          I Understand, Continue
        </button>
      </div>
    </div>
  );
};

const DomainConfigPage = ({ data, updateData, nextStep, prevStep }) => {
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
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
        <h2>Domain Configuration</h2>
        <p className="section-description">
          Configure how you'll access the Watch Tower dashboard. This determines the URL 
          structure and accessibility of your moderation interface.
        </p>

        <div className="domain-options">
          <div 
            className={`domain-option ${data.domain === 'localhost' ? 'selected' : ''}`}
            onClick={() => updateData('domain', 'localhost')}
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
            onClick={() => updateData('domain', 'custom')}
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
          <div className="custom-domain-input">
            <label className="setting-label">Your Domain</label>
            <input
              type="text"
              value={data.customDomain}
              onChange={(e) => updateData('customDomain', e.target.value)}
              placeholder="bot.localdatahost.com"
              className="setting-input"
            />
            <div className="domain-preview">
              <strong>Dashboard URL:</strong> {getExampleUrl()}
            </div>
          </div>
        )}
      </div>

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

const ApprovalUserPage = ({ data, updateData, guildData, nextStep, prevStep }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredMembers = guildData.members.filter(member => {
    if (!searchTerm.trim()) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      member.username?.toLowerCase().includes(searchLower) ||
      member.display_name?.toLowerCase().includes(searchLower) ||
      member.global_name?.toLowerCase().includes(searchLower)
    );
  });

  const handleUserSelect = (member) => {
    updateData('approvalUser', member);
  };

  const clearSelection = () => {
    updateData('approvalUser', null);
  };

  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
        <h2>Bot Change Approval User</h2>
        <p className="section-description">
          Select a Discord user who will approve bot setting changes. When settings are modified 
          through the dashboard, this user will receive verification messages. This is optional.
        </p>

        <div className="user-search-container">
          <input
            type="text"
            placeholder="Search users by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="setting-input"
          />
          {searchTerm && (
            <div className="search-info">
              Found {filteredMembers.length} user{filteredMembers.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>

        {data.approvalUser && (
          <div className="selected-user">
            <div className="selected-user-header">
              <h3>Selected User:</h3>
              <button onClick={clearSelection} className="clear-selection-btn">
                Clear Selection
              </button>
            </div>
            <div className="user-item selected">
              <img 
                src={data.approvalUser.avatar_url} 
                alt={data.approvalUser.username}
                className="user-avatar"
              />
              <div className="user-info">
                <h4>{data.approvalUser.display_name || data.approvalUser.global_name}</h4>
                <p>@{data.approvalUser.username}</p>
              </div>
            </div>
          </div>
        )}

        <div className="user-list">
          {filteredMembers.length === 0 ? (
            <div className="no-users-found">
              <p>No users found matching "{searchTerm}"</p>
            </div>
          ) : (
            filteredMembers.slice(0, 50).map(member => (
              <div
                key={member.user_id}
                className={`user-item ${data.approvalUser?.user_id === member.user_id ? 'selected' : ''}`}
                onClick={() => handleUserSelect(member)}
              >
                <img 
                  src={member.avatar_url} 
                  alt={member.username}
                  className="user-avatar"
                />
                <div className="user-info">
                  <h4>{member.display_name || member.global_name || member.username}</h4>
                  <p>@{member.username}</p>
                  {member.display_name && member.display_name !== member.username && (
                    <span className="user-real-name">{member.username}</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="setup-navigation">
        <button onClick={prevStep} className="nav-button secondary">
          Back
        </button>
        <div className="nav-group">
          <button onClick={() => { updateData('approvalUser', null); nextStep(); }} className="nav-button secondary">
            Skip
          </button>
          <button onClick={nextStep} className="nav-button primary">
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

const CoreSettingsPage = ({ data, updateData, nextStep, prevStep }) => {
  const handleChange = (field, value) => {
    updateData('coreSettings', { [field]: value });
  };

  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
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
      </div>

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

const ChannelConfigPage = ({ data, updateData, guildData, nextStep, prevStep }) => {
  const handleChannelChange = (field, value) => {
    updateData('channels', { [field]: value });
  };

  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
        <h2>Channel Configuration</h2>
        <p className="section-description">
          Set up the essential channels for Watch Tower to communicate with your moderation team.
        </p>

        <div className="settings-grid">
          <div className="setting-item">
            <label className="setting-label">Report Channel (Required)</label>
            <select 
              className="setting-input"
              value={data.channels.reportChannel || ''}
              onChange={(e) => handleChannelChange('reportChannel', e.target.value)}
            >
              <option value="">Select a channel...</option>
              {guildData.channels.map(channel => (
                <option key={channel.id} value={channel.id}>
                  #{channel.name} {channel.category && `(${channel.category})`}
                </option>
              ))}
            </select>
            <p className="setting-description">
              Where moderation reports and flagged messages are sent. This is required for the bot to function.
            </p>
          </div>

          <div className="setting-item">
            <label className="setting-label">Mod Chat Channel (Optional)</label>
            <select 
              className="setting-input"
              value={data.channels.modChatChannel || ''}
              onChange={(e) => handleChannelChange('modChatChannel', e.target.value)}
            >
              <option value="">Select a channel...</option>
              {guildData.channels.map(channel => (
                <option key={channel.id} value={channel.id}>
                  #{channel.name} {channel.category && `(${channel.category})`}
                </option>
              ))}
            </select>
            <p className="setting-description">
              Private channel for moderator discussions and coordination.
            </p>
          </div>

          <div className="setting-item">
            <label className="setting-label">Mod Action Reports (Optional)</label>
            <select 
              className="setting-input"
              value={data.channels.modActionReportChannel || ''}
              onChange={(e) => handleChannelChange('modActionReportChannel', e.target.value)}
            >
              <option value="">Select a channel...</option>
              {guildData.channels.map(channel => (
                <option key={channel.id} value={channel.id}>
                  #{channel.name} {channel.category && `(${channel.category})`}
                </option>
              ))}
            </select>
            <p className="setting-description">
              Channel for logging moderation actions like warns, timeouts, and bans.
            </p>
          </div>
        </div>
      </div>

      <div className="setup-navigation">
        <button onClick={prevStep} className="nav-button secondary">
          Back
        </button>
        <button 
          onClick={nextStep} 
          className="nav-button primary"
          disabled={!data.channels.reportChannel}
        >
          Continue
        </button>
      </div>
    </div>
  );
};

const ModStringsPage = ({ data, updateData, nextStep, prevStep }) => {
  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
        <h2>ModStrings Configuration</h2>
        <p className="section-description">
          ModStrings are Watch Tower's custom moderation syntax that allows you to create powerful 
          automation rules. Think of them as smart moderation scripts that can trigger actions 
          based on user behavior patterns.
        </p>

        <div className="settings-grid">
          <div className="setting-item">
            <label className="setting-label">
              <input
                type="checkbox"
                checked={data.modStrings.enabled}
                onChange={(e) => updateData('modStrings', { enabled: e.target.checked })}
                className="setting-checkbox"
              />
              <span className="checkmark"></span>
              Enable ModStrings
            </label>
            <p className="setting-description">
              Enable the ModStrings automation system. You can create custom rules later 
              in the dashboard once setup is complete.
            </p>
          </div>

          {data.modStrings.enabled && (
            <div className="setting-item">
              <label className="setting-label">Scope Configuration</label>
              <select
                value={data.modStrings.scopeConfig}
                onChange={(e) => updateData('modStrings', { scopeConfig: e.target.value })}
                className="setting-select"
              >
                <option value="PERM">PERM - Permanent rules (always active)</option>
                <option value="WAKEUP">WAKEUP - Triggered rules (activate on conditions)</option>
                <option value="TEMP">TEMP - Temporary rules (time-limited)</option>
              </select>
              <p className="setting-description">
                Choose the default scope for ModString rules. PERM rules are always active, 
                WAKEUP rules trigger based on conditions, and TEMP rules have time limits.
              </p>
            </div>
          )}
        </div>

        {data.modStrings.enabled && (
          <div className="info-card">
            <h3>💡 ModStrings Examples</h3>
            <div className="examples-grid">
              <div className="example-card">
                <h4>Spam Detection</h4>
                <code>PERM: links{'>'}=3 → warn "Too many links"</code>
              </div>
              <div className="example-card">
                <h4>Toxicity Filter</h4>
                <code>WAKEUP: ai=yes AND bl=toxicity → delete</code>
              </div>
            </div>
          </div>
        )}
      </div>

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

const AIMonitoringPage = ({ data, updateData, nextStep, prevStep }) => {
  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
        <h2>AI Monitoring System</h2>
        <p className="section-description">
          Watch Tower's AI system can analyze messages for potential issues like toxicity, 
          harassment, spam, and mental health concerns. It uses advanced language models 
          to provide intelligent moderation assistance.
        </p>

        <div className="ai-choice-cards">
          <div 
            className={`choice-card ${data.aiMonitoring.enabled ? 'selected' : ''}`}
            onClick={() => updateData('aiMonitoring', { enabled: true })}
          >
            <div className="choice-icon">🤖</div>
            <h3>Enable AI Monitoring</h3>
            <p>
              Use AI to automatically analyze messages and flag potential issues. 
              Requires Ollama with llama3.1 model installed.
            </p>
            <div className="choice-benefits">
              <div>✓ Automatic content analysis</div>
              <div>✓ Mental health support detection</div>
              <div>✓ Toxicity and spam filtering</div>
            </div>
          </div>

          <div 
            className={`choice-card ${!data.aiMonitoring.enabled ? 'selected' : ''}`}
            onClick={() => updateData('aiMonitoring', { enabled: false })}
          >
            <div className="choice-icon">👥</div>
            <h3>Manual Moderation Only</h3>
            <p>
              Rely on human moderators and ModStrings automation without AI analysis. 
              You can enable AI later if needed.
            </p>
            <div className="choice-benefits">
              <div>✓ No AI dependencies</div>
              <div>✓ Full human control</div>
              <div>✓ ModStrings still available</div>
            </div>
          </div>
        </div>
      </div>

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

const AIConfigPage = ({ data, updateData, guildData, nextStep, prevStep }) => {
  useEffect(() => {
    if (!data.aiMonitoring.enabled) {
      nextStep();
    }
  }, [data.aiMonitoring.enabled, nextStep]);

  if (!data.aiMonitoring.enabled) {
    return null;
  }

  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
        <h2>AI Configuration</h2>
        <p className="section-description">
          Configure the AI analysis system. Make sure you have Ollama installed with the llama3.1 model.
        </p>

        <div className="settings-grid">
          <div className="setting-item">
            <label className="setting-label">Ollama Endpoint</label>
            <input
              type="text"
              value={data.aiMonitoring.ollamaEndpoint}
              onChange={(e) => updateData('aiMonitoring', { ollamaEndpoint: e.target.value })}
              className="setting-input"
              placeholder="http://127.0.0.1:11434"
            />
            <p className="setting-description">
              URL of your Ollama instance. Default is local installation.
            </p>
          </div>

          <div className="setting-item">
            <label className="setting-label">Monitoring Scope</label>
            <select
              value={data.aiMonitoring.monitoringScope}
              onChange={(e) => updateData('aiMonitoring', { monitoringScope: e.target.value })}
              className="setting-select"
            >
              <option value="ALL">Monitor All Channels</option>
              <option value="SELECTED">Monitor Selected Channels Only</option>
              <option value="EXCLUDE">Monitor All Except Selected</option>
           </select>
           <p className="setting-description">
             Choose which channels the AI should monitor.
           </p>
         </div>

         {(data.aiMonitoring.monitoringScope === 'SELECTED' || data.aiMonitoring.monitoringScope === 'EXCLUDE') && (
           <div className="setting-item full-width">
             <label className="setting-label">
               {data.aiMonitoring.monitoringScope === 'SELECTED' ? 'Channels to Monitor' : 'Channels to Exclude'}
             </label>
             <div className="channel-list">
               {guildData.channels.map(channel => (
                 <label key={channel.id} className="channel-item">
                   <input
                     type="checkbox"
                     checked={data.aiMonitoring.watchedChannels.includes(channel.id)}
                     onChange={(e) => {
                       const channels = data.aiMonitoring.watchedChannels;
                       if (e.target.checked) {
                         updateData('aiMonitoring', { watchedChannels: [...channels, channel.id] });
                       } else {
                         updateData('aiMonitoring', { watchedChannels: channels.filter(id => id !== channel.id) });
                       }
                     }}
                     className="setting-checkbox"
                   />
                   <span className="checkmark"></span>
                   #{channel.name}
                 </label>
               ))}
             </div>
           </div>
         )}

         <div className="setting-item">
           <label className="setting-label">Flag Threshold</label>
           <div className="threshold-container">
             <input
               type="range"
               min="1"
               max="10"
               value={data.aiMonitoring.flagThreshold}
               onChange={(e) => updateData('aiMonitoring', { flagThreshold: parseInt(e.target.value) })}
               className="threshold-slider"
             />
             <span className="threshold-value">{data.aiMonitoring.flagThreshold}</span>
           </div>
           <p className="setting-description">
             Sensitivity level for AI flagging (1=least sensitive, 10=most sensitive).
           </p>
         </div>
       </div>
     </div>

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

const PermissionsPage = ({ data, updateData, guildData, nextStep, prevStep }) => {
  const toggleRole = (roleId) => {
    const roles = data.permissions.moderatorRoles;
    if (roles.includes(roleId)) {
      updateData('permissions', { moderatorRoles: roles.filter(id => id !== roleId) });
    } else {
      updateData('permissions', { moderatorRoles: [...roles, roleId] });
    }
  };

  const adminRoles = guildData.roles.filter(role => 
    role.permissions && (
      role.permissions.includes('ADMINISTRATOR') || 
      role.permissions.includes('MANAGE_GUILD') ||
      role.name.toLowerCase().includes('admin') ||
      role.name.toLowerCase().includes('owner')
    )
  );
  
  const modRoles = guildData.roles.filter(role => 
    !adminRoles.includes(role) && (
      role.permissions && (
        role.permissions.includes('MANAGE_MESSAGES') ||
        role.permissions.includes('KICK_MEMBERS') ||
        role.permissions.includes('BAN_MEMBERS') ||
        role.permissions.includes('MODERATE_MEMBERS') ||
        role.name.toLowerCase().includes('mod') ||
        role.name.toLowerCase().includes('staff')
      )
    )
  );
  
  const otherRoles = guildData.roles.filter(role => 
    !adminRoles.includes(role) && !modRoles.includes(role) && role.name !== '@everyone'
  );

  return (
    <div className="setup-page-content">
      <div className="page-header">
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
        <div className="header-text">
          <h1>Watch Tower</h1>
          <p>Vibe coded. Vibe Moddin'</p>
        </div>
      </div>

      <div className="setup-content-area">
        <h2>Permissions & Roles</h2>
        <p className="section-description">
          Configure which Discord roles have moderation permissions. Members with these roles 
          can view moderation reports, manage cases, and access advanced bot features.
        </p>

        <div className="setting-item">
          <label className="setting-label">Moderator Roles</label>
          
          {adminRoles.length > 0 && (
            <div className="role-section">
              <h4 className="role-section-title">👑 Administrator Roles</h4>
              <div className="roles-grid">
                {adminRoles.map(role => (
                  <div
                    key={role.id}
                    className={`role-item admin ${data.permissions.moderatorRoles.includes(role.id) ? 'selected' : ''}`}
                    onClick={() => toggleRole(role.id)}
                  >
                    <div 
                      className="role-color" 
                      style={{ backgroundColor: role.color || '#f39c12' }}
                    ></div>
                    <span className="role-name">{role.name}</span>
                    <span className="role-members">({role.members || 0} members)</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {modRoles.length > 0 && (
            <div className="role-section">
              <h4 className="role-section-title">🛡️ Moderator Roles</h4>
              <div className="roles-grid">
                {modRoles.map(role => (
                  <div
                    key={role.id}
                    className={`role-item moderator ${data.permissions.moderatorRoles.includes(role.id) ? 'selected' : ''}`}
                    onClick={() => toggleRole(role.id)}
                  >
                    <div 
                      className="role-color" 
                      style={{ backgroundColor: role.color || '#3498db' }}
                    ></div>
                    <span className="role-name">{role.name}</span>
                    <span className="role-members">({role.members || 0} members)</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {otherRoles.length > 0 && (
            <div className="role-section">
              <h4 className="role-section-title">👥 Other Roles</h4>
              <div className="roles-grid">
                {otherRoles.map(role => (
                  <div
                    key={role.id}
                    className={`role-item ${data.permissions.moderatorRoles.includes(role.id) ? 'selected' : ''}`}
                    onClick={() => toggleRole(role.id)}
                  >
                    <div 
                      className="role-color" 
                      style={{ backgroundColor: role.color || '#99aab5' }}
                    ></div>
                    <span className="role-name">{role.name}</span>
                    <span className="role-members">({role.members || 0} members)</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <p className="setting-description">
            Select roles that should have moderation permissions. Administrator roles typically have full access, 
            while moderator roles have limited permissions. You can modify this later in settings.
          </p>
        </div>
      </div>

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

const CasesConfigPage = ({ data, updateData, nextStep, prevStep }) => {
 return (
   <div className="setup-page-content">
     <div className="page-header">
       <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
       <div className="header-text">
         <h1>Watch Tower</h1>
         <p>Vibe coded. Vibe Moddin'</p>
       </div>
     </div>

     <div className="setup-content-area">
       <h2>Cases Configuration</h2>
       <p className="section-description">
         Cases are records of moderation actions and user behavior patterns. Configure how 
         Watch Tower creates and manages these moderation cases.
       </p>

       <div className="settings-grid">
         <div className="setting-item">
           <label className="setting-label">Auto-Resolve Cases After (Days)</label>
           <input
             type="number"
             min="1"
             max="365"
             value={data.cases.autoResolveAfter}
             onChange={(e) => updateData('cases', { autoResolveAfter: parseInt(e.target.value) })}
             className="setting-input"
           />
           <p className="setting-description">
             Automatically mark cases as resolved after this many days of inactivity.
           </p>
         </div>

         <div className="setting-item">
           <label className="setting-label">
             <input
               type="checkbox"
               checked={data.cases.requireModeratorApproval}
               onChange={(e) => updateData('cases', { requireModeratorApproval: e.target.checked })}
               className="setting-checkbox"
             />
             <span className="checkmark"></span>
             Require Moderator Approval
           </label>
           <p className="setting-description">
             Require a moderator to manually approve case creation for AI-flagged content.
           </p>
         </div>
       </div>

       <div className="info-card">
         <h3>📋 What are Cases?</h3>
         <p>
           Cases are comprehensive records that include the flagged message, surrounding context, 
           user history, and any moderation actions taken. They help moderators make informed 
           decisions and track patterns over time.
         </p>
       </div>
     </div>

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

const AdvancedSettingsPage = ({ data, updateData, nextStep, prevStep }) => {
 return (
   <div className="setup-page-content">
     <div className="page-header">
       <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
       <div className="header-text">
         <h1>Watch Tower</h1>
         <p>Vibe coded. Vibe Moddin'</p>
       </div>
     </div>

     <div className="setup-content-area">
       <h2>Advanced Settings</h2>
       <p className="section-description">
         Configure advanced options for data retention, file handling, and system behavior. 
         These settings affect how Watch Tower stores and manages moderation data.
       </p>

       <div className="settings-grid">
         <div className="setting-item">
           <label className="setting-label">Max Case Days</label>
           <input
             type="number"
             min="1"
             max="365"
             value={data.advanced.maxCaseDays}
             onChange={(e) => updateData('advanced', { maxCaseDays: parseInt(e.target.value) })}
             className="setting-input"
           />
           <p className="setting-description">
             Maximum number of days to keep case data before archiving.
           </p>
         </div>

         <div className="setting-item">
           <label className="setting-label">
             <input
               type="checkbox"
               checked={data.advanced.saveDeletedAttachments}
               onChange={(e) => updateData('advanced', { saveDeletedAttachments: e.target.checked })}
               className="setting-checkbox"
             />
             <span className="checkmark"></span>
             Save Deleted Attachments
           </label>
           <p className="setting-description">
             Automatically save attachments from deleted messages for evidence preservation.
           </p>
         </div>

         <div className="setting-item">
           <label className="setting-label">Deleted Message Retention (Days)</label>
           <input
             type="number"
             min="1"
             max="90"
             value={data.advanced.deletedMessageRetention}
             onChange={(e) => updateData('advanced', { deletedMessageRetention: parseInt(e.target.value) })}
             className="setting-input"
           />
           <p className="setting-description">
             How long to keep deleted message logs and attachments.
           </p>
         </div>

         <div className="setting-item">
           <label className="setting-label">Max Attachment Size (MB)</label>
           <input
             type="number"
             min="1"
             max="100"
             value={data.advanced.maxAttachmentSize || ''}
             onChange={(e) => updateData('advanced', { maxAttachmentSize: e.target.value ? parseInt(e.target.value) : null })}
             className="setting-input"
             placeholder="No limit"
           />
           <p className="setting-description">
             Maximum size for saved attachments. Leave empty for no limit.
           </p>
         </div>
       </div>
     </div>

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

const FinalPage = ({ data, onComplete }) => {
 const [isCompleting, setIsCompleting] = useState(false);

 const completeSetup = async () => {
   setIsCompleting(true);
   
   try {
     await new Promise(resolve => setTimeout(resolve, 2000));
     
     if (onComplete) {
       onComplete();
     }
     window.location.href = '/dashboard';
   } catch (error) {
     console.error('Setup completion error:', error);
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
     <div className="setup-content-area">
       <div className="congratulations-header">
         <div className="celebration-icon">🎉</div>
         <h1 className="congrats-title">Congratulations!</h1>
         <h2 className="congrats-subtitle">Watch Tower Setup Complete</h2>
       </div>

       <div className="setup-summary">
         <div className="summary-grid">
           <div className="summary-card">
             <h3>🔧 Core Settings</h3>
             <ul>
               <li>Bot Enabled: {data.coreSettings.enableBot ? 'Yes' : 'No'}</li>
               <li>Time Window: {data.coreSettings.timeWindow} hours</li>
               <li>Messages Per Case: {data.coreSettings.messagesPerCase}</li>
               <li>Report Channel: {data.channels.reportChannel ? 'Set' : 'Not set'}</li>
             </ul>
           </div>

           <div className="summary-card">
             <h3>🤖 AI & ModStrings</h3>
             <ul>
               <li>AI Monitoring: {data.aiMonitoring.enabled ? 'Enabled' : 'Disabled'}</li>
               <li>ModStrings: {data.modStrings.enabled ? 'Enabled' : 'Disabled'}</li>
               <li>AI Threshold: {data.aiMonitoring.enabled ? data.aiMonitoring.flagThreshold : 'N/A'}</li>
               <li>Moderator Roles: {data.permissions.moderatorRoles.length}</li>
             </ul>
           </div>

           <div className="summary-card">
             <h3>🌐 Access & Security</h3>
             <ul>
               <li>Type: {data.domain === 'localhost' ? 'Localhost' : 'Custom Domain'}</li>
               {data.customDomain && <li>Domain: {data.customDomain}</li>}
               <li>Approval User: {data.approvalUser ? data.approvalUser.display_name : 'None'}</li>
               <li>Cases Auto-Resolve: {data.cases.autoResolveAfter} days</li>
             </ul>
           </div>

           <div className="summary-card">
             <h3>⚙️ Advanced</h3>
             <ul>
               <li>Max Case Days: {data.advanced.maxCaseDays}</li>
               <li>Save Attachments: {data.advanced.saveDeletedAttachments ? 'Yes' : 'No'}</li>
               <li>Message Retention: {data.advanced.deletedMessageRetention} days</li>
               <li>Moderator Approval: {data.cases.requireModeratorApproval ? 'Required' : 'Not required'}</li>
             </ul>
           </div>
         </div>
       </div>

       <div className="completion-actions">
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
       </div>
     </div>
   </div>
 );
};

export default FirstTimeSetup;