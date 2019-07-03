export default{
    state:{
        greenhouse:{type:"none",amount:0},
        plantSpecies:[]
    },
    getters:{
        greenhouse: state => state.greenhouse,
        plantSpecies: state => state.plantSpecies,
        plantSpeciesTypes: state => {
            let species = state.plantSpecies
            let types = []
            
            species.forEach((item) =>{
                types.push(item.type)
            })

            return types
        },
    },
    mutations:{
        greenhouseType: (state,type) => state.greenhouse.type = type,
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
                amount: null
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
    },
}