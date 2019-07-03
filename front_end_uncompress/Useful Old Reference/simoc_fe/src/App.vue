<template>
  <div id="app" class='app'>
      <div class='orientation-portrait'>
        <img src='./assets/orientation.svg' class='orientation-logo'/>
      </div>
      <div class='normal orientation-landscape'>
        <router-view />
      </div>
  </div>
</template>


<script>
export default {

}
</script>


<style lang="scss">
  @import './sass/styles';

  body{
    padding: 0px;
    margin: 0px;
    background-image:url('./assets/mars-bg.jpg');
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: 50% 10%;
    background-color: #1e1e1e;
    color: #eee;
  }

  .orientation-portrait{
    display:none;
  }

  .orientation-landscape{
    display:block;
  }

  .orientation-logo{
    width: 256px;
    height: auto;
  }

   .app{
    width: 100vw;
    height: 100vh;
    min-width: 600px;
    //position: relative;  
  
    display:flex;
    justify-content:center;
    align-items:center;
  }

   @media all and (orientation: portrait){
    .orientation-portrait{
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 100%;
      background-color: rgba(#1e1e1e,.75);
    }

    .orientation-landscape{
      display:none;
    }
  }

</style>
