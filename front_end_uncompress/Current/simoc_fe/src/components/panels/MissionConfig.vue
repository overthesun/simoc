<template>
    <div class='two-line-wrapper'>
        <div class='line-title'>Location:</div>
        <div class='line-item'>Mars</div>
        <div class='line-title'>Duration Length:</div>
        <div class='line-item'>{{getConfiguration.duration.amount}} {{stringFormatter(getConfiguration.duration.units)}}</div>
        <div class='line-title'>Inhabitants:</div>
        <div class='line-item'>{{getConfiguration.humans.amount}}</div>
        <div class='line-title'>Food:</div>
        <div class='line-item'>{{getConfiguration.food.amount}}</div>
        <div class='line-title'>Crew Quarters:</div>
        <div class='line-item'>{{stringFormatter(getConfiguration.crewQuarters.type)}}</div>
        <div class='line-title'>ECLSS:</div>
        <div class='line-item'>{{getConfiguration.eclss.amount}}</div>
        <div class='line-title'>Greenhouse:</div>
        <div class='line-item'>{{stringFormatter(getConfiguration.greenhouse.type)}}</div>
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
