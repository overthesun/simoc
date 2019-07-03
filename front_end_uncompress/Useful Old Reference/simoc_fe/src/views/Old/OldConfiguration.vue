<template>
    <div class='configuration-wrapper'>
        <header class='header'>
            <img src='../../assets/simoc-logo-horizontal.svg' class='logo'/>
            <div class='header-message-wrapper'>
                <div class='header-message header-message--normal'>Session Configuration</div>
                <div class='header-message header-message--italic'>{{section}}</div>
            </div>
        </header>
        <main class='main'>
            <div class='test'>Lorem ipsum dolor sit amet, ad scripta lucilius mei, cu minimum complectitur qui. Ne eros probatus eam, quaestio definitionem et quo, errem euismod inermis an sed. Mea assum iriure adipisci cu. Cu sit urbanitas incorrupte, dolor omnium iriure vix ne. An brute modus per, dicant interpretaris cum eu. Vivendum definitionem necessitatibus eum eu. Duo id menandri definiebas. In tollit deleniti persecuti vim. Te usu falli tractatos, qui liber mediocrem disputando cu. Ius ex option vulputate. Soluta facete persequeris per id, et vel ridens everti.</div>
            <div class='test'>Lorem ipsum dolor sit amet, ad scripta lucilius mei, cu minimum complectitur qui. Ne eros probatus eam, quaestio definitionem et quo, errem euismod inermis an sed. Mea assum iriure adipisci cu. Cu sit urbanitas incorrupte, dolor omnium iriure vix ne. An brute modus per, dicant interpretaris cum eu. Vivendum definitionem necessitatibus eum eu. Duo id menandri definiebas. In tollit deleniti persecuti vim. Te usu falli tractatos, qui liber mediocrem disputando cu. Ius ex option vulputate. Soluta facete persequeris per id, et vel ridens everti.</div>
        </main>
        <footer class='footer'>
            <div>Previous Section</div>
            <div>Next Section</div>
            <button>Disabled</button>
            <button>Humans</button>
        </footer>
    </div>
</template>

<script>

export default {
    props:{
        section:String,
    }
}
</script>

<style lang="scss" scoped>
    @import "../sass/views/_configuration";

    .main{
        display: flex;
        overflow: hidden;
    
        *:not(:last-child){
            margin-bottom: 16px;
        }

        *{
            height: 100%;
            overflow:hidden;
            overflow-y:auto;
            scrollbar-color: dark;
        }
    }

    .footer{
        box-sizing: border-box;
        display: flex;
        flex-wrap:wrap;
        text-align:center;
        width: 100%;

        *{
            width: 50%;
        }
    }
</style>
