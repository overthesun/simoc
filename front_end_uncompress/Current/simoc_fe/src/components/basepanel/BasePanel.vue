<template v-slot:panel-content>
    <div class='panel'>
        <div class='panel-title'>
            <slot name='panel-title'></slot>
            <slot name='panel-select'></slot>
        </div>
        <slot name='panel-content'></slot>
    </div>
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    data(){
        return{
            
        }
    }
}
</script>

<style lang="scss" scoped>
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
        display:flex;
        justify-content:flex-start;
        align-items:center;
    }

    .panel-select{
        margin-left:auto;
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
