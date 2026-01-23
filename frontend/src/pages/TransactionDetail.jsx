import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MapPin,
  CreditCard,
  Calendar,
  TrendingUp,
} from 'lucide-react';
import { Card, CardHeader } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { fraudService } from '../services/fraudService';
import {
  formatCurrency,
  formatDateTime,
  getRiskLevelColor,
  getStatusColor,
} from '../utils/helpers';
import toast from 'react-hot-toast';

export const TransactionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactionDetail();
  }, [id]);

  const fetchTransactionDetail = async () => {
    try {
      setLoading(true);
      const data = await fraudService.getTransactionDetail(id);
      setTransaction(data);
    } catch (error) {
      toast.error('Failed to load transaction details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (!transaction) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Transaction not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="secondary"
            icon={ArrowLeft}
            onClick={() => navigate('/transactions')}
          >
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Transaction Details
            </h1>
            <p className="text-gray-600 mt-1 font-mono">{transaction.reference}</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Badge className={getRiskLevelColor(transaction.risk_level)} size="lg">
            {transaction.risk_level} Risk
          </Badge>
          <Badge className={getStatusColor(transaction.status)} size="lg">
            {transaction.status}
          </Badge>
        </div>
      </div>

      {/* Fraud Score Card */}
      <Card>
        <div className="text-center py-8">
          <div className="relative inline-flex items-center justify-center">
            <svg className="w-32 h-32">
              <circle
                className="text-gray-200"
                strokeWidth="8"
                stroke="currentColor"
                fill="transparent"
                r="56"
                cx="64"
                cy="64"
              />
              <circle
                className={
                  transaction.fraud_score >= 0.7
                    ? 'text-danger-600'
                    : transaction.fraud_score >= 0.5
                    ? 'text-warning-500'
                    : 'text-success-500'
                }
                strokeWidth="8"
                strokeDasharray={`${transaction.fraud_score * 352} 352`}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="56"
                cx="64"
                cy="64"
                transform="rotate(-90 64 64)"
              />
            </svg>
            <div className="absolute">
              <p className="text-4xl font-bold text-gray-900">
                {(transaction.fraud_score * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Fraud Score</p>
            </div>
          </div>
          <p className="text-gray-600 mt-4">
            This transaction has been analyzed and scored for fraud risk
          </p>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transaction Information */}
        <Card>
          <CardHeader title="Transaction Information" icon={CreditCard} />
          <div className="space-y-4">
            <DetailRow
              label="Amount"
              value={formatCurrency(transaction.amount, transaction.currency)}
              highlight
            />
            <DetailRow label="User ID" value={transaction.user_id} />
            <DetailRow label="Account Number" value={transaction.account_number} />
            <DetailRow label="Transaction Type" value={transaction.transaction_type} />
            <DetailRow
              label="Date"
              value={formatDateTime(transaction.transaction_date)}
            />
            <DetailRow
              label="Processed At"
              value={formatDateTime(transaction.processed_at)}
            />
          </div>
        </Card>

        {/* Merchant Information */}
        <Card>
          <CardHeader title="Merchant Information" icon={MapPin} />
          <div className="space-y-4">
            <DetailRow label="Merchant Name" value={transaction.merchant_name || 'N/A'} />
            <DetailRow label="Merchant ID" value={transaction.merchant_id || 'N/A'} />
            <DetailRow
              label="Category"
              value={transaction.merchant_category || 'N/A'}
            />
            <DetailRow label="Country" value={transaction.country || 'N/A'} />
            <DetailRow label="City" value={transaction.city || 'N/A'} />
            <DetailRow label="IP Address" value={transaction.ip_address || 'N/A'} />
          </div>
        </Card>
      </div>

      {/* Alerts */}
      {transaction.alerts && transaction.alerts.length > 0 && (
        <Card>
          <CardHeader title="Associated Alerts" icon={AlertTriangle} />
          <div className="space-y-3">
            {transaction.alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg"
              >
                <div className="p-2 bg-danger-100 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-danger-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium text-gray-900">{alert.alert_type}</p>
                    <Badge variant="danger">{alert.severity}</Badge>
                  </div>
                  <p className="text-sm text-gray-600">{alert.message}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {formatDateTime(alert.created_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Fraud Cases */}
      {transaction.fraud_cases && transaction.fraud_cases.length > 0 && (
        <Card>
          <CardHeader title="Related Fraud Cases" />
          <div className="space-y-3">
            {transaction.fraud_cases.map((fraudCase) => (
              <div
                key={fraudCase.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => navigate(`/cases/${fraudCase.id}`)}
              >
                <div>
                  <p className="font-medium text-gray-900">{fraudCase.case_number}</p>
                  <p className="text-sm text-gray-600">{fraudCase.title}</p>
                </div>
                <Badge className={getStatusColor(fraudCase.status)}>
                  {fraudCase.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

const DetailRow = ({ label, value, highlight = false }) => (
  <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
    <span className="text-sm text-gray-600">{label}</span>
    <span
      className={`text-sm font-medium ${
        highlight ? 'text-primary-600 text-lg' : 'text-gray-900'
      }`}
    >
      {value || 'N/A'}
    </span>
  </div>
);
