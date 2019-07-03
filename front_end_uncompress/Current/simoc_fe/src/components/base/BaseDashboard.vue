<!-- This component is incomplete, as such there are no slots added currently for the addition of 
future dashboard views
-->

<template>
    <div class='dashboard-wrapper'>
        <MainMenu v-if="getMenuActive" /> <!-- Menu component for the dashboard. Uses a simple v-if statement to show the menu active or hidden. 
        <!--<section class='toolbar-wrapper'></section>-->
        <section class='main-wrapper'>
            <Main/>
        </section>
        <section class='footer-wrapper'>
            <div class='menu-icon'>
                <fa-icon class='fa-icon menu-icon' :icon="['fas','bars']" @click='SETMENUACTIVE(true)'/> <!-- Menu button on the tool bar. On click call the mutation method within the dashboard store -->
            </div>
            <Controls/> <!-- Speed controls component -->
            <Timeline/> <!-- Timeline bar component -->
        </section>
    </div>
</template>

<script>
import {Timeline,Controls,Main,MainMenu} from '../../components/dashboard'
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {
    components:{
        "Timeline":Timeline,
        "Controls":Controls, 
        "Main":Main,
        "MainMenu":MainMenu
    },
    computed:{
        ...mapGetters('dashboard',['getMenuActive']) 
    },
    methods:{

        ...mapMutations('dashboard',['SETMENUACTIVE','SETTERMINATED','SETISTIMERRUNNING','SETTIMERID'])
    }
    
}
</script>

<style lang="scss" scoped>
    .fa-icon{
        font-size:44px;
    }

    .dashboard-wrapper{
        position:relative;
        width:100vw;
        height:100vh;
        min-width:100vw;
        min-height:100vh;

        display:grid;
        grid-template-rows: minmax(0px,1fr) 128px;
        grid-template-columns: 196px minmax(0px,1fr);
    }

    .menu-icon{
        position: absolute;
        width:48px;
        height:48px;
        top:50%;
        transform:translateY(-50%);
        left:16px;
    }

    .toolbar-wrapper{
        background-color: #252525;
    }
    .main-wrapper{
        grid-column: span 2;
    }

    .footer-wrapper{
        position: relative;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction: column;
        grid-column: span 2;
        background-color: #1e1e1e;
        box-sizing:border-box;
    }

</style>