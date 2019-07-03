<template>
    <div class='session-wrapper session-wrapper--reference'>
        <div class='content-wrapper content-wrapper--reference'>
            <header class='header'>
                <div class='navigation-link' :class="{active: 'reference' === isActive}" @click="activate('reference')">Encyclopedia</div>
                <div class='navigation-link' :class="{active: 'graphs' === isActive}"  @click="activate('graphs')">Graphs</div>
                <div class='navigation-link' :class="{active: 'recommended' === isActive}"  @click="activate('recommended')">Recommended</div>
                <div class='navigation-link' :class="{active: 'menu' === isActive}"  @click="activate('menu')">Menu</div>               
                <!--<div class='navigation-link navigation-link--menu'>
                    <fa-icon class='fa-icon navigation-icon' :icon="['fal','bars']"/>
                </div>-->
            </header>
            <main class='main'>
                <keep-alive>
                    <component :is="isActive"/>
                </keep-alive>
             </main>
            <footer class='footer'>
             </footer>
        </div>
    </div>
</template>


<script>
import {Reference} from '../reference'
import {GreenhouseConfig,PowerUsage} from '../graphs'
export default {
    components:{
        "reference":Reference,
        "graphs":GreenhouseConfig
        //"recommended"
    },

    data(){
        return{
            isActive:'reference'
        }
    },

    methods:{
        activate:function(string){
            this.isActive = string
        }       
    }

}
</script>

<style lang="scss" scoped>
    @import "../../sass/components/configuration-session";

    .session-wrapper--reference{
        background-color: rgba(#252525,.75);
    }

    .navigation-link{
        font-size: 1.15rem;
        position: relative;
        font-weight: 400;
        &:not(:last-of-type){
            margin-right: 24px;
        }
    }

    .navigation-link--menu{
        margin-left:auto;        
        font-size: 2.25rem;
    }

    .main{
        position:relative;
        display:flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 16px;
        box-sizing:border-box;
    }

    .chart-wrapper{
        position:relative;
        width: 384px;

        &:before{
            content:"";
            display:block;
            padding-top:100%;
            box-sizing: border-box;
        }
    }

    .navigation-link{
        &:after{
            position: absolute;
            right: 0;
            display:block;
            content:"";
            width: 0;
            border-bottom: 3px solid lightgreen;
            margin-top: 8px;
            transition: width .2s ease;
        }
    }

    .active{
        &:after{
            width: 100%;     
            left: 0;      
        }
    }

</style>
