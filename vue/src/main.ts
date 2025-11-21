import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
// import store from './store'
import './assets/scss/app.scss'

import 'leaflet/dist/leaflet.css'

import Buefy from 'buefy'
import 'buefy/dist/buefy.css'

import VueGtag from 'vue-gtag-next'

import titleMixin from './mixins/titleMixin'

const app = createApp(App)
app.mixin(titleMixin)
app.use(VueGtag, {
  property: { id: 'G-X1CBD2T8XH' }
})
app.use(Buefy)
app.use(router)
// app.use(store)

app.mount('#app')
