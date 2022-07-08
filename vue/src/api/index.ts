import axios from 'axios'

let API_URL = 'unset'
if (process.env.NODE_ENV === 'production') {
  API_URL = `https://${process.env.VUE_APP_API_URL}/api`
} else {
  API_URL = 'http://localhost:5000/api'
}

export function api_url () {
  return API_URL
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

export function fetchProjectMetadata (model_bioproject: string) {
  return axios.get(`${API_URL}/project?model_bioproject=${model_bioproject}`)
}

export function fetchOtus (runId: string) {
  return axios.get(`${API_URL}/full_profile/${runId}`)
}

export function fetchRunsByTaxonomy (taxonomy: string, page: number, sortField: string, sortDirection: string, pageSize: number) {
  return axios.get(`${API_URL}/taxonomy_search_run_data/${taxonomy}?sort_field=${sortField}&sort_direction=${sortDirection}&page=${page}&page_size=${pageSize}`)
}

export function fetchGlobalDataByTaxonomy (taxonomy: string) {
  return axios.get(`${API_URL}/taxonomy_search_global_data/${taxonomy}`)
}

export function fetchTaxonomySearchHints (taxonomy: string) {
  return axios.get(`${API_URL}/taxonomy_search_hints/${taxonomy}`)
}

export function fetchRandomAccession(host: boolean, ecological: boolean, two_gbp: boolean) {
  return axios.get(`${API_URL}/random_run?host=${host}&ecological=${ecological}&two_gbp=${two_gbp}`)
}
