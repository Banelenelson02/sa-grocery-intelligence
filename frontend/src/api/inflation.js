import { get } from './client'

export function fetchInflation(months = 6, storeName = null) {
  const params = new URLSearchParams({ months })
  if (storeName) params.set('store_name', storeName)
  return get(`/inflation?${params.toString()}`)
}
