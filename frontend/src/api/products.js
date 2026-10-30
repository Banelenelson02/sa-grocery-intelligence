import { get } from './client'

export function getProducts() {
  return get('/products')
}
