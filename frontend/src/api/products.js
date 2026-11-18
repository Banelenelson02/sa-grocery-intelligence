import { get } from './client'

export function fetchProducts() {
  return get('/products')
}

// Keep the name used by the catalogue and product detail pages.
export const getProducts = fetchProducts
