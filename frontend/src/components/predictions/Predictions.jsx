import React, { useState, useEffect } from 'react';
import {
  Line,
  Bar
} from 'react-chartjs-2';
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  Calendar,
  Layers,
  Activity,
  BarChart2,
  Download,
  RefreshCw,
  Info
} from 'lucide-react';
import predictionService from '../../services/prediction';
import transactionService from '../../services/transaction';
import toast from 'react-hot-toast';
import { formatZMK } from '../../utils/currency';
import './Predictions.css';

const Predictions = () => {
  const [loading, setLoading] = useState(false);
  const [activeModel, setActiveModel] = useState('ensemble');
  const [predictionData, setPredictionData] = useState(null);
  const [categoryPredictions, setCategoryPredictions] = useState(null);
  const [multiMonthPredictions, setMultiMonthPredictions] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [categories, setCategories] = useState({ expense: [], income: [] });

  useEffect(() => {
    loadCategories();
    loadAllPredictions();
  }, []);

  useEffect(() => {
    if (activeModel === 'ensemble') {
      loadEnsemblePrediction();
    } else if (activeModel === 'category') {
      loadCategoryPredictions();
    } else if (activeModel === 'multi') {
      loadMultiMonthPredictions();
    }
  }, [activeModel, selectedCategory]);

  const loadCategories = async () => {
    try {
      const data = await transactionService.getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadAllPredictions = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadEnsemblePrediction(),
        loadCategoryPredictions(),
        loadMultiMonthPredictions(),
        loadPredictionHealth(),
        loadPredictionInsights()
      ]);
    } catch (error) {
      toast.error('Failed to load prediction data');
    } finally {
      setLoading(false);
    }
  };

  const loadEnsemblePrediction = async () => {
    try {
      if (selectedCategory === 'all') {
        const data = await predictionService.getEnsemblePrediction();
        setPredictionData(data);
        
        // Also load historical data for chart
        if (data.individual_predictions) {
          setHistoricalData({
            linear: data.individual_predictions.linear,
            moving_avg_3m: data.individual_predictions.moving_avg_3m,
            moving_avg_6m: data.individual_predictions.moving_avg_6m
          });
        }
      } else {
        const data = await predictionService.getNextMonthPrediction({ 
          category: selectedCategory 
        });
        setPredictionData(data);
      }
    } catch (error) {
      console.error('Failed to load ensemble prediction:', error);
    }
  };

  const loadCategoryPredictions = async () => {
    try {
      const data = await predictionService.getCategoryPredictions();
      setCategoryPredictions(data);
    } catch (error) {
      console.error('Failed to load category predictions:', error);
    }
  };

  const loadMultiMonthPredictions = async () => {
    try {
      const data = await predictionService.getMultiMonthPrediction({ months: 3 });
      setMultiMonthPredictions(data);
    } catch (error) {
      console.error('Failed to load multi-month predictions:', error);
    }
  };

  const loadPredictionHealth = async () => {
    try {
      const data = await predictionService.getPredictionHealth();
      setHealthData(data);
    } catch (error) {
      console.error('Failed to load prediction health:', error);
    }
  };

  const loadPredictionInsights = async () => {
    try {
      const data = await predictionService.getPredictionInsights();
      setInsights(data);
    } catch (error) {
      console.error('Failed to load prediction insights:', error);
    }
  };

  const handleRefresh = () => {
    loadAllPredictions();
    toast.success('Predictions refreshed');
  };

  const handleExport = () => {
    const data = {
      predictions: predictionData,
      category_predictions: categoryPredictions,
      multi_month: multiMonthPredictions,
      generated_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `predictions_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    toast.success('Predictions exported successfully');
  };

  const formatCurrency = (value) => {
  return formatZMK(value);
};
  const getConfidenceColor = (level) => {
    switch(level?.toLowerCase()) {
      case 'high':
        return '#10b981';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getConfidenceIcon = (level) => {
    switch(level?.toLowerCase()) {
      case 'high':
        return <CheckCircle size={20} className="confidence-icon high" />;
      case 'medium':
        return <AlertCircle size={20} className="confidence-icon medium" />;
      case 'low':
        return <AlertCircle size={20} className="confidence-icon low" />;
      default:
        return <Info size={20} className="confidence-icon" />;
    }
  };

  // Chart data for model comparison
  const getComparisonChartData = () => {
    if (!historicalData) return null;

    const labels = ['Linear Regression', '3-Month MA', '6-Month MA', 'Ensemble'];
    const values = [
      historicalData.linear,
      historicalData.moving_avg_3m,
      historicalData.moving_avg_6m,
      predictionData?.prediction?.total
    ];

    return {
      labels,
      datasets: [
        {
          label: 'Predicted Amount',
          data: values,
          backgroundColor: [
            'rgba(59, 130, 246, 0.5)',
            'rgba(16, 185, 129, 0.5)',
            'rgba(245, 158, 11, 0.5)',
            'rgba(139, 92, 246, 0.5)'
          ],
          borderColor: [
            '#3b82f6',
            '#10b981',
            '#f59e0b',
            '#8b5cf6'
          ],
          borderWidth: 1
        }
      ]
    };
  };

  // Chart data for historical trend
  const getHistoricalTrendData = () => {
    if (!predictionData?.historical_data) return null;

    const historical = predictionData.historical_data;
    
    return {
      labels: historical.months,
      datasets: [
        {
          label: 'Historical Spending',
          data: historical.totals,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: false
        },
        {
          label: 'Predicted Next Month',
          data: [...historical.totals, predictionData.prediction.total],
          borderColor: '#ef4444',
          borderDash: [5, 5],
          pointRadius: (ctx) => ctx.dataIndex === historical.totals.length ? 8 : 0,
          pointBackgroundColor: '#ef4444',
          pointBorderColor: 'white',
          pointBorderWidth: 2,
          fill: false
        }
      ]
    };
  };

  // Chart data for category predictions
  const getCategoryChartData = () => {
    if (!categoryPredictions?.by_category) return null;

    const categories = Object.entries(categoryPredictions.by_category)
      .sort((a, b) => b[1].predicted - a[1].predicted)
      .slice(0, 8); // Top 8 categories

    return {
      labels: categories.map(([cat]) => cat),
      datasets: [
        {
          label: 'Predicted Next Month',
          data: categories.map(([, data]) => data.predicted),
          backgroundColor: categories.map(([, data]) => 
            getConfidenceColor(data.confidence?.level)
          ),
          borderWidth: 1
        }
      ]
    };
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.raw || 0;
            return `Predicted: ${formatCurrency(value)}`;
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
    <div className="predictions-container">
      <div className="predictions-header">
        <h1 className="page-title">Expense Predictions</h1>
        
        <div className="header-actions">
          <button className="btn btn-outline" onClick={handleExport}>
            <Download size={18} />
            Export
          </button>
          <button className="btn btn-outline" onClick={handleRefresh}>
            <RefreshCw size={18} />
            Refresh
          </button>
        </div>
      </div>

      {/* Model Selector */}
      <div className="model-selector">
        <button
          className={`model-button ${activeModel === 'ensemble' ? 'active' : ''}`}
          onClick={() => setActiveModel('ensemble')}
        >
          <Layers size={18} />
          Ensemble
        </button>
        <button
          className={`model-button ${activeModel === 'category' ? 'active' : ''}`}
          onClick={() => setActiveModel('category')}
        >
          <BarChart2 size={18} />
          By Category
        </button>
        <button
          className={`model-button ${activeModel === 'multi' ? 'active' : ''}`}
          onClick={() => setActiveModel('multi')}
        >
          <Calendar size={18} />
          3-Month Outlook
        </button>
      </div>

      {/* Data Health Indicator */}
      {healthData && (
        <div className={`health-indicator ${healthData.can_predict ? 'healthy' : 'warning'}`}>
          <div className="health-info">
            {healthData.can_predict ? (
              <CheckCircle size={20} className="health-icon healthy" />
            ) : (
              <AlertCircle size={20} className="health-icon warning" />
            )}
            <span>
              {healthData.can_predict 
                ? `Ready to predict (${healthData.months_of_data} months of data)` 
                : `Need at least 3 months of data (currently ${healthData.months_of_data} months)`}
            </span>
          </div>
          {healthData.available_methods && (
            <div className="available-methods">
              Available: {healthData.available_methods.join(' • ')}
            </div>
          )}
        </div>
      )}

      {/* Category Filter (for ensemble view) */}
      {activeModel === 'ensemble' && (
        <div className="category-filter">
          <label>Category:</label>
          <select 
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Categories</option>
            {categories.expense?.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Running prediction models...</p>
        </div>
      )}

      {/* Content */}
      {!loading && (
        <div className="predictions-content">
          {/* Ensemble Model View */}
          {activeModel === 'ensemble' && predictionData && (
            <div className="ensemble-view">
              {/* Main Prediction Card */}
              <div className="prediction-main-card">
                <div className="prediction-header">
                  <h2>Next Month Prediction</h2>
                  {predictionData.confidence && (
                    <div 
                      className="confidence-badge"
                      style={{ backgroundColor: getConfidenceColor(predictionData.confidence.level) }}
                    >
                      {getConfidenceIcon(predictionData.confidence.level)}
                      {predictionData.confidence.level} Confidence
                    </div>
                  )}
                </div>

                <div className="prediction-amount">
                  {formatCurrency(predictionData.prediction?.total)}
                </div>

                {predictionData.trend && (
                  <div className={`trend-indicator ${predictionData.trend.direction}`}>
                    {predictionData.trend.direction === 'increasing' ? (
                      <TrendingUp size={20} />
                    ) : predictionData.trend.direction === 'decreasing' ? (
                      <TrendingDown size={20} />
                    ) : (
                      <Activity size={20} />
                    )}
                    <span>
                      Trend: {predictionData.trend.direction} 
                      ({predictionData.trend.strength})
                    </span>
                  </div>
                )}

                <div className="prediction-details">
                  {predictionData.prediction?.transaction_count && (
                    <div className="detail-item">
                      <span>Expected Transactions:</span>
                      <strong>{predictionData.prediction.transaction_count}</strong>
                    </div>
                  )}
                  {predictionData.prediction?.average_per_transaction && (
                    <div className="detail-item">
                      <span>Average per Transaction:</span>
                      <strong>{formatCurrency(predictionData.prediction.average_per_transaction)}</strong>
                    </div>
                  )}
                  <div className="detail-item">
                    <span>Based on:</span>
                    <strong>{predictionData.based_on_months} months of data</strong>
                  </div>
                </div>
              </div>

              {/* Historical Trend Chart */}
              {getHistoricalTrendData() && (
                <div className="chart-card">
                  <h3>Historical Trend & Prediction</h3>
                  <div className="chart-container">
                    <Line data={getHistoricalTrendData()} options={lineOptions} />
                  </div>
                </div>
              )}

              {/* Model Comparison */}
              {getComparisonChartData() && (
                <div className="chart-card">
                  <h3>Model Comparison</h3>
                  <div className="chart-container">
                    <Bar data={getComparisonChartData()} options={barOptions} />
                  </div>
                </div>
              )}

              {/* Confidence Details */}
              {predictionData.confidence && (
                <div className="confidence-details">
                  <h3>Confidence Analysis</h3>
                  <div className="confidence-metrics">
                    <div className="metric">
                      <span>R² Score:</span>
                      <strong>{predictionData.confidence.r2_score}</strong>
                    </div>
                    <div className="metric">
                      <span>Data Points:</span>
                      <strong>{predictionData.confidence.data_points}</strong>
                    </div>
                    <div className="metric">
                      <span>Volatility:</span>
                      <strong>{predictionData.confidence.volatility}</strong>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Category Predictions View */}
          {activeModel === 'category' && categoryPredictions && (
            <div className="category-view">
              <div className="category-summary">
                <div className="summary-card">
                  <h3>Total Predicted</h3>
                  <p className="summary-value">{formatCurrency(categoryPredictions.total_predicted)}</p>
                  <p className="summary-sub">{categoryPredictions.categories_analyzed} categories</p>
                </div>
              </div>

              {/* Category Chart */}
              {getCategoryChartData() && (
                <div className="chart-card">
                  <h3>Predicted Spending by Category</h3>
                  <div className="chart-container">
                    <Bar data={getCategoryChartData()} options={barOptions} />
                  </div>
                </div>
              )}

              {/* Category List */}
              <div className="category-list">
                <h3>Category Breakdown</h3>
                <div className="category-items">
                  {Object.entries(categoryPredictions.by_category || {})
                    .sort((a, b) => b[1].predicted - a[1].predicted)
                    .map(([category, data]) => (
                      <div key={category} className="category-prediction-item">
                        <div className="category-info">
                          <span className="category-name">{category}</span>
                          <div className="category-stats">
                            <span className="category-amount">
                              {formatCurrency(data.predicted)}
                            </span>
                            <div 
                              className="confidence-dot"
                              style={{ backgroundColor: getConfidenceColor(data.confidence?.level) }}
                              title={`${data.confidence?.level} confidence`}
                            />
                          </div>
                        </div>
                        {data.trend && (
                          <div className={`category-trend ${data.trend.direction}`}>
                            {data.trend.direction === 'increasing' ? (
                              <TrendingUp size={14} />
                            ) : data.trend.direction === 'decreasing' ? (
                              <TrendingDown size={14} />
                            ) : (
                              <Activity size={14} />
                            )}
                            <span>{data.trend.strength}</span>
                          </div>
                        )}
                        <div className="category-bar">
                          <div 
                            className="category-bar-fill"
                            style={{ 
                              width: `${(data.predicted / categoryPredictions.total_predicted) * 100}%`,
                              backgroundColor: getConfidenceColor(data.confidence?.level)
                            }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Multi-Month Predictions View */}
          {activeModel === 'multi' && multiMonthPredictions && (
            <div className="multi-view">
              <h3>3-Month Outlook</h3>
              
              <div className="timeline">
                {multiMonthPredictions.predictions?.map((pred, index) => (
                  <div key={index} className="timeline-item">
                    <div className="timeline-marker">
                      <Clock size={20} />
                      <div className="timeline-line"></div>
                    </div>
                    
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <h4>{pred.month}</h4>
                        <div 
                          className="confidence-badge small"
                          style={{ 
                            backgroundColor: pred.confidence_factor > 70 ? '#10b981' :
                                          pred.confidence_factor > 40 ? '#f59e0b' : '#ef4444'
                          }}
                        >
                          {pred.confidence_factor}% confidence
                        </div>
                      </div>
                      
                      <div className="prediction-amount">
                        {formatCurrency(pred.predicted_total)}
                      </div>
                      
                      <div className="prediction-note">
                        {index === 0 ? (
                          <span className="note-highest">Highest confidence</span>
                        ) : index === 2 ? (
                          <span className="note-lowest">Lowest confidence</span>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="confidence-explanation">
                <h4>About Confidence Levels</h4>
                <p>
                  Confidence decreases for predictions further in the future due to 
                  increasing uncertainty. The next month's prediction has the highest 
                  confidence based on recent trends.
                </p>
              </div>
            </div>
          )}

          {/* Insights Section */}
          {insights && (
            <div className="insights-section">
              <h3>Prediction Insights</h3>
              
              {insights.method_comparison && (
                <div className="method-comparison">
                  <h4>Method Comparison</h4>
                  <div className="comparison-grid">
                    {insights.method_comparison.map((method, index) => (
                      <div key={index} className="comparison-card">
                        <h5>{method.method}</h5>
                        <p className="comparison-value">{formatCurrency(method.predicted)}</p>
                        <span className={`comparison-confidence ${method.confidence?.toLowerCase()}`}>
                          {method.confidence}
                        </span>
                      </div>
                    ))}
                    
                    {insights.average_prediction && (
                      <div className="comparison-card average">
                        <h5>Average</h5>
                        <p className="comparison-value">{formatCurrency(insights.average_prediction)}</p>
                        <span>of all methods</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Predictions;