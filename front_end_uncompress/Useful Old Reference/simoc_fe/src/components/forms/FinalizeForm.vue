<template>
    <div class='finalize-wrapper'>
        <InitialForm :handleChange="handleChange" :handleIndex="handleIndex"/>
        <InhabitantsForm :handleChange="handleChange" :handleIndex="handleIndex"/>
        <GreenhouseForm :handleChange="handleChange" :handleIndex="handleIndex"/>
        <PowerForm :handleChange="handleChange" :handleIndex="handleIndex"/>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
import {InitialForm,GreenhouseForm,InhabitantsForm,PowerForm,FinalizeForm} from '../forms'
export default {
    components:{
        "InitialForm":InitialForm,
        "InhabitantsForm":InhabitantsForm,
        "GreenhouseForm":GreenhouseForm,
        "PowerForm":PowerForm,
        "FinalizeForm":FinalizeForm,
    },

    props:{
        //handleEntry:Function,
        //handleChange:Function,
        //handleIndex:Function
    },

    methods:{ 
    
        handleChange: function(event){
            const {name, value, type, checked} = event.target;
            console.log(value);
            type === 'checkbox' ? this.$store.commit(name,checked) : this.$store.commit(name,value);
        },
        handleIndex:function(event){
            const {name, value, type, checked, id} = event.target;
            console.log(value);
            let param = {
                index: id,
                secondary:value
            }
            this.$store.commit(name,param);
        }
    }

}
</script>

<style lang="scss" scoped>
    @import "../../sass/components/configuration-form-internal";
</style>
