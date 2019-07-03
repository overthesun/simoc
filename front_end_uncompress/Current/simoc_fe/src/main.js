import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store/index.js";

Vue.config.productionTip = false;

import { library } from '@fortawesome/fontawesome-svg-core'
import {faExclamationCircle} from '@fortawesome/pro-light-svg-icons'
import {faBackward,faForward,faPause,faPlay,faTimes,faBars,faArrowLeft,faArrowRight,faCircle,faPlusCircle,faTrash} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon, FontAwesomeLayers } from '@fortawesome/vue-fontawesome'

library.add(faPlay,faTimes,faExclamationCircle,faBars,faArrowLeft,faArrowRight,faBackward,faForward,faPause,faCircle,faPlusCircle,faTrash)

Vue.component('fa-icon', FontAwesomeIcon)
Vue.component('fa-layers',FontAwesomeLayers)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
