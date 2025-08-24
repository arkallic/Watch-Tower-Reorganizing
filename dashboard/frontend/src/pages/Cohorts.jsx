import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { UserGroupIcon, FunnelIcon, UsersIcon, ShieldExclamationIcon, SparklesIcon, ExclamationTriangleIcon, FlagIcon, EyeSlashIcon, ShieldCheckIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, QuestionMarkCircleIcon, HeartIcon, UserMinusIcon, ChatBubbleLeftRightIcon, SpeakerWaveIcon, ArrowPathIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import CohortUserRow from '../components/CohortUserRow';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// #############################################################################
// # SUB-COMPONENTS
// #############################################################################

const CohortSnapshotCard = ({ title, icon: Icon, stats, onClick, colorClass = 'text-gray-400' }) => (
    <div 
        onClick={onClick}
        className="card p-4 cursor-pointer transition-all duration-200 hover:border-yellow-600/50 hover:bg-gray-800/50"
    >
        <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-gray-400">{title}</p>
                <p className={`text-2xl font-bold ${stats?.user_count > 0 ? 'text-white' : 'text-gray-600'}`}>{stats?.user_count || 0}</p>
            </div>
            <div className="p-3 bg-gray-500/20 rounded-lg">
                <Icon className={`h-6 w-6 ${stats?.user_count > 0 ? colorClass : 'text-gray-500'}`} />
            </div>
        </div>
        <div className="mt-2 text-xs text-gray-500 flex justify-between">
            <span>Avg. Risk: {stats?.avg_risk_score || 0}</span>
            <span>Total Cases: {stats?.total_cases || 0}</span>
        </div>
    </div>
);

const CohortVisualizations = ({ cohortUsers }) => {
    const riskData = useMemo(() => {
        const counts = new Map([['Low', 0], ['Medium', 0], ['High', 0], ['Critical', 0]]);
        cohortUsers.forEach(u => counts.set(u.risk_level, (counts.get(u.risk_level) || 0) + 1));
        return Array.from(counts.entries()).map(([name, value]) => ({ name, value }));
    }, [cohortUsers]);

    const roleData = useMemo(() => {
        const counts = new Map();
        cohortUsers.flatMap(u => u.roles.map(r => r.name)).forEach(role => counts.set(role, (counts.get(role) || 0) + 1));
        return Array.from(counts.entries()).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 5);
    }, [cohortUsers]);
    
    // Using the exact color scheme from your Users.jsx for consistency
    const RISK_COLORS = { 'Low': '#22c55e', 'Medium': '#f59e0b', 'High': '#ef4444', 'Critical': '#a855f7' };
    const THEME_COLORS = ['#3b82f6', '#818cf8', '#f97316', '#fbbf24', '#10b981']; // Blue, Indigo, Orange, Yellow, Green

    return (
        <div className="card p-4">
            <h3 className="font-semibold text-gray-200 mb-4">Selected Cohort Snapshot</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-56">
                <div>
                    <p className="text-sm text-center text-gray-400">Risk Profile of Selected Users</p>
                    <ResponsiveContainer>
                        <BarChart data={riskData} margin={{ top: 20, right: 20, bottom: 5, left: -20 }}>
                            <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                            <Tooltip wrapperClassName="card !bg-gray-800" cursor={{fill: 'rgba(107, 114, 128, 0.1)'}} />
                            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                {riskData.map((entry) => (
                                    <Cell key={`cell-${entry.name}`} fill={RISK_COLORS[entry.name]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                 <div>
                    <p className="text-sm text-center text-gray-400">Top 5 Roles</p>
                    <ResponsiveContainer>
                       <PieChart>
                           <Pie data={roleData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={5}>
                               {roleData.map((entry, index) => <Cell key={`cell-${index}`} fill={THEME_COLORS[index % THEME_COLORS.length]} />)}
                           </Pie>
                           <Tooltip wrapperClassName="card !bg-gray-800" />
                           <Legend iconSize={10} layout="vertical" verticalAlign="middle" align="right" />
                       </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

// #############################################################################
// # DATA STRUCTURES & CONFIGURATION
// #############################################################################

const cohortCategories = [
    { name: 'Behavioral Trends', icon: ArrowTrendingUpIcon, cohorts: [ { key: 'surging_activity', title: 'Surging Activity', description: 'Users whose message activity in the last 7 days is 200% or more of their monthly average.' }, { key: 'declining_activity', title: 'Declining Activity', description: 'Previously active users whose message activity has dropped by 50% or more in the last 7 days.' }, { key: 'anomalous_behavior', title: 'Anomalous Behavior', description: 'Users exhibiting unusual behavior, such as suddenly posting in many new channels.' } ] },
    { name: 'Moderation Focus', icon: ShieldExclamationIcon, cohorts: [ { key: 'high_risk', title: 'High-Risk', description: 'Users with a "High" or "Critical" risk score based on their moderation history.' }, { key: 'recently_moderated', title: 'Recently Moderated', description: 'Users who have had a moderation case created for them in the last 30 days.' }, { key: 'ai_flagged', title: 'AI-Flagged', description: 'Users flagged by the AI for potentially problematic content who do not have a manual case.' } ] },
    { name: 'Community Engagement', icon: HeartIcon, cohorts: [ { key: 'power_users', title: 'Power Users', description: 'The top 5% most active users by message volume in the last 30 days.' }, { key: 'community_pillars', title: 'Community Pillars', description: 'Users who receive the most replies and mentions, acting as social hubs.' }, { key: 'community_uplifters', title: 'Uplifters', description: 'Users who give the most positive reactions to community content.' }, { key: 'chronic_critics', title: 'Critics', description: 'Users who give the most negative reactions to community content.' }, { key: 'voice_vanguards', title: 'Voice Vanguards', description: 'The most active users by time spent in voice channels.' } ] },
    { name: 'Membership Status', icon: UsersIcon, cohorts: [ { key: 'new_members', title: 'New Members', description: 'Users who joined the server within the last 7 days.' }, { key: 'returning_members', title: 'Returning Members', description: 'Users who have left and rejoined the server one or more times.' }, { key: 'isolated_members', title: 'Isolated Members', description: 'Active users whose messages rarely receive replies or mentions.' }, { key: 'lurkers', title: 'Lurkers', description: 'The bottom 10% of users by message activity.' }, { key: 'clean_record', title: 'Clean Record', description: 'Users with zero moderation cases against them.' } ] }
];

// #############################################################################
// # MAIN PAGE COMPONENT: Cohorts
// #############################################################################

const Cohorts = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeCohort, setActiveCohort] = useState('new_members');
    const [expandedRow, setExpandedRow] = useState(null);
    const [filters, setFilters] = useState({ role: 'All', risk: 'All' });
    const [openCategory, setOpenCategory] = useState(null);

    const fetchData = useCallback(async () => { setLoading(true); setError(null); try { const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'; const response = await fetch(isDevelopment ? 'http://localhost:8000/api/pagedata/cohorts' : '/api/pagedata/cohorts'); if (!response.ok) { const errData = await response.json(); throw new Error(errData.detail || 'Failed to fetch cohort data'); } setData(await response.json()); } catch (err) { setError(err.message); } finally { setLoading(false); } }, []);
    useEffect(() => { fetchData(); }, [fetchData]);

    const allRoles = useMemo(() => { if (!data?.cohorts) return []; const allUsers = Object.values(data.cohorts).flat(); const roleSet = new Set(allUsers.flatMap(u => u.roles.map(r => r.name))); return Array.from(roleSet).sort(); }, [data]);
    const filteredUsers = useMemo(() => { if (!data?.cohorts?.[activeCohort]) return []; let users = data.cohorts[activeCohort]; if (filters.risk !== 'All') users = users.filter(u => u.risk_level === filters.risk); if (filters.role !== 'All') users = users.filter(u => u.roles.some(r => r.name === filters.role)); return users; }, [data, activeCohort, filters]);
    
    const handleCategoryClick = (categoryName) => { setOpenCategory(prev => prev === categoryName ? null : categoryName); };
    
    if (loading) return ( <div className="p-6 h-full flex flex-col items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div><p className="mt-4 text-gray-400">Analyzing user cohorts...</p></div> );
    if (error) return <div className="p-6 text-center text-red-500">Error: {error}</div>;

    const activeCohortDetails = cohortCategories.flatMap(c => c.cohorts).find(c => c.key === activeCohort);

    return (
        <div className="p-6 space-y-6">
            <div className="card border-t-2 border-yellow-400/50 p-6">
                <h1 className="text-2xl font-bold text-yellow-400 flex items-center"><UserGroupIcon className="h-7 w-7 mr-3" />User Cohorts</h1>
                <p className="text-sm text-gray-400 mt-1">Dynamic user segments based on behavior and metadata.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <CohortSnapshotCard title="New Members" icon={UsersIcon} stats={data?.summary?.new_members} onClick={() => setActiveCohort('new_members')} colorClass="text-blue-400" />
                <CohortSnapshotCard title="Surging Activity" icon={ArrowTrendingUpIcon} stats={data?.summary?.surging_activity} onClick={() => setActiveCohort('surging_activity')} colorClass="text-green-400" />
                <CohortSnapshotCard title="Declining Activity" icon={ArrowTrendingDownIcon} stats={data?.summary?.declining_activity} onClick={() => setActiveCohort('declining_activity')} colorClass="text-yellow-400" />
                <CohortSnapshotCard title="Anomalous Behavior" icon={QuestionMarkCircleIcon} stats={data?.summary?.anomalous_behavior} onClick={() => setActiveCohort('anomalous_behavior')} colorClass="text-orange-400" />
            </div>

            <div className="flex flex-col lg:flex-row gap-6">
                <aside className="lg:w-72">
                    <div className="card p-4 space-y-4">
                        <h3 className="font-semibold text-gray-200 flex items-center"><FunnelIcon className="w-5 h-5 mr-2" />Filter Active Cohort</h3>
                        <div>
                            <label className="text-xs text-gray-400">Risk Level</label>
                            <select value={filters.risk} onChange={e => setFilters({...filters, risk: e.target.value})} className="input-select mt-1">
                                <option>All</option><option>Low</option><option>Medium</option><option>High</option><option>Critical</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-xs text-gray-400">Role</label>
                            <select value={filters.role} onChange={e => setFilters({...filters, role: e.target.value})} className="input-select mt-1">
                                <option>All</option>
                                {allRoles.map(r => <option key={r}>{r}</option>)}
                            </select>
                        </div>
                    </div>
                </aside>

                <main className="flex-1 space-y-6">
                    <CohortVisualizations cohortUsers={filteredUsers} />
                    <div className="card">
                        <div className="p-4 border-b border-gray-800">
                            <div className="flex items-start gap-2 flex-wrap">
                                {cohortCategories.map(category => (
                                    <div key={category.name} className="relative">
                                        <button onClick={() => handleCategoryClick(category.name)} className="btn btn-secondary bg-gray-800/60">
                                            <category.icon className="w-5 h-5" />
                                            <span>{category.name}</span>
                                            <ChevronDownIcon className={`w-4 h-4 ml-2 transition-transform duration-200 ${openCategory === category.name ? 'rotate-180' : ''}`} />
                                        </button>
                                        {openCategory === category.name && (
                                            <div className="absolute top-full left-0 mt-2 w-60 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-10 p-2 space-y-1">
                                                {category.cohorts.map(cohort => (
                                                    <button key={cohort.key} onClick={() => {setActiveCohort(cohort.key); setExpandedRow(null);}} 
                                                        className={`w-full text-left px-3 py-1.5 rounded-md text-sm font-medium transition-colors whitespace-nowrap flex justify-between items-center ${activeCohort === cohort.key ? 'bg-yellow-500/20 text-yellow-300' : 'text-gray-400 hover:bg-gray-700/50'}`}>
                                                        <span>{cohort.title}</span>
                                                        <span className="text-xs text-gray-500">{data?.cohorts?.[cohort.key]?.length || 0}</span>
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="p-4 bg-gray-800/20 border-b border-gray-800">
                            <p className="text-sm text-gray-400 italic">{activeCohortDetails?.description || 'Select a cohort to view its members.'}</p>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="min-w-full">
                                <thead className="bg-gray-800/40"><tr className="text-left text-xs text-gray-400 uppercase">
                                    <th className="p-3 font-medium">User</th><th className="p-3 font-medium text-center">Tenure</th>
                                    <th className="p-3 font-medium text-center">Messages (30d)</th><th className="p-3 font-medium text-center">Cases</th>
                                    <th className="p-3 font-medium text-center">Risk</th><th className="p-3 font-medium text-center w-12">Details</th>
                                </tr></thead>
                                <tbody>
                                    {filteredUsers.length > 0 ? (
                                        filteredUsers.map(user => (
                                            <CohortUserRow key={user.user_id} user={user} cohortKey={activeCohort} isExpanded={expandedRow === user.user_id} onToggle={() => setExpandedRow(expandedRow === user.user_id ? null : user.user_id)} />
                                        ))
                                    ) : (
                                        <tr><td colSpan="6" className="text-center p-8 text-gray-500">No users match the current filters in this cohort.</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Cohorts;