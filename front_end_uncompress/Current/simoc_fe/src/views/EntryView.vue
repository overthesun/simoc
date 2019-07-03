<!-- Container for all entry related components -->

<template>
    <div class='base-entry-wrapper'>
        <router-view/>
    </div>
</template>

<script>

export default {

}
</script>

<style lang="scss" scoped>
    .base-entry-wrapper{
        position:relative;
        width: 480px;
        height: 600px;
        max-height: 600px;
        background-color: #1e1e1e;
        
        box-sizing:border-box;
        padding: 16px;

        overflow:hidden;
    }


</style>
