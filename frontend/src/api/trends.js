import { get } from './client'

export function fetchTrends(productId, weeks = 12) {
  return get(`/trends?product_id=${productId}&weeks=${weeks}`)
}
