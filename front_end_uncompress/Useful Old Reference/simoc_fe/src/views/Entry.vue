<template>
    <div class='entry-wrapper'>
       <!-- <header class='header'>
            <img src='../assets/simoc-logo.svg' class='logo'/>
            <span class='header-title'>
                SIMOC
            </span>
        </header>-->
        <router-view/>
    </div>
</template>

<script>

export default {

}
</script>

<style lang="scss" scoped>
@import "../sass/views/_entry";
    .entry-wrapper{
        position: relative;
        width: 480px;
        height: 600px;
        box-sizing: border-box;
        background-color: rgba(#1e1e1e,1);
        padding: 16px;
        display:grid;
        grid-template-rows: auto 1fr;
        grid-row-gap: 48px;
        overflow:hidden;
    }
</style>
