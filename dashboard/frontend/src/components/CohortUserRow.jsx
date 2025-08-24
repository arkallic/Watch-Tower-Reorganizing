import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronDownIcon, ShieldExclamationIcon, ExclamationTriangleIcon, FlagIcon } from '@heroicons/react/24/outline';

// #############################################################################
// # SUB-COMPONENTS
// #############################################################################

const DetailStat = ({ label, value, color = 'text-gray-200' }) => (
    <div>
        <p className="text-xs text-gray-500 uppercase font-semibold">{label}</p>
        <p className={`text-sm font-medium ${color}`}>{value}</p>
    </div>
);

const ActivityGraph = ({ current, baseline }) => {
    const max = Math.max(current, baseline, 1);
    const currentPercent = Math.min((current / max) * 100, 100);
    const baselinePercent = Math.min((baseline / max) * 100, 100);
    const isSurging = current > baseline * 1.5;

    return (
        <div className="col-span-2 space-y-2">
            <p className="text-xs text-gray-500 uppercase font-semibold">Activity Trend (vs. 30d Avg)</p>
            <div>
                <div className="flex justify-between items-center text-xs mb-1">
                    <span className="text-gray-400">Last 7 Days</span>
                    <span className={`font-semibold ${isSurging ? 'text-green-400' : 'text-yellow-400'}`}>{current} msgs</span>
                </div>
                <div className="w-full bg-gray-700/50 rounded-full h-2.5">
                    <div className={`${isSurging ? 'bg-green-500' : 'bg-yellow-500'} h-2.5 rounded-full`} style={{ width: `${currentPercent}%` }}></div>
                </div>
            </div>
            <div>
                 <div className="flex justify-between items-center text-xs mb-1">
                    <span className="text-gray-400">Weekly Average</span>
                    <span className="font-semibold text-gray-400">{baseline} msgs</span>
                </div>
                <div className="w-full bg-gray-700/50 rounded-full h-2.5">
                    <div className="bg-gray-500 h-2.5 rounded-full" style={{ width: `${baselinePercent}%` }}></div>
                </div>
            </div>
        </div>
    );
};

const UserStatusTags = ({ user }) => {
    // These color classes are inspired by the getRiskBadgeColor function in your Users.jsx
    const isHighRisk = user.risk_level === 'High' || user.risk_level === 'Critical';
    const isRecentlyModerated = user.recent_cases > 0;
    const isAiFlagged = user.total_flags > 0 && user.total_cases === 0;

    if (!isHighRisk && !isRecentlyModerated && !isAiFlagged) {
        return <DetailStat label="Status" value="Normal" color="text-green-400" />;
    }

    return (
        <div className="col-span-1">
             <p className="text-xs text-gray-500 uppercase font-semibold">Status Flags</p>
             <div className="mt-2 flex flex-col space-y-2">
                {isHighRisk && (
                    <div className="flex items-center space-x-2 text-sm text-red-400">
                        <ShieldExclamationIcon className="w-5 h-5 flex-shrink-0" />
                        <span>High Risk ({user.risk_score})</span>
                    </div>
                )}
                {isRecentlyModerated && (
                    <div className="flex items-center space-x-2 text-sm text-amber-400">
                        <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0" />
                        <span>Recently Moderated</span>
                    </div>
                )}
                {isAiFlagged && (
                     <div className="flex items-center space-x-2 text-sm text-orange-400">
                        <FlagIcon className="w-5 h-5 flex-shrink-0" />
                        <span>AI-Flagged ({user.total_flags})</span>
                    </div>
                )}
             </div>
        </div>
    );
};

// #############################################################################
// # MAIN COMPONENT: CohortUserRow
// #############################################################################

const CohortUserRow = ({ user, cohortKey, isExpanded, onToggle }) => {
    const trend = user.activity_trend || {};
    const social = user.social_stats || {};
    const reactions = user.reactions || {};
    
    const showGraph = ['surging_activity', 'declining_activity'].includes(cohortKey);
    const showSocial = ['community_pillars', 'isolated_members'].includes(cohortKey);
    const showSentiment = ['community_uplifters', 'chronic_critics'].includes(cohortKey);
    const showVoice = cohortKey === 'voice_vanguards';
    const showMembership = cohortKey === 'returning_members';

    // This function for getting risk badge colors is taken directly from your Users.jsx
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


    return (
        <>
            <tr className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer" onClick={onToggle}>
                <td className="p-3">
                    <div className="flex items-center space-x-3">
                        <Link to={`/users/${user.user_id}`} className="relative">
                            <img src={user.avatar} alt={user.display_name} className="w-9 h-9 rounded-full" />
                            <div className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-gray-900 ${getStatusColor(user.status)}`}></div>
                        </Link>
                        <div>
                            <Link to={`/users/${user.user_id}`} className="font-medium text-gray-200 hover:text-yellow-400">{user.display_name}</Link>
                            <p className="text-xs text-gray-500">@{user.username}</p>
                        </div>
                    </div>
                </td>
                <td className="p-3 text-sm text-center">{user.server_tenure_days} days</td>
                <td className="p-3 text-sm text-center">{user.messages_30d || 0}</td>
                <td className="p-3 text-sm text-center">{user.total_cases}</td>
                <td className="p-3 text-sm text-center">
                    <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full border ${getRiskBadgeColor(user.risk_level)}`}>
                        {user.risk_level}
                    </span>
                </td>
                <td className="p-3 text-center">
                    <ChevronDownIcon className={`w-5 h-5 text-gray-400 transform transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
                </td>
            </tr>

            {isExpanded && (
                <tr className="bg-black/20">
                    <td colSpan="6" className="p-0">
                        <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-6 border-l-4 border-yellow-500/50">
                            <UserStatusTags user={user} />
                            
                            <div className="col-span-2">
                                {showGraph && <ActivityGraph current={trend.messages_last_7d} baseline={trend.avg_weekly_messages_30d} />}
                                {showSocial && <div className="grid grid-cols-2 gap-4"><DetailStat label="Replies Received" value={social.replies_received || 0} color="text-green-400"/><DetailStat label="Mentions Received" value={social.mentions_received || 0} color="text-green-400"/><DetailStat label="Replies Given" value={social.replies_given || 0} /><DetailStat label="Mentions Given" value={social.mentions_given || 0} /></div>}
                                {showSentiment && <div className="grid grid-cols-2 gap-4"><DetailStat label="Positive Reactions Given" value={reactions.positive || 0} color="text-lime-400" /><DetailStat label="Negative Reactions Given" value={reactions.negative || 0} color="text-rose-400" /></div>}
                                {showVoice && <DetailStat label="Time in Voice (30d)" value={`${user.voice_minutes_30d || 0} minutes`} color="text-cyan-400" />}
                                {showMembership && <DetailStat label="Total Joins" value={user.join_leave_history.filter(h => h.action === 'join').length} color="text-indigo-400" />}
                                {!showGraph && !showSocial && !showSentiment && !showVoice && !showMembership && <DetailStat label="Activity Trend" value={`${trend.activity_change_percentage || 0}% Change vs 30d Avg`} />}
                            </div>
                        </div>
                    </td>
                </tr>
            )}
        </>
    );
};

export default CohortUserRow;