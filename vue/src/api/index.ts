import axios from 'axios'

// Cannot set directly because different running locally (localhost:5000) and in production (sandpiper.qut.edu.au)
let API_URL = 'unset'
if (import.meta.env.PROD) {
  const raw = import.meta.env.VITE_API_URL
  // Allow raw to be passed already with scheme
  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    API_URL = `${raw.replace(/\/$/,'')}/api`
  } else {
    // Use http for localhost or anything containing a port (internal docker host like api:5000)
    const hasPort = raw.includes(':')
    const useHttps = !raw.includes('localhost') && !hasPort
    API_URL = `${useHttps ? 'https' : 'http'}://${raw}/api`
  }
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

export function fetchRunCondensed (runId: string, taxonomyType: string) {
  return axios.get(`${API_URL}/condensed/${runId}?taxonomy_type=${taxonomyType}`)
}

export function fetchProjectMetadata (model_bioproject: string) {
  return axios.get(`${API_URL}/project?model_bioproject=${model_bioproject}`)
}

export function fetchRunsByTaxonomy (
  taxonomy: string,
  taxonomyType: string,
  page: number,
  sortField: string,
  sortDirection: string,
  pageSize: number
) {
  return axios.get(`${API_URL}/taxonomy_search_run_data/${taxonomy}?taxonomy_type=${taxonomyType}&sort_field=${sortField}&sort_direction=${sortDirection}&page=${page}&page_size=${pageSize}`)
}

export function fetchGlobalDataByTaxonomy (taxonomy: string, taxonomyType: string) {
  return axios.get(`${API_URL}/taxonomy_search_global_data/${taxonomy}?taxonomy_type=${taxonomyType}`)
}

export function fetchTaxonomySearchHints (taxonomy: string, taxonomyType?: string) {
  const taxonomyTypeParam = taxonomyType ? `?taxonomy_type=${taxonomyType}` : ''
  return axios.get(`${API_URL}/taxonomy_search_hints/${taxonomy}${taxonomyTypeParam}`)
}

export function fetchRandomAccession(host: boolean, ecological: boolean, two_gbp: boolean) {
  return axios.get(`${API_URL}/random_run?host=${host}&ecological=${ecological}&two_gbp=${two_gbp}`)
}

export function fetchAccession(accession: string) {
  return axios.get(`${API_URL}/accession/${accession}`)
}

export function verifyRecaptcha (token: string) {
  return axios.post(`${API_URL}/verify-recaptcha`, {
    token
  })
}
