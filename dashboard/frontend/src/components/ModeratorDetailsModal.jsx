// dashboard/frontend/src/components/ModeratorDetailsModal.jsx

import React, { useState, useEffect, useCallback } from 'react';
import {
  XMarkIcon, ShieldCheckIcon, ChartBarIcon, DocumentTextIcon, UserGroupIcon, BoltIcon, InformationCircleIcon, ExclamationTriangleIcon, StarIcon, TrophyIcon, CalendarDaysIcon, ClockIcon
} from '@heroicons/react/24/outline';
import { 
  Pie, ResponsiveContainer, PieChart, Cell, Tooltip, Legend
} from 'recharts';
import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';

const StatBox = ({ icon, label, value, subtext }) => {
    const Icon = icon;
    return (
        <div className="card p-4 text-center">
            <Icon className="h-8 w-8 text-yellow-400 mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="text-sm text-gray-400">{label}</p>
            {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
        </div>
    );
};

const ModeratorDetailsModal = ({ moderatorId, onClose }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchData = useCallback(async () => {
    if (!moderatorId) return;
    setLoading(true);
    setError(null);
    try {
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const apiBase = isDevelopment ? 'http://localhost:8000' : '';
        
        // FIX: Removed the incorrect "/proxy" from the URL path
        const response = await fetch(`${apiBase}/api/moderators/${moderatorId}`);

        if(!response.ok) {
            const errorBody = await response.json();
            throw new Error(errorBody.detail || "Failed to fetch moderator details from API");
        }

        const result = await response.json();
        setData(result);
    } catch (err) {
        setError(err.message);
    } finally {
        setLoading(false);
    }
  }, [moderatorId]);

  useEffect(() => {
    if (moderatorId) {
        fetchData();
    }
  }, [fetchData, moderatorId]);

  const renderContent = () => {
    if (loading) return <div className="flex justify-center items-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div></div>;
    if (error || !data) return <div className="text-center py-12 text-red-400"><ExclamationTriangleIcon className="h-10 w-10 mx-auto mb-2" />Could not load moderator details: {error}</div>;

    const { profile, stats, moderated_users, recent_cases, analytics } = data;
    const actionData = Object.entries(stats.breakdowns.by_action).map(([name, value]) => ({ name, value }));
    const severityData = Object.entries(stats.breakdowns.by_severity).map(([name, value]) => ({ name, value }));
    const PIE_COLORS = { action: ['#3b82f6', '#ef4444', '#f97316', '#eab308', '#8b5cf6', '#14b8a6'], severity: ['#10b981', '#f59e0b', '#f97316', '#ef4444'] };

    const tabsContent = {
        overview: (
            <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatBox icon={CalendarDaysIcon} label="Cases Today" value={stats.timeline.today} />
                    <StatBox icon={CalendarDaysIcon} label="This Week" value={stats.timeline.this_week} />
                    <StatBox icon={CalendarDaysIcon} label="This Month" value={stats.timeline.this_month} />
                    <StatBox icon={ClockIcon} label="Avg Resolution" value={stats.performance.avg_resolution_hours ? `${stats.performance.avg_resolution_hours}h` : 'N/A'} subtext="in hours" />
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-1 space-y-6">
                        <div className="card p-4">
                            <h4 className="font-semibold text-gray-200 mb-3">Moderator Profile</h4>
                            <div className="flex items-center gap-4">
                                <img src={profile.avatar_url} alt={profile.name} className="w-16 h-16 rounded-full" />
                                <div>
                                    <h3 className="text-xl font-bold text-white">{profile.name}</h3>
                                    <p className="text-sm text-gray-400">@{profile.username}</p>
                                </div>
                            </div>
                        </div>
                        <div className="card p-4">
                            <h4 className="font-semibold text-gray-200 mb-3">Impact</h4>
                            <div className="space-y-3">
                                <div className="flex justify-between"><span className="text-gray-400">Unique Users Modded</span><span className="font-bold text-white">{stats.overview.unique_users_modded}</span></div>
                                <div className="flex justify-between"><span className="text-gray-400">Share of Total Cases</span><span className="font-bold text-white">{stats.overview.percentage_of_total_cases}%</span></div>
                            </div>
                        </div>
                    </div>
                    <div className="lg:col-span-2 card p-4">
                         <h4 className="font-semibold text-gray-200 mb-3">Most Moderated User</h4>
                         {moderated_users.most_common ? (
                             <div className="bg-gray-800/50 p-3 rounded-lg flex justify-between items-center">
                                 <p className="text-white font-medium">{moderated_users.most_common.display_name}</p>
                                 <p className="text-red-400 font-bold">{moderated_users.most_common.case_count} Cases</p>
                             </div>
                         ) : <p className="text-gray-500 text-center py-2">No user data available.</p>}
                    </div>
                </div>
            </div>
        ),
        cases: (
             <div className="card p-4 max-h-[60vh] overflow-y-auto">
                <h4 className="font-semibold text-gray-200 mb-3 flex items-center gap-2"><DocumentTextIcon className="w-5 h-5 text-yellow-400" /> Recent Cases ({recent_cases.length})</h4>
                <div className="space-y-2 pr-2">
                    {recent_cases.length > 0 ? recent_cases.map(c => (
                        <div key={c.case_number} className="grid grid-cols-4 items-center gap-2 p-2 bg-gray-800/50 rounded-lg text-sm">
                            <span className="font-medium text-white">#{c.case_number}</span>
                            <span className="text-gray-300 truncate">{c.action_type} on {c.display_name}</span>
                            <span className={`px-2 py-0.5 text-xs rounded-full text-center ${ c.severity === 'Critical' ? 'bg-red-500/30 text-red-300' : 'bg-yellow-500/20 text-yellow-300'}`}>{c.severity}</span>
                            <span className="text-xs text-gray-500 text-right">{new Date(c.created_at).toLocaleDateString()}</span>
                        </div>
                    )) : <p className="text-gray-500 text-center py-4">No cases found for this moderator.</p>}
                </div>
            </div>
        ),
        users: (
             <div className="card p-4 max-h-[60vh] overflow-y-auto">
                <h4 className="font-semibold text-gray-200 mb-3 flex items-center gap-2"><UserGroupIcon className="w-5 h-5 text-yellow-400" /> Users Moderated ({moderated_users.list.length})</h4>
                <div className="space-y-2 pr-2">
                    {moderated_users.list.length > 0 ? moderated_users.list.map(u => (
                        <div key={u.user_id} className="flex justify-between items-center p-2 bg-gray-800/50 rounded-lg">
                            <p className="text-white font-medium">{u.display_name}</p>
                            <p className="text-sm text-gray-400">{u.case_count} Case{u.case_count > 1 ? 's' : ''}</p>
                        </div>
                    )) : <p className="text-gray-500 text-center py-4">This moderator has not been involved in any cases yet.</p>}
                </div>
            </div>
        ),
        analytics: (
            <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="card p-4"><h4 className="font-semibold text-gray-200 mb-3">Actions Breakdown</h4><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={actionData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={2}>{actionData.map((e, i) => <Cell key={`cell-${i}`} fill={PIE_COLORS.action[i % PIE_COLORS.action.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /><Legend wrapperStyle={{fontSize: "12px"}}/></PieChart></ResponsiveContainer></div>
                    <div className="card p-4"><h4 className="font-semibold text-gray-200 mb-3">Severity Breakdown</h4><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={severityData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={2}>{severityData.map((e, i) => <Cell key={`cell-${i}`} fill={PIE_COLORS.severity[i % PIE_COLORS.severity.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /><Legend wrapperStyle={{fontSize: "12px"}}/></PieChart></ResponsiveContainer></div>
                </div>
                <div className="card p-4">
                    <h4 className="font-semibold text-gray-200 mb-3">Activity Heatmap (Last Year)</h4>
                    <div className="heatmap-container">
                        <CalendarHeatmap
                            startDate={new Date(new Date().setFullYear(new Date().getFullYear() - 1))}
                            endDate={new Date()}
                            values={analytics.activity_heatmap}
                            classForValue={(value) => {
                                if (!value) return 'color-empty';
                                return `color-scale-${Math.min(value.count, 4)}`;
                            }}
                            tooltipDataAttrs={value => ({ 'data-tip': `${value.date}: ${value.count} cases` })}
                        />
                    </div>
                </div>
            </div>
        )
    };
    return tabsContent[activeTab];
  };
  
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div className="card w-full max-w-6xl max-h-[90vh] flex flex-col">
            <div className="p-4 border-b border-gray-700 flex-shrink-0 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    {data && <img src={data.profile.avatar_url} alt="" className="w-12 h-12 rounded-full"/>}
                    <div>
                        <h2 className="text-xl font-bold text-white">Moderator Details</h2>
                        {data && <p className="text-gray-400">{data.profile.name}</p>}
                    </div>
                </div>
                <button onClick={onClose} className="p-1 text-gray-400 hover:text-white"><XMarkIcon className="h-6 w-6" /></button>
            </div>
            <div className="border-b border-gray-700 flex-shrink-0">
                <nav className="flex space-x-4 px-4">
                    {[
                        { id: 'overview', label: 'Overview', icon: InformationCircleIcon },
                        { id: 'cases', label: 'Cases', icon: DocumentTextIcon },
                        { id: 'users', label: 'Users Modded', icon: UserGroupIcon },
                        { id: 'analytics', label: 'Analytics', icon: ChartBarIcon }
                    ].map(tab => (
                        <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                            className={`py-3 px-1 border-b-2 text-sm flex items-center gap-1.5 ${activeTab === tab.id ? 'border-yellow-400 text-yellow-400' : 'border-transparent text-gray-400 hover:text-white'}`}>
                            <tab.icon className="w-4 h-4" />{tab.label}
                        </button>
                    ))}
                </nav>
            </div>
            <div className="flex-1 overflow-y-auto p-6 bg-gray-900/50">
                {renderContent()}
            </div>
        </div>
    </div>
  );
};

export default ModeratorDetailsModal;