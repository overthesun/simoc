<!-- Initial welcome screen component. Basic HTML component with the exception of the button click sending the user to the login screen.
    Future version should use a cookie and store the current version number of SIMOC the user last accepted the welcome message on. 
    If it matches on mounted then the component should automatically send the user to the entry screens to prevent this from popping up on repeat vistors.
-->

<template>
    <div class='entry-wrapper'>
        <BaseEntry>            
            <template v-slot:option-items>
                <div class='option-item option-item-active'>
                    SIMOC BETA
                </div>
            </template>
            
            <template v-slot:entry-main>
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
            </template>
            
            <template v-slot:entry-button>
                <button class='btn-warning' @click='toLogin'>PROCEED</button>
            </template>
        </BaseEntry>
    </div>
</template>

<script>
import {BaseEntry} from '../../components/base'
export default {
    components:{
        'BaseEntry':BaseEntry,
    },
    methods:{
        toLogin:function(){
            this.$router.push('entry')
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
    }
    
    .welcome-wrapper{
        height:100%;
        width:100%;
    }

    .welcome-paragraph{
        &:not(:last-of-type){
            margin-bottom:12px;
        }
    }
</style>
