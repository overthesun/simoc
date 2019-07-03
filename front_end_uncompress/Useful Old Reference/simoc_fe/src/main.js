import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store/index.js";

Vue.config.productionTip = false;

import { library } from '@fortawesome/fontawesome-svg-core'
import {faExclamationCircle,faUser, faLockAlt,faBars,faArrowAltFromLeft,faArrowAltFromRight,faForward,faBackward,faPlayCircle} from '@fortawesome/pro-light-svg-icons'
import {faTimes,faPlusCircle,faTrash,faCircle} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon, FontAwesomeLayers } from '@fortawesome/vue-fontawesome'

library.add(faExclamationCircle,faTimes,faPlusCircle,faCircle,faUser,faLockAlt,faBars,faArrowAltFromLeft,faArrowAltFromRight,faPlusCircle,faTrash,faForward,faBackward,faPlayCircle)

Vue.component('fa-icon', FontAwesomeIcon)
Vue.component('fa-layers',FontAwesomeLayers)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
