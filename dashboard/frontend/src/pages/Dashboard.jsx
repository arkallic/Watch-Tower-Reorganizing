// dashboard/frontend/src/pages/Dashboard.jsx

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Chart from 'chart.js/auto';
import {
  UserGroupIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
  TrashIcon,
  FlagIcon,
  UserIcon,
  CpuChipIcon,
  ArrowPathIcon,
  ServerIcon,
  CommandLineIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';

const DynamicChart = React.memo(({ chartData }) => {
    const canvasRef = useRef(null);
    const chartInstanceRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || !chartData || !chartData.labels || chartData.labels.length === 0) return;
        
        if (chartInstanceRef.current) {
            chartInstanceRef.current.destroy();
        }

        const ctx = canvas.getContext('2d');
        chartInstanceRef.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: chartData.datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#d1d5db' }
                    },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        titleColor: '#f9fafb',
                        bodyColor: '#d1d5db',
                        borderColor: '#4b5563',
                        borderWidth: 1,
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#9ca3af' },
                        beginAtZero: true
                    }
                }
            }
        });

        return () => {
            if (chartInstanceRef.current) {
                chartInstanceRef.current.destroy();
            }
        };
    }, [chartData]);

    return (
        <div className="px-3 pb-3" style={{ height: '250px' }}>
            <canvas ref={canvasRef} className="w-full h-full" />
        </div>
    );
});

