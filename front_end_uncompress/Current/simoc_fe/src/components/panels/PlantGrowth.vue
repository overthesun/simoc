<template>
    <div class='plant-wrapper'>
        <section class='plant-row-wrapper'>
            <span class='section-title'>Plant Species</span>
            <span class='section-title' style="text-align:center;">Qty</span>
            <span class='section-title' style="text-align:right;">% of Growth</span>
        </section>
        <section class='plant-row-wrapper' v-for="(item,index) in getConfiguration.plantSpecies" :key="index">
            <div class='line-item' >
                {{stringFormatter(getConfiguration.plantSpecies[index].type)}}
            </div>
            <div class='line-item' style="text-align:center;">
                {{getConfiguration.plantSpecies[index].amount}}
            </div>
            <div class='line-item' style="text-align:right;">
                {{getTotalAgentMass(getStepBuffer.current)[getConfiguration.plantSpecies[index].type].value + "%"}}
            </div>
        </section>
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
    .plant-row-wrapper{
        display:grid;
        grid-template-columns: minmax(0px,1fr) minmax(0px,1fr) minmax(0px,1fr);
        grid-column-gap: 8px;
    }
</style>
