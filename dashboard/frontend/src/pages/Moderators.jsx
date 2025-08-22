import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../context/ApiContext';
import {
  MagnifyingGlassIcon, ArrowPathIcon, UserGroupIcon, TrophyIcon, ShieldCheckIcon, BoltIcon,
} from '@heroicons/react/24/outline';

const ModeratorCard = ({ moderator, rank }) => {
    const navigate = useNavigate();
    const isTopPerformer = rank <= 3;
    const isNumberOne = rank === 1;
    const efficiency = moderator.efficiency_score || 0;
    
    const cardClasses = useMemo(() => {
        let base = 'relative card p-4 space-y-4 transition-all duration-300 hover:scale-[1.03] transform cursor-pointer';
        if (isNumberOne) {
            base += ' bg-gradient-to-br from-yellow-800 via-gray-900 to-gray-900 border-yellow-500/80 ring-2 ring-yellow-500/50';
        } else if (isTopPerformer) {
            base += ' bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 border-purple-600/50';
        } else {
            base += ' border-gray-700';
        }
        return base;
    }, [isNumberOne, isTopPerformer]);

    return (
      <div className={cardClasses} onClick={() => navigate(`/moderators/${moderator.moderator_id}`)}>
        {isTopPerformer && (
          <div className={`absolute top-3 right-3 z-20 flex items-center px-2 py-1 rounded-full text-xs font-bold border ${
              isNumberOne 
              ? 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30' 
              : 'bg-purple-500/20 text-purple-300 border-purple-400/30'
          }`}>
            <TrophyIcon className="w-4 h-4 mr-1.5" />
            {isNumberOne ? '#1 Performer' : 'Top Performer'}
          </div>
        )}
  
        <div className="flex items-center space-x-3">
          <img src={moderator.avatar_url} alt={moderator.name} className="w-12 h-12 rounded-full" />
          <div>
            <h3 className="font-semibold text-lg text-white">{moderator.name}</h3>
            <p className="text-sm text-gray-400">@{moderator.username}</p>
          </div>
        </div>
  
        <div className="grid grid-cols-2 gap-4 text-center">
          <div className="bg-gray-800/50 p-2 rounded-lg">
            <p className="text-2xl font-bold text-white">{moderator.total_cases}</p>
            <p className="text-xs text-gray-400">Total Cases</p>
          </div>
          <div className="bg-gray-800/50 p-2 rounded-lg">
            <p className={`text-2xl font-bold ${efficiency >= 80 ? 'text-green-400' : efficiency >= 60 ? 'text-yellow-400' : 'text-red-400'}`}>
              {efficiency}
            </p>
            <p className="text-xs text-gray-400">Efficiency Score</p>
          </div>
        </div>
      </div>
    );
};

const Moderators = () => {
  const { api } = useApi();
  const [moderators, setModerators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getModerators();
      if (data.error) throw new Error(data.error);
      setModerators(data.moderators || []);
      setSummary(data.summary || {});
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch moderators:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const filteredModerators = useMemo(() => 
    moderators.filter(mod =>
      mod.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mod.moderator_id.includes(searchTerm) ||
      mod.username.toLowerCase().includes(searchTerm.toLowerCase())
    ), [moderators, searchTerm]);
  
  if (loading && !moderators.length) {
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
              <h1 className="text-2xl font-bold text-yellow-400">Moderators</h1>
              <p className="text-sm text-gray-400 mt-1">Team performance and activity overview. Last updated: {lastUpdated?.toLocaleTimeString()}</p>
            </div>
            <button onClick={fetchData} className="btn-secondary flex items-center gap-2"><ArrowPathIcon className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} /> Refresh</button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="card p-4 flex items-center gap-4"><UserGroupIcon className="h-8 w-8 text-blue-400" /><div className="flex-1"><p className="text-sm text-gray-400">Total Moderators</p><p className="text-2xl font-bold text-white">{summary.total_moderators || 0}</p></div></div>
            <div className="card p-4 flex items-center gap-4"><ShieldCheckIcon className="h-8 w-8 text-green-400" /><div className="flex-1"><p className="text-sm text-gray-400">Active This Week</p><p className="text-2xl font-bold text-white">{summary.active_moderators_7d || 0}</p></div></div>
            <div className="card p-4 flex items-center gap-4"><BoltIcon className="h-8 w-8 text-yellow-400" /><div className="flex-1"><p className="text-sm text-gray-400">Team Avg. Cases</p><p className="text-2xl font-bold text-white">{summary.avg_cases_team || 0}</p></div></div>
            <div className="card p-4 flex items-center gap-4"><TrophyIcon className="h-8 w-8 text-purple-400" /><div className="flex-1"><p className="text-sm text-gray-400">Total Cases Handled</p><p className="text-2xl font-bold text-white">{summary.total_cases_team || 0}</p></div></div>
        </div>

        <div className="card p-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, username, or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-yellow-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredModerators.map(moderator => (
            <ModeratorCard
              key={moderator.moderator_id}
              moderator={moderator}
              rank={moderator.rank}
            />
          ))}
        </div>
      </div>
    </>
  );
};

export default Moderators;