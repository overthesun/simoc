<template>
    <div class='view-wrapper'>
        <component :is="'Greenhouse'" :overrideDisplay="false"/>
        <component :is="'Mission'" :overrideDisplay="false"/>
        <component :is="'Energy'" :overrideDisplay="false" />
        <component :is="'Ecosytem'" :overrideDisplay="true"/>
            <!--<component :is=""/>
            <component :is=""/>
            <component :is=""/>
            <component :is="" class='desktop-only-panel'/>
        -->
    </div>
</template>

<script>
import {Greenhouse,Mission,Ecosystem,Energy} from '../dashprimary'
export default {
    components:{
        'Greenhouse':Greenhouse,
        'Mission':Mission,
        'Energy':Energy,
        'Ecosystem':Ecosystem
    }
}
</script>

<style lang="scss" scoped>
    @import "../../sass/mediaqueries";
    @import '../../sass/components/dashprimary';

</style>
