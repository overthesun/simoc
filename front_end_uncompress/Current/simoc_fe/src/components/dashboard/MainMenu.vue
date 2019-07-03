<!-- Main menu component used within the dashboard
Some buttons are disabled as functionality hasn't been added yet to 
use some of these features.
 -->

<template>
    <div class='main-menu-wrapper' @click='close'>
        <div class='menu-wrapper'>
            <header class='header'>
                <img src='../../assets/simoc-logo.svg' class='simoc-logo'/>
                <span class='simoc-logo-title'>SIMOC</span>
            </header>
            <div class='main-options'>
                <div class='option-item option-item-active'>Main Menu</div>
            </div>
            <main class='main-menu'>
                <button class='btn-normal btn-disabled'>Reset Session</button>
                <button class='btn-normal' @click="toConfiguration">New Simulation</button>
                <button class='btn-normal btn-disabled'>Save Session</button>
                <button class='btn-outline-warning' @click="close">Close Menu</button>
                <button class='btn-warning btn-logout'  @click="logout">Log Out</button>
            </main>
        </div>
    </div>
</template>

<script>
import {mapState,mapGetters,mapMutations} from 'vuex'
export default {
    computed:{
        ...mapGetters('dashboard',['getTimerID']),
        ...mapGetters(['getUseLocalHost']),


    },
    methods:{
        ...mapMutations('dashboard',['SETMENUACTIVE','SETTIMERID','SETBUFFERCURRENT','SETBUFFERMAX']),

        close:function(){
            this.SETMENUACTIVE(false)
            this.getTimerID.resume()
        },

        //Logout button route, this should reset and kill all timers and reset all step / timer related values to their defaults within the store.
        logout: async function(){
            const localHost = "http://localhost:8000"
            const path = "/logout"
            const logoutRoute = this.getUseLocalHost ? localHost + path : path
            
            this.SETTIMERID = null
            this.SETBUFFERCURRENT = 1
            this.SETBUFFERMAX = 1
            for(let i=0; i<100; i++){
                window.clearTimeout(i)
            }
            try{
                axios.post(logoutRoute)
            }catch(error){
                console.log(error)
            }
            this.$router.push("entry")
        },

        //To New Simulation button route, this should reset and kill all timers and reset all step / timer related values to their defaults within the store.
        toConfiguration: async function(){
            for(let i=0; i<100; i++){
                window.clearTimeout(i)
            }
            this.SETTIMERID = null
            this.SETBUFFERCURRENT = 1
            this.SETBUFFERMAX = 1
            this.$router.push("configuration")
        }
    }
}
</script>

<style lang="scss" scoped>
    .main-menu-wrapper{
        position:absolute;
        z-index:200;
        height: 100vh;
        width: 100vw;
        background-color: rgba(#999,.55);
        display:flex;
        justify-content:center;
        align-items:center;
    }

    .main-menu{
        display:flex;
        justify-content:flex-start;;
        align-items:center;
        flex-direction: column;
    }

    .menu-wrapper{
        width: 480px;
        height: 600px;
        max-height: 600px;
        background-color: #1e1e1e;
        z-index:1000;
        padding:16px;
        box-sizing:border-box;
        display:flex;
        justify-content:start-flex;
        align-items:center;
        flex-direction:column;
    }

    .header{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-bottom: 32px;
    }

    .simoc-logo{
        width: auto;
        height: 48px;
        margin-right:8px;
    }

    .simoc-logo-title{
        font-weight: 400;
        font-size: 22px;
    }

    .main-options{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-bottom: 48px;
    }

    .option-item{
        box-sizing:border-box;
        margin: 0px 16px; 
        font-weight: 600;
        font-size: 24px;
        position: relative;

        &:hover{
            cursor:pointer;
        }

        &:after{
            box-sizing:border-box;
            position: absolute;
            right: 0;
            top: 100%;
            content:"";
            width: 0;
            border-bottom: 2px solid lightgreen;
            transition: width .2s ease;
        }

        &-active:after{
            width: 100%;
            left:0;
        }
    }

.btn-normal{
        width: 256px;
        height: 48px;
        min-height: 48px;

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

    .btn-disabled{
        background-color: transparent !important;
        border: 1px solid #999 !important;
        color: #999 !important;

        &:hover{
            cursor:not-allowed !important;
        }

        &:focus{
            outline:none !important;
        }
    }

    .btn-logout{
        margin-top: auto;
    }

    .btn-outline-warning{
        width: 256px;
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

    .btn-warning{
        width: 256px;
        height: 48px;
        min-height: 48px;
        border-radius: 24px;
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 600;
        background-color: #ff3100;
        border:none;
        color: #eee;
        margin-top:auto;
        &:hover{
            cursor: pointer;
        }

        &:focus{
            outline:none;
        }
    }

</style>
