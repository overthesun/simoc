<template>
    <div class='panel' :class="[overrideDisplay ? 'disableDisplay' : '']">
        <div class='title'>Mission Stats</div>
        <div class='interior'></div>
        <div class='interior'></div>
        <div class='interior'></div>
    </div>
</template>

<script>
import {mapState,mapGetters,mapActions} from 'vuex'
export default {
    props:{
        overrideDisplay:Boolean
    },

    computed:{
        ...mapGetters('configuration',[
            'getLocation',
            'getDuration',
            'getHumans',
            'getFood',
            'getCrewQuarters',
            'getEclss',
            'getPowerGenerator',
            'getPowerStorage',
            'getGreenhouse',
            'getPlantSpecies',
        ])
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/mediaqueries';
    @import '../../sass/components/dashpanel';

    .disableDisplay{
        display:none;

        @include for-md-desktop-up{
            display:grid;
        }
    }


</style>
