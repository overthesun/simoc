<template>
    <div class='panel'>
        <div class='panel-title'>
            Test Title For Panel
        </div>
        <div class='panel-interior'>
            <GreenhouseConfigItem/>
        </div>
        <div class='panel-interior panel-two'>
            <div class='wrapper'>
                <Gauge :id="'canvas1'" :color="'#00aaee'" :value="3" :remainder="2"/>
            </div>
            <div class='wrapper'>
                <Gauge :id="'canvas2'"/>
            </div>
            <div class='wrapper'>
                <Gauge :id="'canvas3'"/>
            </div>
            <div class='wrapper'>
                <Gauge :id="'canvas4'"/>
            </div>
            <div class='wrapper'>
                <Gauge :id="'canvas5'"/>
            </div>
            <div class='wrapper'>
                <Gauge :id="'canvas6'"/>
            </div>
        </div>
        <div class='panel-interior'>
            <GreenhouseConfig />
        </div>
    </div>
</template>

<script>
import {Gauge,GreenhouseConfig} from '../graphs'
import {GreenhouseConfigItem} from '../panels'
export default {
    components:{
        "Gauge":Gauge,
        "GreenhouseConfig":GreenhouseConfig,
        "GreenhouseConfigItem":GreenhouseConfigItem
    }
}
</script>

<style lang="scss" scoped>
    @import "../../sass/mediaqueries";

    .panel{
        padding: 6px 16px;
        flex: 1 100%;
        height: 100%;
        background-color: rgba(#1e1e1e,.85);

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-around;
    
        &:first-of-type{
            margin: none;
            margin-left: 32px;
        }

        &:nth-of-type(2n+0){
            margin: 0px 32px;
        }

        &:last-of-type{
            margin-right: 32px;
        }
    }

    .panel-title{
        height: 56px; 
        min-height: 56px;
        border-bottom: 1px solid #302f2f;
        width: 100%;

        display: flex;
        justify-content: flex-start;
        align-items: center;
        font-size: 16px;
        font-weight: 600;
        font-style:italic;
    }

    .panel-interior{
        position: relative;
        flex: 1 100%;
        height: 100%;
        width: 100%;
        margin: 8px 0px;
        box-sizing: border-box;
        overflow-y:auto;
    }

    .panel-two{
        display: grid;
        grid-template-rows: 1fr 1fr;
        grid-row-gap: 2px;
        grid-column-gap: 16px;
        grid-template-columns: 1fr 1fr 1fr;
        overflow-y:hidden;
    }

    .wrapper{
        width: 100%;
        height: 100%;
        position: relative;
    }   

    .desktop-only{
        display:none;

        @include for-md-desktop-up{
            display:inherit;
        }
    }

</style>
