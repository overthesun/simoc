<template>
    <div class='panel' :class="[overrideDisplay ? 'disableDisplay' : '']">
        <div class='title'>Ecosytem</div>
        <div class='interior'></div>
        <div class='interior'></div>
        <div class='interior'></div>
    </div>
</template>
 
<script>
export default {
    props:{
        overrideDisplay:Boolean
    }
}
</script>

<style lang="scss" scoped>
    @import '../../sass/mediaqueries';
    @import '../../sass/components/dashpanel';

    .disableDisplay{
        display:none;

        @include for-md-desktop-up{
            display:grid;
        }
    }
</style>
