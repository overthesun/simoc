<!-- This is the main view of the dashboard. The intent was to break up each 'panel' into it's own component and use a 'BasePanel' component with slots to populate
the title, and content. Allowing for things like the configuration menu orginally seen on other version, and additional functionality to be placed within the BasePanel
to prevent uncessary duplication as additional planels are created.

-->

<template>
    <div class='dashboard-view-wrapper'>
        <BasePanel v-for="(item,index) in 6" :key="index">
            <template v-slot:panel-title>
                {{panelTitles[activePanel[index]]}}
            </template>
            <template v-slot:panel-select>
                <select class='panel-select' v-model="activePanel[index]"> <!-- Set the activeForm index if the user changes the value to something other than selected -->
                    <option selected disabled>Jump To Section</option>
                    <option value="MissionInformation">Mission Information</option>
                    <option value="MissionConfiguration">Mission Configuration</option>                    
                    <option value="PlantGrowth">Greenhouse Plant Growth</option>
                    <option value="EnergyVersus" >Energy Versus - Graph</option>
                    <option value="GreenhouseConfig" >Greenhouse Configuration - Graph</option>
                    <option value="AtmosphereConfig" >Atmospheric Levels - Graph</option>
                </select>
            </template>
            <template v-slot:panel-content>
                <component :is="activePanel[index]" :canvasNumber="index"></component>
            </template>
        </BasePanel>
    </div>
</template>

<script>
import {BasePanel} from '../../components/basepanel'
import {MissionInfo,MissionConfig,EnergyVersus,PlantGrowth,GreenhouseConfig,AtmosphereConfig} from '../../components/panels'
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
import AtmosphereConfigVue from '../panels/AtmosphereConfig.vue';
export default {
    data(){
        return{
            humans:0,
            activePanel:["MissionInformation","EnergyVersus","MissionConfiguration","PlantGrowth","GreenhouseConfig","AtmosphereConfig"],
            panelTitles:{
                "MissionInformation":"Mission Information",
                "EnergyVersus":"Energy Consumption V. Production - Graph",
                "MissionConfiguration":"Mission Configuration",
                "PlantGrowth":"Greenhouse Plant Growth",
                "GreenhouseConfig":"Greenhouse Configuration - Graph",
                "AtmosphereConfig":"Atmospheric Levels - Gauges"
            }
        }
    },
    components:{
        'BasePanel':BasePanel,
        
        //Graph components imported to be used within the panels.
        'EnergyVersus':EnergyVersus,
        //'Gauge':Gauge,
        'GreenhouseConfig':GreenhouseConfig,
        //'GreenhouseDoughnut':GreenhouseDoughnut,
        'MissionInformation':MissionInfo,
        'MissionConfiguration':MissionConfig,
        'PlantGrowth':PlantGrowth,
        'AtmosphereConfig':AtmosphereConfig
    },
    computed:{
        ...mapGetters('wizard',['getConfiguration']),
        ...mapGetters('dashboard',['getAirStorageRatio','getTotalAgentMass','getStepBuffer','getAgentType']),
    },
    watch:{

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


    .dashboard-view-wrapper{
        width:100%;
        height:100%;
        padding: 16px; 
        box-sizing:border-box;

        display: grid;
        grid-template-columns: repeat(3,minmax(304px,1fr));
        grid-template-rows: repeat(2,minmax(200px,1fr));
        grid-row-gap: 16px;
        grid-column-gap: 16px;
        overflow:hidden;
    }

    /*.panel{
        background-color: #1e1e1e;
        display:grid;
        grid-template-rows: 32px 1fr;
        grid-row-gap: 16px;
        padding:8px;
    }

    .panel-title{
        margin:auto 0px;
        border-bottom: 1px solid #999;
        font-weight: 200;
        font-style:italic;
    }

    .panel-graph{
        position:relative;
    }

    .panel-graph-gauge{
        display:grid;
        grid-template-columns: repeat(3,1fr);
        grid-template-rows: repeat(2,1fr);
        grid-row-gap: 16px;
        grid-column-gap: 16px;
    }

    .panel-graph-doughnut{
        width: 100%;
        height: 100%;
    }

    .two-line-wrapper{
        display:grid;
        grid-template-columns: 1.5fr 1fr;
        grid-template-rows: repeat(auto-fill,32px);
    }

    .line-item,.line-title{
        margin:auto 0px;
    }

    .line-title{
        font-size: 14px;
        font-weight: 200;
    }

    .line-item{
        font-size: 18px;
        font-weight: 600px;
    }

    .plant-wrapper{
        display:grid;
        grid-template-rows: repeat(auto-fill,minmax(32px,1fr));
        grid-template-columns: minmax(0px,1fr);
        grid-row-gap: 4px;
        font-size: 14px;

        *{
            margin: auto 0px;
        }
    }

    .plant-row-wrapper{
        display:grid;
        grid-template-columns: minmax(0px,1fr) minmax(0px,1fr) minmax(0px,1fr);
        grid-column-gap: 8px;
    }

    .section-title{
        font-size: 14px;
        text-decoration: underline;
        font-weight: 200;
    }

    .gauge-wrapper{
        display:grid;
        grid-template-rows: minmax(0px,1fr) 24px;
        grid-row-gap: 8px;
        text-align:center;
    }

    .gauge-text{
        font-size:18px;
        font-weight: 400;
    }*/
</style>
