<template>
    <div class='configuration-wrapper'>
        <!--<router-view name='form'/>
        <router-view name='reference'/>-->
        <Form/>
        <Reference/>
    </div>
</template>

<script>
import {Form,Reference} from '../components/configuration'
export default {
    components:{
        "Form":Form,
        "Reference":Reference,
    },
}
</script>

<style lang="scss" scoped>
    @import "../sass/views/_configuration";
</style>
