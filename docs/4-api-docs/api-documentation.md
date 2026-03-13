# Intelligent Financial Management System (IFMS) - API Documentation

## 1. API Overview

### 1.1 Base Information

| Property | Value |
|----------|-------|
| **Base URL** | `http://localhost:5000/api` (development) |
| **Base URL** | `https://api.ifms.com/v1` (production) |
| **API Version** | v1.0 |
| **Format** | JSON |
| **Authentication** | JWT Bearer Token |
| **Rate Limit** | 60 requests per minute per user |

### 1.2 Headers

All API requests require the following headers:

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <your_jwt_token>

1.3 Response Format
All responses follow a consistent format:

Success Response:
{
  "data": { ... },
  "message": "Success message",
  "status_code": 200
}

Error Response:
{
  "error": "Error type",
  "message": "Detailed error message",
  "status_code": 400,
  "timestamp": "2026-02-21T10:30:00Z",
  "path": "/api/endpoint"
}

1.4 HTTP Status Codes
Code	Description	When to Expect
200	OK	Request succeeded
201	Created	Resource created successfully
400	Bad Request	Invalid input data
401	Unauthorized	Missing or invalid token
403	Forbidden	Insufficient permissions
404	Not Found	Resource doesn't exist
409	Conflict	Resource already exists
422	Unprocessable Entity	Validation failed
429	Too Many Requests	Rate limit exceeded
500	Internal Server Error	Server-side error

2. Authentication Endpoints
2.1 Register User
Creates a new user account.

Endpoint: POST /auth/register

Request Body:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Validation Rules:

Field	Rules
username	Required, 3-50 characters, alphanumeric
email	Required, valid email format
password	Required, min 8 chars, 1 uppercase, 1 number
full_name	Optional, max 100 characters

Success Response (201):
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}

Error Responses:
// 400 - Validation Error
{
  "error": "Validation Error",
  "details": ["Username already exists"]
}

// 400 - Invalid Email
{
  "error": "Invalid email format"
}

2.2 Login
Authenticates a user and returns a JWT token.

Endpoint: POST /auth/login

Request Body:
{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Success Response - No MFA (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}

Success Response - MFA Required (200):
{
  "mfa_required": true,
  "temp_token": "eyJhbGciOiJIUzI1NiIs...",
  "message": "MFA verification required"
}

Error Response (401):
{
  "error": "Invalid username or password"
}

2.3 Setup MFA
Sets up Multi-Factor Authentication for the user.

Endpoint: POST /auth/setup-mfa
Authentication: Required

Response (200):
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgo...",
  "message": "Scan QR code with Google Authenticator"
}

2.4 Verify MFA
Verifies MFA token during login.

Endpoint: POST /auth/verify-mfa
Authentication: Required (with temp_token)

Request Body:
{
  "token": "123456"
}
Success Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "message": "MFA verified successfully"
}

Error Response (401):
{
  "error": "Invalid MFA token"
}

2.5 Disable MFA
Disables MFA for the user.

Endpoint: POST /auth/disable-mfa
Authentication: Required

Success Response (200):
{
  "message": "MFA disabled successfully"
}

2.6 Get Profile
Retrieves the user's profile information.

Endpoint: GET /auth/profile
Authentication: Required

Success Response (200):
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "mfa_enabled": true,
  "profile": {
    "full_name": "John Doe",
    "monthly_salary": 5000.00,
    "savings_goal": 10000.00
  }
}

2.7 Update Profile
Updates the user's profile information.

Endpoint: PUT /auth/update-profile
Authentication: Required

Request Body:
{
  "full_name": "John Updated",
  "monthly_salary": 5500.00,
  "savings_goal": 15000.00
}

Success Response (200):
{
  "message": "Profile updated successfully"
}

3. Transaction Endpoints
3.1 Get Categories
Returns all available transaction categories.

Endpoint: GET /transactions/categories
Authentication: Required

