<template>
    <div class='content-wrapper'>
        <header class='header'>
            <div class='header-message'>Configuration Options</div>
        </header>
        <main class='main'>
            <button class='menu-btn menu-btn--main' v-on:click="configurationHandler">Configuration</button>
            <button class='menu-btn menu-btn--main' v-on:click="advancedHandler">Expert Configuration</button>
        </main>
        <footer class='footer'>
            <button class='menu-btn menu-btn--logout' v-on:click="cancelHandler">Cancel</button>
            <div class='footer-divider--solid'></div>
            <div class='footer-links-wrapper'>
                <div class='footer-link'>View Account</div>
                <div class='footer-link'>Privacy Policy</div>
                <div class='footer-link'>Report Bug</div>
            </div>
        </footer>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    computed:{
        
    },

    methods:{
        ...mapMutations('guideOrder',['skipConfiguration']),

        cancelHandler:function(){
            this.$router.push({name:'menumain'})
        },

        configurationHandler:function(){
            this.skipConfiguration(false)
            this.$router.push({name:'configurationsession'})
        },
        advancedHandler:function(){
            this.skipConfiguration(true)
            this.$router.push({name:'configurationsession'})
        }
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/components/menu';
</style>
