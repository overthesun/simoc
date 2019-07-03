<!--
This component is the base component for creating the configuration wizard view. The slots within are 
used to populate the various sections with the approriate component passed in via the 'ConfigurationView' component.<template>
The plan was that by configuring the base component in this way that the layout could be used for future features such as 
payload creator, greenhouse editor, etc for within the dashboard. With a fimiliar layout, and only the need to populate the slots with the 
approriate filler. A number of modifications would be needed to modify things like the title, and the configuration 
menu button being present on other unrelated configurations.
 -->

<template>
    <div class='configuration-wrapper' >
        <!-- 
            Uses absolute positioning and overflow-hidden to remain off screen when not active 
            Uses class-binding to the menuActive variable to toggle displaying the menu.
        -->
        <section class='menu-wrapper ' :class="{'menu-wrapper-active': menuActive}">
            <header class='header'>
                <div class='simoc-logo-title'>
                    <div class='logo-title'>SIMOC</div>
                    <div class='logo-title-italic logo-title-menu'>CONFIGURATION MENU</div>
                </div>
                <fa-icon class='fa-icon menu-icon' :icon="['fas','times']" @click='toggleMenu'/>
            </header>
            <main class='menu-main'>
                <button class='btn-normal btn-disabled'>Download Configuration</button>
                <button class='btn-normal btn-disabled'>Save Configuration</button>
                <button class='btn-normal btn-disabled'>Load Configuration</button>
                <button class='btn-outline-warning btn-disabled'>Reset To Default</button>
                <button class='btn-warning' @click="logout">Log Out</button>
            </main>
        </section>
        <!-- The form side of the wizard screen -->
        <section class='wizard-wrapper'>
            <header class='header'>
                <!--<img src='../../assets/simoc-logo.svg' class='simoc-logo'/>-->
                <div class='simoc-logo-title'>
                    <div class='logo-title'>SIMOC</div>
                    <div class='logo-title-italic'>CONFIGURATION WIZARD</div>
                </div>
            </header>
            <nav class='navigation-wrapper'>
                <slot name='navigation-section-select'></slot>                
            </nav>
            <main class='main main-wizard'>
                <slot name='main-wizard-input'></slot>           
            </main>
            <footer class='footer'>
                <slot name='wizard-configuration-footer'></slot>
            </footer>
        </section>
        <!-- The reference side of the wizard screen -->
        <section class='reference-wrapper'>
            <header class='header'>
                <div class='simoc-logo-title'>
                    <div class='logo-title'>SIMOC</div>
                    <div class='logo-title-italic'>ENCYCLOPEDIA</div>
                </div>
                <fa-icon class='fa-icon menu-icon' :icon="['fas','bars']" @click='toggleMenu'/>
            </header>
            <!-- This is the navigation section at the top of the wizard reference. class-binding to a universal variable is used to dictate which one is set to active.
                The universal variable is used so that things like the wizard form headers can be used to set what the active section is. Such as clicking a title and
                the approriate reference entry appearing on the right side.
            -->
            <nav class='configuration-options reference-options'>
                <div class='option-item' @click="SETACTIVEREFERENCE('Reference')" :class="{'option-item-active' : 'Reference'===activeOption}">REFERENCE</div>
                <!--<div class='option-item' @click="SETACTIVEREFERENCE('Recommended')" :class="{'option-item-active' : 'Recommended'===activeOption}">RECOMMENDED</div> Enabled Once Recommended Is Completed-->
                <div class='option-item option-item-disabled'>RECOMMENDED</div>
                <div class='option-item' @click="SETACTIVEREFERENCE('Graphs')" :class="{'option-item-active' : 'Graphs'===activeOption}">GRAPHS</div>
            </nav>
            <main class='main main-reference'>
                <slot name='main-wizard-reference'></slot>
            </main>
            <footer class='footer'>
                <slot name='footer-wizard-reference'></slot>
            </footer>
        </section>
    </div>    
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    data(){
        return{
            menuActive:false
        }
    },

    computed:{
        ...mapGetters('wizard',['getActiveReference']), // Used to dictate which navigation title is underlined.
        ...mapGetters(['getUseLocalHost']), //Flag for using localhost within route calls

        //Used to flag which section link is active within the reference navigation. Uses class-binding to activate the class. See wizard store for more details
        activeOption:function(){
            return this.getActiveReference
        }
    },
    methods:{
        ...mapMutations('wizard',['SETACTIVEREFERENCE']),

        //Simple toggle function for showing the menu. Used with class-binding to activate the class to show / hide the menu
        toggleMenu:function(){
            this.menuActive = !this.menuActive
        },
        //Route function for logging the user out. Called from within the wizard menu
        logout: async function(){
            const localHost = "http://localhost:8000"
            const path = "/logout"            
            const logoutRoute = this.getUseLocalHost ? localHost + path : path

            try{
                axios.post(logoutRoute)
                this.$router.push("entry")
            }catch(error){
                console.log(error)
            }
            this.$router.push("entry") // Take the user back to the login screen even if the operation fails.
        }
    }
}
</script>

