import Vue from "vue";
import Vuex from "vuex";

import ConfigurationOrder from "@/store/modules/configuration-order";
import ConfigurationSession from "@/store/modules/configuration-session";

import modules from './modules'

Vue.use(Vuex);

export default new Vuex.Store({
  state:{
    useLocalHost:true
  },  
  modules:{
    modules
  },
  mutations: {},
  actions: {},
  getters:{
    getLocalHost: state => state.useLocalHost,
  }
});
