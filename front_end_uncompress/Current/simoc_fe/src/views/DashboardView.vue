<template>
    <div class='base-dashboard-wrapper'>
        <router-view>            
        </router-view>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
import axios from 'axios'
import {StepTimer} from '../javascript/stepTimer'
export default {
    mounted:function(){
        this.SETGAMEID(this.getGameID)  //Set the game id for the get_step parameters
        
        //Kill the timer if there is still one running somehow
        if(this.getTimerID != null || this.getTimerID != undefined){
            window.clearTimeout(this.getTimerID)
        }

        this.SETTIMERID(undefined)      //Set the timerID to null 
        this.SETISTIMERRUNNING(false)   //Reset the timer has been created flag
        this.SETTERMINATED(false)       //Reset the termination conditions have been met flag
        this.initialSetup()

        //This is the timer object that will be called whenever the step number is increased.
        //It defaults to being called every second. Also this is not started until at least 100 steps have been buffered in.
        //See below methods for where the timer is started. 
        let stepTimer = new StepTimer( () => {
            let {max} = this.getStepBuffer  // Get the max step that has been buffered in
            let current = Math.min(max,this.getStepBuffer.current+1) //Don't go beyond what's buffered already.
            this.SETBUFFERCURRENT(current)  //Set the current step number
        },1000)

        this.SETTIMERID(stepTimer) // The timer is set within the dashboard store
        //This sets the get_step paramter for the totalAgentMass filter. This should actually be done
        //in tandem with the configuration wizard plant updates.
        this.SETPLANTSPECIESPARAM(this.getConfiguration) 



        //stepTimer.resume()
    },
    computed:{
        //Getterss from the vuex stores
        ...mapGetters('dashboard',['getTimerID','getIsTimerRunning','getUpdateTimer','getTerminated','getStepParams','getStepBuffer','getTotalProduction','getTotalConsumption','getAirStorageRatio']),
        ...mapGetters(['getGameID']),
        ...mapGetters('wizard',['getTotalMissionHours','getConfiguration']),
        ...mapGetters(['getUseLocalHost']),

    },
    methods:{    
        //
        ...mapMutations('dashboard',['SETPLANTSPECIESPARAM','STARTTIMER','SETTIMERID','SETUPDATETIMER','SETBUFFERCURRENT','SETISTIMERRUNNING','SETGAMEID','SETMINSTEPNUMBER','SETNSTEPS','SETBUFFERMAX','SETBUFFERCURRENT','SETTERMINATED']),
        //Action used for paring the get_step response on completion of retrieval. SEE dashboard store.
        ...mapActions('dashboard',['parseStep']),


        initialSetup: async function(){    
            const localHost = "http://localhost:8000"
            const getStepToRoute = this.getUseLocalHost ? localHost + "/get_step_to" : "/get_step_to"
            const getStepRoute = this.getUseLocalHost ? localHost + "/get_steps" : "/get_steps"
            
            const stepToParams = {step_num:this.getTotalMissionHours,game_id:this.getGameID} //Use the total number of mission hours as the number of steps to be calculated.
            const stepParams = this.getStepParams //Retrieve the parameters to used from the dashboard store
            try{
                await axios.post(getStepToRoute,stepToParams) //Begin creating the step buffer on the backend using the entire length of the simulation as the base
                this.stepBufferTimer() //If everything went retrieve the first batch of steps.
            }catch(error){
                console.log(error)
            }
        },

        stepBufferTimer: async function(){
            const localHost = "http://localhost:8000"
            const getStepRoute = this.getUseLocalHost ? localHost +  "/get_steps" : "/get_steps"
            const stepParams = this.getStepParams //Filter parameters stored in dashboard store

            //If the termination conditiona hasn't been terminated yet. 
            //Keep grabbing step batches
            if(!this.getTerminated){          
                setTimeout( async () =>{
                    try{
                        const response = await axios.post(getStepRoute,stepParams) //Grab the batch of steps
                        this.updateStepBuffer(response) //Call the function that will parse and reset the timer
                    }catch(error){
                        console.log(error)
                    }
                },500)
            }
        },

        updateStepBuffer: async function(response){
            //Add in termination condition check
            await this.parseStep(Object.values(response.data)) // Call the parseStep ACTION within dashboard to parse the steps. Wait until they have all been parsed.
            
            //If the max of the buffer size is at the end, turn on the terminated condition
            if(this.getStepBuffer.max >= parseInt(this.getTotalMissionHours)){
                this.SETTERMINATED(true)
            }

            //If the buffer has at least 100 steps or if it's been terminated then start the 
            //step update timer.

            //Termination condition is added in so that simulations less than 100 steps can still run.
            if(this.getStepBuffer.max >= 100 || this.getTerminated){
                if(!this.getIsTimerRunning){ //If the timer isn't running yet, get it started.
                    this.STARTTIMER() //Call the mutation used within the dashboard store to start the timer.
                }
            }

            this.stepBufferTimer() //Rinse and repeat
                     
        },
    },
    watch:{
        //This method pauses the current simulation if the current step is at or beyond the 
        //amount of steps that are currently buffered.
        getStepBuffer:{
            handler:function(){
                let {current,max} = this.getStepBuffer
                if(current >= max){
                    this.getTimerID.pause()
                }
            },
            deep:true
        }
    }
}
</script>

<style lang="scss" scoped>
    .base-dashboard-wrapper{
        width: 100vw;
        height: 100vh;
        min-width: 100vw;
        min-height: 100vh;
        overflow:hidden;
        position:relative;
    }
</style>
