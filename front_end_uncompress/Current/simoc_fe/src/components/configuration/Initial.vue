<template>
    <form class='form-wrapper' @submit.prevent="">
        <label class='input-wrapper'>
            <div class='input-title' @click="SETACTIVEREFENTRY('Location')">Location</div> <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>The destination of your off-world "Vaction"</div>
            <select class='input-field-select' v-model="location" v-on:change="setInitial">
                <option value="none" disabled hidden selected>Location</option>
                <option value="mars">Mars</option>
            </select>
        </label>
        <label class='input-wrapper'>
            <div class='input-title' @click="SETACTIVEREFENTRY('Duration')">Mission Duration</div> <!-- On click make the value the active entry on the reference. Set the wiki as active.-->
            <div class='input-description'>How long your stay be with us is.</div>
            <div class='input-duration-wrapper'>
                <input class='input-field-number' v-model="duration.amount" pattern="^\d+$" maxlength=8 placeholder="Length" v-on:change="setInitial">
                <select class='input-field-select' v-model="duration.units" v-on:change="setInitial">
                    <option value="none" hidden disabled selected>Units</option>
                    <option value="hour">Hours</option>
                    <option value="day">Earth Days (24h)</option>
                    <option value="year">Earth Years (8760h)</option>
                </select>
            </div>
        </label>
    </form>    
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    data(){
        return{
            location:undefined,
            duration:undefined,
        }
    },
    mounted:function(){
        //Get the values from the configuration that is initially set
        const {duration,location} = this.getConfiguration
        this.location = location
        this.duration = duration
    },
    computed:{
        ...mapGetters('wizard',['getConfiguration']),
    },
    methods:{
        ...mapMutations('wizard',['SETINITIAL']),
        ...mapMutations('wizard',['SETACTIVEREFENTRY']),
        

        //Called when any of the field's values are changed, or input happens. Updates all related fields to the Initial form within the wizard store.
        setInitial:function(){
            const value = {'location':this.location,'duration':this.duration}
            this.SETINITIAL(value)
        }
    },
    watch:{
        getConfiguration:{
            handler:function(){
                const {location,duration} = this.getConfiguration
                this.location = location
                this.duration = duration
            },
            deep:true //Must be used for watching any object type values.
        }
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/components/configuration-input';

    .input-duration-wrapper{
        display:flex;
        justify-content: flex-start;
        align-items:center;
    }

    .input-field-number{
        margin-right:24px;
    }
</style>
