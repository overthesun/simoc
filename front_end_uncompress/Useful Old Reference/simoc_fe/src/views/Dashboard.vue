
<template>
    <div class='dashboard-wrapper'>
        <div class='toolbar-wrapper'></div>
        <div class='view-wrapper'>
            <div class='panel'>
                <div class='panel-title'>Plant Species Growth - Line Items</div>
                <div class='plant-wrapper'>
                    <span class='section-title'>Plant Species</span>
                    <span class='section-title'>Qty</span>
                    <span class='section-title'>% of Growth</span>
                    <div class='plant-wrapper' v-for="(item,index) in getPlantSpecies" :key="index">
                        <div class='line-title' >
                            {{formattedPlantNames(getPlantSpecies[index].type)}}
                        </div>
                        <div class='line-item'>
                            {{formattedPlantNames(getPlantSpecies[index].amount)}}
                        </div>
                        <div class='line-item'>
                            0%
                        </div>
                    </div>
                </div>
            </div>
            <div class='panel'>
                <div class='panel-title'>Greenhouse Configuration - Graph</div>
                <div class='panel-graph'>
                    <GreenhouseConfig/>
                </div>
            </div>
            <div class='panel'>
                <div class='panel-title'>Mission Information</div>
                <div class='two-line-wrapper'>
                    <div class='line-title'>Location:</div>
                    <div class='line-item'>Mars</div>
                    <div class='line-title'>Inhabitants:</div>
                    <div class='line-item'>{{getHumans.amount}}</div>
                    <div class='line-title'>Duration Length:</div>
                    <div class='line-item'>{{getDuration.amount}}</div>
                    <div class='line-title'>Duration Units:</div>
                    <div class='line-item'>{{getDuration.type}}</div>
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
                <div class='panel-title'>Atmospheric Levels - Graph</div>
                <div class='panel-graph-gauge'>
                    <div style='position:relative'>
                        <Gauge :id="'canvas1'" :color="'#00aaee'" :keyValue="'atmo_co2'" :maximum=".03" :getter="getAirStorageRatio"/>
                    </div>
                    <div style='position:relative'>
                        <Gauge :id="'canvas2'" :color="'#00aaee'" :keyValue="'atmo_o2'" :maximum="1.0" :getter="getAirStorageRatio"/>
                    </div>
                    <div style='position:relative'>
                        <Gauge :id="'canvas3'" :color="'#00aaee'" :keyValue="'atmo_h2o'" :maximum="1.0" :getter="getAirStorageRatio"/>
                    </div>
                    <div style='position:relative'>
                        <Gauge :id="'canvas4'" :color="'#00aaee'" :keyValue="'atmo_h2'" :maximum=".01" :getter="getAirStorageRatio"/>                    </div>
                    <div style='position:relative'>
                        <Gauge :id="'canvas5'" :color="'#00aaee'" :keyValue="'atmo_n2'" :maximum="1.0" :getter="getAirStorageRatio"/>
                    </div>
                    <div style='position:relative'>
                        <Gauge :id="'canvas6'" :color="'#00aaee'" :keyValue="'atmo_ch4'" :maximum=".01" :getter="getAirStorageRatio"/>
                    </div>
                </div>
            </div>
                <div class='panel'>
                <div class='panel-title'>Energy Consumption v Production</div>
                <div class='panel-graph'>
                    <EnergyVersus :id="'canvas-energy'"/>
                </div>
            </div>
            <div class='panel'>
                <div class='panel-title'>Mission Configuration</div>
                <div class='two-line-wrapper'>
                    <div class='line-title'>Location:</div>
                    <div class='line-item'>Mars</div>
                    <div class='line-title'>Duration Length:</div>
                    <div class='line-item'>{{getDuration.amount}} {{getDuration.type}}</div>
                    <div class='line-title'>Inhabitants:</div>
                    <div class='line-item'>{{getHumans.amount}}</div>
                    <div class='line-title'>Food:</div>
                    <div class='line-item'>{{getFood.amount}}</div>
                    <div class='line-title'>Crew Quarters:</div>
                    <div class='line-item'>{{getCrewQuarters.type}}</div>
                    <div class='line-title'>ECLSS:</div>
                    <div class='line-item'>{{getEclss.amount}}</div>
                    <div class='line-title'>Greenhouse:</div>
                    <div class='line-item'>{{getGreenhouse.type}}</div>
                </div>
            </div>
        </div>
        <div class='timeline-wrapper'>
            <div class='controls-wrapper'>
                <div class='step-wrapper'>{{getStepNumber}}</div>
                <fa-icon class='fa-icon navigation-icon' :icon="['fal','backward']"/>
                <fa-icon class='fa-icon fa-icon-play navigation-icon' :icon="['fal','play-circle']"/>
                <fa-icon class='fa-icon navigation-icon' :icon="['fal','forward']"/>
                <div class='step-wrapper'>{{getDuration.amount}} </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import {GreenhouseConfig,EnergyVersus,Gauge} from '../components/graphs'
