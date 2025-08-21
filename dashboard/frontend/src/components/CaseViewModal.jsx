// dashboard/frontend/src/components/CaseViewModal.jsx
import React from 'react';
import {
  XMarkIcon,
  UserIcon,
  ShieldCheckIcon,
  CalendarIcon,
  TagIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ChatBubbleLeftIcon,
  DocumentIcon
} from '@heroicons/react/24/outline';

const CaseViewModal = ({ selectedCase, isOpen, onClose, getSeverityColor, getStatusColor, getActionIcon }) => {
  if (!isOpen || !selectedCase) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold">Case #{selectedCase.case_number}</h2>
              <p className="text-blue-100 mt-1">Detailed case information and history</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="p-6 space-y-6">
            {/* Case Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-4 bg-white">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <UserIcon className="h-5 w-5" />
                    User Information
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium text-gray-700">Username:</span> <span className="text-gray-900">{selectedCase.username}</span></div>
                    <div><span className="font-medium text-gray-700">Display Name:</span> <span className="text-gray-900">{selectedCase.display_name}</span></div>
                    <div><span className="font-medium text-gray-700">User ID:</span> <span className="text-gray-900">{selectedCase.user_id}</span></div>
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg p-4 bg-white">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <ShieldCheckIcon className="h-5 w-5" />
                    Moderation Details
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium text-gray-700">Action:</span> <span className="text-gray-900">{getActionIcon(selectedCase.action_type)} {selectedCase.action_type}</span></div>
                    <div><span className="font-medium text-gray-700">Moderator:</span> <span className="text-gray-900">{selectedCase.moderator_name}</span></div>
                    <div className="flex items-center"><span className="font-medium text-gray-700">Severity:</span> 
                      <span className={`ml-2 px-2 py-1 rounded-full text-xs border ${getSeverityColor(selectedCase.severity)}`}>
                        {selectedCase.severity}
                      </span>
                    </div>
                    <div className="flex items-center"><span className="font-medium text-gray-700">Status:</span> 
                      <span className={`ml-2 px-2 py-1 rounded-full text-xs border ${getStatusColor(selectedCase.status)}`}>
                        {selectedCase.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-4 bg-white">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <CalendarIcon className="h-5 w-5" />
                    Timeline
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium text-gray-700">Created:</span> <span className="text-gray-900">{new Date(selectedCase.created_at).toLocaleString()}</span></div>
                    {selectedCase.resolved_at && (
                      <div><span className="font-medium text-gray-700">Resolved:</span> <span className="text-gray-900">{new Date(selectedCase.resolved_at).toLocaleString()}</span></div>
                    )}
                    {selectedCase.duration && (
                      <div><span className="font-medium text-gray-700">Duration:</span> <span className="text-gray-900">{selectedCase.duration} minutes</span></div>
                    )}
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg p-4 bg-white">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <TagIcon className="h-5 w-5" />
                    Additional Info
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium text-gray-700">DM Sent:</span> <span className="text-gray-900">{selectedCase.dm_sent ? '✅ Yes' : '❌ No'}</span></div>
                    <div><span className="font-medium text-gray-700">Resolvable:</span> <span className="text-gray-900">{selectedCase.resolvable}</span></div>
                    {selectedCase.tags && selectedCase.tags.length > 0 && (
                      <div>
                        <span className="font-medium text-gray-700">Tags:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {selectedCase.tags.map((tag, index) => (
                            <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Reason and Comments */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border border-gray-200 rounded-lg p-4 bg-white">
                <h3 className="font-semibold text-gray-800 mb-3">Reason</h3>
                <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg border">
                  {selectedCase.reason || 'No reason provided'}
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4 bg-white">
                <h3 className="font-semibold text-gray-800 mb-3">Internal Comment</h3>
                <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg border">
                  {selectedCase.internal_comment || 'No internal comment'}
                </p>
              </div>
            </div>

            {/* Flagged Message */}
            {selectedCase.flagged_message && (
              <div className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />
                  Flagged Message
                </h3>
                <p className="text-sm text-gray-700 bg-white p-3 rounded-lg border">
                  {selectedCase.flagged_message}
                </p>
              </div>
            )}

            {/* Message History */}
            {selectedCase.message_history && selectedCase.message_history.length > 0 && (
              <div className="border border-gray-200 rounded-lg p-4 bg-white">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <ChatBubbleLeftIcon className="h-5 w-5" />
                  Message History ({selectedCase.message_history.length} messages)
                </h3>
                <div className="space-y-3 max-h-60 overflow-y-auto">
                  {selectedCase.message_history.map((msg, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded-lg border">
                      <div className="flex justify-between items-start mb-2">
                        <div className="text-xs text-gray-500">
                          {new Date(msg.timestamp).toLocaleString()}
                        </div>
                        {msg.deleted && (
                          <span className="text-xs text-red-600 bg-red-100 px-2 py-1 rounded-full">
                            Deleted
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-700">{msg.content}</p>
                      {msg.channel_name && (
                        <div className="text-xs text-gray-400 mt-1">
                          #{msg.channel_name}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Attachments */}
            {selectedCase.attachments && selectedCase.attachments.length > 0 && (
              <div className="border border-gray-200 rounded-lg p-4 bg-white">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <DocumentIcon className="h-5 w-5" />
                  Attachments ({selectedCase.attachments.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedCase.attachments.map((attachment, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border">
                      <DocumentIcon className="h-8 w-8 text-gray-400" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {attachment.filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          {attachment.size ? `${(attachment.size / 1024).toFixed(1)} KB` : 'Unknown size'}
                        </p>
                      </div>
                      {attachment.saved_path && (
                        <button className="text-blue-600 hover:text-blue-800 text-xs">
                          View
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Resolution Info */}
            {selectedCase.status !== 'Open' && (
              <div className="border border-green-200 rounded-lg p-4 bg-green-50">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                  Resolution Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Resolved by:</span> <span className="text-gray-900">{selectedCase.resolved_by_name || 'System'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Method:</span> <span className="text-gray-900">{selectedCase.resolution_method}</span>
                  </div>
                  {selectedCase.resolution_comment && (
                    <div className="md:col-span-2">
                      <span className="font-medium text-gray-700">Comment:</span>
                      <p className="mt-1 text-gray-600">{selectedCase.resolution_comment}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseViewModal;