import React, { useState, useEffect, useCallback } from 'react';
import {
  DocumentTextIcon,
  CloudArrowDownIcon,
  TrashIcon,
  ClockIcon,
  FolderIcon,
  ArrowPathIcon,
  PlusCircleIcon
} from '@heroicons/react/24/outline';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);
  
  const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const apiBase = isDevelopment ? 'http://localhost:8000' : '';

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // FIX: Changed URL from /api/pagedata/reports to the correct backend route
      const response = await fetch(`${apiBase}/api/reports`);
      if (!response.ok) throw new Error('Failed to fetch reports list');
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      // Assuming the backend returns a flat array now
      setReports(data.reports || []);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    setError(null);
    try {
      // FIX: Changed URL to the correct backend route
      const response = await fetch(`${apiBase}/api/reports/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report_type: 'moderation_summary' }),
      });
      if (!response.ok) throw new Error('Failed to generate report');
      const result = await response.json();
      if (result.error) throw new Error(result.error);
      await fetchData(); // Refresh list after generating
    } catch (err) {
      console.error('Failed to generate report:', err);
      setError('Could not generate the report. Please check the bot console.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (filename) => {
    if (window.confirm(`Are you sure you want to delete ${filename}? This action cannot be undone.`)) {
      setError(null);
      try {
        // FIX: Changed URL to the correct backend route
        const response = await fetch(`${apiBase}/api/reports/${filename}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete report');
        await fetchData(); // Refresh list after deleting
      } catch (err) {
        console.error('Failed to delete report:', err);
        setError('Could not delete the report.');
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / 1024 ** i).toFixed(2)} ${['B', 'KB', 'MB', 'GB'][i]}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };
  
  const totalSize = reports.reduce((acc, report) => acc + (report.size || 0), 0);

  return (
    <div className="p-6 space-y-6">
      <div className="card border-t-2 border-yellow-400/50">
        <div className="px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-yellow-400">Reporting & Exports</h1>
            <p className="text-sm text-gray-400 mt-1">Generate and manage historical data exports.</p>
          </div>
          <button onClick={fetchData} className="btn-secondary flex items-center gap-2">
            <ArrowPathIcon className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} /> Refresh List
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="card p-4 space-y-4 h-full">
            <h3 className="text-md font-semibold text-gray-100 flex items-center gap-2">
              <PlusCircleIcon className="w-6 h-6 text-yellow-400"/>
              Generate New Report
            </h3>
            <div>
              <label className="text-xs text-gray-400">Report Type</label>
              <select value={'moderation_summary'} disabled className="select mt-1">
                <option value="moderation_summary">Moderation Summary (CSV)</option>
              </select>
            </div>
            <button onClick={handleGenerateReport} disabled={generating} className="btn-primary w-full flex items-center justify-center gap-2">
              {generating ? <ArrowPathIcon className="w-5 h-5 animate-spin" /> : <CloudArrowDownIcon className="w-5 h-5" />}
              {generating ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 card p-4">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-md font-semibold text-gray-100">Generated Reports</h3>
                <div className="text-sm text-gray-400">
                    {reports.length} files • {formatFileSize(totalSize)}
                </div>
            </div>
            {error && <div className="text-center py-4 text-red-400">{error}</div>}
            <div className="space-y-2 max-h-[60vh] overflow-y-auto">
              {loading ? (
                 <div className="text-center py-10 text-gray-400">Loading reports...</div>
              ) : reports.length === 0 ? (
                <div className="text-center py-10 text-gray-500">
                  <FolderIcon className="h-12 w-12 mx-auto mb-2" />
                  <p>No reports have been generated yet.</p>
                </div>
              ) : (
                reports.map(report => (
                  <div key={report.filename} className="grid grid-cols-1 md:grid-cols-3 items-center gap-2 p-3 bg-gray-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                        <DocumentTextIcon className="h-6 w-6 text-blue-400 flex-shrink-0"/>
                        <div className="flex-1 min-w-0">
                            <p className="font-medium text-white truncate" title={report.filename}>{report.filename}</p>
                            <p className="text-xs text-gray-400">{formatFileSize(report.size)}</p>
                        </div>
                    </div>
                    <div className="text-sm text-gray-500 md:text-center">
                        <ClockIcon className="h-4 w-4 inline-block mr-1"/>
                        {formatDate(report.created_at)}
                    </div>
                    <div className="flex items-center justify-end gap-2">
                      <a href={`${apiBase}/api/reports/download/${report.filename}`} target="_blank" rel="noopener noreferrer" className="btn-secondary flex items-center gap-1.5 px-2 py-1">
                          <CloudArrowDownIcon className="h-4 w-4"/> Download
                      </a>
                      <button onClick={() => handleDelete(report.filename)} className="p-2 text-red-400 hover:bg-red-500/10 rounded-md">
                          <TrashIcon className="h-4 w-4"/>
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;