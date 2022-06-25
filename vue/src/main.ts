import Vue from 'vue'
import App from './App.vue'
import router from './router'
// import store from './store'
import './assets/scss/app.scss'

import 'leaflet/dist/leaflet.css'

import Buefy from 'buefy'
import 'buefy/dist/buefy.css'

import VueGtag from "vue-gtag";

Vue.use(VueGtag, {
  config: { id: "G-X1CBD2T8XH" }
});

Vue.use(Buefy)

Vue.config.productionTip = process.env.NODE_ENV === 'production'

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  // store,
  components: { App },
  template: '<App/>',
  render: h => h(App)
})
