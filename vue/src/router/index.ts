import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import Run from '../views/Run.vue'
import SearchResults from '../views/SearchResult.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/search',
    name: 'Search',
    component: Search
  },
  {
    path: '/taxonomy/:taxonomy',
    name: 'SearchResults',
    component: SearchResults,
    props: true
  },
  {
    path: '/run/:accession',
    name: 'Run',
    component: Run,
    props: true
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