const Dashboard = () => {
  const navigate = useNavigate();

  // State Management - Kept clean and simple
  const [stats, setStats] = useState({});
  const [systemHealth, setSystemHealth] = useState({});
  const [topUsers, setTopUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [debugInfo, setDebugInfo] = useState({});
  const [showDebug, setShowDebug] = useState(false);
  
  const [timeSeriesData, setTimeSeriesData] = useState(null);
  const [chartLoading, setChartLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('Messages');
  const [timeRange, setTimeRange] = useState('24h');

  // --- HONED DATA FETCHING ---
  // Main data fetch - simplified to rely on the BFF
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const response = await fetch(isDevelopment ? 'http://localhost:8000/api/pagedata/dashboard' : '/api/pagedata/dashboard');

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const allData = await response.json();

      if (allData.error) {
        throw new Error(allData.error);
      }

      setStats(allData.stats || {});
      setSystemHealth(allData.systemHealth || {});
      setTopUsers(allData.topUsers || []);
      
      setDebugInfo({ apiStatus: allData.stats ? 'Connected' : 'Error' });
      setLastUpdated(new Date());
    } catch (err) { 
      console.error('Dashboard fetch error:', err);
      setError('Failed to load dashboard data. Ensure the bot and dashboard backend are running.'); 
    } finally { 
      setLoading(false); 
    }
  }, []);
  
  // Chart data fetch - now uses its own dedicated, efficient endpoint
  const fetchChartData = useCallback(async (range) => {
    setChartLoading(true);
    try {
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const response = await fetch(isDevelopment ? `http://localhost:8000/api/pagedata/dashboard-chart?range=${range}` : `/api/pagedata/dashboard-chart?range=${range}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch chart data');
        }
        
        const chartData = await response.json();
        setTimeSeriesData(chartData);
    } catch (chartError) {
        console.error('Chart fetch error:', chartError);
        setTimeSeriesData(null); // Clear old data on error
    } finally {
        setChartLoading(false);
    }
  }, []);

  // --- EFFECT HOOKS ---
  // Initial and interval fetch for main dashboard stats
  useEffect(() => { 
    fetchDashboardData(); 
    const interval = setInterval(fetchDashboardData, 120000); 
    return () => clearInterval(interval); 
  }, [fetchDashboardData]);

  // Fetch chart data when the component mounts or when the time range changes
  useEffect(() => {
    fetchChartData(timeRange);
  }, [timeRange, fetchChartData]);

  // --- HELPER FUNCTIONS (UNCHANGED) ---
  const getHealthColor = p => (p < 60 ? 'bg-green-500' : p < 80 ? 'bg-yellow-500' : 'bg-red-500');
  const getHealthTextColor = p => (p < 60 ? 'text-green-400' : p < 80 ? 'text-yellow-400' : 'text-red-400');
  const formatBytes = (bytes) => {
    if (bytes === 0 || !bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  const formatUptime = (seconds) => {
    if (!seconds) return 'Unknown';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  // --- CHART DATA PROCESSING (UNCHANGED) ---
  const getChartData = () => {
    if (!timeSeriesData || !timeSeriesData.dataMap) return { labels: [], datasets: [] };

    const { labels, dataMap } = timeSeriesData;
    const colors = {
        Messages: 'rgba(59, 130, 246, 0.7)',
        Cases: 'rgba(239, 68, 68, 0.7)',
        Kicks: 'rgba(249, 115, 22, 0.7)',
        Bans: 'rgba(168, 85, 247, 0.7)',
        Notes: 'rgba(107, 114, 128, 0.7)',
    };

    const createDataset = (label, dataKey) => ({
        label,
        data: labels.map(l => dataMap[l]?.[dataKey.toLowerCase()] || 0),
        borderColor: colors[label],
        backgroundColor: colors[label].replace('0.7', '0.2'),
        fill: true,
        tension: 0.4,
        pointRadius: 0,
    });
    
    let datasets = [];
    if (activeTab === 'All Data') {
        datasets = Object.keys(colors).map(key => createDataset(key, key));
    } else {
        datasets.push(createDataset(activeTab, activeTab));
    }

    return { labels, datasets };
  };
  
  // --- RENDER LOGIC (UNCHANGED) ---
  if (loading) return (
    <div className="p-6 h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div>
    </div>
  );
  
  if (error) return (
    <div className="p-6 h-full">
      <div className="card flex flex-col items-center justify-center p-8 h-full">
        <ExclamationTriangleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-200">Error</h2>
        <p className="text-gray-400 mb-4">{error}</p>
        <button onClick={fetchDashboardData} className="btn-primary">Retry</button>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-5 bg-transparent min-h-full">
      {/* Header section remains the same */}
      <div className="card border-t-2 border-yellow-400/50">
        <div className="px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <img src="/images/logo.png" alt="Watch Tower Logo" className="h-12 w-12" />
              <div>
                <h1 className="text-2xl font-bold text-yellow-400">Dashboard</h1>
                <div className="flex items-center space-x-4 text-sm text-gray-400 mt-1">
                  <div className="flex items-center space-x-2"><ServerIcon className="h-4 w-4" /><span>{stats.guildName}</span></div>
                  <span>•</span><span>Last updated: {lastUpdated?.toLocaleTimeString()}</span><span>•</span>
                  <div className="flex items-center space-x-1.5"><div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div><span>{stats.messageVelocity} msg/hr</span></div>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 bg-black/20 rounded-lg px-3 py-2">
                <div className={`w-2 h-2 rounded-full ${stats.botOnline ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className="text-sm text-gray-300">Bot Online</span>
                <span className="text-xs text-gray-500">• {stats.botLatency}</span>
              </div>
                <div className="flex items-center space-x-2 bg-black/20 rounded-lg px-3 py-2">
                <CpuChipIcon className={`w-4 h-4 ${stats.ollamaConnected ? 'text-green-400' : 'text-red-400'}`} />
                <span className="text-sm text-gray-300">
                  {stats.ollamaConnected ? 'AI Connected' : 'AI Offline'}
                </span>
              </div>
              <button onClick={fetchDashboardData} className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 px-3 py-2 rounded-lg transition-colors flex items-center space-x-2"><ArrowPathIcon className="w-4 h-4" /><span className="text-sm">Refresh</span></button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content grid remains the same */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Stat cards remain the same */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="card hover:scale-105 transition-transform cursor-pointer" onClick={() => navigate('/cases')}>
              <div className="p-4"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-400">Open Cases</p><p className="text-2xl font-bold text-white">{stats.openCases}</p><p className="text-xs text-gray-500 mt-1">{stats.totalCases} total</p></div><div className="p-3 bg-red-500/20 rounded-lg"><ExclamationTriangleIcon className="h-6 w-6 text-red-400" /></div></div></div>
            </div>
            <div className="card hover:scale-105 transition-transform cursor-pointer" onClick={() => navigate('/users')}>
              <div className="p-4"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-400">High Risk</p><p className="text-2xl font-bold text-white">{stats.highRiskUsers}</p><p className="text-xs text-gray-500 mt-1">{stats.flaggedUsers} flagged</p></div><div className="p-3 bg-orange-500/20 rounded-lg"><UserIcon className="h-6 w-6 text-orange-400" /></div></div></div>
            </div>
            <div className="card hover:scale-105 transition-transform cursor-pointer" onClick={() => navigate('/users')}>
              <div className="p-4"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-400">Clean Users</p><p className="text-2xl font-bold text-white">{stats.cleanUsers}</p><p className="text-xs text-gray-500 mt-1">{stats.humanMembers > 0 ? Math.round((stats.cleanUsers / stats.humanMembers) * 100) : 0}% of humans</p></div><div className="p-3 bg-green-500/20 rounded-lg"><ShieldCheckIcon className="h-6 w-6 text-green-400" /></div></div></div>
            </div>
            <div className="card hover:scale-105 transition-transform cursor-pointer">
              <div className="p-4"><div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-400">Deleted (24h)</p><p className="text-2xl font-bold text-white">{stats.totalDeletions}</p><p className="text-xs text-gray-500 mt-1">messages</p></div><div className="p-3 bg-purple-500/20 rounded-lg"><TrashIcon className="h-6 w-6 text-purple-400" /></div></div></div>
            </div>
          </div>

          {/* Chart section remains the same */}
          <div className="card flex flex-col">
            <div className="p-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                    <h3 className="text-md font-semibold text-gray-100 mb-2 sm:mb-0">Live Activity Monitor</h3>
                    <div className="flex items-center space-x-2">
                        {['24h', '7d', '30d'].map(range => (
                            <button key={range} onClick={() => setTimeRange(range)}
                                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                    timeRange === range ? 'bg-yellow-500/30 text-yellow-300' : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/40'
                                }`}>
                                {range === '24h' ? '24 Hours' : range === '7d' ? 'Week' : 'Month'}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="flex space-x-1 mt-3 border-b border-gray-700/50 overflow-x-auto">
                    {['Messages', 'Cases', 'Kicks', 'Bans', 'Notes', 'All Data'].map(tab => (
                        <button key={tab} onClick={() => setActiveTab(tab)}
                            className={`px-3 py-2 text-xs font-medium whitespace-nowrap transition-colors duration-200 border-b-2 ${
                                activeTab === tab ? 'text-yellow-400 border-yellow-400' : 'text-gray-400 border-transparent hover:text-white'
                            }`}>
                            {tab}
                        </button>
                    ))}
                </div>
            </div>
            {chartLoading ? (
                <div className="h-[250px] flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
                </div>
            ) : (
                <DynamicChart chartData={getChartData()} />
            )}
          </div>
          
          {/* Info cards remain the same */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center"><UserGroupIcon className="h-5 w-5 mr-2 text-yellow-400" />Guild Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between"><span className="text-gray-400">Total Members</span><span className="text-white font-medium">{stats.totalMembers}</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Humans</span><span className="text-white font-medium">{stats.humanMembers}</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Bots</span><span className="text-white font-medium">{stats.botMembers}</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Online</span><span className="text-green-400 font-medium">{stats.onlineMembers}</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Channels</span><span className="text-white font-medium">{stats.guildChannels}</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Roles</span><span className="text-white font-medium">{stats.guildRoles}</span></div>
                  <div className="flex justify-between"><span className="text-gray-400">Server Boosts</span><span className="text-purple-400 font-medium">{stats.serverBoosts} (Level {stats.serverBoostLevel})</span></div>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="p-6">
                 <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center"><FlagIcon className="h-5 w-5 mr-2 text-yellow-400" />Moderation Stats</h3>
                 <div className="space-y-3">
                     <div className="flex justify-between"><span className="text-gray-400">Total Cases</span><span className="text-white font-medium">{stats.totalCases}</span></div>
                     <div className="flex justify-between"><span className="text-gray-400">Open Cases</span><span className="text-red-400 font-medium">{stats.openCases}</span></div>
                     <div className="flex justify-between"><span className="text-gray-400">AI Flags</span><span className="text-orange-400 font-medium">{stats.totalFlags}</span></div>
                     <div className="flex justify-between"><span className="text-gray-400">Active Moderators</span><span className="text-blue-400 font-medium">{stats.moderatorActivity}</span></div>
                     <div className="flex justify-between"><span className="text-gray-400">Avg Response</span><span className="text-green-400 font-medium">N/A</span></div>
                     <div className="flex justify-between"><span className="text-gray-400">Messages/Hour</span><span className="text-cyan-400 font-medium">{stats.messageVelocity}</span></div>
                 </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Sidebar panels remain the same */}
        <div className="space-y-6">
          <div className="card">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-100 mb-4 flex items-center justify-between">
                <span className="flex items-center"><FlagIcon className="h-5 w-5 mr-2 text-yellow-400" />Top Risky Users</span>
                <button onClick={() => navigate('/users')} className="text-xs text-yellow-400 hover:text-yellow-300">View All</button>
              </h3>
              <div className="space-y-3">
                {topUsers.length > 0 ? topUsers.map((user, index) => (
                  <div key={user.user_id || index} className="flex items-center justify-between p-3 bg-gray-800/30 rounded-lg">
                    <div className="flex items-center space-x-3"><div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-xs font-medium">{index + 1}</div><div><p className="text-sm font-medium text-white">{user.display_name || user.username}</p><p className="text-xs text-gray-400">{user.total_cases || 0} cases</p></div></div>
                    <div className="text-right"><p className="text-sm font-medium text-red-400">{user.risk_score || 0} score</p><p className="text-xs text-gray-500">{user.risk_level || 'Low'} risk</p></div>
                  </div>
                )) : <div className="text-center py-6 text-gray-400"><FlagIcon className="h-12 w-12 mx-auto mb-2 opacity-50" /><p className="text-sm">No users with cases found</p></div>}
              </div>
            </div>
          </div>
          
          <div className="card">
             <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-100 flex items-center">
                        <CommandLineIcon className="h-5 w-5 mr-2 text-yellow-400" />
                        System Health
                    </h3>
                    <button onClick={() => setShowDebug(!showDebug)} className="text-xs text-gray-400 hover:text-white flex items-center">
                        {showDebug ? 'Hide Debug' : 'Show Debug'}
                        {showDebug ? <ChevronUpIcon className="h-4 w-4 ml-1" /> : <ChevronDownIcon className="h-4 w-4 ml-1" />}
                    </button>
                </div>
                 <div className="space-y-3">
                     <div>
                         <div className="flex justify-between items-center"><span className="text-gray-400 text-sm">CPU</span><span className={`text-sm font-medium ${getHealthTextColor(systemHealth.cpu?.usage_percent || 0)}`}>{systemHealth.cpu?.usage_percent?.toFixed(1) || 0}%</span></div>
                         <div className="w-full bg-gray-700 rounded-full h-2 mt-1"><div className={`h-2 rounded-full ${getHealthColor(systemHealth.cpu?.usage_percent || 0)}`} style={{ width: `${Math.min(systemHealth.cpu?.usage_percent || 0, 100)}%` }}></div></div>
                     </div>
                     <div>
                         <div className="flex justify-between items-center"><span className="text-gray-400 text-sm">Memory</span><span className={`text-sm font-medium ${getHealthTextColor(systemHealth.memory?.usage_percent || 0)}`}>{systemHealth.memory?.usage_percent?.toFixed(1) || 0}%</span></div>
                         <div className="w-full bg-gray-700 rounded-full h-2 mt-1"><div className={`h-2 rounded-full ${getHealthColor(systemHealth.memory?.usage_percent || 0)}`} style={{ width: `${Math.min(systemHealth.memory?.usage_percent || 0, 100)}%` }}></div></div>
                     </div>
                     <div className="border-t border-gray-700 pt-3 text-xs text-gray-500 space-y-1">
                         <div>Uptime: {formatUptime(systemHealth.system?.uptime_seconds)}</div>
                         <div>Bot Memory: {systemHealth.bot?.memory_usage_mb?.toFixed(1) || 0} MB</div>
                     </div>
                     <div className="border-t border-gray-700 pt-3">
                         <div className="flex justify-between"><span className="text-gray-400 text-sm">Data Sent</span><span className="text-green-400 text-sm">{formatBytes(systemHealth.network?.bytes_sent || 0)}</span></div>
                         <div className="flex justify-between"><span className="text-gray-400 text-sm">Data Received</span><span className="text-blue-400 text-sm">{formatBytes(systemHealth.network?.bytes_recv || 0)}</span></div>
                     </div>
                 </div>
                {showDebug && (
                    <div className="mt-4 pt-4 border-t border-gray-700">
                        <h4 className="text-sm font-medium text-orange-400 mb-2">API Connection Status</h4>
                        <div className="space-y-1 text-xs">
                          <div className={`flex justify-between ${debugInfo.apiStatus === 'Connected' ? 'text-green-400' : 'text-red-400'}`}>
                              <span>Dashboard API:</span>
                              <span>{debugInfo.apiStatus === 'Connected' ? '✓ Connected' : '✗ Error'}</span>
                          </div>
                        </div>
                    </div>
                )}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;