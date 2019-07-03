<template>
    <div class='entry-wrapper'>
        <!-- This sectoin uses absolute positioning and overflow:hidden on the parent to hide it from the user.
        class binding is used to display / hide the warning.  v-if will simply display it or not, and will not activate the 
        animation for displaying or hiding 
        -->
        <div class='warning-wrapper' :class="{'warning-active': activeWarning}">
            <fa-icon class='fa-icon dismiss-icon' :icon="['fas','times']" @click="dismissWarning"/>
            <div class='warning-item' v-for="(item,index) in activeWarnings" :key="index">
                <fa-icon class='fa-icon warning-icon' :icon="['fal','exclamation-circle']"/>
                {{activeWarnings[index]}}
            </div>     
        </div>
        <!--Uses the BaseEntry component as its and fills in the slots to populate the sections -->
        <BaseEntry>
            <template v-slot:option-items>
                <div class='option-item' :class="{'option-item-active' : 'login'===activeOption}" @click="activateOption('login')"> SIGN IN </div>
                <div class='option-item' :class="{'option-item-active' : 'register'===activeOption}" @click="activateOption('register')"> SIGN UP </div>
            </template>            
            <!-- The forms within use class binding to show / hide depending on which one is active. -->
            <template v-slot:entry-main>
                <form @submit.prevent="loginUser" id='login-form' class='entry-form entry-form-login' :class="{'entry-form-active' : 'login'===activeOption}">
                    <input v-model="user.username" type='text' class='input-field-text ' placeholder="Username"/>
                    <input v-model="user.password" type='password' class='input-field-text' placeholder="Password"/>
                </form>
                <form @submit.prevent="registerUser" id='register-form' class='entry-form entry-form-register' :class="{'entry-form-active' : 'register'===activeOption}">
                    <input v-model="register.username" type='text' class='input-field-text' placeholder="Choose Username"/>
                    <input v-model="register.password" type='password' class='input-field-text' placeholder="Enter Password"/>
                    <input v-model="register.confirmPassword" type='password' class='input-field-text' placeholder="Confirm Password"/>
                </form>
            </template>       
            <!-- Uses class binding to show / hide the approriate section to the user -->
            <template v-slot:entry-button>
                <div class='btn-wrapper btn-wrapper-login' :class="{'btn-wrapper-active' : 'login'===activeOption}">
                    <button form='login-form' class='btn-warning'>SIGN IN</button>
                </div>
                <div class='btn-wrapper btn-wrapper-register' :class="{'btn-wrapper-active' : 'register'===activeOption}">
                    <button form='register-form' class='btn-warning'>SIGN UP</button>
                </div>
            </template>
            <template v-slot:entry-footer>
                <!--<a class='link link-disabled'>Forgot Password?</a>-->
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

    data(){

        //Initialize all the values that will be used for v-model
        return{
            activeWarning:false, // Used to hidden or display the warning panel
            activeOption:'login', //Which 'option' should be active
            activeWarnings: [], //The current active warnings. This should really be a 'set' so that it only contains unique warnings. Currently will display duplicates.

            user:{
                username:"",
                password:"",
            },

            register:{
                username:"",
                password:"",
                confirmPassword:""
            },
        }
    },
    computed:{
        ...mapGetters(['getUseLocalHost']), //Should I be using the local host or relative.

    },
    methods:{

    //On registration make sure the username + password meet the criteria before attempting to register.
    //Warnings cannot be active before attempting login.
    registerUser: async function(){
            this.activeWarning = false;

            const usernameRegex = await this.verifyUsername()
            const passwordRegex = await this.verifyPassword()
            const passwordMatch = await this.verifyPasswordMatch()
            if(!usernameRegex) {this.activeWarnings.push("Username Regex")}
            if(!passwordRegex) {this.activeWarnings.push("Password Regex")}
            if(!passwordMatch) {this.activeWarnings.push("Password Match")}
            if(this.activeWarnings.length > 0) {this.activeWarning = true} //If any warnings were added from the above set the state.

            //If no warning were present pass in the username object to the register route.
            if(!this.activeWarning){
                const {username,password} = this.register
                
                const params = {
                    'username':username,
                    'password':password
                }
                
                await this.entryHandler(params,'/register') //Attempt the route
            }
        },

        //Login the user if the criteria is met.
        loginUser: async function(){
            this.activeWarning = false;
            const loginCorrect = await this.verifyLogin()

            if(!loginCorrect) {this.activeWarnings.push("Login Error")}
            if(this.activeWarnings.length > 0) {this.activeWarning = true}

            if(loginCorrect){
               const params = this.user
               await this.entryHandler(params,'/login') //Atempt the route
            }
        },

        //Connection handler for the login / registeration. Takes in the parameters to be used, and the route to be called.
        //This method should be converted over to the try/catch block as seen elsewhere. Simply to reduce the callback hell.
        //It would also need to be made async in that case.
        entryHandler:function(params,route){
            axios.defaults.withCredentials = true;

            //const target = this.getUseLocalHost ? this.getUseLocalHost + route : route
            const localHost = "http://localhost:8000"
            const target = this.getUseLocalHost ? localHost + route : route
            axios.post(target,params).then(response => {
                const {status} = response
                
                if(status === 200){
                    this.$router.push('menu')
                }
            }).catch(error => {
                const {status} = error.response
                
                if(status === 401){
                    this.activeWarnings.push("Login Error")
                    this.activeWarning = true
                }

                if(status === 409){
                    console.log("Username Unavailable")
                    this.activeWarnings.push("Username Unavailable")
                    this.activeWarning = true
                }
            })
        },

        //Make sure that the password and username are at least not empty before proceeding.
        verifyLogin:function(){
            const {username,password} = this.user

            if(username.length < 0 || password.length < 0){
                return false
            }

            return true
        },
        
        //Disabled due to too heavy of restrictions 
        //SImply returns true if not empty
        verifyUsername:function(){
            const {username} = this.register
            const userRegex = RegExp('^[a-zA-Z0-9](_(?!(\.|_))|\.(?!(_|\.))|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$');
            
            if(username.length <= 0){
                return false
            } 

            return true//userRegex.test(username);            
        },
        //Disabled due to too heavy of restrictions 
        //SImply returns true if not empty
        verifyPassword:function(){
            const {password,confirmPassword} = this.register
            const passRegex = RegExp('(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9].*[0-9])(?=.*[^a-zA-Z0-9]).{8,}');

            if(password.length <= 0 || confirmPassword.length <= 0){
                return false
            }

           
            return true//(passRegex.test(password) && passRegex.test(confirmPassword));
        },

        //Verifies that both the password field and confirm field match and neither is empty
        //Returns the solved boolean value
        verifyPasswordMatch:function(){
            const {password,confirmPassword} = this.register

            if(password.length <= 0 || confirmPassword.length <= 0){
                return false
            }

            return password === confirmPassword
        },

        //Called when the user closes the warning message popup.
        //Clears all warning entries.
        dismissWarning:function(string){
            this.activeWarning = false
            this.activeWarnings = []
        },

        //Used to activate which section the user is under Sign In or Sign Up
        //Called from the above options sections within the HTMl, passes in the 
        //name value of the section that should have the active class.
        activateOption:function(string){
            this.activeOption = string
        },
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

    .entry-form{
        width:100%;
        position:absolute;
        display:flex;
        justify-content: center;
        align-items:center;
        flex-direction:column;
        transition: left .5s ease;

        &-login{
            left:-100%;
        }

        &-register{
            left:100%;
        }

        &-active{
            left:0;
        }
    }

    .btn-wrapper{
        width:100%;
        position:absolute;
        display:flex;
        justify-content:center;
        align-items:center;
        transition: left .5s ease;

        &-login{
            left:-100%;
        }

        &-register{
            left:100%;
        }

        &-active{
            left:0;
        }
    }

    .warning-wrapper{
        position:absolute;
        left:0;
        top:-256px;
        z-index:99;
        height: auto;
        min-height:96px;
        max-height:256px;
        width:100%;
        background-color:#ff3100;
        transition: top .3s ease;
        padding:16px;
        box-sizing:border-box;
        border-bottom: 1px solid #eee;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
        color:white;

        .warning-item{
            width:100%;
            margin: 4px 0px;
        }

       .warning-icon{
            font-size: 16px;
            //vertical-align: middle;
            margin-right:6px;
        }

        .dismiss-icon{
            position:absolute;
            top:0;
            right:0;
            margin:4px 8px;
            padding:4px;

            &:hover{
                cursor: pointer;
            }
        }
    }

    .warning-active{
        top:0px;
    }
</style>
