import { get } from './client'

export function fetchComparison(category) {
  return get(`/compare?category=${encodeURIComponent(category)}`)
}
