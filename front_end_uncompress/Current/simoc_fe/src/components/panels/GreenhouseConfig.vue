<template>
    <div class='panel-graph-doughnut'>
        <GreenhouseDoughnut :id="'canvas'+ canvasNumber"/>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
import {GreenhouseConfig} from '../../components/graphs'

export default {
    props:{
        canvasNumber:0,
    },
    components:{
       'GreenhouseConfig':GreenhouseConfig,
    },
}
</script>


<style lang="scss" scoped>

</style>
