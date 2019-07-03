<template>
    <div class='base-configuration-wrapper'>
        <router-view>
            <!-- Wizard Jump Options -->
            <template v-slot:navigation-section-select>
                <select class='section-select' v-on:change="setActiveForm"> <!-- Set the activeForm index if the user changes the value to something other than selected -->
                    <option selected disabled>Jump To Section</option>
                    <option value=0 :selected="formIndex === 0">Initial</option>
                    <option value=1 :selected="formIndex === 1">Inhabitants</option>
                    <option value=2 :selected="formIndex === 2">Greenhouse</option>
                    <option value=3 :selected="formIndex === 3">Energy</option>
                    <option value=4 :selected="formIndex === 4">Finalize</option>
                </select>
            </template>
            <template v-slot:main-wizard-input>
                <component :is="activeForm" v-if="activeForm != 'Finalize'"/> <!-- show the activeForm component if it's not the finalize form, uses the name of the component stored within activeForm -->
                <section class='form-wrapper' v-if="activeForm === 'Finalize'"> <!-- show all components below if it's the finalize form section. This prevents having to repeat and create the actual component -->
                    <Presets/>
                    <Initial/>
                    <Inhabitants/>
                    <Greenhouse/>
                    <Energy/>
                </section>
            </template>
            <template v-slot:wizard-configuration-footer>
                <nav class='configuration-button-wrapper'>
                    <!-- These use v-if instead of class binding, since they are simply either displayed or hidden. No animations present to require it. -->
                    <button class='btn-previous' @click='decrementIndex' v-if="!isFirstForm">Previous Section</button>
                    <button class='btn-next' @click="incrementIndex" v-if="!isFinalForm">Next Section</button>
                    <button class='btn-finalize' @click="finalizeConfiguration" v-if="isFinalForm">Finalize Settings</button>
                </nav>
            </template>

            <template v-slot:main-wizard-reference>
                <keep-alive>
                    <component :is="getActiveReference"/> <!-- Display the component with the name stored in the variable-->
                </keep-alive>
                <!--<Reference/>-->
                <!--<GreenhouseDoughnut/>-->
            </template>  
            <template v-slot:footer-wizard-reference>
            </template>         
        </router-view>
    </div>
        
</template>

<script>
import axios from 'axios'
//import form components
import {Inhabitants,Greenhouse,Initial,Energy,Reference,Graphs,Presets} from '../components/configuration'
import {GreenhouseDoughnut} from '../components/graphs'
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    components:{
        'Energy':Energy,
        'Presets':Presets,
        'Inhabitants':Inhabitants,
        'Greenhouse':Greenhouse,
        'Initial':Initial,
        'Reference':Reference,
        'GreenhouseDoughnut':GreenhouseDoughnut,
        'Graphs':Graphs
    },
    data(){
        return{
            formIndex:0, //Current index of the form that should be used from the wizard store
            activeForm:"Initial", //Default starting form
            menuActive:false, //Used with class binding to display the menu.
            stepMax:1, 
            greenhouseSize:{
                'none':0,
                'greenhouse_small':490,
                'greenhouse_medium':2454,
                'greenhouse_large':5610
            },
        }
    },
    mounted:function(){
        this.activeForm = this.getActiveForm(this.formIndex)
    },
    computed:{
        ...mapGetters('wizard',['getConfiguration','getActiveForm','getFormLength','getFormattedConfiguration']),
        ...mapGetters('wizard',['getActiveReference','getActiveRefEntry']),
        ...mapGetters('dashboard',['getStepParams']),
        ...mapGetters(['getUseLocalHost']),

        //Used to hide the normal button and display the active button
        isFinalForm:function() {
            return (this.getFormLength-1) === this.formIndex
        },
        //Hides the prvevious button if the active form is the first one.
        isFirstForm:function() {
            return this.formIndex === 0
        },
    },
    methods:{
        ...mapMutations(['SETGAMEID']),
        

        toggleMenu:function(){
            this.menuActive = !this.menuActive
        },

        //Sets the active form, using the value from the select field
        setActiveForm:function(event){
            let {value:index} = event.target
            this.formIndex = parseInt(index)
            this.activeForm = this.getActiveForm(index)
        },

        decrementIndex:function(){
            let index = Math.max(0,(this.formIndex-1))      
            this.formIndex = index
        },

        incrementIndex:function(){            
            let max = this.getFormLength-1
            this.formIndex = Math.min(max,(this.formIndex+1))       
        },

        finalizeConfiguration:async function(){
            const configParams = {game_config:this.getFormattedConfiguration} //Get the formatted configuration from wizard store
            const localHost = "http://localhost:8000" 
            const path ="/new_game"
            const configurationRoute = this.getUseLocalHost ? localHost + path : path

            try{
                const response = await axios.post(configurationRoute,configParams) //Wait for the new game to be created
                const gameID = response.data //store the game ID from the response
                this.SETGAMEID(gameID)
                this.$router.push('dashboard') //If all is well then move the user to the dashboard screen
            }catch(error){
                console.log(error)
            }
        },
    },
    watch:{
        //If the active form changes update the activeForm variable with the one at the formIndex
        getActiveForm:{
            handler:function(){
                this.activeForm = this.getActiveForm(this.formIndex)
            },
            deep:true
        },
        //If the form index changes update the active form with the one at the formIndex
        //Mostly used for when either the buttons or the select menu or used to navigate
        formIndex:{
            handler:function(){
                this.activeForm = this.getActiveForm(this.formIndex)
            }
        }
    }
}
</script>

<style lang="scss" scoped>
    .base-configuration-wrapper{
        position:relative;
        width: 1024px;
        height: 768px;
        max-height: 768px;
        overflow:hidden;
    }

    .form-wrapper{
        *:not(:last-of-type){
            margin-bottom:24px;
        }
    }

    .configuration-button-wrapper{
        display:flex;
        justify-content:flex-start;
        align-items:center;
    }

    .btn-next{
        width: 196px;
        height: 48px;
        min-height: 48px;
        margin-left: auto;
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

    .btn-previous{
        width: 196px;
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

    .btn-finalize{
        width: 196px;
        height: 48px;
        min-height: 48px;
        margin-left:auto;
        margin-bottom: 24px;
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
    