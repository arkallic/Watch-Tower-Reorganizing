import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  MagnifyingGlassIcon,
  UserIcon,
  ShieldCheckIcon,
  ArrowPathIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import UserDetailsModal from '../components/UserDetailsModal';
import CaseViewModal from '../components/CaseViewModal';

const getRiskBadgeColor = (riskLevel) => {
    if (riskLevel === 'Critical') return 'bg-purple-500/20 text-purple-300 border-purple-400/30';
    if (riskLevel === 'High') return 'bg-red-500/20 text-red-300 border-red-400/30';
    if (riskLevel === 'Medium') return 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30';
    return 'bg-green-500/20 text-green-300 border-green-400/30';
};
const getStatusBadge = (status) => {
    const styles = { Open: 'bg-orange-500/20 text-orange-300', Resolved: 'bg-green-500/20 text-green-300', 'Auto-Resolved': 'bg-cyan-500/20 text-cyan-300' };
    return styles[status] || 'bg-gray-500/20 text-gray-300';
};
const getActionIcon = (actionType) => {
    switch (actionType?.toLowerCase()) { case 'warn': return '⚠️'; case 'timeout': return '⏰'; case 'kick': return '👢'; case 'ban': return '🔨'; case 'mod_note': return '📝'; default: return '📋'; }
};

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const searchContainerRef = useRef(null);

  const [selectedUserId, setSelectedUserId] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [isCaseModalOpen, setCaseModalOpen] = useState(false);

  const performSearch = useCallback(async (query) => {
    if (query.length < 2) {
      setResults(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      const response = await fetch(`${apiBase}/api/pagedata/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error("Search request failed");
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError("Failed to fetch search results. Please try again later.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const handler = (event) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setResults(null);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (searchQuery.length > 1) {
        performSearch(searchQuery);
      } else {
        setResults(null);
      }
    }, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery, performSearch]);

  const openCaseModal = (caseItem) => {
    setSelectedCase(caseItem);
    setCaseModalOpen(true);
    setSearchQuery('');
    setResults(null);
  };

  const openUserModal = (userId) => {
    setSelectedUserId(userId);
    setSearchQuery('');
    setResults(null);
  };

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="card border-t-2 border-yellow-400/50">
          <div className="px-6 py-4">
            <h1 className="text-2xl font-bold text-yellow-400">Global Search</h1>
            <p className="text-sm text-gray-400 mt-1">Instantly find users and cases across the entire system.</p>
          </div>
        </div>

        <div className="relative" ref={searchContainerRef}>
          <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none z-20" />
          <input
            type="text"
            placeholder="Search by User ID, Name, Case #, or Reason..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input w-full pl-12 text-base relative z-10"
          />
          {searchQuery.length > 1 && (
            <div className="absolute z-0 w-full mt-2 card p-2 space-y-2 max-h-96 overflow-y-auto">
              {loading && <div className="flex items-center justify-center p-4 text-gray-400"><ArrowPathIcon className="w-5 h-5 animate-spin mr-2"/>Searching...</div>}
              {error && <div className="text-red-400 p-4">{error}</div>}
              {results && !loading && (
                <>
                  {results.users.length > 0 && (
                    <div>
                      <h4 className="px-3 py-1 text-xs font-bold text-gray-500 uppercase">Users</h4>
                      {results.users.map(user => (
                        <div key={user.user_id} onClick={() => openUserModal(user.user_id)} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-700/50 cursor-pointer">
                          <div className="flex items-center gap-3"><img src={user.avatar} alt="" className="w-8 h-8 rounded-full"/><div><p className="font-medium text-white">{user.display_name}</p><p className="text-xs text-gray-400">@{user.username}</p></div></div>
                          <span className="text-xs text-gray-400">User ID: {user.user_id}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {results.cases.length > 0 && (
                    <div>
                      <h4 className="px-3 py-1 text-xs font-bold text-gray-500 uppercase">Cases</h4>
                      {results.cases.map(c => (
                        <div key={`${c.user_id}-${c.case_number}`} onClick={() => openCaseModal(c)} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-700/50 cursor-pointer">
                          <div className="flex-1"><p className="font-medium text-white">Case #{c.case_number} - {c.display_name}</p><p className="text-xs text-gray-400 truncate pr-4">{c.reason}</p></div>
                          <span className="text-xs text-gray-400">{c.action_type}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {results.users.length === 0 && results.cases.length === 0 && (
                    <div className="text-center p-4 text-gray-500">No results found.</div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
      <UserDetailsModal userId={selectedUserId} isOpen={!!selectedUserId} onClose={() => setSelectedUserId(null)} />
      <CaseViewModal isOpen={isCaseModalOpen} onClose={() => setCaseModalOpen(false)} selectedCase={selectedCase} getSeverityColor={getRiskBadgeColor} getStatusColor={getStatusBadge} getActionIcon={getActionIcon}/>
    </>
  );
}