import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

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

  const selectUser = (user) => {
    updateData('approvalUser', user);
  };

  const skipApprovalUser = () => {
    updateData('approvalUser', null);
    nextStep();
  };

  const clearSelection = () => {
    updateData('approvalUser', null);
  };

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
        <h2>Bot Change Approval User</h2>
        <p className="section-description">
          Select a Discord user who will approve bot setting changes. When settings are modified 
          through the dashboard, this user will receive verification messages to approve the changes. 
          This is optional - if no user is selected, changes will be applied immediately.
        </p>

        <div className="user-search-container">
          <input
            type="text"
            placeholder="Search users by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="setting-input"
          />
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
          {filteredMembers.length > 0 ? (
            filteredMembers.slice(0, 50).map(user => (
              <div
                key={user.user_id}
                className={`user-item ${data.approvalUser?.user_id === user.user_id ? 'selected' : ''}`}
                onClick={() => selectUser(user)}
              >
                <img 
                  src={user.avatar_url} 
                  alt={user.username}
                  className="user-avatar"
                />
                <div className="user-info">
                  <h4>{user.display_name}</h4>
                  <p>@{user.username}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="no-results text-center py-8 text-gray-500">
                {guildData.members.length > 0 ? `No users found matching "${searchTerm}"` : "Loading server members..."}
            </div>
          )}
        </div>
      </motion.div>

      <div className="setup-navigation">
        <button onClick={prevStep} className="nav-button secondary">
          Back
        </button>
        <div className="nav-group">
          <button onClick={skipApprovalUser} className="nav-button secondary">
            Skip (No Approval)
          </button>
          <button 
            onClick={nextStep} 
            className="nav-button primary"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApprovalUserPage;