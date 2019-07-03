<template>
    <div class='wrapper'>
        <img class='logo' src='../../assets/logo.svg'/>
        <div class='welcome-message'>
            Welcome To <div class='welcome-simoc'>SIMOC</div>
        </div>  
    </div>

</template>

<script>
export default {
    methods:{

    }
}
</script>

<style lang="scss" scoped>
    .wrapper{
        width: 100%;
        height: 100%;
        display: flex;
        justify-content:center;
        align-items:center;
        flex-direction: column;
    }


    .logo{
        width: 128px;
        height: auto;
        margin: 0px auto;
    }

    .welcome-message{
        margin-top: 64px;
        text-align: center;
        font-family:'open sans';
        font-size: 1.5rem;
        font-weight: 200;
    }

    .welcome-simoc{
        font-size: 4rem;
        font-family:'nasalization';
        margin: 16px 0px;
    }
</style>
