<template>
    <div class='content-wrapper'>
        <header class='header'>
            <div class='header-message'>Options</div>
        </header>
        <main class='main'>
            <button class='menu-btn menu-btn--main' v-on:click='configurationHandler'>New Configuration</button>
            <button class='menu-btn menu-btn--main'>Load Session</button>
        </main>
        <footer class='footer'>
            <button class='menu-btn menu-btn--logout' v-on:click="logoutHandler">Log Out</button>
            <div class='footer-divider--solid'></div>
            <div class='footer-links-wrapper'>
                <div class='footer-link'>View Account</div>
                <div class='footer-link'>Privacy Policy</div>
                <div class='footer-link'>Report Bug</div>
            </div>
        </footer>
    </div>
</template>

<script>
import axios from 'axios'
import {mapState,mapGetters} from 'vuex'
require('promise.prototype.finally');
export default {
    methods:{
        logoutHandler:function(){
            axios.defaults.withCredentials = true;

            const localHost = 'http://localhost:8000';
            const path = '/logout';
            
            const target = this.useLocalHost ? localHost + path : path;
            const params = {'username':this.username,'password':this.password};

            this.loading = true;
            console.log(target);
            axios.get(target,params)
                .then(response=>{
                    const {status} = response;
                    if(status === 200){
                        console.log("logout is working");
   
                    }
                }).catch(error=>{
                    const {status} = error.response;
                    if(status === 500){
                        console.log("Server Error Occurred");
                        
                    }
                }).finally(()=>{
                    this.$router.push({name:'login'})
                })
        },
        configurationHandler:function(){
            this.$router.push({name:'menuconfiguration'})
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
    @import '../../sass/components/menu';
</style>
