<template>
    <div class='register-wrapper'>     
        <header class='header' v-if='!loading'>   
            <img src='../../assets/simoc-logo-horizontal.svg' class='logo'/>
            <div class='header-message-wrapper'>
                <div class='header-message header-message--normal'>Welcome Back,</div>
                <div class='header-message header-message--italic'>Sign In To Continue</div>
            </div>
        </header>
        <main class='main' v-if='!loading'>   
            <div class='input-wrapper'>
                <label class='input-label'>
                    <div class='input-title' >Username</div>
                    <input type='text' class='input-text' v-model="username"/>
                    <div class='input-reminder-wrapper'>
                        <span class='input-reminder input-reminder--warning' :class="{'hidden':noUsername}">Username is required!</span>
                    </div>
                </label>
            </div>
            <div class='input-wrapper'>
                <label class='input-label'>
                    <div class='input-title'>Password</div>
                    <input type='password' class='input-text' v-model="password"/>
                    <div class='input-reminder-wrapper'>
                        <span class='input-reminder input-reminder--warning' :class="{'hidden':noPassword}">Password is required!</span>
                    </div>
                </label>
            </div>
            <div class='text-wrapper' v-if='!loginCorrect'>
               Username or password are invalid.
            </div>
        </main>
        <footer class='footer' v-if='!loading'>   
            <button class='btn-register' v-on:click='loginUser'>SIGN IN</button>
            <div class='footer-divider'>OR</div>
            <div class='footer-message-wrapper'>
                Don't have an account? 
                <router-link :to="{path:'register'}" class='footer-link'>Sign Up</router-link>
            </div>
        </footer>
        <Spinner v-if='loading' />
    </div>
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters} from 'vuex'
import {Spinner} from '../../components/general'
require('promise.prototype.finally');
export default {
    components:{
        'Spinner':Spinner
    },

    mounted:function(){
        this.$nextTick(()=>{
            window.addEventListener('keyup',event =>{
                if(event.keyCode === 13){
                    this.registerUser();
                }
            })
        })
    },

    data(){
        return{
            username:"",
            password:"",
            noUsername:true,
            noPassword:true,
            loginCorrect: true,
            serverError: false,
            loading: false,
        }
    },

    methods:{
        loginUser:function(){
            this.noUsername = (this.username.length > 0);
            this.noPassword = (this.password.length > 0);

            if(this.noUsername && this.noPassword){
                this.connectionHandler();
            }
        },

        connectionHandler:function(){
            axios.defaults.withCredentials = true;

            const localHost = 'http://localhost:8000';
            const path = '/login';
            
            const target = this.useLocalHost ? localHost + path : path;
            const params = {'username':this.username,'password':this.password}

            this.loading = true;
            
            axios.post(target,params)
                .then(response =>{
                    if(response.status === 200){
                        console.log("login is working");
                        this.$router.push({name:'mainmenu'})
                    }
                }).catch(error=>{
                    const {status} = error.response
                    if(status === 401){ 
                        console.log("Login Error")
                        this.loginCorrect = false;
                    }
                }).finally(()=>{
                    setTimeout(()=>{
                        this.loading = false;
                    },2000)
                })            
        }
    },

    computed:{
        ...mapGetters({
            useLocalHost:'getLocalHost'
        })
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/components/register';
</style>
