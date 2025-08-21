// dashboard/frontend/src/pages/Settings.jsx

import React, { useState, useEffect, useCallback } from 'react';
import {
  Cog6ToothIcon, CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon, ServerIcon, EyeIcon, HeartIcon,
  ArrowPathIcon, CommandLineIcon, ShieldCheckIcon, DocumentArrowDownIcon, DocumentArrowUpIcon, ClockIcon,
  ArrowUturnLeftIcon, LightBulbIcon, PlayIcon, PlusIcon, MinusIcon
} from '@heroicons/react/24/outline';

{/* ==========================================
    MAIN SETTINGS COMPONENT
   ========================================== */}

const Settings = () => {
  
  {/* ==========================================
      STATE MANAGEMENT
     ========================================== */}
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({});
  const [pendingChanges, setPendingChanges] = useState({});
  const [settingsHistory, setSettingsHistory] = useState([]);
  const [activeSection, setActiveSection] = useState('core');
  const [channels, setChannels] = useState([]);
  const [categories, setCategories] = useState([]);
  const [roles, setRoles] = useState([]);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [importData, setImportData] = useState('');

  {/* ==========================================
      SETTINGS SECTIONS CONFIGURATION
     ========================================== */}
  
  const settingSections = [
    { id: 'core', title: 'Core Settings', icon: Cog6ToothIcon, description: 'Essential bot configuration.' },
    { id: 'discord', title: 'Discord Integration', icon: ServerIcon, description: 'Server channels and roles.' },
    { id: 'modstrings', title: 'ModString Configuration', icon: CommandLineIcon, description: 'Configure ModString execution scope.' },
    { id: 'monitoring', title: 'AI Monitoring', icon: EyeIcon, description: 'AI detection, flags, and model configuration.' },
    { id: 'permissions', title: 'Permissions & Roles', icon: ShieldCheckIcon, description: 'Configure moderator roles and permissions.' },
    { id: 'mental_health', title: 'Mental Health', icon: HeartIcon, description: 'Support system configuration.' },
    { id: 'spotlight', title: 'Spotlight Gate', icon: LightBulbIcon, description: 'User verification and screening system.' },
    { id: 'advanced', title: 'Advanced', icon: Cog6ToothIcon, description: 'Expert options and tuning.' }
  ];

  {/* ==========================================
      DATA FETCHING FUNCTIONS
     ========================================== */}
  
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';

      const settingsResponse = await fetch(`${apiBase}/api/settings/`);
      if (!settingsResponse.ok) throw new Error('Failed to fetch settings');
      const settingsData = await settingsResponse.json();
      
      const currentSettings = {};
      if (settingsData.settings) {
        Object.values(settingsData.settings).forEach(section => {
          if (section.settings) {
            Object.entries(section.settings).forEach(([key, setting]) => {
              currentSettings[key] = setting.current_value;
            });
          }
        });
      }
      
      setSettings(currentSettings);
      
      const guildInfo = settingsData.metadata?.guild_info || {};
      setChannels(guildInfo.channels?.text_channels || []);
      setCategories(guildInfo.channels?.categories || []);
      setRoles(guildInfo.roles || []);

      const historyResponse = await fetch(`${apiBase}/api/settings/history`);
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setSettingsHistory(historyData.history || []);
      }

    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  {/* ==========================================
      SETTINGS CHANGE HANDLERS
     ========================================== */}
  
  const handleSettingChange = (key, value) => {
    setPendingChanges(prev => ({ ...prev, [key]: value }));
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveChanges = async () => {
    if (Object.keys(pendingChanges).length === 0) return;

    setSaving(true);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';

      const response = await fetch(`${apiBase}/api/settings/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pendingChanges)
      });

      if (!response.ok) throw new Error('Failed to save settings');

      setPendingChanges({});
      await fetchAllData();
      
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDiscardChanges = () => {
    setPendingChanges({});
    fetchAllData();
  };

  const handleImport = async () => {
    try {
      const parsedData = JSON.parse(importData);
      if (parsedData.settings) {
        setPendingChanges(parsedData.settings);
        setSettings(prev => ({ ...prev, ...parsedData.settings }));
      }
      setShowImportModal(false);
      setImportData('');
    } catch (error) {
      alert('Invalid JSON format');
    }
  };

  const handleExport = () => {
    const exportData = { settings, exported_at: new Date().toISOString(), version: '1.0' };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `watch-tower-settings-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const testSpotlightGate = async () => {
    try {
      const testUserId = "123456789012345678";
      const testKey = `test-${Date.now()}`;
      const testUrl = `/spotlight/${testUserId}/${testKey}`;
      window.open(testUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    } catch (error) {
      console.error('Error opening test Spotlight Gate:', error);
      alert('Error opening test: ' + error.message);
    }
  };

  {/* ==========================================
      HELPER & UI COMPONENTS
     ========================================== */}
  
  const getChannelName = (channelId) => channels.find(c => String(c.id) === String(channelId))?.name || 'Unknown Channel';
  const getRoleName = (roleId) => roles.find(r => String(r.id) === String(roleId))?.name || 'Unknown Role';

  const StylishNumberInput = ({ value, onChange, min, max }) => (
    <div className="flex items-center gap-2">
      <button onClick={() => onChange(Math.max(min, (value || 0) - 1))} className="p-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"><MinusIcon className="h-4 w-4 text-white" /></button>
      <input type="text" value={value} onChange={(e) => { let v = parseInt(e.target.value, 10); if(isNaN(v)) v=min; onChange(Math.max(min, Math.min(max, v)))}} className="input text-center w-20 font-semibold" />
      <button onClick={() => onChange(Math.min(max, (value || 0) + 1))} className="p-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"><PlusIcon className="h-4 w-4 text-white" /></button>
    </div>
  );

  const Selector = ({ value, onChange, placeholder, items, nameKey, idKey, prefix }) => (
    <select value={value || ''} onChange={(e) => onChange(e.target.value || null)} className="input-select">
      <option value="">{placeholder}</option>
      {items.map(item => <option key={item[idKey]} value={item[idKey]}>{prefix}{item[nameKey]}</option>)}
    </select>
  );
  const ChannelSelector = (props) => <Selector {...props} items={channels} nameKey="name" idKey="id" prefix="#" />;
  const RoleSelector = (props) => <Selector {...props} items={roles} nameKey="name" idKey="id" prefix="@" />;

  const MultiSelector = ({ values = [], onChange, items, nameKey, idKey, placeholder, renderItem }) => (
    <div className="space-y-2">
      {values.map((itemId) => (
        <div key={itemId} className="flex items-center gap-2 px-3 py-2 bg-gray-800/50 rounded-lg">
          <div className="flex-1 font-medium text-gray-100">{renderItem(itemId)}</div>
          <button onClick={() => onChange(values.filter(id => id !== itemId))} className="p-1 text-red-400 hover:bg-red-500/20 rounded-full"><XCircleIcon className="h-4 w-4" /></button>
        </div>
      ))}
      <select value="" onChange={(e) => { const itemId = e.target.value; if (itemId && !values.includes(itemId)) onChange([...values, itemId]); e.target.value = ""; }} className="input-select">
        <option value="">{placeholder}</option>
        {items.filter(item => !values.includes(String(item[idKey]))).map(item => <option key={item[idKey]} value={item[idKey]}>{item[nameKey]}</option>)}
      </select>
    </div>
  );
  const MultiChannelSelector = (props) => <MultiSelector {...props} items={channels} nameKey="name" idKey="id" placeholder="+ Add Channel" renderItem={id => `#${getChannelName(id)}`} />;
  const MultiCategorySelector = (props) => <MultiSelector {...props} items={categories} nameKey="name" idKey="id" placeholder="+ Add Category" renderItem={id => categories.find(c => String(c.id) === String(id))?.name || 'Unknown'} />;
  const MultiRoleSelector = (props) => <MultiSelector {...props} items={roles} nameKey="name" idKey="id" placeholder="+ Add Role" renderItem={id => `@${getRoleName(id)}`} />;

  const SettingField = ({ title, description, required, children }) => (
    <div>
      <h4 className="text-gray-100 font-medium">{title}{required && <span className="text-red-400 ml-1">*</span>}</h4>
      {description && <p className="text-sm text-gray-400 mt-1 mb-3">{description}</p>}
      <div className={description ? "" : "mt-2"}>{children}</div>
    </div>
  );

  {/* ==========================================
      SETTINGS SECTIONS RENDERERS
     ========================================== */}
  
  const renderCoreSettings = () => (
    <div className="space-y-6">
      <SettingField title="Bot Enabled" description="Enable or disable the Watch Tower moderation system" required><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.enabled ?? false} onChange={(e) => handleSettingChange('enabled', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
      <SettingField title="Time Window (Hours)" description="How many hours of message history to analyze for patterns"><StylishNumberInput value={settings.time_window_hours ?? 24} onChange={(v) => handleSettingChange('time_window_hours', v)} min={1} max={168} /></SettingField>
      <SettingField title="Messages Per Case" description="Number of flagged messages before creating a moderation case"><StylishNumberInput value={settings.messages_per_case ?? 10} onChange={(v) => handleSettingChange('messages_per_case', v)} min={1} max={50} /></SettingField>
    </div>
  );

  const renderDiscordSettings = () => (
    <div className="space-y-6">
      <SettingField title="Report Channel" description="Channel where flagged messages are reported" required><ChannelSelector value={settings.report_channel} onChange={(id) => handleSettingChange('report_channel', id)}/></SettingField>
      <SettingField title="Mod Action Report Channel" description="Channel for moderation action logs"><ChannelSelector value={settings.mod_action_report_channel} onChange={(id) => handleSettingChange('mod_action_report_channel', id)}/></SettingField>
      <SettingField title="Mod Chat Channel" description="Private channel for moderator discussions"><ChannelSelector value={settings.mod_chat_channel} onChange={(id) => handleSettingChange('mod_chat_channel', id)}/></SettingField>
    </div>
  );

  const renderModStringSettings = () => (
    <div className="space-y-6">
      <SettingField title="ModString Enabled" description="Enable ModString pattern matching system"><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.modstring_enabled ?? true} onChange={(e) => handleSettingChange('modstring_enabled', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
      <SettingField title="ModString Scope" description="Which channels ModStrings should monitor">
        <select value={settings.modstring_scope ?? 'all_channels'} onChange={(e) => handleSettingChange('modstring_scope', e.target.value)} className="input-select">
          <option value="all_channels">All Channels</option><option value="specific_channels">Specific Channels</option><option value="categories">Specific Categories</option>
        </select>
      </SettingField>
      {settings.modstring_scope === 'specific_channels' && <SettingField title="ModString Channels" description="Channels where ModStrings should be active"><MultiChannelSelector values={Array.isArray(settings.modstring_channels) ? settings.modstring_channels.map(String) : []} onChange={(ids) => handleSettingChange('modstring_channels', ids)} /></SettingField>}
      {settings.modstring_scope === 'categories' && <SettingField title="ModString Categories" description="Categories where ModStrings should be active"><MultiCategorySelector values={Array.isArray(settings.modstring_categories) ? settings.modstring_categories.map(String) : []} onChange={(ids) => handleSettingChange('modstring_categories', ids)} /></SettingField>}
    </div>
  );

  const renderMonitoringSettings = () => (
    <div className="space-y-6">
      <SettingField title="AI Monitoring Enabled" description="Enable AI-powered message analysis"><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.ai_enabled ?? true} onChange={(e) => handleSettingChange('ai_enabled', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
      <SettingField title="AI Model URL" description="Ollama server endpoint for AI processing"><input type="url" value={settings.ai_model_url ?? 'http://localhost:11434'} onChange={(e) => handleSettingChange('ai_model_url', e.target.value)} className="input" placeholder="http://localhost:11434" /></SettingField>
      <SettingField title="Watch Channels" description="Channels to monitor with AI"><MultiChannelSelector values={Array.isArray(settings.watch_channels) ? settings.watch_channels.map(String) : []} onChange={(ids) => handleSettingChange('watch_channels', ids)} /></SettingField>
      <SettingField title="Flag Threshold" description="AI confidence threshold for flagging messages (1-10)"><StylishNumberInput value={settings.flag_threshold ?? 7} onChange={(v) => handleSettingChange('flag_threshold', v)} min={1} max={10} /></SettingField>
    </div>
  );

  const renderPermissionsSettings = () => (
    <div className="space-y-6">
      <SettingField title="Moderator Roles" description="Roles that can access moderation features"><MultiRoleSelector values={Array.isArray(settings.moderator_roles) ? settings.moderator_roles.map(String) : []} onChange={(ids) => handleSettingChange('moderator_roles', ids)} /></SettingField>
      <SettingField title="Admin Roles" description="Roles with full administrative access"><MultiRoleSelector values={Array.isArray(settings.admin_roles) ? settings.admin_roles.map(String) : []} onChange={(ids) => handleSettingChange('admin_roles', ids)} /></SettingField>
      <SettingField title="Bypass Roles" description="Roles that bypass all moderation checks"><MultiRoleSelector values={Array.isArray(settings.bypass_roles) ? settings.bypass_roles.map(String) : []} onChange={(ids) => handleSettingChange('bypass_roles', ids)} /></SettingField>
    </div>
  );

  const renderMentalHealthSettings = () => (
    <div className="space-y-6">
      <SettingField title="Mental Health Support Enabled" description="Enable mental health monitoring"><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.mental_health_enabled ?? false} onChange={(e) => handleSettingChange('mental_health_enabled', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
      {settings.mental_health_enabled && (
        <>
          <SettingField title="Mental Health Alert Channel" description="Channel for alerts"><ChannelSelector value={settings.mental_health_alert_channel} onChange={(id) => handleSettingChange('mental_health_alert_channel', id)} /></SettingField>
          <SettingField title="Support Template" description="Template message for support"><textarea value={settings.mental_health_template ?? ''} onChange={(e) => handleSettingChange('mental_health_template', e.target.value)} className="input h-24" placeholder="Template..."/></SettingField>
        </>
      )}
    </div>
  );

  const renderSpotlightSettings = () => {
    const handleSpotlightChange = (key, value) => handleSettingChange(`spotlight_${key}`, value);
    const getQuestions = () => { try { const q = settings.spotlight_questions || '[]'; return typeof q === 'string' ? JSON.parse(q) : q; } catch { return []; } };
    const setQuestions = (q) => handleSpotlightChange('questions', JSON.stringify(q));
    
    const handleQuestionChange = (i, field, value) => { const q = getQuestions(); q[i][field] = value; setQuestions(q); };
    const handleOptionChange = (qI, oI, value) => { const q = getQuestions(); q[qI].options[oI] = value; setQuestions(q); };
    const addQuestion = () => setQuestions([...getQuestions(), { id: `q${Date.now()}`, text: '', options: ['', '', '', ''], correct_answer: '' }]);
    const removeQuestion = (i) => setQuestions(getQuestions().filter((_, idx) => idx !== i));
    
    const questions = getQuestions();

    return (
      <div className="space-y-8">
        <div className="card border-l-4 border-yellow-500 bg-yellow-500/5 p-6 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-yellow-400 flex items-center gap-2"><PlayIcon className="h-5 w-5" /> Test Spotlight Gate</h3>
            <p className="text-sm text-gray-400 mt-1">Preview the verification wizard with your current settings.</p>
          </div>
          <button onClick={testSpotlightGate} className="btn-primary flex items-center gap-2"><EyeIcon className="h-4 w-4" /> Open Preview</button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          <SettingField title="Enable Spotlight Gate" description="Enable the user verification system" required><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.spotlight_enabled ?? false} onChange={(e) => handleSpotlightChange('enabled', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
          <SettingField title="Verified Role" description="Role to grant upon successful verification"><RoleSelector placeholder="Select verified role..." value={settings.spotlight_verified_role_id} onChange={(id) => handleSpotlightChange('verified_role_id', id)} /></SettingField>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          <SettingField title="Enable reCAPTCHA" description="Require users to complete reCAPTCHA"><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.spotlight_captcha_enabled ?? false} onChange={(e) => handleSpotlightChange('captcha_enabled', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
          {settings.spotlight_captcha_enabled && (
            <div className="space-y-6">
              <SettingField title="reCAPTCHA Site Key"><input type="text" value={settings.spotlight_recaptcha_site_key || ''} onChange={(e) => handleSpotlightChange('recaptcha_site_key', e.target.value)} className="input" placeholder="6Lc..." /></SettingField>
              <SettingField title="reCAPTCHA Secret Key"><input type="password" value={settings.spotlight_recaptcha_secret_key || ''} onChange={(e) => handleSpotlightChange('recaptcha_secret_key', e.target.value)} className="input" placeholder="••••••••" /></SettingField>
            </div>
          )}
        </div>
        
        <SettingField title="Server Rules" description="Rules displayed to users (supports Markdown)"><textarea value={settings.spotlight_rules || ''} onChange={(e) => handleSpotlightChange('rules', e.target.value)} className="input h-48 font-mono text-sm" placeholder="# Welcome!" /></SettingField>
        <SettingField title="Passing Score" description="Correct answers required to pass"><StylishNumberInput value={settings.spotlight_passing_score ?? 3} onChange={(v) => handleSpotlightChange('passing_score', v)} min={1} max={questions.length || 1} /></SettingField>
        
        <div>
            <h4 className="text-gray-100 font-medium">Verification Questions</h4>
            <p className="text-sm text-gray-400 mt-1 mb-3">Questions to test users' understanding of the rules</p>
            <div className="space-y-4">
                {questions.map((q, qIndex) => (
                <div key={q.id || qIndex} className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-4"><h5 className="font-medium text-gray-100">Question {qIndex + 1}</h5><button onClick={() => removeQuestion(qIndex)} className="text-gray-400 hover:text-red-400 transition-colors text-sm font-medium">Remove</button></div>
                    <div className="space-y-3">
                    <input type="text" value={q.text} onChange={(e) => handleQuestionChange(qIndex, 'text', e.target.value)} className="input" placeholder="Enter question text..."/>
                    <div className="space-y-3 pl-2">
                        {q.options.map((opt, oIndex) => (
                        <label key={oIndex} className="flex items-center gap-3 cursor-pointer group">
                            <input type="radio" name={`correct-${q.id}`} checked={q.correct_answer === opt} onChange={() => handleQuestionChange(qIndex, 'correct_answer', opt)} className="hidden"/>
                            <div className={`w-5 h-5 rounded-full flex items-center justify-center border-2 transition-all ${q.correct_answer === opt ? 'border-yellow-500 bg-yellow-500/20' : 'border-gray-600 group-hover:border-gray-500'}`}><div className={`w-2.5 h-2.5 rounded-full transition-all ${q.correct_answer === opt ? 'bg-yellow-500' : 'bg-transparent'}`}></div></div>
                            <input type="text" value={opt} onChange={(e) => handleOptionChange(qIndex, oIndex, e.target.value)} className="input flex-1" placeholder={`Option ${oIndex + 1}`}/>
                        </label>
                        ))}
                    </div>
                    </div>
                </div>
                ))}
                <button onClick={addQuestion} className="btn-secondary w-full mt-4">+ Add Question</button>
            </div>
        </div>
      </div>
    );
  };
  
  const renderAdvancedSettings = () => (
    <div className="space-y-6">
      <SettingField title="Debug Mode" description="Enable detailed logging"><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.debug_mode ?? false} onChange={(e) => handleSettingChange('debug_mode', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
      <SettingField title="API Rate Limit" description="API requests per minute"><StylishNumberInput value={settings.api_rate_limit ?? 60} onChange={(v) => handleSettingChange('api_rate_limit', v)} min={10} max={1000} /></SettingField>
      <SettingField title="Auto Backup" description="Automatically backup settings"><label className="relative inline-flex items-center cursor-pointer"><input type="checkbox" checked={settings.auto_backup ?? true} onChange={(e) => handleSettingChange('auto_backup', e.target.checked)} className="sr-only peer"/><div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-500"></div></label></SettingField>
      <SettingField title="Max Case Age (Days)" description="Auto-archive old cases"><StylishNumberInput value={settings.max_case_age_days ?? 365} onChange={(v) => handleSettingChange('max_case_age_days', v)} min={30} max={3650} /></SettingField>
    </div>
  );

  const renderSection = () => {
    switch (activeSection) {
      case 'core': return renderCoreSettings(); case 'discord': return renderDiscordSettings(); case 'modstrings': return renderModStringSettings();
      case 'monitoring': return renderMonitoringSettings(); case 'permissions': return renderPermissionsSettings(); case 'mental_health': return renderMentalHealthSettings();
      case 'spotlight': return renderSpotlightSettings(); case 'advanced': return renderAdvancedSettings(); default: return renderCoreSettings();
    }
  };

  const ImportModal = () => (<div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"><div className="card w-full max-w-2xl mx-4"><h3 className="text-lg font-semibold mb-4 text-yellow-400">Import Settings</h3><p className="text-gray-400 mb-4">Paste exported JSON below. This will replace current settings on save.</p><textarea value={importData} onChange={(e) => setImportData(e.target.value)} className="input w-full h-64 font-mono text-sm" placeholder="Paste JSON..."/>
  <div className="flex justify-end gap-3 mt-4"><button onClick={() => { setShowImportModal(false); setImportData(''); }} className="btn-secondary">Cancel</button><button onClick={handleImport} disabled={!importData.trim()} className="btn-primary">Import Settings</button></div></div></div>);
  const HistoryModal = () => (<div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"><div className="card w-full max-w-4xl mx-4 max-h-[80vh] flex flex-col"><h3 className="text-lg font-semibold mb-4 text-yellow-400">Settings History</h3><div className="overflow-y-auto flex-grow">{settingsHistory.length === 0 ? <div className="text-center text-gray-400 py-8"><ClockIcon className="h-12 w-12 mx-auto mb-4 opacity-50" /><p>No changes recorded.</p></div> : <div className="space-y-3">{settingsHistory.map((c, i) => (<div key={i} className="card-secondary p-4"><div className="flex items-center justify-between mb-2"><div className="text-sm font-medium text-gray-100">{Object.keys(c.changes).length} setting(s) changed</div><div className="text-xs text-gray-400">{new Date(c.timestamp).toLocaleString()}</div></div><div className="text-xs text-gray-400">By: {c.updated_by}</div>
  <div className="mt-2 space-y-1">{Object.entries(c.changes).map(([key, val]) => (<div key={key} className="text-xs"><span className="text-gray-300">{key}:</span><span className="text-red-400 ml-1">{JSON.stringify(val.old)}</span><span className="text-gray-500 mx-1">→</span><span className="text-green-400">{JSON.stringify(val.new)}</span></div>))}</div></div>))}</div>}</div><div className="flex justify-end mt-4"><button onClick={() => setShowHistoryModal(false)} className="btn-secondary">Close</button></div></div></div>);

  if (loading) return (<div className="p-6"><div className="card p-8 text-center"><ArrowPathIcon className="h-8 w-8 animate-spin mx-auto mb-4 text-yellow-400" /><p className="text-gray-400">Loading settings...</p></div></div>);
 
  return (
    <div className="p-6 space-y-6">
      <div className="card border-t-2 border-yellow-400/50"><div className="px-6 py-4 flex items-center justify-between"><div><h1 className="text-2xl font-bold text-yellow-400">Settings</h1><p className="text-sm text-gray-400 mt-1">Configure Watch Tower moderation system</p></div><div className="flex items-center gap-3"><button onClick={() => setShowHistoryModal(true)} className="btn-secondary flex items-center gap-2"><ClockIcon className="h-4 w-4" />History</button><button onClick={() => setShowImportModal(true)} className="btn-secondary flex items-center gap-2"><DocumentArrowUpIcon className="h-4 w-4" />Import</button><button onClick={handleExport} className="btn-secondary flex items-center gap-2"><DocumentArrowDownIcon className="h-4 w-4" />Export</button></div></div></div>
      {Object.keys(pendingChanges).length > 0 && (<div className="card border-l-4 border-yellow-400 bg-yellow-400/10"><div className="flex items-center justify-between p-4"><div className="flex items-center gap-3"><ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" /><div><p className="font-medium text-yellow-300">You have {Object.keys(pendingChanges).length} unsaved change(s)</p><p className="text-sm text-yellow-400/80">Save your changes or they will be lost.</p></div></div><div className="flex items-center gap-3"><button onClick={handleDiscardChanges} className="btn-secondary flex items-center gap-2"><ArrowUturnLeftIcon className="h-4 w-4" />Discard</button><button onClick={handleSaveChanges} disabled={saving} className="btn-primary flex items-center gap-2">{saving ? <><ArrowPathIcon className="h-4 w-4 animate-spin" /> Saving...</> : <><CheckCircleIcon className="h-4 w-4" /> Save Changes</>}</button></div></div></div>)}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1"><nav className="space-y-1">{settingSections.map((s) => (<button key={s.id} onClick={() => setActiveSection(s.id)} className={`w-full text-left px-3 py-2 rounded-lg flex items-center gap-3 transition-colors ${activeSection === s.id ? 'bg-gray-700/50 text-yellow-300' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'}`}><s.icon className="h-5 w-5" /><div className="font-medium">{s.title}</div></button>))}</nav></div>
        <div className="lg:col-span-3"><div className="card p-6"><div className="mb-6 border-b border-gray-700/50 pb-4"><h2 className="text-xl font-semibold text-gray-100">{settingSections.find(s => s.id === activeSection)?.title}</h2><p className="text-gray-400 mt-1">{settingSections.find(s => s.id === activeSection)?.description}</p></div>{renderSection()}</div></div>
      </div>
      {showImportModal && <ImportModal />}
      {showHistoryModal && <HistoryModal />}
    </div>
  );
};

export default Settings;