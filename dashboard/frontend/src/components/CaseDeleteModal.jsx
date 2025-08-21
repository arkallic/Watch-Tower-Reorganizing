// dashboard/frontend/src/components/CaseDeleteModal.jsx
import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const CaseDeleteModal = ({ 
  selectedCase, 
  isOpen, 
  onClose, 
  onDelete, 
  submitting 
}) => {
  if (!isOpen || !selectedCase) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="bg-red-100 rounded-full p-3">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Delete Case</h3>
              <p className="text-sm text-gray-600">This action cannot be undone</p>
            </div>
          </div>

          <div className="mb-6">
            <p className="text-gray-700">
              Are you sure you want to delete <strong>Case #{selectedCase.case_number}</strong> for user <strong>{selectedCase.username}</strong>?
            </p>
            <p className="text-sm text-gray-500 mt-2">
              This will permanently remove the case and all associated data.
            </p>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={onDelete}
              disabled={submitting}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {submitting ? 'Deleting...' : 'Delete Case'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseDeleteModal;