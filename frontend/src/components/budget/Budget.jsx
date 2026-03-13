import React, { useState, useEffect } from 'react';
import {
  Bar,
  Line
} from 'react-chartjs-2';
import {
  Calendar,
  Target,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  DollarSign,
  PieChart,
  Clock,
  RefreshCw,
  Download,
  Edit,
  Save,
  X,
  Plus,
  Minus,
  Info
} from 'lucide-react';
import budgetService from '../../services/budget';
import transactionService from '../../services/transaction';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import { formatZMK } from '../../utils/currency';
import './Budget.css';

const Budget = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('current');
  const [currentBudget, setCurrentBudget] = useState(null);
  const [budgetComparison, setBudgetComparison] = useState(null);
  const [futureBudgets, setFutureBudgets] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [budgetHistory, setBudgetHistory] = useState(null);
  const [currentStatus, setCurrentStatus] = useState(null);
  const [categories, setCategories] = useState({ expense: [], income: [] });
  const [showSmartBudgetModal, setShowSmartBudgetModal] = useState(false);
  const [smartBudgetTarget, setSmartBudgetTarget] = useState(20);
  const [smartBudgetResult, setSmartBudgetResult] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  });

  useEffect(() => {
    loadCategories();
    loadAllBudgetData();
  }, []);

  useEffect(() => {
    if (activeTab === 'current') {
      loadCurrentBudget();
      loadCurrentStatus();
    } else if (activeTab === 'compare') {
      loadBudgetComparison();
    } else if (activeTab === 'future') {
      loadFutureBudgets();
    } else if (activeTab === 'history') {
      loadBudgetHistory();
    }
  }, [activeTab, selectedMonth]);

  const loadCategories = async () => {
    try {
      const data = await transactionService.getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadAllBudgetData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadCurrentBudget(),
        loadBudgetComparison(),
        loadFutureBudgets(),
        loadBudgetRecommendations(),
        loadBudgetHistory(),
        loadCurrentStatus()
      ]);
    } catch (error) {
      toast.error('Failed to load budget data');
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentBudget = async () => {
    try {
      const data = await budgetService.getMonthlyBudget({
        month: selectedMonth.month,
        year: selectedMonth.year
      });
      setCurrentBudget(data);
    } catch (error) {
      console.error('Failed to load current budget:', error);
    }
  };

  const loadBudgetComparison = async () => {
    try {
      const data = await budgetService.compareBudgetActual({
        month: selectedMonth.month,
        year: selectedMonth.year
      });
      setBudgetComparison(data);
    } catch (error) {
      console.error('Failed to load budget comparison:', error);
    }
  };

  const loadFutureBudgets = async () => {
    try {
      const data = await budgetService.getFutureBudgets({ months: 3 });
      setFutureBudgets(data);
    } catch (error) {
      console.error('Failed to load future budgets:', error);
    }
  };

  const loadBudgetRecommendations = async () => {
    try {
      const data = await budgetService.getBudgetRecommendations();
      setRecommendations(data);
    } catch (error) {
      console.error('Failed to load budget recommendations:', error);
    }
  };

  const loadBudgetHistory = async () => {
    try {
      const data = await budgetService.getBudgetHistory({ months: 6 });
      setBudgetHistory(data);
    } catch (error) {
      console.error('Failed to load budget history:', error);
    }
  };

  const loadCurrentStatus = async () => {
    try {
      const data = await budgetService.getCurrentBudgetStatus();
      setCurrentStatus(data);
    } catch (error) {
      console.error('Failed to load current status:', error);
    }
  };

  const handleCreateSmartBudget = async () => {
    setLoading(true);
    try {
      const result = await budgetService.createSmartBudget({
        target_savings_rate: smartBudgetTarget
      });
      setSmartBudgetResult(result);
      toast.success('Smart budget created successfully!');
    } catch (error) {
      toast.error('Failed to create smart budget');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadAllBudgetData();
    toast.success('Budget data refreshed');
  };

  const handleExport = () => {
    const data = {
      current_budget: currentBudget,
      comparison: budgetComparison,
      future_budgets: futureBudgets,
      history: budgetHistory,
      generated_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `budget_${selectedMonth.month}_${selectedMonth.year}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    toast.success('Budget data exported successfully');
  };

  const formatCurrency = (value) => {
  return formatZMK(value);
};

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i + 1);

  // Chart data for budget vs actual
  const getComparisonChartData = () => {
    if (!budgetComparison?.category_comparison) return null;

    const categories = budgetComparison.category_comparison.slice(0, 8);
    
    return {
      labels: categories.map(c => c.category),
      datasets: [
        {
          label: 'Budgeted',
          data: categories.map(c => c.budgeted),
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: '#3b82f6',
          borderWidth: 1
        },
        {
          label: 'Actual',
          data: categories.map(c => c.actual),
          backgroundColor: 'rgba(239, 68, 68, 0.5)',
          borderColor: '#ef4444',
          borderWidth: 1
        }
      ]
    };
  };

  // Chart data for budget history
  const getHistoryChartData = () => {
    if (!budgetHistory?.history) return null;

    const history = budgetHistory.history.reverse();
    
    return {
      labels: history.map(h => h.period),
      datasets: [
        {
          label: 'Budgeted',
          data: history.map(h => h.budgeted),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: false
        },
        {
          label: 'Actual',
          data: history.map(h => h.actual),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          fill: false
        }
      ]
    };
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
            const value = context.raw || 0;
            return `${context.dataset.label}: ${formatCurrency(value)}`;
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

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.raw || 0;
            return `${context.dataset.label}: ${formatCurrency(value)}`;
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
    <div className="budget-container">
      <div className="budget-header">
        <h1 className="page-title">Budget Planner</h1>
        
        <div className="header-actions">
          <button className="btn btn-outline" onClick={handleExport}>
            <Download size={18} />
            Export
          </button>
          <button className="btn btn-outline" onClick={handleRefresh}>
            <RefreshCw size={18} />
            Refresh
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => setShowSmartBudgetModal(true)}
          >
            <Target size={18} />
            Smart Budget
          </button>
        </div>
      </div>

      {/* Month Selector */}
      <div className="month-selector">
        <div className="selector-group">
          <Calendar size={18} className="selector-icon" />
          <select
            className="selector-select"
            value={selectedMonth.month}
            onChange={(e) => setSelectedMonth(prev => ({ 
              ...prev, 
              month: parseInt(e.target.value) 
            }))}
          >
            {months.map((month, index) => (
              <option key={index} value={index + 1}>{month}</option>
            ))}
          </select>
        </div>

        <div className="selector-group">
          <select
            className="selector-select"
            value={selectedMonth.year}
            onChange={(e) => setSelectedMonth(prev => ({ 
              ...prev, 
              year: parseInt(e.target.value) 
            }))}
          >
            {years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div className="budget-tabs">
        <button
          className={`tab-button ${activeTab === 'current' ? 'active' : ''}`}
          onClick={() => setActiveTab('current')}
        >
          <DollarSign size={18} />
          Current Budget
        </button>
        <button
          className={`tab-button ${activeTab === 'compare' ? 'active' : ''}`}
          onClick={() => setActiveTab('compare')}
        >
          <PieChart size={18} />
          Budget vs Actual
        </button>
        <button
          className={`tab-button ${activeTab === 'future' ? 'active' : ''}`}
          onClick={() => setActiveTab('future')}
        >
          <Clock size={18} />
          Future Outlook
        </button>
        <button
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <TrendingUp size={18} />
          History
        </button>
        <button
          className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          <Target size={18} />
          Recommendations
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading budget data...</p>
        </div>
      )}

      {/* Content */}
      {!loading && (
        <div className="budget-content">
          {/* Current Budget Tab */}
          {activeTab === 'current' && currentBudget && (
            <div className="current-budget-tab">
              {/* Current Status Alert */}
              {currentStatus && (
                <div className={`status-alert ${currentStatus.on_track ? 'on-track' : 'off-track'}`}>
                  <div className="status-info">
                    {currentStatus.on_track ? (
                      <CheckCircle size={20} className="status-icon success" />
                    ) : (
                      <AlertCircle size={20} className="status-icon warning" />
                    )}
                    <div>
                      <h3>
                        {currentStatus.on_track ? 'On Track' : 'Behind Budget'}
                      </h3>
                      <p>
                        {currentStatus.percent_used}% of budget used • 
                        {currentStatus.percent_time_passed}% of month passed
                      </p>
                    </div>
                  </div>
                  <div className="status-stats">
                    <div className="stat">
                      <span>Spent:</span>
                      <strong>{formatCurrency(currentStatus.spent_so_far)}</strong>
                    </div>
                    <div className="stat">
                      <span>Remaining:</span>
                      <strong>{formatCurrency(currentStatus.remaining)}</strong>
                    </div>
                    <div className="stat">
                      <span>Daily budget:</span>
                      <strong>{formatCurrency(currentStatus.daily_budget)}</strong>
                    </div>
                  </div>
                </div>
              )}

              {/* Budget Summary */}
              <div className="budget-summary">
                <h3>Budget Overview - {months[selectedMonth.month - 1]} {selectedMonth.year}</h3>
                
                <div className="summary-cards">
                  <div className="summary-card">
                    <div className="card-icon income">
                      <DollarSign size={24} />
                    </div>
                    <div className="card-info">
                      <h4>Total Income</h4>
                      <p className="card-value">{formatCurrency(currentBudget.income?.total_income)}</p>
                    </div>
                  </div>
                  
                  <div className="summary-card">
                    <div className="card-icon expense">
                      <DollarSign size={24} />
                    </div>
                    <div className="card-info">
                      <h4>Total Budgeted</h4>
                      <p className="card-value">{formatCurrency(currentBudget.summary?.total_budgeted)}</p>
                    </div>
                  </div>
                  
                  <div className="summary-card">
                    <div className="card-icon savings">
                      <DollarSign size={24} />
                    </div>
                    <div className="card-info">
                      <h4>Projected Savings</h4>
                      <p className="card-value">{formatCurrency(currentBudget.summary?.projected_savings)}</p>
                      <span className="savings-rate">{currentBudget.summary?.savings_rate}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Category Budgets */}
              <div className="category-budgets">
                <h3>Category Breakdown</h3>
                
                <div className="budget-list">
                  {Object.entries(currentBudget.category_budgets || {}).map(([category, data]) => (
                    <div key={category} className="budget-item">
                      <div className="budget-item-header">
                        <span className="category-name">{category}</span>
                        <span className={`category-type ${data.type}`}>
                          {data.type}
                        </span>
                      </div>
                      
                      <div className="budget-amounts">
                        <span className="budget-label">Allocated:</span>
                        <span className="budget-value">{formatCurrency(data.allocated)}</span>
                      </div>
                      
                      {data.historical_avg > 0 && (
                        <div className="budget-amounts">
                          <span className="budget-label">Historical avg:</span>
                          <span className="budget-value">{formatCurrency(data.historical_avg)}</span>
                        </div>
                      )}
                      
                      {data.notes && (
                        <div className="budget-note">
                          <Info size={14} />
                          <span>{data.notes}</span>
                        </div>
                      )}
                      
                      {currentStatus?.category_status && (
                        <div className="budget-progress">
                          {(() => {
                            const catStatus = currentStatus.category_status.find(
                              c => c.category === category
                            );
                            if (catStatus) {
                              return (
                                <>
                                  <div className="progress-bar">
                                    <div 
                                      className={`progress-fill ${catStatus.status}`}
                                      style={{ width: `${Math.min(catStatus.percent_used, 100)}%` }}
                                    />
                                  </div>
                                  <div className="progress-stats">
                                    <span>Spent: {formatCurrency(catStatus.spent)}</span>
                                    <span className={catStatus.status}>
                                      {catStatus.percent_used}%
                                    </span>
                                  </div>
                                </>
                              );
                            }
                            return null;
                          })()}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Budget Tips */}
              {currentBudget.tips && currentBudget.tips.length > 0 && (
                <div className="budget-tips">
                  <h3>Budget Tips</h3>
                  <div className="tips-list">
                    {currentBudget.tips.map((tip, index) => (
                      <div key={index} className="tip-item">
                        <Info size={16} className="tip-icon" />
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Budget vs Actual Tab */}
          {activeTab === 'compare' && budgetComparison && (
            <div className="compare-tab">
              {/* Comparison Summary */}
              <div className="comparison-summary">
                <div className={`summary-card ${budgetComparison.summary?.total_difference >= 0 ? 'positive' : 'negative'}`}>
                  <h3>Total Variance</h3>
                  <p className="summary-value">
                    {formatCurrency(Math.abs(budgetComparison.summary?.total_difference))}
                  </p>
                  <p className="summary-label">
                    {budgetComparison.summary?.total_difference >= 0 ? 'Under Budget' : 'Over Budget'}
                  </p>
                </div>
                
                <div className="summary-card">
                  <h3>Categories</h3>
                  <p className="summary-value">
                    {budgetComparison.categories_over_budget} / {budgetComparison.categories_under_budget}
                  </p>
                  <p className="summary-label">Over / Under</p>
                </div>
                
                <div className="summary-card">
                  <h3>Actual Savings</h3>
                  <p className="summary-value">
                    {formatCurrency(budgetComparison.summary?.actual_savings)}
                  </p>
                  <p className="summary-label">
                    vs {formatCurrency(budgetComparison.summary?.budgeted_savings)} budgeted
                  </p>
                </div>
              </div>

              {/* Comparison Chart */}
              {getComparisonChartData() && (
                <div className="chart-card">
                  <h3>Budget vs Actual - Top Categories</h3>
                  <div className="chart-container">
                    <Bar data={getComparisonChartData()} options={barOptions} />
                  </div>
                </div>
              )}

              {/* Category Comparison Table */}
              <div className="comparison-table">
                <h3>Category Details</h3>
                <div className="table-responsive">
                  <table>
                    <thead>
                      <tr>
                        <th>Category</th>
                        <th>Budgeted</th>
                        <th>Actual</th>
                        <th>Difference</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {budgetComparison.category_comparison?.map((item, index) => (
                        <tr key={index}>
                          <td>{item.category}</td>
                          <td>{formatCurrency(item.budgeted)}</td>
                          <td>{formatCurrency(item.actual)}</td>
                          <td className={item.difference >= 0 ? 'positive' : 'negative'}>
                            {item.difference >= 0 ? '+' : ''}{formatCurrency(item.difference)}
                          </td>
                          <td>
                            <span className={`status-badge ${item.status}`}>
                              {item.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Future Outlook Tab */}
          {activeTab === 'future' && futureBudgets && (
            <div className="future-tab">
              <h3>Next 3 Months Budget Projections</h3>
              
              <div className="future-timeline">
                {futureBudgets.future_budgets?.map((budget, index) => (
                  <div key={index} className="future-card">
                    <div className="future-header">
                      <h4>{budget.month} {budget.year}</h4>
                      <span className={`confidence-badge ${budget.confidence.toLowerCase()}`}>
                        {budget.confidence} Confidence
                      </span>
                    </div>
                    
                    <div className="future-details">
                      <div className="detail">
                        <span>Total Budget:</span>
                        <strong>{formatCurrency(budget.total_budget)}</strong>
                      </div>
                      <div className="detail">
                        <span>Projected Savings:</span>
                        <strong>{formatCurrency(budget.projected_savings)}</strong>
                      </div>
                      <div className="detail">
                        <span>Savings Rate:</span>
                        <strong>{budget.savings_rate}%</strong>
                      </div>
                    </div>
                    
                    <div className="future-categories">
                      <span>Categories: {budget.categories}</span>
                    </div>
                    
                    {index === 0 && (
                      <div className="future-note">
                        <Info size={14} />
                        <span>Highest confidence prediction</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && budgetHistory && (
            <div className="history-tab">
              <h3>Budget Performance History</h3>
              
              {/* History Chart */}
              {getHistoryChartData() && (
                <div className="chart-card">
                  <div className="chart-container">
                    <Line data={getHistoryChartData()} options={lineOptions} />
                  </div>
                </div>
              )}

              {/* History Table */}
              <div className="history-table">
                <h4>Monthly Breakdown</h4>
                <div className="table-responsive">
                  <table>
                    <thead>
                      <tr>
                        <th>Month</th>
                        <th>Budgeted</th>
                        <th>Actual</th>
                        <th>Difference</th>
                        <th>Categories Over</th>
                      </tr>
                    </thead>
                    <tbody>
                      {budgetHistory.history?.map((item, index) => (
                        <tr key={index}>
                          <td>{item.period}</td>
                          <td>{formatCurrency(item.budgeted)}</td>
                          <td>{formatCurrency(item.actual)}</td>
                          <td className={item.difference >= 0 ? 'positive' : 'negative'}>
                            {item.difference >= 0 ? '+' : ''}{formatCurrency(item.difference)}
                          </td>
                          <td>
                            <span className="over-badge">
                              {item.categories_over} over / {item.categories_under} under
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations Tab */}
          {activeTab === 'recommendations' && recommendations && (
            <div className="recommendations-tab">
              <h3>Budget Optimization Suggestions</h3>
              
              <div className="recommendations-list">
                {recommendations.recommendations?.map((rec, index) => (
                  <div key={index} className={`recommendation-card type-${rec.type}`}>
                    <div className="recommendation-header">
                      {rec.type === 'budget_adjustment' && <Target size={20} />}
                      {rec.type === 'reallocation' && <TrendingUp size={20} />}
                      {rec.type === 'savings_opportunity' && <DollarSign size={20} />}
                      <h4>
                        {rec.type === 'budget_adjustment' && 'Budget Adjustment Needed'}
                        {rec.type === 'reallocation' && 'Reallocation Opportunity'}
                        {rec.type === 'savings_opportunity' && 'Savings Opportunity'}
                      </h4>
                    </div>
                    
                    <div className="recommendation-details">
                      {rec.type === 'budget_adjustment' && (
                        <>
                          <p className="recommendation-desc">
                            {rec.reason}
                          </p>
                          <div className="adjustment-details">
                            <div className="detail">
                              <span>Current budget:</span>
                              <strong>{formatCurrency(rec.current_budget)}</strong>
                            </div>
                            <div className="detail">
                              <span>Suggested:</span>
                              <strong className="suggested">
                                {formatCurrency(rec.suggested_budget)}
                              </strong>
                            </div>
                          </div>
                        </>
                      )}
                      
                      {rec.type === 'reallocation' && (
                        <>
                          <p className="recommendation-desc">
                            {rec.suggestion}
                          </p>
                          <div className="savings-amount">
                            Potential savings: {formatCurrency(rec.potential_savings)}
                          </div>
                        </>
                      )}
                      
                      {rec.type === 'savings_opportunity' && (
                        <>
                          <p className="recommendation-desc">
                            {rec.description}
                          </p>
                          <div className="savings-amount">
                            {formatCurrency(rec.potential_savings)}/month
                          </div>
                          <p className="recommendation-suggestion">
                            {rec.suggestion}
                          </p>
                        </>
                      )}
                    </div>
                    
                    <button className="recommendation-action">
                      Apply Suggestion
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Smart Budget Modal */}
      {showSmartBudgetModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Create Smart Budget</h2>
              <button className="close-button" onClick={() => {
                setShowSmartBudgetModal(false);
                setSmartBudgetResult(null);
              }}>
                <X size={20} />
              </button>
            </div>

            <div className="modal-body">
              {!smartBudgetResult ? (
                <>
                  <p className="modal-description">
                    Set your target savings rate and we'll create an optimized budget based on your spending patterns.
                  </p>
                  
                  <div className="target-input">
                    <label>Target Savings Rate (%)</label>
                    <div className="input-with-controls">
                      <button 
                        className="control-btn"
                        onClick={() => setSmartBudgetTarget(Math.max(5, smartBudgetTarget - 5))}
                      >
                        <Minus size={16} />
                      </button>
                      <input
                        type="number"
                        value={smartBudgetTarget}
                        onChange={(e) => setSmartBudgetTarget(Math.min(50, Math.max(5, parseInt(e.target.value) || 5)))}
                        min="5"
                        max="50"
                        step="5"
                      />
                      <button 
                        className="control-btn"
                        onClick={() => setSmartBudgetTarget(Math.min(50, smartBudgetTarget + 5))}
                      >
                        <Plus size={16} />
                      </button>
                    </div>
                    <span className="input-hint">Recommended: 20%</span>
                  </div>

                  <button 
                    className="btn btn-primary modal-action"
                    onClick={handleCreateSmartBudget}
                    disabled={loading}
                  >
                    {loading ? 'Creating...' : 'Generate Smart Budget'}
                  </button>
                </>
              ) : (
                <div className="smart-budget-result">
                  <h3>Your Optimized Budget</h3>
                  
                  <div className="result-summary">
                    <div className="result-item">
                      <span>Monthly Income:</span>
                      <strong>{formatCurrency(smartBudgetResult.income)}</strong>
                    </div>
                    <div className="result-item">
                      <span>Target Savings:</span>
                      <strong>{smartBudgetResult.target_savings_rate}%</strong>
                    </div>
                    <div className="result-item">
                      <span>Available for Expenses:</span>
                      <strong>{formatCurrency(smartBudgetResult.available_for_expenses)}</strong>
                    </div>
                  </div>

                  <div className="result-categories">
                    <h4>Category Allocations</h4>
                    {Object.entries(smartBudgetResult.category_budgets || {}).map(([category, data]) => (
                      <div key={category} className="result-category">
                        <div className="category-header">
                          <span>{category}</span>
                          <span className="category-amount">
                            {formatCurrency(data.allocated)}
                          </span>
                        </div>
                        {data.change && (
                          <div className={`category-change ${data.change > 0 ? 'increase' : 'decrease'}`}>
                            {data.change > 0 ? '+' : ''}{formatCurrency(data.change)} from historical
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="result-footer">
                    <p className={`result-status ${smartBudgetResult.summary?.on_target ? 'success' : 'warning'}`}>
                      {smartBudgetResult.summary?.on_target 
                        ? '✓ Budget meets your savings target' 
                        : '⚠ Budget slightly off target - consider adjustments'}
                    </p>
                    
                    <button 
                      className="btn btn-primary"
                      onClick={() => {
                        setShowSmartBudgetModal(false);
                        setSmartBudgetResult(null);
                        loadCurrentBudget(); // Refresh current budget
                      }}
                    >
                      Apply This Budget
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budget;