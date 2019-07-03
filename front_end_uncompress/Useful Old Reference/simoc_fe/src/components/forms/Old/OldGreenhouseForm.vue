<template>
    <div class='form-wrapper'>
        <div class='input-wrapper'>
            <label class='input-label'>
                <div class='title-wrapper'>
                    <span class='input-title'>Greenhouse - </span>
                    <span class='input-snippet'>Placeholder for the added text</span>
                </div>
                <select class='input-select' name='greenhouseType' :selected="greenhouse.type" v-on:input="handleChange">
                    <option value="none">None</option>
                </select>
                <div class='input-reminder-wrapper'>
                </div>
            </label>
        </div>
        <div class='input-wrapper'>
            <label class='input-label'>
                <div class='title-wrapper'>
                    <span class='input-title'>Plants - </span>
                    <span class='input-snippet'>Placeholder for the added text</span>
                </div>
                <span class='input-number input-number--quantity'>Species</span>
                <select class='input-select' name='greenhouseType' :selected="greenhouse.type" v-on:input="handleChange">
                    <option value="none">None</option>
                </select>
                <span class='input-number input-number--quantity'>Qty:</span>
                <input type='text' class='input-number input-number--qty' name="humansAmount" value="0"/>
                <div class='input-reminder-wrapper'>
                </div>
            </label>
        </div>
        <fa-icon class='fa-icon navigation-icon' :icon="['fas','plus-circle']"/>
    </div>    
</template>

<script>
import {mapState,mapGetters} from 'vuex'
export default {
    name:'GreenhouseForm',

    computed:{
        ...mapGetters('greenhouse',['greenhouse']),      
    },

    props:{
        handleChange:Function
    },

    methods:{

    }

}
</script>

<style lang="scss" scoped>
    .input-wrapper{
        margin-bottom: 32px;
        position: relative;
    }

    .title-wrapper{
        margin-bottom: 4px;
    }

    .input-title{
        font-weight: 600;
    }

    .input-snippet{
        font-weight: 200;
        font-style: italic;
    }

    .input-number,.input-select{
        border:none;
        background:none;
        color: #eee;
        font-size: 18px;
        border-bottom: 1px solid #eee;
        margin: 4px 0px 0px 0px;
        width: 10rem;
    }

    .input-number--quantity{
        font-weight: 200;
        font-style: italic;
        margin: 0px 8px 0px 16px;
        border:none;
    }
    
    .input-number--qty{
        width: 5rem;
    }

    option{
        color:#1e1e1e;
    }

    .input-reminder-wrapper{
        position: absolute;
        bottom: -20px;
    }

    .input-reminder{
        font-size: 12px;
        margin-right: 4px;
    }

    .input-reminder--warning{
        color: #f42929 !important;
    }


</style>

