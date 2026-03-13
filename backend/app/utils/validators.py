from datetime import datetime

def validate_transaction(data):
    """Validate transaction data"""
    errors = []
    
    print(f"Validating data: {data}")  # Debug log
    
    # Check required fields
    required_fields = ['amount', 'category', 'date']
    for field in required_fields:
        if field not in data:
            errors.append(f"{field} is required")
            print(f"Missing field: {field}")
    
    if errors:
        return False, errors
    
    # Validate amount
    try:
        amount = float(data['amount'])
        print(f"Amount parsed: {amount}")
        if amount <= 0:
            errors.append("Amount must be greater than 0")
    except (ValueError, TypeError) as e:
        print(f"Amount error: {e}")
        errors.append("Amount must be a valid number")
    
    # Validate category - just check it's not empty
    category = data.get('category', '')
    if not category or not str(category).strip():
        errors.append("Category cannot be empty")
        print("Category is empty")
    
    # Validate date
    try:
        date_str = data.get('date', '')
        print(f"Date string: {date_str}")
        datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError) as e:
        print(f"Date error: {e}")
        errors.append("Date must be in YYYY-MM-DD format")
    
    # Validate description length if provided
    if 'description' in data and data['description']:
        if len(data['description']) > 200:
            errors.append("Description must be less than 200 characters")
    
    print(f"Final errors: {errors}")
    return len(errors) == 0, errors