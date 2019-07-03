import axios from 'axios'

export default{
    state:{
        stepNumber:0,
        humans:0,
        food:0,        
        co2:{ratio:0,consumed:0,produced:0},
        o2:{ratio:0,consumed:0,produced:0},
        h2oAtmo:0,
        h2oRatio:0,
        h2oPotable:{consumed:0,produced:0},
        h2oWasteRatio:0,
        kwhEnergy:{consumed:0,produced:0},
    },
    getters:{
        getStepNumber: state => state.stepNumber,
        getHumans: state => state.humans,
        getFood: state => state.food,
        getCO2: state => state.co2,
        getO2: state => state.o2,
        getH2OAtmo: state => state.h2oAtmo,
        getH2ORatio: state => state.h2oRatio,
        getH2OPotable: state => state.h2oPotable,
        getH2OWasteRatio: state => state.h2oWasteRatio,
        getKWHEnergy: state => state.kwhEnergy
    },
    mutations:{
        setAgentTypes:function(state,value){
            let {step} = value
            let {agents:{total_agent_types:{human_agent}}} = value

            state.stepNumber = step
            state.humans = human_agent
        },

        setConsumption:function(state,value){
            let {agents:{total_consumption:{atmo_co2,atmo_o2,food_edbl,h2o_potb,enrg_kwh}}} = value
        
            state.co2.consumed = atmo_co2
            state.o2.consumed = atmo_o2
            state.h2oPotable.consumed = h2o_potb
            state.kwhEnergy.consumed = enrg_kwh
        },

        setProduction:function(state,value){
            let {agents:{total_production:{atmo_co2,atmo_o2,food_edbl,h2o_potb,enrg_kwh}}} = value
        
            state.co2.production = atmo_co2
            state.o2.production = atmo_o2
            state.h2oPotable.production = h2o_potb
            state.kwhEnergy.production = enrg_kwh
        },

        setModelStats:function(state,value){
            let {model_stats:{air_storage_1:{atmo_ch4_ratio,atmo_co2_ratio,atmo_h2_ratio,atmo_h2o_ratio,atmo_n2_ratio,atmo_o2_ratio}}} = value
            
            console.log(atmo_h2o_ratio)
            state.h2oRatio = atmo_h2o_ratio
            state.co2.ratio = atmo_co2_ratio
            state.o2.ratio = atmo_o2_ratio
        },
    },

    actions:{
        getStepTo ({commit,dispatch},stepNumber,minStepNumber){
            console.log(stepNumber)
            axios.defaults.withCredentials = true

            const localHost = "http://localhost:8000"
            const path = '/get_step_to'

            const target = localHost + path
            const params = {step_num:stepNumber}

            axios.get(target,{params:params})
                .then(response =>{
                    if(response.status === 200){
                        dispatch('getSteps',stepNumber)
                        stepNumber += 100
                        dispatch('getStepTo',stepNumber)
                        
                    }
                })
        },  

        getSteps ({commit,dispatch},minStepNumber){
            axios.defaults.withCredentials = true
            console.log(minStepNumber)
            const localHost = "http://localhost:8000"
            const path = '/get_steps'

            const target = localHost + path
            
            
            const params = {
                
                "min_step_num": minStepNumber, 
                "n_steps": 100,
                "total_production":["atmo_co2","atmo_o2","h2o_potb","enrg_kwh"],
                "total_consumption":["atmo_o2","h2o_potb","enrg_kwh"],
                "storage_ratios":{"air_storage_1":["atmo_co2","atmo_o2","atmo_ch4","atmo_n2","atmo_h2","atmo_h2o"]},
                "parse_filters":[]
            }
            axios.post(target,params)
                .then(response =>{
                    if(response.status == 200){
                        console.log(response.data)
                        console.log('Steps Got')
                    }
                })
        }
    }
}