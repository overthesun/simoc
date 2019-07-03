<!-- This is the main view of the dashboard. The intent was to break up each 'panel' into it's own component and use a 'BasePanel' component with slots to populate
the title, and content. Allowing for things like the configuration menu orginally seen on other version, and additional functionality to be placed within the BasePanel
to prevent uncessary duplication as additional planels are created.

-->

<template>
    <div class='dashboard-view-wrapper'>
        <div class='panel'>
            <div class='panel-title'>Mission Information</div>
            <div class='two-line-wrapper'>
                <div class='line-title'>Location:</div>
                <div class='line-item'>Mars</div>
                <div class='line-title'>Inhabitants:</div>
                <div class='line-item'>{{humanCount}}</div>
                <div class='line-title'>Duration Length:</div>
                <div class='line-item'>{{humans}}</div>
                <div class='line-title'>Duration Units:</div>
                <div class='line-item'>{{stringFormatter(getConfiguration.duration.units)}}</div>
                <div class='line-title'>Surface Temperature:</div>
                <div class='line-item'>210K | -63C</div>
                <div class='line-title'>Solar Gain:</div>
                <div class='line-item'>500 W/m<sup>2</sup></div>
                <div class='line-title'>Atmospheric Pressure:</div>
                <div class='line-item'>0.636 kPa</div>
                <div class='line-title'>Gravity:</div>
                <div class='line-item'>7.11 m/s<sup>2</sup></div>
            </div>
        </div>
        <div class='panel'>
            <div class='panel-title'>Mission Configuration</div>
                <div class='two-line-wrapper'>
                    <div class='line-title'>Location:</div>
                    <div class='line-item'>Mars</div>
                    <div class='line-title'>Duration Length:</div>
                    <div class='line-item'>{{getConfiguration.duration.amount}} {{stringFormatter(getConfiguration.duration.units)}}</div>
                    <div class='line-title'>Inhabitants:</div>
                    <div class='line-item'>{{getConfiguration.humans.amount}}</div>
                    <div class='line-title'>Food:</div>
                    <div class='line-item'>{{getConfiguration.food.amount}}</div>
                    <div class='line-title'>Crew Quarters:</div>
                    <div class='line-item'>{{stringFormatter(getConfiguration.crewQuarters.type)}}</div>
                    <div class='line-title'>ECLSS:</div>
                    <div class='line-item'>{{getConfiguration.eclss.amount}}</div>
                    <div class='line-title'>Greenhouse:</div>
                    <div class='line-item'>{{stringFormatter(getConfiguration.greenhouse.type)}}</div>
                </div>
        </div>
        <div class='panel'>
            <div class='panel-title'>Energy Consumption v Production</div>
            <div class='panel-graph'>
                <EnergyVersus :id="'canvas-energy'"/>
            </div>
        </div>
        <div class='panel'>
            <div class='panel-title'>Plant Species Growth - Line Items</div>
            <div class='plant-wrapper'>
                <section class='plant-row-wrapper'>
                    <span class='section-title'>Plant Species</span>
                    <span class='section-title' style="text-align:center;">Qty</span>
                    <span class='section-title' style="text-align:right;">% of Growth</span>
                </section>
                <section class='plant-row-wrapper' v-for="(item,index) in getConfiguration.plantSpecies" :key="index">
                    <div class='line-item' >
                        {{stringFormatter(getConfiguration.plantSpecies[index].type)}}
                    </div>
                    <div class='line-item' style="text-align:center;">
                        {{getConfiguration.plantSpecies[index].amount}}
                    </div>
                    <div class='line-item' style="text-align:right;">
                        {{getTotalAgentMass(getStepBuffer.current)[getConfiguration.plantSpecies[index].type].value + "%"}}
                    </div>
                </section>
            </div>
        </div>
        <div class='panel'>
            <div class='panel-title'>Greenhouse Configuration - Graph</div>
            <div class='panel-graph-doughnut'>
                <GreenhouseDoughnut/>
            </div>
        </div>
        <!-- Props are used to pass in the values for the gauges to use within the 'Gauge' component. Passing in the getter method
        was simply added so that the gauges were more generalized for future implementations beyond atmospheric tracking.
         -->
        <div class='panel'>
            <div class='panel-title'>Atmospheric Levels - Graph</div>
            <div class='panel-graph-gauge'>
                <div class='gauge-wrapper' style='position:relative'>
                    <Gauge :id="'canvas1'" :color="'#00aaee'" :keyValue="'atmo_co2'" :maximum=".03" :getter="getAirStorageRatio"/>
                    <div class='gauge-text'>CO<sub>2</sub> (0-3%)</div>
                </div>
                <div class='gauge-wrapper' style='position:relative'>
                    <Gauge :id="'canvas2'" :color="'#00aaee'" :keyValue="'atmo_o2'" :maximum="1.0" :getter="getAirStorageRatio"/>
                    <div class='gauge-text'>O<sub>2</sub> (0-100%)</div>
                </div>
                <div class='gauge-wrapper' style='position:relative'>
                    <Gauge :id="'canvas3'" :color="'#00aaee'" :keyValue="'atmo_h2o'" :maximum="1.0" :getter="getAirStorageRatio"/>
                    <div class='gauge-text'>H<sub>2</sub>O Vapor (0-100%)</div>
                </div>
                <div class='gauge-wrapper' style='position:relative'>
                    <Gauge :id="'canvas4'" :color="'#00aaee'" :keyValue="'atmo_h2'" :maximum=".01" :getter="getAirStorageRatio"/>                    
                    <div class='gauge-text'>H<sub>2</sub> (0-1%)</div>
                </div>
                <div class='gauge-wrapper' style='position:relative'>
                    <Gauge :id="'canvas5'" :color="'#00aaee'" :keyValue="'atmo_n2'" :maximum="1.0" :getter="getAirStorageRatio"/>
                    <div class='gauge-text'>N<sub>2  (0-100%)</sub></div>
                </div>
                <div class='gauge-wrapper' style='position:relative'>
                    <Gauge :id="'canvas6'" :color="'#00aaee'" :keyValue="'atmo_ch4'" :maximum=".01" :getter="getAirStorageRatio"/>
                    <div class='gauge-text'>CH<sub>4</sub> (0-1%)</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {GreenhouseConfig,EnergyVersus,Gauge,GreenhouseDoughnut} from '../../components/graphs'
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {
    data(){
        return{
            humans:0
        }
    },
    components:{
        //Graph components imported to be used within the panels.
        'EnergyVersus':EnergyVersus,
        'Gauge':Gauge,
        'GreenhouseConfig':GreenhouseConfig,
        'GreenhouseDoughnut':GreenhouseDoughnut,
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

    .panel{
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
    }
</style>
