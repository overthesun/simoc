<!-- Component to house all graphs related to the reference sectoin of the wizard. This component would have a 
similar functionality to that of the reference wiki. Table of contents to select which graph is active.
-->

<template>
        <GreenhouseDoughnut/>   
</template>

<script>
import {GreenhouseDoughnut} from '../../components/graphs'
export default {
    components:{
        'GreenhouseDoughnut':GreenhouseDoughnut
    }
}
</script>

<style lang="scss" scoped>
    .graphs-wrapper{
        width: 100%;
        height: 100%;
        position:relative;
    }
</style>
