<template>
    <div class="configuration-wrapper">
        <div class='configuration-inner-wrapper'>
            <div class='content-wrapper content-wrapper--form'>
                <header class='content-header'>
                    <div class='header-wrapper'>
                        <img src='../../assets/simoc-logo.svg' class='logo'/>
                        <div class='title-wrapper'>
                            <div class='title title--normal'>Session Configuration</div>
                            <div class='title title--italic'>Test</div>
                        </div>
                    </div>
                </header>
                <main class='content-main'></main>
                <footer class='content-footer'></footer>
            </div>
            <div class='content-wrapper content-wrapper--reference'>
                <header class='content-header'>
                    <div class='header-wrapper'>
                        <div class='reference-nav'>Encylopedia</div>
                        <div class='reference-nav'>Graphs</div>
                        <div class='reference-nav'>Recommended</div>
                        <div class='menu-wrapper'>
                            <fa-icon class='fa-icon menu--icon' :icon="['fal','bars']"/>
                        </div>
                    </div>
                </header>
                <main class='content-main'></main>
                <footer class='content-footer'></footer>
            </div> 
        </div>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>
    @import '../sass/mediaqueries';
    @import "../sass/divider";
    
    .configuration-wrapper{
        height:100%;
        width: 100%;
        min-width: 960px;
        max-width: 1024px;
        margin: 0px auto;
        box-sizing:border-box;
        display:flex;
        justify-content:center;
        align-items:center;  
        font-family: 'open sans';

        @include for-desktop-up{
            border-left: 1px solid #4c4c4c;
            border-right: 1px solid #4c4c4c;    
        }
    }

    .configuration-inner-wrapper{
        width: 100%;
        height: 100%;
        max-height: 768px;
        display:grid;
        grid-template-columns: 1fr 1fr;
        grid-template-areas:'form wiki';
        box-sizing:border-box;
    }

    .content-header{
        height: 100%;
        &:after{
            content:"";
            display:block;
            width:100%;
            margin-top: 12px;
            box-sizing: border-box;
            border-bottom: 1px solid;
        }
    }

    .content-wrapper{
        padding: 24px;
        display: grid;
        grid-template-rows: 48px 1fr 48px;
        grid-row-gap: 24px;
    }

    .header-wrapper{
        height: 100%;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        box-sizing: border-box;
    }

    .logo{
        width: 48px; 
        height: auto;
    }

    .title{        
        margin-left: 24px;
        font-size: 16px;
        font-weight: 200;
    }

    .title--italic{
        font-style:italic;
    }

    .reference-nav:not(:last-of-type){
        margin-right: 32px;
        font-size: 1rem;
    }

    .reference-nav{
        font-size: 1rem;
        font-weight: 200;
    }

    .menu-wrapper{
        margin-left: auto;
        font-size: 2rem;
    }

    .content-main{
        height: 100%;
    }
</style>