Response (200):
{
  "expense_categories": [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Rent/Mortgage",
    "Insurance",
    "Personal Care",
    "Gifts & Donations",
    "Travel",
    "Other Expenses"
  ],
  "income_categories": [
    "Salary",
    "Freelance",
    "Investment",
    "Business",
    "Gift",
    "Refund",
    "Other Income"
  ]
}

3.2 Get Transactions
Retrieves transactions with optional filters.

Endpoint: GET /transactions
Authentication: Required

Query Parameters:
Parameter	Type	Description
month	integer	Filter by month (1-12)
year	integer	Filter by year
category	string	Filter by category
type	string	Filter by type (income/expense)
limit	integer	Number of records (default: 100)
offset	integer	Pagination offset

Example Request:
GET /transactions?month=3&year=2024&type=expense&limit=10

Response (200):
{
  "transactions": [
    {
      "id": 1,
      "amount": -45.99,
      "category": "Food & Dining",
      "description": "Grocery shopping",
      "date": "2024-03-15",
      "type": "expense"
    },
    {
      "id": 2,
      "amount": 3000.00,
      "category": "Salary",
      "description": "Monthly salary",
      "date": "2024-03-01",
      "type": "income"
    }
  ],
  "pagination": {
    "total": 45,
    "offset": 0,
    "limit": 10,
    "has_more": true
  }
}

3.3 Create Transaction
Adds a new transaction.

Endpoint: POST /transactions
Authentication: Required

Request Body:
{
  "amount": 45.99,
  "category": "Food & Dining",
  "description": "Grocery shopping",
  "date": "2024-03-15"
}

Validation Rules:

Field	Rules
amount	Required, positive number
category	Required, must exist in categories
description	Optional, max 200 chars
date	Required, format: YYYY-MM-DD

Success Response (201):
{
  "message": "Transaction added successfully",
  "transaction": {
    "id": 3,
    "amount": -45.99,
    "category": "Food & Dining",
    "description": "Grocery shopping",
    "date": "2024-03-15",
    "type": "expense"
  }
}

3.4 Get Transaction
Retrieves a specific transaction.

Endpoint: GET /transactions/{id}
Authentication: Required

Response (200):
{
  "id": 1,
  "amount": -45.99,
  "category": "Food & Dining",
  "description": "Grocery shopping",
  "date": "2024-03-15",
  "type": "expense"
}

3.5 Update Transaction
Updates an existing transaction.

Endpoint: PUT /transactions/{id}
Authentication: Required

Request Body:
{
  "amount": 55.99,
  "description": "Updated grocery shopping"
}
Response (200):
{
  "message": "Transaction updated successfully",
  "transaction": {
    "id": 1,
    "amount": -55.99,
    "category": "Food & Dining",
    "description": "Updated grocery shopping",
    "date": "2024-03-15",
    "type": "expense"
  }
}

3.6 Delete Transaction
Deletes a transaction.

Endpoint: DELETE /transactions/{id}
Authentication: Required

Response (200):
{
  "message": "Transaction deleted successfully"
}

3.7 Get Monthly Summary
Returns a summary of transactions for a specific month.

Endpoint: GET /transactions/summary
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
month	integer	current	Month to summarize
year	integer	current	Year to summarize
Response (200):
{
  "period": "2024-03",
  "summary": {
    "total_income": 5000.00,
    "total_expenses": 3245.50,
    "net_savings": 1754.50,
    "transaction_count": 23
  },
  "category_breakdown": {
    "Food & Dining": {
      "amount": 450.75,
      "percentage": 13.9,
      "count": 8
    },
    "Rent/Mortgage": {
      "amount": 1500.00,
      "percentage": 46.2,
      "count": 1
    }
  }
}

3.8 Get Recent Transactions
Returns the 10 most recent transactions.

Endpoint: GET /transactions/recent
Authentication: Required

Response (200):
[
  {
    "id": 23,
    "amount": -25.50,
    "category": "Food & Dining",
    "description": "Lunch",
    "date": "2024-03-20",
    "type": "expense"
  },
  // ... 9 more transactions
]

