import { get } from './client'

export function fetchProducts() {
  return get('/products')
}
