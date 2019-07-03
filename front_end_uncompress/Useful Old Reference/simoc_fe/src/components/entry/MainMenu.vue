<template>
    <div class='entry-child-wrapper'>
        <main class='main'>
            <button class='btn-entry'>NEW CONFIGURATION</button>
            <button class='btn-entry'>LOAD SESSION</button>
            <button class='btn-entry btn-logout'>LOG OUT</button>
        </main>
        <footer class='footer'>
            Test thit out
        </footer>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>
    .entry-child-wrapper{
        height: 100%;
        width: 100%;
        margin: auto auto;
        display:grid;
        grid-template-rows: 1fr auto;
        grid-row-gap: 48px;
    }

    .main{
        height: 100%;
        display:flex;
        justify-content:flex-start;
        align-items:center;
        flex-direction:column;
    }

    .btn-entry{        
        
        &:not(:last-of-type){
            margin-bottom: 24px;
        }

        width: 256px;
        height: 48px;
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

    
    .btn-logout{
        margin-top: auto;
        background-color: #ff3100;
    }
</style>
