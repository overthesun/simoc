import Vue from 'vue'
import Vuex from 'vuex'
import modules from './modules'

Vue.use(Vuex)
export default new Vuex.Store({
    modules,
    state:{
        useLocalHost:true,
        localHost:"http://localhost:8000"
    },  
    mutations: {},
    actions: {},
    getters:{
        getUseLocalHost: state => state.useLocalHost,
        getLocalHost: state => state.localHost,
    }
})