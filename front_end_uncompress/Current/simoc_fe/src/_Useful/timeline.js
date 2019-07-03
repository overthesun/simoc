<template>
    <div class='dashboard-wrapper'>
        <div class='timeline-wrapper'>
            <input class='timeline' type='range' min='0' max='100' v-model="value" :style="{'background-image':'linear-gradient(to right,green 0%, green ' + value + '%,lightgreen ' + value +'%,lightgreen '+ stepMax +'%,#999 ' + stepMax + '%,#999 100%)'}" v-on:input="killClock" v-on:change="updateStep">    
        </div>
    </div>
</template>

<script>
    
export default {
    data(){
        return{
            value:1,
            stepMax:40
        }
    },
    computed:{
        ...mapGetters(['getUseLocalHost'])
    },
    methods:{
        updateStep:function(){
            this.clock = setTimeout(()=>{
                this.value = parseInt(this.value) +  1

                if(this.value >= this.stepMax){
                    window.clearInterval(this.clock)
                    this.updateBuffer()
                }else{
                    this.updateStep()
                }
            },100)
        },
        killClock:function(){
            window.clearInterval(this.clock)
        },
        updateBuffer:function(){
            let bufferClock = setTimeout(()=>{
                if(this.value < this.stepMax)
                    this.updateStep()
                else
                    this.updateBuffer()
            },100)


        }
    },
    mounted(){
        this.updateStep()
        setTimeout(()=>{
        this.stepMax = 75
        },3000)
        setTimeout(()=>{
                this.stepMax = 100
        },6000)
    }
}
</script>

<style lang="scss" scoped>
    .dashboard-wrapper{
        width: 100%;
        height:100%;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
    }

    .timeline-wrapper{
        width: auto;
        height: auto;
        padding: 16px;
        background-color: #1e1e1e;
        display:flex;
        justify-content:center;
        align-items:center;
    }

    .timeline{
        appearance:none;
        border-radius: 2px;
        width: 512px;
        height: 4px;
        outline:none;
        background:transparent;
        background-repeat:no-repeat;
        //background-image: linear-gradient(orange,red);
    }

    .timeline::-webkit-slider-thumb{
        appearance:none;
        width: 16px;
        height: 16px;
        border-radius:50%;
        background-color: seagreen;
    }

    .timeline::-moz-range-thumb{
        width: 16px;
        height: 16px;
        border-radius:50%;
        background-color: seagreen;
        cursor:pointer;
    }

</style>







