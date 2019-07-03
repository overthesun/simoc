<!-- Energy Configuration Wizard Form -->

<template>
    <form class='form-wrapper'@submit.prevent="">
        <label class='input-wrapper'>
            <div class='input-title'  @click="SETACTIVEREFENTRY('PowerGeneration')">Power Generation</div>
            <div class='input-description'>This is the thing that will keep the lights and heat on</div>
            <div class='input-generator-wrapper'>
                <select class='input-field-select' v-model="generator.type" v-on:change="setEnergy"> <!-- Uses the retrieved generator value as the value for the field. On change sets the configuration store value -->
                    <option value='none' selected>None</option>
                    <option value='solar_arrays'>Solar PV Array</option>
                </select>
                <input class='input-field-number' v-model="generator.amount" pattern="^\d+$" maxlength=8 placeholder="Quantity" v-on:input="setEnergy">  <!-- Uses the retrieved generator value as the value for the field. On change sets the configuration store value -->
            </div>
        </label>
        <label class='input-wrapper'>
            <div class='input-title'  @click="SETACTIVEREFENTRY('PowerStorage')">Power Storage</div>
            <div class='input-description'>Really big batteries, impossibly good storage</div>
            <input class='input-field-number' v-model="storage.amount" pattern="^\d+$" maxlength=8 placeholder="Quantity" v-on:input="setEnergy">  <!-- Uses the retrieved generator value as the value for the field. On change sets the configuration store value -->
        </label>
    </form>    
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    data(){
        return{
            generator:undefined,
            storage:undefined,
        }
    },
    mounted:function(){
        const {powerGeneration,powerStorage} = this.getConfiguration
        this.generator = powerGeneration
        this.storage = powerStorage
    },
    computed:{
        ...mapGetters('wizard',['getConfiguration']),
        
    },
    methods:{
        ...mapMutations('wizard',['SETENERGY']),
        ...mapMutations('wizard',['SETACTIVEREFENTRY']),

        //This method sets the selected values from above fields to the wizard store - configuration -powerGeneration & powerStorage values.
        //It is called from all fields on change, and updates with all selected values from this form.
        setEnergy:function(){
            const value = {'powerGeneration':this.generator,'powerStorage':this.storage}
            this.SETENERGY(value)
        }
    },
    watch:{
        //If any part of the configuration has changed, update the values this form uses too. This is useful for watching when
        // a preset changes all values within the configuration object within wizard store.
        getConfiguration:{
            handler:function(){
                const {powerGeneration,powerStorage} = this.getConfiguration // get the configuration and extract the approriate values using deconstructing
                this.generator = powerGeneration
                this.storage = powerStorage
            },
            deep:true // Makes sure to watch values within the object too. Not just the root level of the object.
        }
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/components/configuration-input';

    .input-energy-wrapper{
        display:flex;
        justify-content: flex-start;
        align-items:center;
    }

    .input-field-select{
        margin-right:24px;
    }
</style>