import {Primary} from '../components/dashviews'
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {
    components:{
        'Primary':Primary,
        'GreenhouseConfig':GreenhouseConfig,
        'Gauge':Gauge,
        'EnergyVersus':EnergyVersus
    },

    mounted(){
        //console.log("TEST");
        this.getStepTo()
    },

    computed:{
        ...mapGetters('configuration',['getPlantSpecies','getHumans','getDuration','getFood','getCrewQuarters','getEclss','getGreenhouse']),
        ...mapGetters('stepData',['getStorageRatio','getAirStorageRatio']),
        ...mapGetters('stepData',['getStepNumber']),
    },

    methods:{
        ...mapMutations('stepData',['incrementStepNumber']),
        ...mapActions('stepData',['parseStep']),  


        formattedPlantNames:function(name){
            let formatted = ""

            formatted = name = name.replace(/_|-/g," ")
            formatted = name.toLowerCase()
                    .split(" ")
                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                    .join(" ")
            
            return formatted
        },

        getStepTo:function(){
            console.log("TEST");
            axios.defaults.withCredentials = true

            const localHost = "http://localhost:8000"
            const path = '/get_step_to'

            const target = localHost + path
            const params = {step_num:100}

            axios.get(target,{params:params})
            .then(response =>{
                if(response.status === 200){
                    this.getSteps()     
                }
            })
        },

        getSteps:function(){
            axios.defaults.withCredentials = true
            const localHost = "http://localhost:8000"
            const path = '/get_steps'

            const target = localHost + path

            const params = {  
                "min_step_num": 1, 
                "n_steps": 100,
                "total_production":["atmo_co2","atmo_o2","h2o_potb","enrg_kwh"],
                "total_consumption":["atmo_o2","h2o_potb","enrg_kwh"],
                "storage_ratios":{"air_storage_1":["atmo_co2","atmo_o2","atmo_ch4","atmo_n2","atmo_h2","atmo_h2o"]},
                "parse_filters":[]
            }
            axios.post(target,params)
                .then(response =>{
                    if(response.status == 200){
                        let array = Object.values(response.data)
                        this.parseStep(array)     
                        this.updateStepInterval()
                    }
                })
        },

        updateStepInterval(){
            let updateIntervalID = setTimeout( ()=>{
                this.incrementStepNumber()
                this.updateStepInterval()
            }, 1000)
        }
    },
}
</script>

<style lang="scss" scoped>

   .dashboard-wrapper{
        display: grid;

        width: 100vw;
        height: 100vh;
        min-width: 100vw;
        min-height: 100vh;

        grid-template-rows: auto 1fr auto;
        grid-template-columns: 160px 1fr;
        font-family: 'open sans'; 
    }

    .toolbar-wrapper{
        background-color: #181818;
        grid-area: span 2 / span 1;
    }

    .view-wrapper{
        padding: 16px;
        box-sizing:border-box;

        //background-color: blue;
        grid-area: span 2 / span 1;

        display: grid;
        grid-template-columns: repeat(3,minmax(304px,1fr));
        grid-template-rows: repeat(2,minmax(200px,1fr));
        grid-row-gap: 16px;
        grid-column-gap: 16px;
        overflow:hidden;
    }

    .timeline-wrapper{
        background-color: #1e1e1e;
        grid-area: span 1 / span 2;
        height: 96px;
        display:flex;
        justify-content:center;
        align-items:center;
    }

    .controls-wrapper{
        margin: auto 0px;
        height: 64px;
        width: auto;
        display:grid;
        grid-template-columns: repeat(5,96px);
        grid-column-gap: 4px;
        *{
            margin: auto auto;
        }
    }

    .fa-icon{
        font-size: 32px;
    }

    .fa-icon-play{
        font-size: 48px;
    }

    .step-wrapper{
        font-size: 24px;
        font-weight: 400;
    }

    .panel{
        background-color: rgba(#1e1e1e,.75);
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

    .plant-wrapper{
        display:grid;
        grid-template-rows: repeat(auto-fill,minmax(32px,1fr));
        grid-template-columns: 1.5fr 1fr 1fr;
        grid-row-gap: 4px;
        font-size: 14px;

        *{
            margin: auto 0px;
        }
    }

    .section-title{
        width: auto;
        display:block;
        border-bottom: 1px solid #eee;
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

    .plant-wrapper{
        grid-column: span 3;
    }
</style>
