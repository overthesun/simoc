<template>
    <div class='entry-child-wrapper'>
        <div class='warning-wrapper' :class="{'warning-active': isWarning}">
            <fa-icon class='fa-icon dismiss-icon' :icon="['fas','times']" @click="dismissWarning"/>
            <!--<fa-icon class='fa-icon warning-icon' :icon="['fal','exclamation-circle']" /> -->
            <div class='warning-item' v-for="(item,index) in activeWarnings" :key="index">
                <fa-icon class='fa-icon warning-icon' :icon="['fal','exclamation-circle']"/>
                {{activeWarnings[index]}}
            </div>
            
        </div>

        <main class='main'>
            <div class='options-wrapper'>
                <div class='options-item options-item-login' :class="{'active ': 'login' === isActive}" @click="activate('login')">SIGN IN</div>
                <div class='options-item options-item-register' :class="{'active' : 'register' === isActive}" @click="activate('register')">SIGN UP</div>
            </div>
            <div class='form-wrapper'>
                <form  @submit.prevent="loginUser" class='entry-form entry-form-login' id='login-form' :class="{'entry-form-active' : 'login' === isActive}">

                    <label>
                        <input v-model="user.username" type='text' class='input-field-text' placeholder="Username"/>
                    </label>
                    <label>
                        <input v-model="user.password" type='password' class='input-field-text' placeholder="Password"/>
                    </label>
                    <label class='label-checkbox disabled'>
                        <input  disabled type='checkbox' class='input-field-checkbox' name='saveLogin' value='saveLogin'/>
                        <span class='checkbox-text'>Stay Logged In</span>
                    </label>
                    <button class='btn-entry'>SIGN IN</button>
                </form>
                <form @submit.prevent="registerUser" class='entry-form entry-form-register' id='register-form' :class="{'entry-form-active' : 'register' === isActive}">
                    <label>
                        <input disabled  type='text' class='input-field-text' placeholder="Email Address"/>
                    </label>
                    <label>
                        <input v-model="register.username" type='text' class='input-field-text' placeholder="Choose Username"/>
                    </label>
                    <label>
                        <input v-model="register.password" type='password' class='input-field-text' placeholder="Create Password"/>
                    </label>
                    <label>
                        <input v-model="register.confirmPassword" type='password' class='input-field-text' placeholder="Confirm Password"/>
                    </label>
                    <button class='btn-entry' >SIGN UP</button>
                </form>
            </div>
        </main>
        
    </div>
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters} from 'vuex'
export default {
    computed:{
        ...mapGetters(['getUseLocalHost','getLocalHost'])
    },

    data(){
        return{
            user:{
                username:"",
                password:"",
            },

            register:{
                username:"",
                password:"",
                confirmPassword:""
            },

            isActive:'login',
            
            isWarning:false,            
            activeWarnings: [],
        }
    },

    methods:{
        registerUser: async function(){
            this.isWarning = false;

            const usernameRegex = await this.verifyUsername()
            const passwordRegex = await this.verifyPassword()
            const passwordMatch = await this.verifyPasswordMatch()
            if(!usernameRegex) {this.activeWarnings.push("Username Regex")}
            if(!passwordRegex) {this.activeWarnings.push("Password Regex")}
            if(!passwordMatch) {this.activeWarnings.push("Password Match")}
            if(this.activeWarnings.length > 0) {this.isWarning = true}

            if(!this.isWarning){
                const {username,password} = this.register
                
                const params = {
                    'username':username,
                    'password':password
                }
                
                await this.entryHandler(params,'/register')
            }
        },

        loginUser: async function(){
            this.isWarning = false;
            const loginCorrect = await this.verifyLogin()

            if(!loginCorrect) {this.activeWarnings.push("Login Error")}
            if(this.activeWarnings.length > 0) {this.isWarning = true}

            if(loginCorrect){
               const params = this.user
               await this.entryHandler(params,'/login')
            }
        },

        entryHandler:function(params,route){
            axios.defaults.withCredentials = true;

            const target = this.getUseLocalHost ? this.getLocalHost + route : route

            axios.post(target,params).then(response => {
                const {status} = response
                
                if(status === 200){
                    console.log("This is working")
                    this.$router.push('menu')
                }
            }).catch(error => {
                const {status} = error.response
                
                if(status === 401){
                    this.activeWarnings.push("Login Error")
                    this.isWarning = true
                }

                if(status === 409){
                    console.log("Username Unavailable")
                    this.activeWarnings.push("Username Unavailable")
                    this.isWarning = true
                }
            })
        },

        verifyLogin:function(){
            const {username,password} = this.user

            if(username.length < 0 || password.length < 0){
                return false
            }

            return true
        },

        verifyUsername:function(){
            const {username} = this.register
            const userRegex = RegExp('^[a-zA-Z0-9](_(?!(\.|_))|\.(?!(_|\.))|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$');
            
            if(username.length <= 0){
                return false
            } 

            return userRegex.test(username);            
        },

        verifyPassword:function(){
            const {password,confirmPassword} = this.register
            const passRegex = RegExp('(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9].*[0-9])(?=.*[^a-zA-Z0-9]).{8,}');

            if(password.length <= 0 || confirmPassword.length <= 0){
                return false
            }

           
            return (passRegex.test(password) && passRegex.test(confirmPassword));
        },

        verifyPasswordMatch:function(){
            const {password,confirmPassword} = this.register

            if(password.length <= 0 || confirmPassword.length <= 0){
                return false
            }

            return password === confirmPassword
        },

        activate:function(string){
            this.isActive = string
            this.isWarning = false
            this.activeWarnings = []
        },

        dismissWarning:function(string){
            this.isWarning = false
            this.activeWarnings = []
        }
    }
}
</script>

