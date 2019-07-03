<template>
    <div class='entry-child-wrapper'>
        <header class='header' v-if='!loading'>   
            <img src='../../assets/simoc-logo-horizontal.svg' class='logo'/>
            <div class='header-message-wrapper'>
                <div class='header-message header-message--normal'>Welcome Back,</div>
                <div class='header-message header-message--italic'>Sign In To Continue</div>
            </div>
        </header>
        <main class='main'>
            <div class='welcome-wrapper'>
                <div class='welcome-paragraph welcome-title'>
                    WELCOME TO THE SIMOC BETA
                </div>  

                <div class='welcome-paragraph'>
                    Below are a few things to keep in mind while using this product.
                </div>
                <div class='welcome-paragraph'> No personal information will be stored or used by SIMOC services. All 
                    login information is required simply for the creation of each user 
                    session, tracking of user settings, and session data. Server wipes may 
                    occur during the course of this private beta, including user login 
                    information.
                </div>
                <div class='welcome-paragraph'> This product remains in development. Not all functionality may be 
                    present. If an error or bug occurs, please submit a bug report to bugs@simoc.space, 
                    with as complete a description, including what lead to the issue, as is possible.
                </div>
                <div class='welcome-paragraph'>
                    For further details and explanations please visit: 
                    <a class='link' href="https://simoc.space/">SIMOC.SPACE</a> 
                </div>

            </div>
            <button class='btn-entry' @click='toEntry'>PROCEED</button>
        </main>
    </div>
</template>

<script>
export default {
    methods:{
        toEntry:function(){
            this.$router.push({path:'entry'});
        }
    }
}
</script>

<style lang="scss" scoped>
    .entry-child-wrapper{
        height:100%;
    }

    .main{
        width:100%;
        height:100%;
        display: flex;
        justify-content: flex-start;
        align-items:center;
        flex-direction:column;
        overflow:hidden;
        font-family:'open sans';
    }

    .welcome-wrapper{
        height:auto;
        max-height:360px;
        overflow-y:auto;
    
    }

    .welcome-paragraph{
        font-size: 14px;
    }

    .welcome-title{
        font-weight: 600;
        font-size: 24px;
        text-decoration: underline;
        text-align:center;
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

    .welcome-paragraph{        
        margin-bottom: 16px;
    }

    .link{
        font-weight: 600;
        &:visited{
            color:lightgreen;
        }
    }
</style>
