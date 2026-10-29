import { post } from './client'

export function optimizeBasket(items, budget) {
  return post('/basket', { items, budget })
}
