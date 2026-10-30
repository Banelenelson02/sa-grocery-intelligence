import { get } from './client'

export function getProducts(params = {}) {
  const query = new URLSearchParams()

  if (params.search?.trim()) {
    query.set('search', params.search.trim())
  }

  if (params.category && params.category !== 'All') {
    query.set('category', params.category)
  }

  const suffix = query.toString()
  return get(`/products${suffix ? `?${suffix}` : ''}`)
}
