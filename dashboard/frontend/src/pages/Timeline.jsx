import React, { useState, useEffect, useCallback } from 'react';
import { ClockIcon, FunnelIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import TimelineEvent from '../components/TimelineEvent';

const Timeline = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({
        page: 1,
        limit: 25,
        total_pages: 1,
        total_items: 0,
    });

    const fetchData = useCallback(async (page = 1) => {
        setLoading(true);
        setError(null);
        try {
            const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const params = new URLSearchParams({ page, limit: pagination.limit });
            const response = await fetch(isDevelopment ? `http://localhost:8000/api/pagedata/timeline?${params}` : `/api/pagedata/timeline?${params}`);
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to fetch timeline events.');
            }

            const data = await response.json();
            setEvents(Array.isArray(data.logs) ? data.logs : []);
            setPagination({
                page: data.page,
                limit: data.limit,
                total_pages: data.total_pages,
                total_items: data.total_items,
            });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [pagination.limit]);

    useEffect(() => {
        fetchData(1);
    }, [fetchData]);

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= pagination.total_pages) {
            fetchData(newPage);
        }
    };
    
    // Filter out any null or undefined items from the events array before rendering
    const validEvents = events.filter(Boolean);
    
    return (
        <div className="p-6 space-y-5 bg-transparent min-h-full">
            {/* Header */}
            <div className="card border-t-2 border-yellow-400/50">
                <div className="px-6 py-4">
                    <h1 className="text-2xl font-bold text-yellow-400 flex items-center">
                        <ClockIcon className="h-7 w-7 mr-3" />
                        Timeline
                    </h1>
                    <p className="text-sm text-gray-400 mt-1">A chronological and filterable log of all significant server and bot events.</p>
                </div>
            </div>

            {/* Main Content Card */}
            <div className="card">
                <div className="p-4 flex justify-between items-center border-b border-gray-800">
                    <h3 className="text-md font-semibold text-gray-100">Recent Events</h3>
                    <button className="flex items-center space-x-2 px-3 py-2 bg-gray-700/50 hover:bg-gray-700/80 rounded-lg text-sm text-gray-300">
                        <FunnelIcon className="h-4 w-4" />
                        <span>Filter Events</span>
                    </button>
                </div>

                <div className="relative">
                    {/* The timeline vertical line */}
                    <div className="absolute left-4 top-0 w-0.5 h-full bg-gray-700"></div>

                    {loading && <div className="text-center p-12 text-gray-400">Loading events...</div>}
                    {error && <div className="text-center p-12 text-red-400">{error}</div>}
                    
                    {/* This loop now correctly maps over the validEvents array */}
                    {!loading && !error && validEvents.map(event => (
                        <TimelineEvent key={`${event.timestamp}-${event.details?.['Message ID'] || Math.random()}`} event={event} />
                    ))}

                    {!loading && !error && validEvents.length === 0 && (
                        <div className="text-center p-12 text-gray-500">No timeline events found.</div>
                    )}
                </div>

                 {/* Pagination Controls */}
                <div className="p-4 flex items-center justify-between border-t border-gray-800">
                    <span className="text-sm text-gray-400">
                        Showing <span className="font-medium text-gray-200">{Math.min((pagination.page - 1) * pagination.limit + 1, pagination.total_items)}</span> to <span className="font-medium text-gray-200">{Math.min(pagination.page * pagination.limit, pagination.total_items)}</span> of <span className="font-medium text-gray-200">{pagination.total_items}</span> events
                    </span>
                    <div className="flex items-center space-x-2">
                        <button onClick={() => handlePageChange(pagination.page - 1)} disabled={pagination.page <= 1} className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed bg-gray-700/50 hover:bg-gray-700">
                            <ChevronLeftIcon className="h-5 w-5 text-gray-300"/>
                        </button>
                        <span className="text-sm text-gray-300">Page {pagination.page} of {pagination.total_pages}</span>
                        <button onClick={() => handlePageChange(pagination.page + 1)} disabled={pagination.page >= pagination.total_pages} className="p-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed bg-gray-700/50 hover:bg-gray-700">
                             <ChevronRightIcon className="h-5 w-5 text-gray-300"/>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Timeline;