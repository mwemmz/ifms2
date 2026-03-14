import api from './api';

class BudgetService {
  async getMonthlyBudget(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/budget/monthly${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch monthly budget:', error);
      throw error;
    }
  }

  async compareBudgetActual(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/budget/compare${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to compare budget:', error);
      throw error;
    }
  }

  async getFutureBudgets(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/budget/future${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch future budgets:', error);
      throw error;
    }
  }

  async getBudgetRecommendations() {
    try {
      const response = await api.get('/api/budget/recommendations');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch budget recommendations:', error);
      throw error;
    }
  }

  async createSmartBudget(data) {
    try {
      const response = await api.post('/api/budget/smart', data);
      return response.data;
    } catch (error) {
      console.error('Failed to create smart budget:', error);
      throw error;
    }
  }

  async getBudgetHistory(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/budget/history${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch budget history:', error);
      throw error;
    }
  }

  async getCurrentBudgetStatus() {
    try {
      const response = await api.get('/api/budget/current-status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch current budget status:', error);
      throw error;
    }
  }
}

export default new BudgetService();