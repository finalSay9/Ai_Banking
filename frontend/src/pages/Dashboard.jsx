import React, { useState, useEffect } from 'react';
import {
  CreditCard,
  AlertTriangle,
  FileText,
  TrendingUp,
  Activity,
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { Card, CardHeader } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { fraudService } from '../services/fraudService';
import { formatCurrency, formatRelativeTime, getRiskLevelColor } from '../utils/helpers';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import toast from 'react-hot-toast';

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState(null);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, trendsData, alertsData] = await Promise.all([
        fraudService.getDashboardStats(7),
        fraudService.getTrends(30),
        fraudService.getCriticalAlerts(),
      ]);

      setStats(statsData);
      setTrends(trendsData);
      setRecentAlerts(alertsData.results || alertsData);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#22c55e'];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Real-time fraud detection overview and analytics
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Transactions"
          value={stats?.total_transactions?.toLocaleString() || '0'}
          change={5.2}
          changeType="positive"
          icon={CreditCard}
          loading={loading}
        />
        <StatCard
          title="Flagged Transactions"
          value={stats?.flagged_transactions?.toLocaleString() || '0'}
          change={-2.1}
          changeType="negative"
          icon={AlertTriangle}
          loading={loading}
        />
        <StatCard
          title="Active Cases"
          value={stats?.active_cases?.toLocaleString() || '0'}
          change={12.5}
          changeType="positive"
          icon={FileText}
          loading={loading}
        />
        <StatCard
          title="Fraud Rate"
          value={`${stats?.fraud_rate?.toFixed(2) || '0'}%`}
          change={-0.8}
          changeType="negative"
          icon={TrendingUp}
          loading={loading}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fraud Trends Chart */}
        <Card>
          <CardHeader
            title="Fraud Detection Trends"
            subtitle="Last 30 days"
            icon={Activity}
          />
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trends?.trends || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="total_transactions"
                stackId="1"
                stroke="#3b82f6"
                fill="#93c5fd"
                name="Total Transactions"
              />
              <Area
                type="monotone"
                dataKey="flagged_transactions"
                stackId="2"
                stroke="#ef4444"
                fill="#fca5a5"
                name="Flagged"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Risk Distribution */}
        <Card>
          <CardHeader
            title="Risk Level Distribution"
            subtitle="Current status"
          />
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Low', value: 45 },
                  { name: 'Medium', value: 30 },
                  { name: 'High', value: 20 },
                  { name: 'Critical', value: 5 },
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {COLORS.map((color, index) => (
                  <Cell key={`cell-${index}`} fill={color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Alerts */}
      <Card>
        <CardHeader
          title="Critical Alerts"
          subtitle="Requires immediate attention"
          icon={AlertTriangle}
        />
        <div className="space-y-3">
          {recentAlerts.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No critical alerts at the moment
            </p>
          ) : (
            recentAlerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-danger-100 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-danger-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{alert.message}</p>
                    <p className="text-sm text-gray-600">
                      {formatRelativeTime(alert.created_at)}
                    </p>
                  </div>
                </div>
                <Badge variant="danger">{alert.severity}</Badge>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
};
