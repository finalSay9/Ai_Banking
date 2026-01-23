import React, { useState, useEffect } from 'react';
import { FileText, Plus, Filter, Eye, User } from 'lucide-react';
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
  getStatusColor,
  getSeverityColor,
} from '../utils/helpers';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

export const Cases = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
  });

  useEffect(() => {
    fetchCases();
  }, [filters]);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const data = await fraudService.getFraudCases(filters);
      setCases(data.results || data);
    } catch (error) {
      toast.error('Failed to load fraud cases');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      key: 'case_number',
      label: 'Case Number',
      render: (value) => (
        <span className="font-mono text-sm font-medium text-gray-900">
          {value}
        </span>
      ),
    },
    {
      key: 'title',
      label: 'Title',
      render: (value) => (
        <span className="text-sm text-gray-900 font-medium">{value}</span>
      ),
    },
    {
      key: 'transaction_reference',
      label: 'Transaction',
      render: (value) => (
        <span className="text-sm text-gray-700 font-mono">{value}</span>
      ),
    },
    {
      key: 'severity',
      label: 'Severity',
      render: (value) => (
        <Badge className={getSeverityColor(value)}>{value}</Badge>
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
      key: 'assigned_to_email',
      label: 'Assigned To',
      render: (value) => (
        <span className="text-sm text-gray-600">{value || 'Unassigned'}</span>
      ),
    },
    {
      key: 'estimated_loss',
      label: 'Est. Loss',
      render: (value) => (
        <span className="text-sm font-semibold text-danger-600">
          {value ? formatCurrency(value) : '-'}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
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
          onClick={() => navigate(`/cases/${row.id}`)}
        >
          View
        </Button>
      ),
    },
  ];

  const statusCounts = {
    total: cases.length,
    pending: cases.filter((c) => c.status === 'PENDING').length,
    investigating: cases.filter((c) => c.status === 'INVESTIGATING').length,
    resolved: cases.filter((c) => c.status === 'RESOLVED').length,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Fraud Cases</h1>
          <p className="text-gray-600 mt-1">
            Manage and investigate fraud cases
          </p>
        </div>
        <Button icon={Plus} onClick={() => setShowNewModal(true)}>
          New Case
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Cases</p>
              <p className="text-2xl font-bold text-gray-900">
                {statusCounts.total}
              </p>
            </div>
            <FileText className="w-8 h-8 text-primary-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-warning-600">
                {statusCounts.pending}
              </p>
            </div>
            <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
              <span className="text-warning-600 font-bold">⏳</span>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Investigating</p>
              <p className="text-2xl font-bold text-primary-600">
                {statusCounts.investigating}
              </p>
            </div>
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <span className="text-primary-600 font-bold">🔍</span>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Resolved</p>
              <p className="text-2xl font-bold text-success-600">
                {statusCounts.resolved}
              </p>
            </div>
            <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
              <span className="text-success-600 font-bold">✓</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <Select
            options={[
              { value: '', label: 'All Status' },
              { value: 'PENDING', label: 'Pending' },
              { value: 'INVESTIGATING', label: 'Investigating' },
              { value: 'CONFIRMED', label: 'Confirmed' },
              { value: 'FALSE_POSITIVE', label: 'False Positive' },
              { value: 'RESOLVED', label: 'Resolved' },
            ]}
            value={filters.status}
            onChange={(e) =>
              setFilters({ ...filters, status: e.target.value })
            }
            className="w-64"
          />
          <Select
            options={[
              { value: '', label: 'All Severity' },
              { value: 'LOW', label: 'Low' },
              { value: 'MEDIUM', label: 'Medium' },
              { value: 'HIGH', label: 'High' },
              { value: 'CRITICAL', label: 'Critical' },
            ]}
            value={filters.severity}
            onChange={(e) =>
              setFilters({ ...filters, severity: e.target.value })
            }
            className="w-64"
          />
        </div>
      </Card>

      {/* Cases Table */}
      <Table
        columns={columns}
        data={cases}
        loading={loading}
        onRowClick={(row) => navigate(`/cases/${row.id}`)}
      />

      {/* New Case Modal */}
      <NewCaseModal
        isOpen={showNewModal}
        onClose={() => setShowNewModal(false)}
        onSuccess={() => {
          fetchCases();
          setShowNewModal(false);
        }}
      />
    </div>
  );
};

// New Case Modal Component
const NewCaseModal = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    transaction: '',
    title: '',
    description: '',
    severity: 'MEDIUM',
    estimated_loss: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await fraudService.createFraudCase(formData);
      toast.success('Fraud case created successfully');
      onSuccess();
    } catch (error) {
      toast.error('Failed to create fraud case');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Fraud Case">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Transaction ID"
          type="number"
          required
          value={formData.transaction}
          onChange={(e) =>
            setFormData({ ...formData, transaction: e.target.value })
          }
        />

        <Input
          label="Case Title"
          required
          value={formData.title}
          onChange={(e) =>
            setFormData({ ...formData, title: e.target.value })
          }
          placeholder="Brief description of the fraud case"
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            required
            rows={4}
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Detailed description of the suspected fraud..."
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="Severity"
            options={[
              { value: 'LOW', label: 'Low' },
              { value: 'MEDIUM', label: 'Medium' },
              { value: 'HIGH', label: 'High' },
              { value: 'CRITICAL', label: 'Critical' },
            ]}
            value={formData.severity}
            onChange={(e) =>
              setFormData({ ...formData, severity: e.target.value })
            }
          />

          <Input
            label="Estimated Loss"
            type="number"
            step="0.01"
            value={formData.estimated_loss}
            onChange={(e) =>
              setFormData({ ...formData, estimated_loss: e.target.value })
            }
            placeholder="0.00"
          />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={loading}>
            Create Case
          </Button>
        </div>
      </form>
    </Modal>
  );
};
