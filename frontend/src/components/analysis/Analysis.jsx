import React, { useState, useEffect } from 'react';
import {
  Pie,
  Bar,
  Line
} from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Filler
} from 'chart.js';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  PieChart,
  BarChart2,
  Activity,
  AlertCircle,
  Info
} from 'lucide-react';
import analysisService from '../../services/analysis';
import transactionService from '../../services/transaction';
import toast from 'react-hot-toast';
import { formatZMK } from '../../utils/currency';
import './Analysis.css';
import { useCallback } from 'react';
// Register ChartJS components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Filler
);

const Analysis = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    compareMonth: new Date().getMonth(),
    compareYear: new Date().getMonth() === 0 ? new Date().getFullYear() - 1 : new Date().getFullYear()
  });
  const [categoryData, setCategoryData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [trends, setTrends] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [insights, setInsights] = useState(null);
  const [categories, setCategories] = useState({ expense: [], income: [] });

  useEffect(() => {
    loadCategories();
    loadAllData();
  }, []);

  useEffect(() => {
    if (activeTab === 'category') {
      loadCategoryBreakdown();
    } else if (activeTab === 'trends') {
      loadTrends();
    } else if (activeTab === 'compare') {
      loadComparison();
    } else if (activeTab === 'patterns') {
      loadPatterns();
    } else {
      loadOverview();
    }
  }, [activeTab, dateRange]);

  const loadCategories = async () => {
    try {
      const data = await transactionService.getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadOverview(),
        loadCategoryBreakdown(),
        loadTrends(),
        loadComparison(),
        loadPatterns(),
        loadInsights()
      ]);
    } catch (error) {
      toast.error('Failed to load analysis data');
    } finally {
      setLoading(false);
    }
  };

  const loadOverview = async () => {
    try {
      const [monthly, insights] = await Promise.all([
        analysisService.getMonthlySummary({ months: 6 }),
        analysisService.getInsights()
      ]);
      setMonthlyData(monthly);
      setInsights(insights);
    } catch (error) {
      console.error('Failed to load overview:', error);
    }
  };

  const loadCategoryBreakdown = async () => {
    try {
      const data = await analysisService.getCategoryBreakdown({
        month: dateRange.month,
        year: dateRange.year
      });
      setCategoryData(data);
    } catch (error) {
      console.error('Failed to load category breakdown:', error);
    }
  };

  const loadTrends = async () => {
    try {
      const data = await analysisService.getTrends({ months: 6 });
      setTrends(data);
    } catch (error) {
      console.error('Failed to load trends:', error);
    }
  };

  const loadComparison = async () => {
    try {
      const data = await analysisService.comparePeriods({
        current_month: dateRange.month,
        current_year: dateRange.year,
        previous_month: dateRange.compareMonth,
        previous_year: dateRange.compareYear
      });
      setComparison(data);
    } catch (error) {
      console.error('Failed to load comparison:', error);
    }
  };

  const loadPatterns = async () => {
    try {
      const data = await analysisService.getSpendingPatterns();
      setPatterns(data);
    } catch (error) {
      console.error('Failed to load patterns:', error);
    }
  };

  const loadInsights = async () => {
    try {
      const data = await analysisService.getInsights();
      setInsights(data);
    } catch (error) {
      console.error('Failed to load insights:', error);
    }
  };

  const formatCurrency = (value) => {
  return formatZMK(value);
};
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  // Chart configurations
  const getCategoryPieData = () => {
    if (!categoryData?.categories) return null;

    const categories = categoryData.categories;
    const colors = [
      '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
      '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF9F40'
    ];

    return {
      labels: Object.keys(categories),
      datasets: [
        {
          data: Object.values(categories).map(c => c.total),
          backgroundColor: colors.slice(0, Object.keys(categories).length),
          borderWidth: 1
        }
      ]
    };
  };

  const getMonthlyTrendData = () => {
    if (!monthlyData?.monthly_data) return null;

    const data = monthlyData.monthly_data.reverse();
    
    return {
      labels: data.map(m => m.month_name),
      datasets: [
        {
          label: 'Income',
          data: data.map(m => m.income),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: false
        },
        {
          label: 'Expenses',
          data: data.map(m => m.expenses),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          fill: false
        },
        {
          label: 'Savings',
          data: data.map(m => m.savings),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: false
        }
      ]
    };
  };

  const getComparisonBarData = () => {
    if (!comparison?.category_comparison) return null;

    const categories = comparison.category_comparison.slice(0, 5);
    
    return {
      labels: categories.map(c => c.category),
      datasets: [
        {
          label: 'Previous Period',
          data: categories.map(c => c.previous),
          backgroundColor: 'rgba(156, 163, 175, 0.5)',
          borderColor: '#6b7280',
          borderWidth: 1
        },
        {
          label: 'Current Period',
          data: categories.map(c => c.current),
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: '#3b82f6',
          borderWidth: 1
        }
      ]
    };
  };

  const getWeekdayPatternData = () => {
    if (!patterns?.by_day_of_week) return null;

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    
    return {
      labels: days,
      datasets: [
        {
          label: 'Average Spending',
          data: days.map(day => patterns.by_day_of_week[day]?.average || 0),
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: '#3b82f6',
          borderWidth: 1
        }
      ]
    };
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.raw || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${formatCurrency(value)} (${percentage}%)`;
          }
        }
      }
    }
  };

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.raw || 0;
            return `${label}: ${formatCurrency(value)}`;
          }
        }
      }
    },
    scales: {
      y: {
        ticks: {
          callback: (value) => formatCurrency(value)
        }
      }
    }
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || '';
            const value = context.raw || 0;
            return `${label}: ${formatCurrency(value)}`;
          }
        }
      }
    },
    scales: {
      y: {
        ticks: {
          callback: (value) => formatCurrency(value)
        }
      }
    }
  };

  return (
    <div className="analysis-container">
      <div className="analysis-header">
        <h1 className="page-title">Spending Analysis</h1>
        
        <div className="date-range-selector">
          <div className="selector-group">
            <Calendar size={18} className="selector-icon" />
            <select
              className="selector-select"
              value={dateRange.month}
              onChange={(e) => setDateRange(prev => ({ ...prev, month: parseInt(e.target.value) }))}
            >
              {months.map((month, index) => (
                <option key={index} value={index + 1}>{month}</option>
              ))}
            </select>
          </div>

          <div className="selector-group">
            <select
              className="selector-select"
              value={dateRange.year}
              onChange={(e) => setDateRange(prev => ({ ...prev, year: parseInt(e.target.value) }))}
            >
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="analysis-tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Activity size={18} />
          Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'category' ? 'active' : ''}`}
          onClick={() => setActiveTab('category')}
        >
          <PieChart size={18} />
          Categories
        </button>
        <button
          className={`tab-button ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          <TrendingUp size={18} />
          Trends
        </button>
        <button
          className={`tab-button ${activeTab === 'compare' ? 'active' : ''}`}
          onClick={() => setActiveTab('compare')}
        >
          <BarChart2 size={18} />
          Compare
        </button>
        <button
          className={`tab-button ${activeTab === 'patterns' ? 'active' : ''}`}
          onClick={() => setActiveTab('patterns')}
        >
          <Calendar size={18} />
          Patterns
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading analysis data...</p>
        </div>
      )}

      {/* Content */}
      {!loading && (
        <div className="analysis-content">
          {/* Overview Tab */}
          {activeTab === 'overview' && monthlyData && (
            <div className="overview-tab">
              {/* Summary Cards */}
              {monthlyData.averages && (
                <div className="summary-cards">
                  <div className="summary-card">
                    <div className="card-icon income">
                      <DollarSign size={24} />
                    </div>
                    <div className="card-info">
                      <h3>Avg. Monthly Income</h3>
                      <p className="card-value">{formatCurrency(monthlyData.averages.monthly_income)}</p>
                    </div>
                  </div>
                  
                  <div className="summary-card">
                    <div className="card-icon expense">
                      <DollarSign size={24} />
                    </div>
                    <div className="card-info">
                      <h3>Avg. Monthly Expenses</h3>
                      <p className="card-value">{formatCurrency(monthlyData.averages.monthly_expenses)}</p>
                    </div>
                  </div>
                  
                  <div className="summary-card">
                    <div className="card-icon savings">
                      <DollarSign size={24} />
                    </div>
                    <div className="card-info">
                      <h3>Avg. Monthly Savings</h3>
                      <p className="card-value">{formatCurrency(monthlyData.averages.monthly_savings)}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Monthly Trend Chart */}
              <div className="chart-card">
                <h3>6-Month Trend</h3>
                <div className="chart-container">
                  {getMonthlyTrendData() && (
                    <Line data={getMonthlyTrendData()} options={lineOptions} />
                  )}
                </div>
              </div>

              {/* Insights Section */}
              {insights && (
                <div className="insights-section">
                  <h3>Key Insights</h3>
                  <div className="insights-grid">
                    {insights.insights?.map((insight, index) => (
                      <div key={index} className="insight-card">
                        <Info size={20} className="insight-icon" />
                        <p>{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Category Tab */}
          {activeTab === 'category' && categoryData && (
            <div className="category-tab">
              <div className="category-header">
                <h3>Spending by Category - {months[dateRange.month - 1]} {dateRange.year}</h3>
                <p className="total-spent">
                  Total Spent: {formatCurrency(categoryData.total_spent)}
                </p>
              </div>

              <div className="category-charts">
                <div className="chart-card pie-chart">
                  {getCategoryPieData() && (
                    <Pie data={getCategoryPieData()} options={pieOptions} />
                  )}
                </div>

                <div className="category-list">
                  <h4>Category Breakdown</h4>
                  <div className="category-items">
                    {Object.entries(categoryData.categories || {}).map(([category, data]) => (
                      <div key={category} className="category-item">
                        <div className="category-info">
                          <span className="category-name">{category}</span>
                          <span className="category-percentage">{data.percentage}%</span>
                        </div>
                        <div className="category-bar">
                          <div 
                            className="category-bar-fill"
                            style={{ width: `${data.percentage}%` }}
                          />
                        </div>
                        <div className="category-amount">
                          {formatCurrency(data.total)}
                          <span className="transaction-count">
                            ({data.transaction_count} transactions)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Trends Tab */}
          {activeTab === 'trends' && trends && (
            <div className="trends-tab">
              <h3>Spending Trends (Last 6 Months)</h3>
              
              <div className="trends-grid">
                {Object.entries(trends.trends || {}).map(([category, data]) => (
                  <div key={category} className={`trend-card ${data.direction}`}>
                    <div className="trend-header">
                      <h4>{category}</h4>
                      <div className="trend-indicator">
                        {data.direction === 'increasing' ? (
                          <TrendingUp size={20} className="trend-up" />
                        ) : data.direction === 'decreasing' ? (
                          <TrendingDown size={20} className="trend-down" />
                        ) : (
                          <Activity size={20} className="trend-stable" />
                        )}
                      </div>
                    </div>
                    
                    <div className="trend-values">
                      <div className="trend-value">
                        <span>Current:</span>
                        <strong>{formatCurrency(data.current_monthly_avg)}</strong>
                      </div>
                      <div className="trend-value">
                        <span>Previous:</span>
                        <strong>{formatCurrency(data.previous_monthly_avg || 0)}</strong>
                      </div>
                    </div>
                    
                    <div className="trend-change">
                      <span>Change:</span>
                      <span className={data.percentage_change > 0 ? 'negative' : 'positive'}>
                        {data.percentage_change > 0 ? '+' : ''}{data.percentage_change}%
                      </span>
                    </div>
                    
                    <div className="trend-volatility">
                      Volatility: {data.volatility?.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>

              {Object.keys(trends.trends || {}).length === 0 && (
                <div className="empty-state">
                  <p>No trend data available for the selected period</p>
                </div>
              )}
            </div>
          )}

          {/* Compare Tab */}
          {activeTab === 'compare' && comparison && (
            <div className="compare-tab">
              <div className="compare-header">
                <h3>Period Comparison</h3>
                
                <div className="compare-selectors">
                  <div className="compare-period">
                    <span>Current:</span>
                    <select
                      value={dateRange.month}
                      onChange={(e) => setDateRange(prev => ({ ...prev, month: parseInt(e.target.value) }))}
                    >
                      {months.map((month, index) => (
                        <option key={index} value={index + 1}>{month}</option>
                      ))}
                    </select>
                    <select
                      value={dateRange.year}
                      onChange={(e) => setDateRange(prev => ({ ...prev, year: parseInt(e.target.value) }))}
                    >
                      {years.map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="compare-period">
                    <span>vs Previous:</span>
                    <select
                      value={dateRange.compareMonth}
                      onChange={(e) => setDateRange(prev => ({ ...prev, compareMonth: parseInt(e.target.value) }))}
                    >
                      {months.map((month, index) => (
                        <option key={index} value={index + 1}>{month}</option>
                      ))}
                    </select>
                    <select
                      value={dateRange.compareYear}
                      onChange={(e) => setDateRange(prev => ({ ...prev, compareYear: parseInt(e.target.value) }))}
                    >
                      {years.map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Overall Comparison */}
              {comparison.overall_change && (
                <div className="overall-comparison">
                  <div className={`change-card ${comparison.overall_change.percentage > 0 ? 'negative' : 'positive'}`}>
                    <h4>Overall Change</h4>
                    <p className="change-value">
                      {comparison.overall_change.percentage > 0 ? '+' : ''}
                      {comparison.overall_change.percentage}%
                    </p>
                    <p className="change-absolute">
                      {formatCurrency(Math.abs(comparison.overall_change.absolute))}
                    </p>
                  </div>
                </div>
              )}

              {/* Category Comparison Chart */}
              <div className="chart-card">
                <h4>Top 5 Categories Comparison</h4>
                <div className="chart-container">
                  {getComparisonBarData() && (
                    <Bar data={getComparisonBarData()} options={barOptions} />
                  )}
                </div>
              </div>

              {/* Category Changes Table */}
              <div className="changes-table">
                <h4>Category Changes</h4>
                <table>
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Previous</th>
                      <th>Current</th>
                      <th>Change</th>
                      <th>% Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.category_comparison?.map((item, index) => (
                      <tr key={index}>
                        <td>{item.category}</td>
                        <td>{formatCurrency(item.previous)}</td>
                        <td>{formatCurrency(item.current)}</td>
                        <td className={item.absolute_change > 0 ? 'negative' : 'positive'}>
                          {item.absolute_change > 0 ? '+' : ''}
                          {formatCurrency(item.absolute_change)}
                        </td>
                        <td className={item.percentage_change > 0 ? 'negative' : 'positive'}>
                          {item.percentage_change > 0 ? '+' : ''}
                          {item.percentage_change}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Patterns Tab */}
          {activeTab === 'patterns' && patterns && (
            <div className="patterns-tab">
              <h3>Spending Patterns</h3>
              
              <div className="patterns-grid">
                {/* Weekday vs Weekend */}
                {patterns.weekday_vs_weekend && (
                  <div className="pattern-card">
                    <h4>Weekday vs Weekend</h4>
                    <div className="pattern-stats">
                      <div className="stat">
                        <span className="stat-label">Weekday Average:</span>
                        <span className="stat-value">
                          {formatCurrency(patterns.weekday_vs_weekend.weekday.average)}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Weekend Average:</span>
                        <span className="stat-value">
                          {formatCurrency(patterns.weekday_vs_weekend.weekend.average)}
                        </span>
                      </div>
                      <div className="stat-difference">
                        {patterns.weekday_vs_weekend.weekend.average > patterns.weekday_vs_weekend.weekday.average ? (
                          <span className="warning">
                            You spend {((patterns.weekday_vs_weekend.weekend.average / patterns.weekday_vs_weekend.weekday.average - 1) * 100).toFixed(1)}% more on weekends
                          </span>
                        ) : (
                          <span className="info">
                            You spend less on weekends
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Day of Week Chart */}
                {getWeekdayPatternData() && (
                  <div className="pattern-card chart-card">
                    <h4>Spending by Day of Week</h4>
                    <div className="chart-container">
                      <Bar data={getWeekdayPatternData()} options={barOptions} />
                    </div>
                  </div>
                )}

                {/* Month Halves */}
                {patterns.month_halves && (
                  <div className="pattern-card">
                    <h4>First Half vs Second Half</h4>
                    <div className="pattern-stats">
                      <div className="stat">
                        <span className="stat-label">First Half (Days 1-15):</span>
                        <span className="stat-value">
                          {formatCurrency(patterns.month_halves.first_half.average)}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Second Half (Days 16-31):</span>
                        <span className="stat-value">
                          {formatCurrency(patterns.month_halves.second_half.average)}
                        </span>
                      </div>
                      <div className="stat-difference">
                        {patterns.month_halves.second_half.average > patterns.month_halves.first_half.average ? (
                          <span className="warning">
                            You spend more in the second half of the month
                          </span>
                        ) : (
                          <span className="info">
                            You spend more in the first half of the month
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Analysis;