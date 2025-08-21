// dashboard/frontend/src/components/UserDetailsModal.jsx

import React, { useState, useEffect, useCallback } from 'react';
import {
  XMarkIcon, UserGroupIcon, ShieldCheckIcon, DocumentTextIcon, GlobeAltIcon, ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const UserDetailsModal = ({ isOpen, onClose, userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState(null);

  const fetchUserDetail = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      
      // FIX: Removed the incorrect "/proxy" segment from the URL
      const response = await fetch(`${apiBase}/api/users/${userId}`);

      if (!response.ok) {
        // IMPROVEMENT: Parse the JSON error from the backend for a better message
        const errorBody = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
        throw new Error(errorBody.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setUser(data);
    } catch (err) {
      console.error('Error fetching user details:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (isOpen && userId) {
      setActiveTab('overview');
      fetchUserDetail();
    }
  }, [isOpen, userId, fetchUserDetail]);

  const formatDate = (dateString) => dateString ? new Date(dateString).toLocaleString() : 'N/A';
  const getRiskBadgeColor = (riskLevel) => {
    if (riskLevel === 'Critical') return 'bg-purple-500/20 text-purple-300 border-purple-400/30';
    if (riskLevel === 'High') return 'bg-red-500/20 text-red-300 border-red-400/30';
    if (riskLevel === 'Medium') return 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30';
    return 'bg-green-500/20 text-green-300 border-green-400/30';
  };
  const getStatusColor = (status) => {
    if (status === 'online') return 'bg-green-400';
    if (status === 'idle') return 'bg-yellow-400';
    if (status === 'dnd') return 'bg-red-400';
    return 'bg-gray-500';
  };

  const renderContent = () => {
    if (loading) return <div className="text-center p-8 text-gray-400">Loading Details...</div>;
    if (error) return <div className="text-center py-12 text-red-400"><ExclamationTriangleIcon className="h-10 w-10 mx-auto mb-2" />Could not load user details: {error}</div>;
    if (!user) return <div className="text-center p-8 text-gray-400">User not found.</div>;
    
    switch (activeTab) {
      case 'overview':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card p-4 space-y-3">
              <h4 className="font-semibold text-gray-200">Account Information</h4>
              <p className="text-sm"><strong className="text-gray-400">Created:</strong> {formatDate(user.created_at)} ({user.account_age_days} days ago)</p>
              <p className="text-sm"><strong className="text-gray-400">Joined Server:</strong> {formatDate(user.joined_at)} ({user.server_tenure_days} days ago)</p>
            </div>
            <div className="card p-4 space-y-3">
              <h4 className="font-semibold text-gray-200">Activity Summary</h4>
              <p className="text-sm"><strong className="text-gray-400">AI Flags:</strong> {user.total_flags || 0}</p>
              <p className="text-sm"><strong className="text-gray-400">Deleted Messages:</strong> {user.total_deletions || 0}</p>
            </div>
            <div className="card p-4 lg:col-span-2">
              <h4 className="font-semibold text-gray-200 mb-3">Action Breakdown</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
                <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-yellow-300">{user.action_breakdown.warns}</p><p className="text-xs text-gray-400">Warns</p></div>
                <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-orange-300">{user.action_breakdown.timeouts}</p><p className="text-xs text-gray-400">Timeouts</p></div>
                <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-red-300">{user.action_breakdown.kicks}</p><p className="text-xs text-gray-400">Kicks</p></div>
                <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-red-200">{user.action_breakdown.bans}</p><p className="text-xs text-gray-400">Bans</p></div>
                <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-blue-300">{user.action_breakdown.mod_notes}</p><p className="text-xs text-gray-400">Notes</p></div>
              </div>
            </div>
          </div>
        );
      case 'cases':
        return (
          <div className="space-y-4">
            {(user.cases && user.cases.length > 0) ? user.cases.slice(0, 20).map(c => (
              <div key={c.case_number} className="card p-4">
                <div className="flex justify-between items-center"><span className="font-bold text-white">Case #{c.case_number}</span><span className="text-xs text-gray-400">{formatDate(c.created_at)}</span></div>
                <p className="text-sm"><strong className="text-gray-400">Action:</strong> {c.action_type}</p>
                <p className="text-sm"><strong className="text-gray-400">Reason:</strong> {c.reason || 'N/A'}</p>
                <p className="text-sm"><strong className="text-gray-400">Moderator:</strong> {c.moderator_name}</p>
                <span className={`text-xs px-2 py-1 rounded-full ${getRiskBadgeColor(c.severity)}`}>{c.severity}</span>
              </div>
            )) : <p className="text-gray-400 text-center p-4">No cases found for this user.</p>}
          </div>
        );
      case 'profile':
        return (
          <div className="card p-4">
            <h4 className="font-semibold text-gray-200 mb-3">Roles ({user.roles?.length || 0})</h4>
            <div className="flex flex-wrap gap-2">
              {user.roles && user.roles.map(role => (
                <span key={role.name} className="text-xs px-2 py-1 rounded-full border" style={{ backgroundColor: role.color === '#000000' ? '#4b5563' : role.color + '40', borderColor: role.color === '#000000' ? '#6b7280' : role.color, color: role.color === '#000000' ? '#f3f4f6' : role.color }}>{role.name}</span>
              ))}
            </div>
          </div>
        );
      case 'permissions':
          return (
            <div className="card p-4">
                <h4 className="font-semibold text-gray-200 mb-3">Key Permissions</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                    {user.permissions && Object.entries(user.permissions).map(([perm, has]) => (
                        <div key={perm} className="flex items-center gap-2"><span className={`w-2 h-2 rounded-full ${has ? 'bg-green-400' : 'bg-red-400'}`}></span><span className="text-gray-300 capitalize">{perm.replace(/_/g, ' ')}</span></div>
                    ))}
                </div>
            </div>
          );
      default: return null;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="card w-full max-w-3xl max-h-[90vh] flex flex-col">
        <div className="p-4 border-b border-gray-700 flex-shrink-0">
          <button onClick={onClose} className="absolute top-3 right-3 p-1 text-gray-400 hover:text-white"><XMarkIcon className="h-6 w-6" /></button>
          {user && (
            <div className="flex items-center gap-4">
              <div className="relative"><img src={user.avatar || `https://cdn.discordapp.com/embed/avatars/${(user.discriminator || 0) % 5}.png`} alt="" className="w-16 h-16 rounded-full" /><div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-gray-800 ${getStatusColor(user.status)}`}></div></div>
              <div>
                <h2 className="text-xl font-bold text-white">{user.display_name}</h2>
                <p className="text-sm text-gray-400">@{user.username}#{user.discriminator}</p>
                <div className="flex items-center gap-2 mt-2">
                    <span className={`text-xs px-2 py-1 rounded-full inline-block ${getRiskBadgeColor(user.risk_level || 'Low')}`}>{user.risk_level || 'Low'} Risk</span>
                    <span className="text-xs px-2 py-1 rounded-full inline-block bg-gray-700 text-gray-300">Score: {user.risk_score || 0}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="border-b border-gray-700 flex-shrink-0">
          <nav className="flex space-x-4 px-4">
            {[{ key: 'overview', label: 'Overview', icon: UserGroupIcon }, { key: 'cases', label: `Cases (${user?.cases?.length || 0})`, icon: DocumentTextIcon }, { key: 'profile', label: 'Discord Profile', icon: GlobeAltIcon }, { key: 'permissions', label: 'Permissions', icon: ShieldCheckIcon }].map(tab => (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)} className={`py-3 px-1 border-b-2 text-sm flex items-center gap-1.5 ${activeTab === tab.key ? 'border-yellow-400 text-yellow-400' : 'border-transparent text-gray-400 hover:text-white'}`}><tab.icon className="w-4 h-4" />{tab.label}</button>
            ))}
          </nav>
        </div>
        <div className="flex-1 overflow-y-auto p-6 bg-gray-900/50">{renderContent()}</div>
      </div>
    </div>
  );
};

export default UserDetailsModal;