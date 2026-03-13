import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const DatabaseCheck = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkDatabase();
  }, []);

  const checkDatabase = async () => {
    try {
      // Check if we can access the database through various endpoints
      const [transactions, categories, summary] = await Promise.all([
        api.get('/transactions?limit=5'),
        api.get('/transactions/categories'),
        api.get('/transactions/summary')
      ]);

      setStats({
        transactions: transactions.data,
        categories: categories.data,
        summary: summary.data,
        hasData: transactions.data.transactions?.length > 0
      });
    } catch (error) {
      console.error('Database check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Checking database...</div>;

  return (
    <div style={{ padding: '20px', background: '#f0f0f0', margin: '10px', borderRadius: '5px' }}>
      <h3>Database Status</h3>
      <p>Has Transactions: {stats?.hasData ? '✅ Yes' : '❌ No'}</p>
      {!stats?.hasData && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          <p>⚠️ No transactions found! You need to seed the database.</p>
          <button 
            onClick={() => window.location.href = '/seed-instructions'}
            style={{
              padding: '10px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            View Seeding Instructions
          </button>
        </div>
      )}
    </div>
  );
};

export default DatabaseCheck;
