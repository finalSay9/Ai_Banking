import React, { useState, useEffect } from 'react';
import { AlertTriangle, Bell, CheckCircle, Filter } from 'lucide-react';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Select } from '../components/common/Input';
import { fraudService } from '../services/fraudService';
import { formatRelativeTime, getSeverityColor } from '../utils/helpers';
import toast from 'react-hot-toast';

export const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAlerts();
  }, [filter]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      let data;
      if (filter === 'unacknowledged') {
        data = await fraudService.getUnacknowledgedAlerts();
      } else if (filter === 'critical') {
        data = await fraudService.getCriticalAlerts();
      } else {
        data = await fraudService.getAlerts();
      }
      setAlerts(data.results || data);
    } catch (error) {
      toast.error('Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await fraudService.acknowledgeAlert(alertId);
      toast.success('Alert acknowledged');
      fetchAlerts();
    } catch (error) {
      toast.error('Failed to acknowledge alert');
    }
  };

  const unacknowledgedCount = alerts.filter((a) => !a.is_acknowledged).length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-1">
            Real-time fraud detection alerts and notifications
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 bg-danger-50 rounded-lg">
            <p className="text-sm text-gray-600">Unacknowledged</p>
            <p className="text-2xl font-bold text-danger-600">
              {unacknowledgedCount}
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <Select
            options={[
              { value: 'all', label: 'All Alerts' },
              { value: 'unacknowledged', label: 'Unacknowledged' },
              { value: 'critical', label: 'Critical Only' },
            ]}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-64"
          />
        </div>
      </Card>

      {/* Alerts List */}
      <div className="space-y-4">
        {loading ? (
          <Card>
            <div className="animate-pulse space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-20 bg-gray-200 rounded" />
              ))}
            </div>
          </Card>
        ) : alerts.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No alerts found</p>
            </div>
          </Card>
        ) : (
          alerts.map((alert) => (
            <Card
              key={alert.id}
              className={`${
                !alert.is_acknowledged ? 'border-l-4 border-l-danger-500' : ''
              }`}
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div
                  className={`p-3 rounded-lg ${
                    alert.severity === 'CRITICAL'
                      ? 'bg-danger-100'
                      : alert.severity === 'HIGH'
                      ? 'bg-warning-100'
                      : 'bg-primary-100'
                  }`}
                >
                  <AlertTriangle
                    className={`w-6 h-6 ${
                      alert.severity === 'CRITICAL'
                        ? 'text-danger-600'
                        : alert.severity === 'HIGH'
                        ? 'text-warning-600'
                        : 'text-primary-600'
                    }`}
                  />
                </div>

                {/* Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {alert.alert_type}
                        </h3>
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                        {alert.is_acknowledged && (
                          <Badge variant="success">Acknowledged</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{alert.message}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">
                        {formatRelativeTime(alert.created_at)}
                      </p>
                    </div>
                  </div>

                  {/* Transaction Info */}
                  <div className="flex items-center gap-4 mt-3 p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-xs text-gray-500">Transaction</p>
                      <p className="text-sm font-mono font-medium text-gray-900">
                        {alert.transaction_reference}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  {!alert.is_acknowledged && (
                    <div className="mt-4 flex gap-2">
                      <Button
                        size="sm"
                        icon={CheckCircle}
                        onClick={() => handleAcknowledge(alert.id)}
                      >
                        Acknowledge
                      </Button>
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};
