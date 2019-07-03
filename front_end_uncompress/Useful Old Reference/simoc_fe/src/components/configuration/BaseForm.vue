<template>
    <div class='session-wrapper session-wrapper--form'>
        <div class='content-wrapper content-wrapper--form' v-if="!loading">
            <header class='header'>
                <img src='../../assets/simoc-logo.svg' class='logo'/>
                <div class='title-wrapper'>
                    <div class='title title--normal'>Session Configuration</div>
                    <div class='title title--italic'>{{formTitle}}</div>
                </div>
            </header>
            <main class='main'>
                <keep-alive>
                    <component :is="formElement" :handleEntry="handleEntry" :handleChange="handleChange" :handleIndex="handleIndex" :handleSpecial="handleSpecial"/>
                </keep-alive>
            </main>
            <footer class='footer'>
                <div class='navigation-wrapper navigation-wrapper--left' v-if="lowerBound" @click="decrementIndex">
                    <fa-icon class='fa-icon navigation-icon' :icon="['fal','arrow-alt-from-right']"/>
                    <div class='navigation-title'>{{formPrevious}}</div>
                </div>
                <div class='navigation-wrapper navigation-wrapper--right' v-if="!upperBound" @click="incrementIndex">
                    <div class='navigation-title'>{{formNext}}</div>
                    <fa-icon class='fa-icon navigation-icon' :icon="['fal','arrow-alt-from-left']"/>
                </div>
               <div class='navigation-wrapper navigation-wrapper--right' v-if="upperBound" @click="confirmConfiguration">
                    <div class='navigation-title'>Confirm</div>
                    <fa-icon class='fa-icon navigation-icon' :icon="['fal','arrow-alt-from-left']"/>
                </div>
            </footer>
        </div>
    </div>
</template>

<script>
import {InitialForm,GreenhouseForm,InhabitantsForm,PowerForm,FinalizeForm} from '../forms'
import {mapState,mapGetters,mapActions} from 'vuex'
import axios from 'axios'
export default {
    mounted(){
        this.loading = false
        this.index = this.skipGuidance ? (this.sectionOrder.length-1) : 0
    },

    components:{
        "InitialForm":InitialForm,
        "InhabitantsForm":InhabitantsForm,
        "GreenhouseForm":GreenhouseForm,
        "PowerForm":PowerForm,
        "FinalizeForm":FinalizeForm,
    },

    data(){
        return{
            index: 0,
            loading: true,
            //game_config:{"duration":{"value":90,"type":"day"},"human_agent":{"amount":2},"habitat":"crew_habitat_small","greenhouse":"greenhouse_small","food_storage":{"amount":1000},"solar_arrays":{"amount":3},"power_storage":{"amount":1},"eclss":{"amount":0},"plants":[{"species":"cabbage","amount":100},{"species":"none","amount":0},{"species":"none","amount":0},{"species":"none","amount":0},{"species":"none","amount":0},{"species":"none","amount":0}]}	
        }
    },

    computed:{
        ...mapGetters('guideOrder',['sectionOrder','skipGuidance']), 
        ...mapGetters('configuration',['getFormattedConfiguration']),    
        ...mapGetters(['getLocalHost']),  

        game_config:function(){
            console.log(this.getFormattedConfiguration)
            return this.getFormattedConfiguration
        },

        formElement: function() {
            return this.sectionOrder[this.index].componentName   
        },
        formTitle: function(){
            return this.sectionOrder[this.index].sectionName
        },
        formNext:function(){
            return this.sectionOrder[this.upperLimit].sectionName
        },
        formPrevious:function(){
            return this.sectionOrder[this.lowerLimit].sectionName
        },
        lowerBound: function() {
            return (this.index-1) >= 0;
        },   
        upperBound: function() {
            return (this.sectionOrder.length) === (this.index + 1)
        },
        lowerLimit: function() {
            return Math.max((this.index - 1), 0)
        },
        upperLimit: function(){
            return Math.min((this.index + 1), (this.sectionOrder.length-1))
        }
    },

    methods:{

        ...mapActions('configuration',['mutateConfiguration']),

        incrementIndex: function(){
            this.index = Math.min((this.index + 1), this.sectionOrder.length)
        },
        decrementIndex: function() {
            this.index = Math.max((this.index - 1), 0)
        },
        handleChange: function(event){
            const {name, value, type, checked} = event.target
            console.log(value);
            type === 'checkbox' ? this.$store.commit(name,checked) : this.$store.commit(name,value);
        },
        handleIndex:function(event){
            const {name, value, type, checked, id} = event.target
            console.log(value)
            let param = {
                index: id,
                secondary:value
            }
            this.$store.commit(name,param)
        },
        handleEntry:function(event,key){
            console.log()
            this.$store.commit('referenceEntries/setEntry',key)
        },
        handleSpecial: function(event,key){
            /*const {name,value,type,checked,id} = event.target
            let special = {}
            special[key] = value*/
            this.$store.commit('configuration/test',1)
            this.$store.dispatch('configuration/test',2)
            
        },
        confirmConfiguration:function(){
            axios.defaults.withCredentials = true

            const localHost = "http://localhost:8000"
            const path = "/new_game"

            const target = this.getLocalHost ? localHost + path : path
            const params = {game_config:this.game_config}

            console.log(params)

            return axios.post(target,params)
                .then(response =>{
                    if(response.status === 200){
                        console.log(response.data)
                        this.$router.push({name:'dashboard'})
                    }
                }).catch( error => {
                    const {status} = error.response
                    console.log(status)
                })
        },

        getStep:function(){
            axios.defaults.withCredentials = true

            const localHost = "http://localhost:8000"
            const path = "/get_step"

            const target = this.getLocalHost ? localHost + path : path
            const params = {step_num:1}

                axios.get(target,{params:params})
                .then(response => {
                    if(response.status === 200){
                        console.log(response.data)
                        console.log("TEST")
                    }
                }).catch(error => {
                    const {status} = error.response
                    if(status === 401){
                        console.log("Login Error")
                    }
                }).finally( () => {
                    
                })
        }
    },    
}
</script>

<style lang="scss" scoped>
    @import "../../sass/components/configuration-session";
    @import "../../sass/components/configuration-form";
</style>
