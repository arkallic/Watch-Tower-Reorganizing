import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon, ExclamationTriangleIcon, UserGroupIcon, ShieldCheckIcon, DocumentTextIcon, FireIcon, ClockIcon, CalendarDaysIcon, ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import CalendarHeatmap from 'react-calendar-heatmap';
import { Tooltip as ReactTooltip } from 'react-tooltip';
import 'react-calendar-heatmap/dist/styles.css';

const StatBox = ({ title, value, icon: Icon, color, subtext }) => (
    <div className="card p-4 text-center">
        <Icon className={`h-6 w-6 ${color} mx-auto mb-2`} />
        <p className="text-xl font-bold text-white">{value}</p>
        <p className="text-xs text-gray-400">{title}</p>
        {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
    </div>
);

const ModeratorProfile = () => {
  const { moderatorId } = useParams();
  const navigate = useNavigate();
  const [modData, setModData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      const response = await fetch(`${apiBase}/api/pagedata/moderator-profile/${moderatorId}`);
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({ detail: `API Error: ${response.status}` }));
        throw new Error(errorBody.detail);
      }
      const data = await response.json();
      setModData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [moderatorId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const heatmapValuesWithCases = useMemo(() => {
    if (!modData?.analytics?.activity_heatmap || !modData?.full_case_history) return [];
    const caseMap = {};
    modData.full_case_history.forEach(c => {
        if (c.created_at) {
            const dateStr = c.created_at.split('T')[0];
            if (!caseMap[dateStr]) caseMap[dateStr] = [];
            caseMap[dateStr].push(c);
        }
    });
    return modData.analytics.activity_heatmap.map(day => ({...day, cases: caseMap[day.date] || [] }));
  }, [modData]);

  if (loading) return <div className="p-6 h-full flex items-center justify-center"><div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div></div>;
  if (error) return <div className="p-6 text-center text-red-400"><ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-2" />Error: {error}</div>;
  if (!modData) return <div className="p-6 text-center text-gray-400">No moderator data found.</div>;

  const { profile, stats, analytics, moderated_users_list, full_case_history } = modData;
  const PIE_COLORS = ['#3b82f6', '#ef4444', '#f97316', '#eab308', '#8b5cf6', '#14b8a6'];
  const actionData = Object.entries(stats.breakdowns.by_action).map(([name, value]) => ({ name, value }));
  const severityData = Object.entries(stats.breakdowns.by_severity).map(([name, value]) => ({ name, value }));

  return (
    <>
      <div className="p-6 space-y-6">
          <div className="card flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 border-t-2 border-yellow-400/50">
              <div className="flex items-center gap-4">
                  <button onClick={() => navigate('/moderators')} className="btn-secondary p-2"><ArrowLeftIcon className="w-5 h-5" /></button>
                  <img src={profile.avatar_url} alt="avatar" className="w-16 h-16 rounded-full" />
                  <div>
                      <h1 className="text-xl font-bold text-white">Moderator Profile: {profile.name}</h1>
                      <p className="text-sm text-gray-400">@{profile.username}</p>
                  </div>
              </div>
              <div className="flex items-center gap-2 text-xs font-semibold">
                  <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-300">Efficiency: {stats.overview.efficiency_score}</span>
                  <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300">{stats.overview.percentage_of_total_cases}% of Team Cases</span>
              </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <StatBox title="Cases This Week" value={stats.timeline.this_week} icon={CalendarDaysIcon} color="text-blue-400" />
              <StatBox title="Cases (30d)" value={stats.timeline.this_month} icon={CalendarDaysIcon} color="text-sky-400" />
              <StatBox title="Avg Resolution" value={stats.performance.avg_resolution_hours ? `${stats.performance.avg_resolution_hours}h` : 'N/A'} icon={ClockIcon} color="text-green-400" />
              <StatBox title="Unique Users Modded" value={stats.overview.unique_users_modded} icon={UserGroupIcon} color="text-purple-400" />
              <StatBox title="Peak Activity" value={analytics.peak_activity_hour_utc} icon={FireIcon} color="text-red-400" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 card p-4">
                  <h3 className="text-base font-semibold text-gray-100 mb-3">Activity Heatmap (Last Year)</h3>
                  <div className="heatmap-container">
                      <CalendarHeatmap
                          startDate={new Date(new Date().setFullYear(new Date().getFullYear() - 1))}
                          endDate={new Date()}
                          values={heatmapValuesWithCases}
                          classForValue={(value) => !value ? 'color-empty' : `color-scale-${Math.min(value.count, 4)}`}
                          tooltipDataAttrs={value => {
                              if (!value || !value.date || !value.cases || value.cases.length === 0) return { 'data-tooltip-id': 'heatmap-tip', 'data-tooltip-content': `No cases on ${value.date}` };
                              const caseLines = value.cases.map(c => `• #${c.case_number} on ${c.display_name}`).join('<br />');
                              return { 'data-tooltip-id': 'heatmap-tip', 'data-tooltip-html': `<strong>${value.date}</strong><br />${value.count} cases:<br />${caseLines}` };
                          }}
                      />
                  </div>
              </div>
              <div className="card p-4">
                  <h3 className="text-base font-semibold text-gray-100 mb-3">Top Modded Channels</h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                      {analytics.top_modded_channels.length > 0 ? analytics.top_modded_channels.map(ch => (
                          <div key={ch.name} className="flex justify-between items-center card-secondary p-2"><p className="text-white font-medium">#{ch.name}</p><p className="text-sm text-gray-400">{ch.count} Case{ch.count > 1 ? 's' : ''}</p></div>
                      )) : <p className="text-center text-gray-500 py-4">No channel data available.</p>}
                  </div>
              </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="card p-4"><h3 className="text-base font-semibold text-gray-100 mb-4">Actions Breakdown</h3><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={actionData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={2}>{actionData.map((e, i) => <Cell key={`cell-${i}`} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /><Legend wrapperStyle={{fontSize: "12px"}}/></PieChart></ResponsiveContainer></div>
              <div className="card p-4"><h3 className="text-base font-semibold text-gray-100 mb-4">Severity Breakdown</h3><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={severityData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={2}>{severityData.map((e, i) => <Cell key={`cell-${i}`} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} /><Legend wrapperStyle={{fontSize: "12px"}}/></PieChart></ResponsiveContainer></div>
              <div className="card p-4">
                  <h3 className="text-base font-semibold text-gray-100 mb-4">Users Moderated (Top 10)</h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                      {moderated_users_list.length > 0 ? moderated_users_list.slice(0, 10).map(u => (
                          <div key={u.name} className="flex justify-between items-center card-secondary p-2"><p className="text-white font-medium">{u.name}</p><p className="text-sm text-gray-400">{u.cases} Case{u.cases > 1 ? 's' : ''}</p></div>
                      )) : <p className="text-center text-gray-500 py-4">No users moderated.</p>}
                  </div>
              </div>
          </div>

          <div className="card">
              <div className="p-4 border-b border-gray-700"><h3 className="text-base font-semibold text-gray-100">Full Case History ({full_case_history.length} cases)</h3></div>
              <div className="overflow-x-auto max-h-[60vh]">
                  <table className="min-w-full">
                      <thead className="bg-gray-800/50"><tr><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Case #</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">User</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Action</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Severity</th><th className="px-4 py-2 text-left text-xs font-medium text-gray-300">Date</th></tr></thead>
                      <tbody className="divide-y divide-gray-700/50">
                          {full_case_history.map(c => (
                              <tr key={c.case_number} className="hover:bg-gray-800/40">
                                  <td className="px-4 py-2 text-sm text-white font-medium">#{c.case_number}</td>
                                  <td className="px-4 py-2 text-sm text-gray-300">{c.display_name}</td>
                                  <td className="px-4 py-2 text-sm text-gray-300">{c.action_type}</td>
                                  <td className="px-4 py-2 text-sm text-gray-300">{c.severity}</td>
                                  <td className="px-4 py-2 text-sm text-gray-400">{new Date(c.created_at).toLocaleDateString()}</td>
                              </tr>
                          ))}
                      </tbody>
                  </table>
              </div>
          </div>
      </div>
      <ReactTooltip id="heatmap-tip" html={true} />
    </>
  );
};

export default ModeratorProfile;