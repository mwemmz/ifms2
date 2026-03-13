import React, { useState, useEffect, useRef } from 'react';
import {
  Bar,
  Line,
  Pie
} from 'react-chartjs-2';
import {
  FileText,
  Download,
  Calendar,
  PieChart,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Filter,
  Printer,
  FileJson,
  FileSpreadsheet,
  File,
  AlertCircle,
  CheckCircle,
  Info,
  Award,
  Clock,
  ChevronLeft,
  ChevronRight,
  RefreshCw
} from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import html2canvas from 'html2canvas';
import reportsService from '../../services/reports';
import toast from 'react-hot-toast';
import { formatZMK } from '../../utils/currency';
import './Reports.css';

const Reports = () => {
  const [loading, setLoading] = useState(false);
  const [activeReport, setActiveReport] = useState('monthly');
  const [availableReports, setAvailableReports] = useState(null);
  const [monthlyReport, setMonthlyReport] = useState(null);
  const [yearlyReport, setYearlyReport] = useState(null);
  const [categoryReport, setCategoryReport] = useState(null);
  const [yearComparison, setYearComparison] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  });
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedCategory, setSelectedCategory] = useState('');
  const [compareYears, setCompareYears] = useState({
    year1: new Date().getFullYear() - 1,
    year2: new Date().getFullYear()
  });
  const [categories, setCategories] = useState([]);
  const [exportFormat, setExportFormat] = useState('json');
  
  const reportRef = useRef(null);

  useEffect(() => {
    loadAvailableReports();
  }, []);

  useEffect(() => {
    if (activeReport === 'monthly') {
      loadMonthlyReport();
    } else if (activeReport === 'yearly') {
      loadYearlyReport();
    } else if (activeReport === 'category') {
      loadCategoryReport();
    } else if (activeReport === 'compare') {
      loadYearComparison();
    }
  }, [activeReport, selectedMonth, selectedYear, selectedCategory, compareYears]);

  const loadAvailableReports = async () => {
    try {
      const data = await reportsService.getAvailableReports();
      setAvailableReports(data);
      setCategories(data.available_categories || []);
    } catch (error) {
      toast.error('Failed to load available reports');
    }
  };

  const loadMonthlyReport = async () => {
    setLoading(true);
    try {
      const data = await reportsService.getMonthlyReport({
        month: selectedMonth.month,
        year: selectedMonth.year
      });
      setMonthlyReport(data);
    } catch (error) {
      toast.error('Failed to load monthly report');
    } finally {
      setLoading(false);
    }
  };

  const loadYearlyReport = async () => {
    setLoading(true);
    try {
      const data = await reportsService.getYearlyReport({
        year: selectedYear
      });
      setYearlyReport(data);
    } catch (error) {
      toast.error('Failed to load yearly report');
    } finally {
      setLoading(false);
    }
  };

  const loadCategoryReport = async () => {
    if (!selectedCategory) return;
    
    setLoading(true);
    try {
      const data = await reportsService.getCategoryReport({
        category: selectedCategory,
        months: 6
      });
      setCategoryReport(data);
    } catch (error) {
      toast.error('Failed to load category report');
    } finally {
      setLoading(false);
    }
  };

  const loadYearComparison = async () => {
    setLoading(true);
    try {
      const data = await reportsService.compareYears({
        year1: compareYears.year1,
        year2: compareYears.year2
      });
      setYearComparison(data);
    } catch (error) {
      toast.error('Failed to load year comparison');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      let data;
      let filename;
      
      switch (exportFormat) {
        case 'json':
          if (activeReport === 'monthly') data = monthlyReport;
          else if (activeReport === 'yearly') data = yearlyReport;
          else if (activeReport === 'category') data = categoryReport;
          else if (activeReport === 'compare') data = yearComparison;
          
          filename = `${activeReport}_report_${new Date().toISOString().split('T')[0]}.json`;
          const jsonBlob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          const jsonUrl = window.URL.createObjectURL(jsonBlob);
          const jsonLink = document.createElement('a');
          jsonLink.href = jsonUrl;
          jsonLink.download = filename;
          jsonLink.click();
          window.URL.revokeObjectURL(jsonUrl);
          break;
          
        case 'csv':
          await exportToCSV();
          break;
          
        case 'pdf':
          await exportToPDF();
          break;
      }
      
      toast.success(`Report exported as ${exportFormat.toUpperCase()}`);
    } catch (error) {
      toast.error('Failed to export report');
    }
  };

  const exportToCSV = () => {
    // Implementation for CSV export
    let csvContent = '';
    
    if (activeReport === 'monthly' && monthlyReport) {
      // Monthly report CSV
      const headers = ['Category', 'Amount', 'Percentage', 'Transactions'];
      const rows = Object.entries(monthlyReport.category_breakdown || {}).map(([cat, data]) => [
        cat,
        data.total,
        data.percentage + '%',
        data.transaction_count
      ]);
      
      csvContent = [
        [`Monthly Report - ${monthlyReport.period?.month} ${monthlyReport.period?.year}`],
        ['Summary'],
        ['Total Income', monthlyReport.summary?.total_income],
        ['Total Expenses', monthlyReport.summary?.total_expenses],
        ['Net Savings', monthlyReport.summary?.net_savings],
        ['Savings Rate', monthlyReport.summary?.savings_rate + '%'],
        [],
        ['Category Breakdown'],
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeReport}_report_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const exportToPDF = async () => {
    if (!reportRef.current) return;
    
    try {
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        logging: false,
        backgroundColor: '#ffffff'
      });
      
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'px',
        format: [canvas.width * 0.75, canvas.height * 0.75]
      });
      
      pdf.addImage(imgData, 'PNG', 0, 0, canvas.width * 0.75, canvas.height * 0.75);
      pdf.save(`${activeReport}_report_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (error) {
      console.error('PDF export failed:', error);
      toast.error('Failed to export PDF');
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const formatCurrency = (value) => {
  return formatZMK(value);
};
  const formatPercentage = (value) => {
    return `${value?.toFixed(1) || 0}%`;
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i + 1);

  // Chart configurations
  const getMonthlyCategoryData = () => {
    if (!monthlyReport?.category_breakdown) return null;

    const categories = Object.entries(monthlyReport.category_breakdown)
      .sort((a, b) => b[1].total - a[1].total)
      .slice(0, 8);

    return {
      labels: categories.map(([cat]) => cat),
      datasets: [
        {
          label: 'Amount',
          data: categories.map(([, data]) => data.total),
          backgroundColor: [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
            '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
          ],
          borderWidth: 1
        }
      ]
    };
  };

  const getYearlyTrendData = () => {
    if (!yearlyReport?.monthly_breakdown) return null;

    return {
      labels: yearlyReport.monthly_breakdown.map(m => m.month),
      datasets: [
        {
          label: 'Income',
          data: yearlyReport.monthly_breakdown.map(m => m.income),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: false
        },
        {
          label: 'Expenses',
          data: yearlyReport.monthly_breakdown.map(m => m.expenses),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          fill: false
        }
      ]
    };
  };

  const getCategoryMonthlyData = () => {
    if (!categoryReport?.monthly_breakdown) return null;

    return {
      labels: categoryReport.monthly_breakdown.map(m => m.month),
      datasets: [
        {
          label: 'Monthly Spending',
          data: categoryReport.monthly_breakdown.map(m => m.total),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    };
  };

  const getComparisonChartData = () => {
    if (!yearComparison?.category_comparison) return null;

    const categories = yearComparison.category_comparison.slice(0, 8);
    
    return {
      labels: categories.map(c => c.category),
      datasets: [
        {
          label: `Year ${compareYears.year1}`,
          data: categories.map(c => c.year1),
          backgroundColor: 'rgba(156, 163, 175, 0.5)',
          borderColor: '#6b7280',
          borderWidth: 1
        },
        {
          label: `Year ${compareYears.year2}`,
          data: categories.map(c => c.year2),
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
        position: 'bottom'
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
    <div className="reports-container">
      <div className="reports-header">
        <h1 className="page-title">Financial Reports</h1>
        
        <div className="header-actions">
          <div className="export-format">
            <select 
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              className="format-select"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="pdf">PDF</option>
            </select>
          </div>
          
          <button className="btn btn-outline" onClick={handleExport}>
            <Download size={18} />
            Export
          </button>
          
          <button className="btn btn-outline" onClick={handlePrint}>
            <Printer size={18} />
            Print
          </button>
        </div>
      </div>

      {/* Report Type Selector */}
      <div className="report-types">
        <button
          className={`type-button ${activeReport === 'monthly' ? 'active' : ''}`}
          onClick={() => setActiveReport('monthly')}
        >
          <Calendar size={18} />
          Monthly Report
        </button>
        <button
          className={`type-button ${activeReport === 'yearly' ? 'active' : ''}`}
          onClick={() => setActiveReport('yearly')}
        >
          <FileText size={18} />
          Yearly Report
        </button>
        <button
          className={`type-button ${activeReport === 'category' ? 'active' : ''}`}
          onClick={() => setActiveReport('category')}
        >
          <PieChart size={18} />
          Category Report
        </button>
        <button
          className={`type-button ${activeReport === 'compare' ? 'active' : ''}`}
          onClick={() => setActiveReport('compare')}
        >
          <TrendingUp size={18} />
          Year Comparison
        </button>
      </div>

      {/* Report Filters */}
      <div className="report-filters">
        {activeReport === 'monthly' && (
          <div className="filter-group">
            <Calendar size={18} className="filter-icon" />
            <select
              className="filter-select"
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
            <select
              className="filter-select"
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
        )}

        {activeReport === 'yearly' && (
          <div className="filter-group">
            <Calendar size={18} className="filter-icon" />
            <select
              className="filter-select"
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            >
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        )}

        {activeReport === 'category' && (
          <div className="filter-group">
            <PieChart size={18} className="filter-icon" />
            <select
              className="filter-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">Select a category</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        )}

        {activeReport === 'compare' && (
          <div className="filter-group compare-group">
            <div className="compare-input">
              <span>Year 1:</span>
              <select
                value={compareYears.year1}
                onChange={(e) => setCompareYears(prev => ({ 
                  ...prev, 
                  year1: parseInt(e.target.value) 
                }))}
              >
                {years.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
            <div className="compare-input">
              <span>Year 2:</span>
              <select
                value={compareYears.year2}
                onChange={(e) => setCompareYears(prev => ({ 
                  ...prev, 
                  year2: parseInt(e.target.value) 
                }))}
              >
                {years.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Generating report...</p>
        </div>
      )}

      {/* Report Content */}
      {!loading && (
        <div className="report-content" ref={reportRef}>
          {/* Monthly Report */}
          {activeReport === 'monthly' && monthlyReport && (
            <div className="report-section">
              <div className="report-header">
                <h2>Monthly Financial Report</h2>
                <p className="report-period">
                  {monthlyReport.period?.month} {monthlyReport.period?.year}
                </p>
                <p className="report-generated">
                  Generated: {new Date(monthlyReport.generated_at).toLocaleString()}
                </p>
              </div>

              {/* Summary Cards */}
              <div className="summary-cards">
                <div className="summary-card">
                  <h3>Total Income</h3>
                  <p className="summary-value income">
                    {formatCurrency(monthlyReport.summary?.total_income)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Total Expenses</h3>
                  <p className="summary-value expense">
                    {formatCurrency(monthlyReport.summary?.total_expenses)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Net Savings</h3>
                  <p className={`summary-value ${monthlyReport.summary?.net_savings >= 0 ? 'income' : 'expense'}`}>
                    {formatCurrency(monthlyReport.summary?.net_savings)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Savings Rate</h3>
                  <p className="summary-value">
                    {monthlyReport.summary?.savings_rate}%
                  </p>
                </div>
              </div>

              {/* Category Breakdown */}
              <div className="report-row">
                <div className="report-chart">
                  <h3>Spending by Category</h3>
                  {getMonthlyCategoryData() && (
                    <div className="chart-container">
                      <Pie data={getMonthlyCategoryData()} options={pieOptions} />
                    </div>
                  )}
                </div>

                <div className="report-table">
                  <h3>Category Details</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Category</th>
                        <th>Amount</th>
                        <th>%</th>
                        <th>Transactions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(monthlyReport.category_breakdown || {}).map(([category, data]) => (
                        <tr key={category}>
                          <td>{category}</td>
                          <td>{formatCurrency(data.total)}</td>
                          <td>{data.percentage}%</td>
                          <td>{data.transaction_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Insights */}
              {monthlyReport.insights && monthlyReport.insights.length > 0 && (
                <div className="insights-section">
                  <h3>Key Insights</h3>
                  <div className="insights-list">
                    {monthlyReport.insights.map((insight, index) => (
                      <div key={index} className="insight-item">
                        <Info size={16} />
                        <span>{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Daily Spending */}
              {monthlyReport.daily_spending && (
                <div className="daily-spending">
                  <h3>Daily Spending Pattern</h3>
                  <div className="spending-grid">
                    {monthlyReport.daily_spending.map((day, index) => (
                      <div key={index} className="day-item">
                        <span className="day">Day {day.day}</span>
                        <span className="amount">{formatCurrency(day.amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Yearly Report */}
          {activeReport === 'yearly' && yearlyReport && (
            <div className="report-section">
              <div className="report-header">
                <h2>Yearly Financial Report</h2>
                <p className="report-period">{yearlyReport.period?.year}</p>
                <p className="report-generated">
                  Generated: {new Date(yearlyReport.generated_at).toLocaleString()}
                </p>
              </div>

              {/* Yearly Summary */}
              <div className="summary-cards">
                <div className="summary-card">
                  <h3>Total Income</h3>
                  <p className="summary-value income">
                    {formatCurrency(yearlyReport.summary?.total_income)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Total Expenses</h3>
                  <p className="summary-value expense">
                    {formatCurrency(yearlyReport.summary?.total_expenses)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Total Savings</h3>
                  <p className={`summary-value ${yearlyReport.summary?.total_savings >= 0 ? 'income' : 'expense'}`}>
                    {formatCurrency(yearlyReport.summary?.total_savings)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Avg Monthly</h3>
                  <p className="summary-value">
                    {formatCurrency(yearlyReport.summary?.avg_monthly_expense)}
                  </p>
                </div>
              </div>

              {/* Monthly Trend */}
              {getYearlyTrendData() && (
                <div className="report-chart full-width">
                  <h3>Monthly Income vs Expenses</h3>
                  <div className="chart-container">
                    <Line data={getYearlyTrendData()} options={lineOptions} />
                  </div>
                </div>
              )}

              {/* Monthly Breakdown */}
              <div className="report-table">
                <h3>Monthly Breakdown</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Income</th>
                      <th>Expenses</th>
                      <th>Savings</th>
                      <th>Transactions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {yearlyReport.monthly_breakdown?.map((month, index) => (
                      <tr key={index}>
                        <td>{month.month}</td>
                        <td>{formatCurrency(month.income)}</td>
                        <td>{formatCurrency(month.expenses)}</td>
                        <td className={month.savings >= 0 ? 'positive' : 'negative'}>
                          {formatCurrency(month.savings)}
                        </td>
                        <td>{month.transaction_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Yearly Insights */}
              {yearlyReport.insights && yearlyReport.insights.length > 0 && (
                <div className="insights-section">
                  <h3>Year in Review</h3>
                  <div className="insights-list">
                    {yearlyReport.insights.map((insight, index) => (
                      <div key={index} className="insight-item">
                        <Award size={16} />
                        <span>{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Category Report */}
          {activeReport === 'category' && categoryReport && (
            <div className="report-section">
              <div className="report-header">
                <h2>Category Report: {categoryReport.category}</h2>
                <p className="report-period">Last 6 Months</p>
                <p className="report-generated">
                  Generated: {new Date().toLocaleString()}
                </p>
              </div>

              {/* Category Summary */}
              <div className="summary-cards">
                <div className="summary-card">
                  <h3>Total Spent</h3>
                  <p className="summary-value">
                    {formatCurrency(categoryReport.summary?.total_spent)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Monthly Average</h3>
                  <p className="summary-value">
                    {formatCurrency(categoryReport.summary?.average_monthly)}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Total Transactions</h3>
                  <p className="summary-value">
                    {categoryReport.summary?.total_transactions}
                  </p>
                </div>
                <div className="summary-card">
                  <h3>Trend</h3>
                  <p className={`summary-value trend-${categoryReport.summary?.trend}`}>
                    {categoryReport.summary?.trend === 'increasing' ? (
                      <><TrendingUp /> Increasing</>
                    ) : categoryReport.summary?.trend === 'decreasing' ? (
                      <><TrendingDown /> Decreasing</>
                    ) : (
                      'Stable'
                    )}
                  </p>
                </div>
              </div>

              {/* Monthly Trend */}
              {getCategoryMonthlyData() && (
                <div className="report-chart full-width">
                  <h3>Monthly Spending Trend</h3>
                  <div className="chart-container">
                    <Line data={getCategoryMonthlyData()} options={lineOptions} />
                  </div>
                </div>
              )}

              {/* Monthly Breakdown */}
              <div className="report-table">
                <h3>Monthly Details</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Amount</th>
                      <th>Transactions</th>
                      <th>Average</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryReport.monthly_breakdown?.map((month, index) => (
                      <tr key={index}>
                        <td>{month.month}</td>
                        <td>{formatCurrency(month.total)}</td>
                        <td>{month.count}</td>
                        <td>{formatCurrency(month.average)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Recent Transactions */}
              {categoryReport.monthly_breakdown?.[0]?.transactions && (
                <div className="recent-transactions">
                  <h3>Recent Transactions</h3>
                  <div className="transaction-list">
                    {categoryReport.monthly_breakdown[0].transactions.map((t, index) => (
                      <div key={index} className="transaction-item">
                        <span className="transaction-date">{t.date}</span>
                        <span className="transaction-desc">{t.description}</span>
                        <span className="transaction-amount">{formatCurrency(t.amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Category Advice */}
              {categoryReport.advice && (
                <div className="advice-box">
                  <Info size={20} />
                  <p>{categoryReport.advice}</p>
                </div>
              )}
            </div>
          )}

          {/* Year Comparison */}
          {activeReport === 'compare' && yearComparison && (
            <div className="report-section">
              <div className="report-header">
                <h2>Year Comparison: {compareYears.year1} vs {compareYears.year2}</h2>
                <p className="report-generated">
                  Generated: {new Date().toLocaleString()}
                </p>
              </div>

              {/* Comparison Summary */}
              <div className="comparison-summary">
                <div className={`comparison-card ${yearComparison.comparison?.expenses_change?.trend === 'down' ? 'positive' : 'negative'}`}>
                  <h3>Expense Change</h3>
                  <p className="comparison-value">
                    {yearComparison.comparison?.expenses_change?.percentage > 0 ? '+' : ''}
                    {yearComparison.comparison?.expenses_change?.percentage}%
                  </p>
                  <p className="comparison-absolute">
                    {formatCurrency(Math.abs(yearComparison.comparison?.expenses_change?.absolute))}
                  </p>
                </div>
                
                <div className={`comparison-card ${yearComparison.comparison?.income_change?.trend === 'up' ? 'positive' : 'negative'}`}>
                  <h3>Income Change</h3>
                  <p className="comparison-value">
                    {yearComparison.comparison?.income_change?.percentage > 0 ? '+' : ''}
                    {yearComparison.comparison?.income_change?.percentage}%
                  </p>
                  <p className="comparison-absolute">
                    {formatCurrency(Math.abs(yearComparison.comparison?.income_change?.absolute))}
                  </p>
                </div>
                
                <div className={`comparison-card ${yearComparison.comparison?.savings_change?.trend === 'up' ? 'positive' : 'negative'}`}>
                  <h3>Savings Change</h3>
                  <p className="comparison-value">
                    {yearComparison.comparison?.savings_change?.percentage > 0 ? '+' : ''}
                    {yearComparison.comparison?.savings_change?.percentage}%
                  </p>
                  <p className="comparison-absolute">
                    {formatCurrency(Math.abs(yearComparison.comparison?.savings_change?.absolute))}
                  </p>
                </div>
              </div>

              {/* Category Comparison Chart */}
              {getComparisonChartData() && (
                <div className="report-chart full-width">
                  <h3>Category Comparison</h3>
                  <div className="chart-container">
                    <Bar data={getComparisonChartData()} options={barOptions} />
                  </div>
                </div>
              )}

              {/* Monthly Comparison */}
              <div className="report-table">
                <h3>Monthly Comparison</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>{compareYears.year1} Expenses</th>
                      <th>{compareYears.year2} Expenses</th>
                      <th>Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {yearComparison.monthly_comparison?.map((month, index) => {
                      const change = month.year2_expenses - month.year1_expenses;
                      return (
                        <tr key={index}>
                          <td>{month.month}</td>
                          <td>{formatCurrency(month.year1_expenses)}</td>
                          <td>{formatCurrency(month.year2_expenses)}</td>
                          <td className={change >= 0 ? 'negative' : 'positive'}>
                            {change >= 0 ? '+' : ''}{formatCurrency(change)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Category Changes */}
              <div className="report-table">
                <h3>Category Changes</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>{compareYears.year1}</th>
                      <th>{compareYears.year2}</th>
                      <th>Change</th>
                      <th>%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {yearComparison.category_comparison?.map((item, index) => (
                      <tr key={index}>
                        <td>{item.category}</td>
                        <td>{formatCurrency(item.year1)}</td>
                        <td>{formatCurrency(item.year2)}</td>
                        <td className={item.change >= 0 ? 'negative' : 'positive'}>
                          {item.change >= 0 ? '+' : ''}{formatCurrency(item.change)}
                        </td>
                        <td className={item.change_percentage >= 0 ? 'negative' : 'positive'}>
                          {item.change_percentage >= 0 ? '+' : ''}{item.change_percentage}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Reports;