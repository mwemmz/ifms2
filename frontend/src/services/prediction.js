import api from './api';

class PredictionService {
  async getNextMonthPrediction(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/predict/next-month${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch next month prediction:', error);
      throw error;
    }
  }

  async getCategoryPredictions() {
    try {
      const response = await api.get('/predict/by-category');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch category predictions:', error);
      throw error;
    }
  }

  async getMovingAverage(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/predict/moving-average${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch moving average:', error);
      throw error;
    }
  }

  async getPolynomialPrediction(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/predict/polynomial${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch polynomial prediction:', error);
      throw error;
    }
  }

  async getEnsemblePrediction() {
    try {
      const response = await api.get('/predict/ensemble');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch ensemble prediction:', error);
      throw error;
    }
  }

  async getMultiMonthPrediction(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/predict/multi-month${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch multi-month prediction:', error);
      throw error;
    }
  }

  async getPredictionInsights() {
    try {
      const response = await api.get('/predict/insights');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch prediction insights:', error);
      throw error;
    }
  }

  async getPredictionHealth() {
    try {
      const response = await api.get('/predict/health');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch prediction health:', error);
      throw error;
    }
  }
}

export default new PredictionService();