4. Analysis Endpoints
4.1 Get Category Breakdown
Returns spending breakdown by category.

Endpoint: GET /analysis/category-breakdown
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
month	integer	current	Month to analyze
year	integer	current	Year to analyze
Response (200):
{
  "period": {
    "start": "2024-03-01",
    "end": "2024-03-31",
    "month": "March 2024"
  },
  "total_spent": 3245.50,
  "categories": {
    "Rent/Mortgage": {
      "total": 1500.00,
      "percentage": 46.2,
      "transaction_count": 1,
      "average_per_transaction": 1500.00
    },
    "Food & Dining": {
      "total": 450.75,
      "percentage": 13.9,
      "transaction_count": 8,
      "average_per_transaction": 56.34
    }
  },
  "category_count": 6
}

4.2 Get Monthly Summary
Returns monthly spending summary for the last N months.

Endpoint: GET /analysis/monthly-summary
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
months	integer	6	Number of months to analyze

Response (200):
{
  "months_analyzed": 6,
  "averages": {
    "monthly_expenses": 2850.33,
    "monthly_income": 4850.33,
    "monthly_savings": 2000.00
  },
  "monthly_data": [
    {
      "year": 2024,
      "month": 3,
      "month_name": "March",
      "income": 5000.00,
      "expenses": 3245.50,
      "savings": 1754.50,
      "transaction_count": 23
    },
    // ... 5 more months
  ]
}

4.3 Get Spending Trends
Detects spending trends across categories.

Endpoint: GET /analysis/trends
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
months	integer	3	Analysis period in months
Response (200):
{
  "analysis_period_months": 3,
  "trends": {
    "Food & Dining": {
      "direction": "increasing",
      "slope": 45.20,
      "percentage_change": 15.3,
      "current_monthly_avg": 450.75,
      "previous_monthly_avg": 391.00,
      "volatility": 32.45
    },
    "Entertainment": {
      "direction": "decreasing",
      "slope": -12.50,
      "percentage_change": -8.2,
      "current_monthly_avg": 140.25,
      "previous_monthly_avg": 152.75,
      "volatility": 15.80
    }
  },
  "summary": {
    "increasing_categories": ["Food & Dining", "Utilities"],
    "decreasing_categories": ["Entertainment", "Shopping"],
    "stable_categories": ["Rent/Mortgage"],
    "total_categories_analyzed": 6
  }
}

4.4 Get Top Categories
Returns top spending categories.

Endpoint: GET /analysis/top-categories
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
limit	integer	5	Number of categories to return

Response (200):
{
  "top_categories": [
    {
      "category": "Rent/Mortgage",
      "total": 1500.00,
      "percentage": 46.2,
      "transaction_count": 1,
      "average_per_transaction": 1500.00
    },
    {
      "category": "Food & Dining",
      "total": 450.75,
      "percentage": 13.9,
      "transaction_count": 8,
      "average_per_transaction": 56.34
    }
  ],
  "total_categories": 5
}

4.5 Compare Periods
Compares spending between two periods.

Endpoint: GET /analysis/compare
Authentication: Required

Query Parameters:

Parameter	Type	Description
current_month	integer	Current period month
current_year	integer	Current period year
previous_month	integer	Previous period month
previous_year	integer	Previous period year
Response (200):
{
  "current_period": {
    "start": "2024-03-01",
    "end": "2024-03-31",
    "total": 3245.50,
    "categories": {
      "Food & Dining": { "total": 450.75 }
    }
  },
  "previous_period": {
    "start": "2024-02-01",
    "end": "2024-02-29",
    "total": 2950.25,
    "categories": {
      "Food & Dining": { "total": 391.00 }
    }
  },
  "overall_change": {
    "absolute": 295.25,
    "percentage": 10.0
  },
  "changes": {
    "Food & Dining": {
      "current": 450.75,
      "previous": 391.00,
      "absolute_change": 59.75,
      "percentage_change": 15.3
    }
  }
}

