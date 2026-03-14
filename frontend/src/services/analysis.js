import api from './api';

class AnalysisService {
  async getCategoryBreakdown(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/analysis/category-breakdown${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch category breakdown:', error);
      throw error;
    }
  }

  async getMonthlySummary(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/analysis/monthly-summary${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch monthly summary:', error);
      throw error;
    }
  }

  async getTrends(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/analysis/trends${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch trends:', error);
      throw error;
    }
  }

  async getTopCategories(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/analysis/top-categories${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch top categories:', error);
      throw error;
    }
  }

  async comparePeriods(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/api/analysis/compare${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to compare periods:', error);
      throw error;
    }
  }

  async getSpendingPatterns() {
    try {
      const response = await api.get('/api/analysis/patterns');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch spending patterns:', error);
      throw error;
    }
  }

  async getInsights() {
    try {
      const response = await api.get('/api/analysis/insights');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch insights:', error);
      throw error;
    }
  }
}

export default new AnalysisService();