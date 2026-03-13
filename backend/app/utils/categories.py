# Available transaction categories
EXPENSE_CATEGORIES = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    'Entertainment',
    'Bills & Utilities',
    'Healthcare',
    'Education',
    'Rent/Mortgage',
    'Insurance',
    'Personal Care',
    'Gifts & Donations',
    'Travel',
    'Other Expenses'
]

INCOME_CATEGORIES = [
    'Salary',
    'Freelance',
    'Investment',
    'Business',
    'Gift',
    'Refund',
    'Other Income'
]

ALL_CATEGORIES = EXPENSE_CATEGORIES + INCOME_CATEGORIES

def get_category_type(category):
    """Determine if category is expense or income"""
    if category in EXPENSE_CATEGORIES:
        return 'expense'
    elif category in INCOME_CATEGORIES:
        return 'income'
    else:
        return 'unknown'

def validate_category(category):
    """Validate if category exists"""
    return category in ALL_CATEGORIES

def get_expense_categories():
    """Get all expense categories"""
    return EXPENSE_CATEGORIES

def get_income_categories():
    """Get all income categories"""
    return INCOME_CATEGORIES