4.6 Get Spending Patterns
Analyzes spending patterns by day of week, month halves, etc.

Endpoint: GET /analysis/patterns
Authentication: Required

Response (200):
{
  "weekday_vs_weekend": {
    "weekday": {
      "total": 2450.75,
      "average": 89.12,
      "count": 27
    },
    "weekend": {
      "total": 794.75,
      "average": 132.46,
      "count": 6
    }
  },
  "by_day_of_week": {
    "Monday": { "total": 325.50, "average": 65.10, "count": 5 },
    "Tuesday": { "total": 412.25, "average": 68.71, "count": 6 },
    "Wednesday": { "total": 289.75, "average": 57.95, "count": 5 },
    "Thursday": { "total": 456.00, "average": 76.00, "count": 6 },
    "Friday": { "total": 967.25, "average": 138.18, "count": 7 },
    "Saturday": { "total": 489.50, "average": 139.86, "count": 3.5 },
    "Sunday": { "total": 305.25, "average": 122.10, "count": 2.5 }
  },
  "month_halves": {
    "first_half": {
      "total": 1895.50,
      "average": 126.37
    },
    "second_half": {
      "total": 1350.00,
      "average": 90.00
    }
  }
}

4.7 Get Insights
Returns comprehensive spending insights.

Endpoint: GET /analysis/insights
Authentication: Required

Response (200):
{
  "current_month": {
    "breakdown": { ... },
    "total": 3245.50
  },
  "comparison": { ... },
  "trends": { ... },
  "patterns": { ... },
  "top_categories": [ ... ],
  "summary": {
    "total_categories": 6,
    "has_trends": true,
    "comparison_with_last_month": {
      "absolute": 295.25,
      "percentage": 10.0
    },
    "top_spending_category": {
      "category": "Rent/Mortgage",
      "amount": 1500.00,
      "percentage": 46.2
    }
  }
}

5. Prediction Endpoints
5.1 Next Month Prediction
Predicts expenses for next month using linear regression.

Endpoint: GET /predict/next-month
Authentication: Required

Query Parameters:

Parameter	Type	Description
category	string	Optional category filter

Response (200):
{
  "prediction": {
    "total": 3350.50,
    "transaction_count": 25,
    "average_per_transaction": 134.02
  },
  "confidence": {
    "score": 75.5,
    "level": "High",
    "r2_score": 0.82,
    "data_points": 12,
    "volatility": 0.18
  },
  "trend": {
    "direction": "increasing",
    "strength": "moderate"
  },
  "based_on_months": 12,
  "historical_data": {
    "months": ["2024-03", "2024-02", "2024-01"],
    "totals": [3245.50, 2950.25, 3100.75]
  }
}

5.2 Category Predictions
Returns predictions broken down by category.

Endpoint: GET /predict/by-category
Authentication: Required

Response (200):
{
  "total_predicted": 3350.50,
  "by_category": {
    "Rent/Mortgage": {
      "predicted": 1500.00,
      "confidence": { "level": "High" },
      "trend": { "direction": "stable" }
    },
    "Food & Dining": {
      "predicted": 475.50,
      "confidence": { "level": "Medium" },
      "trend": { "direction": "increasing", "strength": "moderate" }
    }
  },
  "categories_analyzed": 6
}

5.3 Moving Average Prediction
Predicts using moving average method.

Endpoint: GET /predict/moving-average
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
window	integer	3	Moving average window
Response (200):
{
  "prediction": {
    "total": 3200.25,
    "method": "3_month_moving_average"
  },
  "trend": {
    "direction": "increasing",
    "percentage_change": 4.2
  },
  "window_months": 3,
  "based_on_months": 6
}

5.4 Polynomial Prediction
Predicts using polynomial regression.

Endpoint: GET /predict/polynomial
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
degree	integer	2	Polynomial degree (2-4)
category	string	-	Optional category filter
Response (200):
{
  "prediction": {
    "total": 3425.75,
    "method": "polynomial_degree_2"
  },
  "confidence": "Medium",
  "r2_score": 0.75,
  "based_on_months": 12
}

