<template>
    <div class='reference-wrapper'>
        <div class='contents-link' @click="setEntry('contents')" v-show="getCurrentEntry != 'contents' && getCurrentEntry != 'welcome'">Table Of Contents</div>
        <div v-html="getEntry"></div>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex' 
export default {
    mounted(){
        console.log("Mounted")
    },
    activated(){
        console.log("Runs Again")
    },
    computed:{
        ...mapGetters('referenceEntries',['getEntry','getCurrentEntry'])
    },

    methods:{
        ...mapMutations('referenceEntries',['setEntry'])
    }
}
</script>

<style lang="scss" scoped>
    .reference-wrapper{
        width: 100%;
        height: 100%;
    }

    .contents-link{
        font-size: 1.25rem;
        color: lightgreen;
        text-decoration: underline;
    }
</style>
