<template>
    <div class='register-wrapper'>
        <main class='main main--scroll'>
        <p>WELCOME to the SIMOC PRIVATE BETA.</p>        

        <p> Below are a few things to keep in mind while using this product.</p>
        <p> No personal information will be stored or used by SIMOC services. All 
            login information is required simply for the creation of each user 
            session, tracking of user settings, and session data. Server wipes may 
            occur during the course of this private beta, including user login 
            information.
            </p>
        <p> This product remains in development. Not all functionality may be 
            present. If an error or bug occurs, please submit a bug report to bugs@simoc.space, 
            with as complete a description, including what lead to the issue, as is possible.
        </p>
        <p>
            For further details and explanations please visit: SIMOC.space 
        </p>
        </main>
        <footer class='footer'>
            <div class='footer-divider--solid'></div>
            <button class='btn-entry' v-on:click='toLogin'>PROCEED</button>
        </footer>
    </div>
</template>

<script>
export default {
    methods:{
        toLogin:function(){
            this.$router.push({path:'login'});
        }
    }
}
</script>

<style lang="scss" scoped>
    .register-wrapper{
        height:100%;
        width:100%;
        display:flex;
        justify-content: flex-start;
        align-items:center;
        flex-direction:column;
    }

    .footer{
        margin-top:auto;
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

    @import '../../sass/components/register';
</style>