5.5 Ensemble Prediction
Combines multiple prediction methods.

Endpoint: GET /predict/ensemble
Authentication: Required

Response (200):
{
  "prediction": {
    "total": 3325.50,
    "method": "ensemble"
  },
  "individual_predictions": {
    "linear": 3350.50,
    "moving_avg_3m": 3200.25,
    "moving_avg_6m": 3150.75
  },
  "confidence": "High",
  "methods_used": 3
}

5.6 Multi-Month Prediction
Predicts expenses for multiple months ahead.

Endpoint: GET /predict/multi-month
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
months	integer	3	Number of months to predict (1-6)

Response (200):
{
  "predictions": [
    {
      "month": "April 2024",
      "predicted_total": 3350.50,
      "confidence_factor": 85.0
    },
    {
      "month": "May 2024",
      "predicted_total": 3425.25,
      "confidence_factor": 70.0
    },
    {
      "month": "June 2024",
      "predicted_total": 3500.00,
      "confidence_factor": 55.0
    }
  ],
  "based_on_months": 12,
  "method": "linear_trend_extrapolation"
}

5.7 Prediction Health
Checks if enough data is available for predictions.

Endpoint: GET /predict/health
Authentication: Required

Response (200):
{
  "has_enough_data": true,
  "transaction_count": 245,
  "months_of_data": 12,
  "can_predict": true,
  "available_methods": [
    "linear_regression",
    "moving_average",
    "polynomial_regression",
    "ensemble",
    "seasonal_analysis"
  ]
}

5.8 Prediction Insights
Returns comprehensive prediction insights.

Endpoint: GET /predict/insights
Authentication: Required

Response (200):
{
  "next_month": { ... },
  "by_category": { ... },
  "ensemble": { ... },
  "three_month_outlook": { ... },
  "method_comparison": [
    {
      "method": "Linear Regression",
      "predicted": 3350.50,
      "confidence": "High"
    },
    {
      "method": "3-Month Moving Average",
      "predicted": 3200.25,
      "confidence": "Medium"
    },
    {
      "method": "Ensemble",
      "predicted": 3325.50,
      "confidence": "High"
    }
  ],
  "average_prediction": 3292.08
}

6. Financial Advice Endpoints
6.1 Get Health Score
Returns the user's financial health score.

Endpoint: GET /advice/health-score
Authentication: Required

Response (200):
{
  "score": 75,
  "rating": "Good",
  "max_score": 100
}

6.2 Get Recommendations
Returns personalized financial recommendations.

Endpoint: GET /advice/recommendations
Authentication: Required

Response (200):
{
  "recommendations": [
    {
      "type": "warning",
      "category": "savings",
      "priority": "high",
      "title": "Low Savings Rate",
      "message": "You are only saving 12% of your income.",
      "suggestion": "Try to save at least 20% of your income.",
      "actionable": true,
      "action": "Set up automatic savings transfer"
    },
    {
      "type": "info",
      "category": "budgeting",
      "priority": "medium",
      "title": "High Essential Expenses",
      "message": "Essentials are consuming 65% of your income.",
      "suggestion": "Look for ways to reduce fixed costs.",
      "actionable": true,
      "action": "Review essential expenses"
    }
  ],
  "count": 2
}

6.3 Get Budget Suggestions
Returns 50/30/20 budget analysis.

Endpoint: GET /advice/budget-suggestions
Authentication: Required

Response (200):
{
  "monthly_income": 5000.00,
  "ideal_budget": {
    "essentials": 2500.00,
    "wants": 1500.00,
    "savings": 1000.00
  },
  "current_spending": {
    "essentials": 2750.00,
    "wants": 1400.00,
    "savings": 850.00
  },
  "adjustments_needed": [
    {
      "category": "essentials",
      "current": 2750.00,
      "target": 2500.00,
      "excess": 250.00,
      "suggestion": "Look for ways to reduce fixed costs"
    }
  ],
  "health_score": 75
}

