<template>
    <div class='configuration-wrapper'>
        <div class='interior-wrapper' v-if="!loading">
            <header class='header'>
                <img src='../../assets/simoc-logo-horizontal.svg' class='logo'/>
                <div class='header-message-wrapper'>
                    <div class='header-message header-message--normal'>Session Configuration</div>
                    <div class='header-message header-message--italic'>{{section[index].sectionName}}</div>
                </div>
            </header>
            <main class='main'>
                <div class='main-section-wrapper form-wrapper'>
                    <FormTest :handleChange="handleChange"/>
                    <!--<component :is="section[index].componentName"/>-->
                </div>
                <div class='main-section-wrapper wiki-wrapper'>
                    Wiki
                <!--<component :is="ConfigurationWiki" :entry="section[index].entryName" v-if="beginner"/>-->
                </div>
            </main>
            <footer class='footer'>
                <div class='footer-wrapper'>
                    <div class='button-title button-title--previous' v-if="lowerBound">Previous Section</div>
                    <div class='button-title button-title--next' >Next Section</div>
                    <button class='btn-navigation btn-navigation--previous' @click="decrementIndex" v-if="lowerBound > 0">{{section[lowerLimit].buttonName}}</button>
                    <button class='btn-navigation btn-navigation--next' @click="incrementIndex" v-if="!upperBound">{{section[upperLimit].buttonName}}</button>
                    <button class='btn-navigation btn-navigation--next' v-if="upperBound">Finalize Configuration</button>
                </div>
            </footer>
        </div>     
    </div>
</template>

<script>
import ConfigurationHumans from "../components/ConfigurationHumans"
import ConfigurationTest from "../components/ConfigurationTest"
import FormTest from "../components/ConfigurationHumans"

import {mapState,mapGetters} from 'vuex'
export default {
    components:{
        "FormTest":FormTest,
    },
    computed:{
        lowerBound:function(){
            return (this.index-1) >= 0;
        },

        upperBound:function(){
            let maxIndex = this.section.length;
            console.log(maxIndex);
            return this.index+1 === maxIndex;
        },

        lowerLimit:function(){
            let minIndex = 0;
            return Math.max(this.index-1,minIndex);
        },

        upperLimit:function(){
            let maxIndex = this.section.length - 1;
            return Math.min(this.index+1,maxIndex);
        },

        ...mapGetters({
            sectionOrder:'getSectionOrder',
        }),
    },

    methods:{
        incrementIndex: function(){
            let maxIndex = this.section.length;
            this.index = Math.min(this.index+1,maxIndex);
        },

        decrementIndex: function(){
            let minIndex = 0;
            this.index = Math.max(this.index-1,minIndex);
        },

        handleChange: function(event){
            const {name,value,type,checked} = event.target;
            type === "checkbox" ? this.$store.commit(name,checked):
                this.$store.commit(name,value);
        }
    },

    data(){
        return{
            loading: true,
            index:0,
            section:[]
        }
    },

    mounted(){
        this.section = [...this.sectionOrder];
        this.loading = false;
    }
}
</script>

<style lang="scss" scoped>
    @import "../sass/views/configuration";
    @import "../sass/components/configuration-interior";
    @import "../sass/components/configuration-main";

</style>
