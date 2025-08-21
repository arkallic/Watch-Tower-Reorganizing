import React, { useState } from 'react';
import { motion } from 'framer-motion';

const ChannelConfigPage = ({ data, updateData, guildData, nextStep, prevStep }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleChannelChange = (field, channelId) => {
    updateData('channels', { [field]: channelId });
  };

  const filteredChannels = guildData.channels.filter(channel =>
    channel.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const ChannelSelector = ({ value, onChange, placeholder }) => (
    <div className="channel-selector">
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className="setting-input"
      >
        <option value="">{placeholder}</option>
        {filteredChannels.map(channel => (
          <option key={channel.id} value={channel.id}>
            #{channel.name} {channel.category && `(${channel.category})`}
          </option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="setup-page-content">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <img src="/images/logo.png" alt="Watch Tower" className="header-logo" />
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
        <h2>Channel Configuration</h2>
        <p className="section-description">
          Configure which channels Watch Tower uses for reporting and monitoring. 
          These channels are essential for the bot's communication with your moderation team.
        </p>

        {guildData.channels.length === 0 ? (
          <div className="loading-spinner">Loading channels...</div>
        ) : (
          <div className="settings-grid">
            <div className="setting-item required">
              <label className="setting-label">Report Channel *</label>
              <ChannelSelector
                value={data.channels.reportChannel}
                onChange={(value) => handleChannelChange('reportChannel', value)}
                placeholder="Select report channel"
              />
              <p className="setting-description">
                Where moderation reports and flagged messages are sent. This is required 
                for the bot to function properly.
              </p>
            </div>

            <div className="setting-item">
              <label className="setting-label">Mod Action Report Channel</label>
              <ChannelSelector
                value={data.channels.modActionReportChannel}
                onChange={(value) => handleChannelChange('modActionReportChannel', value)}
                placeholder="Select mod action channel"
              />
              <p className="setting-description">
                Channel for logging moderation actions like warns, timeouts, and bans. 
                Helps track moderator activity.
              </p>
            </div>

            <div className="setting-item">
              <label className="setting-label">Mod Chat Channel</label>
              <ChannelSelector
                value={data.channels.modChatChannel}
                onChange={(value) => handleChannelChange('modChatChannel', value)}
                placeholder="Select mod chat channel"
              />
              <p className="setting-description">
                Private channel for moderator discussions and coordination. 
                Used for internal mod team communication.
              </p>
            </div>
          </div>
        )}
      </motion.div>

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

export default ChannelConfigPage;