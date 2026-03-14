import api from './api';

class AdviceService {
  async getHealthScore() {
    try {
      const response = await api.get('/api/advice/health-score');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch health score:', error);
      throw error;
    }
  }

  async getRecommendations() {
    try {
      const response = await api.get('/api/advice/recommendations');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      throw error;
    }
  }

  async getBudgetSuggestions() {
    try {
      const response = await api.get('/api/advice/budget-suggestions');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch budget suggestions:', error);
      throw error;
    }
  }

  async getOverspending() {
    try {
      const response = await api.get('/api/advice/overspending');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch overspending:', error);
      throw error;
    }
  }

  async getSavingsOpportunities() {
    try {
      const response = await api.get('/api/advice/savings-opportunities');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch savings opportunities:', error);
      throw error;
    }
  }

  async getFinancialInsights() {
    try {
      const response = await api.get('/api/advice/insights');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch financial insights:', error);
      throw error;
    }
  }

  async getGoalProgress() {
    try {
      const response = await api.get('/api/advice/goal-progress');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch goal progress:', error);
      throw error;
    }
  }

  async getEmergencyFundStatus() {
    try {
      const response = await api.get('/api/advice/emergency-fund');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch emergency fund status:', error);
      throw error;
    }
  }
}

export default new AdviceService();