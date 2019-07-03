<template>
    <div class='form-wrapper'>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'humans')">HUMANS</div>
            <div class='section-subtitle'>The people that will be living in your community.</div>
            <div class='input-wrapper'>
                <input type='text' class='input-number' name="configuration/humansAmount" :value="getHumans.amount" size=4 v-on:input="handleChange"/>
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'food')">FOOD</div>
            <div class='section-subtitle'>People have got to eat something while the plants grow.</div>
            <div class='input-wrapper'>
                <input type='text' class='input-number' name="configuration/foodAmount" :value="getFood.amount" size=4 v-on:input="handleChange"/>
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'crewQuarters')">CREW QUARTERS</div>
            <div class='section-subtitle'>Home is where the head rest.</div>
            <div class='input-wrapper'>
                <select class='input-select' name='configuration/crewQuartersType' :selected="getCrewQuarters.type" v-on:input="handleChange">
                    <option value="none">None</option>
                    <option value="crew_habitat_small">Small 1000 m^3</option>
                    <option value="crew_habitat_medium">Medium 2260 m^3</option>
                    <option value="crew_habitat_large">Large 4020 m^3</option>
                </select>
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>
        <div class='section-wrapper'>
            <div class='section-title' @click="handleEntry($event,'elcss')">ECLSS</div>
            <div class='section-subtitle'>Very complicated air conditioning rack, air and water filters too.</div>
            <div class='input-wrapper'>
                <input type='text' class='input-number' name="configuration/eclssAmount" :value="getEclss.amount" size=4 v-on:input="handleChange"/>
            </div>
            <div class='input-warning hidden'>Test out the warning text</div>
        </div>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    computed:{
        ...mapGetters('configuration',['getHumans','getFood','getCrewQuarters','getEclss']),      
    },

    props:{
        handleChange:Function,
        handleEntry:Function,
    },

    methods:{
        ...mapMutations('configuration',['humansAmount'])
    }

}
</script>

<style lang="scss" scoped>
    @import "../../sass/components/configuration-form-internal";
</style>
