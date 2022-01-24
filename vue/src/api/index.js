import axios from 'axios'

const API_URL = "http://127.0.0.1:5000/api"

export function fetchMarkers () {
    return axios.get(`${API_URL}/markers`)
}

export function fetchCondensed (sample_id) {
    return axios.get(`${API_URL}/condensed/${sample_id}`)
}
