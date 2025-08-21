import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ChatBubbleLeftRightIcon, MagnifyingGlassIcon, ExclamationTriangleIcon, ArrowPathIcon, TrashIcon, FlagIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const ChannelDetails = ({ channel }) => {
    const actionBreakdown = useMemo(() => {
        if (!channel.cases || channel.cases.length === 0) return [];
        const counts = channel.cases.reduce((acc, c) => {
            const action = c.action_type || 'unknown';
            acc[action] = (acc[action] || 0) + 1;
            return acc;
        }, {});
        return Object.entries(counts).map(([name, value]) => ({ name, value }));
    }, [channel.cases]);

    const topOffenders = useMemo(() => {
        if (!channel.cases || channel.cases.length === 0) return [];
        const counts = channel.cases.reduce((acc, c) => {
            const user = c.display_name || c.username;
            acc[user] = (acc[user] || 0) + 1;
            return acc;
        }, {});
        return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 5);
    }, [channel.cases]);

    const PIE_COLORS = ['#3b82f6', '#ef4444', '#f97316', '#eab308', '#8b5cf6', '#14b8a6'];

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-white">#{channel.name}</h2>
                <p className="text-sm text-gray-400">Category: {channel.category || 'Uncategorized'}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="card p-4 text-center"><p className="text-2xl font-bold text-white">{channel.message_count.toLocaleString()}</p><p className="text-sm text-gray-400">Messages (30d)</p></div>
                <div className="card p-4 text-center"><p className="text-2xl font-bold text-white">{channel.case_count}</p><p className="text-sm text-gray-400">Total Cases</p></div>
                <div className="card p-4 text-center"><p className="text-2xl font-bold text-orange-400">{channel.flag_count}</p><p className="text-sm text-gray-400">AI Flags</p></div>
                <div className="card p-4 text-center"><p className="text-2xl font-bold text-red-400">{channel.deletion_count}</p><p className="text-sm text-gray-400">Deletions</p></div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card p-4">
                    <h3 className="font-semibold text-gray-100 mb-3 flex items-center gap-2"><UserGroupIcon className="w-5 h-5 text-yellow-400"/>Top Offenders</h3>
                    <div className="space-y-2">
                        {topOffenders.length > 0 ? topOffenders.map(([name, count]) => (
                            <div key={name} className="flex justify-between items-center card-secondary p-2">
                                <span className="text-white font-medium">{name}</span>
                                <span className="text-red-400">{count} cases</span>
                            </div>
                        )) : <p className="text-center text-gray-500 py-4">No repeat offenders in this channel.</p>}
                    </div>
                </div>
                <div className="card p-4">
                    <h3 className="font-semibold text-gray-100 mb-3">Action Breakdown</h3>
                    {actionBreakdown.length > 0 ? (
                        <ResponsiveContainer width="100%" height={150}>
                            <PieChart><Pie data={actionBreakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60} label>{actionBreakdown.map((entry, index) => <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /></PieChart>
                        </ResponsiveContainer>
                    ) : <p className="text-center text-gray-500 py-4">No case actions to display.</p>}
                </div>
            </div>
            <div className="card p-4">
                <h3 className="font-semibold text-gray-100 mb-3 flex items-center gap-2"><TrashIcon className="w-5 h-5 text-yellow-400"/>Recent Deleted Messages</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
                    {channel.recent_deletions && channel.recent_deletions.length > 0 ? (
                        channel.recent_deletions.map(msg => (
                            <div key={msg.message_id} className="card-secondary p-3">
                                <div className="flex justify-between text-xs text-gray-500 mb-1"><span>By: {msg.author_name}</span><span>At: {new Date(msg.deleted_at).toLocaleTimeString()}</span></div>
                                <p className="text-sm text-gray-300 italic">"{msg.content}"</p>
                            </div>
                        ))
                    ) : <p className="text-center text-gray-500 py-8">No recent deleted messages in this channel.</p>}
                </div>
            </div>
        </div>
    );
};

