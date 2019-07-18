<template>
    <div class='two-line-wrapper'>
        <div class='line-title'>Location:</div>
        <div class='line-item'>Mars</div>
        <div class='line-title'>Inhabitants:</div>
        <div class='line-item'>0</div>
        <div class='line-title'>Duration Length:</div>
        <div class='line-item'>{{getConfiguration.duration.amount}}</div>
        <div class='line-title'>Duration Units:</div>
        <div class='line-item'>{{stringFormatter(getConfiguration.duration.units)}}</div>
        <div class='line-title'>Surface Temperature:</div>
        <div class='line-item'>210K | -63C</div>
        <div class='line-title'>Solar Gain:</div>
        <div class='line-item'>500 W/m<sup>2</sup></div>
        <div class='line-title'>Atmospheric Pressure:</div>
        <div class='line-item'>0.636 kPa</div>
        <div class='line-title'>Gravity:</div>
        <div class='line-item'>7.11 m/s<sup>2</sup></div>
    </div>
</template>


<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {
    computed:{
        ...mapGetters('wizard',['getConfiguration']),
        ...mapGetters('dashboard',['getAirStorageRatio','getTotalAgentMass','getStepBuffer','getAgentType']),
    },
    methods:{
        stringFormatter: function(value){
            let formatted = ""

            formatted = value.replace(/_/g," ")
            formatted = formatted.toLowerCase()
                    .split(" ")
                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                    .join(" ")

            return formatted   
        }
    }
}
</script>


<style lang="scss" scoped>

</style>
