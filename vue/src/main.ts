import Vue from 'vue'
import App from './App.vue'
import router from './router'
// import store from './store'
import './assets/scss/app.scss'

import Buefy from 'buefy'
import 'buefy/dist/buefy.css'
Vue.use(Buefy)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  // store,
  components: { App },
  template: '<App/>',
  render: h => h(App)
})
