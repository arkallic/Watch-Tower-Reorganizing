import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon, ExclamationTriangleIcon, ShieldCheckIcon, DocumentTextIcon, FireIcon, TrashIcon, GlobeAltIcon, ChatBubbleBottomCenterTextIcon
} from '@heroicons/react/24/outline';
import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';

const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="card p-4 text-center">
        <Icon className={`h-8 w-8 ${color} mx-auto mb-2`} />
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-sm text-gray-400">{title}</p>
    </div>
);

const UserProfile = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      const response = await fetch(`${apiBase}/api/pagedata/user-profile/${userId}`);

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({ detail: `API Error: ${response.status}` }));
        throw new Error(errorBody.detail);
      }
      const data = await response.json();
      setUserData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getRiskBadgeColor = (riskLevel) => {
    if (riskLevel === 'Critical') return 'bg-purple-500/20 text-purple-300';
    if (riskLevel === 'High') return 'bg-red-500/20 text-red-300';
    if (riskLevel === 'Medium') return 'bg-yellow-500/20 text-yellow-300';
    return 'bg-green-500/20 text-green-300';
  };
  const getStatusColor = (status) => {
    if (status === 'online') return 'bg-green-400';
    if (status === 'idle') return 'bg-yellow-400';
    if (status === 'dnd') return 'bg-red-400';
    return 'bg-gray-500';
  };
  const formatDate = (dateString) => dateString ? new Date(dateString).toLocaleString() : 'N/A';

  if (loading) return <div className="p-6 h-full flex items-center justify-center"><div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div></div>;
  if (error) return <div className="p-6 text-center text-red-400"><ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-2" />Error: {error}</div>;
  if (!userData) return <div className="p-6 text-center text-gray-400">No user data found.</div>;
  
  const { profile, stats, case_history, recent_deletions, activity_analytics } = userData;

  return (
    <div className="p-6 space-y-6">
      {/* --- HEADER --- */}
      <div className="card flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 border-t-2 border-yellow-400/50">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/users')} className="btn-secondary p-2"><ArrowLeftIcon className="w-5 h-5" /></button>
          <div className="relative">
            <img src={profile.avatar_url} alt="avatar" className="w-16 h-16 rounded-full" />
            <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-gray-800 ${getStatusColor(profile.status)}`}></div>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">{profile.display_name}</h1>
            <p className="text-sm text-gray-400">@{profile.username}#{profile.discriminator}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getRiskBadgeColor(stats.risk_info.level)}`}>{stats.risk_info.level} Risk</span>
          <span className="px-3 py-1 text-sm font-semibold rounded-full bg-gray-700 text-gray-300">Score: {stats.risk_info.score}</span>
        </div>
      </div>
      
      {/* --- OVERVIEW & STATS (NO TABS) --- */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Cases" value={stats.total_cases} icon={ShieldCheckIcon} color="text-blue-400" />
        <StatCard title="Open Cases" value={stats.open_cases} icon={ExclamationTriangleIcon} color="text-orange-400" />
        <StatCard title="Messages (30d)" value={stats.messages_30d} icon={ChatBubbleBottomCenterTextIcon} color="text-green-400" />
        <StatCard title="Deletions (72h)" value={stats.total_deletions} icon={TrashIcon} color="text-red-400" />
      </div>

      <div className="card p-4">
        <h3 className="font-semibold text-gray-100 mb-3">Action Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-yellow-300">{stats.action_breakdown.warns}</p><p className="text-xs text-gray-400">Warns</p></div>
            <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-orange-300">{stats.action_breakdown.timeouts}</p><p className="text-xs text-gray-400">Timeouts</p></div>
            <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-red-300">{stats.action_breakdown.kicks}</p><p className="text-xs text-gray-400">Kicks</p></div>
            <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-red-200">{stats.action_breakdown.bans}</p><p className="text-xs text-gray-400">Bans</p></div>
            <div className="bg-gray-700/50 p-2 rounded-lg"><p className="text-xl font-bold text-blue-300">{stats.action_breakdown.mod_notes}</p><p className="text-xs text-gray-400">Notes</p></div>
        </div>
      </div>

      {/* --- ACTIVITY ANALYTICS --- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-4">
          <h3 className="font-semibold text-gray-100 mb-3">Activity Heatmap (Last Year)</h3>
          <div className="heatmap-container"><CalendarHeatmap startDate={new Date(new Date().setFullYear(new Date().getFullYear() - 1))} endDate={new Date()} values={activity_analytics.heatmap_data} classForValue={(value) => !value ? 'color-empty' : `color-scale-${Math.min(value.count, 4)}`} tooltipDataAttrs={value => ({ 'data-tip': value.date ? `${value.date}: ${value.count} messages` : 'No activity' })} /></div>
        </div>
        <div className="card p-4">
          <h3 className="font-semibold text-gray-100 mb-3 flex items-center gap-2"><FireIcon className="w-5 h-5 text-yellow-400"/>Most Active Channels</h3>
          <div className="space-y-2">
            {activity_analytics.top_channels.length > 0 ? activity_analytics.top_channels.map(ch => (
              <div key={ch.name} className="flex justify-between items-center card-secondary p-2"><span className="text-white font-medium">#{ch.name}</span><span className="text-gray-300">{ch.count} msgs</span></div>
            )) : <p className="text-center text-gray-500 py-4">No message activity recorded.</p>}
          </div>
        </div>
      </div>
      
      {/* --- CASE HISTORY & DELETIONS --- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-4">
            <h3 className="font-semibold text-gray-100 mb-4">Case History ({case_history.length})</h3>
            <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2">
                {case_history.length > 0 ? case_history.map(c => (
                <div key={c.case_number} className="card-secondary p-3">
                    <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-white">Case #{c.case_number} - {c.action_type}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getRiskBadgeColor(c.severity)}`}>{c.severity}</span>
                    </div>
                    <p className="text-sm text-gray-300 italic">"{c.reason || 'No reason provided.'}"</p>
                    <div className="text-xs text-gray-500 mt-2 flex justify-between">
                        <span>By: {c.moderator_name}</span>
                        <span>On: {formatDate(c.created_at)}</span>
                    </div>
                </div>
                )) : <p className="text-gray-500 text-center p-8">No cases found for this user.</p>}
            </div>
        </div>
        <div className="card p-4">
            <h3 className="font-semibold text-gray-100 mb-4">Recent Deleted Messages ({recent_deletions.length})</h3>
            <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2">
                {recent_deletions.length > 0 ? recent_deletions.map(msg => (
                <div key={msg.message_id} className="card-secondary p-3">
                    <p className="text-sm text-gray-300 italic">"{msg.content}"</p>
                    <div className="text-xs text-gray-500 mt-2 flex justify-between">
                        <span>In: #{msg.channel_name}</span>
                        <span>Deleted at: {formatDate(msg.deleted_at)}</span>
                    </div>
                </div>
                )) : <p className="text-gray-500 text-center p-8">No recently deleted messages found.</p>}
            </div>
        </div>
      </div>

      {/* --- DISCORD PROFILE INFO --- */}
      <div className="card p-4">
        <h3 className="font-semibold text-gray-100 mb-3">Discord Profile</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h4 className="font-semibold text-gray-200 mb-3 text-sm">Account Information</h4>
                <div className="space-y-2 text-sm">
                    <p><strong className="text-gray-400 w-28 inline-block">Created:</strong> {formatDate(profile.created_at)} ({profile.account_age_days} days ago)</p>
                    <p><strong className="text-gray-400 w-28 inline-block">Joined Server:</strong> {formatDate(profile.joined_at)} ({profile.server_tenure_days} days ago)</p>
                </div>
            </div>
            <div>
                <h4 className="font-semibold text-gray-200 mb-3 text-sm">Roles ({profile.roles?.length || 0})</h4>
                <div className="flex flex-wrap gap-2">
                    {profile.roles?.map(role => (
                        <span key={role.name} className="text-xs px-2 py-1 rounded-full border" style={{ backgroundColor: role.color === '#000000' ? '#4b5563' : role.color + '40', borderColor: role.color === '#000000' ? '#6b7280' : role.color, color: role.color === '#000000' ? '#f3f4f6' : role.color }}>{role.name}</span>
                    ))}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;