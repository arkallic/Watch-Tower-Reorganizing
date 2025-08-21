// dashboard/frontend/src/pages/Spotlight.jsx

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  LightBulbIcon, 
  ArrowPathIcon, 
  ExclamationTriangleIcon, 
  UserIcon, 
  ClockIcon, 
  NoSymbolIcon, 
  CheckCircleIcon,
  XMarkIcon,
  EyeIcon,
  ShieldCheckIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

{/* ==========================================
    UTILITY COMPONENTS
   ========================================== */}

const StatCard = ({ title, value, subtext, icon: Icon, color = "text-white" }) => (
  <div className="card p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-400 mb-1">{title}</p>
        <p className={`text-3xl font-bold ${color}`}>{value}</p>
        {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
      </div>
      {Icon && <Icon className="h-8 w-8 text-gray-400" />}
    </div>
  </div>
);

const RedFlagIcon = ({ flag }) => {
  const iconMap = {
    'New Account': <ClockIcon className="w-3 h-3" />,
    'No Avatar': <NoSymbolIcon className="w-3 h-3" />,
    'Account created less than 48 hours ago': <ClockIcon className="w-3 h-3" />,
    'Using default Discord avatar': <NoSymbolIcon className="w-3 h-3" />
  };
  return iconMap[flag] || <ExclamationCircleIcon className="w-3 h-3" />;
};

{/* ==========================================
    MAIN SPOTLIGHT COMPONENT
   ========================================== */}

const Spotlight = () => {
  
  {/* ==========================================
      STATE MANAGEMENT
     ========================================== */}
  
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('review');
  const [selectedUser, setSelectedUser] = useState(null);
  const [processingDecision, setProcessingDecision] = useState(null);
  const [expandedUser, setExpandedUser] = useState(null);

  {/* ==========================================
      DATA FETCHING
     ========================================== */}
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      
      const response = await fetch(`${apiBase}/api/pagedata/spotlight`);
      if (!response.ok) throw new Error("Failed to fetch Spotlight data");
      
      const data = await response.json();
      setSummary(data.summary);
      setHistory(data.history?.history || []);
    } catch (err) {
      setError(err.message);
      console.error('Spotlight data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  {/* ==========================================
      COMPUTED VALUES
     ========================================== */}
  
  const reviewQueue = useMemo(() => 
    history.filter(h => h.status === 'Pending'), [history]
  );

  const recentActivity = useMemo(() => 
    history.slice(0, 10), [history]
  );

  const PIE_COLORS = ['#22c55e', '#f97316', '#ef4444', '#3b82f6'];

  {/* ==========================================
      HELPER FUNCTIONS
     ========================================== */}
  
  const getStatusBadge = (status) => {
    const styles = {
      'Passed': 'bg-green-500/20 text-green-300 border-green-500/30',
      'Pending': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      'Rejected': 'bg-red-500/20 text-red-300 border-red-500/30',
      'Manually Approved': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    };
    return styles[status] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  {/* ==========================================
      ACTION HANDLERS
     ========================================== */}
  
  const handleDecision = async (userId, decision) => {
    setProcessingDecision(userId);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';

      const response = await fetch(`${apiBase}/api/spotlight/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userId,
          decision: decision,
          moderatorId: 'dashboard_user' // You could get this from auth context
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process decision');
      }

      const result = await response.json();
      
      if (result.success) {
        // Refresh data to reflect changes
        await fetchData();
        
        // Show success message
        alert(`User ${decision === 'approve' ? 'approved' : 'rejected'} successfully!`);
      } else {
        throw new Error(result.message || 'Decision failed');
      }
    } catch (err) {
      console.error('Decision error:', err);
      alert(`Failed to ${decision} user: ${err.message}`);
    } finally {
      setProcessingDecision(null);
    }
  };

  const toggleUserExpansion = (userId) => {
    setExpandedUser(expandedUser === userId ? null : userId);
  };

  {/* ==========================================
      LOADING AND ERROR STATES
     ========================================== */}
  
  if (loading) {
    return (
      <div className="p-6 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400 mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading Spotlight data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="card border-l-4 border-red-500 bg-red-500/10 p-6">
          <div className="flex items-center gap-3">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-400" />
            <div>
              <h3 className="text-lg font-semibold text-red-400">Error Loading Spotlight Data</h3>
              <p className="text-red-300 mt-1">{error}</p>
              <button 
                onClick={fetchData}
                className="btn-secondary mt-3 flex items-center gap-2"
              >
                <ArrowPathIcon className="w-4 h-4" />
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  {/* ==========================================
      MAIN RENDER
     ========================================== */}
  
  return (
    <div className="p-6 space-y-6">
      
      {/* ==========================================
          HEADER
         ========================================== */}
      
      <div className="card border-t-2 border-yellow-400/50">
        <div className="px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-yellow-400 flex items-center gap-3">
              <LightBulbIcon className="h-8 w-8" />
              Spotlight Gate
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Monitor new user verification and screening activity
            </p>
          </div>
          <button 
            onClick={fetchData} 
            className="btn-secondary flex items-center gap-2"
            disabled={loading}
          >
            <ArrowPathIcon className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* ==========================================
          OVERVIEW DESCRIPTION
         ========================================== */}
      
      <div className="card-secondary p-6">
        <div className="flex items-start gap-4">
          <div className="bg-yellow-500/20 p-3 rounded-lg">
            <ShieldCheckIcon className="h-6 w-6 text-yellow-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-100 mb-2">How Spotlight Gate Works</h3>
            <p className="text-gray-300 leading-relaxed">
              The Spotlight Gate is an automated screening process for new members. When users join the server, 
              they receive a private verification channel with a QR code and link to complete verification. 
              The process includes reading server rules, answering comprehension questions, and completing security checks. 
              Failed attempts are queued here for manual review.
            </p>
          </div>
        </div>
      </div>

      {/* ==========================================
          STATISTICS GRID
         ========================================== */}
      
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard 
            title="Total Screened" 
            value={summary.total_screened || 0}
            icon={UserIcon}
            subtext="All time"
          />
          <StatCard 
            title="Pass Rate" 
            value={`${summary.pass_rate || 0}%`}
            icon={CheckCircleIcon}
            color={summary.pass_rate >= 70 ? "text-green-400" : summary.pass_rate >= 50 ? "text-yellow-400" : "text-red-400"}
            subtext="Automatic approvals"
          />
          <StatCard 
            title="Pending Review" 
            value={summary.pending_review || 0}
            icon={ClockIcon}
            color={summary.pending_review > 0 ? "text-yellow-400" : "text-green-400"}
            subtext="Require manual action"
          />
          <StatCard 
            title="Avg. Completion" 
            value={`${summary.avg_completion_time || 0}s`}
            icon={ExclamationCircleIcon}
            subtext="Time to complete"
          />
        </div>
      )}

      {/* ==========================================
          CHARTS SECTION
         ========================================== */}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Top Failed Questions Chart */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Most Failed Questions</h3>
          {summary?.top_failed_questions?.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={summary.top_failed_questions}>
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 12, fill: '#9ca3af' }}
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #4b5563',
                    borderRadius: '8px'
                  }} 
                />
                <Bar dataKey="fails" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-500 py-16">
              <ExclamationCircleIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No failed question data available yet</p>
            </div>
          )}
        </div>

        {/* Outcome Breakdown Pie Chart */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">Verification Outcomes</h3>
          {summary?.outcome_breakdown?.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie 
                  data={summary.outcome_breakdown} 
                  dataKey="value" 
                  nameKey="name" 
                  cx="50%" 
                  cy="50%" 
                  outerRadius={80} 
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {summary.outcome_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1f2937', 
                    border: '1px solid #4b5563',
                    borderRadius: '8px'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-500 py-16">
              <UserIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No outcome data available yet</p>
            </div>
          )}
        </div>
      </div>

      {/* ==========================================
          USER TABLE WITH TABS
         ========================================== */}
      
      <div className="card">
        
        {/* Tab Navigation */}
        <div className="border-b border-gray-700">
          <nav className="flex space-x-4 px-6">
            <button 
              onClick={() => setActiveTab('review')} 
              className={`py-4 px-2 border-b-2 text-sm font-medium flex items-center gap-2 transition-colors ${
                activeTab === 'review' 
                  ? 'border-yellow-400 text-yellow-400' 
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-300'
              }`}
            >
              Review Queue
              {reviewQueue.length > 0 && (
                <span className="bg-yellow-500/20 text-yellow-300 text-xs px-2 py-1 rounded-full">
                  {reviewQueue.length}
                </span>
              )}
            </button>
            <button 
              onClick={() => setActiveTab('history')} 
              className={`py-4 px-2 border-b-2 text-sm font-medium transition-colors ${
                activeTab === 'history' 
                  ? 'border-yellow-400 text-yellow-400' 
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-300'
              }`}
            >
              All History
            </button>
          </nav>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          {(activeTab === 'review' ? reviewQueue : history).length === 0 ? (
            <div className="text-center py-16">
              <UserIcon className="h-16 w-16 mx-auto mb-4 text-gray-400 opacity-50" />
              <h3 className="text-lg font-medium text-gray-300 mb-2">
                {activeTab === 'review' ? 'No pending reviews' : 'No verification history'}
              </h3>
              <p className="text-gray-500">
                {activeTab === 'review' 
                  ? 'All recent verifications have been processed' 
                  : 'No users have attempted verification yet'
                }
              </p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Time
                  </th>
                  {activeTab === 'review' && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Actions
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-gray-900 divide-y divide-gray-700">
                {(activeTab === 'review' ? reviewQueue : history).map((user) => (
                  <React.Fragment key={user.userId || user.user_id}>
                    <tr className="hover:bg-gray-800/50 transition-colors">
                      
                      {/* User Info */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <img 
                            src={user.avatar || '/default-avatar.png'} 
                            alt="" 
                            className="w-10 h-10 rounded-full"
                            onError={(e) => { e.target.src = '/default-avatar.png'; }}
                          />
                          <div>
                            <p className="font-medium text-white">{user.display_name}</p>
                            <p className="text-xs text-gray-400">@{user.username}</p>
                            
                            {/* Red Flags */}
                            {user.red_flags && user.red_flags.length > 0 && (
                              <div className="flex items-center gap-2 mt-1">
                                {user.red_flags.map((flag, index) => (
                                  <span 
                                    key={index} 
                                    title={flag} 
                                    className="flex items-center gap-1 text-xs text-red-400"
                                  >
                                    <RedFlagIcon flag={flag} />
                                    <span className="truncate max-w-24">{flag}</span>
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusBadge(user.status)}`}>
                          {user.status}
                        </span>
                      </td>

                      {/* Details */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        <div className="space-y-1">
                          {user.time_to_complete && (
                            <div className="text-xs">
                              <span className="text-gray-400">Completed in:</span> {user.time_to_complete.toFixed(1)}s
                            </div>
                          )}
                          {user.captcha_fails > 0 && (
                            <div className="text-xs text-yellow-400">
                              <span className="text-gray-400">CAPTCHA fails:</span> {user.captcha_fails}
                            </div>
                          )}
                          {user.failed_questions && user.failed_questions.length > 0 && (
                            <div className="text-xs text-red-400">
                              Failed {user.failed_questions.length} question{user.failed_questions.length !== 1 ? 's' : ''}
                            </div>
                          )}
                          {user.score !== undefined && user.total_questions && (
                            <div className="text-xs">
                              <span className="text-gray-400">Score:</span> {user.score}/{user.total_questions}
                            </div>
                          )}
                        </div>
                        
                        {/* Expandable Details Button */}
                        <button
                          onClick={() => toggleUserExpansion(user.userId || user.user_id)}
                          className="text-xs text-blue-400 hover:text-blue-300 mt-2"
                        >
                          {expandedUser === (user.userId || user.user_id) ? 'Hide' : 'Show'} details
                        </button>
                      </td>

                      {/* Time */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                        {formatTimeAgo(user.date || user.timestamp)}
                      </td>

                      {/* Actions (Review Queue Only) */}
                      {activeTab === 'review' && (
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex gap-2">
                            <button 
                              onClick={() => handleDecision(user.userId || user.user_id, 'approve')}
                              disabled={processingDecision === (user.userId || user.user_id)}
                              className="btn-tertiary text-xs bg-green-500/20 text-green-300 hover:bg-green-500/30 border border-green-500/30 disabled:opacity-50"
                            >
                              {processingDecision === (user.userId || user.user_id) ? '...' : 'Approve'}
                            </button>
                            <button 
                              onClick={() => handleDecision(user.userId || user.user_id, 'reject')}
                              disabled={processingDecision === (user.userId || user.user_id)}
                              className="btn-tertiary text-xs bg-red-500/20 text-red-300 hover:bg-red-500/30 border border-red-500/30 disabled:opacity-50"
                            >
                              {processingDecision === (user.userId || user.user_id) ? '...' : 'Reject'}
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>

                    {/* Expanded Details Row */}
                    {expandedUser === (user.userId || user.user_id) && (
                      <tr className="bg-gray-800/50">
                        <td colSpan={activeTab === 'review' ? 5 : 4} className="px-6 py-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            
                            {/* Failed Questions */}
                            {user.failed_questions && user.failed_questions.length > 0 && (
                              <div>
                                <h4 className="font-medium text-red-400 mb-2">Failed Questions:</h4>
                                <ul className="space-y-1 text-red-300">
                                  {user.failed_questions.map((question, index) => (
                                    <li key={index} className="text-xs">• {question}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Security Check Results */}
                            {user.abuse_checks && Object.keys(user.abuse_checks).length > 0 && (
                              <div>
                                <h4 className="font-medium text-blue-400 mb-2">Security Checks:</h4>
                                <div className="space-y-1">
                                  {Object.entries(user.abuse_checks).map(([check, result]) => (
                                    <div key={check} className="text-xs">
                                      <span className="text-gray-400">{check}:</span> 
                                      <span className="ml-1 text-gray-300">{result}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* User Info */}
                            <div>
                              <h4 className="font-medium text-gray-400 mb-2">User Information:</h4>
                              <div className="space-y-1 text-xs">
                                <div><span className="text-gray-400">User ID:</span> <span className="text-gray-300">{user.userId || user.user_id}</span></div>
                                <div><span className="text-gray-400">Username:</span> <span className="text-gray-300">{user.username}</span></div>
                                {user.passed !== undefined && (
                                  <div><span className="text-gray-400">Passed:</span> <span className={user.passed ? 'text-green-400' : 'text-red-400'}>{user.passed ? 'Yes' : 'No'}</span></div>
                                )}
                              </div>
                            </div>

                            {/* Red Flags Details */}
                            {user.red_flags && user.red_flags.length > 0 && (
                              <div>
                                <h4 className="font-medium text-red-400 mb-2">Red Flags:</h4>
                                <div className="space-y-1">
                                  {user.red_flags.map((flag, index) => (
                                    <div key={index} className="text-xs text-red-300 flex items-center gap-2">
                                      <RedFlagIcon flag={flag} />
                                      {flag}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

{/* ==========================================
    EXPORT
   ========================================== */}

export default Spotlight;