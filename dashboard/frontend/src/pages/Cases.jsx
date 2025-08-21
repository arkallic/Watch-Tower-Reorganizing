import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  EyeIcon, PencilIcon, TrashIcon, ChevronDownIcon, ChevronUpIcon, FunnelIcon, MagnifyingGlassIcon,
  ArrowPathIcon, ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import CaseViewModal from '../components/CaseViewModal';
import CaseEditModal from '../components/CaseEditModal';
import CaseDeleteModal from '../components/CaseDeleteModal';

const Cases = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('case_number');
  const [sortDirection, setSortDirection] = useState('desc');
  const [filters, setFilters] = useState({ status: 'all', severity: 'all', action: 'all' });
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(50);
  
  const [selectedCase, setSelectedCase] = useState(null);
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [editForm, setEditForm] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const response = await fetch(isDevelopment ? 'http://localhost:8000/api/pagedata/cases' : '/api/pagedata/cases');
      if (!response.ok) throw new Error(`API Error: ${response.status}`);
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setCases(data.cases || []);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching cases:', err);
      setError(err.message);
      setCases([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const stats = useMemo(() => {
    if (!cases.length) return { total: 0, open: 0, resolved: 0, critical: 0, today: 0, thisWeek: 0 };
    const now = new Date();
    const todayStr = now.toDateString();
    const weekAgo = new Date(new Date().setDate(now.getDate() - 7));
    return {
      total: cases.length,
      open: cases.filter(c => c.status === 'Open').length,
      resolved: cases.filter(c => c.status === 'Resolved' || c.status === 'Auto-Resolved').length,
      critical: cases.filter(c => c.severity === 'Critical').length,
      today: cases.filter(c => new Date(c.created_at).toDateString() === todayStr).length,
      thisWeek: cases.filter(c => new Date(c.created_at) >= weekAgo).length
    };
  }, [cases]);

  const chartData = useMemo(() => {
    const dailyData = {};
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toISOString().split('T')[0];
      dailyData[key] = { name: d.toLocaleDateString('en-US', { weekday: 'short' }), Total: 0, Critical: 0, Resolved: 0 };
    }
    cases.forEach(c => {
      const key = c.created_at.split('T')[0];
      if (dailyData[key]) {
        dailyData[key].Total++;
        if (c.severity === 'Critical') dailyData[key].Critical++;
        if (c.status === 'Resolved' || c.status === 'Auto-Resolved') dailyData[key].Resolved++;
      }
    });
    return Object.values(dailyData);
  }, [cases]);

  const severityData = useMemo(() => [
    { name: 'Low', value: cases.filter(c => c.severity === 'Low').length, color: '#22c55e' },
    { name: 'Medium', value: cases.filter(c => c.severity === 'Medium').length, color: '#f59e0b' },
    { name: 'High', value: cases.filter(c => c.severity === 'High').length, color: '#ef4444' },
    { name: 'Critical', value: cases.filter(c => c.severity === 'Critical').length, color: '#a855f7' }
  ].filter(item => item.value > 0), [cases]);

  const filteredAndSortedCases = useMemo(() => {
    return cases
      .filter(c => {
        const s = searchTerm.toLowerCase();
        return (!s || 
          c.username?.toLowerCase().includes(s) ||
          c.display_name?.toLowerCase().includes(s) ||
          c.reason?.toLowerCase().includes(s) ||
          c.moderator_name?.toLowerCase().includes(s) ||
          c.case_number?.toString().includes(s)) &&
          (filters.status === 'all' || c.status === filters.status) &&
          (filters.severity === 'all' || c.severity === filters.severity) &&
          (filters.action === 'all' || c.action_type === filters.action);
      })
      .sort((a, b) => {
        const aVal = a[sortField];
        const bVal = b[sortField];
        if (sortField === 'created_at') {
          return sortDirection === 'asc' ? new Date(aVal) - new Date(bVal) : new Date(bVal) - new Date(aVal);
        }
        if (typeof aVal === 'string') {
          return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        }
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      });
  }, [cases, searchTerm, filters, sortField, sortDirection]);
  
  const paginatedCases = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredAndSortedCases.slice(start, start + pageSize);
  }, [filteredAndSortedCases, currentPage, pageSize]);
  
  const totalPages = Math.ceil(filteredAndSortedCases.length / pageSize);

  const handleSort = (field) => {
    setSortDirection(sortField === field && sortDirection === 'desc' ? 'asc' : 'desc');
    setSortField(field);
    setCurrentPage(1);
  };
  
  const openEditModal = (caseItem) => {
    setSelectedCase(caseItem);
    setEditForm({
      reason: caseItem.reason || '',
      internal_comment: caseItem.internal_comment || '',
      severity: caseItem.severity || 'Low',
      status: caseItem.status || 'Open',
      tags: caseItem.tags?.join(', ') || '',
      resolvable: caseItem.resolvable || 'Yes'
    });
    setEditModalOpen(true);
  };
  
  const openDeleteModal = (caseItem) => { setSelectedCase(caseItem); setDeleteModalOpen(true); };
  const openViewModal = (caseItem) => { setSelectedCase(caseItem); setViewModalOpen(true); };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const updateData = { ...editForm, tags: editForm.tags ? editForm.tags.split(',').map(tag => tag.trim()).filter(Boolean) : [] };
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const response = await fetch(isDevelopment ? `http://localhost:8000/api/proxy/cases/${selectedCase.user_id}/${selectedCase.case_number}` : `/api/proxy/cases/${selectedCase.user_id}/${selectedCase.case_number}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      if (!response.ok) throw new Error('Failed to update case');
      await fetchData();
      setEditModalOpen(false);
      setSelectedCase(null);
    } catch (error) {
      console.error('Error updating case:', error);
      alert('Failed to update case. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    setSubmitting(true);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const response = await fetch(isDevelopment ? `http://localhost:8000/api/proxy/cases/${selectedCase.user_id}/${selectedCase.case_number}` : `/api/proxy/cases/${selectedCase.user_id}/${selectedCase.case_number}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete case');
      await fetchData();
      setDeleteModalOpen(false);
      setSelectedCase(null);
    } catch (error) {
      console.error('Error deleting case:', error);
      alert('Failed to delete case. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getSeverityBadge = (severity) => {
    const styles = {
      Critical: 'bg-purple-500/20 text-purple-300 border-purple-400/30',
      High: 'bg-red-500/20 text-red-300 border-red-400/30',
      Medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30',
      Low: 'bg-green-500/20 text-green-300 border-green-400/30',
    };
    return styles[severity] || 'bg-gray-500/20 text-gray-300 border-gray-400/30';
  };
  
  const getStatusBadge = (status) => {
    const styles = {
        Open: 'bg-orange-500/20 text-orange-300',
        Resolved: 'bg-green-500/20 text-green-300',
        'Auto-Resolved': 'bg-cyan-500/20 text-cyan-300',
    };
    return styles[status] || 'bg-gray-500/20 text-gray-300';
  };
  
  const getActionIcon = (actionType) => {
    switch (actionType?.toLowerCase()) {
      case 'warn': return '⚠️';
      case 'timeout': return '⏰';
      case 'kick': return '👢';
      case 'ban': return '🔨';
      case 'mod_note': return '📝';
      default: return '📋';
    }
  };
  
  if (loading && !cases.length) {
    return (
      <div className="p-6 h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div>
      </div>
    );
  }
  if (error) {
    return <div className="p-6 text-center text-red-400">Error: {error}</div>;
  }

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="card border-t-2 border-yellow-400/50">
           <div className="px-6 py-4 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-yellow-400">Moderation Cases</h1>
              <p className="text-sm text-gray-400 mt-1">Last updated: {lastUpdated?.toLocaleTimeString()}</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="text-right"><p className="text-xl font-bold text-white">{stats.total}</p><p className="text-xs text-gray-400">Total Cases</p></div>
              <button onClick={fetchData} className="p-2 bg-gray-700/80 text-gray-300 rounded-lg border border-gray-600/50 hover:text-white transition-all"><ArrowPathIcon className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} /></button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="card p-4"><p className="text-sm text-gray-400">Open Cases</p><p className="text-2xl font-bold text-orange-400">{stats.open}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-400">Resolved</p><p className="text-2xl font-bold text-green-400">{stats.resolved}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-400">Critical Cases</p><p className="text-2xl font-bold text-purple-400">{stats.critical}</p></div>
            <div className="card p-4"><p className="text-sm text-gray-400">This Week</p><p className="text-2xl font-bold text-blue-400">{stats.thisWeek}</p></div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 card p-4">
                <h3 className="text-md font-semibold text-gray-100 mb-4">Weekly Case Volume</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                        <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', color: '#d1d5db' }} cursor={{ fill: 'rgba(255,255,255,0.1)' }} />
                        <Legend wrapperStyle={{ fontSize: '12px', color: '#d1d5db' }} />
                        <Bar dataKey="Total" fill="#3b82f6" name="Total" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Critical" fill="#a855f7" name="Critical" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Resolved" fill="#22c55e" name="Resolved" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
            <div className="card p-4">
                <h3 className="text-md font-semibold text-gray-100 mb-4">Severity Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                        <Pie data={severityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} labelLine={false} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                            {severityData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
        
        <div className="card p-4">
            <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-grow"><MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" /><input type="text" placeholder="Search by user, reason, mod, or case #" value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-yellow-500" /></div>
                <button onClick={() => setShowFilters(!showFilters)} className="btn-secondary flex items-center gap-2"><FunnelIcon className="h-5 w-5" /> Filters {showFilters ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}</button>
            </div>
            {showFilters && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-700">
                    <div><label className="text-xs text-gray-400">Status</label><select value={filters.status} onChange={e => setFilters(f => ({...f, status: e.target.value}))} className="select mt-1"><option value="all">All</option><option value="Open">Open</option><option value="Resolved">Resolved</option><option value="Auto-Resolved">Auto-Resolved</option></select></div>
                    <div><label className="text-xs text-gray-400">Severity</label><select value={filters.severity} onChange={e => setFilters(f => ({...f, severity: e.target.value}))} className="select mt-1"><option value="all">All</option><option value="Low">Low</option><option value="Medium">Medium</option><option value="High">High</option><option value="Critical">Critical</option></select></div>
                    <div><label className="text-xs text-gray-400">Action</label><select value={filters.action} onChange={e => setFilters(f => ({...f, action: e.target.value}))} className="select mt-1"><option value="all">All</option><option value="warn">Warn</option><option value="timeout">Timeout</option><option value="kick">Kick</option><option value="ban">Ban</option><option value="mod_note">Note</option></select></div>
                </div>
            )}
        </div>
        
        <div className="card overflow-hidden">
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-800">
                        <tr>
                            {['case_number', 'username', 'action_type', 'severity', 'status', 'created_at', 'moderator_name'].map(field => (
                                <th key={field} className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => handleSort(field)}>
                                    {field.replace('_', ' ')}
                                    {sortField === field && (sortDirection === 'asc' ? ' ▲' : ' ▼')}
                                </th>
                            ))}
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-gray-900 divide-y divide-gray-700">
                        {paginatedCases.map(c => (
                            <tr key={`${c.user_id}-${c.case_number}`} className="hover:bg-gray-800">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">#{c.case_number}</td>
                                <td className="px-6 py-4 whitespace-nowrap"><div className="flex items-center"><img className="h-8 w-8 rounded-full" src={c.user_avatar_url || `https://cdn.discordapp.com/embed/avatars/${(c.username.charCodeAt(0)) % 5}.png`} alt="" /><div className="ml-3"><div className="text-sm font-medium text-gray-100">{c.display_name}</div><div className="text-xs text-gray-400">@{c.username}</div></div></div></td>
                                <td className="px-6 py-4"><div className="text-sm text-gray-100">{c.action_type}</div><div className="text-xs text-gray-400 max-w-xs truncate" title={c.reason}>{c.reason}</div></td>
                                <td className="px-6 py-4 whitespace-nowrap"><span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full border ${getSeverityBadge(c.severity)}`}>{c.severity}</span></td>
                                <td className="px-6 py-4 whitespace-nowrap"><span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(c.status)}`}>{c.status}</span></td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{new Date(c.created_at).toLocaleString()}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-100">{c.moderator_name}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <div className="flex items-center gap-2">
                                        <button onClick={() => openViewModal(c)} className="text-blue-400 hover:text-blue-300"><EyeIcon className="h-5 w-5" /></button>
                                        <button onClick={() => openEditModal(c)} className="text-green-400 hover:text-green-300"><PencilIcon className="h-5 w-5" /></button>
                                        <button onClick={() => openDeleteModal(c)} className="text-red-400 hover:text-red-300"><TrashIcon className="h-5 w-5" /></button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {totalPages > 1 && (
                <div className="bg-gray-800 px-4 py-3 flex items-center justify-between border-t border-gray-700">
                    <div className="text-sm text-gray-400">Page <span className="font-medium text-white">{currentPage}</span> of <span className="font-medium text-white">{totalPages}</span></div>
                    <div className="flex-1 flex justify-end gap-2"><button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} className="btn-secondary disabled:opacity-50">Previous</button><button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} className="btn-secondary disabled:opacity-50">Next</button></div>
                </div>
            )}
            {filteredAndSortedCases.length === 0 && (
                <div className="text-center py-16 text-gray-500"><ExclamationCircleIcon className="h-12 w-12 mx-auto mb-2" /><p>No cases match your criteria.</p></div>
            )}
        </div>
      </div>
      
      <CaseViewModal isOpen={viewModalOpen} onClose={() => setViewModalOpen(false)} selectedCase={selectedCase} getSeverityColor={getSeverityBadge} getStatusColor={getStatusBadge} getActionIcon={getActionIcon} />
      <CaseEditModal isOpen={editModalOpen} onClose={() => setEditModalOpen(false)} selectedCase={selectedCase} editForm={editForm} setEditForm={setEditForm} onSubmit={handleEditSubmit} submitting={submitting} />
      <CaseDeleteModal isOpen={deleteModalOpen} onClose={() => setDeleteModalOpen(false)} selectedCase={selectedCase} onDelete={handleDelete} submitting={submitting} />
    </>
  );
};

export default Cases;