import React, { useState, useEffect } from 'react';
import { CreditCard, Filter, Plus, Download, Eye } from 'lucide-react';
import { Card, CardHeader } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Table } from '../components/common/Table';
import { Modal } from '../components/common/Modal';
import { Input, Select } from '../components/common/Input';
import { fraudService } from '../services/fraudService';
import {
  formatCurrency,
  formatDateTime,
  getRiskLevelColor,
  getStatusColor,
} from '../utils/helpers';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

export const Transactions = () => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    risk_level: '',
    search: '',
  });

  useEffect(() => {
    fetchTransactions();
  }, [filters]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const data = await fraudService.getTransactions(filters);
      setTransactions(data.results || data);
    } catch (error) {
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      key: 'reference',
      label: 'Reference',
      render: (value) => (
        <span className="font-mono text-sm font-medium text-gray-900">
          {value}
        </span>
      ),
    },
    {
      key: 'user_id',
      label: 'User ID',
      render: (value) => (
        <span className="text-sm text-gray-700">{value}</span>
      ),
    },
    {
      key: 'amount',
      label: 'Amount',
      render: (value, row) => (
        <span className="font-semibold text-gray-900">
          {formatCurrency(value, row.currency)}
        </span>
      ),
    },
    {
      key: 'fraud_score',
      label: 'Fraud Score',
      render: (value) => (
        <div className="flex items-center gap-2">
          <div className="w-16 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                value >= 0.7
                  ? 'bg-danger-600'
                  : value >= 0.5
                  ? 'bg-warning-500'
                  : 'bg-success-500'
              }`}
              style={{ width: `${(value || 0) * 100}%` }}
            />
          </div>
          <span className="text-sm font-medium text-gray-700">
            {((value || 0) * 100).toFixed(1)}%
          </span>
        </div>
      ),
    },
    {
      key: 'risk_level',
      label: 'Risk',
      render: (value) => (
        <Badge className={getRiskLevelColor(value)}>{value}</Badge>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => (
        <Badge className={getStatusColor(value)}>{value}</Badge>
      ),
    },
    {
      key: 'transaction_date',
      label: 'Date',
      render: (value) => (
        <span className="text-sm text-gray-600">{formatDateTime(value)}</span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <Button
          variant="outline"
          size="sm"
          icon={Eye}
          onClick={() => navigate(`/transactions/${row.id}`)}
        >
          View
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
          <p className="text-gray-600 mt-1">
            Monitor and analyze all financial transactions
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" icon={Download}>
            Export
          </Button>
          <Button icon={Plus} onClick={() => setShowNewModal(true)}>
            New Transaction
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <Input
            placeholder="Search by reference or user ID..."
            value={filters.search}
            onChange={(e) =>
              setFilters({ ...filters, search: e.target.value })
            }
            className="flex-1"
          />
          <Select
            options={[
              { value: '', label: 'All Status' },
              { value: 'PENDING', label: 'Pending' },
              { value: 'APPROVED', label: 'Approved' },
              { value: 'REJECTED', label: 'Rejected' },
              { value: 'FLAGGED', label: 'Flagged' },
            ]}
            value={filters.status}
            onChange={(e) =>
              setFilters({ ...filters, status: e.target.value })
            }
            className="w-48"
          />
          <Select
            options={[
              { value: '', label: 'All Risk Levels' },
              { value: 'LOW', label: 'Low' },
              { value: 'MEDIUM', label: 'Medium' },
              { value: 'HIGH', label: 'High' },
              { value: 'CRITICAL', label: 'Critical' },
            ]}
            value={filters.risk_level}
            onChange={(e) =>
              setFilters({ ...filters, risk_level: e.target.value })
            }
            className="w-48"
          />
        </div>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">
                {transactions.length}
              </p>
            </div>
            <CreditCard className="w-8 h-8 text-primary-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Flagged</p>
              <p className="text-2xl font-bold text-warning-600">
                {
                  transactions.filter((t) => t.status === 'FLAGGED').length
                }
              </p>
            </div>
            <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
              <span className="text-warning-600 font-bold">!</span>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High Risk</p>
              <p className="text-2xl font-bold text-danger-600">
                {
                  transactions.filter(
                    (t) => t.risk_level === 'HIGH' || t.risk_level === 'CRITICAL'
                  ).length
                }
              </p>
            </div>
            <div className="w-8 h-8 bg-danger-100 rounded-lg flex items-center justify-center">
              <span className="text-danger-600 font-bold">⚠</span>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-success-600">
                {
                  transactions.filter((t) => t.status === 'APPROVED')
                    .length
                }
              </p>
            </div>
            <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
              <span className="text-success-600 font-bold">✓</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Transactions Table */}
      <Table
        columns={columns}
        data={transactions}
        loading={loading}
        onRowClick={(row) => navigate(`/transactions/${row.id}`)}
      />

      {/* New Transaction Modal */}
      <NewTransactionModal
        isOpen={showNewModal}
        onClose={() => setShowNewModal(false)}
        onSuccess={() => {
          fetchTransactions();
          setShowNewModal(false);
        }}
      />
    </div>
  );
};

// New Transaction Modal Component
const NewTransactionModal = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    user_id: '',
    amount: '',
    currency: 'USD',
    transaction_type: 'payment',
    merchant_name: '',
    merchant_category: '',
    country: '',
    city: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await fraudService.submitTransaction(formData);
      toast.success('Transaction submitted successfully');
      onSuccess();
    } catch (error) {
      toast.error('Failed to submit transaction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Submit New Transaction">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="User ID"
            required
            value={formData.user_id}
            onChange={(e) =>
              setFormData({ ...formData, user_id: e.target.value })
            }
          />
          <Input
            label="Amount"
            type="number"
            step="0.01"
            required
            value={formData.amount}
            onChange={(e) =>
              setFormData({ ...formData, amount: e.target.value })
            }
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="Currency"
            options={[
              { value: 'USD', label: 'USD' },
              { value: 'EUR', label: 'EUR' },
              { value: 'GBP', label: 'GBP' },
            ]}
            value={formData.currency}
            onChange={(e) =>
              setFormData({ ...formData, currency: e.target.value })
            }
          />
          <Select
            label="Transaction Type"
            options={[
              { value: 'payment', label: 'Payment' },
              { value: 'transfer', label: 'Transfer' },
              { value: 'withdrawal', label: 'Withdrawal' },
            ]}
            value={formData.transaction_type}
            onChange={(e) =>
              setFormData({ ...formData, transaction_type: e.target.value })
            }
          />
        </div>

        <Input
          label="Merchant Name"
          value={formData.merchant_name}
          onChange={(e) =>
            setFormData({ ...formData, merchant_name: e.target.value })
          }
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Country"
            value={formData.country}
            onChange={(e) =>
              setFormData({ ...formData, country: e.target.value })
            }
          />
          <Input
            label="City"
            value={formData.city}
            onChange={(e) =>
              setFormData({ ...formData, city: e.target.value })
            }
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={loading}>
            Submit Transaction
          </Button>
        </div>
      </form>
    </Modal>
  );
};
