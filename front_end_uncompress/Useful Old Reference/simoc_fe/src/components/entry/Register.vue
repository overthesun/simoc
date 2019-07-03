<template>
    <div class='register-wrapper'>
        <header class='header' v-if='!loading'>
            <img src='../../assets/simoc-logo-horizontal.svg' class='logo'/>
            <div class='header-message-wrapper'>
                <div class='header-message header-message--normal'>Sign Up,</div>
                <div class='header-message header-message--italic'>Register Up To Continue</div>
            </div>
        </header>
        <main class='main' v-if='!loading'>
            <div class='input-wrapper'>
                <label class='input-label'>
                    <div class='input-title'>Username</div>
                    <input type='text' class='input-text' v-model="username" @focus="usernameRegex=true; usernameAvailability=true"/>
                    <div class='input-reminder-wrapper'>
                        <span class='input-reminder' :class="{'input-reminder--warning':(!usernameRegex)}" >You can use letters, numbers, underscores &amp periods.</span>
                        <span class='input-reminder input-reminder--warning' :class="{'hidden':usernameAvailability}">Username Already Taken!</span>
                    </div>
                </label>
            </div>
            <div class='input-wrapper'>
                <label class='input-label'>
                    <div class='inputg-title'>Password</div>
                    <input type='password' class='input-text' v-model="password" @focus="passwordRegex=true;"/>
                    <div class='input-reminder-wrapper'>
                        <span class='input-reminder' :class="{'input-reminder--warning':(!passwordRegex)}">Use 8 or more characters with a mix of uppercase and lowercase letters, numbers &amp symbols.</span>
                        <span class='input-reminder input-reminder--warning'></span>
                    </div>
                </label>
            </div>
            <div class='input-wrapper'>
                <label class='input-label'>
                    <div class='input-title'>Confirm</div>
                    <input type='password' class='input-text' v-model="confirm"/>
                    <div class='input-reminder-wrapper'>
                        <span class='input-reminder'></span>
                        <span class='input-reminder input-reminder--warning' :class="{'hidden':passwordMatch}">Passwords Do Not Match!</span>
                    </div>
                </label>
            </div>
        </main>
        <footer class='footer' v-if='!loading'>
            <button class='btn-register' v-on:click="registerUser">CREATE ACCOUNT</button>
            <div class='footer-divider'>OR</div>
            <div class='footer-message-wrapper'>
                Already have an account? 
                <router-link :to="{path:'login'}" class='footer-link'>Login</router-link>
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

    data(){
        return{
            username:"",
            password:"",
            confirm:"",

            usernameAvailability: true,
            usernameRegex:true,
            passwordRegex: true,
            passwordMatch: true,
            loading:false,
        }
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

    watch:{
        password: function(){
            this.verifyPasswordMatch();
        },

        confirm: function(){
            this.verifyPasswordMatch();
        }
    },

    methods:{
        registerUser: async function(){
            this.usernameRegex = await this.verifyUserRegex();
            //this.verifyUserAvailability();
            this.passwordRegex = await this.verifyPasswordRegex();
            this.passwordMatch = await this.verifyPasswordMatch();
        
            if(this.usernameRegex && this.passwordRegex && this.passwordMatch){
                await this.connectionHandler();
            }
        },

        verifyUserRegex:function(){
            if(this.username.length > 0){
                const userRegex = RegExp('^[a-zA-Z0-9](_(?!(\.|_))|\.(?!(_|\.))|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$');
                return userRegex.test(this.username);
            } else{
                return false;
            }
        },

        verifyPasswordRegex:function(){
            const passRegex = RegExp('(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9].*[0-9])(?=.*[^a-zA-Z0-9]).{8,}');
            return passRegex.test(this.password);
        },

        verifyPasswordMatch:function(){
            this.passwordMatch = true;
            
            const password = this.password;
            const confirm = this.confirm;

            if(confirm.length > 0){
                return password === confirm;
            }
        },

        connectionHandler: async function(){
            axios.defaults.withCredentials = true;

            const localHost = 'http://localhost:8000';
            const path = '/register';
            const target = this.useLocalHost ? localHost + path : path;
            
            const params = {'username':this.username,'password':this.password}
        
            this.loading = true;

            axios.post(target,params)
                .then(response =>{
                    console.log(response.status);
                    if(response.status === 200){
                        console.log("register is working");
                        this.$router.push({name:'mainmenu'})
                    }
                }).catch(error=>{
                    const {status} = error.response
                    if(status === 409){ 
                        console.log("Login Error")
                        this.usernameAvailability = false;
                    }
                }).finally(()=>{
                    this.loading = false
                    /*setTimeout(()=>{
                        this.loading = false;
                    },2000)*/
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

