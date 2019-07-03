<!-- Timeline component 
There is an issues with this that causes the stepTimer to resume once the user slides the timeline indicator to a new place. It will override the current state of the timer. 
A condition needs to be added in if the timer is paused by some other means than just by the timeline indicator methods 
-->

<template>
        <div class='timeline-wrapper'>
<!--            <input class='timeline' type='range' min='0' max='100' v-model="value" :style="{'background-image':'linear-gradient(to right,green 0%, green ' + value + '%,lightgreen ' + value +'%,lightgreen '+ stepMax +'%,#999 ' + stepMax + '%,#999 100%)'}" v-on:input="killClock" v-on:change="updateStep">    
            -->
            <div class='timeline-item timeline-text'>{{getStepBuffer.current}}</div>
            <span class='timeline-item'>
                <input class='timeline' type='range' min='1' :disabled="getForcedPause" :max="getTotalMissionHours" v-model="currentStep" v-on:input="pauseBuffer" v-on:change="updateBuffer" :style="{'background-image':'linear-gradient(to right,#67e300 0%, #67e300 ' + currentPercentage + '%,#d0d0d0 ' + currentPercentage +'%,#d0d0d0 '+ bufferPercentage +'%,#444343 ' + bufferPercentage + '%,#444343 100%)'}" >    
            </span>
            <div class='timeline-item timeline-text'>{{getTotalMissionHours}}</div>
        </div>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
import {StepTimer} from '../../javascript/stepTimer'
export default {
    data(){
        return{
            currentPercentage:1,
            bufferPercentage:1,
            currentStep:1
        }
    },

    mounted:function(){
        const {current} = this.getStepBuffer
    },

    computed:{
        ...mapGetters('dashboard',['getStepBuffer','getTimerID','getForcedPause']),
        ...mapGetters('wizard',['getTotalMissionHours'])
        
    },
    methods:{
        ...mapMutations('dashboard',['SETTIMERID','SETBUFFERCURRENT']),

        //Pause the timer if the user has started to drag the timeline slider. This prevents updates while the user 
        //interactives with the timeline.
        pauseBuffer:function(){
            this.getTimerID.pause()
        },

        //If the user has set the slider to a new value, reset everything to the new step.
        //Remember pause actually kills the old timer within the stepTimer.js
        updateBuffer:function(){
            this.SETBUFFERCURRENT(parseInt(this.currentStep))            

            //Create a new timer object once the user has deselected the indicator
            //The interval also needs to be stored universally to allow this to create a 
            //new timer object with the last used speed.
            let stepTimer = new StepTimer( () => {
                let {max} = this.getStepBuffer
                let current = Math.min(max,this.getStepBuffer.current+1) //Don't go beyond what's buffered already.
                this.SETBUFFERCURRENT(current)
            },1000)

            this.SETTIMERID(stepTimer) // Set the new timer ID to the dashboard store
            this.getTimerID.resume() // Resume the timer. This is also the spot that causes a bug with the timeline starting up regardless of the state.
            
        }
    },
    watch:{
        getStepBuffer:{
            handler:function(){
                let {max,current} = this.getStepBuffer
                this.currentStep = current
                this.currentPercentage = (current / this.getTotalMissionHours) * 100
                this.bufferPercentage = (max / this.getTotalMissionHours) * 100
            },
            deep:true
        }
    }
}
</script>

<style lang="scss" scoped>
    .timeline-wrapper{
        width: auto;
        height: 32px;
        background-color: #1e1e1e;
        display:grid;
        grid-template-rows:1fr;
        grid-template-columns: auto 1fr auto;
        grid-column-gap: 32px;
        margin: 8px 0px;
        position:relative;
    }



    .timeline-item{
        display:flex;
        justify-content:center;
        align-items:center;
    }

    .timeline-text{
        font-size: 16px;
        font-weight: 200;
    }

    .timeline{
        z-index:99;
        appearance:none;
        border-radius: 2px;
        width: 704px;
        height: 4px;
        outline:none;
        background:transparent;
        background-repeat:no-repeat;
    }

    .timeline::-webkit-slider-thumb{
        appearance:none;
        width: 8px;
        height: 16px;
        border-radius:25%;
        background-color: #67e300;
    }

    .timeline::-moz-range-thumb{
        width: 16px;
        height: 16px;
        border-radius:50%;
        background-color: #67e300;
        cursor:pointer;
    }
</style>