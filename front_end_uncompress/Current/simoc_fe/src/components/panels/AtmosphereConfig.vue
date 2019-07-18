<template>
    <div class='panel-graph-gauge'>
        <div class='gauge-wrapper' style='position:relative'>
            <Gauge :id="'canvas1'+id" :color="'#00aaee'" :keyValue="'atmo_co2'" :maximum=".03" :getter="getAirStorageRatio"/>
            <div class='gauge-text'>CO<sub>2</sub> (0-3%)</div>
        </div>
        <div class='gauge-wrapper' style='position:relative'>
            <Gauge :id="'canvas2'+id" :color="'#00aaee'" :keyValue="'atmo_o2'" :maximum="1.0" :getter="getAirStorageRatio"/>
            <div class='gauge-text'>O<sub>2</sub> (0-100%)</div>
        </div>
        <div class='gauge-wrapper' style='position:relative'>
            <Gauge :id="'canvas3'+id" :color="'#00aaee'" :keyValue="'atmo_h2o'" :maximum="1.0" :getter="getAirStorageRatio"/>
            <div class='gauge-text'>H<sub>2</sub>O Vapor (0-100%)</div>
        </div>
        <div class='gauge-wrapper' style='position:relative'>
            <Gauge :id="'canvas4'+id" :color="'#00aaee'" :keyValue="'atmo_h2'" :maximum=".01" :getter="getAirStorageRatio"/>                    
            <div class='gauge-text'>H<sub>2</sub> (0-1%)</div>
        </div>
        <div class='gauge-wrapper' style='position:relative'>
            <Gauge :id="'canvas5+id'" :color="'#00aaee'" :keyValue="'atmo_n2'" :maximum="1.0" :getter="getAirStorageRatio"/>
            <div class='gauge-text'>N<sub>2  (0-100%)</sub></div>
        </div>
        <div class='gauge-wrapper' style='position:relative'>
            <Gauge :id="'canvas6'+id" :color="'#00aaee'" :keyValue="'atmo_ch4'" :maximum=".01" :getter="getAirStorageRatio"/>
            <div class='gauge-text'>CH<sub>4</sub> (0-1%)</div>
        </div>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
import {Gauge} from '../../components/graphs'
export default {
    props:{
        id:String,
    },
    components:{
       'Gauge':Gauge,
    },
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
