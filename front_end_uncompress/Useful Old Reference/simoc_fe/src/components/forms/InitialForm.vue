<template>

    <div class="form-wrapper">
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'location')">LOCATION</div>
            <div class='section-subtitle'>The destination of your off-world vacation</div>
            <div class='input-wrapper'>
                <select class='input-select' name="configuration/locationType" :selected="getLocation.type" v-on:input="handleChange">
                    <option class='option' value="none" disabled selected hidden>Location</option>
                    <option class='option' value="mars">Mars</option>
                    <option class='option' value="none" disabled>Earth</option>
                    <option class='option' value="none" disabled>Lunar Surface</option>
                    <option class='option' value="none" disabled>Earth Orbit</option>
                </select>
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'duration')">DURATION</div>
            <div class='section-subtitle'>How long you will be staying</div>
            <div class='input-wrapper'>
                <select class='input-select' name='configuration/durationType' :selected="getDuration.type" v-on:input="handleChange">
                    <option value="none" disabled hidden :selected="'none' === getDuration.type || null === getDuration.type">Duration Units</option>
                    <option :value="'hours'" :selected="'hours' === getDuration.type">Hours</option>
                    <option :value="'days'" :selected="'days' === getDuration.type">Sols</option>
                    <option :value="'months'" :selected="'months' === getDuration.type">Solar Months</option>
                    <option :value="'year'" :selected="'years' === getDuration.type">Solar Years </option>
                </select>
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>        
    </div>
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {

    computed:{
        ...mapGetters('configuration',['getDuration','getLocation']),
    },

    methods:{
        ...mapMutations('configuration',['locationType','durationType','durationAmount']),
    },

    props:{
        handleChange:Function,
        handleIndex:Function,
        handleEntry:Function,
    },
}
</script>

<style lang="scss" scoped>
    @import "../../sass/components/configuration-form-internal";
</style>
