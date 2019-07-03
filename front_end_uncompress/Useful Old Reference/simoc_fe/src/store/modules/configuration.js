/*import axios from 'axios' 

const getLocalHost = true
const localHost = "http://localhost:8000"
const energyPath = "/get_energy"
const target = getLocalHost ? localHost + path : path*/

export default{
    state:{
        location:{type:"none"},
        duration:{amount:90,type:"day"},
        humans:{type:"human_agent",amount:0,energy:0},
        food:{type:"food_storage",amount:0,energy:0},
        crewQuarters:{type:"none",amount:0,energy:0},
        eclss:{type:"eclss",amount:0,energy:0},
        powerGenerator:{type:"none",amount:0,energy:0},
        powerStorage:{type:"power_storage",amount:0,energy:0},
        greenhouse:{type:"none",amount:0,energy:0},
        plantSpecies:[]
    },

    getters:{
        getLocation: state => state.location,
        getDuration: state => state.duration,
        getHumans: state => state.humans,
        getFood: state => state.food,
        getCrewQuarters: state => state.crewQuarters,
        getEclss: state => state.eclss,
        getPowerGenerator: state => state.powerGenerator,
        getPowerStorage: state => state.powerStorage,
        getGreenhouse: state => state.greenhouse,
        getPlantSpecies: state => state.plantSpecies,
        getPlantSpeciesTypes: state => {
            let species = state.plantSpecies
            let types = []
            
            species.forEach((item) =>{
                types.push(item.type)
            })

            return types
        },

        getFormattedConfiguration: state =>{
            let game_config = {
                duration:{value:parseInt(state.duration.amount),type:state.duration.type},
                human_agent:{amount:parseInt(state.humans.amount)},
                habitat:state.crewQuarters.type,
                greenhouse:state.greenhouse.type,
                food_storage:{amount:parseInt(state.food.amount)},
                solar_arrays:{amount:parseInt(state.powerGenerator.amount)},
                power_storage:{amount:parseInt(state.powerStorage.amount)},
                eclss:{amount:parseInt(state.eclss.amount)},
                plants:new Array(),
                single_agent:1,
            }

            state.plantSpecies.forEach(element =>{
                game_config.plants.push({species:element.type,amount:parseInt(element.amount)})
            })

            return game_config
        }
    },

    mutations:{
        powerGenerator:function(state,value){
            let {type,amount} = value;
            let currAmount = state.powerGenerator.amount
            let currType = state.powerGenerator.type

            console.log(amount)
            console.log(type)

            state.powerGenerator.amount = amount != null ? amount : currAmount
            state.powerGenerator.type = type != null ? type : currType

            //console.log(retrieveEnergy(type,amount))

            //Create call to axios method for getting energy production with 
            //callback to set the value for powerGenerator energy
        },

        locationType: (state,type) => state.location.type = type,
        durationType: (state,type) => state.duration.type = type,
        crewQuartersType: (state,type) => state.crewQuarters.type = type,
        powerGeneratorType: (state,type) => state.powerGenerator.type = type,
        durationAmount: (state,amount) => state.duration.amount = amount,
        humansAmount: (state,amount) => state.humans.amount = amount,
        foodAmount: (state,amount) => state.food.amount = amount,
        eclssAmount: (state,amount) => state.eclss.amount = amount,
        powerStorageAmount: (state,amount) => state.powerStorage.amount = amount,
        powerGeneratorAmount:(state,amount) => state.powerGenerator.amount = amount,       
        greenhouseAmount: (state,amount) => state.greenhouse.amount = amount,
        greenhouseType: (state,type) => {state.greenhouse.type = type; console.log(type)},
        plantSpeciesType:(state,value) => {
            let {index} = value
            let {secondary} = value

            state.plantSpecies[index].type = secondary
            console.log(value);
        },
        plantSpeciesAmount:(state,value) => {
            let {index} = value;
            let {secondary} = value;

            state.plantSpecies[index].amount = secondary;
        },
        addPlantSpecies:(state) => {

            state.plantSpecies.push({
                type: null,
                amount: null,
                energy:0,
            })
        },
        removePlantSpecies:(state,value) => {
            let length = state.plantSpecies.length

            if(length > 1){
                state.plantSpecies.splice(value,1)
            } else if(length === 1){
                state.plantSpecies[0].type = null
                state.plantSpecies[0].amount = null
                
            }
        },
        test:(state,value) =>{
            console.log("MUTATION")
        }
    },
    actions:{
        test: ({commit},value) =>{
            console.log(state.configuration.crewQuarters.type)
        }
    }
}