<style lang="scss" scoped>
    .entry-child-wrapper{
        height:100%;
        width: 100%;
        margin: auto auto;
        /*display:grid;
        grid-template-rows: auto 1fr;
        grid-row-gap: 36px;*/
    }

    .warning-wrapper{
        z-index: 99;
        top: -256px;
        left:0;
        position:absolute;
        height: auto;
        min-height: auto;
        width: 100%;
        background-color: #ff3100;
        border-bottom: 1px solid #eee;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
        color:white;
        font-family:'open sans';
        padding:16px;
        box-sizing:border-box;
        transition: top .5s ease;

        .warning-item{
            width:100%;
            margin: 4px 0px;
        }

        .dismiss-icon{
            position:absolute;
            top:0;
            right:0;
            margin: 4px;
            padding:4px;

            &:hover{
                cursor: pointer;
            }
        }

        .warning-icon{
            font-size: 16px;
            //vertical-align: middle;
            margin-right:6px;
        }
    }

    .warning-active{
        top:0px;
    }

    .header{
        display: flex;
        justify-content: center;
        align-items:center;
    }

    .logo{
        width: 48px;
        height: auto;
        margin: 0px 4px;
    }

    .header-title{
        font-weight: 400;
        font-size: 22px;        
        margin: 0px 4px;
        font-family: 'open sans';
    }

    .main{
        height: 100%;
        display:grid;
        grid-template-rows:auto 1fr;
        grid-row-gap: 42px;
        box-sizing:border-box;
    }

    .options-wrapper{
        display:flex;
        justify-content: center;
        align-items:center;
    }

    .options-item{
        margin: 0px 16px;
        font-family:'open sans';
        font-weight: 600;
        font-size: 24px;
        position:relative;
    
        &:hover{
            cursor: pointer;
        }

        &:after{
            position: absolute;
            right: 0;
            top: 100%;
            content:"";
            width: 0;
            border-bottom: 3px solid lightgreen;
            transition: width .2s ease;
        }
    }

    .form-wrapper{
        overflow:hidden;
        position:relative;
    }

    .active{
        &:after{
            width: 100%;
            left: 0;        
        }
    }

    .entry-form{
        position: absolute;
        top: 0;

        &-register{
            left: 150%;
        }

        &-login{
            left:-50%;
        }

        &-active{
            left: 50%;
        }
        transform:translateX(-50%);
        height: 100%;
        display:flex;
        justify-content:flex-start;
        align-items:center;
        flex-direction:column;
        transition: left .5s ease;
    }

    .input-field-text{
        height: 36px;
        margin-bottom: 24px;
        outline:none;
        padding: 8px 8px;
        width: 256px;
        border-radius: 8px;
        border:none;
        box-sizing: border-box;
        font-weight: 600;
    }

    .label-checkbox{
        display:inline-block;
        //padding-right: 10px;
        white-space:nowrap;
    }

    .input-field-checkbox,.checkbox-text{
        font-family:'open sans';
        font-weight: 200;
        font-size: 14px;
        color: #999;
        vertical-align:bottom;
    }

    .footer{
        display:flex;
        justify-content:center;
        align-items:center;
    }

    .btn-entry{        
        width: 256px;
        height: 48px;
        margin-top: auto;
        border-radius: 24px; 
        padding: 12px 16px;
        font-size: 18px;
        font-weight: 600;
        background-color: #0099ee;
        border:none;
        //border: 2px solid #eee;
        color: #eee;

        &:hover{
            color: #eee;
            cursor: pointer;
        }

        &:focus{
            outline:none;
        }
    }

    *:disabled{
        background-color: #999;
    }

</style>
