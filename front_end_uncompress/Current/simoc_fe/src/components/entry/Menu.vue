
<!-- Menu screen presented to the user on successful login. -->

<template>
    <div class='entry-wrapper'>
        <BaseEntry>
            <template v-slot:option-items>
                <div class='option-item option-item-active'> MAIN MENU </div>
            </template>            
            <template v-slot:entry-main>
                <button form='login-form' class='btn-normal' @click="toConfiguration">NEW CONFIGURATION</button>
                <button form='login-form' class='btn-normal btn-disabled'>LOAD SESSION</button>               
            </template>       
            <template v-slot:entry-button>
                <div class='btn-wrapper'>
                    <button form='login-form' class='btn-warning'>LOG OUT</button>
                </div>
            </template>
            <template v-slot:entry-footer>
                <a class='link link-disabled'>View Account</a>
                <a class='link link-disabled'>Privacy Policy</a>
                <a class='link link-disabled'>Report Bug</a>
            </template>
        </BaseEntry>

    </div>
</template>

<script>
import axios from 'axios'
import {BaseEntry} from '../../components/base'
import {mapState,mapGetters,mapMutations,mapActions} from 'vuex'
export default {  
    components:{
        'BaseEntry':BaseEntry,
    },
    computed:{
        ...mapGetters(['getUseLocalHost']),

    },
    methods:{
        //Sends the user to the configuration menu screen. See router.js
        toConfiguration:function(){
            this.$router.push('menuconfig')
        },
        //Logout method called when the user hits the logout button
        //Sends the user back to the entry screen regardless if the server has successfully logged them out
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
        }
    }
}
</script>

<style lang="scss" scoped>
    .entry-wrapper{
        height:100%;
        width:100%;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
        box-sizing:border-box;
        position:relative;
    }

    .btn-warning{
        background-color: #ff3100;
    }
</style>
