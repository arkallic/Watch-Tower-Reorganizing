import React from 'react';

export default function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`animate-spin rounded-full border-2 border-gray-600 border-t-accent-500 ${sizeClasses[size]}`}></div>
      {text && (
        <p className="mt-3 text-sm text-gray-400">{text}</p>
      )}
    </div>
  );
}