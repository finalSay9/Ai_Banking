import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  Clock,
  MessageSquare,
  FileText,
} from 'lucide-react';
import { Card, CardHeader } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Input, Select } from '../components/common/Input';
import { fraudService } from '../services/fraudService';
import {
  formatCurrency,
  formatDateTime,
  getStatusColor,
  getSeverityColor,
} from '../utils/helpers';
import toast from 'react-hot-toast';

export const CaseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseDetail, setCaseDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [addingNote, setAddingNote] = useState(false);

  useEffect(() => {
    fetchCaseDetail();
  }, [id]);

  const fetchCaseDetail = async () => {
    try {
      setLoading(true);
      const data = await fraudService.getFraudCaseDetail(id);
      setCaseDetail(data);
    } catch (error) {
      toast.error('Failed to load case details');
    } finally {
      setLoading(false);
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    try {
      setAddingNote(true);
      await fraudService.addCaseNote(id, newNote);
      toast.success('Note added successfully');
      setNewNote('');
      fetchCaseDetail();
    } catch (error) {
      toast.error('Failed to add note');
    } finally {
      setAddingNote(false);
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    try {
      await fraudService.updateCaseStatus(id, newStatus);
      toast.success('Case status updated');
      fetchCaseDetail();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (!caseDetail) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Case not found</p>
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
            onClick={() => navigate('/cases')}
          >
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {caseDetail.title}
            </h1>
            <p className="text-gray-600 mt-1 font-mono">
              {caseDetail.case_number}
            </p>
          </div>
        </div>
        <div className="flex gap-3">
          <Badge className={getSeverityColor(caseDetail.severity)} size="lg">
            {caseDetail.severity}
          </Badge>
          <Badge className={getStatusColor(caseDetail.status)} size="lg">
            {caseDetail.status}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Case Information */}
          <Card>
            <CardHeader title="Case Information" icon={FileText} />
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-600">
                  Description
                </label>
                <p className="text-gray-900 mt-1">{caseDetail.description}</p>
              </div>

              {caseDetail.investigation_notes && (
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Investigation Notes
                  </label>
                  <p className="text-gray-900 mt-1 whitespace-pre-line">
                    {caseDetail.investigation_notes}
                  </p>
                </div>
              )}

              {caseDetail.resolution_notes && (
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Resolution Notes
                  </label>
                  <p className="text-gray-900 mt-1 whitespace-pre-line">
                    {caseDetail.resolution_notes}
                  </p>
                </div>
              )}
            </div>
          </Card>

          {/* Transaction Details */}
          {caseDetail.transaction_details && (
            <Card>
              <CardHeader title="Associated Transaction" />
              <div className="space-y-3">
                <DetailRow
                  label="Reference"
                  value={caseDetail.transaction_details.reference}
                />
                <DetailRow
                  label="Amount"
                  value={formatCurrency(
                    caseDetail.transaction_details.amount,
                    caseDetail.transaction_details.currency
                  )}
                />
                <DetailRow
                  label="User ID"
                  value={caseDetail.transaction_details.user_id}
                />
                <DetailRow
                  label="Fraud Score"
                  value={`${(
                    caseDetail.transaction_details.fraud_score * 100
                  ).toFixed(1)}%`}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    navigate(`/transactions/${caseDetail.transaction}`)
                  }
                >
                  View Transaction
                </Button>
              </div>
            </Card>
          )}

          {/* Notes Section */}
          <Card>
            <CardHeader title="Investigation Notes" icon={MessageSquare} />

            {/* Add Note Form */}
            <form onSubmit={handleAddNote} className="mb-6">
              <textarea
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Add investigation note..."
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 mb-2"
              />
              <Button type="submit" loading={addingNote} size="sm">
                Add Note
              </Button>
            </form>

            {/* Notes List */}
            <div className="space-y-3">
              {caseDetail.notes && caseDetail.notes.length > 0 ? (
                caseDetail.notes.map((note) => (
                  <div
                    key={note.id}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                          {note.author_name?.[0] || 'U'}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {note.author_name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatDateTime(note.created_at)}
                          </p>
                        </div>
                      </div>
                      {note.is_internal && (
                        <Badge variant="info" size="sm">
                          Internal
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 whitespace-pre-line">
                      {note.note}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-center text-gray-500 py-4">
                  No notes added yet
                </p>
              )}
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Actions */}
          <Card>
            <CardHeader title="Case Actions" />
            <div className="space-y-3">
              <Select
                label="Update Status"
                options={[
                  { value: 'PENDING', label: 'Pending' },
                  { value: 'INVESTIGATING', label: 'Investigating' },
                  { value: 'CONFIRMED', label: 'Confirmed Fraud' },
                  { value: 'FALSE_POSITIVE', label: 'False Positive' },
                  { value: 'RESOLVED', label: 'Resolved' },
                ]}
                value={caseDetail.status}
                onChange={(e) => handleUpdateStatus(e.target.value)}
              />
            </div>
          </Card>

          {/* Case Details */}
          <Card>
            <CardHeader title="Details" icon={Clock} />
            <div className="space-y-3">
              <DetailRow
                label="Created"
                value={formatDateTime(caseDetail.created_at)}
              />
              <DetailRow
                label="Updated"
                value={formatDateTime(caseDetail.updated_at)}
              />
              {caseDetail.resolved_at && (
                <DetailRow
                  label="Resolved"
                  value={formatDateTime(caseDetail.resolved_at)}
                />
              )}
              <DetailRow
                label="Assigned To"
                value={
                  caseDetail.assigned_to_details?.email || 'Unassigned'
                }
              />
            </div>
          </Card>

          {/* Financial Impact */}
          <Card>
            <CardHeader title="Financial Impact" />
            <div className="space-y-3">
              <DetailRow
                label="Estimated Loss"
                value={
                  caseDetail.estimated_loss
                    ? formatCurrency(caseDetail.estimated_loss)
                    : '-'
                }
              />
              <DetailRow
                label="Actual Loss"
                value={
                  caseDetail.actual_loss
                    ? formatCurrency(caseDetail.actual_loss)
                    : '-'
                }
              />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

const DetailRow = ({ label, value }) => (
  <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
    <span className="text-sm text-gray-600">{label}</span>
    <span className="text-sm font-medium text-gray-900">{value || 'N/A'}</span>
  </div>
);