const ChannelOverview = ({ channels }) => {
    const totalMessages = useMemo(() => channels.reduce((sum, ch) => sum + ch.message_count, 0), [channels]);
    const totalCases = useMemo(() => channels.reduce((sum, ch) => sum + ch.case_count, 0), [channels]);
    const totalFlags = useMemo(() => channels.reduce((sum, ch) => sum + ch.flag_count, 0), [channels]);
    const totalDeletions = useMemo(() => channels.reduce((sum, ch) => sum + ch.deletion_count, 0), [channels]);

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">Channels Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="card p-4"><p className="text-sm text-gray-400">Total Channels</p><p className="text-2xl font-bold text-white">{channels.length}</p></div>
                <div className="card p-4"><p className="text-sm text-gray-400">Messages (30d)</p><p className="text-2xl font-bold text-white">{totalMessages.toLocaleString()}</p></div>
                <div className="card p-4"><p className="text-sm text-gray-400">AI Flags (30d)</p><p className="text-2xl font-bold text-orange-400">{totalFlags.toLocaleString()}</p></div>
                <div className="card p-4"><p className="text-sm text-gray-400">Deletions (24h)</p><p className="text-2xl font-bold text-red-400">{totalDeletions.toLocaleString()}</p></div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card p-4">
                    <h3 className="font-semibold text-gray-100 mb-3">Busiest Channels (by Messages)</h3>
                    <div className="space-y-2">
                        {[...channels].sort((a,b) => b.message_count - a.message_count).slice(0,5).map(ch => (
                            <div key={ch.id} className="flex justify-between items-center card-secondary p-2">
                                <span className="text-white font-medium">#{ch.name}</span>
                                <span className="text-gray-300">{ch.message_count.toLocaleString()} msgs</span>
                            </div>
                        ))}
                    </div>
                </div>
                <div className="card p-4">
                    <h3 className="font-semibold text-gray-100 mb-3">Most Problematic (by Cases)</h3>
                    <div className="space-y-2">
                        {[...channels].sort((a,b) => b.case_count - a.case_count).slice(0,5).map(ch => (
                             <div key={ch.id} className="flex justify-between items-center card-secondary p-2">
                                <span className="text-white font-medium">#{ch.name}</span>
                                <span className="text-red-400">{ch.case_count} cases</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

const Channels = () => {
    const [channelData, setChannelData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedChannelId, setSelectedChannelId] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const apiBase = isDevelopment ? 'http://localhost:8000' : '';
            const response = await fetch(`${apiBase}/api/pagedata/channels`);
            if (!response.ok) throw new Error("Failed to fetch channel data");
            const data = await response.json();
            setChannelData(data.channels || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const filteredChannels = useMemo(() =>
        channelData.filter(channel =>
            channel.name.toLowerCase().includes(searchTerm.toLowerCase())
        ), [channelData, searchTerm]);

    const selectedChannel = useMemo(() =>
        channelData.find(ch => ch.id === selectedChannelId),
    [channelData, selectedChannelId]);

    if (loading) return <div className="p-6 h-full flex items-center justify-center"><div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div></div>;
    if (error) return <div className="p-6 text-center text-red-400">Error: {error}</div>;

    return (
        <div className="p-6 space-y-6">
            <div className="card border-t-2 border-yellow-400/50">
                <div className="px-6 py-4 flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-yellow-400">Channel Analytics</h1>
                        <p className="text-sm text-gray-400 mt-1">Explore activity and moderation by channel.</p>
                    </div>
                    <button onClick={fetchData} className="btn-secondary flex items-center gap-2"><ArrowPathIcon className="w-5 h-5" /> Refresh</button>
                </div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
                <div className="lg:col-span-1 card p-2 flex flex-col h-full">
                    <div className="relative p-2">
                        <MagnifyingGlassIcon className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                        <input type="text" placeholder="Search channels..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="input w-full pl-10"/>
                    </div>
                    <div className="flex-1 overflow-y-auto pr-2">
                        {filteredChannels.map(channel => (
                            <button key={channel.id} onClick={() => setSelectedChannelId(channel.id)} className={`w-full text-left p-3 rounded-lg my-1 transition-colors ${selectedChannelId === channel.id ? 'bg-yellow-500/20 text-yellow-300' : 'hover:bg-gray-700/50'}`}>
                                <p className="font-medium text-white">#{channel.name}</p>
                                <div className="text-xs text-gray-400 flex items-center gap-2 mt-1">
                                    <span>{channel.case_count} cases</span>
                                    <span>·</span>
                                    <span className="text-orange-400">{channel.flag_count} flags</span>
                                    <span>·</span>
                                    <span className="text-red-400">{channel.deletion_count} del</span>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
                <div className="lg:col-span-3 card p-6 overflow-y-auto h-full">
                    {selectedChannel ? <ChannelDetails channel={selectedChannel} /> : <ChannelOverview channels={channelData} />}
                </div>
            </div>
        </div>
    );
};

export default Channels;