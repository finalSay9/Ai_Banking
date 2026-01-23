import React from 'react';
import clsx from 'clsx';

export const Input = ({
  label,
  error,
  icon: Icon,
  className,
  ...props
}) => {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="h-5 w-5 text-gray-400" />
          </div>
        )}
        <input
          className={clsx(
            'w-full px-4 py-2 border rounded-lg transition-all',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            Icon && 'pl-10',
            error
              ? 'border-danger-500 focus:ring-danger-500'
              : 'border-gray-300'
          )}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1 text-sm text-danger-600">{error}</p>
      )}
    </div>
  );
};

export const Select = ({ label, error, options, className, ...props }) => {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <select
        className={clsx(
          'w-full px-4 py-2 border rounded-lg transition-all',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          error ? 'border-danger-500' : 'border-gray-300'
        )}
        {...props}
      >
        {options?.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-sm text-danger-600">{error}</p>
      )}
    </div>
  );
};
