<template>
    <div class='wrapper'>
        <div class='input-wrapper'>
            <label class='input-label'>
                <div class='title-wrapper'>
                    <span class='input-title'>Humans - </span>
                    <span class='input-snippet'>Placeholder for simple description</span>
                </div>                
                <input type='text' class='input-number'  name="humansAmount" :value="humans.amount" v-on:input="handleChange"/>
                <div class='input-reminder-wrapper'></div>
            </label>
        </div>
    </div>
</template>

<script>
import store from '@/store'
import {mapState,mapGetters} from 'vuex'
export default {
    computed:{
        ...mapGetters(['humans','food','crewQuarters','eclss']),      
    },
    props:{
        handleChange:Function
    }

}
</script>

<style lang="scss" scoped>
    .wrapper{
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 100%;
    }

    .input-title,.input-snippet{
        font-size: 14px;   
    }
    
    .input-title{
        font-weight: 600;
    }

    .input-snippet{
        font-weight: 200;
        font-style:italic;
    }
    
    .input-wrapper{
        position: relative;
        margin-bottom: 16px; 
    }


    .input-number{
        border:none;
        background:none;
        font-size: 18px;
        color: #eee;
        border-bottom: 1px solid #eee;
        margin: 4px 0px 0px 0px;
    }

    input[type='number']{
         -moz-appearance:textfield;
    }

    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
</style>
