<template>
    <div class='register-wrapper'>
        <header class='top'>
            <img src='../../assets/simoc-logo-horizontal.svg' class='logo'/>
            <div class='welcome-wrapper'>
                <div class='welcome-message'>Registration</div>
                <div class='welcome-instruction'>Sign Up To Continue</div>
            </div>
        </header>
        <main class='main'>
            <div class='input-wrapper'>
                <label class='input-label'>
                    <span class='input-warning' :class="{'input-danger':userError}">You can use letters, numbers, underscores &amp periods.</span>
                    <span class='input-title'>Username</span>      
                    <span class='input-title--warning title-danger' :class="{'hidden':userAvailable}">(Username already exists)</span>              
                    <input type='text' class='input-text' :class="{'input-danger':userError}" v-model="username"/>
                </label>
            </div>
            <div class='input-wrapper'>
                <label class='input-label'>
                    <span class='input-warning' :class="{'input-danger':passError}">Use 8 or more characters with a mix of uppercase and lowercase letters, numbers &amp symbols.</span>
                    <span class='input-title'>Password</span>
                    <input type='password' class='input-text' @focus="passError = false;" v-model="pass"/>
                </label>
            </div>
            <div class='input-wrapper'>
                <label class='input-label'>
                    <span class='input-warning input-danger' :class="{'hidden':passMatch}">Passwords must match</span>
                    <span class='input-warning' ></span>
                    <span class='input-title' >Confirm</span>
                    <input type='password' class='input-text' @focus="passMatch = true;" v-model='confirm'/>
                </label>
            </div>
        </main>
        <footer class='bottom'>
            <button class='btn-register' @click="registerUser">CREATE ACCOUNT</button>
            <div class='footer-divider'>OR</div>
            <div class='login-wrapper'>
                Already have an account?
                <span class='login-link'>Login</span>
            </div>
        </footer>
    </div>

</template>

<script>
export default {
    data(){
        return{
            username:"",
            pass:"",
            confirm:"",
            userError:false,
            userAvailable:true, 
            passError:false, 
            passMatch:true, 
        }
    },

    methods:{
        registerUser:function(){
            this.verifyUserFormat();
            this.verifyPassFormat();
            this.verifyPassMatch();
        },

        verifyUserFormat:function(){
            const userRegex = RegExp('^[a-zA-Z0-9](_(?!(\.|_))|\.(?!(_|\.))|[a-zA-Z0-9]){4,18}[a-zA-Z0-9]$');
            this.userError = !userRegex.test(this.username);
            console.log(!userRegex.test(this.username));
        },

        verifyPassFormat:function(){
            const passRegex = RegExp('(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9].*[0-9])(?=.*[^a-zA-Z0-9]).{8,}');
            this.passError = !passRegex.test(this.pass);
        },

        verifyPassMatch:function(){
            let password = this.pass;
            let confirmation = this.confirm;
            this.passMatch = (password === confirmation);            

            if(!this.passMatch){
                this.pass="";
                this.confirm="";
            }
        }
    }



}
</script>

<style lang="scss" scoped>

    @import '../../sassmediaqueries';
    @import "../../sassdivider";
    @import "../../sass/components/register";
    
</style>
