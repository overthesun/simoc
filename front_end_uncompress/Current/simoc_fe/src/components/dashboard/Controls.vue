<!-- Time speed control component used on the dashboard. SEE stepTimer.js in JS folder for more details on the functionality of the timer -->

<template>
    <div class='controls-wrapper'>
        <span class='icon-wrapper'>
            <fa-icon class='fa-icon menu-icon' :icon="['fas','backward']" @click="decreaseStepsPerSecond"/>
        </span>
        <span class='icon-wrapper icon-play' :class="{'icon-play-hidden':isPaused}">
             <fa-icon class='fa-icon menu-icon' :icon="['fas','pause']"  @click="pauseTimer"/>
        </span>
        <span class='icon-wrapper icon-play' :class="{'icon-play-hidden':!isPaused}" >
             <fa-icon class='fa-icon menu-icon' :icon="['fas','play']" @click="resumeTimer"/>
        </span>
        <span class='icon-wrapper'>
            <fa-icon class='fa-icon menu-icon' :icon="['fas','forward']" @click="increaseStepsPerSecond"/>
        </span>
    </div>    
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {
    data(){
        return{ 
            isPaused:false,
            stepInterval:1000,
        }
    },
    computed:{
        ...mapGetters('dashboard',['getTimerID'])
    },
    methods:{
        //Calls the pause method on the timer object stored within the dashboard store.
        pauseTimer:function(){
            this.isPaused = true
            this.getTimerID.pause()
        },
        //Calls the resume method on the timer object stored within the dashboard store.
        resumeTimer:function(){            
            this.isPaused = false
            this.getTimerID.resume()
        },
        //Calls the changeInterval method on the timer object stored within the dashboard store.
        increaseStepsPerSecond:function(){
            this.stepInterval = Math.max(250,this.stepInterval-250)
            this.getTimerID.changeInterval(this.stepInterval)
        },
        //Calls the changeInterval method on the timer object stored within the dashboard store.
        decreaseStepsPerSecond:function(){
            this.stepInterval = Math.min(2000,this.stepInterval+250)
            this.getTimerID.changeInterval(this.stepInterval)
        }
    }
}
</script>

<style lang="scss" scoped>
    .controls-wrapper{
        height: 48px;
        width:196px;
        display:flex;
        justify-content: space-between;
        align-items:center;
    }
    .icon-wrapper{
        font-size:32px;
    }

    .icon-disabled{
        color: #999;
    }

    .icon-play{
        font-size: 36px;    
        &:hover{
            font-size:42px;
        }

        &-hidden{
            display:none;
        }
    }
</style>
