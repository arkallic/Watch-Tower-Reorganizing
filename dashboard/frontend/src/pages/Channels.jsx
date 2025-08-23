import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  MagnifyingGlassIcon, ArrowPathIcon, TrashIcon, UserGroupIcon, EyeIcon, 
  ArrowUturnLeftIcon, SpeakerWaveIcon, InformationCircleIcon, FlagIcon, 
  ChartPieIcon, ExclamationTriangleIcon, DocumentTextIcon 
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const ChannelDetails = ({ channel, onBack }) => {
    const [activeTab, setActiveTab] = useState('overview');

    const actionBreakdown = useMemo(() => {
        if (!channel.cases || channel.cases.length === 0) return [];
        const counts = channel.cases.reduce((acc, c) => {
            acc[c.action_type || 'unknown'] = (acc[c.action_type || 'unknown'] || 0) + 1;
            return acc;
        }, {});
        return Object.entries(counts).map(([name, value]) => ({ name, value }));
    }, [channel.cases]);

    const PIE_COLORS = ['#3b82f6', '#ef4444', '#f97316', '#eab308', '#8b5cf6', '#14b8a6'];

    const renderContent = () => {
        switch (activeTab) {
            case 'overview':
                return (
                    <div className="space-y-6 animate-fade-in">
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <div className="card p-3 text-center"><p className="text-lg font-bold text-white">{channel.message_count.toLocaleString()}</p><p className="text-xs text-gray-400">Messages (30d)</p></div>
                            <div className="card p-3 text-center"><p className="text-lg font-bold text-white">{channel.case_count}</p><p className="text-xs text-gray-400">Total Cases</p></div>
                            <div className="card p-3 text-center"><p className="text-lg font-bold text-orange-400">{channel.open_case_count}</p><p className="text-xs text-gray-400">Open Cases</p></div>
                            <div className="card p-3 text-center"><p className="text-lg font-bold text-red-400">{channel.deletion_count}</p><p className="text-xs text-gray-400">Deletions (24h)</p></div>
                        </div>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="card p-4">
                                <h3 className="text-base font-semibold text-gray-100 mb-3"><InformationCircleIcon className="w-5 h-5 inline mr-2 text-yellow-400"/>Channel Info</h3>
                                <div className="text-sm space-y-2">
                                    <p><strong>Topic:</strong> <span className="text-gray-300 italic">"{channel.topic || 'Not set'}"</span></p>
                                    <p className="flex justify-between"><strong>NSFW:</strong> <span className={channel.is_nsfw ? 'text-red-400 font-semibold' : 'text-green-400'}>{channel.is_nsfw ? 'Yes' : 'No'}</span></p>
                                    <p className="flex justify-between"><strong>Slowmode:</strong> <span className="text-gray-300">{channel.slowmode_delay > 0 ? `${channel.slowmode_delay}s` : 'Off'}</span></p>
                                </div>
                            </div>
                            <div className="card p-4">
                                <h3 className="text-base font-semibold text-gray-100 mb-3"><ChartPieIcon className="w-5 h-5 inline mr-2 text-yellow-400"/>Action Breakdown</h3>
                                {actionBreakdown.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={150}><PieChart><Pie data={actionBreakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60}>{actionBreakdown.map((entry, index) => <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /></PieChart></ResponsiveContainer>
                                ) : <p className="text-center text-gray-500 py-4 h-[150px] flex items-center justify-center">No case actions to display.</p>}
                            </div>
                        </div>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="card p-4">
                                <h3 className="text-base font-semibold text-gray-100 mb-3"><UserGroupIcon className="w-5 h-5 inline mr-2 text-yellow-400"/>Top Moderators</h3>
                                <div className="space-y-2">
                                    {channel.most_active_mods && channel.most_active_mods.length > 0 ? (
                                        channel.most_active_mods.map(mod => (
                                            <div key={mod.name} className="flex justify-between items-center card-secondary p-2">
                                                <span className="text-white font-medium">{mod.name}</span>
                                                <span className="text-gray-400">{mod.count} cases</span>
                                            </div>
                                        ))
                                    ) : <p className="text-center text-gray-500 py-4">No moderators active in this channel.</p>}
                                </div>
                            </div>
                            <div className="card p-4">
                                <h3 className="text-base font-semibold text-gray-100 mb-3"><TrashIcon className="w-5 h-5 inline mr-2 text-yellow-400"/>Recent Deleted Messages</h3>
                                <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
                                    {channel.recent_deletions && channel.recent_deletions.length > 0 ? (
                                        channel.recent_deletions.map(msg => (
                                            <div key={msg.message_id} className="card-secondary p-3">
                                                <p className="text-sm text-gray-300 italic">"{msg.content}"</p>
                                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                                    <span>By: {msg.deleted_by_name}</span>
                                                    <span>At: {new Date(msg.deleted_at).toLocaleString()}</span>
                                                </div>
                                            </div>
                                        ))
                                    ) : <p className="text-center text-gray-500 py-8">No recent deleted messages.</p>}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            case 'open_cases':
            case 'all_cases':
                const casesToShow = activeTab === 'open_cases' ? channel.cases.filter(c => c.status === 'Open') : channel.cases;
                return (
                    <div className="card animate-fade-in">
                        <div className="overflow-x-auto max-h-[70vh]">
                            <table className="min-w-full">
                                <thead className="bg-gray-800/50 sticky top-0"><tr><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Case #</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">User</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Action</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Moderator</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Date</th></tr></thead>
                                <tbody className="divide-y divide-gray-700/50">
                                    {casesToShow.length > 0 ? casesToShow.map(c => (
                                        <tr key={c.case_number} className="hover:bg-gray-800/40">
                                            <td className="px-4 py-3 text-sm text-white font-medium">#{c.case_number}</td>
                                            <td className="px-4 py-3 text-sm text-gray-300">{c.display_name}</td>
                                            <td className="px-4 py-3 text-sm text-gray-300">{c.action_type}</td>
                                            <td className="px-4 py-3 text-sm text-gray-300">{c.moderator_name}</td>
                                            <td className="px-4 py-3 text-sm text-gray-400">{new Date(c.created_at).toLocaleDateString()}</td>
                                        </tr>
                                    )) : (
                                        <tr><td colSpan="5" className="text-center py-8 text-gray-500">No cases found.</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-4">
                <button onClick={onBack} className="btn-secondary p-2"><ArrowUturnLeftIcon className="w-5 h-5" /></button>
                <div>
                    <h2 className="text-xl font-bold text-white">#{channel.name}</h2>
                    <p className="text-xs text-gray-400">Category: {channel.category || 'Uncategorized'}</p>
                </div>
            </div>
            <div className="border-b border-gray-700">
                <nav className="flex space-x-4">
                    <button onClick={() => setActiveTab('overview')} className={`py-2 px-1 border-b-2 text-sm ${activeTab === 'overview' ? 'border-yellow-400 text-yellow-400' : 'border-transparent text-gray-400 hover:text-white'}`}>Overview</button>
                    <button onClick={() => setActiveTab('open_cases')} className={`py-2 px-1 border-b-2 text-sm ${activeTab === 'open_cases' ? 'border-yellow-400 text-yellow-400' : 'border-transparent text-gray-400 hover:text-white'}`}>Open Cases ({channel.open_case_count})</button>
                    <button onClick={() => setActiveTab('all_cases')} className={`py-2 px-1 border-b-2 text-sm ${activeTab === 'all_cases' ? 'border-yellow-400 text-yellow-400' : 'border-transparent text-gray-400 hover:text-white'}`}>All Cases ({channel.case_count})</button>
                </nav>
            </div>
            <div className="pt-4">{renderContent()}</div>
        </div>
    );
};

const ChannelOverview = ({ overview, textChannels, voiceChannels }) => {
    const PIE_COLORS = ['#3b82f6', '#ef4444', '#f97316', '#eab308', '#8b5cf6', '#14b8a6'];
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">Channels Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="card p-4"><p className="text-sm text-gray-400">Total Text Channels</p><p className="text-2xl font-bold text-white">{overview.total_text_channels}</p></div>
                <div className="card p-4"><p className="text-sm text-gray-400">Messages (30d)</p><p className="text-2xl font-bold text-white">{overview.total_messages_30d?.toLocaleString()}</p></div>
                <div className="card p-4"><p className="text-sm text-gray-400">AI Flags (30d)</p><p className="text-2xl font-bold text-orange-400">{overview.total_ai_flags_30d?.toLocaleString()}</p></div>
                <div className="card p-4"><p className="text-sm text-gray-400">Total Cases</p><p className="text-2xl font-bold text-red-400">{overview.total_cases?.toLocaleString()}</p></div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card p-4"><h3 className="text-base font-semibold text-gray-100 mb-4">Server-Wide Action Breakdown</h3><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={overview.action_breakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={70}>{overview.action_breakdown.map((e, i) => <Cell key={`cell-${i}`} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /><Legend wrapperStyle={{fontSize: "12px"}}/></PieChart></ResponsiveContainer></div>
                <div className="card p-4"><h3 className="text-base font-semibold text-gray-100 mb-4">Server-Wide Severity Breakdown</h3><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={overview.severity_breakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={70}>{overview.severity_breakdown.map((e, i) => <Cell key={`cell-${i}`} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /><Legend wrapperStyle={{fontSize: "12px"}}/></PieChart></ResponsiveContainer></div>
            </div>
             <div className="card p-4">
                <h3 className="text-base font-semibold text-gray-100 mb-3"><SpeakerWaveIcon className="w-5 h-5 inline mr-2 text-yellow-400"/>Live Voice Activity</h3>
                <div className="space-y-2">
                    {voiceChannels.length > 0 && voiceChannels.some(vc => vc.connected_users > 0) ? voiceChannels.filter(vc => vc.connected_users > 0).map(vc => (
                         <div key={vc.name} className="flex justify-between items-center card-secondary p-2"><span className="text-white font-medium">#{vc.name}</span><span className="text-green-400 flex items-center gap-1.5"><UserGroupIcon className="w-4 h-4"/>{vc.connected_users}</span></div>
                    )) : <p className="text-center text-gray-500 py-4">No users in voice channels.</p>}
                </div>
            </div>
        </div>
    );
};

const Channels = () => {
    const [channelData, setChannelData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedChannelId, setSelectedChannelId] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('name');
    const [selectedCategory, setSelectedCategory] = useState('all');

    const fetchData = useCallback(async () => {
        setLoading(true); setError(null);
        try {
            const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const apiBase = isDevelopment ? 'http://localhost:8000' : '';
            const response = await fetch(`${apiBase}/api/pagedata/channels`);
            if (!response.ok) throw new Error("Failed to fetch channel data");
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            setChannelData(data);
        } catch (err) {
            setError(err.message);
        } finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const sortedAndFilteredChannels = useMemo(() => {
        if (!channelData?.channels_by_category) return {};
        const result = {};
        
        const categoriesToProcess = selectedCategory === 'all'
            ? Object.keys(channelData.channels_by_category)
            : [selectedCategory];

        for (const category of categoriesToProcess) {
            if (!channelData.channels_by_category[category]) continue;

            let channels = channelData.channels_by_category[category]
                .filter(ch => ch.name.toLowerCase().includes(searchTerm.toLowerCase()));

            if (channels.length > 0) {
                channels.sort((a, b) => {
                    if (sortBy === 'name') {
                        return a.name.localeCompare(b.name);
                    }
                    return (b[sortBy] || 0) - (a[sortBy] || 0);
                });
                result[category] = channels;
            }
        }
        return result;
    }, [channelData, searchTerm, sortBy, selectedCategory]);

    const selectedChannel = useMemo(() => {
        if (!selectedChannelId || !channelData?.channels_by_category) return null;
        for (const category in channelData.channels_by_category) {
            const found = channelData.channels_by_category[category].find(ch => ch.id === selectedChannelId);
            if (found) return found;
        }
        return null;
    }, [channelData, selectedChannelId]);
    
    const getHotspotColor = (rate) => {
        if (rate > 5) return 'bg-red-500/50';
        if (rate > 2) return 'bg-orange-500/50';
        return 'bg-transparent';
    }

    if (loading) return <div className="p-6 h-full flex items-center justify-center"><div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div></div>;
    if (error) return <div className="p-6 text-center text-red-400">Error: {error}</div>;

    return (
        <div className="p-6 space-y-6">
            <div className="card border-t-2 border-yellow-400/50">
                <div className="px-6 py-4 flex justify-between items-center">
                    <div><h1 className="text-2xl font-bold text-yellow-400">Channel Analytics</h1><p className="text-sm text-gray-400 mt-1">Explore activity and moderation by channel.</p></div>
                    <button onClick={fetchData} className="btn-secondary flex items-center gap-2"><ArrowPathIcon className="w-5 h-5" /> Refresh</button>
                </div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
                <div className="lg:col-span-1 card p-2 flex flex-col h-full">
                    <div className="relative p-2"><MagnifyingGlassIcon className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" /><input type="text" placeholder="Search channels..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="input w-full pl-10"/></div>
                    
                    <div className="px-3 pt-2 pb-3 border-b border-gray-700/50 space-y-2">
                        <div className="flex bg-gray-900/70 rounded-lg p-1">
                            <button onClick={() => setSortBy('name')} className={`flex-1 text-xs py-1 rounded-md transition-colors ${sortBy === 'name' ? 'bg-yellow-500/20 text-yellow-300' : 'text-gray-400 hover:bg-gray-700/50'}`}>Name</button>
                            <button onClick={() => setSortBy('open_case_count')} className={`flex-1 text-xs py-1 rounded-md transition-colors ${sortBy === 'open_case_count' ? 'bg-yellow-500/20 text-yellow-300' : 'text-gray-400 hover:bg-gray-700/50'}`}>Activity</button>
                            <button onClick={() => setSortBy('deletion_count')} className={`flex-1 text-xs py-1 rounded-md transition-colors ${sortBy === 'deletion_count' ? 'bg-yellow-500/20 text-yellow-300' : 'text-gray-400 hover:bg-gray-700/50'}`}>Deletions</button>
                        </div>
                        <div>
                            <select
                                value={selectedCategory}
                                onChange={e => setSelectedCategory(e.target.value)}
                                className="input w-full text-sm"
                            >
                                <option value="all">All Categories</option>
                                {channelData && Object.keys(channelData.channels_by_category).map(category => (
                                    <option key={category} value={category}>{category}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2">
                        {Object.entries(sortedAndFilteredChannels).map(([category, channels]) => (
                            <div key={category}>
                                <h3 className="text-xs font-bold uppercase text-gray-500 px-3 pt-4 pb-2">{category}</h3>
                                {channels.map(channel => (
                                    <button key={channel.id} onClick={() => setSelectedChannelId(channel.id)} className={`w-full text-left p-3 rounded-lg my-1 transition-colors relative overflow-hidden ${selectedChannelId === channel.id ? 'bg-yellow-500/20 text-yellow-300' : 'hover:bg-gray-700/50'}`}>
                                        <div className={`absolute left-0 top-0 h-full w-1 ${getHotspotColor(channel.problem_rate)}`}></div>
                                        <p className="font-medium text-white">#{channel.name}</p>
                                        <div className="text-xs text-gray-400 grid grid-cols-4 gap-1 items-center mt-1">
                                            <span className="flex items-center gap-1" title="Open Cases"><ExclamationTriangleIcon className="w-3 h-3 text-orange-400"/>{channel.open_case_count}</span>
                                            <span className="flex items-center gap-1" title="Total Cases"><DocumentTextIcon className="w-3 h-3 text-blue-400"/>{channel.case_count}</span>
                                            <span className="flex items-center gap-1" title="AI Flags"><FlagIcon className="w-3 h-3 text-yellow-400"/>{channel.flag_count}</span>
                                            <span className="flex items-center gap-1" title="Deletions (24h)"><TrashIcon className="w-3 h-3 text-red-400"/>{channel.deletion_count}</span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
                <div className="lg:col-span-3 card bg-black/30 overflow-y-auto h-full">
                    <div className="p-6">
                      {selectedChannel ? <ChannelDetails channel={selectedChannel} onBack={() => setSelectedChannelId(null)} /> : <ChannelOverview overview={channelData?.overview || {}} textChannels={Object.values(channelData?.channels_by_category || {}).flat()} voiceChannels={channelData?.voice_channels || []} />}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Channels;