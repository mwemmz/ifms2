import api from './api';

class NotificationService {
  async getNotifications() {
    try {
      // In a real app, this would fetch from a notifications endpoint
      // For now, we'll generate sample notifications based on app state
      const response = await api.get('/advice/insights');
      const insights = response.data;
      
      return this.generateNotifications(insights);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      return this.getDefaultNotifications();
    }
  }

  generateNotifications(insights) {
    const notifications = [];
    
    // Add overspending notifications
    if (insights?.overspending?.length > 0) {
      insights.overspending.forEach(item => {
        notifications.push({
          id: `overspend-${Date.now()}-${Math.random()}`,
          type: 'warning',
          title: 'Overspending Alert',
          message: `You've spent ${item.increase_percentage}% more on ${item.category} this month`,
          timestamp: new Date(),
          read: false,
          actionable: true,
          action: 'View Details',
          link: '/advice',
          icon: 'alert'
        });
      });
    }

    // Add savings opportunities
    if (insights?.savings_opportunities?.length > 0) {
      insights.savings_opportunities.slice(0, 2).forEach(opp => {
        notifications.push({
          id: `savings-${Date.now()}-${Math.random()}`,
          type: 'info',
          title: 'Savings Opportunity',
          message: opp.description || `Potential savings in ${opp.category}`,
          timestamp: new Date(),
          read: false,
          actionable: true,
          action: 'Review',
          link: '/advice?savings',
          icon: 'piggy'
        });
      });
    }

    // Add budget alerts
    if (insights?.budget_suggestions?.adjustments_needed?.length > 0) {
      notifications.push({
        id: `budget-${Date.now()}`,
        type: 'warning',
        title: 'Budget Adjustment Needed',
        message: 'Your budget needs attention in several categories',
        timestamp: new Date(),
        read: false,
        actionable: true,
        action: 'Adjust Budget',
        link: '/budget',
        icon: 'budget'
      });
    }

    // Add prediction alerts
    if (insights?.next_month_prediction) {
      notifications.push({
        id: `prediction-${Date.now()}`,
        type: 'info',
        title: 'Next Month Prediction',
        message: `Expected expenses: $${insights.next_month_prediction.total}`,
        timestamp: new Date(),
        read: false,
        actionable: true,
        action: 'View Details',
        link: '/predictions',
        icon: 'trend'
      });
    }

    // Add goal progress notifications
    if (insights?.summary?.goal_progress) {
      const progress = insights.summary.goal_progress;
      if (progress >= 90) {
        notifications.push({
          id: `goal-${Date.now()}`,
          type: 'success',
          title: 'Goal Almost Achieved!',
          message: `You're ${progress}% to your savings goal`,
          timestamp: new Date(),
          read: false,
          actionable: true,
          action: 'Celebrate',
          link: '/advice',
          icon: 'goal'
        });
      }
    }

    // If no notifications, add some default ones
    if (notifications.length === 0) {
      return this.getDefaultNotifications();
    }

    return notifications;
  }

  getDefaultNotifications() {
    return [
      {
        id: 'welcome-1',
        type: 'success',
        title: 'Welcome to IFMS!',
        message: 'Start by adding your first transaction',
        timestamp: new Date(),
        read: false,
        actionable: true,
        action: 'Add Transaction',
        link: '/transactions',
        icon: 'welcome'
      },
      {
        id: 'tip-1',
        type: 'info',
        title: 'Pro Tip',
        message: 'Set up MFA for extra security',
        timestamp: new Date(),
        read: false,
        actionable: true,
        action: 'Enable Now',
        link: '/profile',
        icon: 'tip'
      }
    ];
  }

  async markAsRead(notificationId) {
    // In a real app, this would update the backend
    return { success: true };
  }

  async markAllAsRead() {
    // In a real app, this would update the backend
    return { success: true };
  }

  async deleteNotification(notificationId) {
    // In a real app, this would delete from backend
    return { success: true };
  }

  async clearAll() {
    // In a real app, this would clear all notifications
    return { success: true };
  }
}

export default new NotificationService();