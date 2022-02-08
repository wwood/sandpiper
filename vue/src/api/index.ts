import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api'

export function fetchMarkers () {
  return axios.get(`${API_URL}/markers`)
}

export function fetchCondensed (accession: String) {
  return axios.get(`${API_URL}/condensed/${accession}`)
}

export function fetchMetadata (accession: String) {
  return axios.get(`${API_URL}/metadata/${accession}`)
}
