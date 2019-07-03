<template>
    <div class='configuration-wrapper'>
        <div class='interior-wrapper' v-if='!loading'>
            <header class='header'>
                <img src='../../assets/simoc-logo.svg' class='logo'/>
                <div class='header-message-wrapper'>
                    <div class='header-title'>
                        Session Configuration
                    </div>
                    <div class='header-title header-title--italic'>
                        {{section[index].sectionName}}
                    </div>
                </div>
                <fa-icon class='fa-icon menu--icon' :icon="['fal','bars']"/>
            </header>
            <main class='main'>
                <div class='main-section-wrapper form-wrapper'>
                    <div class='main-header main-header--form'></div>
                    <div class='main-content'>
                        <component :is="section[index].componentName" :handleChange="handleChange"/>
                    </div>
                    <div class='main-footer main-footer--form'>
                        <div class='footer-nav-wrapper footer-nav-wrapper--left' v-if="lowerBound" v-on:click="decrementIndex">
                            <fa-icon class='fa-icon menu--icon' :icon="['fal','arrow-left']"/>
                            <div class='footer-title'>{{section[lowerLimit].buttonName}}</div>
                        </div>
                        <div class='footer-nav-wrapper footer-nav-wrapper--right' v-on:click="incrementIndex">
                            <div class='footer-title' v-if="!upperBound">{{section[upperLimit].buttonName}}</div>
                            <div class='footer-title' v-if="upperBound">Finalize</div>
                            <fa-icon class='fa-icon menu--icon' :icon="['fal','arrow-right']"/>
                        </div>
                    </div>
                </div>
                <div class='main-section-wrapper wiki-wrapper'>
                    <div class='main-header main-header--wiki'>
                        <div class='main-header-link'>Encyclopedia</div>
                        <div class='main-header-link'>Graphs</div>
                        <div class='main-header-link'>Recommended</div>
                    </div>
                    <div class='main-content'>
                        Lorem ipsum dolor sit amet, cum movet laudem omittantur ad, cu legere incorrupte mel, eum pericula referrentur eu. Ex cibo omnis mei. Te congue repudiare usu, et platonem euripidis nec, vix no odio tale. Nec iudico cetero civibus ad. Alii putant instructior pro ad, nam ferri saepe qualisque id. Vel fugit primis mandamus id. Pro facilis appellantur efficiantur ei. Mei alterum denique antiopam cu, sea vocent ceteros cu. Ut deserunt argumentum mel, nihil dicant ne sed. Odio munere veritus in mei, in ipsum saepe principes mei, quod graece dignissim cum id. Lorem ipsum dolor sit amet, cum movet laudem omittantur ad, cu legere incorrupte mel, eum pericula referrentur eu. Ex cibo omnis mei. Te congue repudiare usu, et platonem euripidis nec, vix no odio tale. Nec iudico cetero civibus ad. Alii putant instructior pro ad, nam ferri saepe qualisque id. Vel fugit primis mandamus id. Pro facilis appellantur efficiantur ei. Mei alterum denique antiopam cu, sea vocent ceteros cu. Ut deserunt argumentum mel, nihil dicant ne sed. Odio munere veritus in mei, in ipsum saepe principes mei, quod graece dignissim cum id.
                    </div>
                </div>                
            </main>
        </div>
    </div>
</template>

<script>
import Inhabitants from "../components/ConfigurationHumans"
import ConfigurationTest from "../components/ConfigurationTest"

import {mapState,mapGetters} from 'vuex'
export default {
    components:{
        "Inhabitants":Inhabitants,
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