6.4 Get Overspending
Detects categories with overspending.

Endpoint: GET /advice/overspending
Authentication: Required

Response (200):
{
  "overspending_categories": [
    {
      "category": "Food & Dining",
      "current": 450.75,
      "previous": 391.00,
      "increase_percentage": 15.3,
      "excess_amount": 59.75,
      "severity": "medium"
    }
  ],
  "count": 1
}
6.5 Get Savings Opportunities
Identifies potential savings opportunities.

Endpoint: GET /advice/savings-opportunities
Authentication: Required

Response (200):
{
  "opportunities": [
    {
      "type": "subscription",
      "description": "Netflix",
      "monthly_cost": 15.99,
      "annual_cost": 191.88,
      "suggestion": "Review if you're actively using this subscription"
    },
    {
      "type": "high_spending",
      "category": "Food & Dining",
      "monthly_avg": 150.25,
      "suggestion": "Set a monthly limit for Food & Dining"
    }
  ],
  "count": 2
}

6.6 Get Goal Progress
Returns progress toward savings goal.

Endpoint: GET /advice/goal-progress
Authentication: Required

Response (200):
{
  "goal_amount": 10000.00,
  "current_amount": 2500.00,
  "progress_percentage": 25.0,
  "remaining": 7500.00,
  "on_track": false
}

6.7 Get Emergency Fund Status
Returns emergency fund analysis.

Endpoint: GET /advice/emergency-fund
Authentication: Required

Response (200):
{
  "current_amount": 5000.00,
  "monthly_expenses_estimate": 3245.50,
  "months_covered": 1.5,
  "target_months": 6,
  "target_amount": 19473.00,
  "status": "needs_attention"
}

6.8 Get Financial Insights
Returns comprehensive financial insights.

Endpoint: GET /advice/insights
Authentication: Required

Response (200):
{
  "health_score": 75,
  "recommendations": [ ... ],
  "budget_suggestions": { ... },
  "savings_opportunities": [ ... ],
  "overspending": [ ... ],
  "summary": {
    "monthly_income": 5000.00,
    "savings_goal": 10000.00,
    "emergency_fund": 5000.00
  },
  "next_month_prediction": {
    "total": 3350.50
  }
}

7. Budget Endpoints
7.1 Get Monthly Budget
Generates a monthly budget.

Endpoint: GET /budget/monthly
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
month	integer	current	Month for budget
year	integer	current	Year for budget

Response (200):
{
  "budget_id": "budget_2024_3_1",
  "period": {
    "month": "March",
    "year": 2024,
    "start_date": "2024-03-01",
    "end_date": "2024-03-31",
    "days_in_month": 31
  },
  "income": {
    "monthly_salary": 5000.00,
    "other_income": 0,
    "total_income": 5000.00
  },
  "ideal_budget": {
    "essentials": 2500.00,
    "wants": 1500.00,
    "savings": 1000.00
  },
  "category_budgets": {
    "Rent/Mortgage": {
      "allocated": 1500.00,
      "type": "essential",
      "historical_avg": 1500.00,
      "notes": "Matches historical spending."
    },
    "Food & Dining": {
      "allocated": 400.00,
      "type": "essential",
      "historical_avg": 450.75,
      "notes": "Reduced by 11.3% from historical average."
    }
  },
  "summary": {
    "total_budgeted": 4750.00,
    "projected_savings": 250.00,
    "savings_rate": 5.0,
    "savings_goal_met": false,
    "remaining_for_savings": 750.00
  },
  "adjustments_needed": [ ... ],
  "tips": [
    "⚠️ Low savings rate. Review wants categories for reduction opportunities.",
    "🎯 Your Food & Dining budget is 8.0% of income."
  ],
  "savings_goal": {
    "target": 10000.00,
    "current": 2500.00,
    "progress_percentage": 25.0,
    "months_to_goal": 30.0,
    "on_track": false
  }
}

7.2 Compare Budget vs Actual
Compares budgeted amounts with actual spending.

