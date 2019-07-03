<template>
    <form class='form-wrapper' @submit.prevent="">
        <label class='input-wrapper'>
            <div class='input-title' @click="SETACTIVEREFENTRY('Greenhouse')">Greenhouse</div> <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>The plant house, it's also a hot house</div>
            <select class='input-field-select' v-model="greenhouse.type" v-on:change="setGreenhouse">
                <option value='none' selected>None</option>
                <option value='greenhouse_small'>Small (490 m³)</option>
                <option value='greenhouse_medium'>Medium (2452 m³)</option>
                <option value='greenhouse_large'>Large (5610 m³)</option>
            </select>
        </label>
        <label class='input-wrapper'>
            <div class='input-title'  @click="SETACTIVEREFENTRY('PlantSpecies')">Plant Species</div> <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>The plants that will be growing in your greenhouse</div>
            <!-- This is the row object for each plant entry within the wizard. v-for automatically rebuilds the fields if one is added or deleted. Index is used as a key to 
            store which plant field has been updated within the configuration 
            -->
            <div class='input-plant-wrapper' v-for="(item,index) in plantSpecies" :key=index>
                <select class='input-field-select' v-model="plantSpecies[index].type" v-on:change="updatePlantSpecies(index)">
                    <option value="" selected hidden disabled>Species</option>
                    <option value="none">None</option>
                    <!-- create options for each plant species within plantValue. Formats them before displaying the. As the plantValue is used for the actual value of the field 
                    for the configuration call. Unique plant names function would normally be called here to retrieve the unique names not already used.
                    -->
                    <option :value="name" v-for="(name,k) in plantValue" :key=k >{{plantFormatted[k]}}</option>
                </select>
                <input class='input-field-number' pattern="^\d+$" maxlength="8" placeholder="Quantity" v-model="plantSpecies[index].amount" v-on:input="updatePlantSpecies(index)">
                <fa-layers class="fa-2x plant-row-icon icon-add" @click="addPlantSpecies">
                    <fa-icon :icon="['fas','plus-circle']" /> 
                </fa-layers>
                <fa-layers class="fa-2x plant-row-icon icon-trash" @click="REMOVEPLANTSPECIES(index)"> <!-- Deletes the object at the specicied key within the wizard store. -->
                    <fa-icon :icon="['fas','trash']" mask="circle" transform="shrink-7"/> 
                </fa-layers>
            </div>
        </label>
    </form>
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    data(){
        return{
            //Initialize the localized variables used for v-model
            greenhouse:undefined,
            plantSpecies:undefined,
            plantValue:[],
            plantFormatted:[],
        }
    },
    mounted(){
        const{plantSpecies,greenhouse} = this.getConfiguration //Get the values from the configuration that is initially set

        //If there isn't a plant present object in the configuration add at least one.
        //This forces the above v-for to populate with at the very least one plant row. 
        //This is done this way to prevent from having to duplicate the above HTML for the platns section for the single starting plant.
        if(plantSpecies.length <= 0){
            this.ADDPLANTSPECIES() 
        }

        this.greenhouse = greenhouse
        this.plantSpecies = plantSpecies

        this.retrievePlantSpecies() //See below. This is used to add all options for the plant names to the selection field.
    },
    computed:{
        ...mapGetters('wizard',['getConfiguration']),  // Gets the configuration from the store
        ...mapGetters(['getUseLocalHost']), //Do I use localhost or relative.

        
    },
    methods:{
        ...mapMutations('wizard',['SETGREENHOUSE','ADDPLANTSPECIES','UPDATEPLANTSPECIES','REMOVEPLANTSPECIES']),
        ...mapMutations('wizard',['SETACTIVEREFENTRY']),
        
        //This method creates a new plant object within the wizard store. It also makes sure that the user 
        // can't add more fields than there are options for plants.
        addPlantSpecies:function(){
            let {plantSpecies} = this.getConfiguration
            const arrLength = plantSpecies.length
            const maxLength = this.plantValue.length

            if(arrLength < maxLength){
                this.ADDPLANTSPECIES()
            }
        },
        
        //This method is used to update a plant at the specified index, updates the plant species and amount.
        //The index is passed in from the above v-for index key when the fields are created.
        //Indexes are repopulated on deletion of any row. Row 3 becomes 2 if row 2 is deleted. This is done
        //automatically be Vue
        updatePlantSpecies:function(index){
            let plantSpecies = this.plantSpecies[index]
            //let amount = parseInt(this.plantSpecies[index].amount)
            let amount = this.plantSpecies[index].amount.toString()
            //const regex = RegExp('^/d+$')
            
            plantSpecies.amount = amount
            
            this.UPDATEPLANTSPECIES({'index':index,'plantSpecies':plantSpecies})
        },

        //Set the greenhouse type within the wizard store. It also sets the default number of greenhouses to one 
        //if any type other than 'none' is selected. Plants are not included as they do their own thing differently than other form elemetns.
        setGreenhouse:function(){
            this.greenhouse.amount = this.greenhouse.type == "none" ? 0 : 1
            const value = {'greenhouse':this.greenhouse}
            this.SETGREENHOUSE(value)
        },

        /*
        //Unused method for gathering unique plant names for a particular field.
        uniquePlantNames:function(index){
            const {plantSpecies} = this.getConfiguration
            //const indexType = plantSpecies[index].type

            let selectedValues = plantSpecies.splice(index,1)
            return false;
        },

        //This method should have returned a list of all plant values not currently selected within the fields.
        //It was to also add back on the actual selected value for the selection field, so that it was not excluded too.
        /*uniquePlantNames:function(index){
            let {plantSpecies} = this.getConfiguration
            let currentOption = plantSpecies[index].type
            let plantTypes = []
            let plantNames = []
            plantSpecies.forEach((item) =>{
                plantTypes.push(item.type)
            })

            console.log(plantTypes)
            

            let selectedOptions = currentOption != null ? plantTypes.filter(x => !currentOption.includes(x)) : plantTypes
            let uniqueOptions = this.plantNames.filter(x => !selectedOptions.includes(x))

            return uniqueOptions
        },*/

        //Format the plant names so that the first letter is capitalized and remove any underscores or dashes and replace them with spaces.
        formatPlantName:function(name){
            let formatted = ""

            formatted = name.replace(/_/g," ")
            formatted = formatted.toLowerCase()
                    .split(" ")
                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                    .join(" ")

            this.plantFormatted.push(formatted)           
        },

        //Call the '/get_agent_types' route to retrieve all agents with the class of plants. 
        //This is used to populate the selection field for the plant species. Stored within the plantValue array on 
        //OK code.

        //this method should also be switch over to the try/catch block of similar route calls. Simply to reduce the callback hell look.
        retrievePlantSpecies:function(){
            axios.defaults.withCredentials = true

            const localHost = "http://localhost:8000"
            const route = "/get_agent_types"
            const path = this.getUseLocalHost ? localHost + route : route

            const params = {agent_class:'plants'}

            axios.get(path,{params:params}).then( response => {
                if(response.status === 200){
                    response.data.forEach((item) =>{
                        let {name} = item
                        this.plantValue.push(name)
                        //console.log(this.formatPlantName(name))
                        this.formatPlantName(name)
                        
                    })
                }
            }).catch(error=>{
                const {status} = error.response
                if(status == 401){
                    console.log("Plant retrieval error")
                }
            })
        },

    },
    //If any part of the configuration has changed, update the values this form uses too. This is useful for watching when
    // a preset changes all values within the configuration object within wizard store.
    watch:{
        getConfiguration:{
            handler:function(){
                const {greenhouse,plantSpecies} = this.getConfiguration
                this.greenhouse = greenhouse
                this.plantSpecies = plantSpecies
            },
            deep:true // Watch all values within not just the root value. Necessary for watching objects.
        }
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/components/configuration-input';

    .input-plant-wrapper{
        display:flex;
        justify-content:flex-start;
        align-items:center;
    }

    .input-field-select{
        margin-right:24px;
    }

    .input-field-number{
        margin-right:24px;
    }

    .plant-row-icon{
        &:first-of-type{
            margin-left:auto;
        }

        margin-right:24px;
    }
</style>
