/**
 * Currency utility for Zambian Kwacha (ZMK)
 */

export const formatZMK = (amount, options = {}) => {
  const {
    symbol = 'ZMK',
    decimals = 2,
    compact = false,
    label = 'Kwacha'
  } = options;
  if (amount === null || amount === undefined) return `${symbol} 0.00`;
  if (compact && Math.abs(amount) >= 1000000) {
    return `${symbol} ${(amount / 1000000).toFixed(1)}M`;
  }
  if (compact && Math.abs(amount) >= 1000) {
    return `${symbol} ${(amount / 1000).toFixed(1)}K`;
  }
  return `${symbol} ${amount.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
};

export const formatKwacha = (amount, compact = false) => {
  return formatZMK(amount, { symbol: 'ZMK', compact });
};

export const parseZMK = (value) => {
  if (typeof value === 'number') return value;
  // Remove 'ZMK', commas and convert
  const cleaned = String(value)
    .replace(/[ZMK\s,]/g, '')
    .trim();
  return parseFloat(cleaned) || 0;
};

// Zambian salary guide
export const ZAMBIAN_SALARY_GUIDE = {
  entryLevel: { min: 2500, max: 4000, label: 'Entry Level' },
  midLevel: { min: 4500, max: 8000, label: 'Mid Level' },
  seniorLevel: { min: 8500, max: 15000, label: 'Senior Level' },
  executive: { min: 16000, max: 30000, label: 'Executive' }
};

// Zambian expense categories with typical ranges
export const ZAMBIAN_EXPENSE_CATEGORIES = [
  { name: 'Rent/Mortgage', typicalRange: [1500, 6000], type: 'essential' },
  { name: 'Electricity (ZESCO)', typicalRange: [300, 800], type: 'essential' },
  { name: 'Water', typicalRange: [80, 200], type: 'essential' },
  { name: 'Internet', typicalRange: [350, 600], type: 'essential' },
  { name: 'Mobile Data', typicalRange: [100, 300], type: 'essential' },
  { name: 'Groceries', typicalRange: [800, 2500], type: 'essential' },
  { name: 'Transport', typicalRange: [300, 1500], type: 'essential' },
  { name: 'Restaurants', typicalRange: [200, 800], type: 'want' },
  { name: 'Entertainment', typicalRange: [200, 600], type: 'want' },
  { name: 'Shopping', typicalRange: [300, 1500], type: 'want' },
  { name: 'School Fees', typicalRange: [1000, 5000], type: 'essential' },
  { name: 'Medical', typicalRange: [200, 1500], type: 'essential' },
];