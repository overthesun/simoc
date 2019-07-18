<template>
    <div class='panel-graph-doughnut'>
        <GreenhouseDoughnut :id="'canvas'+ canvasNumber"/>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
import {GreenhouseDoughnut} from '../../components/graphs'

export default {
    props:{
        canvasNumber:0,
    },
    components:{
       'GreenhouseDoughnut':GreenhouseDoughnut,
    },
}
</script>


<style lang="scss" scoped>

</style>
