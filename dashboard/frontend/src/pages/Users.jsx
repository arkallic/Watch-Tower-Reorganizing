import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  MagnifyingGlassIcon, ArrowPathIcon, EyeIcon, AdjustmentsHorizontalIcon, FlagIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, AreaChart, Area, XAxis, YAxis } from 'recharts';
import { useNavigate } from 'react-router-dom';

const Users = () => {
  const navigate = useNavigate();

  // --- STATE MANAGEMENT ---
  const [users, setUsers] = useState([]);
  const [userStats, setUserStats] = useState({});
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [serverGrowth, setServerGrowth] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('risk_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [pageSize] = useState(50);
  const [currentPage, setCurrentPage] = useState(1);
  
  const [filters, setFilters] = useState({
    riskLevel: 'all',
    botFilter: 'humans',
    hasOpenCases: 'all'
  });

  // --- DATA FETCHING (STREAMLINED) ---
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const response = await fetch(isDevelopment ? 'http://localhost:8000/api/pagedata/users-enhanced' : '/api/pagedata/users-enhanced');
      if (!response.ok) throw new Error(`API failed: ${response.statusText}`);
      
      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setUsers(data.users || []);
      setUserStats(data.userStats || {});
      setRiskDistribution(data.riskDistribution || []);
      setServerGrowth(data.serverGrowth || []);
      setLastUpdated(new Date());
      
    } catch (err) {
      console.error('Error fetching user page data:', err);
      setError(`Failed to load data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // --- MEMOIZED LISTS FOR UI ---
  const mostModeratedUsers = useMemo(() => users
    .filter(u => !u.bot && (u.total_cases || 0) > 0)
    .sort((a,b) => (b.total_cases || 0) - (a.total_cases || 0))
    .slice(0, 5), [users]);

  const filteredUsers = useMemo(() => users.filter(user => {
    const search = searchTerm.toLowerCase();
    const matchesSearch = !searchTerm || user.display_name.toLowerCase().includes(search) || user.username.toLowerCase().includes(search) || user.user_id.includes(search);
    
    let matchesAdvanced = true;
    if (showAdvancedFilters) {
        if (filters.riskLevel !== 'all') matchesAdvanced = matchesAdvanced && user.risk_level === filters.riskLevel;
        if (filters.botFilter !== 'all') matchesAdvanced = matchesAdvanced && (filters.botFilter === 'bots' ? user.bot : !user.bot);
        if (filters.hasOpenCases !== 'all') matchesAdvanced = matchesAdvanced && (filters.hasOpenCases === 'yes' ? (user.open_cases || 0) > 0 : (user.open_cases || 0) === 0);
    }
    return matchesSearch && matchesAdvanced;
  }), [users, searchTerm, showAdvancedFilters, filters]);

  const sortedUsers = useMemo(() => [...filteredUsers].sort((a, b) => {
    const aVal = a[sortBy] || 0;
    const bVal = b[sortBy] || 0;
    if (sortBy === 'joined_at') {
        if (!aVal) return 1; if (!bVal) return -1;
        return sortOrder === 'asc' ? new Date(aVal) - new Date(bVal) : new Date(bVal) - new Date(aVal);
    }
    if (typeof aVal === 'string') return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
  }), [filteredUsers, sortBy, sortOrder]);

  const paginatedUsers = useMemo(() => sortedUsers.slice((currentPage - 1) * pageSize, currentPage * pageSize), [sortedUsers, currentPage, pageSize]);
  const totalPages = useMemo(() => Math.ceil(sortedUsers.length / pageSize), [sortedUsers]);

  // --- HANDLERS AND HELPERS ---
  const handleSort = (field) => {
    setSortOrder(sortBy === field && sortOrder === 'desc' ? 'asc' : 'desc');
    setSortBy(field);
  };
  const handleFilterChange = (key, value) => setFilters(prev => ({ ...prev, [key]: value }));
  const resetFilters = () => {
    setSearchTerm('');
    setShowAdvancedFilters(false);
    setFilters({ riskLevel: 'all', botFilter: 'humans', hasOpenCases: 'all' });
  };
  
  const getUserAvatar = (user) => user.avatar || `https://cdn.discordapp.com/embed/avatars/${(user.discriminator || 0) % 5}.png`;
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

  if (loading) return <div className="p-6 h-full flex items-center justify-center"><div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div></div>;
  if (error) return <div className="p-6 text-center text-red-400">Error: {error}</div>;

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="card border-t-2 border-yellow-400/50">
          <div className="px-6 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-yellow-400">Server Members</h1>
                <p className="text-sm text-gray-400 mt-1">Last updated: {lastUpdated?.toLocaleTimeString()}</p>
              </div>
              <div className="flex items-center space-x-2">
                 <div className="text-right">
                    <p className="text-xl font-bold text-white">{userStats.total}</p>
                    <p className="text-xs text-gray-400">Total Members</p>
                 </div>
                 <button onClick={fetchData} className="p-2 bg-gray-700/80 text-gray-300 rounded-lg border border-gray-600/50 hover:text-white transition-all"><ArrowPathIcon className="w-5 h-5" /></button>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card p-4"><p className="text-sm text-gray-400">Total Humans</p><p className="text-2xl font-bold text-white">{userStats.humans}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-400">Clean Users</p><p className="text-2xl font-bold text-green-400">{userStats.clean}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-400">High Risk</p><p className="text-2xl font-bold text-red-400">{userStats.highRisk}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-400">New (7d)</p><p className="text-2xl font-bold text-blue-400">{userStats.newMembers}</p></div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="card p-4">
                <h3 className="text-md font-semibold text-gray-100 mb-2">Risk Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                        <Pie data={riskDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                            {riskDistribution.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
                    </PieChart>
                </ResponsiveContainer>
            </div>
            <div className="card p-4">
                <div className="flex justify-between items-center mb-2">
                    <h3 className="text-md font-semibold text-gray-100">Server Growth</h3>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={serverGrowth}>
                        <defs><linearGradient id="colorMembers" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/><stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/></linearGradient></defs>
                        <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(str) => new Date(str).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})} />
                        <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} domain={['dataMin - 5', 'dataMax + 5']} />
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
                        <Area type="monotone" dataKey="members" stroke="#3b82f6" fillOpacity={1} fill="url(#colorMembers)" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
            <div className="card p-4">
                <h3 className="text-md font-semibold text-gray-100 mb-2 flex items-center gap-2"><FlagIcon className="w-5 h-5 text-yellow-400"/>Most Moderated</h3>
                <div className="space-y-2">
                    {mostModeratedUsers.length > 0 ? mostModeratedUsers.map(user => (
                        <div key={user.user_id} className="flex items-center justify-between bg-gray-800/50 p-2 rounded-lg">
                            <div className="flex items-center gap-3">
                                <img src={getUserAvatar(user)} alt="" className="w-8 h-8 rounded-full" />
                                <div>
                                    <p className="text-sm font-medium text-white">{user.display_name}</p>
                                    <p className="text-xs text-gray-400">{user.risk_level} Risk</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-sm font-bold text-red-400">{user.total_cases} cases</p>
                                <p className="text-xs text-gray-500">{user.open_cases} open</p>
                            </div>
                        </div>
                    )) : <p className="text-center text-gray-400 py-4">No moderated users found.</p>}
                </div>
            </div>
        </div>

        <div className="card p-4">
            <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-grow">
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input type="text" placeholder="Search by name, username, or ID..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-yellow-500" />
                </div>
                <div className="flex gap-2">
                    <button onClick={() => setShowAdvancedFilters(!showAdvancedFilters)} className="btn-secondary flex items-center gap-2"><AdjustmentsHorizontalIcon className="h-5 w-5" /> Advanced</button>
                    <button onClick={resetFilters} className="btn-secondary flex items-center gap-2"><ArrowPathIcon className="h-5 w-5" /> Reset</button>
                </div>
            </div>
            {showAdvancedFilters && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-700">
                    <div><label className="text-xs text-gray-400">Risk Level</label><select value={filters.riskLevel} onChange={e => handleFilterChange('riskLevel', e.target.value)} className="select mt-1"><option value="all">All</option><option value="Low">Low</option><option value="Medium">Medium</option><option value="High">High</option><option value="Critical">Critical</option></select></div>
                    <div><label className="text-xs text-gray-400">User Type</label><select value={filters.botFilter} onChange={e => handleFilterChange('botFilter', e.target.value)} className="select mt-1"><option value="all">All</option><option value="humans">Humans</option><option value="bots">Bots</option></select></div>
                    <div><label className="text-xs text-gray-400">Open Cases</label><select value={filters.hasOpenCases} onChange={e => handleFilterChange('hasOpenCases', e.target.value)} className="select mt-1"><option value="all">Any</option><option value="yes">Yes</option><option value="no">No</option></select></div>
                </div>
            )}
        </div>

        <div className="card overflow-hidden">
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-800">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('display_name')}>User</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('total_cases')}>Cases</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('risk_score')}>Risk</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('joined_at')}>Joined</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-gray-900 divide-y divide-gray-700">
                        {paginatedUsers.map(user => (
                            <tr key={user.user_id} className="hover:bg-gray-800">
                                <td className="px-6 py-4 whitespace-nowrap"><div className="flex items-center"><div className="flex-shrink-0 h-10 w-10 relative"><img className="h-10 w-10 rounded-full" src={getUserAvatar(user)} alt="" /><div className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-gray-900 ${getStatusColor(user.status)}`}></div></div><div className="ml-4"><div className="text-sm font-medium text-gray-100">{user.display_name}</div><div className="text-xs text-gray-400">@{user.username}</div></div></div></td>
                                <td className="px-6 py-4 whitespace-nowrap"><div className="text-sm text-gray-100">{user.total_cases || 0} Total</div><div className="text-xs text-orange-400">{user.open_cases || 0} Open</div></td>
                                <td className="px-6 py-4 whitespace-nowrap"><span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskBadgeColor(user.risk_level)}`}>{user.risk_level}</span><div className="text-xs text-gray-400">Score: {user.risk_score || 0}</div></td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{user.joined_at ? new Date(user.joined_at).toLocaleDateString() : 'N/A'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <button onClick={() => navigate(`/users/${user.user_id}`)} className="text-yellow-400 hover:text-yellow-300 flex items-center gap-1">
                                        <EyeIcon className="h-4 w-4" /> View
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {totalPages > 1 && (
                <div className="bg-gray-800 px-4 py-3 flex items-center justify-between border-t border-gray-700">
                    <div className="text-sm text-gray-400">Page {currentPage} of {totalPages}</div>
                    <div className="flex-1 flex justify-end gap-2">
                        <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} className="btn-secondary">Previous</button>
                        <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} className="btn-secondary">Next</button>
                    </div>
                </div>
            )}
        </div>
      </div>
    </>
  );
};

export default Users;