import Vue from 'vue'
import Vuex from 'vuex'

// imports of AJAX functions will go here
import { fetchCondensed } from '../api'

Vue.use(Vuex)

const state = {
  // set this to null rather than {} fixed some loading issues where sunburst
  // didn't show up on refresh/hard refresh. Was easy to reproduce
  currentCondensed: null
}

const actions = {
  // asynchronous operations
  loadCondensed (context: { commit: (arg0: string, arg1: { condensed: any }) => void }, id: string) {
    return fetchCondensed(id)
      .then((response) => {
        context.commit('setCondensed', { condensed: response.data })
      })
  }
}

const mutations = {
  // isolated data mutations
  setCondensed (state: { currentCondensed: any }, payload: { condensed: any }): void {
    state.currentCondensed = payload.condensed
  }
}

const getters = {
  // reusable data accessors
}

const store = new Vuex.Store({
  state,
  actions,
  mutations,
  getters
})

export default store
