import api from './api';

class TransactionService {
  async getTransactions(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/transactions${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      throw error;
    }
  }

  async getTransaction(id) {
    try {
      const response = await api.get(`/transactions/${id}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch transaction:', error);
      throw error;
    }
  }

  async createTransaction(transactionData) {
    try {
      const response = await api.post('/transactions', transactionData);
      return response.data;
    } catch (error) {
      console.error('Failed to create transaction:', error);
      throw error;
    }
  }

  async updateTransaction(id, transactionData) {
    try {
      const response = await api.put(`/transactions/${id}`, transactionData);
      return response.data;
    } catch (error) {
      console.error('Failed to update transaction:', error);
      throw error;
    }
  }

  async deleteTransaction(id) {
    try {
      const response = await api.delete(`/transactions/${id}`);
      return response.data;
    } catch (error) {
      console.error('Failed to delete transaction:', error);
      throw error;
    }
  }

  async getCategories() {
    try {
      const response = await api.get('/transactions/categories');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  }

  async getSummary(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/transactions/summary${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch summary:', error);
      throw error;
    }
  }

  async getRecentTransactions() {
    try {
      const response = await api.get('/transactions/recent');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch recent transactions:', error);
      throw error;
    }
  }
}

export default new TransactionService();