Endpoint: GET /budget/compare
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
month	integer	current	Month to compare
year	integer	current	Year to compare

Response (200):
{
  "period": {
    "month": "March",
    "year": 2024,
    "start_date": "2024-03-01",
    "end_date": "2024-03-31"
  },
  "income": {
    "monthly_salary": 5000.00,
    "total_income": 5000.00
  },
  "summary": {
    "total_budgeted": 4750.00,
    "total_actual": 4845.50,
    "total_difference": -95.50,
    "actual_savings": 154.50,
    "budgeted_savings": 250.00,
    "savings_variance": -95.50
  },
  "category_comparison": [
    {
      "category": "Food & Dining",
      "budgeted": 400.00,
      "actual": 450.75,
      "difference": -50.75,
      "difference_percentage":


7.3 Get Future Budgets
Generates budgets for future months.

Endpoint: GET /budget/future
Authentication: Required

Query Parameters:

Parameter	Type	Default	Description
months	integer	3	Number of months (1-12)

Response (200):
{
  "future_budgets": [
    {
      "month": "April",
      "year": 2024,
      "total_budget": 4800.00,
      "projected_savings": 200.00,
      "savings_rate": 4.2,
      "confidence": "High",
      "categories": 6
    },
    {
      "month": "May",
      "year": 2024,
      "total_budget": 4850.00,
      "projected_savings": 150.00,
      "savings_rate": 3.1,
      "confidence": "Medium",
      "categories": 6
    }
  ],
  "total_months": 2
}

7.4 Get Budget Recommendations
Returns budget optimization recommendations.

Endpoint: GET /budget/recommendations
Authentication: Required

Response (200):
{
  "recommendations": [
    {
      "type": "budget_adjustment",
      "category": "Food & Dining",
      "current_budget": 400.00,
      "suggested_budget": 460.00,
      "reason": "Consistently over budget by 12.7%",
      "action": "Consider increasing budget or reducing spending"
    },
    {
      "type": "reallocation",
      "category": "Entertainment",
      "potential_savings": 50.00,
      "suggestion": "You consistently spend less in Entertainment. Consider reallocating to savings."
    },
    {
      "type": "savings_opportunity",
      "description": "Netflix subscription",
      "potential_savings": 15.99,
      "suggestion": "Review if you're actively using this subscription"
    }
  ],
  "count": 3
}

7.5 Create Smart Budget
Creates an optimized budget for a target savings rate.

Endpoint: POST /budget/smart
Authentication: Required

Request Body:
{
  "target_savings_rate": 20
}

11. Error Codes Reference
11.1 Authentication Errors (AUTH-xxx)
Code	Message	Description
AUTH-001	Invalid credentials	Username or password incorrect
AUTH-002	Token expired	JWT token has expired
AUTH-003	Invalid token	JWT token is malformed
AUTH-004	MFA required	Endpoint requires MFA
AUTH-005	Invalid MFA token	MFA verification failed
AUTH-006	Account locked	Too many failed attempts
11.2 Validation Errors (VAL-xxx)
Code	Message	Description
VAL-001	Required field missing	Field is required
VAL-002	Invalid format	Field format is invalid
VAL-003	Value out of range	Number outside allowed range
VAL-004	Invalid category	Category doesn't exist
VAL-005	Invalid date	Date format incorrect
11.3 Resource Errors (RES-xxx)
Code	Message	Description
RES-001	Resource not found	Requested resource doesn't exist
RES-002	Already exists	Resource already exists
RES-003	Insufficient data	Not enough data for operation
RES-004	Resource locked	Resource is currently locked
11.4 Rate Limit Errors (RATE-xxx)
Code	Message	Description
RATE-001	Too many requests	Rate limit exceeded
RATE-002	Try again later	Cooling period active
11.5 Server Errors (SRV-xxx)
Code	Message	Description
SRV-001	Internal server error	Unexpected error
SRV-002	Service unavailable	Maintenance mode
SRV-003	Database error	Database connection issue