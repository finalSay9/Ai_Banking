import api from './api';
import { API_ENDPOINTS } from '../config/api';

export const fraudService = {
  // Transactions
  getTransactions: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.TRANSACTIONS, { params });
    return response.data;
  },

  getTransactionDetail: async (id) => {
    const response = await api.get(API_ENDPOINTS.TRANSACTION_DETAIL(id));
    return response.data;
  },

  submitTransaction: async (data) => {
    const response = await api.post(API_ENDPOINTS.TRANSACTION_SUBMIT, data);
    return response.data;
  },

  getFlaggedTransactions: async () => {
    const response = await api.get(API_ENDPOINTS.TRANSACTIONS_FLAGGED);
    return response.data;
  },

  getHighRiskTransactions: async () => {
    const response = await api.get(API_ENDPOINTS.TRANSACTIONS_HIGH_RISK);
    return response.data;
  },

  // Fraud Cases
  getFraudCases: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.FRAUD_CASES, { params });
    return response.data;
  },

  getFraudCaseDetail: async (id) => {
    const response = await api.get(API_ENDPOINTS.FRAUD_CASE_DETAIL(id));
    return response.data;
  },

  createFraudCase: async (data) => {
    const response = await api.post(API_ENDPOINTS.FRAUD_CASES, data);
    return response.data;
  },

  assignCase: async (id, userId) => {
    const response = await api.post(API_ENDPOINTS.CASE_ASSIGN(id), { user_id: userId });
    return response.data;
  },

  updateCaseStatus: async (id, status, notes = '') => {
    const response = await api.post(API_ENDPOINTS.CASE_UPDATE_STATUS(id), {
      status,
      resolution_notes: notes
    });
    return response.data;
  },

  addCaseNote: async (id, note, isInternal = true) => {
    const response = await api.post(API_ENDPOINTS.CASE_ADD_NOTE(id), {
      note,
      is_internal: isInternal
    });
    return response.data;
  },

  getMyCases: async () => {
    const response = await api.get(API_ENDPOINTS.MY_CASES);
    return response.data;
  },

  // Alerts
  getAlerts: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.ALERTS, { params });
    return response.data;
  },

  acknowledgeAlert: async (id) => {
    const response = await api.post(API_ENDPOINTS.ALERT_ACKNOWLEDGE(id));
    return response.data;
  },

  getUnacknowledgedAlerts: async () => {
    const response = await api.get(API_ENDPOINTS.ALERTS_UNACKNOWLEDGED);
    return response.data;
  },

  getCriticalAlerts: async () => {
    const response = await api.get(API_ENDPOINTS.ALERTS_CRITICAL);
    return response.data;
  },

  // Statistics
  getDashboardStats: async (days = 7) => {
    const response = await api.get(API_ENDPOINTS.STATISTICS, { params: { days } });
    return response.data;
  },

  getTrends: async (days = 30) => {
    const response = await api.get(API_ENDPOINTS.TRENDS, { params: { days } });
    return response.data;
  }
};
