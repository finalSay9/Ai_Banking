import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import clsx from 'clsx';

export const StatCard = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  loading = false,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          {loading ? (
            <div className="h-8 w-24 bg-gray-200 animate-pulse rounded mt-2" />
          ) : (
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          )}
          {change !== undefined && (
            <div className="flex items-center gap-1 mt-2">
              {changeType === 'positive' ? (
                <TrendingUp className="w-4 h-4 text-success-600" />
              ) : changeType === 'negative' ? (
                <TrendingDown className="w-4 h-4 text-danger-600" />
              ) : null}
              <span
                className={clsx(
                  'text-sm font-medium',
                  changeType === 'positive' && 'text-success-600',
                  changeType === 'negative' && 'text-danger-600',
                  changeType === 'neutral' && 'text-gray-600'
                )}
              >
                {change > 0 ? '+' : ''}
                {change}%
              </span>
              <span className="text-sm text-gray-500">vs last period</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className="p-3 bg-primary-50 rounded-xl">
            <Icon className="w-6 h-6 text-primary-600" />
          </div>
        )}
      </div>
    </div>
  );
};
