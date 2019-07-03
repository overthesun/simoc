<template>
    <div class='display-wrapper'>
        <div class='panel'></div>
        <div class='panel'></div>
        <div class='panel desktop-only'></div>
    </div>

</template>

<script>
import {mapState,mapGetters,mapActions} from 'vuex'
import axios from 'axios'
export default {
    mounted:function(){

    },

    methods:{
        ...mapMutations('stepData',['setStepData']),

        getStep:function(){
        axios.defaults.withCredentials = true

        const localHost = "http://localhost:8000"
        const path = "/get_step"

        const target = this.getLocalHost ? localHost + path : path
        const params = {step_num:1}

            axios.get(target,{params:params})
            .then(response => {
                if(response.status === 200){
                    setStepData(response.data)
                }
            }).catch(error => {
                const {status} = error.response
                if(status === 401){
                    console.log("Login Error")
                }
            }).finally( () => {
                
            })
        }
    }
}
</script>

<style lang="scss" scoped>

@import "../sass/mediaqueries";

    .display-wrapper{
        width: 100%;
        height: 100%;
        display: flex;
        flex-flow:row nowrap;
        justify-content: space-around;
        align-items:center;
    }

        .panel{
        flex: 1 100%;
        height: 100%;
        background-color: rgba(#1e1e1e,.85);
        
        &:first-of-type{
            margin:none;
            margin-left: 32px;
        }

        &:nth-of-type(2n+0){
            margin: 0px 32px;
        }

        &:last-of-type{
            margin-right: 32px;
        }
    }

    .desktop-only{
        display:none;

        @include for-md-desktop-up{
            display:inherit;
        }
    }

    .lg-desktop-only{
        display:none;

        @include for-lg-desktop-up{
            display:inherit;
        }
    }

</style>
