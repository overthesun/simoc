<template>
    <div class='item-wrapper'>
        <div class='line-wrapper'>
            <div class='line-title'>Greenhouse Type:</div>
            <div class='line-item'>{{formattedPlantNames(getGreenhouse.type)}}</div>
        </div>
        <div class='plant-wrapper' v-for="(line,index) in getPlantSpecies" :key="index">
            <div class='line-title'>Plant Species:</div>
            <div class='line-item'>{{formattedPlantNames(getPlantSpecies[index].type)}}</div>
            <div class='line-title'>Qty:</div>
            <div class='line-item'>{{getPlantSpecies[index].amount}}</div>
        </div>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    computed:{
        ...mapGetters('configuration',['getPlantSpecies','getGreenhouse','getPlantSpeciesTypes']),
    },

    methods:{
        formattedPlantNames:function(name){
            let formatted = ""

            formatted = name = name.replace(/_|-/g," ")
            formatted = name.toLowerCase()
                    .split(" ")
                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                    .join(" ")
            
            return formatted
        },
    }
}
</script>

<style lang="scss" scoped>
    .item-wrapper{
        width: 100%;
        display:flex;
        justify-content: flex-start;
        align-items: flex-start;
        flex-direction: column;

    }

    .line-wrapper{
        width: 100%;
        display: grid;
        grid-template-columns: 1.5fr 2fr;
        margin-bottom: 16px;
    }

    .plant-wrapper{
        width: 100%;
        display: grid;
        grid-template-columns: 1.5fr 1.5fr .75fr .75fr;
        margin-bottom: 8px;
    }
</style>
