export default{
    state:{
        stepNumber:1,
        agentType:{},
        totalProduction:{},
        totalConsumption:{},
        storageRatio:{},
    },

    getters:{
        //Returns the approriate store at the specified step
        //See Vuex documentation on getters
        //https://vuex.vuejs.org/guide/getters.html
        getStepNumber: state => state.stepNumber,
        getAgentType: state => stepNumber => state.agentType[stepNumber],
        getTotalProduction: state => stepNumber => state.totalProduction[stepNumber],
        getTotalConsumption: state => stepNumber => {console.log(stepNumber); return state.totalConsumption[stepNumber]},
        getStorageRatio: state => stepNumber => state.storageRatio[stepNumber],  
        getAirStorageRatio: state => stepNumber => state.storageRatio[stepNumber]['air_storage_1']
    },

    //Setters
    mutations:{
        incrementStepNumber:function(state,value = 1){
            // Make sure that the new step number is at the very least one
            state.stepNumber = Math.max(1,(state.stepNumber + value))
            console.log(state.stepNumber)
        },

        setCurrentStepNumber:function(state,value){
            // Make sure that the new step number is at the very least one
            state.stepNumber = Math.max(1,value)
        },

        // Mutates the agent type totals using step as the key
        //Takes in a single steps worth of data
        setAgentType:function(state,value){

            let{step_num:step} = value
            let{} = value
        },

        // Mutates the total consumption using step as the key
        //Takes in a single steps worth of data
        setTotalConsumption:function(state,value){

            let {step_num:step} = value
            let {total_consumption} = value

            state.totalConsumption[step] = total_consumption
        },

        // Mutates the total production using step as the key
        //Takes in a single steps worth of data
        setTotalProduction:function(state,value){

            let {step_num:step} = value
            let {total_production} = value

            state.totalProduction[step] = total_production
        },
        //Mutates the storage ratios using the step as the key
        //Takes in a single steps worth of data
        setStorageRatios:function(state,value){
   
            let {step_num:step} = value
            let {storage_ratios} = value

            state.storageRatio[step] = storage_ratios
        }
    },
    //Async Setter
    actions:{
        //Called after the step retrieval method has completed. 
        //Parses out each step from the returned data and calls
        //the approriate mutations to store the data.
        parseStep ({commit,dispatch},stepData){
            stepData.forEach((item) =>{
                commit('setTotalConsumption',item)
                commit('setTotalProduction',item)
                commit('setAgentType',item)
                commit('setStorageRatios',item)
            })
        }
    }
}