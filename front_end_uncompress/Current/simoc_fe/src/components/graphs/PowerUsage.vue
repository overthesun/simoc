<!-- This chart is currently out of date. Needs to be updated to the new format for retrieving the configuration and poweru usage -->

<template>
    <canvas id="canvas" style='height: 100%; width: 100%;' height='auto' width='auto'></canvas>
</template>
<script>
import axios from 'axios'
import Chart from 'chart.js';
import "chartjs-plugin-annotation";
import {mapState,mapGetters} from 'vuex' 
export default {

    data(){
        return{
            energyConsumption:{
                crewQuarters:0,
                eclss:0,
                powerStorage:0,
                greenhouse:0,
                plantSpecies:0
            },
            energyProduction:{
                powerGenerator:0,
            }
        }
    },

    computed:{
        ...mapGetters('configuration',['getCrewQuarters','getEclss','getPowerGenerator','getPowerStorage','getGreenhouse','getPlantSpecies']),
        ...mapGetters(['getUseLocalHost']),

        crewQuarters: function(){
            return this.getCrewQuarters
        },
        eclss: function(){
            return this.getEclss
        },
        powerGenerator: function(){
            return this.getPowerGenerator
        },
        powerStorage: function(){
            return this.getPowerStorage
        },
        greenhouse: function(){
            return this.getGreenhouse
        },
        plantSpecies: function(){
            return this.getPlantSpecies
        }
    },

    watch:{
        plantSpecies:{
            handler: function(){
                this.energyConsumption.plantSpecies = 0
                this.plantSpecies.forEach((element)=>{
                    if(element.type != null && element.amount > 0){
                        this.retrievePower(element.type,element.amount,(response)=>{                            
                            let {energy_input} = response
                            this.energyConsumption.plantSpecies += energy_input
                        })
                    }
                })
            },
            deep:true
        },

        crewQuarters:{
            handler: function(){
                this.retrievePower(this.crewQuarters.type,1,(response)=>{
                    let {energy_input} = response
                    this.energyConsumption.crewQuarters = energy_input
                })
               
            },
            deep:true
        },
        eclss:{
            handler:function(){
                this.energyConsumption.eclss = this.retrievePower(this.eclss.type,this.eclss.amount,(response)=>{
                    let {energy_input} = response
                    this.energyConsumption.eclss = energy_input
                })
            },
            deep:true
        },
        /*powerGenerator:{
            handler:function(){
                this.retrievePower(this.powerGenerator.type)
            },
            deep:true
        },*/
        powerStorage:{
            handler:function(){
                this.retrievePower(this.powerStorage.type,this.powerStorage.amount,(response)=>{
                    let {energy_input} = response
                    this.energyConsumption.powerStorage = energy_input
                })
            },
            deep:true
        },
        greenhouse:{
            handler:function(){
                this.energyConsumption.greenhouse = this.retrievePower(this.greenhouse.type,1,(response)=>{
                    let {energy_input} = response
                    this.energyConsumption.greenhouse = energy_input
                })
            },  
            deep:true
        },
        
    },

    methods:{

        updateGraph:function(){
            this.chart.data.labels = []
            this.chart.data.labels = "Power Production"
        },

        retrievePower: function(agent,amount=1,callback){

            axios.defaults.withCredentials = true

            const localHost = "http://localhost:8000"
            const path = "/get_energy"

            const target = this.getUseLocalHost ? localHost + path : path
            const params = {agent_name:agent,quantity:amount}
            return axios.get(target,{params:params})
                .then(response =>{
                    if(response.status === 200){
                        callback(response.data)
                    }
                }).catch(error => {
                    const {status} = error.response
                    console.log(status)
                })
        }
    },

    mounted(){
        
    }
}
</script>

<style lang="scss" scoped>
    
    canvas{
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        position:absolute;
        width:100%;
        height:100%;
    }
</style>
