import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { format, formatDistanceToNow } from 'date-fns';
import {
    ChevronDownIcon, CogIcon, UserPlusIcon, UserMinusIcon, NoSymbolIcon,
    ArrowLeftOnRectangleIcon, ScaleIcon, TrashIcon, FlagIcon, UserCircleIcon,
    ChatBubbleBottomCenterTextIcon, ShieldExclamationIcon
} from '@heroicons/react/24/outline';

// Helper to get a descriptive icon and title for each event type
const getEventMetadata = (eventType) => {
    const defaultMeta = { icon: UserCircleIcon, color: 'text-gray-400', title: 'Unknown Event' };
    const eventMap = {
        'SETTING_CHANGED': { icon: CogIcon, color: 'text-yellow-400', title: 'Bot Setting Changed' },
        'ROLE_CHANGED': { icon: ShieldExclamationIcon, color: 'text-indigo-400', title: 'User Role Changed' },
        'CASE_CREATED': { icon: ScaleIcon, color: 'text-green-400', title: 'Case Created' },
        'MESSAGE_DELETED': { icon: TrashIcon, color: 'text-rose-400', title: 'Message Deleted' },
        'COMMAND_USED': { icon: ChatBubbleBottomCenterTextIcon, color: 'text-cyan-400', title: 'Command Used' },
        'AI_FLAGGED_MESSAGE': { icon: FlagIcon, color: 'text-orange-400', title: 'AI Flagged Message' },
        'USER_NAME_CHANGED': { icon: UserCircleIcon, color: 'text-teal-400', title: 'User Name Changed' },
        'MEMBER_KICKED': { icon: UserMinusIcon, color: 'text-amber-500', title: 'Member Kicked' },
        'MEMBER_LEFT': { icon: ArrowLeftOnRectangleIcon, color: 'text-gray-400', title: 'Member Left' },
        'MEMBER_BANNED': { icon: NoSymbolIcon, color: 'text-red-500', title: 'Member Banned' },
        'MEMBER_JOINED': { icon: UserPlusIcon, color: 'text-lime-400', title: 'Member Joined' },
    };
    return eventMap[eventType] || defaultMeta;
};

// Component to render a user with a clickable link
const UserDisplay = ({ user }) => {
    if (!user || !user.id) {
        return <span className="font-medium text-gray-300">{user?.name || 'System'}</span>;
    }
    return (
        <Link to={`/users/${user.id}`} className="inline-flex items-center space-x-2 group hover:underline">
            <img 
                src={user.avatar || '/images/default-avatar.png'}
                alt={user.name || 'User'} 
                className="w-6 h-6 rounded-full" 
            />
            <span className="font-medium text-gray-200 group-hover:text-yellow-400 transition-colors">{user.name}</span>
        </Link>
    );
};

const TimelineEvent = ({ event }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!event || !event.event_type || !event.timestamp) {
        return null; 
    }

    const eventDate = new Date(event.timestamp);
    const isDateValid = !isNaN(eventDate);

    const { icon: Icon, color, title } = getEventMetadata(event.event_type);

    // This makes the logic more reusable for any event that has channel info
    const channelName = event.details?.Channel;

    return (
        <div className="relative pl-8 py-4">
            {/* Timeline Icon */}
            <div className="absolute left-0 top-4 h-full">
                <div className={`w-8 h-8 rounded-full bg-gray-800 border-2 border-gray-700 flex items-center justify-center -translate-x-1/2`}>
                    <Icon className={`w-5 h-5 ${color}`} />
                </div>
            </div>

            {/* Main Content */}
            <div 
                className="card-sm cursor-pointer hover:border-yellow-500/50 transition-colors duration-200"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="p-4 flex items-start justify-between">
                    <div className="flex-1 pr-4">
                        <p className="font-semibold text-gray-100">{title}</p>
                        
                        <div className="text-sm text-gray-400 mt-1 flex items-center flex-wrap gap-x-2">
                           <span>By</span>
                           <UserDisplay user={event.actor} />
                           
                           {event.target?.id && (
                               <>
                                   <span>on</span>
                                   <UserDisplay user={event.target} />
                               </>
                           )}
                           
                           <span className="hidden sm:inline mx-1">•</span>
                           
                           <span className="whitespace-nowrap">
                               {isDateValid ? formatDistanceToNow(eventDate, { addSuffix: true }) : "Invalid date"}
                           </span>
                        </div>

                        {/* --- NEW SECTION FOR CHANNEL PREVIEW --- */}
                        {/* This will now show for ANY event that has channel info in its details */}
                        {channelName && (
                            <p className="mt-2 text-xs text-gray-500">
                                in channel <span className="font-medium text-gray-400">{channelName}</span>
                            </p>
                        )}
                        {/* --- END OF NEW SECTION --- */}

                        {/* Message Preview Section */}
                        {event.event_type === 'MESSAGE_DELETED' && event.details?.Content && event.details.Content !== '[Content not available]' && (
                            <blockquote className="mt-2 pl-3 py-1 border-l-2 border-gray-700 text-gray-400 italic text-sm max-w-prose">
                                "{event.details.Content.length > 120 
                                    ? `${event.details.Content.substring(0, 120)}...` 
                                    : event.details.Content}"
                            </blockquote>
                        )}

                    </div>
                    <div className="flex items-center space-x-4 pl-2">
                        <span className="text-xs text-gray-500 hidden md:block" title={isDateValid ? format(eventDate, 'MMM d, yyyy HH:mm:ss') : "Invalid Date"}>
                            {isDateValid ? format(eventDate, 'HH:mm') : "--:--"}
                        </span>
                        <ChevronDownIcon className={`w-5 h-5 text-gray-400 transform transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
                    </div>
                </div>

                {/* Collapsible Details */}
                <div 
                    className={`overflow-hidden transition-all duration-300 ease-in-out ${isExpanded ? 'max-h-[500px]' : 'max-h-0'}`}
                >
                    <div className="border-t border-gray-700/50 p-4 bg-black/20">
                        <h4 className="font-semibold text-gray-300 mb-2">Event Details</h4>
                        <div className="space-y-1 text-xs text-gray-400">
                           {event.details && typeof event.details === 'object' ? (
                                Object.entries(event.details).map(([key, value]) => (
                                   <div key={key} className="flex">
                                       <span className="w-1/3 sm:w-1/4 font-medium text-gray-500">{key}:</span>
                                       <span className="w-2/3 sm:w-3/4 whitespace-pre-wrap break-words">{String(value)}</span>
                                   </div>
                                ))
                           ) : (
                                <div>No details available.</div>
                           )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TimelineEvent;