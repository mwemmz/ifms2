import React, { useState, useEffect } from 'react';
import {
  Heart,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Target,
  DollarSign,
  Shield,
  PiggyBank,
  Lightbulb,
  Clock,
  Calendar,
  ArrowUp,
  ArrowDown,
  Info,
  Award,
  Zap,
  Coffee,
  ShoppingBag,
  Home,
  Car,
  Utensils,
  Gift
} from 'lucide-react';
import adviceService from '../../services/advice';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import { formatZMK } from '../../utils/currency';
import './Advice.css';

const Advice = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [healthScore, setHealthScore] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [budgetSuggestions, setBudgetSuggestions] = useState(null);
  const [overspending, setOverspending] = useState([]);
  const [savingsOpportunities, setSavingsOpportunities] = useState([]);
  const [financialInsights, setFinancialInsights] = useState(null);
  const [goalProgress, setGoalProgress] = useState(null);
  const [emergencyFund, setEmergencyFund] = useState(null);

  useEffect(() => {
    loadAllAdvice();
  }, []);

  useEffect(() => {
    if (activeTab === 'overview') {
      loadOverview();
    } else if (activeTab === 'budget') {
      loadBudgetSuggestions();
    } else if (activeTab === 'savings') {
      loadSavingsOpportunities();
    } else if (activeTab === 'goals') {
      loadGoals();
    }
  }, [activeTab]);

  const loadAllAdvice = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadHealthScore(),
        loadRecommendations(),
        loadBudgetSuggestions(),
        loadOverspending(),
        loadSavingsOpportunities(),
        loadFinancialInsights(),
        loadGoalProgress(),
        loadEmergencyFund()
      ]);
    } catch (error) {
      toast.error('Failed to load financial advice');
    } finally {
      setLoading(false);
    }
  };

  const loadOverview = async () => {
    try {
      await Promise.all([
        loadHealthScore(),
        loadRecommendations(),
        loadFinancialInsights()
      ]);
    } catch (error) {
      console.error('Failed to load overview:', error);
    }
  };

  const loadHealthScore = async () => {
    try {
      const data = await adviceService.getHealthScore();
      setHealthScore(data);
    } catch (error) {
      console.error('Failed to load health score:', error);
    }
  };

  const loadRecommendations = async () => {
    try {
      const data = await adviceService.getRecommendations();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  };

  const loadBudgetSuggestions = async () => {
    try {
      const data = await adviceService.getBudgetSuggestions();
      setBudgetSuggestions(data);
    } catch (error) {
      console.error('Failed to load budget suggestions:', error);
    }
  };

  const loadOverspending = async () => {
    try {
      const data = await adviceService.getOverspending();
      setOverspending(data.overspending_categories || []);
    } catch (error) {
      console.error('Failed to load overspending:', error);
    }
  };

  const loadSavingsOpportunities = async () => {
    try {
      const data = await adviceService.getSavingsOpportunities();
      setSavingsOpportunities(data.opportunities || []);
    } catch (error) {
      console.error('Failed to load savings opportunities:', error);
    }
  };

  const loadFinancialInsights = async () => {
    try {
      const data = await adviceService.getFinancialInsights();
      setFinancialInsights(data);
    } catch (error) {
      console.error('Failed to load financial insights:', error);
    }
  };

  const loadGoalProgress = async () => {
    try {
      const data = await adviceService.getGoalProgress();
      setGoalProgress(data);
    } catch (error) {
      console.error('Failed to load goal progress:', error);
    }
  };

  const loadEmergencyFund = async () => {
    try {
      const data = await adviceService.getEmergencyFundStatus();
      setEmergencyFund(data);
    } catch (error) {
      console.error('Failed to load emergency fund:', error);
    }
  };

  const formatCurrency = (value) => {
  return formatZMK(value);
};

  const getHealthScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    if (score >= 40) return '#ef4444';
    return '#6b7280';
  };

  const getHealthScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  const getPriorityIcon = (priority) => {
    switch(priority) {
      case 'high':
        return <Zap size={16} className="priority-high" />;
      case 'medium':
        return <Clock size={16} className="priority-medium" />;
      case 'low':
        return <Info size={16} className="priority-low" />;
      default:
        return <Info size={16} />;
    }
  };

  const getCategoryIcon = (category) => {
    const categoryLower = category?.toLowerCase() || '';
    
    if (categoryLower.includes('food') || categoryLower.includes('dining')) {
      return <Utensils size={20} />;
    }
    if (categoryLower.includes('shopping')) {
      return <ShoppingBag size={20} />;
    }
    if (categoryLower.includes('transport') || categoryLower.includes('car')) {
      return <Car size={20} />;
    }
    if (categoryLower.includes('home') || categoryLower.includes('rent')) {
      return <Home size={20} />;
    }
    if (categoryLower.includes('gift') || categoryLower.includes('donation')) {
      return <Gift size={20} />;
    }
    if (categoryLower.includes('coffee')) {
      return <Coffee size={20} />;
    }
    return <DollarSign size={20} />;
  };

  return (
    <div className="advice-container">
      <div className="advice-header">
        <h1 className="page-title">Financial Advice</h1>
        
        <div className="header-greeting">
          <Heart size={20} className="heart-icon" />
          <span>Hello, {user?.username}! Here's your personalized financial advice</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="advice-tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Heart size={18} />
          Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'budget' ? 'active' : ''}`}
          onClick={() => setActiveTab('budget')}
        >
          <Target size={18} />
          Budget
        </button>
        <button
          className={`tab-button ${activeTab === 'savings' ? 'active' : ''}`}
          onClick={() => setActiveTab('savings')}
        >
          <PiggyBank size={18} />
          Savings
        </button>
        <button
          className={`tab-button ${activeTab === 'goals' ? 'active' : ''}`}
          onClick={() => setActiveTab('goals')}
        >
          <Award size={18} />
          Goals
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Analyzing your finances...</p>
        </div>
      )}

      {/* Content */}
      {!loading && (
        <div className="advice-content">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="overview-tab">
              {/* Health Score */}
              {healthScore && (
                <div className="health-score-card">
                  <div className="score-circle">
                    <svg viewBox="0 0 120 120" className="score-chart">
                      <circle
                        cx="60"
                        cy="60"
                        r="54"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="12"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="54"
                        fill="none"
                        stroke={getHealthScoreColor(healthScore.score)}
                        strokeWidth="12"
                        strokeDasharray={`${2 * Math.PI * 54 * healthScore.score / 100} ${2 * Math.PI * 54}`}
                        strokeDashoffset={2 * Math.PI * 54 * 0.25}
                        strokeLinecap="round"
                        transform="rotate(-90 60 60)"
                      />
                      <text x="60" y="60" textAnchor="middle" dy="0.3em" className="score-text">
                        {healthScore.score}
                      </text>
                    </svg>
                  </div>
                  <div className="score-info">
                    <h2>{getHealthScoreLabel(healthScore.score)}</h2>
                    <p className="score-rating">{healthScore.rating}</p>
                    <p className="score-description">
                      Your financial health is {healthScore.rating.toLowerCase()}. 
                      Keep up the good work!
                    </p>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {recommendations.length > 0 && (
                <div className="recommendations-section">
                  <h3>Priority Recommendations</h3>
                  <div className="recommendations-list">
                    {recommendations.map((rec, index) => (
                      <div key={index} className={`recommendation-card priority-${rec.priority}`}>
                        <div className="recommendation-header">
                          <div className="recommendation-icon">
                            {getCategoryIcon(rec.category)}
                          </div>
                          <div className="recommendation-title">
                            <h4>{rec.title}</h4>
                            <span className="recommendation-priority">
                              {getPriorityIcon(rec.priority)}
                              {rec.priority} priority
                            </span>
                          </div>
                        </div>
                        <p className="recommendation-message">{rec.message}</p>
                        {rec.suggestion && (
                          <div className="recommendation-suggestion">
                            <Lightbulb size={16} />
                            <span>{rec.suggestion}</span>
                          </div>
                        )}
                        {rec.actionable && (
                          <button className="recommendation-action">
                            {rec.action}
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              {financialInsights && (
                <div className="quick-stats">
                  <h3>Quick Stats</h3>
                  <div className="stats-grid">
                    {financialInsights.summary && (
                      <>
                        <div className="stat-card">
                          <div className="stat-icon income">
                            <TrendingUp size={20} />
                          </div>
                          <div className="stat-info">
                            <span className="stat-label">Monthly Income</span>
                            <span className="stat-value">
                              {formatCurrency(financialInsights.summary.monthly_income)}
                            </span>
                          </div>
                        </div>
                        <div className="stat-card">
                          <div className="stat-icon savings">
                            <PiggyBank size={20} />
                          </div>
                          <div className="stat-info">
                            <span className="stat-label">Emergency Fund</span>
                            <span className="stat-value">
                              {formatCurrency(financialInsights.summary.emergency_fund)}
                            </span>
                          </div>
                        </div>
                      </>
                    )}
                    
                    {financialInsights.next_month_prediction && (
                      <div className="stat-card">
                        <div className="stat-icon prediction">
                          <Clock size={20} />
                        </div>
                        <div className="stat-info">
                          <span className="stat-label">Next Month Prediction</span>
                          <span className="stat-value">
                            {formatCurrency(financialInsights.next_month_prediction.total)}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Budget Tab */}
          {activeTab === 'budget' && (
            <div className="budget-tab">
              {/* 50/30/20 Rule */}
              {budgetSuggestions && (
                <div className="budget-rule-card">
                  <h3>The 50/30/20 Rule</h3>
                  <p className="rule-description">
                    A popular budgeting method: 50% for needs, 30% for wants, and 20% for savings.
                  </p>
                  
                  <div className="rule-visualization">
                    <div className="rule-segment needs" style={{ width: '50%' }}>
                      <span className="segment-label">Needs</span>
                      <span className="segment-value">50%</span>
                    </div>
                    <div className="rule-segment wants" style={{ width: '30%' }}>
                      <span className="segment-label">Wants</span>
                      <span className="segment-value">30%</span>
                    </div>
                    <div className="rule-segment savings" style={{ width: '20%' }}>
                      <span className="segment-label">Savings</span>
                      <span className="segment-value">20%</span>
                    </div>
                  </div>

                  {budgetSuggestions.monthly_income && (
                    <div className="budget-comparison">
                      <h4>Your Budget vs Ideal</h4>
                      
                      <div className="comparison-item">
                        <div className="comparison-label">
                          <span>Needs (Essentials)</span>
                          <span className="ideal-target">Target: {formatCurrency(budgetSuggestions.ideal_budget?.essentials)}</span>
                        </div>
                        <div className="comparison-bar">
                          <div 
                            className="bar-fill needs"
                            style={{ 
                              width: `${(budgetSuggestions.current_spending?.essentials / budgetSuggestions.monthly_income) * 100}%` 
                            }}
                          />
                          <div 
                            className="bar-marker"
                            style={{ left: '50%' }}
                          />
                        </div>
                        <div className="comparison-values">
                          <span className="current">
                            Current: {formatCurrency(budgetSuggestions.current_spending?.essentials)}
                          </span>
                          <span className={`status ${budgetSuggestions.current_spending?.essentials > budgetSuggestions.ideal_budget?.essentials ? 'over' : 'under'}`}>
                            {budgetSuggestions.current_spending?.essentials > budgetSuggestions.ideal_budget?.essentials ? 'Over' : 'Under'}
                          </span>
                        </div>
                      </div>

                      <div className="comparison-item">
                        <div className="comparison-label">
                          <span>Wants (Discretionary)</span>
                          <span className="ideal-target">Target: {formatCurrency(budgetSuggestions.ideal_budget?.wants)}</span>
                        </div>
                        <div className="comparison-bar">
                          <div 
                            className="bar-fill wants"
                            style={{ 
                              width: `${(budgetSuggestions.current_spending?.wants / budgetSuggestions.monthly_income) * 100}%` 
                            }}
                          />
                          <div 
                            className="bar-marker"
                            style={{ left: '30%' }}
                          />
                        </div>
                        <div className="comparison-values">
                          <span className="current">
                            Current: {formatCurrency(budgetSuggestions.current_spending?.wants)}
                          </span>
                          <span className={`status ${budgetSuggestions.current_spending?.wants > budgetSuggestions.ideal_budget?.wants ? 'over' : 'under'}`}>
                            {budgetSuggestions.current_spending?.wants > budgetSuggestions.ideal_budget?.wants ? 'Over' : 'Under'}
                          </span>
                        </div>
                      </div>

                      <div className="comparison-item">
                        <div className="comparison-label">
                          <span>Savings</span>
                          <span className="ideal-target">Target: {formatCurrency(budgetSuggestions.ideal_budget?.savings)}</span>
                        </div>
                        <div className="comparison-bar">
                          <div 
                            className="bar-fill savings"
                            style={{ 
                              width: `${(budgetSuggestions.current_spending?.savings / budgetSuggestions.monthly_income) * 100}%` 
                            }}
                          />
                          <div 
                            className="bar-marker"
                            style={{ left: '20%' }}
                          />
                        </div>
                        <div className="comparison-values">
                          <span className="current">
                            Current: {formatCurrency(budgetSuggestions.current_spending?.savings)}
                          </span>
                          <span className={`status ${budgetSuggestions.current_spending?.savings < budgetSuggestions.ideal_budget?.savings ? 'under' : 'over'}`}>
                            {budgetSuggestions.current_spending?.savings < budgetSuggestions.ideal_budget?.savings ? 'Behind' : 'Ahead'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {budgetSuggestions.adjustments_needed?.length > 0 && (
                    <div className="budget-adjustments">
                      <h4>Suggested Adjustments</h4>
                      {budgetSuggestions.adjustments_needed.map((adj, index) => (
                        <div key={index} className="adjustment-item">
                          <div className="adjustment-header">
                            <span className="adjustment-category">{adj.category}</span>
                            <span className={`adjustment-amount ${adj.excess ? 'negative' : 'positive'}`}>
                              {adj.excess ? `-${formatCurrency(adj.excess)}` : `+${formatCurrency(adj.deficit)}`}
                            </span>
                          </div>
                          <p className="adjustment-suggestion">{adj.suggestion}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Overspending Alert */}
              {overspending.length > 0 && (
                <div className="overspending-section">
                  <h3 className="section-title warning">
                    <AlertCircle size={20} />
                    Overspending Detected
                  </h3>
                  
                  <div className="overspending-list">
                    {overspending.map((item, index) => (
                      <div key={index} className={`overspending-item severity-${item.severity}`}>
                        <div className="overspending-header">
                          <span className="overspending-category">{item.category}</span>
                          <span className="overspending-badge">{item.increase_percentage}% increase</span>
                        </div>
                        <div className="overspending-details">
                          <span>Last month: {formatCurrency(item.previous)}</span>
                          <ArrowUp size={14} className="trend-up" />
                          <span className="current">This month: {formatCurrency(item.current)}</span>
                        </div>
                        <p className="overspending-note">
                          You spent {formatCurrency(item.excess_amount)} more than last month
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Savings Tab */}
          {activeTab === 'savings' && (
            <div className="savings-tab">
              {/* Emergency Fund */}
              {emergencyFund && (
                <div className="emergency-fund-card">
                  <h3>
                    <Shield size={20} />
                    Emergency Fund
                  </h3>
                  
                  <div className="fund-progress">
                    <div className="fund-circle">
                      <svg viewBox="0 0 120 120" className="fund-chart">
                        <circle
                          cx="60"
                          cy="60"
                          r="54"
                          fill="none"
                          stroke="#e5e7eb"
                          strokeWidth="12"
                        />
                        <circle
                          cx="60"
                          cy="60"
                          r="54"
                          fill="none"
                          stroke={emergencyFund.months_covered >= emergencyFund.target_months ? '#10b981' : '#f59e0b'}
                          strokeWidth="12"
                          strokeDasharray={`${2 * Math.PI * 54 * Math.min(emergencyFund.months_covered / emergencyFund.target_months, 1)} ${2 * Math.PI * 54}`}
                          strokeDashoffset={2 * Math.PI * 54 * 0.25}
                          strokeLinecap="round"
                          transform="rotate(-90 60 60)"
                        />
                        <text x="60" y="60" textAnchor="middle" dy="0.3em" className="fund-text">
                          {emergencyFund.months_covered.toFixed(1)}mo
                        </text>
                      </svg>
                    </div>
                    
                    <div className="fund-details">
                      <div className="fund-stat">
                        <span>Current:</span>
                        <strong>{formatCurrency(emergencyFund.current_amount)}</strong>
                      </div>
                      <div className="fund-stat">
                        <span>Target ({emergencyFund.target_months} months):</span>
                        <strong>{formatCurrency(emergencyFund.target_amount)}</strong>
                      </div>
                      <div className="fund-status">
                        Status: 
                        <span className={`status-badge ${emergencyFund.status}`}>
                          {emergencyFund.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Savings Opportunities */}
              {savingsOpportunities.length > 0 && (
                <div className="opportunities-section">
                  <h3>
                    <PiggyBank size={20} />
                    Savings Opportunities
                  </h3>
                  
                  <div className="opportunities-grid">
                    {savingsOpportunities.map((opp, index) => (
                      <div key={index} className={`opportunity-card type-${opp.type}`}>
                        <div className="opportunity-header">
                          {opp.type === 'subscription' ? (
                            <Clock size={20} className="opportunity-icon" />
                          ) : (
                            <TrendingDown size={20} className="opportunity-icon" />
                          )}
                          <h4>{opp.type === 'subscription' ? 'Subscription' : 'High Spending'}</h4>
                        </div>
                        
                        <div className="opportunity-details">
                          {opp.description && (
                            <p className="opportunity-description">{opp.description}</p>
                          )}
                          {opp.category && (
                            <p className="opportunity-category">{opp.category}</p>
                          )}
                          
                          <div className="opportunity-savings">
                            {opp.monthly_cost && (
                              <div className="saving-item">
                                <span>Monthly:</span>
                                <strong>{formatCurrency(opp.monthly_cost)}</strong>
                              </div>
                            )}
                            {opp.annual_cost && (
                              <div className="saving-item">
                                <span>Annual:</span>
                                <strong>{formatCurrency(opp.annual_cost)}</strong>
                              </div>
                            )}
                            {opp.monthly_avg && (
                              <div className="saving-item">
                                <span>Monthly avg:</span>
                                <strong>{formatCurrency(opp.monthly_avg)}</strong>
                              </div>
                            )}
                          </div>
                          
                          <p className="opportunity-suggestion">{opp.suggestion}</p>
                        </div>
                        
                        <button className="opportunity-action">
                          Review
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Goals Tab */}
          {activeTab === 'goals' && (
            <div className="goals-tab">
              {/* Savings Goal */}
              {goalProgress && (
                <div className="goal-card">
                  <h3>
                    <Target size={20} />
                    Savings Goal
                  </h3>
                  
                  <div className="goal-progress">
                    <div className="progress-circle">
                      <svg viewBox="0 0 120 120" className="progress-chart">
                        <circle
                          cx="60"
                          cy="60"
                          r="54"
                          fill="none"
                          stroke="#e5e7eb"
                          strokeWidth="12"
                        />
                        <circle
                          cx="60"
                          cy="60"
                          r="54"
                          fill="none"
                          stroke="#10b981"
                          strokeWidth="12"
                          strokeDasharray={`${2 * Math.PI * 54 * goalProgress.progress_percentage / 100} ${2 * Math.PI * 54}`}
                          strokeDashoffset={2 * Math.PI * 54 * 0.25}
                          strokeLinecap="round"
                          transform="rotate(-90 60 60)"
                        />
                        <text x="60" y="60" textAnchor="middle" dy="0.3em" className="progress-text">
                          {goalProgress.progress_percentage}%
                        </text>
                      </svg>
                    </div>
                    
                    <div className="goal-details">
                      <div className="goal-stat">
                        <span>Goal:</span>
                        <strong>{formatCurrency(goalProgress.goal_amount)}</strong>
                      </div>
                      <div className="goal-stat">
                        <span>Current:</span>
                        <strong>{formatCurrency(goalProgress.current_amount)}</strong>
                      </div>
                      <div className="goal-stat">
                        <span>Remaining:</span>
                        <strong>{formatCurrency(goalProgress.remaining)}</strong>
                      </div>
                      
                      {goalProgress.months_to_goal !== 'N/A' && (
                        <div className="goal-timeline">
                          <Clock size={16} />
                          <span>{goalProgress.months_to_goal} months to goal</span>
                        </div>
                      )}
                      
                      <div className="goal-status">
                        <span className={`status-badge ${goalProgress.on_track ? 'on-track' : 'off-track'}`}>
                          {goalProgress.on_track ? 'On Track' : 'Off Track'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Goal Setting Form */}
              {(!user?.profile?.savings_goal || user?.profile?.savings_goal === 0) && (
                <div className="goal-setup-card">
                  <h4>Set a Savings Goal</h4>
                  <p>Setting a goal helps you stay motivated and track your progress.</p>
                  
                  <button 
                    className="btn btn-primary"
                    onClick={() => window.location.href = '/profile'}
                  >
                    Set Goal in Profile
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Advice;