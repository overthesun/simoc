//Contains the shared state for all things related to the dashboard.

//Parameters for the get_step route

//Step data - broken doewn into objects based on filter type. These can be accessed via the below getters.
//The idea is to use object deconstruction to set the variables for the individual parts within the calling method.
// agentCount | totalAgentMass | totalProduction | totalConsumption | storageRatio 

//stepBuffer - This actually needs to be broken down into individual pieces for each value, and refactored in the 
//called places to the approriate variable. A number of watcher functions within components reference this for updating various data points
//such as panels and charts.

//Timer ID - this is used to pause, resume, speed controls or kill the setTimeout object within. SEE stepTimer.js within js folder for 
//further details.

//Termination flag - Universally accessible point to check if the simulation has terminated.

//ACTIONS
//ParseStep function is an async call to parse all data from a particular get_step response object. It's setup as async so that 
//it can continue to process get_step objects out of order as the step_number is used as the key within the resulting filter objects.
//So order doesn't matter as long as the step_number is correct. This should also prevent any issues if a step is duplicated within two 
//different step objects

//To be added: Need to add a variable to store the current step interval. This is currently only done locally within the Controls component.

export default{
    state:{
        parameters:{
            "game_id":undefined,
            "min_step_num": 1, 
            "n_steps": 10,
            "total_agent_count":["human_agent"],
            "total_agent_mass":[],
            "total_production":["atmo_co2","atmo_o2","h2o_potb","enrg_kwh"],
            "total_consumption":["atmo_o2","h2o_potb","enrg_kwh"],
            "storage_ratios":{"air_storage_1":["atmo_co2","atmo_o2","atmo_ch4","atmo_n2","atmo_h2","atmo_h2o"]},
            "parse_filters":[],
            "single_agent":1,                
        },

        agentCount:{1:{"human_agent":0}},
        totalAgentMass:{},
        totalProduction:{},
        totalConsumption:{},
        storageRatio:{},
        stepBuffer:{
            max:1,
            current:1
        },
        terminated:false,
        timerID:undefined,
        forcedPause:false,
        isTimerRunning:false,
        menuActive:false
    },
    getters:{
        getMenuActive:(state) => state.menuActive,
        getStepParams:(state) => state.parameters,
        getStepBuffer:(state) => state.stepBuffer,
    
        getStepNumber: state => state.stepNumber,
        getAgentType: state => stepNumber => state.agentCount[stepNumber],
        getTotalAgentMass: state => stepNumber => state.totalAgentMass[stepNumber],
        getTotalProduction: state => stepNumber => state.totalProduction[stepNumber],
        getTotalConsumption: state => stepNumber => state.totalConsumption[stepNumber],
        getStorageRatio: state => stepNumber => state.storageRatio[stepNumber],  
        getAirStorageRatio: state => stepNumber => state.storageRatio[stepNumber]['air_storage_1'],

        getTerminated: state => state.terminated,
        
        getUpdateTimer: state => state.updateTimer,
        getTimerID: state => state.timerID,
        getIsTimerRunning: state =>state.isTimerRunning,
        getForcedPause: state => state.forcedPause, //Used for menus and such when the range bar absolute must not have input
    },
    mutations:{
        SETPARAMETERS:function(state,value){
            state.parameters = value
        },
        SETMENUACTIVE:function(state,value){
            state.menuActive = value
        },

        // Starts the step timer. This object is actually created within the 
        // DashboardView component on mounted. The timer is not started until the conditions 
        // are met for a reasonable buffer amount.
        STARTTIMER:function(state,value){
            //if((state.stepBuffer.max >= 100 || state.terminated ) && !state.isTimerRunning){
                console.log("Step Timer Running")
                state.timerID.resume()
                state.isTimerRunning = true
            //}
        },
        SETTIMERID:function(state,value){
            state.timerID = value
        },

        SETTERMINATED:function(state,value){
            state.terminated = value
        },  
        //Is the step_timer already been created and running initiall?
        SETISTIMERRUNNING:function(state,value){
            state.isTimerRunning = value
        },
        SETGAMEID:function(state,value){
            state.parameters.game_id = value
        },
        //This is used for the starting step of get_step batches. Updated after every get_step call
        SETMINSTEPNUMBER:function(state,value){
            let {step_num:step} = value
            state.parameters.min_step_num = Math.max(step,state.parameters.min_step_num) 
        },
        //This is used for the number of steps to grab from get_step_to, after 100 steps have been buffered, . Updated after every get_step call
        SETNSTEPS:function(state,value){
            let {step_num:step} = value
            state.parameters.n_steps = state.stepBuffer.max > 100 ? 100 : 10
        },
        //This is used for the max value of the current number of steps currently in the buffer.
        SETBUFFERMAX:function(state,value){
            let {step_num:step} = value
            state.stepBuffer.max = Math.max(step,state.stepBuffer.max)
        },
        //The current step the simulation is displaying. 
        SETBUFFERCURRENT:function(state,value){
            state.stepBuffer.current = value
        },
        SETAGENTTYPE:function(state,value){
            let{step_num:step} = value
            let{total_agent_count} = value
            state.agentCount = total_agent_count
        },
        SETTOTALAGENTMASS:function(state,value){
            let{step_num:step,total_agent_mass} = value
            state.totalAgentMass[step] = total_agent_mass
        },
        SETTOTALCONSUMPTION:function(state,value){
            let{step_num:step} = value
            let{total_consumption} = value

            state.totalConsumption[step] = total_consumption
        },
        SETTOTALPRODUCTION:function(state,value){            
            let {step_num:step} = value
            let {total_production} = value

            state.totalProduction[step] = total_production
        },
        SETSTORAGERATIOS:function(state,value){
            let {step_num:step} = value
            let {storage_ratios} = value

            state.storageRatio[step] = storage_ratios
        },

        //Populates the parameters object with the selected plants from the 
        //configuration wizard. This should actually called and updated similar to how the
        //wizard store updates its plants list on the fly. 
        SETPLANTSPECIESPARAM:function(state,value){
            let {plantSpecies} = value

            plantSpecies.forEach((item) =>{
                state.parameters.total_agent_mass.push(item.type)
                state.totalAgentMass[item.type] = {"value":0,"units":undefined}
            })
        }
    },
    actions:{
        parseStep({commit,dispatch},stepData){
            console.log(stepData)
            stepData.forEach((item) => {
                commit('SETTOTALCONSUMPTION',item)
                commit('SETTOTALPRODUCTION',item)
                commit('SETAGENTTYPE',item)
                commit('SETTOTALAGENTMASS',item)
                commit('SETSTORAGERATIOS',item)
                commit('SETBUFFERMAX',item)
                commit('SETNSTEPS',item)
                commit('SETMINSTEPNUMBER',item)
                //commit('SETTERMINATED',item)
            })
        },
    }
}