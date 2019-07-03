import Vue from 'vue'
import Vuex from 'vuex'
import modules from './modules'

Vue.use(Vuex)
export default new Vuex.Store({
    modules,
    state:{
        useLocalHost:true,
        localHost:"http://localhost:8000",
        gameID:""
    },  
    mutations: {
        SETGAMEID:function(state,value){
            state.gameID = value
        }
    },
    actions: {},
    getters:{
        getUseLocalHost: state => state.useLocalHost,
        getUseLocalHost: state => state.localHost,
        getGameID: state => state.gameID,
    }
})