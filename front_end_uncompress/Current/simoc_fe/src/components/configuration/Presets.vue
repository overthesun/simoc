<!-- This particular component has one job and that is to populate and create the PRESETS field at the top of the finalization screen. This would also be at the 
top of the expert(finalized screen only) configuration screen too. Selecting one of these will trigger the getConfiguration watcher in all configuration form components.

Presets should really be stored within the database and retrieved similar to that of the plant names.

Future version would also retrieve any saved configurations the user has saved either in cookies or under a user profile. 

Future version should also automatically switch the selected preset to 'custom' if the current configuration doesn't match all field values within each configuration
-->

<template>
    <form class='form-wrapper' @submit.prevent="">
        <label class='input-wrapper'>
            <div class='input-title'>Presets</div>
            <div class='input-description'>Let us choose for you.</div>
            <div class='input-duration-wrapper'>
                <select class='input-field-select' v-model="presets" v-on:change="SETCONFIGURATION(presets)">
                    <option :value=none hidden disabled selected>Preset</option>
                    <option :value=humansonly>Humans Only</option>
                    <option :value=hybridone>Hybrid One</option>
                    <option :value=hybridtwo>Hybrid Two</option>
                    <option :value=hybridthree>Hybrid Three</option>
                    <option :value=hybridfour>Hybrid Four</option>
                    
                </select>
            </div>
        </label>
    </form>    
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    data(){
        return{
            presets:{
                location:"none",
                duration:{type:"none",amount:'0',units:"none"},
                humans:{type:"none",amount:'0',units:""},
                food:{type:"none",amount:'0',units:""},
                crewQuarters:{type:"none",amount:'0',units:""},
                eclss:{type:"none",amount:'0',units:""},
                powerGeneration:{type:"none",amount:'0',units:""},
                powerStorage:{type:"none",amount:'0',units:""},
                greenhouse:{type:"none",amount:'0',units:""},
                plantSpecies:[],
            },
            humansonly:{
                location:"none",
                duration:{type:"none",amount:'30',units:"day"},
                humans:{type:"none",amount:2,units:""},
                food:{type:"none",amount:'10000',units:""},
                crewQuarters:{type:"crew_habitat_small",amount:'0',units:""},
                eclss:{type:"none",amount:'1',units:""},
                powerGeneration:{type:"solar_arrays",amount:'2',units:""},
                powerStorage:{type:"none",amount:'1',units:""},
                greenhouse:{type:"none",amount:'0',units:""},
                plantSpecies:[],
            },
        
            hybridone:{
                location:"none",
                duration:{type:"none",amount:'90',units:"day"},
                humans:{type:"none",amount:2,units:""},
                food:{type:"none",amount:'10000',units:""},
                crewQuarters:{type:"crew_habitat_small",amount:'1',units:""},
                eclss:{type:"none",amount:'0',units:""},
                powerGeneration:{type:"solar_arrays",amount:'3',units:""},
                powerStorage:{type:"none",amount:'1',units:""},
                greenhouse:{type:"greenhouse_small",amount:'1',units:""},
                plantSpecies:[{"type":"cabbage","amount":100}],
            },
            hybridtwo:{
                location:"none",
                duration:{type:"none",amount:'90',units:"day"},
                humans:{type:"none",amount:2,units:""},
                food:{type:"none",amount:'10000',units:""},
                crewQuarters:{type:"crew_habitat_small",amount:'1',units:""},
                eclss:{type:"none",amount:'0',units:""},
                powerGeneration:{type:"solar_arrays",amount:'3',units:""},
                powerStorage:{type:"none",amount:'1',units:""},
                greenhouse:{type:"greenhouse_small",amount:'1',units:""},
                plantSpecies:[{"type":"wheat","amount":100}],
            },
            hybridthree:{
                location:"none",
                duration:{type:"none",amount:'90',units:"day"},
                humans:{type:"none",amount:2,units:""},
                food:{type:"none",amount:'10000',units:""},
                crewQuarters:{type:"crew_habitat_small",amount:'1',units:""},
                eclss:{type:"none",amount:'0',units:""},
                powerGeneration:{type:"solar_arrays",amount:'20',units:""},
                powerStorage:{type:"none",amount:'1',units:""},
                greenhouse:{type:"greenhouse_small",amount:'1',units:""},
                plantSpecies:[{"type":"wheat","amount":100}],
            },
            hybridfour:{
                location:"none",
                duration:{type:"none",amount:'90',units:"day"},
                humans:{type:"none",amount:4,units:""},
                food:{type:"none",amount:'10000',units:""},
                crewQuarters:{type:"crew_habitat_small",amount:'1',units:""},
                eclss:{type:"none",amount:'1',units:""},
                powerGeneration:{type:"solar_arrays",amount:'30',units:""},
                powerStorage:{type:"none",amount:'1',units:""},
                greenhouse:{type:"greenhouse_small",amount:'1',units:""},
                plantSpecies:[
                    {"type":"wheat","amount":50},
                    {"type":"cabbage","amount":50},
                    {"type":"strawberry","amount":50},
                    {"type":"radish","amount":50},
                    {"type":"red_beet","amount":33},
                    {"type":"lettuce","amount":34}
                ],
            },
            none:{
                location:"none",
                duration:{type:"none",amount:'0',units:"none"},
                humans:{type:"none",amount:'0',units:""},
                food:{type:"none",amount:'0',units:""},
                crewQuarters:{type:"none",amount:'0',units:""},
                eclss:{type:"none",amount:'0',units:""},
                powerGeneration:{type:"none",amount:'0',units:""},
                powerStorage:{type:"none",amount:'0',units:""},
                greenhouse:{type:"none",amount:'0',units:""},
                plantSpecies:[],
            },
        }
    },
    methods:{
        ...mapMutations('wizard',['SETCONFIGURATION'])
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/components/configuration-input';


</style>
