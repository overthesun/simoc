<template>
    <div class="form-wrapper">
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'powerGenerator')">POWER GENERATOR</div>
            <div class='section-subtitle'>This will help keep the lights on.</div>
            <div class='input-wrapper'>
                <select class='input-select' name='configuration/powerGeneratorType' :selected="getPowerGenerator.type" v-on:input="handleChange">
                    <option value="none" disabled hidden :selected="'none' === getPowerGenerator.type || null === getPowerGenerator.type">Power Generator</option>
                    <option value="solar_pv_array_mars" :selected="'solar_pv_array_mars' === getPowerGenerator.type">Solar PV Array</option>
                </select>
                <input class='input-number' min="0" step="1" max=10000 placeholder="Qty" name='configuration/powerGeneratorAmount' type='number' :value="getPowerGenerator.amount" v-on:input="handleChange"/>
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'powerStorage')">POWER STORAGE</div>
            <div class='section-subtitle'>Stores the power for when the sun goes down.</div>
            <div class='input-wrapper'>
                <input class='input-number' min="0" step="1" max=10000 placeholder="Qty" name='configuration/powerStorageAmount' type='number' :value="getPowerStorage.amount" v-on:input="handleChange"/>
            </div>
            <div class='input-warning hidden' >Test out the warning text</div>
        </div>
    </div>

</template>

<script>
import axios from 'axios'
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {

    computed:{
        ...mapGetters('configuration',['getPowerGenerator','getPowerStorage']),
    },

    methods:{
        ...mapMutations('configuration',['powerGenerator','powerGeneratorAmount','powerGeneratorType','powerStorageAmount']),
    },

    props:{
        handleChange:Function,
        handleIndex:Function,
        handleSpecial:Function,
        handleEntry:Function,
    },
}
</script>

<style lang="scss" scoped>
    @import "../../sass/components/configuration-form-internal";
    /*.subtitle-wrapper{
        display: flex;
        justify-content: flex-start;
        align-items: center;
        margin-bottom: 12px;
    }

    .input-title{
        margin-right: 4px;
        font-weight: 700;
    }

    .input-snippet{
        font-weight: 200;
        font-style:italic;
    }

    .input-wrapper{
        margin-bottom: 28px;
        position: relative;
        display: flex;
        justify-content:flex-start;
        align-items:center;
    }

    .input-number,.input-select{
        border:none;
        background:none;
        color: #eee;
        font-size: 18px;
        border-bottom: 1px solid #eee;
        margin: 4px 32px 0px 0px;
    }

    .input-number{
        width: 3.5rem;
    }

    .icon{
        &:first-of-type{
            margin-left: 64px;
        }

        margin-right: 18px;
    }

    .input-select{
        width: 9rem;
    }*/

</style>
