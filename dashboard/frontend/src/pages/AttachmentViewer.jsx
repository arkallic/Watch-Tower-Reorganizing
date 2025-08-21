import React, { useState, useEffect, useCallback } from 'react';
import { 
  PaperClipIcon,
  DocumentIcon,
  PhotoIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  CheckBadgeIcon,
  XCircleIcon,
  FolderIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

export default function AttachmentViewer() {
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    file_type: '',
    sort_by: 'date',
    sort_order: 'desc'
  });

  const fetchAttachments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      const apiBase = isDevelopment ? 'http://localhost:8000' : '';
      
      const params = new URLSearchParams({
        search: filters.search,
        status: filters.status,
        file_type: filters.file_type,
        sort_by: filters.sort_by,
        sort_order: filters.sort_order,
      });

      const response = await fetch(`${apiBase}/api/pagedata/attachments?${params.toString()}`);
      if (!response.ok) throw new Error("Failed to fetch attachments data.");
      
      const data = await response.json();
      if(data.error) throw new Error(data.error);

      setAttachments(data.attachments || []);
    } catch (error) {
      console.error('Failed to fetch attachments:', error);
      setError(error.message);
      setAttachments([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);
  
  useEffect(() => {
    fetchAttachments();
  }, [fetchAttachments]);

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'image': return PhotoIcon;
      case 'video': return VideoCameraIcon;
      case 'audio': return MusicalNoteIcon;
      case 'archive': return ArchiveBoxIcon;
      case 'document': return DocumentIcon;
      default: return PaperClipIcon;
    }
  };

  const getFileTypeFromExtension = (filename) => {
    if (!filename) return 'other';
    const ext = filename.split('.').pop().toLowerCase();
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
    const videoExts = ['mp4', 'avi', 'mov', 'mkv', 'webm'];
    const audioExts = ['mp3', 'wav', 'ogg', 'flac', 'm4a'];
    const archiveExts = ['zip', 'rar', '7z', 'tar', 'gz'];
    const docExts = ['pdf', 'doc', 'docx', 'txt', 'csv', 'xls', 'xlsx', 'ppt', 'pptx'];
    
    if (imageExts.includes(ext)) return 'image';
    if (videoExts.includes(ext)) return 'video';
    if (audioExts.includes(ext)) return 'audio';
    if (archiveExts.includes(ext)) return 'archive';
    if (docExts.includes(ext)) return 'document';
    return 'other';
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if(!dateString) return "N/A";
    return new Date(dateString).toLocaleString();
  };

  const stats = {
    total: attachments.length,
    preserved: attachments.filter(a => a.preserved).length,
    lost: attachments.filter(a => !a.preserved).length,
    totalSize: attachments.filter(a => a.preserved).reduce((sum, a) => sum + (a.size || 0), 0)
  };
  
  if (loading) {
    return (
      <div className="p-6 h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-yellow-400"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="card border-t-2 border-yellow-400/50">
        <div className="px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-yellow-400">Attachment Viewer</h1>
            <p className="text-sm text-gray-400 mt-1">Browse and manage preserved deleted message attachments.</p>
          </div>
          <button onClick={fetchAttachments} className="btn-secondary flex items-center gap-2">
            <ArrowPathIcon className="w-5 h-5" /> Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <div className="card p-4"><p className="text-sm text-gray-400">Total Logged</p><p className="text-2xl font-bold text-white">{stats.total}</p></div>
          <div className="card p-4"><p className="text-sm text-gray-400">Successfully Preserved</p><p className="text-2xl font-bold text-green-400">{stats.preserved}</p></div>
          <div className="card p-4"><p className="text-sm text-gray-400">Lost / Failed</p><p className="text-2xl font-bold text-red-400">{stats.lost}</p></div>
          <div className="card p-4"><p className="text-sm text-gray-400">Total Size Preserved</p><p className="text-2xl font-bold text-blue-400">{formatFileSize(stats.totalSize)}</p></div>
      </div>

      <div className="card p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input type="text" placeholder="Search filename or user..." value={filters.search} onChange={(e) => setFilters(prev => ({...prev, search: e.target.value}))} className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-yellow-500" />
          </div>
          <select value={filters.status} onChange={(e) => setFilters(prev => ({...prev, status: e.target.value}))} className="select">
            <option value="">All Statuses</option>
            <option value="preserved">Preserved</option>
            <option value="lost">Lost/Failed</option>
          </select>
          <select value={filters.file_type} onChange={(e) => setFilters(prev => ({...prev, file_type: e.target.value}))} className="select">
             <option value="">All File Types</option>
             <option value="image">Images</option>
             <option value="video">Videos</option>
             <option value="audio">Audio</option>
             <option value="document">Documents</option>
             <option value="archive">Archives</option>
             <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {error && <p className="col-span-full text-center text-red-400">{error}</p>}
        {!error && attachments.length > 0 ? attachments.map((attachment) => {
          const FileIcon = getFileIcon(getFileTypeFromExtension(attachment.filename));
          return (
            <div key={attachment.id} className="card flex flex-col group overflow-hidden">
              <div className="p-4 flex items-start justify-between">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 bg-gray-800/50 rounded-lg">
                      <FileIcon className="w-6 h-6 text-yellow-400" />
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-semibold text-white truncate" title={attachment.filename}>{attachment.filename}</h4>
                      <p className="text-sm text-gray-400">{formatFileSize(attachment.size)}</p>
                    </div>
                  </div>
              </div>
              <div className="bg-gray-800/20 border-t border-gray-700/50 p-4 flex-grow flex flex-col justify-between">
                <div className="text-sm space-y-1.5">
                    <p className="flex justify-between"><strong>User:</strong> <span className="text-gray-300 truncate">{attachment.user_name}</span></p>
                    <p className="flex justify-between"><strong>Channel:</strong> <span className="text-gray-300">#{attachment.channel_name}</span></p>
                    <p className="flex justify-between"><strong>Deleted:</strong> <span className="text-gray-300">{formatDate(attachment.deleted_timestamp)}</span></p>
                    <p className="flex justify-between items-center"><strong>Status:</strong> 
                      <span className={`font-medium px-2 py-0.5 rounded-full text-xs ${attachment.preserved ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
                        {attachment.preserved ? 'Preserved' : 'Lost'}
                      </span>
                    </p>
                </div>
                {attachment.preserved && attachment.local_path && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-400 mb-1">Local Path:</p>
                    <p className="text-xs text-gray-300 font-mono bg-gray-900 p-2 rounded break-all">{attachment.local_path}</p>
                  </div>
                )}
                {!attachment.preserved && attachment.error && (
                  <div className="mt-3">
                    <p className="text-xs font-medium text-red-400 mb-1">Error Details:</p>
                    <p className="text-xs text-red-300">{attachment.error}</p>
                  </div>
                )}
              </div>
            </div>
          );
        }) : !error && (
          <div className="col-span-full text-center py-12 card">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-white">No attachments found</h3>
            <p className="mt-1 text-sm text-gray-500">When attachments are preserved from deleted messages, they will appear here.</p>
          </div>
        )}
      </div>
    </div>
  );
}