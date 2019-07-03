<template>
    <div class='form-wrapper'>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'greenhouse')">GREENHOUSE</div>
            <div class='section-subtitle'>The plant house, it's also a hot house</div>
            <div class='input-wrapper'>
                <select class='input-select' name="configuration/greenhouseType" :selected="getGreenhouse.type" v-on:input="handleChange">
                    <option value="none" disabled selected hidden>Size</option>
                    <option value="greenhouse_small">Small: 490 m^3</option>
                    <option value="greenhouse_medium">Medium: 2454 m^3</option>
                    <option value="greenhouse_large">Large: 5610 m^3</option>
                </select>                
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'plants')">PLANTS</div>
            <div class='section-subtitle'>The plants that will be growing in your greenhouse</div>
            <div class='input-wrapper input-wrapper-plants' v-for="(line,index) in getPlantSpecies" :key="index">
                <select class='input-select' :id="index" name='configuration/plantSpeciesType' :selected="getPlantSpecies[index].type" v-on:input="handleIndex">
                    <option value="none" disabled hidden :selected="'none' === getPlantSpecies[index].type || null === getPlantSpecies[index].type">Species</option>
                    <option :value="item" v-for="(item,i) in uniquePlantNames(index)" :key="i" :selected="item === getPlantSpecies[index].type">{{formattedPlantNames(item)}}</option>          
                </select>   
                <input class='input-number' min="0" step="1" max=10000 :id="index"  name='configuration/plantSpeciesAmount' type='number' :value="getPlantSpecies[index].amount" placeholder="Qty" v-on:input="handleIndex"/>             
                <div class='icon-wrapper'>
                    <fa-layers class="fa-2x icon" @click="removePlantSpecies(index)">
                        <fa-icon :icon="['fas','trash']" mask="circle" transform="shrink-6"/> 
                    </fa-layers>
                    <fa-layers class="fa-2x icon" @click="addLine()">
                        <fa-icon :icon="['fas','plus-circle']" /> 
                    </fa-layers>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {

    computed:{
        ...mapGetters('configuration',['getPlantSpecies','getGreenhouse','getPlantSpeciesTypes']),
    },

    methods:{
        ...mapGetters(['getLocalHost']),
        //...mapGetters('configuration',['getPlantSpeciesTypes']),
        ...mapMutations('configuration',['addPlantSpecies','removePlantSpecies','resetPlantSpecies','plantSpeciesType']),
        test:function(value){
            console.log(value)
        },

        retrievePlantSpecies:function(){
            console.log("TEST");
            axios.defaults.withCredentials = true

            const localHost = "http://localhost:8000"
            const path = "/get_agent_types"

            const target = this.getLocalHost ? localHost + path : path
            const params = {agent_class:'plants'}

            /*axios.get(target,{params:params})
                .then(response => {
                    if(response.status === 200){
                        response.data.forEach((item) => {
                            let {name} = item      
                            this.plantNames.push(name)
                        })
                        console.log("TEST");
                    }
                }).catch(error => {
                    const {status} = error.response
                    if(status === 401){
                        console.log("Login Error")
                    }
                }).finally( () => {
                    
                })*/
        },

        formattedPlantNames:function(name){
            let formatted = ""

            formatted = name = name.replace(/_|-/g," ")
            formatted = name.toLowerCase()
                    .split(" ")
                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                    .join(" ")
            
            return formatted
        },

        uniquePlantNames:function(index){
            let currentOption = this.getPlantSpecies[index].type
            let plantTypes = [...this.getPlantSpeciesTypes]
            let selectedOptions = currentOption != null ? plantTypes.filter(x => !currentOption.includes(x)) : plantTypes
            let uniqueOptions = this.plantNames.filter(x => !selectedOptions.includes(x))

            return uniqueOptions
        },

        addLine:function(){
            let length = this.getPlantSpecies.length
            let maximum = this.plantNames.length

            if(length < maximum)
                this.addPlantSpecies()
        }
    },

    props:{
        handleChange:Function,
        handleIndex:Function,
        handleEntry:Function,
    },

    mounted(){
        
        if(this.getPlantSpecies.length <= 0){
            this.addPlantSpecies(); 
        }

        this.retrievePlantSpecies();

    },

    data(){
        return{
            plantNames:[],
            blockRemoval:true,
        }
    },

    watch:{
        plantSpecies(){
            this.blockRemoval = this.plantSpecies.length <= 1
        }
    }
}
</script>

<style lang="scss" scoped>
    @import "../../sass/components/configuration-form-internal";
    .icon-wrapper{
        margin-left: 48px;
    }

    .icon:first-of-type{
        margin-right: 24px;
    }

    .input-wrapper-plants{
        margin-bottom: 24px;
    }

</style>
