// There's no GET /products endpoint yet, so the frontend has no way to look
// up product names/categories from the API. This mirrors db/seed/products.sql
// as a stand-in -- once a real endpoint exists, swap any usage of this file
// for a fetch call instead.
export const KNOWN_PRODUCTS = [
  { id: 1, name: 'White Bread 700g', category: 'Staples' },
  { id: 2, name: 'Maize Meal 5kg', category: 'Staples' },
  { id: 3, name: 'Full Cream Milk 2L', category: 'Dairy' },
  { id: 4, name: 'Cheddar Cheese 400g', category: 'Dairy' },
  { id: 5, name: 'Chicken Breasts 1kg', category: 'Meat' },
  { id: 6, name: 'Beef Mince 500g', category: 'Meat' },
  { id: 7, name: 'Rice 2kg', category: 'Staples' },
  { id: 8, name: 'Cooking Oil 750ml', category: 'Staples' },
  { id: 9, name: 'Tomatoes 1kg', category: 'Produce' },
  { id: 10, name: 'Bananas 1kg', category: 'Produce' },
]

export const KNOWN_CATEGORIES = [...new Set(KNOWN_PRODUCTS.map((p) => p.category))]
