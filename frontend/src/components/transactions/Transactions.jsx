import React, { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Filter,
  Download,
  Edit,
  Trash2,
  Calendar,
  DollarSign,
  Tag,
  FileText,
  X,
  ChevronLeft,
  ChevronRight,
  RefreshCw
} from 'lucide-react';
import transactionService from '../../services/transaction';
import toast from 'react-hot-toast';
import './Transactions.css';
import { format } from 'date-fns';
import { formatZMK } from '../../utils/currency';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState({ expense: [], income: [] });
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [filters, setFilters] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    category: '',
    type: '',
    search: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    hasMore: false
  });
  const [summary, setSummary] = useState(null);
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    description: '',
    date: format(new Date(), 'yyyy-MM-dd')
  });
  const [formErrors, setFormErrors] = useState({});
  const [categorySuggestions, setCategorySuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Add body scroll lock effect
  useEffect(() => {
    if (showModal) {
      document.body.classList.add('modal-open');
    } else {
      document.body.classList.remove('modal-open');
    }
    
    return () => {
      document.body.classList.remove('modal-open');
    };
  }, [showModal]);

  useEffect(() => {
    loadCategories();
    loadTransactions();
    loadSummary();
  }, []);

  useEffect(() => {
    loadTransactions();
    loadSummary();
  }, [filters.month, filters.year, filters.category, filters.type]);

  // Update category suggestions when user types
  useEffect(() => {
    if (formData.category && formData.category.length > 1) {
      const allCategories = [...(categories.expense || []), ...(categories.income || [])];
      const filtered = allCategories.filter(cat => 
        cat.toLowerCase().includes(formData.category.toLowerCase())
      );
      setCategorySuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setCategorySuggestions([]);
      setShowSuggestions(false);
    }
  }, [formData.category, categories]);

  const loadCategories = async () => {
    try {
      const data = await transactionService.getCategories();
      setCategories(data);
    } catch (error) {
      toast.error('Failed to load categories');
    }
  };

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const params = {
        month: filters.month,
        year: filters.year,
        ...(filters.category ? { category: filters.category } : {}),
        ...(filters.type ? { type: filters.type } : {}),
        ...(filters.search ? { search: filters.search } : {}),
        limit: pagination.limit,
        offset: (pagination.page - 1) * pagination.limit
      };
      const data = await transactionService.getTransactions(params);
      setTransactions(data.transactions || []);
      setPagination(prev => ({
        ...prev,
        total: data.pagination?.total || 0,
        hasMore: data.pagination?.has_more || false
      }));
    } catch (error) {
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const data = await transactionService.getSummary({
        month: filters.month,
        year: filters.year
      });
      setSummary(data);
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  };

  const handleSearch = (e) => {
    const value = e.target.value;
    setFilters(prev => ({ ...prev, search: value }));
  };

  // Use transactions directly from backend, since search is now handled server-side
  const filteredTransactions = transactions;

  const handlePrevPage = () => {
    if (pagination.page > 1) {
      setPagination(prev => ({ ...prev, page: prev.page - 1 }));
      loadTransactions();
    }
  };

  const handleNextPage = () => {
    if (pagination.hasMore) {
      setPagination(prev => ({ ...prev, page: prev.page + 1 }));
      loadTransactions();
    }
  };

  const handleAddTransaction = () => {
    setEditingTransaction(null);
    setFormData({
      amount: '',
      category: '',
      description: '',
      date: format(new Date(), 'yyyy-MM-dd')
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleEditTransaction = (transaction) => {
    setEditingTransaction(transaction);
    setFormData({
      amount: Math.abs(transaction.amount).toString(),
      category: transaction.category,
      description: transaction.description || '',
      date: transaction.date
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleDeleteTransaction = async (id) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) {
      return;
    }

    try {
      await transactionService.deleteTransaction(id);
      toast.success('Transaction deleted successfully');
      loadTransactions();
      loadSummary();
    } catch (error) {
      toast.error('Failed to delete transaction');
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      errors.amount = 'Please enter a valid amount';
    }
    
    if (!formData.category || formData.category.trim() === '') {
      errors.category = 'Please enter a category';
    }
    
    if (!formData.date) {
      errors.date = 'Please select a date';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      const transactionData = {
        amount: parseFloat(formData.amount),
        category: formData.category.trim(),
        description: formData.description || '',
        date: formData.date
      };
      
      // Log the exact data being sent
      console.log('=== SENDING TRANSACTION ===');
      console.log('Raw formData:', formData);
      console.log('Processed transactionData:', transactionData);
      console.log('JSON stringified:', JSON.stringify(transactionData, null, 2));
      
      if (editingTransaction) {
        await transactionService.updateTransaction(editingTransaction.id, transactionData);
        toast.success('Transaction updated successfully');
      } else {
        await transactionService.createTransaction(transactionData);
        toast.success('Transaction added successfully');
      }
      
      setShowModal(false);
      loadTransactions();
      loadSummary();
    } catch (error) {
      console.error('=== ERROR DETAILS ===');
      console.error('Error object:', error);
      console.error('Response data:', error.response?.data);
      console.error('Response status:', error.response?.status);
      console.error('Response headers:', error.response?.headers);
      
      // Show the specific error message
      const errorMsg = error.response?.data?.errors?.join(', ') || 
                       error.response?.data?.error || 
                       'Failed to save transaction';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    // Create CSV content
    const headers = ['Date', 'Description', 'Category', 'Amount (ZMW)', 'Type'];
    const rows = transactions.map(t => [
      t.date,
      t.description || '',
      t.category,
      Math.abs(t.amount).toFixed(2),
      t.type
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transactions_${filters.month}_${filters.year}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    toast.success('Transactions exported successfully');
  };

  const handleSuggestionClick = (suggestion) => {
    setFormData({ ...formData, category: suggestion });
    setShowSuggestions(false);
  };

  const formatCurrency = (value) => {
    return formatZMK(value);
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  return (
    <div className="transactions-container">
      <div className="transactions-header">
        <h1 className="page-title">Transactions</h1>
        <div className="header-actions">
          <button className="btn btn-outline" onClick={handleExport}>
            <Download size={18} />
            Export
          </button>
          <button className="btn btn-primary" onClick={handleAddTransaction}>
            <Plus size={18} />
            Add Transaction
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="summary-cards">
          <div className="summary-card">
            <h3>Total Income</h3>
            <p className="summary-amount income">
              {formatCurrency(summary.summary?.total_income || 0)}
            </p>
          </div>
          
          <div className="summary-card">
            <h3>Total Expenses</h3>
            <p className="summary-amount expense">
              {formatCurrency(summary.summary?.total_expenses || 0)}
            </p>
          </div>
          
          <div className="summary-card">
            <h3>Net Savings</h3>
            <p className={`summary-amount ${(summary.summary?.net_savings || 0) >= 0 ? 'income' : 'expense'}`}>
              {formatCurrency(summary.summary?.net_savings || 0)}
            </p>
          </div>
          
          <div className="summary-card">
            <h3>Transactions</h3>
            <p className="summary-amount">
              {summary.summary?.transaction_count || 0}
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <div className="filters-row">
          <div className="filter-group">
            <Calendar size={18} className="filter-icon" />
            <select
              className="filter-select"
              value={filters.month}
              onChange={(e) => setFilters(prev => ({ ...prev, month: parseInt(e.target.value) }))}
            >
              {months.map((month, index) => (
                <option key={index} value={index + 1}>{month}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <select
              className="filter-select"
              value={filters.year}
              onChange={(e) => setFilters(prev => ({ ...prev, year: parseInt(e.target.value) }))}
            >
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <Filter size={18} className="filter-icon" />
            <select
              className="filter-select"
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
            >
              <option value="">All Categories</option>
              {categories.expense?.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
              {categories.income?.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <select
              className="filter-select"
              value={filters.type}
              onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
            >
              <option value="">All Types</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
          </div>

          <div className="search-group">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search transactions..."
              value={filters.search}
              onChange={handleSearch}
            />
          </div>

          <button className="btn btn-outline btn-sm" onClick={loadTransactions}>
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="transactions-table-container">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading transactions...</p>
          </div>
        ) : transactions.length === 0 ? (
          <div className="empty-state">
            <p>No transactions found</p>
            <button className="btn btn-primary" onClick={handleAddTransaction}>
              Add your first transaction
            </button>
          </div>
        ) : (
          <>
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Category</th>
                  <th>Amount (ZMK)</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTransactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>{transaction.date}</td>
                    <td>{transaction.description || '-'}</td>
                    <td>
                      <span className={`category-badge ${transaction.type}`}>
                        {transaction.category}
                      </span>
                    </td>
                    <td className={transaction.type}>
                      {transaction.type === 'income' ? '+' : '-'}
                      {formatCurrency(Math.abs(transaction.amount))}
                    </td>
                    <td className="actions-cell">
                      <button
                        className="icon-button edit"
                        onClick={() => handleEditTransaction(transaction)}
                        title="Edit"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        className="icon-button delete"
                        onClick={() => handleDeleteTransaction(transaction.id)}
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="pagination">
              <button
                className="pagination-button"
                onClick={handlePrevPage}
                disabled={pagination.page === 1}
              >
                <ChevronLeft size={18} />
              </button>
              <span className="pagination-info">
                Page {pagination.page} of {Math.ceil(pagination.total / pagination.limit)}
              </span>
              <button
                className="pagination-button"
                onClick={handleNextPage}
                disabled={!pagination.hasMore}
              >
                <ChevronRight size={18} />
              </button>
            </div>
          </>
        )}
      </div>

      {/* Add/Edit Transaction Modal - FIXED STRUCTURE */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{editingTransaction ? 'Edit Transaction' : 'Add Transaction'}</h2>
              <button className="close-button" onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>

            {/* Added modal-body wrapper */}
            <div className="modal-body">
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Amount (ZMW) *</label>
                  <div className="input-with-icon">
                    <DollarSign size={18} className="input-icon" />
                    <input
                      type="number"
                      name="amount"
                      className={`form-input with-icon ${formErrors.amount ? 'error' : ''}`}
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      placeholder="0.00"
                      step="0.01"
                      min="0.01"
                    />
                  </div>
                  {formErrors.amount && (
                    <p className="error-message">{formErrors.amount}</p>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Category *</label>
                  <div className="input-with-icon">
                    <Tag size={18} className="input-icon" />
                    <input
                      type="text"
                      className={`form-input with-icon ${formErrors.category ? 'error' : ''}`}
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      placeholder="Enter category (e.g., Food, Rent, Salary)"
                      list="category-suggestions"
                      autoComplete="off"
                    />
                    
                    {/* Simple datalist for suggestions */}
                    <datalist id="category-suggestions">
                      {[...(categories.expense || []), ...(categories.income || [])].map(cat => (
                        <option key={cat} value={cat} />
                      ))}
                    </datalist>
                  </div>
                  {formErrors.category && (
                    <p className="error-message">{formErrors.category}</p>
                  )}
                  <small className="helper-text">
                    You can type any category name. Previously used categories will appear as suggestions.
                  </small>
                </div>

                <div className="form-group">
                  <label className="form-label">Description</label>
                  <div className="input-with-icon">
                    <FileText size={18} className="input-icon" />
                    <input
                      type="text"
                      className="form-input with-icon"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Enter description"
                      maxLength="200"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Date *</label>
                  <div className="input-with-icon">
                    <Calendar size={18} className="input-icon" />
                    <input
                      type="date"
                      className={`form-input with-icon ${formErrors.date ? 'error' : ''}`}
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    />
                  </div>
                  {formErrors.date && (
                    <p className="error-message">{formErrors.date}</p>
                  )}
                </div>

                <div className="modal-actions">
                  <button
                    type="button"
                    className="btn btn-outline"
                    onClick={() => setShowModal(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? 'Saving...' : (editingTransaction ? 'Update' : 'Add')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Transactions;