import React, { useState, useEffect } from 'react';
import transactionService from '../../services/transaction';
import { formatZMK } from '../../utils/currency';
import './Dashboard.css';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [summaryData, recentData] = await Promise.all([
        transactionService.getSummary({
          month: new Date().getMonth() + 1,
          year: new Date().getFullYear()
        }),
        transactionService.getRecentTransactions()
      ]);
      
      setSummary(summaryData);
      setRecentTransactions(recentData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return formatZMK(value);
  };

  if (loading) {
    return <div className="loading-state">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1 className="page-title">Dashboard</h1>
      
      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <h3>Total Income</h3>
          <p className="summary-amount income">
            {formatCurrency(summary?.summary?.total_income || 0)}
          </p>
        </div>
        
        <div className="summary-card">
          <h3>Total Expenses</h3>
          <p className="summary-amount expense">
            {formatCurrency(summary?.summary?.total_expenses || 0)}
          </p>
        </div>
        
        <div className="summary-card">
          <h3>Net Savings</h3>
          <p className={`summary-amount ${(summary?.summary?.net_savings || 0) >= 0 ? 'income' : 'expense'}`}>
            {formatCurrency(summary?.summary?.net_savings || 0)}
          </p>
        </div>
        
        <div className="summary-card">
          <h3>Transactions</h3>
          <p className="summary-amount">
            {summary?.summary?.transaction_count || 0}
          </p>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="recent-transactions">
        <h3>Recent Transactions</h3>
        {recentTransactions.length === 0 ? (
          <div className="empty-state">
            <p>No transactions yet. Add your first transaction to get started!</p>
            <button 
              className="btn btn-primary"
              onClick={() => window.location.href = '/transactions'}
            >
              Add Transaction
            </button>
          </div>
        ) : (
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.map((t) => (
                <tr key={t.id}>
                  <td>{t.date}</td>
                  <td>{t.description || '-'}</td>
                  <td>
                    <span className={`category-badge ${t.type}`}>
                      {t.category}
                    </span>
                  </td>
                  <td className={t.type}>
                    {t.type === 'income' ? '+' : '-'}
                    {formatCurrency(Math.abs(t.amount))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Dashboard;