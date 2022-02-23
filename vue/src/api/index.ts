import axios from 'axios'

let API_URL = 'unset'
if (process.env.NODE_ENV === 'production') {
  API_URL = `http://${process.env.BASE_URL}/api`
} else {
  API_URL = 'http://localhost:5000/api'
}

export function fetchSandpiperStats () {
  return axios.get(`${API_URL}/sandpiper_stats`)
}

export function fetchRunMetadata (runId: string) {
  return axios.get(`${API_URL}/metadata/${runId}`)
}

export function fetchRunCondensed (runId: string) {
  return axios.get(`${API_URL}/condensed/${runId}`)
}

export function fetchRunsByTaxonomy (taxonomy: string) {
  return axios.get(`${API_URL}/taxonomy_search/${taxonomy}`)
}

export function fetchTaxonomySearchHints (taxonomy: string) {
  console.log('fetching ' + taxonomy)
  return axios.get(`${API_URL}/taxonomy_search_hints/${taxonomy}`)
}
