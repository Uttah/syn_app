import Vue from 'vue'
import Vuetify from 'vuetify'
import App from './App.vue'
import VueApollo from 'vue-apollo'
import Meta from 'vue-meta'
import router from './router'
import apolloClient from './apollo-client.js'
import auth from './auth/auth'
import theme from './theme'
import moment from 'moment'
import '../node_modules/vuetify/dist/vuetify.min.css'
import '../node_modules/mdi/css/materialdesignicons.min.css'
import Notifications from 'vue-notification'

auth.client = apolloClient
moment.locale('ru')

Vue.config.productionTip = false
Vue.use(Vuetify, {theme})
Vue.use(VueApollo)
Vue.use(Meta)
Vue.use(Notifications)

const apolloProvider = new VueApollo({
  defaultClient: apolloClient
})

/* eslint-disable no-new */
export default new Vue({
  el: '#app',
  router,
  apolloProvider,
  render: h => h(App)
})