<style lang="scss" scoped>
    .configuration-wrapper{
        position:relative;
        overflow:hidden;
        height:100%;
        width:100%;
        display:grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: minmax(0,1fr);
        box-sizing: border-box;
    }

    .menu-wrapper{
        position: absolute;
        background-color: #252525;
        width: 50%;
        height: 100%;
        top: 0;
        left:100%;
        z-index:10;
        transition: left .3s ease; 
        display:grid;
        grid-template-rows: 32px 1fr;        
        grid-row-gap: 88px;
        padding:16px;
        box-sizing:border-box;
    
        &-active{
            left:50%
        }
    }

    .menu-main{
        display:flex;
        justify-content:flex-start;;
        align-items:center;
        flex-direction: column;
    }

    .wizard-wrapper{
        height:100%;
        width:100%;
        padding:16px;
        background-color:#1e1e1e;
        box-sizing:border-box;
    

    }

    .wizard-wrapper,.reference-wrapper{
        display:grid;
        grid-template-rows: 32px 32px minmax(0,1fr) 48px;        
        grid-row-gap: 32px;
    }


    .reference-wrapper{
        height:100%;
        padding:16px;
        background-color:#252525;
        box-sizing:border-box;
    }

    .header{
        display:flex;
        justify-content:flex-start;
        align-items:center;
        position:relative;

       &:after{
            position:absolute;
            content:"";
            display:block;
            width:100%;
            border-bottom:2px solid #999;
            left:0;
            top:100%;
            margin-top:16px;
        }
    }

    .simoc-logo{
        width: auto;
        height: 32px;
        margin-right:8px;
    }

    .simoc-logo-title{
        font-weight: 600;
        font-size: 12px;
    }

    .logo-title-italic{
        font-weight: 200;
        font-size:16px;
    }

    .logo-title-main{
        margin-top:auto;
    }
    .section-select{
        border:none;
        background:transparent;
        color: #eee;
        width:auto;
        height:100%;
        //padding:2px 4px;
        font-size:24px;
        font-weight:600;
        position:relative;
        //text-decoration: underline;
        //text-decoration-color: lightgreen;

        &:hover{
            cursor:pointer;
        }

        &:focus{
            outline:none;
        }
    
        option{
            font-size: 16px;
            color:#1e1e1e;
        }
    }

    .menu-icon{
        font-size:32px;
        margin-left:auto;
    }

    .configuration-options{
        width:100%;
        display:flex;
        justify-content:space-between;
        align-items:center;
        font-size:24px;
        font-weight:600;
    }    

    .main-wizard{
        min-height:0;
        height:100%;
        overflow:hidden;
        overflow-y:auto;
        position:relative;
    }

    .option-item{
        position:relative;

        &:hover{
            cursor:pointer;
        }

        &:after{
            box-sizing:border-box;
            position:absolute;
            right:0;
            top:100%;
            content:"";
            width:0;
            border-bottom: 2px solid lightgreen;
            transition: width .2s ease;
        }

        &-active:after{
            width:100%;
            left:0;
        }

        &-disabled{
            color:#999;
        }
    }

    .btn-normal{
        width: 256px;
        height: 48px;
        min-height: 48px;

        margin-bottom: 24px;
        border-radius: 24px;
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 600;
        background-color: #0099ee;
        border:none;
        color: #eee;

        &:hover{
            cursor: pointer;
        }

        &:focus{
            outline:none;
        }
    }

    .btn-disabled{
        background-color: transparent !important;
        border: 1px solid #999 !important;
        color: #999 !important;

        &:hover{
            cursor:not-allowed !important;
        }

        &:focus{
            outline:none !important;
        }
    }

    .btn-logout{
        margin-top: auto;
    }

    .btn-outline-warning{
        width: 256px;
        height: 48px;
        min-height: 48px;
        margin-bottom: 24px;
        border-radius: 24px;
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 600;
        background-color: transparent;
        border:2px solid #ff3100;
        color: #eee;

        &:hover{
            cursor: pointer;
        }

        &:focus{
            outline:none;
        }
    }

    .btn-warning{
        width: 256px;
        height: 48px;
        min-height: 48px;
        border-radius: 24px;
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 600;
        background-color: #ff3100;
        border:none;
        color: #eee;

        &:hover{
            cursor: pointer;
        }

        &:focus{
            outline:none;
        }
    }
   
</style>
