import api from './api';

class ReportsService {
  async getMonthlyReport(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/reports/monthly${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch monthly report:', error);
      throw error;
    }
  }

  async getYearlyReport(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/reports/yearly${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch yearly report:', error);
      throw error;
    }
  }

  async getCategoryReport(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/reports/category${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch category report:', error);
      throw error;
    }
  }

  async compareYears(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/reports/compare-years${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to compare years:', error);
      throw error;
    }
  }

  async exportData(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const url = `/reports/export${queryParams ? `?${queryParams}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to export data:', error);
      throw error;
    }
  }

  async getDashboard() {
    try {
      const response = await api.get('/reports/dashboard');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      throw error;
    }
  }

  async getAvailableReports() {
    try {
      const response = await api.get('/reports/available-reports');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch available reports:', error);
      throw error;
    }
  }
}

export default new ReportsService();