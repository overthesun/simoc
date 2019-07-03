<template>
    <div class='configuration-wrapper'>
        
        <div class='configuration-inner-wrapper configuration-inner-wrapper--form'>
           <div class='content-wrapper'>
                <header class='header'>
                    <img src='../../assets/simoc-logo.svg' class='logo'/>
                    <div class='title-wrapper'>
                        <div class='title title--normal'>Session Configuration</div>
                        <div class='title title--italic'>Test</div>
                    </div>
                </header>
                <main class='main'>
                </main>
                <footer class='footer'></footer>
            </div>
        </div>
         <div class='configuration-inner-wrapper configuration-inner-wrapper--reference'>
            <div class='content-wrapper'>
                <header class='header'>
                    <div class='nav-link'>Encyclopedia</div>
                    <div class='nav-link'>Graphs</div>
                    <div class='nav-link'>Recommended</div>
                    <fa-icon class='fa-icon icon--menu' :icon="['fal','bars']"/>
                </header>
                <main class='main'>
                    If you design a mission that includes humans in your off-world habitat, then several other components will be required:
                    <p>Food for the humans to consume as they travel from Earth to Mars and for their time on Mars until the greenhouse produces the first edible plants; an Environmental Control and Life Support System (ECLSS) to maintain breathable air and potable water, as well as manage the human waste products; and a place for the humans to work, recreate, and sleep. Humans are not required for a mission configuration.</p>
                </main>
                <footer class='footer'></footer>
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
        height: 100%;
        width: 100%;
        min-width: 900px;
        max-width: 1024px;
        display: grid;
        grid-template-columns:1fr 1fr;
        margin: 0px auto;
        box-sizing: border-box;
        font-family: 'open sans';

        @include for-desktop-up{
            border-left: 1px solid #4c4c4c;
            border-right: 1px solid #4c4c4c;    
        }
    }

    .configuration-inner-wrapper{
        height: 100%;
        display:flex;
        justify-content:center;
        align-items:center;
        box-sizing: border-box;
        padding: 24px;
        &--form{
            background-color: rgba(#1e1e1e,.75);
        }

        &--reference{
            background-color: rgba(#252525,.75);
        }
    }

    .content-wrapper{
        box-sizing: border-box;
        width:100%;
        height: 100%;
        max-height: 800px;
        display:grid;
        grid-template-rows: 64px 1fr 64px;
        grid-row-gap: 8px;
    }

    .header,.footer{
        display:flex;
        width: 100%;
    }
    
    .header{
        justify-content: center;
        align-items: center;
    }

    .header{
        justify-content:flex-start;
    }

    .logo{
        width: 48px;
        height: auto;
        margin-right: 24px;
    }

    .title-wrapper{
        display: flex;
        justify-content: center;
        align-items:flex-start;
        flex-direction: column;
    }

    .title{
        font-weight: 200;
    }

    .title--italic{
        font-style: italic;
    }

    .nav-link{
        &:not(:last-of-type){
            margin-right: 32px;
        }
    }

    .icon--menu{
        margin-left: auto;
        font-size: 2.5rem;
    }

    .main{
        //margin: 16px 0px;
        box-sizing:border-box;
        border-top: 1px solid #4c4c4c;
        border-bottom: 1px solid #4c4c4c;
        overflow:hidden;
        overflow-y: auto;
        padding: 8px 0px;
    }

    .footer{

    }
</style>
