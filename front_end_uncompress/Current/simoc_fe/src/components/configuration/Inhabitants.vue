<template>
    <form class='form-wrapper' @submit.prevent="">
        <label class='input-wrapper'>
            <div class='input-title' @click="SETACTIVEREFENTRY('Inhabitants')">Inhabitants</div>  <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>The people that will be living in your community.</div>
            <input class='input-field-number' pattern="^\d+$" maxlength="8" placeholder="Quantity" v-on:input="setInhabitants" v-model="humans.amount">
        </label>
        <label class='input-wrapper'>
            <div class='input-title' @click="SETACTIVEREFENTRY('Food')">Food Supply</div>  <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>People have got to eat something while the plants grow.</div>
            <input class='input-field-number' pattern="^\d+$" maxlength="8" placeholder="Quantity" v-on:input="setInhabitants" v-model="food.amount">
        </label>
        <label class='input-wrapper'>
            <div class='input-title' @click="SETACTIVEREFENTRY('CrewQuarters')">Crew Habitat</div>  <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>Home is where the head rests.</div>
            <select class='input-field-select' v-on:change="setInhabitants" v-model="crewQuarters.type">
                <option value="none" selected>None</option>
                <option value="crew_habitat_small">Small 1000 m³</option>
                <option value="crew_habitat_medium">Medium 2260 m³</option>
                <option value="crew_habitat_large">Large 4020 m³</option>
            </select >
        </label>
        <label class='input-wrapper'>
            <div class='input-title' @click="SETACTIVEREFENTRY('ECLSS')">Environmental Control</div>  <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>Very complicated air conditioning rack, air and water filters too. Better than Brita.</div>
            <input class='input-field-number' pattern="^\d+$" maxlength="8" placeholder="Quantity" v-on:input="setInhabitants" v-model="eclss.amount">
        </label>
    </form>
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {   
    data(){
        return{
            humans:undefined,
            food:undefined,
            crewQuarters:undefined,
            eclss:undefined,
        }
    },
    mounted:function(){
      //Get the values from the configuration that is initially set
        const {humans,food,crewQuarters,eclss} = this.getConfiguration
        this.humans = humans
        this.food = food
        this.crewQuarters = crewQuarters
        this.eclss = eclss
    },
    computed:{
        ...mapGetters('wizard',['getConfiguration']),
    },
    methods:{
        ...mapMutations('wizard',['SETINHABITANTS']),
        ...mapMutations('wizard',['SETACTIVEREFENTRY']),


        //Sets all related values for the inhabitants form into the wizard store. If any of the fields update them all.
        setInhabitants:function(){
            const value = {'humans':this.humans,'food':this.food,'crewQuarters':this.crewQuarters,'eclss':this.eclss}
            this.SETINHABITANTS(value)
        }
    },
    watch:{
        //If any part of the configuration has changed, update the values this form uses too. This is useful for watching when
        // a preset changes all values within the configuration object within wizard store.
        getConfiguration:{
            handler:function(){
                this.crewQuarters.amount = this.crewQuarters.type === "none" ? 0 : 1

                const {humans,food,crewQuarters,eclss} = this.getConfiguration
                this.humans = humans
                this.food = food
                this.crewQuarters = crewQuarters
                this.eclss = eclss
            },
            deep:true //Must be used if the watched value is an object.
        }
    }
    
}
</script>

<style lang="scss" scoped>
    @import '../../sass/components/configuration-input';
</style>
