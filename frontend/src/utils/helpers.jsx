import { format, formatDistance } from 'date-fns';

export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

export const formatDate = (date, formatStr = 'MMM dd, yyyy') => {
  if (!date) return '-';
  return format(new Date(date), formatStr);
};

export const formatDateTime = (date) => {
  if (!date) return '-';
  return format(new Date(date), 'MMM dd, yyyy HH:mm');
};

export const formatRelativeTime = (date) => {
  if (!date) return '-';
  return formatDistance(new Date(date), new Date(), { addSuffix: true });
};

export const getRiskLevelColor = (riskLevel) => {
  const colors = {
    LOW: 'text-success-700 bg-success-100',
    MEDIUM: 'text-warning-700 bg-warning-100',
    HIGH: 'text-danger-700 bg-danger-100',
    CRITICAL: 'text-danger-900 bg-danger-200',
  };
  return colors[riskLevel] || colors.LOW;
};

export const getStatusColor = (status) => {
  const colors = {
    PENDING: 'text-warning-700 bg-warning-100',
    APPROVED: 'text-success-700 bg-success-100',
    REJECTED: 'text-danger-700 bg-danger-100',
    FLAGGED: 'text-warning-700 bg-warning-100',
    INVESTIGATING: 'text-primary-700 bg-primary-100',
    CONFIRMED: 'text-danger-700 bg-danger-100',
    FALSE_POSITIVE: 'text-gray-700 bg-gray-100',
    RESOLVED: 'text-success-700 bg-success-100',
  };
  return colors[status] || colors.PENDING;
};

export const getSeverityColor = (severity) => {
  const colors = {
    LOW: 'text-success-700 bg-success-100',
    MEDIUM: 'text-warning-700 bg-warning-100',
    HIGH: 'text-danger-700 bg-danger-100',
    CRITICAL: 'text-danger-900 bg-danger-200',
  };
  return colors[severity] || colors.LOW;
};

export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const calculatePercentageChange = (current, previous) => {
  if (!previous) return 0;
  return ((current - previous) / previous) * 100;
};
