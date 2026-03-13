# Intelligent Financial Management System (IFMS) - User Guide

## Table of Contents

1. [Getting Started](#1-getting-started)
   - 1.1 [Creating an Account](#11-creating-an-account)
   - 1.2 [Logging In](#12-logging-in)
   - 1.3 [Setting Up Multi-Factor Authentication](#13-setting-up-multi-factor-authentication)
   - 1.4 [Understanding the Dashboard](#14-understanding-the-dashboard)

2. [Managing Your Profile](#2-managing-your-profile)
   - 2.1 [Viewing Profile Information](#21-viewing-profile-information)
   - 2.2 [Editing Personal Details](#22-editing-personal-details)
   - 2.3 [Setting Financial Goals](#23-setting-financial-goals)
   - 2.4 [Managing MFA Settings](#24-managing-mfa-settings)
   - 2.5 [Viewing Active Sessions](#25-viewing-active-sessions)

3. [Transactions](#3-transactions)
   - 3.1 [Adding a Transaction](#31-adding-a-transaction)
   - 3.2 [Viewing Transactions](#32-viewing-transactions)
   - 3.3 [Filtering Transactions](#33-filtering-transactions)
   - 3.4 [Editing a Transaction](#34-editing-a-transaction)
   - 3.5 [Deleting a Transaction](#35-deleting-a-transaction)
   - 3.6 [Understanding Categories](#36-understanding-categories)
   - 3.7 [Exporting Transactions](#37-exporting-transactions)

4. [Spending Analysis](#4-spending-analysis)
   - 4.1 [Overview Dashboard](#41-overview-dashboard)
   - 4.2 [Category Breakdown](#42-category-breakdown)
   - 4.3 [Monthly Trends](#43-monthly-trends)
   - 4.4 [Spending Patterns](#44-spending-patterns)
   - 4.5 [Period Comparison](#45-period-comparison)

5. [Expense Predictions](#5-expense-predictions)
   - 5.1 [Understanding Predictions](#51-understanding-predictions)
   - 5.2 [Next Month Prediction](#52-next-month-prediction)
   - 5.3 [Category Predictions](#53-category-predictions)
   - 5.4 [3-Month Outlook](#54-3-month-outlook)
   - 5.5 [Confidence Levels](#55-confidence-levels)

6. [Financial Advice](#6-financial-advice)
   - 6.1 [Financial Health Score](#61-financial-health-score)
   - 6.2 [Personalized Recommendations](#62-personalized-recommendations)
   - 6.3 [Budget Suggestions (50/30/20 Rule)](#63-budget-suggestions-503020-rule)
   - 6.4 [Overspending Alerts](#64-overspending-alerts)
   - 6.5 [Savings Opportunities](#65-savings-opportunities)
   - 6.6 [Emergency Fund Tracking](#66-emergency-fund-tracking)

7. [Budget Planning](#7-budget-planning)
   - 7.1 [Viewing Your Monthly Budget](#71-viewing-your-monthly-budget)
   - 7.2 [Understanding Category Allocations](#72-understanding-category-allocations)
   - 7.3 [Budget vs Actual Comparison](#73-budget-vs-actual-comparison)
   - 7.4 [Creating a Smart Budget](#74-creating-a-smart-budget)
   - 7.5 [Future Budget Projections](#75-future-budget-projections)
   - 7.6 [Budget Tips](#76-budget-tips)

8. [Reports](#8-reports)
   - 8.1 [Monthly Reports](#81-monthly-reports)
   - 8.2 [Yearly Reports](#82-yearly-reports)
   - 8.3 [Category Reports](#83-category-reports)
   - 8.4 [Year Comparison Reports](#84-year-comparison-reports)
   - 8.5 [Exporting Reports](#85-exporting-reports)
   - 8.6 [Printing Reports](#86-printing-reports)

9. [Security](#9-security)
   - 9.1 [Viewing Security Logs](#91-viewing-security-logs)
   - 9.2 [Managing Alerts](#92-managing-alerts)
   - 9.3 [Understanding Security Score](#93-understanding-security-score)
   - 9.4 [Session Management](#94-session-management)

10. [Troubleshooting](#10-troubleshooting)
    - 10.1 [Login Issues](#101-login-issues)
    - 10.2 [MFA Problems](#102-mfa-problems)
    - 10.3 [Data Not Showing](#103-data-not-showing)
    - 10.4 [Export Problems](#104-export-problems)
    - 10.5 [Getting Help](#105-getting-help)

11. [FAQ](#11-faq)
    - 11.1 [General Questions](#111-general-questions)
    - 11.2 [Account Questions](#112-account-questions)
    - 11.3 [Feature Questions](#113-feature-questions)
    - 11.4 [Security Questions](#114-security-questions)

---

## 1. Getting Started

### 1.1 Creating an Account

To start using IFMS, you'll need to create an account:

1. Navigate to the IFMS application URL
2. Click on **"Sign Up"** or **"Create Account"** button
3. Fill in the registration form:

![Registration Form](../assets/images/register-form.png)

| Field | Description | Requirements |
|-------|-------------|--------------|
| Username | Your unique identifier | 3-50 characters, alphanumeric |
| Email | Your email address | Valid email format |
| Password | Your secure password | Min 8 chars, 1 uppercase, 1 number |
| Full Name | Your name (optional) | Max 100 characters |

4. Click **"Sign Up"** to create your account
5. You'll see a success message and be redirected to the login page

**Password Strength Indicator:**
The password field includes a strength meter that shows:
- **Red**: Weak password
- **Orange**: Fair password
- **Blue**: Good password
- **Green**: Strong password

### 1.2 Logging In

Once you have an account, you can log in:

1. Go to the login page
2. Enter your username and password
3. Click **"Sign In"**

![Login Form](../assets/images/login-form.png)

**If you have MFA enabled:**
- After entering your credentials, you'll be prompted to enter a 6-digit code from your authenticator app
- Enter the code and click **"Verify Code"**

**If you don't have MFA enabled:**
- You'll be logged in directly and redirected to the dashboard

### 1.3 Setting Up Multi-Factor Authentication

MFA adds an extra layer of security to your account:

1. Log in to your account
2. Navigate to **Profile** from the sidebar
3. Scroll to the **"Two-Factor Authentication"** section
4. Click **"Setup MFA"**

![MFA Setup](../assets/images/mfa-setup.png)

5. You'll see a QR code and a secret key
6. Open Google Authenticator (or any TOTP app) on your phone
7. Scan the QR code or enter the secret key manually
8. The app will generate a 6-digit code
9. Enter the code in the verification field
10. Click **"Verify & Enable"**

Once verified, MFA will be enabled for your account. You'll need to enter a code from your authenticator app every time you log in.

### 1.4 Understanding the Dashboard

The dashboard is your home screen after logging in:

![Dashboard](../assets/images/dashboard.png)

**Key elements:**

1. **Sidebar Navigation**: Access all features:
   - Dashboard
   - Transactions
   - Analysis
   - Predictions
   - Financial Advice
   - Budget Planner
   - Reports
   - Security
   - Profile

2. **Header**:
   - Menu button (mobile)
   - Notifications
   - User menu

3. **Summary Cards**:
   - Total Balance
   - Monthly Income
   - Monthly Expenses
   - Savings Rate

4. **Charts**:
   - Spending by Category (pie chart)
   - Monthly Trend (line chart)

5. **Recent Transactions**:
   - Latest 5 transactions
   - Date, description, category, amount

---

## 2. Managing Your Profile

### 2.1 Viewing Profile Information

To view your profile:

1. Click on **"Profile"** in the sidebar
2. You'll see several sections:
   - Personal Information
   - Security Status
   - Two-Factor Authentication
   - Active Sessions

![Profile Page](../assets/images/profile.png)

### 2.2 Editing Personal Details

To update your personal information:

1. On the Profile page, find the **"Personal Information"** card
2. Click the **"Edit"** button
3. Update the fields you want to change:
   - Full Name
   - Monthly Salary
   - Savings Goal
4. Click **"Save Changes"**

![Edit Profile](../assets/images/edit-profile.png)

### 2.3 Setting Financial Goals

Setting financial goals helps track your progress:

1. In the **"Personal Information"** card, click **"Edit"**
2. Enter your **Monthly Salary** (if not already set)
3. Enter your **Savings Goal** (target amount)
4. Click **"Save Changes"**

Your savings goal progress will appear in:
- Financial Advice page
- Budget Planner page
- Profile page (goal progress section)

### 2.4 Managing MFA Settings

**To enable MFA:**
1. Go to **Profile** → **"Two-Factor Authentication"** card
2. Click **"Setup MFA"**
3. Follow the QR code verification process

**To disable MFA:**
1. Go to **Profile** → **"Two-Factor Authentication"** card
2. Click **"Disable MFA"**
3. Confirm when prompted

![MFA Status](../assets/images/mfa-status.png)

### 2.5 Viewing Active Sessions

The **"Active Sessions"** section shows all devices where you're currently logged in:

- Device/browser information
- IP address
- Last activity time
- Current session indicator

**To log out from other devices:**
1. Click **"Logout All"** button
2. Confirm the action
3. All other sessions will be terminated

---

## 3. Transactions

### 3.1 Adding a Transaction

To add a new transaction:

1. Go to **Transactions** from the sidebar
2. Click the **"Add Transaction"** button
3. Fill in the transaction details:

![Add Transaction Modal](../assets/images/add-transaction.png)

| Field | Description | Example |
|-------|-------------|---------|
| Amount | Transaction amount | 45.99 |
| Category | Select from dropdown | Food & Dining |
| Description | Optional notes | Grocery shopping |
| Date | Transaction date | 2024-03-15 |

4. Click **"Add"** to save

**Note:** The system automatically determines if it's income or expense based on the category selected.

### 3.2 Viewing Transactions

The Transactions page shows all your transactions:

![Transactions List](../assets/images/transactions.png)

**Columns:**
- Date
- Description
- Category (color-coded)
- Amount (green for income, red for expenses)
- Actions (Edit/Delete)

**Pagination:**
- Navigate between pages using the Previous/Next buttons
- Shows current page and total pages

### 3.3 Filtering Transactions

You can filter transactions using the filter bar:

![Transaction Filters](../assets/images/transaction-filters.png)

**Available filters:**
- **Month/Year**: Select specific month
- **Category**: Filter by expense/income category
- **Type**: Income or Expense only
- **Search**: Search in descriptions

**To apply filters:**
1. Select your filter criteria
2. The table updates automatically
3. Clear filters by resetting selections

### 3.4 Editing a Transaction

To edit a transaction:

1. Find the transaction in the list
2. Click the **Edit** icon (pencil) in the Actions column
3. Update the fields you want to change
4. Click **"Update"**

![Edit Transaction](../assets/images/edit-transaction.png)

### 3.5 Deleting a Transaction

To delete a transaction:

1. Find the transaction in the list
2. Click the **Delete** icon (trash) in the Actions column
3. Confirm when prompted
4. The transaction is permanently removed

### 3.6 Understanding Categories

Categories help organize your spending:

**Expense Categories:**
- Food & Dining
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Education
- Rent/Mortgage
- Insurance
- Personal Care
- Gifts & Donations
- Travel
- Other Expenses

**Income Categories:**
- Salary
- Freelance
- Investment
- Business
- Gift
- Refund
- Other Income

Categories are color-coded in the interface:
- **Blue**: Expense categories
- **Green**: Income categories

### 3.7 Exporting Transactions

To export your transactions:

1. On the Transactions page, click the **"Export"** button
2. A CSV file will be downloaded automatically
3. Filename format: `transactions_MONTH_YEAR.csv`

The exported file contains:
- Date
- Description
- Category
- Amount
- Type (income/expense)

---

## 4. Spending Analysis

### 4.1 Overview Dashboard

The Analysis page starts with an overview:

![Analysis Overview](../assets/images/analysis-overview.png)

**Average Monthly Stats:**
- Average Income
- Average Expenses
- Average Savings

**6-Month Trend Chart:**
- Income (green line)
- Expenses (red line)
- Savings (blue line)

**Key Insights:**
- Automated insights about your spending
- Trends and patterns identified

### 4.2 Category Breakdown

The **Categories** tab shows your spending by category:

![Category Breakdown](../assets/images/category-breakdown.png)

**Features:**
- **Pie Chart**: Visual representation of spending distribution
- **Category List**: Detailed breakdown with:
  - Category name
  - Percentage of total
  - Amount spent
  - Number of transactions
  - Progress bar visualization

**To view category details:**
1. Click on the **Categories** tab
2. Select a month/year using the date selector
3. Hover over pie chart slices for details

### 4.3 Monthly Trends

The **Trends** tab shows how your spending changes over time:

![Spending Trends](../assets/images/spending-trends.png)

**Trend Cards:**
- **Increasing** (red border): Spending is going up
- **Decreasing** (green border): Spending is going down
- **Stable** (orange border): Spending is consistent

Each card shows:
- Category name
- Current monthly average
- Previous monthly average
- Percentage change
- Volatility measure

### 4.4 Spending Patterns

The **Patterns** tab reveals when you spend:

![Spending Patterns](../assets/images/spending-patterns.png)

**Patterns analyzed:**
- **Weekday vs Weekend**: Compare spending on weekdays vs weekends
- **Day of Week**: Bar chart showing average spending by day
- **Month Halves**: Compare first half vs second half of month

**Insights provided:**
- "You spend 35% more on weekends"
- "Highest spending on Fridays"
- "You spend more in the second half of the month"

### 4.5 Period Comparison

The **Compare** tab lets you compare two periods:

![Period Comparison](../assets/images/period-comparison.png)

**How to use:**
1. Select current period (month/year)
2. Select previous period (month/year)
3. View comparison results:

**Comparison shows:**
- Overall change percentage
- Category comparison chart
- Detailed table with changes per category

---

## 5. Expense Predictions

### 5.1 Understanding Predictions

The Predictions page uses machine learning to forecast your future expenses:

![Predictions Page](../assets/images/predictions.png)

**Three prediction methods:**
- **Ensemble**: Combines multiple methods for best accuracy
- **By Category**: Predictions broken down by category
- **3-Month Outlook**: Future projections

### 5.2 Next Month Prediction

The **Ensemble** tab shows the main prediction:

![Next Month Prediction](../assets/images/next-month-prediction.png)

**Elements:**
- **Prediction Card**: Shows predicted amount for next month
- **Confidence Badge**: High/Medium/Low confidence indicator
- **Trend Indicator**: Whether spending is trending up/down
- **Details**: Expected transactions count, average per transaction

**Historical Trend Chart:**
- Shows your actual spending over time
- Red dot marks the predicted next month
- Dotted line extends the trend

### 5.3 Category Predictions

The **By Category** tab shows predictions for each category:

![Category Predictions](../assets/images/category-predictions.png)

**Features:**
- **Total Predicted**: Sum of all category predictions
- **Category Chart**: Bar chart of predicted amounts
- **Category List**: Detailed breakdown with:
  - Category name
  - Predicted amount
  - Confidence dot (color-coded)
  - Trend indicator
  - Progress bar showing proportion

### 5.4 3-Month Outlook

The **3-Month Outlook** tab shows future projections:

![3-Month Outlook](../assets/images/3-month-outlook.png)

**Timeline view:**
- Each month as a card
- Predicted amount
- Confidence percentage
- Confidence decreases with time:
  - Month 1: Highest confidence
  - Month 2: Medium confidence
  - Month 3: Lowest confidence

### 5.5 Confidence Levels

Understanding prediction confidence:

| Level | Color | Meaning |
|-------|-------|---------|
| **High** | Green | Reliable prediction based on consistent data |
| **Medium** | Orange | Moderate confidence, some variability |
| **Low** | Red | High uncertainty, use with caution |

**Factors affecting confidence:**
- Amount of historical data
- Spending volatility
- R² score of the model
- Data consistency

---

## 6. Financial Advice

### 6.1 Financial Health Score

The Financial Advice page starts with your health score:

![Financial Health Score](../assets/images/health-score.png)

**Score ranges:**
- **80-100**: Excellent
- **60-79**: Good
- **40-59**: Fair
- **0-39**: Needs Improvement

**Score factors:**
- Savings rate
- Essentials ratio
- Emergency fund size
- Spending consistency
- Goal progress

### 6.2 Personalized Recommendations

The **Overview** tab shows prioritized recommendations:

![Recommendations](../assets/images/recommendations.png)

**Priority levels:**
- **High** (red): Immediate attention needed
- **Medium** (orange): Address soon
- **Low** (green): Good to consider

**Each recommendation includes:**
- Title
- Description
- Suggestion for improvement
- Action button (when applicable)

### 6.3 Budget Suggestions (50/30/20 Rule)

The **Budget** tab applies the 50/30/20 rule:

![Budget Suggestions](../assets/images/budget-suggestions.png)

**The rule:**
- **50%** for Needs (essentials)
- **30%** for Wants (discretionary)
- **20%** for Savings

**Visualization:**
- Colored bars showing the rule
- Comparison bars showing your actual spending
- Target markers for each category
- Status indicators (Over/Under)

**Suggested adjustments:**
- Specific recommendations for each category
- Amount to adjust
- Actionable suggestion

### 6.4 Overspending Alerts

The **Budget** tab also shows overspending:

![Overspending Alerts](../assets/images/overspending.png)

**Severity levels:**
- **High**: >50% increase
- **Medium**: 20-50% increase

**Each alert shows:**
- Category name
- Percentage increase
- Last month amount
- Current month amount
- Excess amount

### 6.5 Savings Opportunities

The **Savings** tab identifies money-saving opportunities:

![Savings Opportunities](../assets/images/savings-opportunities.png)

**Types of opportunities:**
- **Subscriptions**: Recurring services you might not use
- **High Spending**: Categories with above-average spending

**Each opportunity shows:**
- Description/Category
- Monthly cost/average
- Annual cost (for subscriptions)
- Suggestion for action

### 6.6 Emergency Fund Tracking

The **Savings** tab also tracks your emergency fund:

![Emergency Fund](../assets/images/emergency-fund.png)

**Status indicators:**
- **Healthy**: 6+ months covered
- **Adequate**: 3-6 months covered
- **Needs Attention**: 1-3 months covered
- **Critical**: <1 month covered

**Display:**
- Progress circle showing months covered
- Current amount
- Target amount
- Status badge

---

## 7. Budget Planning

### 7.1 Viewing Your Monthly Budget

The Budget Planner page shows your current month's budget:

![Monthly Budget](../assets/images/monthly-budget.png)

**Current Status Alert:**
- Green: "On Track" - spending within budget
- Red: "Behind Budget" - overspending detected

**Summary Cards:**
- Total Income
- Total Budgeted
- Projected Savings
- Savings Rate

### 7.2 Understanding Category Allocations

The budget breaks down by category:

![Category Budgets](../assets/images/category-budgets.png)

**Each category shows:**
- **Category name** and type (Essential/Want)
- **Allocated amount**
- **Historical average** (for comparison)
- **Notes** explaining the allocation
- **Progress bar** showing spending to date

**Progress bar colors:**
- **Green**: Under budget
- **Orange**: Near budget limit (75-100%)
- **Red**: Over budget

### 7.3 Budget vs Actual Comparison

The **Budget vs Actual** tab compares planned vs actual spending:

![Budget Comparison](../assets/images/budget-comparison.png)

**Summary cards:**
- Total Variance (Under/Over budget)
- Categories Over/Under count
- Actual vs Budgeted Savings

**Comparison chart:**
- Bar chart comparing budgeted vs actual for top categories
- Blue bars: Budgeted
- Red bars: Actual

**Detailed table:**
- Category
- Budgeted amount
- Actual amount
- Difference
- Status badge (over/under)

### 7.4 Creating a Smart Budget

The **Smart Budget** feature creates an optimized budget:

![Smart Budget Modal](../assets/images/smart-budget.png)

**How to use:**
1. Click **"Smart Budget"** button
2. Set your target savings rate (5-50%)
3. Click **"Generate Smart Budget"**

**Results:**
- Optimized allocations for each category
- Comparison with historical averages
- Changes highlighted (green/red)
- On-target indicator

**To apply:** Click **"Apply This Budget"**

### 7.5 Future Budget Projections

The **Future Outlook** tab shows projected budgets:

![Future Budgets](../assets/images/future-budgets.png)

**Each month card shows:**
- Month and Year
- Confidence badge (High/Medium/Low)
- Total budget
- Projected savings
- Savings rate
- Number of categories

**Confidence levels:**
- Month 1: High confidence
- Month 2: Medium confidence
- Month 3: Low confidence

### 7.6 Budget Tips

The budget page includes helpful tips:

![Budget Tips](../assets/images/budget-tips.png)

**Tip types:**
- Savings rate encouragement
- Category-specific suggestions
- Emergency fund reminders
- Goal progress updates

---

## 8. Reports

### 8.1 Monthly Reports

The **Monthly Report** provides a comprehensive view of a single month:

![Monthly Report](../assets/images/monthly-report.png)

**Sections:**
- **Summary Cards**: Income, Expenses, Savings, Savings Rate
- **Category Breakdown**: Pie chart and detailed table
- **Key Insights**: Automated observations
- **Daily Spending**: Grid showing spending by day

**To generate:**
1. Select **Monthly Report** from report types
2. Choose month and year
3. View the generated report

### 8.2 Yearly Reports

The **Yearly Report** shows your entire year at a glance:

![Yearly Report](../assets/images/yearly-report.png)

**Sections:**
- **Yearly Summary**: Total income, expenses, savings
- **Monthly Trend Chart**: Line chart of income vs expenses
- **Monthly Breakdown**: Table with month-by-month data
- **Year in Review**: Key insights and patterns
- **Seasonal Patterns**: Quarter-by-quarter analysis

**To generate:**
1. Select **Yearly Report** from report types
2. Choose year
3. View the generated report

### 8.3 Category Reports

The **Category Report** focuses on a specific category:

![Category Report](../assets/images/category-report.png)

**Sections:**
- **Category Summary**: Total spent, monthly average, transactions, trend
- **Monthly Trend Chart**: Line chart of spending over time
- **Monthly Breakdown**: Table with month-by-month data
- **Recent Transactions**: Latest transactions in this category
- **Advice**: Category-specific financial advice

**To generate:**
1. Select **Category Report** from report types
2. Choose a category
3. View the generated report

### 8.4 Year Comparison Reports

The **Year Comparison** report compares two years:

![Year Comparison](../assets/images/year-comparison.png)

**Sections:**
- **Comparison Summary**: Percentage changes for income, expenses, savings
- **Category Comparison Chart**: Bar chart comparing categories
- **Monthly Comparison**: Table comparing month by month
- **Category Changes**: Detailed table of changes by category

**To generate:**
1. Select **Year Comparison** from report types
2. Choose Year 1 and Year 2
3. View the generated report

### 8.5 Exporting Reports

To export a report:

1. Generate the report you want to export
2. Choose export format from the dropdown:
   - **JSON**: Raw data format
   - **CSV**: Spreadsheet-compatible format
   - **PDF**: Printable document
3. Click **"Export"**
4. File will download automatically

**Export tips:**
- Use CSV for spreadsheet analysis
- Use PDF for sharing/printing
- Use JSON for data backup

### 8.6 Printing Reports

To print a report:

1. Generate the report you want to print
2. Click the **"Print"** button
3. Use your browser's print dialog to:
   - Select printer
   - Choose layout (portrait/landscape)
   - Adjust scale if needed
4. Click **"Print"**

**Print preview** will show the report formatted for paper:
- Clean layout
- All charts included
- Proper margins

---

## 9. Security

### 9.1 Viewing Security Logs

The Security page shows your security events:

![Security Logs](../assets/images/security-logs.png)

**Logs include:**
- Login attempts (success/failure)
- MFA events
- Password changes
- Session management

**Each log shows:**
- Event type
- Status (success/failure)
- Date and time
- IP address
- Device/browser

### 9.2 Managing Alerts

Security alerts notify you of suspicious activity:

![Security Alerts](../assets/images/security-alerts.png)

**Alert types:**
- Multiple failed logins
- Suspicious IP activity
- MFA failures
- New device login

**To resolve an alert:**
1. Click on the alert to investigate
2. If legitimate, click **"Resolve"**
3. Add notes about your investigation
4. Alert will be marked as resolved

### 9.3 Understanding Security Score

Your security score rates account safety:

![Security Score](../assets/images/security-score.png)

**Score factors:**
- MFA status (+15 points if enabled)
- Active sessions (-10 for >3 sessions)
- Failed logins (-20 for >5 in 24h)
- Active alerts (-15 per alert)

**Score ranges:**
- 80-100: Excellent security
- 60-79: Good security
- 40-59: Fair security
- Below 40: Needs improvement

### 9.4 Session Management

The **Active Sessions** section shows where you're logged in:

![Active Sessions](../assets/images/active-sessions.png)

**For each session:**
- Device/browser info
- IP address
- Last activity time
- Current session indicator

**Actions:**
- **Logout All**: End all other sessions
- Sessions automatically expire after 1 hour of inactivity

---

## 10. Troubleshooting

### 10.1 Login Issues

**Problem: "Invalid username or password"**
- Check Caps Lock
- Verify username spelling
- Try password reset
- Clear browser cache

**Problem: Account locked**
- Too many failed attempts
- Wait 15 minutes
- Contact support if persists

**Problem: Can't remember password**
- Use password reset (if available)
- Contact support

### 10.2 MFA Problems

**Problem: Lost access to authenticator app**
- Use backup codes (if saved)
- Contact support for reset

**Problem: Code not working**
- Ensure time sync on phone (Google Authenticator > Settings > Time correction)
- Try generating a new code
- Check you're using the correct account

**Problem: QR code won't scan**
- Click to show secret key
- Enter manually in authenticator app
- Ensure good lighting and focus

### 10.3 Data Not Showing

**Problem: Transactions missing**
- Check selected month/year filter
- Verify you're in the correct account
- Try refreshing the page

**Problem: Charts not loading**
- Check internet connection
- Clear browser cache
- Try different browser

**Problem: Predictions not available**
- Need at least 3 months of data
- Add more transactions
- Check prediction health indicator

### 10.4 Export Problems

**Problem: Export button not working**
- Check browser pop-up blocker
- Try different browser
- Clear browser cache

**Problem: PDF export blank**
- Ensure report has data
- Try smaller date range
- Check browser print settings

**Problem: CSV format issues**
- Open in spreadsheet software
- Check delimiter settings (comma-separated)
- Ensure proper encoding (UTF-8)

### 10.5 Getting Help

**Self-help options:**
- Check this user guide
- Review FAQ section
- Check browser console for errors

**Contact support:**
- Email: support@ifms.com
- Include: Username, issue description, screenshots
- Response time: Within 24 hours

---

## 11. FAQ

### 11.1 General Questions

**Q: Is IFMS free to use?**
A: Yes, IFMS is completely free for personal use.

**Q: Do I need to install anything?**
A: No, IFMS runs in your web browser. Just visit the website.

**Q: Which browsers are supported?**
A: Chrome, Firefox, Safari, and Edge (latest versions).

**Q: Is my data backed up?**
A: Yes, automatic backups run daily.

### 11.2 Account Questions

**Q: Can I have multiple accounts?**
A: Yes, you can create multiple accounts with different email addresses.

**Q: What if I forget my password?**
A: Contact support for password reset assistance.

**Q: How do I delete my account?**
A: Contact support to request account deletion.

**Q: Can I change my username?**
A: Usernames cannot be changed after creation.

### 11.3 Feature Questions

**Q: How accurate are predictions?**
A: Predictions are typically 70-85% accurate with sufficient data.

**Q: How much data do I need for predictions?**
A: At least 3 months of transactions for basic predictions.

**Q: Can I track investments?**
A: Not in the current version (planned for future).

**Q: Can I import bank statements?**
A: Not yet, but you can manually add transactions.

### 11.4 Security Questions

**Q: Is MFA really necessary?**
A: Highly recommended for financial accounts. It adds essential security.

**Q: What if I lose my phone with authenticator?**
A: Contact support immediately for account recovery.

**Q: Who can see my financial data?**
A: Only you. Your data is private and encrypted.

**Q: Is my data encrypted?**
A: Yes, all data is encrypted at rest and in transit.

---

## 12. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + D` | Go to Dashboard |
| `Ctrl + T` | Go to Transactions |
| `Ctrl + A` | Go to Analysis |
| `Ctrl + P` | Go to Predictions |
| `Ctrl + F` | Go to Financial Advice |
| `Ctrl + B` | Go to Budget Planner |
| `Ctrl + R` | Go to Reports |
| `Ctrl + S` | Go to Security |
| `Ctrl + Shift + P` | Go to Profile |
| `Ctrl + /` | Show shortcuts |
| `Esc` | Close modal/panel |

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **MFA** | Multi-Factor Authentication - requires two forms of verification |
| **TOTP** | Time-based One-Time Password - used by authenticator apps |
| **JWT** | JSON Web Token - used for authentication |
| **50/30/20 Rule** | Budgeting rule: 50% needs, 30% wants, 20% savings |
| **Ensemble** | Combining multiple prediction methods for better accuracy |
| **Volatility** | Measure of how much spending varies |
| **R² Score** | Statistical measure of prediction accuracy |
| **Emergency Fund** | Savings for unexpected expenses |

---

## 14. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Feb 2026 | Initial release |

---

**✅ STEP D6 COMPLETE!**

You now have:
- ✅ Complete user guide with 14 sections
- ✅ Getting started instructions
- ✅ Profile management guide
- ✅ Transaction management guide
- ✅ Analysis and predictions guide
- ✅ Financial advice guide
- ✅ Budget planning guide
- ✅ Reports guide
- ✅ Security guide
- ✅ Troubleshooting section
- ✅ FAQ section
- ✅ Keyboard shortcuts
- ✅ Glossary
- ✅ Placeholder for screenshots

**Next Step (D7)**: We'll create the Deployment Guide

Let me know when you're ready for Step D7!