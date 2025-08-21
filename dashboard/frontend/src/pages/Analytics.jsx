// dashboard/frontend/src/pages/Analytics.jsx

import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer, Area, AreaChart
} from 'recharts';
import {
  ArrowPathIcon, CalendarDaysIcon, ChartBarIcon, TrophyIcon, ShieldCheckIcon, ClockIcon, CheckCircleIcon, FireIcon
} from '@heroicons/react/24/outline';

// (Components StatCard, ChartContainer are unchanged)
const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="card p-4 flex items-center gap-4">
        <Icon className={`h-8 w-8 ${color}`} />
        <div className="flex-1">
            <p className="text-sm text-gray-400">{title}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
        </div>
    </div>
);

const ChartContainer = ({ title, children }) => (
    <div className="card p-4">
      <h3 className="text-md font-semibold text-gray-100 mb-4">{title}</h3>
      <div className="h-80">{children}</div>
    </div>
);

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('30');
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      
      // FIX: Changed URL from /api/pagedata/analytics to the correct backend route
      const response = await fetch(`${apiBase}/api/analytics/comprehensive?days=${timeRange}`);
      
      if (!response.ok) throw new Error(`API Error: ${response.status}`);
      const data = await response.json();
      if (data.error || data.detail) throw new Error(data.error || data.detail);
      
      setAnalyticsData(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch analytics data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  const PIE_COLORS = ['#3b82f6', '#ef4444', '#f97316', '#eab308', '#8b5cf6', '#14b8a6'];

  if (loading) {
    return (
      <div className="p-6 h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div>
      </div>
    );
  }
  
  if (error || !analyticsData) {
    return <div className="p-6 text-center text-red-400">Error: {error || 'Could not load analytics data.'}</div>;
  }

  const { overview, trends, leaderboards, breakdowns } = analyticsData;

  // ... (rest of the component's JSX is unchanged) ...
  return (
    <div className="p-6 space-y-6">
      <div className="card border-t-2 border-yellow-400/50">
        <div className="px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-yellow-400">Analytics Dashboard</h1>
            <p className="text-sm text-gray-400 mt-1">
              Comprehensive moderation insights. Last updated: {lastUpdated?.toLocaleTimeString()}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center gap-2 bg-gray-800/50 p-1 rounded-lg">
                <CalendarDaysIcon className="h-5 w-5 text-gray-400 ml-2" />
                <select 
                    value={timeRange} 
                    onChange={(e) => setTimeRange(e.target.value)} 
                    className="select bg-transparent border-0 focus:ring-0"
                >
                    <option value="7">Last 7 Days</option>
                    <option value="30">Last 30 Days</option>
                    <option value="90">Last 90 Days</option>
                    <option value="365">Last Year</option>
                </select>
            </div>
            <button onClick={fetchData} className="btn-secondary flex items-center gap-2">
              <ArrowPathIcon className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} /> Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Cases" value={overview.total_cases} icon={ShieldCheckIcon} color="text-blue-400" />
        <StatCard title="Resolution Rate" value={`${overview.resolution_rate}%`} icon={CheckCircleIcon} color="text-green-400" />
        <StatCard title="Open Cases" value={overview.open_cases} icon={ClockIcon} color="text-orange-400" />
        <StatCard title="Busiest Day" value={trends.peak_day} icon={FireIcon} color="text-red-400" />
      </div>

      <ChartContainer title={`Daily Case Volume (Last ${timeRange} Days)`}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={trends.daily_stats} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
            <defs><linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/><stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/></linearGradient></defs>
            <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} tickFormatter={(str) => new Date(str).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})} />
            <YAxis stroke="#9ca3af" fontSize={12} allowDecimals={false} />
            <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" />
            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
            <Area type="monotone" dataKey="cases" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCases)" />
          </AreaChart>
        </ResponsiveContainer>
      </ChartContainer>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartContainer title="Actions Breakdown">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={breakdowns.by_action} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2}>
                {breakdowns.by_action.map((entry, index) => <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>

        <ChartContainer title="Severity Breakdown">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={breakdowns.by_severity} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2}>
                {breakdowns.by_severity.map((entry, index) => <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>

        <div className="card p-4">
            <h3 className="text-md font-semibold text-gray-100 mb-4 flex items-center gap-2"><TrophyIcon className="h-5 w-5 text-yellow-400"/>Moderator Leaderboard</h3>
            <div className="space-y-2">
                {leaderboards.top_moderators.map((mod, index) => (
                    <div key={mod.name} className="flex items-center justify-between p-2 bg-gray-800/50 rounded-lg">
                        <div className="flex items-center gap-3">
                            <span className="font-bold text-gray-400 w-5">#{index + 1}</span>
                            <span className="font-medium text-white">{mod.name}</span>
                        </div>
                        <span className="font-bold text-blue-400">{mod.cases} cases</span>
                    </div>
                ))}
            </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;