"""
Currency utility for handling Zambian Kwacha (ZMK)
"""

class CurrencyFormatter:
    """Format amounts in Zambian Kwacha"""
    
    CURRENCY_SYMBOL = "ZMK"
    CURRENCY_CODE = "ZMK"
    
    @staticmethod
    def format(amount, include_symbol=True):
        """Format amount as ZMK currency string"""
        if include_symbol:
            return f"ZMK {amount:,.2f}"
        return f"{amount:,.2f}"
    
    @staticmethod
    def format_kwacha(amount):
        """Format with Kwacha symbol"""
        return f"Kwacha {amount:,.2f}"
    
    @staticmethod
    def parse(amount_str):
        """Parse ZMK amount string to float"""
        # Remove 'ZMK', 'Kwacha', commas and convert
        cleaned = amount_str.replace('ZMK', '').replace('Kwacha', '').replace(',', '').strip()
        return float(cleaned)

# Zambian-specific category names (optional)
ZAMBIAN_CATEGORIES = {
    'expense': [
        'Rent/Mortgage',
        'Electricity (ZESCO)',
        'Water (LWSC)',
        'Internet',
        'Mobile Data/Airtime',
        'DSTV/GOtv',
        'Groceries (Shoprite/Spar)',
        'Market Shopping',
        'Restaurants',
        'Transport (Fuel/Bus/Taxi)',
        'Entertainment',
        'Shopping',
        'Personal Care',
        'Home Supplies',
        'Medical',
        'School Fees',
        'Wedding/Gifts',
        'Travel',
        'Miscellaneous'
    ],
    'income': [
        'Salary',
        'Business Income',
        'Rental Income',
        'Bonus',
        'Dividends',
        'Tax Refund',
        'Other Income'
    ]
}

# Realistic Zambian salary ranges (monthly, in ZMW)
ZAMBIAN_SALARY_RANGES = {
    'entry_level': (2500, 4000),
    'mid_level': (4500, 8000),
    'senior_level': (8500, 15000),
    'executive': (16000, 30000)
}

# Typical Zambian expense amounts (in ZMW)
ZAMBIAN_EXPENSE_GUIDE = {
    'Rent (Lusaka)': {
        'low': (1500, 2500),
        'medium': (3000, 5000),
        'high': (6000, 10000)
    },
    'Rent (Other towns)': {
        'low': (800, 1500),
        'medium': (1800, 3000),
        'high': (3500, 6000)
    },
    'Groceries (monthly)': {
        'single': (800, 1500),
        'couple': (1500, 2500),
        'family': (2500, 4000)
    },
    'Transport (monthly)': {
        'bus': (300, 600),
        'taxi': (600, 1200),
        'car': (1500, 3000)
    },
    'Utilities (monthly)': {
        'electricity': (300, 800),
        'water': (80, 200),
        'internet': (350, 600)
    }
}