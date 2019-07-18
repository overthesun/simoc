<template>
    <div class='panel-graph'>
        <EnergyVersus :id="'canvas-energy' + canvasNumber"/>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
import {EnergyVersus} from '../../components/graphs'

export default {
    props:{
        canvasNumber:0,
    },
    components:{
       'EnergyVersus':EnergyVersus,
    },
}
</script>


<style lang="scss" scoped>

</style>
