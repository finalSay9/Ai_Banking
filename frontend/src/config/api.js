const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const ML_API_URL = import.meta.env.VITE_ML_API_URL || 'http://localhost:8001/api/v1';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: `${API_BASE_URL}/auth/login/`,
  REFRESH: `${API_BASE_URL}/auth/refresh/`,
  USERS: `${API_BASE_URL}/auth/users/`,
  ME: `${API_BASE_URL}/auth/users/me/`,
  
  // Transactions
  TRANSACTIONS: `${API_BASE_URL}/fraud/transactions/`,
  TRANSACTION_SUBMIT: `${API_BASE_URL}/fraud/transactions/`,
  TRANSACTION_DETAIL: (id) => `${API_BASE_URL}/fraud/transactions/${id}/`,
  TRANSACTIONS_FLAGGED: `${API_BASE_URL}/fraud/transactions/flagged/`,
  TRANSACTIONS_HIGH_RISK: `${API_BASE_URL}/fraud/transactions/high_risk/`,
  
  // Fraud Cases
  FRAUD_CASES: `${API_BASE_URL}/fraud/cases/`,
  FRAUD_CASE_DETAIL: (id) => `${API_BASE_URL}/fraud/cases/${id}/`,
  CASE_ASSIGN: (id) => `${API_BASE_URL}/fraud/cases/${id}/assign/`,
  CASE_UPDATE_STATUS: (id) => `${API_BASE_URL}/fraud/cases/${id}/update_status/`,
  CASE_ADD_NOTE: (id) => `${API_BASE_URL}/fraud/cases/${id}/add_note/`,
  MY_CASES: `${API_BASE_URL}/fraud/cases/my_cases/`,
  PENDING_CASES: `${API_BASE_URL}/fraud/cases/pending/`,
  
  // Alerts
  ALERTS: `${API_BASE_URL}/fraud/alerts/`,
  ALERT_ACKNOWLEDGE: (id) => `${API_BASE_URL}/fraud/alerts/${id}/acknowledge/`,
  ALERTS_UNACKNOWLEDGED: `${API_BASE_URL}/fraud/alerts/unacknowledged/`,
  ALERTS_CRITICAL: `${API_BASE_URL}/fraud/alerts/critical/`,
  
  // Statistics
  STATISTICS: `${API_BASE_URL}/fraud/statistics/dashboard/`,
  TRENDS: `${API_BASE_URL}/fraud/statistics/trends/`,
  
  // ML Service
  ML_SCORE: `${ML_API_URL}/score`,
  ML_SCORE_DETAILED: `${ML_API_URL}/score/detailed`,
  ML_HEALTH: `${ML_API_URL}/health`,
};

export default API_BASE_URL;
